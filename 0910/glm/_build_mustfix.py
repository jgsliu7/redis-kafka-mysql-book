# -*- coding: utf-8 -*-
"""mustfix.html 生成器：必改级问题批注对比页（自包含，内联 CSS/JS）。"""
import html as H
import difflib
import re
import json
import io
import sys
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = r'D:\data\redis-kafka-mysql\chapters'
SRC = {
    '序言': '00-preface.md',
    'ch1': os.path.join('01-introduction', 'chapter.md'),
    'ch2': os.path.join('02-data-structures-protocols', 'chapter.md'),
    'ch3': os.path.join('03-lifecycle', 'chapter.md'),
    'ch4': os.path.join('04-memory-disk', 'chapter.md'),
    'ch5': os.path.join('05-layered-architecture', 'chapter.md'),
    'ch6': os.path.join('06-security', 'chapter.md'),
    'ch7': os.path.join('07-cluster', 'chapter.md'),
    'ch8': os.path.join('08-storage-format', 'chapter.md'),
    'ch9': os.path.join('09-data-sync', 'chapter.md'),
    'ch10': os.path.join('10-summary', 'chapter.md'),
    '后记': '10-epilogue.md',
    '参考文献': '11-references.md',
}
CH_ORDER = ['序言', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'ch9', 'ch10', '后记', '参考文献']
CH_TITLE = {'序言': '序言', 'ch1': '第 1 章 引言', 'ch2': '第 2 章 数据结构与协议', 'ch3': '第 3 章 生命周期',
            'ch4': '第 4 章 内存与磁盘', 'ch5': '第 5 章 分层架构', 'ch6': '第 6 章 安全',
            'ch7': '第 7 章 集群', 'ch8': '第 8 章 存储格式', 'ch9': '第 9 章 数据同步',
            'ch10': '第 10 章 总结', '后记': '后记', '参考文献': '参考文献'}
CH_ANCHOR = {'序言': 'preface'}
for i in range(1, 11):
    CH_ANCHOR['ch%d' % i] = 'ch%d' % i
CH_ANCHOR['后记'] = 'epilogue'
CH_ANCHOR['参考文献'] = 'refs'

CAT = {'A': ('事实', '#c62828', '#fdecea'), 'B': ('矛盾', '#e65100', '#fff3e0'),
       'C': ('文字', '#1565c0', '#e8f0fe'), 'D': ('合规', '#6a1b9a', '#f3e5f5')}

# ---------------- 条目数据 ----------------
# 每条: id, cat, cons(E叠加), ch(分组章), loc(位置显示), hits(命中徽章), src(读者来源),
#       why(一句话), evidence(证据行,可空), edits[{ch,line,old,new,label}], nfix(改动处文本覆盖,可空)
I = []


def add(id_, cat, cons, ch, loc, hits, src, why, evidence, edits, nfix=None, dual=None, styl=None):
    I.append(dict(id=id_, cat=cat, cons=cons, ch=ch, loc=loc, hits=hits, src=src,
                  why=why, evidence=evidence, edits=edits, nfix=nfix, dual=dual, styl=styl))


add('MF-01', 'C', False, '序言', '序言 L17', '3 位·夜轮', 'V001/V006/V008',
    '"速度"（名词）对"持久"（形容词）词性失对，同句其余四组皆对仗，全书固定说法是"速度 vs 持久性"（第 1、4、10 章及图 10-2）', '',
    [dict(ch='序言', line=17,
          old='速度还是持久、一致还是可用、空间还是时间、简单还是灵活、通用还是专用',
          new='速度还是持久性、一致还是可用、空间还是时间、简单还是灵活、通用还是专用')])

add('MF-02', 'C', False, 'ch1', 'ch1 L50', '1 位·本轮', 'W49',
    '列表项后无空行，CommonMark lazy continuation 使全书总起句渲染后并入 Kafka 条目内部（全书仅此一处）', '',
    [dict(ch='ch1', line=50,
          old='- **Kafka**：用"追加写日志 + 顺序 I/O + 分区并行"换高吞吐与线性扩展，代价是延迟偏高、不适合随机查询。\n这三组设计就是本书的主线，后面每章都是它们在不同问题上的展开。',
          new='- **Kafka**：用"追加写日志 + 顺序 I/O + 分区并行"换高吞吐与线性扩展，代价是延迟偏高、不适合随机查询。\n〔空行〕\n这三组设计就是本书的主线，后面每章都是它们在不同问题上的展开。')])

add('MF-03', 'C', False, 'ch1', 'ch1 L76', '两轮 17 位', 'V009/V010/V015/V016/R01/R02/R09/W11/W18/W19/W20/W22/W23/W31/W37/W39/W48',
    '全书最高命中："一句话说清"实为 150 字双层括号嵌套长句（R01 判"第一次下马威"）；拆三句，并补隔离级别限定——快照时机仅默认 RR 成立，RC 每语句重拍（顺带消除与 L44"隔离级别细节不在范围"的口径冲突）', '',
    [dict(ch='ch1', line=76,
          old='MVCC 的原理一句话说清：改一行时保留旧版本，读事务持有一个 Read View 判断哪些版本对它可见（Read View 在事务首次读时拍下快照，记下当时的活跃事务集合；判断方式是沿 undo log 串起的版本链从新到旧，找第一个对自己可见的版本），于是读不加锁、不阻塞写，写也不阻塞读；undo log（回滚日志）里串起来的那条旧版本链，就是它的载体。',
          new='MVCC 的原理可以拆成三句话说清。第一，改一行时不抹掉旧版本，旧版本串在 undo log（回滚日志）形成的版本链上。第二，事务第一次读时拍下一个 Read View（读视图），记下"此刻还有哪些事务开着没提交"（活跃事务集合）。第三，之后这个事务读任何一行，都沿版本链从新到旧找第一个对自己可见的版本。于是读不加锁、不阻塞写，写也不阻塞读。快照时机随隔离级别而变：默认的可重复读下首次读拍一次、沿用整个事务，读已提交下每条语句重拍；更细的比对规则不在本书范围。')], styl='双席')

add('MF-04', 'A', False, 'ch1', 'ch1 L137', '1 位·官方文档', 'V011',
    '括号把 min.insync.replicas 释义成"确认数需求"，实为 ISR 数量下限：跌破即拒写（NotEnoughReplicas）；RF=3、ISR=3 时要 3 个确认，不是 2 个', '证据：Kafka 官方文档 broker 配置 min.insync.replicas',
    [dict(ch='ch1', line=137,
          old='| Kafka 副本 | 设 acks=all、min.insync.replicas=2（写入至少需 2 个同步副本确认） | ISR 为何要"动态收缩"？Leader 切换与一致性如何兼顾？ |',
          new='| Kafka 副本 | 设 acks=all、min.insync.replicas=2（ISR 少于 2 个时拒绝写入；写入要等 ISR 中全部副本确认） | ISR 为何要"动态收缩"？Leader 切换与一致性如何兼顾？ |')], styl='文风')

add('MF-05', 'A', False, 'ch2', 'ch2 L41', '4 位·两轮', 'V018/V019/W10/R10',
    'ZRANGE 官方复杂度为 O(log(N)+M)（M 为返回元素数），同段隔两行自己就写了"O(log N + M)"，同段自相矛盾', '证据：redis.io/commands/zrange',
    [dict(ch='ch2', line=41,
          old='member→score 的查找走 dict，ZSCORE 是 O(1)；按序拉段走跳表，ZRANGE 是 O(log N)。',
          new='member→score 的查找走 dict，ZSCORE 是 O(1)；按序拉段走跳表，ZRANGE 是 O(log N + M)（M 为拉取条数）。')])

