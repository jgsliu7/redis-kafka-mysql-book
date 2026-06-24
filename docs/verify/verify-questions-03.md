# 第03章《内存与磁盘》事实核查问题清单

## 3.1 问题本质

### Q1: CPU L1 缓存访问延迟 ~1 ns
**章节位置**: 3.1, 表 3-1
**原文陈述**: CPU L1 缓存典型访问延迟约 1 ns
**待确认点**: 现代 CPU L1 缓存延迟是否确实约为 1 纳秒（Skylake/Zen 等常见架构实测值通常在 0.5-1.5 ns 范围，确认数量级是否准确）
**建议验证来源**: Intel/AMD 优化手册中的 latency 表；uops.info 实测数据

### Q2: 内存（DRAM）访问延迟 ~100 ns
**章节位置**: 3.1, 表 3-1
**原文陈述**: 内存（DRAM）典型访问延迟约 100 ns
**待确认点**: DDR4/DDR5 常见延迟通常约 60-100 ns（含 TLB miss），确认 100 ns 是否合理
**建议验证来源**: Intel/AMD 性能计数手册；https://colin-scott.github.io/personal_website/research/interactive_latency.html

### Q3: SSD 随机读延迟 ~100 μs
**章节位置**: 3.1, 表 3-1
**原文陈述**: SSD（随机读）典型访问延迟约 100 μs
**待确认点**: 现代 NVMe SSD 随机读延迟通常更低（约 20-80 μs），SATA SSD 约 50-150 μs。"100 μs"是否为合理的数量级表述
**建议验证来源**: AnandTech / Tom's Hardware SSD 基准；各厂商（Samsung/Kioxia/WD）数据手册

### Q4: SSD 顺序写吞吐 ~300-500 MB/s
**章节位置**: 3.1, 表 3-1
**原文陈述**: SSD（顺序写）吞吐约 300-500 MB/s
**待确认点**: 现代 NVMe SSD 顺序写吞吐可达 2000-7000 MB/s（如 Samsung 990 Pro ~5000 MB/s），SATA SSD 才约 500 MB/s。300-500 MB/s 是否明显过时或偏低
**建议验证来源**: NVMe SSD 产品规格；AnandTech 存储基准

### Q5: 机械盘随机寻道延迟 ~10 ms
**章节位置**: 3.1, 表 3-1
**原文陈述**: 机械盘（随机寻道）典型访问延迟约 10 ms
**待确认点**: 企业级 HDD 寻道时间约 3-8 ms，消费级约 7-15 ms。10 ms 是否为合理的数量级表述
**建议验证来源**: 各 HDD 厂商（Seagate/WD/Toshiba）数据手册

### Q6: 机械盘顺序写吞吐 ~100-200 MB/s
**章节位置**: 3.1, 表 3-1
**原文陈述**: 机械盘（顺序写）典型吞吐约 100-200 MB/s
**待确认点**: 现代企业级 HDD（如 Seagate Exos 20TB）顺序吞吐约 250-280 MB/s，100-200 MB/s 是否偏低
**建议验证来源**: 各 HDD 厂商数据手册；StorageReview.com 测试

### Q7: 体感换算 "16 分钟" 与 "28 小时"
**章节位置**: 3.1, 第 28 行
**原文陈述**: "如果内存访问是 1 秒，SSD 一次随机访问就是 17 分钟，机械盘一次随机寻道就是 28 小时"
**待确认点**: 以 ~100 ns 内存为基准 vs ~100 μs SSD：倍数约 1000 倍，对应 ~17 分钟（1000 秒 ≈ 16.7 分钟）。以 ~100 ns 内存 vs ~10 ms 机械盘：倍数约 100000 倍，对应 ~28 小时（100000 秒 ≈ 27.8 小时）。确认换算是否正确
**建议验证来源**: 自行验算

### Q8: SSD 顺序读比随机读快 100 倍
**章节位置**: 3.1, 第 33 行图注
**原文陈述**: "同一块 SSD，顺序读比随机读快 100 倍"
**待确认点**: NVMe SSD 顺序读延迟约 10-20 μs，随机读延迟约 20-80 μs，相差通常仅有 2-4 倍而非 100 倍。如果指吞吐：顺序读可达 7000 MB/s，随机读约数百 MB/s（~10 倍差距）。100 倍是否准确，是基于延迟还是吞吐的对比
**建议验证来源**: SSD 厂商数据手册；AnandTech 基准测试

