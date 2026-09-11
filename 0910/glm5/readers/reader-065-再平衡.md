# 读者065 · 再平衡
身份：Kafka 运维，7年，爱好：双板滑雪
主读：第 7 章

## 五个问题
1. 【7.5|深度广度】表 7-1 把 Kafka 横向扩展写成"分区与 Broker 提供吞吐和容量扩展空间"，但漏了运维最要命的一条：加 Broker 后存量分区一条也不会自动迁过去，必须手工 kafka-reassign-partitions 或上 Cruise Control。7.2.3 把 Redis 内置槽迁移（MOVED/ASK 配套）讲透了，Kafka 这边"扩容后数据谁来搬"整段空白，我这个靠再平衡吃饭的人读到这行不服。
2. 【7.4.1|案例示例】"扩分区是一次语义迁移，得按数据迁移来规划，不是单纯的容量操作"——判断我全认，但说完就停了：按什么路径规划？是新建 topic 双写切换，还是旧 topic 重放到新 topic？我实操过一次保 key 顺序的迁移，最想从书里拿路线，结果只有定性没有下文。
3. 【7.3.2|读不懂】"默认等待点下，主节点将 binlog 刷盘后，至少等一个从节点确认"——既然说"默认"，就存在非默认的等待点，但本章没说另一种是什么、差在哪。我从 Kafka 的 acks=1/acks=all 过来找对应物，这条线断了，只能自己猜。
4. 【7.1|表达可读】"它不是'数据是否落盘'，也不能直接换算成产品的快慢排序"——什么叫"产品的快慢排序"？我反复读了三遍，仍不确定是"不能用 CAP 给产品按一致性/性能排名"还是别的意思，这句话卡住了我进入后文 CAP 讨论的节奏。
5. 【7.4.2|逻辑论证】"ISR 数量不足也会使 acks=all 写入失败"——低于多少算不足？我的告警盯的是 UnderReplicatedPartitions 加 min.insync.replicas：ISR 从 3 缩到 2 时若 min.insync.replicas=2 写入照常，只有低于 min.insync.replicas 才失败，而这个参数要到 7.4.3 才出现，此处指代悬空。

## 五个建议
1. 【7.4|深度广度】补一段 Kafka 扩容实操：加 Broker → 生成 reassignment 计划（带 --throttle 节流）→ 用 kafka-leader-election/preferred 副本做 leader 均衡；并给表 7-1 加一行"存量数据再平衡"（Redis 内置槽迁移 / MySQL 靠 GTID 重建副本 / Kafka 外部工具手工迁）。"谁来搬数据"是三家扩容成本的分水岭，也是运维可操作性差距最大的一点。
2. 【图 7-4|图示】图 7-4 里 Partition 2 那一行没有 ISR 标注条，与前两行不一致；且全图只有盒子没有箭头，正文反复强调的"写入只走 Leader、Follower 用 fetch 拉取"在图上看不出来，建议补 produce 进 Leader、fetch 从 Leader 出、消费者读 Leader 三条箭头。
3. 【7.4.2|案例示例】给 ISR 补一个带数字的场景：acks=all 加 min.insync.replicas=2 时，一台慢盘 Follower 反复进出 ISR，生产端间歇性 NotEnoughReplicasException，以及 replica.lag.time.max.ms（默认 30 秒，图 7-4 用对了）调大调小的取舍——运维读这一节最想要的就是这种案例。
4. 【7.4|结构导航】Kafka 圈日常说的"再平衡"多指消费组 rebalance（风暴、cooperative 协议），本章讲的却是服务端分区/副本分布。建议在 7.4 开头或 7.7 加一句范围声明，指出消费组协调在书中何处（或明说不讲），免得 Kafka 读者带着另一半预期进来找不到。
5. 【7.6|深度广度】启示四"把确认条件做成可调参数"建议落成一张可查小表：acks(0/1/all) × min.insync.replicas × unclean.leader.election.enable 的典型组合，每档标"什么故障场景下丢什么数据"。论断我认，但运维的习惯是拿着故障场景查表，这张表会是我全书翻得最多的一页。
