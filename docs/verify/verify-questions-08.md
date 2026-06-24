# 第08章《数据同步》事实核查问题清单

## 8.2 Redis 的做法

### Q1: PSYNC2 引入版本
**章节位置**: 8.2 增量同步：PSYNC2 与复制积压缓冲区
**原文陈述**: "PSYNC2（Redis 4.0 引入，是对 2.8 版 PSYNC 的加固）"
**待确认点**: PSYNC2 是否在 Redis 4.0 引入（有说法是 Redis 4.0 引入 partial resync 增强），以及老版 PSYNC 是否确实在 2.8 引入（Redis 2.8 首次引入复制中的部分重同步功能）。
**建议验证来源**: Redis release notes / Redis source code / 官方文档

### Q2: PSYNC 命令格式
**章节位置**: 8.2 全量同步
**原文陈述**: "主节点收到副本的 `PSYNC ? -1`（表示'我什么都没有'）"
**待确认点**: 全量同步时副本是否使用 PSYNC ? -1（当前版本已用 REPLCONFIG + PSYNC 新格式还是旧格式仍使用？数据完整同步的初始请求格式究竟是 `PSYNC ? -1` 还是其他）。
**建议验证来源**: Redis 官方复制文档 / Redis 源码 replication.c

### Q3: PSYNC 重连命令格式
**章节位置**: 8.2 增量同步：PSYNC2 与复制积压缓冲区
**原文陈述**: "把自己的 `replica_offset` 通过 `PSYNC <replid> <offset>` 报给主节点"
**待确认点**: 重连时 PSYNC 的参数顺序和格式是否正确。PSYNC 命令参数顺序是 `PSYNC <replicationid> <offset>` 还是其他。
**建议验证来源**: Redis 官方文档、源码

### Q4: repl-backlog-size 默认值
**章节位置**: 8.2 增量同步：PSYNC2 与复制积压缓冲区
**原文陈述**: "主节点维护一个固定大小（默认约 1MB，可调 `repl-backlog-size`）的环形缓冲区"
**待确认点**: `repl-backlog-size` 的默认值是否确实是 1MB（不同 Redis 版本中该默认值是否发生过变化，例如 7.0 及后续版本是否调整）。
**建议验证来源**: Redis 配置文件 redis.conf / redis.io 文档

### Q5: backlog 环形缓冲区结构
**章节位置**: 8.2 增量同步：PSYNC2 与复制积压缓冲区
**原文陈述**: "存'最近 N 字节的复制流'。这是一个滑动窗口——新命令进来，老命令被覆盖。"
**待确认点**: backlog 本质上是否确实是环形缓冲区（ring buffer），使用方式是否如描述（覆盖老数据）。
**建议验证来源**: Redis 源码 replication.c 或相关数据结构

### Q6: replid2 保留老 replid 与 offset
**章节位置**: 8.2 增量同步：PSYNC2 与复制积压缓冲区
**原文陈述**: "新主会生成新的 replid，同时把老 replid 作为 `replid2` 连同老 offset 一起保留"
**待确认点**: PSYNC2 中 replid2 和 offset2 的保留机制是否如此描述。故障转移后新主是否确实会保留老 replid 作为 replid2，并保留对应的老 offset。
**建议验证来源**: Redis 源码 replication.c / Redis 官方博客

### Q7: PSYNC2 比对 replid2 的判断逻辑
**章节位置**: 8.2 增量同步：PSYNC2 与复制积压缓冲区
**原文陈述**: "可拿老 replid 与新主的 `replid2` 比对，若 offset 仍在 backlog 窗口内，照样走部分重同步"
**待确认点**: PSYNC2 中副本重连新主后，具体判断流程是否如此描述。除了比对 replid，还需要比对 offset 和 backlog 的边界关系，以及 repl_offset2 的使用。
**建议验证来源**: Redis 官方博客 / Redis 源码

