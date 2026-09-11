# -*- coding: utf-8 -*-
"""聚类 104 份读者挑错报告 → stats.html（共识仪表板）。
规则：同章 + 行号差≤3 + (意见 bigram Jaccard≥0.16 或 containment≥0.30 或 交集≥22)
主题簇（跨章/跨行人工标注）单独吸收成员。
"""
import json, io, os, re

DIR = os.path.dirname(os.path.abspath(__file__))
D = json.load(io.open(os.path.join(DIR, "_reports.json"), encoding="utf-8"))
FT = json.load(io.open(os.path.join(DIR, "_fulltext.json"), encoding="utf-8"))
CHAPTERS = D["chapters"]; CH_LABEL = D["ch_label"]; PERSPECTIVES = D["perspectives"]
REPORTS = D["reports"]

# ---------------- 行数据 ----------------
rows = []
for r in REPORTS:
    for row in r["rows"]:
        rows.append({
            "vid": r["vid"], "file": r["file"], "chapter": r["chapter"],
            "chLabel": r["chapter_label"], "perspective": r["perspective"],
            "num": row["num"], "pos": row["pos_raw"], "line": row["line"] or 0,
            "lines": row["lines"] or [], "quote": row["quote"],
            "opinion": row["opinion"], "type": row["type"],
        })
for i, r in enumerate(rows):
    r["id"] = i

# ---------------- 相似度 ----------------
STOP_BI = set()
for tok in """这句 这样 这种 这些 一般 一个 之一 上下 作者 举例 建议改 建议改为 读者 读到 读出 读来 读三遍 应该 归纳 改为 改成 改进 措辞 描述 表述 说法 口吻 口径 句子 句法 句式 后文 后面 因为 因此 图注 图片 处理 复杂 如果 完全 实际 对照 常见 平常 应用 开头 引用 引入 悬空 情境 意思 感觉 承诺 括号 括注 指代 提出 改写 方式 方法 早已 时间 晚于 没有 没说 没讲 没给 本书 本行 本条 正文 母语 汉语 注意 深入 满句 漏字 灵活 版本 环境 现成 语境 语境 读完 读书 知道 短句 硬伤 示例 直接 相关 相同 真实 真正 硬要 确定 确实 类似 统一 结论 绝对 细节 结构 编辑 组合 经典 缺了 缺少 缺失 考虑 虽然 落点 要求 语句 说法 说清 责任 资深 起来 足够 较为 过头 过于 运行 进一步 逐字 长句 逗号 通常 逻辑 误读 语言 账面 赘余 资料 距离 连读 连续 选型 适合 部件 里面 阅读附 难懂 集中 需求 非常 顺序 预期 验证 高频 默认 默读""".split():
    if len(tok) >= 2:
        for k in range(len(tok) - 1):
            STOP_BI.add(tok[k:k+2])

def norm(s):
    return re.sub(r"[`\*·—–…、，。；：''\"\"()\[\]（）<>《》/\s\|　]", "", s)

def cjk_bi(s):
    s = norm(s)
    return set(s[i:i+2] for i in range(len(s) - 1))

def latin_tok(s):
    return set(t.lower() for t in re.findall(r"[A-Za-z_][A-Za-z0-9_.\-]{2,}", s))

_cache = {}
def sigs(i):
    if i in _cache: return _cache[i]
    r = rows[i]
    b = set(x for x in cjk_bi(r["opinion"]) if x not in STOP_BI)
    l = latin_tok(r["opinion"])
    q = norm(r["quote"])[:60]
    qb = set(q[k:k+2] for k in range(len(q) - 1))
    _cache[i] = (b, l, qb)
    return _cache[i]

def related(i, j):
    ab, al, aq = sigs(i); bb, bl, bq = sigs(j)
    uni = ab | bb
    j_jac = len(ab & bb) / len(uni) if uni else 0
    inter = len(ab & bb) + len(al & bl)
    denom = max(1, min(len(ab) + len(al), len(bb) + len(bl)))
    cont = inter / denom
    q_jac = len(aq & bq) / len(aq | bq) if (aq | bq) else 0
    return j_jac >= 0.16 or cont >= 0.30 or (q_jac >= 0.50 and len(ab & bb) >= 18)

# ---------------- 位置聚类（union-find） ----------------
parent = list(range(len(rows)))
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]; x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[ra] = rb

bych = {}
for i, r in enumerate(rows):
    bych.setdefault(r["chapter"], []).append(i)
for ch, idxs in bych.items():
    idxs.sort(key=lambda i: rows[i]["line"])
    for a in range(len(idxs)):
        for b in range(a + 1, len(idxs)):
            ia, ib = idxs[a], idxs[b]
            if rows[ib]["line"] - rows[ia]["line"] > 3: break
            if rows[ia]["vid"] == rows[ib]["vid"] and False: pass
            if related(ia, ib): union(ia, ib)

groups = {}
for i in range(len(rows)):
    groups.setdefault(find(i), []).append(i)

# ---------------- 主题簇（人工标注，核对种子） ----------------
def row_by(vid, num):
    for i, r in enumerate(rows):
        if r["vid"] == vid and r["num"] == num: return i
    raise KeyError("V%03d#%d not found" % (vid, num))

