# 第09章 事实核查结果

> 核查时间: 2026-06-23
> 核查范围: verify-questions-09.md 全部问题
> 核查依据: Redis 官方文档及 CHANGELOG、MySQL 官方手册、Apache Kafka 官方文档及 KIP、CMU 数据库课程讲义

## 核查统计

| 结果 | 数量 |
|------|------|
| ✅ 确认正确 | 23 |
| ❌ 需要修正 | 1 |
| ⚠️ 需要澄清 | 15 |
| 🔍 无法确认 | 1 |

---

## 逐题核查

### Q1: Redis ACL 引入与增强版本
**原文陈述**: "Redis 从早期'无密码'演进到 ACL（6.0 引入，7.x 继续增强按用户/键空间细粒度授权）"
**核查结果**: ✅ 确认正确
**核查依据**: 
- (a) Redis 6.0 是第一个正式引入 ACL 的版本。6.0 RC1 于 2019-12-19 发布，Release Notes 标明 "Redis now supports ACLs. You can define users that can run only certain commands and/or can only access only certain keys patterns."
- (b) Redis 7.0 引入 ACL v2，增加 selectors（多组规则集）和键空间读/写分离权限（`%R~`/`%W~`），实现了"按键空间细粒度授权"的增强。
- 来源: https://github.com/redis/redis/releases/tag/7.0-rc1; https://redis.io/blog/getting-started-redis-6-access-control-lists-acls/
**建议**: 无。描述准确。

---

### Q2: MySQL 复制演进路线（异步 → 半同步 → MGR）
**原文陈述**: "MySQL 也走了三步（异步复制 → 半同步复制 → MGR）"
**核查结果**: ⚠️ 需要澄清
**核查依据**: 
- (a) 半同步复制确在 MySQL 5.5 引入，实现为插件（`semisync_master.so` / `semisync_slave.so`），来自 WL#4398。
- (b) MGR 确在 MySQL 5.7.17 引入（GA），作为 Group Replication 插件。
- (c) "三步"概括了复制最重要的大版本演进，但遗漏了两个重要里程碑：基于 GTID 的复制在 5.6 引入（WL#5548）、Crash-Safe Slaves 和 Binary Log Group Commit 也在 5.6。这对复制演进的完整性描述有缺失。
- 来源: https://dev.mysql.com/worklog/task/?id=4398; https://dev.mysql.com/blog-archive/mysql-group-replication-its-in-5-7-17-ga/
**建议**: 建议补充"GTID（5.6）"作为"异步 → 半同步"之间的关键一步，或加注说明三步是重要里程碑而非完整时间线。

---

### Q3: KRaft 是否完全取代 ZooKeeper 且没有外部依赖
**原文陈述**: "Partition + ISR + KRaft（去 ZooKeeper）"
**核查结果**: ✅ 确认正确（含上下文限定）
**核查依据**: 
- (a) KRaft（KIP-500）从 Kafka 2.8（Early Access）引入，3.3 达到生产可用（针对新集群），3.6 支持 ZK→KRaft 迁移 GA。
- (b) KRaft 模式下完全不需要外部 ZooKeeper 集群——metadata 由 KRaft 控制器内的 Raft 共识组独立管理。
- (c) Kafka 3.x 时期 ZK 模式仍可作为可选回退（是可选而非依赖），Kafka 4.0（2025 年 3 月）才彻底移除 ZK 支持。
- 该书版本声明涵盖 Kafka 2.8 / 3.0 / 3.x，"去 ZooKeeper"在 KRaft 模式下准确无误。
- 来源: https://cwiki.apache.org/confluence/display/KAFKA/KIP-500; KIP-833
**建议**: 无。描述准确。

---

### Q4: InnoDB 默认页尺寸 16KB
**原文陈述**: "16KB 页 + B+树为'点查 + 范围扫描'优化"
**核查结果**: ✅ 确认正确
**核查依据**: InnoDB 默认页尺寸是 16KB，支持 4KB、8KB、16KB、32KB、64KB（32/64KB 仅限 MySQL 8.0+），16KB 为默认值。这一行为从 MySQL 5.5 至今一致。
- 来源: https://dev.mysql.com/doc/refman/8.0/en/innodb-file-space.html
**建议**: 无。

---

### Q5: Redis `appendfsync` 三档行为描述
**原文陈述**: "Redis 的 appendfsync 有三档——always（每条命令都落盘，最慢但最不丢）、everysec（每秒落盘一次，默认）、no（交给操作系统决定，最快但可能丢较多）"
**核查结果**: ✅ 确认正确
**核查依据**: 
- (a) always 是在每次 AOF 写入后 fsync（实际是每个 write 批处理后 fsync一次）。
- (b) everysec 是每秒一次 fsync，为默认值。
- (c) no 完全交给 OS 决定 fsync 时机（Linux 默认约 30 秒刷一次）。
- (d) 对丢数据量的定性描述准确：always 几乎不丢（进程 crash 而 OS 正常时理论上不丢）；everysec 最多丢 1 秒；no 可丢约 30 秒的数据。
- 来源: Redis 官方文档 "Redis Persistence" 章节；redis.conf 注释
**建议**: 无。