## 3.2 Redis 做法

### Q9: Redis 官方定义 "in-memory data structure store"
**章节位置**: 3.2, 第 57 行
**原文陈述**: "Redis 在官方文档里把自己定义为'内存数据结构存储（in-memory data structure store）'"
**待确认点**: Redis 官网（redis.io）的官方描述是否仍为 "in-memory data structure store"。当前官网首页描述为 "The open source, in-memory data store..."，确认关于 "data structure store" 的表述是否准确
**建议验证来源**: https://redis.io 官方首页；redis.io/documentation

### Q10: maxmemory-samples 默认值为 5
**章节位置**: 3.2, 第 67 行
**原文陈述**: "由 maxmemory-samples 控制，默认 5"
**待确认点**: Redis `maxmemory-samples` 配置项默认值是否仍为 5
**建议验证来源**: Redis 官方配置文件 (redis.conf)；https://redis.io/docs/latest/operate/oss_and_stack/management/config/

### Q11: 近似 LRU 从全部键随机采样 N 个
**章节位置**: 3.2, 第 67 行
**原文陈述**: "淘汰时从全部键里随机采样 N 个（由 maxmemory-samples 控制，默认 5），从中淘汰最久未用的那一个"
**待确认点**: Redis 近似 LRU 的实现细节：是否确实从全部键空间随机采样而非从某个候选池（pool）采样。Redis 实测在 maxmemory-samples 外还有采样候选池（eviction pool）机制，淘汰时从池中选最佳而非单次采样。确认描述是否过于简化
**建议验证来源**: Redis 源码 evict.c；https://redis.io/docs/latest/operate/oss_and_stack/management/eviction/

### Q12: Redis 4.0 引入 LFU
**章节位置**: 3.2, 第 69 行
**原文陈述**: "Redis 4.0 引入了 LFU（Least Frequently Used，最不经常使用）"
**待确认点**: LFU 淘汰策略是否确实自 Redis 4.0 引入
**建议验证来源**: Redis 4.0 release notes；redis.io 版本历史

### Q13: Morris 近似计数器：8 位对数计数器
**章节位置**: 3.2, 第 69 行
**原文陈述**: "它用的是 Morris 近似计数器：一个 8 位的对数计数器"
**待确认点**: Redis LFU 使用的计数器实现是否确实是 Morris 计数器（也叫 Morris Approximate Counter / Morris Algorithm），8 位描述是否准确
**建议验证来源**: Redis 源码的 evict.c 中 LFU 实现；https://redis.io/docs/latest/operate/oss_and_stack/management/eviction/#the-new-lfu-mode

### Q14: lfu-log-factor 控制对数底，lfu-decay-time 单位分钟
**章节位置**: 3.2, 第 69-70 行
**原文陈述**: "关键参数是 lfu-log-factor（控制计数器增长的对数底）和 lfu-decay-time（控制衰减周期，单位分钟）"
**待确认点**: `lfu-log-factor` 是否控制计数器增长的对数底；`lfu-decay-time` 的单位是否是分钟（确认为分钟而非秒或其他）
**建议验证来源**: Redis 源码 evict.c 中 LFU 相关代码；redis.conf 注释；redis.io 官方文档

### Q15: Redis 八种淘汰策略分三组
**章节位置**: 3.2, 第 73 行
**原文陈述**: "Redis 把淘汰策略做成八种，可以归成三组。noeviction...allkeys-lru / allkeys-lfu / allkeys-random...volatile-lru / volatile-lfu / volatile-random / volatile-ttl"
**待确认点**: 八种策略的列举是否完整准确。当前 Redis 版本中是否存在 volatile-ttl 等所有八种
**建议验证来源**: Redis 官方文档 (redis.io/docs/latest/operate/oss_and_stack/management/eviction/)

### Q16: RDB 依赖 fork + COW
**章节位置**: 3.2, 第 85 行
**原文陈述**: "生成方式是 fork 一个子进程，子进程拿到父进程内存的副本（依赖操作系统的写时复制 COW 机制）"
**待确认点**: RDB 持久化是否使用 fork() + COW 机制，描述是否准确
**建议验证来源**: Redis 源码 rdb.c；redis.io 持久化文档

