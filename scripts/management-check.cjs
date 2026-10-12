module.exports=async({p,read,fixture,shot,results})=>{
 const assert=require('assert'),fs=require('fs');
 await fixture('management');await p.locator('#canvas').focus();
 async function choose(n){for(let i=0;i<n;i++)await p.keyboard.press('Tab');await p.keyboard.press('Enter');await p.waitForTimeout(250);}
 async function close(){await p.keyboard.press('Escape');await p.waitForTimeout(220);}
 // Five offers, three hero managers, inventory, reroll, next.
 await choose(1);await shot('keyboard-full-team-offer');await choose(2);await shot('keyboard-replace-confirm');
 const before=await read();await choose(2);let r=await read();assert.equal(r.team['1'].id,'gale');assert.equal(r.gold,before.gold-4);
 // Offer 1 is now sold; four remaining offers precede Manage hero 1.
 await choose(5);await choose(3);r=await read();assert.equal(r.team['1'].weapon,'scepter');assert.equal(Object.keys(r.weapons).length,1);
 await choose(3);r=await read();assert(!r.team['1'].weapon);assert.equal(Object.keys(r.weapons).length,2);await close();
 await choose(8);await shot('keyboard-inventory');await choose(2);await choose(2);assert.equal(Object.keys((await read()).weapons).length,1);await close();
 await choose(5);await choose(2);await choose(2);assert.equal(Object.keys((await read()).team).length,2);
 // Four offers + two managers + inventory + reroll + next.
 const gold=(await read()).gold;await choose(8);assert((await read()).gold<gold);
 await close(); // no modal; resets focus through Escape's menu handling only when applicable
 await shot('keyboard-management-complete');
 results.push('keyboard-only full-team replacement, confirmation, equip, unequip, inventory sale, hero sale, reroll');
 fs.writeFileSync('.test-results/management.json',JSON.stringify({results},null,2));
};
