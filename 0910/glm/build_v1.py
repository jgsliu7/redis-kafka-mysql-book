# -*- coding: utf-8 -*-
"""
build_v1.py — 把 10 份读者挑错报告（R01–R10）汇总成审阅用单文件 v1.html
仅标准库。用法：python build_v1.py
"""
import html
import json
import re
import sys
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE / "v1.html"
META = BASE / "meta.json"

# (编号, 人设名, 文件名, 预期条数)
REPORTS = [
    ("R01", "新人读者", "R01-新人读者.md", 16),
    ("R02", "资深架构师", "R02-资深架构师.md", 10),
    ("R03", "DBA运维", "R03-DBA运维.md", 10),
    ("R04", "技术图书编辑", "R04-技术图书编辑.md", 17),
    ("R05", "AI味猎手", "R05-AI味猎手.md", 18),
    ("R06", "语感挑剔者", "R06-语感挑剔者.md", 26),
    ("R07", "质疑论者", "R07-质疑论者.md", 14),
    ("R08", "跳读导航者", "R08-跳读导航者.md", 11),
    ("R09", "面试讲解者", "R09-面试讲解者.md", 14),
    ("R10", "对读读者", "R10-对读读者.md", 10),
]

# 章序：序言=0, ch1..ch10=1..10, 后记=11, 参考文献=12（ch11 即参考文献文件）
CH_ORDER = {"序言": 0, "后记": 11, "参考文献": 12}
CH_NAME = {0: "序言", 11: "后记", 12: "参考文献"}
for i in range(1, 11):
    CH_NAME[i] = "第 %d 章" % i

POS_RE = re.compile(r"^(序言|后记|参考文献|ch(\d+))\s*L(\d+)")

# 附录收录：排除纯计数小节（R10“汇总”仅条数；R05/R06/R08“统计”仅条数。
# R02“汇总”含连带修订提示、R04“统计”含薄弱章分析，保留）
APPENDIX_EXCLUDE = {
    ("R10-对读读者.md", "汇总"),
    ("R05-AI味猎手.md", "统计"),
    ("R06-语感挑剔者.md", "统计"),
    ("R08-跳读导航者.md", "统计"),
}

# 指令式建议（插入/补空行/统一为…），不做 diff，两列纯展示
NO_DIFF_PREFIX = (
    "[整句删除]",
    "（在",
    "（将",
    "（导读原文不动",
    "统一为",
    "图注行与下一行",
    "ch9 处改为",
    "序言改为",
    "L5 改为",
    "L57 ",
)

warnings = []
repairs = []


def warn(msg):
    warnings.append(msg)


def repair_row(parts, path, ln):
    """列数>8 时的边界重分列：parts[1]=编号、parts[2]=位置、parts[-2]=级别 均可锚定，
    中间各段重新组合成 原文/建议/分析 三列，取 原文↔建议 相似度最高的切分（多余 | 还原回单元格内）。"""
    try:
        num = int(parts[1].strip())
    except ValueError:
        warn("%s L%d: 修复失败，编号列非整数" % (path.name, ln))
        return None
    pos = parts[2].strip()
    if not POS_RE.match(pos):
        warn("%s L%d: 修复失败，位置列无法锚定：%r" % (path.name, ln, pos))
        return None
    level = parts[-2].strip().upper()
    if level not in ("P0", "P1", "P2"):
        warn("%s L%d: 修复失败，级别列无法锚定：%r" % (path.name, ln, parts[-2]))
        return None
    mid = parts[3:-2]
    best, best_score = None, -1.0
    for i in range(1, len(mid) - 1):
        for j in range(i + 1, len(mid)):
            orig, sug = "|".join(mid[:i]), "|".join(mid[i:j])
            score = SequenceMatcher(None, orig, sug).ratio()
            if score > best_score:
                best_score, best = score, (orig, sug, "|".join(mid[j:]))
    if best is None:
        warn("%s L%d: 修复失败，中段不足三列" % (path.name, ln))
        return None
    repairs.append("%s L%d（#%d，多余管道符重分列，原文↔建议相似度 %.2f）" % (path.name, ln, num, best_score))
    return [str(num), pos, best[0], best[1], best[2], level]


