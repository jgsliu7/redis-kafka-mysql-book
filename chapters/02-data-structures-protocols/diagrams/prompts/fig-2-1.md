# fig-2-1 GPT 生图提示词

## 2026-07-09 第 1 次

### 提示词

```
A technical concept diagram showing Redis's five core data structures and their upgrade paths, for a Chinese programming book. The diagram should show:

Five boxes/layers for the five data structures:
1. SDS (简单动态字符串) - basic string type, with header showing len/alloc/free fields
2. 跳表 (Skip List) - for sorted sets, multi-level ordered linked list
3. 字典 (Dict) - hash table with progressive rehash (ht[0]→ht[1])
4. ziplist/listpack - compact list, continuous memory, high density  
5. intset - integer set with encoding upgrade (int16→int32→int64)

Show upgrade paths: ziplist→skiplist, intset→hashtable, listpack replacing ziplist (Redis 7.0)
Bottom annotation: "全部为内存快速存取服务" (All serve fast in-memory access)
Central theme label: "目标：极低延迟 + 省内存"

Clean flat design, white background, blue/green muted color scheme. Chinese labels. System-ui sans-serif font. Suitable for technical book illustration.
```

### 结果
- 2026-07-09 v1：结构可行但文字偏多 ⚠️
- 2026-07-09 v2：✅ 通过。五个盒子+升级箭头，中文正常，简洁明了。

### v2 提示词（最终采用）

```
A clean concept diagram for a Chinese programming book titled Redis五种底层数据结构. Show five rounded boxes arranged horizontally, each box containing a data structure icon and Chinese label: SDS简单动态字符串, 跳表SkipList, 字典Dict, 紧凑列表listpack, 整数集合intset. Draw upgrade arrows between boxes showing paths: intset升级为hashtable, ziplist升级为skiplist. Bottom annotation: 全为内存低延迟服务. Blue and green muted colors, flat design, white background, 16:9.
```
