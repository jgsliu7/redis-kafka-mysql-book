# 三席独立核实 · C席（源码与版本）审核报告

审核人视角：Redis/MySQL/Kafka 开源系统源码贡献者。对象：`0912/glm/items-agg.json` 全部 53 条。
方法：①去掉 ⟦⟧ 标记取特征短语 Grep/Read 书稿逐处定位（以实测 file:line 为准）；②每条涉及的可验证断言落到参数默认值、版本分界、KIP、源码行为层核实；③拿不准或需要出版事实的用 ali-web-search 联网核实（来源在文中标注）。chapters/ 只读，未改任何书稿与清单文件。

## 联网核实记录

| 事实 | 结论 | 来源 |
|---|---|---|
| Kafka KRaft 模式就绪日志 | 实际序列为 `[BrokerServer id=0] Transition from SHUTDOWN to STARTING` → `[BrokerLifecycleManager id=0] Transitioning from STARTING to RECOVERY.` → `[BrokerLifecycleManager id=0] The broker has been unfenced. Transitioning from RECOVERY to RUNNING.`；**不存在** `[BrokerServer id=0] Transition from STARTING to STARTED`（BrokerState 枚举无 STARTED） | github.com/bitnami/charts/issues/16669（KRaft 真实日志）＋AK 源码 org.apache.kafka.server.common.BrokerState 状态集 |
| binlog_transaction_dependency_tracking | 8.0.35 / 8.2 弃用、8.4 移除，移除后多线程复制始终按 writeset 生成依赖 | chenxutan.com/d/6379.html（8.0→8.4 迁移清单，与 Oracle removed-features 页口径一致） |
| High Performance MySQL 4th ed 出版年 | 中译本 2022-10 电子工业出版社；英文原版 O'Reilly 2022-03。2021 为误 | 夸克百科「高性能MySQL（第4版）」条目＋O'Reilly 书页 |
| MySQL 出身 | 1995 年 MySQL AB 公司尚不存在，开发发生在 TCX DataKonsult；MySQL AB 由 Monty/Axmark/Larsson 创立，主流口径 2001 年前后 | 常识＋条目自带的双向证据（本条原本就留作者裁决） |
| Kafka 3.9.0 Tiered Storage | 3.9.0 发布公告将 KIP-405 列为 production-ready（3.6 为 Early Access） | kafka.apache.org 3.9.0 release announcement（与既知一致） |

未联网、凭源码知识核实的项（均为高置信）：Redis aof.c everysec「write 每事件循环迭代、fsync 后台每秒」；6.x `protectedModeEnabled()` 含 `bindaddr_count==0` vs 7.0 `checkProtectedMode()` 无 bind 条件；6.x 命令表位置初始化器 vs 7.0 JSON 生成；`io-threads-do-reads no`、`cluster-allow-reads-when-down no`、`repl-diskless-sync` 7.0 翻转、`save 3600 1 300 100 60 10000`、`sync_relay_log=10000`、`max.in.flight≤5`（幂等下）、KIP-480/794 行为差、sendfile 仅 Fetch 方向且 TLS/降级转换失效、RDB LZF「>20 字节且省 ≥4 字节」、RecordBatch V2 61B/V1 同口径 34B、Linux `read_ahead_kb=128`、`vm.dirty_expire_centisecs=3000`（30s）、MERGE_THRESHOLD 默认 50 可按索引设。

---

## 第 1 章

### V12a（表 1-1 MySQL「可舍弃」格）
- 位置：`chapters/01-introduction/chapter.md:115`，格文本「写性能」逐字存在。✔
- 判定：成立。1.2.2（:82、:84）明说代价是「提交延迟（每次提交都刷盘的配置下）＋调优门槛」；「写性能」三字把有条件代价扩大为无条件，且与 1.1.3（:50 写放大/事务开销/调优门槛）也对不上。
- 改法：认可。定案长版与 1.2.2 逐字同口径；无版本/数字问题。

### V12b（fig-1-1.svg MySQL 盒「舍弃」标签）
- 位置：`chapters/01-introduction/diagrams/fig-1-1.svg:54`，实测标签「舍弃：写入性能」（条目摘录「写性能」，以文件为准）。✔
- 判定：成立，同 V12a。
- 改法：认可。「提交延迟、调优门槛」12 字，与图内另两处「舍弃」行的顿号体例一致；连接词从「与」改「、」更佳。无技术风险。