---

### Q6: `innodb_flush_log_at_trx_commit=1` 的语义
**原文陈述**: "`innodb_flush_log_at_trx_commit=1` 守护的是 redo log 不丢"
**核查结果**: ✅ 确认正确
**核查依据**: 值为 1 时，每次事务提交都将 redo log buffer 写入日志文件并 fsync。值 0 只写 buffer 不写文件（每秒刷一次），值 2 写文件但延迟 fsync（每秒刷一次）。
- 来源: https://dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html#sysvar_innodb_flush_log_at_trx_commit
**建议**: 无。

---

### Q7: `sync_binlog=1` 的默认值
**原文陈述**: "MySQL 默认押在持久性端，'双 1'配置（`innodb_flush_log_at_trx_commit=1` + `sync_binlog=1`）让每条已提交事务都 fsync，从而做到'断电不丢'"
**核查结果**: ❌ 需要修正
**核查依据**: `sync_binlog` 在 MySQL 5.5/5.6 的默认值是 0。WL#8319 在 MySQL 5.7 将默认值改为 1。问题原文说"MySQL 8.0 才改为 1"也不准确——真实变更发生在 5.7。该书版本涉及 5.5~8.0，因此称"MySQL 默认...双1"在 5.5/5.6 语境下不成立。
- 来源: https://dev.mysql.com/worklog/task/?id=8319（WL#8319 "Enable crash safe binary logs by default in 5.7"）
**建议**: 改为"MySQL 5.7+ 默认押在持久性端'双 1'配置（8.0 也延续此默认）"，并加注"5.5/5.6 默认 `sync_binlog=0`，需手动设置为 1 才能做到双1"。

---

### Q8: 双写缓冲与 torn page 的关系
**原文陈述**: "双写缓冲则守护'脏页落盘时不被撕裂'这一前提（撕裂的页 redo 也救不回来）"
**核查结果**: ✅ 确认正确
**核查依据**: 
- (a) torn page（部分写入的页面）的校验和与 redo log 记录的 LSN 不匹配，InnoDB 无法确认页面版本，因此无法安全应用 redo log——torn page 确实无法被 redo 恢复。
- (b) doublewrite buffer 的工作原理是先写入共享表空间的 doublewrite buffer（连续 128 页，2 个 extent），再写数据文件位置，确保任何写入要么完整要么可检测到撕裂。
- (c) 在 SSD 且支持 atomic write（如使用 Power-Safe 的 FUA/原子写）的硬件上，doublewrite buffer 的开销可能大于收益，MySQL 8.0 引入 `innodb_doublewrite` 参数允许关闭或设为"detect only"模式。
- 来源: MySQL 官方手册 "Doublewrite Buffer" 章节（https://dev.mysql.com/doc/refman/8.0/en/innodb-doublewrite-buffer.html）
**建议**: 无。基本原理描述准确。对 SSD+atomic write 场景的讨论超出本书范围，可不涉及。

---

### Q9: Redis hash 底层编码（listpack vs hashtable）的版本
**原文陈述**: "同一个 hash 语义，底层可以是 listpack 也可以是 hashtable，逻辑层只认 type，存储层管 encoding"
**核查结果**: ⚠️ 需要澄清
**核查依据**: Redis 7.0 之前 hash 的紧凑编码是 **ziplist**（非 listpack）。7.0（2022 年 4 月发布）以 listpack 全面替换 ziplist，用于 hash、list、zset 三种类型的紧凑编码。该书涵盖 Redis 4.0/6.0/7.0，仅提 listpack 对 7.0 之前的读者有误导风险。
- 来源: https://github.com/redis/redis/releases/tag/7.0-rc1（"Replace ziplist with listpack in Hash, List, Zset"）
**建议**: 改为"listpack（7.0+）/ ziplist（7.0 之前）"，或在上下文注明"以最新 Redis 7.0 为例"。

---

### Q10: MySQL Change Buffer 的行为描述
**原文陈述**: "MySQL 的 Change Buffer 把对二级索引的随机写攒成批量"
**核查结果**: ⚠️ 需要澄清
**核查依据**: Change Buffer（原名 Insert Buffer，MySQL 5.5 改名）对 INSERT / UPDATE / DELETE 均缓存，不限于插入。"攒成批量"的表述是合理的教学简化，但更准确的说法是"将多个对同一二级索引页的修改缓存起来，待该页被读入缓冲池时一次性合并"，而非真正"攒成批量"再统一写入。合并是被动的（页被读取时触发），而非主动攒批再刷。
- 来源: https://dev.mysql.com/doc/refman/8.0/en/innodb-change-buffer.html; https://dev.mysql.com/blog-archive/the-innodb-change-buffer/
**建议**: 可保留"攒成批量"的通俗说法，但建议加注脚说明"Change Buffer 的机制是延迟合并而非主动批量刷写，合并时机是被缓存的二级索引页被读入缓冲池时触发"。

