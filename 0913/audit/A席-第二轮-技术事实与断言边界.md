# 0913 三席核实 · A 席报告（第二轮：技术事实与断言边界）

> 状态：已完成 · 判定 11/11 存在、11/11 改法认可（5 条附修正/微调）
> 基线更正确认：本席独立复核 git log（commit e6c440f，2026-09-13 12:14），第一轮 G1–G14 确已全部落地现行工作区。兼容性判断均按「R2 整段替换是否回退/覆盖第一轮已落地改文」。
> 证据等级：Kafka 侧一手源码逐行核对（/tmp 缓存：BrokerServer.scala、KafkaRaftServer.scala、BrokerMetadataPublisher.scala、SharedServer.scala，apache/kafka 3.9.0 tag）；Redis 侧一手源码（dict.c、evict.c、db.c，redis/redis 7.0.0 tag）；InnoDB 侧源码记忆+官方文档常识级（条目内标注）。

## 逐条判定

**R2-01 | 存在：是 | 引文：逐字 | 建议：认可 | ch2:63**
桶号数学经 Redis 7.0.0 dict.c 一手验证：`h = dictHashKey(d, de->key) & DICTHT_SIZE_MASK(ht_size_exp[1])`，旧 size=4 时桶 2 即哈希低两位为 10，新 size=8 只多取一位，故只能落桶 2（010）或 6（110）——现文「分别落在不同的桶里」与三个键互异不可能成立。改稿技术正确、保留「非整桶平移 + 开销摊还」原论点，且用「旧表从 4 扩到 8」限定推导条件，断言边界恰当。与第一轮无重叠，不回退。

**R2-02 | 存在：是 | 引文：逐字（SVG 文本节点抽取式拼接，内容一致）| 建议：认可 | fig-2-3.svg:39-51（箭头 35-36）**
现图 k7→新桶1、k3→新桶3、k9→新桶5，三个落点全部非法。改稿示例经源码核验合法：dictRehash 头插（`de->next = ht_table[1][h]; ht_table[1][h] = de`），沿旧链 k7→k3→k9 处理后，同落桶 2 的 k7/k9 链序确为 k9→k7；且 rehashidx 升序推进下，轮到旧桶 2 时新桶 2/6 必为空（此前只迁了旧桶 0/1，落新桶 0/4 与 1/5），与图中桶 0/1「已搬空」、k1 在新桶 0 完全自洽。改稿为布局规格而非现成 SVG，落地时须保留桶 0/1 已搬空、rehashidx=2 与「本次只搬这一个桶」注记。与第一轮无重叠。

**R2-10 | 存在：是 | 引文：逐字 | 建议：认可（与 R2-02 成组）| ch2:61**
现图把键同时画在旧桶 2（k7→k3→k9）与新表，严格按现图注「搬迁进行到一半的一个时刻」读即为自相矛盾（任一时刻键只在一处），须与 R2-02 成组落地为「前后对照」。新图注保留图号、双表主题与本次搬迁范围，无信息损失。

**R2-03a | 存在：是 | 引文：逐字（含图片行与图注 129-132）| 建议：认可但需微调措辞 | ch2:129-132**
fig-2-7 实读确认为功能分组：第二行排 baseTimestamp/maxTimestamp/lastOffsetDelta/recordsCount，第三行排 producerId/epoch/baseSequence，而磁盘真实顺序（KIP-98，表 2-1 即按此序）是 lastOffsetDelta 在两个时间戳之前、recordsCount 在 baseSequence 之后——现文「完整的字段排布」确会误导。改稿保留 V0/V1/V2 演进信息与 61 字节总量（8+4+4+1+4+2+4+8+8+8+2+4+4=61，与字段显示顺序无关，成立），真实顺序已由表 2-1 承载，图改「功能分组」是低成本正解。微调：图注「字段分组：按功能分组」语义重复，宜作「字段分组示意：按功能归类，不代表磁盘字节顺序」。兼容性：不波及 G5 已落地表行（ch2:125）与 G6 已落地 SVG:41。

**R2-03b | 存在：是 | 引文：逐字 | 建议：认可 | fig-2-7.svg:11**
仅在图内标题追加「，按功能分组」，与 R2-03a 图注互为印证，改动最小。与 G6（fig-2-7.svg:41）不重叠。

