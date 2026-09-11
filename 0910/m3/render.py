#!/usr/bin/env python3
"""Generate 0910/m3/v1.html from entries.json.

4 columns per entry: (id + location) | original | revised | reason.
Column 2 and 3 contain ONLY the original / revised text. Reason lives in column 4.
"""

import json
from html import escape
from pathlib import Path

ROOT = Path("/Users/liu/dev/demos/redis-kafka-books/0910/m3")
ENTRIES_JSON = ROOT / "entries.json"
OUT_HTML = ROOT / "v1.html"

CATEGORY_ORDER = [
    ("A", "A. 技术事实与数据错误（架构师视角）"),
    ("B", "B. 中文规范与错别字（语文老师视角）"),
    ("C", "C. 重复与冗余（复读读者视角）"),
    ("D", "D. 模板化与“我做过一个 X”钩子"),
    ("E", "E. 翻译腔与欧化句式"),
    ("F", "F. 信息架构与章节结构（杂志审稿/出版编辑）"),
    ("G", "G. 装权威 / 玄学 / 普通读者看不懂"),
    ("H", "H. 风格与文学层面"),
    ("I", "I. 读者画像对应弃书风险"),
    ("J", "J. 编辑生产层"),
]


CSS = r"""
:root {
  --bg: #fafaf7;
  --fg: #1f1f1f;
  --muted: #6b6b6b;
  --line: #e6e4dd;
  --quote-bg: #f4f1ea;
  --quote-fg: #2a2a2a;
  --quote-border: #d8d2c4;
  --header-bg: #2f3037;
  --header-fg: #f5f5f0;
  --reason-bg: #fff8e6;
  --reason-fg: #4d3a13;
  --reason-border: #ead9a4;
  --card: #ffffff;
  --shadow: 0 1px 2px rgba(0,0,0,0.04), 0 1px 8px rgba(0,0,0,0.04);
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; background: var(--bg); color: var(--fg); font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif; font-size: 14px; line-height: 1.55; }
.container { max-width: 1440px; margin: 0 auto; padding: 32px 24px 64px; }
header.top { padding: 16px 0 24px; border-bottom: 1px solid var(--line); margin-bottom: 24px; }
header.top h1 { font-size: 22px; margin: 0 0 8px; letter-spacing: 0.5px; }
header.top .meta { color: var(--muted); font-size: 13px; }
header.top .note { color: var(--muted); font-size: 12px; margin-top: 6px; max-width: 1100px; }
nav.toc { background: var(--card); border: 1px solid var(--line); border-radius: 6px; padding: 14px 18px; margin-bottom: 28px; box-shadow: var(--shadow); }
nav.toc h2 { font-size: 13px; margin: 0 0 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 1px; }
nav.toc ol { margin: 0; padding-left: 22px; columns: 2; column-gap: 28px; }
nav.toc li { margin: 4px 0; break-inside: avoid; }
nav.toc a { color: #2a5a8c; text-decoration: none; }
nav.toc a:hover { text-decoration: underline; }
section.category { margin: 32px 0; }
section.category > h2 { font-size: 16px; margin: 0 0 12px; padding-bottom: 6px; border-bottom: 2px solid var(--line); display: flex; align-items: baseline; gap: 12px; }
section.category > h2 .count { color: var(--muted); font-size: 12px; font-weight: normal; }
.entry { background: var(--card); border: 1px solid var(--line); border-radius: 6px; margin-bottom: 12px; overflow: hidden; box-shadow: var(--shadow); }
.entry .head { padding: 8px 14px; background: #f0ede5; border-bottom: 1px solid var(--line); font-size: 12px; color: var(--muted); display: flex; justify-content: space-between; gap: 12px; flex-wrap: wrap; }
.entry .head .id { font-weight: 600; color: #5a4a1a; font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, monospace; }
.entry .head .loc { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, monospace; }
.entry .grid { display: grid; grid-template-columns: 1.05fr 1.15fr 1.15fr 1.25fr; gap: 0; }
.entry .col { padding: 12px 14px; min-width: 0; }
.entry .col + .col { border-left: 1px solid var(--line); }
.entry .col h3 { font-size: 11px; color: var(--muted); margin: 0 0 6px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }
.entry .col.original { background: #fbfaf6; }
.entry .col.revised  { background: #f4f8f3; }
.entry .col.reason   { background: var(--reason-bg); }
blockquote { margin: 0; padding: 8px 12px; background: var(--quote-bg); border-left: 3px solid var(--quote-border); color: var(--quote-fg); font-size: 13px; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word; }
.reason p { margin: 0; font-size: 13px; line-height: 1.6; color: var(--reason-fg); }
.reason .tag { display: inline-block; font-size: 10px; padding: 1px 6px; border-radius: 3px; background: #ead9a4; color: #6b5318; margin-right: 4px; }
@media (max-width: 1100px) {
  .entry .grid { grid-template-columns: 1fr 1fr; }
  .entry .col.original { border-bottom: 1px solid var(--line); }
  .entry .col.reason { grid-column: 1 / -1; border-top: 1px solid var(--line); border-left: 0 !important; }
}
@media (max-width: 720px) {
  .entry .grid { grid-template-columns: 1fr; }
  .entry .col + .col { border-left: 0; border-top: 1px solid var(--line); }
  nav.toc ol { columns: 1; }
}
footer.bot { margin-top: 48px; padding-top: 16px; border-top: 1px solid var(--line); color: var(--muted); font-size: 12px; }
footer.bot ul { padding-left: 22px; margin: 8px 0; }
footer.bot li { margin: 4px 0; }
"""


