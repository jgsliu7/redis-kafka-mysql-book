# 第01章 事实核查结果

> 核查时间: 2026-06-23
> 核查范围: verify-questions-01.md 全部54个问题
> 核查方法: 官方文档、Release Notes、GitHub仓库、Wikipedia、权威技术博客

## 核查统计

| 结果 | 数量 |
|------|------|
| ✅ 确认正确 | 41 |
| ❌ 需要修正 | 0 |
| ⚠️ 需要澄清 | 5 |
| 🔍 无法确认 | 8 |

---

## 逐题核查

### Q1: Redis 出身年份与创始人
**原文陈述**: "2009 年，意大利开发者 Salvatore Sanfilippo（社区里更常用的名字是 antirez）"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 于 2009 年 5 月 10 日首次发布，由意大利开发者 Salvatore Sanfilippo（antirez）创建。他当时在开发实时网站访问统计工具 LLOOGG，为解决 MySQL 扩展性问题而创建了 Redis。名字意为 Remote Dictionary Server。
- 来源: Wikipedia Redis 条目（2023年3月存档版）; redis.io 官方博客
**建议**: 无需修改。

---

### Q2: Redis 多线程 IO 引入版本
**原文陈述**: "自 6.0 起引入了可选的多线程 IO 来加速网络读写"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 6.0（2020年5月2日发布）引入了多线程网络 I/O（io-threads），默认关闭。I/O 线程仅处理网络读写和解析请求，不执行命令。antirez 在 RedisConf 2019 上报告性能提升至少 2 倍。来源: staging.redis.io/blog/diving-into-redis-6/
**建议**: 无需修改。

---

### Q3: Redis 命令执行仍为单线程
**原文陈述**: "但命令执行仍是单线程"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 6.0 引入多线程 I/O 后，命令的实际执行仍然在单一主线程中顺序进行。I/O 线程负责 socket 读写，主线程收集解析后的命令后逐一执行。来源: Redis 官方文档、Redis 6.0 release notes。
**建议**: 无需修改。

---

### Q4: Redis 持久化方式
**原文陈述**: "持久化靠 RDB 快照与 AOF（Append-Only File，仅追加文件）两种方式互补"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 官方文档列出的持久化方式只有 RDB（定期快照）和 AOF（追加写命令日志）。两者可以同时启用实现互补：RDB 恢复快但丢失数据多，AOF 数据更完整但恢复慢。官方文档推荐两者同时使用以获得类似 PostgreSQL 的数据安全级别。来源: redis.io/docs/latest/operate/oss_and_stack/management/persistence/
**建议**: 无需修改。

---

### Q5: Memcached 功能定位
**原文陈述**: "Memcached 走的是简单键值缓存路线"
**核查结果**: ✅ 确认正确
**核查依据**: Memcached 官方文档将其描述为 "an in-memory key-value store for small arbitrary data (strings, objects)"。它只支持字符串/blob 类型的值，不提供 Redis 式的数据结构操作。任何结构化数据必须由客户端序列化后存储。来源: docs.memcached.org
**建议**: 无需修改。

---

### Q6: Aerospike 功能定位
**原文陈述**: "Aerospike 主打持久化键值"
**核查结果**: ✅ 确认正确
**核查依据**: Aerospike 官方文档将其定位为支持 DRAM 和 Flash 混合存储的持久化键值存储。支持 CRUD 操作、二级索引、强一致性模式（Aerospike 8.0+支持多记录事务）。来源: aerospike.com/docs/develop/learn/
**建议**: 无需修改。

---

### Q7: MySQL 起源年份
**原文陈述**: "MySQL 的历史是一部商业与工程交织的演化史。它 1995 年起源于瑞典 MySQL AB"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL 的第一个内部版本于 1995 年 5 月 23 日发布，创始人为 Michael "Monty" Widenius、David Axmark、Allan Larsson（瑞典人）。公司 MySQL AB 总部在瑞典乌普萨拉。来源: Britannica MySQL 条目; Wikipedia MySQL 历史存档; Planet MySQL 时间线。
**建议**: 无需修改。

---

### Q8: MySQL 收购时间线
**原文陈述**: "2008 年被 Sun Microsystems 收购，2010 年随 Sun 被 Oracle 收购后正式归入 Oracle 旗下"
**核查结果**: ✅ 确认正确
**核查依据**: Sun 于 2008 年 2 月 26 日宣布以约 10 亿美元收购 MySQL AB。Oracle 于 2009 年 4 月 20 日宣布收购 Sun，经过欧盟反垄断审查后，于 2010 年 1 月 27 日完成交易。来源: Wikipedia "Acquisition of Sun Microsystems by Oracle Corporation"; New York Times 2010年1月22日报道。
**建议**: 无需修改。

---

### Q9: InnoDB 默认页大小
**原文陈述**: "InnoDB 是默认引擎...它把数据组织成页（page，默认 16KB）"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL 8.0 官方文档明确说明："The default size of an index page is 16KB"。页大小由 innodb_page_size 参数控制，支持 4KB、8KB、16KB、32KB、64KB，但默认是 16KB。来源: dev.mysql.com/doc/refman/8.0/en/innodb-physical-structure.html
**建议**: 无需修改。

