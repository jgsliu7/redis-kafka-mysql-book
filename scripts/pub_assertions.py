#!/usr/bin/env python3
"""
出版审查断言回归(regression assertions)
把"已核实为正确/已清理"的事实与规范编码成确定性 grep 断言。
任何改稿后跑一遍 `python3 scripts/pub_assertions.py`,立即发现"修了又回"的回归。

设计动机:飞轮/审查中多次出现 agent 把已修好的改回去(CAP 扁平措辞、KIP-679 误改、
aof-preamble 7.0 默认开启、破折号/半角回归)。本脚本是 docs/出版审查清单与盲区.md §5
"核查闭环没接上"的治本手段——把一次性核查变成持续回归。
"""
import glob, re, sys

FILES = sorted(glob.glob('chapters/0*.md') + glob.glob('chapters/*/chapter.md'))
TEXT = ''.join(open(f).read() for f in FILES)

fails = []
checks = 0

def assert_zero(name, pattern, text=TEXT, flags=0):
    global checks; checks += 1
    n = len(re.findall(pattern, text, flags))
    if n: fails.append(f"FAIL  {name}: {n} 处 {pattern!r}")

def assert_eq(name, actual, expected):
    global checks; checks += 1
    if actual != expected:
        fails.append(f"FAIL  {name}: 期望 {expected!r}, 实际 {actual!r}")

def assert_present(name, pattern, text=TEXT):
    global checks; checks += 1
    if not re.search(pattern, text):
        fails.append(f"FAIL  {name}: 缺少 {pattern!r}")

# ── 锚点 / 规范(必须保持) ──────────────────────────────
assert_zero("三家(应=0)", "三家")
assert_zero("半角标点贴CJK", r"[一-鿿],|,[一-鿿]|[一-鿿]:(?!=)|[一-鿿];")
assert_eq("破折号 ≤12", TEXT.count("——") <= 12, True)
for w in ["真相之源", "骨架", "取舍", "状态机", "同题作答"]:
    assert_present(f"锚点 {w}", w)

# ── CAP 归类(应全 hedged,无绝对措辞) ────────────────────
assert_zero("CAP 绝对措辞(本质上是/写死/必须/走/锁在 AP)",
            r"本质上是 ?AP|写死 ?AP|必须 ?AP|走 ?AP|把自己锁在 AP")

# ── 命令/参数正确性(已核实) ────────────────────────────
assert_zero("ACL FILE(不存在的子命令)", r"ACL FILE")
assert_zero("min-replicas 字节偏移折算(应心跳判定)", r"折算到秒")
assert_zero("aof-use-rdb-preamble 7.0 默认开启(应已移除)",
            r"aof-use-rdb-preamble[^。]*7\.0[^。]*默认开启")
assert_present("KIP-679 保留(acks=all 默认,勿改 588)", r"KIP-679")
assert_zero("一千万倍(应十万倍)", r"一千万倍")
assert_present("SipHash(Redis dict 哈希函数)", r"SipHash")

# ── 术语统一 ──────────────────────────────────────────
assert_zero("中文小写 broker(应 Broker)", r"(?<![a-zA-Z一-鿿])broker(?![a-zA-Z])")
assert_zero("Checkpoint/检查点(应小写 checkpoint)", r"Checkpoint|检查点")
assert_eq("重做日志(中文为主)多于裸 redo log",
          TEXT.count("重做日志") > TEXT.count("redo log"), True)
assert_zero("从库(应从节点;主库=primary DB 语境除外)", r"从库")

# ── 参考文献 ──────────────────────────────────────────
ref = open('chapters/11-references.md').read()
assert_eq("references 无 U+2500 制表符", ref.count(chr(0x2500)), 0)

# ── ch4 图号单调(出现顺序=图号) ────────────────────────
ch4 = open('chapters/04-memory-disk/chapter.md').read()
seen = []
for m in re.finditer(r'图 4-(\d)', ch4):
    n = int(m.group(1))
    if n not in seen:
        seen.append(n)
assert_eq("ch4 图号单调 1→6", seen, [1, 2, 3, 4, 5, 6])

# ── 结论 ──────────────────────────────────────────────
if fails:
    print(f"\n❌ {len(fails)} 项断言失败(共 {checks} 项):\n")
    print("\n".join(fails))
    sys.exit(1)
print(f"✅ 全部 {checks} 项出版断言通过。")
