# Gate to Hell — Blender UI and arena library

Open `preview.html` in a browser to view the floor variants, looping objects,
button states, element medallions and item icons. It works without a server.

Editable source: `art-src/blender/house-ui.blend`. Select a scene from Blender's
scene selector. Each export has its own camera, lighting, modeled geometry and
materials; animated scenes have keyframes 1–9. Frame 9 duplicates the initial
pose; exports sample 1–8 for seamless one-second loops. No external artwork or
font rasterization is used. Text remains live in LÖVE for accessibility.

Rebuild from the repository root using Blender 5.2 and ImageMagick:

```sh
blender -b -t 4 -P scripts/blender/build_house_ui.py
# Optional selected exports, saved to a separate Blender source:
blender -b -t 4 -P scripts/blender/build_house_ui.py -- coin infinity_key
```

Cycles renders use 16 samples, CPU rendering, denoising and Standard color
management. Intermediate frames are in `art-src/ui-frames/`. ImageMagick only
packs already-rendered frames into atlases. The older `build_ui.py` generates
the previous skin and should not be used to rebuild this library.

| Asset | Export | Runtime use |
| --- | --- | --- |
| button / button_hover / button_disabled | 192 × 64 RGBA | Default, hover/focus and unavailable actions |
| panel / card / slot / bar_track | 128 × 128 RGBA | Nine-slice frames with 12px corners |
| bg_title / bg_screen / bg_arena | 1280 × 720 | Title, all management screens, arena gallery |
| arena_floor | 1280 × 720 RGBA | Fallback stone platform |
| arena_floor_{element} | Nine 1280 × 720 RGBA images | Element-tinted stone for every encounter |
| ember_seal / coin / infinity_key / brazier / crystal | 768 × 96 RGBA | Eight 96px animation cells at 8 FPS |
| cardback | 1280 × 208 RGBA | Eight 160 × 208 cells, empty recruitment slots |
| floor_rune | 2048 × 128 RGBA | Eight 256 × 128 cells, quiet breathing floor inlay |
| elements | 768 × 192 RGBA | Nine 96px medallions; eight columns |
| items | 768 × 288 RGBA | All 23 items; 96px cells, eight columns |

Element and item orders are in `src/render/ui_textures.lua` and the renderer's
`ELEMENTS` / `ITEMS` arrays. `emblem.png` is a preserved legacy asset.

The floor camera uses azimuth 45°, elevation 30° and orthographic scale
`1280 / (78 × sqrt(2))`. One modeled unit equals 100 game units. The top surface
is z = 0 and the runtime draws its image at y = −15, aligning it with the
`iso.project()` centre (640, 345) and the complete ±350 world boundary.
Slab seams follow the original 70-unit grid. Props stand outside that boundary
and introduce no collisions. Amber/red telegraphs render above the floor.

Animations use visual clocks only, never combat RNG. Arena decoration freezes
when combat pauses. Reduced motion fixes animated images to frame zero and
disables drifting embers and card/medallion breathing. Missing textures keep
the procedural fallback. Runtime PNGs ship; Blender sources, previews and
intermediate renders stay outside the downloadable game.

Resource/action symbols added in `icons.png` come from the separate editable
`art-src/blender/element-effects.blend` source. Its generator is
`scripts/blender/build_polish.py`; the symbol and particle viewer is
`assets/effects/preview.html`. The original UI/scenery generator does not
overwrite these symbols.
