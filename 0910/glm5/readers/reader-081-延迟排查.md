# 读者081 · 延迟排查
身份：主从复制 DBA，11年，爱好：冰球
主读：第 9 章

## 五个问题
1. 【9.3|技术事实】半同步一节说 ACK 的条件是「副本 I/O 线程把事件写入 relay log 并落盘后即回 ACK」，图 9-5 也标着「已写 relay log 并落盘」——半同步 ACK 只要求事件写入 relay log（write），是否 fsync 由副本的 sync_relay_log（默认 10000）另行控制，不在 ACK 条件内，副本整机掉电时已 ACK 事务照样丢。我处理过半同步误配丢数据的故障，「落盘」二字给了读者过强保证。
2. 【9.3|技术事实】多线程并行复制一节说 COMMIT_ORDER「根据主节点上事务提交窗口是否重叠来生成这些依赖，不只限于同一次组提交」，与实现相反：COMMIT_ORDER 恰恰以同一次组提交为单位（同组事务共享 last_committed 才可并行），跨组扩大并行正是 WRITESET 才有的能力。我调 MTS 时天天看 last_committed，这半句把两个机制弄混了。
3. 【9.3|深度广度】9.3.5 讲「单线程回放容易遇到复制延迟」并给了一串参数，但全章没有一处告诉读者怎么量化延迟：Seconds_Behind_Master 基于事件时间戳的坑（长事务、时钟回拨会跳变）、MTS 下要看 performance_schema 各 worker 与队列状态。Redis 侧还给了一句 offset 差可用于监控，MySQL 侧反而一句没有，排障读者两头对照会断粮。
4. 【9.4|逻辑论证】作者表态碰钱碰库存「宁可写失败让业务立刻感知，也不要超时后静默降级」站 Kafka，但没点破对照面：MySQL 半同步超时后必然降级放行，没有拒绝写的开关。读者容易带着「半同步＝不丢」的印象离开 9.3——那场景 MySQL 侧的出路（换 MGR 或应用层把关）书里没接上这半句。
5. 【9.3|图示】图 9-5 用 9px 小字标「两档：AFTER_COMMIT（图示）/AFTER_SYNC」，主图画的是非默认档 AFTER_COMMIT（引擎提交后才等 ACK），而 8.0 默认是 AFTER_SYNC（等 ACK 后才提交引擎）。我按图核对默认等待点位置时被误导了一拍，正文反复强调的正是这个先后差。

## 五个建议
1. 【9.3|案例示例】GTID 一节只讲「简化切换」的正面叙事，建议补 errant transaction（幽灵事务）反例：从库误写产生的本地 GTID 会在切换后让新主补发冲突事务、副本应用报 1062。这正是我做切换前必查两边 Executed_Gtid_Set 差异的原因，有这个反例，GTID 的叙事才完整。
2. 【9.3|深度广度】并行复制给了机制没给选型判据：主库并发低时组提交窗口窄、COMMIT_ORDER 并行度塌缩，写冲突密集时 WRITESET 也没收益。建议补一句什么负载该切 WRITESET 的实操判据（从库 lag 且 worker 空闲、主库低并发），对真正在调 lag 的人最有用。
3. 【9.5|深度广度】表 9-1 六个维度建议加一行「人为延迟/延迟副本」：MySQL 有原生延迟复制（SOURCE_DELAY，误操作恢复的救命稻草），Redis 没有对应物，Kafka 只能按时间戳重置位点。这是三软件差异显著、DBA 实际天天在用的一维，现有六行没盖住。
4. 【9.1|结构导航】「关键数字」框只在 9.1 出现一次，之后 9.2–9.4 散落大量默认值与版本号（Redis 7.0 共享缓冲块、8.0.26 半同步改名、8.0.27 MTS 默认 4 worker、Kafka 3.9 Tiered Storage）。建议章末汇总一张「参数与默认值速查表」，排障时翻书即得，也收敛正文里越积越多的版本号。
5. 【9.3|案例示例】MGR 一节把 group_replication_consistency 五个档位一口气列完，没有场景锚点；对比 9.4 谈 acks 时作者给了「碰钱站 Kafka」的鲜明倾向，这节恰好缺席。建议补一句第一人称判断（如读写都走主库的组用 EVENTUAL 就够、读本地节点的组才需要 BEFORE/AFTER），这本书的招牌就是作者的取舍判断。

## 附：核对与来源
- repl-diskless-sync：Redis 7.0 起默认 yes（github.com/redis/redis/issues/9992），书中 9.2 的说法正确（我原本存疑，核对后撤回）。
- 半同步 ACK 与 fsync：MySQL 8.0 手册 19.1.6.3（sync_relay_log）、WL#4398。
- COMMIT_ORDER 与组提交：MySQL 8.0 手册 19.1.6.4（binlog_transaction_dependency_tracking）、hackmysql.com《Group Commit and Transaction Dependency Tracking》。