### Q17: 大实例 fork 阻塞数百毫秒
**章节位置**: 3.2, 第 85-86 行
**原文陈述**: "一个几十 GB 的实例 fork 一次可能阻塞主线程数百毫秒，期间整个实例看上去像卡住了"
**待确认点**: fork 耗时与内存大小的关系是否如此显著（数十 GB 内存 fork 阻塞数百毫秒）；实际生产中的 fork 延迟数据
**建议验证来源**: Redis 社区经验帖；Redis 作者 antirez 的博客论述；实测 fork 耗时文档

### Q18: appendfsync 三种模式及默认值 everysec
**章节位置**: 3.2, 第 89-93 行
**原文陈述**: "always：每条命令都执行一次 fsync...everysec：每秒 fsync 一次，默认值。no：把刷盘时机完全交给操作系统"
**待确认点**: `appendfsync` 的三个选项是否准确；默认值是否为 `everysec`
**建议验证来源**: redis.conf 配置文件；Redis 官方持久化文档

### Q19: AOF 重写把多次 INCR 合并为 SET
**章节位置**: 3.2, 第 95 行
**原文陈述**: "一个键被反复 INCR 一万次，AOF 里就有一万条 INCR。AOF 重写解决这个问题...把那一万条 INCR 压成一条 SET key 10000"
**待确认点**: AOF 重写是否确实按内存当前状态重生成命令集，示例描述是否准确
**建议验证来源**: Redis AOF 重写实现源码；redis.io 持久化文档

### Q20: Redis 4.0 引入混合持久化
**章节位置**: 3.2, 第 97 行
**原文陈述**: "Redis 4.0 又推出了混合持久化"
**待确认点**: 混合持久化（`aof-use-rdb-preamble`）是否由 Redis 4.0 引入
**建议验证来源**: Redis 4.0 release notes；redis.io 版本历史

### Q21: aof-use-rdb-preamble 自 7.0 起默认 yes
**章节位置**: 3.2, 第 97 行
**原文陈述**: "aof-use-rdb-preamble 自 7.0 起默认就是 yes，是当前推荐配置"
**待确认点**: `aof-use-rdb-preamble` 的默认值是否自 Redis 7.0 起为 yes；7.0 之前默认值是什么
**建议验证来源**: Redis 7.0 release notes；redis.conf 各版本比较；redis.io 文档

### Q22: Redis 7.0 Multi-Part AOF 改造
**章节位置**: 3.2, 第 99-100 行
**原文陈述**: "7.0 的多部 AOF（Multi-Part AOF）改造...拆成了一个目录（appendonlydir/），里面由清单文件（manifest）统一管理三类文件：至多一个基础文件（base，RDB 格式）、零或多个增量文件（incr，AOF 命令）、以及重写后被标记为历史（history）待删的旧文件"
**待确认点**: Redis 7.0 Multi-Part AOF 的文件结构描述是否准确：目录名是否为 `appendonlydir/`；文件分类是否为 base / incr / history 三类；manifest 文件是否存在及作用
**建议验证来源**: Redis 7.0 release notes；Redis源码；https://redis.io/docs/latest/develop/release-notes/redis-7-0/

### Q23: 7.0 之前 AOF 是单文件
**章节位置**: 3.2, 第 99 行
**原文陈述**: "7.0 之前 AOF 是一个单文件（RDB 前导 + 增量命令挤在一起）"
**待确认点**: Redis 7.0 之前 AOF 是否确实是单文件，描述是否准确
**建议验证来源**: Redis 6.x 及之前版本 AOF 文件结构文档

## 3.3 MySQL 做法

### Q24: InnoDB New Sublist 占 5/8，Old Sublist 占 3/8
**章节位置**: 3.3, 第 131 行
**原文陈述**: "靠头的 New Sublist 占约 5/8，是热区；靠尾的 Old Sublist 占约 3/8，是冷区"
**待确认点**: InnoDB 缓冲池 LRU 链表新旧分区比例是否为 5/8 和 3/8（通常描述为 37% 为 old 区，即约 5/8 new + 3/8 old），确认准确比例
**建议验证来源**: MySQL 官方文档 "InnoDB Buffer Pool LRU Chain"；MySQL 源码 buf0lru.cc

### Q25: innodb_old_blocks_time 默认 1000 毫秒
**章节位置**: 3.3, 第 131 行
**原文陈述**: "它必须在冷区停留超过 innodb_old_blocks_time（默认 1000 毫秒）之后再次被访问，才有资格晋升进热区"
**待确认点**: `innodb_old_blocks_time` 的默认值是否为 1000 毫秒
**建议验证来源**: MySQL 官方文档；`SHOW VARIABLES LIKE 'innodb_old_blocks_time'`

