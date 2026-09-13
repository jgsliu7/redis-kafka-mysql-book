#!/usr/bin/env python3
"""0912/glm/items-agg.json → 汇总结果.html（四列批注对照 + 状态列）

状态来源（可选）：0912/glm/statuses.json  {id: {"status": "done|split|author|pending|converged", "note": "..."}}
- pending 待核（初始） / done 三席一致·已修改 / split 分歧·未修改 / author 留作者裁决·未修改 / converged 作者修订轮亲改·已收敛
"""
import html, json, pathlib, re

D = pathlib.Path("/Users/liu/dev/demos/redis-kafka-books/0912/glm")
data = json.loads((D / "items-agg.json").read_text(encoding="utf-8"))
rows = data["rows"]
by_id = {r["id"]: r for r in rows}
CHAPTERS = [(c, [r["id"] for r in rows if r["chapter"] == c]) for c in data["chapters"]]
assert sum(len(i) for _, i in CHAPTERS) == len(rows) == 53

try:
    ST = json.loads((D / "statuses.json").read_text(encoding="utf-8"))
except FileNotFoundError:
    ST = {}

ST_META = {
    "pending": ("待核", "st-pending"),
    "done": ("三席一致 · 已修改", "st-done"),
    "split": ("分歧 · 未修改", "st-split"),
    "author": ("留作者裁决 · 未修改", "st-author"),
    "converged": ("作者修订 · 已收敛", "st-converged"),
}


def render_cell(text: str) -> str:
    t = html.escape(text)
    t = re.sub(r"`([^`\n]+)`", r"<code>\1</code>", t)
    t = re.sub(r"^([^⟦⟧<>\n]{1,32}?)｜", r'<span class="lbl">\1</span>｜', t, count=1)
    t = re.sub(r"⟦-(.*?)-⟧", r'<del class="del">\1</del>', t, flags=re.S)
    t = re.sub(r"⟦\+(.*?)\+⟧", r'<ins class="ins">\1</ins>', t, flags=re.S)
    return t.replace("\n", "<br>")


body, seq = [], 0
n_status = {k: 0 for k in ST_META}
for chap, ids in CHAPTERS:
    body.append(f'<tr class="chap"><td colspan="4"><span class="chap-name">{html.escape(chap)}</span>'
                f'<span class="chap-count">{len(ids)} 项</span></td></tr>')
    for rid in ids:
        seq += 1
        r = by_id[rid]
        st = ST.get(rid, {}).get("status", "pending")
        n_status[st] += 1
        label, cls = ST_META[st]
        note = ST.get(rid, {}).get("note", "")
        srcs = "＋".join(s.replace("0910/", "") for s in r["src"])
        body.append(
            '<tr class="row">'
            f'<td class="loc"><div class="rid">{seq:02d} · {html.escape(rid)}'
            f'<span class="srcfrom">{html.escape(srcs)}</span></div>'
            f'<span class="badge {cls}">{label}</span>'
            + (f'<div class="stnote {cls}-note">{html.escape(note)}</div>' if note else "")
            + f'<div class="where">{html.escape(r["location"])}</div></td>'
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
  --hot-bg:#AC3324;--ok-ink:#1C6B41;--ok-bg:#E8F3EB;--ok-line:#BCDCC8;
  --split-ink:#AC3324;--split-bg:#FAECE8;--split-line:#EBC7BF;
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --ground:#191A18;--surface:#212220;--ink:#E8E5DE;--muted:#9B978C;--line:#383630;
    --accent:#9BBDD2;--accent-soft:#243038;
    --del-ink:#F09B8D;--del-bg:#3B2622;--ins-ink:#83D0A2;--ins-bg:#1E3327;
    --code-bg:#2C2B27;--warn-ink:#E3BE7C;--warn-bg:#332A19;--warn-line:#5A4A28;
    --hot-bg:#B8483A;--ok-ink:#83D0A2;--ok-bg:#1E3327;--ok-line:#2C4A38;
    --split-ink:#F09B8D;--split-bg:#3B2622;--split-line:#5A3A32;
  }
}
:root[data-theme="dark"]{
  --ground:#191A18;--surface:#212220;--ink:#E8E5DE;--muted:#9B978C;--line:#383630;
  --accent:#9BBDD2;--accent-soft:#243038;
  --del-ink:#F09B8D;--del-bg:#3B2622;--ins-ink:#83D0A2;--ins-bg:#1E3327;
  --code-bg:#2C2B27;--warn-ink:#E3BE7C;--warn-bg:#332A19;--warn-line:#5A4A28;
  --hot-bg:#B8483A;--ok-ink:#83D0A2;--ok-bg:#1E3327;--ok-line:#2C4A38;
  --split-ink:#F09B8D;--split-bg:#3B2622;--split-line:#5A3A32;
}
*{box-sizing:border-box}
body{margin:0;background:var(--ground);color:var(--ink);
  font-family:"Noto Sans SC","PingFang SC","Hiragino Sans GB","Microsoft YaHei",sans-serif;
  font-size:14px;line-height:1.7;}
