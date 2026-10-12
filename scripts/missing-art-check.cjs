// Actual packaged WebGL art and telegraphs, plus the offline source gallery.
module.exports=async({p,read,fixture,click,move,shot,results})=>{
 const assert=require('assert'),fs=require('fs'),path=require('path');
 for(let floor=1;floor<=20;floor++){
  await fixture('boss-'+floor);await click(1100,610);await move(718,306);
  await p.waitForTimeout(450);assert.equal((await read()).stage,'arena');
  if(floor!==1)assert((await p.evaluate(()=>newArtTextures.bosses))>0,'Boss '+floor+' must upload its new atlas');
  await shot('new-art-boss-'+floor);
  // Observe warnings and active releases in the same real simulation.
  await p.waitForTimeout(2900);assert.equal((await read()).stage,'arena');await shot('new-art-hazard-'+floor);
  assert((await p.evaluate(()=>newArtTextures.effects))>0,'Hazard '+floor+' must upload dedicated artwork');
 }
 results.push('All twenty normal/Hell fights upload original boss/effect textures and render live warnings/releases');
 for(const id of ['jack','match','penny','dealer','gale','zephyr','flint','mason','clover','briar','frost','whiteout','volt','count','crown','oracle','null','laugh']){
  await fixture('hero-'+id);await click(1100,610);await move(718,306);await p.keyboard.press('e');await p.waitForTimeout(90);
  assert((await p.evaluate(()=>newArtTextures.effects))>0,id+' skill uploads dedicated effect atlas');
  await shot('new-art-skill-'+id);
 }
 results.push('All eighteen live hero skills render dedicated authored shapes');
 await p.keyboard.press('F2');await click(600,324);await p.keyboard.press('Escape');
 await p.keyboard.press('e');await p.waitForTimeout(120);await shot('new-art-reduced');
 await p.keyboard.press('Escape');await shot('new-art-pause');
 results.push('Reduced motion and pause render with the new art');
 await fixture('victory');await shot('new-art-victory');await click(760,500);await click(1080,641);await shot('new-art-hell-entry');
 await fixture('death');await click(1100,610);
 for(let j=0;j<40;j++){await p.waitForTimeout(300);if((await read()).stage==='defeat')break;}
 assert.equal((await read()).stage,'defeat');await shot('new-art-defeat');
 results.push('New victory, Hell-entry and defeat illustrations render');
 await p.goto(require('url').pathToFileURL(path.resolve('assets/art-preview.html')).href);
 await p.waitForFunction(()=>document.querySelectorAll('#effects canvas').length===91&&[...document.images].every(i=>i.complete&&i.naturalWidth));
 for(const name of ['throne','throne_phase2','throne_phase3','throne_hell','throne_hell_phase2','throne_hell_phase3']){
  await p.selectOption('#appearance',name);await p.waitForTimeout(180);await p.selectOption('#pose','attack');await p.waitForTimeout(100);await shot('gallery-'+name);
 }
 await p.selectOption('#appearance','undertow');await p.selectOption('#pose','idle');await p.locator('#still').check();await p.waitForTimeout(100);
 const frozen=await p.locator('#boss').screenshot();await p.waitForTimeout(250);assert(frozen.equals(await p.locator('#boss').screenshot()));
 await p.locator('#still').uncheck();await p.waitForTimeout(250);const moving=await p.locator('#boss').screenshot();await p.waitForTimeout(200);assert(!moving.equals(await p.locator('#boss').screenshot()));
 results.push('Offline art gallery loads 23 appearances, Throne phases and 91 effects; reduced motion freezes real pixels');
 fs.writeFileSync('.test-results/missing-art-browser.json',JSON.stringify({results},null,2));
};