### Q26: MySQL 8.0.20 双写区从共享表空间改为独立文件
**章节位置**: 3.3, 第 157 行
**原文陈述**: "MySQL 8.0.20 起把双写区从共享表空间（ibdata1）里独立出来，改成独立的 doublewrite 文件"
**待确认点**: MySQL 8.0.20 是否确实将 Double Write Buffer 从共享表空间分离为独立文件
**建议验证来源**: MySQL 8.0.20 release notes；MySQL 官方文档 "Doublewrite Buffer"

### Q27: InnoDB 页大小为 16 KB
**章节位置**: 3.3, 第 157 行
**原文陈述**: "InnoDB 的页是 16 KB"
**待确认点**: InnoDB 默认页大小是否为 16 KB（注意 16 KB 是默认值，但可配置为 4 KB、8 KB、16 KB、32 KB、64 KB）
**建议验证来源**: MySQL 官方文档 "InnoDB Page Size"；`innodb_page_size` 配置项

### Q28: 操作系统和磁盘扇区通常是 4 KB 或更小
**章节位置**: 3.3, 第 157 行
**原文陈述**: "操作系统和磁盘的扇区通常是 4 KB 或更小"
**待确认点**: 现代磁盘扇区大小——HDD 已从 512B 过渡到 4K（高级格式化），NVMe SSD 通常也以 4K 为基础。表述是否准确
**建议验证来源**: 各磁盘厂商规格；Linux 块设备层文档

### Q29: 修改缓冲只对非唯一二级索引生效
**章节位置**: 3.3, 第 159-160 行
**原文陈述**: "修改缓冲只对二级索引的非唯一索引生效，因为唯一索引必须立刻检查约束"
**待确认点**: Change Buffer 的应用范围描述是否完全准确（针对非唯一二级索引的 INSERT/UPDATE/DELETE 操作）
**建议验证来源**: MySQL 官方文档 "Change Buffer"；MySQL 源码

### Q30: AHI 把 3-4 次页访问压成 1 次
**章节位置**: 3.3, 第 161 行
**原文陈述**: "自动给这些路径建哈希，把 3 到 4 次页访问压成 1 次"
**待确认点**: AHI 的优化效果是否确实将 B+ 树路径从 3-4 次页访问减少到 1 次哈希查找
**建议验证来源**: MySQL 官方文档 "Adaptive Hash Index"；MySQL 性能基准研究

### Q31: 缓冲池三分链表（Free / LRU / Flush）
**章节位置**: 3.3, 第 125-130 行
**原文陈述**: "缓冲池（Buffer Pool）由三条链表精密管理：Free List、LRU List、Flush List"
**待确认点**: InnoDB 缓冲池是否确实使用此三种链表管理；是否有其他辅助链表（如 unzip LRU list）
**建议验证来源**: MySQL 官方文档 InnoDB Buffer Pool 章节；MySQL 源码 buf0buf.h 和 buf0lru.cc

### Q32: 一次大扫描后延迟回暖现象
**章节位置**: 3.3, 第 121 行
**原文陈述**: "平时几十毫秒的查询，某天有人跑了一个大报表，之后整个库的延迟集体飙上去，要等热数据重新被访问回暖才慢慢回落"
**待确认点**: 描述的业务逻辑是否准确（缓冲池污染导致延迟上升的热点数据替换原理）
**建议验证来源**: MySQL 缓冲池工作原理文档；生产环境案例分析

## 3.4 Kafka 做法

### Q33: SSD 顺序写吞吐 300-500 MB/s
**章节位置**: 3.4, 第 181 行
**原文陈述**: "SSD 顺序写吞吐约 300 到 500 MB/s"
**待确认点**: 同 Q4。现代 NVMe SSD 远高于此，300-500 MB/s 仅对应 SATA SSD，是否应更新
**建议验证来源**: NVMe SSD 产品规格；Kafka 性能基准测试

### Q34: 机械盘顺序写吞吐 100-200 MB/s
**章节位置**: 3.4, 第 181 行
**原文陈述**: "机械盘顺序写约 100 到 200 MB/s"
**待确认点**: 同 Q6。现代高性能 HDD 可达 250+ MB/s，是否应更新为含当前产品范围
**建议验证来源**: HDD 厂商数据手册