def esc(s):
    return html.escape(s, quote=False)


def ch_keys(pos):
    """位置串 -> (章序, 行号)。位置列格式：chN L数字 / 序言|后记|参考文献 L数字，后可带附注。"""
    m = POS_RE.match(pos.strip())
    if not m:
        warn("位置无法解析：%r" % pos)
        return (99, 0)
    if m.group(1) in CH_ORDER:
        ch = CH_ORDER[m.group(1)]
    else:
        n = int(m.group(2))
        ch = 12 if n == 11 else n
    return (ch, int(m.group(3)))


SEP_RE = re.compile(r"^\|[\s:\-\|]+\|?$")
HDR_RE = re.compile(r"^\|\s*#")


def parse_table(path, rid, expect):
    """解析报告表格行 -> list of dict(num, pos, orig, sug, why, level, file_line)"""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    rows = []
    in_table = False
    for ln, raw in enumerate(lines, 1):
        s = raw.strip()
        if not s.startswith("|"):
            if rows:  # 表格已结束
                break
            continue
        if HDR_RE.match(s):
            in_table = True
            continue
        if not in_table:
            continue
        if SEP_RE.match(s):
            continue
        tmp = s.replace("\\|", "\x00")
        parts = tmp.split("|")
        if len(parts) != 8:
            if len(parts) > 8:
                fixed = repair_row([p.replace("\x00", "|") for p in parts], path, ln)
                if fixed is None:
                    continue
                cells = fixed
            else:
                warn("%s L%d: 列数 %d ≠ 6，原始行：%s" % (path.name, ln, len(parts) - 2, s[:80]))
                continue
        else:
            cells = [p.replace("\x00", "|").strip() for p in parts[1:7]]
        try:
            num = int(cells[0])
        except ValueError:
            warn("%s L%d: 编号列非整数：%r" % (path.name, ln, cells[0]))
            continue
        level = cells[5].strip().upper()
        if level not in ("P0", "P1", "P2"):
            warn("%s L%d: 级别列异常：%r" % (path.name, ln, cells[5]))
            level = "P2"
        rows.append({
            "key": "%s-%d" % (rid, num),
            "num": num, "pos": cells[1], "orig": cells[2], "sug": cells[3],
            "why": cells[4], "level": level, "file_line": ln,
        })
    if len(rows) != expect:
        warn("%s: 解析条数 %d ≠ 预期 %d" % (path.name, len(rows), expect))
    nums = [r["num"] for r in rows]
    if nums != list(range(1, len(rows) + 1)):
        warn("%s: 条目编号不连续：%s" % (path.name, nums))
    return rows


def parse_appendix(path, fname):
    """收录表格之后（首个 ## 段若在表格前出现则取表格后内容）的 '## ' 二级节，返回 [(title, body)]"""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    # 找表格结束行（最后一个以 | 开头的行）
    last_pipe = max((i for i, l in enumerate(lines) if l.strip().startswith("|")), default=-1)
    secs, title, body = [], None, []
    for l in lines[last_pipe + 1:]:
        if l.startswith("## "):
            if title is not None:
                secs.append((title, "\n".join(body).strip()))
            title, body = l[3:].strip(), []
        elif title is not None:
            body.append(l)
    if title is not None:
        secs.append((title, "\n".join(body).strip()))
    return [(t, b) for (t, b) in secs if (fname, t) not in APPENDIX_EXCLUDE and b]


# ---------------- diff 渲染 ----------------
TOK_RE = re.compile(r"[\u3000-\u9fff\uff00-\uffef]|[^\u3000-\u9fff\uff00-\uffef]+")


def tokenize(t):
    return TOK_RE.findall(t)


