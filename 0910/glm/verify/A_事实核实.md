# A 类（技术事实）18 条逐条核实报告

核实人：事实核实官（A 类专责）。方法：逐条 Read 书稿原文与上下文 → Grep 孪生表述 → 逐条取一手证据（官方文档 / 源码 / 论文 PDF / 出版方页面）裁决。基线版本口径：Redis 7.x、MySQL 8.0.x、Kafka 3.x（书稿自述）。

裁决图例：CONFIRM（书稿错+改法对）/ REVISE（书稿错但改法需调整）/ REJECT（书稿没错，读者误报）/ INSUFFICIENT（查不到硬证据）。

**总裁决：18 条全部 CONFIRM，0 REVISE / 0 REJECT / 0 INSUFFICIENT。** 其中 MF-04、MF-23、MF-26 三条在"原文是否严格为假"上有细微裁量（逐条注明），但改法均与官方现行文档逐字吻合、零风险，维持照改结论。另发现 4 处清单未覆盖的孪生/连带问题（见各条"孪生检查"与文末汇总）。

---

## MF-04 · ch1 L137 · min.insync.replicas 释义

**裁决：CONFIRM**（附裁量说明）

**书稿原文错了吗？** 原括号释义"写入至少需 2 个同步副本确认"把 min.insync.replicas 讲成确认数门槛。Kafka 官方文档经历了一次关键改写：0.11–3.x 时代的老措辞确实是"min.insync.replicas specifies the minimum number of replicas that must acknowledge a write for the write to be considered successful"（https://kafka.apache.org/23/configuration/broker-configs ）——书稿这句几乎是老官方文档的直译。但官方 4.x 文档专门重写了这一段来消除这个误读：

> "min.insync.replicas — Specifies the minimum number of **in-sync replicas (including the leader) required for a write to succeed** when a producer sets acks to 'all'. In the acks=all case, **every in-sync replica must acknowledge** a write... E.g., if a topic has replication.factor of 3 and the ISR set includes all three replicas, **then all three replicas must acknowledge an acks=all write for it to succeed, even if min.insync.replicas happens to be less than 3**. If acks=all and the current ISR set contains fewer than min.insync.replicas members, then the producer will raise an exception (either NotEnoughReplicas or NotEnoughReplicasAfterAppend)."
> —— https://kafka.apache.org/42/configuration/topic-configs （4.1 同文）

即：min.insync.replicas 是 ISR 数量下限（跌破即抛 NotEnoughReplicas 拒写），acks=all 下实际确认数 = 当前 ISR 全部（RF=3、ISR=3 时是 3 个，不是 2 个）。读者修正与 4.x 官方文档逐字一致。书稿自身 ch9 L237 也早已用正确口径（"min.insync.replicas（ISR 最少要有几个副本才允许写入）"），ch1 是全书唯一偏差处。

**裁量说明：** 严格说，"至少需 2 个确认"作为下界命题在 ISR≥2 时为真（老官方文档也这么写），不是假命题；但它正是官方 4.x 改写要消除的那个误读口径（会让人以为 minISR 能把确认数降到 2），且与书稿 ch9 自相矛盾。改法向现行官方口径对齐，零风险，**建议照改**。

**改法复核：** 新文本"ISR 少于 2 个时拒绝写入；配合 acks=all，写入要等 ISR 中全部副本确认"——两个分句分别对应 4.x 文档的 NotEnoughReplicas 句和 every-in-sync-replica-must-acknowledge 句，无新错误。✓

**孪生检查：** Grep `min.insync.replicas` 全书命中 ch1 L137（本条）、ch4 L218/L312、ch7 L174、ch9 L237/239/266、ch10 L100——其余各处均为正确或中性表述（ch9 L237 释义正确、L239 给出"副本数 3 + minISR=2 + acks=all"推荐组合），无漏改。outline.md 内部工作文件不计入书稿。

---

## MF-05 · ch2 L41 · ZRANGE 复杂度漏 +M

**裁决：CONFIRM**

**书稿原文错了吗？** 错。官方命令页：

> "Time complexity: **O(log(N)+M)** with N being the number of elements in the sorted set and M the number of elements returned."
> —— https://redis.io/docs/latest/commands/zrange/

同段隔两行书稿自己写"范围扫描只需沿底层链表前进（O(log N + M)）"，同段自相矛盾成立（漏 M 时 ZRANGE 全集拉取会被误读为 O(log N)）。

**改法复核：** 新文本"ZRANGE 是 O(log N + M)（M 为拉取条数）"与官方逐字对应。✓

**孪生检查：** Grep `ZRANGE`/`O(log` —— ch2 L41 唯一错处；fig-2-2.svg 写"平均 O(log N) · 范围扫描沿底层链表"（描述跳表查找本身，可容忍）、fig-2-6.svg 写"点查 O(log N) · 范围扫描 O(log N + M)"（B+ 树，正确）。无漏改。

---

## MF-06 · ch3 L151 · KRaft 下没有 `[KafkaServer id=0] started`

**裁决：CONFIRM**

**书稿原文错了吗？** 错，且已在源码与真实日志两级验证：

