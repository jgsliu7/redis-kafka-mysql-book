# 0913 三席核实 · A 席报告（技术事实与断言边界）

> 状态：已完成 · 判定 14/14 存在、14/14 改法认可（含执行级附注）
> 取证说明：对 6 个关键争议点做了在线一手取证——Redis 7.2.0 src/t_set.c + redis.conf、Redis 7.0.0 evict.c/db.c、Kafka 3.9.0 KafkaRaftServer.scala/KafkaBroker.scala、Kafka 3.9.0 官方发布公告、MySQL 8.0 官方手册 InnoDB 物理结构页。未在线取证的条目标注证据等级。所有引文均已对照现行书稿逐字核验。

## 逐条明细

**G1 | 存在：是 | 引文：逐字 | 改法：认可（附一项配套要求） | chapters/02-data-structures-protocols/chapter.md:22**
MySQL 8.0 官方手册原文："InnoDB tries to leave 1/16 of the page free for future insertions and updates……sequential order, the resulting index pages are about 15/16 full. If records are inserted in a random order, the pages are from 1/2 to 15/16 full"——页从不有意装满，随机插入还常约半满，正文"每一页都装满了索引键，而不是半页索引半页无用数据"与官方行为相反，且页内本就有 FIL 头尾、Page Directory 等管理字节。改稿各句均成立（默认 16KB、内部节点多键高分支、"通常可以复用解析结果"与本章 154/213 行既有口径一致）。**但**改稿新增"页内仍有……供后续写入使用的空闲空间"与 2.2.2 开头 89 行"让每一次磁盘 I/O 读上来的 16KB，每一个字节都有用"正面冲突，该行不在 14 条清单内（见清单外发现 1，须配套处理）。

**G2 | 存在：是 | 引文：逐字 | 改法：认可 | chapters/02-data-structures-protocols/diagrams/fig-2-6.svg:25**
"装满键"延续正文错误且图内自相矛盾——根节点例只画 1 个键 [30] 加 2 个指针，谈不上装满。"键与指针"与根节点框内"只存键 + 子节点指针"口径一致；4 个 9px 字在 70px 角标框内不超宽。

**G3 | 存在：是 | 引文：逐字 | 改法：认可 | chapters/02-data-structures-protocols/chapter.md:76**
已取 Redis 7.2.0 源码核对：intset 收到非整数时，须 `intsetLen < 128` 且新成员 `len ≤ 64`（set-max-listpack-value）且 `lpSafeToAdd` 才转 listpack，否则 `setTypeConvertAndExpand` 直转 HT；listpack 后续 `lpLength ≥ 128` 或新成员 >64B 也转 HT。边界逐例吻合（现集合 127 个+新成员→listpack；128 个+新成员→HT），redis.conf 默认 128/64 与改稿一致；7.2 前直转 HT 亦符合 7.0 行为。原句"小集合先转 listpack"对 65 字节成员、129 元素集合两 case 都给出错误走向，问题成立。

**G4 | 存在：是 | 引文：偏差 | 改法：认可（需渲染复核） | chapters/02-data-structures-protocols/diagrams/fig-2-5.svg:61-69**
original 列的 ⟦⟧ 拼读不能精确还原现文（路径二拼出"纯整数超intsett直达hashtable"类碎块，是 diff 对齐噪声），但其所指文本（"混入非整数成员""元素数 > 128"标注及两处注释）在现文中逐字存在，已直接读 SVG 核实。三条新标注与 t_set.c 条件一一对应，且与 G3 改稿及未动的 78 行（>512 直转 HT）口径一致；建议自注的渲染宽度复核应执行——">128 个或成员 >64B"约 95px，逼近两箭头 111px 间距上限。

**G5 | 存在：是 | 引文：逐字 | 改法：认可 | chapters/02-data-structures-protocols/chapter.md:125**
baseTimestamp 是首条记录时间戳、作全批差值基准；生产者时间戳允许乱序，第一条可晚于后续记录，"这批消息的时间范围"暗示它是最早端点即错。maxTimestamp 在 CreateTime 下为批内最大值、LogAppendTime 下由 Broker 写入追加时间——改稿两点均符合 Kafka 3.9 语义（证据等级：官方源码记忆，未在线复核，与 items 所引 MemoryRecordsBuilder 行为一致），且与 129 行"存它和 baseTimestamp 的差值"呼应。

