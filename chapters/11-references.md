# 附录　参考文献与延伸阅读（按章索引）

本书写作参考了大量官方文档、Kafka 改进提案（KIP）、经典论文与社区资料。此处按正文章节顺序组织，每章列出 2–5 份最相关的外部参考，附一句话说明它为何对该章重要。正文中的版本与参数以各章注明的版本为准；实际使用时，再核对所用版本的官方文档。著录格式参照 GB/T 7714，在线资源均附访问日期。

## 第 1 章 引言 — 为什么是这三个软件

[1] Kleppmann M. Designing Data-Intensive Applications[M]. Sebastopol: O'Reilly Media, 2017. —— 跨系统比较架构取舍的方法论范本。本书让三个软件面对同一批问题、对比各自设计的做法，直接参照了它，强烈推荐配套阅读。
[2] Kreps J. I Heart Logs[M]. Sebastopol: O'Reilly Media, 2014. —— Kafka 核心贡献者将日志当作统一抽象的极简论述，全书核心抽象观的缩影。
[3] Sanfilippo S (antirez). antirez 博客（Redis 设计随笔）[EB/OL]. [2026-08-14]. http://antirez.com. —— Redis 作者本人对数据全部放内存这一设计取舍的第一手阐述。

## 第 2 章 数据结构与协议 — 为各自的目标而设计

[4] Redis. Redis Serialization Protocol (RESP) Specification[EB/OL]. [2026-08-14]. https://redis.io/docs/latest/develop/reference/protocol-spec/. —— RESP 是 Redis 客户端与服务器之间的通信协议，AOF 的命令部分也复用 RESP 编码，可对照理解通信与日志表示之间的联系。
[5] Redis. Redis 7.0 源码（数据结构与对象编码）[EB/OL]. [2026-09-09]. https://github.com/redis/redis/tree/7.0.0/src. —— SDS、listpack、intset 与哈希表等结构承担不同用途；对象按类型、数据规模和配置选择适用编码，可对照第 2 章与第 5 章查看类型和编码的关系。
[6] Apache Kafka. KIP-98: Exactly Once Delivery and Transactional Messaging[EB/OL]. (2016)[2026-08-14]. https://cwiki.apache.org/confluence/display/KAFKA/KIP-98+-+Exactly+Once+Delivery+and+Transactional+Messaging. —— 幂等生产者与事务消息的设计提案，包含消息批次中的生产者身份、序号及事务标记，也说明实现这些保证所需的协议与状态管理。
[7] MySQL. Client/Server Protocol (MySQL Internals Manual)[EB/OL]. [2026-08-14]. https://dev.mysql.com/doc/dev/mysql-server/latest/PAGE_PROTOCOL.html. —— MySQL 客户端/服务器协议（握手、查询、结果集、预处理语句）的规范，理解 MySQL 网络层与 SQL 层交互的基础。

## 第 3 章 生命周期管理 — 优雅启动与关闭

[8] Redis. Redis Persistence (RDB / AOF / Multi-Part AOF)[EB/OL]. [2026-08-14]. https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/. —— 启动时状态重建（RDB/AOF 加载）与关闭时持久化（SAVE/NOSAVE 两条路径）的官方规范，对应本章"状态机重建与快照"模型。
[9] Mohan C, Haderle D, Lindsay B, et al. ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging[J]. ACM Transactions on Database Systems, 1992, 17(1): 94-162. —— 关于 WAL、细粒度锁与部分回滚的经典论文，可用于对照理解第 3 章的重做与回滚恢复机制。
[10] Apache Kafka. Controlled Shutdown（Kafka Documentation）[EB/OL]. [2026-08-14]. https://kafka.apache.org/documentation/. —— 优雅关闭时分区 Leader 主动迁移的协议说明，体现分布式系统停止时需额外协调责任的特殊挑战。

## 第 4 章 内存与磁盘 — 速度与持久化的平衡

[11] MySQL. InnoDB Buffer Pool[EB/OL]. [2026-09-09]. https://dev.mysql.com/doc/refman/8.0/en/innodb-buffer-pool.html. —— 缓冲池中的页缓存、改良 LRU、预读与后台刷盘的官方说明，对应第 4 章内存缓存与磁盘 I/O 的取舍。
[12] O'Neil P, Cheng E, Gawlick D, et al. The Log-Structured Merge-Tree (LSM-Tree)[J]. Acta Informatica, 1996, 33(4): 351-385. —— LSM-Tree 的理论论文，是 RocksDB、LevelDB、HBase 等 MySQL 之外另一类存储引擎的共同理论基础；本书三个软件均未采用 LSM，但在依赖顺序写这一点上与它相同。

