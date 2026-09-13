# 0913 三席核实 · C 席报告（第二轮：源码与版本席）

> 状态：已完成 · 判定 11/11 存在、11/11 改法认可（1 条附修正：R2-07 版本括注）
> 取证说明：Kafka 证据为 archive.apache.org 下载的 3.9.0 官方源码包（与被审版本完全一致，[一手]）；Redis 证据为 gitee 镜像 unstable（8.x dev）源码，涉及 7.x 同构性由源码记忆佐证（[一手]+[记忆]）；GitHub/dev.mysql.com 本会话不可达，MySQL 仅能 [记忆]（详见 R2-08）。任务前提已按更正处理：G1–G14 已落地，本轮逐条核查 R2 整段替换是否回退第一轮改文。

## 逐条判定

**R2-01 | 存在：是 | 引文：逐字 | 建议：认可 | 锚点 chapters/02-data-structures-protocols/chapter.md:63**
新桶号 = `hash & (size-1)`：旧 size=4 掩码 `0b11`，旧桶 2 锁定哈希低两位为 `10`；扩到 8 只多取一位，落点必为 `010`=2 或 `110`=6，现文（配合图）声称散落到三个不同桶是源码级错误。改稿「只能落在桶 2 或桶 6」「用同一个哈希值和新表的掩码重新计算桶号」与 `dictRehash`→`rehashEntriesInBucketAtIndex` 的 `dictHashKey(...) & DICTHT_SIZE_MASK(ht_size_exp[1])` 逐点对应，且「原来在同一桶里的键可能因此分开」的「可能」用得准（同桶键未必分开）。
证据：[一手] gitee.com/mirrors/redis `src/dict.c`（unstable，核心循环 4.0 以来未变，7.x 同构 [记忆] 高置信）。

**R2-02 | 存在：是 | 引文：逐字（图内文字节点）| 建议：认可 | 锚点 chapters/02-data-structures-protocols/diagrams/fig-2-3.svg:39-51**
逐桶核对 SVG：k7 在新桶 1（行 44）、k3 在桶 3（行 46）、k9 在桶 5（行 49）——按上述掩码数学不可能；且现图在同一「时刻」里 k7/k3/k9 同时存在于两表，本身自相矛盾。改稿的合法示例（桶 2:k9→k7、桶 6:k3）与源码头插顺序精确吻合：沿旧链 k7→k3→k9 逐个 `dictSetNext(de, ht_table[1][h])` 头插，k7、k9 同落桶 2 时链序正是 k9→k7，「落点为一种示例」的标注也避免了把示例当必然。
证据：[一手] 同上 `rehashEntriesInBucketAtIndex`（头插、整桶搬迁）。

**R2-10 | 存在：是（随 R2-02 成立）| 引文：逐字 | 建议：认可 | 锚点 chapters/02-data-structures-protocols/chapter.md:61**
新图改为「一次搬迁的前后对照」后，现图注「搬迁进行到一半的一个时刻」与之冲突，必须同步。任务单问的「一次搬迁处理一个桶中全部元素」：现文 58 行该句与源码一致（`rehashEntriesInBucketAtIndex` 整桶搬迁、`empty_visits=n*10` 跳空桶），无需 R2 触碰，改后亦保留。
证据：[一手] 同上。

**R2-03a | 存在：是 | 引文：逐字 | 建议：认可 | 锚点 chapters/02-data-structures-protocols/chapter.md:129-132**
DefaultRecordBatch.java（3.9.0）偏移常量给出的磁盘序：attributes(21)→lastOffsetDelta(23)→baseTimestamp(27)→maxTimestamp(35)→producerId(43)→producerEpoch(51)→baseSequence(53)→recordsCount(57)→records(61)；现图把 lastOffsetDelta 排在两个时间戳之后、recordsCount 排在 Producer 状态之前，确非磁盘序，「完整的字段排布」措辞误导成立。改稿「按功能分组，不表示磁盘字节顺序」诚实且保留图的解释价值；61 字节头部（RECORDS_OFFSET=61）经逐字段累加验证无误。第一轮兼容性：未触碰 G5 已落地的表 2-1 行（ch2:125）。
证据：[一手] kafka-3.9.0-src/clients/.../record/DefaultRecordBatch.java:102-129。

