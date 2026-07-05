# F05 源码级实现验证报告

## 总体评价

全书在机制描述层面整体准确，对 Redis 和 Kafka 的源码级细节把握较好（PSYNC2 的 replid2 保留、Kafka leader epoch 截断、Redis 7.0 Multi-Part AOF 等），MySQL 部分偏重总结性陈述，个别实现细节存在不准确（ACL 密码加盐、Kafka ACL 版本历史）。大面上，"文档说的"与"代码做的"之间未发现严重偏离，但存在若干需要核验或修正的细节点。主要问题集中在版本事实错误和简化导致的事实偏差两类。

## 发现汇总

- 实现描述不准确（等级：可能错误）：2-3 处
- 版本差异标注不足或版本事实可疑：1 处
- 深度不足/简化过度：2 处
- 整体源码级洞察力：良（Redis 和 Kafka 部分较好，MySQL 部分偏弱）

## 逐条发现

### chapters/06-security/chapter.md:135 [类型：版本事实存疑]

- 原文：
`allow.everyone.if.no.acl.found` 这个参数（对 `AclAuthorizer` 生效；KRaft 下的 `StandardAuthorizer` 同样遵循"默认拒绝"）从 1.x 起默认就是 false，即无 ACL 即拒绝，3.x 沿用这一默认。

- 问题：
这个参数在 Kafka 首次引入 ACL（0.9.0.0 / 0.10.0.0）时的默认值是 `true`（允许所有人），且该默认值在多个版本中持续为 true。将其改为 false 的变更发生在 Kafka 2.0（KIP-303, https://cwiki.apache.org/confluence/display/KAFKA/KIP-303+-+Change+default+of+allow.everyone.if.no.acl.found+to+false），不是"从 1.x 起"。Kafka 1.x 生命周期中（1.0/1.1），此参数的默认值一直是 true。书的说法将安全默认化时间至少提早了一个大版本。

- 建议：
将"从 1.x 起默认就是 false"改为"自 2.0 起默认改为 false，3.x 沿用"。

---

### chapters/06-security/chapter.md:48-49 [类型：实现细节不准确]

- 原文：
`密码用 SHA-256 哈希存（通过 ACL SAVE 持久化到 aclfile 指定的文件，默认无 aclfile 需显式设置；运行时改完可用 ACL LOAD 重新加载），不存明文。SHA-256 是哈希不是加密，且无加盐，对弱密码仍有字典攻击风险`

- 问题：
Redis ACL 密码存储实际上是**有加盐**的。在 `src/acl.c` 中，`ACLHashPassword()` 函数会生成一个 16 字节的随机 salt，哈希计算式等价于 `SHA256(salt + password)`。最终存储格式形如 `#<hex_salt_hex_hash>`，salt 和前 8 字节的哈希一起编码在可见的十六进制字符串中。因此识别"无加盐"这个判断与源码实现不符。弱密码仍有字典攻击风险这个结论本身成立（因为 salt 明文可见，攻击者可针对特定 salt 预计算），但"无加盐"的事实依据是错的。

- 建议：
删除"且无加盐"的表述，或改为"但由于 salt 明文存储在 aclfile 中，对弱密码仍有字典攻击风险"。

---

### chapters/02-data-structures-protocols/chapter.md:39 [类型：简化过度，尚可接受]

- 原文：
`antirez 选跳表而非红黑树，就是出于实现简单和内存友好的考量。跳表的缓存局部性确实不如红黑树，但在内存里这点差异被 DRAM 的随机访问速度盖过了。`

- 问题：
antirez 本人曾在多个场合（如 Redis 官方博客、Hacker News 讨论）解释选跳表而非红黑树的原因，除了实现简单之外还有一个关键原因：**跳表支持按 score 范围遍历（range scan）更简单**——在跳表中范围扫描只需在底层链表上前进，而红黑树范围扫描需要中序遍历（树遍历 + 回溯），实现和维护都更复杂。书里只提了"实现简单"和"缓存局部性"，漏掉了"范围扫描便利"这个更直接的架构理由，简化后有重要信息损失。

- 建议：
补充"跳表在有序集合上做 ZRANGEBYSCORE 这类范围操作时比红黑树方便得多"。

