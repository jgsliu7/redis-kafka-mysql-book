#!/usr/bin/env python3
"""Tally consensus across 5 agent reviews."""

import re
from collections import Counter
from pathlib import Path

ROOT = Path('/Users/liu/dev/demos/redis-kafka-books/0910/m3')

AGENTS = [
    ('编辑部主任', 'agent1_editor.md'),
    ('作者代言人', 'agent2_author.md'),
    ('读者代表',  'agent3_reader.md'),
    ('语言学家',  'agent4_linguist.md'),
    ('保守派',    'agent5_conservative.md'),
]

LINE_RE = re.compile(
    r'\[([A-J]\d+)\]\s*是否值得改:([^\s|]+)\s*\|\s*要不要改:([^\s|]+)\s*\|\s*改得对不对:([^\s|]+)'
)


def parse(text):
    out = {}
    for line in text.split('\n'):
        m = LINE_RE.search(line)
        if m:
            eid, worth, do, result = m.groups()
            out[eid] = (worth, do, result)
    return out


# Load all 5 verdicts
verdicts = {}
for name, fn in AGENTS:
    text = (ROOT / fn).read_text(encoding='utf-8')
    verdicts[name] = parse(text)

# Load entries to get the canonical ID list
import json
entries = json.loads((ROOT / 'entries.json').read_text(encoding='utf-8'))
all_ids = list(entries.keys())

print(f'Total entries: {len(all_ids)}')
print(f'Agent coverage:')
for name in verdicts:
    print(f'  {name}: {len(verdicts[name])}')

# Classify each entry by 3-axis consensus
def axis_consensus(eid, axis):
    """Returns (most_common_value, vote_count, total_relevant)."""
    vals = []
    for name in verdicts:
        v = verdicts[name].get(eid)
        if not v: continue
        # '语言学家' uses '超出语言维度' / '不在审查范围' as out-of-scope markers
        if name == '语言学家':
            if v[axis] in ('超出语言维度', '不在审查范围'):
                continue  # skip — linguist abstained
        if v[axis] in ('值得', '不值得', '视情况'):
            vals.append((name, v[axis]))
        elif v[axis] in ('要', '不要', '看读者', '看作者', '看情况', '看成本', '看事实', '看结构', '看风格', '看合规', '看密度', '看节奏', '看钩子', '看读者定位', '看编辑', '看本书标准', '看数字'):
            vals.append((name, v[axis]))
        elif v[axis] in ('改对了', '改坏了', '改得不对不改也不好', '改对了但代价大', '改得勉强', '改细了', '改过头', '改窄了', '改松了', '部分对', '参考', '风险高', '待定', '可', '略啰嗦', '伪问题'):
            vals.append((name, v[axis]))
    if not vals: return ('(弃权)', 0, 0)
    counter = Counter(v for _, v in vals)
    return counter.most_common(1)[0][0], len(vals), len(vals)


# Print summary tables
print('\n' + '='*100)
print('CONVERGENCE TABLE')
print('='*100)
print(f'{"ID":<6} {"Worth":<12} {"Do":<12} {"Result":<14} 备注')
print('-'*100)

strong_agree = []
strong_disagree = []
abstained = []

for eid in all_ids:
    worth_v, worth_n, _ = axis_consensus(eid, 0)
    do_v, do_n, _      = axis_consensus(eid, 1)
    res_v, res_n, _    = axis_consensus(eid, 2)
    # pick majority on "do改" axis as the main verdict
    if do_n >= 4 and do_v == '要' and res_n >= 4 and res_v in ('改对了', '可'):
        strong_agree.append(eid)
    elif do_n >= 3 and do_v == '不要' and res_n >= 3 and res_v in ('改坏了', '伪问题', '风险高'):
        strong_disagree.append(eid)
    if worth_n == 0 or do_n == 0:
        abstained.append(eid)
    print(f'{eid:<6} {worth_v[:10]:<12} {do_v[:10]:<12} {res_v[:12]:<14}')

print('\n' + '='*100)
print(f'STRONG AGREEMENT (≥4 agents say "要改" + "改对了/可"): {len(strong_agree)} 条')
print('='*100)
print(' / '.join(strong_agree))

print('\n' + '='*100)
print(f'STRONG DISAGREEMENT (≥3 agents say "不要改" + "改坏了/伪问题"): {len(strong_disagree)} 条')
print('='*100)
print(' / '.join(strong_disagree))

print('\n' + '='*100)
print(f'ABSTAINED (语言学家全部跳过该类): {len(abstained)} 条')
print('='*100)
print(' / '.join(abstained))


# Now compute consensus strength — SEPARATING "支持改" vs "反对改"
print('\n' + '='*100)
print('CONVERGENCE PER ENTRY (count of agents agreeing on "要不要改")')
print('='*100)

