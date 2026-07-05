# F03 命令可运行性审查报告

## 验证汇总
- 总命令/SQL/配置参数检查数：全部 chapters/\*/chapter.md（共 10 章 + 3 个附录文件）
- 确认有问题：2 条（1 个参数不存在声称错误，1 个配置默认值陈述偏差）
- 存疑待作者核实：1 条
- 已核实正确：大量（详见下文典型项列表）

---

## 逐条发现

### 🔴 错误

#### 1. [chapters/04-memory-disk/chapter.md:105] 配置参数不存在声称错误："aof-use-rdb-preamble 已移除"

- **原文**：
  ```
  `aof-use-rdb-preamble` 在 5.x–6.x 中默认即为 `yes`；7.0 多部 AOF 改造后该配置项已移除，base 文件始终为 RDB 格式，行为等效。
  ```

- **问题**：`aof-use-rdb-preamble` 在 Redis 7.0 中并**没有被移除**。该配置项在 7.x 中仍然存在，且默认值仍为 `yes`。Redis 核心团队曾讨论过弃用计划（GitHub issue #9794），但最终决定保留该配置项。7.0 引入的 Multi-Part AOF 是独立的新特性，不替代也不移除 `aof-use-rdb-preamble`。

- **建议**：去掉"该配置项已移除"的表述。可改为：`"aof-use-rdb-preamble` 配置项在 7.x 中保留且默认仍为 `yes`，AOF 重写生成的 base 文件始终为 RDB 格式；同时 7.0 引入了 Multi-Part AOF 新架构，文件组织改为 base + incr + manifest 的多文件方式"。

- **来源**：
  - GitHub redis/redis issue #9794 "Additional AOFRW deprecation cleanups"（讨论过但未执行移除）
  - Redis 官方 7.0 发行说明（未列出 `aof-use-rdb-preamble` 移除）
  - 社区实测：`redis-server --version` + `CONFIG GET aof-use-rdb-preamble` 在 7.0+ 仍返回 `yes`

#### 2. [chapters/10-summary/chapter.md:96] MySQL 配置默认值陈述有偏差："若再开启 syn_binlog=1"

- **原文**：
  ```
  MySQL 默认偏向持久性（`innodb_flush_log_at_trx_commit=1` 是默认），若再开启 `sync_binlog=1` 即"双 1"配置...
  ```

- **问题**：在 MySQL 8.0.x（本书基线）中，`sync_binlog=1` 本身就是默认值（与 `innodb_flush_log_at_trx_commit=1` 同为默认），"双 1"已是 MySQL 8.0 的出厂默认配置，不是需要"再开启"的额外选项。原文"若再开启"的表述暗示 `sync_binlog=1` 不是默认值，在 MySQL 8.0 语境下不准确。

- **建议**：改为：`"MySQL 默认即使用"双 1"配置（`innodb_flush_log_at_trx_commit=1` 与 `sync_binlog=1` 均为 8.0 默认值），让每条已提交事务都 fsync..."`

- **来源**：
  - MySQL 8.0 官方文档确认：`sync_binlog` 默认值 = 1（自 MySQL 5.7 起从未改变）
  - MySQL 8.0 新的默认值公告：`log_bin` 在 8.0 默认开启，使得 `sync_binlog=1` 自然生效

---

### 🟡 存疑

#### 3. [chapters/06-security/chapter.md:135] Kafka `allow.everyone.if.no.acl.found` 默认值历史声称

- **原文**：
  ```
  `allow.everyone.if.no.acl.found` 这个参数（对 `AclAuthorizer` 生效...）从 1.x 起默认就是 false
  ```

- **存疑点**：在 Kafka 3.x 基线下该参数默认值为 `false` 是正确的。但"从 1.x 起默认就是 false"这一历史断言需要作者核实。Kafka 授权模型在 0.x→1.x 过渡期间经历较大变化，`AclAuthorizer` 在某些早期版本（如 0.9/0.10）可能默认更宽松。建议确认 KAFKA-XXXX 中该参数的默认值变更记录。

- **建议**：如果无法精确回溯到 1.x，可改为"自 Kafka 2.0 起默认即为 false（3.x 沿用），即无 ACL 即拒绝"。

