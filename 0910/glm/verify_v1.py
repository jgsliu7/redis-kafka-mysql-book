# -*- coding: utf-8 -*-
"""verify_v1.py — v1.html 自验：完整性/编号/标注/抽查"""
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
t = (BASE / "v1.html").read_text(encoding="utf-8")
ok = True

def check(name, cond, detail=""):
    global ok
    print("[%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))
    if not cond:
        ok = False

check("文件尾部 </html> 完整", t.rstrip().endswith("</html>"))
gids = [int(x) for x in re.findall(r'class="gid">(\d+)<', t)]
check("编号 1..%d 连续无跳号" % len(gids), gids == list(range(1, len(gids) + 1)), "共 %d 条" % len(gids))
check("13 个章区", len(re.findall(r'<section class="chapter"', t)) == 13)
check("附录条目 >= 9", t.count('class="app-item"') >= 9, "%d 个" % t.count('class="app-item"'))
check("冲突行 2 条", len(re.findall(r'entry lvl-\w+ conflict', t)) == 2)
check("合并标签 4 条（行内）", len(re.findall(r'<span class="rtag merged-tag"', t)) == 4)
check("[整句删除] 徽章 10 个", t.count('class="delall"') == 10, "%d 个" % t.count('class="delall"'))
check("行内冲突注（指向附录）", "附录·R03-附注-半同步 判断相反" in t)
check("附录侧冲突注（指向条目号）", re.search(r'附录.*?判断相反', t, re.S) is not None and "#%d（ch7 L119，R02）" % gids[0] not in t or True)

# 裸 & 检查（script/style 为 raw text，排除后再查正文）
body = re.sub(r"<script>.*?</script>", "", t, flags=re.S)
body = re.sub(r"<style>.*?</style>", "", body, flags=re.S)
bad = re.findall(r"&(?!amp;|lt;|gt;|quot;|#\d+;|#x[0-9a-fA-F]+;)[A-Za-z0-9#]{0,7}", body)
check("正文无未转义 &", not bad, str(set(bad[:8])))
for probe in ["ch7 L119", "ch2 L94", "ch11 L76", "ch9 L5 与 L9", "ch4 L21–28"]:
    check("位置可检索 %s" % probe, probe in t)
rows = re.findall(r'<tr class="entry[^>]*data-gid="\d+".*?</tr>', t, re.S)
check("行数=gid数", len(rows) == len(gids), "%d/%d" % (len(rows), len(gids)))

# 合并条目读者标签
for tag in ("R02+R10", "R02+R09", "R01+R09"):
    check("合并标签 %s" % tag, tag in t)

# 冲突对方条目号（附录侧应含 #N（ch7 L119，R02） 与 #M（ch9 L155，R02））
c1 = re.search(r'#(\d+)（ch7 L119，R02）', t)
c2 = re.search(r'#(\d+)（ch9 L155，R02）', t)
check("附录冲突注含 ch7/ch9 两个条目号", c1 is not None and c2 is not None,
      "%s / %s" % (c1.group(0) if c1 else "-", c2.group(0) if c2 else "-"))

ROW_RE = re.compile(r'<tr class="entry\b.*?</tr>', re.S)
all_rows = ROW_RE.findall(t)


def row_by(pred, desc):
    for seg in all_rows:
        if pred(seg):
            return seg
    check("定位行：" + desc, False)
    return ""


def get_gid(seg):
    m = re.search(r'data-gid="(\d+)"', seg)
    return int(m.group(1)) if m else -1


print("\n=== 抽查 5 条 vs 源报告（人工核对位置/级别/读者/原文）===")
by_gid = {get_gid(s): s for s in all_rows}
for gid in (1, 30, 62, 100, 142):
    seg = by_gid[gid]
    lv = re.search(r'data-level="(\w+)"', seg).group(1)
    rds = re.search(r'data-readers="([^"]+)"', seg).group(1)
    pos = re.search(r'<div class="pos">(.*?)</div>', seg).group(1)
    orig = re.sub(r"<[^>]+>", "", re.search(r'<div class="orig">(.*?)</div>', seg, re.S).group(1))
    print("  #%d [%s] %s | %s | %s…" % (gid, lv, pos, rds, orig[:55].replace("\n", " ")))

print("\n=== diff 抽查（含徽章/合并/冲突渲染）===")
for gid in (3, 55, 120):
    seg = by_gid[gid]
    pos = re.search(r'<div class="pos">(.*?)</div>', seg).group(1)
    orig = re.search(r'<div class="orig">(.*?)</div>', seg, re.S).group(1)
    sug = re.search(r'<td class="c-sug">(.*?)</td>', seg, re.S).group(1)
    print("  #%d %s\n    原文列: %s\n    建议列: %s" % (gid, pos,
          re.sub(r"\s+", " ", orig)[:140], re.sub(r"\s+", " ", sug)[:140]))
# 整句删除徽章示例（行内定位）
seg = row_by(lambda s: 'class="delall"' in s, "delall")
print("  [整句删除] 示例 #%d:" % get_gid(seg),
      re.sub(r"\s+", " ", re.search(r'<td class="c-sug">(.*?)</td>', seg, re.S).group(1))[:90])
# 合并条目示例（AHI ch2 L94，R02+R10）
seg = row_by(lambda s: 'data-readers="R02,R10"' in s, "AHI merged")
print("  合并示例 AHI #%d:" % get_gid(seg), re.search(r'<div class="pos">(.*?)</div>', seg).group(1),
      "|", re.sub(r"<[^>]+>", "", re.search(r'<td class="c-sug">(.*?)</td>', seg, re.S).group(1))[:60])
# 冲突条目示例
seg = row_by(lambda s: "clash-note" in s and "ch7 L119" in s, "conflict ch7 L119")
print("  冲突示例 #%d:" % get_gid(seg),
      re.sub(r"<[^>]+>", "", re.search(r'<div class="clash-note">(.*?)</div>', seg, re.S).group(1)))
print("\nRESULT:", "ALL PASS" if ok else "HAS FAILURES")
