# Agent 应用存储现状调研报告

> 主题：验证"是否值得做一个面向 Agent 的轻量、嵌入式、统一存储"这一产品假设。
> 方法：deep-research 工作流（5 路并行搜索 → 抓取 → 对抗式核验）采集 **228 条独立 claims、28 个信源域、2024–2026**。综合阶段工作流两次卡死（核验→综合衔接点的重现性 bug），最终由主调度直接综合已采集 claims 完成。结论区分 **强证据 / 弱证据 / 推测**。

---

## 结论速览

| 假设 | 裁决 | 证据强度 |
|------|------|---------|
| ① Agent 真的需要关系/缓存/队列/文档/向量五类存储 | **理论成立，实践收缩到 1–2 个** | 强（多源） |
| ② 多存储部署成本是真痛点 | **成立，且可量化** | 强（含具体数字） |
| ③ 单 Agent 需要轻量全能嵌入式存储 | **成立，且已被部分验证**（sqlite-vec/LanceDB/本地文件） | 强 |
| **总体 go/no-go** | **条件性 GO**——但定位必须修正 | 推断（见 §7） |

一句话：**痛点真实、窗口存在，但"统一存储引擎"这个赛道已经拥挤（Postgres+pgvector、SurrealDB、LanceDB、Turso）；真正没人占住的不是"统一"也不是"向量"，而是"Agent 运行时原语（幂等/重放/checkpoint）+ 嵌入式零运维"，且目标应锁定 Postgres 太重、sqlite-vec 太弱的"单 Agent/本地"夹层。**

---

## 1. 假设①：五类存储需求是否真实存在？

**强证据：理论上是的。** 多个权威来源（AWS 最佳实践、Agent 架构博客、框架文档）一致指出，生产级 Agent 跨越 4–5 个存储类别：

- 短期记忆（会话/状态，类缓存）+ 长期记忆（向量召回）+ 结构化状态（关系/NoSQL）+ 制品（文件）+ 消息（队列）。〔aws.amazon.com / 多篇架构 taxonomy〕
- 典型生产栈确实多组件：n8n 官方 AI Starter Kit = n8n + Postgres + Redis + Qdrant **各自独立 Docker 服务**；"Agency 模式" = Postgres + 文件存储 + Pinecone；混合方案 = Redis + Postgres+pgvector + 后台 consolidation worker。〔forum / blog，多源印证〕

**但书（同样强）：实践中大多数团队把记忆塌缩成 1–2 个库。**

- "对很多团队来说，memory = 就是一个向量库"——并未真的搭五件套。〔blog〕
- LongMemEval 基准：单范式记忆系统（Mem0 49%、Zep 63.8%）检索准确率都不超过 ~64%——说明连"该用多种召回策略"都还没普及，五件套更是少数。〔primary benchmark〕

> 结论：**五类需求在架构上真实存在，但真实部署里是"理论五件套、实践一两件"。** 产品不能假设用户真的在跑五个库；痛点更多来自"想用一个但又不够用"的塌缩，而非"被迫维护五个"。

---

## 2. 假设②：多存储部署成本是真痛点？

**强证据，且可量化——这是三假设里最硬的一个：**

- **资源占用**：n8n 自托管 AI 栈指南警告"最低 4GB 内存（推荐 8GB+）、10GB+ 磁盘"。〔forum〕
- **Weaviate 实例**：100K 条 768 维记录，空闲就吃 **33.75GB 内存**，3 分钟内崩溃（默认 `LIMIT_RESOURCES=false` 会吞光主机资源）；多个独立用户复现同一症状。〔forum，多用户印证〕
- **迁移成本**：向量库迁移 40–200 工程时，开发者低估约 3 倍——可见部分（索引/搜索）只占 20%，隐藏的 80% 是一致性保证、跨系统同步、重建索引。〔blog〕
- **运维线性放大**：N 个存储 = N 套故障模式 / 监控 / 凭证。〔secondary〕
- **本地开发摩擦**：组装这套多存储栈"通常要一整天"vs 宣传的 15 分钟。〔forum〕

**反证（也强）："那就别上独立向量库，Postgres+pgvector 够了"：**

- pgvector 在 <1000 万向量、需要关系 join、成本敏感的部署里足够，比独立向量库 TCO 低约 3 倍，零新增基础设施。〔blog，多源〕
- Discourse 在数千个库、数十亿页览的生产环境跑 pgvector；pgvector 0.8.0 在 AWS 测试中快 9.4 倍、召回提升 100 倍。〔primary / forum〕
- 向量搜索在 RAG 里很少是延迟瓶颈（向量 5–50ms vs embedding 100–300ms vs LLM 500ms–3s）。〔blog〕

> 结论：**多存储部署痛真实且可量化，尤其在本地/单机/个人场景最尖锐（Postgres 的 10GB 磁盘 + 数小时索引构建在这里就是过度）。** 但对"能接受一个 Postgres"的团队，pgvector 已经把痛吃掉大半——所以痛点集中在一个特定夹层：**Postgres 太重、文件/sqlite-vec 太弱的中间地带**。