## 第 5 章 分层架构设计 — 存储层 / 逻辑层 / 交互层

[13] Parnas D L. On the Criteria to Be Used in Decomposing Systems into Modules[J]. Communications of the ACM, 1972, 15(12): 1053-1058. —— 模块分解与信息隐藏的经典判据，本章"接口稳定性比接口优雅更重要"的说法的直接学术渊源。
[14] MySQL. MySQL 8.0.36 源码（handler 与 THD）[EB/OL]. [2026-09-09]. https://github.com/mysql/mysql-server/blob/mysql-8.0.36/sql/handler.h；https://github.com/mysql/mysql-server/blob/mysql-8.0.36/sql/sql_class.h. —— 存储引擎接口与连接上下文的定义，可对照第 5 章查看 handler 的虚函数接口及 THD 保存的跨层状态。
[15] Apache Kafka. Kafka Documentation: Design / Implementation[EB/OL]. [2026-08-14]. https://kafka.apache.org/documentation/. —— Design 与 Implementation 部分介绍网络请求处理、批量传输和存储组织，可对照第 5 章理解线程交接与对象调用的分工。

## 第 6 章 安全机制 — 权限、加密、审计

[16] Redis. Redis ACL[EB/OL]. [2026-08-14]. https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/. —— 从全局 `requirepass` 到基于命令类别与键模式细粒度 ACL 的演进设计，在性能优先的既有架构中补入安全机制的案例。
[17] MySQL. Security Features (Pluggable Authentication / RBAC / TDE)[EB/OL]. [2026-08-14]. https://dev.mysql.com/doc/refman/8.0/en/security.html. —— 五级权限体系、基于系统表的 RBAC 在 8.0 的落地，以及表空间与日志加密的企业级安全分层。
[18] Apache Kafka. Security (SASL / Delegation Tokens / Listener Separation)[EB/OL]. [2026-08-14]. https://kafka.apache.org/documentation/#security. —— SASL 认证、委托令牌与监听器配置的官方入口，可对照第 6 章区分身份认证、授权和不同网络连接的保护。

## 第 7 章 集群架构 — 从单点到分布式

[19] Redis. Redis Cluster Specification[EB/OL]. [2026-08-14]. https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/. —— 16384 槽位哈希分布、Gossip 元数据传播、异步复制与 PFAIL/FAIL 故障检测的一手规范，Redis 集群设计的官方权威来源。
[20] MySQL. MySQL Group Replication (MGR) 与 XCom[EB/OL]. [2026-08-14]. https://dev.mysql.com/doc/refman/8.0/en/group-replication.html. —— MGR 的组通信、事务认证与故障处理的官方入口，可对照第 7 章理解多数派协调、写入等待与故障后的成员状态。
[21] Apache Kafka. KIP-833: Mark KRaft as Production Ready[EB/OL]. (2022)[2026-08-14]. https://cwiki.apache.org/confluence/display/KAFKA/KIP-833%3A+Mark+KRaft+as+Production+Ready. —— 将 KRaft 标记为生产可用的版本推进提案，可与第 7 章一起理解 Kafka 从 ZooKeeper 向内置元数据仲裁组迁移的过程。
[22] Gilbert S, Lynch N. Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services[J]. ACM SIGACT News, 2002, 33(2): 51-59. —— CAP 定理的形式化证明，本书讨论网络分区下一致性与可用性取舍的理论根基。

## 第 8 章 磁盘存储格式 — 文件结构的设计哲学

[23] Apache Kafka. Message Format (RecordBatch V2)[EB/OL]. [2026-08-14]. https://kafka.apache.org/documentation/#messageformat. —— 批量元数据共享、偏移量与时间戳增量编码、幂等与事务字段的存储格式规范，Kafka 把日志当作数据本身这一设计落进字节布局的依据。
[24] MySQL. The Physical Structure of an InnoDB Index[EB/OL]. [2026-09-09]. https://dev.mysql.com/doc/refman/8.0/en/innodb-physical-structure.html. —— 索引页、默认 16KB 页大小和页空间利用的官方说明，可作为理解第 8 章索引页组织方式的入口。
[25] Redis. Redis 7.0 源码（RDB 文件编码）[EB/OL]. [2026-09-09]. https://github.com/redis/redis/blob/7.0.0/src/rdb.c. —— RDB 对象与长度编码、CRC64 校验及保存/加载流程的源码，可对照第 8 章查看快照文件的具体字节布局。
[26] Apache Kafka. KIP-405: Kafka Tiered Storage[EB/OL]. (2018)[2026-08-14]. https://cwiki.apache.org/confluence/display/KAFKA/KIP-405%3A+Kafka+Tiered+Storage. —— Kafka 将符合条件的已关闭日志段复制到远程存储、分别管理本地与远程保留策略的架构设计，是第 8 章 Tiered Storage 一节的关键参考。