### Q8: RESP 重写后发送
**章节位置**: 8.2 传播单元：命令本身
**原文陈述**: "把这条命令（用 Redis 序列化协议 RESP 重写后）原样发送给所有副本"
**待确认点**: 复制流中传输的是否确实是 RESP 序列化后的命令原样（副本侧直接执行该命令）。某些场景（如 EXPIRE、带有绝对时间的命令）是否会先转换或使用 PEXPIREAT 等效命令再下发。
**建议验证来源**: Redis replication 文档、源码

### Q9: 非确定性命令改写（TIME）
**章节位置**: 8.2 传播单元：命令本身
**原文陈述**: "复制链路上对这类命令做特殊改写（比如把 `TIME` 在主节点取到的时间作为参数下发）"
**待确认点**: Redis 复制中是否确实将 TIME 命令结果作为参数下发，还是对 TIME 等非确定性命令的处理方式是不传播该命令本身（仅主节点执行，结果不复用），或者根本不允许非确定性命令的传播。
**建议验证来源**: Redis 源码 / 官方文档关于 non-deterministic commands 的处理

### Q10: min-replicas-to-write 和 min-replicas-max-lag 语义
**章节位置**: 8.2 关键取舍：把同步强度做成可写门槛
**原文陈述**: "`min-replicas-to-write N` + `min-replicas-max-lag T`。这条规则的意思是——主节点接受写入的前提是：至少有 N 个副本在线（连接存活），且这些副本的延迟（`master_repl_offset - replica_offset` 折算到秒）不超过 T 秒。"
**待确认点**: min-replicas-to-write 和 min-replicas-max-lag 语义是否如此（连接的 replica 数量及最大允许延迟）。min-replicas-max-lag 是否确实以秒为单位，延迟计算方式是否基于 offset 差距折算。
**建议验证来源**: Redis 官方文档 / redis.conf

### Q11: 复制拓扑——树状结构
**章节位置**: 8.2 单向异步
**原文陈述**: "副本只能有一个主（一个数据集的权威来源），形成树状的复制拓扑。"
**待确认点**: 副本是否可以设置为其他副本的从，形成类似链式或树（tree）状结构。
**建议验证来源**: Redis 复制文档

### Q12: BGSAVE fork 内存翻倍风险
**章节位置**: 8.2 全量同步
**原文陈述**: "`BGSAVE` 的 fork 在大实例上会有一瞬间的内存翻倍风险（写时复制）和短暂的停顿"
**待确认点**: fork 执行 BGSAVE 是否确实因写时复制（Copy-on-Write）可能导致内存翻倍。大实例上的"短暂的停顿"的确切范围是否与内存大小相关（通常是秒级到几十毫秒级）。
**建议验证来源**: Redis 持久化文档、性能分析文章

## 8.3 MySQL 的做法

### Q13: binlog 主流 ROW 格式
**章节位置**: 8.3 传播单元：binlog event
**原文陈述**: "现代主流是 ROW 格式，记录的是'行 k 从值 v1 变成了 v2'这样的行级事件"
**待确认点**: MySQL 主流是否确认为 ROW 格式；ROW 格式记载内容是否包括完整的前后镜像（包含所有列值的 before image 和 after image）。
**建议验证来源**: MySQL 官方文档关于 binlog 格式

### Q14: ROW 格式解决歧义
**章节位置**: 8.3 传播单元：binlog event
**原文陈述**: "`UPDATE t SET x = x + 1` 在不同副本上可能影响不同行数（如果副本上数据状态不同），还可能因为非确定性函数产生不同结果。ROW 格式把'最终状态变化'作为事实下发，绕开了所有歧义"
**待确认点**: ROW 格式是否确实完全避免了语句级 binlog 的歧义问题。但是 ROW 格式下同一个 ROW 事件如果在不同副本上有不同的字符集/排序规则是否也会产生不同结果。
**建议验证来源**: MySQL 官方手册关于 ROW vs STATEMENT 模式的差异

### Q15: IO 线程与 SQL 线程架构
**章节位置**: 8.3 传统复制：两段式的拉取 + 回放
**原文陈述**: "IO 线程（从节点上）：主动连接主节点，订阅主节点的 binlog 流，把收到的事件写入本地的中继日志（relay log）"
**待确认点**: 主节点角度是否有 dump 线程与之对应；IO 线程写入 relay log 的细节（是否写到 relay log，不是直接写到存储引擎）。
**建议验证来源**: MySQL 复制架构官方文档