---

## 3. 假设③：轻量嵌入式需求是否真实？

**强证据，已被市场行为验证：**

- **本地 Agent 直接用文件系统**：Claude Code、Amazon Q Developer、Cline 把会话/状态存本地文件，而非数据库——单 Agent 场景天然倾向最轻量方案。〔secondary，多例〕
- **嵌入式向量库有真实 traction**：sqlite-vec ~7,736 star（Mozilla/Turso/Fly.io 赞助）、LanceDB ~10,600 star（集成 LangChain/LlamaIndex）、Turso/libSQL 原生向量（DiskANN GA）。〔primary，多源〕
- **隐私/本地优先需求**：sqlite-vec 跑在树莓派 Zero、全设备内推理、"一字节都不出设备"；个人 AI 助手 Kin 用 libSQL 在端上做向量检索。〔primary / blog〕
- **最简 Agent 记忆就是 markdown 文件**（CLAUDE.md / AGENTS.md）。〔blog〕

**但现有嵌入式方案都不够：**

- **sqlite-vec**：仍 pre-v1、**只有暴力搜索无 ANN**，100 万向量时 3072 维查询 8.52 秒、192 维都要 192ms，实用上限"几十万"；而且**只给 SQLite 加向量，不是统一引擎**（无 KV/队列/Agent 运行时原语）。〔primary，作者自述〕
- **LanceDB**：最接近"嵌入式统一"（向量+全文+SQL 一引擎），但定位向量/检索为中心、向上游 lakehouse 走，**不是 Agent 运行时存储**。〔primary〕
- **DuckDB VSS**：官方标注实验性；HNSW 不受 buffer manager 管（必须全装内存、不计入 memory_limit）；持久化是实验开关、WAL 恢复未实现、崩溃丢索引——**官方明确不建议生产用**。〔primary / duckdb.org〕

> 结论：**轻量嵌入式需求真实且已被验证（star 数、本地 Agent 行为），但现有方案要么向量太弱（sqlite-vec）、要么向量为中心（LanceDB）、要么不稳（DuckDB VSS）——"嵌入式 + 够用的向量 + Agent 运行时原语"的组合位确实空着。**

---

## 4. 竞争地形：谁已经在做"统一/嵌入式/Agent 记忆"

这是最关键的一节——**赛道不空，且有重量级玩家：**

| 玩家 | 形态 | 与假设的关系 |
|------|------|------------|
| **Postgres + pgvector** | 关系+向量+JSONB+全文一引擎 | **最大威胁**：持续吞掉"统一存储"叙事，且官方/云厂商力推 |
| **SurrealDB** | 多模型（文档/图/向量/时序/关系）一 ACID + Spectron 记忆层 | **直接竞品**：已经在做"统一引擎 for Agent 上下文层" |
| **LanceDB** | 嵌入式 向量+全文+SQL | 嵌入式统一的最强在位者，但向量为中心 |
| **Turso / libSQL** | SQLite fork + 原生向量（DiskANN GA） | SQLite 系统一向量路线，LangChain 官方支持 |
| **sqlite-vec** | SQLite 向量扩展 | 嵌入式向量的草根赢家，但 pre-v1、暴力搜索 |
| **Mem0 / Zep / Letta / LangMem** | Agent 记忆**薄层** | 见下——关键洞察 |
| **LangGraph checkpointer** | DB-agnostic 适配器（Postgres/Redis/Mongo/SQLite） | 框架把持久化交给现有库，不做新引擎 |

### 关键洞察：记忆层产品全是"薄层叠在别人引擎上"，没人占住底层

- **Mem0**（~48K star、YC、$24M Series A）= 向量库 + 可选 Neo4j 图；**Zep/Graphiti**（~24K star）= Neo4j/FalkorDB + Graphiti，社区版已弃用转托管；**Letta/MemGPT**（$10M 种子，Felicis 领投，Jeff Dean/Clem Delangue 天使）= 把 LLM 当"有状态 API"、记忆是模型之上的层；**LangGraph** checkpointer 是刻意 DB-agnostic 的薄适配器，LangGraph Cloud 直接用托管 Postgres。〔primary / forum，多源〕
- **结论**：所有"Agent 记忆"明星公司都**坐在 Postgres / Neo4j / 向量库之上**，没有一家做底层引擎。**底层引擎这个位是空的——但这恰恰是因为 Postgres 太能打，大家懒得重造。**

---

## 5. 最大威胁与反证

