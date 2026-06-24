# 第02章《生命周期》事实核查问题清单

## 2.2 Redis 做法

### Q1: Redis 默认端口
**章节位置**: 2.2 启动四段式 — 第一段
**原文陈述**: "Redis 先用 `initServerConfig` 给所有参数设一个合法的默认值（比如端口 6379、TCP backlog 511）"
**待确认点**: Redis 默认端口是否为 6379；TCP backlog 默认值是否为 511。
**建议验证来源**: Redis 源码 `server.h` 中 `CONFIG_DEFAULT_TCP_BACKLOG` 的值；官方文档 `redis.conf` 中 `tcp-backlog` 的默认值说明。

### Q2: 预创建共享整数对象范围与数量
**章节位置**: 2.2 启动四段式 — 第二段
**原文陈述**: "预创建 0–9999 共 10000 个共享整数对象以复用常见小整数"
**待确认点**: Redis 共享对象的范围是否为 0 到 9999（共 10000 个）；该常量在源码中是否为 `REDIS_SHARED_INTEGERS` 且值为 10000。
**建议验证来源**: Redis 源码 `server.h` 中 `REDIS_SHARED_INTEGERS` 的宏定义；`object.c` 中 `createSharedObjects()` 函数。

### Q3: 信号处理器注册
**章节位置**: 2.2 启动四段式 — 第二段
**原文陈述**: "注册信号处理器（SIGTERM/SIGINT 触发优雅关闭、SIGPIPE 忽略、SIGCHLD 回收 RDB/AOF 子进程）"
**待确认点**: Redis 是否对 SIGTERM/SIGINT 注册了优雅关闭处理器；SIGPIPE 是否被忽略；SIGCHLD 是否用于回收 RDB/AOF 子进程。
**建议验证来源**: Redis 源码 `server.c` 中 `setupSignalHandlers()` 函数。

### Q4: 事件循环创建函数
**章节位置**: 2.2 启动四段式 — 第二段
**原文陈述**: "调用 `aeCreateEventLoop` 创建事件循环"
**待确认点**: Redis 是否确实通过 `aeCreateEventLoop` 创建事件循环；该函数命名是否正确。
**建议验证来源**: Redis 源码 `ae.c` / `ae.h` 中事件循环创建函数名。

### Q5: Redis 7.0 引入多分片 AOF
**章节位置**: 2.2 启动四段式 — 第三段
**原文陈述**: "Redis 7.0 引入了多分片 AOF（multi-part AOF）"
**待确认点**: Redis 7.0（GA 版本 2022-04-27）是否正式引入了 multi-part AOF 功能。
**建议验证来源**: Redis 7.0 release notes；Redis 官方文档关于 multi-part AOF 的介绍。

### Q6: Multi-part AOF base 文件格式
**章节位置**: 2.2 启动四段式 — 第三段
**原文陈述**: "AOF 目录里的 base 文件本身就是 RDB 格式"
**待确认点**: Multi-part AOF 的 base 文件是否确实是 RDB 二进制格式，而非纯文本协议格式。
**建议验证来源**: Redis 源码 `aof.c` 中关于 base/incr 文件的实现；Redis 官方文档 multi-part AOF 说明。

### Q7: AOF 加载方式
**章节位置**: 2.2 启动四段式 — 第三段
**原文陈述**: '"加载 AOF"其实是先按 RDB 二进制快速加载 base，再重放 incr 里的命令'
**待确认点**: Redis 7.0+ 加载 AOF 是否确实先加载 base（RDB 格式）再重放 incr 中的命令。
**建议验证来源**: Redis 源码 `server.c` 中 `loadDataFromDisk()` 或类似加载函数的实现。

