# fig-2-3 GPT 生图提示词

## 2026-07-09 第 1 次

### 提示词

```
A three-column comparison diagram of communication protocols for a Chinese programming book. Three columns side by side:

Left column - Redis RESP:
- Title: "Redis RESP（纯文本）"
- 5 prefix characters: + (简单字符串), - (错误), : (整数), $ (批量字符串), * (数组)
- Example interaction: *3\r\n$3\r\nSET\r\n$3\r\nkey\r\n$5\r\nvalue\r\n
- Key traits: 人眼可读, 调试友好, 无版本协商
- Trade-off: 体积大, 无 Batch

Middle column - MySQL Binary Protocol:
- Title: "MySQL（紧凑二进制）"
- Three phases: 握手 → 命令 → 响应
- Pre-compiled statements: COM_STMT_PREPARE → statement_id → COM_STMT_EXECUTE
- Binary result set: 列元数据前置 + 行数据紧凑编码
- Key traits: 预编译省 CPU, 二进制省带宽
- Trade-off: 人不可读, 实现复杂

Right column - Kafka Request/Response:
- Title: "Kafka（请求/响应体系）"
- Unified header: api_key(2B) + api_version(2B) + correlation_id(4B) + client_id
- Version negotiation via api_key + api_version
- Batch-first: Produce/Fetch in RecordBatch units, zero-copy (sendfile)
- Key traits: 版本独立演进, 批量优先
- Trade-off: 协议复杂, 学习曲线

Bottom row: 4-dimension comparison table (编码方式/批量策略/版本演进/人机可读性)

Clean technical diagram, white background, three distinct column colors (red/magenta for Redis, blue for MySQL, green for Kafka). Chinese labels.
```

### 结果
- 2026-07-09 v1：中文密集部分模糊 ⚠️
- 2026-07-09 v2：✅ 通过。三列对比清晰，中文正常。

### v2 提示词（最终采用）

```
A three-column comparison diagram for a Chinese programming book comparing three communication protocols. Left column red header Redis RESP: show a simple text command example SET key value with arrows, labeled 纯文本人眼可读. Middle column blue header MySQL二进制协议: show precompiled statement flow Prepare Execute Fetch, labeled 预编译省CPU. Right column green header Kafka请求响应: show a unified header with api_key api_version fields and zero-copy sendfile path, labeled 批量优先版本独立演进. Bottom row: four-dimension comparison table 编码方式 批量策略 版本演进 人机可读性. Clean flat design, white background, three distinct muted colors, 16:9.
```
