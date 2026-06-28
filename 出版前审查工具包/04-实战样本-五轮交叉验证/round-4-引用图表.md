# 第 4 轮：交叉引用 + 图表语义（交叉印证）

> **方法**：4 Finder（引用域 2 + 图表域 2）+ 验证员复核冲突/单 Agent 候选。
> - 引用域：`crossref-validity` + `general-purpose`
> - 图表域：`svg-semantics` + `architect-reviewer`
> - 验证员 = `general-purpose`（读 SVG 源码 + WebSearch）
>
> **门槛**：同域 ≥2 Agent 认定才 CONFIRMED；两方冲突由验证员读源码裁定。
>
> **结论**：CONFIRMED **8 条**（引用 5 + 图表 3），驳回 6 条。**全书图表体系 52 张整体自洽**（三方编号一致、数值/参数与正文吻合 49/52），仅 3 张有语义问题；引用体系唯一硬错是 ch7:158 指向不存在的"9.4.3 节"。**references 是持续灾区**（R2/R3/R4 连续命中）。

---

## 一、CONFIRMED 发现（8 条）

### 🔴 交叉引用硬错

| # | 位置 | 问题 | 印证 | 改法 |
|---|------|------|------|------|
| X1 | ch7:158 | 引用"LEO/HW…见**第 9 章 9.4.3 节**"——ch9 9.4 节下 ### 全是无编号标题，**不存在 9.4.3** | crossref + GP（双中） | 改"见第 9 章 9.4 节'LEO、HW 与 ISR'" |
| X2 | ch9:345 | "第 10 章会把**八章**的零散发现收敛成…"——全书口径"前九章"（ch10:5/11、epilogue:3、fig-1-2），且 ch9 自身就是第九章，**自相矛盾** | GP + 验证员 | "八章"→"前九章" |

### 🟠 references 系统性问题（R2/R3/R4 连续命中）

| # | 位置 | 问题 | 印证 | 改法 |
|---|------|------|------|------|
| X3 | references:5/18/24/30/36/42/49/55/62 | **章标题与正文 H1/SUMMARY 系统性不对应**（如 ref"为什么要比"vs 正文"引言"；ref"融会贯通"vs 正文"万法归一"） | crossref + GP + R2（三方） | 按 SUMMARY.md/正文 H1 权威基准统一 10 个章标题 |
| X4 | references:5-62 | **章序号体例混用**：references 用"第一章/第二章…"（中文数字），正文 H1 全用"第 1 章/第 2 章"（阿拉伯数字） | GP + 验证员 | 统一阿拉伯数字"第 1 章" |

### 🟠 图序倒置（编号连续，但物理位置乱序）

| # | 位置 | 问题 | 印证 | 改法 |
|---|------|------|------|------|
| X5 | ch1:202 / ch7:199 / ch8:310 | **图出现顺序与编号不符**：图 1-2(L202)晚于图 1-3(L126)；图 7-3(L199)晚于图 7-4(L94)/7-5(L139)；图 8-7(L310)晚于图 8-8(L216) | GP + 验证员 | 重编号或重排，使物理顺序=编号顺序 |

### 🔴 图表语义问题（3 张，52 张中）

| # | 位置 | 问题 | 印证 | 改法 |
|---|------|------|------|------|
| G1 | fig-7-1:48 ↔ ch7:86 | **CAP 立场图文矛盾**：图标"偏 AP"，但正文 ch7:86"分区时实际偏 CP…本书不作绝对的 AP/CP 一刀切归类"（图丢了"偏 CP"纠偏） | svg-semantics + R3 CAP 印证 | 改"归类有争议（异步复制偏 AP，分区时少数派停写偏 CP；本书不作绝对归类）"，与正文/表格对齐 |
| G2 | fig-9-7 ↔ ch9:219 | **leader epoch 截断表示歧义**：请求/响应 epoch 写成 1/2 跨值比较，endOffset 与"epoch 起点"混淆，读者难判 m2' 的 offset | svg-semantics + architect（双中，严重度分歧） | 统一锚定 epoch=1：副本上报 (epoch=1, lastOffset=4)；Leader 回 (epoch=1, endOffset=3)；副本截断到 3 |
| G3 | fig-9-5:36-44 ↔ ch9:147 | **半同步 ACK 两档只画一档**：图只画 AFTER_COMMIT 顺序，但标注并列 after_sync/after_commit；AFTER_SYNC 是"先 ACK 再 commit"顺序相反 | svg-semantics + architect（双中） | 加注"图示 AFTER_COMMIT；AFTER_SYNC 先 ACK 再 commit"，或分画两流程 |

---

## 二、已驳回（6 条，正确剔除）

| 位置 | 原候选 | 驳回理由 |
|------|--------|---------|
| fig-8-2:21 | RDB "version 0010 (4B)" 错（architect 称应"0011"且非二进制） | **FALSE——architect 误读**：RDB 版本是 4 字节 ASCII 十进制串，"0010"=v10=Redis 7.0，与 ch8:62 正文一致。svg-semantics 判对 |
| fig-9-6:39 | "同一组内事务无锁冲突"措辞不准 | **KEEP**——与 ch9:165 正文"本身就没冲突过·基于既成事实的并行"同义，简化表达非误导 |
| fig-8-4:81 | "超过页半时溢出"阈值粗 | **KEEP**——InnoDB 经典近似阈值（COMPACT 亦然），示意图粗近似可接受 |
| fig-4-6:100 | "消费者按内存速度读"误导 | **KEEP**——指 sendfile 源端从 PageCache 读（相对磁盘 IO 是内存速度），第 105 行 caveat 已限定 |
| ch10:1 / ch2:1 | H1 双破折号"——"违规 | **KEEP**——ch2 也用"——"，集中在 2 章，落在"个位数"约束内非违规；可选统一为"—" |
| fig-7-2 槽范围 | B"5461–10922"边界显示歧义 | **CORRECT**——5461+5462+5461=16384 算术正确（svg-semantics 验证），仅显示可加"含两端"注 |

---

## 三、本轮"优化"动作

1. **冲突裁定靠读 SVG 源码 + 官方文档**：fig-8-2 的 RDB version 冲突（architect vs svg-semantics）由验证员查 RDB 文件格式规范（ASCII 十进制串）裁定——**architect 误读为二进制**，svg-semantics 对。技术图争议必须查规范，不能靠肉眼/记忆。
2. **图表体系整体健康**：52 张中 49 张语义正确（箭头/流程/数值/参数/术语全与正文吻合，含 16384 槽、2KB bitmap、16KB 页、FIL Header 38B、replica.lag.time.max.ms 30s、acks 默认等），仅 3 张有问题。这是全书最扎实的部分。
3. **references 持续灾区**：R2（4 处字符/术语）、R3（LSM 事实错）、R4（章标题/序号体例）连续命中 references——**建议第 5 轮 compliance 把 references 整表重做**（章标题对齐 + 序号统一 + GB/T 7714 著录格式）。
4. **CAP 第 N 次浮现**：fig-7-1 的"偏 AP"标注是 CAP nuance 丢失在图里的又一处（R3 已发现 ch9/ch10 三处正文）。**建议把 fig-7-1 + ch9:59/143 + ch10:100 的 CAP nuance 统一改成同句式**，并写入 pub_assertions.py 断言。

---

*印证 Agent：crossref-validity / svg-semantics / general-purpose(引用域+验证员) / architect-reviewer(图表域)。本文件是五轮交叉验证第 4 轮结果，CONFIRMED 条目汇总进 `00-总览.md`。*
