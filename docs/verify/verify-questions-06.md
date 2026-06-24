# 第06章《集群架构》事实核查问题清单

> 生成日期: 2026-06-23
> 核查范围: 第6章全文（含引言、6.1-6.7节）
> 说明: 以下每个问题均以"原文具体陈述→需要验证的点"为结构展开，建议逐一查阅官方文档、源码或已被社区广泛引用的权威资料。

---

## 一、Redis 部分（6.2 节及散见于其他节）

### Q01: REPLICAOF vs SLAVEOF 命令名
**章节位置**: 6.2.1
**原文陈述**: "在从节点上执行 `REPLICAOF host port`（旧版叫 `SLAVEOF`）"
**待确认点**: `REPLICAOF` 命令从哪个 Redis 版本起引入的？`SLAVEOF` 是何时标记为 deprecated 的？
**建议验证来源**: Redis 官方文档 / CHANGELOG (Redis 5.0 引入 REPLICAOF)

### Q02: 全量同步中 fork + RDB 的机制
**章节位置**: 6.2.1
**原文陈述**: "第一次建立连接时做全量同步——主节点 `fork` 出子进程，把内存打成一个 RDB（快照文件）发给从节点"
**待确认点**: Redis 主从全量同步的具体流程是否完全如此？是否存在 diskless 复制（直接通过网络发送 RDB 而不落盘）等变体？该描述忽略了 6.2 之后引入的 diskless 复制选项（repl-diskless-sync）。
**建议验证来源**: Redis 官网 replication 文档

### Q03: 复制积压缓冲区（replication backlog）的用途
**章节位置**: 6.2.1
**原文陈述**: "期间主节点新产生的写命令先存进复制积压缓冲区（replication backlog），RDB 发完再补发这部分增量"
**待确认点**: 积压缓冲区在有从节点连接时是否始终存在？大小由什么参数（repl-backlog-size）控制？默认值是多少？
**建议验证来源**: redis.conf 默认配置 / 官方文档

### Q04: 部分重同步的条件
**章节位置**: 6.2.1
**原文陈述**: "如果从节点短暂断线又重连，且断线期间主节点的写位移（offset）没有超出积压缓冲区的范围，就只补差量，这叫部分重同步（partial resync）"
**待确认点**: 部分重同步还涉及 master_replid 的匹配（主节点重启后 master_replid 会变化，导致从节点必须做全量同步），原文未提及此前提。
**建议验证来源**: Redis 官方 replication 文档 / `PSYNC` 命令说明

### Q05: Sentinel 主观下线与客观下线的过程
**章节位置**: 6.2.2
**原文陈述**: "超过 `down-after-milliseconds` 没回应，这个 Sentinel 把主节点标记为**主观下线**（SDOWN）...如果达到配置的 quorum 数量都认为主节点挂了，就升级为**客观下线**（ODOWN）"
**待确认点**: SDOWN→ODOWN 的完整决策流程是否符合原文所述？ODOWN 的触发除了 quorum 还需要满足 `is-master-down-after-milliseconds` 等参数条件吗？
**建议验证来源**: Redis Sentinel 官方文档

### Q06: Sentinel 的 Gossip 传播判断
**章节位置**: 6.2.2
**原文陈述**: "然后它通过 Gossip 把这个判断扩散给其他 Sentinel"
**待确认点**: Sentinel 之间交换消息使用的是 Gossip 协议还是 Pub/Sub 频道（`__sentinel__:hello`）？准确地说，Sentinel 间通过 Redis Pub/Sub 来发现彼此并交换关于主从节点的信息，而非传统意义的 Gossip。
**建议验证来源**: Redis Sentinel 官方文档

### Q07: Sentinel 的 Raft-like 选举
**章节位置**: 6.2.2
**原文陈述**: "Sentinels 之间用一种 Raft 风格的选举（Redis 官方文档称之为 "Raft-like"，借鉴了 Raft 的任期号加多数派投票，但没有完整的 Raft 日志复制）选出一个 Leader Sentinel 主持转移"
**待确认点**: Redis 官方文档是否仍使用 "Raft-like" 来描述 Sentinel 选举？选举的具体机制（epoch 递增 + 多数派票数）与 Raft 选举算法的异同？
**建议验证来源**: Redis Sentinel 官方文档 / Redis 源码 (`sentinel.c`)

### Q08: Sentinel 选新主的三个维度
**章节位置**: 6.2.2
**原文陈述**: "再按优先级、复制位移（offset）、runid 三个维度从从节点里挑一个提升为新主"
**待确认点**: 这三个维度的排序和比较规则是否准确？runid 的比较是字典序较大还是较小者优先？
**建议验证来源**: Redis 官方文档 / `sentinel.c` 源码中的 `sentinelSelectSlave()` 函数