**R2-03b | 存在：是（与 03a 同源）| 引文：逐字（SVG 行 11）| 建议：认可 | 锚点 chapters/02-data-structures-protocols/diagrams/fig-2-7.svg:11**
标题加「按功能分组」与 03a 的图注限定配套，防止标题层面单独被误读。第一轮兼容性：不动 G6 已落地的「8B · 时间戳差值基准」（SVG 行 41）。
证据：[一手] 同 03a。

**R2-04 | 存在：是 | 引文：逐字 | 建议：认可 | 锚点 chapters/03-lifecycle/chapter.md:139-154**
源码逐条支持改稿：KafkaRaftServer.startup 先 `controller.foreach(_.startup())` 后 broker（含注释 "Controller component must be started before the broker"）；BrokerServer 创建 LogManager 但不启动（注释 "delay any possible unclean shutdown log recovery until we catch up on the metadata log"），真正的 `logManager.startup → replicaManager.startup → 协调器 startup` 发生在 BrokerMetadataPublisher.initializeManagers 的首次元数据发布；`lifecycleManager.start`（注册/心跳）在 installPublishers 与开启请求处理之前；末段依次等 initialCatchUpFuture→firstPublishFuture→setReadyToUnfence→authorizer futures→`socketServer.enableRequestProcessing`，与改稿第 3 条逐句对应。另外原「八阶段」的顺序实际是 ZK 模式 KafkaServer.startup 的调用序（logManager.startup:327 → SocketServer:383 → replicaManager:404 → kafkaController:415 → 注册:633），挂在 KRaft 3.9 标题下属版本错置；「恢复按需」亦有源码直证（LogManager.scala "Skipping recovery of N logs … since clean shutdown file was found"）。第一轮兼容性：改稿完整保留 G9 已落地的 `[KafkaRaftServer nodeId=0] Kafka Server started`（与 KafkaRaftServer logIdent + KafkaBroker.STARTED_MESSAGE="Kafka Server started" 一致）。
证据：[一手] KafkaRaftServer.scala:94-111、BrokerServer.scala:172-550、BrokerMetadataPublisher.scala:270-310、LogManager.scala:470-485、KafkaServer.scala:327-633。

**R2-05 | 存在：是（随 R2-04 成立）| 引文：逐字（SVG 行 86-87）| 建议：认可 | 锚点 chapters/03-lifecycle/diagrams/fig-3-5.svg:86-87**
「八阶段的第 4 阶段」直接固化正文错误序；源码是 SocketServer 中段创建、acceptor 先绑定端口、"Delay starting processors until the end of the initialization sequence"，请求处理在元数据/恢复/授权就绪后才开启。改稿替换的两行说明与该序列一致，且保留网络结构图不变。
证据：[一手] BrokerServer.scala:249-252、525-548。

**R2-06 | 存在：是 | 引文：逐字（L163+L165 两段）| 建议：认可 | 锚点 chapters/03-lifecycle/chapter.md:163-165**
三个源码级错误全部坐实：① `stopProcessingRequests()` 关 acceptor/processor 后执行 `dataPlaneRequestChannel.clear()`——排队未处理请求被直接丢弃，随后立即关闭 handler 线程池，不存在「处理完在途请求」的排空保证；② 组件顺序——KRaft 的 BrokerServer.shutdown 为 stopProcessingRequests→handler 池→协调器→replicaManager→logManager 刷盘收尾，合并进程的 Controller 在 Broker 之后才关（KafkaRaftServer.shutdown 注释 "shut down the broker first, since the controller may be needed for controlled shutdown"），即使 ZK 模式 kafkaController.shutdown 也在 replicaManager/logManager 之后，原文「停控制器→停副本管理」两版本皆错；③ 分类句「是否提前告知」不精确——受控关闭超时回退时 Controller 已收到过关闭意图，改稿「受控关闭在退出前协调 Leader 迁移，并等待 Controller 批准」与 beginControlledShutdown + `controlledShutdownFuture.get(timeout)`（超时报错原文即 "waiting for the controller to approve controlled shutdown"）精确对应。改稿对「尚未迁移的 Leader 分区」的限定同时覆盖了回退情形。
证据：[一手] BrokerServer.scala:613-713、KafkaRaftServer.scala:104-111、SocketServer.scala:281-292、RequestChannel.scala clear()、KafkaServer.scala:977-1048。