### Q8: AOF 加载速度对比 4.x
**章节位置**: 2.2 启动四段式 — 第三段
**原文陈述**: "加载速度比 4.x 以前那种'纯命令重放'快很多"
**待确认点**: 7.0 的 multi-part AOF 加载速度是否确实比 4.x 时代的纯命令重放快很多；有无权威基准数据支持此表述。
**建议验证来源**: Redis 官方博客或 KIP 文档中关于 multi-part AOF 性能对比的数据。

### Q9: "Ready to accept connections" 日志
**章节位置**: 2.2 启动四段式 — 第四段
**原文陈述**: "控制台会打印一条 `Ready to accept connections` 日志"
**待确认点**: Redis 启动完成后打印的就绪日志是否确实是 `Ready to accept connections`（注意大小写和标点）。
**建议验证来源**: Redis 源码 `server.c` 中 `main()` 函数；启动一个 Redis 实例验证日志输出。

### Q10: SHUTDOWN SAVE 触发 BGSAVE
**章节位置**: 2.2 关闭 — 第二步
**原文陈述**: "`SHUTDOWN SAVE` 会触发一次 `BGSAVE` 落盘（fork 子进程做 RDB）"
**待确认点**: `SHUTDOWN SAVE` 是否触发 `BGSAVE`（fork 子进程），而不是 `SAVE`（阻塞主进程）。
**建议验证来源**: Redis 源码 `server.c` 中 `shutdownCommand()` 或 `prepareForShutdown()` 函数；Redis 官方 `SHUTDOWN` 命令文档。

### Q11: SHUTDOWN NOSAVE 跳过落盘
**章节位置**: 2.2 关闭 — 第二步
**原文陈述**: "`SHUTDOWN NOSAVE` 直接跳过落盘，适合 Redis 当缓存用的场景，能做到秒级退出"
**待确认点**: `SHUTDOWN NOSAVE` 是否完全跳过 RDB 和 AOF 刷盘；"秒级退出"是否有可靠的性能依据。
**建议验证来源**: Redis 源码 `server.c` 中 `prepareForShutdown()` 函数（检查 NOSAVE 分支）；Redis 官方 `SHUTDOWN` 命令文档。

### Q12: RDB 和 AOF 使用"写临时文件再 rename"
**章节位置**: 2.2 关闭 — 第一步
**原文陈述**: "RDB 和 AOF 都用'写临时文件再 rename'的方式落盘"
**待确认点**: Redis 的 RDB 落盘和 AOF 重写是否确实使用"先写临时文件再 rename"的原子化落盘策略。
**建议验证来源**: Redis 源码 `rdb.c` 中 `rdbSave()` 和 `aof.c` 中 `rewriteAppendOnlyFileBackground()` 的实现。

### Q13: SIGTERM/SIGINT 触发优雅关闭
**章节位置**: 2.2 信号即协议
**原文陈述**: "Redis 把 SIGTERM/SIGINT 当作'操作系统请求我优雅退出'的信号，而不是立即终止的命令"
**待确认点**: Redis 是否将 SIGTERM 和 SIGINT 都注册为优雅关闭的触发信号。SIGINT 通常来自 Ctrl+C，SIGTERM 来自 kill/systemctl；两者处理方式是否确有区别。
**建议验证来源**: Redis 源码 `server.c` 中 `setupSignalHandlers()` 中的信号处理器注册；信号处理器函数 `sigShutdownHandler()`。

### Q14: systemctl stop redis 发送 SIGTERM
**章节位置**: 2.2 信号即协议
**原文陈述**: "`systemctl stop redis` 背后其实就是发一个 SIGTERM"
**待确认点**: systemd 的 `redis.service` 单元文件中 `KillSignal` 是否默认为 SIGTERM；`ExecStop` 是否有自定义的行为。
**建议验证来源**: Redis 的官方 systemd 服务单元文件；systemd `kill` 命令的默认信号行为。

## 2.3 MySQL 做法

