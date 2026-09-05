# A1-A7 二票核验报告（源码级验证，改前第二票）

> 日期：2026-09-05 | Agent：source-contributor | 只读
> 职责：不信第一票（架构师）、不信 GPT 版，只信一手信源。信源：Kafka 3.9.0 源码（raw.githubusercontent）、Redis 7.2.5 tarball（sds.c/server.c/config.c）、MySQL 8.0 官方手册（option-files / replication-semisync）、内核文档（sysctl/vm）、KIP-405 官方页＋Kafka 3.9.0/4.0.0 自带 upgrade.html。

## 总判定

**同意执行 A1、A2、A3、A5-①②④、A6、A7（共 11 处 diff）；否决 A4；否决 A5-③。**

A4 是对第一票的否决：**原版正确，GPT 版与架构师第一票都错**——KIP-405 官方页 Status 写 "marked production-ready since Kafka 3.9"；3.9.0 自带 docs/upgrade.html 写 "Tiered storage is now a production ready feature"；4.0.0 的 upgrade.html 对 tiered storage 只字未提。时间线 3.6 EA → 3.9 production-ready/GA。"4.0 才 GA"是社区误记。原版"3.9 起正式 GA"**零改动**，GPT 版的 EA 化改写不移植。

## 各项结论与信源

### A1（同意）Kafka Tiered Storage Follower 追赶
- `AbstractFetcherThread.scala` L411-416：OFFSET_MOVED_TO_TIERED_STORAGE 分支。
- `TierStateMachine.java` 类注释＋`buildRemoteLogAuxState()`：从远程存储 fetchIndex(LEADER_EPOCH/PRODUCER_SNAPSHOT)，truncateFullyAndStartAt(nextOffset)，leaderEpochCache().assign(epochs)。
- 结论："永远追不上会被移出 ISR"不成立；成立的是弱版本：远程追赶依赖对象存储可用＋元数据完整，失败反复重试，拖过 replica.lag.time.max.ms 仍会被移出 ISR。"FETCH 从不被 Leader 远程回源服务"半句保留。
- fig-8-7 题注（窄义为真）与 ch9 L212 hedge（"对本地日志段成立"）均不必改。

### A2（同意）半同步 ACK 刷盘
MySQL 8.0 手册原文："acknowledges receipt … only after the events have been written to its relay log **and flushed to disk**"。原版 ch7/ch9 两处都漏 flush，统一用"落盘"（ch9 本章用词）。

### A3（同意）dirty_background_ratio 分母
内核文档："as a percentage of **total available memory that contains free pages and reclaimable pages** … not equal to total system memory"。只改分母口径，保留 10%/20% 默认值（GPT 删默认值属过度矫正，不采纳）。

### A5-①（同意）聚簇/二级索引叶子
InnoDB 基本事实；全书 grep 确认 ch2 此句是唯一表述点，补括号区分。

### A5-②（同意）SDS 预分配条件化
Redis 7.2.5 `src/sds.c`：`_sdsMakeRoomFor(s, addlen, greedy)` greedy=1 才翻倍；`sdsMakeRoomForNonGreedy` 按需。调用方 `src/networking.c` L2362/L2659（querybuf 大参数），源码注释写明理由。每条客户端命令都走 querybuf，非冷僻路径。

### A5-③（否决）Query Cache 8.0 移除注记
ch4 L9 出现在引语内（作者第一人称选型争论案例），绝对保留；ch5 L113 已完整交代"8.0 被彻底移除"。不改。

### A5-④（同意）幻读术语
MySQL 手册 semi-sync 页全文无 "phantom"；隔离级别幻读是重复范围查询看到新出现的行，此处是已提交且被读过的行切换后消失，方向与定义都对不上。改直述机制。

### A6（同意，追加项）MySQL 配置读取方向写反
手册 option-files："files listed first are read first, **files read later take precedence**"。Unix 顺序：/etc/my.cnf → … → ~/.my.cnf → ~/.mylogin.cnf → DATADIR/mysqld-auto.cnf。原版"`/etc/my.cnf` 优先于 `~/.my.cnf`"方向颠倒；排障案例根因"被 /etc/my.cnf 覆盖"在此顺序下不可能成立。SET PERSIST（mysqld-auto.cnf，读取顺序最末、最隐蔽）补入案例句，修正后反而更真实。

### A7（同意，追加项）Redis 7.0 关闭等副本
Redis 7.2.5 `src/server.c` prepareForShutdown()：`if (!(flags & SHUTDOWN_NOW) && server.shutdown_timeout != 0 && !isReadyToShutdown())` → sendGetackToReplicas()＋pauseActions(PAUSE_DURING_SHUTDOWN, …, PAUSE_ACTIONS_CLIENT_WRITE_SET)。isReadyToShutdown() 对任一 replica->repl_ack_off != master_repl_offset 返回 0。`shutdown-timeout` 默认 10 秒（config.c）；NOW/FORCE/ABORT "since 7.0.0"（commands/shutdown.json）；SIGTERM 路径同走等待。表 3-2 行必改，§3.2 补一句（含 NOW 从句；FORCE/ABORT 不进正文）。fig-3-3 不必改。

## 产出
11 个 diff（old_string 逐一 grep 验证唯一；new_string 全部直引号 U+0022、不新增"——"、无免责腔连环句）。执行记录见同目录《修改执行记录.md》。

## 执行建议
改后派第三视角复核 11 处接缝，重点：Diff 1/2 与 fig-8-7 题注、ch9 L212 hedge 的衔接。
