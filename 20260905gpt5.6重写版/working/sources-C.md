# C组正文来源账本

核查日期：2026-09-05。Redis7.x（源码示例7.2）、MySQL8.0.x、Kafka3.9.0；在线API页面可能标同系列更新小版本，精确恢复实现固定3.9.0。以下是正文实际引用，支持相邻具体机制，不表示整个软件或全部命令完成源码终审。第10章为设计推演，SQL为参数绑定片段，未宣称生产实测。

## 第8章

| 标识 | 来源与支持主题 |
|---|---|
| R8-01 | [Redis 7.2 RDB 类型及操作码](https://github.com/redis/redis/blob/7.2/src/rdb.h) |
| R8-02 | [RDB 保存与加载实现](https://github.com/redis/redis/blob/7.2/src/rdb.c) |
| R8-03 | [RESP 规范](https://redis.io/docs/latest/develop/reference/protocol-spec/) |
| R8-04 | [Redis 持久化与多部分 AOF](https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/) |
| R8-05 | [Redis 7.2 AOF 清单及重写实现](https://github.com/redis/redis/blob/7.2/src/aof.c) |
| R8-06 | [InnoDB 页大小配置](https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html#sysvar_innodb_page_size) |
| R8-07 | [InnoDB 文件空间管理](https://dev.mysql.com/doc/refman/8.0/en/innodb-file-space.html) |
| R8-08 | [InnoDB 行格式](https://dev.mysql.com/doc/refman/8.0/en/innodb-row-format.html) |
| R8-09 | [InnoDB 双写缓冲与文件](https://dev.mysql.com/doc/refman/8.0/en/innodb-doublewrite-buffer.html) |
| R8-10 | [InnoDB redo log](https://dev.mysql.com/doc/refman/8.0/en/innodb-redo-log.html) |
| R8-11 | [Kafka 3.9 设计与日志管理](https://kafka.apache.org/39/design/design/) |
| R8-12 | [Kafka 记录格式](https://kafka.apache.org/39/implementation/message-format/) |
| R8-13 | [Kafka 3.9.0 OffsetIndex](https://github.com/apache/kafka/blob/3.9.0/storage/src/main/java/org/apache/kafka/storage/internals/log/OffsetIndex.java) |
| R8-14 | [Kafka 3.9.0 TimeIndex](https://github.com/apache/kafka/blob/3.9.0/storage/src/main/java/org/apache/kafka/storage/internals/log/TimeIndex.java) |
| R8-15 | [KIP-405 分层存储设计](https://cwiki.apache.org/confluence/spaces/KAFKA/pages/97554472/KIP-405%2BKafka%2BTiered%2BStorage) |
| R8-16 | [Kafka 3.9.0 TierStateMachine](https://github.com/apache/kafka/blob/3.9.0/core/src/main/java/kafka/server/TierStateMachine.java) |

## 第9章

| 标识 | 来源与支持主题 |
|---|---|
| R9-01 | [Redis 复制机制](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/) |
| R9-02 | [Redis 脚本复制说明](https://redis.io/docs/latest/develop/programmability/eval-intro/) |
| R9-03 | [Redis 7.2 复制实现](https://github.com/redis/redis/blob/7.2/src/replication.c) |
| R9-04 | [WAIT 的范围与限制](https://redis.io/docs/latest/commands/wait/) |
| R9-05 | [WAITAOF](https://redis.io/docs/latest/commands/waitaof/) |
| R9-06 | [binlog 格式](https://dev.mysql.com/doc/refman/8.0/en/binary-log-formats.html) |
| R9-07 | [复制线程](https://dev.mysql.com/doc/refman/8.0/en/replication-threads.html) |
| R9-08 | [多线程副本配置](https://dev.mysql.com/doc/refman/8.0/en/replication-options-replica.html) |
| R9-09 | [GTID 格式与存储](https://dev.mysql.com/doc/refman/8.0/en/replication-gtids-concepts.html) |
| R9-10 | [GTID 自动定位](https://dev.mysql.com/doc/refman/8.0/en/replication-gtids-auto-positioning.html) |
| R9-11 | [半同步复制](https://dev.mysql.com/doc/refman/8.0/en/replication-semisync.html) |
| R9-12 | [半同步等待点与可见性](https://dev.mysql.com/doc/refman/8.0/en/replication-semisync-interface.html) |
| R9-13 | [生产者 acks](https://kafka.apache.org/39/configuration/producer-configs/#producerconfigs_acks) |
| R9-14 | [最小 ISR 配置](https://kafka.apache.org/39/configuration/broker-configs/#brokerconfigs_min.insync.replicas) |
| R9-15 | [KIP-101 的恢复问题与方案](https://cwiki.apache.org/confluence/spaces/KAFKA/pages/67634337/KIP-101+-+Alter+Replication+Protocol+to+use+Leader+Epoch+rather+than+High+Watermark+for+Truncation) |
| R9-16 | [3.9.0 TierStateMachine 与恢复条件](https://github.com/apache/kafka/blob/3.9.0/core/src/main/java/kafka/server/TierStateMachine.java) |
| R9-17 | [KafkaConsumer 的位置与提交说明](https://kafka.apache.org/39/javadoc/org/apache/kafka/clients/consumer/KafkaConsumer.html) |

## 第10章

| 标识 | 来源与支持主题 |
|---|---|
| R10-01 | [CHECK 约束](https://dev.mysql.com/doc/refman/8.0/en/create-table-check-constraints.html) |
| R10-02 | [事务性 outbox](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html) |
| R10-03 | [UPDATE 与锁](https://dev.mysql.com/doc/refman/8.0/en/innodb-locks-set.html) |
| R10-04 | [事务提交与回滚](https://dev.mysql.com/doc/refman/8.0/en/commit.html) |
| R10-10 | [死锁处理](https://dev.mysql.com/doc/refman/8.0/en/innodb-deadlocks-handling.html) |
| R10-05 | [InnoDB 锁定读取](https://dev.mysql.com/doc/refman/8.0/en/innodb-locking-reads.html) |
| R10-06 | [Kafka 生产者幂等配置](https://kafka.apache.org/39/configuration/producer-configs/#producerconfigs_enable.idempotence) |
| R10-07 | [消费者进度提交](https://kafka.apache.org/39/javadoc/org/apache/kafka/clients/consumer/KafkaConsumer.html) |
| R10-08 | [InnoDB 与事务持久性](https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html#sysvar_innodb_flush_log_at_trx_commit) |
| R10-09 | [binlog同步](https://dev.mysql.com/doc/refman/8.0/en/replication-options-binary-log.html#sysvar_sync_binlog) |

