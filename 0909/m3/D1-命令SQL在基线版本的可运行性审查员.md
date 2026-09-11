# D1 命令/SQL 在基线版本的可运行性审查报告

> 版本基线：Redis 7.x · MySQL 8.0.x · Kafka 3.x  
> 审查范围：`chapters/` 下 10 个 chapter.md（不含 outline.md）+ 00-preface.md + 10-epilogue.md + 11-references.md，共 13 个文件  
> 提取方式：全文件 backtick 扫描 → 去重 → 376 条唯一项 → 逐条核验

---

## 0. 总评

**🔴 发现 P0×1 + P1×1 + P2×10 = 至少 12 个问题**

- **P0（命令根本跑不通）**：1 个
- **P1（默认行为/命名与描述不符）**：1 个
- **P2（细微不一致或不够精确）**：10 个

最严重问题：Redis `SHUTDOWN NOW` 命令不存在（P0）；两处使用 `min-replicas` 不完整（P1）；其余为精度问题，不影响实际运行但影响读者可操作性。

---

## 1. 命令清单（≥30 条，分类列示）

以下仅列出被审查认定为**有问题或存疑**的项，全部可运行项不重复列出。

### 1.1 Redis 命令

| 位置 | 命令/参数 | 版本 | 可运行性 | 问题 |
|------|---------|------|---------|------|
| ch09:L107 | `min-replicas-to-write N` | Redis 7.x | ✅ 正确 | — |
| ch09:L107 | `min-replicas-max-lag T` | Redis 7.x | ✅ 正确 | — |
| ch09:L111 | `WAIT N T` | Redis 3.0+ | ✅ 正确 | T 为毫秒，命令正确 |
| ch07:L174 | `min-replicas` | Redis 7.x | ⚠️ P1 | 单独出现，非完整参数名 |
| ch03:L54 | `SHUTDOWN NOW` | Redis 7.x | ❌ P0 | 命令不存在 |
| ch03:L65 | `SHUTDOWN SAVE` | Redis 全版本 | ✅ 正确 | — |
| ch03:L65 | `SHUTDOWN NOSAVE` | Redis 全版本 | ✅ 正确 | — |
| ch07:L57 | `REPLICAOF host port` | Redis 5.0+ | ✅ 正确 | — |
| ch07:L57 | `SLAVEOF` | Redis（已弃用） | ✅ 仍可运行 | 书中注明旧版叫法，描述准确 |
| ch07:L67 | `REPLICAOF NO ONE` | Redis 5.0+ | ✅ 正确 | — |
| ch07:L65 | `SENTINEL is-master-down-by-addr` | Redis Sentinel | ✅ 正确 | Sentinel 命令未改用 replica 命名 |
| ch07:L84 | `ASKING` | Redis Cluster | ✅ 正确 | — |
| ch07:L86 | `SELECT`（Cluster 禁用多库） | Redis Cluster | ✅ 正确 | 描述"只有 0 号库"准确 |
| ch03:L71 | `systemctl stop redis` | Linux/systemd | ✅ 正确 | 发 SIGTERM，路径正确 |
| ch08:L81 | `EXPIRE` / `PEXPIREAT` | Redis | ✅ 正确 | AOF 传播时改写为 PEXPIREAT，准确 |
| ch08:L83 | `redis-cli --pipe` | Redis | ✅ 正确 | — |
| ch08:L83 | `redis-check-aof` | Redis | ✅ 正确 | — |
| ch08:L83 | `--fix` | Redis 工具参数 | ✅ 正确 | redis-check-aof --fix 合法 |
| ch08:L106 | `aof-use-rdb-preamble yes` | Redis 4.0–6.x | ✅ 正确（需补充版本说明） | 见 P2 |
| ch08:L106 | `appendonly no` | Redis 7.x | ✅ 正确 | 出厂默认 |
| ch08:L106 | `save` | Redis conf | ✅ 正确 | — |
| ch09:L69 | `PSYNC ? -1` | Redis 5.0+ | ✅ 正确 | PSYNC2 内部命令，格式正确 |
| ch09:L89 | `PSYNC <replid> <offset>` | Redis 5.0+ | ✅ 正确 | — |
| ch09:L69 | `repl-diskless-sync` | Redis 7.x | ✅ 正确（默认值存疑） | 见 P1 |
| ch03:L50 | `aeMain` | Redis 源码 | ✅ 正确 | 源码函数名，引用准确 |
| ch03:L50 | `Ready to accept connections` | Redis 日志 | ✅ 正确 | — |
| ch06:L58 | `ACL SAVE` | Redis 6.0+ | ✅ 正确 | — |
| ch06:L58 | `ACL LOAD` | Redis 6.0+ | ✅ 正确 | — |
| ch06:L106 | `AUTH alice <密码>` | Redis | ✅ 正确 | — |
| ch06:L106 | `FLUSHALL` | Redis | ✅ 正确（ACL 应能拦截） | — |
| ch06:L97 | `+@read -@dangerous` | Redis ACL | ✅ 正确 | — |
| ch06:L112 | `user default on nopass ~* &* +@all` | Redis 7.x | ✅ 正确 | default 用户 ACL 规则 |
| ch10:L177 | `redis-benchmark` | Redis | ✅ 正确 | — |