### Q35: 内存随机读吞吐约 100 MB/s 量级
**章节位置**: 3.4, 第 181 行
**原文陈述**: "内存随机读的吞吐大约在 100 MB/s 这个量级（取决于访问模式与并发）"
**待确认点**: 内存随机读吞吐是否仅为 ~100 MB/s（实际单线程 memcpy 可达 10+ GB/s，随机指针追逐取决于缓存行，但也不应低至 100 MB/s。确认该数字所指的具体场景）
**建议验证来源**: 内存带宽实测数据；Stream 基准测试

### Q36: Kafka 日志段默认 1 GB
**章节位置**: 3.4, 第 183 行
**原文陈述**: "每个段默认 1 GB（可配）"
**待确认点**: Kafka `log.segment.bytes` 默认值是否为 1 GB（1073741824 字节）
**建议验证来源**: Kafka 官方文档；Apache Kafka 配置项说明

### Q37: 零拷贝传统路径“4 次拷贝加 4 次上下文切换”
**章节位置**: 3.4, 第 199 行
**原文陈述**: "传统路径：磁盘 → 内核缓冲 → 用户缓冲 → Socket 缓冲 → 网卡，4 次拷贝加 4 次上下文切换"
**待确认点**: 传统 IO 路径的拷贝次数和上下文切换次数是否准确描述；具体路径细节
**建议验证来源**: Linux 零拷贝技术文档（sendfile/splice）；Kafka 零拷贝官方说明

### Q38: 零拷贝路径“2 次上下文切换”
**章节位置**: 3.4, 第 199 行
**原文陈述**: "零拷贝路径...只有 2 次上下文切换"
**待确认点**: sendfile 系统调用的上下文切换次数——一次 sendfile 调用（切换到内核态 + 返回用户态）是否为恰好 2 次
**建议验证来源**: Linux man page sendfile(2)；性能分析文章

### Q39: 零拷贝只在 PageCache 命中时生效
**章节位置**: 3.4, 第 199-200 行
**原文陈述**: "零拷贝只在消费者读'已经缓存在 PageCache 里的数据'时才生效；冷数据还是要走磁盘 IO"
**待确认点**: 此边界条件的描述是否准确（sendfile 也可用于磁盘 IO，只是会有 page fault 导致的阻塞）
**建议验证来源**: Linux sendfile 文档；Kafka 存储层文档

### Q40: log.flush.interval.messages 和 log.flush.interval.ms 配置参数
**章节位置**: 3.4, 第 203 行
**原文陈述**: "可以显式配置 log.flush.interval.messages（攒多少条消息刷一次）和 log.flush.interval.ms（多久刷一次）"
**待确认点**: Kafka 刷盘配置参数名称是否准确；默认值及其作用
**建议验证来源**: Apache Kafka 官方文档中 broker 配置部分

### Q41: acks 三种模式的行为描述
**章节位置**: 3.4, 第 207-209 行
**原文陈述**: 
- "acks=0：生产者发出去就不管，不等任何确认。吞吐最高，可能丢消息。"
- "acks=1：只要主节点（leader）把消息写到本地日志就确认。主节点崩溃且未同步到从节点时，这条消息可能丢。"
- "acks=all（也叫 acks=-1）：消息必须被 ISR（同步副本集合，In-Sync Replicas）里的全部副本确认才算成功。配合合理的副本数和 min.insync.replicas，这是最强的'不丢'保证"
**待确认点**: 三种 acks 模式的语义描述是否准确。特别注意 acks=all 的定义：是否为"ISR 中全部副本"确认才成功，还是"所有正在同步的副本"（ISR 的语义）
**建议验证来源**: Apache Kafka 官方文档；Kafka 源码中的生产者配置

### Q42: ISR 缩写全称是 In-Sync Replicas
**章节位置**: 3.4, 第 209 行
**原文陈述**: "ISR（同步副本集合，In-Sync Replicas）"
**待确认点**: ISR 全称是否为 In-Sync Replicas（确认官方文档拼写）
**建议验证来源**: Apache Kafka 官方文档

### Q43: Kafka 3.0 之前默认 acks=1，3.0 起默认 acks=all
**章节位置**: 3.6, 第 287 行
**原文陈述**: "Kafka 的 acks=1（3.0 之前的默认；3.0 起默认已升至 acks=all）"
**待确认点**: Kafka 3.0 是否将默认 acks 从 1 改为 all
**建议验证来源**: Kafka 3.0 release notes；Apache Kafka 配置变更说明