THEMES = [
  {"name": "半同步 ACK 是否等 relay log 落盘（判错 vs 判对 3:3）", "conflict": True, "pin": True,
   "members": [(59,2),(64,6)],
   "opposite": [
     {"vid": 63, "excerpt": "V063（ch7 论断质疑·前言）已核实后主动撤回候选质疑：L119 半同步“写入 relay log 并落盘”与 MySQL 官方文档（§19.4.10 Semisynchronous Replication）口径一致，不报。"},
     {"vid": 75, "excerpt": "V075（ch9 命令实操·附注）L155 “副本 I/O 线程把事件写入 relay log 并落盘后即回 ACK”——官方手册原文即 “written to its relay log and flushed to disk”，“落盘”二字不过强。"},
   ],
   "note": "上午轮 R02 判书稿错、R03 判书稿对——夜轮 2:2 + 上午 1:1 = 3:3 平局，头号待作者裁决冲突。同句另涉 ch9 L155。"},
  {"name": "“acks=all 就不丢”缺 min.insync.replicas 前提（ch7 L172 + ch10 表 10-2）", "pin": False,
   "members": [(58,6),(59,4),(63,2),(82,4),(83,2),(87,7)],
   "note": "min.insync.replicas 默认 1，ISR 缩到 1 时 acks=all 退化为 acks=1；ch7 正文句与 ch10 表 10-2 RPO 行同源。"},
  {"name": "“全书九章 / 八个主题”口径矛盾（后记 L3、L31 + ch10 L5）", "pin": False,
   "members": [(89,1),(95,1),(96,3),(92,1),(94,4),(81,1),(88,1)],
   "note": "后记 L3“九章走完”/L31“全书九章”与全书十章结构矛盾；ch10 L5“前九章、八个主题”同一口径问题。"},
  {"name": "Cluster Linking 不是 Apache Kafka 官方组件（ch10）", "pin": False,
   "members": [(82,5),(83,3),(87,8)],
   "note": "MirrorMaker 2 为官方（KIP-382），Cluster Linking 是 Confluent 商业特性。"},
  {"name": "Redis 7.0 起无盘复制为默认（ch7 L57 + ch9 L69）", "pin": False,
   "members": [(59,1),(74,1)],
   "note": "repl-diskless-sync 7.0 起默认 yes，全量同步不落主节点盘。跨章两处表述同源。"},
  {"name": "zstd 压缩比“2–6 倍”无出处（ch2 L124 + ch8）", "pin": False,
   "members": [(23,4),(71,3)],
   "note": "公开基准数据不收敛于该区间，且无出处标注。"},
  {"name": "run_id 全书未定义 / 与 PSYNC2 replid 角色混淆（ch9）", "pin": False,
   "members": [(73,4),(75,1)],
   "note": "run_id 从未定义；PSYNC2 下 ? 表示 replid 而非 run_id，书中沿用老概念。"},
  {"name": "半角直引号 vs 弯引号：全书体例路线之争（序言 + ch4）", "pin": False, "style_route": True,
   "members": [(4,1),(36,13)],
   "note": "全书 chapter.md 弯引号为 0、直引号数百处——是“统一直引号”还是“按 GB/T 15834 改弯引号”的体例路线选择，非单点错字。"},
]

# 人工核实注记（挂在位置簇上）
VERIFY_NOTES = [
  {"chapter": "ch2", "line": 94, "vid": 18,
   "excerpt": "V018/V019（ch2 技术事实/命令实操）核实记录：AHI“5.7.8 起拆成 8 个分区”版本号无误（innodb_adaptive_hash_index_parts，5.7.8 引入），未计为问题。"},
  {"chapter": "ch10", "line": 41, "vid": 87,
   "excerpt": "上午轮 R02 亦报此条（偏移量可重放重算，因果不成立）。"},
  {"chapter": "ch10", "line": 74, "vid": 88,
   "excerpt": "上午轮 R07 关联：ch10“强一致调参数”与 ch7 MGR“调不了参数只能选协议”表述矛盾，建议两处对齐。"},
  {"chapter": "ch1", "line": 76, "vid": 10,
   "excerpt": "上午轮另有读者关联此问题（Read View 快照时机 RR-only）。"},
]

# 吸收主题成员
theme_of_row = {}
for t in THEMES:
    t["_rows"] = []
    for vid, num in t["members"]:
        i = row_by(vid, num)
        theme_of_row[i] = t
        t["_rows"].append(i)

# ---------------- 簇构建 ----------------
def auto_verifications(cluster_rows):
    """扫描同章其他报告的非表格文本：L{line} + 核实为正确关键词。
    只有一行里 L 引用 ≤3 个的"聚焦核实"才计为反向判断（枚举式长清单仅作参考注记）。"""
    chapters = {rows[i]["chapter"] for i in cluster_rows}
    lines = set()
    for i in cluster_rows:
        lines.add(rows[i]["line"])
        for L in rows[i]["lines"][:4]:
            lines.add(L)
    member_vids = {rows[i]["vid"] for i in cluster_rows}
    KEY = re.compile(r"正确|无误|不报|不挑|未计|撤回|口径一致|不构成|不过强|不必改|可保留")
    LREF = re.compile(r"L\s*\d+")
    out = []
    for ch in chapters:
        for rep in REPORTS:
            if rep["chapter"] != ch or rep["vid"] in member_vids: continue
            text = FT.get(rep["file"], "")
            for ln in text.splitlines():
                if ln.startswith("|"): continue
                nrefs = len(LREF.findall(ln))
                for L in lines:
                    if L <= 0: continue
                    if re.search(r"L\s*%d\b" % L, ln) and KEY.search(ln):
                        excerpt = ln.strip()
                        if len(excerpt) > 220: excerpt = excerpt[:220] + "…"
                        strong = nrefs <= 3 and len(excerpt) < 400
                        item = {"vid": rep["vid"], "perspective": rep["perspective"],
                                "chapter": ch, "strong": strong,
                                "excerpt": "V%03d（%s·文内核实记录）%s" % (rep["vid"], rep["perspective"], excerpt)}
                        if item not in out: out.append(item)
    return out[:6]

