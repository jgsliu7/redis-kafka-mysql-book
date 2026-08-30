# 第三轮修复日志：技术正确性（2026-08-30）

流水线：5 个找茬镜头（architect-reviewer 技术断言 / source-contributor 实现细节 / version-shelf-life 版本口径 / number-provenance 数字溯源 / command-runnable 可运行性）60 条发现 → 3 个复核 agent 独立裁定 → 仅执行 3/3 全票项 38 条（离散项全票；M1/M2/M3 等由 ≥2 席 endorse 的措辞合成）→ 单人 Edit 执行 → 重建双 HTML → 改后 3 agent 验证（技术正确性 / 跨章一致性 / SVG 几何）。

## 执行明细（38 过门项 + 3 连带一致性）

### ch2 chapters/02-data-structures-protocols/chapter.md
- **R9** SDS：补 sdshdr5 细节（整个头 1 字节、长度嵌 flags 高 5 位）。
- **R10** intset 类型升级类比改"listpack → hashtable"（原"ziplist → listpack 或 hashtable"混入格式更替）。
- **M1**（spot2）行格式溢出：改整行判定口径（约 8126 字节、最长变长列整列外移、20 字节指针、≤约 40 字节 TEXT/BLOB 留行内）。
- **K15** 表 2-1 batchLength：补"除最前 12 字节（baseOffset 与 batchLength 自身）外"。
- **R6** RESP：长度信息两处（数组元素个数 + 批量字符串内容长度），非协议头。

### ch3 chapters/03-lifecycle/chapter.md
- **R12** SIGCHLD 只标记退出，由 serverCron 非阻塞 waitpid 回收（原"SIGCHLD 回收子进程"）。
- **R2** 关闭第一步：直接杀掉子进程不等（原"要么等它完成，要么杀掉""等它完成更干净"与源码 beforeShutdown 行为相反）。
- **M4** 关闭慢根因：改从库侧（从库等 SQL 线程停在事件组边界；主库直接断 dump 线程不等从库拉 binlog）。
- **K3** 受控关闭 Leader 任免传达分 ZK（LeaderAndIsr 请求）/KRaft（写元数据日志）两模式。
- **R2 连带** 容器段：优雅关闭不等重写子进程，耗时来自重写操作本身（fork 页表/COW）；保留 preStop BGSAVE 建议。

### fig-3-3.svg（连带）
- 原图"是 → 等待其完成，或杀掉子进程"与 R2 修正矛盾，改"是 → 直接杀掉，不等它完成"。

### ch4 chapters/04-memory-disk/chapter.md
- **N1** 图 4-1 解读分介质：机械盘顺序→随机延迟差两个数量级；SSD 单次延迟同量级、差距在吞吐（带宽 vs IOPS）与写放大。
- **M10** redo log"物理页变更日志"→"物理到页、逻辑到操作"的混合日志。

### fig-4-1.svg（N1 图）
- SSD 顺序读柱 ~1μs → ~100μs（与随机柱等长）；删"顺序比随机快 100×"标注，换"延迟同量级/差距在吞吐"；右下结论框改三行（机械盘省寻道延迟差两档 / SSD 差距转向吞吐与写放大）。

### ch5 chapters/05-layered-architecture/chapter.md
- **M11** Handler 事务方法补 handlerton 括注（commit/rollback 转发给引擎级插件结构）。
- **K14** 版本协商：客户端先发 ApiVersions 问区间，之后由客户端选定版本（原"Broker 选最高版本回应"）。
- **K1** "3.9 起 Tiered Storage 引入"→"正式 GA（3.6 起以早期版本引入）"，与 ch1/ch8 口径对齐。

### ch6 chapters/06-security/chapter.md
- **K5** SCRAM 按 RFC 5802 改写：客户端持有密码但不上网、服务端只存加盐迭代哈希派生密钥；PLAIN 对比改为"密码在网络上走"。
- **R8** ACL 类别"几个语义组"→"二十来个类别（语义组 + 性能分桶）"。
- **C3** resetpass 语义按源码改写（acl.c：清空密码并移除 nopass，此后无密码无法认证 default）。
- **R7** ACL LOG 删"和参数"（不记命令参数）。
- **K6** Authorizer 日志：被拒 INFO / 放行 DEBUG，默认级别只看得到拒绝（kafka.authorizer.logger）。

### ch7 chapters/07-cluster/chapter.md
- **C2** 全量同步期间命令存"连接专属复制缓冲区"（非 backlog；backlog 是常驻环形缓冲服务部分重同步）。
- **M2** 半同步改写：防住"binlog 没发出去主就没了"；防不住超时降级窗口与晋升非 ACK 副本；保留"最后一段未覆盖的差距"锋芒。
- **M3+M8** MTS 补版本口径（8.0.27 起默认开启、replica_parallel_workers 默认 4、更早默认 0）+ 锁区间标记（last_committed / sequence_number）划定并行窗口。

### fig-7-1.svg
- **K10** "内嵌 Raft · 单进程强一致"→"内嵌 Raft · 控制器组多数派强一致"。

### ch8 chapters/08-storage-format/chapter.md
- **K12+N7** V0/V1 开销 14/22 字节补"不含最外层 12 字节消息框，同口径 26/34"；压缩收益改"文本近上限、二进制次之、已压缩趋近 1 倍"。
- **M6** 页内记录改"单向指针 next_record"（原"前后指针"）。
- **M1**（主 spot）Dynamic 溢出整行判定段（同 ch2 口径；保留 COMPACT 768 前缀对比）。
- **M7** 双写缓冲开关去"MySQL 8.0 给了选择"（innodb_doublewrite=OFF 早于 8.0 存在）；**M7-spot2**（8.6.4）同步去 "MySQL 8.0" 主语。
- **K11** V0/V1 压缩口径改"整包 wrapper 压缩（内条仍各带元数据）"（正文 + 表 8-1）。
- **K7** Tiered Storage 消费者读远程段"流式读取、不重新物化成本地日志段"（原"拉取并缓存到本地 fetch-through 语义"）。

