# 第10章《后记》事实核查问题清单

---

### Q1: Redis Cluster 网络分区下自动选举新 master
**章节位置**: 第23-25行（真实故事段落）
**原文陈述**: "一个网络分区刚好把负责库存那个槽的 master 从集群里割了出去，Redis Cluster 自动选举了新 master"
**待确认点**: Redis Cluster 在 minority partition 场景下是否真的能自动选举新 master。当 master 被割入 minority 分区后，majority 分区的 replicas 需要满足什么条件才能触发选举并成为新 master？是否依赖 `cluster-node-timeout` 参数？
**建议验证来源**: Redis Cluster 官方规范 (redis.io/docs/reference/cluster-spec/)；Redis 源码 cluster.c 中的 `clusterSendPing`/`clusterHandleSlaveFailover` 逻辑

---

### Q2: Redis Cluster 少数派分区短暂接受写入
**章节位置**: 第25行
**原文陈述**: "老 master 在被割出去的少数派分区里还在短暂地接受写入"
**待确认点**: Redis Cluster 中，被隔离到 minority 分区的 master 是否会在 `cluster-node-timeout` 时间内继续接受写入？超时后是否拒绝写入？具体行为与 `cluster-node-timeout` 和 `cluster-slave-validity-factor` 的关系如何？
**建议验证来源**: Redis 官方文档 Cluster Spec 的 Partition Handling 章节；Redis 源码 `processCommand` 函数中 `clusterNodeIsDead` 检查逻辑

---

### Q3: 网络恢复后老 master 写入被新 master 数据覆盖
**章节位置**: 第25-26行
**原文陈述**: "网络恢复后，这部分写入被新 master 的数据覆盖了——库存多卖了。"
**待确认点**: Redis Cluster 在网络分区恢复后，old master 是否确实会将自己转换为 replica 并全量同步新 master 的数据，从而丢失其在分区期间接受的写入？增量同步还是全量同步？是否有选项可以保留或禁止这种行为？
**建议验证来源**: Redis Cluster Spec "Split-Brain" 章节；Redis 文档关于 Partition and Node Failure 的描述

---

### Q4: Redis Cluster 被归类为 AP（可用性优先）系统
**章节位置**: 第27行
**原文陈述**: "把一个设计成 AP（优先保证可用性）的系统用在了需要 CP（必须保证一致性）的场景上"
**待确认点**: Redis Cluster 在 CAP 定理中的分类。Redis Cluster 少数派分区在超时后会拒绝写入（趋向 CP），多数派分区继续服务（趋向 AP）。这种做法是否属于"AP"？实际上 Redis Cluster 是"AP with eventual consistency + partition detection timeout"，这个分类是否有权威来源支撑？
**建议验证来源**: Redis 官方博客关于 CAP 的讨论；分布式系统学术界关于 Redis Cluster CAP 分类的分析；Redis Cluster Spec 关于一致性模型的描述

---

### Q5: MySQL 作为库存/账本系统的"真相之源"
**章节位置**: 第27-28行
**原文陈述**: "库存是'账'，账本系统必须有一个在任何故障下都不被质疑的真相之源。Redis 不是那个真相之源，MySQL 才是。"
**待确认点**: 这是一个架构建议而非硬性事实，但隐含的断言是"MySQL 具备比 Redis 强的一致性保证"，需要确认：MySQL 在双1配置下是否能"在任何故障下都不被质疑"？InnoDB 在 crash recovery、power loss 等情况下的数据持久性保证究竟是什么？
**建议验证来源**: MySQL 官方文档 "InnoDB Crash Recovery" 章节；MySQL 关于 ACID 和 Durability 的官方说明

---

### Q6: MySQL "双1配置"的含义
**章节位置**: 第29行
**原文陈述**: "MySQL 双1配置做真相之源"
**待确认点**: "双1配置"指的具体是 `innodb_flush_log_at_trx_commit=1` 和 `sync_binlog=1` 吗？是否还有其它参数需要设置为 1（如 `innodb_doublewrite=1`）？这个俗称的覆盖面有多广？
**建议验证来源**: MySQL 官方文档对 `innodb_flush_log_at_trx_commit` 和 `sync_binlog` 参数的说明

---

### Q7: Redis SETEX + INCR 用于预扣减挡板
**章节位置**: 第29行
**原文陈述**: "Redis 只做预扣减挡板（SETEX + INCR，挡掉大部分流量读）"
**待确认点**: SETEX 和 INCR 组合使用是否适用于库存预扣减场景？INCR 返回的新值可以用于判断是否超卖，SETEX 设置 TTL 防止 key 一直存在。这个模式是否是一个被社区验证过的常见做法？INCR 在 Redis Cluster 下跨 slot 使用时是否有注意事项？
**建议验证来源**: Redis 官方文档对 INCR 命令的并发安全说明；业界关于 Redis 库存扣减的最佳实践文档

---

### Q8: `innodb_flush_log_at_trx_commit` 从 1 调到 2 导致吞吐提升
**章节位置**: 第41行（"下一步做什么"段落）
**原文陈述**: "`innodb_flush_log_at_trx_commit` 从 1 调到 2，吞吐能涨多少？"
**待确认点**: `innodb_flush_log_at_trx_commit=1` VS `=2` 的性能差异。值 1 表示每次事务提交都调用 fsync 写日志到磁盘，值 2 表示只写入 OS cache（每秒才 fsync 一次）。吞吐提升幅度是否有常见的基准数据？是否存在数据丢失风险的具体差异（OS crash 时值 2 丢数据）？
**建议验证来源**: MySQL 官方文档对这两个参数值的性能与可靠性比较；Percona 或 MySQL Performance Blog 关于该参数的基准测试文章

---

### Q9: `appendfsync` 从 everysec 调到 always 导致延迟增加
**章节位置**: 第41-42行（"下一步做什么"段落）
**原文陈述**: "`appendfsync` 从 everysec 调到 always，延迟会增加多少？"
**待确认点**: Redis AOF 的 `appendfsync always` VS `everysec` 的性能差异。`always` 在每个命令执行后都 fsync，延迟显著高于每秒 fsync 一次的 `everysec`。具体的吞吐量下降或延迟增加的数值范围是否有公认的基准数据？
**建议验证来源**: Redis 官方文档关于 AOF 持久化策略的性能说明；Redis 源码中 `aof_fsync` / `flushAppendOnlyFile` 的实现

---

### Q10: Kafka 的"追加日志+顺序写"是核心工作机制
**章节位置**: 第43行（"下一步做什么"段落的示例）
**原文陈述**: "Kafka 的追加日志+顺序写是合适的"
**待确认点**: Kafka 的核心架构是 append-only commit log，利用磁盘顺序写获得高吞吐。这个描述是否准确涵盖了 Kafka 的核心机制？Kafka 的零拷贝（sendfile）、页缓存利用、批次发送等关键优化未提及，但"追加日志+顺序写"作为概括是否足够准确？
**建议验证来源**: Kafka 官方文档关于 Log 和 Performance 的内容；Kafka 论文 "Kafka: a Distributed Messaging System for Log Processing" (2011)

---

## 统计

- **问题总数**: 10
- **涉及系统**: Redis (Q1-Q4, Q7, Q9), MySQL (Q5, Q6, Q8), Kafka (Q10), CAP 理论 (Q4)
- **核查类型**: 配置行为/算法细节 (Q1-Q4, Q6, Q8, Q9), 架构定性 (Q4, Q10), 性能影响 (Q8, Q9), API/命令使用 (Q7), 架构建议 (Q5)