### V06a（1.2.2 MySQL 起源句）
- 位置：`chapters/01-introduction/chapter.md:74`，「它 1995 年起源于瑞典 MySQL AB」逐字存在。✔
- 判定：成立。「1995 年起源于 MySQL AB」是年代错置——1995 年 MySQL 在 TCX DataKonsult 开发，MySQL AB 公司 2001 年前后才成立（主流口径；条目已注明官方公司史与创始人时间线互斥、留作者裁决，C 席事实侧支持改）。
- 改法：认可。「1995 年由 Michael Widenius 在瑞典 TCX DataKonsult 开发发布，2001 年前后成立 MySQL AB 公司化运营」中「2001 年前后」的模糊化处理恰好覆盖了出处分歧（部分资料记 2000 末注册），措辞稳。

### V06b（表 1-1「出身」格）
- 位置：`chapters/01-introduction/chapter.md:112`，「1995，MySQL AB，经 Sun 入 Oracle」逐字存在。✔
- 判定：成立，同 V06a。
- 改法：认可。「TCX（后 MySQL AB）」短版与 V06a 长版同口径，须与 V06a 同批落地。

### T2（1.4.3 版本基线段补截止声明）
- 位置：`chapters/01-introduction/chapter.md:196`，基线句逐字存在；:198 版本状态提示（2026 年 9 月）确认已含 Kafka 4.0 去 ZK、MySQL 8.0 Sustaining Support，故不重复。✔
- 判定：成立。全书 Grep 无 Valkey/许可证内容，「信息核对截止时间」声明也确缺（参考文献最晚 [2026-09-09]）。
- 改法：认可。「Redis 许可证变更与 Valkey 分叉」所指事件真实（2024 双许可变更与 Valkey 分叉、2025 Redis 8 增 AGPLv3），只用事件名不展开，不会误导 7.0 基线读者；「2026 年 9 月」与版本状态提示及参考文献时间戳自洽，取「年初」反而自相矛盾（条目说明正确）。

### MF-02（ch1 L51-52 列表后无空行）
- 位置：`chapters/01-introduction/chapter.md:51-52`，Kafka 列表项与「这三组设计……」总起句之间无空行，逐字确认。✔
- 判定：成立。CommonMark lazy continuation 会使总起句并入 Kafka 条目。
- 改法：认可。纯格式加固，零技术风险。

---

## 第 2 章

### V04a（2.3.3 零拷贝句加限定）
- 位置：`chapters/02-data-structures-protocols/chapter.md:172`，整句逐字存在。✔
- 判定：成立。源码层：sendfile 快路径（`TransportLayer.transferTo`）只服务 Fetch/日志发送方向；`SslTransportLayer` 不支持 transferTo（TLS 加密必须过用户态 SSL 引擎）；消费者请求旧消息格式触发 down-conversion 时在 `KafkaApis` 层做用户态转换，均使数据回用户态。Produce 方向本就不走 sendfile。
- 改法：认可。「仅消费方向成立，且要求明文传输、消息格式无需降级转换」三点全部与实现一致；未加前向引用，合规。

---

## 第 3 章

### V09a（导读补 SIGKILL 机理）
- 位置：`chapters/03-lifecycle/chapter.md:5`，句逐字存在。✔
- 判定：成立。SIGKILL 不可捕获、内核立即终止进程，语义表述准确。
- 改法：认可。导读级一句话，「没来得及落盘的写入就此丢失」在导入语境可接受（严格说进程被杀只丢未 write() 出去的缓冲，已在 V09d 处给出精确修正，导读不必背这个包袱）。

### V09b（3.1「只是丢几秒数据」补前提）
- 位置：`chapters/03-lifecycle/chapter.md:15`，句逐字存在。✔
- 判定：成立。7.x 出厂默认 `appendonly no`、save 点为 3600 1 / 300 100 / 60 10000；RDB-only 下 kill -9 丢「自上次成功快照起」的写入，写入稀疏时丢近一小时属实。everysec「窗口约一秒」是 redis.conf 官方口径，与 ch4:101 现文一致。
- 改法：认可。两点推算均与 4.2/8.2 现文口径吻合。技术备注（不阻塞落地）：everysec 下进程被杀的真实丢失通常小于一秒（详见 V09d 条）——「约一秒」作为官方口径上界可保留，不必在此展开。

### V09c（表 3-1 档位 2 格补界线）
- 位置：`chapters/03-lifecycle/chapter.md:114`，格文本逐字存在。✔
- 判定：成立。`innodb_fast_shutdown=2` 只做日志 flush、跳过脏页刷盘/purge/change buffer 合并（类崩溃），但 mysqld 关闭序列仍有序执行，redo 已刷；`innodb_flush_log_at_trx_commit=1` 下已提交事务不丢。原格「近乎 kill -9」确实需要这道硬界线。
- 改法：认可。:71 处「只有 SIGKILL……跳过所有清理逻辑」核对为正确语义，不需改（条目处置正确）。

