# 术语规范审查报告 T02

**审查范围**: chapters/ 下所有 chapter.md（共 10 章） + 序言 / 后记
**参考标准**: docs/book-bible.md §7 术语对照表
**日期**: 2026-07-03

---

## 已统一（✅ 相符）

以下核心术语在全书中使用一致，符合 book-bible 规范：

| 术语 | 状态 | 说明 |
|------|------|------|
| redo log | ✅ | "重做日志（redo log）"首现后统一用 en "redo" |
| undo log | ✅ | "回滚日志（undo log）"首现后统一用 en "undo" |
| MVCC | ✅ | 首现"多版本并发控制（MVCC, Multi-Version Concurrency Control）"后均用 en "MVCC" |
| ACID | ✅ | 首现"ACID（原子性、一致性、隔离性、持久性）"后均用 en "ACID" |
| offset | ✅ | 全书统一"偏移量（offset）", 未见"位移" |
| partition | ✅ | 统一"分区" |
| replica / 副本 | ✅ | 统一"副本" |
| leader / 主节点 | ✅ | 统一"主节点"（Kafka 特有"Leader"保留为角色名，见备注） |
| follower / 从节点 | ✅ | 统一"从节点"（Kafka 特有"Follower"保留为角色名，见备注） |
| snapshot / 快照 | ✅ | 统一"快照" |
| segment / 日志段 | ✅ | 统一"日志段" |
| flush / 刷盘 | ✅ | "刷盘"统一为中文 |
| fsync / 落盘 | ✅ | 统一"fsync（落盘）"后可混用 |
| Buffer Pool / 缓冲池 | ✅ | 统一"缓冲池" |
| append-only log / 追加写日志 | ✅ | 统一中文"追加写日志" |
| replication / 复制 | ✅ | 统一"复制" |
| AOF | ✅ | 首现"AOF（Append-Only File, 仅追加文件）"后统一用 en "AOF" |
| ISR | ✅ | 首现"ISR（In-Sync Replicas, 同步副本集合）"后统一用 en "ISR" |
| GTID | ✅ | 首现"全局事务标识（GTID, Global Transaction Identifier）"后统一用 en "GTID" |
| MGR | ✅ | 首现"组复制（MGR, MySQL Group Replication）"后统一用 en "MGR" |
| LEO | ✅ | 首现"LEO（Log End Offset, 日志末端偏移量）"后统一用 en "LEO" |
| HW | ✅ | 首现"HW（High Watermark, 高水位）"后统一用 en "HW" |
| SDOWN/ODOWN | ✅ | 首现"主观下线（SDOWN, subjectively down）" / "客观下线（ODOWN, objectively down）"后均用 en |
| checkpoint | ✅ | "checkpoint"作为英文术语一致 |
| LSN | ✅ | 首现"LSN（日志序号）"后统一用 en "LSN" |
| RDB | ✅ | 首现"RDB（快照文件）"后统一用 en "RDB" |
| ACL | ✅ | 首现"ACL（Access Control List, 访问控制列表）"后统一用 en "ACL" |
| SASL | ✅ | 首现"SASL（Simple Authentication and Security Layer, 简单认证与安全层）"后统一用 en "SASL" |
| TLS | ✅ | SSL/TLS 未单独定义，但作为通用术语可接受 |
| RESP | ✅ | 首现"RESP（REdis Serialization Protocol）"后统一用 en "RESP" |
| RTO | ✅ | 首现"RTO（Recovery Time Objective, 恢复时间目标）" |
| RPO | ✅ | 首现"RPO（Recovery Point Objective, 恢复点目标）" |
| DML/DDL | ✅ | 在 Ch6:121 展开 |
| KRaft | ✅ | 首现"KRaft（Kafka Raft）"后统一 |

---

## 🔴 漂移（同一概念多种叫法 / 缩写首次未展开 / 术语表违反）

### R1. WAL 首次出现未展开 + 后续全称不一致

**标准**: `WAL | WAL（预写日志，Write-Ahead Log） | 英文`