### Q16: SQL 线程回放
**章节位置**: 8.3 传统复制：两段式的拉取 + 回放
**原文陈述**: "SQL 线程（从节点上）：读 relay log，按顺序回放事件到本地存储引擎"
**待确认点**: 在 8.0 多线程并行复制模式下，复制架构中 SQL 线程是否已变为协调线程（coordinator thread）加多个 worker 线程，而非单个 SQL 线程串行回放。
**建议验证来源**: MySQL 8.0 并行复制文档

### Q17: 异步复制默认行为
**章节位置**: 8.3 异步复制：默认的 AP 形态
**原文陈述**: "默认配置下，MySQL 复制是异步的：主节点提交事务（写完 binlog 并落盘）就立刻给客户端返回 OK，不等任何副本"
**待确认点**: MySQL 异步复制是否确实为默认配置。binlog 是否必须落盘才返回（中间还涉及 sync_binlog 配置的影响，若 sync_binlog=0 则 binlog 并非每次提交都落盘）。
**建议验证来源**: MySQL 官方手册

### Q18: 半同步 ACK 条件
**章节位置**: 8.3 半同步复制：可降级的一致性
**原文陈述**: "主节点等至少一个副本的 ACK（副本 IO 线程把事件写到 relay log 即回 ACK，不等本地回放）才返回成功"
**待确认点**: 半同步复制中，ACK 条件是否确实是"IO 线程把事件写入 relay log"即回 ACK，不等 SQL 线程回放。还是说 AFTER_SYNC 和 AFTER_COMMIT 两种模式影响 ACK 的时机。
**建议验证来源**: MySQL 官方文档关于半同步复制

### Q19: rpl_semi_sync_source_timeout 默认值
**章节位置**: 8.3 半同步复制：可降级的一致性
**原文陈述**: "主节点等 ACK 超时（`rpl_semi_sync_source_timeout`，默认 10 秒）会自动降级回异步"
**待确认点**: rpl_semi_sync_source_timeout 默认值是否为 10 秒（在 MySQL 8.0.x 中）。
**建议验证来源**: MySQL 8.0 官方文档关于半同步复制参数

### Q20: 8.0.26 重命名
**章节位置**: 8.3 半同步复制：可降级的一致性
**原文陈述**: "8.0.26 起，半同步相关的 master/slave 命名变量统一重命名为 source/replica（如 `rpl_semi_sync_master_enabled` → `rpl_semi_sync_source_enabled`），旧名变量在过渡期仍可用但已标记弃用。"
**待确认点**: 该重命名是否在 8.0.26 发生（有说法是 8.0.26/8.0.27 或更晚版本）。变量名 `rpl_semi_sync_master_enabled` 是否确切重命名为 `rpl_semi_sync_source_enabled`。
**建议验证来源**: MySQL 8.0 release notes

### Q21: GTID 格式
**章节位置**: 8.3 GTID：让位点从脆弱变得鲁棒
**原文陈述**: "GTID（Global Transaction Identifier，全局事务标识）把位点升级成 `source_id:transaction_id` 的形式——`source_id` 是发起事务的源节点的 UUID，`transaction_id` 是该节点上单调递增的事务序号。"
**待确认点**: GTID 格式确切为 `UUID:sequence_number`，其中 sequence_number 是否为单调递增且不能回滚；如果事务在源节点回滚了，sequence_number 是否仍被消耗不重用。
**建议验证来源**: MySQL 官方文档关于 GTID

### Q22: GTID 的唯一性
**章节位置**: 8.3 GTID：让位点从脆弱变得鲁棒
**原文陈述**: "每个事务在 binlog 里都有一个全局唯一的 GTID。"
**待确认点**: 是否真的"每个事务"都有 GTID（仅在 GTID 模式下开启 `gtid_mode=ON` 时生效，传统非 GTID 复制模式下没有 GTID）。
**建议验证来源**: MySQL 官方文档