### Q09: Sentinel 的 quorum 配置
**章节位置**: 6.2.2
**原文陈述**: "如果达到配置的 quorum 数量都认为主节点挂了，就升级为**客观下线**"
**待确认点**: quorum 是 Sentinel 配置中的哪个参数？它的确切含义（仅仅是 ODOWN 所需的票数，不是 Leader 选举所需的票数）？
**建议验证来源**: Redis Sentinel 官方文档

### Q10: CRC16 哈希算法
**章节位置**: 6.2.3
**原文陈述**: "映射公式是 `CRC16(key) mod 16384`"
**待确认点**: Redis Cluster 使用的具体是哪种 CRC16 变种（如 CRC16-CCITT、CRC16-IBM 等）？不同客户端实现是否确保完全一致的哈希结果？
**建议验证来源**: Redis Cluster 规范 / 源码 (`cluster.c`)

### Q11: 16384 个槽（slot）的由来
**章节位置**: 6.2.3
**原文陈述**: "为什么是 16384 这个数，而不是更大或更小？社区的主流解释（以社区主流解释为准，官方未严格论证）是：Gossip 消息里每个节点要携带自己负责的槽位 bitmap，16384 个槽对应 16384/8 = 2KB 的 bitmap"
**待确认点**: Redis 官方是否有对 16384 这一数字选型的正式解释？Gossip 消息中是否确实每个节点都携带完整 2KB bitmap（还是仅携带增量变更）？
**建议验证来源**: Redis 作者 antirez 的博客 / Redis Cluster 规范 / GitHub issues

### Q12: MOVED 与 ASK 重定向的语义区别
**章节位置**: 6.2.3
**原文陈述**: "MOVED 表示"这个槽已经永久不在你这了，去这个新地址"，客户端收到后更新本地映射表，以后都走新地址；ASK 表示"这个槽正在迁移中，本次请求请去临时地址试一下"，是一次性重定向，客户端不更新映射表"
**待确认点**: ASK 重定向的确切语义是否如原文所述？ASKING 命令起什么作用？客户端在收到 ASK 后是否需要发送 ASKING 命令再重试？
**建议验证来源**: Redis Cluster 规范 / 官方文档

### Q13: Redis Cluster 禁用 SELECT 命令
**章节位置**: 6.2.3
**原文陈述**: "此外，Redis Cluster 禁用了多数据库的 `SELECT` 命令（只有 0 号库）"
**待确认点**: Redis Cluster 是否确实禁用了 `SELECT` 命令？是否所有版本（包括 7.x）都是如此？
**建议验证来源**: Redis Cluster 规范

### Q14: 哈希标签（hash tag）语法
**章节位置**: 6.2.3
**原文陈述**: "可以用哈希标签（hash tag）`{user:1001}.name`、`{user:1001}.email` 强制让带相同 `{...}` 的 key 落到同槽"
**待确认点**: hash tag 的精确匹配规则——是否只匹配第一个 `{` 与第一个 `}` 之间的内容？是否支持嵌套花括号？如果花括号内为空（`{}`）会怎样？
**建议验证来源**: Redis Cluster 规范

### Q15: Gossip 消息类型（PING/PONG/MEET/FAIL）
**章节位置**: 6.2.3
**原文陈述**: "靠 Gossip 协议（PING/PONG/MEET/FAIL 消息）互相交换和传播集群状态"
**待确认点**: FAIL 消息是 Gossip 消息的一种还是通过 Pub/Sub 传播的？在 Redis Cluster 的 Gossip 实现中，MEET/PING/PONG/FAIL 各自的用途是否如原文所述？
**建议验证来源**: Redis 源码 (`cluster.c`) / Redis Cluster 规范

### Q16: Gossip 收敛时间
**章节位置**: 6.2.3
**原文陈述**: "代价是收敛慢，故障感知到全集群达成共识可能要几秒到十几秒"
**待确认点**: Redis Cluster 的 Gossip 收敛时间是否有官方或基准测试数据？收敛时间受哪些因素影响（节点数、消息间隔 `cluster-node-timeout` 等）？
**建议验证来源**: Redis 官方文档 / 性能基准测试

### Q17: 从节点发起选举的 epoch 机制
**章节位置**: 6.2.3
**原文陈述**: "它的某个从节点会发起选举请求，向其他主节点拉票（用集群纪元 epoch 防止过期投票）"
**待确认点**: epoch（currentEpoch）在 Redis Cluster 选举中的具体作用是什么？它与 Raft 的 term 有何异同？从节点发起选举的触发条件是什么？
**建议验证来源**: Redis Cluster 规范

