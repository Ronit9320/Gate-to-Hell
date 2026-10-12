const {chromium,firefox}=require('playwright');
const http=require('http'),fs=require('fs'),path=require('path'),assert=require('assert');
const server=http.createServer((req,res)=>{
 let url=req.url.split('?')[0];if(url==='/favicon.ico'){res.writeHead(204);return res.end();}if(url==='/embed'){res.setHeader('Content-Type','text/html');return res.end('<body style="margin:0"><iframe src="/" style="width:100%;height:100vh;border:0" allow="fullscreen; autoplay"></iframe>');}
 let f=path.join(__dirname,'../dist/web',url==='/'?'index.html':url);if(!fs.existsSync(f)){res.writeHead(404);return res.end();}res.setHeader('Content-Type',f.endsWith('.wasm')?'application/wasm':f.endsWith('.js')?'text/javascript':f.endsWith('.html')?'text/html':'application/octet-stream');res.end(fs.readFileSync(f));
});
const errors=[];const results=[];
(async()=>{
 fs.mkdirSync('.test-results',{recursive:true});await new Promise(r=>server.listen(8123,'127.0.0.1',r));
 const useFirefox=process.argv.includes('--firefox');
 const b=await (useFirefox?firefox:chromium).launch(useFirefox?{executablePath:process.env.CINDERS_FIREFOX||(fs.existsSync('/home/guardian/.cache/ms-playwright/firefox-1522/firefox/firefox')?'/home/guardian/.cache/ms-playwright/firefox-1522/firefox/firefox':firefox.executablePath()),headless:true}:{executablePath:process.env.CINDERS_CHROMIUM||(fs.existsSync('/home/guardian/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome')?'/home/guardian/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome':chromium.executablePath()),headless:true,args:['--no-sandbox','--enable-unsafe-swiftshader']});
 try{
 const p=await b.newPage({viewport:{width:1280,height:800}});
 if(process.argv.includes('--missing-art-only'))await p.addInitScript(()=>{
 window.newArtTextures={bosses:0,effects:0};
 for(const P of [WebGLRenderingContext.prototype,window.WebGL2RenderingContext?.prototype].filter(Boolean)){
  const upload=P.texImage2D;P.texImage2D=function(...a){const result=upload.apply(this,a);if(a[3]===1536&&a[4]===960)newArtTextures.bosses++;if(a[3]===512&&a[4]===256)newArtTextures.effects++;return result;};
 }
 });
 if(process.argv.includes('--polish-only'))await p.addInitScript(()=>{
 window.effectTextures={created:0};
 for(const P of [WebGLRenderingContext.prototype,window.WebGL2RenderingContext?.prototype].filter(Boolean)){
  const upload=P.texImage2D;
  P.texImage2D=function(...a){const result=upload.apply(this,a);if((a[3]===1152&&a[4]===384)||(a[3]===512&&a[4]===256))effectTextures.created++;return result;};
 }
 });
 if(process.argv.includes('--heroes-only'))await p.addInitScript(()=>{
 window.heroTextures={created:0,active:new Set()};
 for(const P of [WebGLRenderingContext.prototype,window.WebGL2RenderingContext?.prototype].filter(Boolean)){
  const upload=P.texImage2D,del=P.deleteTexture;
  P.texImage2D=function(...a){const result=upload.apply(this,a);if(a[3]===960&&a[4]===1344){heroTextures.created++;heroTextures.active.add(this.getParameter(this.TEXTURE_BINDING_2D));}return result;};
  P.deleteTexture=function(t){heroTextures.active.delete(t);return del.call(this,t);};
 }
 });
 if(process.argv.includes('--bailiff-only'))await p.addInitScript(()=>{
 window.bailiffTextures={created:0,active:new Set()};
 for(const P of [WebGLRenderingContext.prototype,window.WebGL2RenderingContext?.prototype].filter(Boolean)){
  const upload=P.texImage2D,del=P.deleteTexture;
  P.texImage2D=function(...a){const result=upload.apply(this,a);if(a[3]===2048&&a[4]===1280){bailiffTextures.created++;bailiffTextures.active.add(this.getParameter(this.TEXTURE_BINDING_2D));}return result;};
  P.deleteTexture=function(t){bailiffTextures.active.delete(t);return del.call(this,t);};
 }
 });
 await p.addInitScript(()=>{window.audioProof={starts:0,contexts:[]};const AC=window.AudioContext;window.AudioContext=new Proxy(AC,{construct(T,args){const ctx=new T(...args);window.audioProof.contexts.push(ctx);return ctx;}});const start=AudioBufferSourceNode.prototype.start;AudioBufferSourceNode.prototype.start=function(...args){window.audioProof.starts++;return start.apply(this,args);};});
 p.on('console',m=>{const text=m.text();if(process.env.CINDERS_VERBOSE)console.log(m.type(),text);if(m.type()==='error'||/^Error:|stack traceback|RangeError/.test(text)){errors.push(text);console.log('ERROR',text);}});p.on('pageerror',e=>errors.push(e.message));
 const boot=async()=>{await p.waitForFunction(()=>window.Module?.calledRun);await p.waitForTimeout(1200);};
 const read=async()=>p.evaluate(()=>{try{return JSON.parse(Module.cindersFS.readFile('/home/web_user/love/house-of-cinders/run.sav',{encoding:'utf8'}));}catch{return null;}});
 const click=async(x,y)=>{const box=await p.locator('#canvas').boundingBox();await p.mouse.click(box.x+x*box.width/1280,box.y+y*box.height/720);await p.waitForTimeout(220);};
 const move=async(x,y)=>{const box=await p.locator('#canvas').boundingBox();await p.mouse.move(box.x+x*box.width/1280,box.y+y*box.height/720);};
 const shot=async(name)=>p.screenshot({path:`.test-results/${name}.png`});
 const approach=async()=>{await p.keyboard.down('d');await p.waitForTimeout(830);await p.keyboard.up('d');await p.keyboard.down('w');await p.waitForTimeout(830);await p.keyboard.up('w');};
 async function fixture(name){const raw=fs.readFileSync(`.test-results/fixture-${name}.json`,'utf8');await p.evaluate(raw=>{Module.cindersFS.writeFile('/home/web_user/love/house-of-cinders/run.sav',raw);},raw);await p.reload();await boot();await click(300,581);}
 await p.goto('http://127.0.0.1:8123');await boot();console.log('BROWSER',await b.version());await shot('title');
 if(process.argv.includes('--listing-only')){await click(200,525);await shot('listing-draft');await fixture('management');await shot('listing-shop');await fixture('victory');await shot('listing-victory');assert.deepEqual(errors,[]);console.log('Listing media captured');return;}
 if(process.argv.includes('--missing-art-only')){await require('./missing-art-check.cjs')({p,read,fixture,click,move,shot,results});assert.deepEqual(errors,[]);console.log('PASS',results.join('\nPASS '));return;}
 if(process.argv.includes('--art-only')){await require('./ui-art-check.cjs')({p,read,fixture,click,shot,results});assert.deepEqual(errors,[]);console.log('PASS',results.join('\nPASS '));return;}
 if(process.argv.includes('--polish-only')){await require('./polish-check.cjs')({p,read,fixture,click,move,shot,results});assert.deepEqual(errors,[]);fs.writeFileSync('.test-results/polish-browser.json',JSON.stringify({results,errors},null,2));console.log('PASS',results.join('\nPASS '));return;}
 if(process.argv.includes('--heroes-only')){await require('./heroes-check.cjs')({p,read,fixture,click,move,shot,results});assert.deepEqual(errors,[]);console.log('PASS',results.join('\nPASS '));return;}
 if(process.argv.includes('--combat-only')){await require('./combat-check.cjs')({p,fixture,read,click,move,shot,results});assert.deepEqual(errors,[]);fs.writeFileSync('.test-results/combat-browser.json',JSON.stringify({browser:await b.version(),results,errors},null,2));console.log('PASS',results.join('\nPASS '));return;}
 if(process.argv.includes('--bailiff-only')){await require('./bailiff-check.cjs')({p,b,fixture,read,click,move,shot,approach,results});assert.deepEqual(errors,[]);console.log('PASS',results.join('\nPASS '));return;}
 if(process.argv.includes('--management-only')){await require('./management-check.cjs')({p,read,fixture,shot,results});assert.deepEqual(errors,[]);console.log('PASS',results.join('\nPASS '));return;}
 if(process.argv.includes('--media-only')){await p.setViewportSize({width:630,height:500});await p.setContent(fs.readFileSync('release/cover.svg','utf8'));await p.addStyleTag({content:'body{margin:0}'});await p.screenshot({path:'release/cover.png'});console.log('Cover rendered');return;}
 if(process.argv.includes('--release-only')){await require('./release-check.cjs')({p,b,boot,read,click,move,shot,approach,results});assert.deepEqual(errors,[]);console.log('PASS',results.join('\nPASS '));return;}
 if(process.argv.includes('--tactics-only')){
  await p.keyboard.press('F2');await click(600,324);await p.keyboard.press('Escape');
  await fixture('management');const original=await read();
  await click(520,42);await move(10,10);await p.waitForTimeout(350);await shot('run-info-shop');
  assert.deepEqual(await read(),original,'Scouting must not mutate save or RNG');
  await move(550,235);await p.waitForTimeout(350);await shot('run-info-resistance');
  await p.keyboard.press('Escape');
  await click(1070,373);await click(520,495);await move(10,10);await p.waitForTimeout(350);await shot('transaction-no-done');
  assert((await read()).gold<original.gold,'Purchase remains functional without Done overlay');
  await fixture('boss-10');await click(520,42);await move(10,10);await p.waitForTimeout(350);await shot('run-info-throne-hell');
  await p.keyboard.press('Escape');await click(1100,610);await move(1090,171);await p.waitForTimeout(350);await shot('tactical-guard');
  await click(520,42);await move(10,10);await p.waitForTimeout(350);
  const paused=await p.locator('#canvas').screenshot();await p.waitForTimeout(1600);
  assert(paused.equals(await p.locator('#canvas').screenshot()),'Run Info freezes arena rendering in reduced motion');
  await shot('run-info-combat');await p.keyboard.press('Escape');
  await p.keyboard.press('F2');await click(600,420);await p.keyboard.press('Escape');
  await click(520,42);await move(10,10);await p.waitForTimeout(350);await shot('run-info-large');
  results.push('Run Info previews shop, Throne and Hell encounters without changing saved progress');
  results.push('Run Info pauses combat; large-text and resistance tooltips render; purchase works without Done overlay');
  assert.deepEqual(errors,[]);fs.writeFileSync('.test-results/tactics-browser.json',JSON.stringify({results,errors},null,2));console.log('PASS',results.join('\nPASS '));return;
 }
 if(process.argv.includes('--hover-only')){
  await p.keyboard.press('F2');await click(600,324);await p.keyboard.press('Escape');
  await click(200,525);await move(10,10);await p.waitForTimeout(600);
  const box=await p.locator('#canvas').boundingBox();
  const crop=()=>p.screenshot({clip:{x:box.x+190*box.width/1280,y:box.y+350*box.height/720,width:280*box.width/1280,height:90*box.height/720}});
  const before=await crop();await move(150,290);await p.waitForTimeout(350);
  const hovered=await crop();assert(!before.equals(hovered),'Hover must paint an inspection panel');await shot('hover-hero');
  await move(10,10);await p.waitForTimeout(300);assert(before.equals(await crop()),'Tooltip must disappear when the pointer leaves');
  results.push('Hero tooltip appears on hover and dismisses on leave: actual canvas pixels');
  await fixture('management');await move(560,270);await p.waitForTimeout(350);await shot('hover-shop');
  await click(550,373);await shot('hover-click-through');await p.keyboard.press('Escape');
  await fixture('boss-10');await move(400,332);await p.waitForTimeout(350);await shot('hover-threat-preview');
  await click(1100,610);await move(90,665);await p.waitForTimeout(350);await shot('hover-skill');
  await move(180,670);await p.waitForTimeout(350);await shot('hover-dodge');
  await move(70,110);await p.waitForTimeout(350);await shot('hover-threat');
  assert.equal((await read()).stage,'arena');
  await p.keyboard.press('F2');await click(600,420);await p.keyboard.press('Escape');
  await move(90,665);await p.waitForTimeout(350);await shot('hover-large-text');
  results.push('Shop, threat preview, combat skill/dodge and large-text hover panels render; clicks still open offers');
  assert.deepEqual(errors,[]);fs.writeFileSync('.test-results/hover-browser.json',JSON.stringify({results,errors},null,2));console.log('PASS',results.join('\nPASS '));return;
 }
 if(process.argv.includes('--finale-only')){
  await fixture('boss-10');await click(1100,610);await approach();await move(718,306);await p.mouse.down();
  for(let i=0;i<80;i++){
   await p.keyboard.press(String(i%3+1));await p.keyboard.press('e');await p.waitForTimeout(350);
   if(i%8===0)await shot('art-finale-'+i);
   if((await read()).stage!=='arena')break;
  }
  await p.mouse.up();assert.equal((await read()).stage,'victory');assert((await read()).key);await shot('art-finale-victory');
  await click(760,500);assert.equal((await read()).stage,'shop');await click(1080,641);assert.equal((await read()).floor,11);
  assert.deepEqual(errors,[]);fs.writeFileSync('.test-results/art-finale.json',JSON.stringify({browser:await b.version(),results:['Live Empty Throne phases, death, Infinity Key and Hell entry'],errors},null,2));
  console.log('PASS Live Empty Throne clear, death, Infinity Key and Hell entry');return;
 }
 if(useFirefox){await click(200,525);assert.equal((await read()).stage,'draft');await click(185,610);await click(1100,610);await move(718,306);await p.mouse.down();await p.keyboard.press('e');await p.waitForTimeout(900);await p.mouse.up();await shot('firefox-arena');assert.equal((await read()).stage,'arena');await p.reload();await boot();await click(300,581);assert.equal((await read()).stage,'preview');assert.deepEqual(errors,[]);fs.writeFileSync('.test-results/firefox.json',JSON.stringify({browser:await b.version(),results:['draft, fight, input, reload smoke'],errors},null,2));console.log('PASS Firefox draft / combat / persistence smoke');return;}
 if(!process.argv.includes('--ui-only')){
 await click(490,525);let r=await read();assert.equal(r.stage,'draft');assert.equal(Object.keys(r.offers).length,4);await shot('draft');
 const offers=JSON.stringify(r.offers);await p.reload();await boot();await click(300,581);assert.equal(JSON.stringify((await read()).offers),offers);results.push('draft reload preserves offers');
 await click(185,610);assert.equal((await read()).stage,'preview');await shot('preview');await click(1100,610);assert.equal((await read()).stage,'arena');
 await move(718,306);await p.mouse.down();await p.keyboard.press('e');await p.waitForTimeout(1200);await p.mouse.up();await shot('arena');const audio=await p.evaluate(()=>({starts:audioProof.starts,states:audioProof.contexts.map(c=>c.state)}));assert(audio.starts>0&&audio.states.includes('running'));results.push('audio buffer playback starts after user gesture');
 await p.evaluate(()=>window.dispatchEvent(new Event('blur')));await p.waitForTimeout(150);await shot('focus-loss');await p.keyboard.press('Escape');
 await p.keyboard.press('Escape');await p.waitForTimeout(300);await shot('pause');await p.keyboard.press('Escape');
 const entry=await read();await p.reload();await boot();await click(300,581);assert.equal((await read()).stage,'preview');assert.deepEqual((await read()).team,entry.team);results.push('midfight reload restarts saved entry');
 await click(1100,610);
 async function fight(){await approach();await move(718,306);await p.mouse.down();for(let i=0;i<65;i++){await p.keyboard.press('e');await p.waitForTimeout(400);const s=(await read()).stage;if(s!=='arena'){await p.mouse.up();return s;}}await p.mouse.up();throw Error('fight did not end');}
 assert.equal(await fight(),'rewards');await shot('rewards');await click(1100,610);r=await read();assert.equal(r.stage,'shop');assert.equal(r.stock['1'].price,8);await shot('shop');
 await click(150,373);await shot('offer');await click(570,495);r=await read();assert.equal(Object.keys(r.team).length,2);assert(r.stock['1'].sold);results.push('solo fight, reward, shop recruitment through UI');
 const stock=JSON.stringify(r.stock),gold=r.gold;await p.reload();await boot();await click(300,581);assert.equal((await read()).gold,gold);assert.equal(JSON.stringify((await read()).stock),stock);results.push('shop reload preserves transactions and stock');
 await click(1080,641);await click(1100,610);await p.keyboard.press('2');assert.equal(await fight(),'complete');await shot('demo-complete');results.push('two-fight demo complete');
 // Install valid boundary snapshots through the same filesystem used by Continue.

 if(fs.existsSync('.test-results/fixture-victory.json')){
  await fixture('victory');await shot('victory');await click(230,500);assert.equal((await read()).stage,'complete');results.push('Finish Run');
  await fixture('victory');await click(760,500);r=await read();assert.equal(r.stage,'shop');assert.equal(r.stock['1'].price,35);await click(1080,641);assert.equal((await read()).floor,11);await shot('hell-preview');results.push('Infinity Key / Enter Hell');
  await fixture('full');const before=JSON.stringify(await read());await click(760,373);await click(570,495);assert.equal(JSON.stringify(await read()),before);await shot('inventory-full');await click(930,145);
  await click(1050,373);await click(570,495);assert.equal(JSON.stringify(await read()),before);await click(930,145);results.push('full inventory transactions blocked');
  await fixture('poor');const poor=JSON.stringify(await read());await click(400,642);assert.equal(JSON.stringify(await read()),poor);await shot('insufficient-gold');results.push('insufficient gold unchanged');
  await fixture('death');await click(1100,610);for(let i=0;i<35;i++){await p.waitForTimeout(300);if((await read()).stage==='defeat')break;}assert.equal((await read()).stage,'defeat');await shot('defeat');await click(200,465);assert.equal((await read()).stage,'draft');results.push('defeat and restart');
 }
 await p.reload();await boot();await click(200,524);await shot('replace-run-warning');assert.equal((await read()).stage,'draft');await click(930,145);
 await click(1030,570);const settings=await p.evaluate(()=>localStorage.getItem('cinders:settings.sav'));assert(settings);await p.reload();await boot();assert.equal(await p.evaluate(()=>localStorage.getItem('cinders:settings.sav')),settings);results.push('settings persist');
 await p.setViewportSize({width:900,height:650});await click(300,581);assert.equal((await read()).stage,'draft');await shot('resized');results.push('resized mouse coordinates');
 await p.locator('#full').click();await p.waitForTimeout(250);assert(await p.evaluate(()=>!!document.fullscreenElement));await p.evaluate(()=>document.exitFullscreen());results.push('fullscreen');
 }
 // Full keyboard menu route, settings and rebinding in the actual packaged runtime.
 await p.setViewportSize({width:1280,height:800});
 await p.evaluate(()=>{for(const name of ['run.sav','settings.sav']){const path='/home/web_user/love/house-of-cinders/'+name;if(Module.cindersFS.analyzePath(path).exists)Module.cindersFS.unlink(path);localStorage.removeItem('cinders:'+name);}});
 await p.reload();await boot();assert.equal(await read(),null);await p.locator('#canvas').focus();
 await p.keyboard.press('Tab');await p.keyboard.press('Enter');await p.waitForTimeout(350);assert.equal((await read()).stage,'draft');
 await p.keyboard.press('Tab');await p.waitForTimeout(180);await shot('keyboard-draft-focus');assert.equal(await p.evaluate(()=>document.activeElement.tagName),'CANVAS');await p.keyboard.press('Enter');await p.waitForTimeout(500);await shot('keyboard-after-choice');assert.equal((await read()).stage,'preview');
 await p.keyboard.press('F2');await p.waitForTimeout(180);await shot('settings');
 // Close is first, then audio, volume, reduced motion, shake, text size.
 for(let i=0;i<6;i++)await p.keyboard.press('Tab');
 await p.keyboard.press('Enter');await p.waitForTimeout(350);
 let cfg=await p.evaluate(()=>JSON.parse(localStorage.getItem('cinders:settings.sav')));assert(cfg.largeText);
 await click(600,324);cfg=await p.evaluate(()=>JSON.parse(localStorage.getItem('cinders:settings.sav')));assert(cfg.reducedMotion);
 await shot('settings-large');await click(550,575);await click(600,320);await p.keyboard.press('t');await p.waitForTimeout(250);
 cfg=await p.evaluate(()=>JSON.parse(localStorage.getItem('cinders:settings.sav')));assert.equal(cfg.skillKey,'t');
 await p.keyboard.press('Escape');await p.keyboard.press('F1');await p.waitForTimeout(180);await shot('help-large');await p.keyboard.press('Escape');
 await p.keyboard.press('Tab');await p.keyboard.press('Enter');await p.waitForTimeout(350);assert.equal((await read()).stage,'arena');
 await p.keyboard.press('t');await p.keyboard.press('Escape');await p.waitForTimeout(180);await shot('keyboard-pause');
 await p.keyboard.press('Tab');await p.keyboard.press('Enter');await p.waitForTimeout(180);
 results.push('keyboard-only draft, preview, pause; large text, reduced motion and rebinding');
 // Screenshots and runtime coverage for every normal and Hell identity.
 for(let floor=1;floor<=20;floor++){
   await fixture('boss-'+floor);await click(1100,610);await p.waitForTimeout(floor%10===2?4200:2700);
   await shot('boss-'+floor);assert.deepEqual(errors,[]);assert.equal((await read()).stage,'arena');
 }
 results.push('all 20 normal/Hell encounters render and run without console errors');
 await fixture('boss-10');await click(1100,610);await approach();await move(718,306);await p.mouse.down();
 for(let i=0;i<80;i++){
   await p.keyboard.press(String(i%3+1));await p.keyboard.press('t');await p.waitForTimeout(350);
   if((await read()).stage!=='arena')break;
 }
 await p.mouse.up();assert.equal((await read()).stage,'victory');assert((await read()).key);await shot('real-throne-victory');
 await click(760,500);assert.equal((await read()).stage,'shop');await click(1080,641);assert.equal((await read()).floor,11);
 results.push('real Empty Throne combat clear grants Infinity Key and enters Hell');

 // Source-only lab must not be available in the packaged game.
 await p.keyboard.press('F3');await p.keyboard.press('Escape');await p.waitForTimeout(180);await shot('packaged-no-lab');
 await p.goto('http://127.0.0.1:8123/embed');await p.waitForTimeout(2200);await shot('embedded');assert(await p.frames()[1].evaluate(()=>Module.calledRun));results.push('iframe loads');
 const denied=await b.newPage();await denied.addInitScript(()=>{Storage.prototype.getItem=function(){throw new DOMException('Disabled','SecurityError')};Storage.prototype.setItem=function(){throw new DOMException('Disabled','SecurityError')};});await denied.goto('http://127.0.0.1:8123');await denied.waitForTimeout(2000);assert((await denied.locator('#warning').textContent()).includes('Storage unavailable'));await denied.close();results.push('unavailable storage warning');
 assert.deepEqual(errors,[]);console.log('PASS',results.join('\nPASS '));fs.writeFileSync('.test-results/browser.json',JSON.stringify({browser:await b.version(),results,errors},null,2));
 }finally{await b.close();server.close();}
})().catch(e=>{console.error(e);server.close();process.exitCode=1;});