def diff_pair(a, b):
    """返回 (orig_html, sug_html) 或 None（不宜 diff）。调用方保证已 HTML 转义前不插入标签。"""
    at, bt = tokenize(a), tokenize(b)
    if not at or not bt:
        return None
    sm = SequenceMatcher(None, at, bt, autojunk=False)
    if sm.ratio() < 0.3:
        return None
    orig, sug = [], []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            t = esc("".join(at[i1:i2]))
            orig.append(t)
            sug.append(t)
        elif tag == "delete":
            orig.append("<del>%s</del>" % esc("".join(at[i1:i2])))
        elif tag == "insert":
            sug.append("<ins>%s</ins>" % esc("".join(bt[j1:j2])))
        else:  # replace
            orig.append("<del>%s</del>" % esc("".join(at[i1:i2])))
            sug.append("<ins>%s</ins>" % esc("".join(bt[j1:j2])))
    return "".join(orig), "".join(sug)


DEL_ALL_RE = re.compile(r"^\[整句删除\]")


def render_sides(orig, sug):
    """(原文列html, 建议列html)"""
    if DEL_ALL_RE.match(sug):
        rest = sug[DEL_ALL_RE.match(sug).end():]
        return esc(orig), '<span class="delall">[整句删除]</span>' + esc(rest)
    if any(sug.startswith(p) for p in NO_DIFF_PREFIX):
        return esc(orig), esc(sug)
    d = diff_pair(orig, sug)
    if d is None:
        return esc(orig), esc(sug)
    return d