### Q15: My.cnf 搜索优先级
**章节位置**: 2.3 启动 — 配置加载段
**原文陈述**: "按固定优先级搜索多个 my.cnf 路径（`/etc/my.cnf` 优先于 `~/.my.cnf` 等）"
**待确认点**: MySQL 读取 my.cnf 的搜索顺序是否以 `/etc/my.cnf` 为最优先；配置文件加载的完整顺序（包括 `/etc/mysql/my.cnf`、`/usr/local/mysql/etc/my.cnf` 等）是否如本章所述。
**建议验证来源**: MySQL 官方文档"Using Option Files"中关于配置文件搜索顺序的说明；`mysqld --help --verbose` 输出中的配置文件搜索路径。

### Q16: InnoDB 缓冲池初始化
**章节位置**: 2.3 启动 — InnoDB 段
**原文陈述**: "初始化缓冲池（Buffer Pool），这是 InnoDB 缓存数据页的内存区"
**待确认点**: InnoDB 缓冲池初始化是否确实是 InnoDB 启动后的第一个步骤。
**建议验证来源**: MySQL 源码 `storage/innobase/srv/srv0start.cc` 中 `innobase_start_or_create_for_mysql()` 函数的执行顺序；官方文档关于 InnoDB 启动过程的说明。

### Q17: ibdata 文件描述
**章节位置**: 2.3 启动 — InnoDB 段
**原文陈述**: "加载系统表空间（ibdata 文件），拿到数据字典"
**待确认点**: InnoDB 的系统表空间是否默认存储在 ibdata 文件中；数据字典是否存储在系统表空间中（注意 MySQL 8.0 已将部分数据字典从 ibdata 移至 mysql.ibd 等独立表空间）。
**建议验证来源**: MySQL 8.0 关于数据字典架构变更的官方文档（MySQL 8.0 引入了新的 Data Dictionary，与旧版本 ibdata 方式不同）；`SHOW VARIABLES LIKE 'innodb_data_file_path'`。

### Q18: 崩溃恢复读取 checkpoint LSN
**章节位置**: 2.3 启动 — InnoDB 段
**原文陈述**: "读 checkpoint LSN（日志序列号），从该位置扫描重做日志（redo log）"
**待确认点**: InnoDB 崩溃恢复是否从 checkpoint LSN 位置开始扫描 redo log。
**建议验证来源**: MySQL 官方文档 InnoDB Crash Recovery 部分；InnoDB 源码 `storage/innobase/log/log0recv.cc` 中恢复逻辑。

### Q19: Redo 重放无条件补回所有页修改
**章节位置**: 2.3 启动 — InnoDB 段
**原文陈述**: "redo 重放先无差别地把所有页修改补回去（恢复出崩溃瞬间的物理页状态，这一步不区分事务是否提交）"
**待确认点**: InnoDB 的崩溃恢复中，redo 重放阶段是否确实"不区分事务是否提交"，无条件重放所有 redo 记录的页修改。
**建议验证来源**: MySQL 官方文档关于 InnoDB redo log 和崩溃恢复的论述；InnoDB 恢复算法（ARIES 算法的变体）。

### Q20: Undo 回滚未提交事务
**章节位置**: 2.3 启动 — InnoDB 段
**原文陈述**: "undo 回滚再撤掉未提交事务留下的痕迹，最终恢复出严格的事务一致性——已提交的全部保留，未提交的全部回滚"
**待确认点**: InnoDB 崩溃恢复中，undo 回滚阶段是否只针对未提交事务；已提交事务是否在崩溃恢复中保持不变。
**建议验证来源**: MySQL 官方文档 InnoDB Crash Recovery 部分；ARIES 恢复算法理论。

### Q21: Redo 记录页级物理修改
**章节位置**: 2.3 启动 — InnoDB 段
**原文陈述**: "redo 本身只记录页级物理修改"
**待确认点**: InnoDB redo log 的记录格式是否为页级物理修改（如页号、偏移量、旧值/新值），而非逻辑操作描述。
**建议验证来源**: MySQL 官方文档 InnoDB Redo Log 部分的说明；InnoDB redo log 格式的源码文档。

