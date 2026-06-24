# 第04章《分层架构》事实核查问题清单

---

## 4.1 问题的本质：为什么必须分层

> 本章该节未包含需要事实核查的硬性数字/版本/API 声明。核心论点（分层解决关注点分离、修改局部性、可替换性）是设计原则性论述，不涉及可验证的技术事实。跳过。

---

## 4.2 Redis 的做法

### 4.2.1 交互层：RESP 与单线程多路复用

### Q1: RESP 协议前缀字符约定
**章节位置**: 4.2.1
**原文陈述**: "每段数据用前缀字符区分类型（`+` 简单字符串、`-` 错误、`:` 整数、`$` 批量字符串、`*` 数组）"
**待确认点**: RESP 协议中这五种前缀的语义是否完全准确。是否有遗漏类型（如 `_` null、`,` double、`#` boolean 等在 RESP3 中引入的类型）？本章上下文基于 RESP2 还是 RESP3？
**建议验证来源**: Redis 官方协议文档（https://redis.io/docs/reference/protocol-spec/）

### Q2: RESP 分隔符约定
**章节位置**: 4.2.1
**原文陈述**: "用 `\r\n` 分隔"
**待确认点**: RESP 协议是否全部使用 `\r\n` 作为分隔符（包括 inline commands 等场景）。
**建议验证来源**: Redis 官方协议文档

### Q3: 6.0 之前 Redis 网络 IO 与命令执行同一线程
**章节位置**: 4.2.1
**原文陈述**: "在 6.0 之前，Redis 的网络 IO 和命令执行在同一个线程里"
**待确认点**: Redis 6.0 之前的线程模型是否确实网络 IO 与命令执行在同一线程。6.0 是否是引入多线程 IO 的第一个版本。
**建议验证来源**: Redis 6.0 release notes、antirez blog post on Redis multi-threaded IO

### Q4: 6.0 多线程 IO 只分离读写系统调用和 buffer 拷贝
**章节位置**: 4.2.1
**原文陈述**: "6.0 引入...多线程 IO 只动了一件东西：把协议的**读写**（`read`/`write` 系统调用和大块 buffer 拷贝）拆给一组 IO 线程，**命令执行依然在主线程单线程串行**"
**待确认点**: 多线程 IO 的职责范围是否如所述仅限 read/write 系统调用和大块 buffer 拷贝。命令执行是否确实保持单线程串行。
**建议验证来源**: Redis 6.0 源码 `networking.c`、Redis 官方文档关于多线程 IO 的说明

### Q5: 7.x 默认关闭多线程 IO
**章节位置**: 4.2.1
**原文陈述**: "7.x 默认仍然关闭多线程 IO——它是个可选优化"
**待确认点**: Redis 7.x 系列中 `io-threads` 配置的默认值是否为 1（即默认关闭）。不同 7.x 小版本是否一致。
**建议验证来源**: Redis 7.x 配置文件默认值、`redis.conf` 中 `io-threads` 的注释

### Q6: 客户端输出缓冲区固定区默认 16KB
**章节位置**: 4.2.1
**原文陈述**: "每个客户端连接有两个写缓冲区，一个固定大小（默认 16KB），一个动态增长"
**待确认点**: 固定大小缓冲区的默认值是否为 16KB。这个默认值在哪次版本变更过。
**建议验证来源**: Redis 源码 `server.h` 中 `client` 结构体对输出缓冲区的定义、`redis.conf` 默认值

### Q7: client-output-buffer-limit 配置项
**章节位置**: 4.2.1
**原文陈述**: "但有上限（可配置 `client-output-buffer-limit`），超限就强制关闭连接"
**待确认点**: `client-output-buffer-limit` 的默认值是多少；超限后的行为是否一定是强制关闭连接（hard limit vs soft limit 的区别）。
**建议验证来源**: Redis 官方文档、`redis.conf` 中 `client-output-buffer-limit` 说明

### 4.2.2 逻辑层：命令表 + robj 统一抽象

### Q8: redisCommandTable 定义位置
**章节位置**: 4.2.2
**原文陈述**: "这张表叫 `redisCommandTable`，定义在 `server.c` 里"
**待确认点**: `redisCommandTable` 是否确实定义在 `server.c` 中（而非其他文件如 `server.h` 或拆分后的命令文件）。
**建议验证来源**: Redis 源码目录结构，`server.c` 中 `redisCommandTable` 定义位置

### Q9: 命令分派流水线各步骤顺序
**章节位置**: 4.2.2
**原文陈述**: "RESP 解析完得到参数数组 `argv` 和参数个数 `argc` → 用命令名做一次 dict 哈希查到命令表条目 → ACL 权限校验和 arity 校验 → 调用 `cmd->proc(client)` 执行 → 跑慢查询日志和 MONITOR 钩子"
**待确认点**: 命令执行流水线各步骤的顺序是否准确。ACL 校验是在 arity 校验之前还是之后？MONITOR 钩子的触发时机是否在执行后？
**建议验证来源**: Redis 源码 `server.c` 中的 `processCommand()` 或 `call()` 函数

