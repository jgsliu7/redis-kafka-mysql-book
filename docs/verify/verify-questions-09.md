# 第09章《总结》事实核查问题清单

---

## 关于版型与版本引入的声明

- Redis 主版本：4.0 / 6.0 / 7.0
- MySQL 主版本：5.5 / 5.6 / 5.7 / 8.0
- Kafka 主版本：2.8 / 3.0 / 3.x

---

### Q1: Redis ACL 引入与增强版本
**章节位置**: 9.1.2 回扣第5章
**原文陈述**: "Redis 从早期'无密码'演进到 ACL（6.0 引入，7.x 继续增强按用户/键空间细粒度授权）"
**待确认点**: 确认 (a) Redis 6.0 确实是引入 ACL 的第一个版本；(b) Redis 7.x 确实在 ACL 上做了"按键空间细粒度授权"增强。6.0 的 ACL 是否已经支持按 key 空间授权（`~` 模式匹配），还是 7.x 才补全的。
**建议验证来源**: Redis 官方 CHANGELOG / release notes 6.0, 7.0, 7.2; redis.conf 文档

### Q2: MySQL 复制演进路线（异步 → 半同步 → MGR）
**章节位置**: 9.1.2 回扣第6章
**原文陈述**: "MySQL 也走了三步（异步复制 → 半同步复制 → MGR）"
**待确认点**: 确认每个步骤引入的 MySQL 版本：(a) 半同步复制在 MySQL 5.5 引入（通过插件）；(b) InnoDB Group Replication (MGR) 在 MySQL 5.7.17 引入、作为 Group Replication 插件；(c) 这三步是否完整覆盖了 MySQL 复制重要的演进路径（遗漏了基于 GTID 的复制在 5.6 引入、Crash-Safe Slaves 等里程碑）。
**建议验证来源**: MySQL 官方手册 "Replication" 章节历史；MySQL 5.5 / 5.6 / 5.7 / 8.0 release notes

### Q3: KRaft 是否完全取代 ZooKeeper 且没有外部依赖
**章节位置**: 9.1.2 回扣第6章（表9-1及正文）
**原文陈述**: "Partition + ISR + KRaft（去 ZooKeeper）"
**待确认点**: (a) KRaft (Kafka Raft) 是否从 Kafka 2.8（早期访问）开始引入、3.x 达到生产可用；(b) KRaft 模式下是否完全不需要外部 ZooKeeper 集群（即"去 ZooKeeper"表述在当前版本是否准确）；(c) KRaft 是否还依赖 ZooKeeper 作为可选回退。
**建议验证来源**: KIP-500；Apache Kafka 2.8 / 3.0 / 3.x release notes；Kafka 官方文档关于 KRaft mode 的说明

### Q4: InnoDB 默认页尺寸 16KB
**章节位置**: 9.1.2 回扣第7章（表9-1）
**原文陈述**: "16KB 页 + B+树为'点查 + 范围扫描'优化"
**待确认点**: 确认 (a) InnoDB 的默认页尺寸为 16KB；(b) 是否支持其他页尺寸（4KB, 8KB, 32KB, 64KB）且非默认；11-13 行陈述是否准确涵盖 InnoDB 的默认情况。
**建议验证来源**: MySQL InnoDB 手册 "InnoDB Page Size" 章节

### Q5: Redis `appendfsync` 三档行为描述
**章节位置**: 9.2.4 规律四
**原文陈述**: "Redis 的 appendfsync 有三档——always（每条命令都落盘，最慢但最不丢）、everysec（每秒落盘一次，默认）、no（交给操作系统决定，最快但可能丢较多）"
**待确认点**: (a) `appendfsync=always` 是否确实是"每条命令都落盘"（是每条写命令后 fsync，确认），(b) `everysec` 是否确实是每秒一次 fsync，(c) `no` 确实交给 OS 决定，(d) 对这三个档位的"丢数据量"描述是否准确：always 理论上丢 0（但如果进程本身 crash 但 OS 正常，是否可能丢？），everysec 丢最近 1 秒数据，no 可能丢约 30 秒以上的数据。
**建议验证来源**: Redis 官方文档 "AOF configuration" 章节；redis.conf 中 `appendfsync` 注释