**R2-04 | 存在：是 | 引文：逐字（139-154 整节）| 建议：认可但需修正（两处信息损失需补回）| ch3:139-154**
现文「八阶段」线性序对 Kafka 3.9 KRaft 多处不成立，逐条对 3.9.0 源码核实：KafkaRaftServer.startup() 中 `controller.foreach(_.startup())` 先于 broker（源码注释 "Controller component must be started before the broker component"）；kafkaScheduler.startup() 位于 BrokerServer.startup() 前段（:185）；`lifecycleManager.start`（注册+心跳，:370）先于日志管理器启动；LogManager 创建即带注释「不启动，需等追上元数据日志」，正式启动挂在首次元数据发布（BrokerMetadataPublisher `_firstPublish` 分支内 logManager.startup→replicaManager.startup→groupCoordinator.startup），恢复仅按需（unclean shutdown）；末段依次等 controller 确认追上→首次发布→setReadyToUnfence→authorizer endpoint futures→enableRequestProcessing——改稿每条技术断言均与源码对应成立。兼容性：改稿逐字保留 G9 已落地的 KRaft 就绪日志句与「以 3.9、node.id=0 为例」限定语，不回退第一轮。需修正两点：(1) 丢掉「分区要逐个校验/重建索引、没有批量捷径、只能靠多线程分摊」瓶颈成因解释（原第 3 阶段尾句），建议以带「按需」限定的压缩版补回；(2)「比如上万分区」实例丢失（次要）。落地注意：标题改后须同步 outline.md:99 与 docs/写作标准:267 的「八阶段」引用；R2-05 须同组落地。红线侧：「进程承担两种角色」与现行书稿存活用法一致（ch1:63），本席不判违禁，留红线席复核。

**R2-05 | 存在：是（条件性，随 R2-04 成立）| 引文：逐字 | 建议：认可 | fig-3-5.svg:86-88**
图内「三层网络是启动八阶段的第 4 阶段」直接复用正文将删除的框架，若 R2-04 落地则此行悬空。改稿两行说明与源码一致：SocketServer 在 BrokerServer.startup() 前段创建（:252，含端口绑定修正），enableRequestProcessing 在追上/发布/unfence/授权之后（:538）；「恢复就绪」亦成立（日志恢复在首次发布内同步完成后 firstPublishFuture 才完成）。

**R2-06 | 存在：是 | 引文：逐字（163 与 165 两段）| 建议：认可但需修正（两处小信息损失）| ch3:163-165**
「（处理完在途请求）」无源码依据：BrokerServer.shutdown() 先 `stopProcessingRequests()`（注释 "stop accepting any more connections and requests"，关闭现有连接），随后才关请求处理线程池与各组件，无排空保证；在途请求可能已执行未回包，也可能未执行，客户端只能看到连接中断。「停控制器→停副本管理」顺序在 KRaft 组合进程下也不成立（KafkaRaftServer.shutdown() 注释 "In combined mode, we want to shut down the broker first"，broker 先关、controller 后关；纯 Broker 进程则无控制器可停——现顺序更像 ZK 模式 KafkaServer 残留）。改稿各断言（组件关闭顺序、「受控关闭协调 Leader 迁移并等待 Controller 批准」、尚未迁移分区的选举语义）均与源码吻合，且与 fig-3-6 的「④ 允许退出回执」比对现文更一致。需修正：(1) 建议补回「Controller 在会话超时后发现」机制（现图 fig-3-6 也有「靠心跳超时才发现」，正文反而变虚了）；(2)「清临时文件和锁」细节丢失（可接受）。

**R2-07 | 存在：是 | 引文：逐字（SVG 文本抽取）| 建议：认可但需小修正 | fig-4-2.svg:46-67**
正文 ch4:81（已含第一轮后文本）明确「持续维护的淘汰池，再从池中选择最久未用的键」，图却把 5 个当轮样本标为「采样池」并直接从中选 k11，砍掉了会改变决策结果的持久候选池——图文矛盾实锤。改稿机制逐条对 7.0.0 evict.c 核验成立：EVPOOL_SIZE=16、样本按空闲时间插入既有池并保留优者、从池尾找「仍存在」（dictFind 校验）的最大空闲键、「空闲时间估计值」兼容 LFU 逆频次口径、以「删除键」替代绑定 DEL 的写法避开 lazyfree 争议。小修正：「随机抽取最多 N 个」不准确——采样恒为 N 个，是「进入候选池的最多 N 个」，且下一行「保留较长的键」已表达选择性，建议改回「随机抽 N 个键」。兼容性：只动 LRU 左半区，与 G10 已落地的 LFU 修正（fig-4-2.svg:79-86）无文本重叠；落地时须叮嘱执行者不得扰动 79-86 行。

**R2-08 | 存在：是 | 引文：逐字（85 与 99 两处）| 建议：认可但需小修正 | fig-4-4.svg:85,99**
Flush List 按 oldest_modification LSN 排序（ch4:144 自身表述正确）只决定取页顺序，各脏页写回各自表空间页位是随机 I/O，「顺序刷盘/顺序写回」把 WAL 顺序写优势错误延伸到数据页写回，且与 ch3:128「刷盘是随机 I/O」直接冲突（InnoDB 结论为源码记忆+文档常识级：buf0flu.cc 刷表序、innodb_flush_neighbors 0/1/2 语义，置信度高）。改稿两处标签正确，「崩溃恢复按需重放 redo log」比原「重放补齐」更准（仅从 checkpoint LSN 起且跳过已新页）。小修正：第一处标签建议保留「按此队列取页」的取页顺序语义（如「后台线程按此队列取页刷回，使 Checkpoint 向前推进」）——Flush List 的存在意义正在于决定取页顺序；此为增强非阻塞。