### Q22: innodb_fast_shutdown 取值范围
**章节位置**: 2.3 关闭 — 表 2-1
**原文陈述**: "`innodb_fast_shutdown`，取 0、1、2 三档"（且表 2-1 描述了各档位的行为）
**待确认点**: `innodb_fast_shutdown` 是否只接受 0、1、2 三个值；表 2-1 中每个档位的行为描述是否准确：
  - 档位 0：刷所有脏页 + 完整 purge + change buffer 合并 + 完整 checkpoint
  - 档位 1：刷脏页但跳过完整 purge 与 change buffer 合并（默认）
  - 档位 2：只刷 redo 不刷数据页
**建议验证来源**: MySQL 官方文档 `innodb_fast_shutdown` 参数说明；MySQL 源码 `storage/innobase/srv/srv0start.cc` 中 `srv_fast_shutdown` 变量的使用。

### Q23: innodb_fast_shutdown 默认值
**章节位置**: 2.3 关闭 — 表 2-1
**原文陈述**: 表 2-1 中标明 "1 = 快速关闭（默认）"
**待确认点**: `innodb_fast_shutdown` 的默认值是否为 1。
**建议验证来源**: MySQL 官方文档 `innodb_fast_shutdown` 的默认值说明；`SHOW VARIABLES LIKE 'innodb_fast_shutdown'` 的输出（在 5.7 和 8.0 中分别验证）。

### Q24: 档位 0 启动时"几乎不需要崩溃恢复"
**章节位置**: 2.3 关闭 — 表 2-1
**原文陈述**: 表 2-1 档位 0 启动时行为："几乎不需要崩溃恢复，启动快"
**待确认点**: 使用 `innodb_fast_shutdown=0` 关闭后重启，是否确实"几乎不需要崩溃恢复"。
**建议验证来源**: MySQL 官方文档或社区经验关于不同关闭模式对重启恢复时间的影响。

### Q25: FLUSH PRIVILEGES 语义
**章节位置**: 2.3 网络层加权限系统段
**原文陈述**: "改完权限之后要执行 `FLUSH PRIVILEGES`——内存里的权限快照和磁盘表对不上，需要重新加载"
**待确认点**: MySQL 中修改权限表（如 `mysql.user`）后，是否必须执行 `FLUSH PRIVILEGES` 才能生效；`GRANT`/`REVOKE` 等语句是否自动加载到内存。
**建议验证来源**: MySQL 官方文档关于权限变更生效机制（`GRANT` 语句自动生效，而 `INSERT INTO mysql.user` 需要 `FLUSH PRIVILEGES`）。

### Q26: "每连接一线程"连接模型
**章节位置**: 2.3 服务循环段
**原文陈述**: "进入'每连接一线程'（或线程池）的连接处理"
**待确认点**: MySQL 是否默认使用"每连接一线程"（thread-per-connection）模型；MySQL 5.6+/8.0 的线程池（Thread Pool）插件如何工作（Enterprise Edition 和 Percona Server）。
**建议验证来源**: MySQL 官方文档关于连接处理模型和线程池的描述。

### Q27: 回滚是 redo 写入的逆过程
**章节位置**: 2.3 关闭慢的常见根因
**原文陈述**: "回滚是 redo 写入的逆过程，按 undo 记录逐条撤，比写入更慢"
**待确认点**: InnoDB 事务回滚在实现上是否可以被描述为"redo 写入的逆过程"；回滚速度是否通常比写入慢。
**建议验证来源**: InnoDB 源码中回滚（rollback）的实现机制；MySQL 官方文档关于回滚性能的说明。

### Q28: 长事务未提交时启动 undo 回滚慢
**章节位置**: 2.3 启动 — InnoDB 段
**原文陈述**: "大事务一旦在崩溃点未提交，启动期的 undo 回滚会非常慢"
**待确认点**: 崩溃恢复时，长事务的 undo 回滚是否因事务长度而显著变慢；是否有明确的机制导致这一现象。
**建议验证来源**: MySQL 官方文档关于长事务对崩溃恢复影响的分析。

