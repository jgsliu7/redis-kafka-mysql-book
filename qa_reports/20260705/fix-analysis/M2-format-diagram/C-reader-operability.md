# C-Reader-Operability 读者可操作性审查

审查日期: 2026-07-05
审查范围: ch06 (security), ch09 (data-sync), ch10 (summary), 后记 (epilogue)

---

## 1. 逐问题分析

### R02-1 ch06: ACL SETUSER 命令缺执行上下文

**文件**: `/Users/liu/dev/demos/redis-kafka-books/chapters/06-security/chapter.md`
**位置**: L40-L44
**命令/参数**: `ACL SETUSER alice on >pwd ~keys:* +get +set`

**读者照做会不会出问题？**

会。`>` 在 shell 语境下是输出重定向符。读者如果直接从页面复制该命令粘贴到终端（bash/zsh）中执行，会出现两种场景：

- **bash 解释型**：`>` 被 shell 截获为重定向，创建一个空文件 `pwd`，然后剩余参数 `alice` `on` `~keys:*` `+get` `+set` 被当作 `ACL` 命令的参数传给 shell，报 `command not found: ACL`。读者会困惑。
- **redis-cli 内正确执行**：只有读者已经位于 redis-cli 提示符下，`>` 才是 ACL SETUSER 语法的密码前缀。但前文没有提示读者需要先进入 redis-cli。

`redis` 代码块语言标签不足以消除歧义——许多 markdown 渲染器把 `redis` 仅视为语法高亮，读者不会因此自动意识到执行场所。

**严重度**: 中。该命令是第 6 章唯一一个完整代码块，设计为"读者可以照着输入"的形态。`>` 会让不熟悉 ACL 语法的读者在错误的执行场所浪费时间去调试。

**最小可行修复方案**:

在代码块前加一句话，明确指示执行场所。同时用 `>` 的语境说明它不是 shell 重定向。

**old_string**:
```
6.0 引入 ACL（Access Control List，访问控制列表）是一次结构性补回。ACL 的核心是"用户"这个一等概念，每个用户有自己的密码集合、命令权限和键模式。一条典型的规则长这样：

```redis
ACL SETUSER alice on >pwd ~keys:* +get +set
```
```

**new_string**:
```
6.0 引入 ACL（Access Control List，访问控制列表）是一次结构性补回。ACL 的核心是"用户"这个一等概念，每个用户有自己的密码集合、命令权限和键模式。在 redis-cli 中执行以下命令创建一条典型规则（`>` 是 ACL 语法中的密码前缀，不是 shell 重定向符）：

```redis
ACL SETUSER alice on >pwd ~keys:* +get +set
```
```

---

### R02-2 ch09: PSYNC ? -1 非用户命令

**文件**: `/Users/liu/dev/demos/redis-kafka-books/chapters/09-data-sync/chapter.md`
**位置**: L67（在全量同步章节描述全量流程时）
**命令/参数**: `` PSYNC ? -1 ``

**读者照做会不会出问题？**

**不会（但有一定轻度混淆风险）**。该文本出现在全量同步步骤描述的上下文中：

> 1. 主节点收到副本的 `PSYNC ? -1`（表示"我什么都没有"），触发 `BGSAVE`...

分析：
- 文本明确说"主节点**收到**副本的"——用的是被动语态，主语是"主节点"，动作的发出者是"副本"。读者只要稍加留意就能看出这是在描述内部协议行为，不是要求读者执行的命令。
- `PSYNC ? -1` 出现在行内 backtick 中，不是代码块。没有"复制粘贴执行"的暗示。
- `?` 和 `-1` 是协议层面的占位符——实际协议中 `PSYNC` 的参数是 replid 和 offset，这里用 `?` 和 `-1` 表示"未知"。读者即使尝试在 redis-cli 中输入也得不到预期结果（`PSYNC` 本身是内部命令，大多数 redis-cli 客户端也不会把它当用户命令暴露）。

主要的轻度混淆在于：`?` 没有解释为占位符，读者可能认为这是一个字面问号。但结合后文"表示'我什么都没有'"的解释，意图已经清楚。

**严重度**: 低。不建议为这个轻度混淆单独改源文件。如果出于"宁全不遗"的考虑，可以做非常轻量的补丁。

**最小可行修复方案**（可选）:

在不改变句子长度的前提下，给 `?` 和 `-1` 加一句简短说明。

