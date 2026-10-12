module.exports=async({p,b,fixture,read,click,move,shot,approach,results})=>{
 const assert=require('assert'),fs=require('fs'),path=require('path');
 await fixture('boss-1');await click(1100,610);await p.waitForTimeout(350);await shot('bailiff-idle');
 let proof=await p.evaluate(()=>({created:bailiffTextures.created,active:bailiffTextures.active.size}));assert(proof.created>0,'Expected an actual 2048×1280 atlas uploaded to WebGL');
 await p.waitForTimeout(1800);await shot('bailiff-attack');
 // Move around the fixed boss; facing changes must load additional atlas directions.
 await p.keyboard.down('d');await p.waitForTimeout(1900);await p.keyboard.up('d');await shot('bailiff-facing');
 proof=await p.evaluate(()=>({created:bailiffTextures.created,active:bailiffTextures.active.size}));assert(proof.created>=2,'Facing must change');assert(proof.active<=2,'Directional GPU cache must remain bounded');
 await fixture('boss-11');await click(1100,610);await p.waitForTimeout(400);await shot('bailiff-hell');
 await fixture('boss-1');await click(1100,610);await approach();await move(718,306);await p.mouse.down();
 let stage='arena';
 for(let i=0;i<75;i++){
  await p.keyboard.press('e');await p.waitForTimeout(180);stage=(await read()).stage;
  if(i>=12&&i<=40)await shot('bailiff-clear-'+i);
  if(stage!=='arena')break;
 }
 await p.mouse.up();assert.equal(stage,'rewards','Death animation must finish and award rewards');await shot('bailiff-rewards');
 const r=await read();assert.equal(r.stats.clears,1);const gold=r.gold;await p.waitForTimeout(1200);assert.equal((await read()).gold,gold,'Reward must not repeat during death animation');
 results.push('Bailiff atlas uploaded to WebGL; idle/cast/facing/Hell render; at most two resident atlas textures; victory/death completes with one reward');
 await p.goto('file://'+path.join(__dirname,'../assets/bosses/bailiff_iso/preview.html'));await p.waitForTimeout(600);await p.selectOption('#animation','attack');await p.selectOption('#direction','1');await p.waitForTimeout(350);await p.screenshot({path:'art-src/previews/bailiff-animation-viewer.png'});
 fs.writeFileSync('.test-results/bailiff-browser.json',JSON.stringify({browser:await b.version(),results,textureProof:proof},null,2));
};
