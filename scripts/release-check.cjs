// Actual release UI journey: no injected run snapshots or combat overrides.
module.exports=async({p,b,boot,read,click,move,shot,approach,results})=>{
 const fs=require('fs'),assert=require('assert'),os=require('os');
 const press=async(key)=>{await p.keyboard.press(key);await p.waitForTimeout(180);};
 await click(200,525);assert.equal((await read()).stage,'draft');
 await shot('release-draft');await click(185,610);
 const journey=[];let profile;
 for(let floor=1;floor<=10;floor++){
  assert.equal((await read()).floor,floor);await click(1100,610);await approach();await move(718,306);await p.mouse.down();
  let frames;
  if(floor===5){frames=p.evaluate(()=>new Promise(resolve=>{const ds=[];let last=performance.now();function sample(t){ds.push(t-last);last=t;if(ds.length<180)requestAnimationFrame(sample);else{ds.sort((a,b)=>a-b);resolve({frames:ds.length,medianMs:ds[90],p95Ms:ds[171],jsHeapBytes:performance.memory?.usedJSHeapSize,wasmBytes:Module.HEAPU8?.buffer.byteLength});}}requestAnimationFrame(sample);}));}
  for(let step=0;step<220;step++){
   const n=Object.keys((await read()).team).length;
   await p.keyboard.press(String(step%n+1));await p.keyboard.press('e');await p.waitForTimeout(140);
   if((await read()).stage!=='arena')break;
  }
  await p.mouse.up();let r=await read();assert.equal(r.stage,floor===10?'victory':'rewards',`floor ${floor}`);
  console.log('CLEARED',floor);journey.push({floor,gold:r.gold,team:Object.values(r.team).map(h=>h.id),stats:r.stats});
  if(frames)profile=await frames;
  if(floor===10){await shot('release-victory');break;}
  await click(1100,610);r=await read();
  for(let i=1;i<=2;i++){
   r=await read();const offer=r.stock[String(i)];
   if(Object.keys(r.team).length<3&&r.gold>=offer.price){await click(150+(i-1)*238,373);await click(570,495);}
  }
  r=await read();if(r.gold>=r.stock['3'].price&&Object.keys(r.weapons).length<6){
   await click(626,373);await click(570,495);await click(190,562);await click(440,443);await press('Escape');
  }
  if(floor===3)await shot('release-shop');
  await click(1080,641);
 }
 assert((await read()).key);await click(760,500);assert.equal((await read()).stage,'shop');await click(1080,641);assert.equal((await read()).floor,11);await click(1100,610);await shot('release-hell');
 // Deliberately stop attacking and remain exposed until the team naturally loses.
 for(let i=0;i<600;i++){await p.waitForTimeout(400);if((await read()).stage==='defeat')break;}
 assert.equal((await read()).stage,'defeat');await shot('release-defeat');await click(200,465);assert.equal((await read()).stage,'draft');
 results.push('clean-profile release: ten normal victories, earned shop purchases, Infinity Key, Hell, natural defeat, restart');
 // Credits and audio mix persistence on the release UI.
 await p.reload();await boot();await click(300,668);await shot('release-credits');await press('Escape');await press('F2');await click(800,575);await click(600,260);await click(600,330);
 const mix=await p.evaluate(()=>localStorage.getItem('cinders:settings.sav'));await p.reload();await boot();assert.equal(await p.evaluate(()=>localStorage.getItem('cinders:settings.sav')),mix);
 results.push('credits and persistent music/effects controls');
 fs.writeFileSync('.test-results/release.json',JSON.stringify({browser:await b.version(),journey,profile,machine:{cpu:os.cpus()[0].model,platform:os.platform(),arch:os.arch()},renderer:'headless Chromium / SwiftShader',results},null,2));
};
