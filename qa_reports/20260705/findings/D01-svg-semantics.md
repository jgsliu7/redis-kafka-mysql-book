# D01 SVG 语义审查报告

> 审查日期：2026-07-05
> 审查方法：读 SVG 源码 + 比对对应正文段落
> 审查范围：全部 52 张 fig-*.svg 插图

## 审查汇总

- 总 SVG 数：52
- 语义错误：1（图号与内容不匹配）
- 图文轻微不对应：0
- 语义正确：51

## 逐图发现

### 🔴 fig-8-7.svg / fig-8-8.svg 图号与引用内容互换

**文件路径**：
- `/Users/liu/dev/demos/redis-kafka-books/chapters/08-storage-format/diagrams/fig-8-7.svg`
- `/Users/liu/dev/demos/redis-kafka-books/chapters/08-storage-format/diagrams/fig-8-8.svg`

**问题**：SVG 内部自标图号与对应的正文描述互换。

**详细**：
- `fig-8-7.svg` 内部标题为"图 8-7　存储格式设计决策树"
- `fig-8-8.svg` 内部标题为"图 8-8 Kafka Tiered Storage 日志段生命周期"

但正文 `chapter.md` 中：
- 第 222 行：`![图 8-7 Kafka Tiered Storage 日志段生命周期](diagrams/fig-8-7.svg)` —— 描述为 Tiered Storage，实际 fig-8-7.svg 内容是决策树
- 第 316 行：`![图 8-8 存储格式设计决策树](diagrams/fig-8-8.svg)` —— 描述为决策树，实际 fig-8-8.svg 内容是 Tiered Storage

**正文对应**：`chapter.md` L222-L223（Tiered Storage 小节）、L316（决策树小节）

**建议**：交换两个 SVG 文件的文件名：`fig-8-7.svg` ↔ `fig-8-8.svg`，或将 markdown 中的图片链接交换。由于 SVG 内部自标图号（"图 8-7" 与 "图 8-8"）与文件名一致，更稳妥的做法是交换文件名以使其与 SVG 内部编号一致。

### ✅ 已核验语义正确（51 张）

以下 51 张 SVGs 经审查，箭头方向、流程顺序、节点角色与数量、图内数值、图文对应均正确：

