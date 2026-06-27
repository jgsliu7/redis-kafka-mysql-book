#!/usr/bin/env python3
"""
SVG 插图几何审计工具 —— 检测文字越界/超框/互压、框部分重叠、线条穿字等。
支持 <g transform="translate"> 累积与 text transform="rotate"，避免误报。
用法:
    python3 scripts/svg_audit.py            # 审计全部 chapters/**/diagrams/*.svg
    python3 scripts/svg_audit.py fig-9-6     # 只看匹配的图
详见 SVG画图说明.md。
"""
import re, glob, os, json, math
import xml.etree.ElementTree as ET
SVG_NS='{http://www.w3.org/2000/svg}'

def char_w(ch,fs):
    if '　'<=ch<='鿿' or '＀'<=ch<='￯' or '㐀'<=ch<='䶿': return fs
    if ch==' ': return 0.3*fs
    return 0.55*fs
def text_width(s,fs):
    return max((sum(char_w(c,fs) for c in ln) for ln in re.split(r'[\r\n]',s)), default=0)
def pf(v,d=0):
    try: return float(v)
    except: return d
def fs_of(e):
    if e.get('font-size'):
        try: return float(e.get('font-size'))
        except: pass
    m=re.search(r'font-size:\s*([\d.]+)',e.get('style',''))
    return float(m.group(1)) if m else 12.0
def full_text(elem):
    p=[]
    if elem.text: p.append(elem.text)
    for s in elem.iter():
        if s is elem: continue
        if s.text: p.append(s.text)
    return ''.join(p)
def parse_translate(tf):
    # 返回 (tx,ty) 仅 translate; rotate 暂存角度
    m=re.search(r'translate\(\s*([-\d.]+)[\s,]+([-\d.]+)\s*\)',tf or '')
    if m: return float(m.group(1)),float(m.group(2))
    return 0.0,0.0
def has_rotate(tf):
    if not tf: return None
    m=re.search(r'rotate\(\s*([-\d.]+)',tf)
    return float(m.group(1)) if m else None
def contains(o,i):
    ox,oy,ow,oh=o; ix,iy,iw,ih=i
    return ox-1<=ix and oy-1<=iy and ix+iw<=ox+ow+1 and iy+ih<=oy+oh+1
def inter(a,b,tol=1):
    ax,ay,aw,ah=a; bx,by,bw,bh=b
    ix=max(0,min(ax+aw,bx+bw)-max(ax,bx)); iy=max(0,min(ay+ah,by+bh)-max(ay,by))
    return ix>tol and iy>tol, ix*iy

def walk(elem, tx, ty, state):
    etf = elem.get('transform','')
    ntx,nty = parse_translate(etf); tx+=ntx; ty+=nty
    selfrot = has_rotate(etf)
    tag = elem.tag.replace(SVG_NS,'')
    vb=state['vb']
    if tag=='rect':
        x=pf(elem.get('x'))+tx; y=pf(elem.get('y'))+ty
        w=pf(elem.get('width')); h=pf(elem.get('height'))
        if w>2 and h>2:
            state['rects'].append([x,y,w,h])
            VBW,VBH=vb[2],vb[3]
            if x+w>VBW+2: state['iss'].append(("high","框右溢出",f"x={x:.0f},w={w:.0f} 右{x+w:.0f}>画布{VBW:.0f}"))
            if y+h>VBH+2: state['iss'].append(("high","框下溢出",f"y={y:.0f},h={h:.0f} 下{y+h:.0f}>画布{VBH:.0f}"))
            if x<-2: state['iss'].append(("high","框左溢出",f"x={x:.0f}"))
    elif tag=='text':
        x=pf(elem.get('x'))+tx; y=pf(elem.get('y'))+ty
        anchor=elem.get('text-anchor','start'); fs=fs_of(elem)
        t=full_text(elem).strip()
        if not t: return
        tw=text_width(t,fs)
        rot=selfrot
        if rot is not None and abs(rot)>1:
            # 旋转文本: bbox 旋转, 横向仅占字号宽, 纵向占文本长
            cx=x; cy=y
            # 简化: 90/-90 度
            if abs(abs(rot)-90)<1:
                half=len_=(tw/2)
                # 旋转后, 横向范围 ≈ [cx-fs/2, cx+fs/2], 纵向 ≈ [cy-tw/2, cy+tw/2]
                left,right=cx-fs*0.7,cx+fs*0.7
                top,bot=cy-tw/2, cy+tw/2
            else:
                left,right=x-tw/2,x+tw/2; top,bot=y-fs,y
        else:
            if anchor=='middle': left,right=x-tw/2,x+tw/2
            elif anchor=='end': left,right=x-tw,x
            else: left,right=x,x+tw
            top,bot=y-fs*0.95,y+fs*0.3
        VBW,VBH=vb[2],vb[3]
        state['texts'].append({'t':t,'x':x,'y':y,'fs':fs,'left':left,'right':right,'top':top,'bot':bot,'w':tw,'rot':rot})
        if right>VBW+6: state['iss'].append(("high","文字右溢出画布",f"'{t[:18]}' 右{right:.0f}>画布宽{VBW:.0f}"))
        if left<-6: state['iss'].append(("high","文字左溢出画布",f"'{t[:18]}' 左{left:.0f}<0 rot={rot}"))
        if bot>VBH+6: state['iss'].append(("high","文字下溢出画布",f"'{t[:18]}' 下{bot:.0f}>画布高{VBH:.0f}"))
        if top<-6: state['iss'].append(("high","文字上溢出画布",f"'{t[:18]}' 上{top:.0f}<0"))
        if '——' in t: state['iss'].append(("low","破折号AI味",f"'{t[:28]}'"))
    elif tag=='line':
        x1=pf(elem.get('x1'))+tx; y1=pf(elem.get('y1'))+ty
        x2=pf(elem.get('x2'))+tx; y2=pf(elem.get('y2'))+ty
        state['lines'].append((x1,y1,x2,y2))
    for ch in elem:
        walk(ch,tx,ty,state)

