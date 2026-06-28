#!/usr/bin/env python3
"""
SVG 插图几何审计工具 —— 检测文字越界/超框/互压、框部分重叠、线条穿字等。
v5 新增（专治"线/箭头衔接"这一类低级错误，旧版完全漏检）：
  [A] marker 朝向与 orient=auto 冲突       —— 三角形朝 +y 画却配 auto，箭头横着飞（fig-5-7）
  [B] 箭头端点悬空 / 落在框内部             —— 箭头没够到目标框，或戳进框里（fig-3-2/fig-4-4）
  [C] 线段穿过文字                          —— 标注线压在标签上（fig-4-1）
  [D] 连接线穿过框内部（仅查带 marker 的）  —— 归还路径横穿整个框（fig-4-4）
  [E] 图内残留"图 X-Y"编号标题              —— 与下方图注重复（应由构建剥离；此检查兜底）
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

# ---------- path d 展平成折线 ----------
_NUM=r'[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?'
def _nums(s):
    return [float(x) for x in re.findall(_NUM,s)]
def flatten_d(d):
    """把 path d 展平成绝对坐标折线点列表 [(x,y),...]。支持 M L C Q Z 及小写。"""
    if not d: return []
    pts=[]; cx=cy=sx=sy=0.0
    i=0; cmds=re.findall(r'[MLCQZmlcqz]', d)
    args=_nums(d)
    ai=0
    def need(n):
        nonlocal ai
        v=args[ai:ai+n]; ai+=n; return v
    for c in cmds:
        if c in 'Mm':
            x,y=need(2)
            if c=='m': cx+=x; cy+=y
            else: cx,cy=x,y
            sx,sy=cx,cy; pts.append((cx,cy))
            # M 后跟的隐式 L
            while ai<len(args) and (len(args)-ai)>=2 and (cmds[cmds.index(c)] if False else True):
                # 安全做法：直接靠下面 L 循环处理；这里 break 防止误吞
                break
        elif c in 'Ll':
            x,y=need(2)
            if c=='l': cx+=x; cy+=y
            else: cx,cy=x,y
            pts.append((cx,cy))
        elif c in 'Cc':
            x1,y1,x2,y2,x,y=need(6)
            if c=='c':
                x1+=cx;y1+=cy;x2+=cx;y2+=cy;x+=cx;y+=cy
            X0,Y0=cx,cy
            for t in [j/12 for j in range(1,13)]:
                px=(1-t)**3*X0+3*(1-t)**2*t*x1+3*(1-t)*t*t*x2+t*t*t*x
                py=(1-t)**3*Y0+3*(1-t)**2*t*y1+3*(1-t)*t*t*y2+t*t*t*y
                pts.append((px,py))
            cx,cy=x,y
        elif c in 'Qq':
            x1,y1,x,y=need(4)
            if c=='q':
                x1+=cx;y1+=cy;x+=cx;y+=cy
            X0,Y0=cx,cy
            for t in [j/8 for j in range(1,9)]:
                px=(1-t)**2*X0+2*(1-t)*t*x1+t*t*x
                py=(1-t)**2*Y0+2*(1-t)*t*y1+t*t*y
                pts.append((px,py))
            cx,cy=x,y
        elif c in 'Zz':
            if pts and (sx,sy)!=pts[-1]:
                pts.append((sx,sy))
            cx,cy=sx,sy
    return pts

def marker_ref(attr):
    if not attr: return None
    m=re.search(r'url\(#([^)]+)\)', attr)
    return m.group(1) if m else None

def walk(elem, tx, ty, state):
    etf = elem.get('transform','')
    ntx,nty = parse_translate(etf); tx+=ntx; ty+=nty
    selfrot = has_rotate(etf)
    tag = elem.tag.replace(SVG_NS,'')
    vb=state['vb']
    if tag=='marker':
        mid=elem.get('id'); orient=elem.get('orient','')
        pd=elem.find(f'{SVG_NS}path')
        tip=None
        if pd is not None:
            vs=flatten_d(pd.get('d',''))
            if len(vs)>=3:
                cx=sum(p[0] for p in vs)/len(vs); cy=sum(p[1] for p in vs)/len(vs)
                apex=max(vs,key=lambda p:(p[0]-cx)**2+(p[1]-cy)**2)
                others=[p for p in vs if p!=apex]
                if others:
                    bx=sum(p[0] for p in others)/len(others); by=sum(p[1] for p in others)/len(others)
                    dx,dy=apex[0]-bx,apex[1]-by
                    mag=math.hypot(dx,dy) or 1
                    tip=(dx/mag,dy/mag)
        state['markers'][mid]={'orient':orient,'tip':tip}
        return  # marker 内部不再 walk
    if tag=='rect':
        x=pf(elem.get('x'))+tx; y=pf(elem.get('y'))+ty
        w=pf(elem.get('width')); h=pf(elem.get('height'))
        if w>2 and h>2:
            state['rects'].append([x,y,w,h])
            VBX,VBY,VBW,VBH=vb
            if x+w>VBX+VBW+2: state['iss'].append(("high","框右溢出",f"x={x:.0f},w={w:.0f} 右{x+w:.0f}>画布{VBX+VBW:.0f}"))
            if y+h>VBY+VBH+2: state['iss'].append(("high","框下溢出",f"y={y:.0f},h={h:.0f} 下{y+h:.0f}>画布{VBY+VBH:.0f}"))
            if x<VBX-2: state['iss'].append(("high","框左溢出",f"x={x:.0f}<画布左{VBX:.0f}"))
    elif tag=='text':
        x=pf(elem.get('x'))+tx; y=pf(elem.get('y'))+ty
        anchor=elem.get('text-anchor','start'); fs=fs_of(elem)
        t=full_text(elem).strip()
        if not t: return
        tw=text_width(t,fs)
        rot=selfrot
        if rot is not None and abs(rot)>1:
            cx=x; cy=y
            if abs(abs(rot)-90)<1:
                left,right=cx-fs*0.7,cx+fs*0.7
                top,bot=cy-tw/2, cy+tw/2
            else:
                left,right=x-tw/2,x+tw/2; top,bot=y-fs,y
        else:
            if anchor=='middle': left,right=x-tw/2,x+tw/2
            elif anchor=='end': left,right=x-tw,x
            else: left,right=x,x+tw
            top,bot=y-fs*0.95,y+fs*0.3
        VBX,VBY,VBW,VBH=vb
        state['texts'].append({'t':t,'x':x,'y':y,'fs':fs,'left':left,'right':right,'top':top,'bot':bot,'w':tw,'rot':rot})
        if right>VBX+VBW+6: state['iss'].append(("high","文字右溢出画布",f"'{t[:18]}' 右{right:.0f}>画布宽{VBX+VBW:.0f}"))
        if left<VBX-6: state['iss'].append(("high","文字左溢出画布",f"'{t[:18]}' 左{left:.0f}<画布左{VBX:.0f} rot={rot}"))
        if bot>VBY+VBH+6: state['iss'].append(("high","文字下溢出画布",f"'{t[:18]}' 下{bot:.0f}>画布高{VBY+VBH:.0f}"))
        if top<VBY-6: state['iss'].append(("high","文字上溢出画布",f"'{t[:18]}' 上{top:.0f}<画布上{VBY:.0f}"))
        if '——' in t: state['iss'].append(("low","破折号AI味",f"'{t[:28]}'"))
    elif tag=='line':
        x1=pf(elem.get('x1'))+tx; y1=pf(elem.get('y1'))+ty
        x2=pf(elem.get('x2'))+tx; y2=pf(elem.get('y2'))+ty
        mend=marker_ref(elem.get('marker-end')); mstart=marker_ref(elem.get('marker-start'))
        state['segs'].append({'pts':[(x1,y1),(x2,y2)],'mend':mend,'mstart':mstart})
    elif tag=='path':
        d=elem.get('d',''); pts0=flatten_d(d)
        pts=[(p[0]+tx,p[1]+ty) for p in pts0]
        mend=marker_ref(elem.get('marker-end')); mstart=marker_ref(elem.get('marker-start'))
        if pts:
            state['segs'].append({'pts':pts,'mend':mend,'mstart':mstart})
    for ch in elem:
        walk(ch,tx,ty,state)

def pt_in_rect_strict(px,py,r,margin=3):
    rx,ry,rw,rh=r
    return rx+margin<px<rx+rw-margin and ry+margin<py<ry+rh-margin

def seg_interior_hits(p1,p2,r):
    """折线段 p1->p2 落在 rect r 内部的采样点数（共 21 点）。"""
    x1,y1=p1; x2,y2=p2
    hits=0
    for k in range(21):
        t=k/20
        px=x1+(x2-x1)*t; py=y1+(y2-y1)*t
        rx,ry,rw,rh=r
        if rx<px<rx+rw and ry<py<ry+rh:
            hits+=1
    return hits

def seg_crosses_text(p1,p2,tx):
    """段是否穿过文字 bbox 内部（命中文字横向中心带）。"""
    x1,y1=p1; x2,y2=p2
    midx=(tx['left']+tx['right'])/2
    hits=0
    for k in range(25):
        t=k/24
        px=x1+(x2-x1)*t; py=y1+(y2-y1)*t
        if tx['left']<px<tx['right'] and tx['top']<py<tx['bot']:
            hits+=1
    return hits>=2

def dist_pt_to_rect_edge(px,py,r):
    rx,ry,rw,rh=r
    dx=max(rx-px,0,px-(rx+rw)); dy=max(ry-py,0,py-(ry+rh))
    if dx==0 and dy==0: return 0.0
    return math.hypot(dx,dy)

def audit(path):
    tree=ET.parse(path); root=tree.getroot()
    vb=root.get('viewBox','').split()
    if len(vb)!=4: return []
    vb=list(map(float,vb))
    state={'vb':vb,'rects':[],'texts':[],'segs':[],'markers':{},'iss':[]}
    for ch in root: walk(ch,0,0,state)
    rects=state['rects']; texts=state['texts']; segs=state['segs']; markers=state['markers']; issues=state['iss']
    VBX,VBY,VBW,VBH=vb
    # ===== [A] marker 朝向 vs orient 冲突 =====
    for mid,m in markers.items():
        orient=m['orient']; tip=m['tip']
        if tip is None: continue
        if 'auto' not in orient: continue
        dx,dy=tip
        # 正确的 auto marker 应朝 +x（dx>0 且 |dx|>=|dy|）
        if dx<0.3 or abs(dy)>abs(dx):
            issues.append(("high","[A]箭头marker朝向错",f"marker#{mid} 朝向({dx:.1f},{dy:.1f}) 但 orient=auto 需朝(+x)；三角形画错方向，箭头会横飞"))
    # ===== [B] 箭头端点大幅悬空（软信号，仅查离任何框/文字都>18px 的真悬空） =====
    # 注：箭头指向框内某元素、指向文字标签都是合法设计，故"戳进框内"不查、"悬空"阈值取大、降为 low。
    for s in segs:
        pts=s['pts']
        if len(pts)<2: continue
        for which in ('mstart','mend'):
            mk=s.get(which)
            if not mk: continue
            ep = pts[0] if which=='mstart' else pts[-1]
            ex,ey=ep
            best_rect=min((dist_pt_to_rect_edge(ex,ey,r) for r in rects), default=999)
            best_text=min((math.hypot(max(ex-tx['right'],0,tx['left']-ex),max(ey-tx['bot'],0,tx['top']-ey)) for tx in texts if not tx.get('rot')), default=999)
            if best_rect>18 and best_text>18:
                issues.append(("low","[B]箭头端点悬空",f"端点({ex:.0f},{ey:.0f}) 离最近框{best_rect:.0f}px、最近文字{best_text:.0f}px，疑似没指向目标"))
    # ===== [C] 线段穿过文字 =====
    for s in segs:
        pts=s['pts']
        for i in range(len(pts)-1):
            p1,p2=pts[i],pts[i+1]
            for tx in texts:
                if tx.get('rot'): continue
                if seg_crosses_text(p1,p2,tx):
                    issues.append(("high","[C]线段穿过文字",f"'{tshort(tx['t'])}' 被线压过"))
    # ===== [D] 连接线(带marker)横穿框内部（框既非源也非目标） =====
    # 降噪：① 框内穿越采样≥6/21（约30%，排除仅擦边进框连子元素的短段）
    #       ② 连接线两端都不在该框内部（否则是合法连接该框或其子元素）
    for s in segs:
        if not (s.get('mend') or s.get('mstart')): continue
        pts=s['pts']
        sp,ep=pts[0],pts[-1]
        for i in range(len(pts)-1):
            p1,p2=pts[i],pts[i+1]
            for r in rects:
                if seg_interior_hits(p1,p2,r)>=6:
                    if pt_in_rect_strict(sp[0],sp[1],r,1) or pt_in_rect_strict(ep[0],ep[1],r,1):
                        continue
                    issues.append(("high","[D]连接线穿过框内部",f"带箭头连线横穿框[{round(r[0])},{round(r[1])},{round(r[2])}x{round(r[3])}]内部，框既非源也非目标"))
    # ===== [E] 图内残留"图 X-Y"编号标题（应由构建剥离；此检查兜底提示） =====
    for tx in texts:
        if re.match(r'^图\s*\d+[-－]\d+', tx['t']) and tx['y']<70:
            issues.append(("low","[E]图内编号标题",f"'{tshort(tx['t'])}' 将与下方图注重复，构建时应剥离"))
            break
    # ===== 原有检查 =====
    for i in range(len(rects)):
        for j in range(i+1,len(rects)):
            a,b=rects[i],rects[j]
            if contains(a,b) or contains(b,a): continue
            ov,area=inter(a,b)
            if ov and area>400:
                small=min(a[2]*a[3],b[2]*b[3])
                if area>0.2*small:
                    issues.append(("high","框部分重叠",f"{[round(v) for v in a]}↔{[round(v) for v in b]} 重叠{area:.0f}px²"))
    for tx in texts:
        if tx.get('rot'): continue
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
    for i in range(len(texts)):
        for j in range(i+1,len(texts)):
            a,b=texts[i],texts[j]
            if a.get('rot') or b.get('rot'): continue
            ix=max(0,min(a['right'],b['right'])-max(a['left'],b['left']))
            iy=max(0,min(a['bot'],b['bot'])-max(a['top'],b['top']))
            if ix>4 and iy>max(a['fs'],b['fs'])*0.5 and abs(a['y']-b['y'])<max(a['fs'],b['fs'])*0.9:
                issues.append(("high","文字互压",f"'{tshort(a['t'])}'↔'{tshort(b['t'])}'"))
    xs=[];ys=[]
    for r in rects: xs+=[r[0],r[0]+r[2]]; ys+=[r[1],r[1]+r[3]]
    for tx in texts: xs+=[tx['left'],tx['right']]; ys+=[tx['top'],tx['bot']]
    if xs:
        lp,RP,tp,bp=min(xs)-VBX,(VBX+VBW)-max(xs),min(ys)-VBY,(VBY+VBH)-max(ys)
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
# 只打印匹配 argv 的（若有）
import sys
pat=sys.argv[1] if len(sys.argv)>1 else None
hi=0; new_hi=0
for rel,iss in res.items():
    if pat and pat not in rel: continue
    if not iss: continue
    h=[i for i in iss if i[0]=='high']
    m=[i for i in iss if i[0]=='medium']
    if not h and not m: continue
    print(f"\n### {rel}  (high={len(h)} med={len(m)})")
    for sev,cat,det in iss:
        if sev=='low' and cat=='破折号AI味': continue
        print(f"  [{sev:6}] {cat}: {det}")
    hi+=len(h)
    new_hi+=len([i for i in h if i[1].startswith('[')])
print(f"\n=== v5 HIGH 总数(不含破折号): {hi} ===")
print(f"=== v5 新增[A-E]类 HIGH 命中: {new_hi} ===")
open('/tmp/svg_issues_v5.json','w').write(json.dumps(res,ensure_ascii=False))
