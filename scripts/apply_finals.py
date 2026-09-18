#!/usr/bin/env python3
"""按用户页面定稿（0917/finals/<标题>.json）把确认稿写回章节原稿。

当前支持带字符偏移的 A 代报告（如 序言）。写回策略：
  - 每条断言 md[start:end] == old 仍然成立（基线漂移即中止）
  - 区间两两无重叠断言
  - final == old 的条目跳过（等同不改）
  - 降序替换，一次写盘
  - 写后用"原 md + 偏移 + final"离线重构造整文件，与落盘文件逐字节比对
安全：章节文件在 git 内，写坏可 git checkout 恢复。

用法：
  python3 scripts/apply_finals.py 0917/序言精读审查.html           # dry-run，只打印计划
  python3 scripts/apply_finals.py 0917/序言精读审查.html --write   # 实际写回
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))

# 写回时对个别条目做的体例级修正（不动字词，可审计）：id → [(原文片段, 修正片段)]
NORMALIZE = {
    '序言': {
        'P-07': [('无论AI coding多么强大', '无论 AI coding 多么强大')],  # 中英混排补空格（双 agent 核对发现）
    },
}


def load(report_html):
    src = open(os.path.join(ROOT, report_html), encoding='utf-8').read()
    m = re.search(r'id="review-data"[^>]*>(.*?)</script>', src, re.S)
    if not m:
        raise SystemExit('该报告无 review-data JSON（非 A 代模板，暂不支持自动写回）')
    rows = json.loads(m.group(1))
    title = re.match(r'(第.+?章|序言)', os.path.basename(report_html)).group(1)
    finals = json.load(open(os.path.join(ROOT, '0917', 'finals', title + '.json'),
                            encoding='utf-8'))['items']
    md_path = os.path.join(ROOT, re.search(r'<body[^>]*data-path="([^"]+)"', src).group(1))
    return title, rows, finals, md_path


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    report = sys.argv[1]
    write = '--write' in sys.argv[2:]
    title, rows, finals, md_path = load(report)
    md = open(md_path, encoding='utf-8').read()

    todo = []
    for d in sorted(rows, key=lambda r: r['start']):
        rid = d['id']
        if rid not in finals:
            raise SystemExit('%s: finals 缺 %s' % (title, rid))
        fin = finals[rid]['final']
        if fin == '' and d.get('new', '') != '':
            raise SystemExit('%s: %s 定稿为空但建议稿非空（疑似误清空），中止' % (title, rid))
        for a, b in NORMALIZE.get(title, {}).get(rid, []):
            if a in fin:
                fin = fin.replace(a, b)
                print('%-6s 体例修正: %r → %r' % (rid, a, b))
        if md[d['start']:d['end']] != d['old']:
            raise SystemExit('%s: 偏移失效（当前文与 old 不符）: %s' % (title, rid))
        if fin == d['old']:
            print('%-6s SKIP 定稿==原文' % rid)
            continue
        todo.append((d['start'], d['end'], rid, d['old'], fin))

    spans = [(s, e) for s, e, *_ in todo]
    for (s1, e1), (s2, e2) in zip(spans, spans[1:]):
        if e1 > s2:
            raise SystemExit('区间重叠: %s' % [(s, e) for s, e, r, *_ in todo])

    out, cursor = [], 0
    for s, e, rid, old, fin in todo:
        out.append(md[cursor:s]); out.append(fin); cursor = e
    out.append(md[cursor:])
    new_md = ''.join(out).rstrip('\n') + '\n'  # 删句后规整文件尾为单换行

    print('\n%s：%d 条替换 / %d 条跳过；md %d → %d 字符（%+d）'
          % (title, len(todo), len(rows) - len(todo), len(md), len(new_md), len(new_md) - len(md)))
    for s, e, rid, old, fin in todo:
        print('  %-6s L%-3s %4d → %4d 字符  %s…'
              % (rid, next(d['line_start'] for d in rows if d['id'] == rid),
                 len(old), len(fin), fin[:24].replace('\n', '⏎')))

    if not write:
        print('\nDRY-RUN（未写盘）。确认后加 --write 执行。')
        return

    # 落盘 + 离线重构造复核（双保险）
    open(md_path, 'w', encoding='utf-8').write(new_md)
    reread = open(md_path, encoding='utf-8').read()
    if reread != new_md:
        raise SystemExit('写盘校验失败！请 git checkout -- %s 恢复' % md_path)
    print('\n已写回 %s 并通过重构造复核。' % md_path)


if __name__ == '__main__':
    main()