- **Ch1:53** ("用'B+ 树 + 预写日志 + MVCC'") — 全书首次出现 WAL，只写了"预写日志"，未带英文缩写或全称。
- **Ch1:39** — "预写日志（WAL, Write-Ahead Log）" — 正式定义，但该行在正文顺序上晚于第 53 行（1.1.3 在 1.2.2 之前），所以首次出现缺展开。
- **Ch4:149** — "WAL（Write-Ahead Logging, 预写日志）" — 使用 "Write-Ahead **Logging**" 而非 "Write-Ahead **Log**"，与前例和标准不一致。
- **Ch3:29** — "WAL（预写日志）" — 展开顺序为英文在前，与 Ch1:39 不同。

**建议**: 在 Ch1:53 处补全为"预写日志（WAL, Write-Ahead Log）"；统一"Write-Ahead Logging"为"Write-Ahead Log"。

**严重度**: 🔴

### R2. REDO/UNDO 各章节首次出现格式不一致

**标准**: `redo log | 重做日志（redo log） | 英文`

- **Ch1:83** — "重做日志（redo log）记录物理修改" — 格式一致 ✅
- **Ch3:31** — "崩溃恢复靠的是 redo（重做日志，记录页级物理修改...）undo（回滚日志，记录操作的逻辑逆...）" — 格式变为"英文（中文，说明）"，与 Ch1 的"中文（英文）"格式相反
- **Ch3:93** — "重做日志（redo log）" — 与 Ch1 一致 ✅

**建议**: 统一为"重做日志（redo log）"模式，Ch3:31 改为"重做日志（redo log，记录页级物理修改）"。

**严重度**: 🟠

### R3. Quorum 混用英文/中文 + 翻译不一

**标准**: `quorum | 多数派 | 中文`

- **Ch7:63** — "达到配置的 quorum 数量" — 英文 quorum + "数量"
- **Ch7:65** — "多数派投票" — 中文 ✅
- **Ch6:70** — "节点间共识通信（quorum）" — 英文 quorum
- **Ch9:240** — "Controller quorum 维护" — 英文 quorum

全书多数位置用"多数派"中文，但偶尔混入英文"quorum"。

**建议**: [MAYBE_INTENTIONAL] 配置参数引用时可保留英文 quorum，正文描述统一为"多数派"。

**严重度**: 🟡

### R4. Compaction 首次出现格式不符标准

**标准**: `compaction | compaction（压实） | 中英`

- **Ch1:99** — "压实（compaction）" — 中文优先
- **Ch8:158** — "压实（compaction）" — 中文优先
- **Ch8:252** — "compaction（压实）重写日志段" — **英文优先**（与标准一致）
- **Ch8:48** — "后台合并（compaction）" — 另一种译法"合并"而非"压实"

Ch1 先出现"压实（compaction）"中文优先，Ch8:252 改为"compaction（压实）"英文优先，前后不一致。

**建议**: 统一为"compaction（压实）"英文优先格式。

**严重度**: 🟡

### R5. EPOCH 翻译跨章不一致（"纪元" vs "任期号" vs "任期"）

**标准**: `epoch / term | 任期 | 中文`

- **Ch7:84** — "用集群**纪元** epoch 防止过期投票" — "纪元"，与标准"任期"不同
- **Ch7:63** — "借鉴了 Raft 的**任期号**" — "任期号" ✅
- **Ch9:213,219** — "leader epoch 用**任期号**界定权威日志段" — "任期号" ✅
- **Ch10:71** — "Controller 任期（epoch）" — "任期" ✅

**建议**: 将 Ch7:84 的"集群纪元"改为"集群任期"。

**严重度**: 🟠

### R6. OLTP 首次在 Ch2 出现未展开

- **Ch2:25** — "OLTP 场景下" — 全书首次出现，未给全称
- **Ch5:130** — "OLTP（联机事务处理）" — 只给了中文，未给英文全称"Online Transaction Processing"

**建议**: Ch2:25 首次出现时改为"OLTP（联机事务处理，Online Transaction Processing）"。

**严重度**: 🟠

### R7. QPS 全书未展开