### Q44: log.index.interval.bytes 默认 4 KB
**章节位置**: 表 3-2, 第 220 行
**原文陈述**: "每写入 log.index.interval.bytes（默认 4 KB）追加一条索引项"
**待确认点**: Kafka `log.index.interval.bytes` 默认值是否为 4096 (4 KB)
**建议验证来源**: Apache Kafka 官方文档 broker 配置

### Q45: 段文件类型：.log, .index, .timeindex, .snapshot
**章节位置**: 表 3-2, 第 217-223 行
**原文陈述**: Kafka 日志段包含 .log, .index, .timeindex, .snapshot 四种文件
**待确认点**: Kafka 日志段文件类型列举是否完整准确；是否存在其他文件类型（如 .txnindex 等）
**建议验证来源**: Apache Kafka 日志段实现源码；Kafka 文档

### Q46: 索引是稀疏的，不每条消息都建索引项
**章节位置**: 3.4, 第 224 行
**原文陈述**: "索引是稀疏的（不是每条消息都建索引项），是为了让索引文件本身也保持紧凑、能放进 PageCache"
**待确认点**: Kafka 位移索引和时间戳索引是否为稀疏索引，但稀疏策略是否确实为"每 log.index.interval.bytes 建一条"
**建议验证来源**: Apache Kafka 存储层文档；Kafka 源码 Log.scala

### Q47: 二分查找找到最近索引项后顺序扫描到目标位移
**章节位置**: 3.4, 第 224 行
**原文陈述**: "消费者按位移定位消息时，先用索引二分找到最近的索引项，再在 .log 里顺序扫描到目标位移"
**待确认点**: Kafka 消费者使用索引进行位移定位的路径描述是否准确
**建议验证来源**: Apache Kafka 消费协议文档；Kafka 源码

## 3.5 横向对比

### Q48: Redis 崩溃恢复代价 "数分钟"
**章节位置**: 表 3-3, 第 244 行
**原文陈述**: "崩溃恢复代价：加载 RDB / 回放 AOF（大实例数分钟）"
**待确认点**: 大实例（如 30-50 GB）RDB 加载和 AOF 回放的时间是否为数分钟量级
**建议验证来源**: Redis 社区经验帖；Redis 官方文档持久化恢复时间说明

### Q49: Kafka 崩溃恢复 "几乎无"
**章节位置**: 表 3-3, 第 244 行
**原文陈述**: "崩溃恢复代价：几乎无（PageCache 热度取决于 OS）"
**待确认点**: Kafka broker 崩溃重启后的恢复代价是否确实"几乎无"（需考虑日志加载、索引校验、恢复未完成的事务等）
**建议验证来源**: Apache Kafka 运维文档；Kafka 社区经验帖

### Q50: MySQL innodb_flush_log_at_trx_commit 默认值为 1
**章节位置**: 3.5, 第 251 行
**原文陈述**: "MySQL 默认（innodb_flush_log_at_trx_commit=1）保护已提交事务"
**待确认点**: `innodb_flush_log_at_trx_commit` 默认值是否为 1
**建议验证来源**: MySQL 官方文档；`SHOW VARIABLES LIKE 'innodb_flush_log_at_trx_commit'`

## 3.6 架构启示

### Q51: Kafka 消费者追不上时延迟从毫秒级掉到十毫秒以上
**章节位置**: 3.5, 第 259 行
**原文陈述**: "消费者读的数据被挤出 PageCache、落到磁盘读，延迟从毫秒级掉到十毫秒以上"
**待确认点**: 当消费落到磁盘时，延迟是否确实从毫秒级跃升至 10+ 毫秒，而非更高
**建议验证来源**: Kafka 性能基准测试；生产监控数据

### Q52: 缓冲池命中率掉到 95% 以下延迟翻倍甚至翻十倍
**章节位置**: 3.6, 第 303 行
**原文陈述**: "MySQL 的缓冲池命中率掉到 95% 以下...延迟立刻翻倍甚至翻十倍"
**待确认点**: 缓冲池命中率从 99% 降到 95% 是否会导致延迟翻倍或翻十倍
**建议验证来源**: MySQL 性能基准测试资料；InnoDB 缓冲池工作原理文档

## 补充核查项

