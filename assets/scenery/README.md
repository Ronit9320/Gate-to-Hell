# Boss scenery and screen illustrations

Fourteen original Blender RGBA renders, each256 × 256 with transparent padding.
Ten boss props decorate the arena's left and right edges outside the walkable
floor: brazier, tidal arch, wind vane, rune monoliths, flowering trellis,
crystal outcrop, Tesla coil, sun dial, gravity apparatus and fractured portal.
They do not create collision or change navigable space.

Reward chest, Infinity Gate, broken crown and infernal doorway illustrate the
reward, victory/complete, defeat and Hell preview screens. These are static
images; gameplay effects provide the animated transitions.

Source: `art-src/blender/scenery-and-illustrations.blend` and
`scripts/blender/build_finishing_art.py`. Integration: `src/render/scenery.lua`.

```sh
XDG_CACHE_HOME=/tmp/cinders-blender-cache ALSOFT_DRIVERS=null blender -b -t 4 -P scripts/blender/build_finishing_art.py
```