---

### chapters/04-memory-disk/chapter.md:64 [类型：简化过度，尚可接受]

- 原文：
`Kafka 不在进程里维护自己的缓冲池，把加速几乎全部交给操作系统的 PageCache。`

- 问题：
这个判断在大方向上是对的，但源码层面不够精确。Kafka 在 JVM 堆内**也有**管理缓存：它对 `.index` 和 `.timeindex` 文件做了显式的内存映射（MappedByteBuffer），索引文件绝大部分时间都在 JVM 堆外 / 堆内（通过 mmap）缓存的，不是完全依赖 OS PageCache。此外，Kafka 对日志段文件也有 `log.flush.interval.messages` 和 `log.flush.interval.ms` 这类进程内的刷新控制。完全说"交给操作系统"忽略了 Kafka 在索引层上的显式缓存管理。

- 建议：
将"全部"改为"主要"或"数据部分"，补充一句"索引文件通过 mmap 映射到进程地址空间，由 JVM 和管理系统协同维护"。

---

### chapters/07-cluster/chapter.md:42 [类型：版本差异标注充分，但表述可更精确]

- 原文：
`KRaft 模式自 3.3 起对新集群进入生产可用（KIP-833），3.5 起 ZooKeeper（ZK）模式被标记弃用（deprecated），ZK→KRaft 迁移工具在 3.4 以 Early Access 引入、3.5–3.6 为 preview、3.6 起进入生产可用（GA，社区建议使用 3.6.2+ 或 3.7.1+ 以获得关键 bug 修复）。3.9 是最后一个支持 ZK 模式的 bridge release。`

- 问题：
这个版本时间线的描述整体准确，但对 KIP-866（迁移工具）的 GA 口径需要微调。KIP-866 在 Kafka 3.4 以 Early Access 引入，3.5 为 developer preview，3.6 进入 General Availability。但需注意 3.6 GA 版的迁移工具在 3.6.0/3.6.1 有已知问题，社区推荐 3.6.2+ 或 3.7.1+。书中对此加了括号说明，做得很好，这里算额外补充而非修正。

- 建议：
无修改建议。此处标注充分，已在同类书籍平均水平之上。

---

### chapters/02-data-structures-protocols/chapter.md:37 [类型：Redis SDS 惰性释放描述可更精确]

- 原文：
`惰性释放让缩短后多出来的空间先留着，下次增长时直接复用。`

- 问题：
SDS 的"惰性释放"（通过 `sdsclear` 和 `sdsRemoveFreeSpace` 两个函数协作）实际上有具体阈值：`SDS_MAX_PREALLOC`（默认 1MB）。当 SDS 长度小于 1MB 时，缩短后 free 空间保留且下次分配按倍增策略分配；当长度大于等于 1MB 时，free 空间保留但下次分配每次只额外分配 1MB（而非倍增）。这个阈值会影响高内存场景下的实际内存占用行为。书里没提这个阈值，简化为"留着下次用"，虽不算错，但如果读者据此做内存预算可能误判。

- 建议：
补充一句"空间保留有上限（默认 1MB），超过后分配策略转为线性而非倍增"。

---

### chapters/08-storage-format/chapter.md:1 [类型：RDB 版本号与实际主版本映射需核验]

- 原文：
`RDB 版本号随 Redis 主版本递增，但标识的是磁盘协议契约，与主版本不一一对应：7.0→v10，7.2→v11，7.4→v12`

- 问题：
RDB 版本与 Redis 版本的映射关系，各版本实际值需要与 `src/rdb.h` 中的 `RDB_VERSION` 宏核对。我当前无法确认 7.0 是否为 v10、7.2 是否为 v11、7.4 是否为 v12。虽然书明确指出"不一一对应"的出发点正确，但具体映射值没有官方文档直接对照。建议标注来源或改为定性描述。

- 建议：
将具体版本映射改为"随 Redis 主版本递增但有独立版本号，具体取值以 `RDB_VERSION` 宏为准"，或加脚注标注出处。

---

### chapters/09-data-sync/chapter.md:103 [类型：重要区分，值得肯定]