**R2-07 | 存在：是 | 引文：逐字（图内文字节点 45-67）| 建议：认可但需修正（一处小修）| 锚点 chapters/04-memory-disk/diagrams/fig-4-2.svg:45-67**
源码坐实三步机制：`evictionPoolPopulate` 把当轮样本（最多 maxmemory_samples 个，count 可小于 N）插入持久池（EVPOOL_SIZE=16，按 idle 升序保留较优者）；选取时 `for (k = EVPOOL_SIZE-1; k >= 0; k--)` 从池尾向左、跳过已不存在的 "ghost" 键；删除走 `deleteEvictedKeyAndPropagate`（是否 lazyfree 由配置决定）。改稿三框布局与各句表述逐点与源码一致，且与正文 ch4:81 既有描述对齐。需修正：「最多 16 项（Redis 7.0）」的版本括注不当——16 自 4.0 引入淘汰池起即是此值、8.x 仍为 16，读者会误读为 7.0 特有，建议改「（容量 16）」。
第一轮兼容性：改稿文字仅涉左半区，不得触碰 G10 已落地的 LFU 高低位框（行 80-86，低 8 位 logc / 高 16 位 ldt——该方向本身经本轮源码复核仍正确）；左半区加框需扩 viewBox 并下移「精度换性能」注，几何交 svg-checker。
证据：[一手] gitee.com/mirrors/redis `src/evict.c`（unstable；7.x 同构 [记忆] 高置信）。

**R2-08 | 存在：是 | 引文：逐字（SVG 行 85 与行 99 两处标签）| 建议：认可 | 锚点 chapters/04-memory-disk/diagrams/fig-4-4.svg:85,99**
Flush list 以 oldest_modification LSN 升序排列（buf0flu.cc 的有序插入，page cleaner 从队首取最老脏页），这是日志序不是文件偏移序；每张脏页经 fil_io 写回自身 page_no 位置，物理上散布于各表空间，「顺序刷盘/顺序写回」把 redo log 的顺序写优势错移给了数据页。结构性旁证：若数据页真是顺序写回，doublewrite buffer 就没有存在必要；innodb_flush_neighbors 仅在同 extent 内合并邻页、定位 HDD 减少寻道，不改变逐页写回本质。改稿两句（「使 Checkpoint 可以向前推进」「脏页写回各自的表空间位置；崩溃恢复按需重放 redo log」）准确，且消除了与本书 ch3:128「刷盘是随机 I/O」、ch4:168 的自相矛盾。
证据：[记忆]（dev.mysql.com 与 GitHub 本会话不可达）：buf0flu.cc/buf0lru.cc 语义、官方 innodb_flush_neighbors 文档语义；论证链自洽，置信度高但非一手，如后续网络恢复建议拉 mysql-server 8.0 的 `buf_flush_insert_sorted_into_flush_list` 复核一次。

**R2-09 | 存在：是 | 引文：逐字 | 建议：认可 | 锚点 chapters/06-security/chapter.md:99**
源码坐实：`ACLSelectorCheckCmd` 仅对 `getKeysFromCommandWithSpecs` 从命令参数中提取的键做模式检查（注释原文 "explicitly touching the keys mentioned in the command arguments"）；commands.def 中 `#define SCAN_Keyspecs NULL`——SCAN 无键参数，键模式检查整段跳过；`scanGenericCommand` 只按 MATCH/TYPE/过期状态过滤返回键名，无任何 ACL 过滤。改稿的边界表述（GET/SET 受限、SCAN 返回不受过滤、无键参数全库操作不受限、须靠命令权限补位）逐句与源码对应，从「按前缀隔离」收回到「按前缀限制读写」是准确降格。
证据：[一手] gitee unstable `src/acl.c` ACLSelectorCheckCmd:1696-1731、`src/commands.def` SCAN_Keyspecs:2513、`src/db.c` scanGenericCommand:1454。

