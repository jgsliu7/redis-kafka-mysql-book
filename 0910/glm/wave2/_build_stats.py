# -*- coding: utf-8 -*-
"""wave2（50 位画像读者轮）→ stats.html：聚类 + 与 night100（104 位矩阵读者轮）跨轮共识对比。
口径：
- wave2 内部聚类：同章 + 行号差≤3 + 意见语义相关（bigram Jaccard≥0.16 / containment≥0.30 / 原文相似≥0.5 且交集≥18，沿用 night100）
- 主题簇（人工核对种子后合并，成员已逐条核对位置与语义）
- 跨轮匹配：wave2 行 vs night100 行，同章 + 行号差≤5 + 原文或意见相似；匹配上的 wave2 簇经共享夜轮簇合并为跨轮共识组
- 两枚人工跨轮 pin（意见文本互相印证但行号差>5）：消费者组缺位、从从叠字
"""
import io, os, re, json

DIR = os.path.dirname(os.path.abspath(__file__))
NIGHT = os.path.join(os.path.dirname(DIR), "night100")

# ================= 数据加载 =================
D = json.load(io.open(os.path.join(DIR, "_reports.json"), encoding="utf-8"))
CHAPTERS = D["chapters"]; CH_LABEL = D["ch_label"]; GROUPS = D["groups"]; REPORTS = D["reports"]

rows = []
for r in REPORTS:
    for row in r["rows"]:
        rows.append({"wid": r["wid"], "file": r["file"], "reader": r["reader"], "group": r["group"],
                     "num": row["num"], "pos": row["pos_raw"], "chapter": row["chapter"],
                     "line": row["line"] or 0, "lines": row["lines"] or [],
                     "quote": row["quote"], "opinion": row["opinion"], "type": row["type"],
                     "positive": bool(row.get("positive"))})
for i, r in enumerate(rows): r["id"] = i

# night100：从上轮 stats.html 提取最终簇数据（含人工主题簇与核实注记）
_html = io.open(os.path.join(NIGHT, "stats.html"), encoding="utf-8").read()
ND = json.loads(re.search(r'<script type="application/json" id="DATA">(.*?)</script>', _html, re.S).group(1))
NROWS = ND["rows"]; NCL = ND["clusters"]
nrow_cluster = {}
for ci, c in enumerate(NCL):
    for ri in c["rows"]: nrow_cluster[ri] = ci

# ================= 相似度（night100 口径） =================
STOP_BI = set()
for tok in """这句 这样 这种 这些 一般 一个 之一 上下 作者 举例 建议改 建议改为 读者 读到 读出 读来 读三遍 应该 归纳 改为 改成 改进 措辞 描述 表述 说法 口吻 口径 句子 句法 句式 后文 后面 因为 因此 图注 图片 处理 复杂 如果 完全 实际 对照 常见 平常 应用 开头 引用 引入 悬空 情境 意思 感觉 承诺 括号 括注 指代 提出 改写 方式 方法 早已 时间 晚于 没有 没说 没讲 没给 本书 本行 本条 正文 母语 汉语 注意 深入 满句 漏字 灵活 版本 环境 现成 语境 读完 读书 知道 短句 硬伤 示例 直接 相关 相同 真实 真正 硬要 确定 确实 类似 统一 结论 绝对 细节 结构 编辑 组合 经典 缺了 缺少 缺失 考虑 虽然 落点 要求 语句 说清 责任 资深 起来 足够 较为 过头 过于 运行 进一步 逐字 长句 逗号 通常 逻辑 误读 语言 账面 赘余 资料 距离 连读 连续 选型 适合 部件 里面 难懂 集中 需求 非常 顺序 预期 验证 高频 默认 默读""".split():
    if len(tok) >= 2:
        for k in range(len(tok) - 1): STOP_BI.add(tok[k:k+2])

def norm(s): return re.sub(r"[`\*·—–…、，。；：''\"\"()\[\]（）<>《》/\s\|　]", "", s)
def cjk_bi(s):
    s = norm(s); return set(s[i:i+2] for i in range(len(s) - 1))
def latin_tok(s): return set(t.lower() for t in re.findall(r"[A-Za-z_][A-Za-z0-9_.\-]{2,}", s))

