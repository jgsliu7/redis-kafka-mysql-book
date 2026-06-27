# 附录　参考文献与延伸阅读（按章索引）

本书正文引用大量官方文档、Kafka 改进提案（KIP）、经典论文与社区资料。此处按正文章节顺序组织，每章列出 2-4 份最相关的外部参考，附一句话说明它为何对该章重要。版本与参数以官方最新文档为准；书中架构思想长期稳定。

## 第一章　为什么要比——比较的框架

- **Kleppmann, M. *Designing Data-Intensive Applications*（DDIA）. O'Reilly, 2017.** —— 跨系统比较架构取舍的方法论范本，本书"同题作答"框架的直接参照，强烈推荐配套阅读。
- **Kreps, J. *I Heart Logs*. O'Reilly, 2014.** —— Kafka 核心贡献者对"日志即统一抽象"的极简论述，全书核心抽象观的缩影。
- **Sanfilippo, S.（antirez）Redis 设计与取舍（博客与文档）. redis.io.** —— Redis 作者本人对"内存即数据"设计哲学的第一手阐述。

## 第二章　数据结构与协议

- **Redis RESP 协议规范. redis.io/topics/protocol.** —— RESP（REdis Serialization Protocol）是 Redis 客户端与服务器之间的通信协议，同时 RDB 文件也复用同类编码思路，体现了"协议即存储格式"的统一设计哲学。
- **Redis SDS（Simple Dynamic String）与动态编码源码：src/sds.c, src/listpack.c, GitHub.com/redis/redis.** —— SDS、ziplist、listpack 等底层数据结构根据数据规模自动选择编码方式，展现 Redis"按数据特征自适应"的精髓。
- **KIP-98: Exactly Once Delivery and Transactional Messaging. Apache Kafka.** —— RecordBatch V2 格式定义批量消息的元数据共享、增量偏移量/时间戳编码，恰好一次语义内嵌于存储格式中。
- **MySQL Internals Manual: Client/Server Protocol. dev.mysql.com.** —— MySQL 二进制协议（握手、查询、结果集、预处理语句）的完整规范，理解 MySQL 网络层与 SQL 层交互的基础。

## 第三章　启动与关闭——生命周期管理

- **Redis 持久化文档（RDB / AOF / Multi-Part AOF）. redis.io/docs/management/persistence.** —— 启动时状态重建（RDB/AOF 加载）与关闭时持久化（SAVE/NOSAVE 两条路径）的官方规范，对应本章"状态机重建与快照"模型。
- **Mohan, C. et al. *ARIES: A Transaction Recovery Method*（1992）.** —— MySQL InnoDB 崩溃恢复（分析→重做→回滚三阶段）的理论基石，解释为何 MySQL 启动耗时远超 Redis 和 Kafka。
- **Kafka 官方文档：Controlled Shutdown 协议. kafka.apache.org.** —— 优雅关闭时分区 Leader 主动迁移的协议说明，体现分布式系统停止时需额外协调责任的特殊挑战。

## 第四章　内存与磁盘——速度与持久化的舞蹈

- **MySQL InnoDB 文档：Buffer Pool 与 WAL. dev.mysql.com.** —— 三链缓冲池（Free/LRU/Flush List）、Double Write Buffer、Change Buffer 与 WAL 的官方说明，理解"磁盘为真相、缓存为加速"范式的钥匙。
- **O'Neil, P. et al. *The Log-Structured Merge-Tree*（1996）.** —— LSM-Tree 的理论论文，Kafka 段文件与 compaction 机制的设计源头，也是 MySQL 之外另一类存储引擎的共同基础。
- **KIP-405: Tiered Storage in Kafka. Apache Kafka.** —— Kafka 将本地日志数据按层次卸载到远程存储（如 S3）的架构设计，本章内存-磁盘-远程三级存储体系的关键参考。

## 第五章　分层架构——接口即契约

- **Parnas, D. L. *On the Criteria to Be Used in Decomposing Systems into Modules*（1972）.** —— 模块分解与信息隐藏的经典判据，本章"接口稳定性比接口优雅更重要"的说法的直接学术渊源。
- **MySQL Internals Manual / Handler API 文档. dev.mysql.com.** —— InnoDB 插件式引擎接口（Handler API 的 vtable 多态设计）与 THD 跨层上下文对象的官方说明，见证分层灵活性的代价。
- **Kafka 网络层文档（Acceptor / Processor / RequestChannel / Handler 模型）. kafka.apache.org.** —— Reactor 多线程网络模型与有界队列背压机制的架构描述，理解 Kafka 分层中最独特的一层的入口。

## 第六章　安全——认证、授权、加密、审计

- **Redis ACL 文档（6.0+）. redis.io.** —— 从全局 `requirepass` 到基于命令类别与键模式细粒度 ACL 的演进设计，性能优先的安全 retrofit 案例。
- **MySQL 安全文档（可插拔认证 / RBAC / TDE）. dev.mysql.com.** —— 五级权限体系、基于系统表的 RBAC 在 8.0 的落地，以及表空间与日志加密的企业级安全分层。
- **Kafka 安全文档（SASL / 委派令牌 / 监听器分离）. kafka.apache.org.** —— SASL 认证框架 + 委派令牌解决多跳身份传播、分层信任监听器适配不同网络域的分布式安全模式。