## 总表

| 条目 | 存在 | 引文 | 建议 | 证据等级 |
|---|---|---|---|---|
| R2-01 | 是 | 逐字 | 认可 | [一手] Redis dict.c |
| R2-02 | 是 | 逐字 | 认可 | [一手] Redis dict.c |
| R2-10 | 是 | 逐字 | 认可 | [一手] Redis dict.c |
| R2-03a | 是 | 逐字 | 认可 | [一手] Kafka 3.9.0 DefaultRecordBatch.java |
| R2-03b | 是 | 逐字 | 认可 | [一手] 同上 |
| R2-04 | 是 | 逐字 | 认可 | [一手] Kafka 3.9.0 KafkaRaftServer/BrokerServer 等 |
| R2-05 | 是 | 逐字 | 认可 | [一手] Kafka 3.9.0 BrokerServer |
| R2-06 | 是 | 逐字 | 认可 | [一手] Kafka 3.9.0 BrokerServer/SocketServer |
| R2-07 | 是 | 逐字 | 认可但需修正（版本括注） | [一手] Redis evict.c |
| R2-08 | 是 | 逐字 | 认可 | [记忆+官方文档语义] |
| R2-09 | 是 | 逐字 | 认可 | [一手] Redis acl.c/commands.def/db.c |

## 与第一轮（G1–G14 已落地）兼容性专项

- **R2-04 vs G9**：改稿第 2 段末尾逐字保留了 `[KafkaRaftServer nodeId=0] Kafka Server started` 与「都可用来识别启动完成」句式，无回退。
- **R2-07 vs G10**：改稿仅涉左半区；执行时须显式圈定改动范围不含行 80-86 的 LFU 高低位框（本轮源码复核确认该框现文正确）。
- **R2-03a/03b vs G5/G6**：改稿不触碰表 2-1 的 baseTimestamp/maxTimestamp 行与 SVG 行 41 的「时间戳差值基准」标签，无回退；顺带说明，3.9.0 源码访问器即 `BASE_TIMESTAMP_OFFSET`（与协议文档页的 firstTimestamp 名不同），书用 baseTimestamp 与代码命名一致，G5 的落地表述在源码面站得住。
- 其余条目（R2-01/02/10/05/06/08/09）所在区域无第一轮改文，无覆盖风险。

## 清单外（本轮顺带发现，非 R2 范围）

1. `chapters/03-lifecycle/outline.md:99-112`：写作计划仍保留「八阶段」「处理完在途」「停控制器→停副本管理→通知集群」的旧序——若 outline 视为活文档，应随 R2-04/06 一并订正，防止后续轮次回潮。
2. fig-2-7.svg 行 45 `maxTimestamp` 标签「批最晚时间戳」：CreateTime 下确为批内最大时间戳，可守；但 LogAppendTime 模式为 Broker 追加时间（表 2-1 已按 G5 写明），图标签未含此限定，属可留的简化，记录备查。
3. 版本备注：unstable（8.x）中 `dict_force_resize_ratio` 已由 7.x 的 5 改为 4，且新增 `force_full_rehash` 类型标志（`while (dictRehash(d,1000))` 批量搬桶）——本轮无条目触及，若日后讨论 BGSAVE 期间强制扩容比例需按 7.x 口径写 5。
4. Redis 证据源为 unstable 分支的声明：所有被引函数（dictRehash/rehashEntriesInBucketAtIndex、evictionPoolPopulate、performEvictions、ACLSelectorCheckCmd）在 7.x 与 unstable 间结构未变（8.x 仅改字段命名 ht_table/ht_size_exp 与 no_value 优化），如需 7.x 原文逐字引用，网络恢复后可再拉 7.2 tag 复核一次。
