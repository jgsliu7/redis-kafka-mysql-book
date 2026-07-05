# G2: aof-use-rdb-preamble "已移除" — 技术准确性审读（Agent A）

## 审查范围

- `chapters/04-memory-disk/chapter.md` L105
- `chapters/08-storage-format/chapter.md` L92
- 两处均声称 `aof-use-rdb-preamble` 已在 Redis 7.0 移除

---

## 事实核查

### 错误点 1: ch04 L105

**原文：**
> `aof-use-rdb-preamble` 在 5.x–6.x 中默认即为 `yes`；7.0 多部 AOF 改造后该配置项已移除，base 文件始终为 RDB 格式，行为等效。

**错误：** 声称配置项在 7.0 被"已移除"。实际该配置项在 Redis 7.0、7.2、7.4 及最新 unstable 分支中均存在。

**严重程度：** 事实错误。同一条目还包含了 "base 文件始终为 RDB 格式" 的错误推论（见下文）。

### 错误点 2: ch08 L92

**原文：**
> Redis 4.0 引入 `aof-use-rdb-preamble` 开关（5.x–6.x 默认 yes，即混合持久化）；7.0 起 Multi-Part AOF 改造后该配置项已移除，base 文件始终为 RDB 格式，效果等同混合持久化常开。

**错误：** 与 ch04 一致的错误：声称配置项在 7.0 被"已移除"。

**严重程度：** 事实错误。

### 证据链

| 证据来源 | 内容 | 结论 |
|---------|------|------|
| Redis 7.0 `redis.conf` L1509 | `aof-use-rdb-preamble yes` | 配置项存在 |
| Redis 7.0 `src/config.c` L2991 | `createBoolConfig("aof-use-rdb-preamble", ..., server.aof_use_rdb_preamble, 1, ...)` | 配置项注册在配置系统中，默认值 1（yes） |
| Redis 7.0 `src/aof.c` L424-435 | `server.aof_use_rdb_preamble` 控制 base 文件后缀：`yes` 为 `.base.rdb`，`no` 为 `.base.aof` | 配置项在运行时被引用，仍有效 |
| Redis 7.0 `src/aof.c` L2378 | `if (server.aof_use_rdb_preamble) { ... }` 判断是否在重写时写入 RDB 格式 | 配置项影响重写逻辑 |
| Redis 7.2 `redis.conf` L1517 | `aof-use-rdb-preamble yes` | 配置项在 7.2 仍存在 |
| Redis 7.4 `redis.conf` L1528 | `aof-use-rdb-preamble yes` | 配置项在 7.4 仍存在 |
| Redis 7.4 `src/aof.c` L405-416 | 同 7.0 逻辑 | 配置项在 7.4 仍有效 |
| Redis unstable `redis.conf` L1583 | `aof-use-rdb-preamble yes` | 截至最新代码仍未移除 |

**判断：** "已在 7.0 移除" 的说法不成立。核心团队可能讨论过弃用（该选项与 Multi-Part AOF 的设计在功能上有重叠，base 文件默认即为 RDB），但最终**未执行移除**，选项至今仍存在且有效。

### 连带错误的勘定

原文中 "base 文件始终为 RDB 格式" 也是不对的。`aof-use-rdb-preamble no` 时 base 文件后缀为 `.base.aof`，内容为纯 AOF 命令序列而非 RDB 二进制。不过，该选项默认值为 `yes`（7.x 所有版本生产配置均为 yes），所以对绝大多数用户来说 base 文件确实是 RDB 格式。建议将 "始终" 降级为 "默认"，避免读者对配置系统的理解产生偏差。

---

## Tradeoff 深度

此处的技术取舍（mixed persistence vs pure AOF rewrite）的 tradeoff 分析整体正确：混合持久化取 RDB 的加载速度和 AOF 的低丢失率。错误点不涉及 tradeoff，只涉及事实。

但该错误导致读者可能产生一个误判：

- **错误推论：** 读者可能认为 Redis 7.x 的 Multi-Part AOF 强制固定了 base 文件格式，去除了用户的可配置性。
- **实际：** 可配置性仍然保留。Multi-Part AOF 改变的只是文件组织方式（单文件 -> 多文件 + manifest），并没有剥夺用户对 base 格式的选择权。

这个推论虽不致命（默认 yes 下行为与书中描述一致），但损害了读者对 Redis 配置系统可演进性的理解。

---

## 架构启示评分

此处不涉及 N.6 架构启示章节，无需评分。

---

## 生产真实感

**问题段落：** "7.0 多部 AOF 改造后该配置项已移除" — 这句话不像在生产线上验证过的判断。如果在生产 Redis 7.0 实例上执行 `CONFIG GET aof-use-rdb-preamble`，会返回 `yes` 而不是报错。任何在生产环境运维过 Redis 7.x 的人，只要跑过 `CONFIG GET *` 查看配置，就会看到该选项仍然存在。