### Q10: 7.0 起 listpack 全面取代 ziplist
**章节位置**: 4.2.2
**原文陈述**: "7.0 起 listpack 全面取代了旧版 ziplist，成为哈希、列表（作为 quicklist 的节点）、有序集合这三种小集合场景的紧凑编码"
**待确认点**: Redis 7.0 是否确实用 listpack 全面取代 ziplist 在哈希、列表（作为 quicklist 节点）、有序集合（zset）中的角色。有没有例外场景仍保留 ziplist。
**建议验证来源**: Redis 7.0 release notes、Redis 源码中对 listpack 和 ziplist 的使用情况

### Q11: ziplist 连锁更新导致 O(n²) 级联搬移
**章节位置**: 4.2.2
**原文陈述**: "这是为了消除 ziplist 著名的"连锁更新"问题（一个元素长度变化引发 O(n²) 级联搬移）"
**待确认点**: ziplist 连锁更新的时间复杂度是否为 O(n²)。实际最坏情况是什么。
**建议验证来源**: Redis 源码中 ziplist.c 的注释、相关技术文章分析

### Q12: hash 从 listpack 升级到 hashtable 的阈值
**章节位置**: 4.2.2
**原文陈述**: "同一个 type 可以挂不同的 encoding，比如一个哈希在小数据量时用 listpack（紧凑连续内存），膨胀到阈值后自动升级为 hashtable"
**待确认点**: 这个"阈值"是多少（默认配置值如 `hash-max-listpack-entries` 和 `hash-max-listpack-value` 的具体默认值）。不同 Redis 版本之间是否有变化。
**建议验证来源**: Redis 配置文件 `redis.conf` 默认值、`hash-max-listpack-entries` / `hash-max-listpack-value`

### 4.2.3 存储层：内存管理 + 持久化双轨

### Q13: Redis 默认内存分配器为 jemalloc
**章节位置**: 4.2.3
**原文陈述**: "Redis 默认用 jemalloc"
**待确认点**: Redis 是否默认使用 jemalloc 作为内存分配器。是否有编译选项可替换为 tcmalloc 或标准 malloc。
**建议验证来源**: Redis 源码 Makefile、README、jemalloc 集成文档

### Q14: 内存淘汰策略列举
**章节位置**: 4.2.3
**原文陈述**: "按配置的策略（`noeviction`、`allkeys-lru`、`volatile-lru`、`allkeys-lfu` 等）选出该被清理的键"
**待确认点**: Redis 支持的全部淘汰策略是否完整列出（如缺少 `volatile-lfu`、`allkeys-random`、`volatile-random`、`volatile-ttl`）。
**建议验证来源**: Redis 官方文档 `maxmemory-policy` 配置项说明

### Q15: LRU 近似实现方式
**章节位置**: 4.2.3
**原文陈述**: "LRU 用近似实现——每次随机采样若干个键，从中淘汰最久未用的，避免维护全局 LRU 链表的开销"
**待确认点**: Redis LRU 近似的采样数（`maxmemory-samples`）默认值是多少。算法是否确实如所述。
**建议验证来源**: Redis 官方文档、源码 `evict.c`

### Q16: LFU 使用计数加衰减
**章节位置**: 4.2.3
**原文陈述**: "LFU 用计数加衰减，让访问频率随时间淡化"
**待确认点**: LFU 的具体实现机制——计数器是 morris counter（对数近似）还是普通计数器？衰减的逻辑是什么（定期半衰衰减还是每次访问时衰减）？
**建议验证来源**: Redis 源码 `evict.c` 中 LFU 实现、Redis 官方文档

### Q17: 惰性删除 4.0 引入
**章节位置**: 4.2.3
**原文陈述**: "惰性删除（lazy free），4.0 引入"
**待确认点**: Lazy free 是否在 Redis 4.0 首次引入。涉及的具体命令/场景（`UNLINK`、`FLUSHALL ASYNC` 等）是否同时引入。
**建议验证来源**: Redis 4.0 release notes、`UNLINK` 命令文档

### Q18: 4.0 起支持混合重写
**章节位置**: 4.2.3
**原文陈述**: "4.0 起支持混合重写（重写时把当前快照作为 AOF 的开头）"
**待确认点**: AOF 混合持久化是否在 Redis 4.0 引入。机制是否如所述（快照作为 AOF 文件开头）。配置项 `aof-use-rdb-preamble` 的默认值。
**建议验证来源**: Redis 4.0 release notes、AOF 持久化文档

### Q19: 两种持久化均可关闭
**章节位置**: 4.2.3
**原文陈述**: "两者都可以关闭。你可以把 Redis 跑成纯内存、重启即丢的缓存"
**待确认点**: 是否确实完全禁用 RDB 和 AOF（配置 `save ""` 和不配置任何 AOF 选项）即可实现纯内存模式，重启后数据不恢复。
**建议验证来源**: Redis 配置文档