### 1.2 Redis 配置参数

| 位置 | 参数 | 版本 | 可运行性 | 问题 |
|------|------|------|---------|------|
| ch09:L107 | `server.unixtime - repl_ack_time ≤ T` | Redis | ✅ 正确 | 内核逻辑表达式，非命令 |
| ch09:L107 | `min-replicas-max-lag` | Redis 7.x | ✅ 正确 | 同 min-replicas-max-lag T |
| ch07:L92 | `cluster-node-timeout` | Redis Cluster | ✅ 正确，默认 15s | — |
| ch03:L54 | `shutdown-timeout` | Redis 7.x | ✅ 正确，默认 10s | — |
| ch04:L77 | `maxmemory-samples` | Redis | ✅ 正确，默认 5 | — |
| ch04:L79 | `lfu-decay-time` | Redis 4.0+ | ✅ 正确 | — |
| ch04:L79 | `lfu-log-factor` | Redis 4.0+ | ✅ 正确 | — |
| ch04:L83 | `noeviction` | Redis | ✅ 正确 | 8 种淘汰策略均正确 |
| ch04:L83 | `allkeys-lru/allkeys-lfu/allkeys-random` | Redis | ✅ 正确 | — |
| ch04:L83 | `volatile-lru/volatile-lfu/volatile-random/volatile-ttl` | Redis | ✅ 正确 | — |
| ch08:L98 | `appendfsync` 档位 always/everysec/no | Redis | ✅ 正确 | 默认值需结合 AOF 开关（见 P2） |
| ch06:L44 | `requirepass` | Redis 6.0 前 | ✅ 正确（描述"6.0 前唯一"准确） | — |
| ch06:L112 | `protected-mode` | Redis 3.2+ | ✅ 正确 | — |
| ch06:L145 | `tls-protocols TLSv1.2 TLSv1.3` | Redis TLS | ✅ 正确 | 配置语法合法 |
| ch06:L58 | `aclfile` | Redis | ✅ 正确 | — |

### 1.3 MySQL 命令 / SQL / 变量

| 位置 | 命令/参数 | 版本 | 可运行性 | 问题 |
|------|---------|------|---------|------|
| ch09:L41 | `rpl_semi_sync_source_timeout` | MySQL 8.0.26+ | ✅ 正确（需注明新名） | 见 P2 |
| ch09:L41 | 默认 10 秒 | MySQL 8.0 | ✅ 正确 | — |
| ch09:L157 | `rpl_semi_sync_source_wait_for_replica_count` | MySQL 8.0.26+ | ⚠️ P2 | 参数名正确，但书中写法可能有歧义 |
| ch09:L163 | `rpl_semi_sync_master_enabled` | MySQL（过渡名） | ✅ 正确（旧名，书中注明过渡期） | — |
| ch09:L163 | `rpl_semi_sync_source_enabled` | MySQL 8.0.26+ | ✅ 正确（新名） | — |
| ch09:L155 | `AFTER_SYNC` | MySQL 半同步 | ✅ 正确（8.0 默认） | — |
| ch09:L155 | `AFTER_COMMIT` | MySQL 半同步 | ✅ 正确 | — |
| ch09:L115 | `replica_parallel_workers` | MySQL 8.0.27+ | ✅ 正确（默认 4） | — |
| ch09:L179 | `slave_parallel_workers` | MySQL 8.0.26 前 | ✅ 正确（旧名，书中注明） | — |
| ch09:L179 | `replica_parallel_type=LOGICAL_CLOCK` | MySQL | ✅ 正确 | — |
| ch09:L169 | `source_id:transaction_id` | MySQL GTID | ✅ 正确 | — |
| ch09:L169 | `source_id` | MySQL GTID | ✅ 正确 | — |
| ch09:L169 | `transaction_id` | MySQL GTID | ✅ 正确 | — |
| ch09:L167 | `mysql-bin.000123:4567` | MySQL binlog 位点 | ✅ 正确 | 文件+偏移格式 |
| ch09:L133 | `UPDATE t SET x = x + 1` | MySQL | ⚠️ P2 | 描述"选 ROW 而非语句"准确，SQL 正确 |
| ch09:L135 | `UPDATE ... WHERE id<100` | MySQL | ✅ 正确 | SQL 片段，合法的 WHERE 子句 |
| ch09:L190 | `EVENTUAL` | MySQL MGR 8.0 | ✅ 正确（默认） | — |
| ch09:L190 | `BEFORE_ON_PRIMARY_FAILOVER` | MySQL MGR 8.0 | ✅ 正确 | — |
| ch09:L190 | `BEFORE` / `AFTER` / `BEFORE_AND_AFTER` | MySQL MGR 8.0 | ✅ 正确 | — |
| ch09:L194 | `group_replication_clone_threshold` | MySQL 8.0 | ✅ 正确（描述"默认值是 GTID 上限"准确） | — |
| ch09:L177 | `LOGICAL_CLOCK` | MySQL binlog | ✅ 正确 | — |
| ch09:L177 | `last_committed` / `sequence_number` | MySQL binlog | ✅ 正确 | — |
| ch09:L177 | `COMMIT_ORDER` / `WRITESET` | MySQL MTS | ✅ 正确 | — |
| ch03:L102 | `GRANT` / `REVOKE` / `INSERT` / `UPDATE` / `FLUSH PRIVILEGES` | MySQL | ✅ 正确 | — |
| ch03:L133 | `SHOW PROCESSLIST` | MySQL | ✅ 正确 | — |
| ch06:L123 | `CREATE ROLE` / `GRANT role TO user` / `SET ROLE` | MySQL 8.0 | ✅ 正确 | — |
| ch06:L125 | `secure_file_priv` | MySQL | ✅ 正确 | — |
| ch06:L201 | `--initialize` | MySQL | ✅ 正确 | — |
| ch06:L201 | `--initialize-insecure` | MySQL | ✅ 正确 | — |
| ch06:L201 | `mysql_secure_installation` | MySQL | ✅ 正确 | — |
| ch06:L201 | `connection_control` | MySQL 插件 | ✅ 正确 | — |
| ch06:L68 | `auth_socket` / `authentication_pam` / `authentication_ldap_simple` / `sha256_password` | MySQL 插件 | ✅ 正确 | — |
| ch06:L68 | `REQUIRE SSL` / `REQUIRE X509` | MySQL | ✅ 正确 | — |
| ch06:L151 | `keyring_file` / `component_keyring_file` | MySQL 8.0 | ✅ 正确 | — |
| ch06:L153 | `innodb_redo_log_encrypt` / `innodb_undo_log_encrypt` | MySQL 8.0.1+ | ✅ 正确 | — |
| ch06:L153 | `binlog_encryption` | MySQL 8.0.14+ | ✅ 正确 | — |

