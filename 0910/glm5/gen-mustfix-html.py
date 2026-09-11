#!/usr/bin/env python3
"""从 mustfix-draft workflow 输出提取 38 行定案条目，生成批注式对照表 HTML。

数据源（逐字，不转录）：/private/tmp/.../tasks/wx349dd1m.output
产物：0910/glm5/必改对照-rows.json（留档）+ 0910/glm5/必改问题对照表.html
标记约定：原文列 ⟦-…-⟧=红删除；修改后列 ⟦+…+⟧=绿新增。
"""
import html
import json
import pathlib
import re

SRC = "/private/tmp/claude-501/-Users-liu-dev-demos-redis-kafka-books/ae922b37-8a99-4131-801f-d48eaeb6b999/tasks/wx349dd1m.output"
OUT_DIR = pathlib.Path("/Users/liu/dev/demos/redis-kafka-books/0910/glm5")

# 章分组（显示顺序），行号均来自起草 agent 的实测定位
CHAPTERS = [
    ("第 1 章 · 引言", ["V12a", "V12b", "V06a", "V06b", "T2"]),
    ("第 2 章 · 数据结构与协议", ["V04a"]),
    ("第 3 章 · 生命周期管理", ["V09a", "V09b", "V09c", "V09d"]),
    ("第 4 章 · 内存与磁盘", ["V14", "V11", "V04b", "V04c", "V02a", "V10"]),
    ("第 5 章 · 分层架构设计", ["V08"]),
    ("第 6 章 · 安全机制", ["V03"]),
    ("第 7 章 · 集群架构", ["V01a", "V01b", "V01c", "V18a", "V18b", "V17", "T1+N11", "V15a"]),
    ("第 8 章 · 磁盘存储格式", ["V07", "V19", "V05", "W07"]),
    ("第 9 章 · 数据同步机制", ["V01d", "V01e", "V02b", "V15b", "V20", "T2b"]),
    ("第 10 章 · 总结", ["W05"]),
    ("后记", ["W08"]),
]

# 需要作者先裁决再动的行（表内徽标提示）
BADGES = {
    "W08": ("今日必须裁决", "hot"),
    "V06a": ("存疑 · 留作者裁决", "warn"),
    "V06b": ("存疑 · 留作者裁决", "warn"),
    "V03": ("两案并陈 · 留裁决", "warn"),
}

data = json.loads(pathlib.Path(SRC).read_text(encoding="utf-8"))
rows = data["result"]["rows"]
assert len(rows) == 38, f"期望 38 行，实际 {len(rows)}"
by_id = {r["id"]: r for r in rows}
expected = {i for _, ids in CHAPTERS for i in ids}
assert set(by_id) == expected, f"分组与行集不符：{set(by_id) ^ expected}"

# 留档
(OUT_DIR / "必改对照-rows.json").write_text(
    json.dumps({"rows": rows, "chapter_order": [i for _, ids in CHAPTERS for i in ids]},
               ensure_ascii=False, indent=2),
    encoding="utf-8")


def render_cell(text: str) -> str:
    """正文单元格：纯文本渲染，仅标记删除/新增与行内代码，不加任何说明。"""
    t = html.escape(text)
    t = re.sub(r"`([^`\n]+)`", r"<code>\1</code>", t)
    # 表格摘录的行标签（首个「｜」前的定位标签）弱化显示，仍属原文
    t = re.sub(r"^([^⟦⟧<>\n]{1,32}?)｜", r'<span class="lbl">\1</span>｜', t, count=1)
    t = re.sub(r"⟦-(.*?)-⟧", r'<del class="del">\1</del>', t, flags=re.S)
    t = re.sub(r"⟦\+(.*?)\+⟧", r'<ins class="ins">\1</ins>', t, flags=re.S)
    return t.replace("\n", "<br>")


body_rows = []
seq = 0
for chap, ids in CHAPTERS:
    body_rows.append(
        f'<tr class="chap"><td colspan="4"><span class="chap-name">{html.escape(chap)}</span>'
        f'<span class="chap-count">{len(ids)} 项</span></td></tr>')
    for rid in ids:
        seq += 1
        r = by_id[rid]
        badge = ""
        if rid in BADGES:
            label, kind = BADGES[rid]
            badge = f'<span class="badge {kind}">{html.escape(label)}</span>'
        body_rows.append(
            '<tr class="row">'
            f'<td class="loc"><div class="rid">{seq:02d} · {html.escape(rid)}</div>'
            f'{badge}<div class="where">{html.escape(r["location"])}</div></td>'
            f'<td class="src">{render_cell(r["original"])}</td>'
            f'<td class="dst">{render_cell(r["revised"])}</td>'
            f'<td class="why">{html.escape(r["explanation"])}</td>'
            '</tr>')