_cache = {}
def sigs(key, opinion, quote):
    if key in _cache: return _cache[key]
    b = set(x for x in cjk_bi(opinion) if x not in STOP_BI)
    l = latin_tok(opinion)
    q = norm(quote)[:60]
    qb = set(q[k:k+2] for k in range(len(q) - 1))
    _cache[key] = (b, l, qb); return _cache[key]
def wsigs(i):
    r = rows[i]; return sigs(("w", i), r["opinion"], r["quote"])
def nsigs(j):
    r = NROWS[j]; return sigs(("n", j), r["opinion"], r["quote"])
def related_pair(a, b):
    ab, al, aq = a; bb, bl, bq = b
    uni = ab | bb
    j_jac = len(ab & bb) / len(uni) if uni else 0
    inter = len(ab & bb) + len(al & bl)
    denom = max(1, min(len(ab) + len(al), len(bb) + len(bl)))
    cont = inter / denom
    q_jac = len(aq & bq) / len(aq | bq) if (aq | bq) else 0
    return j_jac >= 0.16 or cont >= 0.30 or (q_jac >= 0.50 and len(ab & bb) >= 18)
def quote_jac(a, b):
    return len(a[2] & b[2]) / len(a[2] | b[2]) if (a[2] | b[2]) else 0
def related(i, j): return related_pair(wsigs(i), wsigs(j))

# ================= wave2 位置聚类（问题行） =================
prob_ids = {r["id"] for r in rows if not r["positive"]}
parent = {i: i for i in prob_ids}
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]; x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[ra] = rb
bych = {}
for i in prob_ids:
    bych.setdefault(rows[i]["chapter"], []).append(i)
for ch, idxs in bych.items():
    idxs.sort(key=lambda i: rows[i]["line"])
    for a in range(len(idxs)):
        for b in range(a + 1, len(idxs)):
            ia, ib = idxs[a], idxs[b]
            if rows[ib]["line"] - rows[ia]["line"] > 3: break
            if related(ia, ib): union(ia, ib)

# ================= 主题簇（人工核对种子后合并） =================
def row_by(wid, num):
    for i in prob_ids:
        if rows[i]["wid"] == wid and rows[i]["num"] == num: return i
    raise KeyError("W%02d#%d not found" % (wid, num))
def nrow_by(vid, num):
    for j, r in enumerate(NROWS):
        if r["vid"] == vid and r["num"] == num: return j
    raise KeyError("V%03d#%d not found" % (vid, num))

