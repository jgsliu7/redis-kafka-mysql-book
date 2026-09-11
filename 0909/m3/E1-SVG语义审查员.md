# E1 SVG 语义审查报告

**审查人**：SVG 语义审查员  
**审查范围**：57 张 SVG 插图（ch1–ch10，`chapters/*/diagrams/fig-*.svg`）  
**审查方法**：逐图读源码 + 查正文对应段落 + 对照 `docs/SVG画图说明.md` + 交叉验证 round-4 已知发现  
**基线版本**：Redis 7.x / MySQL 8.0.x / Kafka 3.x

---

## 0. 总评

**状态**：🟢 PASS（发现 0 个 P0/P1 新问题）

57 张 SVG 全部通过语义审查。本轮确认了 round-4 已提出的 3 个 CONFIRMED 问题的当前状态（G1 已隐式修复，G2/G3 原判断有误），未发现新的流程/数值与正文打架的 P0/P1 问题。详细见 §3。

---

## 1. SVG 全清单（57 张）

| 图号 | 标题 | 正文引用位置 | 语义状态 |
|------|------|------------|---------|
| fig-1-1 | 后端基础设施三种核心范式 | ch1:27 | 🟢 通过 |
| fig-1-2 | 五维度定位雷达图 | ch1:119 | 🟢 通过 |
| fig-1-3 | 全书章节结构地图 | ch1:187 | 🟢 通过 |
| fig-2-1 | SDS 与 C 字符串内存布局 | ch2:38 | 🟢 通过 |
| fig-2-2 | 跳表多层索引与查找路径 | ch2:49 | 🟢 通过 |
| fig-2-3 | 渐进式 rehash 双表搬迁 | ch2:60 | 🟢 通过 |
| fig-2-4 | ziplist 连锁更新与 listpack 消除 | ch2:67 | 🟢 通过 |
| fig-2-5 | Redis 五种底层数据结构与升级路径 | ch2:82 | 🟢 通过 |
| fig-2-6 | InnoDB B+ 树三层结构 | ch2:97 | 🟢 通过 |
| fig-2-7 | Kafka RecordBatch V2 字段布局 | ch2:131 | 🟢 通过 |
| fig-2-8 | 三家通信协议对比 | ch2:176 | 🟢 通过 |
| fig-3-1 | 启动与关闭状态机对称 | ch3:25 | 🟢 通过 |
| fig-3-2 | Redis 启动四段式时序 | ch3:45 | 🟢 通过 |
| fig-3-3 | Redis 关闭流程 | ch3:58 | 🟢 通过 |
| fig-3-4 | InnoDB 崩溃恢复时序 | ch3:93 | 🟢 通过 |
| fig-3-5 | Kafka 三层网络架构 | ch3:156 | 🟢 通过 |
| fig-3-6 | Kafka 受控关闭时序 | ch3:169 | 🟢 通过 |
| fig-4-1 | 存储层次延迟对数轴 | ch4:42 | 🟢 通过 |
| fig-4-2 | Redis LRU 采样淘汰与 LFU 计数器 | ch4:87 | 🟢 通过 |
| fig-4-3 | Redis 持久化数据流 | ch4:114 | 🟢 通过 |
| fig-4-4 | InnoDB 缓冲池三分链表 | ch4:148 | 🟢 通过 |
| fig-4-5 | MySQL 一次写操作全链路时序 | ch4:162 | 🟢 通过 |
| fig-4-6 | Kafka 零拷贝数据流 | ch4:210 | 🟢 通过 |
| fig-5-1 | Redis 命令处理流水线 | ch5:57 | 🟢 通过 |
| fig-5-2 | redisObject type/encoding 解耦 | ch5:66 | 🟢 通过 |
| fig-5-3 | THD 贯穿 MySQL 三层 | ch5:99 | 🟢 通过 |
| fig-5-4 | MySQL Handler API 可插拔引擎 | ch5:124 | 🟢 通过 |
| fig-5-5 | Kafka Reactor + RequestChannel 线程模型 | ch5:151 | 🟢 通过 |
| fig-5-6 | Kafka Log 复用 | ch5:180 | 🟢 通过 |
| fig-5-7 | 三层统一视角对照 | ch5:211 | 🟢 通过 |
| fig-6-1 | 安全四维在一次请求链路上的分工 | ch6:27 | 🟢 通过 |
| fig-6-2 | Kafka 同一 Broker 监听器分层 | ch6:84 | 🟢 通过 |
| fig-6-3 | Redis ACL 认证+授权时序 | ch6:103 | 🟢 通过 |
| fig-6-4 | MySQL 五级权限表层级检查 | ch6:118 | 🟢 通过 |
| fig-7-1 | 单点到集群演进路径 | ch7:48 | 🟢 通过（见§2.1） |
| fig-7-2 | Redis Cluster 16384 槽分布与路由 | ch7:79 | 🟢 通过 |
| fig-7-3 | MySQL 主从复制拓扑 | ch7:104 | 🟢 通过 |
| fig-7-4 | Kafka 分区与副本拓扑 | ch7:149 | 🟢 通过 |
| fig-7-5 | 三软件故障转移决策流程 | ch7:209 | 🟢 通过 |
| fig-8-1 | 三家数据真正存放在哪里 | ch8:37 | 🟢 通过 |
| fig-8-2 | RDB 文件布局 | ch8:70 | 🟢 通过 |
| fig-8-3 | AOF 重写与混合持久化双缓冲 | ch8:101 | 🟢 通过 |
| fig-8-4 | InnoDB 16KB 数据页内七段布局 | ch8:140 | 🟢 通过 |
| fig-8-5 | 脏页刷盘与崩溃恢复路径 | ch8:157 | 🟢 通过 |
| fig-8-6 | Kafka 分区到日志段三个主要文件 | ch8:176 | 🟢 通过 |
| fig-8-7 | Kafka Tiered Storage 日志段生命周期 | ch8:239 | 🟢 通过 |
| fig-8-8 | 存储格式设计决策树 | ch8:331 | 🟢 通过 |
| fig-9-1 | 数据同步四个子问题框架 | ch9:27 | 🟢 通过 |
| fig-9-2 | 状态机复制模型 | ch9:32 | 🟢 通过 |
| fig-9-3 | Redis PSYNC2 全量+部分重同步 | ch9:78 | 🟢 通过 |
| fig-9-4 | Redis 复制积压缓冲区与 offset | ch9:96 | 🟢 通过 |
| fig-9-5 | MySQL 异步/半同步复制与 GTID | ch9:146 | 🟢 通过（见§2.2） |
| fig-9-6 | MySQL 多线程并行复制与 MGR 共识 | ch9:181 | 🟢 通过 |
| fig-9-7 | Kafka LEO/HW + leader epoch | ch9:224 | 🟢 通过（见§2.3） |
| fig-10-1 | 存储层次对照 | ch10:67 | 🟢 通过 |
| fig-10-2 | 实践者选型问题图 | ch10:118 | 🟢 通过 |
| fig-10-3 | 从使用者到设计者四个阶段 | ch10:164 | 🟢 通过 |

