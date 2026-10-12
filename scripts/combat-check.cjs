// Exercise the packaged game's real mouse/keyboard input and capture combat polish.
module.exports = async ({ p, fixture, read, click, move, shot, results }) => {
  const assert = require('assert');
  await fixture('boss-1');
  await click(1100, 610);
  await move(718, 306);
  // Two screen directions combine into an approach toward the boss's ground anchor.
  await p.keyboard.down('d');
  await p.waitForTimeout(830);
  await p.keyboard.up('d');
  await p.keyboard.down('w');
  await p.waitForTimeout(830);
  await p.keyboard.up('w');
  await p.mouse.down();
  await p.keyboard.press('e');
  await p.waitForTimeout(100);
  await shot('combat-melee-swing');
  await p.waitForTimeout(800);
  await shot('combat-melee-hit');
  for (let i = 0; i < 55; i++) {
    await p.keyboard.press('e');
    await p.waitForTimeout(200);
    if ((await read()).stage !== 'arena') break;
  }
  await p.mouse.up();
  assert.equal((await read()).stage, 'rewards', 'Melee must clear through close-range mouse attacks');
  results.push('close-range melee swing/hit effects and floor-one clear using real controls');
  await fixture('boss-1');
  await click(1100, 610);
  await p.keyboard.press('2');
  await move(718, 306);
  await p.mouse.down();
  await p.waitForTimeout(2300);
  await shot('combat-ranged-reload');
  await p.waitForTimeout(1400);
  await shot('combat-ranged-ready');
  await p.mouse.up();
  // Capture the targeted slam impact, which shakes even when it misses.
  await p.keyboard.down('d');
  await p.waitForTimeout(400);
  await p.keyboard.up('d');
  for (let i = 0; i < 16; i++) {
    await p.waitForTimeout(100);
    await shot('combat-impact-' + i);
  }
  assert.equal((await read()).stage, 'arena');
  await p.keyboard.press('F2');
  await click(600, 324); // Reduced motion.
  await p.keyboard.press('Escape');
  await p.waitForTimeout(300);
  await shot('combat-reduced-motion');
  results.push('ranged magazine/reload, boss impact, stable HUD and reduced-motion rendering');
};
