#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把全书（序言 + 9 章 + 后记）合并成单个自包含 HTML，SVG 配图内联。
用法: python3 scripts/build_html.py [repo_root]
无第三方依赖。"""
import os, re, sys, html as _html

ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def load_svg(path):
    s = open(path, encoding='utf-8').read()
    s = re.sub(r'<\?xml[^>]*\?>\s*', '', s)   # 去 XML 声明
    s = re.sub(r'<!DOCTYPE[^>]*>\s*', '', s)
    return s  # <svg ...>...</svg>

def split_row(line):
    line = line.strip()
    if line.startswith('|'): line = line[1:]
    if line.endswith('|'): line = line[:-1]
    return [c.strip() for c in line.split('|')]

SEP = re.compile(r'^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$')

def inline(text, svgmap):
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

def convert(md, svgmap, counter):
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
            out.append('<h%d id="%s">%s</h%d>' % (lvl, hid, inline(txt, svgmap), lvl))
            i += 1; continue
        # hr
        if re.match(r'^(-{3,}|\*{3,}|_{3,})\s*$', line):
            out.append('<hr>'); i += 1; continue
        # table
        if line.lstrip().startswith('|') and i + 1 < n and SEP.match(lines[i + 1]):
            header = split_row(line); rows = []; i += 2
            while i < n and lines[i].lstrip().startswith('|'):
                rows.append(split_row(lines[i])); i += 1
            th = ''.join('<th>%s</th>' % inline(c, svgmap) for c in header)
            trs = []
            for r in rows:
                while len(r) < len(header): r.append('')
                trs.append('<tr>%s</tr>' % ''.join('<td>%s</td>' % inline(c, svgmap) for c in r[:len(header)]))
            out.append('<div class="table-wrap"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>' % (th, ''.join(trs)))
            continue
        # blockquote
        if line.lstrip().startswith('>'):
            buf = []
            while i < n and lines[i].lstrip().startswith('>'):
                buf.append(re.sub(r'^\s*>\s?', '', lines[i])); i += 1
            out.append('<blockquote>%s</blockquote>' % inline(' '.join(b.strip() for b in buf), svgmap))
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
            out.append('<%s>%s</%s>' % (tag, ''.join('<li>%s</li>' % inline(t, svgmap) for t in items), tag))
            continue
        # 图片独占行 → figure
        im = re.match(r'^\s*!\[([^\]]*)\]\(([^)]+)\)\s*$', line)
        if im:
            alt, url = im.group(1), im.group(2)
            cap = '<figcaption>%s</figcaption>' % inline(alt, svgmap) if alt else ''
            if url in svgmap:
                out.append('<figure class="fig">%s%s</figure>' % (svgmap[url], cap))
            else:
                out.append('<figure class="fig"><img src="%s" alt="%s">%s</figure>' % (url, alt, cap))
            i += 1; continue
        # paragraph
        buf = [line]; i += 1
        while i < n:
            l = lines[i]; nxt = lines[i + 1] if i + 1 < n else None
            if is_break(l, nxt): break
            buf.append(l); i += 1
        out.append('<p>%s</p>' % inline(' '.join(b.strip() for b in buf), svgmap))
    return '\n'.join(out), heads

CHAPTERS = [
    ('chapters/00-preface.md', None),
    ('chapters/01-introduction/chapter.md', 'chapters/01-introduction/diagrams'),
    ('chapters/02-lifecycle/chapter.md', 'chapters/02-lifecycle/diagrams'),
    ('chapters/03-memory-disk/chapter.md', 'chapters/03-memory-disk/diagrams'),
    ('chapters/04-layered-architecture/chapter.md', 'chapters/04-layered-architecture/diagrams'),
    ('chapters/05-security/chapter.md', 'chapters/05-security/diagrams'),
    ('chapters/06-cluster/chapter.md', 'chapters/06-cluster/diagrams'),
    ('chapters/07-storage-format/chapter.md', 'chapters/07-storage-format/diagrams'),
    ('chapters/08-data-sync/chapter.md', 'chapters/08-data-sync/diagrams'),
    ('chapters/09-summary/chapter.md', 'chapters/09-summary/diagrams'),
    ('chapters/10-epilogue.md', None),
]

CSS = """
*{box-sizing:border-box}
:root{--ink:#1f2328;--mute:#57606a;--line:#d8dee4;--accent:#4f46e5;--bg:#fff;--soft:#f6f8fa}
html{scroll-behavior:smooth}
body{margin:0;font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans CJK SC",system-ui,sans-serif;color:var(--ink);background:#fff;line-height:1.8;font-size:16px}
.layout{display:grid;grid-template-columns:264px 1fr;max-width:1180px;margin:0 auto}
nav.toc{position:sticky;top:0;align-self:start;height:100vh;overflow-y:auto;padding:24px 16px 24px 8px;border-right:1px solid var(--line);font-size:14px}
.toc-title{font-weight:700;font-size:15px;color:var(--accent);margin:0 0 4px 8px}
.toc-sub{font-size:12px;color:var(--mute);margin:0 0 16px 8px}
nav.toc ul{list-style:none;padding:0;margin:0}
nav.toc li>a{display:block;padding:5px 10px;border-radius:6px;color:var(--ink);text-decoration:none;line-height:1.5}
nav.toc li>a:hover{background:var(--soft)}
nav.toc li.active>a{background:#eef2ff;color:var(--accent);font-weight:600}
nav.toc li.nav-sub>a{padding-left:22px;font-size:13px;color:var(--mute)}
.content{padding:32px 40px 120px;max-width:820px}
section.chapter{scroll-margin-top:20px}
section.chapter+section.chapter{margin-top:64px;border-top:2px solid var(--line);padding-top:40px}
h1,h2,h3,h4{line-height:1.35;color:var(--ink);font-weight:700}
h1{font-size:1.9em;margin:0 0 .6em;padding-bottom:.3em}
h2{font-size:1.42em;margin:1.8em 0 .6em}
h3{font-size:1.18em;margin:1.5em 0 .5em}
h4{font-size:1.04em;margin:1.3em 0 .4em;color:#24292f}
p{margin:0 0 1em}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
strong{font-weight:700;color:#111827}
em{font-style:normal;color:var(--mute)}
hr{border:none;border-top:1px solid var(--line);margin:2.4em 0}
code{font-family:"SF Mono",Menlo,Consolas,monospace;background:var(--soft);padding:.12em .4em;border-radius:4px;font-size:.9em;color:#24292f}
pre{background:#1e1e2e;color:#cdd6f4;padding:16px 18px;border-radius:8px;overflow-x:auto;line-height:1.55}
pre code{background:none;color:inherit;padding:0;font-size:.86em}
blockquote{margin:1.2em 0;padding:.6em 1em .6em 1.1em;border-left:4px solid var(--accent);background:#f7f8ff;color:#343a40;border-radius:0 6px 6px 0}
blockquote strong{color:var(--accent)}
ul,ol{margin:0 0 1em;padding-left:1.7em}
li{margin:.25em 0}
.table-wrap{overflow-x:auto;margin:1.2em 0}
table{border-collapse:collapse;width:100%;font-size:.94em}
th,td{border:1px solid var(--line);padding:8px 12px;text-align:left;vertical-align:top}
thead th{background:#eef2ff;color:#3730a3;font-weight:600}
tbody tr:nth-child(even){background:#fafbfd}
figure.fig{margin:1.8em auto;text-align:center}
.svg-wrap,.inline-svg{display:inline-block;max-width:100%}
figure.fig svg,.inline-svg svg,.svg-wrap svg{max-width:100%;height:auto;display:block;margin:0 auto}
figcaption{color:var(--mute);font-size:.88em;margin-top:.6em;line-height:1.5}
.toc-toggle{display:none}
@media(max-width:860px){
  .layout{grid-template-columns:1fr}
  nav.toc{position:fixed;left:0;top:0;width:280px;background:#fff;z-index:50;transform:translateX(-100%);transition:transform .2s;box-shadow:2px 0 12px rgba(0,0,0,.08)}
  nav.toc.open{transform:translateX(0)}
  .content{padding:20px 18px 80px;max-width:100%}
  .toc-toggle{display:inline-block;position:fixed;right:16px;bottom:16px;z-index:60;background:var(--accent);color:#fff;border:none;border-radius:50%;width:48px;height:48px;font-size:13px;box-shadow:0 4px 12px rgba(0,0,0,.2);cursor:pointer}
  .backdrop{display:none;position:fixed;inset:0;background:rgba(0,0,0,.3);z-index:40}
  .backdrop.show{display:block}
}
@media print{nav.toc{display:none}.layout{grid-template-columns:1fr}.content{max-width:100%;padding:0}section.chapter+section.chapter{page-break-before:always;border-top:none}}
"""

JS = """
(function(){
  var btn=document.querySelector('.toc-toggle'),nav=document.getElementById('toc'),bd=document.getElementById('bd');
  if(btn){btn.addEventListener('click',function(){nav.classList.toggle('open');if(bd)bd.classList.toggle('show',nav.classList.contains('open'))});}
  if(bd){bd.addEventListener('click',function(){nav.classList.remove('open');bd.classList.remove('show');});}
  // 当前章节高亮
  var secs=Array.prototype.slice.call(document.querySelectorAll('section.chapter'));
  var links=Array.prototype.slice.call(document.querySelectorAll('nav.toc a[data-target]'));
  if('IntersectionObserver' in window && links.length){
    var map={};links.forEach(function(a){map[a.getAttribute('data-target')]=a;});
    var io=new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if(e.isIntersecting){
          links.forEach(function(a){a.parentElement.classList.remove('active');});
          var a=map[e.target.id]; if(a)a.parentElement.classList.add('active');
        }
      });
    },{rootMargin:'-10% 0px -75% 0px',threshold:0});
    secs.forEach(function(s){io.observe(s);});
  }
})();
"""

def main():
    counter = [0]
    nav_parts = ['<ul>']
    body_parts = []
    for idx, (rel, diag) in enumerate(CHAPTERS):
        path = os.path.join(ROOT, rel)
        md = open(path, encoding='utf-8').read()
        svgmap = {}
        if diag and os.path.isdir(os.path.join(ROOT, diag)):
            for fn in sorted(os.listdir(os.path.join(ROOT, diag))):
                if fn.endswith('.svg'):
                    svg = load_svg(os.path.join(ROOT, diag, fn))
                    svgmap['diagrams/' + fn] = '<div class="svg-wrap">' + svg + '</div>'
        html_body, heads = convert(md, svgmap, counter)
        sec_id = 'ch%d' % idx
        # 章标题（第一个 h1）作为 nav 项
        h1 = next((t for (l, t, _id) in heads if l == 1), os.path.basename(rel))
        nav_parts.append('<li><a href="#%s" data-target="%s">%s</a>' % (heads[0][2] if heads else sec_id, sec_id, h1))
        # 子项 h2
        subs = [h for h in heads if h[0] == 2]
        if subs:
            nav_parts.append('<ul>')
            for (l, t, hid) in subs:
                nav_parts.append('<li class="nav-sub"><a href="#%s">%s</a></li>' % (hid, t))
            nav_parts.append('</ul>')
        nav_parts.append('</li>')
        body_parts.append('<section class="chapter" id="%s">%s</section>' % (sec_id, html_body))
    nav_parts.append('</ul>')

    doc = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>架构之道：从 Redis、MySQL、Kafka 看软件设计的共性</title>
<style>%s</style>
</head>
<body>
<div class="backdrop" id="bd"></div>
<button class="toc-toggle">目录</button>
<div class="layout">
<nav class="toc" id="toc">
  <div class="toc-title">架构之道</div>
  <div class="toc-sub">从 Redis、MySQL、Kafka 看软件设计的共性</div>
  %s
</nav>
<main class="content">
<article>
%s
</article>
</main>
</div>
<script>%s</script>
</body>
</html>""" % (CSS, '\n  '.join(nav_parts), '\n'.join(body_parts), JS)

    out = os.path.join(ROOT, '架构之道.html')
    open(out, 'w', encoding='utf-8').write(doc)
    size = os.path.getsize(out)
    nsvg = doc.count('<svg')
    ntab = doc.count('<table')
    print('已生成: %s' % out)
    print('大小: %.1f KB | 内联 SVG: %d | 表格: %d | 章节: %d' % (size / 1024, nsvg, ntab, len(CHAPTERS)))

if __name__ == '__main__':
    main()