THEMES = [
  {"name": "acks=all 不等于不丢：缺 min.insync.replicas / unclean 选举前提", "pin": False,
   "members": [(2,1),(11,8),(25,5),(45,1),(9,2),(9,11),(29,6)],
   "note": "同源问题三处落点：ch7 L172 正文强断言、ch10 表 10-2 RPO 行、ch4 L312 副本机制兜底句——三处都在“ISR 非空就不丢”类表述上缺前提。"},
  {"name": "ch10 L74 强一致金句：调参数说法与 ch7 正文口径打架", "pin": False,
   "members": [(15,2),(47,1)],
   "note": "同句两侧面：W15 指其与 ch7 L174“MySQL 档位是集群级选择、调不了参数”正面矛盾；W47 指其把 fsync 档位与协议选择混成一根轴。"},
  {"name": "消费者组 / offset 机制全书缺位（GroupCoordinator、__consumer_offsets、rebalance 零介绍）", "pin": True,
   "members": [(2,5),(24,7),(41,2)],
   "note": "跨章主题：ch5 L163 GroupCoordinator 悬空、ch9 L262 “已提交 offset”凭空冒出、ch2 L156 JoinGroup/SyncGroup 无下文。与夜轮 V065#6（ch8 L177 __consumer_offsets 全书唯一一次出现）经人工核对为同主题（行号差>5，pin 合并）。"},
  {"name": "表 4-1 混量纲：延迟列填吞吐数字，倍数列口径断裂", "pin": False,
   "members": [(14,4),(15,10),(19,5),(22,5),(28,7),(39,4),(41,4),(43,5),(49,3),(33,2)],
   "note": "10 位读者 5 个角度（量纲、可念性、倍数口径、表格消费者、纯表格读者）命中同一张表。W33 引表题行 L19 与表体行 L26 差 7 行，人工并入。"},
  {"name": "版次与文献访问日期时间倒挂（后记 L61“2026 年 7 月第 1 版” vs refs 全部 [2026-08-14]）", "pin": False,
   "members": [(4,9),(47,7),(17,2)],
   "note": "7 月付印的书印不进 8 月的访问日期，二者必有一错。夜轮无命中——本轮新发现。"},
  {"name": "全书无习题：练习素材只集中在末章（ch10 L119-L121）", "pin": False,
   "members": [(42,1),(43,6),(44,3)],
   "note": "读书会领读 / 内训讲师 / 课程设计三类读者同报：前九章章末零讨论题、末章练习自带答案。夜轮无命中——本轮新发现。"},
  {"name": "ARIES 指涉不闭环（ch10 说“3.3 节展开”但 3.3 节无 ARIES 一词）", "pin": False,
   "members": [(31,3),(31,6),(34,7),(44,4)],
   "note": "ch3 L88 恢复两步 vs 参考文献[9]“三阶段”、ch8 L151 physiological logging 出身、ch10 L80 ARIES 首现零解释。"},
  {"name": "kill -9 / 信号关闭的丢数据口径（ch3 L7 vs 表 3-2 vs 3.4 节）", "pin": False,
   "members": [(7,3),(29,1),(50,3)],
   "note": "“通常只是丢掉最近一小段时间”与出厂默认配置矛盾；表 3-2 给 Redis“秒级可预测退出”与 3.4 节默认全量 RDB 落盘矛盾；kill -9 与丢 AOF 的因果在内核语义上不成立。"},
  {"name": "compaction 三译名不统一（压实 / 后台合并 / 在线 compaction）", "pin": False,
   "members": [(2,7),(18,13),(36,1)],
   "note": "与 ch1 L200 术语约定“中文已充分沉淀的继续用中文”自相矛盾；ch8 L50“后台合并”与 L87“在线 compaction”同章并存。"},
  {"name": "ch5 L44 io-threads 因果错位：“绝不放开逻辑层并发”解释不了“为什么默认关多线程 I/O”", "pin": False,
   "members": [(15,4),(50,6)],
   "note": "两位读者同一指认：前文那句话解释的是“命令执行为什么单线程”，而 io-threads 不碰命令执行，因果链断裂。夜轮 V041–V048 五位读者在同一句上密集命中（io-threads 默认只拆写回路径、论据机制后置等）——跨轮双重共识。"},
]

used = set()
clusters = []
for t in THEMES:
    rws = sorted(row_by(w, n) for w, n in t["members"])
    used.update(rws)
    clusters.append({"kind": "theme", "name": t["name"], "note": t["note"], "pinned": t["pin"], "rows": rws})
uf_groups = {}
for i in prob_ids: uf_groups.setdefault(find(i), []).append(i)
for root, idxs in uf_groups.items():
    rws = [i for i in idxs if i not in used]
    if rws:
        clusters.append({"kind": "pos", "name": "", "note": "", "pinned": False, "rows": sorted(rws)})
for cid, c in enumerate(clusters): c["id"] = cid
row_cluster = {}
for c in clusters:
    for i in c["rows"]: row_cluster[i] = c["id"]

# ================= 跨轮匹配 =================
# 仅认意见语义相关（沿用 night100 related 口径，quote 相似只作为 related_pair 的内部佐证）：
# 两轮报告常引同一段原文但报完全不同的问题（如 wave2 报技术、夜轮报体例），纯原文重叠=误配。
# 人工 pin 补足意见互相印证但行号差>5 / 措辞差异大的四组（均经逐条核对）。
PINS = [((24,7),(65,6)),   # 消费者组缺位 ↔ V065#6 __consumer_offsets 全书唯一一次出现
        ((18,4),(62,5)),   # “从从”叠字 ch7 L67 ↔ V062#5 ch7 L59（意见自述“同款问题 L67”）
        ((20,6),(64,1)),   # ch7 L7 导读排序矛盾 ↔ V064#1 ch7 L8（同一段、列举序 vs 强度序）
        ((15,2),(88,3))]   # ch10 L74 金句 ↔ V088#3 ch10 L74（调参数 vs 集群级选择，同一矛盾）
pairs = set()
_bychN = {}
for j, r in enumerate(NROWS):
    _bychN.setdefault(r["chapter"], []).append(j)
for i in prob_ids:
    ch = rows[i]["chapter"]; ln = rows[i]["line"]
    if not ch or ln <= 0: continue
    for j in _bychN.get(ch, []):
        if abs(NROWS[j]["line"] - ln) > 5: continue
        if related_pair(wsigs(i), nsigs(j)):
            pairs.add((row_cluster[i], nrow_cluster[j]))