### Q6: `innodb_flush_log_at_trx_commit=1` 的语义
**章节位置**: 9.2.1 规律一
**原文陈述**: "`innodb_flush_log_at_trx_commit=1` 守护的是 redo log 不丢"
**待确认点**: 确认值为 1 表示每次事务提交都将 redo log buffer 写入日志文件并 fsync。值为 0 和 2 的行为是否与原文描述一致（0 只写 buffer 不写文件，2 写文件但延迟 fsync）。
**建议验证来源**: MySQL InnoDB 手册 "Redo Log" 章节；`innodb_flush_log_at_trx_commit` 参数文档

### Q7: `sync_binlog=1` 的默认值
**章节位置**: 9.3.1 维度一
**原文陈述**: "MySQL 默认押在持久性端，'双 1'配置（`innodb_flush_log_at_trx_commit=1` + `sync_binlog=1`）让每条已提交事务都 fsync，从而做到'断电不丢'"
**待确认点**: `sync_binlog=1` 在 MySQL 5.6 / 5.7 默认值是 0，在 MySQL 8.0 才改为 1。原文称"MySQL 默认"双 1，需确认这是否需要限定版本（MySQL 8.0）。若读者使用 5.7，默认不是双 1，双 1 是"建议配置"而非"默认配置"。
**建议验证来源**: MySQL 5.7 与 8.0 参数默认值对比；MySQL 8.0 release notes 关于 `sync_binlog` 默认值变更

### Q8: 双写缓冲与 torn page 的关系
**章节位置**: 9.2.1 规律一
**原文陈述**: "双写缓冲则守护'脏页落盘时不被撕裂'这一前提（撕裂的页 redo 也救不回来）"
**待确认点**: (a) 是否确认 torn page 无法被 redo log 恢复——redo log 是否只能应用于"完好"的页，而 torn page 的页面校验和不匹配导致无法应用 redo；(b) 双写缓冲（doublewrite buffer）的工作原理是否确实是先写入共享表空间的 doublewrite buffer，再写数据文件，从而避免 partial page write；(c) 该机制在 SSD 且 atomic write 支持较完善的硬件下是否仍有必要。
**建议验证来源**: MySQL InnoDB 手册 "Doublewrite Buffer" 章节；Jeremy Cole 等关于 InnoDB 磁盘结构的系列文章

### Q9: Redis hash 底层编码（listpack vs hashtable）的版本
**章节位置**: 9.2.2 规律二
**原文陈述**: "同一个 hash 语义，底层可以是 listpack 也可以是 hashtable，逻辑层只认 type，存储层管 encoding"
**待确认点**: (a) Redis 7.0 之前 hash 的紧凑编码是 ziplist，7.0 起才全面改用 listpack；(b) 原文仅提 listpack 不加版本说明，可能误导读者认为 Redis 一直用 listpack。需确认读者理解的上下文版本——如果以最新版为准则正确，但应声明版本。
**建议验证来源**: Redis 7.0 release notes（listpack 替换 ziplist）；`HASH` 类型编码在 redis.io/documentation 中的说明

### Q10: MySQL Change Buffer 的行为描述
**章节位置**: 9.2.3 规律三
**原文陈述**: "MySQL 的 Change Buffer 把对二级索引的随机写攒成批量"
**待确认点**: (a) Change Buffer 原名 Insert Buffer（MySQL 5.5 改名），它对 INSERT / UPDATE / DELETE 操作都缓存，不限于插入；(b) 它确实将二级索引的随机修改缓冲起来，待页面读入缓冲池时才合并。但"攒成批量"的表述需确认是否准确：是把多个修改缓存起来再批量合并，还是单纯延迟合并。
**建议验证来源**: MySQL InnoDB 手册 "Change Buffer" 章节

