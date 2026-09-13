# 0913 三席核实 · C 席（源码与版本席）判定报告

> 状态：已完成 · 判定 14/14 存在、14/14 改法认可（附执行级建议）
> 证据等级标记：[一手] = 本轮实际抓取并核对的源码/官方文档；[记忆] = 凭源码/官方文档记忆（未抓取）；[推理] = 明确标注的推断。
> 全部 14 条证据链闭合：Redis 7.2.0 源码与 redis.conf、Kafka 3.9.0 五个源文件、MySQL 8.0.36 pack.cc、两页 MySQL 官方文档、Linux v6.6 filemap.c 均已一手抓取核对。

## 逐条明细

### G1 | 存在：是 | 引文：逐字 | 改法：认可（1 处措辞建议）
- **锚点**：chapters/02-data-structures-protocols/chapter.md:22
- **证据**：[一手] MySQL 8.0 官方文档 innodb-physical-structure.html 原文："InnoDB tries to leave 1/16 of the page free for future insertions... sequential order, the resulting index pages are about 15/16 full. If records are inserted in a random order, the pages are from 1/2 to 15/16 full."——「每一页都装满了索引键」与文档正面矛盾，且「半页无用数据」的对照也是错的（空闲空间是留给未来写入的，不是无用）。改稿「默认 16KB 的页」「页内仍有管理信息和供后续写入使用的空闲空间」逐点对齐文档（1/16 留白规则）。
- **理由**：问题确凿。「预编译解析只做一次」也与本章 154 行自己的精确表述（「通常可复用解析结果，元数据变化等情形仍会触发重新预处理」）和 MySQL reprepare 行为冲突，收回到「通常」是必要的。**一处建议**：改稿「子页指针」建议换回全书已用的「子节点指针」（fig-2-6 第 18 行、本章 91 行均用后者），避免同一概念两种叫法。

### G2 | 存在：是 | 引文：逐字 | 改法：认可
- **锚点**：chapters/02-data-structures-protocols/diagrams/fig-2-6.svg:25
- **证据**：[一手] 同上 MySQL 文档（页最多 15/16 满）。SVG 根节点框自身（第 18 行）写的是「只存键 + 子节点指针」，角标「装满键」既错又与图内文字不一致。
- **理由**：问题存在。改稿「键与指针」与图内既有描述一致；新文字 4 字 × 9px ≈ 36px，角标框宽 70px，放得下。无需修正。

### G3 | 存在：是 | 引文：逐字 | 改法：认可
- **锚点**：chapters/02-data-structures-protocols/chapter.md:76
- **证据**：[一手] Redis 7.2.0 `src/t_set.c` `setTypeAddAux` INTSET 分支（约 181–222 行）：插入非整数时转 listpack 的条件是 `intsetLen < set_max_listpack_entries && len <= set_max_listpack_value && maxelelen <= set_max_listpack_value && lpSafeToAdd(...)`，否则直接 `setTypeConvertAndExpand(..., OBJ_ENCODING_HT, ...)`；listpack 分支在 `lpLength >= 128 || len > 64` 时转 HT。`redis.conf:1971-1972`：`set-max-listpack-entries 128` / `set-max-listpack-value 64`。7.2 之前 intset+非整数直接转 HT，属实。
- **理由**：现文只给数量条件、漏 64 字节长度条件，65 字节非整数成员即便集合很小也直达 HT——改稿补齐两个阈值且阈值数字、版本分界全部与源码/配置一致。源码里的第三个条件 `maxelelen <= 64` 对纯 intset 恒成立（int64 十进制最长 20 字符，是防御性检查），改稿略去不构成遗漏。

### G4 | 存在：是 | 引文：逐字 | 改法：认可（渲染复核如报告自注）
- **锚点**：chapters/02-data-structures-protocols/diagrams/fig-2-5.svg:61-69
- **证据**：[一手] 同 G3 的 t_set.c 证据；`maybeConvertIntset`（t_set.c 约 78–82 行）证实纯整数超 512 直转 HT 不经 listpack，与 78 行正文、改稿底部路径文字一致。
- **理由**：图中「混入非整数先转 listpack」写成无条件必经，「元素数 > 128」漏成员长度——与 G3 同根。改稿箭头文字语义正确；「>128 个或成员 >64B」在 10.5px 字号下约 130px，比箭头跨度（111px）宽，**落地时必须按报告自注做渲染复核**，其余无异议。

