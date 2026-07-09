# fig-4-6 GPT 生图提示词
## 2026-07-09 v1：✅ 一次通过
### 提示词
```
A clean technical comparison diagram titled Kafka零拷贝数据流 for a Chinese programming book. Two parallel paths. Top path 传统拷贝: disk to kernel buffer to user buffer to socket buffer to NIC, marked 4次拷贝4次上下文切换. Bottom path 零拷贝sendfile: disk to kernel PageCache to NIC via DMA, marked 2次DMA拷贝2次上下文切换 data never enters user space. Green highlight on zero-copy path. Bottom note: 冷数据仍需走磁盘I/O. Clean flat design, white background, muted green colors, Chinese labels, 16:9.
```
### 结果
- 2026-07-09 v1：✅ 通过。传统 vs 零拷贝两条路径对比清晰，中文正常。