**合计**：57 张，🟢 57 张，🟠 0 张，🔴 0 张

---

## 2. 逐图语义问题

### 2.1 fig-7-1 CAP 立场（原 round-4 G1 跟进）

**原 round-4 发现**：图标"偏 AP"与正文 ch7:86"本书不作绝对 AP/CP 一刀切"矛盾。

**本轮审查结论**：**G1 已隐式修复，无需改图。**

fig-7-1 当前 Redis Cluster 框底部文字为"异步复制仍有丢写窗口，少数派超时后停写（见 7.2.3 节）"。此表述：
- 准确描述了异步复制有丢写窗口（AP 倾向）
- 补充了"少数派超时后停写"（CP 行为）
- 与 ch7:86 的审慎立场一致
- 与 ch9 的"偏 AP 倾向"描述也兼容（正常时偏 AP，分区时行为受限）

当前 SVG 语义正确，无需改动。round-4 的 G1 判定已过时。

---

### 2.2 fig-9-5 半同步 ACK 两档（原 round-4 G3 跟进）

**原 round-4 发现**：图只画 AFTER_COMMIT 顺序，但标注并列 after_sync/after_commit，AFTER_SYNC 是"先 ACK 再 commit"顺序相反。

**本轮审查结论**：**G3 判定有误，原图语义正确。**

检查 fig-9-5 源码：
- 存在一条**虚线半同步 ACK 回路箭头**（从 Replica relay log 框 → 指向 Primary 的半同步 ACK 等待框）
- 标注为"半同步 ACK 回路（从 → 主，仅半同步模式启用）"
- 底部小字说明："两档：AFTER_COMMIT（图示）/ AFTER_SYNC"

图中的 ACK 回路箭头方向正确（Replica → Primary），正确表达了半同步语义。"两档"信息以小字附注提供，不要求图中同时画两套完整流程。SVG 语义无问题。

---

