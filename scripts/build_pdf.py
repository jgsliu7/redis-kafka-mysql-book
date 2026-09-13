#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A4 打印校样 PDF 构建。

复用 build_html 的 markdown→HTML 转换（内容与正式构建同源），套 A4 打印 CSS，
经 Playwright/Chromium 打印为 PDF。目录带真实页码：两遍法——第一遍出 PDF 后
用 pypdf 读锚点的具名目标（named destinations）得到每章/每节落页，回填目录
再出第二遍，并循环校验页码稳定。

用法: python3 scripts/build_pdf.py
产物: build/print-book.html（中间产物，可浏览器打开人工检查）
      dist/print/架构观察笔记-A4校样.pdf
"""
import os, re, sys, glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import build_html as bh  # 复用转换器：convert / link_xrefs / registry / CHAPTERS

from pypdf import PdfReader
from playwright.sync_api import sync_playwright

PDF_DIR = os.path.join(ROOT, 'dist', 'print')
PDF_PATH = os.path.join(PDF_DIR, '架构观察笔记-A4校样.pdf')
HTML_PATH = os.path.join(ROOT, 'build', 'print-book.html')

MARGIN = {'top': '20mm', 'bottom': '18mm', 'left': '22mm', 'right': '22mm'}

# ----------------------------------------------------------------打印 CSS
CSS = """
@page { size: A4; }
*{box-sizing:border-box}
html{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{margin:0;font-family:"Songti SC","STSong","Noto Serif CJK SC",serif;
     font-size:11pt;line-height:1.8;color:#1a1a1a;text-align:justify}
h1,h2,h3,h4{font-family:"PingFang SC","Hiragino Sans GB","Noto Sans CJK SC",sans-serif;
     color:#111;line-height:1.4;text-align:left;break-after:avoid;page-break-after:avoid}
h1{font-size:18pt;margin:0 0 14pt;padding:24pt 0 10pt;border-bottom:2pt solid #222}
h2{font-size:13.5pt;margin:16pt 0 7pt}
h3{font-size:11.5pt;margin:13pt 0 5pt}
h4{font-size:11pt;margin:11pt 0 4pt;color:#24292f}
p{margin:0 0 6pt;orphans:2;widows:2}
/* 中文纸书惯例：正文段首行缩进 2 字。只作用于章内直接子段（blockquote 内、图注、扉页、目录不受影响） */
section.chapter>p{text-indent:2em}
ul,ol{margin:0 0 8pt;padding-left:1.6em}
li{margin:2pt 0;orphans:2;widows:2}
strong{font-weight:700;color:#111}
em{font-style:normal;color:#444}
hr{border:none;border-top:.5pt solid #bbb;margin:14pt 0}
a{color:inherit;text-decoration:none}
code{font-family:"SF Mono",Menlo,Consolas,"PingFang SC",monospace;font-size:9.5pt;
     background:#f1f3f5;padding:.5pt 3pt;border-radius:2pt;color:#1a1a1a}
pre{background:#f6f7f9;border:.5pt solid #d5dbe1;border-radius:3pt;padding:8pt 10pt;
    margin:8pt 0;font-size:9pt;line-height:1.55;white-space:pre-wrap;overflow-wrap:break-word}
pre code{background:none;padding:0;font-size:inherit;border-radius:0;color:inherit}
blockquote{margin:10pt 0;padding:6pt 10pt;border-left:2.5pt solid #4f46e5;background:#f5f6fb;
     border-radius:0 3pt 3pt 0;break-inside:avoid;page-break-inside:avoid}
blockquote p{margin:0}
.table-wrap{margin:10pt 0}
table{border-collapse:collapse;width:100%;font-size:9pt;line-height:1.5;
     font-family:"PingFang SC","Hiragino Sans GB",sans-serif}
thead{display:table-header-group}
tr{break-inside:avoid;page-break-inside:avoid}
th,td{border:.5pt solid #9aa2ab;padding:4pt 6pt;text-align:left;vertical-align:top}
th{background:#edf0f7;font-weight:600;color:#2c3242}
tbody tr:nth-child(even){background:#f7f8fa}
figure.fig{margin:14pt 0;text-align:center;break-inside:avoid;page-break-inside:avoid}
figure.fig svg,.svg-wrap svg,.inline-svg svg{width:100%;max-width:100%;height:auto;display:block;margin:0 auto}
figcaption{font-family:"PingFang SC","Hiragino Sans GB",sans-serif;font-size:9pt;
     color:#555;margin-top:6pt;line-height:1.5;text-align:center}
.inline-svg{display:block}

/* ---------- 扉页 ---------- */
.titlepage{break-after:page;page-break-after:always;text-align:center;
     font-family:"PingFang SC","Hiragino Sans GB",sans-serif;padding-top:70mm}
.titlepage .bk{font-size:30pt;font-weight:700;letter-spacing:3pt;color:#111}
.titlepage .sub{font-size:14pt;color:#333;margin-top:10mm}
.titlepage .meta{margin-top:35mm;font-size:10pt;color:#666;line-height:2}

/* ---------- 目录 ---------- */
section.toc{break-after:page;page-break-after:always}
section.toc h1{font-size:16pt;padding-top:0;border-bottom-width:1.5pt;margin-bottom:12pt}
.toc-row{display:flex;align-items:baseline;font-family:"PingFang SC","Hiragino Sans GB",sans-serif;
     font-size:10pt;margin:3.5pt 0}
.toc-row.lvl1{font-weight:600;font-size:10.5pt;margin-top:9pt}
.toc-row.lvl2{padding-left:14pt;font-weight:400;color:#333}
.toc-row .t{flex:0 1 auto}
.toc-row .dots{flex:1 1 auto;min-width:8pt;margin:0 5pt;border-bottom:.7pt dotted #aaa}
.toc-row .pg{flex:0 0 auto;font-variant-numeric:tabular-nums}

section.chapter{break-before:page;page-break-before:always}
"""

FOOTER_TPL = ('<div style="font-size:8.5px;font-family:\'PingFang SC\',sans-serif;'
              'color:#999;width:100%;text-align:center;padding-top:3mm;">'
              '<span class="pageNumber"></span>&nbsp;/&nbsp;<span class="totalPages"></span></div>')


# ----------------------------------------------------------------组装打印文档
def convert_all():
    """按 build_html.main() 同样的两遍流程转换全书，返回 [(idx, rel, linked_body, heads)]。"""
    counter = [0]
    registry = bh.new_registry()
    converted = []
    for idx, (rel, diag) in enumerate(bh.CHAPTERS):
        md = open(os.path.join(ROOT, rel), encoding='utf-8').read()
        svgmap = {}
        if diag and os.path.isdir(os.path.join(ROOT, diag)):
            for fn in sorted(os.listdir(os.path.join(ROOT, diag))):
                if fn.endswith('.svg'):
                    prefix = fn.replace('.svg', '').replace('-', '_')
                    svgmap['diagrams/' + fn] = '<div class="svg-wrap">' + \
                        bh.load_svg(os.path.join(ROOT, diag, fn), prefix) + '</div>'
        body, heads = bh.convert(md, svgmap, {}, counter, diag, chidx=idx, registry=registry)
        converted.append((idx, rel, body, heads))
    stats = {'linked': 0, 'unresolved': {}}
    out = []
    for (idx, rel, body, heads) in converted:
        out.append((idx, rel, bh.link_xrefs(body, idx, registry, len(bh.CHAPTERS), None, stats), heads))
    return out, stats


def toc_entries(converted):
    """[(anchor, level, title)]：章 h1（锚 ch{idx}）+ 节 h2；参考文献章不再铺 h2（逐章列表与正文章题重复）；
    各章"本章导读"无导航价值，滤除。"""
    entries = []
    for idx, rel, body, heads in converted:
        h1 = next((t for (l, t, _id) in heads if l == 1), os.path.basename(rel))
        entries.append(('ch%d' % idx, 1, h1))
        if rel == 'chapters/11-references.md':
            continue
        for (l, t, hid) in heads:
            if l == 2 and t not in ('本章导读', '导读'):
                entries.append((hid, 2, t))
    return entries


def build_doc(converted, pages):
    """pages: {anchor: 物理页码(1-based)}，缺省时用占位 00。"""
    es = toc_entries(converted)
    rows = []
    for anchor, lvl, title in es:
        pg = str(pages.get(anchor, '00')) if pages.get(anchor) else '00'
        # 标题本身做成锚点链接：Chromium 只为被链接的锚点导出具名目标，
        # 目录行链接 = 两遍法页码回填的数据来源
        rows.append('<div class="toc-row lvl%d"><a class="t" href="#%s">%s</a>'
                    '<span class="dots"></span><span class="pg">%s</span></div>' % (lvl, anchor, title, pg))
    parts = []
    import datetime
    today = datetime.date.today().strftime('%Y年%m月%d日')
    parts.append(
        '<section class="titlepage">'
        '<div class="bk">架构观察笔记</div>'
        '<div class="sub">从 Redis、MySQL、Kafka 说起</div>'
        '<div class="meta">A4 打印校样<br>%s<br>由书稿源文件自动排版生成</div>'
        '</section>' % today)
    parts.append('<section class="toc"><h1>目录</h1>%s</section>' % ''.join(rows))
    for idx, rel, body, heads in converted:
        parts.append('<section class="chapter" id="ch%d">%s</section>' % (idx, body))
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>架构观察笔记：从 Redis、MySQL、Kafka 说起（A4 打印校样）</title>
<style>%s</style>
</head>
<body>
%s
</body>
</html>""" % (CSS, '\n'.join(parts))


def full_chromium():
    """完整版 Chromium（Chrome for Testing）路径；headless shell 不生成 PDF 书签，完整版支持。"""
    g = sorted(glob.glob(os.path.expanduser(
        '~/Library/Caches/ms-playwright/chromium-*/chrome-mac*/'
        'Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing')))
    return g[-1] if g else None


def render_pdf(pw, html_path, pdf_path):
    """优先完整版 Chromium（可出书签）；失败退回 headless shell（无书签，其余一致）。"""
    attempts = []
    exe = full_chromium()
    if exe:
        attempts.append({'executable_path': exe})
    attempts.append({})
    last = None
    for kw in attempts:
        browser = None
        try:
            browser = pw.chromium.launch(**kw)
            page = browser.new_page()
            page.goto('file://' + html_path, wait_until='networkidle')
            page.evaluate('document.fonts.ready.then(() => true)')
            page.pdf(path=pdf_path, format='A4', print_background=True,
                     margin=MARGIN, display_header_footer=True,
                     header_template='<div></div>', footer_template=FOOTER_TPL,
                     outline=True)
            return
        except Exception as e:
            last = e
        finally:
            if browser:
                try:
                    browser.close()
                except Exception:
                    pass
    raise last


def anchor_pages(pdf_path, anchors):
    """读 PDF 具名目标 → {anchor: 1-based 物理页码}。Chromium 导出的名字带前导 '/'。"""
    r = PdfReader(pdf_path)
    nd = r.named_destinations
    pages = {}
    for a in anchors:
        d = nd.get('/' + a) if ('/' + a) in nd else nd.get(a)
        if d is not None:
            try:
                pages[a] = r.get_destination_page_number(d) + 1
            except Exception:
                pass
    return pages, len(nd)


def main():
    os.makedirs(PDF_DIR, exist_ok=True)
    os.makedirs(os.path.dirname(HTML_PATH), exist_ok=True)
    converted, stats = convert_all()
    print('转换完成: %d 个部分 | 交叉引用已链接 %d 处，未解析 %d 种'
          % (len(converted), stats['linked'], len(stats['unresolved'])))
    entries = toc_entries(converted)
    anchors = [a for a, _, _ in entries]

    with sync_playwright() as pw:
        # 两遍法：pass1 拿锚点页码 → 回填目录 → pass2，循环至页码稳定（≤3 轮）
        pages, n_nd = {}, 0
        for rnd in range(1, 4):
            built_with = dict(pages)  # 本遍构建 HTML 时目录里填的页码
            open(HTML_PATH, 'w', encoding='utf-8').write(build_doc(converted, pages))
            render_pdf(pw, HTML_PATH, PDF_PATH)
            new_pages, n_nd = anchor_pages(PDF_PATH, anchors)
            total = len(PdfReader(PDF_PATH).pages)
            missing = [a for a in anchors if a not in new_pages]
            drift = {a: (built_with[a], new_pages[a]) for a in new_pages
                     if a in built_with and built_with[a] != new_pages[a]}
            print('第 %d 遍: %d 页 | 具名目标 %d 个 | 目录锚点命中 %d/%d%s'
                  % (rnd, total, n_nd, len(new_pages), len(anchors),
                     ('，未命中: %s' % ', '.join(missing[:8])) if missing else ''))
            pages = new_pages
            if not missing and new_pages == built_with:
                break  # 落盘 PDF 的目录页码 == 实测页码（第一次发现页码后必再出一遍）
            if drift:
                print('  页码漂移 %d 处，再出一遍' % len(drift))

    size = os.path.getsize(PDF_PATH) / 1024 / 1024
    r = PdfReader(PDF_PATH)

    def walk(items):
        n = 0
        for it in items:
            n += len(walk(it)) if isinstance(it, list) else 1
        return n
    n_bookmarks = walk(r.outline) if r.outline else 0
    print('已生成: %s (%.1f MB) | 书签 %d 条' % (PDF_PATH, size, n_bookmarks))
    print('中间产物: %s（浏览器打开即可人工预览打印效果）' % HTML_PATH)
    for idx, rel, body, heads in converted:
        h1 = next((t for (l, t, _id) in heads if l == 1), rel)
        print('  第 %2d 页起  %s' % (pages.get('ch%d' % idx, 0), h1))


if __name__ == '__main__':
    main()