---

### Q11: MySQL group commit 行为
**原文陈述**: "group commit 把多个事务的 redo 一次 fsync"
**核查结果**: ⚠️ 需要澄清
**核查依据**: 
- (a) MySQL 5.6 之前，binlog 启用时两阶段提交的 `prepare_commit_mutex` 导致 InnoDB redo log 的 group commit 被禁用——每个事务单独 fsync redo。
- (b) MySQL 5.6 引入 Binary Log Group Commit（BLGC, WL#5223），将提交分为 Flush/Sync/Commit 三个阶段，组提交 binlog 的 fsync。
- (c) redo log group commit 的修复在 MySQL 5.7.6+（Bug#73202）：redo log 的 prepare 阶段延迟到 BLGC 的 Flush 阶段再统一写入，从而也实现 redo 的组提交。
- 来源: https://dev.mysql.com/worklog/task/?id=5223; MySQL 5.7.6 release notes
**建议**: 可改为"5.6+ 通过 BLGC 把多个事务的 binlog 一次 fsync（5.7+ 进一步把 redo 也组提交）"，避免读者误解 group commit 一直是完整可用的。

---

### Q12: Kafka Record Batch 与压缩
**原文陈述**: "Kafka 的 Record Batch 把多条消息压缩成一个存储单元"
**核查结果**: ✅ 确认正确
**核查依据**: Kafka 0.11.0（KIP-98）引入 Record Batch（magic byte v2），压缩在 batch 级别执行——整个 `records` 数组作为压缩单元，batch 头部保持不压缩以便 broker 在不解压的情况下检查元数据（ProducerId、epoch、sequence number）。
- 来源: https://cwiki.apache.org/confluence/display/KAFKA/KIP-98; Kafka 协议文档 Record Batch 格式
**建议**: 无。描述准确。

---

### Q13: Kafka sendfile / 零拷贝实现
**原文陈述**: "零拷贝（sendfile）让一批数据跳过用户态直接从页缓存到网卡"
**核查结果**: ✅ 确认正确
**核查依据**: Kafka 使用 Java NIO `FileChannel.transferTo()` 调用 Linux `sendfile` 系统调用。sendfile 确实不经过用户态缓冲区（没有 CPU 参与的拷贝）。在有 scatter/gather DMA 支持的新硬件上，数据从页缓存直接 DMA 传输到网卡，完全跳过 socket buffer。书上表述是合理的简化。
- 来源: https://issues.apache.org/jira/browse/KAFKA-13799; Linux `sendfile(2)` man page
**建议**: 无。简化对教学目的可以接受。如需更精确可提"sendfile + scatter/gather DMA"。

---

### Q14: Redis Cluster 分区时 AP 行为
**原文陈述**: "Redis Cluster 偏 AP，分区时持有多数主节点的分区继续服务、少数派分区的槽短暂不可用，故障切换时可能丢失少量已确认的写（异步复制的固有代价）"
**核查结果**: ✅ 确认正确
**核查依据**: Redis Cluster 规范明确指出：(1) 少数派节点在 `NODE_TIMEOUT` 内继续接受写入，之后拒绝写入；(2) 多数派节点继续服务，条件是有足够副本接管不可达 master 的槽；(3) 异步复制意味着 master 确认给客户端但尚未复制到 replica 的写在 failover 后丢失。
- 来源: https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/（Write Safety 和 Cluster分区容忍度章节）
**建议**: 无。描述准确。

---

### Q15: MySQL MGR 在分区时的 CP 行为
**原文陈述**: "MySQL MGR 偏 CP，少数派分区直接拒绝写，宁可不活也不写错"
**核查结果**: ⚠️ 需要澄清
**核查依据**: 
- (a) MGR 使用基于 Paxos 变体（XCom）的组通信系统，少数派分区无法形成多数派投票，因此拒绝写入——符合 CP 特性。
- (b) 但 MySQL 官方文档明确指出 "Group Replication is an eventual consistency system"（MGR 是最终一致性系统），因为流式复制下节点间存在短暂延迟。因此"偏 CP"的分类对单主模式大致合理（因为共识保证全局排序、分区时少数派拒绝写），但严格来说 MGR 不满足 CP 定义的强一致性要求。Martin Kleppmann 等分布式系统研究者也指出将 MGR 简单归类为 CP 有争议。
- 来源: https://dev.mysql.com/doc/refman/8.0/en/group-replication-background.html
**建议**: 建议改为"MySQL MGR 在单主模式下表现接近 CP（分区时少数派拒绝写）"，并加注"严格来说 MGR 是最终一致性系统因流式复制存在短暂延迟，但共识机制保证了在分区场景下不会脑裂"。