1. ZK 模式（KafkaServer.scala，3.9 分支）：`logContext = new LogContext(s"[KafkaServer id=${config.brokerId}] ")`，startup() 末尾 `info("started")` → 实际日志行 `[KafkaServer id=0] started`。该类仅在 ZK 模式使用（类内 initZkClient、ZkConfigRepository 等）。https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/server/KafkaServer.scala
2. KRaft 模式（BrokerServer.scala，3.9 分支）：类注释"A Kafka broker that runs in KRaft (Kafka Raft) mode."；`private val logContext: LogContext = new LogContext(s"[BrokerServer id=${config.nodeId}] ")`；启动末尾 `maybeChangeStatus(STARTING, STARTED)` 内 `info(s"Transition from $status to $to")` → 实际日志行 `[BrokerServer id=0] Transition from STARTING to STARTED`。https://raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/server/BrokerServer.scala
3. 真实日志多源互证（Kafka 3.4.0–3.9.0 五个独立来源）：
   > `[2024-02-26 10:38:26,890] INFO [BrokerServer id=1] Transition from STARTING to STARTED (kafka.server.BrokerServer)` … `[KafkaRaftServer nodeId=1] Kafka Server started (kafka.server.KafkaRaftServer)`
   > —— https://digitalocean.com/community/tutorials/introduction-to-kafka （另见 CSDN itorac/134342170 3.6.0、dev.to haiphamcoder 3.8.0、github.com/AutoMQ/automq/issues/2833 3.9.0）

本章主线是 KRaft（ch3 L143 阶段 2 即"元数据管理初始化（KRaft 核心）"，L153 讲 ZK→KRaft 换代），把 ZK-only 日志行当通用就绪信号确属错误，运维照书 grep 会失灵。

**改法复核：** 新文本给出的两条日志行均逐字正确（源码 + 五源实测）。补充情报：KRaft 模式该行之后还有一条 `[KafkaRaftServer nodeId=N] Kafka Server started`，语义上更接近 ZK 模式那句话，可作为备选 grep 目标——但改法选用的 BrokerServer 转换行标志 broker 进程就绪、同样成立，无需调整。✓

**孪生检查：** Grep `KafkaServer id`/`started`——ch3 L151 唯一处。无漏改。

---

## MF-11 · ch4 L30 · "纳秒、微秒、毫秒之间相差三到五个数量级"

**裁决：CONFIRM**

**书稿原文错了吗？** 错（算术层面）。按单位换算：ns→μs 与 μs→ms 各差 3 个数量级，ns→ms 差 6 个，"三到五个"对单位对不上（凑不出 5）。原句想锚的是介质：表 4-1 自家数字（内存 ~100ns、SSD 随机读 ~100μs、机械盘 ~10ms）给出 3 与 5 个数量级；同段前一句的换算也自证（内存 1 秒 → SSD 17 分钟 = ×10³；→ 机械盘 28 小时 ≈ ×10⁵）；图 4-1 图注"内存到机械盘横跨五个数量级"同口径。

**改法复核：** 新文本"从内存的百纳秒到 SSD 的百微秒差三个数量级，到机械盘的十毫秒差五个数量级"——与表 4-1、时间类比、图 4-1 注三处自洽，锚点明确。✓

**与 MF-16 的口径关系：** 两条问题域不同（MF-11 是内存 vs 持久介质延迟；MF-16 是进程内调用 vs 网络往返），修正后分别为"3 与 5""3 到 4（跨域 5–6）"，互不冲突，不需统一口径。

**孪生检查：** Grep `数量级`——ch2 L79"内存访问是纳秒级，而磁盘 I/O 是微秒到毫秒级，差着三到五个数量级"是同精神表述，但它锚在介质上（纳秒≈百纳秒内存、微秒到毫秒≈SSD 到机械盘），换算成立，可不动（若求全可把"纳秒级"改"百纳秒"，非必改）。其余命中均为正确用法。无必改漏网。

---

## MF-13 · ch4 L202 · 预读"下几 MB" vs 默认 128KB

**裁决：CONFIRM**

**书稿原文错了吗？** 错。Linux 块设备默认预读窗口为 128KB：

> "The file prefetch parameter is defined in the read_ahead_kb file... 此参数的默认值 128KB" —— 华为鲲鹏官方性能调优文档 https://www.hikunpeng.com/document/detail/zh/kunpenghpcs/hpcindapp/tngg/kunpenghpcsolution_05_0018.html （英文页同句 "The default value of this parameter is 128 KB"）
> 内核 sysfs 规范（blk-sysfs.c RFC）："128 KB for each device is a good starting point, but **increasing to 4-8 MB** might improve performance in environments where sequential reading of large files takes place." —— http://lkml.rescloud.iu.edu/2506.3/01419.html
> 实测口径：`cat /sys/block/sda/queue/read_ahead_kb # 128` —— https://kernel-internals.org/io/readahead

"下几 MB"高估默认值一个数量级以上，且与本章 L258 把"预读大小"列为 OS 可调参数自相矛盾（默认若是几 MB 就无所谓调到 MB 级）。

**改法复核：** 新文本"默认预读窗口约 128KB，调优后可到 MB 级"——"约"字恰好覆盖个别发行版对 SSD 给 256KB 的差异，"调优后可到 MB 级"与内核文档 4–8MB 建议吻合。✓

**孪生检查：** Grep `预读|readahead`——ch4 L202 唯一量化处；L184/L188（机制描述无数字）、ch8 L120（页大小议题）、ch10 L57 均不相涉。无漏改。

---

## MF-16 · ch5 L232 · "进程内纳秒 vs 网络毫秒，差了六个数量级"

**裁决：CONFIRM**

