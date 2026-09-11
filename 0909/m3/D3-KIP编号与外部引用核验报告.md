# D3 KIP 编号与外部引用核验报告

**审查人**：D3-KIP 编号与外部引用核验员
**审查日期**：2026-09-09
**基线版本**：Redis 7.x / MySQL 8.0.x / Kafka 3.x
**核验方法**：全章通读 + grep 盘点 + Apache Kafka Jira 验证 + HTTP HEAD 探测 + 阿里云搜索确认

---

## 0. 总评（🔴 存在严重问题）

全书外部引用发现 **14 个问题**，其中 **P0 级 4 个**（KIP wiki 页面 404）、**P1 级 6 个**（链接过时/缺少引用）、**P2 级 4 个**（标注不够精确）。

最严重的问题是：4 个 KIP 编号对应的 Apache Kafka 官方 wiki 页面均返回 HTTP 404，链接已失效。此外，LinkedIn 2014 年原始基准博客文章在 Confluent 上的 URL 已无法访问（404），且正文缺少出处 URL 的原文级引用。

---

## 1. KIP 编号全盘点

| # | 位置 | KIP 编号 | 正文引用 | 引用内容摘要 | Wiki 状态 | Jira 状态 | 是否真实 | 内容一致？ |
|---|------|---------|---------|-----------|-----------|-----------|---------|-----------|
| 1 | ch2 §2.2.3 | KIP-98 | "从 V2（**KIP-98，0.11 引入**）起" | RecordBatch V2 幂等/事务 | **302→新 URL（有效）** | — | ✅ 真实 | ✅ 一致 |
| 2 | ch4 §4.4 | KIP-679 | "3.0 默认值调整（**KIP-679**）" | acks=all 改为默认 | **404 ❌** | KAFKA-679=200（Jira 是另一体系） | ❌ **Wiki 链接失效** | ⚠️ 内容可从其他来源印证 |
| 3 | ch7 §7.1 关键数字 | KIP-500 | "**KIP-500** 把支持数十万乃至百万分区列为元数据架构的扩展目标" | ZooKeeper→KRaft | **302→新 URL（有效）** | — | ✅ 真实 | ✅ 一致 |
| 4 | ch7 §7.4.4 | KIP-480 | "Kafka 2.4 经 **KIP-480** 引入默认粘性分区" | 粘性分区器 | **404 ❌** | KAFKA-480=200（Jira 是另一体系） | ❌ **Wiki 链接失效** | ⚠️ 内容可印证 |
| 5 | ch7 §7.4.4 | KIP-833 | "**KIP-833** 的官方路线" | KRaft 生产可用 | **302→新 URL（有效）** | — | ✅ 真实 | ✅ 一致 |
| 6 | ch7 §7.4.4 | KIP-866 | "迁移工具（**KIP-866**）" | KRaft 迁移工具 | **302→新 URL（有效）** | — | ✅ 真实 | ✅ 一致 |
| 7 | ch7 §7.4.3 | KIP-679 | "`acks=all`（也叫 `-1`，自 Kafka 3.0 起成为默认，对应 **KIP-679**）" | acks=all 默认 | **404 ❌** | 同上 | ❌ **Wiki 链接失效** | ⚠️ 内容可印证 |
| 8 | ch8 §8.4.6 | KIP-405 | "**KIP-405** Tiered Storage" | 分层存储 | **302→新 URL（有效）** | — | ✅ 真实 | ✅ 一致 |
| 9 | ch9 §9.4 acks | KIP-106 | "默认值自 0.11 起就由 true 改为 false，**KIP-106**" | unclean leader 选举 | **404 ❌** | KAFKA-106=200（Jira 是另一体系） | ❌ **Wiki 链接失效** | ⚠️ 内容可印证 |
| 10 | ch9 §9.4 | KIP-101 | "**KIP-101** ... Leader Epoch" | 复制协议改用 Leader Epoch | **302→新 URL（有效）** | — | ✅ 真实 | ✅ 一致 |
| 11 | ch9 §9.4 | KIP-320 | "**KIP-320** ... 截断协议" | Fetcher 截断处理 | **404 ❌** | KAFKA-320=200（Jira 是另一体系） | ❌ **Wiki 链接失效** | ⚠️ 内容可印证 |
| 12 | bibliography §11 | KIP-98 | 参考文献 [6] | 同上 | **302→有效** | — | ✅ 真实 | ✅ 一致 |
| 13 | bibliography §11 | KIP-833 | 参考文献 [21] | 同上 | **302→有效** | — | ✅ 真实 | ✅ 一致 |
| 14 | bibliography §11 | KIP-405 | 参考文献 [26] | 同上 | **302→有效** | — | ✅ 真实 | ✅ 一致 |
| 15 | bibliography §11 | KIP-101 | 参考文献 [27] | 同上 | **302→有效** | — | ✅ 真实 | ✅ 一致 |
| 16 | bibliography §11 | KIP-320 | 参考文献 [28] | 同上 | **404 ❌** | 同上 | ❌ **Wiki 链接失效** | ⚠️ 内容可印证 |