.wrap{max-width:1500px;margin:0 auto;padding:30px 34px 90px;}
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
.stats{display:flex;flex-wrap:wrap;gap:10px;margin:0 0 22px;}
.method{background:var(--surface);border:1px solid var(--line);border-radius:8px;
  padding:16px 22px 14px;margin:0 0 22px;}
.method h2{font-family:"Noto Serif SC","Songti SC",serif;font-size:16px;font-weight:700;
  color:var(--accent);margin:0 0 6px;letter-spacing:.02em;}
.method .mlead{font-size:12.5px;color:var(--muted);margin:0 0 8px;line-height:1.7;}
.method ol{margin:0;padding-left:20px;}
.method li{font-size:12.8px;line-height:1.72;margin:5px 0;color:var(--ink);}
.method li b{font-weight:600;}
.stat{background:var(--surface);border:1px solid var(--line);border-radius:8px;
  padding:8px 18px;font-size:13px;color:var(--muted);}
.stat b{display:block;font-size:21px;color:var(--ink);font-weight:700;
  font-variant-numeric:tabular-nums;line-height:1.3;}
.table-scroll{overflow-x:auto;border:1px solid var(--line);border-radius:8px;
  background:var(--surface);}
table{border-collapse:collapse;width:100%;min-width:1120px;table-layout:fixed;}
col.c1{width:12%}col.c2{width:27%}col.c3{width:28.5%}col.c4{width:32.5%}
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
.srcfrom{font-weight:400;color:var(--muted);font-size:11px;margin-left:7px;}
.where{color:var(--muted);margin-top:6px;line-height:1.55;word-break:break-all;}
.badge{display:inline-block;font-size:11px;line-height:1;padding:3px 8px;
  border-radius:999px;margin-bottom:4px;}