### 2.3 fig-9-7 leader epoch 截断（原 round-4 G2 跟进）

**原 round-4 发现**：请求/响应 epoch 写成 1/2 跨值比较，endOffset 与"epoch 起点"混淆。

**本轮审查结论**：**G2 原判断有误，图语义正确。**

fig-9-7 下半部分（三栏 epoch 截断场景）：

| 元素 | SVG 中的值 | 与正文对照 |
|------|-----------|---------|
| 老 Leader A 的 epoch | epoch=1 | ch9:224 "leader epoch 标识任期边界" ✓ |
| A 的日志 | m0 m1 m2 m3 m4 | 同上，epoch=1 任期内的日志 ✓ |
| 新 Leader B 的 epoch | epoch=2 | ch9:224 "epoch=2 新任期" ✓ |
| B 的日志 | m0 m1 m2 m3' | B 接管后新写 m3' ✓ |
| A 复活发 FETCH | last_fetched_epoch=1, fetch_offset=5 | ch9:225 描述一致 ✓ |
| B 回 | epoch=1, endOffset=3 | "epoch 1 结束位点=3" ✓ |
| A 截断 | 截断 off≥3 | "截断不一致尾部 m3 m4" ✓ |

图题明确标注"② leader epoch 定位并截断不一致尾部"，内容完全对应正文描述。语义正确。

---

## 3. 发现的问题汇总

**P0（必须修，流程/数值与正文打架）**：0 个

**P1（应修，节点关系不清/标注歧义）**：0 个

**P2（建议改，优化可读性）**：0 个

**本轮无新发现问题。**

---

### 3.1 对 round-4 三个 CONFIRMED 问题的终审裁定

| 原编号 | 原问题 | 本轮结论 |
|--------|--------|---------|
| G1 | fig-7-1 "偏 AP" 与正文矛盾 | **已隐式修复**：图当前用描述性文字（丢写窗口+超时停写），不贴标签，与正文审慎立场一致 |
| G2 | fig-9-7 leader epoch 截断歧义 | **原判断有误**：图完整展示了三栏（epoch=1/2/截断逻辑），与正文完全对应，epoch 值使用正确 |
| G3 | fig-9-5 半同步两档只画一档 | **原判断有误**：ACK 回路方向正确（Replica→Primary），"两档"以附注小字说明，图文无打架 |

**三个原 CONFIRMED 问题全部终审裁定为：语义正确。**

---

## 4. 审查详情摘要

### 4.1 箭头方向（57 图全覆盖）

| 检查项 | 结果 |
|--------|------|
| 时序图消息箭头方向正确 | 🟢 全部通过 |
| 流程图步骤箭头方向正确 | 🟢 全部通过 |
| 状态机状态转移箭头方向正确 | 🟢 全部通过 |
| 层级图中层间连接箭头方向正确 | 🟢 全部通过 |
| 因果/数据流箭头方向正确 | 🟢 全部通过 |
| ACK/响应回程箭头方向正确（从从到主） | 🟢 fig-9-5/9-6 等均正确 |

### 4.2 流程顺序（时序图全覆盖）

| 图号 | 检查内容 | 结果 |
|------|---------|------|
| fig-3-2 | Redis 启动四段：配置→基础设施→数据恢复→事件循环 | 🟢 顺序正确 |
| fig-3-3 | Redis 关闭：清理子进程→刷 AOF→SAVE/NOSAVE→关连接→exit | 🟢 顺序正确 |
| fig-3-4 | InnoDB 恢复：checkpoint LSN→扫 redo→重放→undo→mysqld ready | 🟢 顺序正确 |
| fig-3-6 | Kafka 受控关闭：SIGTERM→通知 Controller→Leader 迁移→回执→exit | 🟢 顺序正确 |
| fig-4-5 | MySQL 写：UPDATE请求→改缓冲池→写 redo→flush→双写→正式页→checkpoint | 🟢 顺序正确 |
| fig-6-3 | Redis ACL：认证一次→会话中每命令授权（GET 放行/FLUSHALL 拒绝） | 🟢 顺序正确 |
| fig-9-3 | PSYNC2：重连→比对→部分分支或全量分支→offset 追平 | 🟢 顺序正确 |
| fig-9-5 | MySQL 复制：写 binlog→半同步等待→dump→relay log→回放→回 ACK | 🟢 顺序正确 |

### 4.3 数值标注核查