pin_pairs = set()
for (w, wn), (v, vn) in PINS:
    p = (row_cluster[row_by(w, wn)], nrow_cluster[nrow_by(v, vn)])
    pairs.add(p); pin_pairs.add(p)
# 人工剔除的误配对（同行不同题）：W02#5（GroupCoordinator 悬空，ch5 L163）↔ V048（ch5 L163
# ReplicaManager 归类冲突）——同一行、英文组件名高度重叠导致 containment 误挂，实为两个问题。
_v48_row = next(j for j, r in enumerate(NROWS) if r["vid"] == 48 and r["line"] == 163)
EXCLUDE = {(row_cluster[row_by(2, 5)], nrow_cluster[_v48_row])}
pairs = {p for p in pairs if p not in EXCLUDE}

# 跨轮组 = 单个 wave2 簇 + 它匹配的全部夜轮簇（不做 wave2 簇间 union：
# 同段落不同问题的簇各自成组，簇间合并只由人工主题簇承担）
wc_to_ncs = {}
for wc, nc in pairs:
    wc_to_ncs.setdefault(wc, set()).add(nc)

XGROUPS = []
for wc, ncs in wc_to_ncs.items():
    wcs = [wc]; ncs = sorted(ncs)
    w_rows = sorted(clusters[wc]["rows"])
    n_rows = sorted({ri for nc in ncs for ri in NCL[nc]["rows"]})
    w_readers = sorted({rows[i]["wid"] for i in w_rows})
    n_readers = sorted({NROWS[j]["vid"] for j in n_rows})
    XGROUPS.append({"wcs": wcs, "ncs": ncs, "wRows": w_rows, "nRows": n_rows,
                    "wReaders": w_readers, "nReaders": n_readers,
                    "total": len(w_readers) + len(n_readers)})
XGROUPS.sort(key=lambda x: (-x["total"], -len(x["wRows"])))
xgroup_of_cluster = {}
for xi, xg in enumerate(XGROUPS):
    xg["xid"] = xi
    for wc in xg["wcs"]: xgroup_of_cluster[wc] = xi

# ================= 元数据 =================
def locs_of(row_ids, R):
    locs = {}
    for i in row_ids:
        if R[i].get("line", 0) > 0: locs.setdefault(R[i]["chapter"], set()).add(R[i]["line"])
    return [{"chapter": ch, "lines": sorted(ls)} for ch, ls in sorted(locs.items(), key=lambda kv: CHAPTERS.index(kv[0]) if kv[0] in CHAPTERS else 99)]

for c in clusters:
    rws = c["rows"]
    c["n"] = len({rows[i]["wid"] for i in rws})
    c["readers"] = sorted({rows[i]["wid"] for i in rws})
    c["locs"] = locs_of(rws, rows)
    c["types"] = {}
    for i in rws:
        tp = rows[i]["type"][:10] or "未标"
        c["types"][tp] = c["types"].get(tp, 0) + 1
    best = max(rws, key=lambda i: len(rows[i]["opinion"]))
    c["summary"] = rows[best]["opinion"][:140]
    c["quoteShort"] = rows[best]["quote"][:80]
    c["xgroup"] = xgroup_of_cluster.get(c["id"], -1)

for xg in XGROUPS:
    xg["kind"] = "theme" if any(clusters[wc]["kind"] == "theme" for wc in xg["wcs"]) else "pos"
    if xg["kind"] == "theme":
        xg["name"] = [clusters[wc]["name"] for wc in xg["wcs"] if clusters[wc]["kind"] == "theme"][0]
    else:
        best = max(xg["wRows"], key=lambda i: len(rows[i]["opinion"]))
        xg["name"] = rows[best]["quote"][:56]
    xg["locs"] = locs_of(xg["wRows"], rows)
    xg["nlocs"] = locs_of(xg["nRows"], NROWS)
    xg["summary"] = rows[max(xg["wRows"], key=lambda i: len(rows[i]["opinion"]))]["opinion"][:140]
    xg["pinned"] = any(clusters[wc].get("pinned") for wc in xg["wcs"]) or \
                   any(nc in {p[1] for p in pin_pairs} for nc in xg["ncs"])