### Q23: 8.0 并行复制基于 LOGICAL_CLOCK
**章节位置**: 8.3 多线程并行复制
**原文陈述**: "8.0 的多线程并行复制（基于 `LOGICAL_CLOCK` 的组提交并行）"
**待确认点**: 基于 LOGICAL_CLOCK 的并行复制是在 MySQL 5.7 引入还是 8.0 引入。5.7 已有 `slave_parallel_type=LOGICAL_CLOCK`，8.0 是否只是沿用并优化。
**建议验证来源**: MySQL 5.7 和 8.0 发布说明

### Q24: 组提交内事务无冲突
**章节位置**: 8.3 多线程并行复制
**原文陈述**: "同一组提交（group commit）内的事务，本身就没冲突过（否则不可能同组落盘）"
**待确认点**: 该推理逻辑是否严谨——InnoDB 组提交（group commit）是将多个事务的 binlog 写入合并为一次 fsync，但不一定意味着这些事务的修改在数据上没有交集（冲突）。同组提交的事务间仍然可能因为锁等待产生冲突，只是它们在 prepare 阶段都已通过锁检测。
**建议验证来源**: MySQL 组提交机制文档

### Q25: replica_parallel_workers 参数名
**章节位置**: 8.3 多线程并行复制
**原文陈述**: "配合 `replica_parallel_workers`（8.0.26 前为 `slave_parallel_workers`）、`replica_parallel_type=LOGICAL_CLOCK` 等参数"
**待确认点**: slave_parallel_workers 和 replica_parallel_workers 的重命名是否在 8.0.26（与半同步相关参数同一批次）。
**建议验证来源**: MySQL 8.0 release notes

### Q26: XCom 是 Paxos 变种
**章节位置**: 8.3 组复制（MGR）
**原文陈述**: "把 binlog event 当作共识协议（XCom，Paxos 变种）的 log entry"
**待确认点**: XCom 是否是 Paxos 变种（确切说是基于 Paxos 的 consensus library），还是基于 Paxos 但做了某种改造。
**建议验证来源**: MySQL Group Replication 文档 / XCom 源码

### Q27: MGR 多数派确认才能提交
**章节位置**: 8.3 组复制（MGR）
**原文陈述**: "要求多数派确认才能提交"
**待确认点**: MGR 中事务是否在多数派确认后才在本地 binlog 落盘并返回客户端。
**建议验证来源**: MySQL Group Replication 架构文档

### Q28: group_replication_consistency 默认值
**章节位置**: 8.3 组复制（MGR）
**原文陈述**: "默认 `EVENTUAL`（不额外等待）"
**待确认点**: group_replication_consistency 的默认值是否为 EVENTUAL（在 MySQL 8.0.x 中）。
**建议验证来源**: MySQL 官方文档

### Q29: group_replication_consistency 档位
**章节位置**: 8.3 组复制（MGR）
**原文陈述**: "从弱到强有 `BEFORE_ON_PRIMARY_FAILOVER`（仅主切换时等追平）、`BEFORE`（读前等本节点追平）、`AFTER`（写后等全组追平）、`BEFORE_AND_AFTER`（读写都等）几档"
**待确认点**: 这些档位的名称和顺序是否正确（EVENTUAL 是否是最弱档，BEFORE_ON_PRIMARY_FAILOVER, BEFORE, AFTER, BEFORE_AND_AFTER 依次增强）。
**建议验证来源**: MySQL 官方文档关于 Group Replication Consistency Levels

### Q30: clone 插件 8.0.17+
**章节位置**: 8.3 分布式恢复
**原文陈述**: "8.0.17+ 提供了 clone 插件"
**待确认点**: clone 插件是否在 MySQL 8.0.17 首次引入。
**建议验证来源**: MySQL 8.0.17 release notes