### Q18: 最小拓扑 3 主 3 从
**章节位置**: 6.2.3
**原文陈述**: "最小拓扑 3 主 3 从是工程惯例：3 个主是为了能在 1 个主宕机时仍有 2 个主凑成多数派完成选举"
**待确认点**: 3 个主节点宕掉 1 个后剩余 2 个是否满足"多数派"？多数派是超过总数的一半还是超过参与投票的一半？3 个主节点的多数派是 2（ceil(3/2+1)=2）还是 3？如果 1 个主宕了，剩余 2 个仍然构成多数（2 > 3/2），选举可以继续。
**建议验证来源**: Redis Cluster 规范

### Q19: Redis Cluster 的 AP 定位
**章节位置**: 6.2.3 / 6.5 / 6.6
**原文陈述**: "Redis Cluster 是 AP 系统" / "Redis 走 AP 路线"
**待确认点**: 严格 CAP 定义下，Redis Cluster 是否在所有分区场景都优先保可用？少数派分区中的主节点是否真的停止服务（不可写）？如果是，则它在某些场景下是 CP 行为。
**建议验证来源**: Redis Cluster 规范 / CAP 定理在 Redis Cluster 上的分析文章

---

## 二、MySQL 部分（6.3 节及散见于其他节）

### Q20: MySQL 5.6 引入 GTID
**章节位置**: 6.3.1
**原文陈述**: "MySQL 5.6 引入了全局事务标识（GTID，Global Transaction Identifier）"
**待确认点**: GTID 首次作为 GA 特性发布是在 MySQL 5.6 的哪个小版本（5.6.5, 5.6.10 等）？5.6.0 是否已包含 GTID？
**建议验证来源**: MySQL 5.6 Release Notes

### Q21: GTID 格式
**章节位置**: 6.3.1
**原文陈述**: "格式是 `source_id:transaction_id`"
**待确认点**: GTID 的完整格式是否还有 server_uuid 以外的组成部分？`source_id` 在 MySQL 文档中是否称为 server_uuid？GTID 的表示是否有 `uuid:seq_no` 的明确规范？
**建议验证来源**: MySQL 官方文档 GTID 章节

### Q22: MySQL 多线程复制（MTS）与组提交粒度
**章节位置**: 6.3.1
**原文陈述**: "MySQL 的多线程复制（MTS，Multi-Threaded Slave）按主节点的组提交（group commit）粒度并行回放——主节点同一组提交的事务之间必然无锁冲突，从节点就可以放心并行"
**待确认点**: MTS 的并行回放策略在 MySQL 5.7 中引入的基于 WRITESET 的并行度是否与组提交有关？不同 MySQL 版本的 MTS 策略（DATABASE、LOGICAL_CLOCK、WRITESET）的区别？原文所述的"同一组提交的事务无锁冲突"是否总是成立？
**建议验证来源**: MySQL 官方文档 / MySQL 5.7 新特性

### Q23: MySQL 8.0.26 半同步变量重命名
**章节位置**: 6.3.2
**原文陈述**: "参数方面，8.0.26 起半同步相关变量由 `master/slave` 统一重命名为 `source/replica`"
**待确认点**: 该重命名是否确实在 MySQL 8.0.26 中完成？涉及的具体变量名列表？是否有兼容性别名保留？
**建议验证来源**: MySQL 8.0.26 Release Notes

### Q24: 半同步复制的提交流程（AFTER_SYNC vs AFTER_COMMIT）
**章节位置**: 6.3.2
**原文陈述**: "半同步的精确提交流程（`AFTER_SYNC` vs `AFTER_COMMIT`）"
**待确认点**: `AFTER_SYNC` 和 `AFTER_COMMIT` 两种模式的准确行为差异是否如业界共识所述？MySQL 5.7 引入的 `AFTER_SYNC` 默认模式是否更安全？
**建议验证来源**: MySQL 官方文档 Semi-Synchronous Replication

### Q25: MySQL 5.7.17 MGR GA
**章节位置**: 6.3.3
**原文陈述**: "组复制（MGR，MySQL Group Replication）...在 MySQL 5.7.17 首次作为 GA 特性提供"
**待确认点**: MGR 是否确实在 MySQL 5.7.17 中达到 GA（General Availability）状态？还是 5.7.17 是首个包含 MGR 的版本但标记为实验室特性/Labs？
**建议验证来源**: MySQL 5.7.17 Release Notes / MGR 官方文档

### Q26: MySQL 8.0 对 MGR 的增强
**章节位置**: 6.3.3
**原文陈述**: "8.0 又做了大量增强（更完善的成员管理、更好的并发写性能）"
**待确认点**: MySQL 8.0 中 MGR 的具体增强点是否可以列举？是否在 8.0.0 还是之后的小版本逐步引入？
**建议验证来源**: MySQL 8.0 Release Notes / MGR 文档