**old_string**:
```
1. 主节点收到副本的 `PSYNC ? -1`（表示"我什么都没有"），触发 `BGSAVE`，fork 出一个子进程把当前内存快照写成 RDB 文件。
```

**new_string**:
```
1. 主节点收到副本自动发送的 `PSYNC ? -1`（问号占 replid 位、-1 占 offset 位，表示"我什么都没有"），触发 `BGSAVE`，fork 出一个子进程把当前内存快照写成 RDB 文件。
```

---

### R02-3 ch10/后记: 动手实验缺操作步骤

**文件1**: `/Users/liu/dev/demos/redis-kafka-books/chapters/10-summary/chapter.md`
**位置**: L177（10.4.3 持续学习与全书收束）

**文件2**: `/Users/liu/dev/demos/redis-kafka-books/chapters/10-epilogue.md`
**位置**: L31（后记"下一步做什么"）

**内容**:

ch10 L177:
> 把 Redis 的 `appendfsync` 从 `everysec` 改成 `always`，用 `redis-benchmark` 看吞吐怎么跌。把 MySQL 的 `innodb_flush_log_at_trx_commit` 从 1 改成 0，强杀进程看丢多少。把 Kafka 的 `acks` 从 all 改成 1，断一个 Broker 看消息丢不丢。

后记 L31:
> `innodb_flush_log_at_trx_commit` 从 1 调到 2，吞吐能涨多少？`appendfsync` 从 everysec 调到 always，延迟会增加多少？

**读者照做会不会出问题？**

**对于 ch10 L177（三个实验）**：

- **Redis 实验（appendfsync everysec -> always）**：读者知道要改配置文件和重启，但不知道 `redis-benchmark` 的具体命令参数。如果直接敲 `redis-benchmark` 不加 `-t` 选项，默认会跑全部测试（包括 PING_INLINE、MSET 等），可能干扰对 SET 命令吞吐的精确对比。建议给一个具体命令。
- **MySQL 实验（强杀进程看丢多少）**：**有潜在危险**。"强杀进程"没有区分 kill -9 与 kill -15（SIGTERM vs SIGKILL），也没有说明"杀了之后如何判断丢了数据"。MySQL 的 `innodb_flush_log_at_trx_commit=0` 下，进程在崩溃恢复后会回滚未提交事务——数据"没丢但被回滚了"和"数据丢了"是两回事，读者可能混淆。
- **Kafka 实验（断 Broker 看丢不丢）**：操作层面上可行，但缺"如何确认丢消息"的具体验证方法。消费者 offset 不会自动回滚，消息可能还在日志文件中只是消费者没读到——不是"丢"而是"不可见"。

**对于后记 L31（两个实验）**：
- 该段落在"下一步做什么"的语境下，语气是思考性提问（"吞吐能涨多少？"），不要求读者立即按步骤执行。风险低于 ch10 的"改参数看行为"段落。
- 但同样的，`redis-benchmark` 具体命令、Docker 环境如何搭建这些前置步骤缺失。

**严重度**: 中低。

理由：该段落在书中定位为"学习建议"而非"实验操作指南"。读者不会被卡住——即使不执行这些实验，书的核心论点（参数调优是性能/可靠性取舍）仍然完整。但作者既然有意让读者动手验证，就应该让实验可执行。当前文本介于"我知道这个道理"和"我能亲自验证"之间，效果打折扣。

两类读者反应：
- **A 类读者（有经验）**：知道怎么配 Docker、怎么改配置文件、怎么跑 benchmark。能自行补全缺失步骤。不会卡住。
- **B 类读者（经验较浅、想跟着做）**：卡在"我不知道如何开始"。建议在书中标注具体的 `redis-benchmark` 命令和配置文件修改路径，降低动手门槛。

**最小可行修复方案**:

针对 ch10 L177 的三个实验，各加一句具体的命令或操作指引。不拆段落结构，仅在原有建议后追加简洁的括号说明。

**old_string (ch10 L177)**:
```
改参数看行为，是最快的理解方式。把 Redis 的 `appendfsync` 从 `everysec` 改成 `always`，用 `redis-benchmark` 看吞吐怎么跌。把 MySQL 的 `innodb_flush_log_at_trx_commit` 从 1 改成 0，强杀进程看丢多少。把 Kafka 的 `acks` 从 all 改成 1，断一个 Broker 看消息丢不丢。亲手制造一次"丢数据"，你对参数的代价就有了肌肉记忆。
```