### Q31: clone 插件行为
**章节位置**: 8.3 分布式恢复
**原文陈述**: "新成员直接从现有成员克隆一份完整的数据目录（物理拷贝），跳过漫长的 binlog 回放；克隆完再用 binlog 增量追平克隆期间的新事务"
**待确认点**: clone 插件的恢复流程是否完整如描述：先做全量物理复制，再用 binlog 增量补追。
**建议验证来源**: MySQL clone 插件文档

## 8.4 Kafka 的做法

### Q32: 纯拉模式描述
**章节位置**: 8.4 纯拉模式
**原文陈述**: "Kafka 复制用的是**纯拉模式**：Follower 主动向 Leader 发 `FETCH` 请求拉取日志。"
**待确认点**: Kafka 复制是否完全是纯拉模式（Follower 主动拉取），还是早期版本可能有所不同（依然通过 FETCH 请求但可视为 pull-based 的复制）。
**建议验证来源**: Kafka 官方文档 / Apache Kafka 源码

### Q33: Follower FETCH 与消费者同路径
**章节位置**: 8.4 纯拉模式
**原文陈述**: "Follower 的 FETCH 请求和消费者的 FETCH 请求走的是同一条读路径。Leader 不区分对面是副本还是消费者"
**待确认点**: Leader 是否对 Follower 的 FETCH 和消费者的 FETCH 使用完全相同的读路径。是否有不同的处理逻辑（例如 Follower FETCH 可能影响 HW 更新而消费者 FETCH 不影响）。
**建议验证来源**: Kafka 源码、架构文档

### Q34: 零拷贝、页缓存
**章节位置**: 8.4 纯拉模式
**原文陈述**: "零拷贝、页缓存命中、批量返回"
**待确认点**: Kafka 读取日志给副本时是否使用零拷贝（sendfile）。页缓存（page cache）命中率是否会因副本 FETCH 而提高（还是副本只是额外消费者）。
**建议验证来源**: Kafka 性能优化文档

### Q35: HW = ISR 中最小 LEO
**章节位置**: 8.4 LEO、HW 与 ISR
**原文陈述**: "HW 等于当前 ISR 中所有副本（含 Leader 自己）的最小 LEO"
**待确认点**: HW 的推进条件是否确实等于 ISR 中最小 LEO。replica.fetch.max.bytes 是否影响 FW（非 ISR 副本的 LEO 是否不计入 HW 计算）。
**建议验证来源**: Apache Kafka 文档 / 源码

### Q36: HW 以下才算已提交
**章节位置**: 8.4 LEO、HW 与 ISR
**原文陈述**: "HW 以下才算已提交、消费者才读得到"
**待确认点**: 消费者读取消息时是否受 HW 限制。Kafka 是否只有 HW 以下的消息才对消费者可见（高版本 Kafka 或某些配置下是否有所调整，如引入 leader epoch 后消费者读取策略的变化）。
**建议验证来源**: Kafka 官方文档 / KIP

### Q37: replica.lag.time.max.ms 参数
**章节位置**: 8.4 LEO、HW 与 ISR
**原文陈述**: "`replica.lag.time.max.ms` 阈值之外就被踢出 ISR"
**待确认点**: 该参数名是否正确。Kafka 参数是 `replica.lag.time.max.ms` 还是 `replica.max.lag.time.ms`。
**建议验证来源**: Apache Kafka 官方文档关于 ISR 配置

### Q38: leader-epoch-checkpoint 文件格式
**章节位置**: 8.4 leader epoch：解决老 Leader 复活的脑裂
**原文陈述**: "落盘到分区的 `leader-epoch-checkpoint` 文件里（一行 = 任期号 + 该任期起始位移）"
**待确认点**: leader-epoch-checkpoint 文件的格式。它存储的是 (epoch, startOffset) 对，还是 (epoch, offset) 对；是否每个分区独立一个文件还是共享的。
**建议验证来源**: Apache Kafka 源码 / 文档

### Q39: EndOffsetForEpoch API
**章节位置**: 8.4 leader epoch：解决老 Leader 复活的脑裂
**原文陈述**: "并在响应里回一个 `EndOffsetForEpoch`（'该 epoch 的权威日志到哪为止'）"
**待确认点**: 该 RPC 名称在 Kafka 协议中是否为 `EndOffsetForEpoch`（或称 `OffsetForLeaderEpoch` / `OffsetsForLeaderEpoch`）。
**建议验证来源**: Apache Kafka 协议文档 / KIP-320