**G6 | 存在：是 | 引文：逐字 | 改法：认可 | chapters/02-data-structures-protocols/diagrams/fig-2-7.svg:41**
"批最早时间戳"比正文表格更直接地写错字段语义（base=最早仅在生产者时间戳单调时成立），"时间戳差值基准"与正文 129 行一致。maxTimestamp 框"批最晚时间戳"保留不动是合理的（CreateTime 下确为批内最大值）。

**G7 | 存在：是 | 引文：逐字 | 改法：认可 | chapters/02-data-structures-protocols/chapter.md:160**
按最自然读法"知道后面还有多少字节"＝已知道字符串长度，与上一段自列的 0xFC/0xFD/0xFE 规则冲突——首字节只指明长度整数占几字节（总长 1/3/4/9），多字节情形必须读完长度字段才知道内容长度；属表述含混按自然读法为错。改稿把两步拆开，无懈可击也不引入新错。

**G8 | 存在：是 | 引文：逐字 | 改法：认可 | chapters/03-lifecycle/chapter.md:133**
官方 shutdown 流程序是先停止接入新连接、终止现有连接与活动，存储引擎（含缓冲池刷盘）收尾在其后——关闭期再连上去执行 SHOW PROCESSLIST 通常不可行；"对着四类根因看就能定位卡点"把关闭前检查工具写成关闭期通用手段且承诺"就能定位"（证据等级：MySQL 8.0 官方文档记忆）。改稿"发起关闭前可查、关闭开始后看错误日志与存储 I/O 状态"与流程次序一致、hedge 恰当。

**G9 | 存在：是 | 引文：逐字 | 改法：认可 | chapters/03-lifecycle/chapter.md:152**
已取 3.9.0 源码逐字验证：`logIdent = s"[KafkaRaftServer nodeId=${config.nodeId}]"`，`startup()` 末行 `info(KafkaBroker.STARTED_MESSAGE)`（= "Kafka Server started"），KRaft 模式实际日志就是 `[KafkaRaftServer nodeId=0] Kafka Server started`，改稿字串精确。现文字串 `[KafkaServer id=0] started` 是 ZK 时代写法，且即便 ZK 模式真实字串也含 "Kafka Server" 两词——两头都不成立；本节前文已明确 KRaft 语境。改稿"以 3.9 的 KRaft 模式、node.id=0 为例"的限定恰当，未把 broker-only 模式的 `[KafkaBroker nodeId=0]` 变体扩大成通则。

**G10 | 存在：是 | 引文：逐字 | 改法：认可（附呈现 nit） | chapters/04-memory-disk/diagrams/fig-4-2.svg:80-86**
已取 7.0.0 源码验证：`val->lru = (LFUGetTimeInMinutes()<<8) | counter`（updateLFU，db.c）、`ldt = o->lru >> 8; counter = o->lru & 255`（LFUDecrAndReturn，evict.c）——时间在高位 16 bit、计数器在低位 8 bit，现图高低标反，成立。仅交换高低字样后每框自洽，技术正确；nit：交换后高位框落在右侧，与位域图"高位在左"惯例相反，若在意可改为两框整体换内容——属呈现偏好非事实问题。

**G11 | 存在：是 | 引文：逐字 | 改法：认可 | chapters/04-memory-disk/chapter.md:182**
"撑不了这个容量"把成本约束写成不可能——本章 124 行自己就说增长路径是"上 Cluster 分片或改用磁盘系统"，几十 TB 在多分片下技术上可行；"给不了随机查询"又与本章 194 行"它可以按偏移量定位"自相矛盾，收窄为按业务 key 点查/通用条件查询是对的。改稿两处修正方向正确、选型结论保留；注记：改后句式变绕（"需要为……配置足够的内存与分片"），锋芒略钝，属可接受代价。

**G12 | 存在：是 | 引文：逐字 | 改法：认可 | chapters/04-memory-disk/chapter.md:216**
零拷贝的真前提是"文件到 socket 的纯转发"（第 5 章 176 行已正确写出）；页缓存命中只决定要不要等磁盘，不是能否走该路径的前提——未命中时内核先在页缓存补页再沿内核路径发送，全程仍不进用户态。改稿把磁盘等待与用户态搬运分开，正确且与第 5 章"硬前提"框架一致。

