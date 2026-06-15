# 附录　参考文献与延伸阅读

本书在正文中多处引用了官方文档、改进提案（KIP）、经典论文与社区资料。为便于读者按图索骥，这里按主题集中列出。版本与参数细节以官方最新文档为准——本书的分析基于 Redis 7.x、MySQL 8.0.x、Kafka 3.x，软件会持续演进，但书中的架构思想长期稳定。

## 一、官方文档

### Redis

- Redis 官方文档：<https://redis.io/docs/>
- Redis 持久化（RDB / AOF / Multi-Part AOF）：<https://redis.io/docs/management/persistence/>
- Redis 复制（Replication）与 PSYNC：<https://redis.io/docs/management/replication/>
- Redis Cluster（槽位、Gossip、MOVED/ASK）：<https://redis.io/docs/reference/cluster-spec/>
- Redis ACL 与安全：<https://redis.io/docs/management/security/acl/>

### MySQL

- MySQL 8.0 参考手册：<https://dev.mysql.com/doc/refman/8.0/en/>
- InnoDB 存储引擎：<https://dev.mysql.com/doc/refman/8.0/en/innodb-introduction.html>
- 二进制日志（binlog）与复制：<https://dev.mysql.com/doc/refman/8.0/en/replication.html>
- 组复制（Group Replication）：<https://dev.mysql.com/doc/refman/8.0/en/group-replication.html>
- 半同步复制：<https://dev.mysql.com/doc/refman/8.0/en/replication-semisync.html>

### Kafka

- Kafka 官方文档：<https://kafka.apache.org/documentation/>
- Kafka 设计文档（含 LinkedIn 早期设计原文）：<https://kafka.apache.org/documentation/#design>
- KRaft 模式：<https://kafka.apache.org/documentation/#kraft>
- Kafka 安全（SASL / TLS / ACL）：<https://kafka.apache.org/documentation/#security>

## 二、Kafka 改进提案（KIP）

正文中引用到的关键 KIP，按编号排列：

- **KIP-32**：为消息增加时间戳（Kafka 0.10，消息格式 V1）。
- **KIP-480**：粘性分区器（Sticky Partitioner），生产者默认攒批策略。
- **KIP-679**：生产者默认 `acks=all`（Kafka 3.0 起）。
- **KIP-833**：KRaft 模式的生产可用路线与版本标记（3.3 起对新集群生产可用）。
- **KIP-866**：既有 ZooKeeper 集群迁移到 KRaft 的工具（3.4 起逐步成熟）。

KIP 全文索引见：<https://cwiki.apache.org/confluence/display/KAFKA/Kafka+Improvement+Proposals>

## 三、经典论文与算法

这些是本书多家机制背后的理论源头，正文在用到处均有标注。

- **Lamport, L. *The Part-Time Parliament*（Paxos）**. 1998. —— MySQL MGR 的 XCom、Kafka KRaft 之外的另一类共识算法家族的起点。
- **Ongaro, D. & Ousterhout, J. *In Search of an Understandable Consensus Algorithm (Raft)***. 2014. —— Kafka KRaft、Redis Sentinel 选举（Raft-like）的思想来源。
- **Mohan, C. et al. *ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging***. 1992. —— MySQL InnoDB 崩溃恢复（分析、重做、回滚三阶段）的理论基础。
- **Gray, J. & Reuter, A. *Transaction Processing: Concepts and Techniques***. 1993. —— 事务、WAL、两阶段提交的系统化论述。
- **Morris, R. *Counting Large Numbers of Events in Small Registers***. 1978. —— Redis LFU 用的对数近似计数器原型。
- **Schneider, F. B. *Implementing Fault-Tolerant Services Using the State Machine Approach***. 1990. —— 第 8 章"状态机复制"模型的经典表述。
- **O'Neil, P. et al. *The Log-Structured Merge-Tree***. 1996. —— 顺序日志与分层压实思想的源头（Kafka compaction、各类 LSM 引擎的共同基础）。

## 四、推荐延伸阅读

### 综合与数据系统

- **Kleppmann, M. *Designing Data-Intensive Applications***（DDIA）. O'Reilly, 2017. —— 本书反复呼应的姊妹篇，从更广的视角讨论数据系统的取舍，强烈推荐配套阅读。
- **Bailis, P. et al. *Readings in Database Systems***（Red Book）. —— 数据库经典论文选读，按主题组织。

### Redis

- **Sanfilippo, S.（antirez）*Redis 设计与实现***（博客与文档）. —— 作者本人对 Redis 设计取舍的第一手阐述。
- **黄健宏《Redis 设计与实现》**. —— 中文社区对 Redis 内部实现的清晰拆解。

### MySQL

- **Jeremiah P. et al. *High Performance MySQL***. O'Reilly. —— MySQL 性能与架构优化的实战参考。
- **InnoDB 引擎源码与官方文档**. —— 页结构、B+ 树、redo/undo、MVCC 的一手资料。

### Kafka

- **Kreps, J. *I Heart Logs***. O'Reilly, 2014. —— Kafka 核心贡献者对"日志即抽象"的精炼论述。
- **Narkhede, N. / Kreps, J. / Rao, J. *Kafka: a Distributed Messaging System for Log Processing***. 2011. —— Kafka 最初的设计论文。

---

> 一点阅读建议：官方文档适合查证参数与版本细节，论文适合理解"为什么这么设计"，而像 DDIA 这样的综合书适合建立跨系统的坐标系。本书的目标是后者——不是替代上述任何一份资料，而是为读懂它们提供一副统一的眼镜。