add('MF-06', 'A', False, 'ch3', 'ch3 L151', '2 位·夜轮', 'V026/V027',
    '`[KafkaServer id=0] started` 是 ZooKeeper 模式的日志，KRaft 模式（本章主线）下不会出现，运维照书 grep 就绪探针直接失灵', '证据：Kafka 3.3+ KRaft broker 实际日志（[BrokerServer id=N] Transition from STARTING to STARTED）',
    [dict(ch='ch3', line=151,
          old='八个阶段全部走完，Kafka 才对外打印 `[KafkaServer id=0] started` 这条就绪日志，和 Redis 的 `Ready to accept connections`、MySQL 的 `ready for connections` 是同一类信号。',
          new='八个阶段全部走完，Kafka 才对外打印就绪日志，和 Redis 的 `Ready to accept connections`、MySQL 的 `ready for connections` 是同一类信号。具体打哪条看部署模式：ZK 模式是 `[KafkaServer id=0] started`，KRaft 模式是 `[BrokerServer id=0] Transition from STARTING to STARTED`，写就绪脚本时按模式 grep 对应那条。')], styl='文风')

add('MF-07', 'B', False, 'ch3', 'ch3 L207（表 3-2 Redis 列）', '2 位·同源两处', 'W50/W07',
    '表格断言"快（仅刷未落盘部分）"与 3.4 节"出厂默认含全量 RDB 落盘、大实例轻松越过 30 秒被 SIGKILL"同章打架，默认路径下最要命的关闭耗时被说没了', '',
    [dict(ch='ch3', line=207, label='表 3-2 "关闭速度与可预测性"行 Redis 列',
          old='快（仅刷未落盘部分；有落后副本时加等追平，上限 10 秒）',
          new='取决于 SAVE/NOSAVE 与数据量（出厂默认含全量 RDB 落盘，大实例可达分钟级，见 3.4；有落后副本时加等追平，上限 10 秒）')])

add('MF-08', 'B', False, 'ch3', 'ch3 L207（表 3-2 MySQL 列）', '1 位·书内自证', 'W33',
    '同一个 MySQL 默认档（innodb_fast_shutdown=1），表 3-1（L116）说"中等"，表 3-2 说"慢且不可预测"，相隔 90 行结论相反', '',
    [dict(ch='ch3', line=207, label='表 3-2 "关闭速度与可预测性"行 MySQL 列',
          old='慢且不可预测（事务回滚 + 脏页）',
          new='默认档中等（见表 3-1），长事务回滚 + 大量脏页时慢且不可预测')])

add('MF-09', 'B', False, 'ch4', 'ch4 L9', '3 位·两轮', 'V035/W01/R08',
    '导读引述"Query Cache 够用"作论据，但全书基线 8.0 已整体移除该功能（ch5 L113 才交代），中间隔着四章错误认知', '',
    [dict(ch='ch4', line=9,
          old='有人坚持"MySQL 有内存表和 Query Cache，够用了"。',
          new='有人坚持"MySQL 有内存表和 Query Cache，够用了"（Query Cache 已在 MySQL 8.0 移除，见第 5 章）。')])

add('MF-10', 'B', False, 'ch4', 'ch4 L17/L26/L28（表 4-1）', '13 位·两轮', 'W14/W15/W19/W21/W22/W28/W33/W39/W41/W43/W49/R09/R01',
    '"典型访问延迟"列末两行填的是 MB/s 吞吐数字，"相对内存"列前四行是延迟倍率、后两行变成带宽对照且换了参照物，同一列两种量纲无法比较', '',
    [dict(ch='ch4', line=17, label='表注',
          old='表中数字用于建立数量级，不是硬件基准；真实值会随 CPU、磁盘、文件系统、队列深度与负载模型变化。',
          new='表中数字用于建立数量级，不是硬件基准；真实值会随 CPU、磁盘、文件系统、队列深度与负载模型变化。末两行"顺序写吞吐"是带宽口径，"相对内存"列对照的是带宽差距而非延迟倍率。'),
     dict(ch='ch4', line=26, label='SSD 顺序写吞吐行"相对内存"列',
          old='SATA 档约相当于单线程内存随机读（几百 MB/s 量级），高代际 NVMe 已进入内存带宽的一个数量级以内',
          new='SATA 档约相当于单线程内存随机读（几百 MB/s 量级），高代际 NVMe 与内存带宽差距不到一个数量级'),
     dict(ch='ch4', line=28, label='机械盘顺序写吞吐行"相对内存"列',
          old='顺序吞吐进入单线程内存随机读的一个数量级以内',
          new='顺序吞吐与单线程内存随机读差距不到一个数量级')], styl='双席')

add('MF-11', 'A', False, 'ch4', 'ch4 L30', '2 位·夜轮', 'V034/V036',
    '按单位换算纳秒到毫秒是 6 个数量级，"三到五个"对不上；前文两个换算例子（内存 vs SSD ≈10³、vs 机械盘 ≈10⁵）的锚是介质不是单位', '',
    [dict(ch='ch4', line=30,
          old='纳秒、微秒、毫秒之间相差三到五个数量级，存储软件要在内存的纳秒和磁盘的毫秒之间跨过这个数量级差距，所有"内存-磁盘"设计都从这里起步。',
          new='从内存的百纳秒到 SSD 的百微秒差三个数量级，到机械盘的十毫秒差五个数量级，存储软件要跨过这个数量级差距，所有"内存-磁盘"设计都从这里起步。')])

add('MF-12', 'C', False, 'ch4', 'ch4 L172', '1 位（三校级 P0）', 'R06',
    '"二级索引的非唯一索引"语序颠倒——字面读成"二级索引所拥有的非唯一索引"，规范语序是"非唯一的二级索引"', '',
    [dict(ch='ch4', line=172,
          old='修改缓冲只对二级索引的非唯一索引生效，因为唯一索引必须立刻检查约束。',
          new='修改缓冲只对非唯一的二级索引生效，因为唯一索引必须立刻检查约束。')])

add('MF-13', 'A', False, 'ch4', 'ch4 L202', '1 位·内核默认值', 'V034',
    '"下几 MB"与 Linux 默认预读窗口 128KB 差一个数量级以上，且与本章 L258 把"预读大小"列为 OS 可调参数相矛盾', '证据：Linux 块设备默认 read_ahead_kb=128',
    [dict(ch='ch4', line=202,
          old='操作系统预读机制能把"消费者将要读的下几 MB"提前加载进 PageCache，命中率天然就高。',
          new='操作系统预读机制能把"消费者将要读的下一段数据"提前加载进 PageCache（默认预读窗口约 128KB，调优后可到 MB 级），命中率天然就高。')])

_cap = [
    ('图 4-2', '图 4-2　Redis 近似 LRU 采样淘汰与 LFU 计数器衰减机制：LRU 比最近访问时间，LFU 比带衰减的对数频次，采样与比较机制共用'),
    ('图 4-3', '图 4-3　Redis 持久化数据流（RDB 快照 / AOF 含混合持久化）：两条路径独立，混合持久化只是文件层拼接'),
    ('图 4-4', '图 4-4　InnoDB 缓冲池三分链表（Free / LRU 新老分区 / Flush）'),
    ('图 4-5', '图 4-5　MySQL 一次写操作的全链路时序（缓冲池→redo log→双写→刷盘）'),
    ('图 4-6', '图 4-6　Kafka 生产-存储-消费的零拷贝数据流'),
]
add('MF-14', 'C', False, 'ch4', 'ch4 L88/115/149/163/211（图注）', '1 位·机械项', 'R04',
    '全书 64 条图注仅 ch4 这 5 条末尾无句号；另 L115/L149/L163/L211 四处图注与下一行正文无空行，Markdown 渲染时并成同段', '',
    [dict(ch='ch4', line=ln, label=name + ' 图注补句号', old=cap_text, new=cap_text + '。')
     for (name, cap_text), ln in zip(_cap, (88, 115, 149, 163, 211))],
    nfix='9 处（句号 5 + 空行 4；空行处在 L115/L149/L163/L211 图注行后各补一个空行）')

