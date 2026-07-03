# F03 命令可运行性审查报告

> 审查日期：2026-07-03
> 基线版本：Redis 7.x / MySQL 8.0.x / Kafka 3.x
> 审查范围：chapters/*/chapter.md（共 10 章）
> 审查方法：提取所有 backtick 内命令/参数 + 代码块，逐条对照基线版本官方文档

---

## 总览

| 指标 | 数量 |
|------|------|
| 提取到的命令/参数引用 | ~150 条 |
| 🔴 错误（基线版本不存在/语法错/默认值错） | 1 |
| 🟠 废弃/参数名变更（功能可用但已弃用） | 2 |
| 🟡 存疑（需作者核实版本细节） | 2 |
| ✅ 已核实正确 | ~145 条 |

---

## 🔴 错误

### 1. `aclfile` 默认值表述错误

- **位置**: `chapters/06-security/chapter.md` 第 46 行
- **原文**: "密码用 SHA-256 哈希存（通过 `ACL SAVE` 持久化到 `aclfile` 指定的文件，默认 `users.acl`；运行时改完可用 `ACL LOAD` 重新加载）"
- **问题**: Redis 7.x 中 `aclfile` 配置项的默认值是**空字符串（未启用）**，而非 `users.acl`。`redis.conf` 中 `aclfile /etc/redis/users.acl` 这一行是被注释掉的。当 `aclfile` 未设置时，ACL 规则通过 `ACL SAVE` 写回 `redis.conf` 本身，而不是写到 `users.acl`。
- **正确写法**: 删除"默认 `users.acl`"，可改为"如配置了 `aclfile` 则指该文件"或"常见设置为 `/etc/redis/users.acl`（非默认值）"
- **来源**: Redis 7.0 `redis.conf` 中 `aclfile` 默认注释掉（空字符串）

---

## 🟠 废弃（Deprecated but still functional in baseline）

### 1. `ZRANGEBYSCORE` 在 Redis 7.x 中已弃用

- **位置**: `chapters/01-introduction/chapter.md` 第 67 行
- **原文**: "对有序集合做 `ZADD` 和 `ZRANGEBYSCORE`"
- **问题**: `ZRANGEBYSCORE` 自 Redis 6.2.0 起已弃用，推荐替换为 `ZRANGE ... BYSCORE`。虽然在 7.x 中功能仍然完整可用，但属于弃用命令。
- **建议**: 可维持原状（无运行时错误），或补充说明该命令已弃用，或改用 `ZRANGE ... BYSCORE`
- **来源**: Redis 6.2 发布说明 + `ZRANGEBYSCORE` 文档标注 deprecated

### 2. `RANDOMKEY` 在复制场景的语义问题

- **位置**: `chapters/09-data-sync/chapter.md` 第 53 行
- **原文**: "比如非确定性命令（`SPOP`、`RANDOMKEY`、依赖时间的 Lua 脚本）"
- **问题**: `RANDOMKEY` 在 Redis 7.x 中仍然存在且功能正常。此处作为非确定性命令的例子列出，语法上无错误。标记为 🟠 仅作提示。

---

## 🟡 存疑

### 1. `min-replicas-max-lag` 的判定依据描述

- **位置**: `chapters/09-data-sync/chapter.md` 第 102 行
- **原文**: "注意：`master_repl_offset - replica_offset` 是字节进度差，用于 INFO 监控，不是 `min-replicas-max-lag` 的判定依据。'字节进度差'和'心跳时间'是两套不同度量。"
- **分析**: 书中指出 `min-replicas-max-lag` 基于心跳时间而非字节进度差，技术方向正确。官方文档中 `min-replicas-max-lag` 判定依据是副本最后一次 REPLCONF ACK 的时间。不作为硬错误，但细节可进一步精确。

### 2. `allow.everyone.if.no.acl.found` 的版本历史描述

- **位置**: `chapters/06-security/chapter.md` 第 133 行
- **原文**: "`allow.everyone.if.no.acl.found` 这个参数...从 1.x 起默认就是 false"
- **分析**: Kafka 1.x 时期该参数尚不存在（Kafka 0.9–2.0 初期默认行为是"无 ACL 则允许所有人"）。该参数是 2.0 附近引入，默认即 `false`。结论（3.x 默认 false）正确，但"从 1.x 起"的历史回溯不够精确。
- **建议**: 改为"该参数自引入起默认即为 `false`（当前 3.x 沿用）"。

---

## ✅ 已核实正确的关键命令/参数

### Redis 7.x 部分

| 命令/参数 | 章节 | 核实结论 |
|-----------|------|---------|
| `SET` | ch01 | ✓ 基础命令，7.x 存在 |
| `KEYS *` | ch01 | ✓ 存在（生产不推荐但语法有效） |
| `ZADD` | ch01 | ✓ 存在 |
| `LPUSH` / `BRPOP` | ch01 | ✓ 存在 |
| `XADD` / `XREAD` | ch01 | ✓ 存在 |
| `SHUTDOWN` / `SHUTDOWN SAVE` / `SHUTDOWN NOSAVE` | ch03 | ✓ 存在 |
| `BGSAVE` / `SAVE` | ch03 | ✓ 存在 |
| `REPLICAOF host port` / `REPLICAOF NO ONE` | ch03/ch07 | ✓ 5.0+ 标准语法，7.x 沿用 |
| `min-replicas-to-write` / `min-replicas-max-lag` | ch09 | ✓ 7.x 正确命名（已从 `min-slaves-*` 重命名） |
| `repl-backlog-size` | ch09 | ✓ 存在，默认 1MB |
| `appendfsync` (always/everysec/no) | ch04 | ✓ 存在，默认 everysec |
| `appendonly` | ch04 | ✓ 默认 no（RDB-only） |
| `maxmemory` | ch04 | ✓ 存在 |
| `maxmemory-samples` | ch04 | ✓ 存在，默认 5 |
| `lfu-log-factor` / `lfu-decay-time` | ch04 | ✓ 存在 |
| `noeviction` / `allkeys-lru` 等淘汰策略 | ch04 | ✓ 存在 |
| `aof-use-rdb-preamble` | ch04 | ✓ 5.x-6.x 默认 yes，7.0 已移除（书中已说明此变化） |
| `ACL SETUSER alice on >pwd ~keys:* +get +set` | ch06 | ✓ 语法正确（`~` 为键模式前缀，`>` 为设置密码） |
| `ACL SAVE` / `ACL LOAD` | ch06 | ✓ 存在 |
| `AUTH` | ch06 | ✓ 存在 |
| `protected-mode` | ch06 | ✓ 存在，默认 yes |
| `FLUSHALL` | ch06 | ✓ 存在 |
| `redis-check-aof --fix` | ch08 | ✓ 工具名正确，`--fix` 参数正确 |
| `redis-benchmark` | ch10 | ✓ 存在 |
| `CONFIG SET` | ch10 | ✓ 存在 |
| `SLOWLOG` | ch06 | ✓ 存在 |
| `ACL LOG` | ch06 | ✓ 存在（6.0+） |
| `INCR` | ch04 | ✓ 存在 |
| `SPOP` | ch09 | ✓ 存在 |
| `EXPIRE` / `EXPIREAT` / `PEXPIREAT` | ch09 | ✓ 存在 |
| `redis.replicate_commands()` | ch09 | ✓ Redis Lua API，存在 |
| `MGET` | ch07 | ✓ 存在 |
| `SELECT` | ch07 | ✓ 存在（Cluster 下受限，书中已说明） |
| `SLAVEOF` | ch03 | ✓ 作为旧名提及（5.0 后弃用） |
| default user ACL: `on nopass ~* &* +@all` | ch06 | ✓ 7.x 默认如此 |
| `ACL SETUSER default off` | ch06 | ✓ 存在 |
| `ACL SETUSER default resetpass` | ch06 | ✓ 存在 |
| `appendonlydir/` | ch08 | ✓ 7.0+ 多部 AOF 目录名正确 |
| `client-output-buffer-limit` | ch05 | ✓ 存在 |
| `tls-protocols` | ch06 | ✓ 存在（6.0+） |

### MySQL 8.0.x 部分

| 命令/参数 | 章节 | 核实结论 |
|-----------|------|---------|
| `innodb_flush_log_at_trx_commit` | ch01/ch04 | ✓ 存在，默认 1 |
| `sync_binlog` | ch01 | ✓ 存在，8.0 默认 1（5.7 默认 0） |
| `FLUSH PRIVILEGES` | ch03 | ✓ 存在，语法正确 |
| `SHOW PROCESSLIST` | ch03 | ✓ 存在 |
| `innodb_fast_shutdown` (0/1/2) | ch03 | ✓ 存在，默认 1 |
| `innodb_old_blocks_time` | ch04 | ✓ 存在，默认 1000ms |
| `innodb_page_size` | ch08 | ✓ 存在，默认 16KB |
| `innodb_default_row_format` | ch08 | ✓ 存在，默认 Dynamic |
| `innodb_redo_log_capacity` | ch08 | ✓ 存在（8.0.30+），默认 100MB |
| `innodb_redo_log_encrypt` / `innodb_undo_log_encrypt` | ch06 | ✓ 存在（8.0.1+） |
| `binlog_encryption` | ch06 | ✓ 存在（8.0.14+），默认 OFF |
| `rpl_semi_sync_source_enabled` | ch09 | ✓ 存在（8.0.26+ 新命名） |
| `rpl_semi_sync_source_timeout` | ch09 | ✓ 存在，默认 10000ms |
| `rpl_semi_sync_source_wait_for_replica_count` | ch09 | ✓ 存在，默认 1 |
| `caching_sha2_password` | ch06 | ✓ 8.0.4+ 默认认证插件 |
| `mysql_native_password` | ch06 | ✓ 作为旧插件提及 |
| `auth_socket` | ch06 | ✓ 存在 |
| `CREATE ROLE` | ch06 | ✓ 8.0+ RBAC 语法 |
| `GRANT role TO user` | ch06 | ✓ 8.0+ 语法 |
| `SET ROLE` | ch06 | ✓ 8.0+ 语法 |
| `REQUIRE SSL` / `REQUIRE X509` | ch06 | ✓ 存在 |
| `SUPER` / `PROCESS` / `FILE` / `RELOAD` | ch06 | ✓ MySQL 权限名 |
| `group_replication_consistency` | ch09 | ✓ MGR 参数 |
| `LOGICAL_CLOCK`（并行复制类型） | ch09 | ✓ 存在 |

### Kafka 3.x 部分

| 命令/参数 | 章节 | 核实结论 |
|-----------|------|---------|
| `acks=all`（3.0 起默认） | ch01/ch04 | ✓ KIP-679，3.0 起默认 |
| `min.insync.replicas` | ch01 | ✓ 存在，默认 1 |
| `controlled.shutdown.enable` | ch03 | ✓ 存在，默认 true |
| `controlled.shutdown.max.retries` | ch03 | ✓ 存在 |
| `controlled.shutdown.retry.backoff.ms` | ch03 | ✓ 存在 |
| `num.recovery.threads.per.data.dir` | ch03 | ✓ 存在 |
| `num.network.threads` | ch03 | ✓ 存在，默认 3 |
| `num.io.threads` | ch03 | ✓ 存在，默认 8 |
| `replica.lag.time.max.ms` | ch09 | ✓ 存在，默认 30000（30 秒） |
| `log.flush.interval.messages` / `log.flush.interval.ms` | ch04 | ✓ 存在 |
| `log.segment.bytes` | ch08 | ✓ 存在，默认 1GB |
| `log.roll.hours` | ch08 | ✓ 存在，默认 168（7 天） |
| `log.index.interval.bytes` | ch04/ch08 | ✓ 存在，默认 4KB |
| `batch.size` / `linger.ms` | ch02 | ✓ Kafka producer 参数 |
| `unclean.leader.election.enable` | ch07 | ✓ 存在，3.x 默认 false |
| `allow.everyone.if.no.acl.found` | ch06 | ✓ 存在，默认 false |
| `AclAuthorizer` / `StandardAuthorizer` | ch06 | ✓ 3.x 中均存在 |
| `listeners` / `listener.security.protocol.map` | ch06 | ✓ 存在 |
| `SASL_SSL` / `SASL_PLAINTEXT` / `SSL` | ch06 | ✓ 有效协议值 |
| `enable.idempotence` | ch09 | ✓ 存在，3.0 起默认 true |
| PRODUCE / FETCH / LIST_OFFSETS / METADATA | ch05 | ✓ Kafka API 正确枚举 |

---

## 重点验证项确认

以下为本书已知疑点的逐一核实结果：

### 1. `min-replicas-to-write` 在 Redis 7.x 的命名
**结论**: ✅ 正确。全书使用 `min-replicas-to-write`（而非 `min-slaves-to-write`），符合 Redis 5.0+ 的命名规范。7.x 继续使用此命名。

### 2. ACL `~keys:*` access selector 语法
**结论**: ✅ 正确。Redis 6.0+ ACL 语法中，`~` 是键模式前缀，`&` 是频道前缀。本书举例 `ACL SETUSER alice on >pwd ~keys:* +get +set` 语法完全正确。

### 3. 半同步变量新旧名
**结论**: ✅ 正确。书中明确指出 MySQL 8.0.26 起半同步变量从 `master/slave` 重命名为 `source/replica`，并正确给出映射。

### 4. `ZRANGEBYSCORE` 存在性
**结论**: 🟠 已弃用但功能完整。7.x 中仍然存在且功能正常。

---

## 总结

本书命令/参数覆盖范围广（约 150 条引用），整体准确率极高。发现的真实硬错误仅 1 处（`aclfile` 默认值描述为 `users.acl`，实际默认值为空字符串）。其余标注为存疑/废弃的 4 项均不产生运行时错误，仅涉及术语精度或版本历史细节。全书在"命令可运行性"维度上质量优秀，读者按照书中示例操作不会遇到命令不存在或语法错误的情况。
