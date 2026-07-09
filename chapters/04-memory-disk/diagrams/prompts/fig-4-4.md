# fig-4-4 GPT 生图提示词
## 2026-07-09 v1：✅ 一次通过
### 提示词
```
A clean technical diagram titled InnoDB缓冲池三分链表 for a Chinese programming book. Three linked lists side by side: Free List 空闲页池 on left, LRU List 活跃页链表 in center split into New Sublist 5/8 hot zone and Old Sublist 3/8 cold zone separated by midpoint, Flush List 脏页链表 on right. Arrows showing page flow: new page from Free List enters LRU at midpoint in Old zone, after innodb_old_blocks_time 1000ms if accessed again promotes to New zone, modified pages enter Flush List for background checkpoint. Clean flat design, white background, muted blue and green colors, Chinese labels, 16:9.
```
### 结果
- 2026-07-09 v1：✅ 通过。三分链表结构清晰，页流转路径可见，中文正常。
