#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a paged HTML review site from the book Markdown sources.

Output:
  dist/index.html
  dist/chapters/*.html

Markdown and SVG remain the source of truth. SVG diagrams are inlined so each
chapter page is self-contained and images display without copying assets.
"""
import os
import shutil
import sys

from build_html import CHAPTERS, JS, convert, load_svg

ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")
CHAPTER_DIR = os.path.join(DIST, "chapters")


PAGE_CSS = """
*{box-sizing:border-box}
:root{--ink:#1f2328;--mute:#57606a;--line:#d8dee4;--accent:#4f46e5;--bg:#fff;--soft:#f6f8fa}
html{scroll-behavior:smooth}
body{margin:0;font-family:"PingFang SC","Hiragino Sans GB","Microsoft YaHei","Noto Sans CJK SC",system-ui,sans-serif;color:var(--ink);background:#fff;line-height:1.8;font-size:16px}
.layout{display:grid;grid-template-columns:292px 1fr;max-width:1340px;margin:0 auto}
nav.toc{position:sticky;top:0;align-self:start;height:100vh;overflow-y:auto;padding:24px 16px 24px 8px;border-right:1px solid var(--line);font-size:14px}
.toc-title{font-weight:700;font-size:15px;color:var(--accent);margin:0 0 4px 8px}
.toc-title a{color:inherit;text-decoration:none}
.toc-sub{font-size:12px;color:var(--mute);margin:0 0 16px 8px}
nav.toc ul{list-style:none;padding:0;margin:0}
nav.toc li>a{display:block;padding:5px 10px;border-radius:6px;color:var(--ink);text-decoration:none;line-height:1.5}
nav.toc li>a:hover{background:var(--soft)}
nav.toc li.active>a{background:#eef2ff;color:var(--accent);font-weight:600}
nav.toc li.nav-sub>a{padding-left:22px;font-size:13px;color:var(--mute)}
.content{padding:32px 48px 120px;max-width:1000px}
.chapter-meta{color:var(--mute);font-size:13px;margin:0 0 18px}
.page-nav{display:flex;justify-content:space-between;gap:16px;margin:40px 0 0;padding-top:20px;border-top:1px solid var(--line)}
.page-nav a{display:block;max-width:48%;padding:10px 12px;border:1px solid var(--line);border-radius:8px;text-decoration:none;color:var(--ink);background:var(--soft);line-height:1.5}
.page-nav a:hover{border-color:var(--accent);color:var(--accent)}
.page-nav .empty{visibility:hidden}
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
figure.fig{margin:2em calc((100% - 1000px)/2);text-align:center}
.svg-wrap,.inline-svg{display:block;width:100%}
figure.fig svg,.inline-svg svg,.svg-wrap svg{width:100%;max-width:1000px;height:auto;display:block;margin:0 auto}
figcaption{color:var(--mute);font-size:.92em;margin-top:.6em;line-height:1.5}
.toc-toggle{display:none}
.review-index{display:grid;gap:12px;margin:24px 0 0}
.review-index a{display:block;padding:14px 16px;border:1px solid var(--line);border-radius:8px;color:var(--ink);text-decoration:none;background:#fff}
.review-index a:hover{border-color:var(--accent);background:#f7f8ff}
.review-index strong{display:block;color:var(--ink)}
.review-index span{display:block;color:var(--mute);font-size:13px;margin-top:2px}
@media(max-width:1200px){figure.fig{margin:2em auto}}
@media(max-width:900px){
  .layout{grid-template-columns:1fr}
  nav.toc{position:fixed;left:0;top:0;width:292px;background:#fff;z-index:50;transform:translateX(-100%);transition:transform .2s;box-shadow:2px 0 12px rgba(0,0,0,.08)}
  nav.toc.open{transform:translateX(0)}
  .content{padding:20px 18px 80px;max-width:100%}
  .toc-toggle{display:inline-block;position:fixed;right:16px;bottom:16px;z-index:60;background:var(--accent);color:#fff;border:none;border-radius:50%;width:48px;height:48px;font-size:13px;box-shadow:0 4px 12px rgba(0,0,0,.2);cursor:pointer}
  .backdrop{display:none;position:fixed;inset:0;background:rgba(0,0,0,.3);z-index:40}
  .backdrop.show{display:block}
}
"""


def html_escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def slug_for(index, rel):
    if rel.endswith("00-preface.md"):
        return "00-preface.html"
    if rel.endswith("10-epilogue.md"):
        return "10-epilogue.html"
    if rel.endswith("11-references.md"):
        return "11-references.html"
    parts = rel.split("/")
    if len(parts) > 1:
        return parts[1] + ".html"
    return "%02d.html" % index


def load_chapters():
    items = []
    counter = [0]
    for idx, (rel, diag) in enumerate(CHAPTERS):
        path = os.path.join(ROOT, rel)
        md = open(path, encoding="utf-8").read()
        svgmap = {}
        gptmap = {}
        if diag and os.path.isdir(os.path.join(ROOT, diag)):
            for fn in sorted(os.listdir(os.path.join(ROOT, diag))):
                if fn.endswith(".svg"):
                    prefix = fn.replace(".svg", "").replace("-", "_")
                    svg = load_svg(os.path.join(ROOT, diag, fn), prefix)
                    svgmap["diagrams/" + fn] = '<div class="svg-wrap">' + svg + "</div>"
                elif fn.endswith('-gpt.png'):
                    gptmap['diagrams/' + fn] = '../../' + diag + '/' + fn
        body, heads = convert(md, svgmap, gptmap, counter, ('../../' + diag) if diag else '')
        title = next((t for (lvl, t, _hid) in heads if lvl == 1), os.path.basename(rel))
        items.append({
            "index": idx,
            "rel": rel,
            "file": slug_for(idx, rel),
            "title": title,
            "body": body,
            "heads": heads,
        })
    return items


def nav_html(items, current_file=None, depth="chapter"):
    prefix = "" if depth == "root" else "../"
    out = ['<ul>']
    out.append('<li><a href="%sindex.html">首页目录</a></li>' % prefix)
    for item in items:
        active = ' class="active"' if item["file"] == current_file else ""
        href = "%schapters/%s" % (prefix, item["file"]) if depth == "root" else item["file"]
        out.append("<li%s><a href=\"%s\">%s</a>" % (active, href, html_escape(item["title"])))
        if item["file"] == current_file:
            subs = [h for h in item["heads"] if h[0] == 2]
            if subs:
                out.append("<ul>")
                for (_lvl, text, hid) in subs:
                    out.append('<li class="nav-sub"><a href="#%s">%s</a></li>' % (hid, html_escape(text)))
                out.append("</ul>")
        out.append("</li>")
    out.append("</ul>")
    return "\n".join(out)


def page_shell(title, nav, main, depth="chapter"):
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s</title>
<style>%s</style>
</head>
<body>
<div class="backdrop" id="bd"></div>
<button class="toc-toggle">目录</button>
<div class="layout">
<nav class="toc" id="toc">
  <div class="toc-title"><a href="%sindex.html">架构之道</a></div>
  <div class="toc-sub">分页审阅版</div>
  %s
</nav>
<main class="content">
%s
</main>
</div>
<script>%s</script>
</body>
</html>""" % (html_escape(title), PAGE_CSS, "" if depth == "root" else "../", nav, main, JS)


def build_index(items):
    cards = []
    for item in items:
        cards.append(
            '<a href="chapters/%s"><strong>%s</strong><span>%s</span></a>'
            % (item["file"], html_escape(item["title"]), html_escape(item["rel"]))
        )
    main = """
<h1>架构之道：分页审阅版</h1>
<p class="chapter-meta">源稿来自 Markdown；本目录用于逐章审阅和单独优化。每章页面已内联 SVG 图示，可直接浏览图片。</p>
<div class="review-index">
%s
</div>
""" % "\n".join(cards)
    return page_shell("架构之道：分页审阅版", nav_html(items, depth="root"), main, depth="root")


def prev_next(items, idx):
    prev_item = items[idx - 1] if idx > 0 else None
    next_item = items[idx + 1] if idx + 1 < len(items) else None
    prev_link = '<a href="%s">← %s</a>' % (prev_item["file"], html_escape(prev_item["title"])) if prev_item else '<span class="empty"></span>'
    next_link = '<a href="%s">%s →</a>' % (next_item["file"], html_escape(next_item["title"])) if next_item else '<span class="empty"></span>'
    return '<nav class="page-nav">%s%s</nav>' % (prev_link, next_link)


def build_chapter_page(items, idx):
    item = items[idx]
    main = '<article class="chapter">%s%s</article>' % (item["body"], prev_next(items, idx))
    return page_shell(item["title"], nav_html(items, current_file=item["file"], depth="chapter"), main, depth="chapter")


def main():
    items = load_chapters()
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(CHAPTER_DIR, exist_ok=True)

    open(os.path.join(DIST, "index.html"), "w", encoding="utf-8").write(build_index(items))
    for idx, item in enumerate(items):
        open(os.path.join(CHAPTER_DIR, item["file"]), "w", encoding="utf-8").write(build_chapter_page(items, idx))

    print("已生成分页站点: %s" % DIST)
    print("首页: %s" % os.path.join(DIST, "index.html"))
    print("章节页: %d" % len(items))


if __name__ == "__main__":
    main()