### Q11: MySQL group commit 行为
**章节位置**: 9.2.3 规律三
**原文陈述**: "group commit 把多个事务的 redo 一次 fsync"
**待确认点**: (a) MySQL 5.6 之前存在 binlog group commit 与 InnoDB redo log group commit 之间的协调问题（binary log group commit 曾因两阶段提交导致 redo 的 group commit 失效）；(b) 5.6 引入 Binary Log Group Commit (BLGC) 后才真正解决；(c) 原文未加版本限定，可能遗漏这个历史背景。
**建议验证来源**: MySQL 5.6 release notes "Binary Log Group Commit"; MySQL internals 文档关于 group commit

### Q12: Kafka Record Batch 与压缩
**章节位置**: 9.2.3 规律三
**原文陈述**: "Kafka 的 Record Batch 把多条消息压缩成一个存储单元"
**待确认点**: (a) Kafka 将批量消息（Record Batch）作为压缩/存储单位，压缩在批级别执行；(b) Kafka 0.11.0 引入 Record Batch 格式（magic byte v2），之前的消息格式不同。需确认原文对此是否有版本语境，或不同版本是否影响该陈述的正确性。
**建议验证来源**: Apache Kafka 协议文档 "Record Batch" 章节；KIP-98 / KIP-120

### Q13: Kafka sendfile / 零拷贝实现
**章节位置**: 9.2.3 规律三
**原文陈述**: "零拷贝（sendfile）让一批数据跳过用户态直接从页缓存到网卡"
**待确认点**: (a) Kafka 的零拷贝路径是否确实使用 Java NIO `FileChannel.transferTo()` 调用底层 `sendfile` 系统调用；(b) sendfile 是否完全"跳过用户态"——用户态确实没有数据拷贝，但存在 kernel 空间的页缓存到 socket buffer 的拷贝（在有 scatter/gather DMA 支持的新硬件上可完全避免）。需确认表述是否过于简化。
**建议验证来源**: Apache Kafka 官方设计文档 "Efficiency" 章节；Linux `sendfile(2)` man page

### Q14: Redis Cluster 分区时 AP 行为
**章节位置**: 9.3.1 维度二
**原文陈述**: "Redis Cluster 偏 AP，分区时持有多数主节点的分区继续服务、少数派分区的槽短暂不可用，故障切换时可能丢失少量已确认的写（异步复制的固有代价）"
**待确认点**: (a) 网络分区时，Redis Cluster 是否确实让多数 partition 继续服务，而少数 partition 的 slot 不可用；(b) 故障切换时的数据丢失是由于异步复制——主节点已确认给客户端但尚未复制到从节点的写会丢失。这两点需确认与 Redis Cluster 规范的对应关系。
**建议验证来源**: Redis Cluster 规范（redis.io/docs/management/scaling/）; Redis 官方文档关于 cluster 分区容忍度的说明

### Q15: MySQL MGR 在分区时的 CP 行为
**章节位置**: 9.3.1 维度二
**原文陈述**: "MySQL MGR 偏 CP，少数派分区直接拒绝写，宁可不活也不写错"
**待确认点**: (a) MGR 使用 Paxos 类共识，少数派确实无法形成多数派投票因此拒绝写入；(b) 但需确认 MGR 是否确实属于"CP"分类——MGR 在单主模式下是一种 eventual consistency + group consensus，部分资料认为它不严格符合 CAP 定义中的 CP。需确认这个分类是否在学术层面被认可。
**建议验证来源**: MySQL Group Replication 官方文档; CAP 理论对 MGR 适用性分析（例如 Martin Kleppmann 的评论）