### Q53: 同价位下磁盘容量通常是内存的上百倍
**章节位置**: 3.1, 第 41 行
**原文陈述**: "同价位下，磁盘容量通常是内存的上百倍"
**待确认点**: 当前市场价格下，同等金额购买的磁盘容量与内存容量之比是否约为 100:1
**建议验证来源**: 当前市场价格调查（如 TB/$ 的 HDD vs 内存条 vs SSD 价格对比）

### Q54: Kafka 进程重启后 PageCache 仍在
**章节位置**: 3.4, 第 177 行
**原文陈述**: "消费者读的数据如果还在 PageCache 里，Kafka 进程哪怕重启过，消费者依然按内存速度读，没有冷启动惩罚"
**待确认点**: 进程重启后 PageCache 中的数据是否仍然保留（PageCache 由内核管理，与进程生命周期无关——此表述正确，但仍需确认此红利在 Kafka 中是否实际显著）
**建议验证来源**: Linux 内核 PageCache 文档；Kafka 运维经验帖

### Q55: 传统路径与零拷贝路径的描述 - 关于 DMA 拷贝的说明
**章节位置**: 3.4, 第 199 行
**原文陈述**: "零拷贝路径（基于 sendfile / Java NIO transferTo）：磁盘 → 内核 PageCache → 网卡（由 DMA 完成实际搬运），数据全程不进用户空间，只有 2 次上下文切换"
**待确认点**: sendfile 实现的零拷贝是否确实只涉及内核态到网卡的 DMA 传输；是否需要考虑 SG-DMA 和对端等因素；"2 次上下文切换"描述是否精确
**建议验证来源**: Linux kernel sendfile 实现说明；Linux 零拷贝技术文档（如 IBM developerWorks 经典文章）

### Q56: Redis LFU 的实现细节——计数器衰减机制
**章节位置**: 3.2, 第 69-70 行
**原文陈述**: "并用一个带衰减的机制让长时间没访问的计数器逐渐回落"
**待确认点**: Redis LFU 的衰减机制是否是在每次访问时根据 `lfu-decay-time` 和上次访问时间计算衰减量，而不是独立的后台线程定时衰减
**建议验证来源**: Redis 源码 evict.c 中 LFU 实现；redis.io 文档

### Q57: Redis 近似 LRU vs 精确 LRU 的描述
**章节位置**: 3.2, 第 65-68 行
**原文陈述**: "教科书里的 LRU 维护一个双向链表，每次访问把节点移到链表头，淘汰时摘掉链表尾。这个方案准确但代价大"
**待确认点**: Redis 未使用精确 LRU 的原因是否主要为 CPU 开销；近似 LRU 的采样+候选池实现是否确实有效
**建议验证来源**: Redis 官方博客或 antirez 在 Redis 近似 LRU 的论述

### Q58: Redis 单实例"几十 GB"可能阻塞"数百毫秒"的量化范围
**章节位置**: 3.2, 第 85-86 行
**原文陈述**: "一个几十 GB 的实例 fork 一次可能阻塞主线程数百毫秒"
**待确认点**: "几十 GB"到"数百毫秒"的比例是否合理——如 30 GB 实例 fork 耗时约 300 ms 是否典型
**建议验证来源**: Redis 社区公开的 fork 耗时数据；https://redis.io/docs/latest/operate/oss_and_stack/management/admin/#fork-time-in-different-units

### Q59: RDB 快照的数据流描述
**章节位置**: 3.2, 第 105 行
**原文陈述**: "RDB 是另一条独立的全量快照路径（fork 触发），而 AOF（含 7.x 默认的混合持久化）走的是追加日志路径"
**待确认点**: Redis 7.x 默认配置下是否同时启用了 RDB 和 AOF（混合持久化模式下），默认配置是否确为混合持久化
**建议验证来源**: Redis 7.x 默认 redis.conf

### Q60: MySQL 双写缓冲的描述准确性
**章节位置**: 3.3, 第 157 行
**原文陈述**: "如果写一个 16 KB 页写到一半断电，这个页就损坏了，而且损坏的不是日志、是数据本身——重做日志也救不回来，因为它记录的是'怎么改这个页'，前提是这个页本来是好的"
**待确认点**: Double Write Buffer 解决的是"部分页写入"（partial page write/torn page）问题，描述是否准确
**建议验证来源**: MySQL 官方文档 Doublewrite Buffer 说明