---

### Q10: InnoDB 三套日志描述
**原文陈述**: "它维护着三套日志——重做日志（redo log）记录物理修改、回滚日志（undo log）支撑回滚与 MVCC、二进制日志（binlog）用于复制与时间点恢复"
**核查结果**: ✅ 确认正确
**核查依据**: 
- Redo log: 物理日志，记录数据页级别的物理变更（页号+偏移量+修改内容），用于崩溃恢复。来源: MySQL 8.0 官方文档。
- Undo log: 逻辑日志（反向操作），串联成版本链，同时支撑事务回滚（原子性）和 MVCC（一致性非锁定读）。来源: MySQL 8.0 Reference Manual - InnoDB Multi-Versioning。
- Binlog: Server 层逻辑日志（支持 STATEMENT/ROW/MIXED 格式），用于主从复制和时间点恢复。来源: MySQL 官方文档。
**建议**: 无需修改。

---

### Q11: 事务提交 fsync 行为
**原文陈述**: "事务提交要做日志落盘（fsync）"
**核查结果**: ✅ 确认正确
**核查依据**: 默认值 `innodb_flush_log_at_trx_commit=1` 表示每次事务提交时 log buffer 写入并 fsync 到磁盘。这是 ACID 合规的必要设置。来源: MySQL 官方文档（dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html）。
**建议**: 无需修改。

---

### Q12: redo 与 binlog 两阶段提交
**原文陈述**: "写操作伴随 redo 与 binlog 的两阶段提交开销"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL 在 redo log 和 binlog 之间使用内部 XA 两阶段提交（2PC）保证一致性。流程：Prepare 阶段（redo log 写入 prepare 状态）→ 写入 binlog → Commit 阶段（redo log 标记 commit）。此机制从 MySQL 5.0+ 开始存在，由 `innodb_support_xa=ON`（默认）控制。来源: MySQL 官方文档 - XA Restrictions; Tencent Cloud/阿里云技术文章。
**建议**: 无需修改。

---

### Q13: LinkedIn Kafka 基准测试 200 万 TPS
**原文陈述**: "LinkedIn 公开基准里 3 台廉价机曾测到约 200 万次写入/秒（TPS，Transactions Per Second）"
**核查结果**: ⚠️ 需要澄清
**核查依据**: LinkedIn Engineering 博客原文 "Benchmarking Apache Kafka: 2 Million Writes Per Second (On Three Cheap Machines)"。但实际测试使用了 6 台机器（3 台 Kafka 节点 + 3 台用于 ZooKeeper 和负载生成），每台为 Intel Xeon 2.5 GHz / 6 核 / 6×7200 RPM SATA 硬盘 / 32GB RAM。最终结果 2,024,032 records/sec 是在 3 个生产者并行、3 倍异步复制条件下达成的。标题中 "On Three Cheap Machines" 容易让人误以为只有 3 台机器。
**建议**: 可补充说明测试实际使用了 6 台机器（3 台 broker + 3 台工具机），使描述更精确。同时可注明 TPS 在此指消息发送/秒而非数据库事务 TPS，书中的表述在通俗意义上可接受。

---

### Q14: Kafka 单机典型吞吐量
**原文陈述**: "单台 broker 的典型吞吐也在十万到几十万量级"
**核查结果**: ✅ 确认正确
**核查依据**: 多项来源交叉验证：Orange Business Cloud 规格显示 4u8g 实例约 100,000 TPS/broker，8u16g 约 150,000, 16u32g 约 250,000。中文技术博客实测 3 broker 集群约 95,877 msg/s（100 字节消息）。生产环境中 100K msg/s per broker 是常用参考值。来源: 多篇基准测试和云服务商规格文档。
**建议**: 无需修改。

---

### Q15: Kafka 创建年份与捐赠时间
**原文陈述**: "2010 年前后，LinkedIn 内部需要把海量的活动日志...于是 LinkedIn 自己写了一套以'日志'为核心的系统，2011 年捐给 Apache"
**核查结果**: ✅ 确认正确
**核查依据**: Kafka 于 2010 年在 LinkedIn 内部由 Jay Kreps、Neha Narkhede、Jun Rao 创建。2011 年 1 月开源，2011 年 7 月进入 Apache Incubator，2012 年 10 月毕业成为 Apache TLP。来源: Confluent "What Is Apache Kafka?" 页面; Wikipedia Kafka 条目; LinkedIn Engineering 博客。
**建议**: 无需修改。

---