### V09d（3.6 事故复盘句重写）
- 位置：`chapters/03-lifecycle/chapter.md:245`，两句原文逐字存在。✔
- 判定：**成立**，且必须改——「没等 AOF 刷完就杀了进程」语义错乱（kill -9 根本不存在「等/不等刷完」的选择权）。
- 改法：**修正后认可**。方向（统一 SIGKILL 语义、保留第一人称故事）对，但两处机制表述在源码层不准：
  1. 「AOF 缓冲区里**还没 fsync** 的写入随进程一起消失」——错。everysec 档 `write(2)` 在每个事件循环迭代（beforeSleep）同步完成，只有 `fsync` 由后台线程每秒做；进程被杀时**已 write() 未 fsync 的数据留在内核页缓存中，重启后不丢**（antirez《Redis persistence demystified》与 aof.c flushAppendOnlyFile 均如此）。随进程消失的只是**还没 write() 出去的 aof_buf 存量**。
  2. 「丢的正是最后一次 fsync 之后那约一秒的写入」——这是**机器断电**的丢失口径，不是 kill -9 的。进程级丢失窗口=最后一次 write() 之后的未落盘缓冲（正常路径约一个事件循环迭代；后台 fsync 卡住被迫延迟写时最坏约 2 秒）。十几条订单要丢，必须恰好压在同一个未 flush 的批次里——「十几条恰好在窗口里」在这个口径下依然讲得通。
  - 具体修正措辞（替换第二处插入句）：
    「当时 AOF 开着，`appendfsync` 是默认的 `everysec`，丢的正是还压在进程输出缓冲里、没来得及写出到 AOF 文件的那批写入，十几条订单恰好都落在这一批里（已写入文件、尚未 fsync 的部分留在内核页缓存，进程被杀并不丢；要丢那一秒量级，得是机器断电）。」
    第一处插入句中「还没 fsync 的写入」改为「还没写出到文件的写入」。
  - 若作者嫌括号太重可删括号，但「还没 fsync 的写入随进程消失」必须改，否则是把断电口径安在进程崩溃上，恰是本书 4.2 反复划线的同类混淆。

### MF-06（Kafka 就绪日志按模式区分）
- 位置：`chapters/03-lifecycle/chapter.md:152`，「`[KafkaServer id=0] started` 这条就绪日志」逐字存在。✔
- 判定：**成立**。`[KafkaServer id=0] started` 是 ZK 模式 KafkaServer.startup() 收尾日志；KRaft 模式跑 BrokerServer，不打印它。运维照书 grep 必失灵，问题真实且严重。
- 改法：**修正后认可**。诊断与「按模式 grep」结构对，但给出的 KRaft 就绪日志字符串错：**不存在** `[BrokerServer id=0] Transition from STARTING to STARTED`（BrokerState 枚举是 NotRunning/Starting/Recovery/Running/…，无 STARTED）。真实 KRaft 序列（bitnami/charts#16669 实测日志）：
  - `[BrokerServer id=0] Transition from SHUTDOWN to STARTING`
  - `[BrokerLifecycleManager id=0] Transitioning from STARTING to RECOVERY.`
  - `[BrokerLifecycleManager id=0] The broker has been unfenced. Transitioning from RECOVERY to RUNNING.` ← 就绪标志
  - 修正措辞：「ZK 模式是 `[KafkaServer id=0] started`，KRaft 模式是 `[BrokerLifecycleManager id=0] The broker has been unfenced. Transitioning from RECOVERY to RUNNING.`，写就绪脚本时按模式 grep 对应那条。」（若嫌长，可简写为 `Transitioning from RECOVERY to RUNNING`。）
  - 该字符串在 3.3–3.9 稳定；证据日志为 3.4 期，3.9 无 KIP 改动此行（如有疑虑可在落地后 grep 一次 3.9 实机日志）。

---

## 第 4 章

### V14（4.1 关键数字框 6.4GB 语义）
- 位置：`chapters/04-memory-disk/chapter.md:38`，句逐字存在。✔
- 判定：成立。`vm.dirty_background_ratio=10` 是**触发线**不是预留缓冲深度；分母为「可用内存」（内核 global_dirtyable_memory＝free＋可回收 file LRU，「free 页加可回收页」是合格简化）；全局阈值经 BDI 机制按各盘写带宽份额分摊；`vm.dirty_expire_centisecs` 默认 3000（30s），稳态脏页量≈写入速率×过期时间的建模成立。
- 改法：认可。新增每个数字（10% 触发线、30 秒、按份额分摊）均与内核实现/默认值一致；「JBOD 单盘窗口更小」正确（per-BDI 阈值随份额缩）。