**威胁 A（最大）：Postgres+pgvector 持续变好，吞掉窗口。** 量化证据：
- pgvector 0.8.0：快 9.4 倍、召回提升 100 倍（AWS 自家测试，1000 万向量）。〔primary〕
- 生产实证：Discourse 数千库/数十亿页览跑 pgvector；单 $180/月 RDS 实例扛 250 万文档/15K QPD、p95 <80ms。〔forum〕
- 生态补 gap：pgvectorscale、VectorChord、sparsevec（BM25/SPLADE）逐步补齐过滤/混合检索。〔blog〕
- 反向：pgvectorscale 不在 RDS 上、HNSW 构建吃 10GB+ 内存跑数小时、实时写入未解、planner 对过滤向量查询常次优——**"just use Postgres"也有真实代价**。〔blog，多源〕

**威胁 B（反证）："大多数人其实不需要新东西"。**
- YAGNI：<10M 向量就用 pgvector，别过早引入独立向量库。〔forum，强共识〕
- 多数 pgvector 用例是小语料、低 churn（"对着技术文档聊天"），正好落在 pgvector 舒适区。〔forum〕
- <10 万 chunk：独立向量库都没必要，JSON 文件或内存 FAISS 就够。〔blog〕
- 甚至有人得出相反结论：既不是 Postgres 也不是轻量嵌入式，而是**托管专用向量库**对多数团队更省事。〔blog〕

**威胁 C：AWS 官方立场反统一**——"Agent 不偏好任何单一数据库，存储选择应跟随数据性质与访问模式"。〔secondary，AWS〕

---

## 6. 机会窗口的形状

把证据拼起来，窗口不是"统一存储"（太挤、Postgres 赢能力），而是这三者的交集：

1. **目标场景**：单 Agent / 本地 / 边缘 / 个人——这里 Postgres 太重（10GB 磁盘 + 数小时索引）、文件系统太弱（无召回/无事务/无可观测）、sqlite-vec 太弱（暴力搜索、向量only）。**这个夹层有真实需求且无在位强者。**
2. **差异化护城河**：不是向量（pgvector 赢）、不是统一（SurrealDB/LanceDB 在做），而是 **Agent 运行时原语**——幂等 run / exactly-once 工具调用、时间旅行重放、checkpoint、记忆分层。**这套连 LangGraph 都只做成 DB-agnostic 薄适配器、Letta 坐在 Postgres 上，没人把它烧进一个嵌入式引擎。**
3. **形态**：单文件嵌入式、零运维（SQLite 式），本地 Agent 框架直接 in-process 调用。

---

## 7. go/no-go 判断与定位修正

**裁决：条件性 GO。** 痛点真实（部署成本 + 本地夹层），窗口存在（Agent 运行时原语 + 嵌入式无人占），但**必须修正定位**，否则会撞死在 Postgres 上：

- ❌ **不要**叫"统一数据库"——赛道拥挤，Postgres+pgvector 在能力上碾压，SurrealDB/LanceDB 已占位。
- ❌ **不要**以"更好的向量"为卖点——那是 pgvector / Qdrant 的主场。
- ✅ **要**叫"**Agent 的嵌入式记忆层**"，slogan 大致：*"让单 Agent 可靠的本地记忆——幂等、可重放、可恢复、带语义召回，一个文件搞定。"*
- ✅ **目标用户**：本地/个人/边缘 Agent 开发者（Claude Code 类、桌面 AI、设备端 AI、隐私优先场景）——他们要的不是"更强的库"，是"别让我装 Postgres+Redis+Qdrant 四个容器还能跑起来"。
- ✅ **胜负手**：嵌入式零运维 + Agent 运行时原语（这是护城河）+ 够用的统一访问模式（KV/事件/向量，准入级）。向量必须做到 pgvector 级（HNSW、混合检索），不能是 sqlite-vec 级暴力搜索——否则被两面夹杀。

**最大风险（诚实）**：窗口在收窄。Postgres+pgvector 从上往下压（变强、变轻、托管化），sqlite-vec/Turso 从下往上长（成熟、加 ANN）。**如果做，速度很重要；如果慢，窗口会关。** 一个保守的验证路径：先用 2–3 周做 MVP 切片（嵌入式 log + KV + HNSW 向量 + 幂等 run 原语），找 3–5 个真实本地 Agent 项目验证"是否真的愿意用它替代文件系统 + 一个向量库"，再决定是否全押。

---

## 信源（28 域，2024–2026）

medium.com · github.com · dev.to · reddit.com · aws.amazon.com · surrealdb.com · encore.dev · news.ycombinator.com · alex-jacobs.com · alexgarcia.xyz（sqlite-vec 作者）· marcobambini.substack.com · lancedb.com · backendbytes.com · sqlite.ai · forum.letta.com · prnewswire.com · langchain.com · vectorize.io · neo4j.com · forum.weaviate.io · duckdb.org · turso.tech · thenuancedperspective.substack.com · sitepoint.com · fast.io · diegopachecotech.substack.com · blog.gopenai.com · youtube.com

> 完整 228 条 claims + URL 留存在 `/tmp/research_digest.md`（调研工作流产物）；本报告为综合判断，关键数据点均可在上述信源核对。