### Q20: RocksDB-Cloud 和 Redis on Flash 项目提及
**章节位置**: 4.2.3
**原文陈述**: "这恰恰是后来 RocksDB-Cloud、Redis on Flash 这类项目想补的空缺，但它们是外部方案，不是 Redis 内建能力"
**待确认点**: RocksDB-Cloud 和 Redis on Flash 是否确实是相关的外部项目。Redis on Flash 是否为 Redis Labs (现 Redis Inc.) 的商业/开源项目。
**建议验证来源**: Redis on Flash (Redis Enterprise)、RocksDB-Cloud 项目文档

### 4.2.4 层间通信

> 本节所述"全程无序列化、无虚函数"、"函数指针实现命令分派"等属于对前述内容的总结性论述。如前述各点已验证，本节无需额外核查。

---

## 4.3 MySQL 的做法

### 4.3.1 交互层：连接、认证与线程模型

### Q21: MySQL 支持四种连接方式
**章节位置**: 4.3.1
**原文陈述**: "它支持四种连接方式：TCP/IP（最常用）、Unix Socket（本机通信）、共享内存（Windows）、命名管道（Windows 历史遗留）"
**待确认点**: MySQL 是否确实支持这四种连接类型。共享内存和命名管道是否仅限 Windows 平台。命名管道是否确实是"历史遗留"。
**建议验证来源**: MySQL 官方文档关于连接方式的说明

### Q22: MySQL 8.0 默认认证插件 caching_sha2_password
**章节位置**: 4.3.1
**原文陈述**: "MySQL 8.0 默认使用 `caching_sha2_password`"
**待确认点**: MySQL 8.0 的默认认证插件是否确实是 `caching_sha2_password`。`mysql_native_password` 是否确实是旧的默认认证插件。
**建议验证来源**: MySQL 8.0 release notes、MySQL 官方认证文档

### Q23: 认证插件可对接 LDAP、Kerberos
**章节位置**: 4.3.1
**原文陈述**: "认证插件可对接 LDAP、Kerberos 等外部身份系统"
**待确认点**: MySQL 是否官方支持 LDAP 和 Kerberos 认证插件。它们是企业版功能还是社区版也支持。
**建议验证来源**: MySQL 官方文档认证插件章节

### Q24: MySQL 默认线程模型为 thread-per-connection
**章节位置**: 4.3.1
**原文陈述**: "默认 thread-per-connection：每个连接一个独立线程"
**待确认点**: 这个默认值在不同 MySQL 版本中是否保持不变。MySQL 5.6/5.7/8.0 的线程模型默认设置。
**建议验证来源**: MySQL 官方文档关于线程模型的说明

### Q25: 线程池存在于企业版/Percona/MariaDB
**章节位置**: 4.3.1
**原文陈述**: "另一种是线程池（企业版/Percona/MariaDB）：固定线程服务所有连接"
**待确认点**: MySQL 线程池（Thread Pool）在哪些版本/分支中可用。MySQL Enterprise 的 Thread Pool 插件和 MariaDB 的 thread pool 是否实现相同。
**建议验证来源**: MySQL Enterprise Thread Pool 文档、Percona Server 文档、MariaDB Thread Pool 文档

### Q26: THD 名称含义
**章节位置**: 4.3.1
**原文陈述**: "**`THD`（类名 `THD`，源码里通常理解为 thread descriptor / 线程描述符，MySQL 官方文档并未给出权威展开）**"
**待确认点**: THD 在 MySQL 源码中的官方展开是什么。MySQL 官方文档是否确实没有给出权威展开。
**建议验证来源**: MySQL 源码中 THD 类的注释、MySQL 内部文档

### 4.3.2 逻辑层：SQL 全生命周期的三段切分

### Q27: bison 解析器和语法文件 sql_yacc.yy
**章节位置**: 4.3.2
**原文陈述**: "**解析器（Parser）** 由 bison 生成（语法文件 `sql_yacc.yy`）"
**待确认点**: MySQL 解析器是否确实使用 bison 生成。语法文件是否确实名为 `sql_yacc.yy`（不同版本文件名可能有变，如 8.0 拆分后的文件）。
**建议验证来源**: MySQL 8.0 源码 `sql/` 目录结构

### Q28: 预处理阶段做语义检查的范围
**章节位置**: 4.3.2
**原文陈述**: "再按 SQL 语法规则建出解析树，然后进入预处理阶段做语义检查（表存不存在、列存不存在、权限够不够）"
**待确认点**: 权限检查是在解析/预处理阶段还是在执行阶段。语义检查的范围是否如所述。
**建议验证来源**: MySQL 源码 sql/sql_yacc.yy、sql/sql_resolver.cc

### Q29: 8.0 引入直方图
**章节位置**: 4.3.2
**原文陈述**: "8.0 引入的直方图让优化器能对没有索引的列做数据分布感知的判断"
**待确认点**: MySQL 8.0 是否引入了直方图（Histogram）功能。用途是否如所述（帮助优化器对非索引列做数据分布感知）。
**建议验证来源**: MySQL 8.0 release notes、MySQL 官方文档关于 Histogram 的说明