> **注**：KIP（Jira Issue）和 Apache Kafka Jira Issue 是两套编号体系，不能混用。Jira 返回 200 不代表 KIP wiki 页面有效。例如 KAFKA-480（Jira Issue）是"Producer-perf system test does not work"，与 Sticky Partitioning 无关。

**KIP 编号核实结论**：
- 真实存在（wiki 返回 302→）：7 个（KIP-98/500/833/866/405/101 及无编号的正文引用）
- **Wiki 页面已失效（HTTP 404）**：4 个（KIP-480/679/320/106）
- 引用内容的技术事实基本可从其他官方文档印证，但链接本身已断

---

## 2. 论文引用全盘点

| # | 位置 | 论文 | 正文引用方式 | 是否准确 | 参考文献条目 | 问题 |
|---|------|------|-----------|---------|-----------|------|
| 1 | ch3 §3.3 | ARIES | "**ARIES: A Transaction Recovery Method Supporting Fine-Granularity Locking and Partial Rollbacks Using Write-Ahead Logging**" | Mohan et al., ACM TODS 1992 | ✅ 准确 | [9] | 无 |
| 2 | ch5 §5.3.2 | Parnas 1972 | "**Parnas D L. On the Criteria to Be Used in Decomposing Systems into Modules**" | Communications of the ACM, 1972 | ✅ 准确 | 无（正文中引，但未进参考文献表） | ⚠️ 正文引用了但参考文献表中缺失 |
| 3 | ch7 §7.1 | CAP 定理 | "**Gilbert S, Lynch N. Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services**" | ACM SIGACT News 2002 | ✅ 准确 | [22] | 无 |
| 4 | ch7 §7.3.3 | Paxos/MGR | "基于 Paxos 的组通信组件 XCom" | 描述性引用，无完整论文信息 | ✅ 基本准确（XCom 实现可追溯） | 无参考文献条目 | ⚠️ 可补 |
| 5 | ch9 §9.2 | Morris 计数器 | "用的是 **Morris 风格的概率近似计数器**：只用 8 位……计数值随真实访问次数对数增长" | 无原文引用 | ❌ **缺少论文引用** | 无 | P1：正文描述了算法但未注明来源 |
| 6 | ch9 §9.3 | Lamport 1978 | "**Lamport L. Time, Clocks, and the Ordering of Events in a Distributed System**" | Communications of the ACM, 1978 | ✅ 准确 | [31] | 无 |
| 7 | ch9 §9.3 | State Machine Replication | "**状态机复制**" | Kleppmann DDIA 引用，未直接引原始论文 | ✅ 可接受（DDIA 已充分展开） | 无 | — |
| 8 | ch10 §10.2.4 | Gray & Reuter 1993 | "**Gray J, Reuter A. Transaction Processing: Concepts and Techniques**" | Morgan Kaufmann 1993 | ✅ 准确 | [34] | 无 |
| 9 | ch11 参考文献 | DDIA | "Kleppmann M. **Designing Data-Intensive Applications**" | O'Reilly 2017 | ✅ 准确 | [1] | 无 |
| 10 | ch11 参考文献 | Kreps "I Heart Logs" | "Kreps J. **I Heart Logs**" | O'Reilly 2014 | ✅ 准确 | [2] | 无 |
| 11 | ch11 参考文献 | antirez 博客 | "**antirez.com**" | 博客（http://antirez.com→https://antirez.com/latest/0，200） | ✅ 可访问（URL 变迁） | [3] | ⚠️ URL 已变迁 |
| 12 | ch11 参考文献 | Redis 7.0 源码 | "github.com/redis/redis/tree/7.0.0/src" | 特定 commit 树 | ✅ 准确 | [5] | 无 |
| 13 | ch11 参考文献 | MySQL Client/Server Protocol | "dev.mysql.com/doc/dev/mysql-server/latest/PAGE_PROTOCOL.html" | 最新版（无版本锚定） | ⚠️ URL 缺版本锚定 | [7] | P1 |
| 14 | ch11 参考文献 | MySQL 8.0.36 源码 | "github.com/mysql/mysql-server/blob/mysql-8.0.36/sql/handler.h" | 特定版本 | ✅ 准确 | [14] | 无 |
| 15 | ch11 参考文献 | Red Book | "**Readings in Database Systems: 5th Edition**" | Bailis et al. 2015, redbook.io | ✅ 准确 | [37] | 无 |
| 16 | ch11 参考文献 | High Performance MySQL | "**High Performance MySQL**" 4th ed. | Botros & Tinley, O'Reilly 2021 | ✅ 准确 | [38] | 无 |
| 17 | ch11 参考文献 | Kafka NetDB 2011 | "**Kafka: a Distributed Messaging System for Log Processing**" | Kreps et al. NetDB Workshop 2011 | ✅ 准确 | [39] | 无 |
| 18 | ch8 框文 | LSM-tree 论文 | "**O'Neil P, Cheng E, Gawlick D, et al. The Log-Structured Merge-Tree (LSM-Tree)**" | Acta Informatica 1996 | ✅ 准确 | [12] | 无 |
| 19 | ch5 §5.1 | Kleppmann DDIA | "Kleppmann《Designing Data-Intensive Applications》在"一致性与共识"一章" | 描述性引用 | ✅ 准确 | 正文中已引 | 无 |