### Q16: Redis 6.0 多线程 IO 的描述
**章节位置**: 9.3.1 维度四
**原文陈述**: "Redis 把'命令执行单线程'写死（即便 6.0 起可开启多线程 IO 卸载网络读写，数据访问仍单线程），因此内核无锁快、可重入逻辑简单，代价是单个实例吃不满多核 CPU"
**待确认点**: (a) Redis 6.0 是否引入可选的 multi-threaded I/O（通过 `io-threads` 配置）用于网络读写，而命令处理核心仍为单线程；(b) 确认多线程 I/O 默认是否关闭；(c) 确认该功能在 6.0 的哪个小版本可用（6.0 正式版 GA 就支持还是后续补全）。
**建议验证来源**: Redis 6.0 release notes; redis.conf 中 `io-threads` 相关配置注释；Antirez 博客关于 multi-threaded I/O 的设计说明

### Q17: MySQL ARIES 三阶段恢复协议
**章节位置**: 9.2.5 规律五
**原文陈述**: "MySQL 把活跃事务、锁等待、LSN 当运行时状态，用 ARIES 协议（分析、重做、回滚三阶段）当崩溃恢复剧本"
**待确认点**: (a) InnoDB 的崩溃恢复是否确实使用 ARIES 协议（Analysis / Redo / Undo 三阶段）；(b) InnoDB 的实现与经典 ARIES 有哪些差异（例如 InnoDB 不使用 ARIES 的 Logical Undo，而是物理逻辑的 redo + 逻辑的 undo）；(c) 确认 LSN（Log Sequence Number）的语义是否准确。
**建议验证来源**: MySQL Internals 手册关于 InnoDB 恢复的章节；CMU 15-721 / 15-445 ARIES 讲义；Jeremy Cole 的 "InnoDB Crash Recovery" 系列

### Q18: Kafka HW / LEO / ISR / Controller epoch 运行时状态
**章节位置**: 9.2.5 规律五
**原文陈述**: "Kafka 把 HW/LEO、ISR、Controller 任期（epoch）当运行时状态，用'日志截断到 HW + Controller 重新分配 leader'当恢复剧本"
**待确认点**: (a) HW（High Watermark）是已被所有 ISR 复制的最大偏移量、LEO（Log End Offset）是日志末尾；(b) 恢复剧本确实是日志截断到 HW、再通过 Controller epoch 机制的 leader 选举来恢复；(c) 需确认新版本 Kafka（KRaft 模式下）的恢复剧本是否有所不同（KRaft 不再依赖 ZooKeeper 进行 Controller 选举）。
**建议验证来源**: Apache Kafka 官方文档关于 replication 的设计；KIP-101（Reassignment and Log Truncation）；KIP-500（KRaft）

### Q19: Redis 的 Pipeline 与 Multi/Exec 网络优化
**章节位置**: 9.2.3 规律三
**原文陈述**: "Redis 的管道（pipeline）与 Multi/Exec 把 N 次网络往返压成 1 次 RTT"
**待确认点**: (a) Pipeline 确实把多次命令的响应合并后一次性返还；(b) Multi/Exec 是事务机制，虽也一次发送多条命令，但 Exec 后才批量返回。需确认说"把 N 次网络往返压成 1 次 RTT"是否准确：Pipeline 和 Multi/Exec 确实减少了往返次数，但严格来说 Pipeline 是减少到 1 次"请求+响应"，Multi/Exec 则是 Exec 响应的 RTT。
**建议验证来源**: Redis 官方文档关于 Pipeline 与 Transaction 的章节

### Q20: MySQL read-ahead 机制
**章节位置**: 9.2.3 规律三
**原文陈述**: "预读把随机页请求变成顺序预取"
**待确认点**: (a) InnoDB 存在两种预读：linear read-ahead（线性预读）和 random read-ahead（随机预读）；(b) "把随机页请求变成顺序预取"可能不够精确——预读存在时请求的可能是随机页，但预读机制猜测接下来需要的连续页并提前一次性加载，这更像是"化随机为预判（推测性顺序预取）"而非"把随机请求转换为顺序请求"。需确认表述是否准确。
**建议验证来源**: MySQL InnoDB 手册 "InnoDB Disk I/O and Page Management"；`innodb_read_ahead_threshold` 参数说明