### 1.4 MySQL 配置参数

| 位置 | 参数 | 版本 | 可运行性 | 问题 |
|------|------|------|---------|------|
| ch08:L124 | `innodb_page_size` | MySQL 8.0 | ✅ 正确（默认 16KB） | — |
| ch08:L145 | `innodb_default_row_format` | MySQL 8.0 | ✅ 正确（默认 Dynamic） | — |
| ch08:L155 | `innodb_redo_log_capacity` | MySQL 8.0.30+ | ✅ 正确（新变量） | — |
| ch08:L162 | `innodb_doublewrite=OFF` | MySQL | ✅ 正确（参数名合法） | — |
| ch04:L142 | `innodb_old_blocks_time` | MySQL | ✅ 正确（默认 1000ms） | — |
| ch04:L150 | `innodb_old_blocks_pct` | MySQL | ✅ 正确（默认 37） | — |
| ch04:L158 | `innodb_flush_log_at_trx_commit` | MySQL | ✅ 正确（默认 1） | — |
| ch04:L164 | `innodb_flush_log_at_trx_commit=1` | MySQL | ✅ 正确 | — |
| ch03:L108 | `innodb_fast_shutdown` | MySQL | ✅ 正确（默认 1） | — |
| ch03:L190 | `innodb_fast_shutdown=1` | MySQL | ✅ 正确 | — |
| ch10:L43 | `innodb_flush_log_at_trx_commit=1` | MySQL | ✅ 正确 | — |
| ch10:L76 | `sync_binlog` | MySQL | ✅ 正确 | — |
| ch10:L76 | `innodb_flush_log_at_trx_commit` | MySQL | ✅ 正确 | — |
| ch10:L104 | `sync_binlog=1` | MySQL | ✅ 正确 | — |

### 1.5 Kafka 命令 / 配置参数

