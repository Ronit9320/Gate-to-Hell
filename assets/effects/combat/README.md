# Dedicated combat artwork

**91 transparent Blender animation sheets**, eight frames per sheet. Each PNG
is **512 × 256**, four columns by two rows, **128 × 128** cells with center anchor
**(64,64)**. Read frames in row-major order. Durations and suggested looping
behavior are in `combat.json` and `src/data/combat_art.lua`. One-shots clamp;
projectiles, fields, hazards and status overlays use gameplay-relative progress.
Reduced motion uses static frame3 at reduced opacity.

The library covers neutral melee/ranged attacks and trails; hit, empowered hit,
hurt, slam/cracks/dust, shield, dodge, switch and reload feedback; all eighteen
hero skill shapes; thirteen named reactions; nine elemental aura overlays;
persistent burn/electric/vulnerability/shield/stagger/Bloom cues; three
consumables; phase/recovery/defeat effects; and eighteen hazard families.
`critical` is visual feedback for existing damage multipliers of at least1.5;
no new critical-hit probability or damage rule was introduced.

Hazard artwork uses LÖVE stencils matching the existing warning/collision
shapes. Wave/Gravity masks omit the open gap with an extra margin. Warning
polygons, labels and arena routes remain live geometry. Pillar bodies rise above
their ground footprint, with eruption timing following the existing hazard.

Original models, curves and particle keyframes: `scripts/blender/build_combat_art.py`.
Editable scenes: `art-src/blender/combat-effects.blend`. The runtime renderer
is `src/render/combat_art.lua`; its shared cache is bounded to sixteen textures.
No cosmetic code consumes combat RNG, alters collision, or writes to saved heroes.

```sh
XDG_CACHE_HOME=/tmp/cinders-blender-cache ALSOFT_DRIVERS=null blender -b -t 4 -P scripts/blender/build_combat_art.py
python3 scripts/verify-art.py
```

Use `-- --ids hit critical` to render selected sheets. Selected runs preserve
the full library source and save a separate `.blend`. The browser gallery is
`assets/art-preview.html`. Runtime PNGs and metadata ship by default; models,
previews and generators remain source deliverables.
