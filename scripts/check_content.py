#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建保真校验器：机器验证"构建产物与源稿逐字一致"。

比对 架构之道.html 与 chapters/ 源稿：
  1. 汉字序列逐单元相等（构建器只做结构转换，不得改动任何文字）
  2. 代码块多重集相等（内容一致，顺序/分组允许不同）
  3. 行内代码多重集相等（`...` 内容逐条比对，堵"行内 code 改字不可见"盲区）
  4. 图编号连续（每章 图 N-M 的 N=章号、M 从 1 递增无跳号；异常致命）
  5. 未被引用的 SVG 源文件检出
输出 qa/content-audit.json；汉字/代码/行内代码失配或图编号异常 exit 1。
已知盲区（设计取舍）：数字/拉丁/标点不在汉字序列；SVG 图内文字不比（图稿另有 svg_audit）；
图注行缺失的图（alt 直接进 figcaption 而源稿侧剥 alt）会误报失配——当前全书图均带图注行。
用法: python3 scripts/check_content.py
"""
import json
import os
import re
import sys
from html import unescape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_html import CHAPTERS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOC = os.path.join(ROOT, '架构之道.html')

HANZI = re.compile(r'[一-鿿]')


def md_hanzi_and_code(md):
    """源稿侧：剥离 fenced code / 行内 code / 图片语法（alt 不进产物），返回 (汉字序列, 代码行多重集, 行内代码多重集）。"""
    code_lines = []
    inline_codes = []
    def stash_fence(m):
        body = m.group(1)
        code_lines.extend(l for l in body.split('\n'))
        return ''
    md = re.sub(r'```[^\n]*\n(.*?)```', stash_fence, md, flags=re.S)
    def stash_inline(m):
        inline_codes.append(m.group(0)[1:-1]); return ''
    md = re.sub(r'`[^`]*`', stash_inline, md)     # 行内代码（内容进多重集比对）
    md = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', md)  # 图片 alt+url（alt 不进产物）
    # 代码行多重集只比非空行（围栏首尾空行在两侧的切分粒度不同）
    return ''.join(HANZI.findall(md)), [l for l in code_lines if l.strip()], inline_codes


def html_hanzi_and_code(section_html):
    """产物侧：剥离 svg / pre / 行内 code / 标签，返回 (汉字序列, 代码行多重集, 行内代码多重集)。figcaption 保留（对应源稿图注行）。"""
    pres = re.findall(r'<pre>.*?</pre>', section_html, re.S)
    code_lines = []
    for p in pres:
        p = re.sub(r'</?pre>', '', p)
        p = re.sub(r'<code[^>]*>|</code>', '', p)
        code_lines.extend(unescape(l) for l in p.split('\n') if l.strip())
    h = re.sub(r'<svg.*?</svg>', '', section_html, flags=re.S)
    h = re.sub(r'<pre>.*?</pre>', '', h, flags=re.S)
    inline_codes = [unescape(x) for x in re.findall(r'<code[^>]*>(.*?)</code>', h, flags=re.S)]
    h = re.sub(r'<code[^>]*>.*?</code>', '', h, flags=re.S)  # 行内 code（与源稿侧剥 `...` 对称）
    h = re.sub(r'<[^>]*>', '', h)
    return ''.join(HANZI.findall(h)), code_lines, inline_codes


def first_diff(a, b):
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i, a[max(0, i - 15):i + 15], b[max(0, i - 15):i + 15]
    if len(a) != len(b):
        i = min(len(a), len(b))
        return i, a[i:i + 30], b[i:i + 30]
    return None


def multiset_diff(xs, ys):
    from collections import Counter
    cx, cy = Counter(xs), Counter(ys)
    only_md = list((cx - cy).elements())
    only_html = list((cy - cx).elements())
    return only_md, only_html


def main():
    doc = open(DOC, encoding='utf-8').read()
    # 按 section 切章
    parts = re.split(r'<section class="chapter" id="ch(\d+)">', doc)
    sections = {}
    for i in range(1, len(parts), 2):
        sections[int(parts[i])] = parts[i + 1].split('</section>')[0]

    audit = {'chapters': {}, 'unreferenced_svgs': [], 'figure_gaps': {}, 'ok': True}
    for idx, (rel, diag) in enumerate(CHAPTERS):
        md = open(os.path.join(ROOT, rel), encoding='utf-8').read()
        sec = sections.get(idx, '')
        md_hz, md_code, md_inline = md_hanzi_and_code(md)
        html_hz, html_code, html_inline = html_hanzi_and_code(sec)

        entry = {'hanzi_md': len(md_hz), 'hanzi_html': len(html_hz)}
        d = first_diff(md_hz, html_hz)
        if d:
            pos, ctx_md, ctx_html = d
            entry['hanzi_mismatch'] = {'at': pos, 'md_context': ctx_md, 'html_context': ctx_html}
            audit['ok'] = False
            print('汉字失配 [%s] 第%d字处: 源稿…%s… 产物…%s…' % (rel, pos, ctx_md, ctx_html))
        om, oh = multiset_diff(md_code, html_code)
        if om or oh:
            entry['code_mismatch'] = {'only_in_md': om[:10], 'only_in_html': oh[:10]}
            audit['ok'] = False
            print('代码失配 [%s]: 仅源稿 %d 行 / 仅产物 %d 行（示例: %r / %r）' % (rel, len(om), len(oh), om[:2], oh[:2]))
        iom, ioh = multiset_diff(md_inline, html_inline)
        if iom or ioh:
            entry['inline_mismatch'] = {'only_in_md': iom[:10], 'only_in_html': ioh[:10]}
            audit['ok'] = False
            print('行内代码失配 [%s]: 仅源稿 %d 条 / 仅产物 %d 条（示例: %r / %r）' % (rel, len(iom), len(ioh), iom[:2], ioh[:2]))

        # 图编号连续性（仅技术章 1..10）：跳号/错章号/同图两嵌皆为致命
        if diag and 1 <= idx <= 10:
            nums = [(int(a), int(b)) for a, b in re.findall(r'!\[图\s*(\d+)\s*[-－–]\s*(\d+)', md)]
            ms = [b for (a, b) in nums]
            bad = [n for (a, n) in nums if a != idx]
            gaps = [n for i, n in enumerate(ms) if n != i + 1]
            if bad or gaps:
                audit['figure_gaps'][rel] = {'wrong_chapter': bad, 'non_sequential': sorted(set(gaps))}
                audit['ok'] = False

        # 未引用 SVG
        if diag and os.path.isdir(os.path.join(ROOT, diag)):
            for fn in sorted(os.listdir(os.path.join(ROOT, diag))):
                if fn.endswith('.svg') and ('diagrams/' + fn) not in md:
                    audit['unreferenced_svgs'].append(diag + '/' + fn)

        audit['chapters'][rel] = entry

    out = os.path.join(ROOT, 'qa', 'content-audit.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(audit, f, ensure_ascii=False, indent=2)

    n_ok = sum(1 for e in audit['chapters'].values() if 'hanzi_mismatch' not in e and 'code_mismatch' not in e)
    print('保真校验: %d/%d 章一致%s' % (n_ok, len(CHAPTERS), '' if audit['ok'] else '（存在失配）'))
    if audit['figure_gaps']:
        print('图编号异常: %s' % json.dumps(audit['figure_gaps'], ensure_ascii=False))
    if audit['unreferenced_svgs']:
        print('未引用 SVG: %s' % '、'.join(audit['unreferenced_svgs']))
    print('→ qa/content-audit.json')
    sys.exit(0 if audit['ok'] else 1)


if __name__ == '__main__':
    main()