### Q16: KRaft 在 Kafka 3.3 达到生产可用
**原文陈述**: "3.x 的标志性变化是 KRaft 在 3.3 达到生产可用，逐步去掉长期依赖的外部 ZooKeeper，改用内置的共识协议（基于 Raft 思想）自治理元数据"
**核查结果**: ✅ 确认正确
**核查依据**: KRaft（KIP-500）在 Kafka 3.3.1（2022年10月3日发布）正式标记为生产可用，但仅限于新建集群（greenfield 部署），从 ZooKeeper 迁移尚未支持。KIP-500 的共识协议基于 Raft 思想（Kafka Raft）。3.x 版本确实做到了"逐步"去掉 ZK：2.8 早期预览 → 3.0 预览 → 3.3.1 生产可用 → 3.5 迁移脚本生产可用 → 4.0 完全移除 ZK。来源: KIP-500 设计文档; Kafka 3.3.1 Release Notes; Confluent KRaft 博客; Conduktor 文档。
**建议**: 可注明 3.3.1 为生产可用起点，且仅适用于新建集群（不含从 ZK 迁移）。但不影响正文准确性。

---

### Q17: Kafka 生产者幂等与事务引入版本
**原文陈述**: "生产者的幂等与事务（早在 0.11 引入）"
**核查结果**: ✅ 确认正确
**核查依据**: Kafka 0.11.0.0（2017年6月28日发布）引入了幂等生产者（KIP-129）和事务支持（KIP-98）。幂等通过 Producer ID + 序列号实现去重；事务通过 Transaction Coordinator 和事务日志实现跨分区原子写入。来源: Confluent Blog "Exactly-once Semantics is Possible"; Apache Kafka 0.11.0.0 Release Notes; KIP-98 / KIP-129 设计文档。
**建议**: 无需修改。

---

### Q18: Kafka 使用页缓存与零拷贝
**原文陈述**: "磁盘 IO 走顺序写，配合操作系统的页缓存（page cache）与零拷贝（sendfile）把单机吞吐压到极限"
**核查结果**: ✅ 确认正确
**核查依据**: Kafka 官方设计文档明确：Kafka 依赖 OS 页缓存（而非 JVM 堆）缓存消息数据，使用 sendfile（Java NIO FileChannel.transferTo()）实现零拷贝，直接从页缓存发送数据到网卡，无需经过用户空间。关键引用："This combination of pagecache and sendfile means that on a Kafka cluster where the consumers are mostly caught up you will see no read activity on the disks whatsoever"。来源: kafka.apache.org/documentation/#maximizingefficiency; Confluent "Efficient Design" 文档。
**建议**: 无需修改。

---

### Q19: Kafka ISR 定义
**原文陈述**: "可靠性靠副本（replica）与 ISR（In-Sync Replicas，同步副本集合）保障，只有落在 ISR 中的副本才算'安全'"
**核查结果**: ✅ 确认正确
**核查依据**: ISR 是与 leader 保持同步的副本集合。acks=all 语义：leader 等待当前 ISR 中所有副本确认写入后才响应生产者，保证数据写入到所有 ISR 成员后才算安全。min.insync.replicas 进一步确保 ISR 不低于下限。来源: kafka.apache.org/documentation/#producerconfigs_acks; KAFKA-8957 改进文档; Confluent 课程 "Guarantees"。
**建议**: 无需修改。

---

### Q20: Redis 单线程执行的原因分析
**原文陈述**: "Redis 选择单线程命令执行，背后的约束是'内存访问远快于网络往返，CPU 不是瓶颈，单线程能省掉所有锁的开销'"
**核查结果**: ✅ 确认正确
**核查依据**: antirez 在自己的博客文章和多个技术交流中反复阐述：Redis 的主要瓶颈不在 CPU 而在内存和网络；单线程模型避免了锁竞争和上下文切换的开销；当网络 I/O（~100μs）远慢于内存访问（<1μs）时，CPU 确实不是瓶颈。来源: antirez.com 博客（"Lazy Redis is better Redis" 等）; Redis 官方 FAQ; Stack Overflow 上 antirez 的回复。
**建议**: 无需修改。注意现代场景下（如 10Gbps 网络、大 Value 操作），CPU 可能成为新瓶颈——这也是 Redis 6.0 引入多线程 I/O 的原因之一。但此表述在历史语境下依然正确。

---

### Q21: Redis 持久化配置推荐
**原文陈述**: "Redis 开 AOF 并把 appendfsync 设为 always"
**核查结果**: ✅ 确认正确
**核查依据**: appendfsync=always 的策略是每次写入都调用 fsync，提供最高可靠性（最多丢失一次写入）。官方文档描述为 "Very very slow, very safe"——性能代价极大（受限于磁盘 fsync 速率，通常仅数千至数万 ops/sec）。来源: redis.io 官方持久化文档; Redis 源码中 flushAppendOnlyFile 实现。
**建议**: 无需修改。这是教材中的极端可靠性示例配置，正文如果提及性能代价会更完整。

---

### Q22: MySQL 持久化配置推荐
**原文陈述**: "MySQL 把 innodb_flush_log_at_trx_commit 设为 1"
**核查结果**: ✅ 确认正确
**核查依据**: innodb_flush_log_at_trx_commit=1 是默认值（无需显式设置），表示每次事务提交时 log buffer 写入日志文件并 fsync 到磁盘，保证 ACID 持久性。来源: MySQL 官方文档（dev.mysql.com/doc/refman/8.0/en/innodb-parameters.html）。
**建议**: 无需修改。

