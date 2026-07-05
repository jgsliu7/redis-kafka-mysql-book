# T02 术语一致性审查报告

审查范围：chapters/00-preface.md、chapters/01-introduction/chapter.md、chapters/02-data-structures-protocols/chapter.md、chapters/03-lifecycle/chapter.md、chapters/04-memory-disk/chapter.md、chapters/05-layered-architecture/chapter.md、chapters/06-security/chapter.md、chapters/07-cluster/chapter.md、chapters/08-storage-format/chapter.md、chapters/09-data-sync/chapter.md、chapters/10-summary/chapter.md、chapters/10-epilogue.md、chapters/11-references.md

参照标准：docs/book-bible.md §7 术语对照表

审查方法：逐术语 grep 全书，核实首次标注格式与后续语种策略是否遵循 bible 契约。

## 发现汇总
- 总问题数：14（7 项首次标注格式 + 3 项语种策略 + 2 项概念混用 + 2 项缺失标注）

---

## 逐条发现

### 一、首次标注格式与 bible §7 术语表不一致

以下术语在**第一次出现位置**的标注格式与 bible 表中指定的格式不符：

#### 1. [01-introduction/chapter.md:39] WAL 首次标注
- 原文：`预写日志（WAL，Write-Ahead Log）`
- Bible 规定：`WAL（预写日志，Write-Ahead Log）`
- 问题：应为缩写优先 `WAL` 在前，而非中文"预写日志"在前。
- 建议：改为 `WAL（预写日志，Write-Ahead Log）`

#### 2. [01-introduction/chapter.md:39] MVCC 首次标注
- 原文：`多版本并发控制（MVCC，Multi-Version Concurrency Control）`
- Bible 规定：`MVCC（多版本并发控制）`
- 问题：bible 只要求缩写 + 中文解释，不应额外加英文全称；且顺序应为缩写优先。
- 建议：改为 `MVCC（多版本并发控制）`

#### 3. [01-introduction/chapter.md:83] binlog 首次标注
- 原文：`二进制日志（binlog）`
- Bible 规定：`binlog（二进制日志）`
- 问题：应为缩写优先 `binlog` 在前。
- 建议：改为 `binlog（二进制日志）`

#### 4. [01-introduction/chapter.md:99] compaction 首次标注
- 原文：`压实（compaction）`
- Bible 规定：`compaction（压实）`
- 问题：应为英文优先 `compaction` 在前（bible 说明列为"中英"均可，但首次标注格式指定了英文优先）。
- 建议：改为 `compaction（压实）`

#### 5. [01-introduction/chapter.md:69] RDB 首次出现缺失标注
- 原文：`RDB 快照`（无独立标注）
- Bible 规定：`RDB（快照文件）`
- 问题：首次出现时没有按 bible 给出标注。
- 建议：首次出现改为 `RDB（快照文件）`

#### 6. [01-introduction/chapter.md:69] AOF 首次标注含多余英文全称
- 原文：`AOF（Append-Only File，仅追加文件）`
- Bible 规定：`AOF（仅追加文件）`
- 问题：bible 只要求缩写 + 中文解释，不应额外加英文全称。
- 建议：改为 `AOF（仅追加文件）`

#### 7. [01-introduction/chapter.md:97] ISR 首次标注含多余英文全称
- 原文：`ISR（In-Sync Replicas，同步副本集合）`
- Bible 规定：`ISR（同步副本集合）`
- 问题：bible 只要求缩写 + 中文解释，不应额外加英文全称。
- 建议：改为 `ISR（同步副本集合）`

### 二、两档制语种策略与 bible 不一致

Bible §7 术语表规定了每个术语在首次标注后的**后续语种**（英文/中文/中英均可），以下术语未遵守该策略：

#### 8. [多个章节] redo log 后续未按"用英文"策略
- Bible 规定：后续用 **英文**（即 "redo log"）
- 实际：全书在首次标注后大量使用"重做日志"（中文），例如：
  - ch08/storage-format/chapter.md 全章：标题、正文、表格共 20+ 处使用"重做日志"
  - ch04/memory-disk/chapter.md:151 `**重做日志（redo log）**`（二次标注，应直接写 `redo log`）
  - ch04/memory-disk/chapter.md:253 表格：`重做日志（WAL）`
  - ch10/summary/chapter.md:45 `磁盘上的重做日志是真相之源`
- 建议：首次标注后，将"重做日志"统一改为英文"redo log"（除非在中文语境中必须提前解释时才保留）。

#### 9. [多个章节] undo log 后续未按"用英文"策略
- Bible 规定：后续用 **英文**（即 "undo log"）
- 实际：全书大量使用"回滚日志"（中文），例如：
  - ch05/layered-architecture/chapter.md:129 `重做日志与回滚日志`
  - ch10/summary/chapter.md:150 `重做日志重做 + 回滚日志回滚`