## 第 9 章 数据同步机制 — 集群一致性的实现

[27] Apache Kafka. KIP-101: Alter Replication Protocol to use Leader Epoch rather than High Watermark for Truncation[EB/OL]. (2016)[2026-08-14]. https://cwiki.apache.org/confluence/display/KAFKA/KIP-101+-+Alter+Replication+Protocol+to+use+Leader+Epoch+rather+than+High+Watermark+for+Truncation. —— Leader Epoch 机制解决选主后旧 Leader 偏移量截断歧义，Kafka 副本对齐最关键的修复设计。
[28] Apache Kafka. KIP-320: Allow fetchers to detect and handle log truncation[EB/OL]. (2018)[2026-08-14]. https://cwiki.apache.org/confluence/display/KAFKA/KIP-320%3A+Allow+fetchers+to+detect+and+handle+log+truncation. —— Leader Epoch 在截断协议中的细化应用，避免副本恢复时按 HW 误截断造成数据丢失与不一致。
[29] Redis. Replication 与 PSYNC2[EB/OL]. [2026-08-14]. https://redis.io/docs/latest/operate/oss_and_stack/management/replication/. —— 复制历史标识、偏移量与积压数据如何支持部分重同步的官方说明；故障转移后能否增量恢复，取决于历史是否匹配以及所需日志是否仍被保留。
[30] MySQL. GTID-Based Replication[EB/OL]. [2026-08-14]. https://dev.mysql.com/doc/refman/8.0/en/replication-gtids.html. —— GTID（`source_id:transaction_id`）按事务标识组织复制进度，使自动定位独立于 binlog 文件名和字节偏移，可对照第 9 章理解已执行事务集合与缺失事务。
[31] Lamport L. Time, Clocks, and the Ordering of Events in a Distributed System[J]. Communications of the ACM, 1978, 21(7): 558-565. —— 逻辑时钟与 happens-before 关系的奠基论文，本章"顺序保证是分布式复制的根基"这一论断的理论源头。

## 第 10 章 总结：架构设计的共性规律与取舍

[32] 同 [1]。—— 贯穿全书的对照之作，更广视角的数据系统取舍论述，本章五条共性规律的上位参照。
[33] 同 [22]。—— CAP 定理的形式化证明，本章"一致 vs 可用"这一取舍维度的理论基础。
[34] Gray J, Reuter A. Transaction Processing: Concepts and Techniques[M]. San Francisco: Morgan Kaufmann, 1993. —— 事务、WAL、两阶段提交、恢复语义的系统化集大成著作，以性能换可靠性这一原则的经典源头。

---

## 综合推荐

[35] 同 [1]。—— 跨系统架构取舍的入门读物，本书反复与之呼应的核心参照。
[36] 同 [2]。—— 将日志当作统一抽象的精炼论述，适合快速建立数据系统统一视角。
[37] Bailis P, Hellerstein J M, Stonebraker M. Readings in Database Systems: 5th Edition[M/OL]. (2015)[2026-08-14]. http://www.redbook.io/. —— 数据库经典论文（社群通称 Red Book）按主题组织的导读索引，适合有论文阅读需求的读者。
[38] Botros S, Tinley J. High Performance MySQL[M]. 4th ed. Sebastopol: O'Reilly Media, 2021. —— MySQL 性能与架构优化的实战参考，适合深化 MySQL 理解。
[39] Kreps J, Narkhede N, Rao J. Kafka: a Distributed Messaging System for Log Processing[C]//NetDB Workshop. Athens, 2011. —— Kafka 原始设计论文，首发于 NetDB 2011，可用于理解日志追加、分区和批量传输等早期设计选择，并与后续复制及元数据架构的演进对照。

---

> **一点阅读建议**：官方文档适合查证参数与版本细节，KIP 能还原 Kafka 每一步设计的背景，论文适合理解"为什么这么设计"的深层逻辑，而像 DDIA 这样的综合书适合建立跨系统的整体视野。本书替代不了这些资料，能做的是先帮你建立一套共同的比较基准，再去读它们就顺了。