add('MF-15', 'B', False, 'ch5', 'ch5 L44（连带 ch1 L62）', '7 位·两轮', 'V042/V047/V048/R02/R09/W15/W50',
    '因果错位：前文刚说"命令执行依然在主线程串行"，又说单线程内存模型"解释了为什么默认关闭多线程 I/O"——开了 I/O 线程也不碰内存模型；且默认只拆写、读需显式 io-threads-do-reads（默认 no）', '证据：redis.conf 7.x（io-threads-do-reads 默认 no）+ 源码 postponeClientRead 条件',
    [dict(ch='ch5', line=44, label='① 读写拆分改写回（读可选）',
          old='把协议的**读写**（`read`/`write` 系统调用和大块 buffer 拷贝）拆给一组 I/O 线程，**命令执行依然在主线程串行**。',
          new='把协议的**写回**（`write` 系统调用和大块 buffer 拷贝）拆给一组 I/O 线程（读默认留在主线程，`io-threads-do-reads` 默认关、要显式开启），**命令执行依然在主线程串行**。'),
     dict(ch='ch5', line=44, label='② 默认关闭的真实原因',
          old='这一句话也解释了为什么 7.x 默认仍然关闭多线程 I/O。它是个可选优化。',
          new='7.x 默认仍然关闭多线程 I/O，是另一个原因：它只在网络 I/O 本身成为瓶颈（大量连接、大响应）时才有收益，多数负载下开起来只是多付线程协调开销，官方就把它留成了可选优化。'),
     dict(ch='ch1', line=62, label='③ 连带：ch1 同病',
          old='自 6.0 起引入了可选的多线程 I/O 来加速网络读写，但命令执行仍是单线程',
          new='自 6.0 起引入了可选的多线程 I/O 来加速网络写——读要显式开 `io-threads-do-reads`，默认关——但命令执行仍是单线程')], styl='双席')

add('MF-16', 'A', False, 'ch5', 'ch5 L232', '2 位·两轮', 'R07/V047',
    '全书语境是同机房 Broker 通信：进程内几十纳秒 vs 同机房往返百微秒到毫秒，"差了六个数量级"须取两端极值才凑得出，读者照抄会高估 100–1000 倍', '证据：Azure 同可用区 RTT 统计（均值约 0.9ms）/ Evan Jones 2021 同机房实测',
    [dict(ch='ch5', line=232,
          old='进程内调用的延迟是纳秒级，网络调用的延迟是毫秒级，差了六个数量级。',
          new='进程内调用是几十纳秒量级，同机房网络往返是百微秒到毫秒量级，差三到四个数量级（跨地域部署才拉开到五六个数量级）。')])

add('MF-17', 'B', False, 'ch6', 'ch6 L15', '4 位·两轮', 'V052/V056/W50/R04',
    '"这四个层面各覆盖一段"把审计也计入，与后半句"审计则贯穿全程"同句互斥；图 6-1 图注（L20）的口径是"三层各覆盖一段 + 审计旁路贯穿"。B 核实官连带发现第三边 L22"四维依次接力"同病（接力把旁路审计算进队伍），另列 MF-46', '',
    [dict(ch='ch6', line=15,
          old='这四个层面在一次"客户端发起请求到数据落盘"的链路上各覆盖一段，审计则贯穿全程。',
          new='这四个层面在一次"客户端发起请求到数据落盘"的链路上，前三层各覆盖一段，审计则贯穿全程。')])

add('MF-18', 'B', False, 'ch6', 'ch6 L72', '2 位·夜轮', 'V050/V056',
    '与 L68 直接冲突：SCRAM 的定义就是"密码从不上网"（同章自己写的），L72 又说"SCRAM 密码在客户端和 Broker 之间反复传会有泄露风险"，读者两段连读必然糊涂', '',
    [dict(ch='ch6', line=72,
          old='长期凭证（SCRAM 密码、Kerberos 票据）在客户端和 Broker 之间反复传会有泄露风险，委托令牌是短期有效的令牌，由已认证的客户端向 Broker 申请，之后用令牌做认证，到期自动失效。',
          new='长期凭证（SCRAM 密码、Kerberos 票据）要静态配进每个客户端、整个生命周期反复使用，暴露面大（SCRAM 密码本身从不上网，但 Kerberos 票据会随请求反复出示），委托令牌是短期有效的令牌，由已认证的客户端向 Broker 申请，之后用令牌做认证，到期自动失效。')], styl='文风')

add('MF-19', 'A', False, 'ch6', 'ch6 L127 + L180（表 6-1）', '3 位·两轮', 'V050/R10/W35',
    'allow.everyone.if.no.acl.found 默认值是 false 不是 true——写反后"生产环境显式设为 false"成为空操作，Apache Kafka 的默认安全姿态（默认拒绝）被整个说反', '证据：Kafka 官方文档 Authorization and ACLs（"no one other than super users"）+ 源码默认值 false；AWS MSK 预置 true 是托管定制',
    [dict(ch='ch6', line=127, label='① 正文',
          old='Kafka 的默认策略要分两种授权器看。`AclAuthorizer`（ZK 时代的经典授权器）下，`allow.everyone.if.no.acl.found` 默认是 **true**：资源上完全没配 ACL 时放行所有人，配了 ACL 之后未命中的请求才被拒绝。KRaft 的 `StandardAuthorizer` 则始终默认拒绝。',
          new='Kafka 的默认策略要分两种授权器看。`AclAuthorizer`（ZK 时代的经典授权器）下，`allow.everyone.if.no.acl.found` 默认是 **false**：资源上完全没配 ACL 时，除 super.users 外一律拒绝；显式设为 true 才会在无 ACL 时放行所有人（Amazon MSK 等托管服务会预置成 true，容易造成"默认放行"的错觉）。KRaft 的 `StandardAuthorizer` 同样默认拒绝。'),
     dict(ch='ch6', line=180, label='② 表 6-1 连带',
          old='AclAuthorizer 无 ACL 默认放行；StandardAuthorizer 默认拒绝',
          new='AclAuthorizer 与 StandardAuthorizer 均默认拒绝（无 ACL 资源仅 super.users 可访问；AclAuthorizer 需显式设 allow.everyone.if.no.acl.found=true 才放行）')])

add('MF-20', 'B', True, 'ch7', 'ch7 L8（导读）', '5 位·两轮', 'R08/V058/V064/W20/W50',
    '导读按 Redis→MySQL→Kafka 顺序列举后接"从弱到强排开"，读成 Kafka 一致性最强；7.5 谱系（L205）是 Redis 弱端→Kafka 中间可滑→MySQL MGR 强端，与 9.5 表 9-1、ch10 L100 三处口径冲突', '',
    [dict(ch='ch7', line=8,
          old='三个答案按一致性强度从弱到强排开。',
          new='三个答案按一致性强度排开：Redis 在弱的一端，MySQL（MGR）在强的一端，Kafka 卡在中间。')], styl='双席')

add('MF-21', 'A', False, 'ch7', 'ch7 L57', '2 位·两轮', 'V059/R03',
    '全书基线 Redis 7.x 的全量同步默认无盘复制（repl-diskless-sync 自 7.0 默认 yes），"写成一个 RDB（快照文件）"是 6.x 默认行为', '证据：redis/redis 7.0 redis.conf + 7.0 changelog（issue #9992）',
    [dict(ch='ch7', line=57,
          old='主节点 `fork` 出子进程，把内存数据写成一个 RDB（快照文件）发给从节点，期间主节点新产生的写命令先存进这条连接专属的复制缓冲区。',
          new='主节点 `fork` 出子进程，把内存数据序列化成 RDB 流直接发给从节点（7.0 起默认无盘复制，`repl-diskless-sync=yes`；设为 no 才先写磁盘文件再发送），期间主节点新产生的写命令先存进这条连接专属的复制缓冲区。')], styl='双席')

add('MF-22', 'C', False, 'ch7', 'ch7 L59/L67 + ch9 L179', '3 位·两轮（3 处）', 'R06/V062/W18',
    '介词"从"紧贴名词"从节点/从库"，双 cóng 连读结巴，三处同病；语法不错但三处都绊人', '',
    [dict(ch='ch7', line=59,
          old='读可以分担到从节点，主节点坏了可以从从节点恢复数据',
          new='读可以分担到从节点，主节点坏了还能靠从节点恢复数据'),
     dict(ch='ch7', line=67,
          old='再按优先级、复制偏移量（offset）、runid 三个维度从从节点里挑一个提升为新主',
          new='再按优先级、复制偏移量（offset）、runid 三个维度在从节点里挑一个提升为新主'),
     dict(ch='ch9', line=179,
          old='串行瓶颈没有消失，只是从从库转移到了主库的提交队列',
          new='串行瓶颈没有消失，只是转移到了主库的提交队列')])