- **来源**：
  - Apache Kafka 3.x 官方文档：`allow.everyone.if.no.acl.found` 默认 `false`
  - Confluent/Kafka 社区资料：该参数在 `StandardAuthorizer` 和 `AclAuthorizer` 中均受支持

---

### ✅ 已核实正确（典型项列表）

以下已验证在基线版本（Redis 7.x / MySQL 8.0.x / Kafka 3.x）下正确：

**Redis 命令：**
- `SET`、`GET`、`KEYS *`、`FLUSHALL`、`ZADD`、`ZRANGEBYSCORE`、`LPUSH`、`BRPOP`、`XADD`、`XREAD`、`INCR`、`SELECT`、`MGET`、`SPOP`、`RANDOMKEY`、`EXPIRE`、`EXPIREAT`、`PEXPIREAT`
- `SHUTDOWN`、`SHUTDOWN SAVE`、`SHUTDOWN NOSAVE`、`SAVE`、`BGSAVE`、`BGREWRITEAOF`
- `ACL SETUSER`（含 `>password`、`~pattern`、`+@category` 语法）、`ACL SAVE`、`ACL LOAD`、`ACL LOG`、`AUTH`
- `PUBLISH` / `SUBSCRIBE`（Pub/Sub）
- `PSYNC`、`REPLCONF ACK`、`REPLICAOF host port`、`REPLICAOF NO ONE`
- `CONFIG SET`、`HELLO`（RESP3 协商）
- `redis-cli`、`redis-benchmark`、`redis-check-aof --fix`
- RESP 类型：`+` 字符串、`-` 错误、`:` 整数、`$` 批量字符串、`*` 数组
- RESP3 类型：`%` Map、`~` Set、`>` Push、`#` Boolean、`_` Null

**Redis 配置参数：**
- `requirepass`、`appendonly`、`appendfsync`（always/everysec/no）、`aof-use-rdb-preamble`（存在且默认 yes，未移除 — 但此纠正为 🔴 项#1）
- `maxmemory`、`maxmemory-samples`（默认 5）、`save`、`lfu-log-factor`、`lfu-decay-time`
- 淘汰策略：`noeviction`、`allkeys-lru`、`allkeys-lfu`、`allkeys-random`、`volatile-lru`、`volatile-lfu`、`volatile-random`、`volatile-ttl`
- `protected-mode`（默认 yes，3.2.0+）、`tls-protocols`、`client-output-buffer-limit`
- `repl-backlog-size`（默认 1MB）、`repl-backlog-ttl`（默认 3600s）
- `min-replicas-to-write`（Redis 5.0+ 新名）、`min-replicas-max-lag`（新名）
- `aclfile`（默认为空，需显式设置）
- `appendonlydir/`（7.0 多部 AOF 目录）

**MySQL 命令 / SQL：**
- `SELECT`、`ORDER BY score DESC LIMIT 100`、`UPDATE ... WHERE`、`FLUSH PRIVILEGES`、`SHOW PROCESSLIST`、`SHOW VARIABLES`
- `CREATE ROLE`、`GRANT role TO user`、`SET ROLE`
- `ALTER USER ... REQUIRE SSL`、`ALTER USER ... REQUIRE X509`
- `COM_STMT_PREPARE`、`COM_STMT_EXECUTE`（MySQL 协议命令）

**MySQL 配置参数：**
- `innodb_flush_log_at_trx_commit`（默认 1）、`sync_binlog`（默认 1）
- `innodb_fast_shutdown`（0/1/2，默认 1）
- `innodb_old_blocks_time`（默认 1000ms）、`innodb_page_size`（默认 16KB，可设 4K/8K/16K/32K/64K）
- `innodb_redo_log_capacity`（8.0.30+，默认 100MB）
- `innodb_doublewrite`（默认 ON/`DETECT_AND_RECOVER`）
- `innodb_redo_log_encrypt`、`innodb_undo_log_encrypt`（8.0.1+）
- `binlog_encryption`（8.0.14+）
- `caching_sha2_password`（正确拼写；8.0.4+ 默认认证插件）
- `innodb_default_row_format`（默认 `dynamic`）
- `rpl_semi_sync_source_enabled`（8.0.26+ 新名，旧名 `_master_enabled` 已弃用）
- `rpl_semi_sync_source_timeout`（默认 10000ms/10s）
- `rpl_semi_sync_source_wait_for_replica_count`（默认 1）
- `replica_parallel_workers`（8.0.26+ 新名，旧名 `slave_parallel_workers`）
- `replica_parallel_type`（`LOGICAL_CLOCK`，8.0 默认）
- `group_replication_consistency`（默认 `EVENTUAL`）
- `binlog_group_commit_sync_delay`、`binlog_group_commit_sync_no_delay_count`
- `connection_control`（插件）
- `max_connections`（通过 `SHOW VARIABLES LIKE 'max_connections'` 查看）

