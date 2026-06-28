# 第 3 轮：技术事实一致性（交叉印证）

> **方法**：3 技术 Finder 并行 + 验证员（带 WebSearch）复核。
> - F1 = `fact-consistency`（9 条，跨章机制/参数/判断矛盾，深挖 CAP）
> - F2 = `number-provenance`（13 条，裸数字溯源，WebSearch 实证）
> - F3 = `command-runnable`（2 错 + 5 存疑，官方文档核实）
> - 验证员 = `general-purpose`（带 WebSearch，逐条核实版本/参数/字节）
>
> **门槛**：≥2 Agent 认定才 CONFIRMED；版本/参数类必须 WebSearch 官方文档/源码实证。
>
> **结论**：CONFIRMED **15 条**（直接 ≥2 共 3 + Finder×验证员 12），驳回 5 条。**两大重要发现**：(1) 近期"P0 CAP 对齐(12处)"提交**不完整**，3 处 CAP nuance 仍丢；(2) 抓出 4 处硬技术错（V0 字节数 / ACL 参数张冠李戴 / LDAP 插件名 / 日志加密版本），全部 WebSearch 实证。同时**洗清**出版审查清单 §3.3 的 3 个疑点（min-replicas/ACL/半同步变量均正确）。

---

## 一、CONFIRMED 发现（15 条）

### 🔴 硬技术错误（WebSearch 实证，最高优先级）

