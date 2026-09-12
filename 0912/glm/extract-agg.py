#!/usr/bin/env python3
"""聚合两个 glm 目录的存活条目 → 0912/glm/items-agg.json

来源一：0910/glm5/必改对照-rows.json（38 项，⟦-…-⟧/⟦+…+⟧ 行内标记，基于 9/11 午后书稿）
来源二：0910/glm/mustfix.html（48 条；经双席评审 32 条已被上午修订消解，
        存活 16 条 + MF-43 年份残点 → 由 <del>/<ins> 解析回 ⟦⟧ 标记）
合并：MF-39≙W08（同一句后记版权句）、MF-10≙V11（同一张表 4-1）→ 各并为一行
"""
import json, pathlib, re, html as H

ROOT = pathlib.Path("/Users/liu/dev/demos/redis-kafka-books")
OUT = ROOT / "0912/glm/items-agg.json"

# ---------- 解析 mustfix.html ----------
mf_html = (ROOT / "0910/glm/mustfix.html").read_text(encoding="utf-8")


def cell_to_marked(html_frag: str) -> str:
    """td 内 utext 列表 → 带 ⟦⟧ 标记的纯文本。"""
    # 取所有 utext 块（原文/修改后各 1 块；MF-14 等多处引用会有多块）
    blocks = re.findall(r'<div class="utext">(.*?)</div>\s*</div>', html_frag, re.S)
    outs = []
    for b in blocks:
        b = re.sub(r'<br\s*/?>', '\n', b)
        b = re.sub(r'<del>(.*?)</del>', r'⟦-\1-⟧', b, flags=re.S)
        b = re.sub(r'<ins>(.*?)</ins>', r'⟦+\1+⟧', b, flags=re.S)
        b = re.sub(r'<[^>]+>', '', b)
        b = H.unescape(b)
        b = re.sub(r'[ \t]+', ' ', b)
        outs.append(b.strip('\n'))
    return '\n'.join(outs)


mf_items = {}
for tr in re.findall(r'<tr class="item[^"]*"[^>]*>(.*?)</tr>', mf_html, re.S):
    mid = re.search(r'<div class="mfid">(MF-\d+)</div>', tr)
    if not mid:
        continue
    mid = mid.group(1)
    loc = re.search(r'<div class="loc">(.*?)</div>', tr)
    tds = re.findall(r'<td class="c[234]">(.*?)</td>', tr, re.S)
    why = re.search(r'<div class="why">(.*?)</div>', tr, re.S)
    hits = re.search(r'<div class="hits"[^>]*>(.*?)</div>', tr, re.S)
    mf_items[mid] = {
        "id": mid,
        "location": H.unescape(re.sub(r'<[^>]+>', '', loc.group(1))) if loc else "",
        "original": cell_to_marked(tds[0]) if len(tds) > 0 else "",
        "revised": cell_to_marked(tds[1]) if len(tds) > 1 else "",
        "explanation": (H.unescape(re.sub(r'<[^>]+>', '', why.group(1)).strip()) if why else ""),
        "hits": (H.unescape(re.sub(r'<[^>]+>', '', hits.group(1)).strip()) if hits else ""),
    }

assert len(mf_items) == 48, f"MF 解析 {len(mf_items)} 条，期望 48"

# ---------- 存活 MF 条目（双席对齐汇总 2026-09-12 定案） ----------
LIVE = ["MF-02", "MF-06", "MF-09", "MF-12", "MF-13", "MF-14", "MF-15",
        "MF-17", "MF-22", "MF-33", "MF-40", "MF-41", "MF-45", "MF-46"]

# 执行注记（来自双席对齐汇总，写进说明）
AUDIT_NOTES = {
    "MF-02": "双席注：build_html.py 渲染不受影响，属防换渲染器的零成本加固。",
    "MF-06": "双席一致成立、认可。",
    "MF-09": "双席一致：『见第 5 章』合书内章级前引惯例。",
    "MF-12": "双席一致：与 ch10 L61 同口径。",
    "MF-13": "双席一致：与 L256『预读大小可调』相容。",
    "MF-14": "双席一致（awk 全扫核实全书仅此 5 条图注缺句号、4 处缺空行）。",
    "MF-15": "双席执行警告：三处同批次落地（ch5 L45 + ch1 L64 + ch10 L110，与 MF-45 连动），勿漏。",
    "MF-17": "双席一致：与图 6-1 图注『前三层各一段＋审计旁路』对齐。",
    "MF-22": "双席执行警告：只改 ch7 L59 这一处；ch7 L67 与 ch9 两处上午已修好，勿被旧清单带回旧措辞。",
    "MF-33": "双席一致：表 10-1 实为 9 行；B 席建议范围写法用『第 2–9 章』。",
    "MF-40": "双席一致：现稿最晚时间戳 [2026-09-09]，改 9 月自洽；若付印再拖按实月定。",
    "MF-41": "双席一致：可循 L61『这一论断的理论源头』同手法。",
    "MF-45": "双席一致：一词改『写』；与 MF-15 三处同批。",
    "MF-46": "双席一致：『四段』对应前文四环节可通，求稳可作『四个环节』。",
}

