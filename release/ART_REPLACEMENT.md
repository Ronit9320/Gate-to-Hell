# Replacing the temporary artwork

The default build includes **all 18 reference-inspired Blender heroes, the Ash Bailiff animation atlases and Blender UI/scenery**. Original flat portraits are preserved and excluded. `heroSprites` and `bailiffSprites` independently control these animated libraries; `usePortraits` controls the older optional flat images used as fallbacks.

To add your art:

1. Put transparent square PNG portraits in `assets/heroes/<id>.png` and `assets/bosses/<id>.png`. 256 × 256 is a useful starting size. Keep the subject centered with transparent margins; previews and the arena scale the same image, currently using nearest-neighbor filtering. Change the filter in `src/render/sprites.lua` for smooth painted art if needed.
2. Set `usePortraits = true` in `src/data/presentation.lua`. To select flat hero portraits, also disable `heroSprites`; to select a flat Bailiff portrait, disable `bailiffSprites`.
3. Run `npm run build -- --include-art`. This includes only top-level PNGs in those two folders. Missing portraits retain geometric fallbacks. Remove/replace any unapproved top-level portrait before using this option, because it includes all top-level PNGs in both folders.
4. Update `assets/ATTRIBUTION.txt`, the in-game credits in `main.lua`, and `release/ITCH_PAGE.md`. Re-run tests and replace the cover/screenshots to match the final art.

Hero IDs: `jack`, `match`, `penny`, `dealer`, `gale`, `zephyr`, `flint`, `mason`, `clover`, `briar`, `frost`, `whiteout`, `volt`, `count`, `crown`, `oracle`, `null`, `laugh`.

Boss IDs: `bailiff`, `undertow`, `kite`, `bedrock`, `bramble`, `regent`, `static`, `sun`, `kings`, `throne`. Hell variants currently share the base boss portrait and keep their distinct patterns, labels and effects.

The preserved older `assets/bosses/bailiff/` directional animation files are not wired into gameplay and are excluded even with `--include-art`. Animation sheets require a separate renderer implementation; replacing a portrait does not enable directional animation.

The UI, element medallions, item icons, backgrounds and arena floors now use original Blender-rendered assets in `assets/ui/`. Their procedural fallbacks remain available; music/SFX (`src/core/audio.lua`) use no external samples. Open `assets/ui/preview.html` to inspect the artwork or see that folder's README to rebuild it. Keep the telegraph shapes and element labels readable when replacing visuals.

Build commands:

```sh
npm ci
npm test
npm run format:check
npm run build
npm run test:browser
node scripts/browser-test.cjs --firefox
node scripts/browser-test.cjs --release-only
```

The commands above test the default package with Blender UI, scenery and Bailiff sprites. Use the `--include-art` build command instead when verifying final portraits. Also pass `--include-art` to `python3 scripts/verify-release.py` and `python3 scripts/package-release.py` for that build. `dist/gate-to-hell-web.zip` is the upload, not the source tree. Developer tools, test fixtures, local saves, media and source-generation scripts are excluded.

## Adopted Blender boss sprites

The Ash Bailiff now uses `assets/bosses/bailiff_iso/` independently of `usePortraits`. See that folder's README and `preview.html` for sheet layout, frame anchors and animation controls. Its approved PNGs/metadata are packaged by default; other original portraits remain excluded. Disable `bailiffSprites` in `src/data/presentation.lua` to select the geometric fallback. Final screenshots now show this adopted boss model.

## Adopted Blender hero sprites

All 18 heroes now use `assets/heroes/isometric/`, with eight directions and
idle/walk/attack/skill/dodge/hurt/death animations. Their isometric portraits
also appear on cards. Open that folder's `preview.html` to compare original
references and the new models. See its README for editable sources and rebuild
commands. Disable `heroSprites` to use the previous fallback; original portraits
still require `usePortraits` plus an `--include-art` build. New hero geometry and
animation do not alter combat values, hitboxes or projectile origins.

## Completed Blender boss/combat library

The default release now includes all ten bosses and ten Hell appearances.
`assets/bosses/isometric/README.md` documents192px cells, eight directions,
clip offsets and the shared ground anchor. The original normal Bailiff export
remains in `assets/bosses/bailiff_iso/`. `bossSprites` enables all new costumes;
`bailiffSprites` controls the preserved normal Bailiff.

`assets/effects/combat/README.md` documents91 dedicated combat animation
sheets and their event hooks. `combatArt` controls this library. Stencils keep
artwork inside the existing hazard boundaries and away from wave/gravity safe
gaps. Replace visual sheets without changing collision or telegraph timers.

Ten optional scenery props and four screen illustrations live in
`assets/scenery/`. Editable sources are preserved in `art-src/blender/`;
`assets/art-preview.html` previews runtime frames offline. Source-only models,
generators and previews never ship in the game packages. Rebuild with
`npm run build`, validate with `python3 scripts/verify-art.py` and
`python3 scripts/verify-release.py`, then run
`node scripts/browser-test.cjs --missing-art-only`.