add('MF-23', 'A', True, 'ch7', 'ch7 L172', '7 位·两轮', 'V058/V059/V063/W2/W11/W25/W45',
    '"只要 ISR 非空"几乎恒真（ISR 恒含 Leader 自己），对"不丢"没有约束力；min.insync.replicas 默认 1，ISR 缩到只剩 Leader 时 acks=all 退化为 acks=1，"不会丢"承诺过头', '证据：Kafka 官方文档（min.insync.replicas 默认 1，官方推荐组合 replication.factor=3 + min.insync.replicas=2）',
    [dict(ch='ch7', line=172,
          old='只要 ISR 非空且 ISR 全部收到，这条消息就不会丢。',
          new='只要 ISR 里的副本数不少于 `min.insync.replicas` 且全部收到，这条消息就不会因正常的 Leader 切换而丢。但 `min.insync.replicas` 默认是 1——ISR 缩到只剩 Leader 一个时，acks=all 实际只等一个确认，要真正守住"不丢"需配到 2。')], styl='双席')

add('MF-24', 'C', False, 'ch8', 'ch8 L71', '1 位', 'V070',
    '"结尾是 8 字节 CRC64 校验"名词位缺"和"字；同句后文"到末尾校验和之前的全部内容"已用全称，自证脱字', '',
    [dict(ch='ch8', line=71,
          old='结尾是 8 字节 CRC64 校验。',
          new='结尾是 8 字节 CRC64 校验和。')])

add('MF-25', 'C', False, 'ch8', 'ch8 L120', '1 位（三校级 P0）', 'R06',
    '引号内"对这台机器的磁盘、这个负载的访问模式"是残句——"对"字悬空没有着落，整段是半截话', '',
    [dict(ch='ch8', line=120,
          old='答案取决于"对这台机器的磁盘、这个负载的访问模式"。',
          new='答案取决于"这台机器的磁盘条件、这个负载的访问模式"。')])

add('MF-26', 'A', False, 'ch8', 'ch8 L151', '1 位·内核证据', 'W29',
    '"一次 512 字节的写要么完整要么不发生"把设计动机写成了硬件承诺：断电半扇区撕裂（torn write）在 SATA/SCSI 设备上是已知现象，InnoDB 真正的机制是每块 redo 自带校验和、恢复时逐块检出丢弃', '证据：PostgreSQL full_page_writes 的设计动机（社区明确不信任扇区原子写）/ 存储工程文献',
    [dict(ch='ch8', line=151,
          old='512 字节匹配传统磁盘扇区的原子写粒度：一次 512 字节的写要么完整要么不发生，不会留下半个扇区的撕裂。',
          new='这个尺寸来自传统磁盘的扇区大小：对齐了它，跨界写的概率更低——但断电撕出半个扇区，在真实设备上照样会发生；每块 redo 自带校验和，恢复时逐块校验、丢弃不完整的尾部，撕裂查得出来。')], styl='双席')

add('MF-27', 'A', False, 'ch9', 'ch9 L69 + L71', '4 位·两轮', 'V074/V075/V059/R03',
    '基线 7.x 全量同步默认无盘复制：子进程把 RDB 流直接写进副本连接、主节点磁盘不生成文件；步骤按 6.x 落盘路径描述。同句"未知 run_id"应为 replid（L89 自己已更正过）', '证据：redis/redis 7.0 与 7.4 分支 redis.conf（repl-diskless-sync 默认 yes）',
    [dict(ch='ch9', line=69, label='① 步骤 1（同时修 replid 释义与无盘路径）',
          old='1. 主节点收到副本的 `PSYNC ? -1`（`?` 与 `-1` 分别表示"未知 run_id"与"无偏移量"，这是 Redis 副本首次连接时发的内部协议命令，不是能在 redis-cli 里直接敲的命令），触发 `BGSAVE`，fork 出一个子进程把当前内存快照写成 RDB 文件。',
          new='1. 主节点收到副本的 `PSYNC ? -1`（`?` 与 `-1` 分别表示"未知复制 ID"与"无偏移量"——复制 ID 就是 replid，这是 Redis 副本首次连接时发的内部协议命令，不是能在 redis-cli 里直接敲的命令），fork 出一个子进程做全量同步。默认路径是无盘复制（7.0 起 `repl-diskless-sync` 默认 yes）：子进程把内存快照序列化成 RDB 流直接写进副本连接；显式配 no 才先 `BGSAVE` 写成 RDB 文件再传。'),
     dict(ch='ch9', line=71, label='② 步骤 3 连带',
          old='3. RDB 文件传给副本，副本加载后，状态回到了"主节点 fork 那一刻"。',
          new='3. RDB 流（或文件）传给副本，副本加载后，状态回到了"主节点 fork 那一刻"。')], styl='双席')

add('MF-28', 'A', False, 'ch9', 'ch9 L99', '1 位·客观事实', 'W27',
    'Redis 是 C 语言实现、没有垃圾回收——"副本做一次短暂的 GC"是把 JVM 系统的病张冠李戴给 C 程序', '',
    [dict(ch='ch9', line=99,
          old='（典型场景：副本做一次短暂的 GC 或网络抖动）',
          new='（典型场景：副本一次短暂阻塞——fork、慢命令——或网络抖动）')])

add('MF-29', 'A', False, 'ch9', 'ch9 L175', '1 位·同句自证', 'W12',
    '主句"只有一个 SQL 线程串行回放"与同句括号"8.0.27 起 MTS 默认开启 4 个 worker"打架——基线 8.0.x 下从库默认不是单线程回放，会把延迟工单的排查方向带偏', '',
    [dict(ch='ch9', line=175,
          old='传统复制最大的问题是**复制延迟**：从节点只有一个 SQL 线程串行回放事件（8.0.27 起 MTS 默认开启 4 个 worker，更早版本默认单线程），主节点并发写入、从节点串行追赶，吞吐不对称导致从节点越落越远。',
          new='传统复制最大的问题是**复制延迟**：从节点靠 SQL 线程回放事件，MTS 出现前只有一个线程串行回放（8.0.27 起 MTS 默认开启 4 个 worker），主节点并发写入、从节点追赶吃力，吞吐不对称导致从节点越落越远。')], styl='双席')

add('MF-30', 'B', False, 'ch9', 'ch9 L281（表 9-1）', '2 位·两轮', 'V074/R03',
    '表 9-1 写"主节点阻塞"，与正文 L70"RDB 生成和传输的整段时间里主节点继续服务"、L76"短暂的停顿"两处直接矛盾', '',
    [dict(ch='ch9', line=281, label='表 9-1 "全量同步代价"行 Redis 列',
          old='fork RDB 传输（主节点阻塞 + 内存翻倍风险）',
          new='fork 短暂停顿 + 写时复制内存翻倍风险 + RDB 传输占用出口带宽')], styl='文风')

add('MF-31', 'C', False, 'ch9', 'ch9 L287', '1 位', 'V076',
    '"序列化小"漏"开销"二字——序列化是动作不能"小"，L57 原话即"序列化开销小"', '',
    [dict(ch='ch9', line=287,
          old='Redis 走命令流这条路，看重的是轻：序列化小、副本直接复用命令处理路径，但非确定性命令得在源头改写。',
          new='Redis 走命令流这条路，看重的是轻：序列化开销小、副本直接复用命令处理路径，但非确定性命令得在源头改写。')])