### Q30: 优化器包含常量折叠、范围优化、JOIN 顺序搜索
**章节位置**: 4.3.2
**原文陈述**: "优化手段包括常量折叠、范围优化、直方图（8.0）辅助索引选择、JOIN 顺序搜索等"
**待确认点**: MySQL 优化器是否确实包含常量折叠（constant folding）、范围优化（range optimization）、JOIN 顺序搜索（join order search）。这些术语的准确性。
**建议验证来源**: MySQL 官方文档关于优化器的章节

### Q31: 执行器按"读取一行评估一行"的循环
**章节位置**: 4.3.2
**原文陈述**: "调用 handler 接口读一行 → 评估 WHERE 条件 → 聚合或返回 → 再读下一行。每一行读写都是一次对存储引擎的虚函数调用"
**待确认点**: MySQL 执行器是否确实使用"读一行评估一行"的火山模型（Volcano-style iteration model）。
**建议验证来源**: MySQL 源码 sql/executor.cc 或 sql/sql_executor.cc 实现

### Q32: 查询缓存 8.0 彻底移除
**章节位置**: 4.3.2
**原文陈述**: "**查询缓存（Query Cache）**。MySQL 5.x 时代有个功能...却在 8.0 被彻底移除"
**待确认点**: MySQL 8.0 是否确实彻底移除了 Query Cache。移除的具体版本是 8.0.0 还是稍晚版本。
**建议验证来源**: MySQL 8.0 release notes、MySQL 官方文档关于 Query Cache 的说明

### Q33: 查询缓存按 SQL 文本做 key
**章节位置**: 4.3.2
**原文陈述**: "把 SELECT 的结果按 SQL 文本做 key 缓存"
**待确认点**: Query Cache 的 key 是否精确到 SQL 文本（包括大小写、空格等差异的处理逻辑）。
**建议验证来源**: MySQL 官方文档、源码 query_cache.cc

### Q34: 查询缓存失效的机制描述
**章节位置**: 4.3.2
**原文陈述**: "任何一张表的任何一次写，都要去检查所有引用了这张表的缓存项并使之失效"
**待确认点**: Query Cache 失效的粒度是否真的涉及检查"所有引用了这张表的缓存项"。失效操作在高写入负载下开销是否确实超过收益。
**建议验证来源**: MySQL 源码 query_cache.cc、MySQL 官方文档

### 4.3.3 存储层：Handler API 与可插拔引擎

### Q35: Handler API 方法列举
**章节位置**: 4.3.3
**原文陈述**: "表级的方法（`open` / `close`）、行级的方法（`rnd_init` / `rnd_next` 顺序扫描、`index_init` / `index_read` 索引扫描）、事务相关的方法（`external_lock` / `start_stmt` / `commit` / `rollback`）"
**待确认点**: 所列方法名是否准确反映 Handler API 中的函数名。`external_lock` 和 `start_stmt` 的语义是否正确。
**建议验证来源**: MySQL 源码 include/mysql/handler.h（或 sql/handler.h）

### Q36: InnoDB 是默认引擎
**章节位置**: 4.3.3
**原文陈述**: "InnoDB 是默认引擎"
**待确认点**: MySQL 从哪个版本起默认引擎从 MyISAM 改为 InnoDB（MySQL 5.5+）。
**建议验证来源**: MySQL 官方文档

### Q37: MyISAM 全文索引比 InnoDB 好
**章节位置**: 4.3.3
**原文陈述**: "MyISAM 是老引擎，无事务、表锁，但全文索引曾经比 InnoDB 好"
**待确认点**: MyISAM 的全文索引是否在某些方面优于 InnoDB。InnoDB 从哪个版本开始支持全文索引（InnoDB 5.6+）。
**建议验证来源**: MySQL 官方全文索引文档

### Q38: Memory 引擎使用哈希索引、重启即失
**章节位置**: 4.3.3
**原文陈述**: "Memory 引擎把数据放内存、用哈希索引、重启即失"
**待确认点**: Memory 引擎默认是否使用哈希索引。是否也支持 B-Tree 索引。重启后数据是否会永久丢失。
**建议验证来源**: MySQL 官方文档 Memory Storage Engine

### Q39: Archive、NDB、RocksDB (MyRocks) 列于可插拔引擎清单
**章节位置**: 4.3.3
**原文陈述**: "此外还有 Archive（压缩归档）、NDB（Cluster）、第三方引擎如 RocksDB（Percona 的 MyRocks）等数十种"
**待确认点**: Archive 引擎是否专注于压缩归档。NDB 是否为集群引擎。MyRocks 是否为 Percona 的 RocksDB 集成方案。引擎数量是否真的达到"数十种"。
**建议验证来源**: MySQL 官方文档存储引擎列表、Percona MyRocks 文档

### Q40: 同实例不同表可用不同引擎
**章节位置**: 4.3.3
**原文陈述**: "可以在同一个 MySQL 实例里并存——同一份数据库里，不同表可以挂不同引擎"
**待确认点**: MySQL 是否确实允许在同一实例/数据库内不同表使用不同存储引擎。
**建议验证来源**: MySQL 官方文档 CREATE TABLE 语法关于 ENGINE 选项