# ---------------- 主流程 ----------------
def main():
    meta = json.loads(META.read_text(encoding="utf-8"))

    entries = {}   # key -> entry dict
    appendix = []  # (rid, persona, title, body)

    for rid, persona, fname, expect in REPORTS:
        path = BASE / fname
        rows = parse_table(path, rid, expect)
        for r in rows:
            e = dict(r)
            e["readers"] = [rid]
            e["persona"] = {rid: persona}
            e["conflict"] = None
            entries[e["key"]] = e
        for title, body in parse_appendix(path, fname):
            appendix.append((rid, persona, title, body))

    rid_index = {rid: i for i, (rid, _, _, _) in enumerate(REPORTS)}
    persona_of = {rid: p for rid, p, _, _ in REPORTS}

    # ---- merge ----
    merged_count = 0
    for group in meta.get("merge", []):
        members = [entries[k] for k in group if k in entries]
        missing = [k for k in group if k not in entries]
        if missing:
            warn("merge 组缺成员：%s" % missing)
        if len(members) < 2:
            continue
        merged_count += 1
        primary, others = members[0], members[1:]
        lv = {"P0": 0, "P1": 1, "P2": 2}
        primary["level"] = min((m["level"] for m in members), key=lambda x: lv[x])
        whys = ["【%s】%s" % (primary["readers"][0], primary["why"])]
        for o in others:
            whys.append("【%s】%s" % (o["readers"][0], o["why"]))
        primary["why"] = "\n\n".join(whys)
        primary["readers"] = sorted({r for m in members for r in m["readers"]}, key=lambda x: rid_index[x])
        primary["merged"] = True
        for o in others:
            del entries[o["key"]]
    # merge 后唯一键重排（key 仍是 primary 的 Rxx-N）

    # ---- conflict ----
    conflict_groups = []
    for gi, group in enumerate(meta.get("conflict", []), 1):
        ids = []
        appendix_keys = []
        for k in group:
            if k in entries:
                ids.append(k)
            else:
                appendix_keys.append(k)  # 如 R03-附注-半同步
        for k in ids:
            entries[k]["conflict"] = gi
        conflict_groups.append({"gi": gi, "entry_keys": ids, "app_keys": appendix_keys, "raw": group})

    # ---- 排序 + 全局编号 ----
    def sort_key(e):
        ch, ln = ch_keys(e["pos"])
        r0 = min(rid_index[r] for r in e["readers"])
        return (ch, ln, r0, e["num"])

    lst = sorted(entries.values(), key=sort_key)
    for i, e in enumerate(lst, 1):
        e["gid"] = i

    # 冲突对方编号解析（条目侧注明附录侧；附录侧注明条目号）
    for cg in conflict_groups:
        cg["gids"] = [entries[k]["gid"] for k in cg["entry_keys"] if k in entries]

    # ---- 统计 ----
    n_total = len(lst)
    n_level = {l: sum(1 for e in lst if e["level"] == l) for l in ("P0", "P1", "P2")}
    per_reader = {rid: 0 for rid, _, _, _ in REPORTS}
    for e in lst:
        for r in e["readers"]:
            per_reader[r] += 1
    per_ch = {}
    for e in lst:
        ch = ch_keys(e["pos"])[0]
        per_ch[ch] = per_ch.get(ch, 0) + 1

    # ---- HTML ----
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    stat_badges = "".join(
        '<span class="badge b-%s">%s × %d</span>' % (l, l, n_level[l]) for l in ("P0", "P1", "P2")
    )
    reader_chips = "".join(
        '<span class="chip" data-rid="%s">%s %s × %d</span>' % (rid, rid, persona_of[rid], per_reader[rid])
        for rid, _, _, _ in REPORTS
    )

    nav_links = []
    sections = []
    for ch in range(0, 13):
        name = CH_NAME[ch]
        ch_entries = [e for e in lst if ch_keys(e["pos"])[0] == ch]
        if not ch_entries:
            continue
        anchor = "sec-%d" % ch
        nav_links.append('<a href="#%s" data-target="%s" id="nav-%d">%s<em>%d</em></a>' % (anchor, anchor, ch, name, len(ch_entries)))
        rows_html = []
        for e in ch_entries:
            orig_html, sug_html = render_sides(e["orig"], e["sug"])
            rtags = '<span class="rtag">%s</span>' % '</span><span class="rtag">'.join(e["readers"]) \
                if len(e["readers"]) == 1 else '<span class="rtag merged-tag" title="合并条目">%s</span>' % "+".join(e["readers"])
            why_html = esc(e["why"]).replace("\n\n", '<br><br>')
            extra = ""
            if e["conflict"]:
                # 冲突对方：同组其余条目 + 附录侧（如 R03-附注-半同步）
                cg = next(g for g in conflict_groups if g["gi"] == e["conflict"])
                others = []
                for gid, k in zip(cg["gids"], cg["entry_keys"]):
                    if k != e["key"]:
                        others.append("#%d（%s，%s）" % (gid, entries[k]["pos"], "+".join(entries[k]["readers"])))
                for ak in cg["app_keys"]:
                    others.append("附录·%s" % esc(ak))
                tip = "、".join(others) if others else "见附录"
                extra = '<div class="clash-note">⚠ 冲突：与 %s 判断相反</div>' % tip
                rows_html.append(
                    '<tr class="entry lvl-%s conflict" data-level="%s" data-readers="%s" data-gid="%d">'
                    % (e["level"], e["level"], ",".join(e["readers"]), e["gid"]))
            else:
                rows_html.append(
                    '<tr class="entry lvl-%s" data-level="%s" data-readers="%s" data-gid="%d">'
                    % (e["level"], e["level"], ",".join(e["readers"]), e["gid"]))
            rows_html.append(
                '<td class="c-id"><div class="gid">%d</div>'
                '<span class="badge b-%s">%s</span>'
                '<span class="clash" title="存在相反判断，见分析列与附录">⚠ 冲突</span>'
                '<div class="rtags">%s</div></td>'
                % (e["gid"], e["level"], e["level"], rtags))
            rows_html.append(
                '<td class="c-pos"><div class="pos">%s</div><div class="orig">%s</div></td>'
                % (esc(e["pos"]), orig_html))
            rows_html.append('<td class="c-sug">%s</td>' % sug_html)
            rows_html.append('<td class="c-why">%s%s</td>' % (why_html, extra))
            rows_html.append("</tr>")
        sections.append(
            '<section class="chapter" id="%s" data-ch="%d">'
            '<h2>%s <span class="ch-count">%d 条</span></h2>'
            '<table><thead><tr><th class="c-id">#</th><th class="c-pos">位置 · 原文（<del>红</del>=删除）</th>'
            '<th class="c-sug">建议改为（<ins>绿</ins>=新增）</th><th class="c-why">原因与分析</th></tr></thead>'
            '<tbody>%s</tbody></table></section>'
            % (anchor, ch, name, len(ch_entries), "".join(rows_html))
        )

    # 附录
    app_html = []
    for rid, persona, title, body in appendix:
        b = esc(body).replace("\n\n", "<br><br>")
        clash = ""
        for cg in conflict_groups:
            for ak in cg["app_keys"]:
                if ak.startswith(rid + "-附注"):
                    gids = "、".join("#%d（%s，%s）" % (g, entries[k]["pos"], "+".join(entries[k]["readers"]))
                                     for g, k in zip(cg["gids"], cg["entry_keys"]))
                    clash = ('<div class="clash-note">⚠ 冲突：本附注认为原书正确，与 %s（R02）判断相反。</div>' % gids)
        app_html.append(
            '<div class="app-item"><h3>%s · %s — %s</h3><p>%s</p>%s</div>'
            % (rid, persona, esc(title), b, clash))

    page = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>《架构观察笔记》读者挑错汇总 v1 · 审阅版</title>
