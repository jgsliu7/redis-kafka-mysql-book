#!/usr/bin/env python3
"""GenC 报告（第 2/3 章旧模板，无字符偏移）按用户定稿写回章节原稿。

定位策略：
  报告的 old/new/final 是渲染纯文本（markdown 行内记号已被剥掉：`code`、**bold**）。
  把章节 md 做同样口径的"剥记号归一化"并建立 归一化字符→原文位置 映射，
  用归一化后的 old 在归一化 md 中查找，要求唯一命中，再映射回原文区间；
  区间边界外扩吃进贴边的记号字符，避免把成对的 **加粗** 拆开留孤儿。

移植策略（保留行内格式）：
  区间整体替换为 final；替换前把原文区间内的 `代码 span` 与 **加粗** 逐个在
  final 中找到同文出现并回填记号：
    - 长 token 先配（防 `SAVE` 错包进 `SHUTDOWN NOSAVE` 的子串）
    - 命中两侧不得是 ASCII 字母/数字/下划线/记号字符（词边界）
    - 命中不得落在已回填的区间内
  原文区间有而 final 找不到的记号 = 随改稿删除，打印备查。
  嵌套记号（加粗内含代码）当前不支持，出现即中止该行转人工。

体例修正（不动字词，可审计）：NORMALIZE 按章对 final 做替换（如弯引号归一为
本章一贯的直引号——双 agent 核对发现）。

守卫：
  - 章节 md 必须与 git HEAD 一致（基线漂移即中止）
  - 每条 old 唯一命中（0 或 >1 都中止，待人工消歧）
  - 区间两两不重叠（首尾相接允许）
  - 替换段归一化结果必须等于 final（自洽断言）
  - 区间内 ` 与 * 记号必须配对（奇偶校验）
  - 写盘后离线重构造复核

用法：
  python3 scripts/apply_finals_genc.py 0917/第三章精读审查_0333f889.html            # dry-run
  python3 scripts/apply_finals_genc.py 0917/第三章精读审查_0333f889.html --write
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))

MARKER = '*_`'

# 写回前对 final 做的体例级修正（不动字词，可审计）：title → [(原文片段, 修正片段)]
NORMALIZE = {
    '第三章': [('“', '"'), ('”', '"')],  # 弯引号归一为本章一贯的直引号
}

# 建议稿更名后按全书体例须恢复的加粗引导句（报告是渲染纯文本带不出格式；
# 仅补记号不动字词，双 agent 改前核对圈定）：title → {rid: [短语, …]}
STRUCT = {
    '第三章': {
        'C3-05': ['收尾工作与停服时间。', '提前准备与按需初始化。'],
        'C3-09': ['第四段：进入事件循环。'],
        'C3-10': ['第三步是否生成 RDB 由用户决定。'],
        'C3-11': ['配置加载段'],
        'C3-16': ['准备配置与节点角色。', '取得元数据，恢复本地日志。', '满足条件后才接请求。'],
        'C3-24': ['第二，关闭参数暴露了不同的取舍。'],
    },
}


def normalize(s):
    """剥 markdown 行内记号，返回 (归一化文本, 归一化字符→原文位置映射)。"""
    out, idx = [], []
    i = 0
    while i < len(s):
        c = s[i]
        if c == '`':                      # 行内代码记号（含 ``` 围栏一起吞）
            j = i + 1
            while j < len(s) and s[j] == '`':
                j += 1
            i = j
            continue
        if c == '*' or c == '_':          # 强调记号
            i += 1
            continue
        out.append(c)
        idx.append(i)
        i += 1
    return ''.join(out), idx


def transplant(raw_span, final):
    """把 raw_span 中的 `代码` 与 **加粗** 回填到 final；返回 (结果, 落空记号列表)。"""
    marks = [(m.start(), m.end(), '`', m.group(1))
             for m in re.finditer(r'`([^`\n]+)`', raw_span)]
    marks += [(m.start(), m.end(), '**', m.group(1))
              for m in re.finditer(r'\*\*([^*\n]+)\*\*', raw_span)]
    for i in range(len(marks)):
        for j in range(len(marks)):
            if i != j and marks[j][0] <= marks[i][0] and marks[i][1] <= marks[j][1]:
                raise SystemExit('嵌套行内记号（加粗内含代码等）暂不支持，转人工: %r'
                                 % (marks[j][3],))
    marks.sort(key=lambda t: (-len(t[3]), t[0]))   # 长 token 先配
    result, wrapped, dropped = final, [], []
    for _, _, mark, tok in marks:
        probe = tok.replace('`', '')
        if mark + probe + mark in result:   # 已有同文记号（结构表或前次回填），不重复包
            continue
        pat = re.compile(r'(?<![A-Za-z0-9_`*])' + re.escape(probe) + r'(?![A-Za-z0-9_`*])')
        hit = next((m for m in pat.finditer(result)
                    if all(m.end() <= w0 or w1 <= m.start() for w0, w1 in wrapped)), None)
        if hit is None:
            dropped.append(mark + tok + mark)
            continue
        s, e = hit.start(), hit.end()
        result = result[:s] + mark + probe + mark + result[e:]
        wrapped.append((s, e + 2 * len(mark)))
    return result, dropped


def git_head(path):
    r = subprocess.run(['git', '-C', ROOT, 'show', 'HEAD:' + path],
                       capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    report = sys.argv[1]
    write = '--write' in sys.argv[2:]
    title = re.match(r'(第.+?章|序言)', os.path.basename(report)).group(1)

    html = open(os.path.join(ROOT, report), encoding='utf-8').read()
    md_path = re.search(r'blob/[^/]+/([^"\'<]+)"', html).group(1)  # 首个 GitHub 原文链接
    md = open(os.path.join(ROOT, md_path), encoding='utf-8').read()
    head = git_head(md_path)
    if head is not None and md != head:
        raise SystemExit('%s 与 git HEAD 不一致（基线漂移），中止。可 git checkout 恢复后重试。'
                         % md_path)
    nmd, idx = normalize(md)

    finals = json.load(open(os.path.join(ROOT, '0917', 'finals', title + '.json'),
                            encoding='utf-8'))['items']

    spans = []
    for rid in sorted(finals):
        it = finals[rid]
        old, fin = it.get('old', ''), it.get('final', '')
        for a, b in NORMALIZE.get(title, {}):
            fin = fin.replace(a, b)
        if title in NORMALIZE:
            assert not re.search('[“”]', fin), rid + ': 弯引号未清干净'
        struct_n = 0
        for phrase in STRUCT.get(title, {}).get(rid, []):
            deco = '**' + phrase + '**'
            if deco not in fin and phrase in fin:
                fin = fin.replace(phrase, deco, 1)
                struct_n += 1
        nold, _ = normalize(old)
        hits = [m.start() for m in re.finditer(re.escape(nold), nmd)]
        if len(hits) != 1:
            print('%-7s ✗ 命中 %d 次（需人工消歧）old[:40]=%r' % (rid, len(hits), old[:40]))
            continue
        h = hits[0]
        r0, r1 = idx[h], idx[h + len(nold) - 1] + 1
        while r0 > 0 and md[r0 - 1] in MARKER:    # 外扩吃进贴边记号，防拆对
            r0 -= 1
        while r1 < len(md) and md[r1] in MARKER:
            r1 += 1
        raw = md[r0:r1]
        if raw.count('`') % 2 or raw.count('*') % 2:
            print('%-7s ✗ 区间内 ` 或 * 记号不成对，转人工' % rid)
            continue
        if fin == '' and it.get('suggested', '') != '':
            print('%-7s ✗ 定稿为空但建议稿非空（疑似误清空）' % rid)
            continue
        new_seg, dropped = transplant(raw, fin)
        assert normalize(new_seg)[0] == normalize(fin)[0], rid + ': 移植自洽断言失败'
        spans.append((r0, r1, rid, raw, new_seg, fin == old, dropped, struct_n))

    # 重叠检查（首尾相接允许）
    ordered = sorted(spans)
    for a, b in zip(ordered, ordered[1:]):
        if a[1] > b[0]:
            raise SystemExit('区间重叠: %s(%d,%d) vs %s(%d,%d)'
                             % (a[2], a[0], a[1], b[2], b[0], b[1]))

    n_code_md = len(re.findall(r'`[^`\n]+`', md))
    n_bold_md = len(re.findall(r'\*\*[^*\n]+\*\*', md))
    print('\n%s：定位成功 %d / %d 条（目标 md：%s，git HEAD 基线 ✓）'
          % (title, len(spans), len(finals), md_path))
    for r0, r1, rid, raw, new_seg, same, dropped, struct_n in ordered:
        cn = len(re.findall(r'`[^`\n]+`', raw))
        bn = len(re.findall(r'\*\*[^*\n]+\*\*', raw))
        cm = len(re.findall(r'`[^`\n]+`', new_seg))
        bm = len(re.findall(r'\*\*[^*\n]+\*\*', new_seg))
        drop = (' 删除记号=' + ','.join(dropped)) if dropped else ''
        st = (' 结构加粗+%d' % struct_n) if struct_n else ''
        print('  %-7s [%5d,%5d) %4d→%4d字 代码%d→%d 加粗%d→%d%s %s%s  %s…'
              % (rid, r0, r1, len(raw), len(new_seg), cn, cm, bn, bm, st,
                 '定稿==原文' if same else '', drop,
                 new_seg[:24].replace('\n', '⏎')))

    out, cursor = [], 0
    for r0, r1, rid, raw, new_seg, same, dropped, struct_n in ordered:
        out.append(md[cursor:r0]); out.append(new_seg); cursor = r1
    out.append(md[cursor:])
    new_md = ''.join(out)
    if new_md.count('`') % 2 or new_md.count('*') % 2:
        raise SystemExit('合成全文 ` 或 * 记号不成对，中止（未写盘）')

    if not write:
        print('\nDRY-RUN（未写盘）。确认后加 --write 执行。')
        return

    open(os.path.join(ROOT, md_path), 'w', encoding='utf-8').write(new_md)
    if open(os.path.join(ROOT, md_path), encoding='utf-8').read() != new_md:
        raise SystemExit('写盘校验失败！git checkout -- %s 恢复' % md_path)
    print('\n已写回 %s（%d → %d 字符；代码 span %d → %d，加粗 %d → %d）并通过重构造复核。'
          % (md_path, len(md), len(new_md), n_code_md,
             len(re.findall(r'`[^`\n]+`', new_md)), n_bold_md,
             len(re.findall(r'\*\*[^*\n]+\*\*', new_md))))


if __name__ == '__main__':
    main()
