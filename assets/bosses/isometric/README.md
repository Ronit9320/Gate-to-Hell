# Original Blender boss library

Nine new stationary bosses, ten distinct Hell appearances, and two additional
phase appearances for each Empty Throne costume. The approved Ash Bailiff base
remains in `../bailiff_iso/`. All models are original meshes; Infernal Bailiff
reuses the preserved Bailiff rig poses with new armor materials and shoulder horns.

Each appearance has eight **1536 × 960 RGBA** sheets and a transparent preview
portrait. Cells are **192 × 192**, packed eight columns by five rows. Fixed ground
anchor **(96,146)**, display scale **0.85**, orthographic azimuth45° / elevation30°.
Directions are southwest, south, southeast, east, northeast, north, northwest,
west (`boss_y000.png` through `boss_y315.png`).

| Animation | Offset | Frames | FPS | Behavior |
| --- | ---: | ---: | ---: | --- |
| Idle | 0 | 8 | 12 | Loop |
| Attack | 8 | 10 | 12 | Clamp; wind-up through frame6, release frame7 |
| Hurt | 18 | 4 | 12 | Clamp |
| Death | 22 | 10 | 10 | Clamp; rewards follow the one-second clip |
| Stagger | 32 | 4 | 8 | Loop while stunned |
| Recovery | 36 | 4 | 12 | Clamp after stagger |

Attack playback follows the first hazard's warning timer. Models do not dictate
collision or damage timing. No locomotion sheets are needed: these bosses stand
in place. Reduced motion freezes a readable pose and shows the final death pose
without waiting. The shared boss cache retains at most two directional atlases,
including when changing boss, Hell costume, or Throne phase.

Metadata: `bosses.json` and `src/data/boss_sprites.lua`. Editable source:
`art-src/blender/bosses-complete.blend`. Every scene has articulated pivots,
named materials and keyed clips. The source contains the preserved Bailiff rig
and its Hell pose bank. Camera-aligned export scenes are temporary.

From the repository root:

```sh
XDG_CACHE_HOME=/tmp/cinders-blender-cache ALSOFT_DRIVERS=null blender -b -t 4 -P scripts/blender/build_missing_bosses.py
python3 scripts/verify-art.py
npm run build
```

Use `-- --ids undertow kite --preview` for model inspection, or `-- --ids
undertow_hell` for selected exports. Selected runs save separate editable files.
Open `assets/art-preview.html` to inspect actual runtime sprites and effects
without a server. Source files and previews are excluded from runtime archives.