| 文件 | 图注主题 | 核验要点 |
|------|---------|---------|
| ch01/fig-1-1.svg | 三种核心范式与代表软件 | 三列范式正确，电商场景流程方向正确，Redis→MySQL→Kafka 箭头方向匹配"读→写→发布→消费" |
| ch01/fig-1-2.svg | 全书章节地图 | 章节分组递进顺序正确，第 2→3→4 章递进、5→6→7 递进、8→9→10 递进 |
| ch01/fig-1-3.svg | 三款软件定位雷达 | Redis(5,3,2,1,2)、MySQL(2,2,5,5,5)、Kafka(3,5,3,4,1) 评分与正文表一致 |
| ch02/fig-2-1.svg | Redis 五种底层数据结构 | SDS/Dict/Skiplist/ziplist→listpack/Intset 五种齐全，升级路径箭头正确 |
| ch02/fig-2-2.svg | Kafka RecordBatch V2 字段布局 | Batch 级头部字段齐全，记录级差值编码说明正确 |
| ch02/fig-2-3.svg | 三款通信协议对比 | RESP/MySQL Binary/Kafka Req-Resp 三列对比，编码/批量/演进/人可读四维正确 |
| ch03/fig-3-1.svg | 启动与关闭：状态机重建与快照 | 三态循环正确，崩溃/kill-9 虚线回退箭头方向正确，三对矛盾准确 |
| ch03/fig-3-2.svg | Redis 启动四段式时序 | ①配置→②基础设施→③数据恢复→④事件循环四段顺序正确，AOF/RDB 分支正确 |
| ch03/fig-3-3.svg | Redis 关闭流程 | 触发→①子进程→②a SAVE/②b NOSAVE→③刷AOF→④关连接→⑤释放，SAVE/NOSAVE 分支正确 |
| ch03/fig-3-4.svg | InnoDB 崩溃恢复时序 | 读checkpoint→扫描redo→重放到缓冲池→undo回滚→恢复一致性，redo与undo方向相反正确 |
| ch03/fig-3-5.svg | Kafka 三层网络架构 | Acceptor→Processor→RequestQueue→Handler 四级正确，响应回路方向正确 |
| ch03/fig-3-6.svg | Kafka 受控关闭时序 | 受控关闭 ①通知→②迁移→③回执→④允许退出→⑤刷盘 时序正确，普通关闭对照正确 |
| ch04/fig-4-1.svg | 存储层次访问延迟对数轴 | L1~1ns, 内存~100ns, SSD顺序~1us, SSD随机~100us, 机械盘~10ms，标注 100x 和 10^5 正确 |
| ch04/fig-4-2.svg | Redis 近似 LRU + LFU | LRU 采样淘汰 5 个样本正确，LFU Morris 8 位计数器 + 衰减机制正确 |
| ch04/fig-4-3.svg | Redis 持久化数据流 | 命令→内存→RDB/AOF/混合三类路径正确，控制流与数据流箭头区分解说正确 |
| ch04/fig-4-4.svg | InnoDB 缓冲池三分链表 | Free/LRU(New 5/8+Old 3/8)/Flush 三分结构正确，midpoint 位置、晋升机制正确 |
| ch04/fig-4-5.svg | MySQL 写操作全链路时序 | WAL→改脏页→提交→双写→checkpoint 时序正确，`innodb_flush_log_at_trx_commit` 落盘标注正确 |
| ch04/fig-4-6.svg | Kafka 零拷贝数据流 | 传统 4 拷贝 4 切换 vs 零拷贝 2 DMA 2 切换对比正确，sendfile 路径正确 |
| ch05/fig-5-1.svg | Redis 命令处理流水线 | 6 步流水线（RESP→查表→ACL→执行→监控→存储）正确，client 结构体贯穿标注正确 |
| ch05/fig-5-2.svg | redisObject type/encoding 解耦 | type 列 5 种类型，encoding 列 7 种编码，ptr 指针连接，底部 key decision 正确 |
| ch05/fig-5-3.svg | THD 贯穿 MySQL 三层 | 8 步时序（连接→THD→SQL→转服务层→解析/优化→handler→读行→返回）正确，THD 横条贯穿三层 |
| ch05/fig-5-4.svg | MySQL Handler API 可插拔引擎 | 服务层(解析→优化→执行)→Handler API→InnoDB/MyISAM/Memory 三层结构正确 |
| ch05/fig-5-5.svg | Kafka Reactor + RequestChannel | Acceptor→Processor→RequestChannel(有界队列，回压标注)→Handler 正确，响应回路标注正确 |
| ch05/fig-5-6.svg | Kafka Log 复用：消费=复制路径 | 左右 Consumer+Follower 走同一条 handleFetchRequest→ReplicaManager→Log→sendfile 路径正确 |
| ch05/fig-5-7.svg | 三层统一视角对照 | Redis/MySQL/Kafka 三列映射交互/逻辑/存储三层正确，层间通信标注正确 |
| ch06/fig-6-1.svg | 安全四维分工 | 客户端→传输加密→认证→授权→执行→存储加密→磁盘 流程正确，审计旁路标注正确 |
| ch06/fig-6-2.svg | Kafka 监听器分层 | 内部 SASL_SSL/外部 SSL/控制面 KRaft 三条路径正确，共享安全内核标注正确 |
| ch06/fig-6-3.svg | Redis ACL 时序 | 认证阶段(①AUTH→②校验SHA-256→③OK) + 每命令授权(GET keys:1 通过, FLUSHALL 拒绝)正确 |
| ch06/fig-6-4.svg | MySQL 五级权限层级检查 | 全局→数据库→表→列→存储程序逐层收窄正确，SELECT phone 列级命中示例正确 |
| ch07/fig-7-1.svg | 单点到集群演进路径 | Redis (主从→Sentinel→Cluster)、MySQL (异步→半同步→MGR)、Kafka (Partition→ISR→KRaft) 三段演进正确 |
| ch07/fig-7-2.svg | Redis Cluster 16384 槽与路由 | CRC16(key) mod 16384 公式正确，3 节点槽范围分配正确，MOVED/ASK 两种语义+示例正确 |
| ch07/fig-7-3.svg | MySQL 主从复制拓扑 | Master(binlog)→Slave(IO线程→relay log→SQL线程) 流程正确，两段式正确 |
| ch07/fig-7-4.svg | Kafka 分区与副本拓扑 | 3 分区 3 副本，Partition 0 ISR 全在、Partition 1 Broker 3 踢出 ISR、Partition 2 Leader 在 Broker 3 正确 |
| ch07/fig-7-5.svg | 故障转移决策流程对比 | 三列决策路径正确，红色箭头标注"放弃可用性以保一致性"取舍节点正确 |
| ch08/fig-8-1.svg | 数据"真正住在哪里" | Redis(内存大/磁盘小)、MySQL(磁盘大/内存小)、Kafka(磁盘即全部) 三种权重正确 |
| ch08/fig-8-2.svg | RDB 文件布局 | magic→version→metadata→db-select→entries→EOF→CRC64 布局正确，变长四档编码正确 |
| ch08/fig-8-3.svg | AOF 重写与混合持久化 | fork→子进程写temp→主进程同时写旧AOF+rewrite_buffer→rename 原子替换时序正确 |
| ch08/fig-8-4.svg | InnoDB 16KB 页七段布局 | FIL Header→Page Header→Infimum/Supremum→User Records→Free Space→Page Directory→FIL Trailer 七段正确 |
| ch08/fig-8-5.svg | 脏页刷盘与崩溃恢复路径 | 正常：脏页→WAL→双写缓冲→正式页；恢复：校验→完整核对→redo重放；流程正确 |
| ch08/fig-8-6.svg | Kafka Segment 三件套 | Partition→Segment 链，.log(RecordBatch) /.index(稀疏8B条目) /.timeindex(12B条目) 及二分查找流程正确 |
| ch09/fig-9-1.svg | 数据同步四个子问题 | ①传播什么②怎么传播③到什么程度④断了怎么办 四分支正确，底部状态机复制主线正确 |
| ch09/fig-9-2.svg | 状态机复制模型 | 输入序列→三副本(Redis命令流/MySQL binlog event/Kafka消息日志)执行→相同终态 正确 |
| ch09/fig-9-3.svg | Redis PSYNC2 流程 | PSYNC→主比对→部分重同步(窗口内) vs 全量同步(窗口外) 分支正确，backlog 标注正确 |
| ch09/fig-9-4.svg | Redis backlog 环形缓冲 | 环形 8 格 backlog，master_repl_offset 和 replica offset 比对逻辑正确，窗口判定正确 |
| ch09/fig-9-5.svg | MySQL 异步/半同步+GTID | 主(事务→binlog→提交+/半同步等ACK→Dump线程)→从(IO→relay log→SQL→回ACK) 两段式正确 |
| ch09/fig-9-6.svg | MySQL MTS + MGR | 左：组提交并行回放 3 worker 正确；右：MGR XCom 多数派确认 3 成员 2/3 法定通过正确 |
| ch09/fig-9-7.svg | Kafka LEO/HW + leader epoch | Leader LEO=5, Follower LEO=2, HW=min=2 正确；leader epoch 截断脑裂场景 epoch=1/2 正确 |
| ch10/fig-10-1.svg | 五条共性规律递进 | 规律一为根→规律二/三/四/五分支服务正确，底部三软件印证带对应正确 |
| ch10/fig-10-2.svg | 实践者选型决策树 | Q1-Q4 四菱形正确，左右分支叶子节点正确，"借形不借器"收束正确 |
| ch10/fig-10-3.svg | 认知跃迁四层台阶 | L1→L2→L3→L4 拾级而上正确，前 9 章对应 L1→L2、第 10 章对应 L2→L3 标注正确 |

## 总体评价

52 张 SVGs 的语义质量高。箭头方向正确（marker 的 `orient="auto-start-reverse"` 确保方向准确），流程顺序与正文描述一致，节点角色与数量吻合，图内数值与正文核对无误，图文对应清晰。唯一发现的语义问题是第 8 章 fig-8-7 与 fig-8-8 的图文引用互换。

几何问题（越界/重叠/文字穿框）不属于本审查范畴，请参见 svg_audit.py 的几何报告。
