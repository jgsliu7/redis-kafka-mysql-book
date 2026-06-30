# 附录　参考文献与延伸阅读（按章索引）

本书正文引用大量官方文档、Kafka 改进提案（KIP）、经典论文与社区资料。此处按正文章节顺序组织，每章列出 2-4 份最相关的外部参考，附一句话说明它为何对该章重要。版本与参数以官方最新文档为准；书中架构思想长期稳定。著录格式参照 GB/T 7714，在线资源均附访问日期。

## 第 1 章 引言 — 为什么是这三款软件，架构视角的意义

[1] Kleppmann M. Designing Data-Intensive Applications[M]. Sebastopol: O'Reilly Media, 2017. —— 跨系统比较架构取舍的方法论范本，本书"同题作答"框架的直接参照，强烈推荐配套阅读。
[2] Kreps J. I Heart Logs[M]. Sebastopol: O'Reilly Media, 2014. —— Kafka 核心贡献者对"日志即统一抽象"的极简论述，全书核心抽象观的缩影。
[3] Sanfilippo S (antirez). Redis Design and Trade-offs[EB/OL]. (2020)[2025-12-01]. https://redis.io/docs/latest/. —— Redis 作者本人对"内存即数据"设计哲学的第一手阐述。

## 第 2 章 数据结构与协议 —— 为各自的目标而设计

[4] Redis. Redis Serialization Protocol (RESP) Specification[EB/OL]. [2025-12-01]. https://redis.io/docs/latest/develop/reference/protocol-spec/. —— RESP 是 Redis 客户端与服务器之间的通信协议，同时 RDB 文件也复用同类编码思路，体现"协议即存储格式"的统一设计哲学。
[5] Redis. Redis 源码（SDS、listpack 等动态编码）[EB/OL]. [2025-12-01]. https://github.com/redis/redis. —— SDS、ziplist、listpack 等底层数据结构根据数据规模自动选择编码方式，展现 Redis"按数据特征自适应"的精髓。
[6] Apache Kafka. KIP-98: Exactly Once Delivery and Transactional Messaging[EB/OL]. (2017)[2025-12-01]. https://cwiki.apache.org/confluence/display/KAFKA/KIP-98. —— RecordBatch V2 格式定义批量消息的元数据共享、增量偏移量/时间戳编码，恰好一次语义内嵌于存储格式中。
[7] MySQL. Client/Server Protocol (MySQL Internals Manual)[EB/OL]. [2025-12-01]. https://dev.mysql.com/doc/dev/mysql-server/latest/PAGE_PROTOCOL.html. —— MySQL 二进制协议（握手、查询、结果集、预处理语句）的完整规范，理解 MySQL 网络层与 SQL 层交互的基础。

## 第 3 章 生命周期管理 — 优雅启动与关闭的艺术

[8] Redis. Redis Persistence (RDB / AOF / Multi-Part AOF)[EB/OL]. [2025-12-01]. https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/. —— 启动时状态重建（RDB/AOF 加载）与关闭时持久化（SAVE/NOSAVE 两条路径）的官方规范，对应本章"状态机重建与快照"模型。
[9] Mohan C, Haderle D, Lindsay B, et al. ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Pre-Image Logging[R]. IBM Research Report RJ 1821, 1992. —— MySQL InnoDB 崩溃恢复（分析→重做→回滚三阶段）的理论基石，解释为何 MySQL 启动耗时远超 Redis 和 Kafka。
[10] Apache Kafka. Controlled Shutdown[EB/OL]. [2025-12-01]. https://kafka.apache.org/documentation/#ctrlshutdown. —— 优雅关闭时分区 Leader 主动迁移的协议说明，体现分布式系统停止时需额外协调责任的特殊挑战。

## 第 4 章 内存与磁盘的舞蹈 — 速度与持久化的平衡

[11] MySQL. InnoDB Buffer Pool 与 Write-Ahead Logging[EB/OL]. [2025-12-01]. https://dev.mysql.com/doc/refman/8.0/en/innodb-buffer-pool.html. —— 三链缓冲池（Free/LRU/Flush List）、Double Write Buffer、Change Buffer 与 WAL 的官方说明，理解"磁盘为真相、缓存为加速"范式的钥匙。
[12] O'Neil P, Cheng E, Gawlick D, et al. The Log-Structured Merge-Tree (LSM-Tree)[J]. Acta Informatica, 1996, 33(4): 351-385. —— LSM-Tree 的理论论文，是 RocksDB、LevelDB、HBase 等 MySQL 之外另一类存储引擎的共同理论基础；本书三款软件均未采用 LSM，但与之在"顺序写"的精神上呼应。
[13] Apache Kafka. KIP-405: Tiered Storage in Kafka[EB/OL]. (2021)[2025-12-01]. https://cwiki.apache.org/confluence/display/KAFKA/KIP-405. —— Kafka 将本地日志数据按层次卸载到远程存储（如 S3）的架构设计，本章内存-磁盘-远程三级存储体系的关键参考。