### Q27: XCom 是 Paxos 变种
**章节位置**: 6.3.3
**原文陈述**: "一个叫 XCom 的 Paxos 变种"
**待确认点**: XCom 的实现是基于 Paxos 还是 Paxos 的变种（如 Multi-Paxos）？XCom 是否对标准 Paxos 做了特定的修改？有文献称 XCom 使用了 Paxos 的一个特定优化变体。
**建议验证来源**: XCom 源码 / MySQL 官方技术博客 / SIGMOD 论文

### Q28: MGR 的容错能力公式 (N-1)/2
**章节位置**: 6.3.3
**原文陈述**: "容错能力是经典的 (N-1)/2——3 个成员能容忍 1 个故障，5 个能容忍 2 个"
**待确认点**: (N-1)/2 这个公式计算的是能容忍的故障节点数吗？对于 N=3，(3-1)/2=1，意味着需要 2 个节点存活（多数派）。但严格来说，如果使用 Raft 风格要求 ceil(N/2) 的多数派，容错数是 floor((N-1)/2)。两个公式结果一致吗？确认是否精确匹配 Paxos/Raft 的容错上限。
**建议验证来源**: Paxos/Raft 容错论文 / MySQL MGR 文档

### Q29: MGR 多主模式的冲突检测机制
**章节位置**: 6.3.3
**原文陈述**: "多主模式（multi-primary）允许所有成员都可写，但写入要在组内做冲突检测（基于事务时间戳的 Certification），冲突的事务会被回滚"
**待确认点**: multi-primary 模式的冲突检测是否确实基于"事务时间戳"？Certification 机制的具体原理是什么——是基于行级别的写写冲突还是事务级别的冲突？
**建议验证来源**: MySQL Group Replication 官方文档 / 技术论文

### Q30: MGR 是 CP 系统
**章节位置**: 6.3.3 / 6.5
**原文陈述**: "MGR 是 CP 系统...当网络分区发生、组内凑不齐多数派时，少数派分区里的成员会**直接停止服务**——宁可不可用，也不允许脑裂写出脏数据"
**待确认点**: 严格 CAP 定义下，MGR 是否在所有网络分区场景都完全符合 CP？少数派分区的写入是否确实被完全阻止？是否有特定配置可以调整此行为？
**建议验证来源**: MySQL MGR 文档 / CAP 分析文章

### Q31: MGR 的写延迟与 Paxos 确认
**章节位置**: 6.3.3 / 6.5
**原文陈述**: "每笔事务都要走一轮跨节点的 Paxos 确认，写延迟随组成员数和跨机房网络延迟上升"
**待确认点**: MGR 的单主模式下，是否每笔事务都进行完整的跨节点 Paxos 确认？XCom 是否有优化（如 batching、pipelining）？
**建议验证来源**: MySQL 官方博客 / MGR 性能基准测试

### Q32: MGR 不分片的定位
**章节位置**: 6.3.4
**原文陈述**: "它不分片。组里每个成员都持有**全量数据**"
**待确认点**: MGR 是否有任何内置或计划中的分片能力？（如 MySQL InnoDB Cluster 中的分表策略？）当前 MySQL 官方是否有任何分片方案？（如 MySQL Cluster NDB 的分片与 MGR 完全不同。）
**建议验证来源**: MySQL MGR 官方文档 / MySQL 架构说明

### Q33: ShardingSphere、Vitess、MyCAT
**章节位置**: 6.3.4
**原文陈述**: "ShardingSphere、Vitess、MyCAT 这类方案在 MySQL 之上做分库分表"
**待确认点**: MyCAT 是否仍然活跃维护？ShardingSphere 的当前项目状态（Apache 基金会毕业）？Vitess 的定位（由 YouTube 开发，现为 CNCF 项目）是否仍适合在此列举。
**建议验证来源**: 各项目官方网站 / GitHub 仓库

---

## 三、Kafka 部分（6.4 节及散见于其他节）

### Q34: murmur2 哈希算法
**章节位置**: 6.4.1
**原文陈述**: "有 key 时默认用 `murmur2(key) % N` 做哈希路由"
**待确认点**: Kafka 默认分区器使用的是 murmur2 还是 murmur3？`murmur2` 的具体实现是否与标准库 `murmur2` 一致？
**建议验证来源**: Kafka 源码 `DefaultPartitioner` / KIP-480

### Q35: Kafka 2.4 粘性分区器默认：KIP-480
**章节位置**: 6.4.1
**原文陈述**: "生产者（Kafka 2.4 起经 KIP-480 改为默认）用"粘性分区"（sticky partitioner）"
**待确认点**: Sticky Partitioner 是否确实在 Kafka 2.4 中作为默认分区器引入？KIP-480 的具体内容是否如原文所述？
**建议验证来源**: Apache Kafka 2.4 Release Notes / KIP-480