## 第七章　集群——从单机到分布式

- **Redis Cluster 规范（antirez）. redis.io/topics/cluster-spec.** —— 16384 槽位哈希分布、Gossip 元数据传播、异步复制与 SDOWN/ODOWN 故障检测的一手规范，Redis 集群设计的官方权威来源。
- **MySQL 组复制（MGR）与 XCom 文档. dev.mysql.com.** —— Paxos 变体实现多数派确认、少数派自动退出的 CP 架构设计，正文中与 Redis 和 Kafka 集群对比的两端锚点之一。
- **KIP-833: Mark KRaft as Production Ready. Apache Kafka.** —— Kafka 自研 Raft 元数据层替代 ZooKeeper 的架构设计，分区上限从万级到百万级的核心支撑。
- **Gilbert, S. & Lynch, N. *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services*（2002）.** —— CAP 定理的形式化证明，本书所有 AP/CP 分类讨论的理论根基。

## 第八章　文件格式——磁盘上的架构抉择

- **KIP-98: Exactly Once Delivery and Transactional Messaging. Apache Kafka.** —— RecordBatch V2 格式规范：批量元数据共享、偏移量和时间戳增量编码、ProducerId/ProducerEpoch 内嵌支持幂等与事务，Kafka 存储格式的里程碑。
- **MySQL InnoDB 页结构文档. dev.mysql.com.** —— 16KB 固定页内七段布局（FIL Header / Page Directory / Infimum+Supremum / User Records 等）与动态行格式溢出页处理，页范式文件设计的权威参考。
- **Redis RDB 格式文档与 RESP 协议规范. redis.io.** —— 变长整数编码（SELECTOR 位标记 6/14/32 位长度）、CRC64 校验与 RESP 协议即文件格式的设计，快照范式文件结构的典型范例。

## 第九章　数据同步——副本一致性的工程实现

- **KIP-101: Replication Protocol Revamp / KIP-320: Leader Epochs. Apache Kafka.** —— Leader Epoch 机制解决选主后旧 Leader 偏移量截断歧义，Kafka 副本对齐最关键的修复设计。
- **Redis 复制与 PSYNC2 文档. redis.io.** —— replid/replid2 双标识符、复制偏移量与环形积压缓冲区实现部分重同步的官方描述，PSYNC2 使故障转移后仍可增量同步。
- **MySQL GTID 与 binlog 复制文档. dev.mysql.com.** —— GTID（`source_id:transaction_id`）使副本定位独立于文件名和字节偏移，binlog ROW 格式确定性复制的基石。
- **Lamport, L. *Time, Clocks, and the Ordering of Events in a Distributed System*（1978）.** —— 逻辑时钟与 happen-before 关系的奠基论文，本章"顺序保证是分布式复制的根基"这一论断的理论源头。

## 第十章　融会贯通——模式提炼与取舍之道

- **Kleppmann, M. *Designing Data-Intensive Applications*（DDIA）. O'Reilly, 2017.** —— 贯穿全书的姊妹篇，更广视角的数据系统取舍论述，本章五大架构法则的上位参照。
- **Gilbert, S. & Lynch, N. *Brewer's Conjecture...*（2002）.** —— CAP 定理的形式化证明，本章"一致 vs 可用"这一永恒取舍维度的理论基础。
- **Gray, J. & Reuter, A. *Transaction Processing: Concepts and Techniques*（1993）.** —— 事务、WAL、两阶段提交、恢复语义的系统化集大成著作，"性能买可靠性"原则的经典源头。

---

## 综合推荐

- **Kleppmann, M. *Designing Data-Intensive Applications*（DDIA）. O'Reilly, 2017.** —— 跨系统架构取舍的最佳入门，本书反复呼应的核心参照。
- **Kreps, J. *I Heart Logs*. O'Reilly, 2014.** —— "日志即抽象"的精炼论述，适合快速建立数据系统统一视角。
- **Bailis, P. et al. *Readings in Database Systems*（Red Book）.** —— 数据库经典论文按主题组织的导读索引，适合有论文阅读需求的读者。
- **Schwartz, B. / Zaitsev, P. / Tkachenko, V. *High Performance MySQL*（4th ed.）. O'Reilly, 2022.** —— MySQL 性能与架构优化的实战参考，适合深化 MySQL 理解。
- **Narkhede, N. / Kreps, J. / Rao, J. *Kafka: a Distributed Messaging System for Log Processing*（2011）.** —— Kafka 原始设计论文，首发于 NetDB 2011，十余年后核心架构依然忠实于此文。

---

> 一点阅读建议：官方文档适合查证参数与版本细节，KIP 能还原 Kafka 每一步设计的幕后背景，论文适合理解"为什么这么设计"的深层逻辑，而像 DDIA 这样的综合书适合建立跨系统的坐标系。本书的目标不是替代上述任何资料——而是为读懂它们，提供一副统一的眼镜。
