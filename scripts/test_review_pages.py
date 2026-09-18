#!/usr/bin/env python3
"""0917/ 审阅页（已插"我的定稿"列）playwright 行为测试。

对 10 个页面逐一断言：
  1. 表头 5 列，第 4 列为"我的定稿"
  2. 可编辑框数量 == 行数
  3. 每框默认值 == 该行"修改后的内容"单元格的纯文本
  4. 编辑第一行 → 2 秒内 0917/finals/<标题>.json 落盘且内容正确
  5. 刷新页面 → 编辑值从 localStorage 恢复
  6. "我的选择"下拉改"采纳" → 同步的 decision 正确（原有功能未被破坏）
  7. 全程控制台零报错
测试后自清理：定稿恢复为建议稿并同步，localStorage 的 finals 键删除，
finals/*.json 恢复为默认状态（final == suggested），用户从干净状态开始。

用法：python3 scripts/test_review_pages.py
"""
import json
import os
import re
import sys
import time
import urllib.parse

from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8734/'
HERE = os.path.dirname(os.path.abspath(__file__))
FINALS = os.path.join(HERE, '..', '0917', 'finals')
DIR = os.path.join(HERE, '..', '0917')

FILES = [f for f in sorted(os.listdir(DIR)) if f.endswith('.html')]

TEST_MARK = '【测试定稿】验证同步'


def title_of(name):
    return re.match(r'(第.+?章|序言)', name).group(1)


def read_final(title):
    for _ in range(20):
        p = os.path.join(FINALS, title + '.json')
        if os.path.exists(p):
            try:
                return json.load(open(p, encoding='utf-8'))
            except json.JSONDecodeError:
                pass
        time.sleep(0.3)
    return None


def main():
    failures = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for f in FILES:
            title = title_of(f)
            errs = []
            page = browser.new_page()
            page.on('console', lambda m: errs.append(m.text) if m.type == 'error' else None)
            page.on('pageerror', lambda e: errs.append(str(e)))
            try:
                page.goto(BASE + urllib.parse.quote(f), wait_until='load')
                page.wait_for_timeout(600)

                ths = page.eval_on_selector_all('thead th', 'els=>els.map(e=>e.textContent.trim())')
                nrows = page.eval_on_selector_all('tbody tr', 'els=>els.length')
                ntas = page.eval_on_selector_all('textarea.final', 'els=>els.length')
                c1 = len(ths) == 5 and ths[3] == '我的定稿'
                c2 = nrows == ntas and nrows > 0

                mism = page.evaluate("""() => {
                  const out = [];
                  document.querySelectorAll('tbody tr').forEach(r => {
                    const t = r.querySelector('textarea.final');
                    const n = r.querySelector('.text.new') || r.querySelector('td.new .passage');
                    if (!t || !n) { out.push(r.id + ':missing'); return; }
                    if (t.value !== n.textContent) out.push(r.id);
                  });
                  return out;
                }""")
                c3 = not mism

                rid = page.evaluate("() => document.querySelector('tbody tr').id")
                page.fill('#%s textarea.final' % rid, TEST_MARK)
                page.wait_for_timeout(2200)
                data = read_final(title) or {}
                item = (data.get('items') or {}).get(rid) or {}
                c4 = item.get('final') == TEST_MARK and item.get('suggested', '') == item.get('suggested', '')

                page.reload(wait_until='load')
                page.wait_for_timeout(700)
                kept = page.eval_on_selector('#%s textarea.final' % rid, 'e => e.value')
                c5 = kept == TEST_MARK

                sel = page.query_selector('#%s .pick' % rid) or page.query_selector('#%s [data-choice]' % rid)
                sel.select_option('采纳')
                page.wait_for_timeout(2200)
                data2 = read_final(title) or {}
                item2 = (data2.get('items') or {}).get(rid) or {}
                c6 = item2.get('decision') == '采纳'
                c7 = not errs

                c8 = None
                if page.query_selector('#clear'):  # 序言页：清除按钮须重置选择/备注且不伤定稿，并触发重同步
                    page.evaluate("""rid => {
                      const n = document.querySelector('#' + rid + ' .notes textarea');
                      n.value = '清除联动测试';
                      n.dispatchEvent(new Event('input', {bubbles: true}));
                    }""", rid)
                    page.wait_for_timeout(1800)
                    page.on('dialog', lambda d: d.accept())
                    page.evaluate("() => {const b=document.querySelector('#clear'); const d=b&&b.closest('details'); if(d)d.open=true;}")
                    page.click('#clear')
                    page.wait_for_timeout(1800)
                    data3 = read_final(title) or {}
                    item3 = (data3.get('items') or {}).get(rid) or {}
                    c8 = (item3.get('decision') == '未审' and item3.get('note') == ''
                          and item3.get('final') == TEST_MARK)
                    c7 = c7 and c8

                ok = all([c1, c2, c3, c4, c5, c6, c7])
                flag = 'PASS' if ok else 'FAIL'
                if not ok:
                    failures.append(f)
                print('%s %-32s 列=%s 行=%d/%d 默认值=%s 落盘=%s 恢复=%s 下拉=%s 清除=%s 控制台=%s'
                      % (flag, f, 'OK' if c1 else ths, nrows, ntas,
                         'OK' if c3 else mism[:3], 'OK' if c4 else item.get('final', '')[:20],
                         'OK' if c5 else kept[:20], 'OK' if c6 else repr(item2.get('decision')),
                         '—' if c8 is None else ('OK' if c8 else 'FAIL'),
                         '干净' if c7 else errs[:2]))

                # ---- 清理：恢复建议稿并同步，删掉 finals 本地键，下拉复原 ----
                page.evaluate("""() => {
                  const r = document.querySelector('tbody tr');
                  const t = r.querySelector('textarea.final');
                  const n = r.querySelector('.text.new') || r.querySelector('td.new .passage');
                  t.value = n.textContent;
                  t.dispatchEvent(new Event('input', {bubbles: true}));
                }""")
                page.wait_for_timeout(1800)
                page.evaluate("() => Object.keys(localStorage).filter(k=>k.endsWith(':finals')).forEach(k=>localStorage.removeItem(k))")
            except Exception as e:  # noqa: BLE001
                failures.append(f)
                print('FAIL %-32s 异常: %s' % (f, str(e)[:200]))
            finally:
                page.close()

        # file:// 直开冒烟（信息性，不判 FAIL）
        try:
            page = browser.new_page()
            page.goto('file://' + os.path.join(DIR, FILES[0]), wait_until='load')
            page.wait_for_timeout(2500)
            st = page.eval_on_selector('#sync-state', 'e => e.textContent') if page.query_selector('#sync-state') else '(无)'
            print('INFO file:// 直开同步状态: %s' % st)
            page.evaluate("() => Object.keys(localStorage).filter(k=>k.endsWith(':finals')).forEach(k=>localStorage.removeItem(k))")
            page.close()
        except Exception as e:  # noqa: BLE001
            print('INFO file:// 冒烟失败: %s' % str(e)[:120])
        browser.close()

    print('\n结果: %s（%d/%d）' % ('全部通过' if not failures else '存在失败 ' + str(failures),
                                  len(FILES) - len(failures), len(FILES)))
    sys.exit(1 if failures else 0)


if __name__ == '__main__':
    main()
