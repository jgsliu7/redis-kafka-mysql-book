# 参考文献与版本资料

本版以 Redis 7.x、MySQL 8.0.x、Apache Kafka 3.9.0 为机制讨论基线。涉及小版本新增功能或精确实现的地方，正文另行限定；MySQL 5.7 Query Cache 等资料仅用于历史对照。

以下按章节列出正文实际引用的资料。相同资料可在不同章节出现，所支撑的是相邻机制或具体限定，不表示整章全部论断均由该资料证明。正文的 R5-01 等短标识与本表对应；前四章使用内容标题链接。本版资料整理与引用日期为 **2026-09-05**，未给出无法确认的网页发布日期。

在线手册可能随维护版本更新。Redis 源码链接分别固定到 7.2 分支或 7.2.5 标签，分支链接仍可能变化；Kafka 恢复实现链接固定到 3.9.0 标签，3.9 系列 Javadoc 则可能显示该系列后续补丁版。涉及复现实验时，软件构建版本、配置与故障条件仍需一并记录。

本书中的 SQL、命令和验证方案是机制说明及设计示例。本版未以运行真实 Redis、MySQL、Kafka 服务或集群故障演练来认证这些示例；第 10 章明确区分设定的目标、待执行的验收与已完成的推理。

## 第 1 章 引言：为什么是这三个软件