**书稿原文错了吗？** 错（量级高估约 2 个数量级）。经典一手数据（Jeff Dean / Peter Norvig，Latency Numbers Every Programmer Should Know，多镜像互证）：

> "Main memory reference .............. 100 ns" / "Round trip within same datacenter .. 500,000 ns (500 us)"
> —— https://gist.github.com/jboner/11349918（CheYulin、influx6 等镜像同数字）

同机房 RTT ~500μs；进程内跨层函数调用（参数传递/虚函数/指针跳转）在几到几十纳秒量级 → 差约 3–4 个数量级（100ns↔500μs = 3.7 个）。要凑出"六个数量级"须同时取 1ns 与 1ms 两个极端端点。书稿自身 ch4 L67 也写"本地或同机房访问通常落在亚毫秒到毫秒级"，与"六个数量级"打架。跨地域（CA→NL→CA ≈ 150ms）才到 6 个数量级上下。

**改法复核：** 新文本"进程内调用是几十纳秒量级，同机房网络往返是百微秒到毫秒量级，差三到四个数量级（跨地域部署才拉开到五六个数量级）"——各数字均落在上述实测带内。✓（清单证据栏提到的 Azure 同可用区 RTT 统计与 Evan Jones 2021 未能直接核到原文，但不影响：Jeff Dean 数字已足以支撑改法。）

**孪生检查：** Grep `六个数量级`——ch5 L232 唯一处。无漏改。

---

## MF-19 · ch6 L127 + L180 · allow.everyone.if.no.acl.found 默认值写反

**裁决：CONFIRM**

**书稿原文错了吗？** 错，默认值确为 false（默认拒绝），三源互证：

1. Apache Kafka 官方（3.7 文档，Authorization and ACLs）：
   > "By default, if no ResourcePatterns match a specific Resource R, then R has no associated ACLs, and therefore **no one other than super users is allowed to access R**. If you want to change that behavior, you can include the following in server.properties. `allow.everyone.if.no.acl.found=true`"
   > —— https://kafka.apache.org/37/security/authorization-and-acls/ （0.10.1 起历代文档同段）
2. AWS 官方把"Apache 默认"与"MSK 定制"分得极清：
   > "If RP doesn't match a specific resource R... no one other than super users is allowed to access R. **To change this Apache Kafka behavior, you set the property allow.everyone.if.no.acl.found to true. Amazon MSK sets it to true by default.**"
   > —— https://docs.aws.amazon.com/msk/latest/developerguide/msk-acls.html ；默认配置表同列 `allow.everyone.if.no.acl.found → true`（https://docs.aws.amazon.com/msk/latest/developerguide/msk-default-configuration.html ）
3. 第三方运维资料一致（AxonOps 配置表：`allow.everyone.if.no.acl.found | false | Allow access when no ACL exists`；Netdata："The allow.everyone.if.no.acl.found setting defaults to false"）。

书稿写"默认是 true"，导致后半句"生产环境要么显式把该参数设为 false"成为空操作，Apache 的默认安全姿态被整体说反。表 6-1"AclAuthorizer 无 ACL 默认放行"同错。

**改法复核：** 新文本"默认是 **false**：资源上完全没配 ACL 时，除 super.users 外一律拒绝；显式设为 true 才会在无 ACL 时放行所有人（Amazon MSK 等托管服务会预置成 true，容易造成'默认放行'的错觉）。KRaft 的 StandardAuthorizer 同样默认拒绝"——与上述官方文档逐字对应（MSK 预置 true 有 AWS 原文直接支撑；StandardAuthorizer 无该放行默认，"同样默认拒绝"成立）。表 6-1 连带改法同理。✓

**孪生检查：** Grep `allow.everyone|默认放行`——正文 L127 + 表 L180 两处，清单已全覆盖。ch6 outline.md L120 内部工作文件持同样错误认知（"默认值历史上是 true"），不进书稿，不列为必改。无漏改。

---

## MF-21 · ch7 L57 · 全量同步"写成一个 RDB 文件"（7.0 起默认无盘）

**裁决：CONFIRM**

**书稿原文错了吗？** 错。官方 redis.conf 一手对照：

- Redis **7.0** 分支 redis.conf：`repl-diskless-sync yes`（生效默认值，原文注释："2) Diskless: The Redis master creates a new process that **directly writes the RDB file to replica sockets, without touching the disk at all**."）—— https://raw.githubusercontent.com/redis/redis/7.0/redis.conf
- Redis **6.2** 分支 redis.conf：`repl-diskless-sync no` —— https://raw.githubusercontent.com/redis/redis/6.2/redis.conf

默认值在 7.0 翻转为无盘。全书基线 7.x 下，"fork 出子进程把内存数据写成一个 RDB（快照文件）发给从节点"描述的是 6.x 及以前的落盘路径。官方复制文档同口径："With slow disks this can be a very stressing operation for the master... In this setup the child process directly sends the RDB over the wire to replicas, without using the disk as intermediate storage."（https://redis.io/docs/latest/operate/oss_and_stack/management/replication/ ）

**改法复核：** 新文本"以 RDB 格式直接经网络流发给从节点（7.0 起默认无盘复制，`repl-diskless-sync=yes`，不在主节点落盘；设为 no 时才先写磁盘文件再发送）"——与 redis.conf 注释及复制文档逐义对应。注意主节点侧表述准确（副本侧默认 `repl-diskless-load disabled` 仍可能先落盘再加载，新文本未做副本侧断言，无越界）。✓