- 建议：首次标注后，将"回滚日志"统一改为英文"undo log"。

#### 10. [多个章节] binlog 后续基本正确，但存在冗余二次标注
- Bible 规定：后续用 **英文**（即 "binlog"）
- 实际：ch07/cluster/chapter.md:96, 107 等处反复出现"二进制日志（binlog）"二次标注。虽然不是错误，但在全书已首次标注后，新章节重复全称标注略显冗余。
- 建议：新章节首次出现时若需提醒，可简化为"binlog"而非完整二次标注。

### 三、概念混用

#### 11. [04-memory-disk/chapter.md:253] "重做日志（WAL）" 概念不准确
- 原文（表格）：`重做日志（WAL）+ 脏页刷盘 + 双写缓冲`
- 问题：此处将"重做日志"（redo log，MySQL 的具体日志实现）与"WAL"（预写日志设计原则）等同标注。WAL 是一种设计模式，redo log 是 MySQL 对 WAL 的一种实现。用 WAL 指代 redo log 容易造成概念混淆。
- 上下文佐证：ch04/memory-disk/chapter.md:151 已正确区分——"重做日志（redo log）"是具体实现，"WAL（Write-Ahead Logging，预写日志）"是设计原则，两者应保持独立。
- 建议：表格改为 `重做日志 + 脏页刷盘 + 双写缓冲`（去掉括号内的 WAL），或改为 `redo log / WAL`。

#### 12. [08-storage-format/chapter.md:237] 表格中"原地改页 + WAL"
- 原文（表格）：`原地改页 + WAL`
- 问题：同样将 WAL（设计原则）等同于具体的日志机制。此处上下文是 MySQL 的写方式，用 WAL 指代 redo log。
- 建议：改为 `原地改页 + redo log`。

### 四、缺失标注的术语（bible 未列但书中使用且首次未加英文全称）

#### 13. [03-lifecycle/chapter.md:93] LSN 首次出现缺英文全称
- 原文：`LSN（日志序号）`
- 问题：LSN 不在 bible 术语表中，首次出现时做了中文解释，但未给出英文全称（Log Sequence Number）。全书缩写的惯例应是首次出现带英文全称。
- 建议：改为 `LSN（Log Sequence Number，日志序号）`

#### 14. [04-memory-disk/chapter.md:253] 横向对比表——Kafka 列用"副本"含义模糊
- 原文：`OS 异步刷盘 + 生产者 \`acks\` + 副本`
- 问题：此处"副本"作为"持久化机制"的一部分放在 Kafka 列。Bible 术语表将"replica / follower"定义为"副本 / 从节点"（中文优先），且此处"副本"含义不够精确（应具体指"多副本复制"）。
- 建议：改为 `OS 异步刷盘 + acks + ISR 多副本复制`，更准确地表述 Kafka 的持久化机制。

---

### 🟡 大小写/中英对照规范

**无问题**：Redis、MySQL、Kafka 三种专有名词全书中英大小写均正确，未发现小写错误。

**偏移量 vs 位移**：全书 grep "位移" 0 处，统一使用"偏移量"或"offset"，符合规范。

---

### ✅ 已统一使用的术语（spot-check 通过）

检查确认以下术语全书一致性良好：

| 术语 | 状态 |
|------|------|
| offset | 始终为"偏移量（offset）"或直接写"offset"，未出现"位移" |
| Buffer Pool / 缓冲池 | 全书统一 |
| partition / 分区 | 全书统一 |
| snapshot / 快照 | 全书统一 |
| segment / 日志段 | 全书统一 |
| quorum / 多数派 | 全书统一 |
| epoch / term / 任期 | 全书统一 |
| graceful / 优雅 | 全书统一 |
| flush / 刷盘 | 全书统一 |
| fsync / 落盘 | 全书统一 |
| LEO / HW | 首次在 ch07:164 正确标注，后续使用一致 |
| GTID | 首次在 ch07:109 正确展开，后续使用一致 |
| SDOWN / ODOWN | 首次在 ch07:69 正确展开，后续使用一致 |
| ACID | 首次在 ch01:83 正确展开 |
| RESP | 首次在 ch02 正确展开 |
| ARIES | 首次在 ch10:71 正确展开 |

---

### 关于"中文（英文）"与"英文（中文）"格式的说明

Bible §3 允许两种格式（"中文（英文）或英文（中文）"），但 §7 术语对照表为每个术语明确指定了首次标注格式（见第 1-7 项）。全文倾向于使用"中文（英文）"格式（如"重做日志（redo log）"），这在 ch01:212 也有明确声明。然而 bible §7 中 binlog、WAL、MVCC、compaction、ISR、AOF、RDB 等 7 个术语指定的是"英文优先"格式。此处存在 §3 通用规则与 §7 特定规则之间的张力。建议由作者裁定：是统一为"中文（英文）"（覆盖全表），还是严格按照 §7 表的格式逐一校正。