**new_string (ch10 L177)**:
```
改参数看行为，是最快的理解方式。把 Redis 的 `appendfsync` 从 `everysec` 改成 `always`，用 `redis-benchmark -t SET -n 100000` 对比两种配置下的吞吐差异。把 MySQL 的 `innodb_flush_log_at_trx_commit` 从 1 改成 0，用 `kill -9` 模拟掉电后检查是否丢事务（重启后检查 `SHOW ENGINE INNODB STATUS` 确认崩溃恢复次数）。把 Kafka 的 `acks` 从 all 改成 1，断一个 Broker 后用 `kafka-dump-log` 检查消息是否存在。亲手制造一次"丢数据"，你对参数的代价就有了肌肉记忆。
```

**old_string (后记 L31-32)**:
```
接下来，挑一个天天在用但从来没动过的参数，把旋钮往反方向拧一次。`innodb_flush_log_at_trx_commit` 从 1 调到 2，吞吐能涨多少？`appendfsync` 从 everysec 调到 always，延迟会增加多少？读过十遍"可靠性是用性能买来的"，不如在自己的终端里看它发生一次。
```

**new_string (后记 L31-32)**:
```
接下来，挑一个天天在用但从来没动过的参数，把旋钮往反方向拧一次。用 Docker 启动一个 MySQL 实例，把 `innodb_flush_log_at_trx_commit` 从 1 调到 2，用 `sysbench --test=oltp_write_only` 跑对比，看吞吐涨了多少。用 Docker 启动一个 Redis 实例，把 `appendfsync` 从 everysec 调到 always，用 `redis-benchmark -t SET -n 100000` 看延迟增加了多少。读过十遍"可靠性是用性能买来的"，不如在自己的终端里看它发生一次。
```

---

## 2. 严重度汇总

| 问题 | 文件 | 行号 | 严重度 | 读者是否会被卡住 |
|------|------|------|--------|-----------------|
| R02-1 ACL SETUSER 缺执行上下文 | ch06-security/chapter.md | L40-44 | **中** | 会。`>` 在 shell 中被解释为重定向符，命令报错 |
| R02-2 PSYNC ? -1 非用户命令 | ch09-data-sync/chapter.md | L67 | **低** | 不会。该文本描述的是内部协议行为，不是用户命令 |
| R02-3 动手实验缺操作步骤 | ch10-summary/chapter.md | L177 | **中低** | 轻度。有经验的读者能自行补全，但 MySQL 的"强杀"实验有模糊处 |
| R02-3 动手实验缺操作步骤 | 10-epilogue.md | L31-32 | **低** | 不会。该段落在"思考提问"语境下，不要求立即执行 |

---

## 3. 每章可复现性评级

| 章 | 评级 | 读者能否复现核心内容 | 缺什么 |
|----|------|---------------------|--------|
| 第 6 章 安全 | **B** | 可复现。全章以概念分析和横向对比为主，唯一代码块（ACL SETUSER）有执行上下文缺失但不影响对章节论点的理解 | 代码块前缺少执行场所说明 |
| 第 9 章 数据同步 | **A** | 可复现。全章为机制描述（状态机复制、PSYNC/GTID/LEO-HW/ISR），无可执行代码块。PSYNC ? -1 行内 backtick 描述内部协议行为，读者不会尝试执行 | 无 |
| 第 10 章 共性规律 | **B** | 大部分可复现。10.1-10.3 为抽象规律和框架，无需复现。10.4.3 的实验建议缺具体命令和验证方法 | redis-benchmark 命令、MySQL 崩溃实验的验证方法、Kafka 丢消息的验证方法 |
| 后记 | **B** | 大部分可复现。主体为回顾和致谢。"下一步做什么"段落的思考提问不需要立即执行，但意图让读者动手验证的 Docker 环境未提及 | 建议补充 Docker 启动命令和基准测试工具 |

### 评级释义

- **A**: 读者能完整复现书中所有命令/配置示例，所有命令有明确的执行上下文。
- **B**: 读者能理解全部内容，但动手验证时需要自行补全少量上下文或配置步骤。
- **C**: 多处命令或配置读者无法正确执行，缺乏关键的上下文说明。