**孪生检查：** Grep `RDB`——ch9 L69/L71（MF-27 覆盖）、**ch9 L76"RDB 文件在网络上的传输要消耗主节点的出口带宽"（未覆盖，见连带发现 ①）**、**ch9 fig-9-3.svg"④ 主节点 BGSAVE，fork 子进程生成 RDB"（未覆盖，见连带发现 ②）**、ch3 L185 与 ch4 fig-4-3（讲持久化 BGSAVE，非复制路径，不相涉）。ch9 outline.md L35 为内部文件。

---

## MF-23 · ch7 L172 · "只要 ISR 非空且 ISR 全部收到，这条消息就不会丢"

**裁决：CONFIRM**

**书稿原文错了吗？** 错在条件无约束力。官方文档的确有一句形似的话，但条件本质不同：

> "acks=all This means the leader will wait for the full set of in-sync replicas to acknowledge the record. This guarantees that the record will not be lost **as long as at least one in-sync replica remains alive**."
> —— Kafka 官方 producer 配置文（RedHat AMQ 7.5 附录全文转引：https://docs.redhat.com/fr/documentation/red_hat_amq/7.5/html/using_amq_streams_on_rhel/producer-configuration-parameters-str ；kafka.apache.org/11/streams/developer-guide/config-streams/ 同句）

官方条件"at least one in-sync replica **remains alive**（事后持续存活）"在丢消息场景（ISR 只剩 Leader、Leader 崩溃）里是失效的、因而官方承诺不覆盖该场景；书稿把它改写成"**只要 ISR 非空**（写入时点条件）且 ISR 全部收到"——ISR 恒含 Leader，该条件几乎恒真，把官方的有条件保证放大成了无条件保证。min.insync.replicas 默认 1（见 MF-04 证据），ISR 缩到只剩 Leader 时 acks=all 退化为 acks=1，多个独立技术来源明确指出这一点：

> "acks=all alone is not enough. If the ISR shrinks to just the leader..., acks=all is satisfied by a single replica — the same as acks=1. min.insync.replicas... If fewer replicas are in-sync, the broker rejects the write with NotEnoughReplicasException."（aicancode.org/learn/kafka/producer-acks；kindatechnical.com、hivebook.wiki 同论）

官方推荐组合原文即书稿 ch9 L239 的"副本数 3、minISR=2、acks=all"。书稿 ch7 L174 与 ch9 acks 节（L237 起，确实存在）也都承诺过"精确交互见第 9 章"，本条指向的修正与之自洽。

**改法复核：** 新文本"只要 ISR 里的副本数不少于 min.insync.replicas 且全部收到，这条消息就不会因正常的 Leader 切换而丢（min.insync.replicas 默认 1——ISR 缩到只剩 Leader 一个时，acks=all 的保证会退化，实质不丢需配 min.insync.replicas≥2，精确交互见第 9 章）"——加了"因正常的 Leader 切换而丢"的限定与 minISR≥2 前提，准确且不与官方文档冲突。✓

**孪生检查：** Grep `ISR 非空`——ch7 L172 唯一处。无漏改。

---

## MF-26 · ch8 L151 · "一次 512 字节的写要么完整要么不发生"

**裁决：CONFIRM**（附证据基础说明）

**书稿原文错了吗？** 错。原文把"512B = 扇区原子写"当成硬件事实陈述（"要么完整要么不发生，不会留下半个扇区的撕裂"），这在任何官方规范里都不是承诺，而 InnoDB 自身也不依赖它：

1. InnoDB redo 真正的机制是**逐块校验和 + 只恢复完整记录组**（MySQL 官方开发者文档）：
   > "Data in the redo log is structured in **consecutive blocks of 512 bytes (OS_FILE_LOG_BLOCK_SIZE)**. Each block contains a header of 12 bytes (LOG_BLOCK_HDR_SIZE) and a footer of 4 bytes (LOG_BLOCK_TRL_SIZE)."... "**During recovery only complete groups of log records are recovered and applied.**"
   > —— https://dev.mysql.com/doc/dev/mysql-server/latest/PAGE_INNODB_REDO_LOG.html （块尾 4 字节即校验和；恢复扫描遇损坏块即止，典型错误行 `[ERROR] InnoDB: Log scan failed: corrupted log block at lsn=...`）
2. 数据库社区对"页/块写会部分完成"的态度（PostgreSQL 官方文档，full_page_writes 的设计动机）：
   > "Disk platters are divided into sectors, commonly 512 bytes each... the process of writing could fail due to power loss at any time, meaning **some of the 512-byte sectors were written, and others were not**. To guard against such failures, PostgreSQL periodically writes full page images..."
   > —— https://www.postgresql.org/docs/8.3/wal-reliability.html （现行版本同段；pgpedia "Torn page" 词条同义）
3. 断电下半扇区/部分写在真实 SSD 上是已知现象：FAST'13 论文 *Understanding the Robustness of SSDs under Power Fault*（Zheng et al.）实测多款 SSD 断电出现部分写/撕裂（本条为存目引用，未直接取 PDF 原文——已用 1、2 的官方文档覆盖核心修正，此为补充）。

