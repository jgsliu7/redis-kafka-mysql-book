# 读者027 · 慢查询姐
身份：MySQL DBA，8年，爱好：追剧
主读：第 3 章

## 五个问题

1. 【3.3|技术事实】「SHOW PROCESSLIST 在关闭期的输出，对着这四类根因看，就能定位卡点」——mysqld 收到 SIGTERM 后就停收新连接、存量连接陆续被断，关闭期几乎不存在能连上去执行 SHOW PROCESSLIST 的窗口。我处理「关不掉」的 mysqld 靠的是 error log 里那串阶段日志（Giving N client threads a chance to die、Waiting for replica SQL thread to die、FTS optimize thread exiting），这句的排障路径在实战里走不通。

2. 【3.3|深度广度】undo 回滚「根据事务提交状态，把尚未 commit 的事务对数据做的修改撤销掉」，但崩溃之后事务提交状态从哪里读出来，全章没有交代。这一步靠的是 redo prepare + binlog XID 的内部 XA 两阶段提交判定——恰是 MySQL 恢复语义与 Redis/Kafka 最不同的一环，「已提交不丢、未提交必滚」的根据就在这里，讲崩溃恢复绕开 binlog 的角色，我认为断了关键一环。

3. 【3.3|技术事实】表 3-1 把 innodb_fast_shutdown=2 说成「只刷 redo 不刷数据页，近乎 kill -9」。=2 仍是走完 server 关闭路径的干净退出：binlog 完整收尾、不会留下写了一半的页，重启后已提交事务不丢；kill -9 连 binlog 缓冲都可能缺尾巴、数据页可能写一半要靠 doublewrite 修。「近乎」二字抹掉的正是我们紧急停机敢用 =2 而绝不敢 kill -9 的那条界线。

4. 【3.5|逻辑论证】表 3-2 说 MySQL 关闭「仅本机自身（主从复制除外）」，可 3.3 自己写了「主库关闭则直接断开 dump 线程，并不等从库把 binlog 拉完」——从库被动积压复制延迟，这对集群是实打实的影响。括注一边承认影响存在、一边仍归为「仅本机」，与 Kafka 行「集群事件」的划分标准前后不一致。

5. 【3.2|术语使用】「这个选择取决于 Redis 是作为缓存还是主存」里的「主存」，在中文技术语境默认指 main memory（内存），而 3.2 开头刚说「Redis 的全部数据都在内存里」，第一遍读真会懵——数据不都在主存里吗。想表达的其实是「主数据库 / primary store」，3.5 的「缓存和主存两种用户」同样别扭。

## 五个建议

1. 【3.4|结构导航】「容器化环境下的生命周期」讲的是三家共同的 K8s 停机问题（grace period、preStop、探针），却作为无编号小节挂在 3.4 Kafka 末尾。我直奔 3.3 查 MySQL 停机建议时根本想不到去 Kafka 节里翻，建议独立成节排在横向对比之前，三家内容各归各的正文。

2. 【3.3|案例示例】「关闭慢的常见根因」四条建议各配一条 error log 标志日志（如 Giving N client threads a chance to die、Waiting for replica SQL thread to die、FTS optimize thread exiting、InnoDB: Starting shutdown）。排障时对着日志卡在哪一句定位根因，四条根因才算落地可查。

3. 【3.3|深度广度】「grace period 给到 120 秒以上」「预留几分钟到几十分钟」缺一个估算方法。建议补一条能照跑的公式：SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_pages_dirty' 拿脏页数乘 16KB，除以该盘实测刷盘吞吐，得出关机耗时量级——120 秒对几十万脏页的大缓冲池实例可能远远不够。

4. 【3.4|术语使用】容器化 MySQL 段写「MySQL 默认 innodb_fast_shutdown=1，受控关闭时刷脏页」，而「受控关闭（controlled shutdown）」是刚在 Kafka 小节定义的术语，MySQL 语境只有优雅/正常关闭。术语串门让我愣了一下，以为 MySQL 也有 controlled shutdown 开关，建议此处改用「正常关闭」。

5. 【3.2|案例示例】全章只有行内命令名，没有一组能照着敲的完整操作序列。建议给 Redis 优雅关闭一个操作框：先 INFO persistence 确认 aof_enabled 与最近落盘状态，再按缓存/主数据库选择 redis-cli SHUTDOWN NOSAVE 或 SAVE，重启后 grep Ready to accept connections 验证就绪——命令要能照着跑，这一章对运维读者才算闭环。