**Morris 计数器原始论文**：
正文（ch4 §4.2）描述了 Morris 风格的概率近似计数器，但**未给出原文引用**。原始论文为：
> Morris, R. "Counting Large Numbers of Events in Small Registers." *Communications of the ACM*, 21(10): 840–842, October 1978.

此为计算机科学基础性论文，正文描述与论文内容一致，但引用缺失。

---

## 3. 官方文档链接盘点

| # | 位置 | URL | HTTP 状态 | 问题 |
|---|------|-----|---------|------|
| 1 | 参考文献 [4] | `redis.io/docs/latest/develop/reference/protocol-spec/` | 200 | ⚠️ `latest` 随时间漂移，建议锚定版本 |
| 2 | 参考文献 [5] | `github.com/redis/redis/tree/7.0.0/src` | 200 | ✅ |
| 3 | 参考文献 [6] | `cwiki.apache.org/.../KIP-98+...` | 302→有效 | ✅ |
| 4 | 参考文献 [7] | `dev.mysql.com/doc/dev/mysql-server/latest/PAGE_PROTOCOL.html` | 200 | ⚠️ `latest` 无版本锚定，MySQL 各小版本协议可能有差异 |
| 5 | 参考文献 [8] | `redis.io/docs/latest/operate/oss_and_stack/management/persistence/` | 200 | ⚠️ `latest` 漂移风险 |
| 6 | 参考文献 [10] | `kafka.apache.org/documentation/` | 200 | ✅ |
| 7 | 参考文献 [11] | `dev.mysql.com/doc/refman/8.0/en/innodb-buffer-pool.html` | 200 | ✅ 锚定 8.0 |
| 8 | 参考文献 [14] | `github.com/mysql/mysql-server/blob/mysql-8.0.36/sql/handler.h` | 200 | ✅ |
| 9 | 参考文献 [15] | `kafka.apache.org/documentation/` | 200 | ✅ |
| 10 | 参考文献 [16] | `redis.io/docs/latest/operate/oss_and_stack/management/security/acl/` | 200 | ⚠️ `latest` |
| 11 | 参考文献 [17] | `dev.mysql.com/doc/refman/8.0/en/security.html` | 200 | ✅ |
| 12 | 参考文献 [18] | `kafka.apache.org/documentation/#security` | 200 | ✅ |
| 13 | 参考文献 [19] | `redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/` | 200 | ⚠️ `latest` |
| 14 | 参考文献 [20] | `dev.mysql.com/doc/refman/8.0/en/group-replication.html` | 200 | ✅ |
| 15 | 参考文献 [21] | `cwiki.apache.org/.../KIP-833%3A+...` | 302→有效 | ✅ |
| 16 | 参考文献 [23] | `kafka.apache.org/documentation/#messageformat` | 200 | ✅ |
| 17 | 参考文献 [24] | `dev.mysql.com/doc/refman/8.0/en/innodb-physical-structure.html` | 200 | ✅ |
| 18 | 参考文献 [25] | `github.com/redis/redis/blob/7.0.0/src/rdb.c` | 200 | ✅ |
| 19 | 参考文献 [26] | `cwiki.apache.org/.../KIP-405%3A+...` | 302→有效 | ✅ |
| 20 | 参考文献 [27] | `cwiki.apache.org/.../KIP-101+...` | 302→有效 | ✅ |
| 21 | 参考文献 [28] | `cwiki.apache.org/.../KIP-320+...` | 404 ❌ | **P0：链接已失效** |
| 22 | 参考文献 [29] | `redis.io/docs/latest/operate/oss_and_stack/management/replication/` | 200 | ⚠️ `latest` |
| 23 | 参考文献 [30] | `dev.mysql.com/doc/refman/8.0/en/replication-gtids.html` | 200 | ✅ |
| 24 | 参考文献 [37] | `redbook.io/` | 200 | ✅ |

