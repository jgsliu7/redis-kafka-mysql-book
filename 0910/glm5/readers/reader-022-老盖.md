# 读者022 · 老盖
身份：运维老兵，18年，爱好：盆景
主读：第 3 章

## 五个问题
1. 【3.3|技术事实】「`SHOW PROCESSLIST` 在关闭期的输出，对着这四类根因看，就能定位卡点」这句和我 18 年的手感对不上：关闭流程一起动监听就停了，新连接进不来，手里已有的连接也很快被收走，多数时候根本没有窗口执行 SHOW PROCESSLIST。而且四类根因里只有长事务回滚在 processlist 里露脸，脏页刷盘、复制线程退出、FTS 优化是内部线程和后台动作，processlist 里看不见。我实战定卡点靠的是 error log 里 "Starting shutdown" 之后的进度信息，以及还有机会连上时的 SHOW ENGINE INNODB STATUS。

2. 【3.3|逻辑论证】表 3-1 之后论证默认档 1「让关闭耗时有个可预期的上界」，可本节「关闭慢的常见根因」第一条就是「大量脏页待刷」——档位 1 恰恰要刷完全部脏页才走。大 buffer pool 加写入密集的库，这个「上界」我在生产等过四十分钟，既不小也很难叫可预期，两段并排读说服力互相打折。建议要么给个按脏页量与磁盘吞吐估算的粗公式，要么坦白档位 1 的上界就是「刷完脏页的时间」。

3. 【3.6|案例示例】结尾事故复盘（呼应导读那次丢数据）缺关键配置上下文：AOF 的 appendfsync 是 everysec 还是 always？当时是直接 kill -9，还是发了 SIGTERM 没等住又补了刀？everysec 下 kill -9 丢的是最后一秒（配置选型问题），SIGTERM 中途被杀丢的是未刷缓冲（操作纪律问题），机理和教训都不一样，读者对不上号。另外订单数据只落 Redis 当主存、没有双写兜底，按我们的复盘模板这会是第一条整改项，值得点一句。

4. 【3.2|深度广度】「启动四阶段」和图 3-2 完全是单机视角，可我管的 Redis 十有八九是 replica/cluster 形态：重启一台 replica 走的是 PSYNC/全量同步，数据来自 master 推过来的 RDB 流而不是本地持久化文件；cluster 节点还要加载 nodes.conf、等 slots 覆盖齐才能服务。3.5 表 3-2 里「基本只关本机」的叙事和这个单机假设互相呼应，但离生产形态有距离，值得补半页「非单机形态的启动」。

5. 【3.2|技术事实】第一段拿「TCP backlog 511」当默认值示例，但 511 在内核 somaxconn=128 的老机器上（CentOS 7 一代默认就是 128）根本落不了地，Redis 启动日志会打那条著名的 "WARNING: The TCP backlog setting of 511 cannot be enforced"。运维看到 511 第一反应就是这个坑——例子挑在了我们最熟的反面教材上却没点破，顺手点破还能给启示五「可观测性」添一个真实的启动期告警例证。

## 五个建议
1. 【3.4|深度广度】容器化一节只讲了 K8s 的 terminationGracePeriodSeconds，建议补一段「同一问题在裸机/VM 进程管理器上的马甲」：systemd 的 TimeoutStopSec（默认 90 秒）、supervisor 的 stopwaitsecs（默认只有 10 秒，大实例优雅关闭必超），以及一些流传的 redis.service 模板里 KillMode=process 让 BGSAVE 子进程躲过清理变孤儿的老坑。存量物理机和虚拟机部署的读者跟 K8s 读者一样需要这份对照。

2. 【3.2|案例示例】「运维脚本靠 grep 这一行来判断就绪」建议升级：grep 日志受采集缓冲、重定向切割影响，容器里 stdout 拉取还有延迟，作为唯一就绪信号不可靠。给三家各配一条程序化探测（redis-cli ping、mysqladmin ping、kafka 的 BrokerApiVersions 命令），并说明与 K8s startupProbe 的接法，正好把启示五落到实处。

3. 【3.3|案例示例】「配置到底在哪生效」点了高频排障点却没给读者趁手的工具，建议补一句实操：`mysqld --verbose --help` 输出开头的 "Default options are read from..." 显示真实读取顺序，`performance_schema.persisted_variables` 能把 SET PERSIST 留下的残留值一网打尽。这种命令我们叫五分钟定位，没有它这段就只是描述现象的段子。

4. 【3.4|版本时效】「多数生产部署如今跑在 Kubernetes 上」这句建议收窄：以我管的和见过的存量，MySQL 这类有状态库大量还活在裸机/VM 上（金融、电信尤甚），中间件类上 K8s 的比例确实高。另建议在版本口径里交代一句 Redis 许可变动与 Valkey 分叉的现状——2026 年新部署选型绕不开它，而第 3 章讲的 7.0 特性在 Valkey 上同样成立。

5. 【3.7|结构导航】3.4 末尾两行「实践清单」太薄，建议在章末收口成一张覆盖三家的重启/发布 SOP 表：摘流、确认从库或副本追平、触发落盘、发 SIGTERM、盯就绪日志与退出码、校验 grace period 是否够。素材全章都齐了，只差拼成一张可打印的单子——跟修盆景一个道理，保活靠流程不靠手感，我们做变更保命靠的就是 checklist。
