# fig-2-2 GPT 生图提示词

## 2026-07-09 第 1 次

### 提示词

```
A technical field layout diagram of Kafka RecordBatch V2 format for a Chinese programming book. Show a large rectangular box representing the full RecordBatch with header fields arranged inside:

Batch-level header fields (blue boxes):
- baseOffset (8B, 起始偏移量)
- batchLength (4B, 总字节长度)  
- partitionLeaderEpoch (4B, 任期号)
- magic (1B, 格式版本号 = 2)
- CRC (4B, 整批校验)
- attributes (2B, 压缩类型+时间戳+事务标记)
- lastOffsetDelta (4B, 末条消息偏移量差值)
- baseTimestamp / maxTimestamp (8B each)
- producerId / producerEpoch / baseSequence (producer state)
- recordsCount (4B, 记录数量)

Below header, show record bodies (green boxes) with annotation: "每条记录只存差值（offset/timestamp 相对 baseOffset/baseTimestamp 的 delta），不存绝对值"

Bottom callout box:
- "Batch 级 CRC 替代逐条 CRC → 省 CPU"
- "magic 字段自描述格式版本 → 新旧格式可共存"
- "批量压缩（zstd）→ 相似消息聚集时压缩比 2-6x"

Clean flat technical diagram, white background, blue/green color scheme. Chinese labels.
```

### 结果
- 2026-07-09 v1：字段名太密，中文乱码 ❌
- 2026-07-09 v2：✅ 通过。简化到 6 个核心字段 + 3 个注解框，中文正常。

### v2 提示词（最终采用）

```
A clean technical diagram titled Kafka RecordBatch V2 字段布局 showing the structure of a Kafka message batch. Left side shows a large rounded rectangle labeled RecordBatch containing several smaller colored blocks representing key header fields. The key fields to label in Chinese: baseOffset起始偏移量, batchLength总长度, magic格式版本号, CRC整批校验, baseTimestamp时间戳, recordsCount记录数量. Right side shows three annotation boxes: 批量压缩zstd压缩比2-6倍, Batch级CRC省去逐条校验CPU开销, 差值编码记录只存delta值. Clean flat design, white background, blue and green color scheme, 16:9.
```