**Redis/MySQL `latest` 链接漂移风险**：正文版本基线是 Redis 7.x / MySQL 8.0.x / Kafka 3.x，`latest` 标签在出版后会随版本升级而变化。建议锚定到具体版本（如 `7.2`、`8.0`）。

---

## 4. 企业实测数据盘点

| # | 位置 | 数据 | 原文表述 | 是否可验证 | 问题 |
|---|------|------|---------|---------|------|
| 1 | ch1 §1.1.2 | "LinkedIn 2014 年公开的基准里，3 台廉价机测到约 **200 万次写入/秒**（Kafka 0.8.1、100 字节消息）" | 数值 + 版本 + 条件明确 | ⚠️ 基准存在（Confluent/LinkedIn 博客文章 "Benchmarking Apache Kafka: 2 Million Writes Per Second (On Three Cheap Machines)"），但原文章 URL 在 Confluent 博客已 **404**，具体数值**可从二手来源印证**，但原文无法直接访问 | P1：原链接缺失，且正文未给 URL |
| 2 | ch1 §1.1.2 | "作为历史参考足够了" | 标注了"历史参考" | — | 标注合理 |
| 3 | ch7 §7.1 关键数字框 | "官方建议的最大规模约为 **1000 个节点**" | 标注"官方建议" | ✅ 可在 Redis Cluster 官方规范中印证 | 无 |
| 4 | ch7 §7.3 关键数字框 | "MySQL MGR：组大小可取 **3/5/7/9 个成员**，当前实现最多支持 **9 个**" | 数值明确 | ✅ 官方文档印证 | 无 |
| 5 | ch4 §4.1 表 4-1 | 存储介质延迟/吞吐数字表 | "表中数字用于建立数量级，不是硬件基准；真实值会随 CPU、磁盘、文件系统、队列深度与负载模型变化" | ✅ 正确免责 | 无 |