**Kafka 配置参数：**
- `acks`（0/1/all/-1；3.0 起默认 `all` — KIP-679 ✅）
- `min.insync.replicas`（默认 1）
- `enable.idempotence`（3.0 起默认 `true` — KIP-679）
- `transactional.id`、`log.segment.bytes`（默认 1GB）
- `log.roll.hours`（默认 168h/7d）
- `log.index.interval.bytes`（默认 4096/4KB）
- `log.flush.interval.messages`、`log.flush.interval.ms`
- `replica.lag.time.max.ms`（默认 30000/30s）
- `unclean.leader.election.enable`（默认 `false`，0.11 起 — KAFKA-4711）
- `controlled.shutdown.enable`（默认 `true`）
- `controlled.shutdown.max.retries`、`controlled.shutdown.retry.backoff.ms`
- `allow.everyone.if.no.acl.found`（3.x 默认 `false` — 以 3.x 为准；1.x 历史待确认见 🟡项）
- `num.network.threads`（默认 3）、`num.io.threads`（默认 8）
- `num.recovery.threads.per.data.dir`（默认 1，KIP-1030 3.9+ 改为动态）
- `batch.size`、`linger.ms`
- `listeners`、`listener.security.protocol.map`、`listener.name.*.ssl.keystore.location`
- `authorizer.class.name`（`kafka.security.authorizer.AclAuthorizer` / `StandardAuthorizer`）
- `super.users`
- `server.properties`（Kafka 配置文件）

**Kafka 日志段文件命名与协议：**
- `.log` `.index` `.timeindex` 三件套 + `.snapshot`
- RecordBatch V2 格式字段：`baseOffset`（8 字节）、`batchLength`、`partitionLeaderEpoch`、`magic`、`CRC`、`attributes`、`lastOffsetDelta`、`baseTimestamp`、`maxTimestamp`、`producerId`、`producerEpoch`、`baseSequence`、`recordsCount`（所有字段存在且语义正确）
- 协议头部：`api_key`（2B）、`api_version`（2B）、`correlation_id`（4B）、`client_id`

**系统级命令 / 信号：**
- `kill -9`（SIGKILL）、SIGTERM、SIGINT、SIGPIPE、SIGCHLD
- `systemctl stop redis`、`nc`（netcat）
- `terminationGracePeriodSeconds`、`preStop hook`、`readiness probe`（K8s 概念）

**各软件启动就绪日志：**
- Redis: `Ready to accept connections`
- MySQL: `ready for connections`
- Kafka: `[KafkaServer id=0] started`

---

## 备注

1. 本报告仅验证命令/参数/语法的**存在性、拼写和默认值准确性**。不验证书中引用的性能数字、延迟基准或吞吐估算（这些已在其他审查维度覆盖）。

2. Redis RDB 版本号映射（7.0→v10、7.2→v11、7.4→v12）已在外部资料中得到印证，书中数据正确。✅

3. RESP3 的五种新增类型前缀字符（`%` `~` `>` `#` `_`）全部正确。✅

4. Kafka 自 0.11 起引入的幂等/事务（KIP-98）语义，以及 3.3+ KRaft 生产可用时间线，书中描述与官方路线图一致。✅

5. Redis 在 6.0 引入多线程 I/O（书中表述为"可选、7.x 默认关闭"）—— 此描述属实：多线程 I/O 仅加速网络读写，命令执行仍单线程。`io-threads-do-reads` 默认关闭。✅