## 第 5 章 分层架构设计 — 存储层 / 逻辑层 / 交互层

[14] Parnas D L. On the Criteria to Be Used in Decomposing Systems into Modules[J]. Communications of the ACM, 1972, 15(12): 1053-1058. —— 模块分解与信息隐藏的经典判据，本章"接口稳定性比接口优雅更重要"的说法的直接学术渊源。
[15] MySQL. The Handler API / Pluggable Storage Engines (Internals Manual)[EB/OL]. [2025-12-01]. https://dev.mysql.com/doc/refman/8.0/en/storage-engines.html. —— InnoDB 插件式引擎接口（Handler API 的 vtable 多态设计）与 THD 跨层上下文对象的官方说明，见证分层灵活性的代价。
[16] Apache Kafka. Network Threading Design[EB/OL]. [2025-12-01]. https://kafka.apache.org/documentation/. —— Reactor 多线程网络模型与有界队列背压机制的架构描述，理解 Kafka 分层中最独特的一层的入口。

## 第 6 章 安全机制 — 权限、加密、审计

[17] Redis. Redis ACL[EB/OL]. [2025-12-01]. https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/. —— 从全局 `requirepass` 到基于命令类别与键模式细粒度 ACL 的演进设计，性能优先的安全 retrofit 案例。
[18] MySQL. Security Features (Pluggable Authentication / RBAC / TDE)[EB/OL]. [2025-12-01]. https://dev.mysql.com/doc/refman/8.0/en/security.html. —— 五级权限体系、基于系统表的 RBAC 在 8.0 的落地，以及表空间与日志加密的企业级安全分层。
[19] Apache Kafka. Security (SASL / Delegation Tokens / Listener Separation)[EB/OL]. [2025-12-01]. https://kafka.apache.org/documentation/#security. —— SASL 认证框架 + 委派令牌解决多跳身份传播、分层信任监听器适配不同网络域的分布式安全模式。

## 第 7 章 集群架构 — 从单点到分布式

[20] Redis. Redis Cluster Specification[EB/OL]. [2025-12-01]. https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/. —— 16384 槽位哈希分布、Gossip 元数据传播、异步复制与 SDOWN/ODOWN 故障检测的一手规范，Redis 集群设计的官方权威来源。
[21] MySQL. MySQL Group Replication (MGR) 与 XCom[EB/OL]. [2025-12-01]. https://dev.mysql.com/doc/refman/8.0/en/group-replication.html. —— Paxos 变体实现多数派确认、少数派自动退出的 CP 架构设计，正文中与 Redis 和 Kafka 集群对比的两端锚点之一。
[22] Apache Kafka. KIP-833: Mark KRaft as Production Ready[EB/OL]. (2022)[2025-12-01]. https://cwiki.apache.org/confluence/display/KAFKA/KIP-833. —— Kafka 自研 Raft 元数据层替代 ZooKeeper 的架构设计，分区上限从万级扩到百万级的核心支撑。
[23] Gilbert S, Lynch N. Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services[J]. ACM SIGACT News, 2002, 33(2): 51-59. —— CAP 定理的形式化证明，本书所有 AP/CP 分类讨论的理论根基。

## 第 8 章 磁盘存储格式 — 文件结构的设计哲学

[24] Apache Kafka. Message Format (RecordBatch V2)[EB/OL]. [2025-12-01]. https://kafka.apache.org/documentation/#messageformat. —— 批量元数据共享、偏移量与时间戳增量编码、幂等与事务字段的存储格式规范，Kafka 把"日志即数据本体"落进字节布局的依据。
[25] MySQL. InnoDB Page Structure[EB/OL]. [2025-12-01]. https://dev.mysql.com/doc/refman/8.0/en/innodb-physical-structure.html. —— 16KB 固定页内七段布局（FIL Header / Page Directory / Infimum+Supremum / User Records 等）与动态行格式溢出页处理，页范式文件设计的权威参考。
[26] Redis. RDB File Format 与 RESP Specification[EB/OL]. [2025-12-01]. https://redis.io/docs/latest/operate/oss_and_stack/persistence/. —— 变长整数编码（length 字段高 2 位作档位标记）、CRC64 校验与 RESP 协议即文件格式的设计，快照范式文件结构的典型范例。

