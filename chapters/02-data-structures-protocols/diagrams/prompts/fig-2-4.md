# fig-2-4 GPT 生图提示词

## 2026-07-09 第 1 次

### 提示词

```
A technical diagram of MySQL InnoDB B+ Tree structure for a Chinese technical book. The diagram should show a three-level B+ tree: Root node at top, Internal nodes in middle, Leaf nodes at bottom.

Key design elements to show:
- Root and internal nodes contain ONLY keys and child pointers (no row data), labeled in Chinese
- Leaf nodes contain complete row data plus bidirectional linked list arrows between them
- Each node represents one 16KB disk page, marked with "16KB 页"
- Blue arrows showing point query path from root to leaf
- Green bidirectional arrows between leaf nodes showing range scan path
- Clean, minimal style with muted colors (blue for internal nodes, green for leaf nodes)
- Chinese labels throughout
- Include a "key tradeoff" callout box at bottom: internal nodes only store keys means hundreds of keys fit in 16KB so tree is only 2-3 levels deep (2-3 I/O for point query); write path cost is page splits

Style: Clean technical illustration, no gradients, flat design, suitable for a programming book. White background. System-ui sans-serif font.
```

### 结果
- 2026-07-09 v1：文字太密，中文部分乱码 ❌
- 2026-07-09 v2：✅ 通过。树结构清晰，中文正常。提示词简化为只标关键字段。

### v2 提示词（最终采用）

```
A clean technical diagram titled MySQL InnoDB B+树结构 for a Chinese programming book. Show a three-level tree: root node at top labeled 根节点只存键和指针, two internal nodes in middle labeled 内部节点只存键不含行数据, five leaf nodes at bottom in green labeled 叶子节点存完整行数据. Draw green bidirectional arrows between leaf nodes for range scan. Mark each node box with 16KB页. Left side blue arrow showing point query path from root to leaf. Bottom callout box: 点查2-3次I/O, 范围扫描顺链表前进. Clean flat design, white background, blue and green muted colors, 16:9.
```
