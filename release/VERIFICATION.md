# Release verification — 0.9.0

## Submission polish — 2026-10-12

Selected four author-provided DreamLayer cutouts (hit, critical, slash and shockwave) and integrated bounded, cached runtime rendering with reduced-motion behavior and missing-file fallback. Existing hazard masks and elemental skill art remain in use. Added bundled Cinzel / Adwaita Sans typography with OFL notices, metric-centered buttons, live control hints, defeated-hero ability states and a simpler damage readout. Added a single-use 180 ms skill buffer (cleared on switch), facing-based neutral dodge and accurate dodge audio.

Fixed a reproduced browser startup stall at 100% download: the optional IndexedDB preload cache write no longer blocks running the game. The browser test captures startup diagnostics on failure.

Validation: **58 Lua scenarios pass**, formatting and exact source/archive/checksum verification pass, native five-second startup is clean (expected timeout 124). Chromium 153 tactics/layout checks pass with large text, pause and transactions; combat checks pass melee victory, reload, impacts and reduced motion. Firefox 150.0.2 draft/combat/persistence smoke passes. No runtime errors captured. These focused checks cover this polish pass; earlier full-release journey evidence below remains historical. Fresh human feel/pacing review and hosted submission are still pending.

Packages: `dist/gate-to-hell.love`, `dist/gate-to-hell-web.zip`, with current checksums in `dist/SHA256SUMS`. New captures: `release/screenshots/polish-*.png`. No upload performed.

## Current Blender artwork delivery — 2026-10-12

All 49 Lua scenarios, formatting, exact package contents/checksums, and native five-second startup pass. Full image verification covers 23 appearances / 7,360 boss frames and 91 effect sheets / 728 frames, checking dimensions, alpha borders and animation variation. Editable Blender source libraries reopen and validate.

Chromium 153 focused artwork checks pass all 20 normal/Hell fights and all 18 skills with actual WebGL texture uploads, reduced motion, pause, victory/Hell-entry/defeat illustrations, and all six Throne phase appearances in the offline gallery. No captured runtime errors. Report: `.test-results/missing-art-browser.json`. Firefox 150.0.2 draft/combat/input/persistence smoke passes with no captured errors. Current screenshots are `release/screenshots/art-*.png`. The web loader reserves 256 MiB; current native/web archives are approximately 124/126 MB. Current hashes are in `dist/SHA256SUMS`.

The focused live Empty Throne fight also passes its phase progression, death, Infinity Key reward and Hell entry (`.test-results/art-finale.json`).

Authored sound/music and human acceptance remain open; no hosted upload performed.

## Earlier verification

Current combat refinement (2026-10-12): 41 LuaJIT scenario groups pass, including all 18 solo starters, 20 encounter victories and eight full runs. Focused Chromium 153 `--combat-only` checks pass melee input/clear, ranged reload/FX and reduced-motion rendering with no captured runtime errors. Native LÖVE startup exits with the expected timeout (124) and no output/errors. Formatting and source/archive/checksum verification pass. Native/browser packages rebuilt for v0.9.0; authoritative current hashes are in `dist/SHA256SUMS`. Full browser/release journeys below are historical; scripts now approach melee range but the complete journeys have not been rerun with the revised combat. Human feel, pacing and audio review remain open.

## Historical release evidence

Date: 2026-10-12. Local upload preparation complete; no hosted upload/submission performed. Final author artwork and human acceptance remain open.

- LuaJIT and Lua 5.5: 33 scenario groups pass.
- Chromium 153.0.8010.12: 19 regression groups, clean-profile full normal victory → Hell → natural defeat → restart, and keyboard-only management paths pass without captured runtime errors.
- Firefox 150.0.2: draft, input/combat and save/reload smoke passes.
- Native LÖVE 11.5 startup: no errors, expected 5-second timeout; null audio driver means no audible review.
- Source/archives/checksums/versions/licenses/exclusions verified by scripts/verify-release.py. Two consecutive final builds are byte-identical.
- Default packages contain the approved Bailiff atlases, with other portrait PNGs, developer lab, tests, local saves and source-generation scripts excluded. All runtime dependencies are included.

The automated full browser run used ordinary draft selection and earned purchases, with no injected snapshots or combat cheats. Its team was Madame Match / Flint Rook / Gale Knave. Total combat time was 48.68 simulated seconds; this is an expert-control result, not a human duration estimate. Eight separate headless runs from all four Commons and representative higher rarities also passed. Human balance and the original 20–35-minute pacing goal remain unverified.

A short 180-frame foreground floor-five sample on Linux x64, Intel i5-12450HX, headless Chromium/SwiftShader measured median16.7ms and p9516.8ms, JS heap8.6MB and WASM64MiB. This is not sustained hardware-GPU performance evidence or a universal60FPS guarantee.

Remaining work is listed in PLAYTEST_CHECKLIST.md and UPLOAD_CHECKLIST.md. Source reports/screenshots are in .test-results/; PHASE_AUDIT.md distinguishes automated evidence from manual acceptance.

Bailiff artwork update (v0.8.1): all35 headless groups pass; all320 rendered frames pass dimension/alpha/clipping/variation checks (minimum margin20px). Current Chromium focused checks confirm actual atlas GPU uploads, facing/cast/Hell rendering, two-sheet resident cache, and a single reward after the death animation. Current Firefox smoke passes. The19-group full regression and clean-profile ten-floor journey described above were performed on v0.8.0; they are historical evidence. Current listing captures use real game screens, with valid management/victory save snapshots for those screens.

Historical v0.8.1 artifact hashes:

```text
17771d40a040af432e1f7000ff0930d359dd329fd94aa0141c76a0ab8b3c4fea  gate-to-hell.love
07a0ada4a42c71927f49ad130c7dfe7cff5caa8b43c21cbf80b337c816e424f5  gate-to-hell-web.zip
```

## Tactical difficulty and Run Info revision

- 55 headless scenarios pass, including guarded damage, elemental resistance,
  reaction openings, shared recovery, automatic death switching, and read-only
  route previews across normal/Hell/demo boundaries.
- With three unequipped heroes and ordinary controls, stationary skill/attack
  cycling loses on floors 8, 10 and 20; warning-aware movement/dodging wins.
  Reproduce with `luajit scripts/balance-check.lua`; current evidence is
  `.test-results/tactics-comparison.json`. This is automated balance evidence,
  not a substitute for human difficulty feedback.
- Chromium `--tactics-only` passes: shop/current/Hell Run Info, resistance hover,
  paused arena, large text, and purchases without the old success overlay.
  Screenshots and report: `.test-results/run-info-*.png`,
  `.test-results/tactical-guard.png`, `.test-results/tactics-browser.json`.
- Formatting and exact release source/archive/checksum verification pass.
- Rebuilt native and web archives. Earlier stationary browser victory scripts
  reflect the previous easier balance; the current combat-control regressions
  use movement and dodging, and the new browser check covers the changed UI.
