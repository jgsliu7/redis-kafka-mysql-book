# fig-4-5 GPT 生图提示词
## 2026-07-09 v1：✅ 一次通过
### 提示词
```
A clean technical sequence diagram titled MySQL一次写操作全链路 for a Chinese programming book. Timeline with lifelines: 客户端, InnoDB存储引擎, redo log重做日志, 双写缓冲DoubleWrite, 表空间数据文件. Flow: UPDATE arrives, write to redo log first WAL, modify buffer pool pages become dirty, transaction commit with innodb_flush_log_at_trx_commit, dirty pages enter flush list, background thread writes via doublewrite buffer to tablespace, checkpoint advances. Clean flat design, white background, muted blue colors, Chinese labels, 16:9.
```
### 结果
- 2026-07-09 v1：✅ 通过。时序流程清晰，WAL→脏页→双写→checkpoint 链路可见，中文正常。