### Q21: AOF 重写行为
**章节位置**: 9.2.3 规律三
**原文陈述**: "AOF 重写把碎片化的历史命令重新压实成一份快照"
**待确认点**: (a) AOF 重写的机制是扫描当前内存状态生成最小命令集，而非压缩现有 AOF 文件；(b) 说"重新压实成一份快照"可能混淆 RDB（真正快照）和 AOF（命令日志）的重写机制。需确认措辞是否准确——AOF 重写产生的不是"快照"而是"当前数据集的最小命令序列"。
**建议验证来源**: Redis 官方文档 "Redis Persistence: AOF rewrite"；redis.conf 注释

### Q22: PSYNC 部分重同步机制
**章节位置**: 9.1.2 回扣第8章（表9-1）及9.1.2正文
**原文陈述**: "PSYNC（部分重同步 + 全量兜底）" 以及 "PSYNC 用复制偏移量和复制积压缓冲区做部分重同步"
**待确认点**: (a) PSYNC 确实使用主节点的复制偏移量（replication offset）和复制积压缓冲区（replication backlog）实现部分重同步；(b) 2.8 引入 PSYNC v1，4.0 引入 PSYNC v2（支持 partial resync 在复制中断后恢复）；(c) 需确认 PSYNC v1/v2 的区别是否在该描述的覆盖范围内。
**建议验证来源**: Redis 2.8 / 4.0 release notes; 书中第8章关于 PSYNC 的详细说明；redis.io 关于 PSYNC 的文档

### Q23: MySQL redo + binlog 两阶段提交
**章节位置**: 9.1.2 回扣第2章（表9-1）
**原文陈述**: "redo + binlog 两阶段提交保提交一致"
**待确认点**: (a) MySQL 在事务提交时确实使用内部两阶段提交（2PC）保证 InnoDB redo log 与 binlog 的一致性——Prepare 阶段写 redo（prepare 状态）、Commit 阶段写 binlog 再写 redo（commit 状态）；(b) 崩溃恢复时通过检验 redo 与 binlog 是否一致来确定事务是提交还是回滚。需确认该描述的准确性与完整性。
**建议验证来源**: MySQL 官方手册 "Binary Log and InnoDB: Two-Phase Commit"；MySQL Internals 关于 XA 两阶段提交的章节

### Q24: Kafka `enable.idempotence=true` 的行为
**章节位置**: 9.3.3 练习二
**原文陈述**: "`enable.idempotence=true`（它内部会强制 `acks=all` + 重试，挡住'重复写入'和'生产者重试导致的乱序'）"
**待确认点**: (a) 启用幂等生产者后是否自动将 `acks` 强制设为 `all`（Kafka 3.0 前强制为 `-1`/`all`）；(b) 幂等性是否确实防止了重复写入和重试乱序——幂等性依赖生产者 ID（Producer ID）+ 序列号（sequence number）机制，确保 broker 端去重；(c) 幂等性是否只能在单分区内保证顺序不重复，跨分区需要事务。
**建议验证来源**: Apache Kafka 官方文档 "Idempotent Producer" 章节；KIP-98（Exactly Once Delivery and Transactional Messaging）；Confluent 关于幂等生产者的文章