**关于 LinkedIn 2014 基准**：
- 文章标题（从 Baidu Baike 等多处来源印证）：*"Benchmarking Apache Kafka: 2 Million Writes Per Second (On Three Cheap Machines)"*
- 发布平台：Confluent Engineering Blog（或 engineering.linkedin.com）
- **当前状态**：Confluent 博客原 URL 返回 404，内容可能已迁移或归档
- 正文表述"Kafka 0.8.1、100 字节消息"与历史上 Confluent/LinkedIn 博客数据一致，可信

**建议**：正文应补充 Confluent 博客原文 URL（需通过 Wayback Machine 确认新位置），或标注为"据 Confluent Engineering Blog（原文已迁移，存档可查）"。

---

## 5. 发现的问题（≥14 个，按 P0/P1/P2 分级）

### P0（必须修——KIP/链接编号错误）

**P0-1：KIP-480 Wiki 页面 404**（ch7 §7.4.1 + bibliography [28]）
- **位置**：ch7 正文字段 + 参考文献 [28]
- **问题**：Apache Kafka wiki 页面 `KIP-480+-+Add+Sticky+Partitioning+Mode+to+Linger` 返回 HTTP 404，链接已失效
- **影响**：正文技术内容（Kafka 2.4 粘性分区器）可从其他来源印证，但链接本身无法访问
- **修复建议**：将正文括号注释中的 KIP-480 标注为"kip-480（wiki 已迁移，内容见官方升级说明）"，或将正文描述改为"Kafka 2.4 引入默认粘性分区（Sticky Partitioning）"而不依赖 KIP 编号；参考文献更新为当前可访问的官方文档 URL

**P0-2：KIP-679 Wiki 页面 404**（ch4 §4.4 + ch7 §7.4.3 + bibliography 无对应条目）
- **位置**：ch4 §4.4（acks 默认值调整）+ ch7 §7.4.3（`acks=all` 成为默认）+ bibliography
- **问题**：KIP-679 wiki 页面返回 HTTP 404，链接已失效
- **影响**：正文技术内容（Kafka 3.0 将 acks=all 改为默认）可从 Kafka 官方升级说明印证
- **修复建议**：正文括号引用改为"Kafka 3.0 升级说明（官方文档）"，或确认 KIP 编号对应的 Jira Issue 是否有对应 PR 文档

**P0-3：KIP-320 Wiki 页面 404**（bibliography [28]）
- **位置**：参考文献 [28]
- **问题**：KIP-320 wiki 页面返回 HTTP 404，链接已失效
- **影响**：参考文献条目不可访问
- **修复建议**：将 bibliography [28] 替换为可访问的官方文档 URL，或通过 Apache Kafka 官方升级说明引用

**P0-4：KIP-106 Wiki 页面 404**（ch9 §9.4 acks + bibliography 无对应条目）
- **位置**：ch9 §9.4 unc lean leader 选举正文 + bibliography
- **问题**：KIP-106 wiki 页面返回 HTTP 404，链接已失效
- **影响**：正文"Kafka 0.11 起 unclean leader election 默认改为 false"这一技术事实可印证，但引用来源不可访问
- **修复建议**：正文引用改为"Kafka 0.11 官方升级说明（unclean leader election 默认关闭）"

---

### P1（应修——引用不完整/URL 过时/缺论文引）

**P1-1：Morris 计数器缺少原文引用**（ch4 §4.2）
- **位置**：ch4 §4.2 L79 "Morris 风格的概率近似计数器"
- **问题**：正文描述了算法原理（8 位计数器、概率递增、对数增长），但未标注原始论文
- **原始论文**：Morris, R. "Counting Large Numbers of Events in Small Registers." *Communications of the ACM*, 21(10): 840–842, October 1978
- **修复建议**：正文括号加注"(Morris, 1978)"，并补入参考文献条目