### Q29: 从节点关闭时 binlog 同步等待
**章节位置**: 2.3 关闭慢的常见根因
**原文陈述**: "从节点二进制日志（binlog）同步等待（关闭要等从节点把 binlog 拉完）"
**待确认点**: MySQL 主节点关闭时是否确实等待从节点拉取完 binlog 才退出；超时机制是怎样的。
**建议验证来源**: MySQL 官方文档关于 `--skip-slave-start`、`--slave-net-timeout` 以及关闭时复制行为的描述。

### Q30: FTS 索引优化影响关闭
**章节位置**: 2.3 关闭慢的常见根因
**原文陈述**: "全文检索（FTS）索引优化在跑"
**待确认点**: InnoDB 全文检索索引的优化（OPTIMIZE TABLE）是否确实会延迟 MySQL 的关闭。
**建议验证来源**: MySQL 官方文档关于全文检索索引和关闭行为的描述。

## 2.4 Kafka 做法

### Q31: KRaft 3.3 生产可用（KIP-833）
**章节位置**: 2.4 启动 — 元数据管理初始化
**原文陈述**: "KRaft 模式自 3.3 起对新集群进入生产可用（KIP-833）"
**待确认点**: Kafka 3.3 是否将 KRaft 模式标记为对新集群生产可用；是否对应 KIP-833。
**建议验证来源**: Kafka 3.3.0 release notes；KIP-833 状态。

### Q32: ZooKeeper 模式 3.5 标记弃用
**章节位置**: 2.4 启动 — 元数据管理初始化
**原文陈述**: "3.5 起 ZooKeeper 模式被标记弃用"
**待确认点**: Kafka 3.5 是否正式将 ZooKeeper 模式标记为 deprecated。
**建议验证来源**: Kafka 3.5.0 release notes；Kafka 官方博文关于 ZK 移除时间线的说明。

### Q33: ZK→KRaft 迁移工具版本演进
**章节位置**: 2.4 启动 — 元数据管理初始化
**原文陈述**: "ZK→KRaft 迁移工具在 3.4 以 Early Access 引入、3.5–3.6 为 preview、3.8 起进入生产可用"
**待确认点**: 迁移工具在各个 Kafka 版本中的成熟度标记是否准确：
  - 3.4: Early Access
  - 3.5–3.6: preview
  - 3.8: 生产可用
**建议验证来源**: Kafka 各版本 release notes；KIP-852（KRaft 迁移工具）的进展记录。

### Q34: 3.9 是最后一个支持 ZK 的 bridge release
**章节位置**: 2.4 启动 — 元数据管理初始化
**原文陈述**: "3.9 是最后一个支持 ZK 模式的 bridge release"
**待确认点**: Kafka 3.9 发布时是否确实被标记为最后一个支持 ZooKeeper 模式的 bridge release。
**建议验证来源**: Kafka 3.9.0 release notes；Apache Kafka 官方 ZK 移除路线图。

### Q35: 4.0 彻底移除 ZooKeeper
**章节位置**: 2.4 启动 — 元数据管理初始化
**原文陈述**: "4.0 彻底移除 ZooKeeper"
**待确认点**: Kafka 4.0 是否已移除所有 ZooKeeper 依赖。
**建议验证来源**: Kafka 4.0 release notes（如已发布）；Apache Kafka 官方公告。

### Q36: KRaft 元数据用 Raft 复制
**章节位置**: 2.4 启动 — 元数据管理初始化
**原文陈述**: "元数据本身变成了一份用 Raft 复制的日志"
**待确认点**: KRaft 模式下的元数据复制是否使用 Raft 共识算法。
**建议验证来源**: Kafka KIP-500（KRaft）设计文档；KRaft 源码中的 Raft 实现。