### ch9 chapters/09-data-sync/chapter.md
- **R5** 非确定性命令例 RANDOMKEY→EXPIRE。
- **C2** 全量同步步骤 2/4 与解读段：副本专属输出缓冲区 vs backlog 职责区分；节标题"传完补积压"→"传完补增量"（连带）。
- **M3** 单 SQL 线程补 8.0.27 限定。
- **M8** 组提交并行补锁区间标记括注。
- **C1** MGR 分布式恢复：clone 触发条件改"补差所需 binlog 已不可得"；group_replication_clone_threshold 默认值实为 int64 上限（原"默认 86,400 笔"错误）；**C1-spot2**（9.5）复述处同步。
- **K9** FETCH 读上界差别：消费者截在 HW 以下、Follower 可读到 LEO（replica_id 区分）。

### ch11 chapters/11-references.md
- **C9** [10] 删 #ctrlshutdown 死锚点（kafka 文档站已迁移为 JS 站，仅落地页可验证）。
- **C10** [15] 题名改"Kafka Documentation: Design / Implementation"（原题名"Network Threading Design"无对应页面）。
- **C8** [25] URL 补 /management/（原 404，新 200，已机械核验）。
- **K16** [27] KIP-101 年份 2015→2017。
- cwiki 短 URL 全部换为全题名 URL（均 200 核验）：[6] KIP-98、[21] KIP-833、[26] KIP-405、[27] KIP-101、[28] KIP-320。
- **题名更正披露**：[26] "Tiered Storage in Kafka"→"Kafka Tiered Storage"、[27] "Replication Protocol Revamp"→KIP-101 全名、[28] "Leader Epochs"→KIP-320 全名（原书题名系讹传，按 Confluence REST 检索到的真实题名更正）。

### fig-2-7.svg
- **K15 连带** batchLength 标签"4B · 总字节长"→"4B · 不含首 12B 总长"（61 字节头部含外框 12B 为既有豁免口径，保留）。

## 未过门（19 项，仅登记不改）

- 多数否决 11 项：含 R1（SipHash 版本）——后经机械核查（curl 官方文档）证明**书原表述正确**、多数派误判；N2/N3 同类（SSD 数字口径分歧被机械证据推翻/存疑维持原文）。
- 争议 2:1（语域类）8 项：登记留作者裁定。

## 机械核查仲裁记录（总调度仅做机械验证，不做语义判断）

- R1 SipHash：redis.io 协议/字典文档确认 4.0 起启用 → 书正确，不改（2:1 多数被推翻）。
- C3 resetpass：redis/redis unstable src/acl.c L1270-1273 注释 + L1333-1335 代码确认双效（清密码 + 移除 nopass）。
- C8：management/persistence/ 200 vs 原 URL 404。
- cwiki 五条 URL：Confluence REST 搜索取真实题名，全 200。
- C10：kafka.apache.org/documentation(.html) 对 curl 均为 JS TechDocs 壳（无内容链接），子路径 /documentation/design/ 等 404；仅落地页可验证 → 保守改题名对齐落地页。

## 改后验证（3 agent：技术正确性 / 跨章一致性 / SVG 几何）

**技术正确性（37 项逐条）**：36 PASS / 1 FAIL。多项为源码级核验（Redis 7.4.1 sds.h/acl.c/server.c、MySQL 8.0.39 handler.h/handler.cc、Kafka 3.9.0 AclAuthorizer.scala）。1 FAIL 已修：R12 的替换文本仍暗含"SIGCHLD 处理器存在"——Redis 7.x 全源码无 SIGCHLD 注册，回收纯靠 serverCron 轮询（checkChildrenDone → waitpid WNOHANG），已改为"子进程退出不由信号驱动，serverCron 每轮非阻塞 waitpid(WNOHANG) 轮询回收"。另采纳两处措辞级建议：K9 replica_id 区分改按取值表述（Follower 填 broker id / 消费者填 -1）；[25] 题名改"Redis Persistence（RDB 文件编码）"对齐 URL 实际页面（官方无字节级 RDB 规范，题名如实标注）。

**跨章一致性（10 组）**：9.5 组自洽。修 1 硬伤 + 2 轻微：fig-9-3.svg 全量同步分支"新写命令进入 backlog"未随 C2 改（改"连接专属复制缓冲"）；ch9:192 "fork RDB + backlog 补差" shorthand 改"期间增量补发"；fig-9-5.svg 底注半同步顺序补 AFTER_COMMIT（图示）/AFTER_SYNC（默认档）区分。登记不修：ch8 outline.md:98 工作稿旧口径（outline 不入书，build 只读 chapter.md）。

**SVG 几何（4 张）**：fig-2-7 / fig-3-3 / fig-7-1 PASS；fig-4-1 FAIL 1 处——新标注框底边削掉柱 4 端注顶部 2.5px（svg_audit 脚本漏检，playwright 渲染像素 A/B 抓出），按验证员预核方案上移收缩（y=252→248、h=36→32，双向净空 5.5/2.5px），并清理失去引用的死 marker arrow-red-3-6。

**本轮验证新证据**：8126（行内上限实测值）、40 字节（TEXT/BLOB 留行内）、handlerton commit/rollback 同名钩子（handler.h:2663-2665）、innodb_doublewrite 开关 5.6/5.7 即存在、ACL 类别恰 21 个、KIP-405 "production-ready since 3.9" + 3.6.0 EA release notes——全部与修改后表述吻合。