### G5 | 存在：是 | 引文：逐字 | 改法：认可
- **锚点**：chapters/02-data-structures-protocols/chapter.md:125
- **证据**：[一手] Kafka 3.9.0 `DefaultRecordBatch.java` 类注释原话："The BaseTimestamp field therefore reflects **the timestamp of the first record** in the batch"；"The MaxTimestamp field reflects **the maximum timestamp of the current records if the timestamp type is CREATE_TIME**. For LOG_APPEND_TIME, on the other hand, the MaxTimestamp field reflects the timestamp **set by the broker**"。`MemoryRecordsBuilder.java:470-472`：`if (baseTimestamp == null) baseTimestamp = timestamp;`（首条记录）；同文件只强制 offset 单调、不强制 timestamp 单调——首条时间戳确实可能大于后续。
- **理由**：「时间范围」暗示 base=最早、max=最晚的区间端点，两端都不精确。改稿「差值的基准 / 批内最大时间戳（CreateTime）；LogAppendTime 下后者记录 Broker 追加时间」与源码注释逐点对应，是三条改法里对得最齐的一条。

### G6 | 存在：是 | 引文：逐字 | 改法：认可
- **锚点**：chapters/02-data-structures-protocols/diagrams/fig-2-7.svg:41
- **证据**：[一手] 同 G5——baseTimestamp 是首条记录的时间戳，「批最早时间戳」直接写错。
- **理由**：改稿「时间戳差值基准」描述的是该字段的真实功能（每条记录存 timestampDelta），且天然覆盖乱序批次。**附带核对**：相邻第 45 行 maxTimestamp 标「批最晚时间戳」，在 CreateTime 下「最晚=最大」成立，不构成错误，可不改。

### G7 | 存在：是 | 引文：逐字 | 改法：认可
- **锚点**：chapters/02-data-structures-protocols/chapter.md:160
- **证据**：[一手] mysql-8.0.36 `mysys/pack.cc` `net_field_length_ll`：首字节 <251 时首字节即值；0xFC/0xFD/0xFE 时分别还要再读 2/3/8 字节才能得到长度——首字节只告诉你长度字段的编码档位，不直接告诉你后面有多少字节。
- **理由**：原句把「知道如何读长度」混成「已经知道长度」，且与上一段（158 行）刚列完的分档规则自相矛盾，长度 ≥251 的字符串即反例。改稿与 `net_field_length_ll` 的实际解码顺序一致。

### G8 | 存在：是 | 引文：逐字 | 改法：认可
- **锚点**：chapters/03-lifecycle/chapter.md:133
- **证据**：[一手] MySQL 8.0 官方文档 server-shutdown.html 原文："the server stops accepting new client connections by closing the handlers for the network interfaces... For each thread associated with a client connection, the server breaks the connection to the client and marks the thread as killed"——停止接入、断开已有连接发生在引擎关闭（刷脏页等慢步骤）之前。
- **理由**：关闭期普遍已无法执行 SHOW PROCESSLIST，原句把关闭前的检查工具写成关闭期的通用定位手段；且四类根因里脏页刷盘、FTS 优化本来就不是 PROCESSLIST 可见的。改稿的时段划分（关前可用 / 关后看错误日志）与文档顺序一致，「就能定位卡点」的绝对化承诺也一并撤掉了。

### G9 | 存在：是 | 引文：逐字 | 改法：认可
- **锚点**：chapters/03-lifecycle/chapter.md:152
- **证据**：[一手] Kafka 3.9.0 `KafkaRaftServer.scala:55`：`this.logIdent = s"[KafkaRaftServer nodeId=${config.nodeId}] "`；`startup()`（94–102 行，与建议引用行号吻合）末行 `info(KafkaBroker.STARTED_MESSAGE)`；`KafkaBroker.scala:71`：`val STARTED_MESSAGE = "Kafka Server started"`（注释还说明系统测试靠正则 `Kafka\s*Server.*started` 匹配此行）。另核实现文：旧 ZK 模式 `KafkaServer.scala:263` 前缀 `[KafkaServer id=${config.brokerId}]`、startup 末行 `info("started")`——**现文字符串真实存在，但属于 3.9 已弃用、4.0 移除的 ZK 模式**，而该节八阶段讲的正是 KRaft。
- **理由**：改稿字符串 `[KafkaRaftServer nodeId=0] Kafka Server started` 与 3.9.0 源码逐字符吻合（含「Kafka Server started」这五个词的写法，不是「started」孤词）。上一轮曾证伪过编造日志串——这条反向：现文不是编造，是模式错配，改法方向正确且证据扎实。