- **R1-01**　Redis 项目．[Redis 数据类型说明](https://redis.io/docs/latest/develop/data-types/)．Redis 7.x 讨论基线，在线文档．[引用日期：2026-09-05]。
- **R1-02**　Oracle．[MySQL8.0一致性非锁定读](https://dev.mysql.com/doc/refman/8.0/en/innodb-consistent-read.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R1-03**　Oracle．[MySQL8.0多版本机制](https://dev.mysql.com/doc/refman/8.0/en/innodb-multi-versioning.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R1-04**　Apache Kafka 项目．[3.9设计文档](https://kafka.apache.org/39/design/design/)．Kafka 3.9 文档．[引用日期：2026-09-05]。

## 第 2 章 数据结构与协议：为各自的目标而设计

- **R2-01**　Redis 项目．[SDS实现](https://github.com/redis/redis/blob/7.2.5/src/sds.c)．Redis 7.2.5 源码．[引用日期：2026-09-05]。
- **R2-02**　Redis 项目．[字典实现](https://github.com/redis/redis/blob/7.2.5/src/dict.c)．Redis 7.2.5 源码．[引用日期：2026-09-05]。
- **R2-03**　Redis 项目．[Redis7.2.5集合实现](https://github.com/redis/redis/blob/7.2.5/src/t_set.c)．Redis 7.2.5 源码．[引用日期：2026-09-05]。
- **R2-04**　Oracle．[MySQL8.0行格式说明](https://dev.mysql.com/doc/refman/8.0/en/innodb-row-format.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R2-05**　Oracle．[自适应哈希索引说明](https://dev.mysql.com/doc/refman/8.0/en/innodb-adaptive-hash.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R2-06**　Apache Kafka 项目．[Kafka3.9消息格式](https://kafka.apache.org/39/implementation/message-format/)．Kafka 3.9 文档．[引用日期：2026-09-05]。
- **R2-07**　Redis 项目．[RESP规范](https://redis.io/docs/latest/develop/reference/protocol-spec/)．Redis 7.x 讨论基线，在线文档．[引用日期：2026-09-05]。
- **R2-08**　Oracle．[文本结果集](https://dev.mysql.com/doc/dev/mysql-server/latest/page_protocol_com_query_response_text_resultset.html)．MySQL 协议开发资料．[引用日期：2026-09-05]。
- **R2-09**　Oracle．[二进制结果集](https://dev.mysql.com/doc/dev/mysql-server/latest/page_protocol_binary_resultset.html)．MySQL 协议开发资料．[引用日期：2026-09-05]。
- **R2-10**　Apache Kafka 项目．[Kafka3.9协议](https://kafka.apache.org/39/design/protocol/)．Kafka 3.9 文档．[引用日期：2026-09-05]。

## 第 3 章 生命周期管理：优雅启动与关闭

- **R3-01**　Redis 项目．[SHUTDOWN文档](https://redis.io/docs/latest/commands/shutdown/)．Redis 7.x 讨论基线，在线文档．[引用日期：2026-09-05]。
- **R3-02**　Oracle．[MySQL8.0选项文件](https://dev.mysql.com/doc/refman/8.0/en/option-files.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R3-03**　Oracle．[InnoDB恢复说明](https://dev.mysql.com/doc/refman/8.0/en/innodb-recovery.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R3-04**　Oracle．[innodb_fast_shutdown 参数定义](https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html#sysvar_innodb_fast_shutdown)．MySQL 8.0．[引用日期：2026-09-05]。
- **R3-05**　Apache Kafka 项目．[Kafka3.9.0 BrokerLifecycleManager](https://github.com/apache/kafka/blob/3.9.0/core/src/main/scala/kafka/server/BrokerLifecycleManager.scala)．Kafka 3.9.0 源码．[引用日期：2026-09-05]。
- **R3-06**　Kubernetes 项目．[探针定义](https://kubernetes.io/docs/concepts/workloads/pods/probes/)．在线文档；行为范围见正文．[引用日期：2026-09-05]。
- **R3-07**　Kubernetes 项目．[容器生命周期钩子](https://kubernetes.io/docs/concepts/containers/container-lifecycle-hooks/)．在线文档；行为范围见正文．[引用日期：2026-09-05]。

## 第 4 章 内存与磁盘：速度与持久化的平衡

- **R4-01**　Redis 项目．[Redis淘汰说明](https://redis.io/docs/latest/develop/reference/eviction/)．Redis 7.x 讨论基线，在线文档．[引用日期：2026-09-05]。
- **R4-02**　Redis 项目．[Redis持久化说明](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)．Redis 7.x 讨论基线，在线文档．[引用日期：2026-09-05]。
- **R4-03**　Redis 项目．[WAITAOF定义](https://redis.io/docs/latest/commands/waitaof/)．Redis 7.2 起．[引用日期：2026-09-05]。
- **R4-04**　Oracle．[缓冲池抗扫描说明](https://dev.mysql.com/doc/refman/8.0/en/innodb-performance-midpoint_insertion.html)．MySQL 8.0；小版本限制见正文．[引用日期：2026-09-05]。
- **R4-05**　Oracle．[redo提交策略](https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html#sysvar_innodb_flush_log_at_trx_commit)．MySQL 8.0；小版本限制见正文．[引用日期：2026-09-05]。
- **R4-06**　Oracle．[binlog同步选项](https://dev.mysql.com/doc/refman/8.0/en/replication-options-binary-log.html#sysvar_sync_binlog)．MySQL 8.0；小版本限制见正文．[引用日期：2026-09-05]。
- **R4-07**　Oracle．[doublewrite说明](https://dev.mysql.com/doc/refman/8.0/en/innodb-doublewrite-buffer.html)．MySQL 8.0；小版本限制见正文．[引用日期：2026-09-05]。
- **R4-08**　Oracle．[change buffer说明](https://dev.mysql.com/doc/refman/8.0/en/innodb-change-buffer.html)．MySQL 8.0；小版本限制见正文．[引用日期：2026-09-05]。
- **R4-09**　Linux 内核项目．[Linux虚拟内存参数](https://docs.kernel.org/admin-guide/sysctl/vm.html)．内核虚拟内存参数在线文档．[引用日期：2026-09-05]。
- **R4-10**　Apache Kafka 项目．[生产者配置](https://kafka.apache.org/39/configuration/producer-configs/)．Kafka 3.9．[引用日期：2026-09-05]。

## 第 5 章 分层架构设计 — 存储层 / 逻辑层 / 交互层

- **R5-01**　Redis 项目．[Redis 客户端处理](https://redis.io/docs/latest/develop/reference/clients/)．Redis 7.x 讨论基线，在线文档．[引用日期：2026-09-05]。
- **R5-02**　Redis 项目．[UNLINK 命令](https://redis.io/docs/latest/commands/unlink/)．Redis 7.x 讨论基线，在线文档．[引用日期：2026-09-05]。
- **R5-03**　Oracle．[可插拔存储引擎概述](https://dev.mysql.com/doc/refman/8.0/en/pluggable-storage-overview.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R5-04**　Oracle．[Query Cache 的工作方式（MySQL 5.7 历史资料）](https://dev.mysql.com/doc/refman/5.7/en/query-cache-operation.html)．MySQL 5.7（历史）．[引用日期：2026-09-05]。
- **R5-05**　Oracle．[MySQL 8.0 新增及移除的功能](https://dev.mysql.com/doc/refman/8.0/en/mysql-nutshell.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R5-06**　Apache Kafka 项目．[Kafka 协议](https://kafka.apache.org/39/design/protocol/)．Kafka 3.9 文档．[引用日期：2026-09-05]。
- **R5-07**　Apache Kafka 项目．[Kafka 设计](https://kafka.apache.org/39/design/design/)．Kafka 3.9 文档．[引用日期：2026-09-05]。
- **R5-08**　Apache Kafka 项目．[Kafka 分层存储](https://kafka.apache.org/39/operations/tiered-storage/)．Kafka 3.9 文档．[引用日期：2026-09-05]。

## 第 6 章 安全机制 — 权限、加密、审计

- **R6-01**　Redis 项目．[Redis 访问控制列表](https://redis.io/docs/latest/operate/oss_and_stack/management/security/acl/)．Redis 7.x 讨论基线，在线文档．[引用日期：2026-09-05]。
- **R6-02**　Redis 项目．[ACL DRYRUN 命令](https://redis.io/docs/latest/commands/acl-dryrun/)．Redis 7.x 讨论基线，在线文档．[引用日期：2026-09-05]。
- **R6-03**　Oracle．[Caching SHA-2 认证插件](https://dev.mysql.com/doc/refman/8.0/en/caching-sha2-pluggable-authentication.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R6-04**　Apache Kafka 项目．[使用 SASL 认证](https://kafka.apache.org/39/security/authentication-using-sasl/)．Kafka 3.9 文档．[引用日期：2026-09-05]。
- **R6-05**　Redis 项目．[Redis 安全机制](https://redis.io/docs/latest/operate/oss_and_stack/management/security/)．Redis 7.x 讨论基线，在线文档．[引用日期：2026-09-05]。
- **R6-06**　Oracle．[访问控制：请求验证](https://dev.mysql.com/doc/refman/8.0/en/request-access.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R6-07**　Oracle．[部分撤销权限](https://dev.mysql.com/doc/refman/8.0/en/partial-revokes.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R6-08**　Apache Kafka 项目．[授权与 ACL](https://kafka.apache.org/39/security/authorization-and-acls/)．Kafka 3.9 文档．[引用日期：2026-09-05]。
- **R6-09**　Redis 项目．[Redis TLS](https://redis.io/docs/latest/operate/oss_and_stack/management/security/encryption/)．Redis 7.x 讨论基线，在线文档．[引用日期：2026-09-05]。
- **R6-10**　Oracle．[InnoDB 静态数据加密](https://dev.mysql.com/doc/refman/8.0/en/innodb-data-encryption.html)．MySQL 8.0．[引用日期：2026-09-05]。

## 第 7 章 集群架构 — 从单点到分布式

- **R7-01**　Seth Gilbert、Nancy Lynch．[Brewer’s Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services](https://doi.org/10.1145/564585.564601)．ACM SIGACT News, 2002, 33(2): 51–59．[引用日期：2026-09-05]。
- **R7-02**　Redis 项目．[WAIT 命令](https://redis.io/docs/latest/commands/wait/)．Redis 7.x 讨论基线，在线文档．[引用日期：2026-09-05]。
- **R7-03**　Redis 项目．[Redis Sentinel](https://redis.io/docs/latest/operate/oss_and_stack/management/sentinel/)．Redis 7.x 讨论基线，在线文档．[引用日期：2026-09-05]。
- **R7-04**　Redis 项目．[Redis Cluster 规范](https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/)．Redis 7.x 讨论基线，在线文档．[引用日期：2026-09-05]。
- **R7-05**　Oracle．[半同步复制](https://dev.mysql.com/doc/refman/8.0/en/replication-semisync.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R7-06**　Oracle．[Group Replication](https://dev.mysql.com/doc/refman/8.0/en/group-replication.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R7-07**　Oracle．[组复制一致性保证](https://dev.mysql.com/doc/refman/8.0/en/group-replication-consistency-guarantees.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R7-08**　Apache Kafka 项目．[生产者配置](https://kafka.apache.org/39/configuration/producer-configs/)．Kafka 3.9 文档．[引用日期：2026-09-05]。
- **R7-09**　Apache Kafka 项目．[主题配置](https://kafka.apache.org/39/configuration/topic-level-configs/)．Kafka 3.9 文档．[引用日期：2026-09-05]。
- **R7-10**　Apache Kafka 项目．[KRaft 运维](https://kafka.apache.org/39/operations/kraft/)．Kafka 3.9 文档．[引用日期：2026-09-05]。

## 第 8 章 磁盘存储格式：数据写下以后

- **R8-01**　Redis 项目．[Redis 7.2 RDB 类型及操作码](https://github.com/redis/redis/blob/7.2/src/rdb.h)．Redis 7.2 分支源码．[引用日期：2026-09-05]。
- **R8-02**　Redis 项目．[RDB 保存与加载实现](https://github.com/redis/redis/blob/7.2/src/rdb.c)．Redis 7.2 分支源码．[引用日期：2026-09-05]。
- **R8-03**　Redis 项目．[RESP 规范](https://redis.io/docs/latest/develop/reference/protocol-spec/)．Redis 7.x 讨论基线，在线文档．[引用日期：2026-09-05]。
- **R8-04**　Redis 项目．[Redis 持久化与多部分 AOF](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/)．Redis 7.x 讨论基线，在线文档．[引用日期：2026-09-05]。
- **R8-05**　Redis 项目．[Redis 7.2 AOF 清单及重写实现](https://github.com/redis/redis/blob/7.2/src/aof.c)．Redis 7.2 分支源码．[引用日期：2026-09-05]。
- **R8-06**　Oracle．[InnoDB 页大小配置](https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html#sysvar_innodb_page_size)．MySQL 8.0．[引用日期：2026-09-05]。
- **R8-07**　Oracle．[InnoDB 文件空间管理](https://dev.mysql.com/doc/refman/8.0/en/innodb-file-space.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R8-08**　Oracle．[InnoDB 行格式](https://dev.mysql.com/doc/refman/8.0/en/innodb-row-format.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R8-09**　Oracle．[InnoDB 双写缓冲与文件](https://dev.mysql.com/doc/refman/8.0/en/innodb-doublewrite-buffer.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R8-10**　Oracle．[InnoDB redo log](https://dev.mysql.com/doc/refman/8.0/en/innodb-redo-log.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R8-11**　Apache Kafka 项目．[Kafka 3.9 设计与日志管理](https://kafka.apache.org/39/design/design/)．Kafka 3.9 文档．[引用日期：2026-09-05]。
- **R8-12**　Apache Kafka 项目．[Kafka 记录格式](https://kafka.apache.org/39/implementation/message-format/)．Kafka 3.9 文档．[引用日期：2026-09-05]。
- **R8-13**　Apache Kafka 项目．[Kafka 3.9.0 OffsetIndex](https://github.com/apache/kafka/blob/3.9.0/storage/src/main/java/org/apache/kafka/storage/internals/log/OffsetIndex.java)．Kafka 3.9.0 源码．[引用日期：2026-09-05]。
- **R8-14**　Apache Kafka 项目．[Kafka 3.9.0 TimeIndex](https://github.com/apache/kafka/blob/3.9.0/storage/src/main/java/org/apache/kafka/storage/internals/log/TimeIndex.java)．Kafka 3.9.0 源码．[引用日期：2026-09-05]。
- **R8-15**　Apache Kafka 项目．[KIP-405 分层存储设计](https://cwiki.apache.org/confluence/spaces/KAFKA/pages/97554472/KIP-405%2BKafka%2BTiered%2BStorage)．设计提案；采用范围见正文．[引用日期：2026-09-05]。
- **R8-16**　Apache Kafka 项目．[Kafka 3.9.0 TierStateMachine](https://github.com/apache/kafka/blob/3.9.0/core/src/main/java/kafka/server/TierStateMachine.java)．Kafka 3.9.0 源码．[引用日期：2026-09-05]。

## 第 9 章 数据同步：确认、历史与续传

- **R9-01**　Redis 项目．[Redis 复制机制](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)．Redis 7.x 讨论基线，在线文档．[引用日期：2026-09-05]。
- **R9-02**　Redis 项目．[Redis 脚本复制说明](https://redis.io/docs/latest/develop/programmability/eval-intro/)．Redis 7.x 讨论基线，在线文档．[引用日期：2026-09-05]。
- **R9-03**　Redis 项目．[Redis 7.2 复制实现](https://github.com/redis/redis/blob/7.2/src/replication.c)．Redis 7.2 分支源码．[引用日期：2026-09-05]。
- **R9-04**　Redis 项目．[WAIT 的范围与限制](https://redis.io/docs/latest/commands/wait/)．Redis 7.x 讨论基线，在线文档．[引用日期：2026-09-05]。
- **R9-05**　Redis 项目．[WAITAOF](https://redis.io/docs/latest/commands/waitaof/)．Redis 7.2 起．[引用日期：2026-09-05]。
- **R9-06**　Oracle．[binlog 格式](https://dev.mysql.com/doc/refman/8.0/en/binary-log-formats.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R9-07**　Oracle．[复制线程](https://dev.mysql.com/doc/refman/8.0/en/replication-threads.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R9-08**　Oracle．[多线程副本配置](https://dev.mysql.com/doc/refman/8.0/en/replication-options-replica.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R9-09**　Oracle．[GTID 格式与存储](https://dev.mysql.com/doc/refman/8.0/en/replication-gtids-concepts.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R9-10**　Oracle．[GTID 自动定位](https://dev.mysql.com/doc/refman/8.0/en/replication-gtids-auto-positioning.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R9-11**　Oracle．[半同步复制](https://dev.mysql.com/doc/refman/8.0/en/replication-semisync.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R9-12**　Oracle．[半同步等待点与可见性](https://dev.mysql.com/doc/refman/8.0/en/replication-semisync-interface.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R9-13**　Apache Kafka 项目．[生产者 acks](https://kafka.apache.org/39/configuration/producer-configs/#producerconfigs_acks)．Kafka 3.9 文档．[引用日期：2026-09-05]。
- **R9-14**　Apache Kafka 项目．[最小 ISR 配置](https://kafka.apache.org/39/configuration/broker-configs/#brokerconfigs_min.insync.replicas)．Kafka 3.9 文档．[引用日期：2026-09-05]。
- **R9-15**　Apache Kafka 项目．[KIP-101 的恢复问题与方案](https://cwiki.apache.org/confluence/spaces/KAFKA/pages/67634337/KIP-101+-+Alter+Replication+Protocol+to+use+Leader+Epoch+rather+than+High+Watermark+for+Truncation)．设计提案；采用范围见正文．[引用日期：2026-09-05]。
- **R9-16**　Apache Kafka 项目．[3.9.0 TierStateMachine 与恢复条件](https://github.com/apache/kafka/blob/3.9.0/core/src/main/java/kafka/server/TierStateMachine.java)．Kafka 3.9.0 源码．[引用日期：2026-09-05]。
- **R9-17**　Apache Kafka 项目．[KafkaConsumer 的位置与提交说明](https://kafka.apache.org/39/javadoc/org/apache/kafka/clients/consumer/KafkaConsumer.html)．Kafka 3.9 系列 API 文档．[引用日期：2026-09-05]。

## 第 10 章 把观察用于一次完整设计

- **R10-01**　Oracle．[CHECK 约束](https://dev.mysql.com/doc/refman/8.0/en/create-table-check-constraints.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R10-02**　Amazon Web Services．[事务性 outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html)．AWS Prescriptive Guidance．[引用日期：2026-09-05]。
- **R10-03**　Oracle．[UPDATE 与锁](https://dev.mysql.com/doc/refman/8.0/en/innodb-locks-set.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R10-04**　Oracle．[事务提交与回滚](https://dev.mysql.com/doc/refman/8.0/en/commit.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R10-10**　Oracle．[死锁处理](https://dev.mysql.com/doc/refman/8.0/en/innodb-deadlocks-handling.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R10-05**　Oracle．[InnoDB 锁定读取](https://dev.mysql.com/doc/refman/8.0/en/innodb-locking-reads.html)．MySQL 8.0．[引用日期：2026-09-05]。
- **R10-06**　Apache Kafka 项目．[Kafka 生产者幂等配置](https://kafka.apache.org/39/configuration/producer-configs/#producerconfigs_enable.idempotence)．Kafka 3.9 文档．[引用日期：2026-09-05]。
- **R10-07**　Apache Kafka 项目．[消费者进度提交](https://kafka.apache.org/39/javadoc/org/apache/kafka/clients/consumer/KafkaConsumer.html)．Kafka 3.9 系列 API 文档．[引用日期：2026-09-05]。
- **R10-08**　Oracle．[InnoDB 与事务持久性](https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html#sysvar_innodb_flush_log_at_trx_commit)．MySQL 8.0．[引用日期：2026-09-05]。
- **R10-09**　Oracle．[binlog同步](https://dev.mysql.com/doc/refman/8.0/en/replication-options-binary-log.html#sysvar_sync_binlog)．MySQL 8.0．[引用日期：2026-09-05]。

## 引用与示例的使用范围

本文的产品名称和相关标识归其各自权利人所有。引用官方文档、源代码页面和原始论文用于说明技术机制，不表示这些项目或机构对本书作出认可。正文图表为本稿已有插图的整理与重绘；本版不对第三方资料重新授予许可。

第 10 章库存系统是为展开设计判断而构造的示例，事务表结构、请求状态及目标负载均已在正文声明为设定。书中保留的作者亲历与该示例分别叙述，参考文献也不被用来证明作者经历或示例的实测结果。
