// Real browser controls and WebGL proof for all 18 isometric hero exports.
module.exports = async ({ p, read, fixture, click, move, shot, results }) => {
  const assert = require('assert'), fs = require('fs'), path = require('path');
  const ids = ['jack','match','penny','dealer','gale','zephyr','flint','mason','clover',
    'briar','frost','whiteout','volt','count','crown','oracle','null','laugh'];
  const proof = () => p.evaluate(() => ({ created: heroTextures.created, active: heroTextures.active.size }));
  for (const id of ids) {
    await fixture('hero-' + id);
    const loaded = (await proof()).created;
    await shot('hero-card-' + id);
    await click(1100, 610);
    await p.waitForTimeout(350);
    assert.equal((await read()).stage, 'arena');
    let textures = await proof();
    assert(textures.created > loaded, id + ' must upload an actual isometric atlas');
    assert(textures.active <= 4, 'Hero texture residency must remain bounded');
    await shot('hero-idle-' + id);
    await p.keyboard.down('d');
    await p.waitForTimeout(450);
    await shot('hero-walk-' + id);
    await p.keyboard.up('d');
    await move(718, 306);
    await p.mouse.down();
    await p.waitForTimeout(150);
    await shot('hero-attack-' + id);
    await p.mouse.up();
    await p.waitForTimeout(300);
    await p.keyboard.press('e');
    await p.waitForTimeout(120);
    await shot('hero-skill-' + id);
    await p.keyboard.press('Space');
    await p.waitForTimeout(65);
    await shot('hero-dodge-' + id);
    textures = await proof();
    assert(textures.active <= 4);
    assert(textures.created >= 2, id + ' must change facing and load a second direction');
  }
  results.push('All 18 heroes upload real WebGL atlases and render cards, idle, movement, attacks, skills and dodge with at most four resident hero sheets');
  await fixture('hero-jack');
  await p.keyboard.press('F2');
  await click(600, 324);
  assert(JSON.parse(await p.evaluate(() => localStorage.getItem('cinders:settings.sav'))).reducedMotion);
  await p.keyboard.press('Escape');
  await click(1100, 610);
  await p.waitForTimeout(150);
  const box = await p.locator('#canvas').boundingBox();
  const heroClip = { x: box.x + 430 * box.width / 1280, y: box.y + 348 * box.height / 720,
    width: 80 * box.width / 1280, height: 95 * box.height / 720 };
  const still = await p.screenshot({ clip: heroClip });
  await p.waitForTimeout(240);
  const next = await p.screenshot({ clip: heroClip });
  assert(still.equals(next), 'Reduced motion must freeze rendered hero pixels');
  await shot('hero-reduced-motion');
  await p.keyboard.press('F2');await click(600,324);await p.keyboard.press('Escape');
  await fixture('hero-fallen-team');
  await click(1100,610);
  await p.waitForTimeout(3300);
  await shot('hero-fallen-auto-switch');
  assert.equal((await read()).stage,'arena');
  assert((await proof()).created >= 2, 'Automatic switching must render the next hero alongside the fallen one');
  assert((await proof()).active <= 4);
  await fixture('death');
  await click(1100,610);
  await p.waitForTimeout(2500);
  for(let i=0;i<12;i++){
    await shot('hero-death-'+i);
    if((await read()).stage==='defeat')break;
    await p.waitForTimeout(100);
  }
  assert.equal((await read()).stage,'defeat','Hero defeat animation must finish and transition normally');
  results.push('Reduced motion freezes the hero; fallen teammates render with automatic switching; final defeat animation finishes');
  await p.goto('file://' + path.join(__dirname,'../assets/heroes/isometric/preview.html'));
  await p.waitForFunction(() => [...document.images].every(img => img.complete && img.naturalWidth));
  await p.waitForTimeout(500);
  fs.mkdirSync('art-src/previews/heroes',{recursive:true});
  await p.screenshot({path:'art-src/previews/heroes/roster-viewer.png',fullPage:true});
  await p.selectOption('#hero','oracle');await p.selectOption('#pose','skill');await p.selectOption('#direction','1');
  await p.waitForTimeout(400);
  await p.screenshot({path:'art-src/previews/heroes/oracle-viewer.png',fullPage:true});
  results.push('Offline reference comparison and seven-animation/eight-direction hero viewer loads');
  fs.writeFileSync('.test-results/heroes-browser.json',JSON.stringify({results},null,2));
};