---

### Q23: Kafka 持久化配置推荐
**原文陈述**: "Kafka 把生产者的 acks 设为 all 且 min.insync.replicas 设为 2"
**核查结果**: ✅ 确认正确
**核查依据**: acks=all 要求 leader 等待所有 ISR 副本确认；min.insync.replicas=2 确保至少 2 个副本（含 leader）同步，低于此数则写入被拒。min.insync.replicas 默认值为 1。此组合（配合 RF=3）可容忍 1 个 broker 宕机且保证不丢数据。来源: kafka.apache.org/documentation/#topicconfigs_min.insync.replicas; Conduktor 文档 — min.insync.replicas Explained。
**建议**: 无需修改。

---

### Q24: 逻辑日志 vs 物理日志的描述
**原文陈述**: "逻辑日志紧凑、跨版本友好，但重放时要重新执行操作，速度慢且要小心幂等；物理日志啰嗦、占空间，但重放就是机械地改页，又快又稳"
**核查结果**: ✅ 确认正确
**核查依据**: 这是数据库系统概论中的标准对比。逻辑日志（如 MySQL binlog 的 STATEMENT 格式、Redis AOF）记录操作语义，紧凑且跨版本兼容，但重放需要重新执行 SQL/命令，必须考虑幂等性问题。物理日志（如 MySQL redo log）记录页级物理变更，冗长、依赖具体版本，但恢复时直接覆写页，速度快、不需要考虑幂等。来源: Silberschatz《Database System Concepts》相关章节; MySQL 官方文档对 redo log 与 binlog 的说明。
**建议**: 无需修改。

---

### Q25: AOF 作为逻辑日志
**原文陈述**: "Redis 走 AOF 命令日志——逻辑日志，记的是'做了什么命令'，重放即重新执行命令"
**核查结果**: ✅ 确认正确
**核查依据**: AOF 以 RESP 协议文本格式记录每个写操作命令。重启时 Redis 创建一个伪客户端，依次读取并重新执行 AOF 文件中的所有命令以重建数据集。记录的是操作语义而非物理页变更，所以属于逻辑日志。来源: redis.io/docs/latest/operate/oss_and_stack/management/persistence/; 《Redis设计与实现》（黄健宏）相关章节。
**建议**: 无需修改。

---

### Q26: Redo Log 作为物理日志与两阶段提交
**原文陈述**: "MySQL 走 redo 物理日志加两阶段提交——物理日志，记的是'页上哪个字节改成什么样'，恢复时机械重放，再配合 binlog 这种逻辑日志做复制"
**核查结果**: ✅ 确认正确
**核查依据**: Redo log 记录表空间号+数据页号+偏移量+修改数据的物理变更，属于物理日志。恢复时直接重放物理操作，速度快。Binlog 是 Server 层的逻辑日志（支持 STATEMENT/ROW 格式），用于主从复制和时间点恢复。两阶段提交发生在 redo log 与 binlog 之间，保证两者一致性。来源: MySQL 官方文档 - Redo Log、Binary Log 格式说明; 数据库内核书籍。
**建议**: 无需修改。

---

### Q27: Kafka 日志即数据
**原文陈述**: "Kafka 最彻底，直接把日志当成数据本体：它没有'日志'和'数据'之分，日志就是数据本身，消费者从日志里读，副本把日志复制过去，连'恢复'这个动作都被消解掉了"
**核查结果**: ✅ 确认正确
**核查依据**: Jay Kreps 的核心设计哲学：日志是数据源，当前状态只是日志的物化视图。Kafka broker 在干净关闭后写入 .kafka_cleanshutdown 标记，启动时跳过恢复——因为日志本身就是权威状态。所有副本通过复制日志段（log segments）实现同步，没有独立的"恢复"过程。来源: Jay Kreps "The Log" 论文（LinkedIn Engineering, 2013）; Confluent VLDB 2015 论文 "Building a Replicated Logging System with Apache Kafka"; Kafka 源码中关于 clean shutdown 的逻辑。
**建议**: 无需修改。

---

### Q28: 版本基线声明
**原文陈述**: "凡涉及具体行为、参数或默认值，本书一律以如下版本基线为准：Redis 7.x、MySQL 8.0.x、Kafka 3.x"
**核查结果**: 🔍 无法确认
**核查依据**: 此声明为全书自洽性要求，需要跨章核查才能确认后续章节是否统一遵循此基线。单从第1章本身无法验证。
**建议**: 建议对全书各章进行版本基线一致性交叉检查，确保涉及具体行为、参数、默认值的内容均与声明基线匹配。

---

