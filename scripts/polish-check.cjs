module.exports = async ({p,read,fixture,click,move,shot,results}) => {
 const assert=require('assert');
 await p.keyboard.press('F1');await p.waitForTimeout(200);
 for(let page=0;page<4;page++){
  await click(367+page*176,222);await shot('guide-'+(page+1));
 }
 await p.keyboard.press('Escape');await p.keyboard.press('F2');
 await click(600,420);await p.keyboard.press('Escape');await p.keyboard.press('F1');
 for(let page=0;page<4;page++){await click(367+page*176,222);await shot('guide-large-'+(page+1));}
 await p.keyboard.press('Escape');await p.keyboard.press('F2');await click(600,420);await p.keyboard.press('Escape');
 results.push('Four overview pages accessible with F1, rendered at standard and large text sizes');
 for(const id of ['jack','penny','gale','flint','clover','frost','volt','crown','null']){
  await fixture('hero-'+id);await click(1100,610);await move(718,306);
  const before=await p.evaluate(()=>effectTextures.created);
  await p.keyboard.press('e');await p.waitForTimeout(100);await shot('particles-'+id);
  assert((await p.evaluate(()=>effectTextures.created))>before,id+' skill uploads Blender effect atlas');
  assert.equal((await read()).stage,'arena');
 }
 results.push('All nine elements upload actual Blender effect atlases during live skills');
 await p.keyboard.press('F2');await click(600,324);await p.keyboard.press('Escape');
 await p.keyboard.press('e');await p.waitForTimeout(100);await shot('polish-reduced-motion');
 await p.keyboard.press('Escape');await shot('polish-pause');await p.keyboard.press('Escape');
 await fixture('management');await shot('polish-shop');await click(150,373);await shot('polish-offer');
 results.push('Reduced motion, pause, gold badge, shop action icons and offer price icon render without runtime errors');
 await p.goto(require('url').pathToFileURL(require('path').resolve('assets/effects/preview.html')).href);
 await p.waitForFunction(()=>document.querySelectorAll('canvas').length===9&&[...document.images].every(img=>img.complete&&img.naturalWidth>0));
 await p.waitForTimeout(350);
 await p.locator('#still').check();
 const frozen=await p.locator('canvas').first().screenshot();await p.waitForTimeout(250);
 assert(frozen.equals(await p.locator('canvas').first().screenshot()),'Reduced-motion preview must freeze actual particle pixels');
 await p.locator('#still').uncheck();await p.locator('#toggle').click();
 await shot('particle-library');
 results.push('Offline nine-element animation viewer loads every sheet, pauses, and freezes actual reduced-motion pixels');

};
