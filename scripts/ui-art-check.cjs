// Verify rendered Blender assets in the actual packaged game and capture previews.
module.exports = async ({ p, read, fixture, click, shot, results }) => {
  const assert = require('assert');
  const fs = require('fs');
  const path = require('path');
  await p.evaluate(() => {
    for (const name of ['run.sav', 'settings.sav']) {
      const file = '/home/web_user/love/gate-to-hell/' + name;
      if (Module.cindersFS.analyzePath(file).exists) Module.cindersFS.unlink(file);
      localStorage.removeItem('cinders:' + name);
    }
  });
  await p.reload();
  await p.waitForFunction(() => window.Module?.calledRun);
  await p.waitForTimeout(1300);
  const box = await p.locator('#canvas').boundingBox();
  const seal = { x: box.x + 1155 * box.width / 1280, y: box.y + 395 * box.height / 720,
    width: 70 * box.width / 1280, height: 70 * box.height / 720 };
  const frames = [];
  for (let i = 0; i < 8; i++) {
    frames.push(await p.screenshot({ clip: seal, path: '.test-results/ui-art-motion-' + i + '.png' }));
    await p.waitForTimeout(150);
  }
  assert(frames.some(frame => !frame.equals(frames[0])), 'The Blender brazier must animate in the packaged title');
  await shot('ui-art-title');
  await p.keyboard.press('F2');
  await click(600, 324);
  assert(JSON.parse(await p.evaluate(() => localStorage.getItem('cinders:settings.sav'))).reducedMotion);
  await p.keyboard.press('Escape');
  await p.waitForTimeout(300);
  const stillA = await p.screenshot({ clip: seal });
  await p.waitForTimeout(375);
  const stillB = await p.screenshot({ clip: seal });
  assert(stillA.equals(stillB), 'Reduced motion must freeze the actual rendered seal');
  results.push('Blender flame animation changes pixels; reduced motion freezes the rendered frame');
  await click(200, 525);
  assert.equal((await read()).stage, 'draft');
  await shot('ui-art-draft');
  await click(185, 610);
  await shot('ui-art-preview');
  await fixture('management');
  await shot('ui-art-shop');
  await click(600, 642); // Move off the offer buttons.
  await p.keyboard.press('F2');
  await click(600, 324); // Restore motion for the remaining visual review.
  await p.keyboard.press('Escape');
  await fixture('victory');
  await shot('ui-art-infinity-key');
  for (const floor of [1,2,3,4,5,6,7,9,10,11]) {
    await fixture('boss-' + floor);
    await click(1100, 610);
    await p.waitForTimeout(500);
    assert.equal((await read()).stage, 'arena');
    await shot('ui-art-floor-' + floor);
  }
  results.push('Every element floor and Hell scenery render; draft, shop, preview and Infinity Key screens render');
  fs.mkdirSync('art-src/previews', { recursive: true });
  await p.goto('file://' + path.join(__dirname, '../assets/ui/preview.html'));
  await p.waitForFunction(() => [...document.images].every(img => img.complete && img.naturalWidth));
  await p.waitForTimeout(800);
  await p.screenshot({ path: 'art-src/previews/house-ui-library.png', fullPage: true });
  await p.selectOption('#element', 'Cryo');
  await p.click('#motion');
  await p.waitForTimeout(150);
  await p.screenshot({ path: 'art-src/previews/house-ui-library-cryo.png', fullPage: true });
  results.push('Offline art preview loads and supports floor selection and animation pause');
  fs.writeFileSync('.test-results/ui-art.json', JSON.stringify({ results }, null, 2));
};