**R2-09 | 存在：是 | 引文：逐字 | 建议：认可 | ch6:99**
经 7.0.0 db.c 一手核验：scanGenericCommand 仅按 MATCH/TYPE/过期过滤，全程无 ACL 键模式过滤；ACL 键模式只作用于经 keyspec 提取的键参数，SCAN 无键参数——`~keys:*` 下用户仍可枚举全部键名（SCAN 属 @keyspace/@read/@slow，不在 @dangerous，+@read 即授予），无键参数的全库操作同理。现文「这让多租户场景下不同应用可以按前缀隔离」从「对键参数的模式检查」越界推出租户隔离，是真实的多租户误配风险。改稿保留有效能力（GET/SET 级读写限定）、补出边界、给出可操作补救（命令权限限制枚举与全库操作），未反向过强；与上文 alice 实例及「+@read -@dangerous」段落完全自洽。

## 总表

| 条目 | 存在 | 引文 | 建议 | 现文锚点 | 与第一轮兼容 |
|---|---|---|---|---|---|
| R2-01 | 是 | 逐字 | 认可 | ch2/…/chapter.md:63 | 无重叠 |
| R2-02 | 是 | 逐字(抽取) | 认可 | ch2/…/fig-2-3.svg:39-51 | 无重叠 |
| R2-03a | 是 | 逐字 | 认可但需微调图注措辞 | ch2/…/chapter.md:129-132 | 不波及 G5/G6 落地行 |
| R2-03b | 是 | 逐字 | 认可 | ch2/…/fig-2-7.svg:11 | 不波及 G6(:41) |
| R2-04 | 是 | 逐字 | 认可但需修正(补回瓶颈成因句) | ch3/…/chapter.md:139-154 | 逐字保留 G9 句，不回退 |
| R2-05 | 是(随R2-04) | 逐字 | 认可 | ch3/…/fig-3-5.svg:86-88 | 无重叠 |
| R2-06 | 是 | 逐字 | 认可但需修正(补回心跳/会话超时机制) | ch3/…/chapter.md:163-165 | 与 G8 异节无重叠 |
| R2-07 | 是 | 逐字(抽取) | 认可但需小修正(「最多N个」表述) | ch4/…/fig-4-2.svg:46-67 | 不动 G10 落地区(79-86) |
| R2-08 | 是 | 逐字 | 认可但需小修正(宜保留取页顺序语义) | ch4/…/fig-4-4.svg:85,99 | 无重叠 |
| R2-09 | 是 | 逐字 | 认可 | ch6/…/chapter.md:99 | 无重叠 |
| R2-10 | 是 | 逐字 | 认可(与 R2-02 成组) | ch2/…/chapter.md:61 | 无重叠 |

## 清单外（核实中撞见、报告未提的问题）

1. **fig-2-7.svg:45 遗留旧表述**：maxTimestamp 标注仍为「8B · 批最晚时间戳」，而 G5 已落地的表行采用「批内最大时间戳（CreateTime）」，且第一轮 G5/G6 核心理由正是拒绝「最早/最晚」端点框架（生产者时间戳不必随记录位置递增）。G6 只修了 baseTimestamp（:41），此行漏网，建议同步改为「批内最大时间戳」。
2. **R2-04 落地的文档联动**：chapters/03-lifecycle/outline.md:99 仍写「启动链路（八阶段…）」，docs/写作标准-讲清楚一个设计.md:267 以「八阶段启动」作反面案例引用本章——正文改后两处需同步，否则外部文档引用悬空（属落地工序，非书稿错误）。
3. **fig-2-3.svg:51 含一个空文本节点**（`<text …> </text>` 紧贴桶 7 标签），R2-02 重绘该图时应顺带清掉，避免渲染歧义。
4. ch3:145 现文把「校验日志段、恢复活跃段、重建索引」写成每次启动的无条件动作，与 LogManager 仅在 unclean shutdown/索引缺失时恢复的源码行为不符——已由 R2-04 改稿的「按需要」限定覆盖，无需另立条目，仅确认 R2-04 落地时勿丢失该限定词。

## 取证文件

/tmp/BrokerServer.scala、/tmp/KafkaRaftServer.scala、/tmp/BrokerMetadataPublisher.scala、/tmp/SharedServer.scala（apache/kafka 3.9.0）、/tmp/dict.c、/tmp/evict.c、/tmp/db.c（redis/redis 7.0.0）。书稿锚点均以现行工作区为准。