### Q37: num.recovery.threads.per.data.dir 配置
**章节位置**: 2.4 启动 — 日志管理器启动
**原文陈述**: "靠 `num.recovery.threads.per.data.dir` 并行加速"
**待确认点**: Kafka 启动恢复时是否使用 `num.recovery.threads.per.data.dir` 控制并行恢复线程数；该配置的确切名称和默认值。
**建议验证来源**: Kafka 官方文档关于 `num.recovery.threads.per.data.dir` 的说明。

### Q38: Processor 默认 3 个
**章节位置**: 2.4 启动 — 三层网络
**原文陈述**: "Processor（默认 3 个，对应 `num.network.threads`）"
**待确认点**: Kafka 的 `num.network.threads` 默认值是否为 3。
**建议验证来源**: Kafka 官方文档 `num.network.threads`；Kafka 源码 `core/src/main/scala/kafka/server/KafkaConfig.scala` 中的默认值定义。

### Q39: Handler 线程池默认 8
**章节位置**: 2.4 启动 — 三层网络
**原文陈述**: "Handler 线程池（`num.io.threads` 控制，默认 8）"
**待确认点**: Kafka 的 `num.io.threads` 默认值是否为 8。
**建议验证来源**: Kafka 官方文档 `num.io.threads`；Kafka 源码中 `KafkaConfig.scala` 的默认值定义。

### Q40: Acceptor 线程 1 个
**章节位置**: 2.4 启动 — 三层网络
**原文陈述**: "最外层 Acceptor（1 个）负责接收新连接"
**待确认点**: Kafka 网络层是否只有一个 Acceptor 线程。
**建议验证来源**: Kafka 源码 `network` 包中 Acceptor 的相关实现（`kafka.network.Acceptor`）。

### Q41: 三层网络请求队列实现
**章节位置**: 2.4 启动 — 三层网络
**原文陈述**: "把请求塞进共享的请求队列...把响应塞回每个 Processor 一个的响应队列"
**待确认点**: Kafka 网络层是否使用一个共享请求队列（request queue）和每个 Processor 一个的响应队列（response queue）。
**建议验证来源**: Kafka 源码 `kafka.network.RequestChannel` 的实现。

### Q42: "[KafkaServer id=0] started" 日志
**章节位置**: 2.4 启动 — 第八阶段
**原文陈述**: "Kafka 才对外打印 `[KafkaServer id=0] started` 这条就绪日志"
**待确认点**: Kafka Broker 启动后的就绪日志是否确实是 `[KafkaServer id=0] started`（注意格式和方括号）。
**建议验证来源**: Kafka 源码 `core/src/main/scala/kafka/server/KafkaServer.scala` 中的 `startup()` 方法。

### Q43: 普通关闭不告知 Controller
**章节位置**: 2.4 关闭 — 普通关闭
**原文陈述**: "它不主动告知 Controller 自己要走——Controller 是在 Broker 退出后通过心跳 / 会话超时才发现它没了"
**待确认点**: Kafka 普通关闭是否确实不主动通知 Controller；Controller 检测 Broker 不可用是否通过心跳/会话超时机制。
**建议验证来源**: Kafka 源码 `server/KafkaServer.scala` 中 `shutdown()` 方法的实现；Kafka 心跳超时机制文档。

### Q44: 受控关闭发送请求给 Controller
**章节位置**: 2.4 关闭 — 受控关闭
**原文陈述**: "Broker 在真正退出之前，先发请求给 Controller，告诉它'我要走了'"
**待确认点**: 受控关闭（Controlled Shutdown）中 Broker 是否确实向 Controller 发送一个明确的关闭请求。
**建议验证来源**: Kafka 源码 `server/KafkaServer.scala` 中 `controlledShutdown()` 方法；受控关闭协议规范。