### V11（表 4-1 延迟/吞吐双量纲重组）
- 位置：`chapters/04-memory-disk/chapter.md:21-28`（表）＋:30（表后首段），各行逐字存在。✔
- 判定：成立。同一「相对内存」列混排延迟倍数与带宽比较，且带宽比较的锚（单线程内存随机读几百 MB/s）是延迟约束的单流上限、不是内存带宽——原表「SATA 档约相当于单线程内存随机读」属跨量纲错位。
- 改法：认可（数值侧逐项换算）：内存顺序带宽 20–100GB/s 量级对（DDR4/DDR5 双通道 42–90GB/s，服务器多通道更高）；SATA 300–500MB/s 对锚点低 1.6–2.5 个量级，标「约低 1–2 个数量级」合格；Gen3 3GB/s 对 20–100GB/s 约 0.8–1.5 个量级，标「约低 1 个数量级」合格；Gen4/Gen5 进入一个量级内成立；机械盘 100–280MB/s 对约 30GB/s 略超两个量级，标「约低 2 个数量级」保守方向正确。表后首段改写与新锚点一致；ch4:194「内存随机读单线程约几百 MB/s」自明为跨口径参照，不冲突（条目说明正确）。

### V04b（图 4-6 标题三处改「消费路径的零拷贝（sendfile）」）
- 位置：`chapters/04-memory-disk/chapter.md:208、210、211` 三处短语逐字齐。✔ fig-4-6.svg 实查：图内无「生产-存储-消费」标题文字，小节标题已是「传统 read() + write()」「零拷贝 sendfile()」口径，SVG 确实无需改（条目说明正确）。
- 判定：成立（同 V04a 依据：sendfile 仅 Fetch 方向）。
- 改法：认可。三处必须同批（alt 文本与图注合并渲染），条目已按三处给出。

### V04c（图 4-6 说明段末补失效条件）
- 位置：`chapters/04-memory-disk/chapter.md:212`，插入锚「它生效的前提是数据已经缓存在 PageCache 里，冷数据仍要先等磁盘 I/O。」逐字存在。✔
- 判定：成立（TLS 用户态加解密、down-conversion 回用户态，同 V04a 源码依据）。
- 改法：认可。两句构成「前提＋失效」闭环；挂靠本章导读取舍框架为后向，合规。

### V02a（表 4-3 Kafka 持久化机制格拆层）
- 位置：`chapters/04-memory-disk/chapter.md:246`，格文本逐字存在。✔
- 判定：成立。acks 是写入确认不是本地持久化机制，与 ch4:218、ch4:286 已划清的界一致。
- 改法：认可。「本地：OS 异步刷盘；跨节点：生产者 acks + 副本兜底」与 4.7 小结口径一致，无新数字。

### V10（appendfsync always「批」定义加注）
- 位置：`chapters/04-memory-disk/chapter.md:100`，条目原文逐字存在。✔
- 判定：成立（防误读加注）。源码侧：always 档在 beforeSleep 的 flushAppendOnlyFile 里 write+fsync，位于回复写出（handleClientsWithPendingWrites）之前，「批」＝本次事件循环迭代积累的 aof_buf，pipeline 多条共用一次、也可能只有一条——加注与实现完全一致。
- 改法：认可。无新数字风险；ch10:76 复用同措辞无需同步改动（条目说明正确）。

### MF-09（导读 Query Cache 括注）
- 位置：`chapters/04-memory-disk/chapter.md:9`，句逐字存在。✔
- 判定：成立。Query Cache 5.7.20 弃用、8.0 移除，属实。
- 改法：认可。括注只陈述移除事实，指向第 5 章为章级引用，合规。

### MF-12（修改缓冲语序）
- 位置：`chapters/04-memory-disk/chapter.md:172`，句逐字存在。✔
- 判定：成立。「二级索引的非唯一索引」字面歧义；change buffer 适用范围＝非唯一二级索引，「非唯一的二级索引」是规范表述，语义不变。
- 改法：认可。

### MF-13（预读「下几 MB」改「一段数据」＋128KB）
- 位置：`chapters/04-memory-disk/chapter.md:202`，句逐字存在。✔
- 判定：成立。Linux `read_ahead_kb` 默认 128（KB），「下几 MB」与默认值差一个量级以上，且与 ch4:256/258「预读大小可调」自相矛盾。
- 改法：认可。「默认预读窗口约 128KB，调优后可到 MB 级」与内核默认值及调优实践一致。

### MF-14（五条图注补句号）
- 位置：ch4:88（图 4-2）、:115（图 4-3）、:149（图 4-4）、:163（图 4-5）、:211（图 4-6）五处图注逐字齐，均无句号；:115/149/163/211 图注与下段无空行属实。✔
- 判定：成立（体例统一，纯排版）。
- 改法：认可。注意条目 diff 只加句号、未补空行（说明里提到的空行问题不在本条 diff 内），落地时按 diff 为准即可。