**一个可能的历史背景：** 该错误可能源于对 PR #9788（Multi-Part AOF）早期设计文档的误读。在开发早期决策中，确实有提议在引入 Multi-Part AOF 后移除这个配置项（因为 base 文件天然独立为 RDB 文件，不再需要 "preamble" 概念）。但这个提议**最终没有被采纳**，选项被保留，只是语义从"append RDB preamble to a single AOF file"调整为"use RDB format for the base file in Multi-Part AOF"。如果作者读到的是早期设计文档而非发布版源码，就容易得出"已移除"的错误结论。

---

## 遗漏与盲区

1. **对 7.0 中该配置项语义变化的讨论缺失：** 书中说"行为等效"——这是对的但理由不对。实际变化是：配置项从"控制单个文件是否以 RDB 二进制开头"变为"控制 base 文件格式是 `.base.rdb` 还是 `.base.aof`"，功能上等效。书中只说"已移除，行为等效"，正确的解释应该是"配置项保留，默认 yes，语义延续"。

2. **`aof-use-rdb-preamble` 设置为 `no` 的场景：** 这是一个被忽略的 corner case。虽然生产极少使用（因为 base 用纯 AOF 命令格式会拖慢恢复速度），但理论上读者从书中会获得"base 始终是 RDB"的绝对印象，不知道还有这个选项。建议在修复时加一句话带出这个可配置性。

---

## 修复方案

### 修复原则

1. 保留原有段落结构和上下文
2. 只修正事实错误，不扩大改动范围
3. 两章的表述应对齐，但允许各自段落风格的差异

### ch04 L105 修复

**old_string：**
```
`aof-use-rdb-preamble` 在 5.x–6.x 中默认即为 `yes`；7.0 多部 AOF 改造后该配置项已移除，base 文件始终为 RDB 格式，行为等效。
```

**new_string：**
```
`aof-use-rdb-preamble` 在 5.x–6.x 中默认即为 `yes`；7.0 多部 AOF 改造后该配置项继续存在（默认 `yes`），控制 base 文件采用 RDB 格式（`.base.rdb`），行为与混合持久化等效。
```

**改动说明：**
- "已移除" -> "继续存在（默认 `yes`）"：纠正事实
- "base 文件始终为 RDB 格式" -> "控制 base 文件采用 RDB 格式"：从绝对断言改为可配置表述
- "行为等效" -> "行为与混合持久化等效"：表述更精确

### ch08 L92 修复

**old_string：**
```
Redis 4.0 引入 `aof-use-rdb-preamble` 开关（5.x–6.x 默认 yes，即混合持久化）；7.0 起 Multi-Part AOF 改造后该配置项已移除，base 文件始终为 RDB 格式，效果等同混合持久化常开。
```

**new_string：**
```
Redis 4.0 引入 `aof-use-rdb-preamble` 开关（5.x–6.x 默认 yes，即混合持久化）；7.0 多部 AOF 改造后该配置项继续存在（默认 `yes`），控制 base 文件采用 RDB 格式（`.base.rdb`），效果等同混合持久化常开。
```

**改动说明：**
- "已移除" -> "继续存在（默认 `yes`）"：纠正事实
- "base 文件始终为 RDB 格式" -> "控制 base 文件采用 RDB 格式"：同 ch04
- "7.0 起" -> "7.0 多部 AOF 改造后"：与 ch04 措辞对齐

### 连带检查：ch04 L107 和 ch08 L94 的 parenthetical

ch04 L107: "至多一个**基础文件（base，RDB 格式）**"
ch08 L94: "至多一个基础文件（base，RDB 格式）"

这两处的 "RDB 格式" 是功能描述，配合修复后的精确表述，在上下文（默认 yes）下可以接受。建议不做改动，否则会过度膨胀段落。如果追求极致的严谨，可将 "RDB 格式" 改为 "默认 RDB 格式"，但不要求。

---

## 改动风险评估

| 维度 | 评估 | 说明 |
|------|------|------|
| 技术准确性 | 修复后 100% 正确 | 与 Redis 7.x 源码、配置文件对齐 |
| 章节一致性 | ch04 和 ch08 表述对齐 | 两章改法一致，消除冲突 |
| 段落衔接 | 无影响 | 修复只改动了一句，前后段落内容不受影响 |
| 读者理解 | 正面 | 纠正了"用户不可配置"的误导，同时不影响混合持久化的结论 |
| 字数变化 | 极小 | 两处修改均只替换句尾部分，不引起排版问题 |
| 图/表引用 | 无影响 | 无图表引用关联该句 |

**风险评级：低。** 这是一个字面替换，不涉及逻辑重构，不涉及跨段联动，不涉及图像或代码示例。唯一的潜在风险是如果修复时错误保留了"已移除"的表述但同时又补充了"继续存在"，会造成同一句内的自相矛盾——只要一次性替换完整，不会有这个问题。

---

## 写得最好的部分（与错误无关）

原文对 Multi-Part AOF 的概述（ch04 L107-113）和文件结构变化的解释（ch08 L94-97）是写得准确的。尤其是将 7.0 的 manifest 原子切换类比为 "git 的 commit 指针切换" 这个比喻恰当且易懂。这些内容在修复后无需调整。
