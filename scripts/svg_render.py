#!/usr/bin/env python3
"""
SVG → PNG 渲染工具（用 playwright + chromium 把 SVG 渲成可视觉检查的 PNG）。
用途:本环境虽然"不能直接看 SVG"，但能把 SVG 渲成 PNG 再用 Read 工具**真看图**，
这是 SVG 插图 QA 的"视觉验证"环节，与 svg_audit.py 的几何审计互为交叉验证。

用法:
    python3 scripts/svg_render.py chapters/04-memory-disk/diagrams/fig-4-4.svg
    python3 scripts/svg_render.py fig-5-7                  # 任意子串匹配全书
    python3 scripts/svg_render.py fig-5-7 --crop 80,135,40,80   # 按 SVG 坐标裁剪放大
    python3 scripts/svg_render.py                            # 渲染全部 52 张到 /tmp/svgpng/

输出固定尺寸:像素 = SVG 单位 × scale(默认 2)，便于按坐标精确裁剪。
依赖:playwright + chromium(pip install playwright; playwright install chromium)。
"""
import sys, re, pathlib, glob, os
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUTDIR = pathlib.Path('/tmp/svgpng')

scale = 2.0
args = []; crops = []
i = 1
while i < len(sys.argv):
    a = sys.argv[i]
    if a == '--scale': scale = float(sys.argv[i+1]); i += 2
    elif a == '--crop': crops.append([float(x) for x in sys.argv[i+1].split(',')]); i += 2
    elif a.startswith('--'): i += 2
    else: args.append(a); i += 1

# 无参 → 全部 SVG
if not args:
    args = sorted(glob.glob(str(ROOT / 'chapters' / '**' / 'diagrams' / '*.svg'), recursive=True))

def vb_of(path):
    t = pathlib.Path(path).read_text(encoding='utf-8')
    m = re.search(r'viewBox="([\d.\s-]+)"', t)
    p = list(map(float, m.group(1).split()))
    return p[2], p[3]

def resolve(a):
    a = a.strip()
    if os.path.isfile(a): return a
    hit = glob.glob(str(ROOT / 'chapters' / '**' / 'diagrams' / f'*{a}*.svg'), recursive=True)
    if hit: return hit[0]
    raise SystemExit(f'找不到匹配 {a} 的 SVG')

OUTDIR.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch()
    for a in args:
        svgp = pathlib.Path(resolve(a)).resolve()
        W, H = vb_of(svgp)
        page = browser.new_page(viewport={'width': int(W)+4, 'height': int(H)+4}, device_scale_factor=scale)
        page.goto('file://' + str(svgp))
        page.evaluate('([W,H]) => { let s=document.querySelector("svg"); s.setAttribute("width",W); s.setAttribute("height",H); }', [W, H])
        page.wait_for_timeout(180)
        if crops:
            for ci, c in enumerate(crops):
                x, y, w, h = c
                page.screenshot(path=str(OUTDIR / f'{svgp.stem}__crop{ci}.png'),
                                clip={'x': x, 'y': y, 'width': w, 'height': h})
        else:
            page.screenshot(path=str(OUTDIR / f'{svgp.stem}.png'),
                            clip={'x': 0, 'y': 0, 'width': W, 'height': H})
        print(f'rendered {svgp.name} ({W:.0f}x{H:.0f})')
    browser.close()
print(f'输出目录: {OUTDIR}')