### Q41: InnoDB 文件组织
**章节位置**: 4.3.3
**原文陈述**: "InnoDB 用 `.ibd` 表空间存数据和索引、`ib_logfile` 存重做日志、`undo_*` 存回滚日志"
**待确认点**: InnoDB 的重做日志文件是否默认命名为 `ib_logfile0` / `ib_logfile1`（而不是 `ib_logfile` 单数形式）。回滚日志是否确实以 `undo_*` 命名（MySQL 8.0 中 undo 表空间是否默认命名不同）。
**建议验证来源**: MySQL 官方文档 InnoDB 文件组织结构、实际 MySQL 数据目录

### Q42: 双写缓冲（doublewrite buffer）防止页撕裂
**章节位置**: 4.3.3
**原文陈述**: "再配合双写缓冲（doublewrite buffer）防止页撕裂"
**待确认点**: doublewrite buffer 的主要作用是否确实是防止页撕裂（partial page write）。其机制是否如常规理解。
**建议验证来源**: MySQL 官方文档 InnoDB Doublewrite Buffer

### Q43: Handler 虚函数多态开销的描述
**章节位置**: 4.3.3
**原文陈述**: "handler 通过虚函数（vtable）多态调用，每次行操作都过一次虚函数表。这意味着一个全表扫描的每一行、一个索引查找的每一次定位，都是一次间接调用，无法被内联优化"
**待确认点**: MySQL Handler API 是否使用 C++ 虚函数（vtable）。每次行操作是否确实经过一次虚函数间接调用，从而阻止编译期内联。
**建议验证来源**: MySQL 源码 handler.h 类定义、MySQL 性能相关分析文章

### Q44: PostgreSQL 与 MySQL 引擎抽象对比
**章节位置**: 4.3.3
**原文陈述**: "PostgreSQL 的 table access method 虽然也抽象但与执行器结合更紧"
**待确认点**: PostgreSQL 是否确实有 table access method 抽象层。它与 MySQL Handler API 在设计上的区别是否如所述（"与执行器结合更紧"）。
**建议验证来源**: PostgreSQL 官方文档关于 Table Access Method 的说明

### 4.3.4 层间通信

### Q45: Linux Native AIO 使用 io_submit
**章节位置**: 4.3.4
**原文陈述**: "引擎层到操作系统：文件 API（`pread` / `pwrite`）和 Native AIO（Linux 上的 `io_submit`）"
**待确认点**: InnoDB 在 Linux 上是否使用 Linux Native AIO（`io_submit` / `io_getevents`）。MySQL 从哪个版本开始支持 Linux AIO。
**建议验证来源**: MySQL 源码 InnoDB 文件 I/O 相关代码（如 os_file.cc）

---

## 4.4 Kafka 的做法

### 4.4.1 交互层：SocketServer 与 Reactor 多线程模型

### Q46: Kafka 网络层受 Netty Reactor 启发
**章节位置**: 4.4.1
**原文陈述**: "它受 Netty 的 Reactor 模式启发，但用 Scala 实现"
**待确认点**: Kafka 的网络层实现是否确实受 Netty 的 Reactor 模式启发。Kafka 自有的 SocketServer 实现是否用 Scala 完成。
**建议验证来源**: Kafka 源码 core/src/main/scala/kafka/network/SocketServer.scala、Apache Kafka 文档

### Q47: Acceptor 单线程，使用 Java NIO Selector
**章节位置**: 4.4.1
**原文陈述**: "**Acceptor** 是单线程，只做一件事：`accept` 新连接。它用 Java NIO 的 Selector 监听服务端 socket"
**待确认点**: Kafka Acceptor 是否使用 Java NIO Selector。Acceptor 是否确实只有一个线程。
**建议验证来源**: Kafka 源码 SocketServer.scala

### Q48: Acceptor 按轮询策略将新连接分配给 Processor
**章节位置**: 4.4.1
**原文陈述**: "每来一个新连接就按轮询策略交给某个 Processor"
**待确认点**: Acceptor 分配新连接到 Processor 的策略是否为轮询（round-robin）。
**建议验证来源**: Kafka 源码 SocketServer.scala

### Q49: Processor 数量和典型范围
**章节位置**: 4.4.1
**原文陈述**: "**Processor** 是一组线程（数量可配，典型几个到十几个）"
**待确认点**: Processor 数量是否可通过配置控制（`num.network.threads`）。典型范围是否如所述。
**建议验证来源**: Kafka 官方配置文档 `num.network.threads`

### Q50: RequestChannel 是有界阻塞队列
**章节位置**: 4.4.1
**原文陈述**: "**RequestChannel** 是 Processor 与业务线程之间的桥梁——一个**有界阻塞队列**"
**待确认点**: RequestChannel 的内部实现是否为有界阻塞队列。它的容量是否可配置。队列满时的行为是否如所述（Processor 入队阻塞）。
**建议验证来源**: Kafka 源码 RequestChannel.scala

### Q51: KafkaRequestHandler 数量等于 num.io.threads
**章节位置**: 4.4.1
**原文陈述**: "**KafkaRequestHandler** 是一组业务线程（数量可配，等于 `num.io.threads`）"
**待确认点**: `num.io.threads` 是否是 KafkaRequestHandler 线程数的配置参数。默认值和语义是否如所述。
**建议验证来源**: Kafka 官方配置文档 `num.io.threads`、Kafka 源码 KafkaRequestHandler.scala