.stnote{margin:2px 0 6px;font-size:11.5px;line-height:1.6;border-radius:5px;padding:5px 8px;}
.st-note{background:var(--accent-soft);color:var(--ink);}
.st-split-note{background:var(--split-bg);color:var(--split-ink);border:1px solid var(--split-line);}
.st-author-note{background:var(--warn-bg);color:var(--warn-ink);border:1px solid var(--warn-line);}
.st-done-note{background:var(--accent-soft);color:var(--ink);}
.st-converged-note{background:var(--accent-soft);color:var(--ink);}
.st-pending-note{background:var(--surface);color:var(--muted);border:1px solid var(--line);}
.st-pending{color:var(--muted);background:var(--surface);border:1px solid var(--line);}
.st-done{color:var(--ok-ink);background:var(--ok-bg);border:1px solid var(--ok-line);font-weight:600;}
.st-split{color:var(--split-ink);background:var(--split-bg);border:1px solid var(--split-line);font-weight:600;}
.st-author{color:var(--warn-ink);background:var(--warn-bg);border:1px solid var(--warn-line);}
.st-converged{color:var(--accent);background:var(--accent-soft);border:1px solid var(--accent);font-weight:600;}
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
    --hot-bg:#AC3324;--ok-ink:#1C6B41;--ok-bg:#E4EFE7;--ok-line:#BCDCC8;
    --split-ink:#AC3324;--split-bg:#F3E3DF;--split-line:#EBC7BF;}
  .wrap{max-width:none;padding:0;}
  thead th{position:static;}
  tr.row{break-inside:avoid;page-break-inside:avoid;}
  .table-scroll{overflow:visible;border:none;}
  table{min-width:0;}
}
"""

HTML = f"""<meta charset="utf-8">
<title>汇总结果</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&amp;family=Noto+Sans+SC:wght@400;500;700&amp;display=swap">
<style>{CSS}</style>
<div class="wrap">
<header class="page">
<h1>汇总结果 · 两目录必改合并</h1>
<div class="meta">《架构观察笔记：从 Redis、MySQL、Kafka 说起》终审修订 · 共 53 项 · 生成于 2026-09-12<br>
来源：0910/glm5（两批 150 名读者 → 三视角核实定案 38 项）＋ 0910/glm（154 位读者 mustfix 48 条中仍存活的 14 条与 1 处年份残点）</div>
<div class="legend">
  <span class="sw"><del class="del">红色删除线</del>＝原文中删去的内容</span>
  <span class="sw"><ins class="ins">绿色底色</ins>＝修改后新写的内容</span>
  <span class="sw" style="color:var(--muted)">第二、三列为纯正文；定位与理由一律在第一、四列</span>
</div>
<div class="notes">
  <p><b>收录口径（53 行）</b>：glm5 38 项 ＋ glm 存活 14 条（其 48 条中 32 条已被 9/11 上午修订 885dbf2 消解——双席复核无新技术错误、与全书口径自洽，不重核，见 <code>0910/glm5/mustfix-audit/双席对齐汇总.md</code>）＋ MF-43 年份残点 － 合并 2 处同位项（W08≙MF-39 后记版权句、V11≙MF-10 表 4-1）。</p>
  <p><b>执行规则</b>：每行经 3 席独立核实（技术事实 / 书内一致性 / 源码与版本），<b>三席全部判定「问题存在＋认可改法」才由调度修改书稿</b>；未达三席一致的只在本表标记，不改。行号均需执行前重新定位。</p>
  <p><b>施工提醒</b>：V01 五处须一次改齐；V15a/V15b 孪生句补句须两处逐字一致；W08 仓库地址按实际 remote 写为 <code>redis-kafka-mysql-v2</code>（书内原 URL 为 <code>redis-kafka-books</code>），3 席若一致认可则照改；V01c fig-7-1 标签宽度余量小，改后须复查；MF-15 与 MF-45 三处同批次。</p>
  <p><b>执行结果（2026-09-12）</b>：36 项三席一致已落地，经双席改后独立验证（一致性核对席 36/36 逐字落地＋17 项未执行零误动；技术复核席 36/36 技术成立、红线零命中、V01 家族四处口径一致）。15 项分歧与 2 项留作者未动，各席立场见行内备注。遗留口径分叉（均为未达一致侧，待作者裁决后收口）：表 1-1「写性能」（V12a）；ch1:64/ch5:45 的 io-threads 读写方向（MF-15）；ch7:100「接收并刷盘」与 ch10:78「刷入 relay log」（V01a 组，本轮已改四处与之不构成新矛盾）。</p>
  <p><b>作者修订轮复核（2026-09-12 · 284a5a8）</b>：作者提交修订后，双席对照（逐条判定席＋落地完整性席）复核 17 项未执行项与上段遗留分叉。结论：V01a 两处残点（ch7:100、ch10:78）作者亲改收敛，全书 14 处 relay log 口径一致（ACK＝写入 relay log 文件即回、fsync 归 sync_relay_log）；MF-15 部分收敛（ch5 段重写与 ch10 同向，残点仅 ch1:65「加速网络读写」）；36 项已落地改文零回退——31 项逐字在位，5 处被作者后续改写但技术要点经复核仍成立。其余 15 项分歧与 2 项留作者未动，表 1-1「写性能」（V12a）与 ch1:65 仍分叉待作者裁决。fig-3-3 已同步补上作者新增的「首次 AOF 重写未完成」例外注记。</p>