### Q40: FETCH 请求中带入 (epoch, offset)
**章节位置**: 8.4 leader epoch：解决老 Leader 复活的脑裂
**原文陈述**: "在 FETCH 请求里带上自己最后一个已知的 `(epoch, offset)`"
**待确认点**: Follower 是否在 FETCH 请求中带入 (epoch, offset)，还是 Kafka 副本使用单独的 `OffsetForLeaderEpochRequest` 来获取截断边界。
**建议验证来源**: Apache Kafka 源码 / KIP-320

### Q41: acks 三档定义
**章节位置**: 8.4 acks 旋钮
**原文陈述**: "`acks` 旋钮（0 / 1 / all 三档）"
**待确认点**: acks 取值是否确切为 0, 1, all（-1 被用作 all 的同义词）。
**建议验证来源**: Apache Kafka 生产者配置文档

### Q42: 3.0 起默认 acks=all
**章节位置**: 8.4 acks 旋钮
**原文陈述**: "3.0 起默认 `acks=all` 的定位调整，已在第 6 章 6.4.3 节展开"
**待确认点**: Kafka 3.0 是否确实将默认 acks 改为 all。需要确认 Kafka 3.0 的确切变更。
**建议验证来源**: Apache Kafka 3.0 release notes / KIP

### Q43: NotEnoughReplicasException
**章节位置**: 8.4 acks 旋钮
**原文陈述**: "Kafka 在 ISR 不足 `min.insync.replicas` 时则是拒绝写入并抛 `NotEnoughReplicasException`"
**待确认点**: 当 ISR 不足 min.insync.replicas 时，Kafka 是否抛 NotEnoughReplicasException（在较新版本中是否可能有不同行为，如 `NotEnoughReplicasAfterAppendException` 等）。
**建议验证来源**: Apache Kafka 官方文档 / 源码

### Q44: unclean.leader.election.enable 3.x 默认值
**章节位置**: 8.4 unclean leader 选举
**原文陈述**: "禁止（false，3.x 默认）"
**待确认点**: Kafka 3.x 中 unclean.leader.election.enable 默认值是否为 false。
**建议验证来源**: Apache Kafka 配置文档

### Q45: unclean.leader.election.enable 自 0.11 起默认 false
**章节位置**: 8.4 unclean leader 选举
**原文陈述**: "这个默认值其实自 0.11 起就是 false，3.x 沿用并强化了这一取向"
**待确认点**: Kafka 0.11 是否已将 unclean.leader.election.enable 的默认值改为 false。
**建议验证来源**: Apache Kafka 0.11 release notes / 配置变更文档

### Q46: KRaft 版本历史
**章节位置**: 8.4 KRaft：元数据同步与数据同步同构
**原文陈述**: "KRaft 自 2.8 作为预览特性引入，在 3.3 达到生产可用"
**待确认点**: KRaft (Kafka Raft) 是否在 2.8 作为预览特性引入，3.3 是否达到生产可用（也有说法是 3.4 或 3.5 才达到生产级别）。
**建议验证来源**: Apache Kafka release notes / KIP-500

### Q47: 幂等通过 ProducerId + ProducerEpoch + BaseSequence
**章节位置**: 8.4 幂等与事务
**原文陈述**: "幂等靠 ProducerId + ProducerEpoch + BaseSequence 实现"
**待确认点**: 幂等机制是否包含 ProducerEpoch（还是只是 ProducerId + Sequence Number，epoch 是事务使用时才涉及的概念）。
**建议验证来源**: Apache Kafka 官方文档关于幂等和事务

### Q48: 事务通过两阶段提交
**章节位置**: 8.4 幂等与事务
**原文陈述**: "事务更进一步：跨多个分区的一组写入要么全部成功要么全部不可见，靠 transaction coordinator 和两阶段提交（对消费者暴露 `committed` 标记）实现"
**待确认点**: Kafka 事务是否确实使用类似两阶段提交（2PC）的协议（先预写 transaction marker，再 commit/abort）。对消费者暴露 committed 标记是否依赖于消费者配置 `isolation.level=read_committed`。
**建议验证来源**: Apache Kafka 事务文档 / KIP-98