# Bucket A: clear "要改" vote
# Bucket B: clear "不要" vote
# Bucket C: split (top is 看X or 2-2 tie)
buckets = {
    'A. 全支持改 (5票"要")': [],
    'B. 4票支持改': [],
    'C. 多数支持改 (3票"要")': [],
    'D. 全反对改 (≥4票"不要")': [],
    'E. 多数反对改 (3票"不要")': [],
    'F. 看情况/分裂 (无多数)': [],
}

for eid in all_ids:
    votes = []
    for name in verdicts:
        v = verdicts[name].get(eid)
        if not v: continue
        if name == '语言学家' and v[1] in ('看事实', '看结构', '看风格', '看合规', '看密度', '看节奏', '看钩子', '看读者定位', '看编辑', '看本书标准', '看数字'):
            continue  # abstained
        votes.append(v[1])
    n_yes  = sum(1 for v in votes if v == '要')
    n_no   = sum(1 for v in votes if v == '不要')
    n_depends = sum(1 for v in votes if v.startswith('看'))
    n_total = len(votes)
    if n_yes >= 4:
        buckets['B. 4票支持改'].append(eid) if n_yes == 4 else buckets['A. 全支持改 (5票"要")'].append(eid)
    elif n_yes == 3:
        buckets['C. 多数支持改 (3票"要")'].append(eid)
    elif n_no >= 4:
        buckets['D. 全反对改 (≥4票"不要")'].append(eid)
    elif n_no == 3:
        buckets['E. 多数反对改 (3票"不要")'].append(eid)
    else:
        buckets['F. 看情况/分裂 (无多数)'].append(eid)

for k, v in buckets.items():
    print(f'  {k:<35}: {len(v):>3} 条  → {" / ".join(v)}')


# Save full report
report = []
report.append('# 5 Agent 二轮评审合并报告')
report.append('')
report.append(f'本报告基于 v1.html 的 84 条意见，由 5 个不同视角 Agent 独立评估后合并。')
report.append('')
report.append('## 共识分类')
report.append('')
report.append('### 🟢 A. 全支持改（5 票"要改"）')
report.append('')
for eid in buckets['A. 全支持改 (5票"要")']:
    worth_v, _, _ = axis_consensus(eid, 0)
    do_v, _, _ = axis_consensus(eid, 1)
    res_v, _, _ = axis_consensus(eid, 2)
    report.append(f'- **{eid}** — {worth_v} / {do_v} / {res_v}')
report.append('')
report.append('### 🟢 B. 强支持改（4 票"要改"）')
report.append('')
for eid in buckets['B. 4票支持改']:
    worth_v, _, _ = axis_consensus(eid, 0)
    do_v, _, _ = axis_consensus(eid, 1)
    res_v, _, _ = axis_consensus(eid, 2)
    report.append(f'- **{eid}** — {worth_v} / {do_v} / {res_v}')
report.append('')
report.append('### 🟡 C. 多数支持改（3 票"要改"）')
report.append('')
for eid in buckets['C. 多数支持改 (3票"要")']:
    worth_v, _, _ = axis_consensus(eid, 0)
    do_v, _, _ = axis_consensus(eid, 1)
    res_v, _, _ = axis_consensus(eid, 2)
    report.append(f'- **{eid}** — {worth_v} / {do_v} / {res_v}')
report.append('')
report.append('### 🔵 D. 全反对改（≥4 票"不要改"）')
report.append('')
for eid in buckets['D. 全反对改 (≥4票"不要")']:
    worth_v, _, _ = axis_consensus(eid, 0)
    do_v, _, _ = axis_consensus(eid, 1)
    res_v, _, _ = axis_consensus(eid, 2)
    report.append(f'- **{eid}** — {worth_v} / {do_v} / {res_v}')
report.append('')
report.append('### 🔷 E. 多数反对改（3 票"不要改"）')
report.append('')
for eid in buckets['E. 多数反对改 (3票"不要")']:
    worth_v, _, _ = axis_consensus(eid, 0)
    do_v, _, _ = axis_consensus(eid, 1)
    res_v, _, _ = axis_consensus(eid, 2)
    report.append(f'- **{eid}** — {worth_v} / {do_v} / {res_v}')
report.append('')
report.append('### ⚪ F. 看情况/分裂（无多数）')
report.append('')
for eid in buckets['F. 看情况/分裂 (无多数)']:
    worth_v, _, _ = axis_consensus(eid, 0)
    do_v, _, _ = axis_consensus(eid, 1)
    res_v, _, _ = axis_consensus(eid, 2)
    report.append(f'- **{eid}** — {worth_v} / {do_v} / {res_v}')

(ROOT / 'consensus_report.md').write_text('\n'.join(report), encoding='utf-8')
print(f'\nWrote {ROOT/"consensus_report.md"}')