CSS = """
:root{
  --ground:#F6F5F1;--surface:#FFFFFF;--ink:#23221D;--muted:#736F66;--line:#E2DFD6;
  --accent:#33566B;--accent-soft:#E7EEF2;
  --del-ink:#AC3324;--del-bg:#FAECE8;--ins-ink:#1C6B41;--ins-bg:#E8F3EB;
  --code-bg:#ECEAE2;--warn-ink:#8A5A17;--warn-bg:#FAF1DE;--warn-line:#E4CF9F;
  --hot-bg:#AC3324;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --ground:#191A18;--surface:#212220;--ink:#E8E5DE;--muted:#9B978C;--line:#383630;
    --accent:#9BBDD2;--accent-soft:#243038;
    --del-ink:#F09B8D;--del-bg:#3B2622;--ins-ink:#83D0A2;--ins-bg:#1E3327;
    --code-bg:#2C2B27;--warn-ink:#E3BE7C;--warn-bg:#332A19;--warn-line:#5A4A28;
    --hot-bg:#B8483A;
  }
}
:root[data-theme="dark"]{
  --ground:#191A18;--surface:#212220;--ink:#E8E5DE;--muted:#9B978C;--line:#383630;
  --accent:#9BBDD2;--accent-soft:#243038;
  --del-ink:#F09B8D;--del-bg:#3B2622;--ins-ink:#83D0A2;--ins-bg:#1E3327;
  --code-bg:#2C2B27;--warn-ink:#E3BE7C;--warn-bg:#332A19;--warn-line:#5A4A28;
  --hot-bg:#B8483A;
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
  font-family:"Noto Sans SC","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  font-size:14px;line-height:1.7;}
.wrap{max-width:1460px;margin:0 auto;padding:30px 34px 90px;}
header.page{margin-bottom:22px;}
h1{font-family:"Noto Serif SC","Songti SC",serif;font-weight:700;font-size:27px;
  letter-spacing:.02em;margin:0 0 6px;text-wrap:balance;}
.meta{color:var(--muted);font-size:13px;margin-bottom:14px;font-variant-numeric:tabular-nums;}
.legend{display:flex;flex-wrap:wrap;gap:10px 26px;align-items:center;
  background:var(--surface);border:1px solid var(--line);border-radius:8px;
  padding:10px 16px;font-size:13px;margin-bottom:14px;}
.legend .sw{display:inline-flex;align-items:center;gap:7px;}
.notes{font-size:12.5px;color:var(--muted);border-left:3px solid var(--accent);
  padding:2px 0 2px 14px;margin:0 0 26px;}
.notes p{margin:4px 0;}
.notes b{color:var(--ink);font-weight:600;}
.table-scroll{overflow-x:auto;border:1px solid var(--line);border-radius:8px;
  background:var(--surface);}
table{border-collapse:collapse;width:100%;min-width:1080px;table-layout:fixed;}
col.c1{width:11%}col.c2{width:28%}col.c3{width:29.5%}col.c4{width:31.5%}
thead th{position:sticky;top:0;z-index:2;background:var(--ground);
  font-size:12px;font-weight:600;color:var(--muted);letter-spacing:.14em;
  text-align:left;padding:11px 13px;border-bottom:2px solid var(--line);}
tr.chap td{padding:20px 13px 8px;border-bottom:1px solid var(--line);}
.chap-name{font-family:"Noto Serif SC","Songti SC",serif;font-weight:700;
  font-size:16px;color:var(--accent);}
.chap-count{float:right;font-size:12px;color:var(--muted);margin-top:3px;
  font-variant-numeric:tabular-nums;}
tr.row td{vertical-align:top;padding:14px 13px;border-bottom:1px solid var(--line);}
tr.row:hover td{background:color-mix(in srgb,var(--accent) 4%,transparent);}
td.loc{font-size:12.5px;}
.rid{font-weight:700;color:var(--accent);font-variant-numeric:tabular-nums;
  letter-spacing:.03em;margin-bottom:5px;}
.where{color:var(--muted);margin-top:6px;line-height:1.55;word-break:break-all;}
.badge{display:inline-block;font-size:11px;line-height:1;padding:3px 8px;
  border-radius:999px;}
.badge.warn{color:var(--warn-ink);background:var(--warn-bg);border:1px solid var(--warn-line);}
.badge.hot{color:#FFF;background:var(--hot-bg);font-weight:600;}
.src,.dst{font-family:"Noto Serif SC","Songti SC",serif;font-size:15px;line-height:1.9;
  word-break:break-word;}
.lbl{color:var(--muted);}
del.del{color:var(--del-ink);background:var(--del-bg);text-decoration:line-through;
  text-decoration-thickness:2px;padding:0 3px;border-radius:3px;}
ins.ins{color:var(--ins-ink);background:var(--ins-bg);text-decoration:none;
  font-weight:600;padding:0 3px;border-radius:3px;}
code{font-family:ui-monospace,"SF Mono",Menlo,Consolas,monospace;font-size:.88em;
  background:var(--code-bg);padding:1px 5px;border-radius:4px;}
.why{font-size:12.8px;color:var(--muted);line-height:1.72;}
footer{margin-top:26px;font-size:12px;color:var(--muted);}
@media print{
  :root,:root[data-theme="dark"]{
    --ground:#FFF;--surface:#FFF;--ink:#111;--muted:#555;--line:#CCC;
    --accent:#33566B;--accent-soft:#EEF2F5;
    --del-ink:#AC3324;--del-bg:#F3E3DF;--ins-ink:#1C6B41;--ins-bg:#E4EFE7;
    --code-bg:#F0EEE8;--warn-ink:#8A5A17;--warn-bg:#FAF1DE;--warn-line:#E4CF9F;
    --hot-bg:#AC3324;}
  .wrap{max-width:none;padding:0;}
  thead th{position:static;}
  tr.row{break-inside:avoid;page-break-inside:avoid;}
  .table-scroll{overflow:visible;border:none;}
  table{min-width:0;}
}
"""