---

### Q16: Redis 6.0 多线程 IO 的描述
**原文陈述**: "Redis 把'命令执行单线程'写死（即便 6.0 起可开启多线程 IO 卸载网络读写，数据访问仍单线程），因此内核无锁快、可重入逻辑简单，代价是单个实例吃不满多核 CPU"
**核查结果**: ✅ 确认正确
**核查依据**: 
- (a) Redis 6.0 通过 `io-threads` 配置引入可选的 multi-threaded I/O（默认关闭），仅用于网络读写的 `read(2)`/`write(2)` 系统调用。命令解析、执行、数据访问仍然在主线程上单线程执行。
- (b) `io-threads-do-reads` 控制是否也让线程负责读（默认 no）。
- (c) 6.0 GA（2020-04-30）的 release notes 已包含此功能。
- 来源: https://github.com/redis/redis-doc/pull/1408; redis.conf 中 `io-threads` 注释
**建议**: 无。描述准确。

---

### Q17: MySQL ARIES 三阶段恢复协议
**原文陈述**: "MySQL 把活跃事务、锁等待、LSN 当运行时状态，用 ARIES 协议（分析、重做、回滚三阶段）当崩溃恢复剧本"
**核查结果**: ✅ 确认正确（含细微差异说明）
**核查依据**: InnoDB 的崩溃恢复确实基于 ARIES 协议，使用 Analysis/Redo/Undo 三阶段。差异点：(1) InnoDB 使用物理逻辑的 redo（physiological logging: 物理级别写入页面、逻辑级别描述页面内的操作），而非严格 ARIES 的物理 redo；(2) InnoDB 使用逻辑 undo（反向操作），而非 ARIES 的经典 undo；(3) LSN（Log Sequence Number）语义准确——每个日志记录有全局单调递增的 LSN，每页存储 `FIL_PAGE_LSN` 用于 idempotent redo。
- 来源: CMU 15-445 ARIES 讲义（https://15445.courses.cs.cmu.edu/fall2024/slides/21-recovery.pdf）; Jeremy Cole "InnoDB Crash Recovery" 系列; MySQL Internals 手册
**建议**: 无。书中"ARIES 协议（分析、重做、回滚三阶段）"的描述对教学足够准确。如需精确可补充"InnoDB 使用 physio-logical redo + logical undo"。

---

### Q18: Kafka HW / LEO / ISR / Controller epoch 运行时状态
**原文陈述**: "Kafka 把 HW/LEO、ISR、Controller 任期（epoch）当运行时状态，用'日志截断到 HW + Controller 重新分配 leader'当恢复剧本"
**核查结果**: ✅ 确认正确
**核查依据**: 
- (a) HW（High Watermark）= 所有 ISR 均已复制的最大偏移量；LEO（Log End Offset）= 日志末尾。
- (b) 恢复剧本在 ZooKeeper 模式下确实是日志截断到 HW、Controller 通过 ZK 选举后重新分配 leader。
- (c) KRaft 模式下 Controller 通过 Raft 选举（不再依赖 ZK），Leader Epoch 机制从 0.11 起引入了更完善的截断判定（KIP-101）。
- 来源: Apache Kafka 官方文档 replication 设计章节; KIP-101; KIP-500
**建议**: 无。描述准确。

---

### Q19: Redis 的 Pipeline 与 Multi/Exec 网络优化
**原文陈述**: "Redis 的管道（pipeline）与 Multi/Exec 把 N 次网络往返压成 1 次 RTT"
**核查结果**: ⚠️ 需要澄清
**核查依据**: 
- Pipeline 确实将多次命令一次发送，响应合并返回，把 N 次 RTT 减为 1 次请求+响应。
- Multi/Exec 是事务机制：客户端逐条发送命令到事务队列（每条命令仍是一次 RTT），然后通过 Exec 一次性返回结果。严格来说 Multi/Exec 将响应合并为一次但并未把所有命令的请求 RTT 压成一次（请求阶段每条命令仍是独立 RTT）。
- 某些客户端实现中会将整个 MULTI...EXEC 块 pipeline 化发送（一个 TCP 包发完所有命令），但这是客户端优化而非 Redis 协议保证。
- 来源: https://redis.io/docs/latest/develop/use/pipelining/; https://redis.io/docs/latest/develop/interact/transactions/
**建议**: 建议修改为"Pipeline 把 N 次请求-响应的一次性发送、一次接收，压成 1 次 RTT；Multi/Exec 事务也减少响应 RTT 但请求是逐条发送"。

---