clusters = []
used = set()
for t in THEMES:
    rws = t["_rows"]
    # 吸收与主题成员同位置簇、行号 ±1 且语义相关的行（同句的第三方读者）
    absorb = set(rws)
    for i in rws:
        for j in groups[find(i)]:
            if j in absorb: continue
            if rows[j]["chapter"] == rows[i]["chapter"] and rows[i]["line"] and rows[j]["line"] \
               and abs(rows[j]["line"] - rows[i]["line"]) <= 1 and (related(i, j) or any(related(j, k) for k in rws if k != i)):
                absorb.add(j)
    rws = sorted(absorb)
    used.update(rws)
    clusters.append({"kind": "theme", "name": t["name"], "rows": rws,
                     "conflict": bool(t.get("conflict")), "style_route": bool(t.get("style_route")),
                     "opposite": t.get("opposite", []), "note": t.get("note", ""), "pin": t.get("pin", False)})

for root, idxs in groups.items():
    rws = [i for i in idxs if i not in used]
    if not rws: continue
    clusters.append({"kind": "pos", "name": "", "rows": sorted(rws), "conflict": False,
                     "opposite": [], "note": "", "pin": False})

# 簇元数据
for c in clusters:
    rws = c["rows"]
    vids = sorted({rows[i]["vid"] for i in rws})
    locs = {}
    for i in rws:
        locs.setdefault(rows[i]["chapter"], set()).add(rows[i]["line"])
    c.setdefault("oppositeHint", False)
    c["readers"] = ["V%03d" % v for v in vids]
    c["readerVids"] = vids
    c["nReaders"] = len(vids)
    c["locs"] = [{"chapter": ch, "lines": sorted(ls)} for ch, ls in sorted(locs.items(), key=lambda kv: CHAPTERS.index(kv[0]))]
    c["types"] = {}
    for i in rws:
        tp = rows[i]["type"][:10] or "未标"
        c["types"][tp] = c["types"].get(tp, 0) + 1
    best = max(rws, key=lambda i: len(rows[i]["opinion"]))
    c["summary"] = rows[best]["opinion"][:110]
    c["quoteShort"] = rows[best]["quote"][:70]
    # 冲突/核实注记：自动扫描仅作"旁证参考"注记；裁决级冲突以人工标注为准
    if c["kind"] == "pos":
        for vn in VERIFY_NOTES:
            hit = any(rows[i]["chapter"] == vn["chapter"] and abs(rows[i]["line"] - vn["line"]) <= 2 for i in rws)
            if hit:
                c.setdefault("verifyNotes", []).append(vn["excerpt"])
        av = auto_verifications(rws)
        if av:
            c.setdefault("verifyNotes", [])
            for a in av: c["verifyNotes"].append(a["excerpt"])
            if any(a["strong"] for a in av):
                c["oppositeHint"] = True

clusters.sort(key=lambda c: (-c["nReaders"], -len(c["rows"]), CHAPTERS.index(c["locs"][0]["chapter"]), c["locs"][0]["lines"][0]))

n_total = len(clusters)
n_cons = sum(1 for c in clusters if c["nReaders"] >= 2)
n_strong = sum(1 for c in clusters if c["nReaders"] >= 3)
n_conflict = sum(1 for c in clusters if c["conflict"])
n_hint = sum(1 for c in clusters if c.get("oppositeHint") and not c["conflict"])

# ---------------- 统计矩阵 ----------------
type_dist = {}
for r in rows:
    t = r["type"][:10] or "未标"
    type_dist[t] = type_dist.get(t, 0) + 1
ch_dist = {}
for r in rows:
    ch_dist[r["chapter"]] = ch_dist.get(r["chapter"], 0) + 1
heat = [[0] * len(PERSPECTIVES) for _ in CHAPTERS]
for r in rows:
    heat[CHAPTERS.index(r["chapter"])][PERSPECTIVES.index(r["perspective"])] += 1

files_appendix = [{"file": r["file"], "vid": r["vid"], "chapter": r["chapter_label"],
                   "perspective": r["perspective"], "count": len(r["rows"])} for r in sorted(REPORTS, key=lambda r: r["vid"])]

