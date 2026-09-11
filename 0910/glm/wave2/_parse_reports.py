# -*- coding: utf-8 -*-
"""解析 50 份 wave2 画像读者报告 → _reports.json。
格式：| # | 位置 | 原文 | 意见 | 类型 |；位置如 ch7 L123 / 序言 L5 / 后记 L12 / refs L76 / 尾声 L27。
处理 \| 转义管道；正面条目（意见以"正面基准/正面典型"等开头）单独标记。
"""
import io, os, re, json, glob

DIR = os.path.dirname(os.path.abspath(__file__))

CH_MAP = {"序言": "preface", "后记": "后记", "尾声": "后记", "refs": "参考文献",
          "参考文献": "参考文献", "preface": "preface"}
CHAPTERS = ["preface", "ch1", "ch2", "ch3", "ch4", "ch5", "ch6", "ch7", "ch8", "ch9", "ch10", "后记", "参考文献"]
CH_LABEL = {"preface": "序言", "ch1": "第1章", "ch2": "第2章", "ch3": "第3章", "ch4": "第4章",
            "ch5": "第5章", "ch6": "第6章", "ch7": "第7章", "ch8": "第8章", "ch9": "第9章",
            "ch10": "第10章", "后记": "后记", "参考文献": "参考文献"}

# 画像分组（7 组，共 50）
def group_of(wid):
    if 1 <= wid <= 10: return "职业纵深"
    if 11 <= wid <= 20: return "带任务读"
    if wid in (21, 22, 39, 49): return "特殊媒介"
    if 23 <= wid <= 31: return "技术对照"
    if 32 <= wid <= 38: return "特殊读法"
    if wid == 46: return "时间维度"
    if wid == 50 or 40 <= wid <= 48: return "写作同行"
    return "未知"

POS_MAIN = re.compile(r"(ch(\d{1,2})|序言|后记|尾声|refs|参考文献)\s*[·/／]?\s*L\s*(\d+)")
BARE_L = re.compile(r"(?:^|[、/／\s(（])L\s*(\d+)")
FIG_NO = re.compile(r"(?:fig|图)\s*-?\s*(\d{1,2})\s*-\s*\d+")
TAB_NO = re.compile(r"表\s*(\d{1,2})\s*-\s*\d+")

def parse_pos(raw):
    """返回 (chapter, line, lines, aux[(ch,line),...])。aux = 该条提到的其余位置。"""
    raw = raw.strip()
    found = []  # (order, ch, line)
    for m in POS_MAIN.finditer(raw):
        ch = CH_MAP.get(m.group(1)) if m.group(1) in CH_MAP else ("ch%d" % int(m.group(2)))
        found.append((m.start(), ch, int(m.group(3))))
    if not found:
        # fig-N-N / 表 N-N 给章号，配合任意 L\d+
        chg = None
        m = FIG_NO.search(raw) or TAB_NO.search(raw)
        if m: chg = "ch%d" % int(m.group(1))
        m2 = re.search(r"chapter\.md\s*L\s*(\d+)", raw) or BARE_L.search(raw)
        if chg and m2:
            return chg, int(m2.group(1)), [int(m2.group(1))], []
        return "", 0, [], []
    main_ch, main_line = found[0][1], found[0][2]
    aux = [(ch, ln) for _, ch, ln in found[1:]]
    # 同章裸 L（如 "ch6 L70、L80"）
    last_end = found[0][0]
    for m in POS_MAIN.finditer(raw):
        last_end = m.end()
    tail = raw[last_end:]
    for m in BARE_L.finditer(tail):
        aux.append((main_ch, int(m.group(1))))
    lines = sorted({main_line} | {ln for ch, ln in aux if ch == main_ch})
    return main_ch, main_line, lines, aux

POSITIVE_START = re.compile(r"^\s*(正面基准|正面典型|正面样板|正面案例|做得好|可放心|高质量断言|高质量示范)")

def split_row(line):
    """按未转义管道分割，还原 \\| 为 |；去掉首尾空段。"""
    parts = re.split(r"(?<!\\)\|", line.strip().strip("|"))
    return [p.replace("\\|", "|").strip() for p in parts]

reports, failed, anomalies = [], [], []
total = 0
for path in sorted(glob.glob(os.path.join(DIR, "W*.md"))):
    base = os.path.basename(path)
    m = re.match(r"W(\d{2})_(.+)\.md", base)
    wid = int(m.group(1)); reader = m.group(2)
    text = io.open(path, encoding="utf-8").read()
    rows = []
    for ln in text.splitlines():
        if not ln.startswith("|"): continue
        cells = split_row(ln.strip())
        if len(cells) != 5 or not re.match(r"^\d+$", cells[0]): continue
        num = int(cells[0])
        ch, line, lines, aux = parse_pos(cells[1])
        if not ch or line <= 0:
            anomalies.append("%s #%d 位置无法解析: %r" % (base, num, cells[1]))
        row = {"num": num, "pos_raw": cells[1], "chapter": ch, "line": line, "lines": lines,
               "quote": cells[2], "opinion": cells[3], "type": cells[4],
               "positive": bool(POSITIVE_START.match(cells[3]))}
        if aux:
            row["aux"] = [{"chapter": c, "line": l} for c, l in aux]
        rows.append(row)
    if not rows:
        failed.append(base); continue
    total += len(rows)
    reports.append({"wid": wid, "file": base, "reader": reader, "group": group_of(wid),
                    "perspective": reader, "rows": rows, "chapters": sorted({r["chapter"] for r in rows if r["chapter"]})})

DATA = {"chapters": CHAPTERS, "ch_label": CH_LABEL, "groups": ["职业纵深", "带任务读", "特殊媒介", "技术对照", "特殊读法", "写作同行", "时间维度"],
        "reports": reports, "failed": failed, "anomalies": anomalies, "total_rows": total}
with io.open(os.path.join(DIR, "_reports.json"), "w", encoding="utf-8") as f:
    json.dump(DATA, f, ensure_ascii=False)

n_pos = sum(1 for r in reports for row in r["rows"] if row["positive"])
print("files=%d rows=%d positive=%d failed=%d anomalies=%d" % (len(reports), total, n_pos, len(failed), len(anomalies)))
for a in anomalies: print("  !!", a)
# 每组条数
from collections import Counter
g = Counter()
for r in reports: g[r["group"]] += len(r["rows"])
print(dict(g))
