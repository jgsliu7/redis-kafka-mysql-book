const fs=require('fs'),path=require('path');
const base='/Users/liu/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/';
const {chromium}=require(base+'playwright');
const {createCanvas}=require(base+'@napi-rs/canvas');
const qa=__dirname,root=path.resolve(qa,'../..'),url='file://'+path.join(root,'20260905gpt5.6版本.html');
async function main(){
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',args:['--allow-file-access-from-files']});
 const p=await browser.newPage({viewport:{width:1440,height:1000},deviceScaleFactor:1});const errors=[],network=[];
 p.on('pageerror',e=>errors.push(String(e)));p.on('request',r=>{if(/^https?:/.test(r.url()))network.push(r.url())});
 await p.goto(url);await p.screenshot({path:path.join(qa,'desktop-cover.png')});
 await p.locator('[id="section-5.3.1"]').scrollIntoViewIfNeeded();await p.screenshot({path:path.join(qa,'desktop-revised-context.png')});
 const desktop=await p.evaluate(()=>({units:document.querySelectorAll('section.chapter').length,svg:document.querySelectorAll('figure svg').length,pre:document.querySelectorAll('pre').length,overflow:document.documentElement.scrollWidth>innerWidth,badLinks:[...document.querySelectorAll('a[href^="#"]')].filter(a=>!document.getElementById(a.hash.slice(1))).map(a=>a.hash)}));
 await p.setViewportSize({width:390,height:844});await p.goto(url);await p.locator('#toc-button').click();await p.waitForTimeout(250);await p.screenshot({path:path.join(qa,'mobile-toc.png')});
 await p.locator('#toc a[href="#chapter-7"]').click();await p.locator('[id="section-7.1.3"]').scrollIntoViewIfNeeded();await p.screenshot({path:path.join(qa,'mobile-revised-heading.png')});
 const mobile=await p.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth,tocExpanded:document.getElementById('toc-button').getAttribute('aria-expanded'),hash:location.hash}));
 await p.emulateMedia({media:'print'});await p.pdf({path:path.join(qa,'print-regression.pdf'),printBackground:true,preferCSSPageSize:true});await browser.close();
 const pdfjs=await import(base+'pdfjs-dist/legacy/build/pdf.mjs');const pdf=await pdfjs.getDocument({data:new Uint8Array(fs.readFileSync(path.join(qa,'print-regression.pdf'))),useSystemFonts:true}).promise;
 const outside=[],samples=[];const sampled=new Set();
 for(let n=1;n<=pdf.numPages;n++){
  const page=await pdf.getPage(n),t=await page.getTextContent(),v=page.getViewport({scale:1}),words=t.items.filter(i=>i.str?.trim());
  for(const w of words){const x=w.transform[4],right=x+w.width;if(x<45||right>v.width-45)outside.push({page:n,text:w.str,x,right})}
  const txt=words.map(w=>w.str).join('').replace(/\s/g,'');let tag=n===1?'cover':txt.includes('连接处理使用客户端身份')?'context':txt.includes('故障检测不能仅凭超时确定原因')?'heading':txt.includes('这个事务不包含Kafka')?'transaction':txt.includes('增量保留确保快照之后')?'snapshot':null;
  if(tag&&!sampled.has(tag)){sampled.add(tag);const vp=page.getViewport({scale:1.5}),c=createCanvas(vp.width,vp.height);await page.render({canvasContext:c.getContext('2d'),viewport:vp}).promise;const filename='print-'+tag+'-'+n+'.png';fs.writeFileSync(path.join(qa,filename),c.toBuffer('image/png'));samples.push(filename)}
 }
 const result={desktop,mobile,pageErrors:errors,networkRequests:network,print:{pages:pdf.numPages,outsideHorizontalMargins:outside,samples,renderer:'PDF.js + @napi-rs/canvas'}};fs.writeFileSync(path.join(qa,'render-regression.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
}
main().catch(e=>{console.error(e);process.exit(1)});