---

## 第 5 章

### V08（命令表「改遍所有命令的声明」句重写）
- 位置：`chapters/05-layered-architecture/chapter.md:62`，句逐字存在；同段首行 :53 已写明 7.0 JSON 化，原句与之自相矛盾属实。✔
- 判定：成立，且是源码级精确的病理：6.x `redisCommandTable` 是**位置初始化器**数组（`{"get",getCommand,2,"rF",0,NULL,…}`），给 `redisCommand` 结构体加一个字段必须动全表每行；而「加一个标志位」本来就不需要动全表（sflags 按命令自带），原句把两件事混为一谈。7.0 起表由 `commands/*.json` 生成，加字段改生成器即可。
- 改法：认可。「新增一类横切标志要逐一审定受影响命令的元数据；6.x 时代加结构体字段才需动全表」这个拆分在实现层准确。「7.0 的 JSON 化正是为消除这一代价」——重构动机还包括文档/CLI hints 单一事实源，「正是为」略强，但生成化消除全表手改是重构的直接效果之一，可接受（不再要求软化）。

### MF-15（多线程 I/O 方向修正，三处）
- 位置：ch5:45（「把协议的**读写**…这一句话也解释了为什么…」两句逐字存在）、ch1:64（「加速网络读写」逐字存在）；第三处 ch10:110 归 MF-45。三处齐。✔
- 判定：成立。`io-threads` 默认 1（关闭）、`io-threads-do-reads` 默认 no——默认开启时只拆写回、读须显式打开，「卸载/加速网络读写」与实现不符；「单线程内存模型解释了默认关闭多线程 I/O」因果错位（I/O 线程不碰内存模型）。
- 改法：认可。三处改法均只收紧方向词并补 `io-threads-do-reads` 默认关，与源码/redis.conf 一致；「官方就把它留成了可选优化」与 redis.conf 官方建议（非瓶颈不开）一致。

---

## 第 6 章

### V03（protected-mode 判定句改正向三条件＋版本注）
- 位置：`chapters/06-security/chapter.md:112`，句逐字存在。✔
- 判定：成立。7.0 源码（server.c `checkProtectedMode`）：protected_mode 开＋default 用户 nopass＋对端非回环 → 拒绝，无 bind 条件，现文否定式表述易绊倒读者属实。版本注：6.x `protectedModeEnabled()` 确含 `bindaddr_count == 0`（显式 bind 后保护模式整体失效），7.0 移除——与 redis.conf 自 3.2 以来的旧措辞（「未显式 bind 且无密码」）对得上，「6.2 及更早/7.0 起」分界正确。
- 改法：认可。三条件表述与 7.0 实现一致；「回环地址（loopback）」首现中英对照合规。unix socket 连接实际也视为本地放行，属可接受省略。删句方案留作者裁决的处置不变。

### MF-17（「四个层面各覆盖一段」改「前三层」）
- 位置：`chapters/06-security/chapter.md:15`，句逐字存在。✔
- 判定：成立（逻辑互斥：审计贯穿全程，不能「各覆盖一段」）。
- 改法：认可。

### MF-46（「四维依次接力」改「四段」）
- 位置：`chapters/06-security/chapter.md:30`（条目写 L22，实测 30，行号漂移），句逐字存在。✔
- 判定：成立。「四维」含审计，接力队伍把旁路算进去；前句链路 TLS→认证→授权→存储加密恰为四段。
- 改法：认可。「四段」与锚口径对上。

---

## 第 7 章

### V01a（7.3 半同步「接收并刷盘」）
- 位置：`chapters/07-cluster/chapter.md:100`，「半同步等待指定数量的副本将日志接收并刷盘」逐字存在。✔
- 判定：成立。半同步副本 ACK 在 I/O 线程把事件写入 relay log 文件后即发，不等 fsync（由 `sync_relay_log` 控制，默认 10000）、更不等回放。「并刷盘」失实。
- 改法：认可。「接收并写入 relay log 后回 ACK」准确；7.5 的「半同步等待副本保存日志」（ch7:207）措辞中性，不改的处置正确。五处 V01 须一次改齐（本条 a/b/c＋ch9 d/e，均确认在位）。

### V01b（7.3.2「并落盘后就回 ACK」）
- 位置：`chapters/07-cluster/chapter.md:119`，句逐字存在。✔
- 判定：成立（同 V01a）。
- 改法：认可。「写入 relay log 文件后即回 ACK」与实现一致；未加 sync_relay_log 括注、留 V01d 统一补，处置合理。