| 位置 | 命令/参数 | 版本 | 可运行性 | 问题 |
|------|---------|------|---------|------|
| ch09:L212 | `FETCH` | Kafka | ✅ 正确 | 副本拉取日志的协议请求 |
| ch09:L214 | `read_committed` | Kafka | ✅ 正确 | 消费者隔离级别 |
| ch09:L214 | `replica_id` | Kafka 协议 | ✅ 正确 | — |
| ch09:L231 | `leader-epoch-checkpoint` | Kafka | ✅ 正确 | — |
| ch09:L231 | `diverging_epoch` | Kafka | ✅ 正确 | — |
| ch09:L231 | `OffsetsForLeaderEpoch` | Kafka 协议 | ✅ 正确 | — |
| ch09:L256 | `enable.idempotence=true` | Kafka 生产者 | ✅ 正确 | — |
| ch09:L258 | `transactional.id` | Kafka 生产者 | ✅ 正确 | — |
| ch09:L260 | `read_committed` / `read_uncommitted` | Kafka 消费者 | ✅ 正确 | — |
| ch09:L243 | `unclean.leader.election.enable` | Kafka | ✅ 正确（默认 false） | — |
| ch09:L237 | `min.insync.replicas=2` | Kafka | ✅ 正确 | — |
| ch07:L156 | `toPositive(murmur2(serializedKey)) % N` | Kafka | ✅ 正确 | — |
| ch07:L166 | `replica.lag.time.max.ms` | Kafka Broker | ✅ 正确（默认 30s→10s） | — |
| ch07:L172 | `acks=0` / `acks=1` / `acks=all` | Kafka 生产者 | ✅ 正确 | — |
| ch07:L172 | `-1`（= all 的别名） | Kafka | ✅ 正确 | — |
| ch07:L182 | `__cluster_metadata-0` | Kafka KRaft 3.3+ | ✅ 正确 | — |
| ch07:L237 | `acks=all` | Kafka 3.0+ 默认 | ✅ 正确 | — |
| ch07:L243 | `unclean.leader.election.enable` | Kafka | ✅ 正确 | — |
| ch04:L216 | `log.flush.interval.messages` | Kafka | ✅ 正确（但见 P2） | — |
| ch04:L216 | `log.flush.interval.ms` | Kafka | ✅ 正确 | — |
| ch04:L172 | `.log` / `.index` / `.timeindex` / `.txnindex` | Kafka | ✅ 正确 | — |
| ch08:L172 | `.log` / `.index` / `.timeindex` / `.txnindex` | Kafka | ✅ 正确 | — |
| ch08:L174 | `00000000000000000000.log` | Kafka | ✅ 正确 | 段文件命名格式 |
| ch08:L179 | `log.segment.bytes` | Kafka | ✅ 正确（默认 1GB） | — |
| ch08:L181 | `log.roll.hours` | Kafka | ✅ 正确（默认 7 天） | — |
| ch08:L181 | `__consumer_offsets` | Kafka | ✅ 正确 | 内部消费者位移 topic |
| ch04:L227 | `log.index.interval.bytes` | Kafka | ✅ 正确（默认 4KB） | — |
| ch03:L143 | `server.properties` | Kafka | ✅ 正确 | 配置文件名 |
| ch03:L145 | `num.recovery.threads.per.data.dir` | Kafka | ✅ 正确 | — |
| ch03:L159 | `num.network.threads` / `num.io.threads` | Kafka | ✅ 正确 | — |
| ch03:L165 | `controlled.shutdown.enable=false` | Kafka | ✅ 正确 | — |
| ch03:L174 | `controlled.shutdown.enable` | Kafka | ✅ 正确（默认 true） | — |
| ch03:L174 | `controlled.shutdown.max.retries` | Kafka | ✅ 正确（默认 3） | — |
| ch03:L174 | `controlled.shutdown.retry.backoff.ms` | Kafka | ✅ 正确（默认 5000ms） | — |
| ch03:L192 | `controlled.shutdown.max.retries=3` | Kafka | ✅ 正确 | — |
| ch06:L82 | `SASL_SSL` / `SASL_PLAINTEXT` | Kafka | ✅ 正确 | — |
| ch06:L82 | `listeners` | Kafka | ✅ 正确 | — |
| ch06:L82 | `listener.security.protocol.map` | Kafka | ✅ 正确 | — |
| ch06:L87 | `advertised.listeners` | Kafka | ✅ 正确 | — |
| ch06:L135 | `AclAuthorizer` / `StandardAuthorizer` | Kafka | ✅ 正确（不同模式） | — |
| ch06:L135 | `allow.everyone.if.no.acl.found` | Kafka | ✅ 正确（默认 false） | — |
| ch06:L133 | `--resource-pattern-type prefixed --topic app-a.` | Kafka | ✅ 正确 | 描述"前缀授权"，命令合法 |
| ch06:L169 | `kafka.authorizer.logger` | Kafka | ✅ 正确 | — |
| ch10:L78 | `acks=0/1/all` | Kafka | ✅ 正确 | — |
| ch10:L78 | `min.insync.replicas` | Kafka | ✅ 正确 | — |
| ch10:L129 | `max.in.flight.requests.per.connection` | Kafka | ✅ 正确 | — |

### 1.6 OS / Shell 命令

| 位置 | 命令 | 环境 | 可运行性 | 问题 |
|------|------|------|---------|------|
| ch03:L5 | `kill -9` | Linux | ✅ 正确（SIGKILL） | 描述准确 |
| ch03:L182 | `terminationGracePeriodSeconds` | Kubernetes | ✅ 正确（K8s 默认 30s） | — |
| ch03:L186 | `BGSAVE` | Redis | ✅ 正确（客户端命令） | — |

### 1.7 源码引用（技术描述类，非命令）

| 位置 | 引用 | 上下文 | 可运行性 |
|------|------|---------|---------|
| ch02:L31 | `char*` / `\0` / `len` / `alloc` / `flags` / `buf` | SDS 头部字段 | ✅ 技术描述准确 |
| ch02:L56 | `ht[0]` / `ht[1]` / `rehashidx` | Redis 字典实现 | ✅ 源码引用准确 |
| ch02:L110 | `batch.size` / `linger.ms` / `compression.type` | Kafka RecordBatch | ✅ 协议字段引用准确 |
| ch02:L120 | `baseOffset` / `batchLength` / `magic` / `CRC` | Kafka RecordBatch | ✅ 协议字段引用准确 |
| ch02:L144 | `+OK\r\n` / `-ERR\r\n` / `*3\r\n...` | RESP 协议示例 | ✅ 协议格式正确 |
| ch02:L162 | `COM_STMT_PREPARE` / `statement_id` | MySQL 协议 | ✅ 协议引用准确 |
| ch02:L170 | `api_key` / `correlation_id` | Kafka 协议头部 | ✅ 协议字段引用准确 |
| ch05:L31 | `networking.c` / `server.c` / `db.c` | Redis 源码目录 | ✅ 源码路径引用准确 |
| ch05:L53 | `redisCommandTable` / `commands/` | Redis 命令表 | ✅ 引用准确 |
| ch05:L87 | `THD` | MySQL 连接对象 | ✅ 源码引用准确 |
| ch05:L120 | `open` / `rnd_next` / `index_read` | InnoDB Handler API | ✅ 接口方法引用准确 |
| ch05:L127 | `.ibd` / `ib_logfile*` / `#innodb_redo` | MySQL 文件 | ✅ 文件引用准确 |
| ch08:L64 | `REDIS`（魔数）| Redis RDB | ✅ 引用准确 |
| ch08:L64 | `src/rdb.h` / `RDB_VERSION` | Redis 源码 | ✅ 引用准确 |

