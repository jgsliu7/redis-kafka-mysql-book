# fig-3-1 GPT 生图提示词

## 2026-07-09 v1：✅ 一次通过

### 提示词

```
A clean technical diagram for a Chinese programming book comparing startup and shutdown as symmetric state machine transitions. Left side shows a process starting up: from executable file through state reconstruction to ready state, with an arrow labeled 启动重建状态. Right side shows graceful shutdown: from running state through snapshot and resource release to stopped state, with an arrow labeled 关闭快照释放资源. Center shows a crash event pulling the system back to incomplete state. Right side annotates three tensions: 一致性vs可用性, 速度vs确定性, 单机vs分布式. Clean flat design, white background, muted blue and orange colors, Chinese labels, 16:9.
```

### 结果
- 2026-07-09 v1：✅ 通过。中文正常，启动/关闭对称结构清晰，三对矛盾标注可见。
