# fig-3-6 GPT 生图提示词

## 2026-07-09 v1：✅ 一次通过

### 提示词

```
A clean technical comparison diagram for a Chinese programming book titled Kafka受控关闭对照普通关闭. Show two parallel timelines. Top timeline 受控关闭: Broker通知Controller我要走, Controller迁移Leader到ISR其他副本, Leader迁移完成回执, Broker刷盘退出 with green arrows and labels indicating no client impact. Bottom timeline 普通关闭: Broker直接刷盘退出, Controller心跳超时发现下线, 触发Leader重选 with red arrows and labels indicating client sees brief partition unavailability. Right side comparison annotation: 受控关闭慢但客户端无感知, 普通关闭快但有抖动窗口. Bottom note: 受控关闭前提Controller可达否则降级为普通关闭. Clean flat design, white background, green and red muted colors, Chinese labels, 16:9.
```

### 结果
- 2026-07-09 v1：✅ 通过。两条时间线对比清晰，绿色受控关闭 vs 红色普通关闭，中文正常。