add('MF-32', 'C', True, 'ch9', 'ch9 L321', '5 位·夜轮', 'V073/V076/V077/V078/V080',
    '前句主语是"全量同步"（单数），"它们"就近没有复数先行词，只能远跳两节之外的"三个软件"，指代悬空', '',
    [dict(ch='ch9', line=321,
          old='全量同步是兜底手段。它们都在"怎么让断线尽量走增量"上投入了大量设计：',
          new='全量同步是兜底手段，三个软件都在"怎么让断线尽量走增量"上投入了大量设计：')])

add('MF-33', 'B', True, 'ch10', 'ch10 L5', '8 位·两轮', 'V081/V088/V089/V092/V094/V095/V096/W18',
    '"前九章/八个主题"与 L11"九章九问"、表 10-1 九行三套计数并存，读者被迫自己数目录才能对上账', '',
    [dict(ch='ch10', line=5,
          old='前九章，三个软件在八个主题上有截然不同的方案。',
          new='前九章——第 1 章引入三个样本、第 2 到 9 章每章一个主题——三个软件在八个主题上有截然不同的方案。')])

add('MF-34', 'C', False, 'ch10', 'ch10 L72（两处）', '1 位', 'V086',
    '"丢较多"缺"得"（动词+程度补语必须用"得"连接）；同段"最不丢"是生造程度式，两档表述不一致', '',
    [dict(ch='ch10', line=72, label='① always 档',
          old='`always`（每条命令都落盘，最慢但最不丢）',
          new='`always`（每条命令都落盘，最慢但丢得最少）'),
     dict(ch='ch10', line=72, label='② no 档',
          old='`no`（交给操作系统决定，最快但可能丢较多）',
          new='`no`（交给操作系统决定，最快但可能丢得较多）')])

add('MF-35', 'B', True, 'ch10', 'ch10 L74（两处）', '6 位·两轮', 'R07/V081/V087/V088/W15/W47',
    '"强一致都是某个参数从 0 调到 1"与 ch7 L174"半同步装插件可开关、MGR 要换一套复制架构"直接矛盾；且本节自己列的 appendfsync/acks 都不是 0/1 参数', '',
    [dict(ch='ch10', line=74, label='① 主句',
          old='所谓"强一致"都是某个参数从 0 调到 1 的结果。',
          new='所谓"强一致"，轻的是调参（`acks`、双 1），重的要换机制乃至换架构（异步复制换到 MGR）。'),
     dict(ch='ch10', line=74, label='② 后句指代连带',
          old='我应用这条规律时，会把这个参数的代价暴露给真正在意它的人',
          new='我应用这条规律时，会把这档代价暴露给真正在意它的人')])

add('MF-36', 'A', False, 'ch10', 'ch10 L145（表 10-2，两处）', '6 位·两轮', 'V082/V083/V087/W9/W13/W29',
    'Redis 列"默认约 1–2 秒（开启 AOF 后）"——出厂默认不开 AOF（与 ch4/ch8 口径矛盾）；Kafka 列"acks=all 接近 0"缺 min.insync.replicas≥2 前提（默认 1 时退化为 acks=1）', '',
    [dict(ch='ch10', line=145, label='① Redis 列（RPO 行）',
          old='默认约 1–2 秒量级窗口（开启 AOF 后）',
          new='出厂默认 RDB-only，丢失量是一个快照周期（最长可达小时级）；开启 AOF everysec 后约 1–2 秒'),
     dict(ch='ch10', line=145, label='② Kafka 列（RPO 行）',
          old='acks=all 接近 0',
          new='acks=all + min.insync.replicas≥2 接近 0（默认 min.insync.replicas=1 时不保证）')], styl='双席')

add('MF-37', 'A', True, 'ch10', 'ch10 L147（表 10-2）', '7 位·两轮', 'R02/R10/V082/V083/V087/W04/W46',
    'Cluster Linking 是 Confluent 平台专有特性（Confluent Enterprise License），不在 Apache Kafka 开源版内——"均为 Kafka 官方工具"归属错误，读者照书在开源版里找不到该组件', '证据：Confluent 官方许可页（Cluster Linking 列 Confluent Enterprise License）+ Confluent Cluster Linking 文档',
    [dict(ch='ch10', line=147,
          old='MirrorMaker / Cluster Linking（均为 Kafka 官方跨集群复制工具）',
          new='MirrorMaker 2（Apache Kafka 官方自带）/ Cluster Linking（Confluent 平台特性，不在 Apache Kafka 开源版内）')])

add('MF-38', 'B', False, '后记', '后记 L3 + L31', '4 位·夜轮', 'V089/V092/V094/V095',
    '"九章走完/全书九章"漏掉第 10 章，同篇 L7"我在第 10 章把它们收成了五条规律"、L39"第 10 章 10.4.3"两处引用第 10 章，一篇之内口径打架', '',
    [dict(ch='后记', line=3,
          old='九章走完，讨论了三个软件、八个主题，贯穿它们的是同一种视角。',
          new='十章走完，讨论了三个软件、八个主题，贯穿它们的是同一种视角。'),
     dict(ch='后记', line=31,
          old='回头看这个故事，全书九章其实都指向这一件事。',
          new='回头看这个故事，全书十章其实都指向这一件事。')], styl='双席')

add('MF-39', 'D', False, '后记', '后记 L59（版权行）', '2 位法务·终审+法务', 'W17/W40',
    'NC（非商业）条款与出版社商业发行正面冲突——按此声明出版社发行、书店销售都在"未经许可的商业用途"之列；ND（禁止演绎）与三审三校的删改加工也冲突。法务判"不整改不能付印"', '证据：CC BY-NC-ND 4.0 条款文本 + 出版合同惯例（需与出版社法务确认）',
    [dict(ch='后记', line=59,
          old='© 2026 本书作者。本书采用知识共享署名-非商业性使用-禁止演绎 4.0 国际许可协议（CC BY-NC-ND 4.0）授权，未经许可不得用于商业用途。',
          new='【方案 A｜删除 CC 声明】© 2026 本书作者。保留所有权利。未经出版方书面许可，不得以任何形式复制、转载本书内容。',
          new2='【方案 B｜改授权·去 ND】© 2026 本书作者。本书网络版以知识共享署名-非商业性使用 4.0 国际许可协议（CC BY-NC 4.0）授权发布；纸质版及相关商业出版权利由出版社依出版合同行使。')],
    nfix='1 处（二选一，需作者拍板并与出版社法务确认）')

add('MF-40', 'D', False, '后记', '后记 L61（版权行）↔ 参考文献 25 处访问日期', '3 位·本轮', 'W04/W17/W47',
    '版权行"2026 年 7 月第 1 版"早于在线文献访问日期 [2026-08-14]（实为 25 处——39 条文献中在线 [EB/OL] 25 条，清单原写"39 处"是把总条数当成了访问日期数）——7 月付印的书里印不进 8 月的日期，两处必有一错。核实官裁决反转改侧：访问日期是"最后核实日"的真实数据，伪造不得，25 处保留不动；版次行是待定占位——书稿 2026-09 仍在修订，"7 月付印"不可能成立，改占位一侧为 9 月。书中最晚时间戳 8-14，任何 ≥9 月的版次声明都自洽；连带 ch1 L194 版本状态提示"（2026 年 7 月）"时间线亦自然（7 月核实版本状态、8 月访问链接、9 月付印）', '',
    [dict(ch='后记', line=61, label='版权行版次日期（参考文献 25 处 [2026-08-14] 访问日期不动）',
          old='2026 年 7 月第 1 版',
          new='2026 年 9 月第 1 版')],
    nfix='1 处（实际付印若拖后按实际付印月定稿——版次日期晚于书中一切内容日期即自洽；访问日期保持真实）')

add('MF-41', 'C', False, '参考文献', 'refs L31（[13] 注释）', '1 位', 'V102',
    '"……的说法的直接学术渊源"两个"的"叠用，读出声必绊；同文件 L61 已用"这一"隔开，照抄同一手法即可', '',
    [dict(ch='参考文献', line=31,
          old='本章"接口稳定性比接口优雅更重要"的说法的直接学术渊源。',
          new='本章"接口稳定性比接口优雅更重要"这一说法的直接学术渊源。')])