### V01c（fig-7-1.svg 副本日志标签）
- 位置：`chapters/07-cluster/diagrams/fig-7-1.svg`「副本日志落盘确认；超时可降级」文字行（y=306，条目写 :56，实测该 text 约在 :58，行号漂移）。✔
- 判定：成立（同 V01a）。
- 改法：认可。「副本写入 relay log 后回 ACK」短版准确；宽度问题走 svg-checker 流程（非本席职责）。

### V18a（7.2.3 少数派「停止写入」改「停止读写服务」）
- 位置：`chapters/07-cluster/chapter.md:92`，句逐字存在；句尾「我更关心停止写入的条件」与 fig-7-1.svg:42「少数派超时后停写（见 7.2.3 节）」确认仍在（条目施工注意已列）。✔
- 判定：成立。cluster.c processCommand：集群状态非 OK 时对所辖槽读写命令一律 `-CLUSTERDOWN`，仅 `cluster-allow-reads-when-down yes`（默认 no）放行读。`cluster-node-timeout` 默认 15000ms 正确。
- 改法：认可。参数名、默认值、CLUSTERDOWN 行为全部与实现一致。

### V18b（表 7-1 Redis 格「停写」）
- 位置：`chapters/07-cluster/chapter.md:202`，格文本逐字存在。✔
- 判定：成立（同 V18a）。
- 改法：认可。「停止读写（CLUSTERDOWN）」准确，与 MySQL 格「读取可能陈旧」形成对照。

### V17（7.1 关键数字框 MGR 组规模）
- 位置：`chapters/07-cluster/chapter.md:42`，框文本逐字存在。✔
- 判定：成立。MGR 组成员数上限 9（硬限制），1–9 任取，偶数规模合法但不多容错（⌊(N−1)/2⌋：4 成员仍容 1）。原粗体把奇数推荐写成许可取值集。
- 改法：认可。「组成员数最多 9 个（1–9 任取），生产上通常取 3/5/7/9 等奇数规模」＋偶数例全部属实；7.5「最多支持 9 个」（ch7:216）口径一致。

### T1+N11（7.4.1 粘性分区版本归属）
- 位置：`chapters/07-cluster/chapter.md:156`，「在本章的 3.9 基线中」逐字存在；全书 Grep 该短语仅此 1 处。✔
- 判定：双病均成立。「本章的 3.9」指代不明（第 7 章无 3.9 小节）；批满才换是 3.3 起 KIP-794 行为，KIP-480（2.4）原行为是「批就绪（满或 linger 到时）即换」。
- 改法：认可。KIP-480「批就绪即换」/KIP-794（3.3）「batch.size 攒满才换」与两份 KIP 的行为描述一致；「本章行为描述以 Kafka 3.9 为准，版本基线约定见 1.4.3」为后向引用且不与 1.4.3（基线 Kafka 3.x、3.9+ 限分层存储）冲突，与 ch7:186 既有口径一致。

### V15a（7.3.1 COMMIT_ORDER 括注）
- 位置：`chapters/07-cluster/chapter.md:115`，句逐字存在。✔
- 判定：成立（防误读补注）。8.0 的 COMMIT_ORDER 按提交窗口重叠生成依赖、不限同一次组提交是 8.0 行为（8.0.35 前默认档）；「低并发时窗口重叠的事务基本就是同一次组提交的成员」为合理的工程性括注。
- 改法：认可。孪生句 V15b（ch9:179）须同批（条目说明正确），本条为 ch7 侧。

### MF-22（ch7 L59「可以从从节点」）
- 位置：`chapters/07-cluster/chapter.md:59`，句逐字存在；全书 Grep「从从」正文仅此一处（其余已修，条目施工警告属实）。✔
- 判定：成立（双 cóng 绊读，纯措辞）。
- 改法：认可。只动此一处，勿动 :67 与 ch9（与条目警示一致）。

---

## 第 8 章

### V07（8.5.2 定长页浪费归因重写）
- 位置：`chapters/08-storage-format/chapter.md:275`，句逐字存在。✔
- 判定：成立。16KB 页的固定结构开销约每页 128B 量级，不足以解释半空页；半空页主因是页分裂与删除留洞，且可治理：MERGE_THRESHOLD（默认 50，可按索引 `COMMENT 'MERGE_THRESHOLD=…'` 调）、在线重建索引回收。innodb_defragment 为 MariaDB 专有、MySQL 8.0 无——不写它是对的。
- 改法：认可。归因、阈值名、治理手段全部属实。