</div>
</header>
<div class="stats">
  <div class="stat"><b>{len(rows)}</b>总条目</div>
  <div class="stat"><b>{n_status['pending']}</b>待核</div>
  <div class="stat"><b>{n_status['done']}</b>三席一致 · 已修改</div>
  <div class="stat"><b>{n_status['converged']}</b>作者修订 · 已收敛</div>
  <div class="stat"><b>{n_status['split']}</b>分歧 · 未修改</div>
  <div class="stat"><b>{n_status['author']}</b>留作者裁决</div>
</div>
<section class="method">
<h2>这轮工作沉淀下的方法论</h2>
<p class="mlead">把「改不改」的裁决权从发现者手里拿走，交给正交视角的独立投票；把每一步状态留下来，让作者修订回流进同一闭环。53 项从两目录读者意见到收敛回写的全过程，可复用的规则六条。</p>
<ol>
<li><b>线索与结论分离。</b>两批 150 名读者与 AI 检查的发现只当线索；逐条经三席独立核实（技术事实 / 书内一致性 / 源码与版本三个正交视角），三票全部「问题存在＋认可改法」才改稿。发现者的置信度不构成修改依据。</li>
<li><b>判、改、验三分离。</b>判定多人投票、施工单人精准替换、改后另派双席独立验证；「36 项逐字落地」与「17 项未执行零误动」都要独立证明，不允许施工者自证。</li>
<li><b>分歧即分层，不是失败。</b>全票项是事实错误，可以改；分歧项几乎全是口径与取舍（V06a 公司史两派互斥、V12a 表格措辞、T1+N11 改文本身有错），归作者裁决。流程自动把「对错」与「裁量」分开，宁可漏改不可错改。</li>
<li><b>状态即文档。</b>statuses.json 是唯一事实源，每项带 status 与各席立场；本页由脚本从状态生成并 assert（行数 53、状态计数），表可复算、不手编漂移。</li>
<li><b>作者修订回流同一闭环。</b>作者按本表自主修订（284a5a8）后不重开审查，只做对照复核：36 项零回退＋清单外修正抽查属实；收敛以状态迁移记录（split → converged），历史不删。对照复核代替重新审查，是人工修订融入机器流程的关键一步。</li>
<li><b>产物必过验证门。</b>SVG 双门（svg_audit 0 HIGH＋渲染真看图）、构建 PASS（183 交叉引用零未解析）、本页计数 assert——生成物不验证不交付。</li>
</ol>
</section>
<div class="table-scroll">
<table>
<colgroup><col class="c1"><col class="c2"><col class="c3"><col class="c4"></colgroup>
<thead><tr><th>编号 · 位置 · 状态</th><th>原文</th><th>修改后</th><th>说明</th></tr></thead>
<tbody>
{chr(10).join(body)}
</tbody>
</table>
</div>
<footer>数据源：items-agg.json（extract-agg.py 逐字提取，未转录）· 3 席核实报告见 0912/glm/audit/ · 执行记录见 statuses.json。</footer>
</div>
"""

out = D / "汇总结果.html"
out.write_text(HTML, encoding="utf-8")
leftover = re.findall(r"[⟦⟧]", HTML)
assert not leftover, "存在未转换的 diff 标记"
assert HTML.count('<tr class="row"') == 53
assert HTML.count('<tr class="chap"') == 12
print(f"OK {out}  rows=53 chapters=12  status={n_status}  bytes={out.stat().st_size}")