add('MF-42', 'A', False, '参考文献', 'refs L43（[19] 注释）', '1 位·官方文档', 'V103',
    'Cluster 规范通篇用 PFAIL/FAIL 两级状态做故障检测，SDOWN/ODOWN 是 Sentinel 体系的术语——读者拿它去规范里检索一无所获', '证据：redis.io Cluster Specification 故障检测一节（"two flags … PFAIL and FAIL"）',
    [dict(ch='参考文献', line=43,
          old='16384 槽位哈希分布、Gossip 元数据传播、异步复制与 SDOWN/ODOWN 故障检测的一手规范',
          new='16384 槽位哈希分布、Gossip 元数据传播、异步复制与 PFAIL/FAIL 故障检测的一手规范')])

add('MF-43', 'A', False, '参考文献', 'refs L76（[38]）', '3 位·两轮', 'R10/V098/V103',
    '第 4 版（2022）作者是 Silvia Botros 与 Jeremy Tinley；Schwartz/Zaitsev/Tkachenko 是第 3 版（2012）的作者班子——3 版作者套在 4 版著录上', '证据：O\'Reilly 官方书页（ISBN 9781492080510）',
    [dict(ch='参考文献', line=76,
          old='[38] Schwartz B, Zaitsev P, Tkachenko V. High Performance MySQL[M]. 4th ed. Sebastopol: O\'Reilly Media, 2022.',
          new='[38] Botros S, Tinley J. High Performance MySQL[M]. 4th ed. Sebastopol: O\'Reilly Media, 2022.')])

add('MF-44', 'A', False, '参考文献', 'refs L77（[39]）', '4 位·两轮', 'R10/V097/V098/W11',
    'NetDB\'11 在希腊雅典与 SIGMOD 2011 同址举行（论文页脚自注），不是斯德哥尔摩；原始论文署名顺序 Kreps 在前，书稿把第一、二作者对调', '证据：论文原文 PDF 页脚（"NetDB\'11, Jun. 12, 2011, Athens, Greece"）/ Apache Kafka Books & Papers 页',
    [dict(ch='参考文献', line=77,
          old='[39] Narkhede N, Kreps J, Rao J. Kafka: a Distributed Messaging System for Log Processing[C]//NetDB Workshop. Stockholm, 2011.',
          new='[39] Kreps J, Narkhede N, Rao J. Kafka: a Distributed Messaging System for Log Processing[C]//NetDB\'11 Workshop. Athens, 2011.')])

# ---------------- 三席核实官裁决新增连带条目（MF-45..48，来源 0910/glm/verify/ 三份报告） ----------------

add('MF-45', 'A', False, 'ch10', 'ch10 L104', 'B 核实官·连带', 'B_矛盾核实.md·MF-15 节',
    'io-threads 口径连带：多线程 I/O 默认只拆写回（读需 io-threads-do-reads 显式开启、默认关），"卸载网络读写"与 MF-15/ch1 L62 同病——Grep "多线程 I/O"全书六处中，L104 是除已列两处外唯一含方向性表述的位置（ch1 L126/L135/L196 与 fig-5-7 图内均无方向细节，不动）', '证据：同 MF-15（redis.conf 7.x：io-threads-do-reads 默认 no）',
    [dict(ch='ch10', line=104,
          old='即便 6.0 起可开启多线程 I/O 卸载网络读写，数据访问仍单线程',
          new='即便 6.0 起可开启多线程 I/O 卸载网络写，数据访问仍单线程')])

add('MF-46', 'B', False, 'ch6', 'ch6 L22', 'B 核实官·连带', 'B_矛盾核实.md·MF-17 节',
    'MF-17 改 L15 后的残余第三边："四维在一条请求上依次接力"与原句同款毛病——接力即各跑一段，把旁路的审计又算进接力队伍；锚口径（L22 前句 + 图 6-1 图注）是 TLS→认证→授权→存储加密四段链路接力、审计旁路留痕，"四维"计数与锚不符', '',
    [dict(ch='ch6', line=22,
          old='四维在一条请求上依次接力，缺了哪一段，攻击面就开在哪一段。',
          new='四段在一条请求上依次接力，缺了哪一段，攻击面就开在哪一段。')])

add('MF-47', 'A', False, 'ch9', 'fig-9-3 图内（步骤④）', 'A 核实官·连带', 'A_事实核实.md·MF-27 连带发现',
    '图内文字连带：全量同步分支步骤框"④ 主节点 BGSAVE，fork 子进程生成 RDB"仍是 6.x 落盘口径，与 MF-27 改后正文步骤 1（7.0 起默认无盘复制、RDB 流直写副本连接）图文矛盾——不改图则正文改对了图还是旧的', '证据：同 MF-27（redis/redis 7.0 redis.conf：repl-diskless-sync 默认 yes）',
    [dict(ch='ch9', line=58, file='09-data-sync/diagrams/fig-9-3.svg', label='fig-9-3 步骤④ 图内文字',
          old='④ 主节点 BGSAVE，fork 子进程生成 RDB',
          new='④ 主节点 fork 子进程，RDB 流直发副本连接（默认无盘）')],
    nfix='1 处图内文字（随 MF-27 同步改图，执行时走 svg-illustrator；改后重建 SVG 与 HTML）')

add('MF-48', 'A', False, 'ch8', 'fig-8-5 图内（redo log 框）', 'A 核实官·连带', 'A_事实核实.md·MF-26 连带发现',
    '图内文字连带：redo log 框内"512B 块对齐 / 匹配扇区原子写"仍把扇区原子写当硬件事实陈述，与 MF-26 改后正文（对齐降低跨界写概率 + 块级校验和检出撕裂）同病——不改图则图文一头改一头没改', '证据：同 MF-26（MySQL 官方开发者文档：redo 按 512B 块组织、恢复只取完整记录组）',
    [dict(ch='ch8', line=26, file='08-storage-format/diagrams/fig-8-5.svg', label='fig-8-5 redo 框上行',
          old='512B 块对齐', new='512B 块 · 对齐扇区粒度'),
     dict(ch='ch8', line=27, file='08-storage-format/diagrams/fig-8-5.svg', label='fig-8-5 redo 框下行',
          old='匹配扇区原子写', new='校验和检出撕裂')], styl='文风',
    nfix='2 处图内文字（随 MF-26 同步改图；改后重建 SVG 与 HTML）')

# ---------------- 词级 diff ----------------
CJK = re.compile(r'[\u4e00-\u9fff]')


def tokenize(s):
    toks = []
    i = 0
    n = len(s)
    while i < n:
        c = s[i]
        if CJK.match(c):
            toks.append(c)
            i += 1
        elif c.isspace():
            j = i
            while j < n and s[j].isspace():
                j += 1
            toks.append(s[i:j])
            i = j
        else:
            j = i
            while j < n and not s[j].isspace() and not CJK.match(s[j]):
                j += 1
            toks.append(s[i:j])
            i = j
    return toks


def esc(t):
    return H.escape(t, quote=False)


def render_diff(old, new, side):
    """side='old'：删除侧（删除部分 del）；side='new'：插入侧（新增部分 ins）。返回 HTML。"""
    a, b = tokenize(old), tokenize(new)
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    if sm.ratio() < 0.3:
        # 相似度过低：不强行 diff，纯展示
        txt = esc(old if side == 'old' else new)
        return '<span class="plain">%s</span><span class="nodiff">%s</span>' % (
            txt, '（重写幅度大，不逐词标注，整段为新文本）' if side == 'new' else '（重写幅度大，原文整段被替换）')
    out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            out.append(esc(''.join(a[i1:i2])))
            continue
        seg_old = ''.join(a[i1:i2])
        seg_new = ''.join(b[j1:j2])
        if side == 'old' and seg_old.strip():
            out.append('<del>%s</del>' % esc(seg_old))
        elif side == 'old':
            out.append(esc(seg_old))
        if side == 'new' and seg_new.strip():
            out.append('<ins>%s</ins>' % esc(seg_new))
        elif side == 'new':
            out.append(esc(seg_new))
    return '<span class="plain">%s</span>' % ''.join(out)


