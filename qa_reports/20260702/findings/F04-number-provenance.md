# F04 — 数字溯源审查报告

**审查范围**：全书 10 章 chapters/*/chapter.md
**审查方法**：Grep 全数字 + 逐章上下文确认 + WebSearch 核实
**审查日期**：2026-07-03
**审查人**：number-provenance agent

---

## 总览

扫出全书数字约 130 处。按严重度分类：
- 🔴 **核心论据裸数字（必须处理）**：2 处
- 🟠 **量级数字前提不足/可能过时**：12 处
- 🟢 **已带源/常识量级/格式细节（合格）**：>100 处

> **注**：InnoDB 16KB 页、Redis 16384 槽、Kafka 1GB 日志段等出厂默认参数视为常识量级，不要求逐条标注来源。

---

## 🔴 核心论据裸数字（无出处/数值有误/必须处理）

### 1. ch3:185 — fork 开销 "约 1-3 ms/GB"
- **原文**：`fork 拷贝页表约 1-3 ms/GB`
- **问题**：数值严重偏低且无出处。WebSearch 核实业界实测范围为约 10-20 ms/GB（x86_64, 4KB 页, PTE 拷贝主导）。VLDB 论文《Faster than Fork》给出 8GB 实例约 72ms、32GB 实例 PTE 拷贝约 60ms+。书中 "1-3 ms/GB" 比实测低 7-20 倍。
- **矛盾**：ch4:32 在同一问题上表述为 "小实例几十毫秒，大实例（几十GB以上）可达数百毫秒"——两处数字打架，ch4 更准确。
- **建议**：① 数值修正为 "约 10-20 ms/GB（4KB 页表, x86_64）" 或直接参考 ch4 改为量级描述；② 补充来源（antirez blog、VLDB 论文、Redis 官方文档）。

### 2. ch1:41 — Kafka "200 万次写入/秒" 引用背景模糊
- **原文**：`LinkedIn 公开基准里 3 台廉价机曾测到约 200 万次写入/秒`
- **问题**：虽有 "LinkedIn 公开基准" 出处，但未注明这是 2014 年 Jay Kreps 对 Kafka 0.8.1 的压测（消息 100 字节、6 台机器、1Gb 网络）。本书基线是 Kafka 3.x（约2023），中间跨了 10 年+5 个大版本。读者若认为这代表 3.x 性能，会严重高估当前版本基线。
- **建议**：加注 "该基准来自 2014 年 LinkedIn 工程博客（Kafka 0.8.1, 100 字节消息, 6 台机器），作为历史参考。3.x 在同类硬件上吞吐通常更高。"

---

## 🟠 量级数字前提不足/可能过时

### 3. ch6:24, 143 — Redis "单核十万级 QPS"（重复 2 处）
- **原文**：`Redis 的内核追求极简和单核十万级 QPS（小包 GET/SET 场景）`；`Redis 追求单核十万级 QPS（小包 GET/SET 场景）`
- **问题**：WebSearch 确认该量级准确（redis-benchmark 默认设置通常 100k-150k QPS），有 "小包 GET/SET 场景" 前提。但无具体来源。作为章节核心论据重复出现。
- **建议**：可加脚注引用 redis-benchmark 官方文档或社区基准，或明确范围 "通常 10-15 万 QPS（依硬件与并发度）"。

### 4. ch7:40 — Kafka "单分区吞吐：约 10-50MB/s"
- **原文**：`Kafka 单分区吞吐：约 10-50MB/s（视硬件与消息大小；1KB 消息约 1-5 万条/秒）`
- **问题**：前提已给（"视硬件与消息大小"），但 Confluent 官方建议通常说 "10s of MB/sec" 而非具体范围。无 Confluent/LinkedIn/社区基准来源。
- **建议**：加 "（Confluent 基准测试显示单分区可达数十 MB/s）" 或引用 Confluent 博客。

### 5. ch7:150 — Kafka "单分区约 10MB/s 或约 1 万条/秒"
- **原文**：`单分区在普通硬件上能跑到约 10MB/s 或约 1 万条/秒（均以约 1KB 消息估算；小于 100 字节消息可达 10 万条/秒以上。以实际压测为准）`
- **问题**：前提已明确（"约 1KB 消息估算"、"以实际压测为准"），但无 Confluent/LinkedIn 来源。作为 "经验值" 出现。
- **建议**：同 ch7:40，可补充 Confluent 来源链接。

### 6. ch8:46 — Redis RDB 压缩比 "300-500MB 快照（1GB 内存）"
- **原文**：`Redis RDB 压缩比：1GB 内存实例（字符串/列表型负载，典型场景）约 300-500MB 快照`
- **问题**：前提 "字符串/列表型负载" 已给。WebSearch 确认合理（内存到磁盘压缩比通常 0.4-0.7）。但无具体来源。注意压缩比高度依赖数据类型——纯整数 set 可低至 0.2，小字符串可能 0.8-1.0。
- **建议**：加 "（压缩比因数据类型而异，整数/已压缩数据接近上限，字符串/列表型负载近下限）"。

### 7. ch4:33 — 缓冲池命中率 "断崖下跌"
- **原文**：`命中率在工作集接近或超过缓冲池大小时断崖下跌`
- **问题**：该表述（及示例 "1TB 数据用 64GB 缓冲池"）是定性规则，无来源。虽为数据库常识，但作为关键数字框内容，建议增加引用。
- **建议**：加注 "（缓冲池命中率分析详见 MySQL 官方手册 'Optimizing InnoDB Disk I/O' 章节）"。

### 8. ch4:34 — "Linux 默认 vm.dirty_background_ratio=10%、vm.dirty_ratio=20%"
- **原文**：`Linux 默认 vm.dirty_background_ratio=10%、vm.dirty_ratio=20%`
- **问题**：数字准确（Red Hat 文档确认），但无来源。建议明确标注引用。
- **建议**：加 "（Linux 内核默认值，可通过 sysctl 确认）"。

### 9. ch8:44 — "约 15/16 存数据，1/16 存页头+目录"
- **原文**：`InnoDB 16KB 页：约 15/16 存数据，1/16 存页头+目录`
- **问题**：InnoDB 页元数据（FIL Header 38B + Page Header 56B + Infimum/Supremum 26B + Trailer 8B 约 128B）约占 16KB 的 0.78%，加上 Page Directory 也不到 6.25%。"1/16" 偏高但作为近似可用。建议加 "约" 或改为 "约 93% 用于数据"。
- **建议**：改为 "约 1/16 存元数据（页头+目录），其余约 15/16 存用户记录"。

### 10. ch4:189 — SSD 吞吐范围跨代标注建议
- **原文**：`SATA SSD 顺序写吞吐约 300 到 500MB/s，NVMe SSD 可达 2-14GB/s（随 PCIe 代际递增，Gen3 约 3GB/s、Gen4 约 5-7GB/s、Gen5 可达 10+GB/s）`
- **问题**：数值范围合理且已按代际分述，是本书处理最完善的跨代数字。但 Gen5 上限可超 14GB/s（2025+ 产品）。建议注明 "2024 年典型值"。
- **建议**：加 "（以上为 2024 年消费级/企业级 SSD 典型值，具体以厂商规格为准）"。

### 11. ch4:313 — "缓冲池命中率掉到 95% 以下"
- **原文**：`MySQL 的缓冲池命中率掉到 95% 以下`
- **问题**：95% 是常见阈值经验值，未注明来源。
- **建议**：加 "（MySQL 官方建议缓冲池命中率保持 99% 以上，低于 95% 表明需扩容）"。

### 12. ch7:39 — "跨 AZ 部署时每笔事务要多约 5-10ms"
- **原文**：`跨 AZ 部署时每笔事务要多约 5-10ms（同城 AZ 典型 RTT 2-5ms；MGR 的 Paxos 共识需多轮往返，实际增加延迟为 RTT 的 2-3 倍）`
- **问题**：前提（RTT 2-5ms, Paxos 2-3 轮）已给，逻辑自洽。但无来源引用。
- **建议**：可加 "（按云厂商同城 AZ 典型 RTT 估算）"。

---

## 🟢 已带源/常识量级/格式细节（合格）

### 常识量级（不需要出处）
| 位置 | 数字 | 原因 |
|------|------|------|
| ch2:50 | "纳秒级/微秒到毫秒级" 差三到五个数量级 | 硬件层次常识 |
| ch4:21-26 | 存储层次延迟表（L1约1ns, DRAM约100ns, SSD约100us, HDD约10ms） | 行业标准数字 |
| ch4:28 | "1秒/17分钟/28小时" 体感类比 | 从延迟表推算的示例 |
| ch6:145 | "TLS 吞吐降至六到八成" | 定性描述，加注了"以实测为准" |
| ch8:62 | "4字节版本号/6位14位32位编码" | RDB 格式细节 |
| ch8:70 | "8字节 CRC64" | RDB 格式细节 |
| ch8:113 | "64连续页组成区（1MB）" | InnoDB 格式常识 |
| ch8:140 | "512字节块对齐" | MySQL 重做日志格式常识 |
| ch8:164 | "8字节/12字节" 索引条目 | Kafka 格式细节 |

### 已带源/参数名引用
| 位置 | 数字 | 来源 |
|------|------|------|
| ch3:183 | "默认 30 秒" K8s grace period | K8s 文档 |
| ch4:96 | "每秒 fsync 一次" everysec | Redis 配置默认值 |
| ch4:153 | "innodb_flush_log_at_trx_commit=1" | MySQL 配置默认值 |
| ch4:191 | "日志段默认 1GB" | Kafka log.segment.bytes 默认值 |
| ch4:228 | "默认每 4KB 落一个索引条目" | Kafka log.index.interval.bytes 默认值 |
| ch7:38 | "16384 个槽" / "2KB bitmap" | Redis Cluster 设计决策 + 算术 |
| ch7:38 | "官方建议不超过 1,000" | 明确标注为官方建议 |
| ch8:119 | "innodb_page_size 可配 4K/8K/16K/32K/64K" | MySQL 配置参数 |
| ch8:166 | "log.segment.bytes=1GB / log.roll.hours=7天" | Kafka 配置默认值 |
| ch8:184 | "log.index.interval.bytes 默认每 4KB" | Kafka 配置默认值 |
| ch9:37 | "PSYNC backlog 默认 1MB" | Redis repl-backlog-size 默认值 |
| ch9:38 | "rpl_semi_sync_source_timeout 默认 10 秒" | MySQL 配置默认值 |
| ch9:39 | "replica.lag.time.max.ms 默认 30 秒" | Kafka 配置默认值 |
| ch9:147 | "rpl_semi_sync_source_wait_for_replica_count 默认 1" | MySQL 配置默认值 |

---

## 矛盾/不一致数字

### ch3:185 与 ch4:32 — fork 开销数字打架
- **ch3:185**：`fork 拷贝页表约 1-3 ms/GB`——数值偏低
- **ch4:32**：`小实例几十毫秒，大实例（几十 GB 以上）可达数百毫秒`——更准确
- **实际范围**（WebSearch 核实）：4KB 页表下约 10-20 ms/GB
- **建议**：统一为 ch4 表述或引用 VLDB/社区基准

---

## WebSearch 核实结果摘要

| 数字 | 书中值 | 业界范围 | 可靠性判断 |
|------|--------|----------|-----------|
| fork 开销 | 1-3 ms/GB | 10-20 ms/GB | **错误**，偏离 7-20 倍 |
| Redis 单核 QPS | 十万级 | 100k-150k (redis-benchmark) | 准确 |
| Kafka 单分区吞吐 | 10-50MB/s | Confluent: "10s of MB/sec" | 合理 |
| RDB 压缩比 | 1GB->300-500MB | 0.4-0.7 倍常见 | 合理（依赖数据类型） |
| Linux dirty_ratio | 10%/20% | 确认为内核默认 | 准确 |
| buffer pool 典型值 | 8-128GB | 50-75% of RAM 推荐 | 合理 |
| LinkedIn Kafka 基准 | 200 万 TPS | 确认为 2014 年实测 | 历史准确，需注版本 |

**WebSearch 来源：**
- VLDB 论文 2023: `https://www.vldb.org/pvldb/vol16/p1033-chen.pdf`
- antirez blog: `https://antirez.com/news/84`
- Confluent partition sizing: `https://www.confluent.io/blog/how-choose-number-topics-partitions-kafka-cluster/`
- LinkedIn benchmark: `https://engineering.linkedin.com/kafka/benchmarking-apache-kafka-2-million-writes-second-three-cheap-machines`
- redis-benchmark 实测: 腾讯云/Arm GCP/OneUptime 多家结果
- Red Hat Linux VM 参数: `https://docs.redhat.com/zh-cn/documentation/red_hat_enterprise_linux/10/html/monitoring_and_managing_system_status_and_performance/virtual-memory-parameters`

---

## 修复优先级建议

### 紧急（数字错误，影响读者判断）
1. **ch3:185** — fork 开销数值修正 + 来源补充

### 重要（核心论据数字，缺出处）
2. **ch1:41** — Kafka 200 万 TPS 补充版本/年代背景
3. **ch6:24 + ch6:143** — "单核十万级 QPS" 补充来源或收敛为量级表述
4. **ch7:40 + ch7:150** — Kafka 单分区吞吐补充 Confluent 来源
5. **ch8:46** — RDB 压缩比补充数据类型依赖说明

### 中等（引用补强）
6. **ch4:33** — 缓冲池 "断崖" 补充 MySQL 手册引用
7. **ch4:34** — dirty_ratio 补充内核文档引用
8. **ch4:313** — 95% 阈值补充 MySQL 建议引用
9. **ch7:39** — 跨 AZ 延迟补充声明
10. **ch8:44** — 页内比例微调
11. **ch4:189** — SSD 吞吐注明年份