# MF-22：三块引文中两块（ch7 L67、ch9）上午已修好，只保留存活的 L59 块
mf22 = mf_items["MF-22"]
live_blocks = [b for b in mf22["original"].split("\n") if "⟦" in b and "从节点恢复" in b]
if len(live_blocks) == 1:
    key = live_blocks[0]
    mf22["original"] = key
    mf22["revised"] = next(r for r in mf22["revised"].split("\n") if "从节点恢复" in r)
    mf22["location"] = "ch7 L59（另两处上午已修，勿动）"

mf_live = []
for mid in LIVE:
    it = mf_items[mid]
    it["src"] = ["0910/glm"]
    note = AUDIT_NOTES.get(mid, "")
    if note:
        it["explanation"] = it["explanation"].rstrip('。') + "。" + note if it["explanation"].endswith('。') else (it["explanation"] + "。" + note)
    mf_live.append(it)

# MF-43 年份残点（上午修订已改对作者班子，年份落 2021；调度联网定案 2022）
mf_live.append({
    "id": "MF-43Y", "src": ["0910/glm", "mustfix-audit"],
    "location": "参考文献 L76（[38]，chapters/11-references.md）",
    "original": "[38] Botros S, Tinley J. High Performance MySQL[M]. 4th ed. Sebastopol: O'Reilly Media, ⟦-2021-⟧ —— MySQL 性能与架构优化的实战参考，适合深化 MySQL 理解。",
    "revised": "[38] Botros S, Tinley J. High Performance MySQL[M]. 4th ed. Sebastopol: O'Reilly Media, ⟦+2022+⟧ —— MySQL 性能与架构优化的实战参考，适合深化 MySQL 理解。",
    "explanation": "MF-43 落地残点：上午修订已把作者班子改对（Schwartz 等→Botros/Tinley），年份落 2021。双席分歧经调度联网裁明：第 4 版 2022 年出版（豆瓣书页 2022-1-8、ISBN 9781492080442；A 席引 O'Reilly 书页 2022-03、ISBN 9781492080510）。",
    "hits": "双席分歧→已裁明",
})

# ---------- glm5 38 项 ----------
g5 = json.loads((ROOT / "0910/glm5/必改对照-rows.json").read_text(encoding="utf-8"))["rows"]
g5 = {r["id"]: {**r, "src": ["0910/glm5"]} for r in g5}
assert len(g5) == 38

# 合并 MF-39→W08、MF-10→V11
mf39 = mf_items["MF-39"]
g5["W08"]["src"].append("0910/glm")
g5["W08"]["explanation"] += " ‖ MF-39（另一清单同句）改法为 A/B 二选一：A=保留所有权利表述；B=即本行写法（CC 授权限定为 Gitee 仓库版本、正式版以出版合同为准）。两席前审均判：属出版决策，作者/法务拍板；3 席若一致认可本行写法则按本行执行。"
mf10 = mf_items["MF-10"]
g5["V11"]["src"].append("0910/glm")
g5["V11"]["explanation"] += " ‖ MF-10（另一清单同表）独立诊断同病（同列双量纲混排），其改法较轻；本行重组方案更完整且经 A 席数值换算核实站得住，以本行为准。"

# ---------- 章分组 ----------
CHAPTERS = [
    ("第 1 章 · 引言", ["V12a", "V12b", "V06a", "V06b", "T2", "MF-02"]),
    ("第 2 章 · 数据结构与协议", ["V04a"]),
    ("第 3 章 · 生命周期管理", ["V09a", "V09b", "V09c", "V09d", "MF-06"]),
    ("第 4 章 · 内存与磁盘", ["V14", "V11", "V04b", "V04c", "V02a", "V10", "MF-09", "MF-12", "MF-13", "MF-14"]),
    ("第 5 章 · 分层架构设计", ["V08", "MF-15"]),
    ("第 6 章 · 安全机制", ["V03", "MF-17", "MF-46"]),
    ("第 7 章 · 集群架构", ["V01a", "V01b", "V01c", "V18a", "V18b", "V17", "T1+N11", "V15a", "MF-22"]),
    ("第 8 章 · 磁盘存储格式", ["V07", "V19", "V05", "W07"]),
    ("第 9 章 · 数据同步机制", ["V01d", "V01e", "V02b", "V15b", "V20", "T2b"]),
    ("第 10 章 · 总结", ["W05", "MF-33", "MF-45"]),
    ("后记", ["W08", "MF-40"]),
    ("参考文献", ["MF-41", "MF-43Y"]),
]

by_id = {**g5, **{m["id"]: m for m in mf_live}}
expected = {i for _, ids in CHAPTERS for i in ids}
got = set(by_id)
assert got == expected, f"聚合与分组不符：{got ^ expected}"

rows = []
for chap, ids in CHAPTERS:
    for rid in ids:
        r = by_id[rid]
        rows.append({"id": rid, "chapter": chap, "src": r["src"], "location": r["location"],
                     "original": r["original"], "revised": r["revised"], "explanation": r["explanation"]})

OUT.write_text(json.dumps({"rows": rows, "chapters": [c for c, _ in CHAPTERS]},
                          ensure_ascii=False, indent=2), encoding="utf-8")
print(f"OK {OUT}  rows={len(rows)}  (glm5=38, glm存活=14+1年份, 合并2处)")
# 抽验 3 条标记转换
for rid in ["MF-06", "MF-22", "MF-46"]:
    r = by_id[rid]
    print(f"--- {rid} @{r['location']}")
    print("  原:", r["original"][:80].replace("\n", "⏎"))
    print("  改:", r["revised"][:80].replace("\n", "⏎"))
