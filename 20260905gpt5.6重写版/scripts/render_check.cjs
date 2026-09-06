// Run with the bundled Node runtime; Chromium renders local files without a server.
const fs = require('fs'), path = require('path');
const { chromium } = require('/Users/liu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
const sharp = require('/Users/liu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root=path.resolve(__dirname,'..'),qa=path.join(root,'qa');
async function main(){
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--allow-file-access-from-files']});
 const page=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});
 const errors=[],network=[];page.on('pageerror',e=>errors.push(String(e)));page.on('request',r=>{if(/^https?:/.test(r.url()))network.push(r.url())});
 await page.goto('file://'+path.join(root,'20260905gpt5.6版本.html'));await page.screenshot({path:path.join(qa,'book-desktop.png')});
 const book=await page.evaluate(()=>({figures:document.querySelectorAll('figure').length,svg:document.querySelectorAll('figure svg').length,chapters:document.querySelectorAll('section.chapter').length,overflow:document.documentElement.scrollWidth>innerWidth,badLinks:[...document.querySelectorAll('a[href^="#"]')].filter(a=>!document.getElementById(a.hash.slice(1))).map(a=>a.hash)}));
 await page.locator('[id="section-10.3"]').scrollIntoViewIfNeeded();await page.screenshot({path:path.join(qa,'book-content-desktop.png')});
 await page.setViewportSize({width:390,height:844});await page.goto('file://'+path.join(root,'20260905gpt5.6版本.html'));await page.screenshot({path:path.join(qa,'book-mobile.png')});
 await page.locator('#toc-button').click();await page.waitForTimeout(250);await page.screenshot({path:path.join(qa,'book-mobile-toc.png')});
 const mobile=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth,tocOpen:document.getElementById('toc-button').getAttribute('aria-expanded')}));
 await page.locator('#toc a[href="#chapter-10"]').click();const navigation=await page.evaluate(()=>({hash:location.hash,tocOpen:document.getElementById('toc-button').getAttribute('aria-expanded')}));
 await page.emulateMedia({media:'print'});await page.pdf({path:path.join(qa,'print-proof.pdf'),printBackground:true,preferCSSPageSize:true});
 await page.emulateMedia({media:'screen'});
 const svgs=[];for(const dir of fs.readdirSync(path.join(root,'chapters'))){const dp=path.join(root,'chapters',dir,'diagrams');if(fs.existsSync(dp))for(const file of fs.readdirSync(dp).filter(f=>f.endsWith('.svg')))svgs.push(path.join(dp,file))}
 const findings=[];fs.mkdirSync(path.join(qa,'figures'),{recursive:true});
 for(const file of svgs){
  await page.goto('file://'+file);const stats=await page.evaluate(()=>{const s=document.querySelector('svg'),v=s.viewBox.baseVal;return{w:v.width,h:v.height,outside:[...s.querySelectorAll('text')].map(t=>{let b=t.getBBox();return{text:t.textContent,x:b.x,y:b.y,w:b.width,h:b.height}}).filter(b=>b.x<v.x||b.y<v.y||b.x+b.w>v.x+v.width||b.y+b.h>v.y+v.height)}});
  await page.setViewportSize({width:900,height:Math.ceil(stats.h)});await page.screenshot({path:path.join(qa,'figures',path.basename(file,'.svg')+'.png')});if(stats.outside.length)findings.push({file:path.basename(file),outside:stats.outside});
 }
 const pngs=svgs.map(f=>path.basename(f,'.svg')+'.png').sort((a,b)=>a.localeCompare(b,undefined,{numeric:true}));
 for(let i=0;i<pngs.length;i+=9){const list=pngs.slice(i,i+9),composite=[];for(let j=0;j<list.length;j++){const p=await sharp(path.join(qa,'figures',list[j])).resize({width:450,height:300,fit:'contain',background:'#ffffff'}).png().toBuffer();composite.push({input:p,left:(j%3)*450,top:Math.floor(j/3)*300})}await sharp({create:{width:1350,height:Math.ceil(list.length/3)*300,channels:3,background:'#d5d5dc'}}).composite(composite).png().toFile(path.join(qa,'contact-'+(i/9+1)+'.png'))}
 const report={book,mobile,navigation,pageErrors:errors,networkRequests:network,svgFiles:svgs.length,svgTextOutOfCanvas:findings};fs.writeFileSync(path.join(qa,'browser-audit.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));await browser.close();
}
main().catch(e=>{console.error(e);process.exit(1)});