<style>
:root{--ink:#1f2937;--mut:#6b7280;--line:#e5e7eb;--bg:#f8fafc;--card:#ffffff;
--p0:#dc2626;--p1:#d97706;--p2:#6b7280;--p0bg:#fef2f2;--p1bg:#fffbeb;--p2bg:#f3f4f6;}
*{box-sizing:border-box}
body{margin:0;font:14px/1.65 "Microsoft YaHei","PingFang SC",system-ui,sans-serif;color:var(--ink);background:var(--bg)}
header.top{padding:18px 20px 10px;background:var(--card);border-bottom:1px solid var(--line)}
h1{margin:0 0 10px;font-size:19px}
.statbar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:8px;font-size:13px;color:var(--mut)}
.badge{display:inline-block;padding:1px 8px;border-radius:10px;font-weight:600;font-size:12.5px}
.b-P0{background:var(--p0bg);color:var(--p0);border:1px solid #fecaca}
.b-P1{background:var(--p1bg);color:var(--p1);border:1px solid #fde68a}
.b-P2{background:var(--p2bg);color:var(--p2);border:1px solid var(--line)}
.chips{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px}
.chip{font-size:12.5px;background:var(--bg);border:1px solid var(--line);border-radius:4px;padding:1px 7px;color:var(--mut)}
.chip b{color:var(--ink);font-weight:600}
.filters{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-bottom:10px}
.filters button{font:inherit;font-size:13px;padding:3px 12px;border:1px solid var(--line);background:var(--card);border-radius:14px;cursor:pointer}
.filters button.on{background:#111827;color:#fff;border-color:#111827}
.filters select{font:inherit;font-size:13px;padding:3px 6px;border:1px solid var(--line);border-radius:6px;background:var(--card)}
#shown{font-size:13px;color:var(--mut);margin-left:4px}
nav.chnav{position:sticky;top:0;z-index:20;display:flex;flex-wrap:wrap;gap:2px;background:var(--card);border-top:1px solid var(--line);padding:6px 20px}
nav.chnav a{font-size:13px;color:var(--mut);text-decoration:none;padding:2px 9px;border-radius:12px}
nav.chnav a em{font-style:normal;font-size:11px;color:#9ca3af;margin-left:2px}
nav.chnav a.act{background:#111827;color:#fff}
nav.chnav a.act em{color:#d1d5db}
main{padding:14px 20px 40px;max-width:1500px}
section.chapter{background:var(--card);border:1px solid var(--line);border-radius:8px;margin-bottom:18px;padding:12px 14px}
section.chapter h2{margin:0 0 8px;font-size:16px}
.ch-count{font-size:12.5px;color:var(--mut);font-weight:400}
table{width:100%;border-collapse:collapse;table-layout:fixed}
th{font-size:12.5px;color:var(--mut);text-align:left;border-bottom:2px solid var(--line);padding:4px 8px;font-weight:600}
td{vertical-align:top;border-bottom:1px solid var(--line);padding:8px;font-size:13px;overflow-wrap:anywhere;word-break:break-word}
tr:last-child td{border-bottom:none}
td.c-id{width:74px;text-align:center}
.gid{font-size:21px;font-weight:700;line-height:1.2}
.rtags{margin-top:4px}
.rtag{display:inline-block;font-size:11.5px;color:#475569;background:#f1f5f9;border-radius:3px;padding:0 4px;margin:1px 0}
.rtag.merged-tag{background:#eef2ff;color:#4338ca;font-weight:600}
.pos{font:600 12.5px/1.4 Consolas,Menlo,monospace;color:#0f766e;background:#f0fdfa;border-radius:3px;display:inline-block;padding:0 5px;margin-bottom:5px}
.orig,.c-sug{white-space:pre-wrap}
del{color:#b91c1c;background:#fef2f2;text-decoration:line-through;padding:0 1px;border-radius:2px}
ins{color:#065f46;background:#dcfce7;text-decoration:none;padding:0 1px;border-radius:2px}
.delall{display:inline-block;background:#fee2e2;color:#b91c1c;border:1px solid #fecaca;border-radius:4px;padding:0 8px;font-weight:700}
tr.conflict td{background:#fff7f7}
tr.conflict td:first-child{border-left:4px solid var(--p0)}
.clash{display:none;font-size:11.5px;color:var(--p0);font-weight:600}
tr.conflict .clash{display:block;margin-top:3px}
.clash-note{margin-top:6px;font-size:12.5px;color:var(--p0);background:#fef2f2;border:1px dashed #fecaca;border-radius:4px;padding:3px 8px}
#appendix{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px 14px}
#appendix h2{margin:0 0 10px;font-size:16px}
.app-item{border-top:1px dashed var(--line);padding:8px 0}
.app-item:first-of-type{border-top:none}
.app-item h3{margin:0 0 4px;font-size:13.5px;color:#334155}
.app-item p{margin:0;font-size:13px;color:#475569;white-space:pre-wrap}
footer{padding:10px 20px 30px;color:#9ca3af;font-size:12.5px}
@media print{nav.chnav,.filters{display:none}}
</style>
</head>
<body>
<header class="top">
<h1>《架构观察笔记》读者挑错汇总 · 审阅版 v1</h1>
<div class="statbar">总条数（合并后）<b>__TOTAL__</b> 条${stat_badges}<span>冲突 ${conflict_groups|len} 组</span><span>合并 ${merged_count} 组</span><span>生成 ${now}</span></div>
<div class="chips">${reader_chips}</div>
<div class="filters">
<button data-lv="all" class="on">全部</button>
<button data-lv="P0">仅 P0</button>
<button data-lv="P1">仅 P1</button>
<button data-lv="P2">仅 P2</button>
<button data-lv="conflict">仅冲突</button>
<select id="sel-reader"><option value="all">全部读者</option>__OPTS__</select>
<span id="shown"></span>
</div>
<nav class="chnav">__NAV__</nav>
</header>
<main>
__SECTIONS__
<section id="appendix">
<h2>附录 · 各报告表格之外的附注原文（裁决参考）</h2>
__APP__
</section>
</main>
<footer>由 build_v1.py 生成于 ${now} · 数据源 R01–R10 共 10 份报告 · 合并 ${merged_count} 组 · 冲突 ${conflict_groups|len} 组</footer>
<script>
(function(){
var curLv='all',curRd='all';
var btns=document.querySelectorAll('.filters button');
btns.forEach(function(b){b.addEventListener('click',function(){
  btns.forEach(function(x){x.classList.remove('on')});b.classList.add('on');curLv=b.dataset.lv;apply();});});
var sel=document.getElementById('sel-reader');
sel.addEventListener('change',function(){curRd=sel.value;apply();});
function apply(){
  var shown=0,perSec={};
  document.querySelectorAll('tr.entry').forEach(function(tr){
    var okL=curLv==='all'||(curLv==='conflict'?tr.classList.contains('conflict'):tr.dataset.level===curLv);
    var rs=tr.dataset.readers.split(',');
    var okR=curRd==='all'||rs.indexOf(curRd)>=0;
    var vis=okL&&okR;
    tr.style.display=vis?'':'none';
    if(vis){shown++;var sec=tr.closest('section.chapter');if(sec){perSec[sec.id]=(perSec[sec.id]||0)+1;}}
  });
  document.querySelectorAll('section.chapter').forEach(function(sec){
    sec.style.display=perSec[sec.id]?'':'none';
    var em=sec.querySelector('h2 .ch-count');
    if(em){em.textContent=(perSec[sec.id]||0)+' / '+em.textContent.split('/ ').pop()+' 条';}
  });
  document.querySelectorAll('nav.chnav a').forEach(function(a){
    var t=a.dataset.target;var s=document.getElementById(t);
    a.style.display=(s&&s.style.display!=='none')?'':'none';
  });
  document.getElementById('shown').textContent='显示 '+shown+' / '+__TOTAL__+' 条';
}
var links=document.querySelectorAll('nav.chnav a');
var io=new IntersectionObserver(function(es){
  es.forEach(function(en){if(en.isIntersecting){
    links.forEach(function(a){a.classList.toggle('act',a.dataset.target===en.target.id);});}});
},{rootMargin:'-20% 0px -70% 0px'});
document.querySelectorAll('section.chapter').forEach(function(s){io.observe(s);});
apply();
})();
</script>
</body>
</html>
"""

    # 简单模板填充（避免 str.format 与 CSS 花括号冲突：先占位再替换）
    opts = "".join('<option value="%s">%s %s</option>' % (rid, rid, persona_of[rid]) for rid, _, _, _ in REPORTS)
    page = (page
            .replace("__TOTAL__", str(n_total))
            .replace("__OPTS__", opts)
            .replace("__NAV__", "".join(nav_links))
            .replace("__SECTIONS__", "".join(sections))
            .replace("__APP__", "".join(app_html))
            .replace("${stat_badges}", stat_badges)
            .replace("${reader_chips}", reader_chips)
            .replace("${now}", now))
    # python 表达式占位
    import string
    tpl = string.Template(page)
    page = tpl.safe_substitute(
        stat_badges=stat_badges, reader_chips=reader_chips, now=now,
        conflict_groups=conflict_groups, merged_count=merged_count)
    # safe_substitute 对 dict 取 len 不行，手动处理剩余
    page = page.replace("${conflict_groups|len}", str(len(conflict_groups)))

    OUT.write_text(page, encoding="utf-8")

    # ---- 输出统计 ----
    print("=" * 56)
    print("v1.html 生成完毕：%s（%.1f KB）" % (OUT, OUT.stat().st_size / 1024))
    print("总条数（合并后）：%d" % n_total)
    for l in ("P0", "P1", "P2"):
        print("  %s：%d" % (l, n_level[l]))
    print("merge 组：%d（%s）" % (merged_count, "；".join("+".join(g) for g in meta.get("merge", []))))
    print("conflict 组：%d（%s）" % (len(conflict_groups), "；".join("+".join(g["raw"]) for g in conflict_groups)))
    print("解析警告：%d" % len(warnings))
    for w in warnings:
        print("  ⚠ " + w)
    print("解析修复：%d 行" % len(repairs))
    for r in repairs:
        print("  ↻ " + r)
    print("每章分布：" + "，".join("%s %d" % (CH_NAME[c], per_ch[c]) for c in sorted(per_ch)))
    print("读者贡献：" + "，".join("%s×%d" % (rid, per_reader[rid]) for rid, _, _, _ in REPORTS))
    if warnings:
        sys.exit(1)


if __name__ == "__main__":
    main()
