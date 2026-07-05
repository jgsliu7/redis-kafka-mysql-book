# 阶段 3a 综合裁决：P0 问题修复方案

> 2026-07-05 | 6 组 × 3 agent = 18 分析完成 | 裁决规则：≥2/3 同意

---

## G1: ch06 ACL 两个事实错误 — ✅ 全票通过修复

| 视角 | Agent | 问题1 (Kafka ACL 版本) | 问题2 (Redis ACL 加盐) |
|------|-------|----------------------|----------------------|
| A 技术 | source-contributor | ✅ FIX | ✅ FIX |
| B 读者 | interviewee-reader | ✅ FIX（面试答错，伤害高） | ✅ FIX（不影响操作但应修） |
| C 精确 | term-consistency | ✅ FIX（章节内部矛盾：L135 vs L204） | ✅ FIX |

**裁决：3/3 通过，两个问题都修。**

### 问题 1 修复方案

```
old: allow.everyone.if.no.acl.found "从 1.x 起默认就是 false"
new: allow.everyone.if.no.acl.found 从 Kafka 2.0（KIP-303）起默认改为 false（1.x 默认为 true）
```

### 问题 2 修复方案

```
old: SHA-256 是哈希不是加密，且无加盐
new: SHA-256 是哈希不是加密；虽有 16 字节随机加盐（salt 明文存储在 aclfile 中），但属快哈希而非慢 KDF
```

---

## G2: ch04/ch08 aof-use-rdb-preamble — ✅ 全票通过修复

| 视角 | Agent | 结论 |
|------|-------|------|
| A 技术 | architect-reviewer | ✅ FIX — 配置项仍存在，默认 yes |
| B 读者 | reader-operability | ✅ FIX — 读者验证 CONFIG GET 会发现矛盾 |
| C 一致 | fact-consistency | ✅ FIX — 两处一致但都错，根因追溯到 squeeze.md 误判 |

**裁决：3/3 通过。两处统一修复。**

### 修复方案（ch04 L105 和 ch08 L92，统一措辞）

```
old: 7.0 多部 AOF 改造后该配置项已移除
new: 7.0 Multi-Part AOF 改造后该配置项仍存在（默认 yes），语义调整为控制 base 文件是否使用 RDB 格式
```

---

## G3: ch10 sync_binlog=1 — ✅ 全票通过修复

| 视角 | Agent | 结论 |
|------|-------|------|
| A 技术 | architect-reviewer | ✅ FIX — MySQL 8.0 双 1 是出厂默认 |
| B 读者 | interviewee-reader | ✅ FIX — 读者会记住"需要手动加"，面试露馅 |
| C 精确 | typo-grammar | ✅ FIX — 改动一字不改义 |

**裁决：3/3 通过。**

### 修复方案

```
old: MySQL 默认偏向持久性（`innodb_flush_log_at_trx_commit=1` 是默认），若再开启 `sync_binlog=1` 即"双 1"配置
new: MySQL 默认偏向持久性（`innodb_flush_log_at_trx_commit=1` 与 `sync_binlog=1` 均为默认值，合称"双 1"配置）
```

---

## G4: ch08 标点冗余 + fig-8-7↔8-8 — ✅ 全票通过修复

| 视角 | Agent | 标点 | 图互换 |
|------|-------|------|--------|
| A 技术 | source-contributor | ✅ 删句号 | ✅ 交换文件名+修内部标题 |
| B 编辑 | tech-editor | ✅ 删句号 | ✅ 交换文件名+修内部标题 |
| C 引用 | crossref-validity | ✅ 删句号 | ✅ 交换文件名+修内部标题 |

**裁决：3/3 通过，图修复方案（交换文件名）全票一致。**

### 问题 1 修复方案

```
old: 不同的原因。：为内存优化
new: 不同的原因：为内存优化
```

### 问题 2 修复方案

三步操作：
1. `mv fig-8-7.svg fig-8-7.svg.tmp`
2. `mv fig-8-8.svg fig-8-7.svg`
3. `mv fig-8-7.svg.tmp fig-8-8.svg`
4. 修正 `fig-8-7.svg` 内部标题：`图 8-8` → `图 8-7`
5. 修正 `fig-8-8.svg` 内部标题：`图 8-7` → `图 8-8`

chapter.md 不改动。

---

## G5: ch01 句子残缺 — ⚠️ 2/3 删除，1/3 改冒号

| 视角 | Agent | 方案 |
|------|-------|------|
| A 文字 | typo-grammar | 句号→冒号，两句合并 |
| B 编辑 | tech-editor | **直接删除整句**（写作残余，不承载新信息） |
| C 一致 | fact-consistency | **直接删除整句**（删除后结构与 Redis/Kafka 段对等） |

**裁决：2/3 — 删除"MySQL 由此付出的代价是。"**

B 和 C 都指出：前面已列举 5 个具体代价，下一句"它的优先级一直是'对'排在'快'前面"已承担总括职能。这句是写作过程中改变写法后未清除的残余。删除后 MySQL 段与 Redis 段、Kafka 段结构一致。

### 修复方案

```
old: 横向分库分表则代价不菲。MySQL 由此付出的代价是。它的优先级一直是"对"排在"快"前面：可以慢，但不能错。
new: 横向分库分表则代价不菲。它的优先级一直是"对"排在"快"前面：可以慢，但不能错。
```

---

## G6: 商标声明 — ✅ 全票通过

| 视角 | Agent | 方案 |
|------|-------|------|
| A 合规 | compliance | ✅ 序言插入 + 后记追加 |
| B 编辑 | tech-editor | ✅ 序言集中声明，正文不加 ® |
| C 术语 | term-consistency | ✅ 方案A：集中声明，正文不标，与 bible 不冲突 |

**裁决：3/3 通过。序言插入商标声明，正文不加 ® 符号。**

### 修复方案

在 `chapters/00-preface.md` 第 33 行（"并独立承担文责。"）与第 34 行（"是为序。"）之间插入：

```markdown
本书提及的商标与产品名称均属其各自所有者。Redis® 是 Redis Ltd. 的注册商标。MySQL® 与 InnoDB® 是 Oracle Corporation 及其附属公司的注册商标。Apache Kafka® 与 Apache ZooKeeper™ 是 Apache 软件基金会在美国及/或其他国家的注册商标或商标。
```

同时在 `docs/book-bible.md` 记录商标策略（防复发）。

---

## 汇总：8 个 P0 问题全部获批执行

| # | 文件 | 问题 | 裁决 | 操作 |
|----|------|------|------|------|
| 1 | ch06 | Kafka ACL 版本历史 | 3/3 | Edit 替换 |
| 2 | ch06 | Redis ACL "无加盐" | 3/3 | Edit 替换 |
| 3 | ch04 | aof-use-rdb-preamble | 3/3 | Edit 替换 |
| 4 | ch08 | aof-use-rdb-preamble | 3/3 | Edit 替换 |
| 5 | ch10 | sync_binlog=1 默认值 | 3/3 | Edit 替换 |
| 6 | ch08 | 标点冗余 "。：" | 3/3 | Edit 替换 |
| 7 | ch08 | fig-8-7↔8-8 互换 | 3/3 | mv + Edit SVG |
| 8a | ch01 | 句子残缺 "代价是。" | 2/3 删除 | Edit 删除 |
| 8b | ch00 | 商标声明缺失 | 3/3 | Edit 插入 |

---

**下一步：阶段 3c 执行修复（6 个文件，逐文件 Edit）→ 阶段 3d 验证（每文件 ≥2 agent）**