### Q29: Redis 7.x 新功能
**原文陈述**: "7.x 又带来了 ACL、Function（函数）、Sharded Pub/Sub 等改进"
**核查结果**: ⚠️ 需要澄清
**核查依据**: ACL 是 Redis 6.0 首次引入的（Redis 史上最大的安全升级）。7.x 对 ACL 做了增强（选择器 Selectors、基于键模式的细粒度权限等），但并非首次引入。Functions（Redis Functions）确为 7.0 引入，作为 Lua EVAL 脚本的更强抽象。Sharded Pub/Sub 亦为 7.0 引入（SPUBLISH/SSUBSCRIBE），解决 Cluster 模式下 PUBLISH 广播全集群的问题。来源: Redis 6.0 Release Notes; Redis 7.0 Release Notes（GitHub releases/tag/7.0-rc1）; Redis 博客 "Redis 7 generally available"。
**建议**: 将 "又带来了ACL" 改为 "又增强了 ACL（ACL 自 6.0 引入，7.x 新增了选择器、键级别权限等细粒度控制），并在 7.0 引入了 Functions、Sharded Pub/Sub 等新特性" 以避免读者误以为 ACL 是 7.x 首次引入。

---

### Q30: MySQL 8.0.x 新功能
**原文陈述**: "MySQL 8.0.x 带来了原子 DDL、新版 redo log、降序索引、直方图"
**核查结果**: ✅ 确认正确
**核查依据**: 
- 原子 DDL：MySQL 8.0 引入，DDL 操作成为原子事务（data dictionary 升级为 InnoDB 表）。来源: dev.mysql.com/doc/refman/8.0/en/atomic-ddl.html。
- "新版 redo log"：MySQL 8.0 对 WAL 做了重大重新设计（WL#10310），引入无锁日志系统和专用后台线程（log_writer、log_flusher 等）。8.0.30 进一步引入动态 redo log 容量（innodb_redo_log_capacity）。来源: dev.mysql.com/blog-archive/mysql-8-0-new-lock-free-scalable-wal-design/。
- 降序索引：MySQL 8.0 正式完全支持 DESC 索引（以前 DESC 在语法上接受但实际以 ASC 存储）。来源: dev.mysql.com/worklog/task/?id=7737。
- 直方图：MySQL 8.0 引入列直方图统计（ANALYZE TABLE ... UPDATE HISTOGRAM），帮助优化器对非索引列做更好的基数估计。来源: dev.mysql.com/worklog/task/?id=9223; dev.mysql.com/doc/refman/8.0/en/optimizer-statistics.html。
**建议**: "新版 redo log" 表述稍模糊，但并非错误。可考虑明确为 "无锁化 WAL 重新设计" 更准确。不影响整体正确性。

---

### Q31: 组复制（MGR）成熟度
**原文陈述**: "组复制（MGR）也在这一代走向成熟"
**核查结果**: ✅ 确认正确
**核查依据**: MySQL Group Replication 在 5.7.17（2016年12月）作为 GA 插件引入。8.0 系列做了大量改进使其走向成熟：一致性级别控制（group_replication_consistency，8.0.14）、自动重加入（auto-rejoin，8.0.16）、通信协议版本化、消息分段、更细粒度的监控（MEMBER_ROLE、MEMBER_VERSION 字段）、group_replication_set_as_primary() 手动选举 UDF 等。来源: MySQL 8.0 Release Notes; Tencent Cloud MGR 5.7 vs 8.0 对比文章; GreatDB MGR 文章。
**建议**: 无需修改。"走向成熟"的描述准确反映了 MGR 在 8.0 系列的演进。

---

### Q32: Kafka 分层存储
**原文陈述**: "分层存储（Tiered Storage）持续完善"
**核查结果**: ⚠️ 需要澄清
**核查依据**: Kafka 3.6.0（2023年底）将 Tiered Storage（KIP-405）作为 Early Access 引入，3.9.0（2024年11月）才达到 GA（生产可用）。在 3.x 系列的大部分版本中（3.6-3.8），Tiered Storage 确实处于"持续完善"阶段而非生产可用。来源: Apache Kafka Wiki - Tiered Storage GA Release; Conduktor - Tiered Storage in Kafka; KIP-405。
**建议**: 对于版本基线为 "Kafka 3.x" 的本书，如果基线指向 3.6+，说 "持续完善" 是准确的。如果基线偏早（如 3.0-3.5），则 Tiered Storage 尚未发布。建议结合选取的具体子版本号确认。目前表述在第1章层面可接受。

---

### Q33: 全书术语标注约定
**原文陈述**: "首次出现以'中文（英文）'标注，之后用中文。例如重做日志（redo log）、缓冲池（Buffer Pool）、分区（partition）、副本（replica）、压实（compaction）"
**核查结果**: 🔍 无法确认
**核查依据**: 此为全书自洽性约定，需要跨章核查才能确认是否一致遵守。
**建议**: 建议对全书逐章检查首次出现的术语是否带英文标注，后续使用是否统一为中文。

---

### Q34: Redis 从单机到 Sentinel 再到 Cluster 的演化
**原文陈述**: "Redis 从单机到哨兵（Sentinel）再到 Cluster，是因为单机扛不住可用性与扩展性的双重压力"
**核查结果**: ✅ 确认正确
**核查依据**: Redis Sentinel 在 2.8（2013年底）稳定，解决高可用（自动故障转移）；Redis Cluster 在 3.0（2015年初）稳定，解决扩展性（自动分片到 16384 个槽位）。演化路径确实是单机 → Sentinel（高可用）→ Cluster（扩展性+高可用）。来源: O'Reilly《Redis Essentials》; ByteByteGo "How Redis Architecture Evolved"; Stack Overflow 讨论（antirez 参与）。
**建议**: 无需修改。

