#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""新版电子书构建：十三个稿件单元、内联 SVG、离线目录及打印。
用法: python3 scripts/build_book.py [--draft]
仅使用标准库。Markdown基础解析改编自本项目原build_html.py；构建路径独立。"""
import os, re, sys, html as _html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def load_svg(path, prefix=''):
    s = open(path, encoding='utf-8').read()
    s = re.sub(r'<\?xml[^>]*\?>\s*', '', s)   # 去 XML 声明
    s = re.sub(r'<!DOCTYPE[^>]*>\s*', '', s)
    # 剥离图内"图 X-Y 编号标题"行：下方 figcaption 已承担编号标题，留着会上下重复。
    # 仅构建时剥离；.svg 源文件仍自带标题，单独打开不受影响。保留解释性副标题。
    m = re.search(r'<text\b[^>]*>\s*图\s*\d+[-－]\d+\s*[^<]*</text>', s)
    if m:
        s = s[:m.start()] + s[m.end():]
    # 内联 SVG 没有 width/height 时浏览器会塌缩为 0×0；注入 width="100%" 保证可见
    s = re.sub(r'(<svg\b)(?![^>]*\swidth=)', r'\1 width="100%"', s)
    # 内联到同一 HTML 时，各 SVG 的 <marker id="arrow"> 等会跨文件冲突
    # （HTML 规范要求 id 唯一，且 url(#id) 会全部指向第一个同名定义）。
    # 给每个图的 id 加上唯一前缀（基于文件名），同步替换 url(#...) 引用。
    if prefix:
        ids = set(re.findall(r'\bid="([^"]+)"', s))
        for _id in ids:
            s = s.replace('id="%s"' % _id, 'id="%s_%s"' % (prefix, _id))
            s = s.replace('url(#%s)' % _id, 'url(#%s_%s)' % (prefix, _id))
            s = s.replace('href="#%s"' % _id, 'href="#%s_%s"' % (prefix, _id))
            s = s.replace('aria-labelledby="%s"' % _id, 'aria-labelledby="%s_%s"' % (prefix, _id))
    return s  # <svg ...>...</svg>

def split_row(line):
    line = line.strip()
    if line.startswith('|'): line = line[1:]
    if line.endswith('|'): line = line[:-1]
    return [c.strip().replace(r'\|', '|') for c in re.split(r'(?<!\\)\|', line)]

SEP = re.compile(r'^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$')

def inline(text, svgmap, diag_prefix=''):
    codes = []
    def stash(m):
        codes.append(m.group(1)); return '\x00C%d\x00' % (len(codes) - 1)
    text = re.sub(r'`([^`]+)`', stash, text)
    text = esc(text)
    # 图片
    def img(m):
        alt, url = m.group(1), m.group(2)
        if url in svgmap:
            return '<span class="inline-svg">' + svgmap[url] + '</span>'
        if not url.endswith('.svg') and diag_prefix:
            url = diag_prefix + '/' + os.path.basename(url)
        return '<img src="%s" alt="%s">' % (url, alt)
    text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', img, text)
    # 链接
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    # 加粗 / 斜体
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)', r'<em>\1</em>', text)
    # 还原行内代码
    text = re.sub(r'\x00C(\d+)\x00', lambda m: '<code>' + esc(codes[int(m.group(1))]) + '</code>', text)
    return text

def convert(md, svgmap, gptmap, counter, diag_prefix=''):
    """返回 (html, headings) ；headings=[(level,text,id)]"""
    lines = md.split('\n')
    out, heads = [], []
    i, n = 0, len(lines)

    def is_break(l, nxt):
        if not l.strip(): return True
        if re.match(r'^#{1,6}\s', l): return True
        if l.strip().startswith('```'): return True
        if l.lstrip().startswith('>'): return True
        if re.match(r'^(\s*)([-*+]|\d+\.)\s+', l): return True
        if re.match(r'^(-{3,}|\*{3,}|_{3,})\s*$', l): return True
        if re.match(r'^\s*!\[[^\]]*\]\([^)]+\)\s*$', l): return True
        if l.lstrip().startswith('|') and nxt is not None and SEP.match(nxt): return True
        return False

    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1; continue
        # fenced code
        if line.strip().startswith('```'):
            lang = line.strip()[3:].strip()
            buf = []; i += 1
            while i < n and not lines[i].strip().startswith('```'):
                buf.append(lines[i]); i += 1
            if i == n: raise ValueError('未闭合代码围栏')
            i += 1
            cls = ' class="lang-%s"' % lang if lang else ''
            out.append('<pre><code%s>%s</code></pre>' % (cls, esc('\n'.join(buf))))
            continue
        # heading
        m = re.match(r'^(#{1,6})\s+(.*)$', line)
        if m:
            lvl = len(m.group(1)); txt = m.group(2).strip()
            counter[0] += 1; hid = 's%d' % counter[0]
            heads.append((lvl, txt, hid))
            out.append('<h%d id="%s">%s</h%d>' % (lvl, hid, inline(txt, svgmap, diag_prefix), lvl))
            i += 1; continue
        # hr
        if re.match(r'^(-{3,}|\*{3,}|_{3,})\s*$', line):
            out.append('<hr>'); i += 1; continue
        # table
        if line.lstrip().startswith('|') and i + 1 < n and SEP.match(lines[i + 1]):
            header = split_row(line); rows = []; i += 2
            while i < n and lines[i].lstrip().startswith('|'):
                rows.append(split_row(lines[i])); i += 1
            th = ''.join('<th>%s</th>' % inline(c, svgmap, diag_prefix) for c in header)
            trs = []
            for r in rows:
                while len(r) < len(header): r.append('')
                trs.append('<tr>%s</tr>' % ''.join('<td>%s</td>' % inline(c, svgmap, diag_prefix) for c in r[:len(header)]))
            out.append('<div class="table-wrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (th, ''.join(trs)))
            continue
        # blockquote
        if line.lstrip().startswith('>'):
            buf = []
            while i < n and lines[i].lstrip().startswith('>'):
                buf.append(re.sub(r'^\s*>\s?', '', lines[i])); i += 1
            out.append('<blockquote>%s</blockquote>' % inline(' '.join(b.strip() for b in buf), svgmap, diag_prefix))
            continue
        # list
        lm = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.*)$', line)
        if lm:
            ordered = bool(re.match(r'\d+\.', lm.group(2)))
            items = []
            while i < n:
                lm2 = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.*)$', lines[i])
                if not lm2: break
                items.append(lm2.group(3)); i += 1
            tag = 'ol' if ordered else 'ul'
            rendered_items = []
            for item in items:
                reference = re.match(r'\*\*(R\d+-\d+)\*\*', item)
                attrs = (' class="reference-entry" id="ref-' + reference[1].lower() + '"') if reference else ''
                rendered_items.append('<li' + attrs + '>' + inline(item, svgmap, diag_prefix) + '</li>')
            out.append('<%s>%s</%s>' % (tag, ''.join(rendered_items), tag))
            continue
        # 图片独占行 → figure
        im = re.match(r'^\s*!\[([^\]]*)\]\(([^)]+)\)\s*$', line)
        if im:
            alt, url = im.group(1), im.group(2)
            cap_text = alt
            consumed = 1
            # 若下一行是图注（*图 X-Y …* 或 图 X-Y　…，仅全角空格体例），合并为唯一图注，避免「figcaption + 图注段落」重复
            if i + 1 < n:
                mc = re.match(r'^\s*\*([^*]+)\*\s*$', lines[i + 1])
                mc2 = re.match(r'^\s*图\s*\d+[-－]\d+　', lines[i + 1])
                if mc:
                    cap_text = mc.group(1); consumed = 2
                elif mc2:
                    cap_text = lines[i + 1].strip(); consumed = 2
            cap = '<figcaption>%s</figcaption>' % inline(cap_text, svgmap, diag_prefix) if cap_text else ''
            if url in svgmap:
                fid = os.path.basename(url).removesuffix('.svg')
                out.append('<figure class="fig" id="%s">%s%s</figure>' % (fid, svgmap[url], cap))
            else:
                img_url = diag_prefix + '/' + os.path.basename(url) if diag_prefix else url
                out.append('<figure class="fig"><img src="%s" alt="%s">%s</figure>' % (img_url, alt, cap))
            i += consumed; continue
        # paragraph
        buf = [line]; i += 1
        while i < n:
            l = lines[i]; nxt = lines[i + 1] if i + 1 < n else None
            if is_break(l, nxt): break
            buf.append(l); i += 1
        out.append('<p>%s</p>' % inline(' '.join(b.strip() for b in buf), svgmap, diag_prefix))
    return '\n'.join(out), heads

CHAPTERS = [
    ('chapters/00-preface.md', None),
    ('chapters/01-introduction/chapter.md', 'chapters/01-introduction/diagrams'),
    ('chapters/02-data-structures-protocols/chapter.md', 'chapters/02-data-structures-protocols/diagrams'),
    ('chapters/03-lifecycle/chapter.md', 'chapters/03-lifecycle/diagrams'),
    ('chapters/04-memory-disk/chapter.md', 'chapters/04-memory-disk/diagrams'),
    ('chapters/05-layered-architecture/chapter.md', 'chapters/05-layered-architecture/diagrams'),
    ('chapters/06-security/chapter.md', 'chapters/06-security/diagrams'),
    ('chapters/07-cluster/chapter.md', 'chapters/07-cluster/diagrams'),
    ('chapters/08-storage-format/chapter.md', 'chapters/08-storage-format/diagrams'),
    ('chapters/09-data-sync/chapter.md', 'chapters/09-data-sync/diagrams'),
    ('chapters/10-summary/chapter.md', 'chapters/10-summary/diagrams'),
    ('chapters/10-epilogue.md', None),
    ('chapters/11-references.md', None),
]

CSS = r'''
:root{--ink:#222b35;--muted:#616b76;--line:#d9dee4;--accent:#4f46e5;--soft:#f5f6fa;--paper:#fffefb}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:24px}
body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.9 system-ui,-apple-system,"PingFang SC","Microsoft YaHei",sans-serif}
a{color:var(--accent);text-underline-offset:.18em}a:hover{text-decoration-thickness:2px}
.layout{max-width:1480px;margin:auto;display:grid;grid-template-columns:276px minmax(0,1fr)}
nav{position:sticky;top:0;height:100vh;overflow:auto;padding:28px 18px;border-right:1px solid var(--line);font-size:13px;line-height:1.65;background:#f8f8f5}
nav h2{font-size:17px;margin:0 0 6px}nav .edition{font-size:11px;color:var(--muted);margin-bottom:20px}nav ul{list-style:none;padding:0;margin:0}nav li{margin:0}nav a{display:block;padding:6px 8px;color:var(--ink);text-decoration:none;border-radius:5px}nav a:hover,nav a.active{background:#eaeafa;color:#3730a3}nav .sub a{padding:3px 8px 3px 20px;font-size:12px;color:var(--muted)}
main{width:100%;max-width:calc(46em + 96px);padding:48px 48px 100px;margin:auto;min-width:0}
.cover{min-height:78vh;display:flex;flex-direction:column;justify-content:center;border-bottom:1px solid var(--line);padding:30px 0 64px;margin-bottom:64px}.cover .kicker{font-size:12px;letter-spacing:.15em;color:var(--accent)}.cover h1{font-size:clamp(2.4rem,5vw,3.6rem);letter-spacing:.025em;line-height:1.35;margin:.4em 0}.cover .subtitle{font-size:1.3em;color:var(--muted);margin:.3em 0 2em}.cover .version{font-size:14px;color:var(--muted)}
h1,h2,h3,h4,h5{line-height:1.5;scroll-margin-top:28px;break-after:avoid}section>h1{font-size:1.9em;margin:0 0 1em}h2{font-size:1.35em;margin:2.1em 0 .65em}h3{font-size:1.13em;margin:1.7em 0 .6em}h4{font-size:1.03em;margin:1.4em 0 .5em}p{margin:0 0 1.05em;text-align:justify;overflow-wrap:break-word}section.chapter+section.chapter{margin-top:84px;border-top:1px solid var(--line);padding-top:52px}strong{font-weight:650}em{font-style:normal}hr{border:0;border-top:1px solid var(--line);margin:2.4em 0}
ul,ol{padding-left:1.6em;margin:0 0 1em}li{margin:.4em 0}blockquote{margin:1.3em 0;padding:14px 20px;border-left:3px solid #a5a1d9;background:#f3f3fa;color:#47505d;font-size:.94em}
code{font: .87em/1.65 ui-monospace,"SFMono-Regular",Menlo,Consolas,monospace;background:#efeff2;padding:.1em .28em;border-radius:3px;overflow-wrap:anywhere}pre{padding:18px 20px;background:#f1f2f5;border:1px solid #e0e3e9;border-radius:7px;overflow:auto;line-height:1.6;margin:1.3em 0;tab-size:4}pre code{background:transparent;padding:0;white-space:pre;overflow-wrap:normal;font-size:13px}
.table-wrap{overflow-x:auto;margin:1.6em 0}table{border-collapse:collapse;min-width:100%;font-size:.85em;line-height:1.7}th,td{border:1px solid var(--line);padding:10px 12px;vertical-align:top;text-align:left;min-width:95px}th{background:#edecf8;color:#343454;font-weight:650}tbody tr:nth-child(even){background:#f8f8fa}
figure.fig{margin:2em 0;scroll-margin-top:24px;break-inside:avoid}figure svg{display:block;width:100%;height:auto;background:#fff;border:1px solid #eeedf2;border-radius:7px}figcaption{font-size:.83em;line-height:1.7;color:var(--muted);margin-top:12px;text-align:left}.xref{color:inherit;text-decoration-color:#a8a3dc;text-decoration-style:dotted}.table-caption{font-size:.92em;font-weight:600;margin-bottom:.5em}
.reference-entry{scroll-margin-top:28px}.ref-backlink{white-space:nowrap;font-size:.85em}.toc-toggle,.backdrop{display:none}.skip{position:fixed;left:10px;top:-60px;background:white;z-index:100;padding:10px}.skip:focus{top:10px}.draft{border:1px solid #c67c16;padding:12px;color:#8e5300}
@media(max-width:900px){body{font-size:16px}.layout{display:block}main{padding:28px 22px 80px;max-width:48em}nav{position:fixed;left:0;top:0;width:290px;z-index:20;transform:translateX(-100%);transition:transform .15s}nav.open{transform:translateX(0)}.toc-toggle{display:block;position:fixed;right:18px;bottom:18px;border:0;border-radius:24px;background:#4f46e5;color:white;padding:12px 18px;z-index:30;font:inherit;box-shadow:0 3px 12px #0002}.backdrop.show{display:block;position:fixed;inset:0;z-index:19;background:#0005}.cover{min-height:70vh}section>h1{font-size:1.65em}pre{padding:14px}figure.fig{margin:1.6em 0;overflow-x:auto}figure.fig svg{min-width:760px}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}nav{transition:none}}
@page{size:A4;margin:18mm 17mm 20mm} @media print{body{background:white;font-size:10.5pt;line-height:1.8}.layout{display:block}nav,.toc-toggle,.backdrop,.skip{display:none!important}main{padding:0;max-width:none}.cover{min-height:230mm;margin:0;border:0;break-after:page}.cover h1{font-size:32pt}section.chapter+section.chapter{break-before:page;border:0;margin:0;padding:0}h1,h2,h3,h4{break-after:avoid}p{orphans:3;widows:3}figure.fig{break-inside:avoid;margin:1.4em 0}figure.fig svg{max-height:220mm;border:0;min-width:0;width:100%}pre{white-space:pre-wrap;overflow:visible;break-inside:auto}pre code{white-space:pre-wrap;overflow-wrap:anywhere;font-size:8pt}.table-wrap{overflow:visible}table{width:100%;font-size:8.5pt;table-layout:fixed}th,td{min-width:0;padding:6px;overflow-wrap:anywhere}thead{display:table-header-group}tr{break-inside:avoid}a{color:inherit;text-decoration:none}h2{margin-top:1.5em}}
@media print{.ref-backlink{display:none}.reference-entry a[href^="http"]::after{content:" <" attr(href) ">";font-size:7pt;overflow-wrap:anywhere;word-break:break-all}}
'''

JS = r'''
(()=>{const nav=document.getElementById('toc'),btn=document.getElementById('toc-button'),bd=document.getElementById('backdrop');
function close(){nav.classList.remove('open');bd.classList.remove('show');btn.setAttribute('aria-expanded','false')}
btn.addEventListener('click',()=>{const on=nav.classList.toggle('open');bd.classList.toggle('show',on);btn.setAttribute('aria-expanded',String(on))});bd.addEventListener('click',close);document.addEventListener('keydown',e=>{if(e.key==='Escape')close()});nav.addEventListener('click',e=>{if(e.target.closest('a'))close()});
const links=[...nav.querySelectorAll('a')];if('IntersectionObserver'in window){const io=new IntersectionObserver(es=>{for(const e of es)if(e.isIntersecting){for(const a of links)a.classList.toggle('active',a.hash==='#'+e.target.id)}},{rootMargin:'0px 0px -72% 0px'});document.querySelectorAll('section>h1,section>h2').forEach(e=>io.observe(e))}})();
'''

def main():
    from pathlib import Path
    from html.parser import HTMLParser
    import json, collections
    root = Path(ROOT)
    missing = [p for p,_ in CHAPTERS if not (root/p).exists()]
    if missing and '--draft' not in sys.argv:
        raise SystemExit('缺少正式稿件：' + ', '.join(missing))
    bodies, toc, targets, figures, counts = [], [], {}, [], {}
    counter = [0]
    for index,(rel,diagrams) in enumerate(CHAPTERS):
        path = root/rel
        if not path.exists(): continue
        md = path.read_text(encoding='utf-8')
        counts[rel] = len(re.findall('[\u4e00-\u9fff]',md))
        svgmap = {}
        for alt,url in re.findall(r'!\[([^\]]*)\]\(([^)]+)\)',md):
            asset = path.parent/url
            if not asset.exists() or asset.suffix != '.svg': raise ValueError('插图缺失或非SVG: '+str(asset))
            svgmap[url] = load_svg(str(asset),asset.stem)
            figures.append(asset.relative_to(root).as_posix())
            targets[re.sub(r'^fig-', '',asset.stem)] = asset.stem
        body, heads = convert(md,svgmap,{},counter)
        chapter_id = ('preface' if index==0 else 'epilogue' if index==11 else 'references' if index==12 else 'chapter-'+str(index))
        for level,title,hid in heads:
            if level == 1:
                body=body.replace('id="'+hid+'"','id="'+chapter_id+'"',1);hid=chapter_id
            else:
                m=re.match(r'(\d+(?:\.\d+)+)\s',title)
                if m:
                    stable='section-'+m[1]
                    body=body.replace('id="'+hid+'"','id="'+stable+'"',1);hid=stable
                    targets['section:'+m[1]]=hid
                elif title in ('本版说明', '术语与主题索引'):
                    stable = 'edition-note' if title == '本版说明' else 'term-index'
                    body=body.replace('id="'+hid+'"','id="'+stable+'"',1);hid=stable
            if level <= 2: toc.append((level,title,hid))
        # Table captions are paragraphs in Markdown; give each a stable target.
        def table_cap(m):
            label=m[1];num=re.search(r'表\s*(\d+[-－]\d+)',label)[1].replace('－','-')
            targets['table:'+num]='table-'+num
            return '<p class="table-caption" id="table-'+num+'">'+label+'</p>'
        body=re.sub(r'<p>((?:<strong>)?表\s*\d+[-－]\d+　[^<]*(?:</strong>)?)</p>',table_cap,body)
        bodies.append('<section class="chapter" aria-labelledby="'+chapter_id+'">'+body+'</section>')
    all_body='\n'.join(bodies)
    # Each citation has its own return target; bibliography IDs remain stable.
    citation_counts = collections.Counter()
    def citation(m):
        ref = m[1]
        citation_counts[ref] += 1
        return '<a id="cite-' + ref + '-' + str(citation_counts[ref]) + '" href="#ref-' + ref + '">' + m[2] + '</a>'
    all_body = re.sub(r'<a href="#ref-(r\d+-\d+)">([^<]+)</a>', citation, all_body)
    def reference_backlinks(m):
        ref, content = m[1], m[2]
        links = ''.join(' <a class="ref-backlink" href="#cite-' + ref + '-' + str(i) + '" aria-label="Return to citation ' + str(i) + '">↩' + (str(i) if citation_counts[ref] > 1 else '') + '</a>' for i in range(1, citation_counts[ref] + 1))
        return '<li class="reference-entry" id="ref-' + ref + '">' + content + links + '</li>'
    all_body = re.sub(r'<li class="reference-entry" id="ref-(r\d+-\d+)">(.*?)</li>', reference_backlinks, all_body)
    # Only link prose text nodes: never rewrite code, SVG, existing links or captions.
    class Linker(HTMLParser):
        def __init__(self): super().__init__(convert_charrefs=False);self.parts=[];self.block=0;self.stack=[]
        def handle_starttag(self,tag,attrs):
            self.parts.append(self.get_starttag_text());blocked=tag in ('a','code','pre','svg','figcaption','h1','h2','h3','h4')
            if tag not in ('br','hr','img','meta','link','input'): self.stack.append((tag,blocked));self.block+=blocked
        def handle_endtag(self,tag):
            self.parts.append('</'+tag+'>')
            if self.stack and self.stack[-1][0]==tag:self.block-=self.stack.pop()[1]
        def handle_data(self,data):
            if self.block:self.parts.append(data);return
            def x(m):
                s=m[0]; key=None
                if s.startswith('图'):key=re.sub(r'\s','',s)[1:].replace('－','-')
                elif s.startswith('表'):key='table:'+re.sub(r'\s','',s)[1:].replace('－','-')
                elif s.startswith('第'):key='chapter:'+re.search(r'\d+',s)[0]
                elif s.startswith('§'):key='section:'+s[1:]
                dest=('chapter-'+key.split(':')[1]) if key and key.startswith('chapter:') and ('id="chapter-'+key.split(':')[1]+'"') in all_body else targets.get(key)
                return '<a class="xref" href="#'+dest+'">'+s+'</a>' if dest else s
            self.parts.append(re.sub(r'图\s*\d+[-－]\d+|表\s*\d+[-－]\d+|第\s*\d+\s*章|§\d+(?:\.\d+)+',x,data))
        def handle_entityref(self,n):self.parts.append('&'+n+';')
        def handle_charref(self,n):self.parts.append('&#'+n+';')
        def handle_comment(self,d):self.parts.append('<!--'+d+'-->')
    linker=Linker();linker.feed(all_body);all_body=''.join(linker.parts)
    nav=''.join('<li'+(' class="sub"' if l==2 else '')+'><a href="#'+hid+'">'+esc(t)+'</a></li>' for l,t,hid in toc)
    draft='<p class="draft">制作预览：尚缺'+str(len(missing))+'个稿件单元。</p>' if missing else ''
    book='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><title>架构观察笔记：从 Redis、MySQL、Kafka 说起 · 2026年9月修订版</title><style>'''+CSS+'''</style></head><body><a class="skip" href="#main">跳至正文</a><div class="layout"><nav id="toc" aria-label="全书目录"><h2>架构观察笔记</h2><div class="edition">2026年9月修订版</div><ul><li><a href="#cover">封面</a></li>'''+nav+'''</ul></nav><main id="main"><header class="cover" id="cover"><div class="kicker">ARCHITECTURE OBSERVATION NOTES</div><h1>架构观察笔记</h1><p class="subtitle">从 Redis、MySQL、Kafka 说起</p><p class="version">2026年9月修订版</p>'''+draft+'''</header>'''+all_body+'''</main></div><button class="toc-toggle" id="toc-button" aria-controls="toc" aria-expanded="false">目录</button><div class="backdrop" id="backdrop"></div><script>'''+JS+'''</script></body></html>'''
    book=book.replace('</header>', '<p class="version"><a href="#edition-note">本版说明</a> · <a href="#references">参考文献</a> · <a href="#term-index">术语与主题索引</a></p></header>', 1)
    ids=re.findall(r'\bid="([^"]+)"',book)
    duplicates=[i for i,c in collections.Counter(ids).items() if c>1]
    broken=sorted(set(re.findall(r'href="#([^"]+)"',book))-set(ids))
    assets=re.findall(r'(?:src|href)="(?!#|https?://|mailto:)([^"]+)"',book)
    if duplicates or broken or assets: raise ValueError({'duplicate_ids':duplicates,'broken_anchors':broken,'external_assets':assets})
    output=root/'20260905gpt5.6版本.html';output.write_text(book,encoding='utf-8')
    audit={'output':output.name,'draft':bool(missing),'missing':missing,'manuscript_units':len(counts),'han_by_unit':counts,'han_total':sum(counts.values()),'svg_count':len(figures),'unique_svg_count':len(set(figures)),'duplicate_ids':duplicates,'broken_anchors':broken,'external_assets':assets,'bytes':output.stat().st_size}
    (root/'qa').mkdir(exist_ok=True)
    (root/'qa/build-audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in audit.items() if k!='han_by_unit'},ensure_ascii=False))

if __name__=='__main__':main()