# ================= 统计 =================
n_pos_rows = sum(1 for r in rows if r["positive"])
n_prob = len(prob_ids)
n_cons = sum(1 for c in clusters if c["n"] >= 2 and c["xgroup"] < 0)
n_solo = sum(1 for c in clusters if c["n"] == 1 and c["xgroup"] < 0)
n_new_found = [c["id"] for c in clusters if c["n"] >= 2 and c["xgroup"] < 0]

type_dist = {}
for i in prob_ids:
    t = rows[i]["type"][:10] or "未标"; type_dist[t] = type_dist.get(t, 0) + 1
ch_dist = {}
for i in prob_ids:
    ch_dist[rows[i]["chapter"]] = ch_dist.get(rows[i]["chapter"], 0) + 1

group_stats = []
for g in GROUPS:
    reps = [r for r in REPORTS if r["group"] == g]
    grews = [i for i in prob_ids if rows[i]["group"] == g]
    tds = {}
    for i in grews:
        t = rows[i]["type"][:10] or "未标"; tds[t] = tds.get(t, 0) + 1
    top_reader = max(reps, key=lambda r: sum(1 for x in r["rows"] if not x["positive"]))
    per_reader = sorted([(r["wid"], sum(1 for x in r["rows"] if not x["positive"])) for r in reps], key=lambda x: -x[1])
    # 组内命中共识（跨轮或轮内≥2）的条数
    cons_rows = sum(1 for i in grews if clusters[row_cluster[i]]["n"] >= 2 or clusters[row_cluster[i]]["xgroup"] >= 0)
    group_stats.append({"group": g, "readers": len(reps), "rows": len(grews),
                        "perCapita": round(len(grews) / len(reps), 1), "types": tds,
                        "topReader": "W%02d %s" % (top_reader["wid"], top_reader["reader"]),
                        "topReaderN": sum(1 for x in top_reader["rows"] if not x["positive"]),
                        "top3": ["W%02d(%d)" % (w, n) for w, n in per_reader[:3]],
                        "consRows": cons_rows})

# ================= 夜轮行嵌入（仅跨轮组引用的，意见截断 300 字） =================
nrows_embed = {}
for xg in XGROUPS:
    for j in xg["nRows"]:
        if j in nrows_embed: continue
        r = NROWS[j]
        op = r["opinion"]
        nrows_embed[j] = {"vid": "V%03d" % r["vid"], "perspective": r["perspective"],
                          "chapter": r["chapter"], "line": r["line"], "num": r["num"],
                          "quote": r["quote"][:90],
                          "opinion": op if len(op) <= 320 else op[:320] + "…（全文见上轮 stats.html）",
                          "type": r["type"]}

# ================= 正面资产 =================
positives_wave = [{"wid": "W%02d" % r["wid"], "reader": r["reader"], "group": r["group"],
                   "chapter": r["chapter"], "line": r["line"], "quote": r["quote"],
                   "opinion": r["opinion"], "type": r["type"]}
                  for r in rows if r["positive"]]
NIGHT_POS = [
  {"who": "V024 · ch2 讲解质量", "text": "本章图配比好（8 图覆盖全部复杂结构）、排行榜例子的开头-中段-小结三段闭环完整，讲解底盘扎实。"},
  {"who": "V056 · ch6 讲解质量", "text": "本章主线（四维模型 → 三家拆解 → 横向表 → 启示）清晰，图 6-1/6-3 配合到位，KRaft 循环依赖（L70）和 TLS 开销来源分析（L151）是讲得透的亮点。"},
  {"who": "V057 · ch7 新人可懂性", "text": "本章主线（分片与副本正交、一致性谱线、元数据两条路）对新人搭建心智模型是有力的，7.2.2 的“共识算法一分钟直觉”框和 7.3.4“MGR 不分片”写得很清楚。"},
  {"who": "V073 · ch9 新人可懂性", "text": "这章主线（四个子问题 → 状态机复制 → 三家各讲 → 横向对比）清楚，PSYNC2、GTID、leader epoch 三段是全书到目前为止讲得最透的部分，场景化写法（脑裂那段）新人能跟上。"},
  {"who": "V093 · 后记 AI味", "text": "后记的“一个真实的故事”一节细节最扎实（槽位、少数派分区、双 1、账只认 MySQL 都可指认），是全书契约保留项。"},
  {"who": "V021 · ch2 AI味", "text": "本章机制讲解主体（SDS/rehash/ziplist/RecordBatch/协议细节）锚点扎实、数字具体，AI 味不重。"},
]
WAVE_POS_EXTRA = [
  {"who": "W45 出题面试官 · 文末总评", "group": "写作同行",
   "text": "全书经得起追问的断言密度很高，例如 ch9 L107 对 min-replicas-max-lag“心跳时间不是字节差”的辨析、ch9 L214 对 consumer/replica FETCH 的 replica_id 区分、ch6 L50 指出 ACL 密码是无盐裸 SHA-256——这些若直接出成题，追问两层仍站得住，值得肯定。"},
  {"who": "W46 十年重读 · 文末总评", "group": "时间维度",
   "text": "值得保住的正面样板：8.2.2 的 RDB 版本号写法（逐版枚举+指向权威宏）、7.4.4 的 KRaft 编年史、表 4-1 顶部的免责声明、参考文献的访问日期——这些是十年后读者还能自救的地方，几条建议本质上是把这几处的做法推广过去。"},
]