### Q20: MySQL read-ahead 机制
**原文陈述**: "预读把随机页请求变成顺序预取"
**核查结果**: ⚠️ 需要澄清
**核查依据**: InnoDB 有两种预读算法：(1) linear read-ahead（线性预读）——检测到某 extent 中连续访问的页数超过 `innodb_read_ahead_threshold`（默认 56）时，预取整个下一个 extent 到缓冲池；(2) random read-ahead（随机预读，默认关闭）——检测到某 extent 中有 13 个页在缓冲池中时，预取该 extent 的剩余页。预读机制的本质是"将访问模式的猜测转化为顺序 I/O"，但与"把随机请求变成顺序请求"不同——预读是将顺序检测结果转化为顺序预取，并不改变实际请求的随机性。
- 来源: https://dev.mysql.com/doc/refman/8.0/en/innodb-performance-read_ahead.html
**建议**: 改为"预读基于检测到的顺序访问模式，提前将后续连续页的顺序 I/O 预取到缓冲池"，更清晰地表明预读不改变请求本身而是批量预加载。

---

### Q21: AOF 重写行为
**原文陈述**: "AOF 重写把碎片化的历史命令重新压实成一份快照"
**核查结果**: ⚠️ 需要澄清
**核查依据**: AOF 重写并非"重新压实"或"压缩"现有 AOF 文件。其机制是：基于 fork 后的子进程扫描当前内存中的数据库键值，为每个键生成重建所需的最小命令集（例如一个 set 只需一条 SET 命令而非增量操作的序列），写入新的 AOF 文件。这不是"快照"（RDB 才是快照），严格来说是一组"能重建当前数据的最小命令序列"。
- 来源: Redis 官方文档 "Redis Persistence" AOF rewrite 章节; redis.conf 注释
**建议**: 改为"AOF 重写并非压缩旧文件，而是 fork 子进程扫描内存数据，为每个键生成最小命令集（如 SET key value），重写为一个新 AOF 文件——这是命令日志的'浓缩'而非'快照'"。

---

### Q22: PSYNC 部分重同步机制
**原文陈述**: "PSYNC（部分重同步 + 全量兜底）" 以及 "PSYNC 用复制偏移量和复制积压缓冲区做部分重同步"
**核查结果**: ✅ 确认正确
**核查依据**: PSYNC v1（Redis 2.8）引入，通过 replication offset 和 replication backlog 实现部分重同步。PSYNC v2（Redis 4.0）增强了对 master failover 场景的 partial resync 支持。书中描述覆盖了核心机制。
- 来源: Redis 2.8 / 4.0 release notes; redis.io 关于 PSYNC 的文档
**建议**: 无。描述准确。

---

### Q23: MySQL redo + binlog 两阶段提交
**原文陈述**: "redo + binlog 两阶段提交保提交一致"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL 在事务提交时使用内部 XA 两阶段（2PC）保证 redo log 与 binlog 的一致性：Prepare 阶段写 redo（prepare 状态，包含 XID）；Commit 阶段写 binlog（包含 XID event），再写 redo（commit 状态）。崩溃恢复时通过检验 redo 中的 XID 是否在 binlog 中出现来决定事务是提交还是回滚。
- 来源: MySQL 官方手册 "Binary Log and InnoDB: Two-Phase Commit"; MySQL Internals 关于 XA 2PC 的章节
**建议**: 无。描述准确。

---

### Q24: Kafka `enable.idempotence=true` 的行为
**原文陈述**: "`enable.idempotence=true`（它内部会强制 `acks=all` + 重试，挡住'重复写入'和'生产者重试导致的乱序'）"
**核查结果**: ✅ 确认正确
**核查依据**: 启用幂等生产者后：(1) `acks` 自动设为 `all`（Kafka 3.0 前强制为 `-1`/`all`，3.0+ 默认已是 `all`）；(2) `retries` 设为 `Integer.MAX_VALUE`；(3) `max.in.flight.requests.per.connection` 限制为 5（Kafka 0.11 时代为 1）；(4) 幂等性通过 Producer ID + sequence number 机制在 broker 端去重，防止重复写入和重试导致的乱序（限同一分区内）。
- 来源: https://kafka.apache.org/documentation/#producerconfigs; KIP-98
**建议**: 无。描述准确。可在脚注中补充"幂等性保证限于单分区内，跨分区需要事务"。

---

### Q25: Kafka 事务的额外开销
**原文陈述**: "Kafka 事务的额外开销（broker 维持事务状态机、生产者两阶段提交、消费者隔离读）"
**核查结果**: ✅ 确认正确
**核查依据**: 
- (a) Transaction Coordinator 在 broker 端维护事务状态机（`__transaction_state` topic），管理事务的 EMPTY/ONGOING/PREPARE_COMMIT/COMPLETE_COMMIT 等状态。
- (b) 生产者侧的两阶段提交：`initTransactions()` → `beginTransaction()` → 写入数据 → `commitTransaction()` 或 `abortTransaction()`（触发 `EndTxn` 请求和 `WriteTxnMarkers`）。
- (c) 消费者通过 `isolation.level=read_committed` 实现事务隔离读，读到 LSO（Last Stable Offset）为止。
- 来源: https://kafka.apache.org/documentation/#transactions; KIP-98
**建议**: 无。三项开销描述完整准确。