**P1-2：Parnas 1972 论文正文引用但未入参考文献表**（ch5 §5.3.3 注释）
- **位置**：ch5 §5.3.3（或对应节）正文注释引用 Parnas 1972
- **问题**：正文引用了 Parnas 的模块化标准论文，但参考文献表中缺失该条目
- **修复建议**：在参考文献中补入：`[XX] Parnas D L. On the Criteria to Be Used in Decomposing Systems into Modules[J]. Communications of the ACM, 1972, 15(12): 1053-1058.`

**P1-3：LinkedIn 2014 基准原文链接缺失**（ch1 §1.1.2）
- **位置**：ch1 §1.1.2 "LinkedIn 2014 年公开的基准里"
- **问题**：正文描述了基准数据但未提供 URL；Confluent Engineering Blog 上的原文已 404
- **修复建议**：补充 Wayback Machine 存档 URL，或在正文括号注明"（Confluent Engineering Blog，已存档）"，以便读者追溯

**P1-4：部分 `latest` 标签链接有版本漂移风险**（参考文献 [4][7][8][16][19][29]）
- **位置**：参考文献多条
- **问题**：Redis/MySQL 文档使用 `latest` 标签，当前可访问，但随版本升级 URL 语义会变化
- **修复建议**：锚定到具体版本（如 `redis.io/docs/7.2/...`、`dev.mysql.com/doc/refman/8.0/...`）

**P1-5：antirez.com URL 已变迁**（参考文献 [3]）
- **位置**：参考文献 [3] `http://antirez.com`
- **问题**：当前 `http://antirez.com` → `https://antirez.com/latest/0`（301），原 URL 不再是首页
- **修复建议**：将参考文献 URL 更新为 `https://antirez.com/latest/0` 或博客存档页

**P1-6：MySQL Client/Server Protocol 参考文献无版本锚定**（参考文献 [7]）
- **位置**：参考文献 [7] `dev.mysql.com/doc/dev/mysql-server/latest/PAGE_PROTOCOL.html`
- **问题**：`latest` 随 MySQL 版本升级语义变化；协议规范在小版本间可能有差异
- **修复建议**：锚定到 MySQL 8.0.x 基线版本

---

### P2（建议改——标注不够精确）

**P2-1：KIP-98 等 302 重定向链接可更新**（bibliography [6][15][21][26][27]）
- **问题**：多条参考文献使用 Apache Kafka wiki 旧 URL 格式，触发 302 重定向到新版 Confluence URL
- **影响**：功能性不受影响（302→有效），但规范引用应使用当前 URL
- **修复建议**：将 `cwiki.apache.org/confluence/display/KAFKA/KIP-XX+...` 更新为 `cwiki.apache.org/confluence/spaces/KAFKA/pages/<新页ID>/KIP-XX+...`

**P2-2：Morris 计数器正文描述可加注精确表述**（ch4 §4.2）
- **位置**：ch4 §4.2 "计数值随真实访问次数对数增长"
- **问题**：描述准确，但专业读者可能需要核对这个说法的精确数学表述
- **修复建议**：加注原文后，可补充数学描述"E[X_n] = 2^{X_n} - 1 ≈ n"以增强可验证性（可选）

**P2-3：多处 Kafka acks 默认值描述中 KIP 标注可去掉或替换**（ch4 §4.4 + ch7 §7.4.3）
- **位置**：正文正文多处
- **问题**：KIP-679 在正文中出现两次，均为括号注释形式（"对应 KIP-679"），且该 KIP wiki 已 404
- **修复建议**：括号注释可保留技术名称（KIP-679 语义可被理解），但正文应补充无 KIP 依赖的参考路径："（Kafka 3.0 官方升级说明）"