| 图号 | 标注值 | 正文对照值 | 结果 |
|------|--------|---------|------|
| fig-7-2 | 槽：0–5460 / 5461–10922 / 10923–16383，总和 5461+5462+5461=16384 | ch7:77 "16384 个槽" | 🟢 一致 |
| fig-8-2 | RDB version=0010（4B），magic=REDIS | ch8:62 "version 10 = Redis 7.0" | 🟢 一致（ASCII 十进制 v10 = Redis 7.0） |
| fig-8-4 | FIL Header 38B | ch8:141 "七段"（FIL Header 为第一段） | 🟢 一致 |
| fig-2-7 | RecordBatch V2 header 61 字节 | ch2:132 "61 字节头部" | 🟢 一致 |
| fig-4-4 | LRU New 5/8 / Old 3/8 | ch4:148 "New 5/8, Old 3/8" | 🟢 一致 |
| fig-4-2 | LFU Morris 计数器高 8 位/低 16 位 | ch4:88 "redisObject.lru 字段 24 bit"（8+16=24） | 🟢 一致 |
| fig-8-6 | .index 条目 8B（offsetDelta 4B + position 4B） | ch8:176 "相对偏移量 4B · 物理位置 4B" | 🟢 一致 |
| fig-7-4 | ISR=Broker 1/2/3（Partition 0）；Broker 3 移出 ISR（Partition 1） | ch7:149 "ISR 动态门槛" | 🟢 一致 |
| fig-9-4 | backlog 窗口：最老=280，新写=520，replica offset=330 | ch9:94 "backlog 窗口与主从 offset 的位置关系" | 🟢 一致 |

### 4.4 节点关系核查（重点图）

| 图号 | 关系类型 | 检查点 | 结果 |
|------|---------|--------|------|
| fig-7-1 | Redis 演进 | 主从复制→Sentinel→Cluster，三步演进 ✓；红字标"丢写窗口+超时停写" ✓ | 🟢 正确 |
| fig-7-5 | 故障决策 | Redis Gossip+epoch→MySQL XCom→Kafka Controller+ISR，三路并行 ✓；红箭头标注各限制条件 ✓ | 🟢 正确 |
| fig-9-7 上 | LEO/HW 时序 | Leader LEO=5，Follower LEO=2，HW=min(5,2)=2 ✓；FETCH 箭头从 Follower→Leader ✓ | 🟢 正确 |
| fig-9-7 下 | epoch 截断 | epoch=1 vs epoch=2 三栏并列 ✓；截断位点=3 ✓ | 🟢 正确 |
| fig-8-4 | InnoDB 页结构 | 七段顺序 FIL Header→Page Header→Inf/Sup→User Records→Free Space→Page Directory→FIL Trailer ✓ | 🟢 正确 |
| fig-5-6 | Kafka Log 复用 | 消费者 FETCH 与 Follower FETCH 走同一 ReplicaManager.fetchMessages() 入口 ✓ | 🟢 正确 |
| fig-4-5 | MySQL WAL | redo 先于脏页刷盘（箭头指向 redo→双写→正式页）✓；checkpoint 推进 ✓ | 🟢 正确 |
| fig-9-6 | MGR vs 并行复制 | 左：LOGICAL_CLOCK 协调器→并行 worker；右：XCom 多数派确认 ✓ | 🟢 正确 |

---

## 5. 总账

```
审查范围：57 张 SVG
P0 问题：0 个（本轮新发现）
P1 问题：0 个（本轮新发现）
P2 问题：0 个（本轮新发现）

round-4 CONFIRMED 裁定：
  G1（fig-7-1 CAP 矛盾）：已隐式修复，语义正确
  G2（fig-9-7 epoch 截断歧义）：原判断有误，语义正确
  G3（fig-9-5 半同步两档）：原判断有误，语义正确

语义审查结论：🟢 57/57 张通过
几何审查（svg_audit.py）：由 svg-checker agent 独立执行
```

---

## 附录：57 图快速索引

```
ch1: fig-1-1, fig-1-2, fig-1-3
ch2: fig-2-1 ~ fig-2-8（8 图）
ch3: fig-3-1 ~ fig-3-6（6 图）
ch4: fig-4-1 ~ fig-4-6（6 图）
ch5: fig-5-1 ~ fig-5-7（7 图）
ch6: fig-6-1 ~ fig-6-4（4 图）
ch7: fig-7-1 ~ fig-7-5（5 图）
ch8: fig-8-1 ~ fig-8-8（8 图）
ch9: fig-9-1 ~ fig-9-7（7 图）
ch10: fig-10-1 ~ fig-10-3（3 图）
合计：3+8+6+6+7+4+5+8+7+3 = 57 ✓
```
