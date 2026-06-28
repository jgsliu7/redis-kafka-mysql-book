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

# ── 五轮交叉验证修复(锁死防回弹,2026-06) ───────────────
assert_zero("ldap_simple 漏前缀(应 authentication_ldap_simple)", r"(?<![a-zA-Z_])ldap_simple")
assert_zero("脏页落盘(应脏页刷盘;flush≠fsync)", r"脏页落盘|脏页.{0,3}落两次盘")
assert_zero("happen-before 拼写(应 happens-before)", r"happen-before")
assert_zero("V0/V1 单条 12 字节(应 V0=14)", r"V0/V1 单条约? ?12 字节")
assert_zero("ch9 MySQL '和 Redis 一样偏 AP'(应区分形态/定位)", r"和 ?Redis 一样偏 ?AP")
assert_zero("八章(全书口径前九章)", r"把八章的零散发现")
assert_zero("背压间隔(应退避 backoff)", r"背压间隔")
assert_zero("分片单位叫分区(自相矛盾)", r"分片单位叫分区")
assert_zero("Page Cache 带空格(应 PageCache 连写)", r"Page Cache")
assert_zero("references 章名'第一章'中文数字(应阿拉伯)", r"## 第[一二三四五六七八九十]+章")
assert_present("CAP nuance 已补(ch9 区分默认形态/产品定位)", r"这只是 MySQL 复制的默认形态，不是它的产品定位")
assert_present("V0 单条 14 字节", r"V0 单条约 14 字节")

# ── SVG 插图:线/箭头衔接修复(锁死防回弹,2026-06) ─────────
import glob as _glob, subprocess
_svgs = {p: open(p, encoding='utf-8').read() for p in _glob.glob('chapters/**/diagrams/*.svg', recursive=True)}
_allsvg = ''.join(_svgs.values())
# fig-5-7:marker 必须朝 +x(配 orient=auto),不能再是朝 +y 的 M0,0 L10,0 L5,9
assert_zero("SVG broken marker(orient=auto 却朝 +y,箭头横飞)", r'<path d="M0,0 L10,0 L5,9', text=_allsvg)
assert_present("fig-5-7 marker 修正(朝 +x)",
               r'M0,0 L10,5 L0,10 z" fill="#4B5563"',
               text=_svgs['chapters/05-layered-architecture/diagrams/fig-5-7.svg'])
# fig-4-1:左侧 x=225 穿标签的纵括号线已删
assert_zero("fig-4-1 左纵括号线(穿标签,已删)", r'x1="225" y1="190"',
            text=_svgs['chapters/04-memory-disk/diagrams/fig-4-1.svg'])
# fig-4-4:归还路径改为绕顶,不再横穿 Free List/LRU 框内部
assert_zero("fig-4-4 旧归还路径(横穿框)", r'M 540 200 Q 200 200',
            text=_svgs['chapters/04-memory-disk/diagrams/fig-4-4.svg'])
assert_present("fig-4-4 新归还路径(绕顶)", r'M 920 170 L 936 170 L 936 80',
               text=_svgs['chapters/04-memory-disk/diagrams/fig-4-4.svg'])
# fig-3-2:③→④ 箭头起止贴边(无缝隙)
assert_present("fig-3-2 ③→④ 贴边", r'M720 166 C 720 210, 450 210, 450 240',
               text=_svgs['chapters/03-lifecycle/diagrams/fig-3-2.svg'])
# 跑几何审计:broken marker([A] 类)不允许回弹
try:
    _r = subprocess.run([sys.executable, 'scripts/svg_audit.py'], capture_output=True, text=True, timeout=90)
    checks += 1
    if '[A]箭头marker朝向错' in _r.stdout:
        fails.append("FAIL  svg_audit [A] broken marker 回弹(应为 0)")
except Exception as _e:
    fails.append(f"FAIL  svg_audit 运行失败: {_e}")

# ── 视觉质检第二轮修复(锁死防回弹,2026-06) ─────────────
# fig-4-5:⑤双写缓冲框的入箭头曾是零长度线(渲染不出)
assert_zero("fig-4-5 零长度线(⑤框缺入箭头)", r'x1="490" y1="408" x2="490" y2="408"',
            text=_svgs['chapters/04-memory-disk/diagrams/fig-4-5.svg'])
# fig-5-6:返回箭头改为绕画布外侧落到 ReplicaManager 框侧边(原悬空 y=312)
assert_present("fig-5-6 返回箭头落 ReplicaManager(非悬空)", r'L 40 260 L 58 260',
               text=_svgs['chapters/05-layered-architecture/diagrams/fig-5-6.svg'])
# fig-7-4:底部文字曾贴画布底被裁 → viewBox 高 380→404
assert_present("fig-7-4 viewBox 加高(防底部裁切)", r'viewBox="0 0 800 404"',
               text=_svgs['chapters/07-cluster/diagrams/fig-7-4.svg'])
# fig-9-6:并行复制绿色箭头与 Worker 框中心对齐(原错位 10px)
assert_present("fig-9-6 Worker 箭头对齐(235/355)", r'x1="235" y1="238" x2="235" y2="258"',
               text=_svgs['chapters/09-data-sync/diagrams/fig-9-6.svg'])
# fig-10-3:底部标注连线够得到台阶(原 8px 悬空) + 删了 stroke-width=0 占位线
assert_present("fig-10-3 标注连线到台阶", r'x2="360" y2="412"',
               text=_svgs['chapters/10-summary/diagrams/fig-10-3.svg'])
assert_zero("fig-10-3 零宽占位线(已删)", r'stroke-width="0"',
            text=_svgs['chapters/10-summary/diagrams/fig-10-3.svg'])

# ── 结论 ──────────────────────────────────────────────
if fails:
    print(f"\n❌ {len(fails)} 项断言失败(共 {checks} 项):\n")
    print("\n".join(fails))
    sys.exit(1)
print(f"✅ 全部 {checks} 项出版断言通过。")