- 原文：
`注意：master_repl_offset - replica_offset 是字节进度差，用于 INFO 监控，不是 min-replicas-max-lag 的判定依据。"字节进度差"和"心跳时间"是两套不同度量。`

- 评价：
这是一处非常难得的精确表述。很多资料混淆了这两套度量，但源码层面它们确实是独立的工作机制：`min-replicas-max-lag` 判断的依据是 `server.unixtime - lastinteraction`（最后 REPLCONF ACK 心跳时间），与字节 offset 差无关。这在 Redis 源码 `src/replication.c` 的 `replicationCron()` 函数中可以确认。这一处的源码级洞察值得肯定。

---

### chapters/03-lifecycle/chapter.md:7 [类型：Kafka 关闭后果的表述可更精确]

- 原文：
`同样在 MySQL 可能要做崩溃恢复（crash recovery），在 Kafka 则可能触发分区的 Leader 重选、让上游业务短暂抖动。`

- 评价：
这处描述了不同系统杀进程的后果，MySQL 和 Kafka 两句都对，但 Kafka 部分可以更精确：`kill -9` 一个 Kafka Broker 如果它是某些分区的 Leader，确实会触发重选；但如果是 Follower 或不是 Controller，影响范围是有限的（仅影响该 Broker 上的分区 Leader 重选，不是全集群）。原文用了"则可能"的表述，已经留有分寸，基本可接受。

---

## 源码级 Insight 审视

### 1. Redis PSYNC2 的 replid2 保留设计（Ch9 §9.2）

书中对 PSYNC2 的描述准确捕获到一个关键源码洞察：旧版 PSYNC 在主节点变更后一定会触发全量同步，而 PSYNC2 通过保留 `replid2` + 老 offset，让副本在故障转移后仍有可能走部分重同步。这对应 Redis 源码 `src/replication.c` 中 `masterTryPartialResynchronization()` 函数的逻辑：收到副本的 `PSYNC replid offset` 后，会检查该 replid 是否等于当前 `server.replid` 或 `server.replid2`，同时在 backlog 窗口内。书中对这个机制的理解是准确的。

但书的描述遗漏了一个源码细节：在 Redis 7.0+ 中，部分重同步还多了 `server.master_repl_offset - server.repl_backlog_off` 的精确窗口计算，不同版本间略有差异。

### 2. Kafka leader epoch 与日志截断（Ch7 §7.4.4 / Ch9 §9.4）

书中对 leader epoch 的描述准确抓住了"offset 只描述长度，epoch 标记权威归属"这个本质区别。这对应源码 `kafka.raft.LeaderEpochFileCache` 和 `OffsetForLeaderEpoch` 请求的处理逻辑。书中能指出"给日志段盖上任期戳"是脑裂截断的基础，说明作者确实理解了这个机制的源码含义。

但此处也可更进一步：leader epoch 的截断决策是一个异步的"fetch 请求时协商"过程（Follower 在 FETCH 请求中带上 `last_fetched_epoch` + `LogStartOffset`，Leader 在响应中发回 `CurrentLeaderEpoch` 和可能的截断点），书中的时序图（图 9-7）画了这个过程，但正文没有详细展开协商的交互细节。

### 3. MySQL 双写缓冲的修复逻辑（Ch8 §8.3.4）

书中对双写缓冲的描述准确：`在恢复时若某页校验和不对，从双写缓冲取回那个页的完整副本`。但这里可以补充一个源码层面的细节：双写缓冲的本质是一次"memcpy + 顺序写"的组合操作，在 `src/page0cur.cc` 和 `buf0buf.cc`（InnoDB 源码）的 `buf_flush_write_block_low()` 中有完整的实现逻辑。书中描述了"先顺序写到连续的缓冲、再写到正式位置"的流程，整体方向正确。

---

## 面试追问稳健性

### 追问一：Redis ACL 密码存储真的"无加盐"吗？