### G10 | 存在：是 | 引文：逐字 | 改法：认可
- **锚点**：chapters/04-memory-disk/diagrams/fig-4-2.svg:79-86
- **证据**：[一手] Redis 7.0.0 `src/evict.c` `LFUDecrAndReturn`：`unsigned long ldt = o->lru >> 8; unsigned long counter = o->lru & 255;`；`src/object.c:52/94/1390`：`o->lru = (LFUGetTimeInMinutes()<<8) | LFU_INIT_VAL;`——时间在**高 16 位**、计数器在**低 8 位**，读写两侧同证。SVG 现标「高 8 位=计数器、低 16 位=时间」，整个反了。
- **理由**：交换两个框的高低位文字即可，映射关系随之全部正确。**两处附带核对**：① 图中「约 31 万次访问打满」经按 `LFULogIncr`（p=1/(baseval·log_factor+1)，baseval 从 0 到 249 累计）算得期望 311,500 次，数字本身没错，不动；② 交换后左框变「低 8 位」即 LSB 在左，因两框等宽、且高/低有明示，不构成事实错误，可接受（若追求惯例可改为保「高」在左、对调框内内容，非必需）。

### G11 | 存在：是（断言边界问题，非机制硬错）| 引文：逐字 | 改法：认可
- **锚点**：chapters/04-memory-disk/chapter.md:182
- **证据**：[记忆/常识级] Redis Cluster 槽分布模型支持横向分片，几十 TB 需要的是内存预算与分片成本，不是「撑不了」的不可能；`KafkaConsumer.seek(TopicPartition, offset)` 支持按 offset 任意定位（API 事实）。
- **理由**：「撑不了」把成本问题写成本质不可能，「给不了随机查询」按 offset 可定位的事实下需要收窄到按业务 key/条件查询——而本章 239 行自己已用精确表述（「没有按主键点查、没有复杂过滤，只能按偏移量区间顺序消费」），改稿正是向该口径对齐。此条证据是 API 面常识而非本轮抓取，等级如实标注。

### G12 | 存在：是 | 引文：逐字 | 改法：认可
- **锚点**：chapters/04-memory-disk/chapter.md:216
- **证据**：[一手] Linux v6.6 `mm/filemap.c` `filemap_splice_read` 文档注释："gets folios from a file's pagecache... **Readahead will be called as necessary to fill more folios**"——未命中时内核按需把页读入 PageCache，随后仍走 splice 路径；Kafka 3.9.0 `docs/design.html`（110–126 行）：sendfile 是「out of pagecache to a socket」，缓存命中时「you will see no read activity on the disks whatsoever」。
- **理由**：原句把「缓存命中可省掉磁盘读」写成了「零拷贝生效的前提」，两个概念被压成一个条件；冷数据等的是磁盘 I/O，不是退回用户态复制。改稿「命中可省去磁盘读取；冷数据仍需先等磁盘 I/O，但也可以沿这条路径传输」与两边源码/文档都对得上。

### G13 | 存在：是 | 引文：逐字 | 改法：认可
- **锚点**：chapters/05-layered-architecture/chapter.md:154
- **证据**：[一手+内部证据] 「并发最多停在 I/O 层」与本章 45 行（多线程 I/O、命令仍在主线程串行、7.x 默认未启用）和 75 行（lazy free 交给后台 BIO 线程）直接冲突；`redis.conf` 7.2.0 约 1277 行起的 THREADED I/O 段自述："Redis is mostly single threaded, however there are certain threaded operations such as UNLINK, slow I/O accesses and other things that are performed on side threads"。「吞吐高出一整个量级/并发需求差几个数量级」属裸数字：msgs/s 口径下 Redis（pipeline）与 Kafka（批量小消息）常在同一数量级，差距主要随消息大小、批量、持久化条件放大——无共同测试口径支撑不了固定量级断言。
- **理由**：改稿把两个固定量级换成机制表述（网络线程与业务线程分工、Redis 主线程执行命令+I/O 与部分后台任务可他用线程），与 SocketServer 的 num.network.threads/num.io.threads 设计和本章前文一致。「交互层最重」的判断保留，未伤原论点。