---

### Q35: MySQL 从 MyISAM 到 InnoDB 到 MGR 的演化
**原文陈述**: "MySQL 从 MyISAM 到 InnoDB 默认化再到 MGR"
**核查结果**: ✅ 确认正确
**核查依据**: MyISAM 是 MySQL 早期默认引擎（5.5 之前）。InnoDB 在 MySQL 5.5.5（2010年12月）成为默认引擎（WL#5349）。MGR 在 5.7.17（2016年12月）作为插件引入，8.0 成熟。演化路径的描述准确。来源: MySQL Worklog WL#5349; MySQL 5.5 参考手册; MySQL 8.0 Release Notes。
**建议**: 无需修改。

---

### Q36: Kafka 从 ZooKeeper 到 KRaft 的演化
**原文陈述**: "Kafka 从依赖外部 ZooKeeper 到内置 KRaft，是因为外部元数据依赖在大规模部署下成了运维负担与单点风险"
**核查结果**: ✅ 确认正确
**核查依据**: KIP-500 设计文档明确列出 ZooKeeper 的多项痛点：双分布式系统运维负担（各自需要网络层、安全配置、监控）、元数据同步漂移风险（ZK 与 Kafka 控制器状态可能不一致）、控制器故障转移慢（需重新加载全量状态）、ZK 成为单点风险（ZK 出问题时整个集群不可用）。来源: cwiki.apache.org/confluence/display/KAFKA/KIP-500; Confluent 博客 "Kafka Needs No Keeper"。
**建议**: 无需修改。

---

### Q37: InnoDB 特征列举的准确性
**原文陈述**: "InnoDB 引擎几乎成了关系型存储的教科书实现：事务、多版本并发控制（MVCC，Multi-Version Concurrency Control）、B+ 树聚簇索引、预写日志（WAL，Write-Ahead Log）"
**核查结果**: ✅ 确认正确
**核查依据**: InnoDB 使用 B+ 树聚簇索引（Clustered Index）作为主键索引组织方式——数据按主键顺序存储在 B+ 树的叶子节点。实现了 MVCC（通过 undo log 版本链 + Read View 实现一致性非锁定读）。采用 WAL（先写 redo log 再写数据页）。来源: dev.mysql.com/doc/refman/8.0/en/innodb-index-types.html; MySQL 官方文档 - InnoDB Multi-Versioning。
**建议**: 无需修改。

---

### Q38: 表 1-1 中 Redis 出身年份
**原文陈述**: "出身 | 2009，antirez 个人项目，为解决真实访问统计问题而生"
**核查结果**: ✅ 确认正确
**核查依据**: 同 Q1。Redis 初始用于 antirez 的实时网站访问统计工具 LLOOGG。
**建议**: 无需修改。

---

### Q39: 表 1-1 中 MySQL 出身年份与事件
**原文陈述**: "出身 | 1995，MySQL AB，经 Sun 入 Oracle，关系库常青树"
**核查结果**: ✅ 确认正确
**核查依据**: 同 Q7、Q8。"经 Sun 入 Oracle" 准确传达了两次收购的路径。
**建议**: 无需修改。

---

### Q40: 表 1-1 中 Kafka 出身年份与事件
**原文陈述**: "出身 | 2010，LinkedIn 内部日志系统，2011 捐 Apache"
**核查结果**: ✅ 确认正确
**核查依据**: 同 Q15。Kafka 2010 年 LinkedIn 内部创建，2011 年开源并进入 Apache Incubator。
**建议**: 无需修改。

---

### Q41: "Redis 选择单线程命令执行"的核心约束表述
**原文陈述**: "内存访问远快于网络往返，CPU 不是瓶颈，单线程能省掉所有锁的开销"
**核查结果**: ⚠️ 需要澄清
**核查依据**: 三个理由中的前两个准确反映了历史设计权衡。"省掉所有锁的开销" 在主要命令执行路径上是成立的——Redis 主线程无需锁保护数据结构。但在 Redis 内部仍有某些角落使用锁或原子操作：IO threads 涉及锁同步（如等待 IO 线程完成的互斥）、lazy free 后台操作涉及原子引用计数、子进程（RDB fork/AOF rewrite）涉及 COW 页表等。此外，Redis 的 `INFO` 命令统计中的 `sync_full` 计数器、replication 中也有加锁场景。来源: antirez 博客关于 Redis 单线程的讨论; Redis 源码中 networking.c 的 IO threads 同步部分; Redis 官方 FAQ。
**建议**: 将"省掉所有锁的开销"改为"省掉了命令执行路径上的锁开销"或"避免了数据结构层面的锁竞争"更为精确。

---

