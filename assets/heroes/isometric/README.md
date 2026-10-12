# Gate to Hell — reference-inspired isometric heroes

All 18 heroes have actual articulated Blender geometry, eight facing directions
and seven animations. Their original 2D portraits remain untouched in the parent
directory and are packed into the editable source as references. Clothing,
palette, headwear, masks, flowers, armor and signature props follow those images;
weapons and casting motions also reflect the existing combat kits.

Open `preview.html` directly in a browser to compare references with the new
models, select a hero, direction and animation, or inspect individual frames.

Editable source: `art-src/blender/heroes-isometric.blend`. Each hero has a named
scene, camera, lights, materials and a parent hierarchy of articulated controls.
Select controls such as `jack | upper.R` or `jack | chest` to adjust motion.
Timeline markers identify each animation; mesh parts follow their controls.

Rebuild the whole library from the repository root:

```sh
blender -b -t 4 -P scripts/blender/build_heroes.py
python3 scripts/verify-heroes.py
npm test
npm run build
luajit tests/fixtures.lua
node scripts/browser-test.cjs --heroes-only
python3 scripts/verify-release.py
```

Selected hero rebuilds preserve the complete source by saving a separate file:

```sh
blender -b -t 4 -P scripts/blender/build_heroes.py -- --heroes jack penny
blender -b -t 4 -P scripts/blender/build_heroes.py -- --heroes oracle --preview
```

Each hero folder contains eight `hero_y000.png` … `hero_y315.png` sheets and a
trimmed isometric `portrait.png` for draft, title, team and management cards.
The atlases are 960 × 1344 RGBA: six columns, seven rows, 160 × 192 cells.
Each animation occupies one complete row and contains six distinct time samples.
Loops have a duplicate endpoint in Blender but omit it from the export.

| Row | Pose | FPS | Behavior |
| --- | --- | --- | --- |
| 0 | Idle | 10 | Breathing loop |
| 1 | Walk | 12 | Articulated legs and opposing arms |
| 2 | Attack | 18 | Melee swing/punch or ranged arm extension |
| 3 | Skill | 12 | Two-arm elemental cast |
| 4 | Dodge | 24 | Crouch and forward lean |
| 5 | Hurt | 20 | Recoil |
| 6 | Death | 8 | Kneeling collapse; hold the final pose |

The camera is orthographic, at 45° azimuth and 30° elevation, with horizontal
sensor fit. Each frame has a fixed ground anchor (80, 154); gameplay draws at
0.70 scale. Facing order: southwest, south, southeast, east, northeast, north,
northwest, west, matching the existing isometric movement and Bailiff renderer.
Pose geometry is validated against every direction before rendering. Exports
are rendered as batches of evaluated 3D poses, not transformed 2D references.
Cycles uses eight samples, CPU rendering, denoising and Standard color management.
Runtime PNGs are re-encoded losslessly to reduce browser preload size; shading
colors and transparency are preserved without palette quantization.

`src/data/hero_sprites.lua` and `heroes.json` define the export contract.
`src/render/sprites.lua` shares a four-sheet GPU cache across all heroes and
directions; portraits have a separate small cache. Missing assets retain the
prior fallback. `heroSprites` in `src/data/presentation.lua` controls this library
independently of `usePortraits` and `bailiffSprites`.

Visual events live in `arena.heroVisuals`, outside the roster/save data. Movement
faces the travel direction; accepted attacks and skills face their aim; dodge
faces its direction. Individual states survive team switching. Fallen heroes
remain visible during the fight as the game switches to another living hero.
Final defeat displays its animation before the result screen. Pause freezes the
combat clock. Reduced motion uses a fixed idle frame and a fixed final fallen
pose, and skips the final defeat delay. Combat values, hitboxes, projectile
origins, damage timing and equipment mechanics are unchanged.

Runtime packages include the new sheets, portraits and metadata. Original flat
portraits, Blender sources, reference images and preview pages remain outside
the default package.