## 第 9 章 数据同步机制 — 集群一致性的实现

[27] Apache Kafka. KIP-101: Replication Protocol Revamp[EB/OL]. (2015)[2025-12-01]. https://cwiki.apache.org/confluence/display/KAFKA/KIP-101. —— Leader Epoch 机制解决选主后旧 Leader 偏移量截断歧义，Kafka 副本对齐最关键的修复设计。
[28] Apache Kafka. KIP-320: Leader Epochs[EB/OL]. (2018)[2025-12-01]. https://cwiki.apache.org/confluence/display/KAFKA/KIP-320. —— Leader Epoch 在截断协议中的细化应用，避免副本恢复时按 HW 误截断造成数据丢失与不一致。
[29] Redis. Replication 与 PSYNC2[EB/OL]. [2025-12-01]. https://redis.io/docs/latest/operate/oss_and_stack/management/replication/. —— replid/replid2 双标识符、复制偏移量与环形积压缓冲区实现部分重同步的官方描述，PSYNC2 使故障转移后仍可增量同步。
[30] MySQL. GTID-Based Replication[EB/OL]. [2025-12-01]. https://dev.mysql.com/doc/refman/8.0/en/replication-gtids.html. —— GTID（`source_id:transaction_id`）使副本定位独立于文件名和字节偏移，binlog ROW 格式确定性复制的基石。
[31] Lamport L. Time, Clocks, and the Ordering of Events in a Distributed System[J]. Communications of the ACM, 1978, 21(7): 558-565. —— 逻辑时钟与 happens-before 关系的奠基论文，本章"顺序保证是分布式复制的根基"这一论断的理论源头。

## 第 10 章 万法归一 —— 架构设计的共性规律与取舍之道

[32] Kleppmann M. Designing Data-Intensive Applications[M]. Sebastopol: O'Reilly Media, 2017. —— 贯穿全书的姊妹篇，更广视角的数据系统取舍论述，本章五条共性规律的上位参照。
[33] Gilbert S, Lynch N. Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services[J]. ACM SIGACT News, 2002, 33(2): 51-59. —— CAP 定理的形式化证明，本章"一致 vs 可用"这一永恒取舍维度的理论基础。
[34] Gray J, Reuter A. Transaction Processing: Concepts and Techniques[M]. San Francisco: Morgan Kaufmann, 1993. —— 事务、WAL、两阶段提交、恢复语义的系统化集大成著作，"性能买可靠性"原则的经典源头。

---

## 综合推荐

[35] Kleppmann M. Designing Data-Intensive Applications[M]. Sebastopol: O'Reilly Media, 2017. —— 跨系统架构取舍的最佳入门，本书反复呼应的核心参照。
[36] Kreps J. I Heart Logs[M]. Sebastopol: O'Reilly Media, 2014. —— "日志即抽象"的精炼论述，适合快速建立数据系统统一视角。
[37] Bailis P, Stonebraker M, et al. Readings in Database Systems (Red Book)[M]. Cambridge: MIT Press, 2019. —— 数据库经典论文按主题组织的导读索引，适合有论文阅读需求的读者。
[38] Schwartz B, Zaitsev P, Tkachenko V. High Performance MySQL[M]. 4th ed. Sebastopol: O'Reilly Media, 2022. —— MySQL 性能与架构优化的实战参考，适合深化 MySQL 理解。
[39] Narkhede N, Kreps J, Rao J. Kafka: a Distributed Messaging System for Log Processing[C]//NetDB Workshop. Stockholm, 2011. —— Kafka 原始设计论文，首发于 NetDB 2011，十余年后核心架构依然忠实于此文。

---

> 一点阅读建议：官方文档适合查证参数与版本细节，KIP 能还原 Kafka 每一步设计的背景，论文适合理解"为什么这么设计"的深层逻辑，而像 DDIA 这样的综合书适合建立跨系统的坐标系。本书替代不了这些资料，能做的是先帮你搭一个共同的坐标系，再去读它们就顺了。