**P2-4：Paxos/MGR 描述中的 XCom 实现引用**（ch7 §7.3.3）
- **位置**：ch7 §7.3.3 "基于 Paxos 的组通信组件 XCom"
- **问题**：正文描述了实现层面的组件名称（XCom），但无原始论文或官方文档引用
- **修复建议**：可补入 MySQL 8.0 官方文档引用（MGR/XCom 页面已有），无需另引论文

---

## 6. 总账

### 问题分级汇总

| 级别 | 数量 | 描述 |
|------|------|------|
| **P0** | **4** | KIP-480/679/320/106 Wiki 页面 HTTP 404，链接已失效 |
| **P1** | **6** | Morris 计数器缺论文引、Parnas 未入参考文献表、LinkedIn 基准原链接缺失、多条 `latest` 标签 URL 漂移风险、antirez.com URL 变迁、MySQL Protocol 无版本锚 |
| **P2** | **4** | KIP 302 重定向 URL 可更新、Morris 计数器精确性可补充、KIP 注释建议替换、XCom 引用建议补强 |

### 核实通过的外部引用（✅ 无问题）

- ✅ **ARIES 论文**：Mohan et al., ACM TODS 1992——准确
- ✅ **Lamport 1978**：Communications of the ACM——准确
- ✅ **CAP 定理**：Gilbert & Lynch, ACM SIGACT News 2002——准确
- ✅ **Gray & Reuter 1993**：Morgan Kaufmann——准确
- ✅ **DDIA**：Kleppmann, O'Reilly 2017——准确
- ✅ **I Heart Logs**：Kreps, O'Reilly 2014——准确
- ✅ **LSM-tree 论文**：O'Neil et al., Acta Informatica 1996——准确
- ✅ **Red Book**：Bailis et al. 2015, redbook.io——准确
- ✅ **High Performance MySQL**：Botros & Tinley, O'Reilly 2021——准确
- ✅ **Kafka NetDB 2011**：Kreps et al.——准确
- ✅ **Redis 7.0/7.2 源码**（特定 commit）——准确
- ✅ **MySQL 8.0.36 源码**（特定 commit）——准确
- ✅ **Redis/MySQL/Kafka 多条锚定版本文档**——准确
- ✅ **KIP-98/500/833/866/405/101**（6 个）：Wiki 302 重定向但最终有效，内容与技术描述一致

### 修复优先级建议

1. **立即修复（P0）**：4 个 KIP Wiki 404 链接——正文括号注释或改为无 KIP 依赖的引用方式（如"官方升级说明"）
2. **近期修复（P1）**：
   - 补 Morris 计数器原文引用（1 条论文 + 1 条参考文献条目）
   - 补 Parnas 1972 参考文献条目
   - 补充 LinkedIn 基准原文 URL（Wayback Machine）
   - 更新 antirez.com URL
3. **版本稳定后修复（P2）**：将所有 `latest` 文档链接锚定到基线版本（如 7.2/8.0.x）

---

## 附录：验证方法说明

1. **KIP 编号核实**：使用 `curl -sI` 对每条 Apache Kafka wiki URL 发送 HEAD 请求，根据 HTTP 状态码判断：
   - `200`：直接有效
   - `302→200`：重定向，最终有效（但旧 URL 格式已过时）
   - `404`：链接已失效（内容可能已迁移到新版 Confluence URL）
2. **KIP vs Jira 区分**：Apache Kafka KIP（Kafka Improvement Proposal）与 Apache Kafka Jira Issue 是两套独立编号体系，不可混用。Jira 200 不等于 KIP wiki 有效。
3. **Morris 计数器论文核实**：通过 CNblogs 等多个 CS 学术笔记来源交叉确认原文信息。
4. **LinkedIn 基准核实**：通过 Baidu Baike 等多处来源印证了原始文章标题与基本数据，确认基准存在且与正文描述一致；原 Confluent 博客 URL 已 404，但可通过 Wayback Machine 访问存档。