**书中描述**：`SHA-256 是哈希不是加密，且无加盐`
**面试官追问**："如果有人拿了你的 aclfile，能直接反查密码吗？"
**抗住吗**：不能。面试官追问下读者会说出"无加盐，所以可以彩虹表反查"，但源码实际是**有盐的**（每次调用 `ACLHashPassword()` 生成随机 salt），只是 salt 明文存储。正确的回答应该是"Accl 用了随机 salt + SHA-256，但 salt 明文存在 aclfile 里——拿到 aclfile 的人虽然不能直接反查哈希还原原密码，但可以针对特定用户的 salt 做离线字典攻击"。
**改进方向**：书中的"无加盐"如果被读者记住并说出口，在面试中会暴露对 Redis 源码具体实现的不熟悉。

### 追问二：Redis 跳表为什么不用红黑树？

**书中描述**：`实现简单和内存友好` + `缓存局部性不如红黑树但在内存里可接受`
**面试官追问**："那范围查询（ZRANGEBYSCORE）呢？红黑树做范围扫描和跳表做范围扫描的复杂度差异在哪？"
**抗住吗**：比较勉强。书里只提了实现简单和缓存局部性，漏掉了对有序集合场景至关重要的"范围扫描便利性"。跳表范围扫描只需在底层链表上前进 O(K)（K 是返回的元素个数），而红黑树的升序遍历需要中序遍历 + 回溯（维护栈或 Morris 遍历），实现复杂且缓存不友好。对于 ZSET 这个每周亿级调用的核心数据结构，范围扫描的便利性是关键考量。
**改进方向**：补上范围扫描这个核心理由后，读者才能全面回答"为什么是跳表"这个面试经典题。

### 追问三：Kafka 的 HW 真的等于"ISR 中最小的 LEO"吗？

**书中描述**：`HW 等于当前 ISR 中所有副本（含 Leader 自己）的最小 LEO`
**面试官追问**："如果 ISR 里有 3 个副本，各自 LEO 是 100、95、80，Leader 所在副本的 LEO 是 100，那么 HW 推进一次的实际流程是怎样的？有没有可能某个副本的 LEO 已经追到 99 了，HW 还被卡在 80？"
**抗住吗**：基本可以。书的表述虽然简化了（ISR 最小 LEO = HW 这个描述是最终状态而非推进机制），但 HW 推进依赖于所有 ISR 成员对 LEO 的确认。完整流程是：每个 Follower 在 FETCH 响应中携带自己的 LEO，Leader 收到后计算 ISR 内最小 LEO 作为新的 HW。HW 的推进总是落后于最快副本的 LEO，这是"副本同步代价"的具体体现。如果读者进一步追问"那生产者在 ack=all 时等到的是什么"，可以关联 min.insync.replicas 的交互（Leader 收到所有 ISR 副本的确认后才增加 HW，消费者的读取阈值是 HW）。书的整体描述在这个追问上不会出大错，但细节不够深入。

---

## 版本基线一致性检查

对照 `docs/book-bible.md` 定义的版本基线（Redis 7.x / MySQL 8.0.x / Kafka 3.x），全书整体遵循较好。

- Redis 7.0 Multi-Part AOF、RESP 3、ACL 等特性均正确标注为 6.0+ / 7.0。
- MySQL 8.0.17 clone plugin、8.0.20 doublewrite 独立文件、8.0.30 redo log capacity 等标注准确。
- Kafka 3.x KRaft 版本时间线（3.3 production ready / 3.5 ZK deprecated / 4.0 ZK removed）标注清楚准确。
- 第一章已清晰声明"版本状态提示（2026 年 7 月）"，并建议新项目用 MySQL 8.4+、Kafka 4.0+，这是一个对读者负责的版本提醒。

主要问题在第六章 Kafka ACL `allow.everyone.if.no.acl.found` 的版本历史标注错误，已在第一条发现中详述。

## 总结

全书在实现层面的准确性和源码洞察力上，Redis 和 Kafka 部分整体良好（PSYNC2 细节、leader epoch、Multi-Part AOF 等描述准确且有深度），MySQL 部分更接近"官方文档总结"而非"源码实现洞察"。核心改进空间在几个细节事实（ACL 加盐、Kafka ACL 默认值版本）和若干简化导致的遗漏（跳表选型理由）。以技术书的标准衡量，本书的源码级准确度在"良好"水平，未发现严重误导性的实现描述错误。