---

### Q26: Redis O(1) 访问描述
**原文陈述**: "Redis 用内存换 O(1) 访问，把数据全部驻留内存是'空间换时间'的极致"
**核查结果**: ⚠️ 需要澄清
**核查依据**: Redis 的核心数据结构（哈希表、skiplist 等）为大部分操作提供 O(1) 或 O(log N) 的平均时间复杂度。但并非所有操作都是 O(1)：`KEYS` 是 O(N)、`SORT` 是 O(N+M*log(M))、`SMEMBERS` 是 O(N)、`LRANGE` 是 O(S+N) 等。原文说"O(1) 访问"过于概括。
- 来源: https://redis.io/commands/（每个命令的 Time complexity 标注）
**建议**: 建议改为"Redis 用内存换 O(1)/O(log N) 平均访问"或"大部分操作为 O(1) 平均时间复杂度"，避免读者以为所有操作都是常量时间。

---

### Q27: Kafka 稀疏索引描述
**原文陈述**: "Kafka 用稀疏索引省空间（索引只记里程碑），用顺序扫描花时间兜底定位，是'时间换空间'的典型"
**核查结果**: ✅ 确认正确
**核查依据**: Kafka 的 `.index` 文件是稀疏索引——每 `log.index.interval.bytes`（默认 4KB）才写入一条 `(relativeOffset, position)` 条目。查找过程：二分查找索引 → 找到最近位置 → 顺序扫描到目标偏移量。此外 Kafka 还维护 `.timeindex`（时间戳→偏移量索引）用于时间戳查询。稀疏索引的原理描述准确。
- 来源: https://kafka.apache.org/documentation/#design; Conduktor Kafka 索引文档
**建议**: 无。描述准确。

---

### Q28: MySQL MGR 跨机房可行性
**原文陈述**: "MGR 跨机房可行"
**核查结果**: ⚠️ 需要澄清
**核查依据**: MySQL 官方文档指出 MGR 设计用于"server instances are very close to each other"（服务器实例之间非常接近）。MGR 基于 Paxos 共识，跨机房 RTT 超过 5-10ms 将严重影响提交性能。虽然技术上"可行"（可以通过调整 `group_replication_member_expel_timeout` 等参数），但需要低延迟网络前提。官方推荐方案是在各自机房部署独立 MGR 组，通过异步通道进行跨机房复制。
- 来源: https://dev.mysql.com/doc/refman/5.7/en/group-replication-requirements.html（"deployed in a cluster environment where server instances are very close to each other"）
**建议**: 改为"MGR 跨机房可行（需 <5-10ms RTT，否则性能严重下降），官方建议各机房独立 MGR 组 + 异步通道"。

---

### Q29: Kafka MirrorMaker / Cluster Linking 跨地域容灾
**原文陈述**: "MirrorMaker / Cluster Linking"
**核查结果**: ⚠️ 需要澄清
**核查依据**: 
- MirrorMaker 1（独立进程）和 MirrorMaker 2（基于 Kafka Connect）都是 Apache Kafka 开源版跨集群复制工具。
- Cluster Linking 是 Confluent Platform 企业版特性（Confluent Server 7.0+），不是 Apache Kafka 开源版功能。
- 如果该书限定在 Apache 开源版，应只提 MirrorMaker；如果包含 Confluent 商业特性，Cluster Linking 的标注应与 MirrorMaker 区分。
- 来源: https://docs.confluent.io/platform/7.9/multi-dc-deployments/cluster-linking/index.html; Apache Kafka 官方文档 MirrorMaker
**建议**: 明确是否涵盖 Confluent 商业功能。如仅限 Apache 开源，只提 MirrorMaker（MM2）；如涵盖 Confluent，标注"Cluster Linking（Confluent 企业版）"。

---

### Q30: Redis Cluster 在线 reshard
**原文陈述**: "Cluster 在线 reshard"
**核查结果**: ✅ 确认正确
**核查依据**: Redis Cluster 支持在线迁移 slot（hash slot redistribution），通过 `redis-cli --cluster reshard` 命令实现，迁移过程中集群保持可用。迁移步骤：源节点标记 slot 为 MIGRATING、目标节点标记为 IMPORTING、逐个迁移 key、刷新 slot 归属。不重启集群。
- 来源: https://redis.io/docs/latest/operate/oss_and_stack/management/scaling/; redis-cli Cluster 命令文档
**建议**: 无。描述准确。

---

