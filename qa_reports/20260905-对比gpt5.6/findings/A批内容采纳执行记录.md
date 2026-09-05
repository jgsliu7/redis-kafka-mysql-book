# A 批内容资产采纳执行记录（A1/A2/A4/A7/A10 五条）

> 日期：2026-09-05 | 执行：总调度（单人 Edit，逐处精准替换）
> 前置：用户圈选"按你的建议来"＝A 批五条内容资产（编号沿用《内容资产与结构装置盘点.md》A 表）＋构建三件套（B2/B3/B8，另见构建轮）。
> 流程：总调度草拟插入文本 → voice-consistency 语域票（5/5 过，附 3 处必改）→ source-contributor 事实票（带一手信源，A1–A4 同意、A5 修改后同意并揪出 1 条既有错误连带必改）→ 两票合并执行 → 改后双 agent 复验。

## 一、两票结论摘要

| 票 | 结论 | 必改/连带 |
|----|------|----------|
| voice-consistency | 5/5 过（语域、第一人称、体例均合格） | A1"这笔处理"→"这条记录的处理"；A4 MiB→MB；A5 弯引号→直引号 |
| source-contributor（一手信源：MySQL §17.18.2 + mysql-server 8.0 srv0start.cc/trx0roll.cc、Kafka javadoc 3.3 + cwiki FAQ、K8s 官方 Pod Lifecycle） | A1/A3/A4 同意；A2 同意＋可选微调；A5 修改后同意 | **连带必改**：ch3 L186"避免 K8s 反复重启"系既有事实错误（readiness 从不管重启），不修则与 A5 新段同页自相矛盾 |

可选微调采纳情况：
- A2"落点就跟着变"全称读法 → 采纳事实票替换（"落点跟着重算……同一个 key 的新旧消息可能就此分在两个分区"），属引入文本的精度修正。
- A4"有效处理速率"歧义 → 不采（不等式 C>W 自身消解读，事实票也判"不改不构成事实错误"）。
- A3 锚句"启动期的 undo 回滚会非常慢" → 维持原文（事实票倾向最小 diff：插入段是顺承限定而非矛盾）。

## 二、执行的 6 处 diff

| # | 文件 | 位置 | 改动 |
|---|------|------|------|
| 1 | 09-data-sync/chapter.md | §9.4 末（"操作语义一致"段后） | 新增段：事务可纳消费 offset 进提交单元、纳不了外部系统处理结果；三个进度（读取位置/已提交 offset/业务处理结果）；前缀提交纪律（越过未完成记录提交→重启跳过）；"我写消费者默认按分区顺序处理完再提交，拿消费并行度换这条规则自动成立" |
| 2 | 09-data-sync/chapter.md | §9.2（backlog 调参段后） | 新增段：追赶预算 B/(C−W)；C>W 才有净追赶能力；120MB÷2MB/s≈一分钟例算；与 9.1 关键数字框"覆盖时长"分工（数据还在不在 vs 追不追得上，两个预算分开算） |
| 3 | 07-cluster/chapter.md | §7.4.1 L156 句中 | "保证同一个 key 永远去同一个分区"→"N 不变时，同一个 key 总是落在同一个分区"（消除绝对化，为段尾扩分区段留口） |
| 4 | 07-cluster/chapter.md | §7.4.1 L156 段尾 | 追加：N 变则落点重算；扩分区旧消息不迁移、同 key 新旧消息可能跨分区、按键顺序失保证；依赖按键顺序的业务扩分区是语义迁移，按数据迁移规划（官方 FAQ 背书：补救=全量重写新主题） |
| 5 | 03-lifecycle/chapter.md | §3.3（"拆小"段后） | 新增段：崩溃恢复后台回滚线程不挡对外就绪；新事务可能遇回滚中记录的锁；ready for connections 之后仍有收尾，业务延迟未回正常水位 |
| 6 | 03-lifecycle/chapter.md | §3.4（Kafka 段后、实践清单前）＋L186 | 新增 K8s 三类探针段（startup 抑制另两类/liveness 重启/readiness 只摘流量；"把恢复期当存活失败"亲历案例）；**连带修正清单句**："readiness 返回 false，避免 K8s 反复重启"→"readiness 返回 false 先摘流量；重启与否由 liveness 判定，与 readiness 无关" |

## 三、事实票信源（均实际拉取核对原文）

- A1：KafkaProducer.sendOffsetsToTransaction javadoc（"marks those offsets as part of the current transaction"）；KafkaConsumer.commitSync javadoc（"committed offset should be… lastProcessedMessageOffset + 1"；"will be used on the first fetch after every rebalance and also on startup"）。
- A2：Kafka 官方 FAQ（cwiki）："adding partitions…changes the topic's partitioning schema…old data is partitioned differently than new data"；补救=读旧主题全量重写新主题。KIP-794 只动无 key 粘性分区，有 key 路由 3.x 不变（对照 BuiltInPartitioner 源码）。
- A3：MySQL 8.0 Reference Manual §17.18.2 InnoDB Recovery（"The rollback is performed by a background thread, executed in parallel with transactions from new connections. Until the rollback…new connections may encounter locking conflicts"）；mysql-server 8.0 srv0start.cc（trx_recovery_rollback_thread 后台启动）+ trx0roll.cc:722 错误日志文案。
- A4：数学自洽核验（120MB÷2MB/s=60s；公式与不等式互相锁定）。
- A5：K8s 官方 Pod Lifecycle（startup 成功前不执行另两类；liveness→kubelet restarts；readiness→仅从 EndpointSlice 摘 IP，无重启语义）。
- 连带修正：同上 readiness 语义——readiness 失败既不触发也不阻止重启。

## 四、改后复验结论

- 构建与保真：build_html + build_pages 双产物重建 PASS（交叉引用 212 处 0 未解析）；check_content 13/13 章一致。
- **fact-consistency 复验：A–E 全 PASS，放行**（衔接/跨章五组/拟人化/体例/教程腔逐项核过；顺带确认 CAP"本质上是 AP"病句全书零残留）。残漏 2 条均轻微：①ch9:101"C 不大于 W 时，副本越落越远"在 C==W 边界不严格——属本轮新引入文本，已按其最小修法落"不大于"→"小于"（C==W 语义已由前句"只有 C 大于 W 才有净追赶能力"覆盖）；②ch7:156"这个映射"指代距离偏长但双锚定无歧义——维持。
- **voice-consistency 复验：A–G 全 PASS，放行，无必修项**（第一人称口吻与既有句同构；"管的是"有 ch7 L71 先例；字节级验证三文件零弯引号零破折号零 MiB；两处低严重度观察均建议维持现状）。
- 复验报告：`A批改后复验-事实一致性.md`、`A批改后复验-声音语域.md`（同目录）。
- 微修后再重建：双产物 PASS、保真 13/13。

## 五、产出物

- 重建：架构之道.html + dist/ + qa/build-audit.json + qa/pages-audit.json + qa/content-audit.json
- 不提交：20260905gpt5.6重写版/、.claude/output-styles/、qa_reports/20260905-整体分析与优化报告.md