### Q25: Kafka 事务的额外开销
**章节位置**: 9.3.3 练习二
**原文陈述**: "Kafka 事务的额外开销（broker 维持事务状态机、生产者两阶段提交、消费者隔离读）"
**待确认点**: (a) broker 端是否确实维护事务状态机（Transaction Coordinator 管理事务状态）；(b) 生产者侧的两阶段提交（BeginTransaction, CommitTransaction/AbortTransaction）；(c) 消费者端通过 `isolation.level=read_committed` 实现事务隔离读。需确认这三个开销描述是否完整且准确。
**建议验证来源**: Apache Kafka 官方文档 "Transactions" 章节；KIP-98

### Q26: Redis O(1) 访问描述
**章节位置**: 9.3.1 维度三
**原文陈述**: "Redis 用内存换 O(1) 访问，把数据全部驻留内存是'空间换时间'的极致"
**待确认点**: (a) Redis 的数据结构核心是哈希表，确实提供大部分操作 O(1) 平均时间复杂度；(b) 但 Redis 并非所有操作都是 O(1)——如 `KEYS` 是 O(N)、`SORT` 是 O(N+M*log(M))、某些集合操作 O(N)。原文隐含全部 O(1) 可能过于概括，需确认是否加限定词更准确。
**建议验证来源**: Redis 官方文档每个命令的 Time complexity 标注

### Q27: Kafka 稀疏索引描述
**章节位置**: 9.3.1 维度三
**原文陈述**: "Kafka 用稀疏索引省空间（索引只记里程碑），用顺序扫描花时间兜底定位，是'时间换空间'的典型"
**待确认点**: (a) Kafka 的索引文件（`.index`）确实是稀疏索引，每若干条消息记录一个偏移量到文件物理位置的映射；(b) 查找时需要二分查找索引再顺序定位到目标偏移量——这确实是时间换空间。需确认 Kafka 是否还维护时间戳索引（`.timeindex`）作为另一种索引方式。
**建议验证来源**: Apache Kafka 官方文档 "Log" 章节关于索引文件格式的说明

### Q28: MySQL MGR 跨机房可行性
**章节位置**: 9.4.1 表 9-2
**原文陈述**: "MGR 跨机房可行"
**待确认点**: (a) MySQL Group Replication 是否真的适合跨机房部署——MGR 对网络延迟敏感（需要多数派共识，跨机房 RTT 高可能严重影响性能）；(b) 虽然技术上"可行"但需要非常低的延迟（建议 < 5-10ms）。需确认该表述是否过于乐观，是否需要加前提"低延迟网络条件下"。
**建议验证来源**: MySQL 官方博客关于 MGR 跨地域部署的限制；DBA 实践经验分析（各类 MySQL Meetup 分享）

### Q29: Kafka MirrorMaker / Cluster Linking 跨地域容灾
**章节位置**: 9.4.1 表 9-2
**原文陈述**: "MirrorMaker / Cluster Linking"
**待确认点**: (a) MirrorMaker 1 和 MirrorMaker 2（基于 Kafka Connect）是否都是跨集群复制工具；(b) Cluster Linking 是 Confluent Platform 企业版特性，不是 Apache Kafka 开源版特性。需确认该书是否限定在 Apache 开源版还是包含 Confluent 的商业特性。
**建议验证来源**: Apache Kafka 官方文档关于 MirrorMaker；Confluent 文档关于 Cluster Linking

### Q30: Redis Cluster 在线 reshard
**章节位置**: 9.4.1 表 9-2
**原文陈述**: "Cluster 在线 reshard"
**待确认点**: (a) Redis Cluster 确实支持在线迁移 slot（hash slot redistribution），迁移过程中不重启集群；(b) 迁移过程中 slot 的源节点和目标节点会短暂同时持有数据。需确认表述"在线 reshard"是否准确。
**建议验证来源**: Redis Cluster 规范关于 slot 迁移的章节；redis-cli --cluster reshard 命令文档