**证据基础说明：** PostgreSQL 文档把撕裂建模在"扇区之间"（多扇区页写一半），字面上未直说"单扇区内撕裂"；单扇区原子性无规范保证、SSD 断电部分写有实测文献，是"512B 原子"只能当 folklore 不能当事实的依据。核心修正（书稿不该把原子性写成硬件承诺、InnoDB 实际靠校验和检出）由 MySQL 官方开发者文档直接支撑，成立无疑。

**改法复核：** 新文本"512 字节对齐传统磁盘扇区粒度，降低跨界写的概率（断电时半扇区撕裂在真实设备上仍是已知现象）；每块 redo 自带校验和，恢复时逐块校验、丢弃不完整的尾部，撕裂可被检出"——"对齐降低跨界写概率""逐块校验、只恢复完整组"均有官方文档支撑；"半扇区撕裂为已知现象"以 SSD 断电文献为据（如上说明）。✓

**孪生检查：** Grep `512`/`原子写`——**fig-8-5.svg L26-27 图内文本"512B 块对齐 / 匹配扇区原子写"与本条同病，清单未覆盖（见连带发现 ③）**；ch8 L158/L307 讲"底层原子写硬件可撤双写"（讲的是具备原子写能力的设备，前提成立，不相涉）；ch2 fig-2-5 的 512 是 set-max-intset-entries，无关。ch8 outline.md L107 为内部文件。

---

## MF-27 · ch9 L69 + L71 · 全量同步步骤按 6.x 落盘路径描述 + `?` 释义

**裁决：CONFIRM**

**书稿原文错了吗？** 两处均错：

1. **无盘默认**：同 MF-21 证据（7.0 redis.conf `repl-diskless-sync yes`，"without touching the disk at all"；6.2 为 no）。步骤 1"触发 BGSAVE，fork 出一个子进程把当前内存快照写成 RDB 文件"是落盘路径描述。
2. **`?` 的含义**：官方复制文档：
   > "When replicas connect to masters, they use the `PSYNC` command to send **their old master replication ID** and the offsets they processed so far... if the replica is referring to an **history (replication ID) which is no longer known**, then a full resynchronization happens."
   > "Every Redis master has a **replication ID**: it is a large pseudo random string that marks a given history of the dataset."
   > —— https://redis.io/docs/latest/operate/oss_and_stack/management/replication/

   `PSYNC ? -1` 的 `?` = 未知复制 ID（replid），非 run_id。书稿 L89 自己写明"PSYNC <replid> <offset>（replid 是主节点的复制 ID，PSYNC2 之前这个角色由上文提到的 run_id 担任）"、L103 讲 replid/replid2——L69 是漏改的旧口径，章内自相矛盾。

**改法复核：** 新步骤 1"（`?` 与 `-1` 分别表示'未知复制 ID（replid）'与'无偏移量'…），fork 出一个子进程做全量同步：7.0 起 repl-diskless-sync 默认 yes（无盘复制），子进程把内存快照序列化成 RDB 流直接写进副本连接，主节点磁盘上并不生成 RDB 文件；显式配 no 时才先 BGSAVE 写成 RDB 文件再传"——与 redis.conf 及复制文档逐义对应；步骤 3"RDB 流（或文件）"兼容两模式。✓

**孪生检查：** Grep `run_id|replid|BGSAVE`——L69（本条）、L89/L103（正确口径，保留对照合理）、**L76（见连带发现 ①）**、**fig-9-3.svg（见连带发现 ②）**、ch3 L185（关闭时显式 BGSAVE 落盘，属持久化非复制，不相涉）、ch4 fig-4-3（持久化图，不相涉）。

---

## MF-28 · ch9 L99 · "副本做一次短暂的 GC"

**裁决：CONFIRM**

**书稿原文错了吗？** 错。Redis 是 C 语言实现，没有垃圾回收器——"GC 停顿"是 JVM 系统的病。书内自证：ch5 L44"命令执行依然在主线程串行"、ch3 L34 fork 拷贝页表的阻塞描述；官方 redis.conf（7.0）THREADED I/O 节自述"Redis is mostly single threaded, however there are certain threaded operations such as UNLINK, slow I/O accesses..."（https://raw.githubusercontent.com/redis/redis/7.0/redis.conf ）。C 程序无 GC 属定义性事实。

**改法复核：** 新文本"（典型场景：副本一次短暂阻塞——fork、慢命令——或网络抖动）"——副本侧短阻塞的真实来源（自身 RDB fork、慢命令等），准确。✓

**孪生检查：** Grep `GC`——ch9 L99 唯一相关处（其余命中为 S3/GCS 对象存储字样，无关）。无漏改。

---

## MF-29 · ch9 L175 · "只有一个 SQL 线程串行回放"同句撞上"8.0.27 起默认 4 worker"

**裁决：CONFIRM**

**书稿原文错了吗？** 错（同句自相矛盾 + 与基线 8.0.x 默认不符）。官方两处一手证据：

1. MySQL 8.0.27 Release Notes（2021-10-19）：
   > "Replication: **Multithreading is now enabled by default for replica servers**... The following default server settings are used to produce the multithreading behavior: **replica_parallel_workers=4**... replica_preserve_commit_order=1... replica_parallel_type=LOGICAL_CLOCK."
   > —— https://dev.mysql.com/doc/relnotes/mysql/8.0/en/news-8-0-27.html
2. 参考手册 19.1.6.3：
   > "**Prior to MySQL 8.0.27, the default value of this system variable is 0**, so replicas are single-threaded by default. **Beginning with MySQL 8.0.27, the default value is 4**, which means that replicas are multithreaded by default."
   > —— https://dev.mysql.com/doc/refman/8.0/en/replication-options-replica.html