def audit(path):
    tree=ET.parse(path); root=tree.getroot()
    vb=root.get('viewBox','').split()
    if len(vb)!=4: return []
    vb=list(map(float,vb))
    state={'vb':vb,'rects':[],'texts':[],'lines':[],'iss':[]}
    for ch in root: walk(ch,0,0,state)
    rects=state['rects']; texts=state['texts']; issues=state['iss']
    VBW,VBH=vb[2],vb[3]
    # 框部分重叠(排除嵌套)
    for i in range(len(rects)):
        for j in range(i+1,len(rects)):
            a,b=rects[i],rects[j]
            if contains(a,b) or contains(b,a): continue
            ov,area=inter(a,b)
            if ov and area>400:
                small=min(a[2]*a[3],b[2]*b[3])
                if area>0.2*small:
                    issues.append(("high","框部分重叠",f"{[round(v) for v in a]}↔{[round(v) for v in b]} 重叠{area:.0f}px²"))
    # 文字超框
    for tx in texts:
        if tx.get('rot'): continue  # 旋转文本跳过框检测
        cx=(tx['left']+tx['right'])/2
        cand=[(rw*rh,rx,ry,rw,rh) for (rx,ry,rw,rh) in rects if rx-1<=cx<=rx+rw+1 and ry-2<=tx['y']<=ry+rh+2]
        if not cand: continue
        cand.sort(); _,rx,ry,rw,rh=cand[0]
        if tx['fs']<8.5: continue
        if not (ry-2<=tx['y']<=ry+rh+2): continue
        pl=cx-tx['w']/2-rx; pr=rx+rw-(cx+tx['w']/2)
        if tx['w']>rw+4:
            issues.append(("high","文字超框",f"'{tshort(tx['t'])}' 宽{tx['w']:.0f}>框宽{rw:.0f} 内边距{pl:.0f}/{pr:.0f}"))
        elif pl<-4 or pr<-4:
            issues.append(("medium","文字贴/超框边",f"'{tshort(tx['t'])}' 内边距{pl:.0f}/{pr:.0f} 框宽{rw:.0f}"))
    # 文字互压
    for i in range(len(texts)):
        for j in range(i+1,len(texts)):
            a,b=texts[i],texts[j]
            if a.get('rot') or b.get('rot'): continue
            ix=max(0,min(a['right'],b['right'])-max(a['left'],b['left']))
            iy=max(0,min(a['bot'],b['bot'])-max(a['top'],b['top']))
            if ix>4 and iy>max(a['fs'],b['fs'])*0.5 and abs(a['y']-b['y'])<max(a['fs'],b['fs'])*0.9:
                issues.append(("high","文字互压",f"'{tshort(a['t'])}'↔'{tshort(b['t'])}'"))
    # 留白
    xs=[];ys=[]
    for r in rects: xs+=[r[0],r[0]+r[2]]; ys+=[r[1],r[1]+r[3]]
    for tx in texts: xs+=[tx['left'],tx['right']]; ys+=[tx['top'],tx['bot']]
    if xs:
        lp,RP,tp,bp=min(xs),VBW-max(xs),min(ys),VBH-max(ys)
        if lp<8: issues.append(("medium","内容顶左",f"左边距{lp:.0f}"))
        if RP<8: issues.append(("medium","内容顶右",f"右边距{RP:.0f}"))
        if tp<8: issues.append(("medium","内容顶上",f"上边距{tp:.0f}"))
        if bp<8: issues.append(("medium","内容顶下",f"下边距{bp:.0f}"))
        if min(lp,RP)>=0 and max(lp,RP)>5*max(min(lp,RP),1) and max(lp,RP)>70:
            issues.append(("low","左右留白失衡",f"左{lp:.0f}右{RP:.0f}"))
        if min(tp,bp)>=0 and max(tp,bp)>5*max(min(tp,bp),1) and max(tp,bp)>70:
            issues.append(("low","上下留白失衡",f"上{tp:.0f}下{bp:.0f}"))
    seen=set();out=[]
    for sev,cat,det in issues:
        k=(cat,det)
        if k in seen: continue
        seen.add(k); out.append((sev,cat,det))
    return out

def tshort(s): return s.replace('\n',' ')[:16]
base='/Users/liu/dev/demos/redis-kafka-books/chapters'
res={}
for s in sorted(glob.glob(f'{base}/**/diagrams/*.svg',recursive=True)):
    res[s.replace(base+'/','')]=audit(s)
hi=0
for rel,iss in res.items():
    if not iss: continue
    h=[i for i in iss if i[0]=='high']
    m=[i for i in iss if i[0]=='medium']
    if not h and not m: continue
    print(f"\n### {rel}  (high={len(h)} med={len(m)})")
    for sev,cat,det in iss:
        if sev=='low' and cat=='破折号AI味': continue
        print(f"  [{sev:6}] {cat}: {det}")
    hi+=len(h)
print(f"\n=== v4 HIGH 总数(不含破折号): {hi} ===")
open('/tmp/svg_issues_v4.json','w').write(json.dumps(res,ensure_ascii=False))