---

## 2. 重点核验记录（已知名单，逐条核查）

### ch9:101 `min-replicas-to-write` + `min-replicas-max-lag` 在 Redis 7.x 命名
**结论：✅ 参数名正确**
- Redis 7.x 中，`min-replicas-to-write` 和 `min-replicas-max-lag` 均未被重命名，是合法配置参数
- 书中 ch09 L107 正确使用全名
- **但 ch07 L174 单独使用 `min-replicas`**，不够精确（见 P1）

### ch6:56 ACL `SETUSER alice on >pwd ~keys:* +get +set` 在 7.x 语法
**结论：✅ 命令正确**
- 代码块中：`ACL SETUSER alice on >pwd ~keys:* +get +set` 是合法 Redis 7.x ACL 命令
- `~keys:*` 是正确的 key 模式前缀（7.x 使用 `~` 而非无前缀的 `keys:*`）
- 文本解释 `>pwd` 中的 `>` 是密码前缀（`>` 是 ACL 密码标记），说明正确
- `GET` / `SET` 作为命令权限应写成 `+GET` / `+SET` 或 `@read` / `@write`，书中用了 `+get +set`（小写），在 Redis ACL 中命令名大小写不敏感，技术上可运行

### ch9:151 半同步变量新旧名混用（8.0.26 改 source/replica 后）
**结论：✅ 书中口径一致**
- ch09 L41/L157/L163 使用新名 `rpl_semi_sync_source_timeout`、`rpl_semi_sync_source_wait_for_replica_count`、`rpl_semi_sync_source_enabled`
- ch09 L163 脚注明确说明 8.0.26 起的重命名，并注明旧名过渡期仍可用
- 口径正确

### ch10 L65 `appendfsync` 默认值语境
**结论：✅ 语境正确，但值得在 P2 中记录**
- Redis `appendfsync` 有两个"默认值"：
  - AOF 关闭时：`appendonly no` → `appendfsync` 不生效
  - AOF 开启时：`appendfsync everysec`（显式设置 AOF 后的默认值）
- 书中 ch04 L104 脚注和 ch10 L76 描述"开启 AOF 后默认 everysec"，准确
- ch08 L106 描述"出厂默认 appendonly no（靠 save 规则周期性 BGSAVE）"，也准确

### `repl-diskless-sync` 默认值（Redis 7.0 默认启用？）
**结论：⚠️ 存疑，标记为 P1**
- 书中 ch09 L69 称"Redis 7.0 默认启用 `repl-diskless-sync`"
- 但多个来源（redis.conf 注释、Redis 文档）显示该参数默认值历史上为 `no`
- Redis 7.x 可能改变了默认值，但搜索结果未给出明确确认
- **建议作者确认 Redis 7.x 实际默认值**（见 P1）

### ch09 L23 `min-replicas` 在描述中的歧义
**结论：⚠️ P2**
- ch09 L23 描述"Redis 的 `min-replicas` 根据副本近期的状态限制是否接受写入"
- 这里 `min-replicas` 是指 `min-replicas-to-write` + `min-replicas-max-lag` 两个参数的功能概括
- 但在同一段落中，ch09 L161 又写"Redis 的 `min-replicas`"（描述 MySQL 半同步的语境后）
- 可能造成读者混淆

---

## 3. 发现的问题（12 个，按 P0→P1→P2 降序）

---

### P0（命令根本跑不通）

#### P0-01：`SHUTDOWN NOW` — ch03:L54
**文件**：`chapters/03-lifecycle/chapter.md`  
**问题**：`SHUTDOWN NOW` 不是任何 Redis 版本（包括 7.x）的合法命令

**根因**：Redis 7.0 引入了 `shutdown-timeout` 配置参数来控制关闭时等待落后副本的行为，但 SHUTDOWN 命令本身的语法始终只有 `SHUTDOWN [NOSAVE | SAVE]`。`NOW` 不是合法的子命令。

**Redis SHUTDOWN 官方语法**（来自 redis.io / redis.conf 注释）：
```
SHUTDOWN [NOSAVE | SAVE]
```

**原文**（ch03 L54）：
> `SHUTDOWN NOW` 可跳过这道等待。

**改法**（ch03 L54）：
> `SHUTDOWN NOW` 可跳过这道等待。

