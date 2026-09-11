# -*- coding: utf-8 -*-
"""解析 104 份读者挑错报告 → _reports.json
每份报告表格行：| # | 位置 | 原文 | 意见 | 类型 |
处理单元格内 \| 转义管道。
"""
import glob, io, json, os, re, sys

DIR = os.path.dirname(os.path.abspath(__file__))

CHAPTERS = ["preface"] + ["ch%d" % i for i in range(1, 11)] + ["后记", "参考文献"]
CH_LABEL = {
    "preface": "序言", "ch1": "第1章", "ch2": "第2章", "ch3": "第3章", "ch4": "第4章",
    "ch5": "第5章", "ch6": "第6章", "ch7": "第7章", "ch8": "第8章", "ch9": "第9章",
    "ch10": "第10章", "后记": "后记", "参考文献": "参考文献",
}
PERSPECTIVES = ["新人可懂性", "技术事实", "命令实操", "编校格式", "AI味", "语言语病", "论断质疑", "讲解质量"]

ROW_RE = re.compile(r"^\|\s*(\d+)\s*\|")
LINE_RE = re.compile(r"L\s*(\d+)")

def split_row(line):
    """按未转义的 | 切分表格行，还原 \\| 为 |。"""
    tmp = line.replace("\\|", "\x00")
    cells = [c.strip() for c in tmp.split("|")]
    cells = [c.replace("\x00", "|") for c in cells]
    if cells and cells[0] == "":
        cells = cells[1:]
    if cells and cells[-1] == "":
        cells = cells[:-1]
    return cells

def parse_file(path):
    fname = os.path.basename(path)
    m = re.match(r"V(\d{3})_(.+?)_(.+)\.md$", fname)
    vid = int(m.group(1))
    ch_key = m.group(2)
    persp = m.group(3)
    with io.open(path, encoding="utf-8") as f:
        text = f.read()
    lines = text.splitlines()
    rows = []
    anomalies = []
    in_table = False
    for ln in lines:
        if ROW_RE.match(ln):
            cells = split_row(ln)
            if len(cells) != 5:
                anomalies.append("%s num=%s fields=%d" % (fname, cells[0] if cells else "?", len(cells)))
                if len(cells) < 5:
                    continue
                # >5 个未转义管道：# / 位置 / 类型 取可靠端，中间全部并入意见（原文并入意见首）
                num, pos, typ = cells[0], cells[1], cells[-1]
                quote = ""
                opinion = " ≁ ".join(cells[2:-1])
            else:
                num, pos, quote, opinion, typ = cells
            all_lines = [int(x) for x in LINE_RE.findall(pos)]
            primary = all_lines[0] if all_lines else None
            rows.append({
                "num": int(num),
                "pos_raw": pos,
                "lines": all_lines,
                "line": primary,
                "quote": quote,
                "opinion": opinion,
                "type": typ,
            })
    return {
        "vid": vid,
        "file": fname,
        "chapter": ch_key if ch_key in CHAPTERS else ch_key,
        "chapter_label": CH_LABEL.get(ch_key, ch_key),
        "perspective": persp,
        "rows": rows,
        "anomalies": anomalies,
        "text": text,  # 供反向判断扫描
    }

def main():
    files = sorted(glob.glob(os.path.join(DIR, "V*_*.md")))
    files = [f for f in files if re.match(r"V\d{3}_", os.path.basename(f))]
    reports = []
    failed = []
    for i in range(1, 105):
        m = glob.glob(os.path.join(DIR, "V%03d_*.md" % i))
        if len(m) != 1:
            failed.append("V%03d: %d 个匹配" % (i, len(m)))
            continue
        try:
            reports.append(parse_file(m[0]))
        except Exception as e:
            failed.append("V%03d: %s" % (i, e))
    # 编号自检：(文件序-1)*8+视角序
    for r in reports:
        fi = CHAPTERS.index(r["chapter"])
        pi = PERSPECTIVES.index(r["perspective"]) if r["perspective"] in PERSPECTIVES else -1
        expect = fi * 8 + pi + 1
        if expect != r["vid"]:
            failed.append("%s 编号自检失败 expect=%d" % (r["file"], expect))
    out = {
        "chapters": CHAPTERS,
        "ch_label": CH_LABEL,
        "perspectives": PERSPECTIVES,
        "reports": [{k: v for k, v in r.items() if k != "text"} for r in reports],
        "failed": failed,
        "anomalies": [a for r in reports for a in r["anomalies"]],
        "total_rows": sum(len(r["rows"]) for r in reports),
    }
    with io.open(os.path.join(DIR, "_reports.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    # 单独存全文供扫描
    with io.open(os.path.join(DIR, "_fulltext.json"), "w", encoding="utf-8") as f:
        json.dump({r["file"]: r["text"] for r in reports}, f, ensure_ascii=False)
    print("parsed=%d failed=%d rows=%d anomalies=%d" % (
        len(reports), len(failed), out["total_rows"], len(out["anomalies"])))
    for x in failed: print("FAILED:", x)
    for a in out["anomalies"]: print("ANOM:", a)

if __name__ == "__main__":
    main()
