# Ash Bailiff — Blender isometric sprites

Refined from the provided 2D portrait and existing skeletal rig. Layered charcoal armor, bronze edges, hollow hood, ember face markings and molten chest seal are modeled geometry, rendered with Blender Eevee. Existing portrait and old 128px sheets are preserved in their original folders.

- Eight directions, five animations, 320 rendered frames total.
- Transparent 256 × 256 RGBA frames, fixed origin `(128, 204)` at the ground plane.
- Each PNG is **2048 × 1280**, packed as 8 columns × 5 rows. Animations may wrap rows. Use the linear offsets in `bailiff.json` or `src/data/bailiff_sprite.lua`; do not assume one animation per row.
- Frame offsets: idle0 (8), attack8 (10), walk18 (8), hurt26 (4), death30 (10). 12fps except death10fps. Idle/walk loop; attack/hurt/death clamp to the last frame.
- Orthographic camera: azimuth45°, elevation30°, giving the game's 2:1 floor projection. This is the game-matching dimetric variant commonly used for isometric sprite art.
- Direction order: `y000` southwest, `y045` south, `y090` southeast, `y135` east, `y180` northeast, `y225` north, `y270` northwest, `y315` west. Angles refer to model yaw, not screen compass angles. Game coordinates use `round(atan2(dx, dy) / (π/4)) mod8`.
- Game draws at0.55 scale (a141px frame with transparent padding), anchored at the boss's projected ground position. The loader caches at most two direction textures and uses linear filtering.
- Reduced motion shows static key poses and skips the defeat-animation delay.

Open `preview.html` to inspect directions and animations. It uses the actual runtime atlases and does not need a server or external libraries. The `.blend`, raw frames, contact sheets and rendering script are source artifacts, not included in the game ZIP.

Editable source: `art-src/blender/bailiff-isometric.blend`. Original snapshot: `art-src/blender/bailiff-original.blend`.

Rebuild model/sheets (from repository root, with Blender5.2 and ImageMagick available):

```sh
ALSOFT_DRIVERS=null XDG_CACHE_HOME=/tmp/cinders-blender-cache blender -b art-src/blender/bailiff-original.blend --python scripts/blender/build_bailiff.py
ALSOFT_DRIVERS=null XDG_CACHE_HOME=/tmp/cinders-blender-cache blender -b art-src/blender/bailiff-isometric.blend --python scripts/blender/render_bailiff.py
npm run format
npm run build
```

Optional renderer flags after `--`: `--direction 0` through7 to regenerate one direction, or `--preview` for one idle frame. `--timer` schedules export in a running Blender GUI, allowing UI updates between renders.

In game: the first normal boss, its demo rematch and the Infernal Bailiff use these sprites. Idle faces the current player location; cast events trigger attack (impact aligned to the hazard's warning), damage triggers hurt, and normal-motion victory plays the death sequence before rewards. Walk is exported for future moving-boss behavior; this boss currently stands in place. Gameplay telegraphs and collision remain the authority for damage timing.

Default packages include only these explicitly approved Bailiff PNGs plus metadata. Other existing PNG portraits remain excluded unless the author chooses `--include-art`. Disable `bailiffSprites` in `src/data/presentation.lua` to restore the geometric Bailiff fallback.