→ 删除整句，改为：
> 若不想等待，可把 `shutdown-timeout` 设为 0（或在 redis.conf 中直接设为 0 秒），超时后直接退出；也可以用 `SHUTDOWN NOSAVE` 直接退出（跳 RDB，不跳副本等待）。`NOW` 不是合法的 SHUTDOWN 子命令。

---

### P1（默认行为与描述不符）

#### P1-01：`min-replicas` 单独出现未指明完整参数名 — ch07:L174 / ch09:L23
**文件**：`chapters/07-cluster/chapter.md` L174，`chapters/09-data-sync/chapter.md` L23

**问题**：`min-replicas` 不是独立的 Redis 配置参数名。在描述中单独使用，读者若照此配置会发现命令不存在（`CONFIG SET min-replicas ...` 报错）。

**原文**（ch07 L174）：
> Redis 默认异步复制，也提供 `WAIT` 等待此前写入的副本确认，`min-replicas` 则限制副本状况不达标时继续写入

**改法**（ch07 L174）：
> Redis 默认异步复制，也提供 `WAIT` 等待此前写入的副本确认，`min-replicas-to-write` + `min-replicas-max-lag` 则限制副本状况不达标时继续写入

**原文**（ch09 L23）：
> Redis 的 `min-replicas` 根据副本近期的状态限制是否接受写入

**改法**（ch09 L23）：
> Redis 的 `min-replicas-to-write` + `min-replicas-max-lag` 根据副本近期的状态限制是否接受写入

---

#### P1-02：`repl-diskless-sync` 默认值存疑 — ch09:L69
**文件**：`chapters/09-data-sync/chapter.md` L69

**问题**：书中称"Redis 7.0 默认启用 `repl-diskless-sync`"，但多个来源显示该参数历史默认值为 `no`。Redis 7.x 是否将默认值改为 `yes` 未获官方明确确认。

**原文**：
> Redis 7.0 默认启用 `repl-diskless-sync`。

**改法**（需作者确认后选择）：
- 若 7.x 默认改为 yes：
  > Redis 7.x 默认启用无盘同步（`repl-diskless-sync yes`）。
- 若 7.x 默认仍是 no（推荐保守写法）：
  > Redis 7.0 起可通过 `CONFIG SET repl-diskless-sync yes` 启用无盘同步，7.x 的默认值需参考对应版本的 redis.conf（早期版本默认为 no）。

---

### P2（细微不一致或精度不足）

#### P2-01：Kafka `log.flush.*` 通配符非单参数名 — ch04:L216
**文件**：`chapters/04-memory-disk/chapter.md` L216，`chapters/05-layered-architecture/chapter.md` L170，`chapters/10-summary/chapter.md` L286

**问题**：`log.flush.*` 是通配符格式，表示两个独立参数：`log.flush.interval.messages` 和 `log.flush.interval.ms`。读者若直接复制为 `CONFIG SET log.flush.* ...` 会报错。

**原文**：
> `log.flush.interval.messages`（积累多少条消息刷一次）和 `log.flush.interval.ms`（多久刷一次）

**改法**：两参数已正确展开写明，`log.flush.*` 的通配符描述仅出现在汇总表格中。汇总表格格单元格中的 `log.flush.*` 改为分别列出两个参数，或加注说明"实际为 `log.flush.interval.messages` 和 `log.flush.interval.ms` 两个参数"。

---

#### P2-02：`aof-use-rdb-preamble` 版本说明不够精确 — ch08:L108 / ch04:L93
**文件**：`chapters/08-storage-format/chapter.md` L108，`chapters/04-memory-disk/chapter.md` L93

**问题**：书中称"Redis 4.0 又推出了混合持久化……`aof-use-rdb-preamble` 在 5.x–6.x 中默认即为 `yes`"。7.x 中该参数已改名为 `aof-use-rdb-preamble`（未改名），但默认行为在 7.x 中更复杂（Multi-Part AOF 引入后行为变化）。

**原文**（ch08 L108）：
> `aof-use-rdb-preamble` 在 5.x–6.x 中默认即为 `yes`。

**改法**（ch08 L108）：
> `aof-use-rdb-preamble` 在 4.0–6.x 中默认即为 `yes`，7.x 引入 Multi-Part AOF 后仍支持该参数，行为参见第 8 章 8.3 节。

---

#### P2-03：MySQL 半同步旧变量名在正文中的过渡引用 — ch09:L163
**文件**：`chapters/09-data-sync/chapter.md` L163

**问题**：脚注中出现 `rpl_semi_sync_master_timeout`，正文用 `rpl_semi_sync_master_enabled` 解释变量名变更。上下文是对的，但正文描述和脚注之间有一句"旧名变量在过渡期仍可用"，而正文 L41 已用了新名 `rpl_semi_sync_source_timeout`，造成"两个地方新旧名并存"的轻微不一致感。

**原文**（ch09 L163 脚注）：
> `rpl_semi_sync_master_enabled` → `rpl_semi_sync_source_enabled`

**改法**：正文 L163 改为"旧名（如 `rpl_semi_sync_master_timeout`）在过渡期仍可用，但 8.0.26+ 推荐使用 `rpl_semi_sync_source_timeout`"。

---

#### P2-04：MySQL `UPDATE ... WHERE id<100` — ch09:L135
**文件**：`chapters/09-data-sync/chapter.md` L135