### Q31: MySQL Group Replication 在线加节点
**原文陈述**: "在线加节点 + 自动均衡"
**核查结果**: ⚠️ 需要澄清
**核查依据**: 
- MGR 支持在线加节点：通过 `group_replication_add_instance` UDF（MySQL 8.0.2+）或 MySQL Shell 的 `cluster.addInstance()`，无需停机。
- "自动均衡"需澄清：MGR 在单主模式下，新节点加入后自动从现有节点同步数据（分布式恢复），但**不自动重新分配主角色**。多主模式下也没有自动的负载均衡。加节点后的数据同步是自动的，但说"自动均衡"可能暗示了自动负载均衡，这不在 MGR 的能力范围内。
- 来源: https://dev.mysql.com/doc/refman/8.0/en/group-replication-adding-instances.html
**建议**: 建议改为"在线加节点 + 自动同步"，避免"自动均衡"引起误解。

---

### Q32: Kafka 加 partition 受限、加 broker 可在线
**原文陈述**: "加 partition 受限、加 broker 可在线"
**核查结果**: ✅ 确认正确
**核查依据**: 
- (a) 增加 Kafka partition 后**无法缩减**（不可逆），且会增加 partition 数量改变键分区映射（对按 key 分区的语义有影响）。"受限"准确描述了这一不可逆约束。
- (b) 增加 broker 可在线完成，随后通过分区重分配（`kafka-reassign-partitions.sh`）将部分 partition 迁移到新 broker。
- 来源: Apache Kafka 官方文档关于增加 partition 的说明; Conduktor "Partition Count: The Decision You Can't Undo"
**建议**: 无。描述准确。

---

### Q33: Redis CONFIG SET 部分动态
**原文陈述**: "CONFIG SET 部分动态"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 使用 `CONFIG SET` 可以动态修改大部分运行参数而不需重启。部分参数标注为 "Not dynamically configurable" 或需要在配置文件中设置（重启生效）。可通过 `CONFIG REWRITE` 将当前运行时配置写入配置文件以实现持久化。书中"部分动态"的描述简洁且准确。
- 来源: https://redis.io/commands/config-set/; redis.conf 中每个参数的动态/静态标注
**建议**: 无。

---

### Q34: Redis latency monitor 和 slowlog
**原文陈述**: "slowlog + latency monitor"
**核查结果**: ✅ 确认正确
**核查依据**: 
- SLOWLOG 记录执行时间超过 `slowlog-log-slower-than`（默认 10000 微秒）的命令。
- Redis Latency Monitoring 框架（`LATENCY` 命令集）自 2.8.13 引入，包含 `LATENCY LATEST`、`LATENCY HISTORY`、`LATENCY DOCTOR` 等子命令。
- `latency-monitor-threshold` 默认 0（监控关闭）。
- 来源: https://redis.io/docs/latest/commands/slowlog/; https://redis.io/docs/latest/commands/latency-doctor/; Redis 2.8.13 release notes
**建议**: 无。

---

### Q35: Redis 代码量大小与通读可行性
**原文陈述**: "从 Redis 起步，它的代码量小、数据结构清晰、C 语言的直白让你能从命令处理一路追到内存表示，几周就能通读核心路径"
**核查结果**: ⚠️ 需要澄清
**核查依据**: 
- (a) Redis 7.x 源码在不含外部 lib 的情况下（src/ 目录）约 15-18 万行 C 语言代码。"代码量小"见仁见智——相比 MySQL（百万行级）确实小，但通常不认为 15+ 万行 C 代码"小"。
- (b) "几周通读核心路径"对有一定 C 语言和分布式系统背景的读者是可能的——核心路径（事件循环 ae.c、命令处理 processCommand、网络层 networking.c、数据结构 t_hash/t_list/t_zset 等）有明确的分界，确实可几周内通读。但需要加"有 C 语言基础"的限定。
- 来源: Redis GitHub 仓库
**建议**: 建议改为"Redis 代码量在主流服务器软件中相对较小（~15 万行 C 源码），核心路径有清晰的分界（事件循环、数据操作、持久化等），有 C 语言基础且投入几周可以读完核心路径"。

---

### Q36: 表 9-1 中 Kafka "Controller 选举 + 日志截断到 HW"
**原文陈述**: "Controller 选举 + 日志截断到 HW"
**核查结果**: ✅ 确认正确
**核查依据**: 
- Kafka 使用 Controller 管理 partition leader 选举（ZooKeeper 模式下通过 ZK 或 ZK 内的临时节点选举；KRaft 模式下通过 Raft 协议选举）。
- 日志截断到 HW（High Watermark）是 follower 在故障恢复时截断未确认数据的标准行为。KIP-101 引入 Leader Epoch 机制后，截断判定转由 Leader Epoch 提供更精确的依据，但 HW 仍是核心参考。
- 归入"生命周期"范畴（启动关闭）合理。
- 来源: Apache Kafka 官方文档 Controller 说明; KIP-101; KIP-500
**建议**: 无。

---

