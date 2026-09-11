# -*- coding: utf-8 -*-
"""verify_order.py — 排序/合并采用文本/修复单元格 定点抽验"""
import re
from pathlib import Path

t = Path(__file__).resolve().parent.joinpath("v1.html").read_text(encoding="utf-8")
rows = re.findall(r'<tr class="entry\b.*?</tr>', t, re.S)
info = []
for seg in rows:
    gid = int(re.search(r'data-gid="(\d+)"', seg).group(1))
    pos = re.search(r'<div class="pos">(.*?)</div>', seg).group(1)
    lv = re.search(r'data-level="(\w+)"', seg).group(1)
    rds = re.search(r'data-readers="([^"]+)"', seg).group(1)
    info.append((gid, pos, lv, rds, seg))

def find(pred):
    return [i for i in info if pred(i)]

print("ch1 L76 两行（R01 应在前）：")
for gid, pos, lv, rds, _ in find(lambda x: x[1] == "ch1 L76"):
    print("  #%d %s %s %s" % (gid, pos, lv, rds))
print("ch9 L155 两行（同读者按条目号：R02-2 在前）：")
for gid, pos, lv, rds, _ in find(lambda x: x[1] == "ch9 L155"):
    print("  #%d %s %s %s" % (gid, pos, lv, rds))
print("ch9 L69 两行（R03-1 在前）：")
for gid, pos, lv, rds, _ in find(lambda x: x[1].startswith("ch9 L69")):
    print("  #%d %s %s %s" % (gid, pos, lv, rds))
print("ch2 L41 三行（R01、R09、R10 顺序）：")
for gid, pos, lv, rds, _ in find(lambda x: x[1] == "ch2 L41"):
    print("  #%d %s %s %s" % (gid, pos, lv, rds))

m3 = find(lambda x: x[1] == "ch1 L76" and x[3] == "R02,R09")[0][4]
orig = re.sub(r"<[^>]+>", "", re.search(r'<div class="orig">(.*?)</div>', m3, re.S).group(1))
print("\n合并条目(ch1 L76, R02+R09) 原文采用 R09 全句：", orig[:42], "…")
why = re.sub(r"<[^>]+>", "", re.search(r'<td class="c-why">(.*?)</td>', m3, re.S).group(1))
print("  分析并列【R09】+【R02】：", "【R09】" in why and "【R02】" in why)

r108 = find(lambda x: x[1] == "ch8 L64" and x[3] == "R10")[0][4]
why8 = re.sub(r"<[^>]+>", "", re.search(r'<td class="c-why">(.*?)</td>', r108, re.S).group(1))
print("\nR10-8（修复行）分析含 `10|000000`：", "10|000000" in why8 or "10&#124;000000" in why8)
print("R10-8 原文含 '走 32 位定长'：", "走 32 位定长" in re.sub(r"<[^>]+>", "", re.search(r'<div class="orig">(.*?)</div>', r108, re.S).group(1)))
print("R10-8 建议含 '低 6 位再分档'：", "低 6 位再分档" in re.sub(r"<[^>]+>", "", re.search(r'<td class="c-sug">(.*?)</td>', r108, re.S).group(1)))