### Q52: 背压（backpressure）机制描述
**章节位置**: 4.4.1
**原文陈述**: "当业务线程处理不过来、队列填满时，Processor 的入队操作会阻塞，进而阻塞网络 IO。这是一个天然的背压（backpressure）点"
**待确认点**: RequestChannel 满时是否确实会导致 Processor 阻塞，进而传导到网络读取。这个背压链路的完整机制是否准确。
**建议验证来源**: Kafka 源码 SocketServer.scala 和 RequestChannel.scala

### 4.4.2 逻辑层（API 层）：请求类型分派

### Q53: ApiKeys 枚举内容
**章节位置**: 4.4.2
**原文陈述**: "Kafka 把所有请求类型枚举成 ApiKeys：PRODUCE、FETCH、LIST_OFFSETS、METADATA、LEADER_AND_ISR 等"
**待确认点**: 所列举的 ApiKeys 是否准确。重要 API 类型是否有明显遗漏（如 API_VERSIONS、CREATE_TOPICS、DESCRIBE_GROUPS、JOIN_GROUP、SYNC_GROUP、HEARTBEAT 等）。
**建议验证来源**: Kafka 源码 ApiKeys.scala

### Q54: 每种 ApiKey 有自己的版本号
**章节位置**: 4.4.2
**原文陈述**: "每一种有自己的版本号，Broker 要兼容新旧版本"
**待确认点**: Kafka 协议是否确实每个请求类型独立版本号。Broker 是否确实需要兼容新旧版本。
**建议验证来源**: Apache Kafka 协议规范文档

### Q55: 鉴权、配额、版本协商作为横切关注点
**章节位置**: 4.4.2
**原文陈述**: "这一层还负责横切关注点：**鉴权、配额（quota）、版本协商**"
**待确认点**: 鉴权、配额、版本协商是否确实在 KafkaApis 层实现。配额的默认值是多少（如 `quota.producer.default`、`quota.consumer.default`）。
**建议验证来源**: Kafka 源码 KafkaApis.scala、Kafka 官方配额管理文档

### Q56: Kafka 将协议分派和领域逻辑分开
**章节位置**: 4.4.2
**原文陈述**: "**Kafka 把"逻辑层"切成"协议分派"和"领域逻辑"两段**。`KafkaApis` 只做协议适配和分派，领域逻辑在更下层——`Log`、`ReplicaManager`、`GroupCoordinator`、`Controller`"
**待确认点**: 这种分离是否准确反映了 Kafka 的代码组织。`KafkaApis` 是否确实不做领域逻辑、只做分派。
**建议验证来源**: Kafka 源码 KafkaApis.scala

### Q57: 协议格式三年才加一个新版本
**章节位置**: 4.4.2
**原文陈述**: "协议格式三年才加一个新版本"
**待确认点**: Kafka 协议版本演进的节奏是否约为三年一个大版本。该说法如何与 Kafka 实际版本发布历史对应。
**建议验证来源**: Apache Kafka 版本发布历史、KIP 文档

### 4.4.3 存储层：Log 抽象 + 零拷贝

### Q58: 每个分区对应一个 Log，Log 由 LogSegment 组成
**章节位置**: 4.4.3
**原文陈述**: "每个分区对应一个 Log，每个 Log 由多个 LogSegment 组成"
**待确认点**: Kafka 中分区和 Log 的关系是否是 1:1。Log 和 LogSegment 的层次关系是否准确。
**建议验证来源**: Kafka 源码 Log.scala、Kafka 官方文档

### Q59: LogSegment 的三个文件
**章节位置**: 4.4.3
**原文陈述**: "每个 LogSegment 在磁盘上是三个文件：消息数据文件（`.log`）、位移索引文件（`.index`）、时间戳索引文件（`.timeindex`）"
**待确认点**: LogSegment 是否确实由这三个文件组成。是否有其他文件（如 `.snapshot` 事务索引文件等）属于 LogSegment 的一部分。
**建议验证来源**: Kafka 源码 LogSegment.scala、实际 Kafka 数据目录

### Q60: 顺序追加写——没有 B 树、没有索引重建、没有写放大
**章节位置**: 4.4.3
**原文陈述**: "没有 B 树、没有索引重建、没有写放大——追加写是磁盘上最快的写法"
**待确认点**: Kafka 的写入是否确实是纯顺序追加写。是否真的完全不存在写放大（考虑压缩 compaction 等机制）。
**建议验证来源**: Kafka 官方设计文档

### Q61: flush.messages 和 flush.ms 配置
**章节位置**: 4.4.3
**原文陈述**: "刷盘策略可配：`flush.messages`（每多少条刷一次）或 `flush.ms`（每多少毫秒刷一次）"
**待确认点**: `flush.messages` 和 `flush.ms` 是否是 Broker 级别的配置。它们的默认值是多少。是否可以同时配置。
**建议验证来源**: Kafka 官方配置文档 `log.flush.interval.messages`、`log.flush.interval.ms`