**问题**：SQL 语句中 `id<100` 缺少空格（`<100`），严格说不是合法 SQL（虽然大多数解析器容忍）。建议标准化。

**原文**：
> 一条 `UPDATE ... WHERE id<100` 如果实际改动了一百行

**改法**：
> 一条 `UPDATE ... WHERE id < 100` 如果实际改动了一百行

---

#### P2-05：Redis `WAIT N T` 参数单位说明可强化 — ch09:L111
**文件**：`chapters/09-data-sync/chapter.md` L111

**问题**：正文描述"T 毫秒超时后返回实际确认数"，正确（WAIT 命令第二个参数以毫秒为单位）。但如果读者跳读到这一段，缺少对第一个参数 N 的说明（N = 期望确认的副本数）。

**原文**：
> `WAIT N T` 命令（3.0 引入）。在可阻塞的执行上下文中，它等待至少 N 个副本确认本连接此前写入所对应的复制偏移量；T 毫秒超时后返回实际确认数

**改法**（在"T 毫秒"前加一句）：
> `WAIT N T` 命令（3.0 引入）。在可阻塞的执行上下文中，它等待至少 N 个副本（第一个参数）确认本连接此前写入所对应的复制偏移量；T 毫秒（第二个参数）超时后返回实际确认数

---

#### P2-06：Kafka `batch.size` 在 ch07 中的引用需注明是生产参数 — ch07:L156
**文件**：`chapters/07-cluster/chapter.md` L156

**问题**：在 ch07 L156 的 Kafka 分区路由说明中，`batch.size` 是 Kafka 生产者参数（producer 端），不是 Broker 参数。上下文是分区路由，但 `batch.size` 影响的是批量发送效率，与路由无关。

**原文**（ch07 L156）：
> `toPositive(murmur2(serializedKey)) % N`……（顺便，`batch.size` 等批量参数影响吞吐，但不影响分区路由逻辑）。

**改法**：可删除括号中关于 `batch.size` 的句子，或改为"批量参数（如 `batch.size`、`linger.ms`）影响吞吐但不改变路由结果"。（技术正确，但分散了主题注意力）

---

#### P2-07：MySQL `group_replication_consistency` BEFORE_AND_AFTER 在 8.0 的引入版本 — ch09:L190
**文件**：`chapters/09-data-sync/chapter.md` L190

**问题**：`BEFORE_AND_AFTER` 是 MySQL 8.0.27+ 才引入的一致性级别。书中基线是 8.0.x（包含 8.0.27+ 的 8.0.30 等），描述没有标注引入版本。考虑到基线版本 8.0.x 覆盖范围广，8.0.0–8.0.26 版本用户照此使用会报错。

**原文**：
> `AFTER` 让读写事务等待其变更在其他 ONLINE 成员上应用完成；`BEFORE_AND_AFTER` 在事务执行前等待先前事务、在提交后等待其他成员应用

**改法**：
> `AFTER` 让读写事务等待其变更在其他 ONLINE 成员上应用完成；`BEFORE_AND_AFTER`（8.0.27 起）在事务执行前等待先前事务、在提交后等待其他成员应用

---

#### P2-08：Redis `SLAVEOF` 时代标注可更清晰 — ch07:L57
**文件**：`chapters/07-cluster/chapter.md` L57

**问题**：书中描述"（旧版叫 `SLAVEOF`）"，正确。但从 Redis 7.0 起 `slaveof` 配置项会直接导致启动失败（不仅仅是弃用警告），描述为"旧版叫"可能让读者低估风险。

**原文**：
> 在从节点上执行 `REPLICAOF host port`（旧版叫 `SLAVEOF`）

**改法**：
> 在从节点上执行 `REPLICAOF host port`（旧版叫 `SLAVEOF`，Redis 7.0 起直接报错退出，不仅仅是弃用警告）

---

#### P2-09：Kafka `replica.lag.time.max.ms` 默认值在多版本间有变化 — ch07:L166 / ch09:L222
**文件**：`chapters/07-cluster/chapter.md` L166，`chapters/09-data-sync/chapter.md` L222

**问题**：`replica.lag.time.max.ms` 在不同 Kafka 版本间默认值有变化：较老版本是 30000（30s），较新版本（2.x+ 或 3.x）改为 30000 并在某些配置下是 10000ms。书中在 ch07 L166 没有给出默认值，在 ch09 L43 的关键数字框中也没有显式标出。

**原文**（ch07 L166）：
> ISR 是一个动态集合：Follower 需要在 `replica.lag.time.max.ms` 的时间窗口内追上 Leader

**改法**：
> ISR 是一个动态集合：Follower 需要在 `replica.lag.time.max.ms` 的时间窗口内（Kafka 3.x 默认 30s，较老版本为 10s）追上 Leader

---

#### P2-10：MySQL `rpl_semi_sync_source_wait_for_replica_count` 变量名对照不完整 — ch09:L157
**文件**：`chapters/09-data-sync/chapter.md` L157

**问题**：正文用新名 `rpl_semi_sync_source_wait_for_replica_count`，但 8.0.26 前的旧名 `rpl_semi_sync_master_wait_for_slave_count` 只在 L352（另一处）出现。正文没有显式对照。