### Q36: Sticky Partitioner 与 Round-Robin 对比
**章节位置**: 6.4.1
**原文陈述**: "老的轮询（round-robin）策略会把消息轮流分发到各分区，批更小、延迟更高"
**待确认点**: Kafka 早期的默认分区器是 round-robin 吗？实际上早期 Kafka 的默认分区器当 key 为 null 时使用 round-robin，但不是严格的轮流分发——它会在一个 batch 满或 linger.ms 到期后随机选择下一个分区。
**建议验证来源**: Kafka 源码历史 / KIP-480 设计文档

### Q37: 单分区吞吐量
**章节位置**: 6.4.1
**原文陈述**: "经验值大致是：单分区在普通硬件上能跑到约 10MB/s 或约 1 万条/秒的量级（以实际压测为准）"
**待确认点**: Kafa 单分区吞吐量是否通常能达到 10MB/s 或 1 万条/秒？这一数值是否与消息大小和硬件高度相关？是否需要更明确的硬件规格和消息大小参考？
**建议验证来源**: Apache Kafka 性能基准测试（Confluent 社区测试 / LinkedIn 工程博客）

### Q38: ISR 定义与动态管理
**章节位置**: 6.4.2
**原文陈述**: "ISR 是一个动态名单：只有那些能在 `replica.lag.time.max.ms` 这个时间窗口内跟上 Leader 进度的副本，才被算作"同步副本"，留在 ISR 里"
**待确认点**: `replica.lag.time.max.ms` 的默认值是多少？ISR 收缩/扩张的准确条件是否就是单一的超时条件？Kafka 早期还有 `replica.lag.max.messages` 参数后来被移除，原文是否应提及此历史？
**建议验证来源**: Apache Kafka 官方文档 / KIP

### Q39: LEO / HW 缩写
**章节位置**: 6.4.2
**原文陈述**: "LEO/HW 的推进规则"
**待确认点**: LEO 是 Log End Offset 的缩写，HW 是 High Watermark 的缩写。它们的推进规则在 Kafka 中是否有精确描述？LEO 是否在其他文档中以 LEO（Log End Offset）的形式出现？原文中是否应该首次使用时给出全称？
**建议验证来源**: Apache Kafka 官方文档 replication 章节 / The Log: What every software engineer should know about real-time data's unifying abstraction (Jay Kreps)

### Q40: acks=1 是 Kafka 3.0 之前的默认值
**章节位置**: 6.4.3
**原文陈述": "`acks=1`（Kafka 3.0 之前的默认）"
**待确认点**: Kafka 3.0 是否确实将默认值从 `acks=1` 改为 `acks=all`？KIP-679 是否在 3.0 中完成？
**建议验证来源**: Apache Kafka 3.0 Release Notes / KIP-679

### Q41: acks=all 自 Kafka 3.0 起成为默认（KIP-679）
**章节位置**: 6.4.3
**原文陈述**: "自 Kafka 3.0 起成为默认，对应 KIP-679"
**待确认点**: Kafka 3.0 中默认 `acks=all` 的精确语义——"all" 是否等于 ISR 内所有副本，还是所有副本（包括不在 ISR 内的）？KIP-679 的完整内容是什么？
**建议验证来源**: Apache Kafka 3.0 Release Notes / KIP-679

### Q42: min.insync.replicas 的默认值
**章节位置**: 6.4.3
**原文陈述**: "`acks=all` 加 `min.insync.replicas`（3.0 起的默认组合）"
**待确认点**: `min.insync.replicas` 的默认值是多少（`1`）？为什么说这是"默认组合"？如果 `min.insync.replicas=1` 且 `acks=all`，实际等待的是 1 个副本还是所有副本？
**建议验证来源**: Apache Kafka 官方文档 broker 配置

### Q43: Kafka 3.3 标记 KRaft 生产可用（KIP-833）
**章节位置**: 6.4.4
**原文陈述**: "KRaft 在 **Kafka 3.3**（2022 年发布）才被标记为"对新集群生产可用"——这是稳定线的起点"
**待确认点**: KIP-833 是否确实在 Kafka 3.3 中将 KRaft 标记为对新集群生产可用？Kafka 3.3 的实际发布日期是 2022 年吗？KRaft 在 3.3 中是否有功能限制（如不支持 ZooKeeper 到 KRaft 的迁移）？
**建议验证来源**: Apache Kafka 3.3 Release Notes / KIP-833

### Q44: Kafka 3.5 将 ZK 模式标记为 deprecated
**章节位置**: 6.4.4
**原文陈述**: "**Kafka 3.5** 把 ZooKeeper 模式正式标记为 deprecated"
**待确认点**: ZK 模式是否在 Kafka 3.5 中正式标记为 deprecated？Release Notes 是否有此声明？
**建议验证来源**: Apache Kafka 3.5 Release Notes