### Q45: Controller 发送 LeaderAndIsr 请求
**章节位置**: 2.4 关闭 — 受控关闭
**原文陈述**: "它会向这些副本发 LeaderAndIsr 请求，让它们接任 Leader"
**待确认点**: Controller 在受控关闭过程中是否使用 `LeaderAndIsr` 请求来实现 Leader 迁移。
**建议验证来源**: Kafka 源码 `controller/KafkaController.scala` 中的受控关闭处理逻辑。

### Q46: controlled.shutdown.enable 默认开启
**章节位置**: 2.4 关闭 — 受控关闭异常路径
**原文陈述**: "受控关闭由开关 `controlled.shutdown.enable`（默认开启，只读参数）控制是否启用"
**待确认点**: `controlled.shutdown.enable` 的默认值是否为 true；该参数是否被标记为只读（read-only）。
**建议验证来源**: Kafka 官方文档 `controlled.shutdown.enable`；`KafkaConfig.scala` 中的参数定义。

### Q47: controlled.shutdown.max.retries 与 controlled.shutdown.retry.backoff.ms
**章节位置**: 2.4 关闭 — 受控关闭异常路径
**原文陈述**: "`controlled.shutdown.max.retries` 与 `controlled.shutdown.retry.backoff.ms` 控制重试次数与退避间隔"
**待确认点**: 这两个参数是否存在；默认值是多少；在 KRaft 模式下参数名是否与 ZK 模式一致。
**建议验证来源**: Kafka 官方文档关于受控关闭参数的说明。

### Q48: Kafka 日志恢复为"截断到最后一致位移"
**章节位置**: 2.4 追加写日志
**原文陈述**: "恢复时，Kafka 只需要'找到最后一段完整写入的位移（offset）并截断未完整部分'"
**待确认点**: Kafka 日志恢复在崩溃后是否只做截断（truncate）到最后一个完整记录的位置；是否不需要重放或回滚。
**建议验证来源**: Kafka 官方文档关于日志恢复的说明；源码 `log/Log.scala` 中的 `recoverSegmentOperations` 或类似方法。

### Q49: 日志"不存在'写了一半'的中间状态"
**章节位置**: 2.4 追加写日志
**原文陈述**: "一条日志要么完整写入、要么不写，不存在'写了一半'的中间状态需要回滚"
**待确认点**: Kafka append-only 日志的写入是否保证 either fully written or not；是否存在部分写入（partial write）情况需要 CRC 校验来发现。
**建议验证来源**: Kafka 日志格式规范中的 CRC 校验机制说明。

## 2.2 / 2.3 / 2.4 跨节综合

### Q50: Redis appendfsync everysec 默认 ~1 秒数据窗口
**章节位置**: 本章导读
**原文陈述**: "everysec 默认是约 1 秒量级的数据窗口"
**待确认点**: Redis `appendfsync everysec` 策略下，崩溃时丢失的数据是否约为 1 秒；`appendfsync everysec` 是否确实是 Redis 的默认配置（AOF 开启时）。
**建议验证来源**: Redis 官方文档 `appendfsync` 参数说明；Redis 源码中 AOF 刷盘的实现。

### Q51: Redis "纯 RDB 则丢自上次快照起的全部"
**章节位置**: 本章导读
**原文陈述**: "纯 RDB 则丢自上次快照起的全部"
**待确认点**: 纯 RDB 模式（仅 RDB，无 AOF）下，崩溃丢失的数据是否为自上次 RDB 快照时间点以来的全部数据。
**建议验证来源**: Redis 官方文档关于 RDB 持久化策略的说明。

### Q52: MySQL 关闭时等待从节点拉取 binlog
**章节位置**: 2.3 关闭慢的常见根因
**原文陈述**: "从节点二进制日志（binlog）同步等待（关闭要等从节点把 binlog 拉完）"
**待确认点**: MySQL 5.7/8.0 中，主节点关闭时是否确实等待从节点完全拉取完 binlog 才退出；控制该行为的参数（如 `--master-retry-count` 等）。
**建议验证来源**: MySQL 官方文档关于关闭时复制行为的描述；`SHOW SLAVE STATUS` 中 Seconds_Behind_Master 与关闭的相关性。

