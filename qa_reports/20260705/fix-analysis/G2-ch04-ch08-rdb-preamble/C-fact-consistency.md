# 全书一致性审查：`aof-use-rdb-preamble` 配置项存废

## 审查范围

审查 `aof-use-rdb-preamble` 配置项在全书各章的描述是否一致。

### 涉及的关键文件

- `chapters/04-memory-disk/chapter.md` 第 105 行
- `chapters/08-storage-format/chapter.md` 第 92 行
- 其他各章（前置核查：ch00/preface, ch01/intro, ch02/paradigm, ch03/comparison, ch09/pattern, ch10/epilogue — 均无相关引用）

---

## 核心事实确认

### Redis 7.x 的真实情况

从 Redis 7.0 / 7.2 / 7.4 的上游源码确认：

1. `aof-use-rdb-preamble yes` 在 redis.conf 中存在（所有 7.x 版本均有，默认 yes）。
2. `src/config.c` 中登记为 `createBoolConfig("aof-use-rdb-preamble", ...)`，配置项未移除。
3. `src/server.h` 中 `server.aof_use_rdb_preamble` 字段声明存在。
4. 7.0 release notes 中 `aof-use-rdb-preamble` 并未被列为移除项；Multi-Part AOF 改写了文件结构（单一文件 → 目录 + base/incr/manifest），但该配置项的语义调整为控制 base 文件的格式（RDB vs AOF），并未删除。

**结论：`aof-use-rdb-preamble` 在 Redis 7.x 中**仍存在**，默认 yes。书中所说的"已移除"是事实性错误。**

配置项的语义变化（非因果性变化，仅补叙）：
- 7.0 前：控制 AOF 单文件是否以 RDB 前导（preamble）开头。
- 7.0 后：控制 base 文件是否使用 RDB 格式（效果等同，但改为多文件结构中的 base 文件）。

### 错误来源追溯

`docs/出版审查-findings-squeeze.md` 第 91-99 行 声称该配置项在 7.0 已被移除，依据为"阿里云 Multi-Part AOF 设计文档"。该判断与 Redis 上游源码不符，是错误审查结论，被错误地作为修理依据采纳，导致两章同时改错。

---

## 一致性审查结论

### 两处表述是否一致

**是。** 两处表述完全一致，均说该配置项"已移除"：

- ch04:105："`aof-use-rdb-preamble` 在 5.x–6.x 中默认即为 `yes`；7.0 多部 AOF 改造后该配置项已移除，base 文件始终为 RDB 格式，行为等效。"
- ch08:92："Redis 4.0 引入 `aof-use-rdb-preamble` 开关（5.x–6.x 默认 yes，即混合持久化）；7.0 起 Multi-Part AOF 改造后该配置项已移除，base 文件始终为 RDB 格式，效果等同混合持久化常开。"

两处在措辞上几乎相同（"已移除""base 文件始终为 RDB 格式""行为/效果等效"），属于 **一致但同为错误** 的典型案例。

### 两处修正后是否需要保持一致

**是。** 修正后两处必须给出完全一致的描述。

### 是否还有别处被这个错误连带影响

**否。** 全书唯一两处提到该配置项存废的就是 ch04:105 和 ch08:92。其他地方的"混合持久化"描述（ch04:107, ch04:113, ch08:82 等）都在讲 4.0+ 混合持久化的行为本身，不涉及该配置项的存在性，不受此错误影响。

---

## 建议的统一修复措辞

### 核心要点

- 保持两章措辞一致
- 纠正"已移除"为"仍存在，默认 yes，语义调整为控制 base 文件格式"
- 保留原有合理的尾句（"base 文件始终为 RDB 格式，行为等效"），因为该描述本身正确

### 推荐措辞（两处统一）

**推荐方案 A（简洁，适合 ch08 原文）**：

> Redis 4.0 引入 `aof-use-rdb-preamble` 开关（5.x–6.x 默认 yes，即混合持久化）；7.0 Multi-Part AOF 改造后该配置项仍存在且默认 yes，语义调整为控制 base 文件是否使用 RDB 格式，效果等同混合持久化常开。

**推荐方案 B（与 ch04 上下文更贴合）**：

> `aof-use-rdb-preamble` 在 5.x–6.x 中默认即为 `yes`；7.0 Multi-Part AOF 改造后该配置项仍存在、默认 yes，语义调整为控制 base 文件格式，base 文件恒为 RDB 格式，行为等效。

**共同改动**：将原文中的"该配置项已移除"替换为"该配置项仍存在且默认 yes,语义调整为控制 base 文件格式"，同时保持"base 文件始终为 RDB 格式，行为等效"不变。

---

## 风险评级

| 维度 | 评级 | 说明 |
|------|------|------|
| 自洽性 | P0（事实错误） | 两处一致但都错了 |
| 互斥性 | ✅ 已自洽 | 两处描述一致，未出现 ch04 说"已移除"ch08 说"仍存在"的矛盾 |
| 修复紧急性 | 高 | 读者如果在 7.x 的 redis.conf 看到该配置项存在，会与书中"已移除"矛盾，产生信任危机 |

---

## 附加检查记录

### 自洽的高风险点确认

以下高风险点经核查在全书范围内一致（未出现自相矛盾）：

1. **5.x–6.x 默认 yes**：ch04 和 ch08 一致，符合 Redis 5.x+ 源码（config.c 默认值从 5.0 起改为 yes）。
2. **混合持久化引入版本 4.0**：一致，符合 Redis 4.0 release notes。
3. **7.x 出厂默认持久化是 RDB-only**：ch04 第 101 行和 ch08 第 103 行一致，符合 Redis 7.x 默认 `appendonly no`。
4. **混合持久化的行为本质**（RDB 基底 + 增量 AOF 拼接）：两章一致描述。

---

*审查人：全书事实一致性审查员（Agent）*
*审查日期：2026-07-05*