- **Ch1:144** — "压到多少 QPS" — 首次出现，无全称
- **Ch6:24** — "单核十万级 QPS" — 同上

**建议**: 首次出现处补全为"QPS（Queries Per Second，每秒查询数）"。

**严重度**: 🟡

### R8. CRC 未给英文全称

- **Ch2:64** — "CRC（整批一条校验）" — 有注释但未给"Cyclic Redundancy Check"
- **Ch8:70** — "CRC64 校验" — 同上

**建议**: 首次出现处补全为"CRC（Cyclic Redundancy Check，循环冗余校验）"。

**严重度**: ⚪

### R9. BIO 未展开

- **Ch5:79** — "后台 BIO 线程异步释放" — BIO（Background I/O）未展开

**建议**: 首次出现处补全为"BIO（Background I/O，后台 I/O）"。

**严重度**: ⚪

### R10. THP 未给英文全称

- **Ch4:32** — "透明大页（THP）" — 仅有缩写无英文全称"Transparent Huge Pages"

**建议**: 补全为"透明大页（THP，Transparent Huge Pages）"。

**严重度**: ⚪

### R11. RDB 首次出现未按标准格式

**标准**: `RDB | RDB（快照文件） | 英文`

- **Ch1:69** — "持久化靠 RDB 快照与 AOF" — 首次出现，"RDB 快照"词组未按"RDB（快照文件）"定义
- **Ch5:81** — "RDB（快照文件）做全量快照" — 按标准格式定义，但 Ch1 已用 RDB

**建议**: Ch1:69 首次出现改为"RDB（快照文件）"。

**严重度**: 🟡

---

## 🟡 大小写 / 格式规范问题

### F1. 中文-英文先后顺序不一致

book-bible §7 允许"中文（英文）"或"英文（中文）"两种标注顺序。实际正文两者混用：
- **中文优先**: redo log / undo log / binlog / MVCC / WAL / Buffer Pool / partition / compaction
- **英文优先**: AOF / RDB / ISR / SASL / ACL / RESP / TPS / GTID / RPO / RTO / LSM-Tree

虽合规范，但未做统一。

**建议**: 不强制统一 [MAYBE_INTENTIONAL]，但若作者选择统一可定标。

**严重度**: ⚪

### F2. binlog 首次出现与标准格式相反

**标准**: `binlog | binlog（二进制日志） | 英文`

- **Ch1:83** — "二进制日志（binlog）" — 中文优先，标准为英文优先

**建议**: 首次改为"binlog（二进制日志）"。

**严重度**: 🟡

---

## 🔴 术语表外问题（建议更新术语表）

### T1. LSM-Tree 未收入术语表

Ch8:48 使用"日志结构合并树（LSM-tree）"、SST，未收入术语表。

### T2. ARIES 未收入术语表

Ch10:71 使用"ARIES 协议（分析、重做、回滚三阶段）"，应补入术语表。

### T3. 常见英文缩写未全部登记

Ch6 安全章节出现 KMS/LDAP/PAM/Kerberos/JAAS 等缩写，建议选择性补入。

---

## 总结统计

| 类别 | 数量 | 明细 |
|------|------|------|
| 已统一（✅ 相符） | 约 30+ 术语 | 全书规范一致 |
| 🔴 严重漂移 | 1 项 | R1: WAL 首次未展开 + 全称分歧 |
| 🟠 中等漂移 | 3 项 | R2: redo/undo 格式 / R5: epoch 翻译 / R6: OLTP 展开 |
| 🟡 轻微漂移 | 4 项 | R3: quorum / R4: compaction / R7: QPS / R11: RDB |
| ⚪ 建议事项 | 4 项 | R8: CRC / R9: BIO / R10: THP / F1 格式 |
| 术语表外建议 | 3 项 | T1: LSM / T2: ARIES / T3: 安全缩写 |

### 最需优先处理的 3 项

1. **R1**: WAL 首次出现（Ch1:53）未展开 + 全称"Logging/Log"不一致
2. **R5**: epoch 在 Ch7:84 译为"纪元"与全书"任期"不一致
3. **R6**: OLTP 在 Ch2:25 首次出现未展开英文全称