### Q62: 稀疏索引默认每 4KB
**章节位置**: 4.4.3
**原文陈述**: "每隔一段距离（默认每 4KB）记一项"
**待确认点**: Kafka 位移索引的稀疏间隔默认值是否为 4KB（通过 `log.index.interval.bytes` 配置）。默认值在不同版本之间是否有变化。
**建议验证来源**: Kafka 官方配置文档 `log.index.interval.bytes`

### Q63: 索引大小被压得很小，常驻内存
**章节位置**: 4.4.3
**原文陈述**: "这把索引大小压得很小，常驻内存"
**待确认点**: Kafka 索引文件是否设计为常驻内存（通过 mmap 方式映射）。索引大小的典型比例（如索引文件大小与数据文件大小的比例）。
**建议验证来源**: Kafka 源码 OffsetIndex.scala、Kafka 官方设计文档

### Q64: sendfile 跳过用户态，省掉两次拷贝和两次上下文切换
**章节位置**: 4.4.3
**原文陈述**: "Kafka 用 Linux 的 `sendfile` 系统调用，让内核直接把页缓存的数据传到网卡 socket：磁盘 → 页缓存 → 网卡，**跳过用户态**，省掉两次拷贝和两次上下文切换"
**待确认点**: sendfile 的路径是否如所述（页缓存 → 网卡，跳过用户态）。传统路径是否确实涉及四次拷贝。sendfile 的传统性能收益是否准确描述。
**建议验证来源**: Linux man page for sendfile(2)、Linux 内核文档关于零拷贝

### Q65: sendfile 要求数据不被修改
**章节位置**: 4.4.3
**原文陈述**: "零拷贝有一个前提：**数据必须是从文件到 socket 的纯转发，中间不能被修改**"
**待确认点**: sendfile 的使用前提是否确实是"数据从文件到 socket 的纯转发，不被修改"。Kafka 的语义是否确实契合这一前提（消息不可变）。
**建议验证来源**: Linux man page for sendfile、Kafka 设计文档

### Q66: 消费者 FETCH 和 Follower FETCH 走同一条代码路径
**章节位置**: 4.4.3
**原文陈述**: "消费者发 FETCH 请求，Follower 也发 FETCH 请求——它们走同一条 `KafkaApis.handleFetchRequest` → `ReplicaManager.fetchMessages` → Log 读取 → sendfile 路径"
**待确认点**: 消费者 FETCH 和 Follower 副本同步 FETCH 是否确实走同一条代码路径。区别是否仅在于请求内的标志位不同。
**建议验证来源**: Kafka 源码 ReplicaManager.scala、KafkaApis.scala

### Q67: Follower 复制本质上是"一个特殊的消费者"
**章节位置**: 4.4.3
**原文陈述**: "**Follower 复制本质上就是'一个特殊的消费者'**"
**待确认点**: Kafka 的副本同步机制是否确实可以理解为"Follower 作为一个特殊的消费者从 Leader 拉取数据"。这个简化是否有遗漏的关键差异（如同步语义、ISR 管理等）。
**建议验证来源**: Kafka 官方复制协议文档

### 4.4.4 协调层：在 Log 之上的额外一层

### Q68: Kafka 协调层包含的组件
**章节位置**: 4.4.4
**原文陈述**: "它包括 ReplicaManager（副本管理）、Partition（分区对象）、Controller（集群控制器），以及 KRaft（取代 ZooKeeper 的元数据管理）"
**待确认点**: ReplicaManager、Partition、Controller 是否属于协调层。KRaft 是否确实取代 ZooKeeper 的元数据管理功能。KRaft 从哪个版本开始 GA（正式可用）。
**建议验证来源**: Kafka 2.8+ / 3.x release notes、Kafka 官方 KRaft 文档

### Q69: Redis Cluster 无独立协调层，MySQL MGR 多数派投票类比
**章节位置**: 4.4.4
**原文陈述**: "Redis Cluster 的槽路由、MySQL MGR 的多数派投票都属于类似的关注点，只是没像 Kafka 那样独立成代码上一个清晰的模块层"
**待确认点**: Redis Cluster 是否确实没有独立的"协调层"模块（其槽路由是否分散在 cluster.c 中）。MySQL MGR 是否使用多数派投票（Paxos 协议）。
**建议验证来源**: Redis 源码 cluster.c、MySQL Group Replication 文档

### 4.4.5 层间通信

> 本节总结层间通信形态与部署形态绑定。核心事实已在之前各节覆盖（RequestChannel 为有界队列、对象方法调用同 JVM、跨 Broker 用网络协议）。无需额外核查。

---

## 4.5 横向对比

### Q70: 表 4-1 各维度对比准确性
**章节位置**: 4.5
**原文陈述**: 表 4-1 "三家分层形态横向对比" 中所有维度（核心抽象、主要存储介质、层数与粒度、层间通信机制、可插拔性、分层的首要目标）
**待确认点**: 表中每一个单元格的描述是否与前述章节内容一致。各维度的分组/断言是否有误。特别是在"主要存储介质"一行中，Redis 是否标为"内存（持久化为辅）"、MySQL 是否标为"磁盘（缓冲池做内存缓存）"、Kafka 是否标为"磁盘（重度依赖页缓存）"，这些描述是否准确。
**建议验证来源**: 各产品的官方文档和技术设计文档

