# fig-3-4 GPT 生图提示词

## 2026-07-09 v1：✅ 一次通过

### 提示词

```
A clean technical sequence diagram for a Chinese programming book titled InnoDB崩溃恢复时序. Show four lifelines: InnoDB存储引擎, redo重做日志, BufferPool缓冲池, undo回滚日志. Time flows top to bottom. First phase marked redo重放往前补: scan redo from checkpoint LSN, replay all page modifications into buffer pool regardless of transaction commit status. Second phase marked undo回滚往后撤: identify uncommitted transactions, rollback their modifications via undo log. Final state marked 一致性恢复: all committed preserved, all uncommitted rolled back. Bottom annotation: 为什么慢因为要重算崩溃瞬间的中间状态. Clean flat design, white background, muted blue and red colors, Chinese labels, 16:9.
```

### 结果
- 2026-07-09 v1：✅ 通过。四条生命线清晰，redo 重放→undo 回滚两阶段分明，中文正常。