def render_plain(s):
    return '<span class="plain">%s</span>' % esc(s)


# ---------------- 校验 ----------------
def verify():
    errs = []
    cache = {}
    for it in I:
        for k, e in enumerate(it['edits']):
            where = e.get('file') or SRC[e['ch']]
            f = os.path.join(BASE, where)
            if f not in cache:
                cache[f] = open(f, encoding='utf-8').read()
            src = cache[f]
            probe = e['old'][:20]
            if probe not in src:
                errs.append('%s edit#%d old 前 20 字未在 %s 命中: %r' % (it['id'], k + 1, where, probe))
            # 整段也应命中
            if e['old'] not in src:
                errs.append('%s edit#%d old 全文未逐字命中 %s' % (it['id'], k + 1, where))
            if e['old'] == e.get('new') or e['old'] == e.get('new2'):
                errs.append('%s edit#%d new 与 old 相同' % (it['id'], k + 1))
    return errs


# ---------------- 渲染 HTML ----------------
def cat_badge(cat, cons):
    name, fg, bg = CAT[cat]
    b = '<span class="badge" style="color:%s;background:%s">%s</span>' % (fg, bg, name)
    if cons:
        b += '<span class="badge cons">共识</span>'
    b += '<span class="vchk">✓核实</span>'
    return b


def edits_col2(it):
    parts = []
    for e in it['edits']:
        label = '位置 %s L%s%s' % (e['ch'], e['line'], ('·' + e['label']) if e.get('label') else '')
        parts.append('<div class="unit"><div class="uloc">%s</div><div class="utext">%s</div></div>'
                     % (esc(label), render_diff(e['old'], e.get('new', ''), 'old')))
    return ''.join(parts)


def edits_col3(it):
    parts = []
    for e in it['edits']:
        label = '位置 %s L%s%s' % (e['ch'], e['line'], ('·' + e['label']) if e.get('label') else '')
        new_html = render_diff(e['old'], e.get('new', ''), 'new')
        if e.get('new2'):
            # 双方案（MF-39）
            n1 = e['new']
            n2 = e['new2']
            tag_a = n1.split('】')[0] + '】' if '】' in n1 else ''
            tag_b = n2.split('】')[0] + '】' if '】' in n2 else ''
            body_a = n1[len(tag_a):] if tag_a else n1
            body_b = n2[len(tag_b):] if tag_b else n2
            html_ = ('<div class="opt">%s%s</div><div class="opt">%s%s</div>'
                     % (esc(tag_a), render_diff(e['old'], body_a, 'new'),
                        esc(tag_b), render_diff(e['old'], body_b, 'new')))
            new_html = html_
        parts.append('<div class="unit"><div class="uloc">%s</div><div class="utext">%s</div></div>'
                     % (esc(label), new_html))
    return ''.join(parts)


def build():
    errs = verify()
    if errs:
        print('!! 校验失败 %d 条：' % len(errs))
        for x in errs:
            print('  ', x)
        sys.exit(1)
    print('校验通过：%d 条 %d 个改动单元 old 文本全部逐字命中书稿源文件。' % (len(I), sum(len(x['edits']) for x in I)))

    nA = sum(1 for x in I if x['cat'] == 'A')
    nB = sum(1 for x in I if x['cat'] == 'B')
    nC = sum(1 for x in I if x['cat'] == 'C')
    nD = sum(1 for x in I if x['cat'] == 'D')
    nE = sum(1 for x in I if x['cons'])

    rows = []
    navs = []
    for ch in CH_ORDER:
        items = [x for x in I if x['ch'] == ch]
        if not items:
            continue
        anchor = CH_ANCHOR[ch]
        navs.append('<a href="#%s">%s<span>%d</span></a>' % (anchor, CH_TITLE[ch].replace('第 ', '第').replace(' 章', '章'), len(items)))
        rows.append('<tr class="grp" id="%s"><td colspan="4">%s<span class="gcount">%d 条</span></td></tr>'
                    % (anchor, CH_TITLE[ch], len(items)))
        for it in items:
            nfix = it.get('nfix') or ('%d 处' % len(it['edits']))
            why = esc(it['why'])
            ev = ('<div class="ev">%s</div>' % esc(it['evidence'])) if it['evidence'] else ''
            styl_txt = '双席文风核' if it['styl'] == '双席' else '文风核'
            styl_html = ('<div class="styl">（表达经%s）</div>' % styl_txt) if it.get('styl') else ''
            rows.append(
                '<tr class="item cat-%s%s" data-cat="%s">'
                '<td class="c1"><div class="mfid">%s</div><div class="loc">%s</div>'
                '<div class="bads">%s</div><div class="hits" title="命中的读者来源">%s</div></td>'
                '<td class="c2"><div class="colhead">原文</div>%s</td>'
                '<td class="c3"><div class="colhead">修改后</div>%s</td>'
                '<td class="c4"><div class="why">%s</div>%s<div class="src">命中：%s</div>'
                '<div class="nfix">改动 %s</div>%s</td></tr>'
                % (it['cat'], ' cons' if it['cons'] else '', it['cat'],
                   it['id'], esc(it['loc']), cat_badge(it['cat'], it['cons']), esc(it['hits']),
                   edits_col2(it), edits_col3(it), why, ev, esc(it['src']), esc(nfix), styl_html))

    css = """
:root{--red:#c62828;--redbg:#fdecea;--orange:#e65100;--orangebg:#fff3e0;--blue:#1565c0;--bluebg:#e8f0fe;--purple:#6a1b9a;--purplebg:#f3e5f5;--green:#0a6b2a;--greenbg:#d6f0d8;--ink:#1c2430;--mut:#5b6675;--line:#dde3ea;--bg:#f6f7f9;--gold:#b8860b}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;font-size:13.5px;line-height:1.65;color:var(--ink);background:var(--bg);padding:14px 16px 60px}
.hd{max-width:1500px;margin:0 auto 10px}
.hd h1{font-size:20px;margin-bottom:6px}
.hd .sub{color:var(--mut);font-size:13px;margin-bottom:8px}
.statbar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-bottom:8px}
.stat{background:#fff;border:1px solid var(--line);border-radius:6px;padding:4px 12px;font-size:13.5px}
.stat b{font-size:16px}
.stat.a b{color:var(--red)}.stat.b b{color:var(--orange)}.stat.c b{color:var(--blue)}.stat.d b{color:var(--purple)}.stat.e b{color:var(--gold)}
.vbar{font-size:13px;font-weight:600;color:var(--green);background:var(--greenbg);border:1px solid #a5d9ad;border-radius:6px;padding:5px 12px;margin-bottom:8px}
.vchk{display:inline-block;font-size:10.5px;color:var(--green);background:var(--greenbg);border:1px solid #bfe3c6;border-radius:4px;padding:0 5px;font-weight:600}
.note{font-size:12.5px;color:var(--mut);background:#eef1f5;border-radius:6px;padding:6px 10px;margin-bottom:4px}
.foot{font-size:12.5px;color:var(--mut);margin-top:14px;border-top:1px dashed var(--line);padding-top:8px;max-width:1500px;margin-left:auto;margin-right:auto}
.toolbar{position:sticky;top:0;z-index:9;background:var(--bg);padding:8px 0;max-width:1500px;margin:0 auto}
.fbtns{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:6px}
.fbtn{border:1px solid var(--line);background:#fff;border-radius:16px;padding:3px 14px;font-size:13px;cursor:pointer;color:var(--ink)}
.fbtn.on{background:var(--ink);color:#fff;border-color:var(--ink)}
.cnav{display:flex;flex-wrap:wrap;gap:4px;font-size:12px}
.cnav a{color:#365;font-size:12.5px;text-decoration:none;border:1px solid var(--line);background:#fff;border-radius:4px;padding:1px 8px}
.cnav a span{color:var(--mut);margin-left:3px}
table{width:100%;max-width:1500px;margin:0 auto;border-collapse:collapse;background:#fff;border:1px solid var(--line);table-layout:fixed}
tr.grp td{background:#e9edf2;font-weight:700;font-size:14px;padding:6px 12px;border-top:2px solid #c8d0da;border-bottom:1px solid var(--line)}
.gcount{font-weight:400;color:var(--mut);font-size:12.5px;margin-left:8px}
tr.item td{border-bottom:1px solid var(--line);vertical-align:top;padding:10px 12px}
tr.item.cons td.c1{box-shadow:inset 3px 0 0 var(--gold)}
.c1{width:118px}.c2{width:31%}.c3{width:31%}.c4{width:auto}
.mfid{font-size:17px;font-weight:800;letter-spacing:.3px}
.loc{font-size:12px;color:var(--mut);margin:2px 0 5px}
.bads{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:5px}
.badge{font-size:11.5px;border-radius:4px;padding:1px 7px;font-weight:600}
.badge.cons{color:var(--gold);background:#fdf6e3;border:1px solid #e6c96a}
.hits{font-size:11.5px;color:var(--mut)}
.colhead{font-size:11px;color:var(--mut);letter-spacing:2px;margin-bottom:4px}
.unit{margin-bottom:10px}
.unit:last-child{margin-bottom:0}
.uloc{font-size:11.5px;color:var(--mut);border-left:3px solid #c8d0da;padding-left:6px;margin-bottom:3px}
.utext{white-space:pre-wrap;word-break:break-word;font-size:13.5px}
del{color:var(--red);background:var(--redbg);text-decoration:line-through;text-decoration-thickness:1.5px;border-radius:2px;padding:0 1px}
ins{text-decoration:none;color:var(--green);background:var(--greenbg);border-radius:2px;padding:0 1px;font-weight:600}
.plain{color:var(--ink)}
.nodiff{color:var(--mut);font-size:12px}
.opt{margin-bottom:8px;padding:6px 8px;border:1px dashed #c8b06a;background:#fffdf4;border-radius:4px}
.why{font-size:13px}
.ev{font-size:12px;color:var(--mut);margin-top:5px}
.src{font-size:12px;color:var(--mut);margin-top:6px;word-break:break-all}
.nfix{font-size:12px;color:#8a5a00;background:#fdf6e3;display:inline-block;border-radius:4px;padding:1px 8px;margin-top:7px}
.styl{font-size:11.5px;color:var(--mut);margin-top:4px}
.hidden{display:none}
.legend{max-width:1500px;margin:6px auto 0;font-size:12.5px;color:var(--mut)}
"""

    js = """
var F='ALL';
function flt(c){
  F=c;
  var bs=document.querySelectorAll('.fbtn');
  for(var i=0;i<bs.length;i++){bs[i].classList.toggle('on',bs[i].getAttribute('data-f')===c);}
  var rs=document.querySelectorAll('tr.item');
  for(var j=0;j<rs.length;j++){
    var ok=(c==='ALL')||rs[j].getAttribute('data-cat')===c;
    rs[j].classList.toggle('hidden',!ok);
  }
  var gs=document.querySelectorAll('tr.grp');
  for(var k=0;k<gs.length;k++){
    var grp=gs[k],nxt=grp.nextElementSibling,vis=false;
    while(nxt&&nxt.classList.contains('item')){if(!nxt.classList.contains('hidden')){vis=true;break;}nxt=nxt.nextElementSibling;}
    grp.classList.toggle('hidden',!vis);
  }
}
document.addEventListener('DOMContentLoaded',function(){
  var bs=document.querySelectorAll('.fbtn');
  for(var i=0;i<bs.length;i++){bs[i].addEventListener('click',function(){flt(this.getAttribute('data-f'));});}
});
"""

    doc = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>必改级问题清单 · 架构观察笔记</title>