书稿主句断言"从节点只有一个 SQL 线程串行回放事件"，同句括号又承认 8.0.27 起默认 4 worker——基线 8.0.x 下从库默认并非单线程。书内 ch7 L115 已是正确版本（"单 SQL 线程回放意味着…**MySQL 的多线程复制（MTS…8.0.27 起默认开启，replica_parallel_workers 默认 4，更早版本默认 0 即单线程回放）**"），ch9 L175 是全书唯一打架处。

**改法复核：** 新文本"从节点靠 SQL 线程回放事件，MTS 出现前只有一个线程串行回放（8.0.27 起 MTS 默认开启 4 个 worker，更早版本默认单线程，但并行度仍受主库组提交宽度限制），主节点并发写入、回放侧追赶吃力，吞吐不对称导致从节点越落越远"——与官方口径及 ch7 L115 一致；"并行度受主库组提交宽度限制"与本章 L179 原有论述自洽。✓

**孪生检查：** Grep `SQL 线程|worker|MTS`——ch9 L175 唯一矛盾处；ch7 L98/L105/L111/L115、ch9 L142/L144、fig-7-3/9-2/9-5/9-6 均为两段式链路或 MTS 机制的正确描述。无漏改。

---

## MF-36 · ch10 L145（表 10-2 RPO 行两处）· Redis"默认 1–2 秒"与 Kafka"acks=all 接近 0"

**裁决：CONFIRM**

**书稿原文错了吗？** 两处均错：

1. **Redis 列**：出厂默认不开 AOF（`appendonly no`，靠 save 规则周期快照）——官方 redis.conf 7.0 逐字：`appendonly no`；AOF 注释"using the default data fsync policy... **Redis can lose just one second of writes** in a dramatic event like a server power outage"；save 默认"**After 3600 seconds (an hour)** if at least 1 change was performed"（https://raw.githubusercontent.com/redis/redis/7.0/redis.conf ）。即默认 RDB-only 的丢失窗口是快照周期（最长小时级），不是 1–2 秒。书内三处自证默认口径：ch4 L104"Redis 7.x 出厂默认并不开启 AOF（appendonly no，即 RDB-only）"、ch8 L102 同、ch10 L98"（出厂默认 RDB-only 时，丢失窗口取决于快照周期）"——表 10-2 该格与全书打架。
2. **Kafka 列**：min.insync.replicas 默认 1（见 MF-04 证据），"acks=all 接近 0"缺前提；ch9 L239 已有正确表述（"一个常见的强可靠配置是副本数 3、min.insync.replicas=2、acks=all，能容忍单副本故障而不丢数据"）。

**改法复核：** 新文本①"出厂默认 RDB-only 为快照周期（最长可达小时级）；开启 AOF everysec 后约 1–2 秒"——与 redis.conf（1 小时 save 规则 + everysec 丢约 1 秒）及书内 ch4 L101"最坏丢失窗口约 2 秒"自洽；②"acks=all + min.insync.replicas≥2 接近 0（默认 min.insync.replicas=1 时不保证）"——与官方推荐组合及 ch9 L239 一致。✓

**孪生检查：** Grep `1–2 秒|everysec|appendonly`——ch10 L145 唯一错处；ch10 L72（appendfsync 三档，正确）、ch10 L98（正确）、ch4 L101/L104、ch8 L83/L102 均正确。无漏改。

---

## MF-37 · ch10 L147 · Cluster Linking 归属"Kafka 官方工具"

**裁决：CONFIRM**（附清单说明栏勘误）

**书稿原文错了吗？** 错。Confluent 官方许可页（7.5）把 Cluster Linking 明确列在 **Confluent Enterprise License** 下（Confluent Server 的商业特性）：

> "Confluent Enterprise License for Confluent Platform subscription: ... **Confluent Server** — The following are a few key features included in Confluent Server: **Cluster Linking**, Multi-Region Clusters, Role-based Access Control, ... Tiered Storage ..."
> "**Apache 2.0 License: Apache Kafka (with Connect and Streams)**, Ansible Playbooks, ..."
> —— https://docs.confluent.io/platform/7.5/installation/license.html （Confluent Community License FAQ 的三栏表同样把 Cluster Linking 列在 Enterprise 列：https://www.confluent.io/confluent-community-license-faq/ ）

即 Cluster Linking 不在 Apache Kafka 开源版内；MirrorMaker 2 基于 Connect、随 Apache Kafka 发行（Apache 2.0 栏含"Apache Kafka (with Connect and Streams)"）。"均为 Kafka 官方跨集群复制工具"归属错误，读者在开源版找不到该组件。

**清单说明栏勘误（不影响改法）：** mustfix 的 why 写"Confluent Community License"，实测为 **Confluent Enterprise License**（比 Community 更严）；所幸替换文本未写许可证名，不受影响。

**改法复核：** 新文本"MirrorMaker 2（Apache Kafka 官方自带）/ Cluster Linking（Confluent 平台特性，不在 Apache Kafka 开源版内）"——两个归属均与官方许可页一致。✓

**孪生检查：** Grep `Cluster Linking|MirrorMaker`——ch10 L147 唯一处。无漏改。

---

## MF-42 · refs L43 · Cluster 规范注释用 SDOWN/ODOWN

**裁决：CONFIRM**