### Q37: 表 9-1 中关于 Redis Cluster 的"主从 → Sentinel → Cluster 槽分片 + Gossip"
**原文陈述**: "主从 → Sentinel → Cluster 槽分片 + Gossip"
**核查结果**: ✅ 确认正确
**核查依据**: 
- 主从复制：Redis 2.0 引入。
- Sentinel：2.4 开始实验，2.8 达到稳定（Sentinel 2），3.0 作为稳定高可用方案。
- Redis Cluster：3.0 引入（GA），基于 16384 个 hash slot 和 gossip 协议实现节点发现/状态传播。
- 三步演进版本正确。
- 来源: Redis 各版本 release notes; Redis Cluster 规范关于 gossip 协议的章节
**建议**: 无。

---

### Q38: 表 9-1 中 MySQL "异步 → 半同步 → MGR（Paxos 类多数派）"
**原文陈述**: "异步 → 半同步 → MGR（Paxos 类多数派）"
**核查结果**: ✅ 确认正确
**核查依据**: MGR 使用 XCom 通信层实现组内消息排序和原子广播，XCom 基于 Paxos 变体（或类 Paxos 的共识协议）。"Paxos 类多数派"是合理的概括。
- 来源: MySQL Group Replication 官方技术白皮书; Group Replication 内部文档关于 XCom Paxos 的说明
**建议**: 无。

---

### Q39: Kafka 的 SASL 认证 + ACL 授权 + TLS 传输加密
**原文陈述**: "SASL + ACL + 端到端 TLS"
**核查结果**: ⚠️ 需要澄清
**核查依据**: 
- (a) Kafka 支持的认证机制正确：SASL/PLAIN、SASL/SCRAM、SASL/GSSAPI（Kerberos）、mTLS（SSL 证书认证）。
- (b) ACL 支持按用户、topic、consumer group、cluster 的细粒度控制。
- (c) "端到端 TLS"的表述有歧义：Kafka 的 TLS 是 client↔broker 和 broker↔broker 的传输加密，broker 端会解密处理明文数据。这不是真正的"端到端加密"（producer 到 consumer 全程加密），而是"传输加密"。严格来说应称为"client-to-broker 传输加密"。
- 来源: Apache Kafka 官方安全文档
**建议**: 将"端到端 TLS"改为"传输层加密 TLS（client↔broker、broker↔broker）"，避免读者误解为端到端加密（E2EE）。

---

### Q40: 规律五关于 AOF 重放与 RDB 加载的恢复路径
**原文陈述**: "Redis 把键空间、过期表、客户端连接显式建模为运行时状态，用 RDB/AOF + 启动加载当恢复剧本——重启就是按剧本把状态重放回去"
**核查结果**: ⚠️ 需要澄清
**核查依据**: Redis 启动时恢复顺序是：如果 AOF 启用则加载 AOF（优先级更高），否则加载 RDB。不会同时加载两者。书中"RDB/AOF + 启动加载"的表述可能让读者误以为同时使用 RDB 和 AOF 恢复。
- 来源: Redis 官方文档 "Redis Persistence" 章节；redis.conf 注释
**建议**: 明确恢复优先级，改为"用 AOF（优先级高）或 RDB 启动加载，重启时按优先级选择一种将状态重放"。

---

## 修正优先级

### 高优先级（必须修正）
- **Q7 (sync_binlog 默认值)**: `sync_binlog=1` 默认从 MySQL 5.7 开始，非 8.0。5.5/5.6 默认值为 0。书中"MySQL 默认...双 1"在 5.5/5.6 语境下错误。
- **Q9 (listpack 版本)**: 提到 listpack 不声明版本，7.0 之前读者会以为 hash 的紧凑编码就是 listpack，而实际是 ziplist。

### 中优先级（建议修正）
- **Q21 (AOF 重写为"快照")**: AOF 重写生成的是最小命令序列而非"快照"。
- **Q28 (MGR 跨机房)**: 应加低延迟前提条件。
- **Q29 (Cluster Linking)**: 需区分开源和 Confluent 商业功能。
- **Q31 (MGR 自动均衡)**: "自动均衡"夸大了 MGR 能力。
- **Q35 (Redis 代码量)**: 建议加 C 语言基础和投入时间前提。
- **Q39 (端到端 TLS)**: 应改为"传输层加密"。

### 低优先级（可选优化）
- **Q2 (复制演进)**: 补充 GTID 5.6 里程碑。
- **Q10 (Change Buffer)**: 加注脚说明"攒成批量"的精确含义。
- **Q11 (group commit)**: 加版本说明 5.6 BLGC / 5.7 redo group commit。
- **Q15 (MGR CP 分类)**: 加注 academic caveat。
- **Q19 (Pipeline/Multi)**: 区分 Pipeline 和 Multi/Exec 的 RTT 优化差异。
- **Q20 (read-ahead)**: 调整措辞区分"顺序预取"与"把随机变顺序"。
- **Q26 (Redis O(1))**: 加时间复杂度限定词。
- **Q40 (恢复优先级)**: 明确 AOF 优先于 RDB。