### Q45: KIP-866 迁移工具版本演进
**章节位置**: 6.4.4
**原文陈述**: "迁移工具（KIP-866）在 3.4 起以 Early Access 引入、3.5–3.6 为 preview、3.8 起进入生产可用"
**待确认点**: KIP-866 的各个版本演进步进是否与原文一致？3.4 是否以 Early Access 引入？3.5–3.6 作为 preview？3.8 进入生产可用？需要逐一验证 Kafka 各小版本的 Release Notes。
**建议验证来源**: Apache Kafka 3.4 / 3.5 / 3.6 / 3.8 Release Notes / KIP-866

### Q46: Kafka 3.9 是最后一个支持 ZK 的 bridge release
**章节位置**: 6.4.4
**原文陈述**: "**Kafka 3.9** 是最后一个支持 ZK 模式的 bridge release。直到后续大版本（Kafka 4.0）才彻底移除 ZK 支持"
**待确认点**: Kafka 3.9 是否确实是最后一个同时支持 ZK 和 KRaft 的 bridge release？Kafka 4.0 是否确实彻底移除了 ZooKeeper 支持？这些版本路线图在 KIP 中是否有明确说明？
**建议验证来源**: Apache Kafka 版本路线图 / KIP-833 / KIP-866

### Q47: Raft 在 KRaft 中的实现
**章节位置**: 6.4.4
**原文陈述**: "选一组 Controller 节点，它们之间跑 Raft 共识协议维护一份强一致的元数据日志"
**待确认点**: KRaft 使用的是 Raft 的"标准实现"还是在 Raft 上做了修改？Kafka 的 Raft 实现（Kafka Raft Metadata, KRM）和标准 Raft 协议有何区别？
**建议验证来源**: Apache Kafka KIP-500 / KIP-630 / KRaft 设计文档

### Q48: @metadata 内部 topic
**章节位置**: 6.4.4
**原文陈述**: "元数据本身也变成了 Kafka 的一个内部 topic（`@metadata`）"
**待确认点**: KRaft 使用的内部 topic 名称是 `@metadata` 还是 `__metadata`（或其他名称）？Kafka 内部 topic 的命名惯例是双下划线前缀（如 `__consumer_offsets`、`__transaction_state`）。
**建议验证来源**: Kafka KRaft 设计文档 / KIP-500

### Q49: 两层独立的 Leader 选举（Controller 层 + partition 层）
**章节位置**: 6.4.4
**原文陈述**: "Kafka 里有**两层独立的 Leader 选举**。一层是 Controller 节点之间的 Raft 选举——决定谁是"活跃 Controller"...另一层是 partition 的 Leader 选举..."
**待确认点**: KRaft 模式下，partition Leader 的选举是由活跃 Controller 从 ISR 中选择，还是由新 Controller 的 Raft 日志恢复来决定？partition Leader 选举是否仍依赖 ZooKeeper 式的临时节点（在 ZK 模式下）？
**建议验证来源**: Apache Kafka 文档 / KRaft 设计文档

### Q50: ZK 模式下 Controller 的脑裂风险
**章节位置**: 6.4.4
**原文陈述**: "更微妙的是 ZK 模式下有个潜在的脑裂风险：Controller 的 Leader 选举在 ZK 里做，partition 的 Leader 选举在 Controller 里做，两层状态可能不一致"
**待确认点**: ZooKeeper 模式下 Controller 的选举和 partition Leader 的选举之间是否存在原文所述的"两层状态不一致"风险？Kafka 通过 ZK 的 ephemeral node + fencing 机制来预防脑裂，原文的表述是否过于简化了这种风险？
**建议验证来源**: Apache Kafka 设计文档 / ZK 模式下 Controller 选举机制

---

## 四、跨系统对比与架构论述（6.5、6.6 节）

### Q51: CAP 立场对比表
**章节位置**: 6.5（表 6-1）
**原文陈述**: CAP 立场列为："AP（Redis）"、"CP（MySQL）"、"3.x 默认偏安全（acks=all），可由 acks / unclean.leader.election 在 AP↔CP 间滑动（Kafka）"
**待确认点**: 
- Redis Cluster 在严格 CAP 定义下是否在分区时始终保可用？少数派分区的槽是否不可写？
- MySQL MGR 在分区时少数派是否一定会停服？是否有 grace period 或其他机制？
- Kafka 通过 `acks` 和 `unclean.leader.election` 是否真的实现了 AP↔CP 间的滑动？
**建议验证来源**: 各系统 CAP 分析文档 / 分布式系统论文