### V19（8.1.3 RDB「压缩比」框归因重写）
- 位置：`chapters/08-storage-format/chapter.md:48`，框文本逐字存在。✔
- 判定：成立。源码侧：每键内存结构开销（robj×2＋SDS 头＋dictEntry＋桶摊销）约 66–110B/键量级，小键值负载下这笔开销占内存大头而完全不落盘——这是 RDB 文件远小于内存占用的主因；次因变长整数编码＋LZF，LZF 触发条件（值 >20 字节且至少省 4 字节）与 rdb.c 的 `len > 20` 与 `outlen = len - 4` 判定一致。
- 改法：认可。框题改「内存/磁盘占用比」名实相符；数字 300–500MB 保留、66–110B 带「约」、LZF 双条件准确。

### V05（8.4.6 Tiered Storage 加注出处）
- 位置：`chapters/08-storage-format/chapter.md:233`，句逐字存在。✔
- 判定：成立（结论本身无误，加注止争）。3.9.0 发布公告确实将 KIP-405 Tiered Storage 列为 production-ready（3.6 起为 Early Access）。
- 改法：认可。括注并入 KIP-405 括号内，不改变结论；ch1/ch5/ch9 三处版本表述已核对一致（条目说明属实）。

### W07（8.4.3 批头 61B 分摊句）
- 位置：`chapters/08-storage-format/chapter.md:195`，句逐字存在；与 ch8:46（26/34 同口径）、ch8:191（61 字节）核对同口径，一致。✔
- 判定：成立。V2 批头 61B（8+4+4+1+4+2+4+8+8+8+2+4+4）、V1 单条同口径 34B（外框 12＋消息头 22）均对；单条成批 V2 总开销（61＋单记录 ~9–10B）高于 V1 的 34B，三条起反超（3×34=102 > 61+3×~10≈91）换算成立，与 KIP-98 的口径一致。
- 改法：认可。两个数字与书内既有口径统一，无自相矛盾。

---

## 第 9 章

### V01d（9.3 半同步句＋sync_relay_log 补句）
- 位置：`chapters/09-data-sync/chapter.md:157`，句逐字存在，插入点（「才返回成功。」与「它有两档等待时点。」之间）干净。✔
- 判定：成立（同 V01a）。`sync_relay_log` 8.0 默认 10000（每累计一万条事件 fsync 一次），=1 才逐事件 fsync，与官方文档口径一致。
- 改法：认可。补句与 9.2（:113）、9.4（:239）的免责口径对齐；与 V01e 成对。

### V01e（fig-9-5.svg ACK 框文字）
- 位置：`chapters/09-data-sync/diagrams/fig-9-5.svg:71`，「回 ACK 给主（已写 relay log 并落盘）」逐字存在。✔
- 判定：成立（同 V01a）。
- 改法：认可。「已写 relay log 文件」更短，降低溢出风险；若 T5 重画另议。

### V02b（9.4 acks=all 退化句）
- 位置：`chapters/09-data-sync/chapter.md:239`，句逐字存在。✔
- 判定：成立。`min.insync.replicas=1` 且 ISR 收缩至 Leader-only 时写入放行（1≥1），`acks=all` 只等 Leader 本地确认——退化接近 `acks=1`，语义正确。
- 改法：认可。与 V02a 联动口径一致；ch1:96「不丢前提」为条件式表述，不改的处置正确。

### V15b（9.3 MTS 段末补分层句）
- 位置：`chapters/09-data-sync/chapter.md:179`，「副本按主节点提供的依赖信息调度，无须重新推导全部行级依赖。」逐字存在。✔
- 判定：成立。`binlog_transaction_dependency_tracking`（COMMIT_ORDER/WRITESET）在主节点侧生成 last_committed/sequence_number 标记；`LOGICAL_CLOCK`（replica_parallel_type）是副本侧调度器——分属两层，读者确实易混。
- 改法：认可。与 V15a（ch7:115）同批、措辞一致是验收条件；与 T2b 括号注同段，两句连读无冲突。

### V20（9.2 无盘同步版本注）
- 位置：`chapters/09-data-sync/chapter.md:71`，句逐字存在。✔
- 判定：成立。`repl-diskless-sync` 默认值 no→yes 翻转在 7.0.0，书对 7.x 基线正确，补 6.x 差异注兑现 1.4.3 承诺。
- 改法：认可。

### T2b（binlog_transaction_dependency_tracking 括号注）
- 位置：`chapters/09-data-sync/chapter.md:179`，「`WRITESET` 还可以根据写集识别互不冲突的事务，扩大可并行范围。」逐字存在；全书 grep 无该参数名（首次点名）。✔
- 判定：成立。联网核实：8.0.35/8.2 弃用、8.4 移除，移除后多线程复制始终按 writeset 生成依赖（chenxutan.com/d/6379.html，与 Oracle removed-features 页一致）。8.4 用户若照旧设该参数确实会启动失败，注有实用价值。
- 改法：认可。「移除后一律按 WRITESET 写集推导依赖」与核实结果一致；对 8.0.x 基线读者不误导（明确说了「MySQL 8.4 起已移除」）。

