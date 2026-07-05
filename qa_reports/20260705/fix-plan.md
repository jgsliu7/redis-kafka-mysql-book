# 阶段 3 修复执行方案

> 创建：2026-07-05 | 基于 22 agent 审查发现汇总（findings_master.md）

## 核心原则（AGENTS.md 规则 1+2）

```
每个问题：3 个不同视角 agent 独立分析 → ≥2 同意才修
每个文件：单人 Edit 执行 → ≥2 agent 验证 → 通过才关
```

## 三视角分析模型

每个修复问题派出 3 个 agent，分别从以下视角独立判断：

| 视角 | Agent 类型 | 核心问题 |
|------|-----------|---------|
| **A. 技术准确性** | architect-reviewer / source-contributor | 修复方案技术上对不对？会不会引入新的事实错误？ |
| **B. 读者影响** | interviewee-reader / tech-editor | 改了之后读者更好懂还是更困惑？上下文衔接自然吗？ |
| **C. 实施精确性** | typo-grammar / term-consistency / crossref-validity | old_string 是否精确匹配？new_string 措辞/术语/格式是否正确？ |

**共识规则**：≥2/3 同意同一修复方案 → 批准执行。1/3 或全分歧 → 总调度介入裁决。

## P0 问题分组（6 组 × 3 agent = 18 agent）

| 组 | 文件 | P0 问题 | Agent A | Agent B | Agent C |
|----|------|--------|---------|---------|---------|
| G1 | ch06 | Kafka ACL 版本历史 + Redis ACL 加盐 | source-contributor | interviewee-reader | term-consistency |
| G2 | ch04, ch08 | aof-use-rdb-preamble "已移除" | architect-reviewer | reader-operability | fact-consistency |
| G3 | ch10 | sync_binlog=1 "需再开启" | architect-reviewer | interviewee-reader | typo-grammar |
| G4 | ch08 | 标点冗余 + fig-8-7↔8-8 互换 | source-contributor | tech-editor | crossref-validity |
| G5 | ch01 | 句子成分残缺 "代价是。" | typo-grammar | tech-editor | fact-consistency |
| G6 | 全书 | 商标声明缺失 | compliance | tech-editor | term-consistency |

## 中严重度问题分组（按文件，6 组）

| 组 | 文件 | 问题数 | 关键问题 |
|----|------|--------|---------|
| M1 | ch01 | 4 | 阅读路径承诺、图编号不连续、设问堆叠、破立句式 |
| M2 | ch02 | 4 | 跳表选型、SDS 惰性释放、全书声音最弱、启示模板化 |
| M3 | ch04 | 6 | PageCache 代价、LFU 衰减、对比表"几乎无"、WAL/redo 混用 |
| M4 | ch07 | 5 | resharding 代价、acks=all 延迟模型、CAP 重复三次 |
| M5 | ch08 | 3 | 图文关联裸奔、图前导语缺失 |
| M6 | ch09+ch10 | 6 | 并行复制并行度、声音空洞、五规律五维度关系、实验不可复现 |

## 执行顺序

1. **先修 P0**（6 组，18 agent 分析 → 综合裁决 → 逐文件 Edit → 12 agent 验证）
2. **再修中严重度**（6 组，18 agent 分析 → 综合裁决 → 逐文件 Edit → 12 agent 验证）
3. **低严重度/MAYBE** — 视时间决定是否修
4. **阶段 4 回归** — 重跑 svg_audit + build + 关键 agent 复检

## 产物

```
qa_reports/20260705/
├── fix-plan.md              ← 本文件
├── fix-analysis/            ← 三视角分析报告
│   ├── G1-ch06-acl/
│   │   ├── A-source-contributor.md
│   │   ├── B-interviewee-reader.md
│   │   └── C-term-consistency.md
│   ├── G2-ch04-ch08-rdb-preamble/
│   └── ...
├── fix-log/                 ← 修复执行日志
└── regression/              ← 回归验证报告
```