### Q42: 关于 MySQL B+ 树的选择理由
**原文陈述**: "MySQL 选择 B+ 树而不是哈希索引作为主索引，背后的约束是'要支持范围查询和排序，磁盘随机访问昂贵，需要一种能批量读相邻键的结构'"
**核查结果**: ✅ 确认正确
**核查依据**: B+ 树在数据库系统中被选为主索引结构的原因正是：支持高效的等值查询、范围查询和排序（叶子节点双向链表支持顺序扫描）；通过聚簇索引减少磁盘随机 I/O；（非叶子节点仅存键值，树低矮，IO 次数少）。InnoDB 也支持自适应哈希索引（Adaptive Hash Index），但作为辅助优化，非主结构。来源: 《Database System Concepts》（Silberschatz）相关章节; dev.mysql.com/doc/refman/8.0/en/innodb-index-types.html。
**建议**: 无需修改。

---

### Q43: 图编号约定
**原文陈述**: "图编号统一为'图 N-M'（第 N 章第 M 张图），表编号统一为'表 N-M'（第 N 章第 M 张表）"
**核查结果**: 🔍 无法确认
**核查依据**: 全书图表编号一致性核查超出本文件范围。
**建议**: 建议对全书逐章核查图/表编号是否连续、是否遵循约定模式。

---

### Q44: 正文中图与表必须由正文导出的约定
**原文陈述**: "每张图、每张表必有正文导语引出、正文段落解读，不允许'裸奔'"
**核查结果**: 🔍 无法确认
**核查依据**: 全书图表引用一致性检查超出本文件范围。
**建议**: 建议对全书所有图表进行导语和解读检查。

---

### Q45: Redis 数据结构类型列举
**原文陈述**: "它把字符串、哈希、列表、集合、有序集合、Stream 等结构化类型直接作为一等公民对外暴露"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 官方文档将核心数据结构列为：Strings、Hashes、Lists、Sets、Sorted Sets、Streams。此外还有 Bitmaps、HyperLogLog、Geospatial、JSON（模块）等，但作为介绍性质的列举，覆盖核心 6 种是充分且准确的。来源: redis.io/docs/latest/develop/data-types/
**建议**: 无需修改。

---

### Q46: Redis 命令举例的准确性
**原文陈述**: "比如对有序集合做 ZADD 和 ZRANGEBYSCORE，对列表做 LPUSH 和 BRPOP，对 Stream 做 XADD 和 XREAD"
**核查结果**: ✅ 确认正确
**核查依据**: 
- ZADD / ZRANGEBYSCORE：确为有序集合（Sorted Set）命令。来源: redis.io/commands/zadd, redis.io/commands/zrangebyscore
- LPUSH / BRPOP：确为列表（List）命令。LPUSH 从头部插入，BRPOP 阻塞式从尾部弹出，组成 FIFO 队列。来源: redis.io/commands/lpush, redis.io/commands/brpop
- XADD / XREAD：确为 Stream 命令。XADD 追加条目，XREAD 读取条目。来源: redis.io/commands/xadd, redis.io/commands/xread
**建议**: 无需修改。

---

### Q47: MySQL InnoDB 行级锁
**原文陈述**: "InnoDB 提供完整的 ACID 事务、靠 MVCC 实现的非阻塞读、行级锁"
**核查结果**: ✅ 确认正确
**核查依据**: InnoDB 提供行级锁（实际通过索引记录锁实现——Record Lock、Gap Lock、Next-Key Lock）。MVCC（通过 undo log 版本链 + Read View）支持一致性非锁定读（Consistent Nonlocking Reads），读取器不阻塞写入器、写入器不阻塞读取器。来源: dev.mysql.com/doc/refman/8.0/en/innodb-multi-versioning.html; dev.mysql.com/doc/refman/8.0/en/innodb-next-key-locking.html。
**建议**: 无需修改。

---

### Q48: Redis ACL 引入版本
**原文陈述**: "7.x 又带来了 ACL"
**核查结果**: ⚠️ 需要澄清
**核查依据**: ACL 最初于 Redis 6.0（2020年5月）引入，包括用户定义、命令和键模式权限控制。7.x 对 ACL 做了重大增强（选择器、键级别读写分离权限等），但并非首次引入。来源: Redis 6.0 Release Notes（ACL LOG、ACL SETUSER 等）; Redis 7.0 Release Notes（ACL selectors 等）。
**建议**: 同 Q29。建议修改为 "7.x 又增强了 ACL" 或明确说明 ACL 始于 6.0、7.x 做了重要增强。

---

### Q49: MySQL 引擎从 MyISAM 到 InnoDB 默认化
**原文陈述**: "从早期的 MyISAM 到 InnoDB 默认化"
**核查结果**: ✅ 确认正确
**核查依据**: MyISAM 是 MySQL 早期版本的默认存储引擎。MySQL 5.5.5（2010年12月）起，InnoDB 取代 MyISAM 成为默认存储引擎（WL#5349），为用户提供 ACID 事务、外键、行级锁、崩溃恢复等开箱即用的能力。来源: dev.mysql.com/worklog/task/?id=5349; MySQL 5.5 Reference Manual - Storage Engine Setting。
**建议**: 无需修改。

