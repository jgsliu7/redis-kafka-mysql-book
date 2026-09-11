# V003 · 序言 · 命令实操视角

审读对象：`chapters/00-preface.md`（23 行，Read 工具逐字核对）。
视角：8 年 DBA/运维，redis-cli / mysql / kafka 命令行参数与默认值烂熟。

| # | 位置 | 原文 | 意见 | 类型 |
|---|------|------|------|------|
| 1 | L17 | （本书基于 Redis 7.x、MySQL 8.0.x、Kafka 3.x） | 序言对全书版本的唯一声明，Kafka 缺模式标注，与全书实际口径不一致。这不是措辞问题，直接影响读者选哪个发行版跟书操作：全书按 KRaft 模式写作——契约 `docs/book-bible.md` §2 的 Kafka 锚点第一项就是"KRaft（去 ZooKeeper）"，第 7 章大纲基线明确写"Kafka 3.x（KRaft）"（`chapters/07-cluster/outline.md` L16），第 3、9 章正文以 KRaft 为主线（`chapters/03-lifecycle/chapter.md` L153、`chapters/09-data-sync/chapter.md` L252）。而正文自己写明"对新集群自 3.3 起生产可用"——"3.x" 字面涵盖的 3.0–3.2 根本不满足全书基线。运维读者若装 3.0–3.2 跟书走，`process.roles`、`controller.listener.names`、`kafka-storage.sh format`、`kafka-metadata-quorum.sh` 这套 KRaft 专属的部署步骤和命令一个都对不上。改进：括号内补三个字，写成 "Kafka 3.x（KRaft）"，与第 7 章口径对齐；成本最低，防的是读者按序言声明选错版本。 | 一致性 |
| 2 | L17 | （本书基于 Redis 7.x、MySQL 8.0.x、Kafka 3.x） | 三家版本锁定粒度不统一，"3.x" 对 Kafka 锁得太松，读者无法据此回答"我该装哪一版来跟书跑"。Redis 7.x 和 MySQL 8.0.x 都锁到 minor——这两个范围内命令面基本稳定，锁到 minor 够用；Kafka 却只锁到 major，而 Kafka 恰恰是三家中小版本跃迁最剧烈的：3.0 移除一批 ZooKeeper 时代参数选项、3.3 KRaft 生产可用、3.5 ZooKeeper 标记弃用，导读正文自己都补了一句"分层存储 Tiered Storage 相关讨论以 3.9+ 为准"（`chapters/01-introduction/chapter.md` L192）。同一个 "x" 在三个名字里的跨度完全不同。改进：统一锁到 minor，或至少注明下限，如 "Kafka 3.x（KRaft，3.3+）"；这样书里所有参数默认值断言才有可锚定的版本。 | 可懂性 |

## 其余内容无发现（说明）

序言是纯文字章节：全文 23 行，零命令块、零参数名、零配置片段、零 SQL，与命令/配置/实操直接相关的表述只有 L17 版本声明这一处（即上表两条意见）。其余可能被实操视角扫到的表述逐一核过，均无问题：

- L5 "Redis 的数据类型有几种，MySQL 的索引怎么建，Kafka 的分区选几个"——是对"市面资料停在怎么用"的概括引用，不含具体命令，无错可挑。
- L9 "怎么启动才能不丢状态、怎么关闭才能不丢请求"等九项——抽象层主题列举，未落到具体命令，不构成实操断言。
- L13 "Redis 写盘不是最快的，Kafka 随机查询也不是最快的"——运维常识上成立：Redis 的持久化（RDB/AOF）不以写盘吞吐为目标，Kafka 本就不提供随机点查能力；判断无误，不硬挑。

本视角真实发现即上表 2 条，均为 L17 版本声明问题（一条管口径一致，一条管锁定粒度）；不凑第 3 条。