DATA = {
    "chapters": CHAPTERS, "chLabel": CH_LABEL, "perspectives": PERSPECTIVES,
    "rows": rows, "clusters": clusters,
    "typeDist": type_dist, "chDist": ch_dist, "heat": heat,
    "files": files_appendix,
    "stats": {"readers": 104, "totalOpinions": len(rows), "clusters": n_total,
              "consensus": n_cons, "strong": n_strong, "conflicts": n_conflict, "hints": n_hint},
}
data_str = json.dumps(DATA, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

# ---------------- HTML ----------------
HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>通宵 104 读者挑错轮 · 共识仪表板</title>
<style>
:root{
  --bg:#f6f7f9; --card:#ffffff; --ink:#1c2330; --sub:#5b6472; --line:#e3e6eb;
  --accent:#2456d6; --accent-soft:#e8eefc; --gold:#b98413; --gold-bg:#fdf6e3; --gold-line:#e6c56a;
  --warn:#b3372f; --warn-bg:#fdf0ee; --ok:#2e7d43; --ok-bg:#eef7f0; --mono:'Consolas','Courier New',monospace;
}
*{box-sizing:border-box; margin:0; padding:0;}
body{background:var(--bg); color:var(--ink); font:14px/1.65 "Microsoft YaHei","PingFang SC",system-ui,sans-serif; padding:20px 18px 60px;}
.wrap{max-width:1180px; margin:0 auto;}
h1{font-size:22px; margin:6px 0 4px;}
h2{font-size:17px; margin:34px 0 12px; padding-bottom:6px; border-bottom:2px solid var(--line);}
h2 .cnt{color:var(--sub); font-weight:normal; font-size:13px; margin-left:8px;}
.sub{color:var(--sub); font-size:13px; margin-bottom:14px;}
/* 卡片 */
.cards{display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px;}
.card{background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px 16px;}
.card .num{font-size:26px; font-weight:700; color:var(--accent);}
.card.warn .num{color:var(--warn);}
.card.gold .num{color:var(--gold);}
.card .lab{font-size:13px; color:var(--sub); margin-top:2px;}
/* 图表区 */
.grid2{display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:12px;}
@media(max-width:900px){.grid2{grid-template-columns:1fr;}}
.panel{background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px 16px;}
.panel h3{font-size:14px; margin-bottom:10px; color:var(--ink);}
.bar-row{display:flex; align-items:center; gap:8px; margin:4px 0; font-size:13px;}
.bar-row .bl{width:120px; text-align:right; color:var(--sub); flex:none; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; cursor:pointer;}
.bar-row .bl:hover{color:var(--accent);}
.bar-row .tr{flex:1; background:#eef0f4; border-radius:4px; height:16px; position:relative;}
.bar-row .fl{position:absolute; left:0; top:0; bottom:0; background:var(--accent); border-radius:4px; min-width:2px; cursor:pointer;}
.bar-row .v{width:34px; flex:none; color:var(--sub); font-size:12px;}
/* 热力图 */
.heatwrap{overflow-x:auto;}
table.heat{border-collapse:collapse; font-size:12px;}
table.heat th{font-weight:600; color:var(--sub); padding:3px 6px; text-align:center; white-space:nowrap;}
table.heat th.rot{writing-mode:vertical-lr; text-orientation:upright; letter-spacing:1px; padding:4px 2px;}
table.heat td{border:1px solid #fff; padding:0; }
table.heat td button{width:100%; min-width:46px; height:30px; border:none; font-size:12px; color:var(--ink); cursor:pointer; background:transparent;}
table.heat td.zero button{color:#c3c8d0; cursor:default;}
.hlegend{font-size:12px; color:var(--sub); margin-top:8px;}
/* 筛选 */
.filters{display:flex; flex-wrap:wrap; gap:10px; align-items:center; background:var(--card); border:1px solid var(--line); border-radius:10px; padding:10px 14px; margin:14px 0; position:sticky; top:0; z-index:40; box-shadow:0 2px 8px rgba(20,30,50,.06);}
.filters label{font-size:13px; color:var(--sub);}
.filters select{font:13px inherit; padding:4px 8px; border:1px solid var(--line); border-radius:6px; background:#fff; color:var(--ink);}
.filters .clear{cursor:pointer; color:var(--accent); font-size:13px; border:none; background:none;}
.filters .res{margin-left:auto; font-size:13px; color:var(--sub);}
/* 簇列表 */
.cluster{background:var(--card); border:1px solid var(--line); border-radius:10px; margin:10px 0; overflow:hidden;}
.cluster.strong{border:1.5px solid var(--gold-line); box-shadow:0 0 0 3px var(--gold-bg);}
.cluster.conflict{border:1.5px solid #e2b3ae;}
.cluster .head{padding:10px 14px; cursor:pointer; display:flex; gap:10px; align-items:flex-start;}
.cluster .head:hover{background:#fafbfd;}
.badge{flex:none; font-size:13px; font-weight:700; color:#fff; background:var(--accent); border-radius:14px; padding:1px 10px; margin-top:2px; white-space:nowrap;}
.badge.strong{background:var(--gold);}
.badge.solo{background:#9aa3b0;}
.badge.conflict{background:var(--warn);}
.cluster .body-h{flex:1; min-width:0;}
.c-title{font-size:14px; font-weight:600;}
.c-loc{font-size:13px; color:var(--accent); font-family:var(--mono); margin:1px 0 3px;}
.c-sum{font-size:13px; color:var(--ink);}
.c-meta{font-size:12.5px; color:var(--sub); margin-top:3px; display:flex; flex-wrap:wrap; gap:6px; align-items:center;}
.tag{display:inline-block; background:#eef0f4; border-radius:4px; padding:0 7px; font-size:12px; color:var(--sub);}
.tag.gold{background:var(--gold-bg); color:var(--gold); border:1px solid var(--gold-line);}
.tag.warn{background:var(--warn-bg); color:var(--warn);}
.c-arrow{flex:none; color:var(--sub); font-size:12px; margin-top:4px;}
.cluster .detail{display:none; border-top:1px solid var(--line); padding:10px 16px 14px; background:#fbfcfe;}
.cluster.open .detail{display:block;}
.op{border-left:3px solid var(--accent-soft); padding:8px 12px; margin:8px 0; background:#fff; border-radius:0 8px 8px 0; border-top:1px solid var(--line); border-right:1px solid var(--line); border-bottom:1px solid var(--line);}
.op .who{font-size:13px; font-weight:700; margin-bottom:4px;}
.op .who .pv{color:var(--sub); font-weight:normal;}
.op .quote{font-size:13px; background:#f4f6fa; border-radius:6px; padding:6px 10px; margin:6px 0; color:#333; font-family:inherit; white-space:pre-wrap; word-break:break-word;}
.op .opinion{font-size:13.5px; white-space:pre-wrap; word-break:break-word; color:var(--ink);}
.op .tp{color:var(--sub); font-size:12px; margin-top:4px;}
.note{background:var(--gold-bg); border:1px solid var(--gold-line); border-radius:8px; padding:8px 12px; font-size:13px; margin:8px 0; color:#6b5310;}
.oppside{background:var(--ok-bg); border:1px solid #bcd9c3; border-radius:8px; padding:8px 12px; font-size:13px; margin:8px 0; color:#274; white-space:pre-wrap; word-break:break-word;}
.vernote{background:#f2f4f8; border:1px solid var(--line); border-radius:8px; padding:8px 12px; font-size:13px; margin:8px 0; color:var(--sub); white-space:pre-wrap; word-break:break-word;}
/* 冲突区 */
.conflict-card{background:var(--warn-bg); border:1.5px solid #e2b3ae; border-radius:10px; margin:12px 0; padding:14px 16px;}
.conflict-card h4{font-size:15px; color:var(--warn); margin-bottom:6px;}
.need{display:inline-block; background:var(--warn); color:#fff; font-size:12px; border-radius:4px; padding:1px 8px; margin-left:8px; vertical-align:middle;}
.cols2{display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:10px;}
@media(max-width:820px){.cols2{grid-template-columns:1fr;}}
.side{background:#fff; border:1px solid var(--line); border-radius:8px; padding:10px 12px;}
.side h5{font-size:13px; margin-bottom:6px;}
.side.err h5{color:var(--warn);}
.side.ok h5{color:var(--ok);}
.side .op{margin:6px 0;}
/* 单读者区 */
details.solo-ch{background:var(--card); border:1px solid var(--line); border-radius:10px; margin:8px 0; padding:0 14px;}
details.solo-ch summary{cursor:pointer; padding:9px 0; font-size:14px; font-weight:600; list-style:none; display:flex; align-items:center; gap:8px;}
details.solo-ch summary::-webkit-details-marker{display:none;}
details.solo-ch summary .n{color:var(--sub); font-weight:normal; font-size:13px;}
/* 附录 */
table.appx{border-collapse:collapse; width:100%; background:var(--card); border:1px solid var(--line); border-radius:10px; overflow:hidden; font-size:13px;}
table.appx th, table.appx td{padding:6px 10px; border-bottom:1px solid var(--line); text-align:left;}
table.appx th{background:#f0f2f6; color:var(--sub); font-weight:600;}
table.appx tr:last-child td{border-bottom:none;}
.mono{font-family:var(--mono); font-size:12.5px;}
.foot{color:var(--sub); font-size:12.5px; margin-top:26px; text-align:center;}
mark{background:var(--accent-soft); color:var(--accent); padding:0 2px; border-radius:3px;}
</style>
</head>
<body>
<div class="wrap">
  <h1>《架构观察笔记》通宵 104 读者挑错轮 · 共识仪表板</h1>
  <div class="sub">13 文件 × 8 视角 = 104 份独立报告 · 聚类口径：同章 + 行号差 ≤3 + 意见语义相关；跨章主题簇为人工核对后合并。点击簇行展开全部意见原文；≥3 位读者命中 = <b style="color:var(--gold)">强共识</b>。</div>

  <div class="cards" id="cards"></div>

  <h2>分布概览</h2>
  <div class="grid2">
    <div class="panel"><h3>类型分布（点击过滤）</h3><div id="typedist"></div></div>
    <div class="panel"><h3>章分布（点击过滤）</h3><div id="chdist"></div></div>
  </div>
  <div class="panel" style="margin-top:12px"><h3>视角 × 章热力矩阵（数字 = 意见条数，点击格子按 章+视角 过滤）</h3>
    <div class="heatwrap"><table class="heat" id="heatmap"></table></div>
    <div class="hlegend">色深随意见数递增：0 → 1–4 → 5–9 → 10–14 → 15+</div>
  </div>

  <h2>冲突裁决区 <span class="cnt" id="confCnt"></span></h2>
  <div class="sub">同一处有读者判"书稿错"、另有读者核实判"书稿对"——这些簇不要直接改稿，先裁决口径。</div>
  <div id="conflictZone"></div>

  <h2>共识排行榜 <span class="cnt" id="rankCnt"></span></h2>
  <div class="filters" id="filters">
    <label>章 <select id="fCh"><option value="">全部</option></select></label>
    <label>类型 <select id="fType"><option value="">全部</option></select></label>
    <label>视角 <select id="fPv"><option value="">全部</option></select></label>
    <label>共识 <select id="fLv">
      <option value="">全部</option><option value="2">≥2 读者</option><option value="3">强共识 ≥3</option><option value="solo">仅单读者</option>
    </select></label>
    <button class="clear" id="fClear">清除筛选</button>
    <span class="res" id="fRes"></span>
  </div>
  <div id="rankList"></div>

  <h2>单读者意见（按章折叠） <span class="cnt" id="soloCnt"></span></h2>
  <div class="sub">仅 1 位读者命中、且未被其他读者交叉印证的意见。价值在于补盲，不在共识。</div>
  <div id="soloZone"></div>

  <h2>附录：104 份报告清单 <span class="cnt" id="appxCnt"></span></h2>
  <table class="appx" id="appx"></table>

  <div class="foot" id="foot"></div>
</div>

<script type="application/json" id="DATA">__DATA__</script>
<script>
var D = JSON.parse(document.getElementById('DATA').textContent);
var ROWS = D.rows, CL = D.clusters, ST = D.stats;
var CHL = D.chLabel, PVS = D.perspectives;
var chName = function(c){ return CHL[c] || c; };
var esc = function(s){ return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); };

/* ---------- 顶部卡片 ---------- */
(function(){
  var cards = [
    ['读者', ST.readers, '份独立报告（V001–V104）', ''],
    ['总意见', ST.totalOpinions, '条挑错意见（表格行）', ''],
    ['聚类后问题簇', ST.clusters, '个（位置 + 主题）', ''],
    ['共识簇', ST.consensus, '个 · ≥2 位读者命中', ''],
    ['强共识簇', ST.strong, '个 · ≥3 位读者命中', 'gold'],
    ['冲突簇', ST.conflicts, '个 · 判断相反待裁决', 'warn'],
  ];
  document.getElementById('cards').innerHTML = cards.map(function(c){
    return '<div class="card ' + c[3] + '"><div class="num">' + c[1] + '</div><div class="lab"><b>' + c[0] + '</b> · ' + c[2] + '</div></div>';
  }).join('');
})();

/* ---------- 分布条形 ---------- */
function bars(el, dist, filterKey, maxLab){
  var arr = Object.keys(dist).map(function(k){ return [k, dist[k]]; });
  arr.sort(function(a,b){ return b[1]-a[1]; });
  var max = Math.max.apply(null, arr.map(function(a){ return a[1]; }));
  document.getElementById(el).innerHTML = arr.map(function(a){
    var lab = a[0].length > maxLab ? a[0].slice(0, maxLab) + '…' : a[0];
    var w = Math.round(a[1] / max * 100);
    return '<div class="bar-row"><span class="bl" title="' + esc(a[0]) + '" data-fk="' + esc(a[0]) + '">' + esc(filterKey === 'ch' ? chName(a[0]) : a[0]) + '</span>'
      + '<span class="tr"><span class="fl" style="width:' + w + '%" data-fk="' + esc(a[0]) + '"></span></span>'
      + '<span class="v">' + a[1] + '</span></div>';
  }).join('');
  Array.prototype.forEach.call(document.querySelectorAll('#' + el + ' [data-fk]'), function(elm){
    elm.onclick = function(){
      if (filterKey === 'ch') { document.getElementById('fCh').value = elm.getAttribute('data-fk'); }
      else { document.getElementById('fType').value = elm.getAttribute('data-fk'); }
      applyFilters(); window.scrollTo({top: document.getElementById('rankList').offsetTop - 120, behavior: 'smooth'});
    };
  });
}
bars('typedist', D.typeDist, 'type', 8);
bars('chdist', D.chDist, 'ch', 8);

/* ---------- 热力矩阵 ---------- */
(function(){
  var heat = D.heat, max = 1;
  heat.forEach(function(r){ r.forEach(function(v){ if (v > max) max = v; }); });
  function color(v){
    if (!v) return 'transparent';
    var t = v / max;
    if (v >= 15) return '#1d3f9e';
    if (v >= 10) return '#3f63c9';
    if (v >= 5) return '#7f9ade';
    return '#c3d1f0';
  }
  function fg(v){ return v >= 10 ? '#fff' : '#1c2330'; }
  var h = '<tr><th></th>' + D.chapters.map(function(c){ return '<th class="rot">' + esc(chName(c)) + '</th>'; }).join('') + '</tr>';
  PVS.forEach(function(p, pi){
    h += '<tr><th style="text-align:right">' + esc(p) + '</th>';
    D.chapters.forEach(function(c, ci){
      var v = heat[ci][pi];
      h += '<td class="' + (v ? '' : 'zero') + '"><button data-ch="' + esc(c) + '" data-pv="' + esc(p) + '" style="background:' + color(v) + ';color:' + fg(v) + '">' + (v || '·') + '</button></td>';
    });
    h += '</tr>';
  });
  document.getElementById('heatmap').innerHTML = h;
  Array.prototype.forEach.call(document.querySelectorAll('#heatmap button'), function(b){
    b.onclick = function(){
      var ch = b.getAttribute('data-ch'), pv = b.getAttribute('data-pv');
      document.getElementById('fCh').value = ch; document.getElementById('fPv').value = pv;
      applyFilters(); window.scrollTo({top: document.getElementById('rankList').offsetTop - 120, behavior: 'smooth'});
    };
  });
})();

/* ---------- 簇渲染 ---------- */
function locText(c){
  return c.locs.map(function(l){ return chName(l.chapter) + ' L' + l.lines.join('/'); }).join(' ＋ ');
}
function clusterHTML(c, idx){
  var strong = c.nReaders >= 3;
  var cls = 'cluster' + (strong ? ' strong' : '') + (c.conflict ? ' conflict' : '');
  var tags = Object.keys(c.types).map(function(t){ return '<span class="tag">' + esc(t) + '×' + c.types[t] + '</span>'; }).join('');
  if (strong) tags = '<span class="tag gold">强共识</span>' + tags;
  if (c.conflict) tags = '<span class="tag warn">有反向判断 · 待裁决</span>' + tags;
  if (c.kind === 'theme') tags = '<span class="tag" style="background:#eef7f0;color:#2e7d43">跨位置主题簇</span>' + tags;
  if (c.style_route) tags = '<span class="tag" style="background:#f0eefb;color:#5b46b8">体例路线之争</span>' + tags;
  var h = '<div class="' + cls + '" data-idx="' + idx + '">'
    + '<div class="head" onclick="var el=this.parentNode;el.classList.toggle(\'open\');">'
    + '<span class="badge ' + (c.nReaders >= 3 ? 'strong' : (c.nReaders === 1 ? 'solo' : '')) + (c.conflict ? ' conflict' : '') + '">' + c.nReaders + ' 位读者</span>'
    + '<div class="body-h"><div class="c-title">' + (c.kind === 'theme' ? esc(c.name) : esc(c.quoteShort)) + '</div>'
    + '<div class="c-loc">' + esc(locText(c)) + (c.kind === 'theme' ? '' : ' · ' + c.rows.length + ' 条意见') + '</div>'
    + '<div class="c-sum">' + esc(c.summary) + '</div>'
    + '<div class="c-meta">' + tags + '<span>' + c.readers.join(' · ') + '</span></div></div>'
    + '<span class="c-arrow">展开 ▾</span></div>'
    + '<div class="detail">';
  if (c.kind === 'theme') h += '<div class="note"><b>主题簇说明：</b>' + esc(c.note || '') + '</div>';
  c.rows.slice().sort(function(a, b){ return ROWS[a].vid - ROWS[b].vid; }).forEach(function(ri){
    var r = ROWS[ri];
    h += '<div class="op"><div class="who">V' + String(r.vid).padStart(3, '0') + ' <span class="pv">· ' + esc(r.perspective) + '视角 · #' + r.num + ' · ' + esc(r.pos) + '</span></div>'
      + '<div class="quote">原文：' + esc(r.quote) + '</div>'
      + '<div class="opinion">' + esc(r.opinion) + '</div>'
      + '<div class="tp">类型：' + esc(r.type) + '</div></div>';
  });
  if (c.conflict && c.opposite && c.opposite.length) {
    h += c.opposite.map(function(o){ return '<div class="oppside"><b>✓ 判“书稿正确”的一方：</b>' + esc(o.excerpt) + '</div>'; }).join('');
  }
  if (c.verifyNotes && c.verifyNotes.length) {
    h += c.verifyNotes.map(function(v){ return '<div class="vernote">🔎 ' + esc(v) + '</div>'; }).join('');
  }
  h += '</div></div>';
  return h;
}

/* ---------- 排行榜 + 筛选 ---------- */
var F = { ch: '', type: '', pv: '', lv: '' };
function passCluster(c){
  var chHit = !F.ch || c.locs.some(function(l){ return l.chapter === F.ch; });
  var pvHit = !F.pv || c.rows.some(function(ri){ return ROWS[ri].perspective === F.pv; });
  var tpHit = !F.type || c.rows.some(function(ri){ return (ROWS[ri].type || '').indexOf(F.type) >= 0; });
  var lvHit = true;
  if (F.lv === '2') lvHit = c.nReaders >= 2;
  else if (F.lv === '3') lvHit = c.nReaders >= 3;
  else if (F.lv === 'solo') lvHit = c.nReaders === 1;
  return chHit && pvHit && tpHit && lvHit;
}
function applyFilters(){
  F.ch = document.getElementById('fCh').value;
  F.type = document.getElementById('fType').value;
  F.pv = document.getElementById('fPv').value;
  F.lv = document.getElementById('fLv').value;
  renderRank();
  renderSolo();
}
function renderRank(){
  var list = CL.filter(function(c, i){ return passCluster(c) && c.nReaders >= 2; });
  document.getElementById('rankCnt').textContent = '（当前 ' + list.length + ' / 共识簇 ' + ST.consensus + '）';
  document.getElementById('rankList').innerHTML = list.map(function(c){
    var i = CL.indexOf(c);
    return clusterHTML(c, i);
  }).join('') || '<div class="sub">无匹配簇。</div>';
}
function renderSolo(){
  var byCh = {};
  CL.forEach(function(c){
    if (c.nReaders !== 1 || !passCluster(c)) return;
    var ch = c.locs[0].chapter;
    (byCh[ch] = byCh[ch] || []).push(c);
  });
  var chs = Object.keys(byCh).sort(function(a, b){ return D.chapters.indexOf(a) - D.chapters.indexOf(b); });
  var total = 0; chs.forEach(function(ch){ total += byCh[ch].length; });
  document.getElementById('soloCnt').textContent = '（当前 ' + total + ' 个单读者簇）';
  document.getElementById('soloZone').innerHTML = chs.map(function(ch){
    return '<details class="solo-ch"><summary>' + esc(chName(ch)) + ' <span class="n">— ' + byCh[ch].length + ' 条单读者意见（点击展开）</span></summary>'
      + byCh[ch].map(function(c){ return clusterHTML(c, CL.indexOf(c)); }).join('')
      + '</details>';
  }).join('') || '<div class="sub">无匹配。</div>';
}

/* ---------- 冲突裁决区 ---------- */
(function(){
  var conf = CL.filter(function(c){ return c.conflict; });
  var hints = CL.filter(function(c){ return !c.conflict && c.oppositeHint; });
  document.getElementById('confCnt').textContent = '（裁决级 ' + conf.length + ' 个，另有 ' + hints.length + ' 个旁证待核）';
  var html = conf.map(function(c){
    var i = CL.indexOf(c);
    var h = '<div class="conflict-card"><h4>' + (c.kind === 'theme' ? esc(c.name) : esc(c.quoteShort)) + '<span class="need">需作者裁决</span></h4>'
      + '<div class="c-loc mono" style="font-size:13px">' + esc(locText(c)) + '</div>';
    if (c.kind === 'theme' && c.note) h += '<div class="note">' + esc(c.note) + '</div>';
    h += '<div class="cols2"><div class="side err"><h5>✗ 判“书稿错”（' + c.nReaders + ' 位读者）</h5>';
    c.rows.forEach(function(ri){
      var r = ROWS[ri];
      h += '<div class="op"><div class="who">V' + String(r.vid).padStart(3, '0') + ' <span class="pv">· ' + esc(r.perspective) + '</span></div>'
        + '<div class="opinion">' + esc(r.opinion.length > 700 ? r.opinion.slice(0, 700) + '…' : r.opinion) + '</div></div>';
    });
    h += '</div><div class="side ok"><h5>✓ 判“书稿对 / 核实无误”</h5>';
    if (c.opposite && c.opposite.length) {
      c.opposite.forEach(function(o){ h += '<div class="op"><div class="opinion">' + esc(o.excerpt) + '</div></div>'; });
    }
    if (c.verifyNotes && c.verifyNotes.length) {
      c.verifyNotes.forEach(function(v){ h += '<div class="op"><div class="opinion">' + esc(v) + '</div></div>'; });
    }
    if (!(c.opposite && c.opposite.length) && !(c.verifyNotes && c.verifyNotes.length)) {
      h += '<div class="op"><div class="opinion">（该簇的反向判断来自文内核实记录，见下方完整簇详情）</div></div>';
    }
    h += '</div></div>';
    h += '<div style="margin-top:8px"><button onclick="jumpCluster(' + i + ')" style="font:13px inherit;padding:4px 12px;border:1px solid var(--accent);color:var(--accent);background:#fff;border-radius:6px;cursor:pointer">在排行榜中查看全部意见 ↗</button></div>';
    h += '</div>';
    return h;
  }).join('');
  if (hints.length) {
    html += '<details class="solo-ch" style="background:#fffbeb;border-color:#e6c56a"><summary style="color:#8a6d1a">🔎 另有 ' + hints.length + ' 个簇存在“核实为正确”旁证（多为同句不同侧面，改前先核对）<span class="n">点击展开</span></summary>';
    hints.forEach(function(c){
      var i = CL.indexOf(c);
      html += '<div style="padding:8px 0;border-top:1px solid var(--line)"><b>' + c.nReaders + ' 位读者</b> · ' + esc(locText(c)) + ' · ' + esc(c.summary.slice(0, 70)) + '…<br>';
      (c.verifyNotes || []).forEach(function(v){ html += '<div class="vernote">' + esc(v) + '</div>'; });
      html += '<button onclick="jumpCluster(' + i + ')" style="font:12.5px inherit;padding:2px 10px;border:1px solid var(--accent);color:var(--accent);background:#fff;border-radius:6px;cursor:pointer;margin-top:4px">查看簇详情 ↗</button></div>';
    });
    html += '</details>';
  }
  document.getElementById('conflictZone').innerHTML = html || '<div class="sub">无冲突簇。</div>';
})();
function jumpCluster(i){
  var el = document.querySelector('.cluster[data-idx="' + i + '"] .head');
  if (!el) { document.getElementById('fLv').value = ''; F.lv = ''; renderRank(); el = document.querySelector('.cluster[data-idx="' + i + '"] .head'); }
  if (el) {
    el.scrollIntoView({behavior: 'smooth', block: 'center'});
    if (!el.parentNode.classList.contains('open')) el.click();
  }
}

/* ---------- 附录 ---------- */
(function(){
  var h = '<tr><th>报告</th><th>章</th><th>视角</th><th>意见数</th></tr>';
  D.files.forEach(function(f){
    h += '<tr><td class="mono">' + esc(f.file) + '</td><td>' + esc(f.chapter) + '</td><td>' + esc(f.perspective) + '</td><td>' + f.count + '</td></tr>';
  });
  document.getElementById('appx').innerHTML = h;
  document.getElementById('appxCnt').textContent = '（合计 ' + ST.totalOpinions + ' 条）';
  document.getElementById('foot').textContent = '聚类口径：同章 + 行号差≤3 + 意见语义相关（bigram Jaccard/containment）；跨章主题簇经人工核对种子合并。生成于 2026-09-11，源数据 _reports.json。';
})();

/* ---------- 初始化筛选器 ---------- */
(function(){
  var sel = document.getElementById('fCh');
  D.chapters.forEach(function(c){ var o = document.createElement('option'); o.value = c; o.textContent = chName(c); sel.appendChild(o); });
  sel = document.getElementById('fType');
  Object.keys(D.typeDist).sort(function(a,b){ return D.typeDist[b] - D.typeDist[a]; }).forEach(function(t){ var o = document.createElement('option'); o.value = t; o.textContent = t; sel.appendChild(o); });
  sel = document.getElementById('fPv');
  PVS.forEach(function(p){ var o = document.createElement('option'); o.value = p; o.textContent = p; sel.appendChild(o); });
  ['fCh','fType','fPv','fLv'].forEach(function(id){ document.getElementById(id).onchange = applyFilters; });
  document.getElementById('fClear').onclick = function(){
    ['fCh','fType','fPv','fLv'].forEach(function(id){ document.getElementById(id).value = ''; });
    applyFilters();
  };
  renderRank(); renderSolo();
})();
</script>
</body>
</html>
"""

html = HTML.replace("__DATA__", data_str)
out = os.path.join(DIR, "stats.html")
with io.open(out, "w", encoding="utf-8") as f:
    f.write(html)
print("clusters=%d consensus(>=2)=%d strong(>=3)=%d conflict=%d rows=%d" % (n_total, n_cons, n_strong, n_conflict, len(rows)))
print("size=%.0f KB" % (os.path.getsize(out) / 1024))
print("\n--- TOP consensus clusters ---")
for c in clusters[:18]:
    if c["nReaders"] < 2: break
    loc = " + ".join("%s L%s" % (CH_LABEL[l["chapter"]], "/".join(str(x) for x in l["lines"])) for l in c["locs"])
    print("%d readers | %s | %s | %s..." % (c["nReaders"], loc, (c["name"] or c["quoteShort"])[:40], c["summary"][:60]))
print("\n--- theme cluster member check ---")
for c in clusters:
    if c["kind"] != "theme": continue
    print("[theme] %s" % c["name"][:44])
    for i in c["rows"]:
        r = rows[i]
        print("   V%03d#%d L%s [%s] %s" % (r["vid"], r["num"], r["line"], r["type"], r["opinion"][:56]))
print("\n--- hint clusters (opposite verifications, neutral) ---")
for c in clusters:
    if c.get("oppositeHint") and not c["conflict"]:
        loc = " + ".join("%s L%s" % (CH_LABEL[l["chapter"]], "/".join(str(x) for x in l["lines"])) for l in c["locs"])
        print("V%s | %s | %s" % (",".join(c["readers"]), loc, c["summary"][:44]))