<style>__CSS__</style>
</head>
<body>
<div class="hd">
<h1>《架构观察笔记》必改级问题清单（批注对比）</h1>
<div class="sub">两轮读者审查 154 位 / 1400 条意见中筛出的必改级 __TOTAL__ 条 · 生成自 R01–R10 报告 + 夜轮 104 报告 + 本轮 50 报告</div>
<div class="statbar">
<span class="stat"><b>__TOTAL__</b> 条总计</span>
<span class="stat a"><b>__NA__</b> A 事实</span>
<span class="stat b"><b>__NB__</b> B 矛盾</span>
<span class="stat c"><b>__NC__</b> C 文字</span>
<span class="stat d"><b>__ND__</b> D 合规</span>
<span class="stat e"><b>__NE__</b> 叠加 E 共识金边</span>
</div>
<div class="vbar">已通过 3 席核实官技术裁决 + 2 席文风核（16 条合成句去 AI 味改写）：48 条终版</div>
<div class="note">必改级标准（满足其一）：A 技术事实错误（≥2 位读者独立核实，或单席位持官方文档/源码硬证据）；B 书内自相矛盾（两处口径打架，按更准确一侧为锚）；C 三校必标级文字硬伤（错字/叠字/缺字/语序颠倒/残句）；D 法务判"不整改不能付印"；E 两轮合计 ≥5 位独立读者命中且一句话内可改的措辞级共识（金边叠加标示）。风格偏好、P2 级打磨、结构性大手术（加半页内容/加习题/重写段落）与读者间判断相反的未决项一律不收。</div>
<div class="legend">批注图例：原文列 <del>红色删除线</del> = 将被改动的部分；修改后列 <ins>绿底</ins> = 新增或改动后的文字；「〔空行〕」= 补一个空行；相似度过低的重写不逐词标注。</div>
</div>
<div class="toolbar">
<div class="fbtns">
<button class="fbtn on" data-f="ALL">全部 __TOTAL__</button>
<button class="fbtn" data-f="A">A 事实 __NA__</button>
<button class="fbtn" data-f="B">B 矛盾 __NB__</button>
<button class="fbtn" data-f="C">C 文字 __NC__</button>
<button class="fbtn" data-f="D">D 合规 __ND__</button>
</div>
<div class="cnav">__NAV__</div>
</div>
<table>
<thead><tr><th style="width:118px">编号/位置</th><th style="width:31%">原文</th><th style="width:31%">修改后</th><th>说明</th></tr></thead>
<tbody>
__ROWS__
</tbody>
</table>
<div class="foot">注：半同步 ACK 是否等 relay log 落盘（判错 vs 判对 3:3）、AHI 分区引入版本 5.7.8 vs 5.7.2、MySQL AB 创立年份 1995 三处读者分歧未决项未列入本表，详见 wave2/stats.html 冲突区。命中所列 V/W/R 编号分别对应夜轮报告、本轮报告与首轮 R01–R10 挑错报告。<br>核实报告：0910/glm/verify/A_事实核实.md · B_矛盾核实.md · CD_文字合规核实.md；三条裁量备注（MF-04/23/26）见 A 报告<br>文风核报告：0910/glm/verify/AI味检测_新文本.md · 文风对照_新文本.md；MF-19 执行时顺带核 L127 段尾"设为 false"句（文风席附注）</div>
<script>__JS__</script>
</body>
</html>
"""
    doc = doc.replace('__CSS__', css).replace('__JS__', js)
    doc = doc.replace('__TOTAL__', str(len(I))).replace('__NA__', str(nA)).replace('__NB__', str(nB))
    doc = doc.replace('__NC__', str(nC)).replace('__ND__', str(nD)).replace('__NE__', str(nE))
    doc = doc.replace('__NAV__', ''.join(navs)).replace('__ROWS__', '\n'.join(rows))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mustfix.html')
    with io.open(out, 'w', encoding='utf-8') as f:
        f.write(doc)
    print('已生成 %s（%.1f KB）' % (out, os.path.getsize(out) / 1024.0))
    print('分类：A 事实 %d · B 矛盾 %d · C 文字 %d · D 合规 %d · E 共识叠加 %d' % (nA, nB, nC, nD, nE))
    # 按章统计
    from collections import Counter
    cc = Counter(x['ch'] for x in I)
    print('按章：', dict(cc))


if __name__ == '__main__':
    build()