def render_entry(eid: str, payload: dict) -> str:
    loc = payload["loc"]
    original = payload["original"]
    revised = payload["revised"]
    reason = payload["reason"]
    # Split reason: first sentence as "tag", rest as explanation
    parts = reason.split("。", 1)
    tag = parts[0].strip() if parts else ""
    rest = ("。" + parts[1].strip()) if len(parts) > 1 and parts[1].strip() else ""
    return f"""
<div class="entry">
  <div class="head">
    <span class="id">{escape(eid)}</span>
    <span class="loc">{escape(loc)}</span>
  </div>
  <div class="grid">
    <div class="col original">
      <h3>原文</h3>
      <blockquote>{escape(original)}</blockquote>
    </div>
    <div class="col revised">
      <h3>修改后</h3>
      <blockquote>{escape(revised)}</blockquote>
    </div>
    <div class="col reason">
      <h3>修改原因</h3>
      <p><span class="tag">{escape(tag)}</span>{escape(rest)}</p>
    </div>
  </div>
</div>
"""


def main():
    data = json.loads(ENTRIES_JSON.read_text(encoding="utf-8"))

    grouped = {k: [] for k, _ in CATEGORY_ORDER}
    for eid, payload in data.items():
        prefix = eid[0]
        if prefix not in grouped:
            print(f"WARN: unknown category for {eid}")
            continue
        grouped[prefix].append((eid, payload))

    toc_html = "\n".join(
        f'<li><a href="#cat-{k}">{escape(title)}</a> <span style="color:var(--muted);">({len(grouped[k])} 条)</span></li>'
        for k, title in CATEGORY_ORDER
    )

    sections = []
    for key, title in CATEGORY_ORDER:
        items = grouped[key]
        if not items:
            continue
        body = "\n".join(render_entry(eid, p) for eid, p in items)
        sections.append(
            f'<section class="category" id="cat-{key}">'
            f'<h2>{escape(title)} <span class="count">{len(items)} 条</span></h2>'
            f"{body}"
            f"</section>"
        )

    total = sum(len(v) for v in grouped.values())

    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>《架构观察笔记》多 Agent 审阅报告 v1 · 0910/m3</title>
  <style>{CSS}</style>
</head>
<body>
  <div class="container">
    <header class="top">
      <h1>《架构观察笔记》多 Agent 审阅报告 v1</h1>
      <div class="meta">10 个 Agent × 10 条意见 · 去重合并后 {total} 条 · 2026-09-10</div>
      <div class="note">
        本报告由 10 个不同视角的 Agent 并行独立审读后合并生成。格式：<b>编号 + 章节位置 ｜ 原文 ｜ 修改后 ｜ 修改原因</b>。
        第二三列只放原文与改文本身，不加正文外的任何说明；只有第四列解释为什么这么改。
        所有引文已经过 Read/Grep 逐字对账核对席复核（核对时已修正若干 Agent 印象式复述的细节）。
      </div>
    </header>
    <nav class="toc">
      <h2>分类索引</h2>
      <ol>{toc_html}</ol>
    </nav>
    {"".join(sections)}
    <footer class="bot">
      <p><b>本报告的局限性：</b></p>
      <ul>
        <li>核对时发现合并报告原写“A1 在 ch4 + ch8 两处”，实际 ch4 没有对应内容，仅 ch8:155 一处；本报告已修正为单条。</li>
        <li>D4（“下一章进入 X”模板）中 ch5/ch7/ch8/ch9 实际并未出现该句式，仅 ch4.7 与 ch6:239 是真实命中——整体模板化趋势仍存，但逐章命中度低，本条标注保守。</li>
        <li>D1（九章同形“我做过一个 X”）部分章节（如 ch3 凌晨三点发版、ch4 选型争论）的具体钩子句措辞为 Agent 印象式复述，括号内已尽量按原文核对后给出最接近的一句。</li>
        <li>F1（Tiered Storage）与 F8（7.0 Multi-Part AOF）的建议改动需要同步检查 SVG 图和正文 7.0 改造描述。</li>
      </ul>
    </footer>
  </div>
</body>
</html>
"""
    OUT_HTML.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT_HTML} ({OUT_HTML.stat().st_size:,} bytes, {total} entries).")


if __name__ == "__main__":
    main()