### Q31: MySQL Group Replication 在线加节点
**章节位置**: 9.4.1 表 9-2
**原文陈述**: "在线加节点 + 自动均衡"
**待确认点**: (a) MGR 是否支持在线加节点（通过 `ADD INSTANCE` 或 group_replication_add_instance）且无需停机；(b) MGR 是否具备"自动均衡"（auto rebalancing）能力，还是需要手动管理成员角色。需确认表述与 MGR 实际能力一致。
**建议验证来源**: MySQL Group Replication 手册关于成员管理的章节；MySQL 8.0 release notes 关于 group_replication 的说明

### Q32: Kafka 加 partition 受限、加 broker 可在线
**章节位置**: 9.4.1 表 9-2
**原文陈述**: "加 partition 受限、加 broker 可在线"
**待确认点**: (a) 增加 Kafka partition 后无法减少或合并 partition（确实受限），且增加 partition 会改变消息的键分区映射；(b) 增加 broker 节点可以在线完成，但需要手动或自动重分配 partition。需确认"受限"描述是否准确反映了 partition 不可缩减这个事实。
**建议验证来源**: Apache Kafka 官方文档关于增加 partition 的说明；KIP-204（关于 partition 数量限制的设计）

### Q33: Redis CONFIG SET 部分动态
**章节位置**: 9.4.1 表 9-2
**原文陈述**: "CONFIG SET 部分动态"
**待确认点**: (a) `CONFIG SET` 确实可以动态修改部分参数而不需重启；(b) 但有一部分参数需要 `CONFIG REWRITE` 才能在重启后持久化；(c) 一部分参数不支持 `CONFIG SET`（只读参数或需重启生效参数）。需确认"部分动态"范围描述是否简洁准确。
**建议验证来源**: Redis 官方文档 `CONFIG SET` 命令说明；redis.conf 中每个参数对动态/静态的标注

### Q34: Redis latency monitor 和 slowlog
**章节位置**: 9.4.1 表 9-2
**原文陈述**: "slowlog + latency monitor"
**待确认点**: (a) Redis 的 SLOWLOG 是否用于记录执行时间超过指定阈值的命令；(b) Redis Latency Monitoring 框架（通过 `LATENCY` 命令集）是否自 2.8.13 引入。需确认参数默认阈值（slowlog-log-slower-than 默认 10000 微秒）。
**建议验证来源**: Redis 官方文档 SLOWLOG / LATENCY DOCTOR 命令说明

### Q35: Redis 代码量大小与通读可行性
**章节位置**: 9.4.3 持续学习
**原文陈述**: "从 Redis 起步，它的代码量小、数据结构清晰、C 语言的直白让你能从命令处理一路追到内存表示，几周就能通读核心路径"
**待确认点**: (a) Redis 核心代码（libC 版本）在 6.x / 7.x 版本大约有 10-15 万行源代码，是否属于"代码量小"见仁见智；(b) "几周就能通读核心路径"是否切合实际——对于有 C 语言基础且有分布式系统背景的读者，"核心路径"（事件循环、命令处理、数据结构实现、持久化）确实可在几周内读通，但仍需确认该表述是否需要更具体的限定。
**建议验证来源**: Redis GitHub 仓库代码行数统计（`cloc` 或 `git ls-files | xargs wc -l`）；是否已有社区成员验证过类似说法

### Q36: 表 9-1 中 Kafka "Controller 选举 + 日志截断到 HW"
**章节位置**: 9.1.1 表 9-1 第 2 章
**原文陈述**: "Controller 选举 + 日志截断到 HW"
**待确认点**: (a) Kafka 确实使用 Controller 进行 partition leader 选举；(b) 日志截断到 HW（High Watermark）是故障恢复时从副本的行为；(c) 需确认原文是否将 Controller 选举和日志截断 HW 都归入"生命周期"范畴（启动关闭）。以 Kafka 版本区分——ZooKeeper 模式下 Controller 通过 ZK 选举，KRaft 模式下通过 Raft 协议选举。
**建议验证来源**: Apache Kafka 官方文档关于 Controller 的说明；KIP-500（KRaft）

