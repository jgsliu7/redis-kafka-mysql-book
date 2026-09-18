#!/usr/bin/env python3
"""给 0917/ 审阅报告 HTML 插入"我的定稿"可编辑列（第 3、4 列之间）。

三套模板自动识别：
  A 代（序言）   ：.text.new 单元格 + #review-data JSON + .pick 选择
  B 代（4-10 章）：.text.new 单元格 + .pick，无 JSON
  C 代（2、3 章）：td.new/.passage + data-choice

每个文件的动作：
  1. thead 在"修改后的内容"后加 <th>我的定稿</th>
  2. colgroup / col 宽度规则改 5 列
  3. 每行在"修改原因"单元格前插入
     <td class="final-col"><textarea class="final">建议稿纯文本</textarea></td>
     （纯文本 = 新单元格去掉 ins 标记后的定稿文字；序言以 #review-data 的 new 字段为准并断言一致）
  4. 现有脚本 querySelector('textarea') 收窄为 '.notes textarea'（否则会误抓新文本框）
  5. 追加列样式 + 同步脚本：编辑即存 localStorage（独立 key，不动原有键）
     并 POST http://127.0.0.1:8734/sync 落盘 0917/finals/<标题>.json

用法：python3 scripts/patch_review_html.py          # 处理 0917/ 全部 *.html
      python3 scripts/patch_review_html.py <文件>    # 只处理指定文件（可反复跑，幂等保护）
"""
import glob
import html as htmllib
import json
import os
import re
import sys

DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '0917'))
SERVER = 'http://127.0.0.1:8734'

CSS_BLOCK = """
/* ---- 我的定稿列（patch_review_html.py 追加）---- */
.final-col{background:#fbfaf5}
.final-col textarea{display:block;width:100%;min-height:150px;resize:vertical;font:15px/1.95 "Noto Serif CJK SC","Songti SC",SimSun,serif;color:#233047;padding:8px 10px;background:#fffefa;border:1px solid #c8d2df;border-radius:4px;tab-size:2}
.final-col textarea:focus{outline:2px solid #5b83b3;outline-offset:1px}
.sync-state{font-size:12px;color:#697789;margin-left:10px}
@media print{.final-col{background:white}.final-col textarea{min-height:0;border:1px solid #aaa;font-size:9pt;line-height:1.65;overflow:hidden}}
"""

SYNC_JS = """
<script>
/* 我的定稿：编辑即存 localStorage 并同步到本地服务（127.0.0.1:8734），Claude 读 finals/*.json */
(function(){'use strict';
var KEY=__KEY__,TITLE=__TITLE__,SERVER='__SERVER__';
var rows=[].slice.call(document.querySelectorAll('tbody tr'));
function newText(r){var el=r.querySelector('.text.new')||r.querySelector('td.new .passage');return el?el.textContent:''}
function oldText(r){var el=r.querySelector('.text.old')||r.querySelector('td.old .passage');return el?el.textContent:''}
function fin(r){var t=r.querySelector('textarea.final');return t?t.value:''}
function pickOf(r){var p=r.querySelector('.pick')||r.querySelector('[data-choice]');return p?p.value:''}
function noteOf(r){var n=r.querySelector('.notes textarea');return n?n.value:''}
function autosize(t){t.style.height='auto';t.style.height=Math.min(t.scrollHeight+4,2400)+'px'}
var finals={};try{finals=JSON.parse(localStorage.getItem(KEY)||'{}')||{}}catch(e){}
rows.forEach(function(r){
  var t=r.querySelector('textarea.final');if(!t)return;
  if(Object.prototype.hasOwnProperty.call(finals,r.id)&&typeof finals[r.id]==='string'&&finals[r.id]!==t.defaultValue)t.value=finals[r.id];
  autosize(t);
  t.addEventListener('input',function(){autosize(t);finals[r.id]=t.value;persist()});
  var p=r.querySelector('.pick')||r.querySelector('[data-choice]');if(p)p.addEventListener('change',persist);
  var n=r.querySelector('.notes textarea');if(n)n.addEventListener('input',persist);
});
function snapshot(){var items={};rows.forEach(function(r){items[r.id]={final:fin(r),suggested:newText(r),old:oldText(r),decision:pickOf(r),note:noteOf(r),level:r.dataset.level||'',section:r.dataset.section||'',search:r.dataset.search||'',link:((r.querySelector('a.filelink')||r.querySelector('a.source')||{}).href||'')}});return items}
var timer=null,lastBody='';
function persist(){try{localStorage.setItem(KEY,JSON.stringify(finals))}catch(e){}clearTimeout(timer);timer=setTimeout(post,700)}
function post(keepalive){
  var body=JSON.stringify({title:TITLE,key:KEY,page:location.pathname,exported_at:new Date().toISOString(),items:snapshot()});
  if(body===lastBody)return;
  var opt={method:'POST',body:body};
  if(keepalive&&body.length<60000)opt.keepalive=true;
  fetch(SERVER+'/sync',opt).then(function(){lastBody=body;status('定稿已同步 '+new Date().toTimeString().slice(0,8))}).catch(function(){status('未连接同步服务，编辑仍保存在本页')});
}
function status(s){var el=document.getElementById('sync-state');if(el)el.textContent=s}
var clr=document.querySelector('#clear');if(clr)clr.addEventListener('click',function(){setTimeout(post,250)});
(function(){var s=document.createElement('span');s.id='sync-state';s.className='sync-state';s.textContent='同步服务待连接…';var tb=document.querySelector('.toolbar')||document.querySelector('.controls');if(tb)tb.appendChild(s);else document.body.insertBefore(s,document.body.firstChild)})();
setTimeout(function(){post()},1500);
window.addEventListener('pagehide',function(){post(true)});
document.addEventListener('visibilitychange',function(){if(document.visibilityState==='hidden')post(true)});
})();
</script>
"""