### G14 | 存在：是 | 引文：逐字 | 改法：认可
- **锚点**：chapters/05-layered-architecture/chapter.md:187
- **证据**：[一手] Kafka 3.9.0 `storage/src/main/java/org/apache/kafka/storage/internals/log/LogSegment.java`（57–89 行，与建议引用行号吻合）字段：`private final FileRecords log; private final LazyIndex<OffsetIndex> lazyOffsetIndex; private final LazyIndex<TimeIndex> lazyTimeIndex; private final TransactionIndex txnIndex;`，类注释首句 "Each segment has two components: a log and an index"——索引就是存储层（LogSegment）持有的。LogCleaner 是日志子系统内的后台压实线程，副本协调（ReplicaManager）才是上层。
- **理由**：现文「索引、复制、压实的复杂度都在上层解决」与源码归属（索引在存储层）和本节 168 行自己的存储层定义（.index/.timeindex 属存储层）双重矛盾。改稿的重新归属（索引与压实仍由日志存储组件处理、副本协调由上层负责）逐项对上源码模块划分。

## 总表

| 条目 | 存在 | 改法 |
|---|---|---|
| G1 InnoDB 页装满键 | 是 | 认可（「子页指针」建议改回「子节点指针」） |
| G2 fig-2-6「装满键」 | 是 | 认可 |
| G3 intset→listpack 双阈值 | 是 | 认可 |
| G4 fig-2-5 转换标注 | 是 | 认可（落地时渲染复核文字宽度，报告已自注） |
| G5 baseTimestamp/maxTimestamp | 是 | 认可 |
| G6 fig-2-7「批最早时间戳」 | 是 | 认可 |
| G7 首字节即知长度 | 是 | 认可 |
| G8 关闭期 PROCESSLIST | 是 | 认可 |
| G9 KRaft 就绪日志 | 是 | 认可 |
| G10 LFU 高低位颠倒 | 是 | 认可（两框等宽可接受，见附带核对） |
| G11 Redis 撑不了/Kafka 无随机查询 | 是（断言边界） | 认可 |
| G12 零拷贝以缓存命中为前提 | 是 | 认可 |
| G13 数量级断言与 I/O 层说法 | 是 | 认可 |
| G14 存储层归属 | 是 | 认可 |

本轮逐字抓取核对的引用源：Redis 7.2.0 `t_set.c`/`redis.conf`、Redis 7.0.0 `evict.c`/`object.c`、Kafka 3.9.0 `KafkaRaftServer.scala`/`KafkaBroker.scala`/`KafkaServer.scala`/`DefaultRecordBatch.java`/`MemoryRecordsBuilder.java`/`LogSegment.java`/`design.html`、mysql-8.0.36 `pack.cc`、MySQL 官方文档两页、Linux v6.6 `filemap.c`。唯一非一手条目是 G11（API 面常识，已标注）。

## 清单外（核实过程中撞见、报告未提的源码/版本级问题）

1. **ch2:89（2.2.2 开头）同族断言未入清单**：「让每一次磁盘 I/O 读上来的 16KB，**每一个字节都有用**」——与 G1 同族的过强表述：按官方文档，随机插入的页可低至 1/2 满，读上来的页里就有此刻闲置的空闲空间。它比「装满键」软（空闲空间对未来写入有用），且第 8 章的页内布局细节可能已构成限定，但若 G1 落地，这句应一并复议，否则 2.1 与 2.2.2 修后口径仍不齐。**建议随 G1 一并裁决。**
2. **fig-2-7:45 maxTimestamp「批最晚时间戳」**：CreateTime 下「最晚=最大」成立，不构成错误；仅当 G5 落地后表内口径变为「批内最大时间戳（CreateTime）」，图与表措辞略异（最晚 vs 最大），属可接受的一致性余量，不必动。
3. **G9 附带事实**：KafkaRaftServer 在 controller-only 角色（process.roles=controller）下同样打印 `Kafka Server started`（`info(KafkaBroker.STARTED_MESSAGE)` 不区分角色执行）。现文与改稿都以 Broker 为语境，无碍；记录在此防后续有人拿 controller 日志质疑这条字符串。
4. **G3 防御性补漏**：若后续轮次有人主张「改稿漏了 maxelelen 条件」——t_set.c 里 `maxelelen <= set_max_listpack_value` 对纯 intset 恒真（int64 十进制最长 20 字符 < 64），是防御性检查，略去不损准确性。预先记录，免得下一轮误报。

**红线自查**：各改稿均未引入拟人化动词（G8 撤掉的「就能定位卡点」原本就是越界承诺）；术语英文规范未被破坏（G5 的 CreateTime/LogAppendTime 是 Kafka 官方 TimestampType 名称，英文优先合规）；无前向节引用引入；G1 的「子页指针」是唯一术语一致性瑕疵，已给出替代写法。