### Q71: 进程内调用纳秒级 vs 网络调用毫秒级，差六个数量级
**章节位置**: 4.5
**原文陈述**: "进程内调用的延迟是纳秒级，网络调用的延迟是毫秒级，差了六个数量级"
**待确认点**: 纳秒级（~10-100ns）到毫秒级（~0.1-10ms）是否确实相差六个数量级（10³ 至 10⁵ 倍）而非固定六个数量级。该数值表述是否需要精确化。
**建议验证来源**: 计算机体系结构和网络延迟的通用参考数据

### Q72: 介质多样性决定引擎抽象必要性
**章节位置**: 4.5
**原文陈述**: "**介质的多样性决定了引擎抽象的必要性**"
**待确认点**: 此论断在 MySQL 中是否准确——MySQL 能否同一实例加载多种物理介质类型的引擎。该论述作为一般性原则的准确性。
**建议验证来源**: MySQL Handler API 文档、各存储引擎的介质需求

---

## 4.6 架构启示

### Q73: MySQL 8.0 移除查询缓存后在高写入场景下性能更好
**章节位置**: 4.6
**原文陈述**: "MySQL 8.0 移除查询缓存就是一个典型例证...8.0 砍掉它之后，整体性能在高写入场景下反而更好"
**待确认点**: MySQL 8.0 移除 Query Cache 后高写入场景的性能是否确实整体提升。是否有官方 benchmark 数据支持。
**建议验证来源**: MySQL 8.0 性能测试报告、DBA 社区实测数据

### Q74: robj 从 Redis 早期到现在核心结构未变
**章节位置**: 4.6
**原文陈述**: "`robj` 从 Redis 早期到现在核心结构没动过"
**待确认点**: `redisObject` 的核心结构（type/encoding/ptr/refcount/lru 字段布局）是否确实从早期版本（~1.x）至今未发生重大变化。
**建议验证来源**: Redis 早期源码（如 1.0/2.0）与最新源码中 redisObject 定义的对比

### Q75: Handler API 自 MySQL 5.x 插件化以来接口稳定
**章节位置**: 4.6
**原文陈述**: "Handler API 自 MySQL 5.x 插件化以来接口形态稳定"
**待确认点**: Handler API 是否从 MySQL 5.x 引入插件化机制（Plugin API）以来保持稳定。重大版本（5.6/5.7/8.0）之间是否有结构性变更。
**建议验证来源**: MySQL 各版本 handler.h 对比

### Q76: Redis 从缓存工具长成多模数据库的演进描述
**章节位置**: 4.6
**原文陈述**: "Redis 从一个缓存工具长成支持多种数据结构、Function、Cluster 的多模数据库"
**待确认点**: Redis 是否确实经过从缓存工具到支持多种数据结构（早期）+ Function（Redis 7.0 引入）+ Cluster（3.0 引入）的演进路径。Redis Functions 是否在 7.0 引入（取代 Lua scripts 的一部分场景）。
**建议验证来源**: Redis 版本发布历史

### Q77: MySQL 早期只有 ISAM/MyISAM
**章节位置**: 4.6
**原文陈述**: "MySQL 从单引擎（早期只有 ISAM/MyISAM）长成多引擎体系"
**待确认点**: MySQL 早期是否确实只有 ISAM（MySQL 3.x）和 MyISAM（MySQL 3.23+）引擎。InnoDB 何时作为插件加入。
**建议验证来源**: MySQL 历史文档

### Q78: Kafka Streams、Connect、KSQL 描述
**章节位置**: 4.6
**原文陈述**: "Kafka 从一个消息队列长成流平台（Kafka Streams、Connect、KSQL）"
**待确认点**: Kafka Streams、Connect、KSQL 分别从哪个版本引入。KSQL 是否已更名为 ksqlDB。
**建议验证来源**: Apache Kafka 版本发布历史、Confluent 平台文档

### Q79: 启示三之"Connect 和 Streams 是扩展点"
**章节位置**: 4.6
**原文陈述**: "Kafka 把扩展点放在边缘——Connect（数据进出 Kafka 的连接器）、Streams（流处理 SDK）——而不是放在存储核心"
**待确认点**: Kafka Connect 和 Kafka Streams 是否确实属于"边缘扩展点"而非核心存储抽象。这一论述是否准确反映了 Kafka 的架构哲学。
**建议验证来源**: Apache Kafka 文档关于 Connect 和 Streams 的定位

---

## 4.7 小结

> 本章小结是对前述内容的高度概括，不包含独立的未验证事实。核心论断与前述各节重复。无需额外核查。

---

## 汇总统计

- 总核查问题数：79
- 覆盖本章节数：全部（4.1-4.7）
- 涵盖类型：版本号引入/变更（~20）、配置默认值（~10）、算法/实现细节（~25）、API/协议行为（~12）、历史演进描述（~6）、架构对比（~6）