def cell_text(inner: str) -> str:
    """单元格 HTML → 纯文本（去 del 段、去标记、还原实体、br 转换行）。"""
    s = re.sub(r'<del\b[^>]*>.*?</del>', '', inner, flags=re.S)
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    return htmllib.unescape(s)


def esc(s: str) -> str:
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def title_of(name: str) -> str:
    m = re.match(r'(第.+?章|序言)', name)
    if not m:
        raise SystemExit('无法从文件名推断标题: ' + name)
    return m.group(1)


def patch(path: str) -> None:
    name = os.path.basename(path)
    src = open(path, encoding='utf-8').read()
    if '我的定稿' in src:
        print('%-32s SKIP（已打过补丁）' % name)
        return

    gen = ('A' if 'id="review-data"' in src else 'C' if '<td class="reason">' in src else 'B')
    n_rows = len(re.findall(r'<tr id=[^>]*>', src))

    # ---- 1. thead ----
    for th in ('<th>修改后的内容</th>', '<th scope="col">修改后的内容</th>'):
        if src.count(th) == 1:
            src = src.replace(th, th + th.replace('修改后的内容', '我的定稿'))
            break
    else:
        raise SystemExit(name + ': 找不到表头锚点')

    # ---- 2. 列宽 ----
    if gen == 'C':
        if 'col class="pos"' in src:  # ch2
            old = '<colgroup><col class="pos"><col class="text"><col class="text"><col class="comment"></colgroup>'
            new = '<colgroup><col class="pos"><col class="text"><col class="text"><col class="finalw"><col class="comment"></colgroup>'
            assert src.count(old) == 1
            src = src.replace(old, new)
            for a, b in (('col.pos{width:13%}', 'col.pos{width:10%}'),
                         ('col.text{width:29%}', 'col.text{width:21%}'),
                         ('col.comment{width:29%}', 'col.comment{width:22%}')):
                assert src.count(a) == 1, name + ': ' + a
                src = src.replace(a, b)
            src = src.replace('col.comment{width:22%}', 'col.finalw{width:24%}col.comment{width:22%}')
            src = src.replace('min-width:920px', 'min-width:1300px')
        else:  # ch3
            old = re.search(r'<colgroup>.*?</colgroup>', src, re.S).group(0)
            new = '<colgroup><col style="width:10%"><col style="width:21%"><col style="width:23%"><col style="width:24%"><col style="width:22%"></colgroup>'
            src = src.replace(old, new)
            src = src.replace('min-width:1050px', 'min-width:1400px')
    else:
        old = '<colgroup><col><col><col><col></colgroup>'
        assert src.count(old) == 1, name + ': colgroup'
        src = src.replace(old, '<colgroup><col><col><col><col><col></colgroup>')
        # 选择器可能是 "col:nth-child(2),col:nth-child(3){...}" 这类逗号组合，逐条识别；
        # 必须以 col:nth-child 开头（裸逗号开头会误匹配 JS 里的对象字面量），且各条连续
        rules = list(re.finditer(r'col:nth-child\([^)]*\)(?:,col:nth-child\([^)]*\))*\{[^}]*\}', src))
        if not (3 <= len(rules) <= 4):
            raise SystemExit(name + ': col 规则数异常 %d' % len(rules))
        if any(b.start() != a.end() for a, b in zip(rules, rules[1:])):
            raise SystemExit(name + ': col 规则不连续，拒绝替换')
        newblock = ('col:nth-child(1){width:10%}col:nth-child(2){width:21%}'
                    'col:nth-child(3){width:23%}col:nth-child(4){width:24%}col:nth-child(5){width:22%}')
        src = src[:rules[0].start()] + newblock + src[rules[-1].end():]
        src = src.replace('min-width:1050px', 'min-width:1400px')

    # ---- 3. 每行插入可编辑格 ----
    anchor = '<td><div class="comment">' if gen != 'C' else '<td class="reason">'
    newcell = (r'(<td[^>]*>)<div class="text new">(.*?)</div>\s*</td>' if gen != 'C'
               else r'(<td class="new">)\s*<div class="passage">(.*?)</div>\s*</td>')
    row_re = re.compile(r'<tr id="([^"]+)"[^>]*>.*?</tr>', re.S)
    rows = list(row_re.finditer(src))
    if len(rows) != n_rows:
        raise SystemExit(name + ': 行数对不上 %d/%d' % (len(rows), n_rows))
    ground_truth = None
    if gen == 'A':
        gt = re.search(r'id="review-data"[^>]*>(.*?)</script>', src, re.S).group(1)
        ground_truth = {d['id']: d['new'] for d in json.loads(gt)}
    out, last, done = [], 0, 0
    for m in rows:
        row = m.group(0)
        nm = re.search(newcell, row, re.S)
        if not nm or row.count(anchor) != 1:
            raise SystemExit('%s: 行 %s 锚点异常' % (name, m.group(1)))
        text = cell_text(nm.group(2))
        if ground_truth is not None and ground_truth.get(m.group(1)) != text:
            raise SystemExit('%s: 行 %s 纯文本与 review-data 不一致\n提取=%r\n数据=%r'
                             % (name, m.group(1), text[:80], ground_truth.get(m.group(1), '')[:80]))
        ta = esc(text)
        if ta.startswith('\n'):
            ta = '\n' + ta  # HTML 规范会吞掉紧跟开标签的首个换行
        td = ('<td class="final-col"><textarea class="final" rows="8" '
              'title="默认为建议稿，可直接编辑；改动会自动保存并同步">%s</textarea></td>') % ta
        out.append(src[last:m.start()])
        out.append(row.replace(anchor, td + anchor, 1))
        last = m.end()
        done += 1
    src = ''.join(out) + src[last:]

    # ---- 4. 修 textarea 选择器冲突（A/B 代现有脚本）----
    fixed = src.count("querySelector('textarea')")
    src = src.replace("querySelector('textarea')", "querySelector('.notes textarea')")

    # ---- 5. CSS + 同步脚本 ----
    pos = src.rfind('</style>')
    src = src[:pos] + CSS_BLOCK + '</style>' + src[pos + len('</style>'):]
    key = re.search(r'data-store="([^"]+)"', src)
    key = key.group(1) + ':finals' if key else \
        re.search(r"const key='([^']+)'", src).group(1) + ':finals'
    js = SYNC_JS.replace('__KEY__', json.dumps(key, ensure_ascii=False)) \
                .replace('__TITLE__', json.dumps(title_of(name), ensure_ascii=False)) \
                .replace('__SERVER__', SERVER)
    src = src.replace('</body>', js + '</body>', 1)

    open(path, 'w', encoding='utf-8').write(src)
    print('%-32s OK  代=%s 行=%d 插入=%d 选择器修复=%d' % (name, gen, n_rows, done, fixed))


if __name__ == '__main__':
    targets = sys.argv[1:] or sorted(glob.glob(os.path.join(DIR, '*.html')))
    for t in targets:
        patch(t)