### Q53: "内存键值对 + 单线程"描述 Redis
**章节位置**: 2.5 横向对比
**原文陈述**: "Redis 的数据结构最简单（内存键值对 + 单线程），恢复就是重放命令"
**待确认点**: Redis 6.0+ 引入了多线程 I/O（网络 I/O 多线程），虽然命令执行仍是主线程；"单线程"描述是否需注明范围。
**建议验证来源**: Redis 官方文档关于线程模型的说明。

### Q54: Kafka 万分区启动耗时
**章节位置**: 2.6 启示一
**原文陈述**: "比如 Kafka 万分区启动要几分钟"
**待确认点**: 一万个分区的 Kafka Broker 启动时间是否确实以"分钟"计；有无参考数据或官方指南提到分区数与启动时间的关系。
**建议验证来源**: Kafka 官方运维指南关于分区数对启动时间影响的说明；社区基准测试数据。

## 2.5 横向对比表 — 综合验证

### Q55: MySQL "默认最保守"
**章节位置**: 2.5 横向对比 — 表 2-2 第三行
**原文陈述**: 表 2-2 MySQL 列："默认最保守，三档可调（`innodb_fast_shutdown`）"
**待确认点**: `innodb_fast_shutdown` 默认值为 1（快速关闭），"默认最保守"的描述是否准确；这里是否指关闭行为默认最保守，还是指 MySQL 整体关闭行为相对 Redis/Kafka 更保守。
**建议验证来源**: 对照 MySQL 官方文档中 `innodb_fast_shutdown` 的默认值和行为。

### Q56: MySQL 关闭"慢且不可预测"
**章节位置**: 2.5 横向对比 — 表 2-2 第五行
**原文陈述**: 表 2-2 MySQL 列："慢且不可预测（事务回滚 + 脏页）"
**待确认点**: MySQL 关闭是否普遍被认为是"慢且不可预测"；关闭时是否需要回滚所有活动事务。
**建议验证来源**: MySQL 官方文档关于 InnoDB 关闭流程的说明；社区运维实战经验。

### Q57: Kafka "强制刷盘，无选项"
**章节位置**: 2.5 横向对比 — 表 2-2 第三行
**原文陈述**: 表 2-2 Kafka 列："强制刷盘，无选项"
**待确认点**: Kafka 关闭时是否强制刷新所有未写入磁盘的日志数据；是否有任何参数可以跳过此刷盘行为。
**建议验证来源**: Kafka 源码 `Log.scala` 中的 `flush()` 调用在关闭流程中的位置。

### Q58: Redis "仅刷脏"
**章节位置**: 2.5 横向对比 — 表 2-2 第五行
**原文陈述**: 表 2-2 Redis 列："快（仅刷脏）"
**待确认点**: Redis 关闭时是否仅刷新脏数据（dirty data）；Redis 关闭操作为何"快"——数据库结构简单和单线程是否为主要原因。
**建议验证来源**: Redis 源码中 `prepareForShutdown()` 的刷盘范围确认。

## 2.6 架构启示

### Q59: Oracle MySQL 与 Percona/MariaDB 的歧义
**章节位置**: 全局
**原文陈述**: 全章使用"MySQL"指代，未区分 Oracle MySQL、Percona Server、MariaDB
**待确认点**: 书中"MySQL"是否特指 Oracle MySQL；`innodb_fast_shutdown`、崩溃恢复机制等在 Percona Server 和 MariaDB 中是否与 Oracle MySQL 行为一致。MariaDB 的 XtraDB 与 InnoDB 在这些行为上是否有差异。
**建议验证来源**: 对比 Oracle MySQL、Percona Server、MariaDB 在 `innodb_fast_shutdown` 和崩溃恢复上的实现差异。