---

### Q50: 本书主题章数量
**原文陈述**: "每一章围绕一个架构主题——生命周期管理、内存与磁盘、分层架构、安全与权限、集群架构、存储格式、数据同步——同时讲三家软件"
**核查结果**: 🔍 无法确认
**核查依据**: 需要核对全书目录和各章标题以确认这 7 个主题是否准确对应第 2-8 章，以及加上第 1 章引言和第 9 章总结是否确实共 9 章。
**建议**: 建议对照全书目录验证此陈述。

---

### Q51: Redis 单线程性能瓶颈描述
**原文陈述**: "CPU 单核吞吐有上限，对一个键做重计算会让整条命令链路阻塞"
**核查结果**: ✅ 确认正确
**核查依据**: Redis 单线程模式下，慢命令（KEYS *、SORT 大数据集、HGETALL 大哈希、ZRANGE 大有序集合）会阻塞所有后续命令，直到该命令执行完毕。Redis 官方文档通过 SLOWLOG 和延迟排查指南强调此问题，建议使用 SCAN 替代 KEYS、限制数据结构大小、使用主从分离等策略。来源: redis.io 文档 - Redis latency problems troubleshooting; Redis 官方 FAQ; 阿里巴巴开发者文章关于 REDIS 时延分析。
**建议**: 无需修改。

---

### Q52: MySQL 缓冲池（Buffer Pool）描述
**原文陈述**: "数据访问先经过缓冲池（Buffer Pool），把热点页留在内存里减少磁盘随机 IO"
**核查结果**: ✅ 确认正确
**核查依据**: InnoDB Buffer Pool 在内存中缓存表数据和索引页，热点页常驻内存，显著减少磁盘 I/O。Buffer Pool 还配合 Change Buffer 将随机写转换为顺序写，进一步提高性能。来源: dev.mysql.com/doc/refman/8.0/en/optimizing-innodb-diskio.html; dev.mysql.com/doc/refman/8.0/en/innodb-buffer-pool.html。
**建议**: 无需修改。

---

### Q53: MySQL 行级锁与 MVCC 描述
**原文陈述**: "InnoDB 提供完整的 ACID 事务、靠 MVCC 实现的非阻塞读、行级锁"
**核查结果**: ✅ 确认正确
**核查依据**: 同 Q47。InnoDB 行级锁通过索引记录锁实现（记录锁、间隙锁、Next-Key 锁），只在索引上生效。MVCC 非阻塞读依赖于 undo log 中保留的版本链和 Read View 判断可见性。来源: dev.mysql.com/doc/refman/8.0/en/innodb-multi-versioning.html; dev.mysql.com/doc/refman/8.0/en/innodb-next-key-locking.html。
**建议**: 无需修改。

---

### Q54: "使用视角教你把车开起来" 比喻的一致性
**原文陈述**: "使用视角教你把车开起来，架构视角让你知道为什么雪天要换防滑链——也让你在设计自己的车时，知道该装哪条链"
**核查结果**: 🔍 无法确认
**核查依据**: 此为基于比喻的写作手法，非事实性陈述。其一致性需要在全书上下文中评估。
**建议**: 建议在全书行文定稿时检查该比喻在后续章节是否被回用、是否保持一致。

---

## 修正优先级

### 高优先级（必须修正）
无。未发现需要必须修正的事实性错误。

### 中优先级（建议修正）

1. **Q29 / Q48: ACL 引入版本的表述**
   - 问题: "7.x 又带来了 ACL" 强烈暗示 ACL 是 7.x 首次引入，实际上 ACL 是 6.0 的核心新功能。
   - 建议: 修改为 "7.x 又增强了 ACL（ACL 自 6.0 引入），并带来了 Functions、Sharded Pub/Sub 等新特性"。

2. **Q13: LinkedIn Kafka 基准测试机器数量**
   - 问题: "3 台廉价机" 源自博客标题 "On Three Cheap Machines"，但实际测试使用了 6 台（3 broker + 3 工具机）。
   - 建议: 改为 "LinkedIn 内部基准中 3 台廉价 Kafka broker 节点（配 3 台工具机）曾测到约 200 万次写入/秒"。

### 低优先级（可选优化）

3. **Q41: "省掉所有锁的开销"表述**
   - 问题: Redis 在 IO threads、lazy free 等场景仍有锁或原子操作。
   - 建议: 改为 "省掉了命令执行路径上的锁开销" 更精确。

4. **Q30: "新版 redo log" 表述**
   - 模糊但非错误。可明确为 "无锁化 WAL 重新设计" 更准确。

5. **Q16 / Q32: Kafka 特性生产可用版本附注**
   - KRaft 3.3.1 仅限新建集群。Tiered Storage 在 3.9 才 GA。建议在正文或脚注中注明这些条件约束。

---

文件路径: /Users/liu/dev/demos/redis-kafka-books/docs/verify/verify-results-01.md