**书稿原文错了吗？** 错。Redis Cluster Specification（本次全文抓取）故障检测一节：

> "There are two flags that are used for failure detection that are called **PFAIL and FAIL**. **PFAIL means Possible failure**, and is a non-acknowledged failure type. **FAIL means that a node is failing and that this condition was confirmed by a majority of masters** within a fixed amount of time."
> —— https://redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/

规范通篇（本次抓取全文）不出现 SDOWN/ODOWN——那是 Sentinel 体系的术语（ch7 L65 在 Sentinel 语境下使用 SDOWN/ODOWN 是正确的）。读者拿 SDOWN/ODOWN 去规范里检索一无所获。

**改法复核：** 新文本"异步复制与 PFAIL/FAIL 故障检测的一手规范"——与规范原文对应。✓

**孪生检查：** Grep `SDOWN|ODOWN|PFAIL`——refs L43 唯一错处；ch7 L65（Sentinel 正文，正确）、fig-7-1.svg（Sentinel 链路，正确）、fig-7-5.svg（Cluster 用 PFAIL，正确）。无漏改。

---

## MF-43 · refs L76 · HPMySQL 第 4 版作者套了第 3 版班子

**裁决：CONFIRM**

**书稿原文错了吗？** 错。第 4 版（2022）作者是 Silvia Botros 与 Jeremy Tinley：

> O'Reilly 官方书页："高性能MySQL:第4版 **by Silvia Botros, Jeremy Tinley** October 2022"—— https://www.oreilly.com/library/view/gao-xing-neng-mysql-di-4ban/9787121442575/
> 英文版（Early Release 版权页）："**High Performance MySQL by Silvia Botros and Jeremy Tinley**. Copyright © 2022... Published by O'Reilly Media, Inc., 1005 Gravenstein Highway North, **Sebastopol**, CA 95472... 978-1-492-08051-0"

Schwartz/Zaitsev/Tkachenko 是第 3 版（2012）作者班子，套在 4 版著录上是张冠李戴。

**改法复核：** 新著录"[38] Botros S, Tinley J. High Performance MySQL[M]. 4th ed. Sebastopol: O'Reilly Media, 2022."——作者、版次、出版地、年份四要素均与 O'Reilly 页面一致（英文版初印 2022 年 1 月，著录 2022 无误）。✓

**孪生检查：** Grep `High Performance MySQL|Schwartz`——refs L76 唯一处。无漏改。

---

## MF-44 · refs L77 · NetDB'11 地点与作者顺序

**裁决：CONFIRM**

**书稿原文错了吗？** 两处均错：

1. **地点**：NetDB 2011 在希腊雅典（与 SIGMOD 2011 同址），微软研究院存档的会议官方页：
   > "**Location: Athens, Greece** ... Session 2: Cloud Serving & Logging ... **Kafka: A Distributed Messaging System for Log Processing — Jay Kreps, Neha Narkhede, Jun Rao (LinkedIn)**"
   > —— https://www.microsoft.com/en-us/research/event/netdb-2011/program/
   ACM DL 正式引文同："In Proceedings of the SIGMOD Workshop on Networking Meets Databases (NetDB). **Athens, Greece.**"（dl.acm.org/doi/abs/10.1145/3328905.3332302 参考文献区）
2. **作者顺序**：原始论文署名 Kreps 在前（论文 PDF 首页："Kafka: a Distributed Messaging System for Log Processing — **Jay Kreps** LinkedIn Corp. / **Neha Narkhede** / **Jun Rao**"，MSR 存档 https://www.microsoft.com/en-us/research/wp-content/uploads/2017/09/Kafka.pdf ）；Apache Kafka 官方 Books and Papers 页同序：
   > "Kafka: a Distributed Messaging System for Log Processing by **Jay Kreps, Neha Narkhede, Jun Rao**; NetDB workshop '11, 2011" —— https://kafka.apache.org/books-and-papers

书稿"Narkhede N, Kreps J, Rao J...Stockholm"把第一、二作者对调且地点错。

**改法复核：** 新著录"[39] Kreps J, Narkhede N, Rao J. Kafka: a Distributed Messaging System for Log Processing[C]//NetDB'11 Workshop. Athens, 2011."——作者序、工作坊名、地点均与上述一手来源一致。✓

**孪生检查：** Grep `NetDB|Narkhede`——refs L77 唯一处。无漏改。

---

# 汇总

## 裁决统计

| 裁决 | 数量 | 条目 |
|---|---|---|
| CONFIRM | 18 | MF-04/05/06/11/13/16/19/21/23/26/27/28/29/36/37/42/43/44（全部） |
| REVISE | 0 | — |
| REJECT | 0 | — |
| INSUFFICIENT | 0 | — |

## 裁量与勘误备注（不影响"照改"结论，供执行人知悉）

