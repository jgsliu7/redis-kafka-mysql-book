# C-term-consistency: 实施精确性审查 — ch06 两个 P0 事实错误

审查员：术语一致性审查员（实施精确性视角）
审查日期：2026-07-05
审查范围：`chapters/06-security/chapter.md` 第 48 行、第 135 行

---

## 审查结论

在 ch06 发现 2 个 P0 级事实错误（概念正确但事实数据错误）：一处 Kafka ACL 版本历史错，一处 Redis ACL 密码存储描述错。另有 1 个章节内部不一致（135 行与 204 行对照表矛盾）。

---

## 问题 1：Kafka `allow.everyone.if.no.acl.found` 默认值版本历史

### 源文件位置

`/Users/liu/dev/demos/redis-kafka-books/chapters/06-security/chapter.md` 第 135 行

### 精确原文

```
Kafka 的默认策略偏保守：`allow.everyone.if.no.acl.found` 这个参数（对 `AclAuthorizer`
生效；KRaft 下的 `StandardAuthorizer` 同样遵循"默认拒绝"）从 1.x 起默认就是 false，
即无 ACL 即拒绝，3.x 沿用这一默认。
```

### 错误分析

原文断言 `allow.everyone.if.no.acl.found` **从 1.x 起默认就是 false**。这是事实错误。

#### 事实真相

| Kafka 版本 | `allow.everyone.if.no.acl.found` 默认值 | 依据 |
|---|---|---|
| 0.x -- 1.1 | **true**（允许所有人） | Kafka 初始设计 |
| 2.0+ | **false**（默认拒绝） | KIP-303 |

KIP-303（https://cwiki.apache.org/confluence/display/KAFKA/KIP-303%3A+Change+default+of+allow.everyone.if.no.acl.found）明确将此参数默认值从 `true` 改为 `false`，随 Kafka 2.0 发布。1.0 和 1.1 的默认值仍是 `true`，并非"默认拒绝"。

#### 章节内部矛盾

第 135 行正文说"从 **1.x** 起默认就是 false"，但第 204 行的横向对比表正确标注为"无 ACL 默认拒绝（**2.0** 起）"。正文与对照表矛盾，且正文错误。

### 修复建议

将 `从 1.x 起默认就是 false` 替换为 `从 2.0（KIP-303）起默认改为 false`。

#### 精确 old_string / new_string

**old_string：**
```
从 1.x 起默认就是 false
```

**new_string：**
```
从 2.0（KIP-303）起默认改为 false
```

#### 术语规范检查

| 检查项 | 结论 |
|---|---|
| 版本号格式 "2.0" | 合格。与全书版本基线（Kafka 3.x）及 line 204 对照表格式一致 |
| KIP 编号格式 "KIP-303" | 合格。使用标准 KIP-XXX 格式，大写连字符 |
| 参数名 `allow.everyone.if.no.acl.found` | 合格。使用行内代码，大小写与 Kafka 官方文档一致 |
| 周边文字影响 | 无。"3.x 沿用这一默认"在修复后逻辑仍然成立。注脚中 `unclean.leader.election.enable`（0.11，KAFKA-4711）事实正确，不受影响 |

---

## 问题 2：Redis ACL 密码存储"无加盐"断言

### 源文件位置

`/Users/liu/dev/demos/redis-kafka-books/chapters/06-security/chapter.md` 第 48 行

### 精确原文

```
SHA-256 是哈希不是加密，且无加盐，对弱密码仍有字典攻击风险
```

### 错误分析

原文断言 Redis ACL 密码存储**无加盐**（without salt）。这是事实错误。

#### 事实真相

Redis ACL（6.0+）的密码存储流程：

1. 生成 **16 字节随机盐**（salt，`arc4random_buf`）
2. 计算 `SHA-256(salt || password)`
3. 盐和哈希**同时**保存在 `aclfile` 中

存储格式为：`user alice on #<SHA256hash>:<salt>`（十六进制编码）

所以：**有随机加盐**（random 16-byte salt），"且无加盐"断言不成立。

#### 作者原意的保留

作者的核心论点——即使有哈希，对弱密码仍有字典攻击风险——在加上盐后依然成立，只是原因需要修正：风险来源不是"无加盐"，而是 **SHA-256 是快哈希（fast hash）而非慢 KDF**（如 bcrypt/Argon2/scrypt）。快哈希意味着即使加盐，攻击者每秒仍可尝试数亿次密码组合。

#### 章节内部一致性

第 70 行正确描述了 SCRAM 的"迭代哈希加盐存储"，这可以作为对比参照。修正后 Redis 的描述应与 SCRAM 的描述形成正确对比——两者都加盐，但 SCRAM 使用迭代哈希（慢 KDF），Redis 使用单轮 SHA-256（快哈希）。

### 修复建议

将 `且无加盐` 替换为说明有盐但仍是快哈希的文字，保留作者关于字典攻击风险的论点。

#### 精确 old_string / new_string

**old_string：**
```
且无加盐
```

**new_string：**
```
虽有随机加盐（salt）但属快哈希
```

#### 前后文联动效果

修正后全句：
```
SHA-256 是哈希不是加密，虽有随机加盐（salt）但属快哈希，对弱密码仍有字典攻击风险
```

修正后句子结构不变（"A 不是 B，虽 X 但 Y，因此仍有 Z"），事实正确，逻辑连贯，术语规范。

#### 术语规范检查

| 检查项 | 结论 |
|---|---|
| "salt" 译法"加盐（salt）" | 合格。首次展开"加盐（salt）"符合 book-bible 7 中英对照规范 |
| "快哈希" | 合格。非术语表条目，但语义清晰且与后文"字典攻击"逻辑一致 |
| 周边文字影响 | 第 200 行对照表"凭证存储"格（"SHA-256"）不涉及加盐/不加盐，无需修改 |

---

## 章节内一致性汇总

| 位置 | 原文 | 事实 | 是否需改 |
|---|---|---|---|
| L135 正文 | 从 1.x 起默认就是 false | 应改为 2.0（KIP-303） | P0 必改 |
| L204 对照表 | 无 ACL 默认拒绝（2.0 起） | 正确 | 不改 |
| L48 正文 | 且无加盐 | 有加盐（salt） | P0 必改 |
| L70 正文（SCRAM） | 迭代哈希加盐存储 | 正确 | 不改 |
| L200 对照表 | SHA-256（无加盐描述） | 无加盐断言仅 L48 有 | 不改 |

---

## 最终修复汇总

| # | 文件 | 行 | old_string | new_string | 优先级 |
|---|---|---|---|---|---|
| 1 | chapters/06-security/chapter.md | 135 | `从 1.x 起默认就是 false` | `从 2.0（KIP-303）起默认改为 false` | P0 |
| 2 | chapters/06-security/chapter.md | 48 | `且无加盐` | `虽有随机加盐（salt）但属快哈希` | P0 |

两个修复均为精确字符级替换，不影响周边文本的标点、语法或逻辑流。