# ================= 冲突区 =================
# 夜轮半同步 3:3 裁决级冲突的完整信息
semi_theme = None
for c in NCL:
    if c.get("kind") == "theme" and "半同步" in c.get("name", ""):
        semi_theme = c; break
semi_rows = [{"vid": "V%03d" % NROWS[i]["vid"], "perspective": NROWS[i]["perspective"],
              "chapter": NROWS[i]["chapter"], "line": NROWS[i]["line"], "quote": NROWS[i]["quote"][:90],
              "opinion": NROWS[i]["opinion"][:600], "type": NROWS[i]["type"]} for i in semi_theme["rows"]]
# 本轮观测维度证据（人工核对）
SEMI_W = []
for wid, num in [(3,9),(12,6),(5,1),(5,11),(12,5)]:
    i = row_by(wid, num); r = rows[i]
    SEMI_W.append({"wid": "W%02d" % r["wid"], "reader": r["reader"], "chapter": r["chapter"],
                   "line": r["line"], "opinion": r["opinion"], "type": r["type"], "quote": r["quote"][:90]})

conflicts = [{
    "title": "半同步 ACK 是否等 relay log 落盘：判错 vs 判对 3:3（夜轮裁决级，未决）",
    "nightName": semi_theme["name"],
    "note": semi_theme.get("note", ""),
    "nightErr": semi_rows,
    "nightOk": semi_theme.get("opposite", []),
    "waveEvidence": SEMI_W,
    "waveNote": "本轮无人直接重报 relay log 落盘之争，但三位读者从“可观测维度”补了新证据：半同步静默降级无变量名、无告警对象、超时参数（rpl_semi_sync_master_timeout）全书缺席——无论落盘口径怎么裁决，这个观测缺口都成立。",
}]

# ================= 自检 =================
check1 = sum(len(c["rows"]) for c in clusters) == n_prob
check2 = sum(1 for c in clusters for i in c["rows"]) == len(prob_ids)
dup = sum(len(c["rows"]) for c in clusters) - len({i for c in clusters for i in c["rows"]})
print("SELF-CHECK rows conservation: prob=%d clustered=%d dup=%d %s" % (
    n_prob, sum(len(c["rows"]) for c in clusters), dup, "OK" if check1 and dup == 0 else "FAIL"))
print("wave2: rows=%d (prob %d + positive %d) clusters=%d consensus-nowave=%d solo-nowave=%d xgroups=%d" % (
    len(rows), n_prob, n_pos_rows, len(clusters), n_cons, n_solo, len(XGROUPS)))

# 种子核对输出
SEEDCHECK = [
  ("acks=all", [(2,1)], [58,59,63,82,83,87]), ("ch10 L74", [(15,2)], [81,87,88]),
  ("Cluster Linking", [(4,1)], [82,83,87]), ("ch7 L8 导读", [(20,6)], [58,64]),
  ("MVCC ch1 L76", [(19,1)], [9,10,15,16]), ("消费者组", [(24,7)], [65]),
  ("表4-1", [(28,7)], []), ("Athens", [(11,11)], [97,98]), ("CC 授权", [(17,1)], []),
  ("访问日期", [(17,2)], []), ("无习题", [(42,1)], []), ("K8s", [(4,6)], [31]),
  ("从从", [(18,4)], [62]), ("compaction", [(18,13)], [65]), ("ARIES", [(44,4)], [81,82,87]),
  ("kill-9", [(50,3)], [26]),
]
print("\n--- seed cross-round check ---")
for name, wrefs, nvids in SEEDCHECK:
    wi = row_by(*wrefs[0]); wc = row_cluster[wi]; xg = clusters[wc]["xgroup"]
    if xg >= 0:
        g = XGROUPS[xg]
        gotN = sorted({"V%03d" % v for v in g["nReaders"]})
        print("[OK] %-16s xg#%-2d total=%-2d wave=%s night=%s" % (name, xg, g["total"],
              ",".join("W%02d" % w for w in g["wReaders"]), ",".join(gotN)))
    else:
        print("[--] %-16s wave-only (readers=%s)" % (name, clusters[wc]["readers"]))

