# 全书交叉引用全量盘点（机械基线，2026-09-06）

> 范围：chapters/ 全部成书 md（含序言/后记/参考文献；排除 outline 与 diagrams）。已剔 fenced 代码块与标题行自身编号。
> 注意：同一行多类命中分别计；"见/参见/详见"行与其他类有重叠（它是引用方式标记非目标）。

## 总量

| 类别 | 命中数 |
|---|---|
| fig | 155 |
| sec | 42 |
| ch | 104 |
| seeref | 92 |
| tab | 28 |

被引节号（去重 29 个）：1.1 节、1.2 节、1.2.1 节、2.2.1 节、2.2.3 节、3.2 节、3.3 节、3.4 节、4.2 节、4.3 节、4.4 节、5.3 节、5.3.2 节、5.5 节、5.6 节、6.6 节、6.7 节、7.2.3 节、7.3.2 节、7.3.3 节、7.4.2 节、7.4.3 节、8.3.2 节、8.3.3 节、8.3.4 节、8.4.4 节、8.4.6 节、9.2 节、9.4 节

被引章号（去重 10 个）：1、2、3、4、5、6、7、8、9、10

## 逐条清单

| # | 文件 | 行 | 类 | 命中 | 所在句（截 110 字） |
|---|---|---|---|---|---|
| 1 | chapters/01-introduction/chapter.md:25 | fig | 图 1-1 | ![图 1-1 后端基础设施的三种核心范式与代表软件](diagrams/fig-1-1.svg) |
| 2 | chapters/01-introduction/chapter.md:26 | fig | 图 1-1 | 图 1-1　后端基础设施的三种核心范式与代表软件：内存型 / 持久化型 / 流式型三类能力分别对应 Redis、MySQL、Kafka。 |
| 3 | chapters/01-introduction/chapter.md:34 | sec | 1.2.1 节 | 在内存数据结构存储领域，**Redis** 是最广泛使用的实现之一，独到之处是"数据结构服务器（data structure server）"这一抽象：一套结构化类型加原子命令，覆盖缓存、排行榜、消息队列、锁服务等多种角 |
| 4 | chapters/01-introduction/chapter.md:38 | ch | 第 7 章 | **Kafka** 从 LinkedIn 内部的日志采集系统起步，逐步演化为一个分布式流平台。几台普通服务器组成的小集群就能撑起百万级每秒写入：LinkedIn 公开基准里 3 台廉价机曾测到约 200 万次写入/秒（T |
| 5 | chapters/01-introduction/chapter.md:38 | seeref | 见 | **Kafka** 从 LinkedIn 内部的日志采集系统起步，逐步演化为一个分布式流平台。几台普通服务器组成的小集群就能撑起百万级每秒写入：LinkedIn 公开基准里 3 台廉价机曾测到约 200 万次写入/秒（T |
| 6 | chapters/01-introduction/chapter.md:44 | sec | 1.2 节 | 面对架构难题，它们采用的方案不同，代价也不同。数据怎么不丢、副本怎么同步、系统怎么扩展，这些是后端系统普遍会面对的问题，后面 8 章逐个深讲；并发怎么控，MySQL 的答案是 MVCC，本章 1.2 节会讲它的原理，锁与 |
| 7 | chapters/01-introduction/chapter.md:66 | sec | 1.1 节 | 典型场景因此也高度集中在它的核心优势领域：缓存、分布式锁、计数器、排行榜、会话存储、轻量级消息。这些场景的共同点是访问频繁、结构清晰、对延迟敏感——1.1 节那个购物车与库存计数就是典型。 |
| 8 | chapters/01-introduction/chapter.md:76 | seeref | 见 | 支撑 MySQL 设计哲学的是一整套为正确性服务的机制。InnoDB 提供完整的 ACID（原子性、一致性、隔离性、持久性）事务、靠 MVCC 实现的非阻塞读、行级锁。MVCC 的原理一句话：改一行时保留旧版本，读事务持 |
| 9 | chapters/01-introduction/chapter.md:104 | tab | 表 1-1 | **表 1-1　三个软件设计概览对比** |
| 10 | chapters/01-introduction/chapter.md:117 | fig | 图 1-2 | ![图 1-2 三个软件在五个维度上的定位雷达](diagrams/fig-1-2.svg) |
| 11 | chapters/01-introduction/chapter.md:118 | fig | 图 1-2 | 图 1-2　三个软件在五个维度上的定位雷达：低延迟、高吞吐、强一致、数据容量、查询灵活度。 |
| 12 | chapters/01-introduction/chapter.md:132 | tab | 表 1-2 | **表 1-2　使用视角 vs 架构视角对照** |
| 13 | chapters/01-introduction/chapter.md:139 | seeref | 详见 | | Kafka 副本 | 设 acks=all、min.insync.replicas=2（Kafka 的可靠性参数，详见第 4、7 章） | ISR 为何要"动态收缩"？主副本切换与一致性如何兼顾？ | |
| 14 | chapters/01-introduction/chapter.md:162 | seeref | 见 | **第一，先写日志还是先改数据？** 可靠存储系统的常见做法是先写日志（WAL）。原因是日志是顺序写，恢复时按顺序重放，比直接改散落各处的数据页快得多、也安全得多。 |
| 15 | chapters/01-introduction/chapter.md:168 | ch | 第 8 章 | **MySQL** 走 redo log 加两阶段提交，redo 记的是"页上哪个字节改成什么样"（严格说是物理到页、逻辑到操作的混合日志，详见第 8 章），恢复时机械重放，再配合 binlog 这种逻辑日志做复制。 |
| 16 | chapters/01-introduction/chapter.md:168 | seeref | 详见 | **MySQL** 走 redo log 加两阶段提交，redo 记的是"页上哪个字节改成什么样"（严格说是物理到页、逻辑到操作的混合日志，详见第 8 章），恢复时机械重放，再配合 binlog 这种逻辑日志做复制。 |
| 17 | chapters/01-introduction/chapter.md:171 | ch | 第 4 章 | 三种答案，一条共同主线：**顺序写的日志保证故障后可恢复，落盘粒度调节安全与吞吐的平衡。** 这条主线贯穿第 4 章（内存与磁盘）与第 9 章（数据同步），并在每一章里以不同的面貌重新出现。 |
| 18 | chapters/01-introduction/chapter.md:171 | ch | 第 9 章 | 三种答案，一条共同主线：**顺序写的日志保证故障后可恢复，落盘粒度调节安全与吞吐的平衡。** 这条主线贯穿第 4 章（内存与磁盘）与第 9 章（数据同步），并在每一章里以不同的面貌重新出现。 |
| 19 | chapters/01-introduction/chapter.md:189 | fig | 图 1-3 | ![图 1-3 全书章节结构](diagrams/fig-1-3.svg) |
| 20 | chapters/01-introduction/chapter.md:190 | fig | 图 1-3 | 图 1-3　全书章节结构：第 2 章数据结构与协议打底，从第 3 章起按"启动与关闭 → 内存与磁盘 → 分层 → 安全 → 集群 → 存储格式 → 数据同步"递进，第 10 章总结。 |
| 21 | chapters/01-introduction/chapter.md:190 | ch | 第 2 章 | 图 1-3　全书章节结构：第 2 章数据结构与协议打底，从第 3 章起按"启动与关闭 → 内存与磁盘 → 分层 → 安全 → 集群 → 存储格式 → 数据同步"递进，第 10 章总结。 |
| 22 | chapters/01-introduction/chapter.md:190 | ch | 第 3 章 | 图 1-3　全书章节结构：第 2 章数据结构与协议打底，从第 3 章起按"启动与关闭 → 内存与磁盘 → 分层 → 安全 → 集群 → 存储格式 → 数据同步"递进，第 10 章总结。 |
| 23 | chapters/01-introduction/chapter.md:190 | ch | 第 10 章 | 图 1-3　全书章节结构：第 2 章数据结构与协议打底，从第 3 章起按"启动与关闭 → 内存与磁盘 → 分层 → 安全 → 集群 → 存储格式 → 数据同步"递进，第 10 章总结。 |
| 24 | chapters/01-introduction/chapter.md:198 | fig | 图 1-1 | 图表约定如下。图编号统一为 `图 N-M`（第 N 章第 M 张图），表编号统一为 `表 N-M`（第 N 章第 M 张表），图与表各自独立连续编号。本章用到三张图（图 1-1、图 1-2、图 1-3）与两张内联表格（表 |
| 25 | chapters/01-introduction/chapter.md:198 | fig | 图 1-2 | 图表约定如下。图编号统一为 `图 N-M`（第 N 章第 M 张图），表编号统一为 `表 N-M`（第 N 章第 M 张表），图与表各自独立连续编号。本章用到三张图（图 1-1、图 1-2、图 1-3）与两张内联表格（表 |
| 26 | chapters/01-introduction/chapter.md:198 | fig | 图 1-3 | 图表约定如下。图编号统一为 `图 N-M`（第 N 章第 M 张图），表编号统一为 `表 N-M`（第 N 章第 M 张表），图与表各自独立连续编号。本章用到三张图（图 1-1、图 1-2、图 1-3）与两张内联表格（表 |
| 27 | chapters/01-introduction/chapter.md:198 | tab | 表 1-1 | 图表约定如下。图编号统一为 `图 N-M`（第 N 章第 M 张图），表编号统一为 `表 N-M`（第 N 章第 M 张表），图与表各自独立连续编号。本章用到三张图（图 1-1、图 1-2、图 1-3）与两张内联表格（表 |
| 28 | chapters/01-introduction/chapter.md:198 | tab | 表 1-2 | 图表约定如下。图编号统一为 `图 N-M`（第 N 章第 M 张图），表编号统一为 `表 N-M`（第 N 章第 M 张表），图与表各自独立连续编号。本章用到三张图（图 1-1、图 1-2、图 1-3）与两张内联表格（表 |
| 29 | chapters/01-introduction/chapter.md:206 | ch | 第 1 章 | **路径 A：系统建立。** 从第 1 章顺序读到第 10 章。适合想建立完整架构认知的读者。每一章都建立在前一章的基础上，读完整本书你会对后端基础设施的设计逻辑有一个连贯的理解。这是最推荐的路径，也是本书写作时假定的阅 |
| 30 | chapters/01-introduction/chapter.md:206 | ch | 第 10 章 | **路径 A：系统建立。** 从第 1 章顺序读到第 10 章。适合想建立完整架构认知的读者。每一章都建立在前一章的基础上，读完整本书你会对后端基础设施的设计逻辑有一个连贯的理解。这是最推荐的路径，也是本书写作时假定的阅 |
| 31 | chapters/01-introduction/chapter.md:208 | ch | 第 1 章 | **路径 B：按需精读。** 先读第 1 章和第 10 章建立全局观，再按工作场景跳读主题章。比如你正在排查持久化问题，直接看第 4 章；做高可用选型或优化存储成本，则分别对应第 7 章和第 8 章。这条路径适合已经有相 |
| 32 | chapters/01-introduction/chapter.md:208 | ch | 第 10 章 | **路径 B：按需精读。** 先读第 1 章和第 10 章建立全局观，再按工作场景跳读主题章。比如你正在排查持久化问题，直接看第 4 章；做高可用选型或优化存储成本，则分别对应第 7 章和第 8 章。这条路径适合已经有相 |
| 33 | chapters/01-introduction/chapter.md:208 | ch | 第 4 章 | **路径 B：按需精读。** 先读第 1 章和第 10 章建立全局观，再按工作场景跳读主题章。比如你正在排查持久化问题，直接看第 4 章；做高可用选型或优化存储成本，则分别对应第 7 章和第 8 章。这条路径适合已经有相 |
| 34 | chapters/01-introduction/chapter.md:208 | ch | 第 7 章 | **路径 B：按需精读。** 先读第 1 章和第 10 章建立全局观，再按工作场景跳读主题章。比如你正在排查持久化问题，直接看第 4 章；做高可用选型或优化存储成本，则分别对应第 7 章和第 8 章。这条路径适合已经有相 |
| 35 | chapters/01-introduction/chapter.md:208 | ch | 第 8 章 | **路径 B：按需精读。** 先读第 1 章和第 10 章建立全局观，再按工作场景跳读主题章。比如你正在排查持久化问题，直接看第 4 章；做高可用选型或优化存储成本，则分别对应第 7 章和第 8 章。这条路径适合已经有相 |
| 36 | chapters/01-introduction/chapter.md:216 | ch | 第 2 章 | 第 2 章讨论三个软件的内部数据结构和通信协议，这是后面所有章节的基础。接着从最朴素也最容易被忽视的启动与关闭讲起（第 3 章生命周期管理）。随后进入存储系统的核心命题"内存与磁盘"（第 4 章），看它们如何处理"快"与 |
| 37 | chapters/01-introduction/chapter.md:216 | ch | 第 3 章 | 第 2 章讨论三个软件的内部数据结构和通信协议，这是后面所有章节的基础。接着从最朴素也最容易被忽视的启动与关闭讲起（第 3 章生命周期管理）。随后进入存储系统的核心命题"内存与磁盘"（第 4 章），看它们如何处理"快"与 |
| 38 | chapters/01-introduction/chapter.md:216 | ch | 第 4 章 | 第 2 章讨论三个软件的内部数据结构和通信协议，这是后面所有章节的基础。接着从最朴素也最容易被忽视的启动与关闭讲起（第 3 章生命周期管理）。随后进入存储系统的核心命题"内存与磁盘"（第 4 章），看它们如何处理"快"与 |
| 39 | chapters/01-introduction/chapter.md:216 | ch | 第 5 章 | 第 2 章讨论三个软件的内部数据结构和通信协议，这是后面所有章节的基础。接着从最朴素也最容易被忽视的启动与关闭讲起（第 3 章生命周期管理）。随后进入存储系统的核心命题"内存与磁盘"（第 4 章），看它们如何处理"快"与 |
| 40 | chapters/01-introduction/chapter.md:216 | ch | 第 6 章 | 第 2 章讨论三个软件的内部数据结构和通信协议，这是后面所有章节的基础。接着从最朴素也最容易被忽视的启动与关闭讲起（第 3 章生命周期管理）。随后进入存储系统的核心命题"内存与磁盘"（第 4 章），看它们如何处理"快"与 |
| 41 | chapters/01-introduction/chapter.md:216 | ch | 第 7 章 | 第 2 章讨论三个软件的内部数据结构和通信协议，这是后面所有章节的基础。接着从最朴素也最容易被忽视的启动与关闭讲起（第 3 章生命周期管理）。随后进入存储系统的核心命题"内存与磁盘"（第 4 章），看它们如何处理"快"与 |
| 42 | chapters/01-introduction/chapter.md:216 | ch | 第 8 章 | 第 2 章讨论三个软件的内部数据结构和通信协议，这是后面所有章节的基础。接着从最朴素也最容易被忽视的启动与关闭讲起（第 3 章生命周期管理）。随后进入存储系统的核心命题"内存与磁盘"（第 4 章），看它们如何处理"快"与 |
| 43 | chapters/01-introduction/chapter.md:216 | ch | 第 9 章 | 第 2 章讨论三个软件的内部数据结构和通信协议，这是后面所有章节的基础。接着从最朴素也最容易被忽视的启动与关闭讲起（第 3 章生命周期管理）。随后进入存储系统的核心命题"内存与磁盘"（第 4 章），看它们如何处理"快"与 |
| 44 | chapters/01-introduction/chapter.md:216 | ch | 第 10 章 | 第 2 章讨论三个软件的内部数据结构和通信协议，这是后面所有章节的基础。接着从最朴素也最容易被忽视的启动与关闭讲起（第 3 章生命周期管理）。随后进入存储系统的核心命题"内存与磁盘"（第 4 章），看它们如何处理"快"与 |
| 45 | chapters/01-introduction/chapter.md:222 | sec | 1.2 节 | 这一章讲清了三个问题。为什么选 Redis、MySQL、Kafka 当样本：因为它们正好覆盖了内存型、持久化型、流式型三种核心范式。它们各自是什么样：1.2 节的三段概览给了各自的出身、抽象与代价。架构视角与使用视角有什 |
| 46 | chapters/02-data-structures-protocols/chapter.md:34 | fig | 图 2-1 | **惰性释放**：缩短字符串时不立即归还内存，只改 `len` 字段（`alloc` 不动，保留已分配空间），把多余空间留作未来的追加缓冲；想真正归还内存需要显式调用 `sdsRemoveFreeSpace`，SDS 自 |
| 47 | chapters/02-data-structures-protocols/chapter.md:36 | fig | 图 2-1 | ![图 2-1 SDS 与 C 字符串的内存布局对比](diagrams/fig-2-1.svg) |
| 48 | chapters/02-data-structures-protocols/chapter.md:37 | fig | 图 2-1 | 图 2-1　SDS 与 C 字符串的内存布局对比：同一个 hello 的两种存法，差别集中在 SDS 的头部。 |
| 49 | chapters/02-data-structures-protocols/chapter.md:41 | fig | 图 2-2 | **跳表（skiplist）** 是 Redis 有序集合（ZSET）底层两种结构之一。跳表是多层有序链表，最底层是一条完整的有序双向链表，上面几层是抽稀的索引层，每隔几个节点保留一个指针。查找时从最顶层快速定位到目标附 |
| 50 | chapters/02-data-structures-protocols/chapter.md:41 | seeref | 见 | **跳表（skiplist）** 是 Redis 有序集合（ZSET）底层两种结构之一。跳表是多层有序链表，最底层是一条完整的有序双向链表，上面几层是抽稀的索引层，每隔几个节点保留一个指针。查找时从最顶层快速定位到目标附 |
| 51 | chapters/02-data-structures-protocols/chapter.md:43 | fig | 图 2-2 | ![图 2-2 跳表的多层索引与查找路径](diagrams/fig-2-2.svg) |
| 52 | chapters/02-data-structures-protocols/chapter.md:44 | fig | 图 2-2 | 图 2-2　跳表的多层索引与查找路径：以查找 17 为例。 |
| 53 | chapters/02-data-structures-protocols/chapter.md:46 | fig | 图 2-2 | 图 2-2 中从 head 到 17 的路径：每一步要么前进、要么下沉，越往下一次跨过的节点越少，到底层逐个对齐。本章开头排行榜的例子也是这两段：按分数定位起点走这条下沉路径，按名次拉一段沿底层链表前进。 |
| 54 | chapters/02-data-structures-protocols/chapter.md:52 | fig | 图 2-3 | 这套机制保证单次字典操作不会因为搬迁而卡顿，每次只搬一个桶，摊还到后续所有操作里。这与前文 SDS 的做法是同一个思想：**用摊还替换集中，把省不掉的工作分摊到后续每次操作里**。这套双表搬迁画出来就是图 2-3。 |
| 55 | chapters/02-data-structures-protocols/chapter.md:54 | fig | 图 2-3 | ![图 2-3 渐进式 rehash 的双表搬迁过程](diagrams/fig-2-3.svg) |
| 56 | chapters/02-data-structures-protocols/chapter.md:55 | fig | 图 2-3 | 图 2-3　渐进式 rehash 的双表搬迁过程：搬迁进行到一半的一个时刻。 |
| 57 | chapters/02-data-structures-protocols/chapter.md:59 | fig | 图 2-4 | **压缩列表（ziplist）与紧凑列表（listpack）** 是 Redis 把内存密度做到最高的数据结构。ziplist 是一块连续内存，所有元素紧挨着存，没有指针开销。每个元素存的是"前一个元素长度 + 自己的编 |
| 58 | chapters/02-data-structures-protocols/chapter.md:61 | fig | 图 2-4 | ![图 2-4 ziplist 连锁更新与 listpack 的消除](diagrams/fig-2-4.svg) |
| 59 | chapters/02-data-structures-protocols/chapter.md:62 | fig | 图 2-4 | 图 2-4　ziplist 连锁更新与 listpack 的消除：同一个元素变长，在两种格式里的不同后果。 |
| 60 | chapters/02-data-structures-protocols/chapter.md:70 | fig | 图 2-5 | 第二条是**类型升级**。当集合里插入一个非整数元素时，intset 作为纯整数结构装不下，会自动升级：7.2 起小集合先转 listpack，超过阈值（默认 128 个元素）再升级为哈希表；7.2 之前直接升级为哈希表 |
| 61 | chapters/02-data-structures-protocols/chapter.md:72 | fig | 图 2-5 | ![图 2-5 Redis 五种底层数据结构的适用场景与升级路径](diagrams/fig-2-5.svg) |
| 62 | chapters/02-data-structures-protocols/chapter.md:73 | fig | 图 2-5 | 图 2-5　Redis 五种底层结构与编码升级路径：五种结构各成卡片，底部三条切换链标出小数据编码的升级去向。 |
| 63 | chapters/02-data-structures-protocols/chapter.md:81 | fig | 图 2-6 | **B+ 树** 是 InnoDB 唯一的主索引结构。一棵 B+ 树从上到下：根节点、内部节点（非叶子）、叶子节点。内部节点只存键和子节点指针（一个 16KB 页就能容纳几百个键，树极矮），叶子节点存完整行数据（这是聚簇 |
| 64 | chapters/02-data-structures-protocols/chapter.md:81 | ch | 第 8 章 | **B+ 树** 是 InnoDB 唯一的主索引结构。一棵 B+ 树从上到下：根节点、内部节点（非叶子）、叶子节点。内部节点只存键和子节点指针（一个 16KB 页就能容纳几百个键，树极矮），叶子节点存完整行数据（这是聚簇 |
| 65 | chapters/02-data-structures-protocols/chapter.md:81 | seeref | 见 | **B+ 树** 是 InnoDB 唯一的主索引结构。一棵 B+ 树从上到下：根节点、内部节点（非叶子）、叶子节点。内部节点只存键和子节点指针（一个 16KB 页就能容纳几百个键，树极矮），叶子节点存完整行数据（这是聚簇 |
| 66 | chapters/02-data-structures-protocols/chapter.md:83 | fig | 图 2-6 | ![图 2-6 MySQL InnoDB B+ 树结构](diagrams/fig-2-6.svg) |
| 67 | chapters/02-data-structures-protocols/chapter.md:84 | fig | 图 2-6 | 图 2-6　InnoDB B+ 树三层结构：一棵示例树，每个方框对应一个 16KB 磁盘页。 |
| 68 | chapters/02-data-structures-protocols/chapter.md:86 | fig | 图 2-2 | 这张图与图 2-2 的跳表对照：两者都为顺序访问准备了底层结构，差别是跳表的节点是内存里的单个节点，B+ 树的节点是一整个 16KB 磁盘页——节点的大小，对齐的是所在介质的访问单位。 |
| 69 | chapters/02-data-structures-protocols/chapter.md:100 | tab | 表 2-1 | **表 2-1　Kafka RecordBatch V2 头部字段** |
| 70 | chapters/02-data-structures-protocols/chapter.md:110 | sec | 9.4 节 | | `producerId` / `producerEpoch` / `baseSequence` | 幂等 + 事务所需的 Producer 状态（Broker 按序列号对重试去重，见 9.4 节） | |
| 71 | chapters/02-data-structures-protocols/chapter.md:110 | seeref | 见 | | `producerId` / `producerEpoch` / `baseSequence` | 幂等 + 事务所需的 Producer 状态（Broker 按序列号对重试去重，见 9.4 节） | |
| 72 | chapters/02-data-structures-protocols/chapter.md:113 | fig | 图 2-7 | 头部之后是实际的消息记录。**每条记录不存绝对 offset 和绝对时间戳**，而是存它和 `baseOffset` / `baseTimestamp` 的差值。差值编码在一个 Batch 内能把编码空间省到很小。V0  |
| 73 | chapters/02-data-structures-protocols/chapter.md:113 | seeref | 见 | 头部之后是实际的消息记录。**每条记录不存绝对 offset 和绝对时间戳**，而是存它和 `baseOffset` / `baseTimestamp` 的差值。差值编码在一个 Batch 内能把编码空间省到很小。V0  |
| 74 | chapters/02-data-structures-protocols/chapter.md:115 | fig | 图 2-7 | ![图 2-7 Kafka RecordBatch V2 字段布局](diagrams/fig-2-7.svg) |
| 75 | chapters/02-data-structures-protocols/chapter.md:116 | fig | 图 2-7 | 图 2-7　RecordBatch V2 字段布局：61 字节头部共享整批元数据，每条 Record 只存与 base 的差值。 |
| 76 | chapters/02-data-structures-protocols/chapter.md:118 | seeref | 见 | 这套设计的取舍摆在明面上。相似消息聚成一批，压缩收益通常可达数倍（zstd，压缩比取决于消息内容相似度与压缩级别，基准测试中常见 2–6 倍）；差值编码把每条记录的元数据开销降到个位数字节；CRC（循环冗余校验）整批只算 |
| 77 | chapters/02-data-structures-protocols/chapter.md:156 | fig | 图 2-8 | ![图 2-8 三个软件通信协议对比：RESP 文本 vs MySQL 二进制 vs Kafka 请求/响应](diagrams/fig-2-8.svg) |
| 78 | chapters/02-data-structures-protocols/chapter.md:157 | fig | 图 2-8 | 图 2-8　三个软件通信协议对比：文本行服务人眼可读与实现简单，二进制服务带宽与解析开销，版本化请求头服务演进兼容。 |
| 79 | chapters/02-data-structures-protocols/chapter.md:165 | tab | 表 2-2 | **表 2-2　三个软件数据结构与协议的横向对比** |
| 80 | chapters/03-lifecycle/README.md:16 | tab | 表 3-1 | - 检查表 3-1、表 3-2 与正文解读是否互相支撑。 |
| 81 | chapters/03-lifecycle/README.md:16 | tab | 表 3-2 | - 检查表 3-1、表 3-2 与正文解读是否互相支撑。 |
| 82 | chapters/03-lifecycle/chapter.md:7 | ch | 第 4 章 | 同样是 `kill -9`，对 Redis 通常只是丢掉最近一小段时间的数据（丢多少取决于持久化配置，详见第 4 章），对 MySQL 可能要做崩溃恢复（crash recovery），对 Kafka 则可能触发分区的  |
| 83 | chapters/03-lifecycle/chapter.md:7 | seeref | 详见 | 同样是 `kill -9`，对 Redis 通常只是丢掉最近一小段时间的数据（丢多少取决于持久化配置，详见第 4 章），对 MySQL 可能要做崩溃恢复（crash recovery），对 Kafka 则可能触发分区的  |
| 84 | chapters/03-lifecycle/chapter.md:21 | seeref | 见 | 3. **单机视角 vs 分布式视角。** 单机软件的关闭只影响自身。分布式组件的关闭是一个集群事件，要让 Leader 迁移、让副本同步可见。 |
| 85 | chapters/03-lifecycle/chapter.md:23 | fig | 图 3-1 | 图 3-1 把启动与关闭画成一对"对称"的过程：启动是重建，关闭是快照，中间任何一次崩溃或 `kill -9` 都会把系统重新拉回"不完整状态"，下次启动得多做恢复工作。 |
| 86 | chapters/03-lifecycle/chapter.md:25 | fig | 图 3-1 | ![图 3-1 启动与关闭：状态机的重建与快照](diagrams/fig-3-1.svg) |
| 87 | chapters/03-lifecycle/chapter.md:26 | fig | 图 3-1 | 图 3-1　启动与关闭作为状态机重建与快照的对称过程。 |
| 88 | chapters/03-lifecycle/chapter.md:40 | seeref | 见 | **第二段：基础设施就位。** 这一段做四件事：注册信号处理器、创建事件循环、分配数据库数组、打开监听端口。信号处理器里，SIGTERM/SIGINT 触发优雅关闭，SIGPIPE 则忽略；RDB/AOF 子进程的退出不 |
| 89 | chapters/03-lifecycle/chapter.md:42 | fig | 图 3-2 | **第三段：数据恢复。AOF 优先于 RDB。** 如果 AOF（仅追加文件）开启且存在，Redis 就加载 AOF；否则加载 RDB（快照文件，二进制格式，快但只到上次快照点）。图 3-2 完整呈现了这段流程。Redi |
| 90 | chapters/03-lifecycle/chapter.md:44 | fig | 图 3-2 | ![图 3-2 Redis 启动四段式时序](diagrams/fig-3-2.svg) |
| 91 | chapters/03-lifecycle/chapter.md:45 | fig | 图 3-2 | 图 3-2　Redis 启动四段式：配置 → 基础设施 → 数据恢复 → 事件循环，数据恢复段含 AOF/RDB 分支。 |
| 92 | chapters/03-lifecycle/chapter.md:55 | fig | 图 3-3 | 图 3-3 画出了关闭流程的主体。 |
| 93 | chapters/03-lifecycle/chapter.md:57 | fig | 图 3-3 | ![图 3-3 Redis 关闭流程](diagrams/fig-3-3.svg) |
| 94 | chapters/03-lifecycle/chapter.md:58 | fig | 图 3-3 | 图 3-3　Redis 关闭流程：先处理 RDB/AOF 重写子进程，刷 AOF 缓冲，再按 SAVE/NOSAVE 决定 RDB 落盘与否。 |
| 95 | chapters/03-lifecycle/chapter.md:80 | seeref | 见 | **配置加载段**按固定顺序读取多个 my.cnf 路径（Unix 上从 `/etc/my.cnf` 读到 `~/.my.cnf`，同名选项后读的覆盖先读的），再叠加命令行覆盖。取舍：多文件叠加方便运维，代价是"配置到底 |
| 96 | chapters/03-lifecycle/chapter.md:88 | fig | 图 3-4 | 第三步是 MySQL 启动比 Redis 慢的根本原因。它必须把"崩溃那一刻内存里未持久化的页修改"和"事务的提交状态"分开处理，最终恢复出严格的事务一致性：已提交的全部保留，未提交的全部回滚。图 3-4 把崩溃恢复画成 |
| 97 | chapters/03-lifecycle/chapter.md:90 | fig | 图 3-4 | ![图 3-4 InnoDB 崩溃恢复时序](diagrams/fig-3-4.svg) |
| 98 | chapters/03-lifecycle/chapter.md:91 | fig | 图 3-4 | 图 3-4　InnoDB 崩溃恢复：从 checkpoint LSN 扫描 redo 无差别重放所有页修改，再用 undo 回滚未提交事务。 |
| 99 | chapters/03-lifecycle/chapter.md:105 | tab | 表 3-1 | MySQL 把"关闭时做多少清理"做成一个可配置参数 `innodb_fast_shutdown`，取 0、1、2 三档。三档之间要权衡的就是一致性和可用性：多清理一步，关闭更安全，但停服时间更长。表 3-1 把三档的取 |
| 100 | chapters/03-lifecycle/chapter.md:107 | tab | 表 3-1 | **表 3-1　innodb_fast_shutdown 三档对比**（这是 MySQL 专属参数，Redis 与 Kafka 无对应概念） |
| 101 | chapters/03-lifecycle/chapter.md:119 | ch | 第 4 章 | 默认设为 1 而不是 0：档位 0 要求的完整 purge 和修改缓冲合并，在繁忙库上可能耗时几十分钟甚至更久（修改缓冲把对二级索引页的修改先缓存在内存，等页读入时再补写回去，第 4 章详述）。这些工作对正确性没有任何贡 |
| 102 | chapters/03-lifecycle/chapter.md:123 | seeref | 见 | 实际运维中"为什么 mysqld 关不掉"是高频排障问题，常见根因有几类： |
| 103 | chapters/03-lifecycle/chapter.md:141 | ch | 第 7 章 | 2. **元数据管理初始化（KRaft 核心）。** 在 KRaft 模式下，元数据本身变成了一份用 Raft 复制的日志（Raft 是什么，第 7 章有一分钟直觉讲解）。节点启动时要先追上这份元数据日志，才能确定当前节 |
| 104 | chapters/03-lifecycle/chapter.md:143 | fig | 图 3-5 | 4. **三层网络架构。** 图 3-5 画出了它的布局。 |
| 105 | chapters/03-lifecycle/chapter.md:145 | fig | 图 3-5 | ![图 3-5 Kafka 三层网络架构](diagrams/fig-3-5.svg) |
| 106 | chapters/03-lifecycle/chapter.md:146 | fig | 图 3-5 | 图 3-5　Kafka 三层网络架构：Acceptor 接连接、Processor 解析协议、Handler 线程池执行，请求与响应走队列。 |
| 107 | chapters/03-lifecycle/chapter.md:148 | ch | 第 5 章 | 三层网络的设计意图是把 I/O 密集（收发包）和 CPU 密集（业务处理）分到不同的线程池，避免互相拖累。最外层 Acceptor（1 个）接收新连接，轮询分发给 Processor。Processor（默认 3 个，对 |
| 108 | chapters/03-lifecycle/chapter.md:161 | seeref | 见 | **普通关闭**（受控关闭被禁用——即 `controlled.shutdown.enable=false`——或受控关闭失败时）的步骤是：标记停服（停收新请求）→ 关网络层（处理完在途请求）→ 停控制器 → 停副本管理 |
| 109 | chapters/03-lifecycle/chapter.md:163 | fig | 图 3-6 | **受控关闭（Controlled Shutdown）**让 Broker 在真正退出之前，先发请求给 Controller，通知它自己即将退出。Controller 收到后，**提前把该 Broker 上的 Leade |
| 110 | chapters/03-lifecycle/chapter.md:165 | fig | 图 3-6 | ![图 3-6 Kafka 受控关闭时序（对照普通关闭）](diagrams/fig-3-6.svg) |
| 111 | chapters/03-lifecycle/chapter.md:166 | fig | 图 3-6 | 图 3-6　受控关闭：Broker 先告知 Controller，Controller 提前迁移 Leader 后才放行；对照普通关闭的抖动窗口。 |
| 112 | chapters/03-lifecycle/chapter.md:170 | seeref | 见 | 受控关闭也有前提：Controller 必须可达，且 Leader 迁移要在超时阈值内完成。否则 Broker 会退化为普通关闭，不再死等。这是分布式系统常见的"有更好选项时就用，没有就降级"的工程化思路。受控关闭由开关 |
| 113 | chapters/03-lifecycle/chapter.md:182 | sec | 3.2 节 | **Redis** 的优雅关闭不等 AOF/RDB 重写子进程，第一步就把它们杀掉，关闭本身不为重写耗时。真正吃掉 grace period 的，是它自己的最后一次落盘——只要配了 save 点（出厂默认就配）且不走 N |
| 114 | chapters/03-lifecycle/chapter.md:184 | sec | 3.3 节 | **MySQL** 默认 `innodb_fast_shutdown=1`，受控关闭时刷脏页但跳过完整 purge 与 change buffer 合并；一旦被 SIGKILL 强杀，连快速关闭流程都没机会走，只能交给下 |
| 115 | chapters/03-lifecycle/chapter.md:188 | seeref | 见 | K8s 的探针（probe）有三类，职责各不相同：startup 探针在成功之前抑制另外两类，给慢启动的数据库留出整段恢复时间；liveness 失败触发容器重启；readiness 失败只摘流量、不重启。把"数据库还在 |
| 116 | chapters/03-lifecycle/chapter.md:194 | tab | 表 3-2 | 表 3-2 按六个维度并排对比三家的启动与关闭做法，三栏顺序固定为 Redis | MySQL | Kafka。 |
| 117 | chapters/03-lifecycle/chapter.md:196 | tab | 表 3-2 | **表 3-2　三个软件生命周期六维对比** |
| 118 | chapters/03-lifecycle/chapter.md:213 | ch | 第 7 章 | **第三，单机 vs 分布式是分界线。** 前两家的关闭只是自己的事，Kafka 的关闭要和 Controller 交接 Leader 职责，牵动整个集群。这道分界将在第 7 章展开，Leader 选举、ISR 维护等机 |
| 119 | chapters/03-lifecycle/chapter.md:229 | sec | 3.4 节 | 优雅关闭做三件事：完成已接受的请求、把脏状态落盘、释放占用的资源。在分布式系统里还要加第四件：把职责移交给别人（Kafka 受控关闭）。这四件事的顺序很重要。单机系统的关闭是先完成请求、再落盘、再释放；分布式系统里移交要 |
| 120 | chapters/03-lifecycle/chapter.md:233 | seeref | 见 | MySQL 三档关闭、Redis SAVE/NOSAVE、Kafka 普通关闭 vs 受控关闭。这些"更快"的选项都是把某部分清理或迁移工作挪到别处：留到下次启动、交给集群其他节点，或直接丢弃。我自己设计系统时，会先想清 |
| 121 | chapters/03-lifecycle/chapter.md:237 | ch | 第 5 章 | 这三个软件的启动都遵循"配置 → 基础设施 → 核心服务 → 数据恢复 → 对外服务"的顺序。这个顺序是依赖关系的硬约束：网络层依赖存储引擎就绪（否则客户端连进来会拿到一个莫名其妙的报错），存储引擎依赖配置（否则不知道数 |
| 122 | chapters/03-lifecycle/chapter.md:241 | sec | 3.3 节 | "Ready to accept connections" / "ready for connections" / "[KafkaServer id=0] started" 是状态机的里程碑标记，承载明确的语义而非噪音。 |
| 123 | chapters/03-lifecycle/chapter.md:241 | sec | 3.4 节 | "Ready to accept connections" / "ready for connections" / "[KafkaServer id=0] started" 是状态机的里程碑标记，承载明确的语义而非噪音。 |
| 124 | chapters/03-lifecycle/chapter.md:249 | ch | 第 4 章 | 其一，关闭时的刷盘保证：Redis AOF/RDB、MySQL redo log、Kafka append-only log 在"快与持久"之间的取舍，正是第 4 章内存与磁盘管理的核心主线。其二，分层与依赖先行的初始化 |
| 125 | chapters/03-lifecycle/chapter.md:249 | ch | 第 5 章 | 其一，关闭时的刷盘保证：Redis AOF/RDB、MySQL redo log、Kafka append-only log 在"快与持久"之间的取舍，正是第 4 章内存与磁盘管理的核心主线。其二，分层与依赖先行的初始化 |
| 126 | chapters/04-memory-disk/chapter.md:9 | sec | 4.3 节 | 我参与过一次选型争论：缓存到底该用 Redis 还是 MySQL？有人坚持"MySQL 有内存表和 Query Cache，够用了"。我花了一下午把两者的访问模式拉了一张表：Redis 是小数据量、高频访问下的 O(1) |
| 127 | chapters/04-memory-disk/chapter.md:9 | sec | 5.3.2 节 | 我参与过一次选型争论：缓存到底该用 Redis 还是 MySQL？有人坚持"MySQL 有内存表和 Query Cache，够用了"。我花了一下午把两者的访问模式拉了一张表：Redis 是小数据量、高频访问下的 O(1) |
| 128 | chapters/04-memory-disk/chapter.md:9 | seeref | 见 | 我参与过一次选型争论：缓存到底该用 Redis 还是 MySQL？有人坚持"MySQL 有内存表和 Query Cache，够用了"。我花了一下午把两者的访问模式拉了一张表：Redis 是小数据量、高频访问下的 O(1) |
| 129 | chapters/04-memory-disk/chapter.md:9 | seeref | 见 | 我参与过一次选型争论：缓存到底该用 Redis 还是 MySQL？有人坚持"MySQL 有内存表和 Query Cache，够用了"。我花了一下午把两者的访问模式拉了一张表：Redis 是小数据量、高频访问下的 O(1) |
| 130 | chapters/04-memory-disk/chapter.md:11 | ch | 第 7 章 | 这个选择在第 7 章集群、第 9 章同步里会被反复追问，但方案的方向，本章从内存和磁盘的物理差异里就能推出来。 |
| 131 | chapters/04-memory-disk/chapter.md:11 | ch | 第 9 章 | 这个选择在第 7 章集群、第 9 章同步里会被反复追问，但方案的方向，本章从内存和磁盘的物理差异里就能推出来。 |
| 132 | chapters/04-memory-disk/chapter.md:19 | tab | 表 4-1 | **表 4-1　存储介质的访问延迟数量级** |
| 133 | chapters/04-memory-disk/chapter.md:34 | seeref | 见 | > **Redis fork 开销：随实例内存增长**。fork 要拷贝页表，阻塞时间随实例内存线性上升，小实例几十毫秒，大实例（几十 GB 以上）可达数百毫秒，还受页表大小和是否开启透明大页（THP）影响。fork 期 |
| 134 | chapters/04-memory-disk/chapter.md:42 | fig | 图 4-1 | ![图 4-1 存储层次访问延迟的数量级（对数轴）](diagrams/fig-4-1.svg) |
| 135 | chapters/04-memory-disk/chapter.md:43 | fig | 图 4-1 | 图 4-1　存储层次访问延迟的数量级（对数轴）：内存到机械盘横跨五个数量级。 |
| 136 | chapters/04-memory-disk/chapter.md:67 | ch | 第 2 章 | Redis 在官方文档里把自己定义为"内存数据结构存储（in-memory data structure store）"，而不是"带内存的缓存"。这一定位下，Redis 的一切取舍围绕一个前提：所有数据默认驻留在内存中， |
| 137 | chapters/04-memory-disk/chapter.md:67 | seeref | 详见 | Redis 在官方文档里把自己定义为"内存数据结构存储（in-memory data structure store）"，而不是"带内存的缓存"。这一定位下，Redis 的一切取舍围绕一个前提：所有数据默认驻留在内存中， |
| 138 | chapters/04-memory-disk/chapter.md:87 | fig | 图 4-2 | ![图 4-2 Redis 近似 LRU 采样淘汰与 LFU 计数器衰减机制](diagrams/fig-4-2.svg) |
| 139 | chapters/04-memory-disk/chapter.md:88 | fig | 图 4-2 | 图 4-2　Redis 近似 LRU 采样淘汰与 LFU 计数器衰减机制 |
| 140 | chapters/04-memory-disk/chapter.md:104 | ch | 第 8 章 | 这三档本质上是同一个取舍的三个落点：可靠性 vs 性能。很多生产环境会选择 `everysec`，代价只是每秒一次的 `fsync`。`appendfsync` 的默认值确实是 `everysec`，但 Redis 7. |
| 141 | chapters/04-memory-disk/chapter.md:104 | seeref | 详见 | 这三档本质上是同一个取舍的三个落点：可靠性 vs 性能。很多生产环境会选择 `everysec`，代价只是每秒一次的 `fsync`。`appendfsync` 的默认值确实是 `everysec`，但 Redis 7. |
| 142 | chapters/04-memory-disk/chapter.md:106 | seeref | 见 | AOF 有一个绕不开的问题：日志只会越写越长。一个键被反复 `INCR` 一万次，AOF 里就有一万条 `INCR`。**AOF 重写** 解决这个问题。重写是按内存当前状态重新生成一份最小的命令集（把那一万条 `INC |
| 143 | chapters/04-memory-disk/chapter.md:110 | fig | 图 4-3 | **7.0 的多部分 AOF（Multi-Part AOF）改造**做了几件事。7.0 之前 AOF 是一个单文件（RDB 前导与增量命令混在一起）；7.0 把它拆成了一个目录（`appendonlydir/`），里面由 |
| 144 | chapters/04-memory-disk/chapter.md:110 | seeref | 详见 | **7.0 的多部分 AOF（Multi-Part AOF）改造**做了几件事。7.0 之前 AOF 是一个单文件（RDB 前导与增量命令混在一起）；7.0 把它拆成了一个目录（`appendonlydir/`），里面由 |
| 145 | chapters/04-memory-disk/chapter.md:114 | fig | 图 4-3 | ![图 4-3 Redis 持久化数据流（RDB 快照 / AOF 含混合持久化）](diagrams/fig-4-3.svg) |
| 146 | chapters/04-memory-disk/chapter.md:115 | fig | 图 4-3 | 图 4-3　Redis 持久化数据流（RDB 快照 / AOF 含混合持久化） |
| 147 | chapters/04-memory-disk/chapter.md:120 | ch | 第 7 章 | Redis 的取舍可以一句话概括：它付出内存成本、接受秒级的持久化窗口，换来读写低延迟和原生的多种数据结构。这套取舍在缓存和快速键值场景成立：访问频繁、对延迟敏感、数据可重建或可容忍少量丢失。代价是容量受物理内存约束。生 |
| 148 | chapters/04-memory-disk/chapter.md:120 | seeref | 详见 | Redis 的取舍可以一句话概括：它付出内存成本、接受秒级的持久化窗口，换来读写低延迟和原生的多种数据结构。这套取舍在缓存和快速键值场景成立：访问频繁、对延迟敏感、数据可重建或可容忍少量丢失。代价是容量受物理内存约束。生 |
| 149 | chapters/04-memory-disk/chapter.md:132 | seeref | 见 | 由于这个假设，MySQL 的延迟不是常数，它取决于"你访问的页此刻在不在内存里"。一个刚启动的实例缓冲池是空的，所有访问都打磁盘，延迟很高。跑稳之后热数据进了内存，延迟降下来。某次大扫描把热数据替换出去了，延迟又会显著上 |
| 150 | chapters/04-memory-disk/chapter.md:148 | fig | 图 4-4 | ![图 4-4 InnoDB 缓冲池三分链表（Free / LRU 新老分区 / Flush）](diagrams/fig-4-4.svg) |
| 151 | chapters/04-memory-disk/chapter.md:149 | fig | 图 4-4 | 图 4-4　InnoDB 缓冲池三分链表（Free / LRU 新老分区 / Flush） |
| 152 | chapters/04-memory-disk/chapter.md:162 | fig | 图 4-5 | ![图 4-5 MySQL 一次写操作的全链路时序（缓冲池→redo log→双写→刷盘）](diagrams/fig-4-5.svg) |
| 153 | chapters/04-memory-disk/chapter.md:163 | fig | 图 4-5 | 图 4-5　MySQL 一次写操作的全链路时序（缓冲池→redo log→双写→刷盘） |
| 154 | chapters/04-memory-disk/chapter.md:164 | fig | 图 4-5 | 图 4-5 的时序：事务提交时先把 redo log 写到日志文件并落盘（保证持久性）。脏页随后进入 Flush List。后台线程把脏页先写到双写缓冲再写到表空间。最后推进 checkpoint，标记之前的日志可以回收 |
| 155 | chapters/04-memory-disk/chapter.md:210 | fig | 图 4-6 | ![图 4-6 Kafka 生产-存储-消费的零拷贝数据流](diagrams/fig-4-6.svg) |
| 156 | chapters/04-memory-disk/chapter.md:211 | fig | 图 4-6 | 图 4-6　Kafka 生产-存储-消费的零拷贝数据流 |
| 157 | chapters/04-memory-disk/chapter.md:224 | sec | 7.4.3 节 | 这三档是"吞吐 vs 不丢"这同一个取舍的三种档位，和 Redis 的 `appendfsync`、MySQL 的 `innodb_flush_log_at_trx_commit` 同构。只是场景换到了分布式。`acks |
| 158 | chapters/04-memory-disk/chapter.md:224 | ch | 第 7 章 | 这三档是"吞吐 vs 不丢"这同一个取舍的三种档位，和 Redis 的 `appendfsync`、MySQL 的 `innodb_flush_log_at_trx_commit` 同构。只是场景换到了分布式。`acks |
| 159 | chapters/04-memory-disk/chapter.md:224 | ch | 第 9 章 | 这三档是"吞吐 vs 不丢"这同一个取舍的三种档位，和 Redis 的 `appendfsync`、MySQL 的 `innodb_flush_log_at_trx_commit` 同构。只是场景换到了分布式。`acks |
| 160 | chapters/04-memory-disk/chapter.md:224 | seeref | 见 | 这三档是"吞吐 vs 不丢"这同一个取舍的三种档位，和 Redis 的 `appendfsync`、MySQL 的 `innodb_flush_log_at_trx_commit` 同构。只是场景换到了分布式。`acks |
| 161 | chapters/04-memory-disk/chapter.md:224 | seeref | 见 | 这三档是"吞吐 vs 不丢"这同一个取舍的三种档位，和 Redis 的 `appendfsync`、MySQL 的 `innodb_flush_log_at_trx_commit` 同构。只是场景换到了分布式。`acks |
| 162 | chapters/04-memory-disk/chapter.md:228 | tab | 表 4-2 | **表 4-2　Kafka 日志段（segment）与索引文件布局** |
| 163 | chapters/04-memory-disk/chapter.md:249 | tab | 表 4-3 | **表 4-3　三个软件"内存-磁盘"哲学横向对比** |
| 164 | chapters/04-memory-disk/chapter.md:257 | ch | 第 3 章 | | 崩溃恢复代价 | 加载 RDB / 重放 AOF（大实例数分钟） | 重放 redo log + 恢复脏页 | 进程重启极快（数据在磁盘，无重放；上万分区时例外，见第 3 章），但 PageCache 冷热影响读性能 |
| 165 | chapters/04-memory-disk/chapter.md:257 | seeref | 见 | | 崩溃恢复代价 | 加载 RDB / 重放 AOF（大实例数分钟） | 重放 redo log + 恢复脏页 | 进程重启极快（数据在磁盘，无重放；上万分区时例外，见第 3 章），但 PageCache 冷热影响读性能 |
| 166 | chapters/04-memory-disk/chapter.md:262 | ch | 第 8 章 | **持久化机制**。它们的持久化都是"日志 + 某种全量"的组合，但日志的形态不同。Redis 的 AOF 是命令日志，MySQL 的 redo log 是"物理到页、逻辑到操作"的混合日志（记到页号与物理偏移，页内记的 |
| 167 | chapters/04-memory-disk/chapter.md:262 | seeref | 见 | **持久化机制**。它们的持久化都是"日志 + 某种全量"的组合，但日志的形态不同。Redis 的 AOF 是命令日志，MySQL 的 redo log 是"物理到页、逻辑到操作"的混合日志（记到页号与物理偏移，页内记的 |
| 168 | chapters/04-memory-disk/chapter.md:268 | ch | 第 3 章 | **崩溃恢复代价**。Redis 大实例加载 RDB 或重放 AOF 可能要数分钟，这段时间实例不可用，是 Redis 高可用方案必须面对的冷启动问题。MySQL 重放 redo log 较快（redo log 设计上就 |
| 169 | chapters/04-memory-disk/chapter.md:268 | seeref | 见 | **崩溃恢复代价**。Redis 大实例加载 RDB 或重放 AOF 可能要数分钟，这段时间实例不可用，是 Redis 高可用方案必须面对的冷启动问题。MySQL 重放 redo log 较快（redo log 设计上就 |
| 170 | chapters/04-memory-disk/chapter.md:272 | tab | 表 4-3 | 三个选择的关键是匹配，匹配的依据就在表 4-3 里：数据量级、访问是否随机、能承受的崩溃恢复代价——哪一列对得上你的场景，就选哪一列。 |
| 171 | chapters/04-memory-disk/chapter.md:290 | sec | 4.2 节 | Redis 和 MySQL 选择自己管理内存，是因为内核的页面缓存策略无法满足它们在淘汰精度上的需求：Redis 要的是按键、可配策略的淘汰（近似 LRU 与 LFU，见 4.2 节），MySQL 要的是抗扫描污染的新老 |
| 172 | chapters/04-memory-disk/chapter.md:290 | seeref | 见 | Redis 和 MySQL 选择自己管理内存，是因为内核的页面缓存策略无法满足它们在淘汰精度上的需求：Redis 要的是按键、可配策略的淘汰（近似 LRU 与 LFU，见 4.2 节），MySQL 要的是抗扫描污染的新老 |
| 173 | chapters/04-memory-disk/chapter.md:294 | sec | 4.4 节 | 它们的每个刷盘参数，都是同一道选择题的不同档位——4.4 节已把 `acks` 三档和另外两家的刷盘参数对照过一次。Redis 的 `appendfsync`（always / everysec / no）、MySQL  |
| 174 | chapters/04-memory-disk/chapter.md:308 | ch | 第 10 章 | 下次评估一个新的存储系统，我会先看它的数据落在快慢介质的哪一层、缓存建在哪一级。第 10 章还会回到这条跨层的线索。 |
| 175 | chapters/04-memory-disk/chapter.md:320 | ch | 第 5 章 | 本章讨论了数据在内存和磁盘间的布局，下一章（第 5 章 分层架构）看软件本身怎么分层。 |
| 176 | chapters/05-layered-architecture/README.md:16 | ch | 第 4 章 | - 复核 Kafka 零拷贝与第 4 章的重复边界。 |
| 177 | chapters/05-layered-architecture/chapter.md:32 | sec | 5.6 节 | 分层的数量取决于性能目标和实际收益。镜像分层、空洞透传、循环依赖这些"看起来分层了、实际没换来价值"的情况，会在 5.6 节展开。带着"这层抽象值不值它的延迟"这个问题，我们先看 Redis 如何把分层做到最薄。 |
| 178 | chapters/05-layered-architecture/chapter.md:56 | fig | 图 5-1 | ![图 5-1 Redis 命令处理流水线](diagrams/fig-5-1.svg) |
| 179 | chapters/05-layered-architecture/chapter.md:57 | fig | 图 5-1 | 图 5-1　Redis 命令处理流水线：交互层与逻辑层用 client 结构体衔接，全程无序列化。 |
| 180 | chapters/05-layered-architecture/chapter.md:59 | sec | 5.3 节 | 图里右边那个贯穿全程的虚线框是 `client` 结构体。它持有查询缓冲区、参数数组、当前命令指针、当前 db 索引、输出缓冲区、用户与 ACL 标志。整个会话上下文都在这一个对象里。交互层往里写、逻辑层往外读、存储层从 |
| 181 | chapters/05-layered-architecture/chapter.md:63 | sec | 2.2.1 节 | 命令的统一抽象靠 `redisObject`（业内简称 robj）完成。robj 是 Redis 统一表示所有数据类型的关键。它的设计核心是把**类型（type）与编码（encoding）分离**。type 决定语义：这 |
| 182 | chapters/05-layered-architecture/chapter.md:65 | fig | 图 5-2 | ![图 5-2 redisObject 的 type/encoding 解耦](diagrams/fig-5-2.svg) |
| 183 | chapters/05-layered-architecture/chapter.md:66 | fig | 图 5-2 | 图 5-2　redisObject 的 type / encoding 解耦：逻辑层只看 type（语义），存储层只看 encoding（内存表示）。 |
| 184 | chapters/05-layered-architecture/chapter.md:98 | fig | 图 5-3 | ![图 5-3 THD 贯穿 MySQL 三层的会话上下文](diagrams/fig-5-3.svg) |
| 185 | chapters/05-layered-architecture/chapter.md:99 | fig | 图 5-3 | 图 5-3　THD 贯穿 MySQL 三层的会话上下文：THD 是跨层共享的可变状态。 |
| 186 | chapters/05-layered-architecture/chapter.md:113 | sec | 5.6 节 | **查询缓存（Query Cache）** 是分层失败的一个案例。MySQL 5.x 时代有个功能：把 SELECT 的结果按 SQL 文本做 key 缓存，下次同样的 SQL 直接返回。设计意图是好的，但它在 8.0  |
| 187 | chapters/05-layered-architecture/chapter.md:123 | fig | 图 5-4 | ![图 5-4 MySQL Handler API 与可插拔存储引擎](diagrams/fig-5-4.svg) |
| 188 | chapters/05-layered-architecture/chapter.md:124 | fig | 图 5-4 | 图 5-4　MySQL Handler API 与可插拔存储引擎：服务层通过 handler 虚函数向下调用，引擎可并存、可替换。 |
| 189 | chapters/05-layered-architecture/chapter.md:126 | sec | 8.3.2 节 | 这张图的关键在中间那条粗黄线：Handler API 接口契约，它把服务层与引擎层彻底切开。下面的引擎们各自实现这套接口，互不干扰，可并存。InnoDB 自己又是多层：事务管理 → 锁与 MVCC → 缓冲池（Buffe |
| 190 | chapters/05-layered-architecture/chapter.md:126 | sec | 8.3.4 节 | 这张图的关键在中间那条粗黄线：Handler API 接口契约，它把服务层与引擎层彻底切开。下面的引擎们各自实现这套接口，互不干扰，可并存。InnoDB 自己又是多层：事务管理 → 锁与 MVCC → 缓冲池（Buffe |
| 191 | chapters/05-layered-architecture/chapter.md:126 | seeref | 见 | 这张图的关键在中间那条粗黄线：Handler API 接口契约，它把服务层与引擎层彻底切开。下面的引擎们各自实现这套接口，互不干扰，可并存。InnoDB 自己又是多层：事务管理 → 锁与 MVCC → 缓冲池（Buffe |
| 192 | chapters/05-layered-architecture/chapter.md:126 | seeref | 见 | 这张图的关键在中间那条粗黄线：Handler API 接口契约，它把服务层与引擎层彻底切开。下面的引擎们各自实现这套接口，互不干扰，可并存。InnoDB 自己又是多层：事务管理 → 锁与 MVCC → 缓冲池（Buffe |
| 193 | chapters/05-layered-architecture/chapter.md:126 | seeref | 见 | 这张图的关键在中间那条粗黄线：Handler API 接口契约，它把服务层与引擎层彻底切开。下面的引擎们各自实现这套接口，互不干扰，可并存。InnoDB 自己又是多层：事务管理 → 锁与 MVCC → 缓冲池（Buffe |
| 194 | chapters/05-layered-architecture/chapter.md:140 | fig | 图 3-5 | Kafka 的网络层是三者里最"重"的。它受 Netty 的 Reactor 模式启发，但用 Scala 实现，分成四级：Acceptor、Processor、RequestChannel、KafkaRequestHan |
| 195 | chapters/05-layered-architecture/chapter.md:140 | ch | 第 3 章 | Kafka 的网络层是三者里最"重"的。它受 Netty 的 Reactor 模式启发，但用 Scala 实现，分成四级：Acceptor、Processor、RequestChannel、KafkaRequestHan |
| 196 | chapters/05-layered-architecture/chapter.md:140 | ch | 第 3 章 | Kafka 的网络层是三者里最"重"的。它受 Netty 的 Reactor 模式启发，但用 Scala 实现，分成四级：Acceptor、Processor、RequestChannel、KafkaRequestHan |
| 197 | chapters/05-layered-architecture/chapter.md:150 | fig | 图 5-5 | ![图 5-5 Kafka Reactor + RequestChannel 线程模型](diagrams/fig-5-5.svg) |
| 198 | chapters/05-layered-architecture/chapter.md:151 | fig | 图 5-5 | 图 5-5　Kafka Reactor + RequestChannel 线程模型：网络线程与业务线程通过有界队列解耦，队列满时天然背压上游。 |
| 199 | chapters/05-layered-architecture/chapter.md:167 | ch | 第 8 章 | 存储层是 Kafka 最具特色的一层。它的核心抽象是 **`Log`**，一个非常具体的对象，指一组顺序追加的日志段（LogSegment），不是泛指的"日志"。每个分区对应一个 Log，每个 Log 由多个 LogSe |
| 200 | chapters/05-layered-architecture/chapter.md:177 | ch | 第 9 章 | 副本同步（Follower 从 Leader 拉日志）的机制详见第 9 章，这里只看它在分层上的一个副作用。下面这张时序图展示了 Kafka 的一个标志性设计：**消费者读路径和副本同步路径是同一条**。 |
| 201 | chapters/05-layered-architecture/chapter.md:177 | seeref | 详见 | 副本同步（Follower 从 Leader 拉日志）的机制详见第 9 章，这里只看它在分层上的一个副作用。下面这张时序图展示了 Kafka 的一个标志性设计：**消费者读路径和副本同步路径是同一条**。 |
| 202 | chapters/05-layered-architecture/chapter.md:179 | fig | 图 5-6 | ![图 5-6 Kafka Log 复用：消费读路径 = 副本同步路径](diagrams/fig-5-6.svg) |
| 203 | chapters/05-layered-architecture/chapter.md:180 | fig | 图 5-6 | 图 5-6　Kafka Log 复用：消费读路径 = 副本同步路径，存储层与复制层共享一份代码。 |
| 204 | chapters/05-layered-architecture/chapter.md:184 | ch | 第 9 章 | **存储层和复制层共享同一份代码**。Kafka 不需要为副本同步单独写一套读路径、单独维护一套状态机。复用消费读路径意味着任何对读路径的优化（零拷贝、索引、缓存）都同时惠及复制。任何 bug 修复只改一处。对比一下：很 |
| 205 | chapters/05-layered-architecture/chapter.md:186 | sec | 8.4.6 节 | **Kafka 把存储做得极薄（就是追加写日志），索引、复制、压实的复杂度都在上层解决**。代价是存储层几乎不可插拔。你不能换 Kafka 的"日志引擎"，因为整个系统对"Log 是顺序追加、按偏移量寻址"的假设贯穿各层 |
| 206 | chapters/05-layered-architecture/chapter.md:186 | ch | 第 8 章 | **Kafka 把存储做得极薄（就是追加写日志），索引、复制、压实的复杂度都在上层解决**。代价是存储层几乎不可插拔。你不能换 Kafka 的"日志引擎"，因为整个系统对"Log 是顺序追加、按偏移量寻址"的假设贯穿各层 |
| 207 | chapters/05-layered-architecture/chapter.md:186 | seeref | 详见 | **Kafka 把存储做得极薄（就是追加写日志），索引、复制、压实的复杂度都在上层解决**。代价是存储层几乎不可插拔。你不能换 Kafka 的"日志引擎"，因为整个系统对"Log 是顺序追加、按偏移量寻址"的假设贯穿各层 |
| 208 | chapters/05-layered-architecture/chapter.md:190 | ch | 第 7 章 | Kafka 还有一个 Redis 和 MySQL 都没有的层：**协调层**。它包括 ReplicaManager（副本管理）、Partition（分区对象）、Controller（集群控制器），以及 KRaft（取代  |
| 209 | chapters/05-layered-architecture/chapter.md:210 | fig | 图 5-7 | ![图 5-7 三层统一视角对照](diagrams/fig-5-7.svg) |
| 210 | chapters/05-layered-architecture/chapter.md:211 | fig | 图 5-7 | 图 5-7　三个软件映射到"交互 / 逻辑 / 存储"统一视角：同样的三段职责，落进各自的层形态。 |
| 211 | chapters/05-layered-architecture/chapter.md:217 | tab | 表 5-1 | **表 5-1　三个软件分层形态横向对比** |
| 212 | chapters/05-layered-architecture/chapter.md:258 | sec | 5.5 节 | 判断标准还是 5.5 节那一条。存在多样性就做接口（如 MySQL 的引擎），不存在就硬编码（如 Redis 的内存、Kafka 的日志）。最糟糕的做法是为了"显得架构高级"而强行做可插拔，你得到的是一个没人用的扩展点， |
| 213 | chapters/05-layered-architecture/chapter.md:272 | seeref | 见 | 我评审分层方案时必问一句：这一层挡住了什么变化？答不上来的层，就是我下一步要删的层；为"将来可能需要"预留的扩展点，我至今没见几个真用上的。 |
| 214 | chapters/05-layered-architecture/chapter.md:276 | sec | 5.3 节 | 分层应随系统演化持续审视和剪裁。5.3 节讲的查询缓存就是例子，8.0 就把它移除了。 |
| 215 | chapters/05-layered-architecture/chapter.md:294 | ch | 第 6 章 | 本章把边界画清楚了，下一章（第 6 章 安全机制）就看这些边界怎么守住。认证、授权、加密、审计四个层面各管一段，分出来的每一层都对应其中一组安全关注点。再往后，第 7 章集群架构会展开 Kafka 的协调层、Redis  |
| 216 | chapters/05-layered-architecture/chapter.md:294 | ch | 第 7 章 | 本章把边界画清楚了，下一章（第 6 章 安全机制）就看这些边界怎么守住。认证、授权、加密、审计四个层面各管一段，分出来的每一层都对应其中一组安全关注点。再往后，第 7 章集群架构会展开 Kafka 的协调层、Redis  |
| 217 | chapters/06-security/chapter.md:17 | fig | 图 6-1 | 图 6-1 把四维模型落在一次请求链路上，展示了各自的分工。 |
| 218 | chapters/06-security/chapter.md:19 | fig | 图 6-1 | ![图 6-1 一次请求链路上的安全四维分工](diagrams/fig-6-1.svg) |
| 219 | chapters/06-security/chapter.md:20 | fig | 图 6-1 | 图 6-1　从客户端发起请求到数据落盘，认证、授权、加密、审计各覆盖链路中的一段。 |
| 220 | chapters/06-security/chapter.md:26 | sec | 6.6 节 | 这三个软件因先天约束差异，走出了不同的安全路线。Redis 的内核追求极简和单核十万级 QPS（小包 GET/SET 场景），因为长期假设部署在内网，安全特性一直往后排。MySQL 面向企业市场，权限模型从第一天就追求列 |
| 221 | chapters/06-security/chapter.md:36 | seeref | 见 | 6.0 之前的 Redis 只有一个 `requirepass` 全局密码，所有客户端共享，无法区分身份。这是"安全让位给极简内核"的取舍：内核不知道调用者是谁，只校验一个共享口令。这种模型在内网可信环境里够用，但一旦  |
| 222 | chapters/06-security/chapter.md:60 | ch | 第 5 章 | 可插拔是更深的设计。认证逻辑与协议解耦，认证变成一个可替换的插件：`auth_socket` 让本机进程免密登录、`authentication_pam` 对接企业 PAM、`authentication_ldap_si |
| 223 | chapters/06-security/chapter.md:72 | sec | 6.7 节 | 委托令牌（Delegation Token）是 Kafka 处理"身份在跳之间频繁传递"的另一招。长期凭证（SCRAM 密码、Kerberos 票据）在客户端和 Broker 之间反复传会有泄露风险，委托令牌是短期有效的 |
| 224 | chapters/06-security/chapter.md:74 | fig | 图 6-2 | 监听器分层是 Kafka 区别于单机系统的能力。同一个 Broker 进程可以同时开多个监听器：内部走 `SASL_SSL`（强制认证加加密），对外一律走 `SASL_SSL`（外部网络最不可信，认证不能省）；受信内网若 |
| 225 | chapters/06-security/chapter.md:74 | seeref | 见 | 监听器分层是 Kafka 区别于单机系统的能力。同一个 Broker 进程可以同时开多个监听器：内部走 `SASL_SSL`（强制认证加加密），对外一律走 `SASL_SSL`（外部网络最不可信，认证不能省）；受信内网若 |
| 226 | chapters/06-security/chapter.md:76 | fig | 图 6-2 | ![图 6-2 Kafka 同一 Broker 的监听器分层](diagrams/fig-6-2.svg) |
| 227 | chapters/06-security/chapter.md:77 | fig | 图 6-2 | 图 6-2　内部 SASL_SSL、外部 SASL_SSL、控制面 KRaft 三条路径并行，按网络域分级信任。 |
| 228 | chapters/06-security/chapter.md:79 | seeref | 见 | 这套分层的代价是配置矩阵成倍增长：每个监听器都要独立配协议、端口、证书与 `advertised.listeners`，配置项随监听器数乘 Broker 数增长。生产环境最常见的故障也出在这里——客户端从 bootstr |
| 229 | chapters/06-security/chapter.md:89 | seeref | 见 | 命令类别是关键抽象。Redis 把上百条命令归成二十来个类别：既有 `@read`、`@write`、`@admin`、`@dangerous` 这类语义组，也有 `@fast`、`@slow` 这类性能分桶。运维一眼就 |
| 230 | chapters/06-security/chapter.md:91 | fig | 图 6-3 | 图 6-3 展示了一次完整连接里 Redis ACL 的工作流程。 |
| 231 | chapters/06-security/chapter.md:93 | fig | 图 6-3 | ![图 6-3 Redis ACL 连接的认证 + 每命令授权检查时序](diagrams/fig-6-3.svg) |
| 232 | chapters/06-security/chapter.md:94 | fig | 图 6-3 | 图 6-3　会话级认证一次，每条命令都走"命令类别加键模式"二维授权检查。 |
| 233 | chapters/06-security/chapter.md:108 | fig | 图 6-4 | 图 6-4 展示了这条逐层收窄的检查流程。 |
| 234 | chapters/06-security/chapter.md:110 | fig | 图 6-4 | ![图 6-4 MySQL 五级权限表的层级收窄检查流程](diagrams/fig-6-4.svg) |
| 235 | chapters/06-security/chapter.md:111 | fig | 图 6-4 | 图 6-4　授权检查从全局到列逐层收窄，命中即停；细粒度优先于粗粒度。 |
| 236 | chapters/06-security/chapter.md:143 | seeref | 见 | 存储加密让 MySQL 区别于另外两款。TDE（Transparent Data Encryption，透明数据加密）在 InnoDB 表空间级别加密数据，密钥由密钥管理插件托管，常见的是对接 HashiCorp Vau |
| 237 | chapters/06-security/chapter.md:167 | tab | 表 6-1 | 表 6-1 按认证、授权、加密、审计四维对比三家的安全选择，重点看"为什么分叉"。 |
| 238 | chapters/06-security/chapter.md:169 | tab | 表 6-1 | **表 6-1　安全机制四维横向对比** |
| 239 | chapters/06-security/chapter.md:217 | seeref | 见 | 它们都支持并推荐最小权限：每个应用独立账号、只授必要命令或操作、限定键或表或主题范围、定期审查。实现手段各不相同：Redis 用键模式隔离、MySQL 用角色加列权限、Kafka 用前缀授权，但原则一致。反模式也一致：用 |
| 240 | chapters/07-cluster/README.md:5 | ch | 第 7 章 | 本章讨论系统从单点走向分布式时必须面对的拓扑、分片、副本、故障检测与选主问题。第 7 章讲集群形态，第 9 章再深入数据如何在节点间同步。 |
| 241 | chapters/07-cluster/README.md:5 | ch | 第 9 章 | 本章讨论系统从单点走向分布式时必须面对的拓扑、分片、副本、故障检测与选主问题。第 7 章讲集群形态，第 9 章再深入数据如何在节点间同步。 |
| 242 | chapters/07-cluster/README.md:15 | ch | 第 9 章 | - 本章篇幅偏长，压缩时保持与第 9 章的分工清楚。 |
| 243 | chapters/07-cluster/chapter.md:8 | ch | 第 9 章 | 三个答案按一致性强度从弱到强排开。集群的拓扑与容错归本章，复制的字节级细节归第 9 章。 |
| 244 | chapters/07-cluster/chapter.md:38 | seeref | 见 | 这四个难题之上，还有一条更根本的约束：**CAP 定理**。网络分区（Partition）是分布式绕不开的现实，于是一致性（Consistency）与可用性（Availability）必须取舍。P 是给定的，C 和 A  |
| 245 | chapters/07-cluster/chapter.md:48 | fig | 图 7-1 | 这三个软件各自走了一条不同的路。图 7-1 把它们的演进主线并列出来，便于先建立一个总体印象。 |
| 246 | chapters/07-cluster/chapter.md:50 | fig | 图 7-1 | ![图 7-1 单点到集群的演进路径](diagrams/fig-7-1.svg) |
| 247 | chapters/07-cluster/chapter.md:51 | fig | 图 7-1 | 图 7-1　三个软件从单点到集群的演进主线并列：Redis 走主从→Sentinel→Cluster，MySQL 走异步→半同步→MGR，Kafka 走 Partition→Replica→KRaft。 |
| 248 | chapters/07-cluster/chapter.md:59 | ch | 第 9 章 | Redis 最朴素的集群化，是主从复制（replication）。在从节点上执行 `REPLICAOF host port`（旧版叫 `SLAVEOF`），从节点发起连接，建立后由主节点把数据推送过来：第一次连接时做全量 |
| 249 | chapters/07-cluster/chapter.md:79 | fig | 图 7-2 | **分片用 16384 个槽（slot）。** Redis Cluster 不直接把 key 映射到节点，而是先映射到 0–16383 这 16384 个槽，再把槽分配给节点。映射公式是 `CRC16(key) mod  |
| 250 | chapters/07-cluster/chapter.md:81 | fig | 图 7-2 | ![图 7-2 Redis Cluster 16384 槽分布与 MOVED/ASK 路由](diagrams/fig-7-2.svg) |
| 251 | chapters/07-cluster/chapter.md:82 | fig | 图 7-2 | 图 7-2　Redis Cluster 16384 槽分布与 MOVED/ASK 路由：槽是 key 到节点的中间抽象，加节点只迁移部分槽。 |
| 252 | chapters/07-cluster/chapter.md:102 | fig | 图 7-3 | ![图 7-3 MySQL 主从复制基础拓扑](diagrams/fig-7-3.svg) |
| 253 | chapters/07-cluster/chapter.md:103 | fig | 图 7-3 | 图 7-3　MySQL 主从复制基础拓扑：主节点写 binlog，从节点 I/O 线程拉到 relay log，SQL 线程回放。 |
| 254 | chapters/07-cluster/chapter.md:109 | ch | 第 9 章 | MySQL 复制的基础是 binlog，链路就是 7.3 开头那条"主写 binlog → I/O 线程拉到中继日志 → SQL 线程回放"。复制是单向的（只能主到从）、异步的（主写完 binlog 立即返回，不等从节点 |
| 255 | chapters/07-cluster/chapter.md:113 | seeref | 见 | 异步复制的代价：主节点不等从节点，主节点宕机时，那些已经提交、但还没来得及发到从节点的事务就丢了。从延迟方面看也有问题：单 SQL 线程回放意味着从节点只能串行重做主节点的所有写，主节点写并发一高，从节点跟不上，复制延迟 |
| 256 | chapters/07-cluster/chapter.md:119 | ch | 第 9 章 | 半同步的精确提交流程（`AFTER_SYNC` vs `AFTER_COMMIT`）、超时降级语义，以及它为何仍然不能保证零丢失，这些细节详见第 9 章半同步复制一节。 |
| 257 | chapters/07-cluster/chapter.md:119 | seeref | 详见 | 半同步的精确提交流程（`AFTER_SYNC` vs `AFTER_COMMIT`）、超时降级语义，以及它为何仍然不能保证零丢失，这些细节详见第 9 章半同步复制一节。 |
| 258 | chapters/07-cluster/chapter.md:147 | fig | 图 7-4 | 图 7-4 把这种分区加副本的拓扑画了出来。 |
| 259 | chapters/07-cluster/chapter.md:149 | fig | 图 7-4 | ![图 7-4 Kafka 分区与副本拓扑](diagrams/fig-7-4.svg) |
| 260 | chapters/07-cluster/chapter.md:150 | fig | 图 7-4 | 图 7-4　Kafka 分区与副本拓扑：Partition 是并行单位，每个分区一个 Leader 加若干 Follower，Leader 分散在各 Broker。 |
| 261 | chapters/07-cluster/chapter.md:168 | sec | 7.3.3 节 | ISR 定义了 Kafka 副本同步的边界。它比 MGR 的多数派确认松：MGR 每笔事务都要拿到组内过半成员的 Paxos 确认（7.3.3 节），写延迟里固定含一次跨节点共识往返，组规模也被共识开销限制在 9 个成员 |
| 262 | chapters/07-cluster/chapter.md:168 | ch | 第 9 章 | ISR 定义了 Kafka 副本同步的边界。它比 MGR 的多数派确认松：MGR 每笔事务都要拿到组内过半成员的 Paxos 确认（7.3.3 节），写延迟里固定含一次跨节点共识往返，组规模也被共识开销限制在 9 个成员 |
| 263 | chapters/07-cluster/chapter.md:168 | seeref | 见 | ISR 定义了 Kafka 副本同步的边界。它比 MGR 的多数派确认松：MGR 每笔事务都要拿到组内过半成员的 Paxos 确认（7.3.3 节），写延迟里固定含一次跨节点共识往返，组规模也被共识开销限制在 9 个成员 |
| 264 | chapters/07-cluster/chapter.md:168 | seeref | 见 | ISR 定义了 Kafka 副本同步的边界。它比 MGR 的多数派确认松：MGR 每笔事务都要拿到组内过半成员的 Paxos 确认（7.3.3 节），写延迟里固定含一次跨节点共识往返，组规模也被共识开销限制在 9 个成员 |
| 265 | chapters/07-cluster/chapter.md:168 | seeref | 见 | ISR 定义了 Kafka 副本同步的边界。它比 MGR 的多数派确认松：MGR 每笔事务都要拿到组内过半成员的 Paxos 确认（7.3.3 节），写延迟里固定含一次跨节点共识往返，组规模也被共识开销限制在 9 个成员 |
| 266 | chapters/07-cluster/chapter.md:174 | ch | 第 9 章 | `acks` 让使用者自己选择一致性强度。这是 Kafka 与 Redis、MySQL 在设计上的关键区别：前两者把取舍写死在默认值里，Kafka 把它做成可配置参数。代价是延迟：`acks` 越严，每条消息要等的副本确 |
| 267 | chapters/07-cluster/chapter.md:174 | seeref | 见 | `acks` 让使用者自己选择一致性强度。这是 Kafka 与 Redis、MySQL 在设计上的关键区别：前两者把取舍写死在默认值里，Kafka 把它做成可配置参数。代价是延迟：`acks` 越严，每条消息要等的副本确 |
| 268 | chapters/07-cluster/chapter.md:190 | tab | 表 7-1 | 表 7-1 从六个维度对比三个集群方案：数据分片策略、副本一致性模型、故障检测与 Leader 选举、元数据管理、CAP 立场、横向扩展能力。 |
| 269 | chapters/07-cluster/chapter.md:192 | tab | 表 7-1 | **表 7-1　三个集群方案横向对比总表（维度作为行，三个软件作为列）** |
| 270 | chapters/07-cluster/chapter.md:200 | seeref | 详见 | | CAP 立场 | 偏 AP（异步复制可丢写，但分区时少数派停止写入偏 CP；社区有 AP/CP 之争，详见 7.2.3） | 偏 CP（产品定位；少数派分区停服，详见正文） | 3.x 默认偏安全（acks=all） |
| 271 | chapters/07-cluster/chapter.md:200 | seeref | 详见 | | CAP 立场 | 偏 AP（异步复制可丢写，但分区时少数派停止写入偏 CP；社区有 AP/CP 之争，详见 7.2.3） | 偏 CP（产品定位；少数派分区停服，详见正文） | 3.x 默认偏安全（acks=all） |
| 272 | chapters/07-cluster/chapter.md:207 | fig | 图 7-5 | **故障检测与 Leader 选举，三个软件各有侧重。** Redis 用 Gossip 让所有节点去中心化地传播和投票，无单点但收敛慢。MySQL 与 Kafka 则走集中仲裁的路：MySQL 用 XCom 在组内跑  |
| 273 | chapters/07-cluster/chapter.md:209 | fig | 图 7-5 | ![图 7-5 三个软件故障转移决策流程对比](diagrams/fig-7-5.svg) |
| 274 | chapters/07-cluster/chapter.md:210 | fig | 图 7-5 | 图 7-5　同一个"谁来当新主"的问题，三个软件走出三条路：Redis 去中心化 Gossip+epoch 投票、MySQL XCom/Paxos View Change、Kafka 活跃 Controller 从 IS |
| 275 | chapters/07-cluster/chapter.md:212 | fig | 图 7-5 | 图 7-5 里的三处红色箭头，标记了"为保一致性而放弃可用性"的取舍点：Redis 在凑不齐多数派主节点票时让对应槽短暂不可用、MySQL 在少数派分区里直接停服、Kafka 在 ISR 为空时（默认）优先等待 ISR  |
| 276 | chapters/07-cluster/chapter.md:228 | ch | 第 4 章 | Redis 异步复制快但可丢，延迟低、一致性弱；MGR 多数派确认不丢，但每次写都要跨节点 Paxos 往返，一致性强、延迟高；Kafka 的 ISR 大小在两端之间可调。我自己设计系统时，会先想清楚业务对一致性的真实需 |
| 277 | chapters/07-cluster/chapter.md:246 | sec | 7.2.3 节 | 单点是故障的根源，分布式是解决方案，但它也带来新的复杂度。集群要同时解决数据怎么切、副本怎么一致、故障怎么转移、元数据谁说了算这四个问题，三个软件各给出了一套不同的方案：Redis Cluster 用去中心化 Gossi |
| 278 | chapters/07-cluster/chapter.md:248 | ch | 第 8 章 | 集群建起来了，这些机制最终要落到磁盘上的存储格式（日志段、RDB/AOF），那是第 8 章的内容；节点之间的数据如何精确同步、字节级的复制流怎么走，则是第 9 章的主题。而 Router、Controller 这类协调层 |
| 279 | chapters/07-cluster/chapter.md:248 | ch | 第 9 章 | 集群建起来了，这些机制最终要落到磁盘上的存储格式（日志段、RDB/AOF），那是第 8 章的内容；节点之间的数据如何精确同步、字节级的复制流怎么走，则是第 9 章的主题。而 Router、Controller 这类协调层 |
| 280 | chapters/07-cluster/chapter.md:248 | ch | 第 5 章 | 集群建起来了，这些机制最终要落到磁盘上的存储格式（日志段、RDB/AOF），那是第 8 章的内容；节点之间的数据如何精确同步、字节级的复制流怎么走，则是第 9 章的主题。而 Router、Controller 这类协调层 |
| 281 | chapters/08-storage-format/chapter.md:17 | ch | 第 5 章 | 更准确的说法是把存储格式当成一份契约：它把"内存里可变的数据结构"序列化成"磁盘上固定的、自描述的字节序列"。这份契约一旦发布就无法更改：明天发布的格式要能读懂今天写的文件，后天升级的代码要能读懂前天写的文件，向前向后兼 |
| 282 | chapters/08-storage-format/chapter.md:37 | fig | 图 8-1 | ![图 8-1　三个软件数据真正存放在哪里](diagrams/fig-8-1.svg) |
| 283 | chapters/08-storage-format/chapter.md:38 | fig | 图 8-1 | 图 8-1　三个软件"数据真正存放在哪里"的内存/磁盘权重示意。 |
| 284 | chapters/08-storage-format/chapter.md:50 | ch | 第 3 章 | > **本书为什么没讲 LSM 树**：日志结构合并树（LSM-tree）是现代存储系统的另一个重要范式，RocksDB、LevelDB、HBase、TiDB 都在用它。它通过"内存写入 + 分层 SST 文件（Sort |
| 285 | chapters/08-storage-format/chapter.md:66 | fig | 图 8-2 | 存储态编码与内存态编码是分离的。内存里 Hash 可能用 listpack 编码，也可能用 hashtable 编码，存盘时不照搬内存布局，改用统一的紧凑二进制序列化；加载后由加载器按当前阈值重新决定编码。这种分离让磁盘 |
| 286 | chapters/08-storage-format/chapter.md:68 | fig | 图 8-2 | ![图 8-2　RDB 文件布局](diagrams/fig-8-2.svg) |
| 287 | chapters/08-storage-format/chapter.md:69 | fig | 图 8-2 | 图 8-2　RDB 文件布局：magic / version / metadata / db-selector / entries / CRC64 footer。 |
| 288 | chapters/08-storage-format/chapter.md:75 | sec | 2.2.1 节 | 还有一处体现"格式为演进服务"的细节：7.0 起用 listpack 取代了旧版的 ziplist。ziplist 的历史包袱是 2.2.1 节讲过的连锁更新：每个元素记前一个元素的长度，长度字段一旦扩张就逐级传导，最坏 |
| 289 | chapters/08-storage-format/chapter.md:79 | sec | 9.2 节 | AOF（仅追加文件）走的是另一条路。它记录的是"写命令本身"：文件内容就是 RESP 协议文本。AOF 落的不是客户端发来的原文，而是命令执行完后、经与复制链路同一套规则改写的传播命令（`EXPIRE` 记成绝对时间的  |
| 290 | chapters/08-storage-format/chapter.md:79 | seeref | 见 | AOF（仅追加文件）走的是另一条路。它记录的是"写命令本身"：文件内容就是 RESP 协议文本。AOF 落的不是客户端发来的原文，而是命令执行完后、经与复制链路同一套规则改写的传播命令（`EXPIRE` 记成绝对时间的  |
| 291 | chapters/08-storage-format/chapter.md:87 | seeref | 见 | 但 fork 那一刻之后，父进程还在处理新写命令，这些命令既不能丢也不能让重写卡住。7.0 之前，Redis 的解法是双缓冲：重写期间的新写命令进 aof_rewrite_buffer，重写完成的子进程产出新文件后，父进 |
| 292 | chapters/08-storage-format/chapter.md:97 | fig | 图 8-3 | ![图 8-3　AOF 重写与混合持久化双缓冲](diagrams/fig-8-3.svg) |
| 293 | chapters/08-storage-format/chapter.md:98 | fig | 图 8-3 | 图 8-3　AOF 重写 + 混合持久化的双缓冲协作时序（7.0 之前的单文件机制；7.0 起为 manifest 原子切换，见上文）。 |
| 294 | chapters/08-storage-format/chapter.md:98 | seeref | 见 | 图 8-3　AOF 重写 + 混合持久化的双缓冲协作时序（7.0 之前的单文件机制；7.0 起为 manifest 原子切换，见上文）。 |
| 295 | chapters/08-storage-format/chapter.md:136 | fig | 图 8-4 | ![图 8-4　InnoDB 16KB 数据页内七段布局](diagrams/fig-8-4.svg) |
| 296 | chapters/08-storage-format/chapter.md:137 | fig | 图 8-4 | 图 8-4　InnoDB 16KB 数据页内部七段布局。 |
| 297 | chapters/08-storage-format/chapter.md:151 | fig | 图 8-5 | ![图 8-5　脏页刷盘与崩溃恢复路径](diagrams/fig-8-5.svg) |
| 298 | chapters/08-storage-format/chapter.md:152 | fig | 图 8-5 | 图 8-5　脏页刷盘流程：双写缓冲 → 正式页，配合 redo log 的崩溃恢复路径。 |
| 299 | chapters/08-storage-format/chapter.md:154 | seeref | 见 | 图中可见完整的双重保护机制：正常写路径上 redo log 先落盘（WAL），脏页先写双写缓冲再写正式位置；崩溃恢复路径上先扫描 redo log，对每条记录检查目标页 LSN，页未损坏且 LSN 落后则重做，页损坏则从 |
| 300 | chapters/08-storage-format/chapter.md:170 | fig | 图 8-6 | ![图 8-6　Kafka 分区到日志段的三个文件](diagrams/fig-8-6.svg) |
| 301 | chapters/08-storage-format/chapter.md:171 | fig | 图 8-6 | 图 8-6　分区 → 日志段 → 三个文件的目录与内部结构。 |
| 302 | chapters/08-storage-format/chapter.md:173 | sec | 8.4.4 节 | 一个分区在磁盘目录里展开成一串日志段，三个文件靠同一个起始偏移量对齐：文件名是它，`.index` 与 `.timeindex` 条目里的偏移量字段存的也是相对它的差值。用相对量有直接的好处：段的大小由 `log.seg |
| 303 | chapters/08-storage-format/chapter.md:179 | tab | 表 2-1 | Kafka 消息格式的关键变化是 V2 引入的 RecordBatch（字段布局见 2.2.3 节表 2-1，这里看它为什么这样演进）。在 V0、V1 时代，最小存储单元是单条消息（Message），每条都自带一份完整元 |
| 304 | chapters/08-storage-format/chapter.md:179 | sec | 2.2.3 节 | Kafka 消息格式的关键变化是 V2 引入的 RecordBatch（字段布局见 2.2.3 节表 2-1，这里看它为什么这样演进）。在 V0、V1 时代，最小存储单元是单条消息（Message），每条都自带一份完整元 |
| 305 | chapters/08-storage-format/chapter.md:179 | seeref | 见 | Kafka 消息格式的关键变化是 V2 引入的 RecordBatch（字段布局见 2.2.3 节表 2-1，这里看它为什么这样演进）。在 V0、V1 时代，最小存储单元是单条消息（Message），每条都自带一份完整元 |
| 306 | chapters/08-storage-format/chapter.md:187 | sec | 9.4 节 | 还有一处设计：ProducerId、ProducerEpoch、BaseSequence 直接进了存储格式本身。这三个字段是幂等生产与事务的根基（生产者带单调递增序列号发消息，Broker 据此把重试的重复去掉，见 9. |
| 307 | chapters/08-storage-format/chapter.md:187 | seeref | 见 | 还有一处设计：ProducerId、ProducerEpoch、BaseSequence 直接进了存储格式本身。这三个字段是幂等生产与事务的根基（生产者带单调递增序列号发消息，Broker 据此把重试的重复去掉，见 9. |
| 308 | chapters/08-storage-format/chapter.md:197 | sec | 8.3.3 节 | 不用稠密索引是因为它体积跟数据量等比例增长，放不进内存，虽然能让查找严格 O(log n)。稀疏索引牺牲一点点顺序扫描，换来索引体积小到能常驻内存：一个 TB 的主题索引可能只有几 GB，热部分全在页缓存里。Page D |
| 309 | chapters/08-storage-format/chapter.md:207 | tab | 表 8-1 | **表 8-1　Kafka 消息格式 V0 / V1 / V2 的字段对比与演进动机** |
| 310 | chapters/08-storage-format/chapter.md:225 | ch | 第 5 章 | 机制核心是 RemoteStorageManager：一个统一接口，定义日志段的上传、下载和删除。当一个日志段被关闭（达到大小或时间阈值）后，Kafka 异步把它上传到 S3、GCS 或 Azure Blob 等对象存储 |
| 311 | chapters/08-storage-format/chapter.md:227 | fig | 图 8-7 | 这一变化带来三方面影响。第一，"日志数据必须在本地磁盘"的假设需要修正：正本仍是日志段，但它的物理位置从"必须在本地"变成了"在本地或远程，格式一致"。第二，PageCache 假设被改写：冷数据不经过 PageCach |
| 312 | chapters/08-storage-format/chapter.md:229 | fig | 图 8-7 | ![图 8-7　Kafka Tiered Storage 日志段生命周期](diagrams/fig-8-7.svg) |
| 313 | chapters/08-storage-format/chapter.md:230 | fig | 图 8-7 | 图 8-7　Kafka Tiered Storage 日志段生命周期：本地热段关闭后异步上传到远程对象存储，消费者读取时先尝试本地、未命中则回源远程；Follower 的副本拉取始终由 Leader 本地日志服务。 |
| 314 | chapters/08-storage-format/chapter.md:232 | fig | 图 8-7 | 图 8-7 把生命周期拆成三步：追加写只发生在本地的活跃段，段关闭后才触发异步上传，远程那份是只读的冷段。读取路径分成两条，本地命中和远程回源的延迟差着一个量级，对应前文说的第二点影响。 |
| 315 | chapters/08-storage-format/chapter.md:240 | tab | 表 8-2 | **表 8-2　三个软件在八个维度上的范式对比** |
| 316 | chapters/08-storage-format/chapter.md:257 | ch | 第 4 章 | 三种格式背后是三种不同的优化目标。第 4 章按数据的主存储放在内存还是磁盘，把三家分成全内存、缓存磁盘、顺序日志三种范式；本节按磁盘文件本身的组织结构来分，快照、页式、追加日志是另一个维度。 |
| 317 | chapters/08-storage-format/chapter.md:263 | seeref | 见 | Kafka 的追加日志做法为"高吞吐的顺序写 + 成批压缩"优化。日志段只追加不改写，磁盘顺序写能用满带宽。RecordBatch 把一批消息当成一个存储单元，压缩在 Batch 边界做，同类消息上常见 2–6 倍压缩比 |
| 318 | chapters/08-storage-format/chapter.md:309 | ch | 第 2 章 | 最后一条回到 8.1.2 的第四个矛盾。存储格式发布即定型，业务会变、字段要加、编码要换、旧 bug 要修，全都要在原格式上做兼容。版本号、保留字段、Magic、编码切换，都是为未来预留的扩展空间（第 2 章启示四在协议 |
| 319 | chapters/08-storage-format/chapter.md:319 | fig | 图 8-8 | 第二问，访问是随机定位要快，还是批量流式进出？随机定位要快，走定长页加索引（B+ 树加页内稀疏槽）。批量流式进出且写远多于点查，走追加日志结构（像 Kafka，纯追加加稀疏索引）。既不原地改也不批量流式、只需要崩溃后整体 |
| 320 | chapters/08-storage-format/chapter.md:321 | fig | 图 8-8 | ![图 8-8　存储格式设计决策树](diagrams/fig-8-8.svg) |
| 321 | chapters/08-storage-format/chapter.md:322 | fig | 图 8-8 | 图 8-8　存储格式设计决策树：先判断会不会原地改，再区分随机定位与批量流式，分别落到页式、追加日志、快照三种范式。 |
| 322 | chapters/08-storage-format/chapter.md:332 | ch | 第 9 章 | 存储格式的选择会长期绑住一个系统：页式再调优也追不上追加日志的写吞吐，追加日志再优化也做不了原地事务。而设计一个格式时，第一个该问的问题是"五年后还能不能加字段、换编码"，省字节决定当下的快慢，可演进性决定这格式三五年后 |
| 323 | chapters/09-data-sync/README.md:5 | ch | 第 7 章 | 本章讨论多副本之间如何对齐状态机。它与第 7 章互为表里：第 7 章讲集群拓扑与选主，本章讲传播单元、位点、一致性强度和故障恢复。 |
| 324 | chapters/09-data-sync/README.md:5 | ch | 第 7 章 | 本章讨论多副本之间如何对齐状态机。它与第 7 章互为表里：第 7 章讲集群拓扑与选主，本章讲传播单元、位点、一致性强度和故障恢复。 |
| 325 | chapters/09-data-sync/README.md:15 | ch | 第 7 章 | - 本章篇幅偏长，压缩时优先删减与第 7 章重复的拓扑和选主背景。 |
| 326 | chapters/09-data-sync/chapter.md:7 | ch | 第 7 章 | 数据同步本质上就是一件事：把一处状态变化可靠地传给其他副本，而且延迟有上限。三个软件表面各做各的：Redis 传命令流、MySQL 传 binlog event、Kafka 传有序消息。底下是同一条主线：状态机复制。第  |
| 327 | chapters/09-data-sync/chapter.md:27 | fig | 图 9-1 | ![图 9-1 数据同步的四个子问题框架](diagrams/fig-9-1.svg) |
| 328 | chapters/09-data-sync/chapter.md:28 | fig | 图 9-1 | 图 9-1　数据同步的四个子问题：传播什么、怎么传播、到什么程度、断了怎么办。 |
| 329 | chapters/09-data-sync/chapter.md:30 | fig | 图 9-2 | 这四个子问题的底层，是同一个模型：**状态机复制**，所有副本按相同顺序执行相同输入序列，终态必然相同。DDIA（《Designing Data-Intensive Applications》）第 5 章对此已有展开。它 |
| 330 | chapters/09-data-sync/chapter.md:30 | ch | 第 5 章 | 这四个子问题的底层，是同一个模型：**状态机复制**，所有副本按相同顺序执行相同输入序列，终态必然相同。DDIA（《Designing Data-Intensive Applications》）第 5 章对此已有展开。它 |
| 331 | chapters/09-data-sync/chapter.md:30 | seeref | 见 | 这四个子问题的底层，是同一个模型：**状态机复制**，所有副本按相同顺序执行相同输入序列，终态必然相同。DDIA（《Designing Data-Intensive Applications》）第 5 章对此已有展开。它 |
| 332 | chapters/09-data-sync/chapter.md:32 | fig | 图 9-2 | ![图 9-2 状态机复制模型](diagrams/fig-9-2.svg) |
| 333 | chapters/09-data-sync/chapter.md:33 | fig | 图 9-2 | 图 9-2　状态机复制模型：顶部同一个输入序列分发到三个副本，对照三列逐步执行后的汇合结果。 |
| 334 | chapters/09-data-sync/chapter.md:35 | sec | 9.2 节 | 模型成立有一个前提：同一条输入在每个副本上必须产生相同的状态变化，执行必须是确定性的。带随机性或依赖本地时间的命令会让三列到不了同一个 S5——Redis 为此在复制链路上改写了哪些命令，见 9.2 节。 |
| 335 | chapters/09-data-sync/chapter.md:35 | seeref | 见 | 模型成立有一个前提：同一条输入在每个副本上必须产生相同的状态变化，执行必须是确定性的。带随机性或依赖本地时间的命令会让三列到不了同一个 S5——Redis 为此在复制链路上改写了哪些命令，见 9.2 节。 |
| 336 | chapters/09-data-sync/chapter.md:55 | ch | 第 8 章 | 这个做法呼应了第 8 章"AOF 持久化文件复用协议格式"的设计：AOF 持久化记录的就是同一种命令流。于是 Redis 把持久化和复制**复用同一种载体**：一份命令流既写给磁盘（AOF）也写给网络（副本），二者天然一 |
| 337 | chapters/09-data-sync/chapter.md:63 | sec | 7.2.3 节 | 这是默认偏 AP（高可用优先）的取向；分区时少数派停写则偏 CP（归类讨论见 7.2.3 节）。主节点的延迟几乎不受副本数量和副本健康度影响，而低延迟正是 Redis 作为缓存/在线存储最看重的特性。代价同样明确：主节点 |
| 338 | chapters/09-data-sync/chapter.md:63 | seeref | 见 | 这是默认偏 AP（高可用优先）的取向；分区时少数派停写则偏 CP（归类讨论见 7.2.3 节）。主节点的延迟几乎不受副本数量和副本健康度影响，而低延迟正是 Redis 作为缓存/在线存储最看重的特性。代价同样明确：主节点 |
| 339 | chapters/09-data-sync/chapter.md:76 | fig | 图 9-3 | 另一类代价在两处：`BGSAVE` 的 fork 在大实例上会有一瞬间的内存翻倍风险（写时复制）和短暂的停顿；RDB 文件在网络上的传输要消耗主节点的出口带宽。全量同步越频繁，这两项代价越痛，所以 Redis 才会重点设 |
| 340 | chapters/09-data-sync/chapter.md:76 | seeref | 见 | 另一类代价在两处：`BGSAVE` 的 fork 在大实例上会有一瞬间的内存翻倍风险（写时复制）和短暂的停顿；RDB 文件在网络上的传输要消耗主节点的出口带宽。全量同步越频繁，这两项代价越痛，所以 Redis 才会重点设 |
| 341 | chapters/09-data-sync/chapter.md:78 | fig | 图 9-3 | ![图 9-3 Redis PSYNC2 全量 + 部分重同步流程](diagrams/fig-9-3.svg) |
| 342 | chapters/09-data-sync/chapter.md:79 | fig | 图 9-3 | 图 9-3　PSYNC2 的核心是 offset 比对：断线后 offset 仍在 backlog 窗口内则部分重同步，否则退回全量。 |
| 343 | chapters/09-data-sync/chapter.md:94 | fig | 图 9-4 | backlog 窗口与主从 offset 的位置关系，见图 9-4。 |
| 344 | chapters/09-data-sync/chapter.md:94 | seeref | 见 | backlog 窗口与主从 offset 的位置关系，见图 9-4。 |
| 345 | chapters/09-data-sync/chapter.md:96 | fig | 图 9-4 | ![图 9-4 Redis 复制积压缓冲区与 replication offset](diagrams/fig-9-4.svg) |
| 346 | chapters/09-data-sync/chapter.md:97 | fig | 图 9-4 | 图 9-4　backlog 滑动窗口：主从各持一个字节位点，offset 在窗口内即可增量补差，否则全量。 |
| 347 | chapters/09-data-sync/chapter.md:99 | seeref | 见 | backlog 默认约 1MB，是"断线容忍窗口"与"内存占用"之间的折中。窗口越大，能容忍越长时间的断线（典型场景：副本做一次短暂的 GC 或网络抖动），但主节点要常驻更多内存。这是个按业务调的参数：大流量实例把它调到 |
| 348 | chapters/09-data-sync/chapter.md:99 | seeref | 见 | backlog 默认约 1MB，是"断线容忍窗口"与"内存占用"之间的折中。窗口越大，能容忍越长时间的断线（典型场景：副本做一次短暂的 GC 或网络抖动），但主节点要常驻更多内存。这是个按业务调的参数：大流量实例把它调到 |
| 349 | chapters/09-data-sync/chapter.md:115 | seeref | 见 | 副本也可以作为下一级副本的主，形成链式（tree）复制拓扑。常见动机是分担主节点的出口带宽：主只推给少数几个一级副本，一级副本再推给二级副本。 |
| 350 | chapters/09-data-sync/chapter.md:144 | fig | 图 9-5 | 主节点写 binlog、从节点 I/O 线程拉到 relay log、SQL 线程回放，这条链路见图 9-5。这里有一个微妙的设计点：把"网络"和"回放"解耦成两个线程，让网络拉取可以快（先行把事件拉到本地缓冲），回放可 |
| 351 | chapters/09-data-sync/chapter.md:144 | seeref | 见 | 主节点写 binlog、从节点 I/O 线程拉到 relay log、SQL 线程回放，这条链路见图 9-5。这里有一个微妙的设计点：把"网络"和"回放"解耦成两个线程，让网络拉取可以快（先行把事件拉到本地缓冲），回放可 |
| 352 | chapters/09-data-sync/chapter.md:146 | fig | 图 9-5 | ![图 9-5 MySQL 异步 / 半同步复制与 GTID 链路](diagrams/fig-9-5.svg) |
| 353 | chapters/09-data-sync/chapter.md:147 | fig | 图 9-5 | 图 9-5　异步 / 半同步 / GTID：异步复制主写完即返回，半同步增加 ACK 回路，GTID 把位点从文件偏移变成全局事务标识。 |
| 354 | chapters/09-data-sync/chapter.md:151 | ch | 第 7 章 | 默认配置下，MySQL 复制是异步的：主节点提交事务（写完 binlog 并落盘）就立刻给客户端返回 OK，不等任何副本。但这只是 MySQL 复制的默认形态，不是它的产品定位：MySQL 通过半同步和组复制把一致性一路 |
| 355 | chapters/09-data-sync/chapter.md:151 | seeref | 见 | 默认配置下，MySQL 复制是异步的：主节点提交事务（写完 binlog 并落盘）就立刻给客户端返回 OK，不等任何副本。但这只是 MySQL 复制的默认形态，不是它的产品定位：MySQL 通过半同步和组复制把一致性一路 |
| 356 | chapters/09-data-sync/chapter.md:155 | seeref | 见 | 半同步（semi-sync）是 MySQL 在异步和强一致之间的中间点：主节点等至少一个副本的 ACK（确认应答；副本 I/O 线程把事件写入 relay log 并落盘后即回 ACK，不等本地回放）才返回成功。它有两档 |
| 357 | chapters/09-data-sync/chapter.md:155 | seeref | 见 | 半同步（semi-sync）是 MySQL 在异步和强一致之间的中间点：主节点等至少一个副本的 ACK（确认应答；副本 I/O 线程把事件写入 relay log 并落盘后即回 ACK，不等本地回放）才返回成功。它有两档 |
| 358 | chapters/09-data-sync/chapter.md:159 | sec | 7.3.2 节 | 半同步仍不保证零丢失：它只确认"副本收到了"，不确认"副本已提交"，且超时降级后等同异步。第 7 章 7.3.2 节从集群拓扑角度也提到了它作为中间路线的定位。 |
| 359 | chapters/09-data-sync/chapter.md:159 | ch | 第 7 章 | 半同步仍不保证零丢失：它只确认"副本收到了"，不确认"副本已提交"，且超时降级后等同异步。第 7 章 7.3.2 节从集群拓扑角度也提到了它作为中间路线的定位。 |
| 360 | chapters/09-data-sync/chapter.md:179 | fig | 图 9-6 | 配合 `replica_parallel_workers`（8.0.26 前为 `slave_parallel_workers`）、`replica_parallel_type=LOGICAL_CLOCK` 等参数，复制 |
| 361 | chapters/09-data-sync/chapter.md:179 | seeref | 见 | 配合 `replica_parallel_workers`（8.0.26 前为 `slave_parallel_workers`）、`replica_parallel_type=LOGICAL_CLOCK` 等参数，复制 |
| 362 | chapters/09-data-sync/chapter.md:181 | fig | 图 9-6 | ![图 9-6 MySQL 多线程并行复制与组复制（MGR）共识](diagrams/fig-9-6.svg) |
| 363 | chapters/09-data-sync/chapter.md:182 | fig | 图 9-6 | 图 9-6　并行回放与 MGR：从节点按组提交边界并行回放，MGR 把 binlog event 当作共识 log entry，多数派确认才提交。 |
| 364 | chapters/09-data-sync/chapter.md:198 | sec | 9.2 节 | MySQL 在数据同步上的取舍是三档：从异步（可丢、最快）到半同步（多数情况下不丢、超时降级）到组复制（多数派强一致、最慢），业务方按场景选档。Redis 则只提供一个默认档，另给一个弱保证参数和一个按写生效的 `WAI |
| 365 | chapters/09-data-sync/chapter.md:198 | seeref | 见 | MySQL 在数据同步上的取舍是三档：从异步（可丢、最快）到半同步（多数情况下不丢、超时降级）到组复制（多数派强一致、最慢），业务方按场景选档。Redis 则只提供一个默认档，另给一个弱保证参数和一个按写生效的 `WAI |
| 366 | chapters/09-data-sync/chapter.md:208 | ch | 第 5 章 | 这一点和第 5 章 Kafka 存储层的 Log 抽象直接呼应：日志天然提供了全序关系，所以"状态机复制里的有序输入序列"在 Kafka 这里是现成的：日志本身就是序列。 |
| 367 | chapters/09-data-sync/chapter.md:214 | ch | 第 5 章 | **Follower 的 FETCH 请求和消费者的 FETCH 请求走的是同一条读路径**（对本地日志段成立，Tiered Storage 的例外见下段）。Leader 不区分对面是副本还是消费者，统一按"给我从偏移量 |
| 368 | chapters/09-data-sync/chapter.md:214 | seeref | 见 | **Follower 的 FETCH 请求和消费者的 FETCH 请求走的是同一条读路径**（对本地日志段成立，Tiered Storage 的例外见下段）。Leader 不区分对面是副本还是消费者，统一按"给我从偏移量 |
| 369 | chapters/09-data-sync/chapter.md:216 | sec | 8.4.6 节 | 拉模式的代价是 Follower 自己掌握追赶节奏，副本数量多时大量 FETCH 请求会集中在 Leader 上。Kafka 的应对是批量化（一次 FETCH 拉一大段日志）和页缓存（Leader 端日志常驻页缓存，FE |
| 370 | chapters/09-data-sync/chapter.md:216 | ch | 第 8 章 | 拉模式的代价是 Follower 自己掌握追赶节奏，副本数量多时大量 FETCH 请求会集中在 Leader 上。Kafka 的应对是批量化（一次 FETCH 拉一大段日志）和页缓存（Leader 端日志常驻页缓存，FE |
| 371 | chapters/09-data-sync/chapter.md:216 | seeref | 详见 | 拉模式的代价是 Follower 自己掌握追赶节奏，副本数量多时大量 FETCH 请求会集中在 Leader 上。Kafka 的应对是批量化（一次 FETCH 拉一大段日志）和页缓存（Leader 端日志常驻页缓存，FE |
| 372 | chapters/09-data-sync/chapter.md:220 | sec | 7.4.2 节 | Kafka 用 LEO（Log End Offset，日志末端偏移量）和 HW（High Watermark，高水位）描述副本的同步进度，用 ISR（同步副本集合）框定"谁算跟上"。ISR 的定义与动态进出机制已在第 7 |
| 373 | chapters/09-data-sync/chapter.md:220 | ch | 第 7 章 | Kafka 用 LEO（Log End Offset，日志末端偏移量）和 HW（High Watermark，高水位）描述副本的同步进度，用 ISR（同步副本集合）框定"谁算跟上"。ISR 的定义与动态进出机制已在第 7 |
| 374 | chapters/09-data-sync/chapter.md:222 | fig | 图 9-7 | 从同步视角看，LEO 是每个副本的本地位点，HW 是 Leader 据此计算出的"已确认边界"：HW 等于当前 ISR 中所有副本（含 Leader 自己）的最小 LEO，HW 以下才算已提交，消费者才读得到。**副本间 |
| 375 | chapters/09-data-sync/chapter.md:222 | seeref | 见 | 从同步视角看，LEO 是每个副本的本地位点，HW 是 Leader 据此计算出的"已确认边界"：HW 等于当前 ISR 中所有副本（含 Leader 自己）的最小 LEO，HW 以下才算已提交，消费者才读得到。**副本间 |
| 376 | chapters/09-data-sync/chapter.md:224 | fig | 图 9-7 | ![图 9-7 Kafka Follower FETCH + LEO/HW + leader epoch](diagrams/fig-9-7.svg) |
| 377 | chapters/09-data-sync/chapter.md:225 | fig | 图 9-7 | 图 9-7　HW 与 leader epoch：HW = ISR 中最小 LEO，只有 HW 以下算已提交；leader epoch 用任期号界定权威日志段，截断老 Leader 的脑裂尾部。 |
| 378 | chapters/09-data-sync/chapter.md:237 | sec | 7.4.3 节 | Kafka 把一致性强度做成了生产者侧的 `acks` 参数（0 / 1 / all 三档），它配合 `min.insync.replicas`（ISR 最少要有几个副本才允许写入）构成 Kafka 的可靠性语义。三档的 |
| 379 | chapters/09-data-sync/chapter.md:237 | ch | 第 7 章 | Kafka 把一致性强度做成了生产者侧的 `acks` 参数（0 / 1 / all 三档），它配合 `min.insync.replicas`（ISR 最少要有几个副本才允许写入）构成 Kafka 的可靠性语义。三档的 |
| 380 | chapters/09-data-sync/chapter.md:239 | seeref | 见 | `acks=all` + `min.insync.replicas` 与 MySQL 半同步在**降级语义**上存在关键差别：MySQL 半同步在超时时降级回异步，弱化一致性以保障可用性，Kafka 在 ISR 不足 ` |
| 381 | chapters/09-data-sync/chapter.md:260 | seeref | 见 | 事务更进一步：跨多个分区的一组写入要么全部成功要么全部不可见，靠 transaction coordinator 和两阶段提交（对消费者暴露 `committed` 标记）实现。这把"状态机复制"从"状态一致"延伸到了" |
| 382 | chapters/09-data-sync/chapter.md:272 | tab | 表 9-1 | **表 9-1　三个软件数据同步机制横向对比** |
| 383 | chapters/09-data-sync/chapter.md:278 | seeref | 见 | | 一致性模型 | 默认偏 AP（异步可丢写，分区时偏 CP；见 7.2.3） | 异步 / 半同步 / 多数派强一致（逐档增强） | ISR + acks 可调（AP ↔ CP） | |
| 384 | chapters/09-data-sync/chapter.md:317 | seeref | 见 | 同步进度怎么表示，是这个机制要解决的头一个问题（三个软件的位点形态见 9.5 解读二）。没有位点，副本断了就无从续传；有了它，增量同步、故障恢复都成了对齐位点的简单操作。多份副本要对齐，靠的就是同一套度量标准。 |
| 385 | chapters/09-data-sync/chapter.md:325 | seeref | 见 | 原因在于全量同步代价巨大。Redis 全量要 fork（阻塞 + 内存风险），MySQL 的全量靠克隆或长 binlog 回放，Kafka 则要拷整个分区日志。频繁全量会拖垮主节点、消耗带宽、延长恢复时间。所以设计原则是 |
| 386 | chapters/09-data-sync/chapter.md:329 | ch | 第 7 章 | 正如 9.5 解读三所说，三个软件在同一条延迟-一致性曲线上站在不同位置；第 7 章启示二从集群选型看过同一条谱线，这里把它落到复制设计的动作上。MySQL 的半同步超时参数（默认 10 秒）就是这条延迟预算的上限：等副 |
| 387 | chapters/09-data-sync/chapter.md:339 | seeref | 见 | 三个常见的反模式，都是从正面启示的反面衍生出来的： |
| 388 | chapters/09-data-sync/chapter.md:353 | ch | 第 10 章 | 导读里"缓存和数据库不一致时该以谁为准"的答案不在多副本，而在正本（source of truth）：数据库是正本、缓存是可重建的派生数据，见第 10 章规律一。 |
| 389 | chapters/09-data-sync/chapter.md:353 | seeref | 见 | 导读里"缓存和数据库不一致时该以谁为准"的答案不在多副本，而在正本（source of truth）：数据库是正本、缓存是可重建的派生数据，见第 10 章规律一。 |
| 390 | chapters/09-data-sync/chapter.md:355 | ch | 第 10 章 | 本章的状态机复制和位点对齐，是第 10 章规律五的核心印证。 |
| 391 | chapters/10-epilogue.md:7 | ch | 第 10 章 | 全书反复出现几条线索，我在第 10 章把它们收成了五条规律：唯一正本、层间契约、顺序与批量、可靠性的代价、显式建模的状态。这些规律不只属于这三个软件。管理状态、权衡性能与可靠性的系统，面对的也是这些约束；在分布式里维持一 |
| 392 | chapters/10-epilogue.md:23 | ch | 第 7 章 | 去年我在一个项目里犯了错。第 7 章开头那次库存事故就出在这个项目，这里完整复盘一遍。那个项目是一个活动库存系统，业务方说"要快"，我们就选了 Redis Cluster 做主存储。上线第一个月一切正常，响应时间在个位数 |
| 393 | chapters/10-epilogue.md:27 | seeref | 见 | 事后复盘，团队所有人的第一反应是"Redis 丢了数据"。但 Redis 其实没出 bug，是我们把一个默认形态偏 AP（异步复制可丢写，CAP 归类见 7.2.3）的系统用在了必须保证一致性的场景上。库存属于交易数据， |
| 394 | chapters/10-epilogue.md:67 | seeref | 见 | 本书勘误与版本更新见 https://gitee.com/flainliu/redis-kafka-books，欢迎读者反馈；技术细节随版本演进，采纳前请以 Redis、MySQL、Kafka 官方文档为准。 |
| 395 | chapters/10-summary/chapter.md:15 | tab | 表 10-1 | **表 10-1　九章启示总表** |
| 396 | chapters/10-summary/chapter.md:19 | ch | 第 1 章 | | 第 1 章 引言 | 选哪三个软件做样本 | 内存型代表 | 持久化型代表 | 流式型代表 | 范式互补才有研究价值，差异越大共性越容易看出来 | |
| 397 | chapters/10-summary/chapter.md:20 | ch | 第 2 章 | | 第 2 章 数据结构与协议 | 如何定义数据格式与通信协议 | RESP 文本协议 + SDS/listpack/intset 按数据量自适应 | 二进制协议 + Dynamic 行格式 | RecordBatch  |
| 398 | chapters/10-summary/chapter.md:21 | ch | 第 3 章 | | 第 3 章 生命周期 | 启动关闭如何不丢状态 | RDB/AOF 重放重建内存 | 崩溃恢复重放 redo log、用 undo log 回滚未提交事务，保住事务一致性 | Controller 选举 + 日志恢复 |
| 399 | chapters/10-summary/chapter.md:22 | ch | 第 4 章 | | 第 4 章 内存与磁盘 | 内存和磁盘怎么分工 | 内存为主存储、磁盘是恢复副本 | 磁盘为主存储、内存是缓冲池 | 磁盘日志为主存储、PageCache 加速 | 先问访问模式，再选存储范式；范式落定，正本位置随之 |
| 400 | chapters/10-summary/chapter.md:23 | ch | 第 5 章 | | 第 5 章 分层架构 | 怎么让系统可替换 | robj type/encoding 解耦直连 | THD + Handler 虚函数（可插拔引擎） | RequestChannel 队列 + 网络协议 | 分层是为 |
| 401 | chapters/10-summary/chapter.md:24 | ch | 第 6 章 | | 第 6 章 安全 | 主体能对客体做什么 | 从无密码演进到 ACL | 细粒度 grant 表写进数据字典 | SASL + ACL + 端到端 TLS | 安全设计的上限取决于数据模型和请求要经过的跳数 | |
| 402 | chapters/10-summary/chapter.md:25 | ch | 第 7 章 | | 第 7 章 集群 | 多副本怎么一致 | 主从 → Sentinel → Cluster 槽分片 + Gossip | 异步 → 半同步 → MGR（Paxos 类多数派） | 分区 + ISR + KRaft（去  |
| 403 | chapters/10-summary/chapter.md:26 | ch | 第 8 章 | | 第 8 章 存储格式 | 字节怎么排列才好访问 | RDB/AOF 为"全量加载 + 增量重放"优化 | 16KB 页 + B+ 树为"点查 + 范围扫描"优化 | 日志段 + 稀疏索引为"顺序追加 + 偏移量定位" |
| 404 | chapters/10-summary/chapter.md:27 | ch | 第 9 章 | | 第 9 章 数据同步 | 怎么让两个状态机一致 | PSYNC（部分重同步 + 全量回退） | binlog + GTID（基于事务的精确位点） | ISR + leader epoch 截断 + acks/幂等/事 |
| 405 | chapters/10-summary/chapter.md:43 | seeref | 见 | 把这条规律拿到你自己的系统里：我自己设计一个有状态系统，第一件事先回答"哪份数据是正本"。这个答案一旦模糊，故障恢复就会失控，因为恢复时你不知道该信谁。一个常见的反例是把缓存和数据库都当正本，结果两者不一致时系统行为不可 |
| 406 | chapters/10-summary/chapter.md:57 | fig | 图 10-1 | 这条规律的根，在更底层的存储层次结构里。CPU 的寄存器、L1/L2 缓存、内存、磁盘，本身就是一套"快而小"与"慢而大"交替的分层，每一层替下一层挡掉大部分访问，顺序和批量因此在所有层级上都占便宜。第 4 章启示五讲的 |
| 407 | chapters/10-summary/chapter.md:57 | ch | 第 4 章 | 这条规律的根，在更底层的存储层次结构里。CPU 的寄存器、L1/L2 缓存、内存、磁盘，本身就是一套"快而小"与"慢而大"交替的分层，每一层替下一层挡掉大部分访问，顺序和批量因此在所有层级上都占便宜。第 4 章启示五讲的 |
| 408 | chapters/10-summary/chapter.md:59 | fig | 图 10-1 | ![图 10-1 存储层次的对照：处理器与存储系统](diagrams/fig-10-1.svg) |
| 409 | chapters/10-summary/chapter.md:60 | fig | 图 10-1 | 图 10-1　存储层次的对照：左侧是处理器的存储层次（寄存器→L1/L2 缓存→内存→磁盘），右侧是 Redis、MySQL、Kafka 在"内存-磁盘"之间的对应分层；两侧是同一条"快而小、慢而大、逐层缓存"的思路。 |
| 410 | chapters/10-summary/chapter.md:74 | sec | 3.3 节 | 一个有状态的系统，运行时都在维护一堆隐式或显式的状态。它们的做法是把这些状态显式建模，并为每个状态预先写定恢复路径。Redis 启动就是按 RDB/AOF 把状态重放回去。MySQL 把活跃事务、锁等待、LSN 当运行时 |
| 411 | chapters/10-summary/chapter.md:94 | seeref | 见 | **维度二：一致性 vs 可用性（CAP 的工程体现）**。网络分区一来，你要么写对要么继续服务，没有两全。Redis Cluster 默认偏 AP（归类见 7.2.3），分区时持有多数主节点的分区继续服务、少数派分区的 |
| 412 | chapters/10-summary/chapter.md:108 | fig | 图 10-2 | ![图 10-2 实践者选型决策树](diagrams/fig-10-2.svg) |
| 413 | chapters/10-summary/chapter.md:109 | fig | 图 10-2 | 图 10-2　实践者选型决策树：四个问题依次收窄，每个叶子对应可借鉴的设计。 |
| 414 | chapters/10-summary/chapter.md:117 | seeref | 见 | **练习一："做一个网约车系统，司机位置上报和派单该放 Redis 还是 MySQL？"** 常见的思路是"都是核心系统，统一放 MySQL"。但这两个子问题的访问模式完全不同。司机位置每几秒上报一次，读写都高频，丢一次 |
| 415 | chapters/10-summary/chapter.md:121 | ch | 第 7 章 | **练习三："一个新业务，要不要一上来就分库分表？"** 分片牺牲了单机事务、JOIN、外键约束，换来水平扩展——这笔账对新业务几乎必亏：过早分片等于为一个还不需要的容量去付昂贵的灵活性代价。用维度四（简单 vs 灵活） |
| 416 | chapters/10-summary/chapter.md:131 | tab | 表 10-2 | 把 10.3 的五个维度拆成 12 个具体问题，按"数据 / 性能 / 可靠性 / 运维"四类组织。表 10-2 把每个问题连同"三个软件的答案"和"你的答案"放在一起，作为动手前的自检工具。 |
| 417 | chapters/10-summary/chapter.md:133 | tab | 表 10-2 | **表 10-2　架构设计 checklist（12 问）** |
| 418 | chapters/10-summary/chapter.md:156 | fig | 图 10-3 | ![图 10-3 从使用者到设计者的四个阶段](diagrams/fig-10-3.svg) |
| 419 | chapters/10-summary/chapter.md:157 | fig | 图 10-3 | 图 10-3　从使用者到设计者的四个阶段：四级台阶自下而上，两个虚线标注框标出本书各部分覆盖的阶段。 |
| 420 | chapters/10-summary/chapter.md:159 | seeref | 见 | 四个阶段的差距不在掌握的名词多少，在能独立产出什么：使用者交出一份能跑的配置；理解者能写出机制解释，能判断一次慢查询慢在哪一层；设计者能给出自己系统的结构与取舍方案；创新者定义新的范式。常见的问题有两种。一种是产出停在使 |
| 421 | chapters/10-summary/chapter.md:175 | ch | 第 1 章 | 回到第 1 章的组织方式：三个软件对同一批问题有三份不同方案，但做决策的步骤是同一套——先认约束，再确定唯一正本，然后用分层、批量、一致性档位、显式状态把正本做成能用的系统。理解共性之后，剩下的判断是：哪个方案适合自己的 |
