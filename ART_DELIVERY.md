# Blender artwork delivery

The new artwork is integrated into the LÖVE game and its default browser/native
packages. No DreamLayer key, paid model generator or image-generation API was
needed. These are modeled and animated Blender meshes rendered into 2D sprites.

- Nine new base bosses, ten Hell costumes and four extra Throne phase costumes:
  `assets/bosses/isometric/`,184 directional sheets /7,360 frames plus23 portraits.
- All 18 dedicated hero skill shapes,13 reactions, status/consumable cues,
  basic attacks/hits and hazard families: `assets/effects/combat/`,91 sheets /728 frames.
- Ten decorative boss props and four screen illustrations: `assets/scenery/`.
- New cover: `release/cover-blender.png`; the existing cover remains preserved.
- Gallery: `assets/art-preview.html` — open locally, select boss/direction/pose,
  or inspect every effect. Pause and reduced-motion controls operate on real frames.

The normal Ash Bailiff keeps its existing approved atlas. All other bosses now
use the shared renderer; Hell models have separate materials and attachments.
The Throne changes appearances for phases 2 and 3 in both normal and Hell fights.
Attacks align with warning timers; death plays before rewards. Texture caches
are bounded, and reduced motion uses readable static poses. Hazard art is
masked to the existing warning shapes, with wave/gravity escape sectors omitted.
No damage, collision, cooldown, balance or combat-RNG rules were changed.

Editable sources live in `art-src/blender/`:

| File | Contents |
| --- | --- |
| `bosses-complete.blend` |23 modeled appearances, materials and animation clips |
| `combat-effects.blend` |91 original effect scenes with keyed geometry |
| `scenery-and-illustrations.blend` |10 props and4 screen illustrations |
| `release-cover.blend` |630 ×500 cover composition and typography |
| `bailiff-isometric.blend` |Preserved Bailiff source used for the Hell costume |

Generation scripts are in `scripts/blender/`. They require Blender 5.2 and
ImageMagick; neither network access nor an API key is required. Run from the
repository root, setting `XDG_CACHE_HOME` to a writable cache folder if needed:

```sh
XDG_CACHE_HOME=/tmp/cinders-blender-cache ALSOFT_DRIVERS=null blender -b -t 4 -P scripts/blender/build_missing_bosses.py
XDG_CACHE_HOME=/tmp/cinders-blender-cache ALSOFT_DRIVERS=null blender -b -t 4 -P scripts/blender/build_combat_art.py
XDG_CACHE_HOME=/tmp/cinders-blender-cache ALSOFT_DRIVERS=null blender -b -t 4 -P scripts/blender/build_finishing_art.py
XDG_CACHE_HOME=/tmp/cinders-blender-cache ALSOFT_DRIVERS=null blender -b -t 4 -P scripts/blender/build_release_cover.py
python3 scripts/verify-art.py
npm test
npm run build
python3 scripts/verify-release.py
node scripts/browser-test.cjs --missing-art-only
```

`dist/gate-to-hell-blender-art.zip` contains this new art library and its
editable sources. Source models, preview pages, generators and test files are
excluded from runtime packages. The full runtime download is approximately 126 MB;
the web loader reserves 256 MiB of WebAssembly memory for the expanded library. See the per-folder READMEs for exact frame order,
anchors, durations and loop/clamp behavior. Authorship is recorded in
`assets/ATTRIBUTION.txt` and the in-game credits.

The README's authored sound/music/ambience tasks remain open; the existing
synthesized audio still works. Human playtesting and hosted/jam acceptance remain
separate from the automated rendering and gameplay checks. Nothing is published.
