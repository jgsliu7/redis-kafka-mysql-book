# -*- coding: utf-8 -*-
"""stats.html 模板（wave2 跨轮对比版）。__DATA__ 为 JSON 占位符。"""

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>wave2 · 50 位画像读者轮 · 共识仪表板（含跨轮对比）</title>
<style>
:root{
  --bg:#f6f7f9; --card:#ffffff; --ink:#1c2330; --sub:#5b6472; --line:#e3e6eb;
  --accent:#2456d6; --accent-soft:#e8eefc; --gold:#b98413; --gold-bg:#fdf6e3; --gold-line:#e6c56a;
  --warn:#b3372f; --warn-bg:#fdf0ee; --ok:#2e7d43; --ok-bg:#eef7f0; --mono:'Consolas','Courier New',monospace;
}
*{box-sizing:border-box; margin:0; padding:0;}
body{background:var(--bg); color:var(--ink); font:14px/1.65 "Microsoft YaHei","PingFang SC",system-ui,sans-serif; padding:20px 18px 60px;}
.wrap{max-width:1180px; margin:0 auto;}
h1{font-size:22px; margin:6px 0 4px;}
h2{font-size:17px; margin:34px 0 12px; padding-bottom:6px; border-bottom:2px solid var(--line);}
h2 .cnt{color:var(--sub); font-weight:normal; font-size:13px; margin-left:8px;}
h2.xh{border-bottom:2px solid #ecc9a0; color:#8c2a1e; font-size:19px;}
.sub{color:var(--sub); font-size:13px; margin-bottom:14px;}
.cards{display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px;}
.card{background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px 16px;}
.card .num{font-size:26px; font-weight:700; color:var(--accent);}
.card.warn .num{color:var(--warn);}
.card.gold .num{color:var(--gold);}
.card.xg .num{color:#a41e22;}
.card.ok .num{color:var(--ok);}
.card .lab{font-size:13px; color:var(--sub); margin-top:2px;}
.grid2{display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-top:12px;}
@media(max-width:900px){.grid2{grid-template-columns:1fr;}}
.panel{background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px 16px;}
.panel h3{font-size:14px; margin-bottom:10px; color:var(--ink);}
.bar-row{display:flex; align-items:center; gap:8px; margin:4px 0; font-size:13px;}
.bar-row .bl{width:150px; text-align:right; color:var(--sub); flex:none; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;}
.bar-row .tr{flex:1; background:#eef0f4; border-radius:4px; height:16px; position:relative;}
.bar-row .fl{position:absolute; left:0; top:0; bottom:0; background:var(--accent); border-radius:4px; min-width:2px;}
.bar-row .fl.g{background:var(--gold);}
.bar-row .v{width:56px; flex:none; color:var(--sub); font-size:12px;}
/* 跨轮共识区 */
.xcluster{background:var(--card); border:1.5px solid transparent; border-radius:10px; margin:10px 0; overflow:hidden;
  background-image:linear-gradient(var(--card),var(--card)),linear-gradient(120deg,#a41e22,#e0a52c 45%,#a41e22);
  background-origin:border-box; background-clip:padding-box,border-box; box-shadow:0 0 0 3px #fbeee6;}
.xcluster .head{padding:10px 14px; cursor:pointer; display:flex; gap:10px; align-items:flex-start;}
.xcluster .head:hover{background:#fdf9f3;}
.xbadge{flex:none; font-size:13px; font-weight:700; color:#fff; border-radius:14px; padding:1px 10px; margin-top:2px; white-space:nowrap;
  background:linear-gradient(120deg,#a41e22,#c98a12);}
.xcluster .body-h{flex:1; min-width:0;}
.c-title{font-size:14px; font-weight:600;}
.c-loc{font-size:13px; color:var(--accent); font-family:var(--mono); margin:1px 0 3px;}
.c-loc .nloc{color:#9a7c1c;}
.c-sum{font-size:13px; color:var(--ink);}
.c-meta{font-size:12.5px; color:var(--sub); margin-top:3px; display:flex; flex-wrap:wrap; gap:6px; align-items:center;}
.tag{display:inline-block; background:#eef0f4; border-radius:4px; padding:0 7px; font-size:12px; color:var(--sub);}
.tag.gold{background:var(--gold-bg); color:var(--gold); border:1px solid var(--gold-line);}
.tag.xg{background:linear-gradient(120deg,#fdf0ec,#fdf6e3); color:#a4531e; border:1px solid #ecc9a0;}
.tag.new{background:#eef7f0; color:#2e7d43; border:1px solid #bcd9c3;}
.tag.pin{background:#f0eefb; color:#5b46b8; border:1px solid #cfc7ec;}
.c-arrow{flex:none; color:var(--sub); font-size:12px; margin-top:4px;}
.xcluster .detail{display:none; border-top:1px solid #ecc9a0; padding:10px 16px 14px; background:#fdfbf6;}
.xcluster.open .detail{display:block;}
.note{background:var(--gold-bg); border:1px solid var(--gold-line); border-radius:8px; padding:8px 12px; font-size:13px; margin:8px 0; color:#6b5310;}
.op{border-left:3px solid var(--accent-soft); padding:8px 12px; margin:8px 0; background:#fff; border-radius:0 8px 8px 0; border-top:1px solid var(--line); border-right:1px solid var(--line); border-bottom:1px solid var(--line);}
.op.night{border-left-color:#f0dfae; background:#fffdf5;}
.op .who{font-size:13px; font-weight:700; margin-bottom:4px;}
.op .who .pv{color:var(--sub); font-weight:normal;}
.op .quote{font-size:13px; background:#f4f6fa; border-radius:6px; padding:6px 10px; margin:6px 0; color:#333; white-space:pre-wrap; word-break:break-word;}
.op .opinion{font-size:13.5px; white-space:pre-wrap; word-break:break-word; color:var(--ink);}
.op .tp{color:var(--sub); font-size:12px; margin-top:4px;}
/* wave2 簇 */
.cluster{background:var(--card); border:1px solid var(--line); border-radius:10px; margin:10px 0; overflow:hidden;}
.cluster.strong{border:1.5px solid var(--gold-line); box-shadow:0 0 0 3px var(--gold-bg);}
.cluster .head{padding:10px 14px; cursor:pointer; display:flex; gap:10px; align-items:flex-start;}
.cluster .head:hover{background:#fafbfd;}
.badge{flex:none; font-size:13px; font-weight:700; color:#fff; background:var(--accent); border-radius:14px; padding:1px 10px; margin-top:2px; white-space:nowrap;}
.badge.strong{background:var(--gold);}
.cluster .detail{display:none; border-top:1px solid var(--line); padding:10px 16px 14px; background:#fbfcfe;}
.cluster.open .detail{display:block;}
/* 冲突区 */
.conflict-card{background:var(--warn-bg); border:1.5px solid #e2b3ae; border-radius:10px; margin:12px 0; padding:14px 16px;}
.conflict-card h4{font-size:15px; color:var(--warn); margin-bottom:6px;}
.need{display:inline-block; background:var(--warn); color:#fff; font-size:12px; border-radius:4px; padding:1px 8px; margin-left:8px; vertical-align:middle;}
.cols2{display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:10px;}
@media(max-width:820px){.cols2{grid-template-columns:1fr;}}
.side{background:#fff; border:1px solid var(--line); border-radius:8px; padding:10px 12px;}
.side h5{font-size:13px; margin-bottom:6px;}
.side.err h5{color:var(--warn);}
.side.ok h5{color:var(--ok);}
.side .op{margin:6px 0;}
.oppside{background:var(--ok-bg); border:1px solid #bcd9c3; border-radius:8px; padding:8px 12px; font-size:13px; margin:8px 0; color:#274; white-space:pre-wrap; word-break:break-word;}
/* 正面资产 */
.poscard{background:var(--ok-bg); border:1px solid #bcd9c3; border-radius:10px; margin:10px 0; padding:12px 14px;}
.poscard .who{font-weight:700; font-size:13.5px; color:var(--ok); margin-bottom:4px;}
.poscard .loc{font-size:12.5px; color:var(--sub); font-family:var(--mono); margin-bottom:6px;}
.poscard .opinion{font-size:13.5px; white-space:pre-wrap; word-break:break-word;}
/* 单读者 */
details.solo-ch{background:var(--card); border:1px solid var(--line); border-radius:10px; margin:8px 0; padding:0 14px;}
details.solo-ch summary{cursor:pointer; padding:9px 0; font-size:14px; font-weight:600; list-style:none; display:flex; align-items:center; gap:8px;}
details.solo-ch summary::-webkit-details-marker{display:none;}
details.solo-ch summary .n{color:var(--sub); font-weight:normal; font-size:13px;}
/* 筛选 */
.filters{display:flex; flex-wrap:wrap; gap:10px; align-items:center; background:var(--card); border:1px solid var(--line); border-radius:10px; padding:10px 14px; margin:14px 0; position:sticky; top:0; z-index:40; box-shadow:0 2px 8px rgba(20,30,50,.06);}
.filters label{font-size:13px; color:var(--sub);}
.filters select{font:13px inherit; padding:4px 8px; border:1px solid var(--line); border-radius:6px; background:#fff; color:var(--ink);}
.filters .clear{cursor:pointer; color:var(--accent); font-size:13px; border:none; background:none;}
.filters .res{margin-left:auto; font-size:13px; color:var(--sub);}
/* 附录 */
table.appx{border-collapse:collapse; width:100%; background:var(--card); border:1px solid var(--line); border-radius:10px; overflow:hidden; font-size:13px;}
table.appx th, table.appx td{padding:5px 10px; border-bottom:1px solid var(--line); text-align:left;}
table.appx th{background:#f0f2f6; color:var(--sub); font-weight:600;}
table.appx tr:last-child td{border-bottom:none;}
.mono{font-family:var(--mono); font-size:12.5px;}
.foot{color:var(--sub); font-size:12.5px; margin-top:26px; text-align:center;}
/* 画像组表 */
table.gs{border-collapse:collapse; width:100%; background:var(--card); border:1px solid var(--line); border-radius:10px; overflow:hidden; font-size:13px; margin-top:12px;}
table.gs th, table.gs td{padding:7px 10px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top;}
table.gs th{background:#f0f2f6; color:var(--sub); font-weight:600;}
table.gs tr:last-child td{border-bottom:none;}
table.gs .tn{font-weight:600;}
</style>
</head>
<body>
<div class="wrap">
  <h1>《架构观察笔记》wave2 · 50 位画像读者轮 · 共识仪表板</h1>
  <div class="sub">50 位画像读者（7 组画像）× 13 文件通读 = 484 条意见（479 条挑错 + 5 条正面基准）· 聚类口径沿用上轮：同章 + 行号差≤3 + 意见语义相关；10 个人工主题簇经种子核对合并。<b>⭐⭐ 跨轮双重共识区</b>为本页核心：与上轮 night100（104 位矩阵读者，916 条意见）独立命中同一问题的，是全书最强修改信号。点击任意条目展开全部意见原文。</div>

  <div class="cards" id="cards"></div>

  <h2 class="xh">⭐⭐ 跨轮双重共识 <span class="cnt" id="xgCnt"></span></h2>
  <div class="sub">两轮独立命中同一问题（本轮簇 ↔ 夜轮簇：同章 + 行号差≤5 + 意见语义相关；4 组人工 pin 均经逐条核对意见原文）。按两轮总命中人数降序——<b>改稿优先级从这里往下走</b>。夜轮意见为节选（全文见 night100/stats.html）。</div>
  <div id="xgZone"></div>

  <h2>wave2 共识排行 <span class="cnt" id="rankCnt"></span></h2>
  <div class="sub">仅统计本轮内部 ≥2 位读者命中、且未被跨轮区收录的簇，按人数降序。绿标 <span class="tag new">本轮新发现</span> = 夜轮 104 位读者未命中的新问题（两轮读者画像不同，新发现多为“任务型/媒介型读者才会在意”的问题）。</div>
  <div class="filters" id="filters">
    <label>章 <select id="fCh"><option value="">全部</option></select></label>
    <label>类型 <select id="fType"><option value="">全部</option></select></label>
    <label>画像组 <select id="fGrp"><option value="">全部</option></select></label>
    <label>共识 <select id="fLv">
      <option value="">全部</option><option value="2">≥2 读者</option><option value="3">强共识 ≥3</option>
    </select></label>
    <button class="clear" id="fClear">清除筛选</button>
    <span class="res" id="fRes"></span>
  </div>
  <div id="rankList"></div>

  <h2>画像组统计 <span class="cnt">（7 组 · 什么样的读者最该听）</span></h2>
  <div class="grid2">
    <div class="panel"><h3>各组意见条数</h3><div id="grpBars"></div></div>
    <div class="panel"><h3>各组命中共识的条数（进入跨轮区或本轮共识簇）</h3><div id="grpCons"></div></div>
  </div>
  <table class="gs" id="gsTable"></table>

  <h2>正面资产 <span class="cnt" id="posCnt"></span></h2>
  <div class="sub">两轮报告中被明确点名“做对了”的地方——修改时的保护清单，别在按共识改稿时顺手磨掉。</div>
  <div id="posZone"></div>

  <h2>冲突裁决区 <span class="cnt" id="confCnt"></span></h2>
  <div class="sub">同一处有读者判“书稿错”、另有读者核实判“书稿对”——这些不要直接改稿，先裁决口径。</div>
  <div id="conflictZone"></div>

  <h2>单读者意见（按章折叠） <span class="cnt" id="soloCnt"></span></h2>
  <div class="sub">仅本轮 1 位读者命中、夜轮也无交叉印证。价值在补盲，不在共识。</div>
  <div id="soloZone"></div>

  <h2>附录：两轮 154 份报告清单 <span class="cnt" id="appxCnt"></span></h2>
  <table class="appx" id="appx"></table>

  <div class="foot" id="foot"></div>
</div>

<script type="application/json" id="DATA">__DATA__</script>
<script>
var D = JSON.parse(document.getElementById('DATA').textContent);
var ROWS = D.rows, CL = D.clusters, XG = D.xgroups, ST = D.stats, GS = D.groupStats;
var CHL = D.chLabel, GRPS = D.groups;
var READER = {};
ROWS.forEach(function(r){ READER['W' + String(r.wid).padStart(2,'0')] = r.reader; });
function wname(w){ return w + ' ' + (READER[w] || ''); }
function chName(c){ return CHL[c] || c; }
function esc(s){ return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

/* ---------- 顶部卡片 ---------- */
(function(){
  var cards = [
    ['两轮合计', ST.totalReaders, '位读者 · ' + ST.totalRows + ' 条意见', 'xg'],
    ['跨轮双重共识', ST.xgroups, '个问题两轮都命中', 'xg'],
    ['本轮新发现', ST.newFound, '个共识簇 · 夜轮未命中', 'ok'],
    ['wave2 簇总数', ST.clusters, '个（位置 + 主题）', ''],
    ['wave2 共识簇', ST.consensus, '个 · 仅本轮 ≥2 读者', 'gold'],
    ['正面基准', ST.wavePos, '条 · 修改时的保护清单', 'ok'],
  ];
  var extra = [
    ['wave2（本轮）', ST.waveReaders + ' 位读者 · ' + ST.waveRows + ' 条（挑错 ' + ST.waveProb + ' + 正面 ' + ST.wavePos + '）'],
    ['night100（上轮）', ST.nightReaders + ' 位读者 · ' + ST.nightRows + ' 条 · 见 night100/stats.html'],
  ];
  document.getElementById('cards').innerHTML = cards.map(function(c){
    return '<div class="card ' + c[3] + '"><div class="num">' + c[1] + '</div><div class="lab"><b>' + c[0] + '</b> · ' + c[2] + '</div></div>';
  }).join('') + extra.map(function(e){
    return '<div class="card"><div class="lab" style="margin-top:6px"><b>' + e[0] + '</b> · ' + e[1] + '</div></div>';
  }).join('');
})();

/* ---------- 跨轮共识区 ---------- */
function locText(locs){ return locs.map(function(l){ return chName(l.chapter) + ' L' + l.lines.join('/'); }).join(' ＋ '); }
var XGTHEME = {};
CL.forEach(function(c){ if (c.kind === 'theme' && c.xgroup >= 0) XGTHEME[c.id] = c.note; });
function typesOf(rowIds){
  var t = {};
  rowIds.forEach(function(ri){ var k = ROWS[ri].type; t[k] = (t[k]||0)+1; });
  return t;
}
function xgroupHTML(xg, idx){
  var tags = '';
  if (xg.kind === 'theme') tags += '<span class="tag xg">人工主题簇</span>';
  if (xg.pinned) tags += '<span class="tag pin">含人工核对 pin</span>';
  var tkeys = Object.keys(typesOf(xg.wRows));
  tkeys.forEach(function(t){ tags += '<span class="tag">' + esc(t) + '</span>'; });
  var h = '<div class="xcluster" data-xg="' + idx + '">'
    + '<div class="head" onclick="var el=this.parentNode;el.classList.toggle(\'open\');">'
    + '<span class="xbadge">' + xg.total + ' 位 · 两轮</span>'
    + '<div class="body-h"><div class="c-title">' + esc(xg.name) + '</div>'
    + '<div class="c-loc">' + esc(locText(xg.locs)) + (xg.nlocs.length && locText(xg.nlocs) !== locText(xg.locs) ? ' <span class="nloc">｜夜轮: ' + esc(locText(xg.nlocs)) + '</span>' : '') + '</div>'
    + '<div class="c-sum">' + esc(xg.summary) + '</div>'
    + '<div class="c-meta">' + tags
    + '<span>本轮: ' + xg.wReaders.map(function(w){return wname(w);}).join(' · ') + '</span>'
    + '<span>夜轮: ' + xg.nReaders.join(' · ') + '</span></div></div>'
    + '<span class="c-arrow">展开 ▾</span></div>'
    + '<div class="detail">';
  var th = XGTHEME[xg.wcs[0]];
  if (th) h += '<div class="note"><b>主题簇说明：</b>' + esc(th) + '</div>';
  h += '<div style="font-size:12.5px;color:var(--sub);margin:6px 0 2px"><b>本轮（wave2）意见：</b></div>';
  xg.wRows.slice().sort(function(a,b){ return ROWS[a].wid - ROWS[b].wid; }).forEach(function(ri){
    var r = ROWS[ri];
    h += '<div class="op"><div class="who">' + wname('W' + String(r.wid).padStart(2,'0')) + ' <span class="pv">· ' + esc(r.group) + ' · #' + r.num + ' · ' + esc(r.pos) + '</span></div>'
      + '<div class="quote">原文：' + esc(r.quote) + '</div>'
      + '<div class="opinion">' + esc(r.opinion) + '</div>'
      + '<div class="tp">类型：' + esc(r.type) + '</div></div>';
  });
  h += '<div style="font-size:12.5px;color:#9a7c1c;margin:10px 0 2px"><b>夜轮（night100）同题意见（节选）：</b></div>';
  xg.nRows.forEach(function(ri){
    var r = D.nrows[ri];
    if (!r) return;
    h += '<div class="op night"><div class="who">' + r.vid + ' <span class="pv">· ' + esc(r.perspective) + ' · ' + chName(r.chapter) + ' L' + r.line + '</span></div>'
      + (r.quote ? '<div class="quote">原文：' + esc(r.quote) + '</div>' : '')
      + '<div class="opinion">' + esc(r.opinion) + '</div>'
      + '<div class="tp">类型：' + esc(r.type) + '</div></div>';
  });
  h += '</div></div>';
  return h;
}
(function(){
  document.getElementById('xgCnt').textContent = '（' + XG.length + ' 个 · 按两轮总命中数降序）';
  document.getElementById('xgZone').innerHTML = XG.map(function(xg, i){ return xgroupHTML(xg, i); }).join('');
})();

/* ---------- wave2 簇渲染 ---------- */
function clusterHTML(c){
  var strong = c.n >= 3;
  var cls = 'cluster' + (strong ? ' strong' : '');
  var tags = '';
  if (c.kind === 'theme') tags += '<span class="tag xg">人工主题簇</span>';
  if (c.n >= 2) tags += '<span class="tag new">本轮新发现</span>';
  Object.keys(c.types).forEach(function(t){ tags += '<span class="tag">' + esc(t) + '×' + c.types[t] + '</span>'; });
  var h = '<div class="' + cls + '" data-cid="' + c.id + '">'
    + '<div class="head" onclick="var el=this.parentNode;el.classList.toggle(\'open\');">'
    + '<span class="badge ' + (strong ? 'strong' : '') + '">' + c.n + ' 位读者</span>'
    + '<div class="body-h"><div class="c-title">' + esc(c.kind === 'theme' ? c.name : c.quoteShort) + '</div>'
    + '<div class="c-loc">' + esc(locText(c.locs)) + ' · ' + c.rows.length + ' 条意见</div>'
    + '<div class="c-sum">' + esc(c.summary) + '</div>'
    + '<div class="c-meta">' + tags + '<span>' + c.readers.map(function(w){ return wname('W' + String(w).padStart(2,'0')); }).join(' · ') + '</span></div></div>'
    + '<span class="c-arrow">展开 ▾</span></div>'
    + '<div class="detail">';
  if (c.kind === 'theme') h += '<div class="note"><b>主题簇说明：</b>' + esc(c.note) + '</div>';
  c.rows.slice().sort(function(a,b){ return ROWS[a].wid - ROWS[b].wid; }).forEach(function(ri){
    var r = ROWS[ri];
    h += '<div class="op"><div class="who">' + wname('W' + String(r.wid).padStart(2,'0')) + ' <span class="pv">· ' + esc(r.group) + ' · #' + r.num + ' · ' + esc(r.pos) + '</span></div>'
      + '<div class="quote">原文：' + esc(r.quote) + '</div>'
      + '<div class="opinion">' + esc(r.opinion) + '</div>'
      + '<div class="tp">类型：' + esc(r.type) + '</div></div>';
  });
  h += '</div></div>';
  return h;
}

/* ---------- 排行 + 筛选 ---------- */
var F = { ch: '', type: '', grp: '', lv: '' };
function passCluster(c){
  var chHit = !F.ch || c.locs.some(function(l){ return l.chapter === F.ch; });
  var grpHit = !F.grp || c.rows.some(function(ri){ return ROWS[ri].group === F.grp; });
  var tpHit = !F.type || c.rows.some(function(ri){ return (ROWS[ri].type || '').indexOf(F.type) >= 0; });
  var lvHit = F.lv === '3' ? c.n >= 3 : true;
  return chHit && grpHit && tpHit && lvHit;
}
function applyFilters(){
  F.ch = document.getElementById('fCh').value;
  F.type = document.getElementById('fType').value;
  F.grp = document.getElementById('fGrp').value;
  F.lv = document.getElementById('fLv').value;
  renderRank(); renderSolo();
}
function renderRank(){
  var list = CL.filter(function(c){ return c.n >= 2 && c.xgroup < 0 && passCluster(c); });
  list.sort(function(a,b){ return b.n - a.n || b.rows.length - a.rows.length; });
  document.getElementById('rankCnt').textContent = '（' + ST.consensus + ' 个共识簇，当前显示 ' + list.length + ' 个）';
  document.getElementById('rankList').innerHTML = list.map(function(c){ return clusterHTML(c); }).join('') || '<div class="sub">无匹配簇。</div>';
}
function renderSolo(){
  var byCh = {};
  CL.forEach(function(c){
    if (c.n !== 1 || c.xgroup >= 0 || !passCluster(c)) return;
    (byCh[c.locs[0].chapter] = byCh[c.locs[0].chapter] || []).push(c);
  });
  var chs = Object.keys(byCh).sort(function(a,b){ return D.chapters.indexOf(a) - D.chapters.indexOf(b); });
  var total = 0; chs.forEach(function(ch){ total += byCh[ch].length; });
  document.getElementById('soloCnt').textContent = '（当前 ' + total + ' 个单读者簇）';
  document.getElementById('soloZone').innerHTML = chs.map(function(ch){
    return '<details class="solo-ch"><summary>' + esc(chName(ch)) + ' <span class="n">— ' + byCh[ch].length + ' 条单读者意见（点击展开）</span></summary>'
      + byCh[ch].map(function(c){ return clusterHTML(c); }).join('') + '</details>';
  }).join('') || '<div class="sub">无匹配。</div>';
}

/* ---------- 画像组 ---------- */
(function(){
  function bars(el, key, gold){
    var max = Math.max.apply(null, GS.map(function(g){ return g[key]; }));
    document.getElementById(el).innerHTML = GS.map(function(g){
      var w = Math.round(g[key] / max * 100);
      return '<div class="bar-row"><span class="bl" title="' + esc(g.group) + ' ' + g.readers + ' 人">' + esc(g.group) + '(' + g.readers + '人)</span>'
        + '<span class="tr"><span class="fl' + (gold?' g':'') + '" style="width:' + w + '%"></span></span>'
        + '<span class="v">' + g[key] + '</span></div>';
    }).join('');
  }
  bars('grpBars', 'rows', false);
  bars('grpCons', 'consRows', true);
  var h = '<tr><th>画像组</th><th>读者数</th><th>意见数</th><th>人均</th><th>命中共识</th><th>最高产读者</th><th>组内前三</th><th>主要类型分布</th></tr>';
  GS.forEach(function(g){
    var tp = Object.keys(g.types).sort(function(a,b){ return g.types[b] - g.types[a]; }).slice(0,3)
      .map(function(t){ return t + '×' + g.types[t]; }).join(' / ');
    h += '<tr><td class="tn">' + esc(g.group) + '</td><td>' + g.readers + '</td><td>' + g.rows + '</td><td>' + g.perCapita + '</td><td>' + g.consRows + '（' + Math.round(g.consRows/g.rows*100) + '%）</td><td>' + esc(g.topReader) + '（' + g.topReaderN + ' 条）</td><td class="mono">' + g.top3.join(' ') + '</td><td>' + esc(tp) + '</td></tr>';
  });
  document.getElementById('gsTable').innerHTML = h;
})();

/* ---------- 正面资产 ---------- */
(function(){
  var P = D.positives;
  document.getElementById('posCnt').textContent = '（本轮 5 条正面基准 + 两轮文末总评 ' + (P.nightParas.length + P.waveExtra.length) + ' 段）';
  var h = '';
  P.wave.forEach(function(p){
    h += '<div class="poscard"><div class="who">' + wname(p.wid) + ' · ' + esc(p.group) + ' · 正面基准</div>'
      + '<div class="loc">' + esc(chName(p.chapter)) + ' L' + p.line + ' · 类型:' + esc(p.type) + '</div>'
      + '<div class="quote" style="font-size:13px;background:#f4f9f5;border-radius:6px;padding:6px 10px;margin:4px 0 8px;color:#333">原文：' + esc(p.quote) + '</div>'
      + '<div class="opinion">' + esc(p.opinion) + '</div></div>';
  });
  h += '<div class="panel" style="margin-top:12px"><h3>报告文末总评中被点名的“做对了”（非表格条目，修改时同样保护）</h3>';
  P.waveExtra.concat(P.nightParas).forEach(function(p){
    h += '<div class="op" style="border-left-color:#cde8d3"><div class="who" style="color:var(--ok)">' + esc(p.who) + '</div><div class="opinion">' + esc(p.text) + '</div></div>';
  });
  h += '</div>';
  document.getElementById('posZone').innerHTML = h;
})();

/* ---------- 冲突区 ---------- */
(function(){
  document.getElementById('confCnt').textContent = '（裁决级 ' + D.conflicts.length + ' 个）';
  var html = D.conflicts.map(function(cf){
    var h2 = '<div class="conflict-card"><h4>' + esc(cf.title) + '<span class="need">需作者裁决</span></h4>'
      + '<div class="c-loc mono" style="font-size:13px">' + esc(cf.nightName) + '</div>'
      + '<div class="note">' + esc(cf.note) + '</div>'
      + '<div class="cols2"><div class="side err"><h5>✗ 判“书稿错”（夜轮 V059/V064 + 上午轮 R02）</h5>';
    cf.nightErr.forEach(function(r){
      h2 += '<div class="op"><div class="who">' + r.vid + ' <span class="pv">· ' + esc(r.perspective) + ' · ' + chName(r.chapter) + ' L' + r.line + '</span></div>'
        + '<div class="quote">原文：' + esc(r.quote) + '</div>'
        + '<div class="opinion">' + esc(r.opinion) + '</div></div>';
    });
    h2 += '</div><div class="side ok"><h5>✓ 判“书稿对 / 核实无误”（夜轮 V063/V075 + 上午轮 R03）</h5>';
    cf.nightOk.forEach(function(o){ h2 += '<div class="oppside">' + esc(o.excerpt) + '</div>'; });
    h2 += '</div></div>';
    h2 += '<div style="margin-top:10px;font-size:13px"><b style="color:#a4531e">本轮新证据（可观测维度——无论落盘口径如何裁决，这个缺口都独立成立）：</b>' + esc(cf.waveNote) + '</div>';
    cf.waveEvidence.forEach(function(r){
      h2 += '<div class="op" style="border-left-color:#ecc9a0"><div class="who">' + wname(r.wid) + ' <span class="pv">· ' + esc(r.reader) + ' · ' + chName(r.chapter) + ' L' + r.line + '</span></div>'
        + '<div class="quote">原文：' + esc(r.quote) + '</div>'
        + '<div class="opinion">' + esc(r.opinion) + '</div></div>';
    });
    h2 += '</div></div>';
    return h2;
  }).join('');
  document.getElementById('conflictZone').innerHTML = html;
})();

/* ---------- 附录 ---------- */
(function(){
  var h = '<tr><th colspan="4" style="background:#fdf6e3">wave2 · 50 份画像读者报告（本轮）</th></tr><tr><th>报告</th><th>画像组</th><th>读者</th><th>意见数</th></tr>';
  D.files.forEach(function(f){
    h += '<tr><td class="mono">' + esc(f.file) + '</td><td>' + esc(f.group) + '</td><td>' + esc(f.reader) + '</td><td>' + f.count + '</td></tr>';
  });
  h += '<tr><th colspan="4" style="background:#eef2fc">night100 · 104 份矩阵读者报告（上轮）</th></tr><tr><th>报告</th><th>章</th><th>视角</th><th>意见数</th></tr>';
  D.nightFiles.forEach(function(f){
    h += '<tr><td class="mono">' + esc(f.file) + '</td><td>' + esc(f.chapter) + '</td><td>' + esc(f.perspective) + '</td><td>' + f.count + '</td></tr>';
  });
  document.getElementById('appx').innerHTML = h;
  document.getElementById('appxCnt').textContent = '（wave2 ' + D.files.length + ' + night100 ' + D.nightFiles.length + '）';
  document.getElementById('foot').textContent = 'wave2 聚类口径：同章 + 行号差≤3 + 意见语义相关（bigram Jaccard/containment，沿用 night100）；跨轮匹配：同章 + 行号差≤5 + 意见语义相关（纯原文重叠不算——两轮常引同一段原文但报不同问题），4 组人工 pin 与 10 个轮内主题簇均经种子逐条核对。生成于 2026-09-11。';
})();

/* ---------- 筛选器初始化 ---------- */
(function(){
  var sel = document.getElementById('fCh');
  D.chapters.forEach(function(c){ var o = document.createElement('option'); o.value = c; o.textContent = chName(c); sel.appendChild(o); });
  sel = document.getElementById('fType');
  Object.keys(D.typeDist).sort(function(a,b){ return D.typeDist[b] - D.typeDist[a]; }).forEach(function(t){ var o = document.createElement('option'); o.value = t; o.textContent = t; sel.appendChild(o); });
  sel = document.getElementById('fGrp');
  GRPS.forEach(function(g){ var o = document.createElement('option'); o.value = g; o.textContent = g; sel.appendChild(o); });
  ['fCh','fType','fGrp','fLv'].forEach(function(id){ document.getElementById(id).onchange = applyFilters; });
  document.getElementById('fClear').onclick = function(){
    ['fCh','fType','fGrp','fLv'].forEach(function(id){ document.getElementById(id).value = ''; });
    applyFilters();
  };
  renderRank(); renderSolo();
})();
</script>
</body>
</html>
"""