HTML = f"""<meta charset="utf-8">
<title>必改问题对照表</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&amp;family=Noto+Sans+SC:wght@400;500;700&amp;display=swap">
<style>{CSS}</style>
<div class="wrap">
<header class="page">
<h1>必改问题对照表</h1>
<div class="meta">《架构观察笔记：从 Redis、MySQL、Kafka 说起》终审修订 · 共 38 项 · 生成于 2026-09-11<br>
来源：两批 150 名读者（100 + 50，完全隔离）试读意见 → 三视角核实定案 / 两批独立复现加冕</div>
<div class="legend">
  <span class="sw"><del class="del">红色删除线</del>＝原文中删去的内容</span>
  <span class="sw"><ins class="ins">绿色底色</ins>＝修改后新写的内容</span>
  <span class="sw" style="color:var(--muted)">第二、三列为纯正文；定位与理由一律在第一、四列</span>
</div>
<div class="notes">
  <p><b>收录口径（38 行）</b>：第一梯队已核实书需修项 23 行（含 V06 存疑求稳版 2 行，采纳前请裁决）＋ 两批复现加冕 3 行（T1+N11 / T2 / T2b）＋ 读者误读加固区 6 行 ＋ 第二批 W 轮定案落笔 3 行（W05 / W07 / W08）。</p>
  <p><b>未收录</b>（可改可不改或需整体裁决）：未核实的 B01–B18 / N01–N16 大部分、T3 横向对比表体系、T4–T8、V13 / V16 可选加固——见 <code>0910/glm5/修订行动清单.md</code>。</p>
  <p><b>施工提醒</b>：本表只做对照，所有修改由作者执行；原文列已逐字核对（14 处抽验全部唯一命中）。V01 五处须一次改齐；V15a / V15b 孪生句措辞须逐字一致；W08 中仓库地址按实际 remote 写为 <code>redis-kafka-mysql-v2</code>（与书内原 URL 不同），请一并确认。</p>
</div>
</header>
<div class="table-scroll">
<table>
<colgroup><col class="c1"><col class="c2"><col class="c3"><col class="c4"></colgroup>
<thead><tr><th>编号 · 位置</th><th>原文</th><th>修改后</th><th>说明</th></tr></thead>
<tbody>
{chr(10).join(body_rows)}
</tbody>
</table>
</div>
<footer>数据源：mustfix-draft 工作流（6 个起草 agent，按章分工，逐字摘录）· 行号均为实测定位 · 本表不改书稿。</footer>
</div>
"""

out = OUT_DIR / "必改问题对照表.html"
out.write_text(HTML, encoding="utf-8")
# 自检：无残留标记、行数正确
leftover = re.findall(r"[⟦⟧]", HTML)
assert not leftover, "存在未转换的 diff 标记"
assert HTML.count('<tr class="row"') == 38
assert HTML.count('<tr class="chap"') == 11
print(f"OK {out}  rows=38 chapters=11  bytes={out.stat().st_size}")