### Q52: Redis Cluster 不适合超大规模（节点上千时 Gossip 流量成负担）
**章节位置**: 6.5
**原文陈述**: "Redis 的 Gossip 最终一致...不适合超大规模（节点数上千时 Gossip 流量本身就成了负担）"
**待确认点**: Redis Cluster 社区推荐的节点数上限是多少？是否有官方文档或基准测试说明 Gossip 流量在何时成为瓶颈？
**建议验证来源**: Redis Cluster 官方文档 / 大规模部署案例分析

### Q53: MySQL 组的大小受 Paxos 性能限制
**章节位置**: 6.5
**原文陈述**: "组的大小受 Paxos 性能限制（成员通常不超过个位数到十几个）"
**待确认点**: MGR 推荐的最大组成员数是多少？MySQL 官方是否有推荐上限？"个位数到十几个"是否准确（如 9 个是官方上限）？
**建议验证来源**: MySQL MGR 文档 / MySQL 官方博客

### Q54: Kafka KRaft 分区数可以到百万级
**章节位置**: 6.5
**原文陈述**: "Kafka 的 KRaft 让元数据同时具备强一致和高可用，分区数可以到百万级"
**待确认点**: KRaft 模式下 Kafka 是否确实支持百万级分区？社区/官方是否有百万分区压测数据？受限于哪些资源（内存、文件句柄）？
**建议验证来源**: Apache Kafka 性能测试 / Confluent 发布的分区数上限报告

### Q55: MySQL 多线程复制不完全根治回放延迟
**章节位置**: 6.3.1
**原文陈述**: "MySQL 的多线程复制（MTS，Multi-Threaded Slave）按主节点的组提交（group commit）粒度并行回放...缓解了但不根治回放延迟"
**待确认点**: MTS 在 MySQL 5.7 中引入的 LOGICAL_CLOCK 并行复制策略是否"不根治"回放延迟？具体瓶颈有哪些？
**建议验证来源**: MySQL 并行复制文档

### Q56: Redis 主从复制"异步"的严格定义
**章节位置**: 6.2.1 / 多处
**原文陈述**: "复制是**异步**的——主节点写完立即返回客户端，不等从节点确认"
**待确认点**: Redis 是否支持通过 `WAIT` 命令强制等待从节点确认？`WAIT` 命令的语义是什么？将其简单称为"异步"是否忽略了可选的同步能力？
**建议验证来源**: Redis 官方文档 `WAIT` 命令

### Q57: "单分区约 1 万条/秒"的基准场景描述
**章节位置**: 6.4.1
**原文陈述**: "单分区在普通硬件上能跑到约 10MB/s 或约 1 万条/秒的量级（以实际压测为准）"
**待确认点**: "普通硬件"的定义含糊不清（几核 CPU、何种磁盘、网络带宽）。不同消息大小下 1 万条/秒对应的 MB/s 差异很大。建议在原文中补充消息大小的假设前提。
**建议验证来源**: Kafka 官方性能测试

### Q58: Redis Sentinel 的"数据层仍然是单主异步复制"
**章节位置**: 6.2.2
**原文陈述**: "数据层仍然是单主异步复制"
**待确认点**: Redis 主从复制是否可以通过 `repl-disable-tcp-nodelay` 和 WAIT 命令实现某种程度的同步复制？在 Sentinel 模式下是否不存在同步复制选项？
**建议验证来源**: Redis 官方文档

### Q59: 对比表中"分片策略"中 Redis 描述为"客户端路由（MOVED/ASK）"
**章节位置**: 表 6-1
**原文陈述**: Redis 分片策略："16384 槽哈希分片，客户端路由（MOVED/ASK）"
**待确认点**: Redis Cluster 的路由是客户端负责缓存的槽映射 + 服务端 MOVED/ASK 重定向的混合模式，将路由策略标记为"客户端路由"是否准确？（也有"smart client"和"proxy"模式。）
**建议验证来源**: Redis Cluster 规范的客户端行为说明

### Q60: 关于 Kafka "原生分布式"的论断
**章节位置**: 6.4 引言
**原文陈述**: "Kafka 天生就是分布式。...一上来就是分布式，分片和副本是从设计起点就内置的"
**待确认点**: Kafka 在最初发布（0.7.x, 0.8.x）时是否一上来就是分布式的？最早的版本有多少功能缺陷？Kafka 是否从首个公开发布的版本就支持分片和副本？
**建议验证来源**: Kafka 原始论文 / LinkedIn 工程博客

---

## 五、版本与发布时间相关

### Q61: Kafka 3.3 发布于 2022 年
**章节位置**: 6.4.4
**原文陈述**: "Kafka 3.3（2022 年发布）"
**待确认点**: Apache Kafka 3.3.0 的准确发布日期是哪一天？是否在 2022 年内发布？
**建议验证来源**: Apache Kafka Release Notes