### Q37: 表 9-1 中关于 Redis Cluster 的"主从 → Sentinel → Cluster 槽分片 + Gossip"
**章节位置**: 9.1.1 表 9-1 第 6 章
**原文陈述**: "主从 → Sentinel → Cluster 槽分片 + Gossip"
**待确认点**: (a) Redis 的集群演进是否确实分为三步：主从复制 (2.0)、Sentinel (2.8/3.0)、Redis Cluster (3.0)；(b) Redis Cluster 是否基于 gossip 协议进行节点发现和状态传播。需确认每个步骤的版本正确性。
**建议验证来源**: Redis 各版本 release notes；Redis Cluster 规范关于 gossip 协议的章节

### Q38: 表 9-1 中 MySQL "异步 → 半同步 → MGR（Paxos 类多数派）"
**章节位置**: 9.1.1 表 9-1 第 6 章
**原文陈述**: "异步 → 半同步 → MGR（Paxos 类多数派）"
**待确认点**: (a) MGR 使用的共识协议是否可以准确称为"Paxos 类"——实际上 MGR 使用 XCom 通信层（一种 Paxos 变体），也有资料称其使用类 Paxos 的共识协议；(b) MGR 的单主模式使用类似 Paxos 的共识进行消息排序和复制，多主模式使用冲突检测。需确认"Paxos 类多数派"的描述是否准确。
**建议验证来源**: MySQL Group Replication 官方技术白皮书；Group Replication 内部文档关于 XCom Paxos 的说明

### Q39: Kafka 的 SASL 认证 + ACL 授权 + TLS 传输加密
**章节位置**: 9.1.2 回扣第5章（表9-1）及正文
**原文陈述**: "SASL + ACL + 端到端 TLS"
**待确认点**: (a) Kafka 支持多种认证机制：SASL/PLAIN、SASL/SCRAM、SASL/GSSAPI（Kerberos）、mTLS（SSL 证书认证）；(b) ACL 支持按用户、topic、consumer group、cluster 的细粒度控制；(c)"端到端 TLS"的描述需要确认——Kafka 的 TLS 是 broker 到 client、broker 到 broker 的传输加密，并非严格意义上的端到端（end-to-end）。如产生者和消费者各自到 broker 的链路是加密的，但 broker 端会解密处理（broker 能看到明文数据）。需确认"端到端"是否应为 client-to-broker 传输加密。
**建议验证来源**: Apache Kafka 官方安全文档；Confluent 文档关于 Kafka 安全配置的最佳实践

### Q40: 规律五关于 AOF 重放与 RDB 加载的恢复路径
**章节位置**: 9.2.5 规律五
**原文陈述**: "Redis 把键空间、过期表、客户端连接显式建模为运行时状态，用 RDB/AOF + 启动加载当恢复剧本——重启就是按剧本把状态重放回去"
**待确认点**: (a) Redis 启动时根据配置选择加载 RDB 还是 AOF（AOF 优先级更高），但不会同时加载两者；(b) "RDB/AOF + 启动加载"的表述可能让读者误以为同时使用 RDB+AOF 恢复。需确认是否需要说明优先级。
**建议验证来源**: Redis 官方文档 "Redis Persistence" 章节关于启动加载顺序的说明

---

## 汇总统计

- 总核查问题数：40
- 覆盖章节：9.1 概述（表及回扣）、9.2 共性规律（五条规律）、9.3 取舍之道（五个维度、决策树、练习）、9.4 实践建议（checklist、认知台阶、持续学习）
- 涉及的软件版本：Redis 2.0~7.x、MySQL 5.5~8.0、Kafka 0.11~3.x
- 建议重点优先核查：Q1（ACL版本）、Q7（sync_binlog默认值）、Q9（listpack版本）、Q11（group commit版本史）、Q17（ARIES协议）、Q24（幂等生产者行为）、Q28（MGR跨机房可行性）