**G13 | 存在：是 | 引文：逐字 | 改法：认可 | chapters/05-layered-architecture/chapter.md:154**
"Redis 的并发最多停在 I/O 层"与本节前文自相矛盾——5.2.1（45 行）明确 7.x 默认连网络 I/O 都在主线程、多线程 I/O 需显式启用，5.2.3（75 行）已列后台 BIO 线程；"差出几个数量级""吞吐高出一整个量级"无共同口径（AGENTS.md 规则 7 裸数字三选一确实存在），小消息下两者消息速率同量级，非通用事实。改稿"普通命令仍在主线程执行，网络 I/O 和部分后台任务**可以**使用其他线程"正确覆盖默认未启用的事实，"网络线程与业务线程"与 5.4.1/图 5-5 既有术语一致；"挂几百个分区"改"承载"还顺带消掉一处口语语域残留。

**G14 | 存在：是 | 引文：逐字 | 改法：认可 | chapters/05-layered-architecture/chapter.md:187**
本节 168 行把 .index/.timeindex 定义为 LogSegment（存储层）的一部分、172 行读取路径在段内用索引定位，收口句"索引……都在上层解决"与自家段落口径冲突；源码中 LogSegment 持有索引、LogCleaner 在日志子系统内重建段，压实也不归"上层"，改稿"索引与压实仍由日志存储组件处理，副本协调则由上层组件负责"（ReplicaManager 在 Log 之上）层次归属准确。保留句"3.9 起 Tiered Storage 正式 GA"已对照 3.9.0 官方公告核实——原文 "Tiered storage is now production-ready in Kafka 3.9"，站得住；"存储快"改"追加路径简单"也更准确。

## 总表

| # | 问题存在 | 改法判定 |
|---|---|---|
| G1 | 是 | 认可（须配套处理 ch2:89，见清单外 1） |
| G2 | 是 | 认可 |
| G3 | 是 | 认可 |
| G4 | 是 | 认可（引文拼读偏差，需渲染宽度复核） |
| G5 | 是 | 认可 |
| G6 | 是 | 认可 |
| G7 | 是 | 认可 |
| G8 | 是 | 认可 |
| G9 | 是 | 认可（源码逐字验证通过） |
| G10 | 是 | 认可（附高位在左的呈现 nit） |
| G11 | 是 | 认可 |
| G12 | 是 | 认可 |
| G13 | 是 | 认可 |
| G14 | 是 | 认可 |

## A 席清单外发现

1. **【重要，与 G1 联动，改法层面】chapters/02-data-structures-protocols/chapter.md:89**："所以 InnoDB 的核心数据结构要解决的正是这个问题：**让每一次磁盘 I/O 读上来的 16KB，每一个字节都有用**"。与 G1 同族的过强表述，且 G1 改稿新增"页内仍有管理信息和供后续写入使用的空闲空间"后两处正面冲突（官方文档：随机插入页 1/2–15/16 满）。已 grep 0913/gpt扫描结果.html，"每一个字节"零命中——报告未覆盖此行。若 G1 落地，此行必须同组裁定（方向：改为"尽量多承载有效内容"一类，去掉"每一个字节都有用"的全称）。
2. **【轻，一致性】chapters/04-memory-disk/chapter.md:7**：导读"Kafka 吞吐高，但换不来随机查询"与 G11 同族宽松说法；全书把"随机查询"口径落在"按 key/条件查询"（ch2:134、ch4:194），导读可保留，若求全可对齐。
3. **【轻，防误改】fig-2-7 maxTimestamp 框"批最晚时间戳"**：G6 未改它是对的——CreateTime 下 maxTimestamp 确为批内最大值，与 G5 细化后的表格构成"图简表详"关系，属可接受分层，后续扫描勿当错改掉。
4. **【备注】G13 领域确认**：现行 154 行"并发最多停在 I/O 层"不仅弱化错误，还直接违反本章 45 行"7.x 默认仍只使用主线程完成这些 I/O 工作"的自述——问题比报告理由所述更实，为该条又添一票。
