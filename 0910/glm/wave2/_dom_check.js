// 轻量 DOM mock：运行 stats.html 的主脚本，验证渲染逻辑无运行时错误
const fs = require('fs');
const html = fs.readFileSync('stats.html', 'utf-8');
const m1 = html.match(/<script type="application\/json" id="DATA">([\s\S]*?)<\/script>/);
const dataStr = m1[1].split('<\\/').join('</');
const mainJs = html.match(/<script>([\s\S]*?)<\/script>/)[1];

const zones = {};
function makeEl(id) {
  return {
    _id: id, innerHTML: '', textContent: '',
    value: '', onchange: null, onclick: null,
    appendChild: function(){}, classList: { toggle(){}, add(){}, remove(){}, contains(){ return false; } },
    getAttribute(){ return null; }, setAttribute(){},
    scrollIntoView(){}, click(){},
  };
}
global.document = {
  getElementById: function(id){
    if (id === 'DATA') { const el = makeEl('DATA'); el.textContent = dataStr; return el; }
    if(!zones[id]) zones[id] = makeEl(id); return zones[id];
  },
  createElement: function(){ return makeEl('opt'); },
  querySelectorAll: function(){ return []; },
};
try {
  const fn = new Function('document', 'window', mainJs);
  fn(global.document, global);
} catch (e) {
  console.error('RUNTIME ERROR:', e.message);
  console.error(e.stack.split('\n').slice(0,4).join('\n'));
  process.exit(1);
}
const D = JSON.parse(dataStr);
console.log('DATA parse OK: rows=%d clusters=%d xgroups=%d nrows=%d', D.rows.length, D.clusters.length, D.xgroups.length, Object.keys(D.nrows).length);
const mustHave = ['cards','xgZone','rankList','soloZone','posZone','conflictZone','gsTable','appx','foot'];
let fail = 0;
mustHave.forEach(function(z){
  const el = zones[z];
  const ok = el && (el.innerHTML.length > 50 || el.textContent.length > 10);
  if (!ok) { console.error('ZONE EMPTY/MISSING:', z); fail = 1; }
  else console.log('zone ' + z.padEnd(12) + ' ' + Math.max(el.innerHTML.length, el.textContent.length) + ' chars OK');
});
const xg = zones.xgZone.innerHTML;
console.log('xgroup cards rendered:', (xg.match(/class="xcluster"/g)||[]).length);
console.log('top badge check:', xg.indexOf('14 位 · 两轮') >= 0 ? 'FOUND "14 位 · 两轮"' : 'NOT FOUND 14');
console.log('night opinions in xg:', (xg.match(/class="op night"/g)||[]).length);
console.log('wave2 opinions total:', ((zones.xgZone.innerHTML + zones.rankList.innerHTML + zones.soloZone.innerHTML).match(/class="opinion"/g)||[]).length);
console.log('positive cards:', (zones.posZone.innerHTML.match(/class="poscard"/g)||[]).length);
console.log('conflict cards:', (zones.conflictZone.innerHTML.match(/class="conflict-card"/g)||[]).length);
console.log('appendix rows:', (zones.appx.innerHTML.match(/<tr>/g)||[]).length);
// 意见总数守恒检查（页面渲染的 wave2 意见块 = 479 问题行 + 5 正面不在此计）
console.log('expect opinions ~= 479 (xgroups+rank+solo unique)');
process.exit(fail);