| # | 位置 | 问题 | 印证 | 正确事实 |
|---|------|------|------|---------|
| H1 | ch8:45 | "V0/V1 单条约 **12 字节**"——数字错 | F2 + 验证员（[Kafka message-format 官方](https://kafka.apache.org/43/implementation/message-format/)） | V0 单条 overhead = CRC4+magic1+attr1+keylen4+vallen4 = **14 字节**；V1（加 timestamp）约 22 字节 |
| H2 | ch6:133 | `allow.everyone.if.no.acl.found` "1.x 默认 true、2.0 起改 false"——**张冠李戴** | F3 + 验证员（[源码](https://github.com/a0x8o/kafka/)+[KAFKA-4711](https://issues.apache.org/jira/browse/KAFKA-4711)） | 该参数从 1.x 至 3.x **默认始终 false**（deny-by-default）。真正 0.11 起 true→false 的是 `unclean.leader.election.enable`（KAFKA-4711）。版本号/JIRA/参数名三重错 |
| H3 | ch6:58 | "`ldap_simple` 对接 LDAP"——**漏前缀** | F3 + 验证员（[MySQL LDAP 官方](https://dev.mysql.com/doc/en/ldap-pluggable-authentication.html)） | 正确名 `authentication_ldap_simple`（另有 `authentication_ldap_sasl`）。照敲 `ldap_simple` 会 "Unknown plugin" |
| H4 | ch6:155 | "8.0.14 binlog 加密、8.0.16 undo、8.0.17 redo 加密"——**三个版本错** | F3 + 验证员（[MySQL 8.0 加密官方](https://dev.mysql.com/doc/refman/8.0/en/innodb-data-encryption.html)） | redo/undo 加密参数 8.0.1 就有；binlog 加密 8.0.14（仅此一个对）。8.0.17 实为 redo **archiving**（归档）非加密 |

### 🔴 CAP nuance 丢失（证明"P0 CAP 对齐(12处)"提交不完整）

| # | 位置 | 问题 | 印证 | 改法 |
|---|------|------|------|------|
| C1 | ch9:143 | "MySQL 复制是异步的…这和 Redis 一样**偏 AP**" vs ch7"MySQL **偏 CP**" | F1 + 验证员 | 区分"默认复制形态偏 AP"与"产品定位偏 CP"，删"和 Redis 一样偏 AP"并列 |
| C2 | ch9:59 | "这是**偏 AP**（高可用优先）的取向"（Redis，无 nuance）vs 同章 ch9:101"**不作绝对归类**" | F1 + 验证员（章内矛盾） | 补"默认偏 AP（分区时偏 CP，社区有争议，本书不作绝对归类）" |
| C3 | ch10:100 | "**Redis Cluster 偏 AP**"（无 nuance）vs ch7:86/232 | F1 + 验证员 | 补 nuance 或改"在 CAP 光谱上偏向 AP 一端" |

### 🔴 跨章事实矛盾

| # | 位置 | 问题 | 印证 | 改法 |
|---|------|------|------|------|
| M1 | references:27 | 称 LSM-Tree 是"**Kafka 段文件与 compaction 设计源头**"，但 ch8:48"三款软件无一采用 LSM 树" | F1 + 验证员 + R2-GP（三方） | 改"LSM-Tree 是 MySQL 之外另一类存储引擎（RocksDB/LevelDB）的共同基础"，删 Kafka 归属 |
| M2 | ch3:201 | 横向表"MySQL…**默认最保守**"vs 同章 L113/123/185"默认=1（快速关闭，=0 才完全关闭）" | F1 + 验证员 | 改"默认中等档（=1），三档可调" |
| M3 | ch7:55 | "从节点就会**去主节点拉数据**"vs ch9:45/57/200/265"**主推送**命令流" | F1 + 验证员（[Redis 官方 push-based](https://redis.io/docs/latest/operate/oss_and_stack/management/replication/)） | 改"从节点发起连接，建立后主节点把命令流 push 给它" |
| M4 | ch4:96/259 + ch10:67/98 | "Redis **默认 everysec**"vs ch8:97"出厂默认 RDB-only（appendonly no）"——读者误以为默认就开 AOF | F1 + 验证员 | 加前提"开启 AOF 后 appendfsync 默认 everysec；Redis 出厂默认不开 AOF" |

### 🟠 数字溯源

| # | 位置 | 问题 | 印证 | 处置 |
|---|------|------|------|------|
| N1 | ch4:311 | "命中率掉到 95% 以下…延迟**翻倍甚至翻十倍**"——断言性数字无出处 | F2 + 验证员 | 软化为体感"命中率每掉几个百分点，未命中线性上升，延迟显著抬升" |
| N2 | ch7:40 | "KRaft 分区数 **10 万以上**"vs 同章 ch7:172/204"**百万级**"——同章数量级打架 | F1 + F2（双 Finder 直接命中） | 全书统一"百万级"（KRaft 官方目标） |

### ✅ 验证为干净（确认无问题，多方一致）

| 项 | 结论 | 印证 |
|----|------|------|
| **§3.3 疑点：min-replicas-to-write + min-replicas-max-lag**（7.x） | 正确（现役名，判定逻辑对） | F3 + 验证员 |
| **§3.3 疑点：ACL `SETUSER alice on >pwd ~keys:* +get +set`**（7.x） | 正确（`~` 是 key selector，7.x 有效） | F3 + 验证员 |
| **§3.3 疑点：半同步变量 source/replica 新旧名** | 正确（未混用，8.0.26 重命名说明准） | F3 + 验证员 |
| CAP 主基调（MySQL=CP、Kafka=可调） | 全书主线一致（仅上述 3 处 nuance 漏网） | F1 + F2 + 验证员 |

---

## 二、已驳回（5 条 + 1，正确剔除）

| 位置 | 原候选 | 驳回理由 |
|------|--------|---------|
| epilogue:27 | "偏 AP 的系统"无 nuance | **KEEP**——后记叙事性复盘（第一人称选型失误），非权威归类，强行加括注破坏叙事；读者已读 8 章完整 nuance |
| ch6:24/143 | "单核十万级 QPS" 7.x 过时 | **KEEP**——Redis 命令执行仍在主线程单核（6.0+ 多线程只卸载网络 IO），单核 8-10 万 QPS 是业界基线。措辞准确 |
| ch4:33 | "断崖下跌"夸张 | **KEEP**——DBA 圈通用比喻，非数字，属作者 nuance |
| ch7:39 | "跨 AZ 5-10 ms 共识"无源 | **KEEP**——同 region 跨 AZ（RTT 1-5ms）量级正确，已标"以实际为准"。跨 region 才 100ms 级 |
| ch9:246 | "事务（transactional）" 易误读为参数名 | **KEEP**——此处是功能类别名（与"幂等"并列），非参数引用，规范。可优化但非错误 |

---

## 三、本轮"优化"动作

1. **WebSearch 是版本类问题的硬要求**：4 处硬技术错（H1-H4）全靠 WebSearch 官方文档/源码实证。单靠记忆判版本号会错（验证员本可凭记忆判，但坚持查证才确认 H2 的 KAFKA-4711 张冠李戴、H4 三个版本错）。
2. **CAP 对齐提交不完整 = 流程问题**：commit `39d66b9`（"P0 CAP 全书对齐 12 处"）后，C1/C2/C3 三处 nuance 仍丢。这正是《出版审查清单与盲区》§5"核查闭环没接上"的活体证据——`pub_assertions.py` 回归脚本应补 CAP nuance 断言（如"ch9:143 不得出现'和 Redis 一样偏 AP'且无 CP 补充"），否则下次改稿又回弹。**建议把 C1-C3 转成断言写进 pub_assertions.py。**
3. **洗清历史疑点**：出版审查清单 §3.3 列的 3 个命令疑点（min-replicas/ACL/半同步）经第 3 轮核实**全部正确**——这些可从"待查清单"移除，并在 pub_assertions.py 标记为"已验证正确"。
4. **下轮调整**：第 3 轮证明 references 是事实/术语双重灾区（M1 + R2 轮 R1-R3）。第 4 轮 crossref-validity 重点查 references 与正文的章号/出处对应。

---

*印证 Agent：fact-consistency / number-provenance / command-runnable / general-purpose(验证员,带 WebSearch)。本文件是五轮交叉验证第 3 轮结果，CONFIRMED 条目汇总进 `00-总览.md`。*