print("\n--- TOP-12 xgroups ---")
for xg in XGROUPS[:12]:
    loc = " + ".join("%s L%s" % (l["chapter"], "/".join(str(x) for x in l["lines"][:6])) for l in xg["locs"])
    print("xg#%-2d total=%-2d (W%d+N%d) %-30s | %s" % (xg["xid"], xg["total"], len(xg["wReaders"]), len(xg["nReaders"]), loc, xg["name"][:36]))

# ================= 导出中间数据 + HTML =================
def ser_rows(ids):
    return [{"wid": rows[i]["wid"], "reader": rows[i]["reader"], "group": rows[i]["group"],
             "chapter": rows[i]["chapter"], "line": rows[i]["line"], "pos": rows[i]["pos"],
             "quote": rows[i]["quote"], "opinion": rows[i]["opinion"], "type": rows[i]["type"],
             "num": rows[i]["num"]} for i in ids]

DATA = {
    "chapters": CHAPTERS, "chLabel": CH_LABEL, "groups": GROUPS,
    "rows": [{"wid": r["wid"], "reader": r["reader"], "group": r["group"], "chapter": r["chapter"],
              "line": r["line"], "pos": r["pos"], "quote": r["quote"], "opinion": r["opinion"],
              "type": r["type"], "num": r["num"], "positive": r["positive"]} for r in rows],
    "clusters": [{"id": c["id"], "kind": c["kind"], "name": c["name"], "note": c["note"],
                  "rows": c["rows"], "n": c["n"], "readers": c["readers"], "locs": c["locs"],
                  "types": c["types"], "summary": c["summary"], "quoteShort": c["quoteShort"],
                  "xgroup": c["xgroup"]} for c in clusters],
    "xgroups": [{"xid": xg["xid"], "kind": xg["kind"], "name": xg["name"], "summary": xg["summary"],
                 "wcs": xg["wcs"], "ncs": xg["ncs"], "wRows": xg["wRows"], "nRows": xg["nRows"],
                 "wReaders": ["W%02d" % w for w in xg["wReaders"]],
                 "nReaders": ["V%03d" % v for v in xg["nReaders"]],
                 "total": xg["total"], "locs": xg["locs"], "nlocs": xg["nlocs"], "pinned": xg["pinned"]}
                for xg in XGROUPS],
    "nrows": nrows_embed,
    "typeDist": type_dist, "chDist": ch_dist, "groupStats": group_stats,
    "positives": {"wave": positives_wave, "nightParas": NIGHT_POS, "waveExtra": WAVE_POS_EXTRA},
    "conflicts": conflicts,
    "files": [{"file": r["file"], "wid": "W%02d" % r["wid"], "reader": r["reader"],
               "group": r["group"], "count": len(r["rows"])} for r in sorted(REPORTS, key=lambda r: r["wid"])],
    "nightFiles": ND["files"],
    "stats": {"waveReaders": 50, "waveRows": len(rows), "waveProb": n_prob, "wavePos": n_pos_rows,
              "clusters": len(clusters), "consensus": n_cons, "solo": n_solo,
              "xgroups": len(XGROUPS), "newFound": len(n_new_found),
              "nightReaders": 104, "nightRows": len(NROWS),
              "totalReaders": 154, "totalRows": len(rows) + len(NROWS)},
}

# ================= 导出 + HTML =================
with io.open(os.path.join(DIR, "_stats_data.json"), "w", encoding="utf-8") as f:
    json.dump(DATA, f, ensure_ascii=False, indent=1)

from _html_template import HTML
data_str = json.dumps(DATA, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
html = HTML.replace("__DATA__", data_str)
out = os.path.join(DIR, "stats.html")
with io.open(out, "w", encoding="utf-8") as f:
    f.write(html)
print("stats.html written: %.0f KB" % (os.path.getsize(out) / 1024))
print("data exported")