### Q62: MySQL 8.0.26 的发布时间
**章节位置**: 6.3.2
**原文陈述**: "8.0.26 起半同步相关变量由 master/slave 统一重命名为 source/replica"
**待确认点**: MySQL 8.0.26 的发布年份（2021 年 7 月？）。是否有必要精确到年月？
**建议验证来源**: MySQL Release Notes

### Q63: MySQL 5.7.17 发布时间
**章节位置**: 6.3.3
**原文陈述**: "MySQL 5.7.17 首次作为 GA 特性提供"
**待确认点**: MySQL 5.7.17 的准确发布日期？（大约 2016 年 12 月）
**建议验证来源**: MySQL Release Notes

### Q64: Redis 各版本演进时间线
**章节位置**: 全书引用
**原文陈述**: 多处提及 Redis 版本（如主从复制、Sentinel、Cluster 的版本引入时间）
**待确认点**: Redis 主从复制首次引入版本？Sentinel 首次引入版本？Redis Cluster 首次 GA 版本（3.0）？原文未直接给出这些版本号，但作为背景知识需要确认。
**建议验证来源**: Redis 发布历史 / CHANGELOG

---

## 六、术语与概念准确性

### Q65: "Gossip 传播判断"在 Sentinel 中的准确性
**章节位置**: 6.2.2
**原文陈述**: "每个 Sentinel 周期性地给主从节点发心跳...然后它通过 Gossip 把这个判断扩散给其他 Sentinel"
**待确认点**: Sentinel 之间并不是通过经典 Gossip 协议交换节点状态，而是通过 Redis 实例的 Pub/Sub 机制（`__sentinel__:hello` 频道）。原文将此称为"Gossip"是否准确？
**建议验证来源**: Redis Sentinel 官方文档

### Q66: 复制积压缓冲区（replication backlog）缓冲区大小默认值
**章节位置**: 6.2.1
**原文陈述**: "主节点新产生的写命令先存进复制积压缓冲区（replication backlog）"
**待确认点**: backlog 的默认大小（`repl-backlog-size`）的默认值是否为 1MB？backlog 是否始终存在还是仅在至少有一个从节点时才存在？
**建议验证来源**: redis.conf 默认配置文件

### Q67: Kafka ISR 动态名单的变化条件
**章节位置**: 6.4.2
**原文陈述**: "跟不上（lag 超时）的副本会被 Leader 踢出 ISR"
**待确认点**: ISR 收缩是否只以 `replica.lag.time.max.ms` 超时为条件？ISR 扩张（副本重新加入）的条件是什么？
**建议验证来源**: Apache Kafka 官方文档 / KIP

### Q68: Redis Cluster epoch 与 Raft term 的类比
**章节位置**: 6.2.3
**原文陈述**: "用集群纪元 epoch 防止过期投票"
**待确认点**: Redis Cluster 的 epoch（currentEpoch, configEpoch）与 Raft 的 term 的具体区别？epoch 在 Redis Cluster 中有多个（currentEpoch 用于选举，configEpoch 用于槽分配），是否应明确区分？
**建议验证来源**: Redis Cluster 规范

### Q69: MGR "单主模式"（single-primary）的 Leader 选举流程
**章节位置**: 6.3.3
**原文陈述**: "单主模式（single-primary）是生产主流：组里只有一个主节点（Primary）可写，其他从节点（Secondary）只读，主节点故障时组内自动选新主"
**待确认点**: 单主模式下新主选举的具体流程——是否使用 XCom 的 View Change？选举的依据是什么（成员 UUID、GTID 进度、还是权重）？
**建议验证来源**: MySQL MGR 文档

### Q70: "共识协议的核心思想是多数派确认"
**章节位置**: 6.1
**原文陈述**: "折中是多数派确认——只要大多数副本确认了就算提交，这也是共识协议的核心思想"
**待确认点**: 是否所有共识协议都以"多数派确认"为核心？Paxos 和 Raft 都要求严格多数派，但也存在不需要严格多数派的共识变体。此描述是否过于简化了共识协议的多样性？
**建议验证来源**: 分布式系统教材 / Lamport Paxos 论文 / Raft 论文

---

## 生成说明

- 本清单共提取 **70 个需验证的事实点**，覆盖 Redis / MySQL / Kafka 三个系统的集群架构相关内容。
- 优先级建议：版本号类（Q20, Q25, Q35, Q40, Q43-Q46, Q61-Q64）和默认值类（Q03, Q09, Q38, Q42）应优先核实，因为它们是事实性最强、歧义最小的类别。
- 算法/协议类（Q10, Q15, Q17, Q27, Q47, Q68）需查阅对应系统的设计文档或源码，确认原理解释的准确性。
- 性能数值类（Q16, Q37, Q57）需确认是否附有基准测试上下文（硬件规格、消息大小等），避免模糊推广。