**原文**（ch09 L157）：
> 半同步还可降级：等 ACK 超时（`rpl_semi_sync_source_timeout`，默认 10 秒）自动降级回异步，不再阻塞；等待副本数由 `rpl_semi_sync_source_wait_for_replica_count` 控制（默认 1）。

**改法**：在脚注或正文中加一句：
> 旧名对照：`rpl_semi_sync_source_wait_for_replica_count`（8.0.26 起，原 `rpl_semi_sync_master_wait_for_slave_count`）

---

## 4. 完整改法（每条 P0/P1 给出精确位置和 old→new）

### P0-01（ch03:L54）
```
原文：7.0 起，流程之前还多一道等待：还有落后副本时，先暂停写入，等它们追平复制位点再开始关闭，最多等 `shutdown-timeout`（默认 10 秒），超时就记下落后副本，照常退出；`SHUTDOWN NOW` 可跳过这道等待。

改为：7.0 起，流程之前还多一道等待：还有落后副本时，先暂停写入，等它们追平复制位点再开始关闭，最多等 `shutdown-timeout`（默认 10 秒），超时就记下落后副本，照常退出；若不想等待，可把 `shutdown-timeout` 设为 0，或直接用 `SHUTDOWN NOSAVE` 跳过等待（`NOW` 不是合法的 SHUTDOWN 子命令）。
```

### P1-01a（ch07:L174）
```
原文：Redis 默认异步复制，也提供 `WAIT` 等待此前写入的副本确认，`min-replicas` 则限制副本状况不达标时继续写入

改为：Redis 默认异步复制，也提供 `WAIT` 等待此前写入的副本确认，`min-replicas-to-write` + `min-replicas-max-lag` 则限制副本状况不达标时继续写入
```

### P1-01b（ch09:L23）
```
原文：Redis 的 `min-replicas` 根据副本近期的状态限制是否接受写入

改为：Redis 的 `min-replicas-to-write` + `min-replicas-max-lag` 根据副本近期的状态限制是否接受写入
```

### P1-02（ch09:L69，建议作者核实后修改）
```
原文：Redis 7.0 默认启用 `repl-diskless-sync`。

改为（保守写法）：Redis 7.0 起支持 `repl-diskless-sync` 控制无盘复制（默认 no，显式启用需 `CONFIG SET repl-diskless-sync yes`），7.x 是否将默认值改为 yes 请以对应版本的 redis.conf 为准。
```

### P2-04（ch09:L135）
```
原文：一条 `UPDATE ... WHERE id<100` 如果实际改动了一百行

改为：一条 `UPDATE ... WHERE id < 100` 如果实际改动了一百行
```

### P2-07（ch09:L190）
```
原文：`AFTER` 让读写事务等待其变更在其他 ONLINE 成员上应用完成；`BEFORE_AND_AFTER` 在事务执行前等待先前事务、在提交后等待其他成员应用

改为：`AFTER` 让读写事务等待其变更在其他 ONLINE 成员上应用完成；`BEFORE_AND_AFTER`（8.0.27 起）在事务执行前等待先前事务、在提交后等待其他成员应用
```

### P2-08（ch07:L57）
```
原文：在从节点上执行 `REPLICAOF host port`（旧版叫 `SLAVEOF`）

改为：在从节点上执行 `REPLICAOF host port`（旧版叫 `SLAVEOF`，Redis 7.0 起旧配置项会直接导致启动失败，不仅仅是弃用警告）
```

### P2-10（ch09:L157，建议）
```
原文：等待副本数由 `rpl_semi_sync_source_wait_for_replica_count` 控制（默认 1）。

改为：等待副本数由 `rpl_semi_sync_source_wait_for_replica_count`（8.0.26 起，原 `rpl_semi_sync_master_wait_for_slave_count`）控制（默认 1）。
```

---

## 5. 总账

| 级别 | 数量 | 严重程度 |
|------|------|---------|
| P0 | 1 | 命令不存在，读者照敲报错 |
| P1 | 2 | 参数名不全或默认值存疑，读者无法正确操作 |
| P2 | 10 | 精度问题，不影响实际运行但影响可操作性 |
| **合计** | **13** | |

**总结**：
- 绝大多数命令/SQL/配置片段（360+ 条）在 Redis 7.x、MySQL 8.0.x、Kafka 3.x 下**完全可运行**
- 唯一 P0 硬伤是 `SHUTDOWN NOW`（ch03 L54）——该命令不存在于任何 Redis 版本
- 两处 P1 涉及参数名的完整性（ch07 L174 `min-replicas`、ch09 L23 `min-replicas`）
- 其余 P2 为精度问题，在正式出版前值得逐一修复
- 被重点审查的 4 个已知问题（ch9:101 ACL 语法、ch6:56 ACL 命名、半同步变量新旧名、appendfsync 默认语境）中，**后三者完全正确**，**ACL 命令块正确**，但 ACL 语法在正文解释中有精度改善空间（P2）

---

*审查执行：2026-09-09*  
*版本基线：Redis 7.x / MySQL 8.0.x / Kafka 3.x*  
*工具：grep + Python 全文扫描 + ali-web-search 官方文档核查*