## 表 8-1 横向对比

### Q49: 一致性模型——Redis AP
**章节位置**: 表 8-1
**原文陈述**: "Redis: 异步最终一致（AP）"
**待确认点**: 将 Redis 归类为"AP"是否准确。Redis 复制是异步最终一致，但 Redis 自身并非完整 AP（它是单线程单节点强一致的，只是副本间是最终一致）。
**建议验证来源**: Redis 复制文档

### Q50: 全量同步——主节点阻塞
**章节位置**: 表 8-1
**原文陈述**: "Redis: fork RDB 传输（主节点阻塞 + 内存翻倍风险）"
**待确认点**: BGSAVE 期间主节点是否阻塞。事实上 BGSAVE 是 fork 后子进程在后台生成 RDB，父进程继续服务请求，主节点不阻塞（尽管 fork 瞬间微阻塞）。
**建议验证来源**: Redis 持久化文档

### Q51: 全量同步——clone 插件或全量 binlog 回放
**章节位置**: 表 8-1
**原文陈述**: "MySQL: clone 插件或全量 binlog 回放"
**待确认点**: MySQL 全量同步是否确实只有 clone 插件或 binlog 回放两种方式（传统复制中使用 rsync + xtrabackup 等工具是否也应该提及）。
**建议验证来源**: MySQL 复制实践

## 其他部分

### Q52: 延迟-一致性曲线定性描述
**章节位置**: 8.1 一致性是延迟的函数
**原文陈述**: "主写完立即返回（异步复制），延迟最低，但故障切换时可能丢已确认的写；等多数派确认（强一致），最安全，但每一次写都要承担一次跨节点的确认往返。"
**待确认点**: 该定性描述在理论上是否准确。强一致在多数派确认中是否需要两次跨节点往返（prepare + accept vs 一次往返），取决于具体共识协议。
**建议验证来源**: 分布式一致性文献

### Q53: 传播单元是"同步机制的基因"的因果论断
**章节位置**: 8.5 解读一
**原文陈述**: "传播单元是同步机制的基因，理解了一家选了什么单元，就理解了它后续一切选择的由来"
**待确认点**: 该因果论断是否过度简化——传播方式、位点形态和故障恢复粒度是否完全由传播单元决定，还是也有独立的设计考量。
**建议验证来源**: 各系统的架构设计文档

### Q54: raft 用 term（原书将 leader epoch 与 raft term 关联）
**章节位置**: 8.4 KRaft
**原文陈述**: "都是日志 + 副本 + Leader + epoch（Raft 用 term）"
**待确认点**: Raft 的术语是 term，Kafka leader epoch 是否与 Raft 的 term 概念严格对应（功能相当但实现有差异）。
**建议验证来源**: Raft 论文和 Kafka 文档

### Q55: "进度坐标"三条件
**章节位置**: 8.6 启示二
**原文陈述**: "这把尺子要满足三个条件：单调（能比较前后）、持久（重启不丢）、唯一（跨节点不歧义）。GTID 把这三点做得最完备"
**待确认点**: GTID 是否满足"跨节点不歧义"（不同节点的 UUID 做前缀，确实唯一）；replication offset 和 Kafka offset 是否不满足"唯一"（一个集群内的字节偏移量是否可能因主切换而产生歧义）。
**建议验证来源**: 三系统的位点设计文档

### Q56: 反模式——位点丢失致全量重灌
**章节位置**: 8.6 反模式提醒
**原文陈述**: "relay log 被清、offset 元数据损坏，都会让原本可以增量的同步退回全量"
**待确认点**: MySQL relay log 被清后是否一定退回全量（GTID 模式是否只需要从主节点 binlog 中查找未应用的事务，可不需要全量）。
**建议验证来源**: MySQL GTID 恢复机制