1. **MF-04**：原文"至少需 2 个确认"作为下界命题在 ISR≥2 时为真，且近似旧版（0.11–3.x）官方文档措辞，严格说不算假命题；但 Kafka 4.x 官方文档专门重写该段并给出反例（"RF=3、ISR=3 时 3 个都要确认，即使 minISR<3"），书稿 ch9 L237 也已是正确口径。改法与现行官方逐字吻合，零风险。
2. **MF-23**：官方 producer 文档确有"not be lost as long as at least one in-sync replica remains alive"的形似表述；差异在条件性质——官方是"事后持续存活"条件（丢消息场景下该条件失效、承诺不覆盖），书稿写成"写入时 ISR 非空"（几乎恒真），把有条件保证放大成无条件保证。改法加了"因正常的 Leader 切换而丢"限定与 minISR≥2 前提，精确。
3. **MF-26**："断电半扇区撕裂在真实设备上是已知现象"的直接文献为 FAST'13 SSD 断电实测（存目引用）；PostgreSQL 官方文档把撕裂建模在扇区之间（页写一半）。核心修正（不应把 512B 原子写成硬件承诺；InnoDB 实际靠逐块校验和 + 只恢复完整记录组）由 MySQL 官方开发者文档直接支撑，成立无疑。
4. **MF-37**：mustfix 说明栏写"Confluent Community License"，实测为 Confluent **Enterprise** License（更严）；替换文本未写许可证名，不受影响。

## 连带发现（清单未覆盖，建议补入或人工裁量）

1. **ch9 L76**："RDB 文件在网络上的传输要消耗主节点的出口带宽"——在 7.x 默认无盘口径下主节点侧是"RDB 流"；代价结论（出口带宽）两模式均成立，属措辞一致性问题（可改"RDB 流在网络上的传输"；同句"`BGSAVE` 的 fork"若求严谨可改"fork（生成 RDB 流）"）。非硬错，P2 级。
2. **ch9 fig-9-3.svg 步骤框**："④ 主节点 BGSAVE，fork 子进程生成 RDB"——图内文本仍是 6.x 落盘口径，与 MF-27 修正后的正文步骤 1 形成图文矛盾。**建议随 MF-27 同步改图**（例如"④ 主节点 fork 子进程，RDB 流直发副本连接（默认无盘）"）。
3. **ch8 fig-8-5.svg L26-27**："512B 块对齐 / 匹配扇区原子写"——图内文本与 MF-26 修正后的正文同病（"匹配扇区原子写"仍在把原子性当事实）。**建议随 MF-26 同步改图**（例如"512B 块对齐扇区粒度"+ 校验和检出，或删"原子"字样）。
4. **ch2 L79**："内存访问是纳秒级，而磁盘 I/O 是微秒到毫秒级，差着三到五个数量级"——与 MF-11 同精神的介质锚定表述，换算成立（百纳秒→百微秒=3、→十毫秒=5），可不动；若求全书口径统一可把"纳秒级"精确为"百纳秒"。非必改。
5. **outline.md 旁证**：ch6/ch8/ch9 的 outline.md 内部工作文件仍含对应错误认知（allow.everyone"默认值历史上是 true"、"匹配扇区原子写粒度"、"BGSAVE fork 出 RDB 传给从节点"）——outline 不进书稿（构建只用 chapter.md），无需改，仅提示源头可能在此。

## 证据源清单（去重）

- Kafka 源码 3.9 分支：KafkaServer.scala / BrokerServer.scala（raw.githubusercontent.com/apache/kafka/3.9/core/src/main/scala/kafka/server/）
- Kafka 官方文档：kafka.apache.org/42/configuration/topic-configs（min.insync.replicas 新释义）、/23/.../broker-configs（旧释义对照）、/37/security/authorization-and-acls/（allow.everyone 默认拒绝）、/11/streams/developer-guide/config-streams/（acks=all 官方措辞）、/books-and-papers（Kafka 论文作者序）
- Redis 官方：raw.githubusercontent.com/redis/redis/7.0/redis.conf 与 /redis/redis/6.2/redis.conf（repl-diskless-sync 翻转、appendonly no、everysec、save 3600）、redis.io/docs/latest/commands/zrange/（O(log(N)+M)）、redis.io/docs/latest/operate/oss_and_stack/management/replication/（PSYNC/复制 ID/diskless）、redis.io/docs/latest/operate/oss_and_stack/reference/cluster-spec/（PFAIL/FAIL 全文）
- MySQL 官方：dev.mysql.com/doc/relnotes/mysql/8.0/en/news-8-0-27.html（MTS 默认 4 worker）、dev.mysql.com/doc/refman/8.0/en/replication-options-replica.html（replica_parallel_workers 默认值沿革）、dev.mysql.com/doc/dev/mysql-server/latest/PAGE_INNODB_REDO_LOG.html（512B 块结构 + 只恢复完整记录组）
- PostgreSQL 官方：postgresql.org/docs/8.3/wal-reliability.html（部分写/扇区语境）；pgpedia.info/t/torn-page.html
- Linux/内核：hikunpeng.com 官方调优文档（read_ahead_kb 默认 128KB）、lkml 内核 sysfs 规范 RFC（128KB 起步、顺序负载可调 4–8MB）、kernel-internals.org/io/readahead
- AWS：docs.aws.amazon.com/msk/latest/developerguide/msk-acls.html 与 msk-default-configuration.html（Apache 默认拒绝 vs MSK 预置 true）
- Confluent：docs.confluent.io/platform/7.5/installation/license.html 与 confluent-community-license-faq（Cluster Linking 归 Enterprise）
- 论文/出版方：microsoft.com/en-us/research/event/netdb-2011/program/（Athens + 作者序）、MSR 存档 Kafka.pdf、oreilly.com 书页（HPMySQL 4e 作者）、gist.github.com/jboner/11349918 镜像（Jeff Dean 延迟数字）、KRaft 真实日志 5 源（digitalocean.com / CSDN×2 / dev.to / github.com/AutoMQ/automq/issues/2833）