---

## 第 10 章 / 后记 / 参考文献

### W05（练习二幂等默认注）
- 位置：`chapters/10-summary/chapter.md:129`，句逐字存在。✔
- 判定：成立。`enable.idempotence` 自 3.0（KIP-679）默认 true；书内 acks 默认变化已标两处而幂等默认零处，确为缺口。练习句本身「要求 acks=all、retries>0、max.in.flight≤5，冲突配置会报错」在 3.x 与 KIP-679 校验规则一致。
- 改法：认可。注与 ch7:174「自 Kafka 3.0 起成为默认，对应 KIP-679」口径一致。

### MF-33（导读「前九章/八个主题」对账）
- 位置：`chapters/10-summary/chapter.md:5`，句逐字存在；表 10-1 实测 9 行（第 1–9 章）。✔
- 判定：成立。第 2–9 章＝8 个主题章＋第 1 章引入，「前九章」与「八个主题」需要对账才能对上。
- 改法：认可。「第 1 章引入三个样本、第 2 到 9 章每章一个主题」计数正确。

### MF-45（维度四「卸载网络读写」改「写」）
- 位置：`chapters/10-summary/chapter.md:110`（条目写 L104，实测 110），句逐字存在。✔
- 判定：成立（同 MF-15 依据）。与 MF-15 三处同批。
- 改法：认可。

### W08（版权句改写）
- 位置：`chapters/10-epilogue.md:63`，句逐字存在。✔
- 判定：成立。NC 条款与商业出版结构性冲突为真；「未经许可不得用于商业用途」与出版发行矛盾。
- 改法：**修正后认可**。两层问题：
  1. 条目把授权对象 URL 写为 `gitee.com/flainliu/redis-kafka-mysql-v2`（与实测 git remote 一致），但同文件 :71 勘误链接现行文本是 `https://gitee.com/flainliu/redis-kafka-books`——落地后同文件出现两个不同仓库地址，自相矛盾。须二选一统一（:63 与 :71 同批对齐），不能只改一处。
  2. 本条本质是出版/法务决策（条目自己也标注留作者与出版方）。C 席只确认事实层：remote 实测为 redis-kafka-mysql-v2；改法方向（出版版保留所有权利＋仓库草稿走 CC）法律上自洽，可执行。
- 修正：落地时 :63 与 :71 的仓库地址统一为同一 URL（以作者最终公开仓库为准）。

### MF-40（版权行月份 7→9）
- 位置：`chapters/10-epilogue.md:65`（条目写 L61，实测 65），「2026 年 7 月第 1 版」逐字存在。✔
- 判定：成立。实测参考文献 [EB/OL] 类访问日期含 2026-08-14（20 处）与 2026-09-09（在 [14] 等处），7 月付印装不进这些日期；书稿 2026-09 仍在修订（本次审核即是），版次行是占位一侧。
- 改法：认可。改 9 月后自洽（最晚时间戳 09-09 < 9 月付印）；若付印再拖按实月定，与条目口径一致。

### MF-41（参考文献 [13] 双「的」）
- 位置：`chapters/11-references.md:31`（[13] 行），「……更重要"的说法的直接学术渊源」逐字存在。✔
- 判定：成立（纯文体，无技术内容）。
- 改法：认可。「这一」手法与 [31] 行既有用法一致。

### MF-43Y（High Performance MySQL 4th 年份 2021→2022）
- 位置：`chapters/11-references.md:76` 附近（[38] 行，实测约 :77），「O'Reilly Media, 2021」逐字存在。✔
- 判定：成立。第 4 版英文原版 2022 年（O'Reilly 2022-03），中译本 2022-10 电子工业出版社；2021 为误。
- 改法：认可。只改年份，其余著录不动。

---

## 汇总

- 53 条全部在书稿实测定位（含 V01 五处、V04b 三处、MF-15 三处、MF-14 五处逐处核对齐）。
- 成立 53 / 不成立 0 / 存疑 0。
- 认可 50 / 修正后认可 3（V09d：everysec kill -9 丢失归因须从「fsync 缺口」改为「未 write() 出去的缓冲」；MF-06：KRaft 就绪日志字符串应改为 `[BrokerLifecycleManager id=0] The broker has been unfenced. Transitioning from RECOVERY to RUNNING.`；W08：授权对象 URL 须与后记 :71 勘误链接统一）/ 不认可 0。
- 行号漂移已按实测修正：V06a(74)、V12a(115)、V09d(245)、MF-45(110)、MF-40(65)、MF-46(30)、MF-15 ch1(64)、V01c(≈58)、MF-43Y(≈77)。
