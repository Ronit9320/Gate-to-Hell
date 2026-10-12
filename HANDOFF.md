# Project handoff

Last updated: 2026-10-12

## Submission polish — 2026-10-12

Selected four author-provided DreamLayer cutouts (hit, critical, slash and shockwave) and integrated bounded, cached runtime rendering with reduced-motion behavior and missing-file fallback. Existing hazard masks and elemental skill art remain in use. Added bundled Cinzel / Adwaita Sans typography with OFL notices, metric-centered buttons, live control hints, defeated-hero ability states and a simpler damage readout. Added a single-use 180 ms skill buffer (cleared on switch), facing-based neutral dodge and accurate dodge audio.

Fixed a reproduced browser startup stall at 100% download: the optional IndexedDB preload cache write no longer blocks running the game. The browser test captures startup diagnostics on failure.

Validation: **58 Lua scenarios pass**, formatting and exact source/archive/checksum verification pass, native five-second startup is clean (expected timeout 124). Chromium 153 tactics/layout checks pass with large text, pause and transactions; combat checks pass melee victory, reload, impacts and reduced motion. Firefox 150.0.2 draft/combat/persistence smoke passes. No runtime errors captured. These focused checks cover this polish pass; earlier full-release journey evidence below remains historical. Fresh human feel/pacing review and hosted submission are still pending.

Packages: `dist/gate-to-hell.love`, `dist/gate-to-hell-web.zip`, with current checksums in `dist/SHA256SUMS`. New captures: `release/screenshots/polish-*.png`. No upload performed.

## Current state

**Version 0.9.0 implements the game through Phase 8 and includes all 18 reference-inspired Blender heroes, UI, animated scenery and the Ash Bailiff sprites.** The complete gameplay catalog, settings, icons, synthesized music/SFX and credits are present. Default packages include the hero and Bailiff atlases and the UI/environment library; original flat portrait PNGs are preserved and excluded. Other bosses retain geometric placeholders. Native/browser files are in `dist/`; upload instructions and listing materials are in `release/`. Art viewers: `assets/ui/preview.html` and `assets/heroes/isometric/preview.html`. Current captures are in `art-src/previews/` and `.test-results/`.

Current phase: **Phase 8 local release preparation delivered**. Automated checks are recorded below. Full human acceptance is not signed off: fresh-player review, manual all-20 encounter clears, pacing and audible review remain open. Hosted checks and jam compliance await actual project/rules details. Nothing has been published. See `PHASE_AUDIT.md` and `release/PLAYTEST_CHECKLIST.md`.

## Reference-inspired isometric heroes — v0.9.0 (2026-10-12)

The author requested isometric heroes inspired by the existing flat sprites.
Inspected all 18 portraits, preserving their costume/palette/headwear/prop cues:
Jack's mining helmet and ember fan; Match's bob and black gown; Penny's cap,
overalls and lance; Dealer's navy suit/fedora/cards; Gale's green feathered hat;
Zephyr's teal hair and wind gown; Flint's silver plate armor; Mason's apron and
quarry stones; Clover's flower crown and thorn staff; Briar's emerald coat;
Frost/Null's jester silhouettes; Whiteout's ice crown and gown; Volt's purple
uniform and spear; Count's copper helmet/armor; Crown's violet armor/crown;
Oracle's jeweled veil and planetary orbit; Laugh's magenta suit and razor cards.

`scripts/blender/build_heroes.py` builds actual articulated 3D geometry, not
flat sprites rotated into diamonds. Editable source:
`art-src/blender/heroes-isometric.blend`, with 18 scenes, packed original
references, cameras/lights/materials, hierarchical joint controls and animation
timeline markers. Originals in `assets/heroes/*.png` are preserved unchanged.

Exports: `assets/heroes/isometric/<id>/hero_y000.png` … `hero_y315.png` and
`portrait.png`. 144 directional atlases contain 6,048 frames: idle, walk,
attack (melee/ranged), skill, dodge, hurt and kneeling defeat. Each atlas is
960×1344 RGBA, six columns/seven rows of 160×192 cells, fixed foot anchor
(80,154), 0.70 display scale. The 30° elevation/45° azimuth camera matches the
game's 2:1 isometric presentation. Geometry bounds are checked before rendering;
PNG bounds and animation variation are checked by `verify-heroes.py` afterward.
Runtime PNGs receive lossless compression; colors/alpha are not quantized.

Integration: `heroSprites` defaults true independently of older flat portraits.
Cards use the new trimmed isometric portraits. Combat uses facing and individual
visual states in `arena.heroVisuals`; accepted attacks, skills, movement, dodge,
hurt and death trigger the corresponding poses. These fields stay outside the
roster/save data and do not consume RNG. Off-field defeated heroes remain visible
while control auto-switches. Final defeat holds for 0.75s to show the animation;
reduced motion skips that hold and selects a static final fallen pose. Pause
freezes the clock. Combat stats, hitboxes, projectile origins and event timing
are unchanged. Four hero sheets remain resident across all heroes/directions;
missing art retains the prior fallback. Build and exact-package verification
include only runtime sheets, portraits and metadata, excluding source references.

Preview: `assets/heroes/isometric/preview.html` compares each original reference
with the new model, selects all seven poses/eight directions and scrubs frames.
Sources/render notes are in that folder's README. Browser evidence is captured
by `node scripts/browser-test.cjs --heroes-only` in `.test-results/hero-*.png`
and `art-src/previews/heroes/`.

Final verification: all 44 LuaJIT scenarios pass. New scenarios cover event
priority, accepted/rejected attack animation, facing, individual switching,
save isolation, static reduced-motion death and four-sheet eviction across
all 144 hero/direction combinations. `verify-heroes.py` passes all 18 heroes,
144 atlases and 6,048 frames: correct dimensions/RGBA, animation variation,
distinct directions, portraits, fixed anchors and a minimum 20px alpha margin.
Existing UI export verification still passes all 29 assets. Formatting passes.

Chromium 153 `--heroes-only` passes every hero's actual WebGL atlas upload,
direction changes, card/idle/walk/attack/skill/dodge presentation, ≤4 resident
hero atlases, frozen reduced-motion pixels, automatic switching with fallen
teammates, final defeat completion and the offline reference/animation viewer.
No captured runtime errors. Final screenshots were visually inspected for
alignment, card readability and combat placement. Reports:
`.test-results/heroes-browser.json`; full roster: `art-src/previews/heroes/roster.png`;
interactive captures: `roster-viewer.png` and `oracle-viewer.png` in that folder.
Native/web artifacts rebuilt and exact source/archive/license/checksum checks
pass. The native archive is approximately 54 MiB; hero exports approximately
44 MiB after lossless compression. Human visual/balance acceptance remains open.

## Blender UI and arena art — v0.9.0 (2026-10-12)

The author requested Blender-made animated UI and scenery. Reviewed the gameplay
catalog, render/input paths, combat patterns, economy/save boundaries, existing
asset generators and release packaging before building the new library.
`scripts/blender/build_house_ui.py` now models and exports 29 assets: three
button states; scalable panel/card/slot/bar frames; three backgrounds; a fallback
platform and nine subtly element-tinted stone platforms; nine element medallions;
all 23 item icons; and seven eight-frame loops (ember seal, coin, Infinity Key,
brazier, crystal, card back and floor rune). Preserved the legacy emblem and
existing character/Bailiff art. All new UI/scenery PNGs ship by default.

Editable source: `art-src/blender/house-ui.blend`, with separate scenes, real
modeled geometry, lighting, orthographic cameras and animation keyframes. The
floor uses the exact game projection: azimuth 45°, elevation 30°, one Blender
unit per 100 game units, centre corrected to (640, 345), slabs on the original
70-unit grid. Decorative props stay outside the ±350 play boundary. Amber/red
warnings draw above the floor; no combat, economy or collision tuning changed.

Runtime uses nine-slice frames, cached sprite cells, live text and rarity borders.
Animated UI seals, breathing cards/medallions, floating embers, braziers, crystals
and floor runes respect reduced motion; arena decoration freezes with combat.
Rebuilt modal/action surfaces, empty recruitment cards, item offer/HUD icons,
rewards and Infinity Key presentation. A brass frame now backs the boss HUD.
Missing art retains procedural fallbacks. Updated credits and attribution.

Review: `assets/ui/preview.html` works offline and has animation pause and floor
selection. Screenshots: `art-src/previews/house-ui-library*.png` and
`.test-results/ui-art-*.png`; the latter include all nine element floors and Hell.

Verification: 42 LuaJIT scenarios pass, including a new scalable-frame/atlas/
reduced-motion contract. `verify-ui-art.py` passes all 29 PNG dimensions/RGBA,
seven loops with distinct poses and transparent margins, nine distinct floor
exports and editable source presence. Chromium 153 `--ui-only` passed keyboard
draft/settings/rebinding/pause, large text/reduced motion, all 20 encounters,
actual Throne victory/Hell progression, iframe and unavailable-storage checks.
Focused `--art-only` passes live flame pixel variation, frozen reduced-motion
pixels, management/reward art, every element floor/Hell and offline preview
controls. Formatting and exact native/web package verification pass. Browser
reports are automated evidence; human visual/gameplay acceptance remains open.

## Combat refinement — v0.9.0 (2026-10-12)

Requested melee heroes, finite ranged attack cadence, increased difficulty, attack/hit effects and impact frames/shake for massive boss attacks. Seven existing heroes now have directional melee basics (Jack, Gale, Flint, Mason, Frost, Volt, Laugh); Flint's elemental stone strike is also melee. Other heroes have five-shot magazines, 0.46s shot cadence and 1.65s automatic reloads. Ammo/cooldowns remain individual across switches; skills work during reload after short basic recovery. Melee windup is 0.09s with 122-unit reach, 23 damage and 0.58s cooldown; dodge cancels a pending swing. Old boundary saves remain readable, new ammo/timers are validated.

Boss base HP is 308 (+10%, capped at 8400), incoming base damage is min(32, 17 + floor), and slams deal 1.3x. Every fourth Bailiff cast adds a boss-centered smash. Existing warning minimums and safe paths remain. Movement slows briefly on attack. FX: slash arcs, muzzle flashes, projectile tails, hit starbursts/actor flashes, dodge trails, landing shockwaves, brief hitstop and a subtle arena impact frame. Boss heavy attacks shake on activation even if avoided; HUD stays fixed. Reduced motion disables shake/screen flashes. Health/reload/attack recovery/dodge readiness are shown; draft/shop cards identify combat style. New attack/heavy-impact audio cues added.

Verification: all 41 LuaJIT scenarios pass, including all 18 solo starters, 20 encounters, eight full-run simulations, save compatibility, melee misses/direction, dodge cancellation, reload timing/switch behavior, activation-only heavy FX and bounded visual events. Chromium 153 focused `--combat-only` check passes real close-range melee clear, ranged reload/FX and reduced-motion rendering with no captured errors. Screenshots/reports: `.test-results/combat-*`. Native/web packages rebuilt. Human balance/audio/pacing acceptance remains open; previous full browser/release journeys are historical and do not establish current balance acceptance. Those scripts now approach melee range using real movement; the full journeys have not been rerun for v0.9.0.

## Confirmed user decisions

- Engine/language: LÖVE 2D and Lua; browser release for itch.io.
- Real-time isometric combat; control one hero and switch instantly, with up to two owned off-field heroes.
- Start with **one free hero chosen from four distinct full-roster offers**. Each offer rolls **65% Common / 25% Uncommon / 8% Rare / 2% Legendary**; then select an unoffered hero of that rarity. This replaces the original three-starter/four-element rule. Recruit additional heroes in shops.
- Never own more than three heroes; buy/sell/manage the team between floors.
- Ten elemental boss floors, followed by the Infinity Key and optional endless Hell with increasing difficulty.
- Nine elements; Gravity and Antimatter heroes are Legendary only. Four hero rarities.
- Visible damage and elemental reactions; buffs, weapons, and hero shops after floors.
- Balatro-inspired management UI leading into an arena; original named hero and boss variations.
- Placeholder first playable, with particles and small effects allowed.
- Update this file after **every phase**.

## Accepted rules and implementation defaults

See `BUILD_PLAN.md` for full details. Individual HP/cooldowns persist while off-field; no off-field AI attacks; all owned heroes dying ends a run, including a solo starter; floor clears revive/heal the team. One weapon per hero, three Curio slots, two consumable slots, six unequipped weapon slots. Full-team purchases require atomic replacement. No selling the last hero. Save at floor/shop boundaries; restarting the browser during a fight restarts the encounter from its entry snapshot.

Content target: 18 named heroes, 10 distinct normal bosses and 10 Hell variants, 8 weapons, 12 Curios, and 3 consumables. The complete gameplay catalog is now implemented; new boss art remains geometric placeholder work. The user accepted the recommended ruleset and proposed naming direction, then confirmed full-roster draft odds. Exact combat numbers and item/shop tuning remain implementation defaults. The canonical catalog is `GAME_CONTENT.md`.

## Phase status

| Phase | Status | Evidence / remaining gate |
| --- | --- | --- |
| Planning | Complete | README read; four gameplay answers incorporated; three planning/content documents created; one-hero draft amendment incorporated. |
| 0 — Runtime and browser proof | Implemented; automated checks pass | Native 11.5 startup; web 11.4 compatibility runtime; Chromium input/audio-start/storage/fullscreen/iframe tests. Audible review and hosted iframe pending. |
| 1 — Combat foundation | Implemented; automated checks pass | Isometric movement/aim, telegraphed lane/slam/bolt attacks, HP, dodge, switching/death, bounded effects, pause, browser fight. Human feel review pending. |
| 2 — Placeholder first playable | Implemented; automated checks pass | 18 functioning kits; 81-pair reaction test; all solo starters win in simulation; browser demo completes with recruitment. Independent fresh-player review pending. |
| 3 — Progression and management | Implemented; automated checks pass | 30-floor scenario; inventory/transactions; versioned saves; browser Continue, Finish, Hell, defeat, full inventory, insufficient gold and reload checks. Human manual acceptance pending. |
| 4 — UI and player flow | Implementation delivered | Nine element icons added; keyboard management and readability verification recorded in final release notes. Human acceptance remains open. |
| 5 — Heroes and reactions | Implemented; automated checks pass | All 18 kits, 8 weapons, 12 Curios, 3 consumables; acquisition/effect/order/cap/save tests. Human balance review pending. |
| 6 — Bosses and Hell | Implemented; acceptance in progress | Ten distinct bosses + ten Hell variants; 20 live-control simulation wins; 100 Hell floors of stress testing; source-only encounter lab. Manual clears and pacing review pending. |
| 7 — Balance and finish | Implementation delivered; human balance/audio acceptance open | Original geometric defaults, music/SFX, mix controls, pools; eight full-run simulations and bounded stress checks. See Phase 7 log. |
| 8 — Release readiness | Local upload preparation delivered | Reproducible packages, listing/cover/screenshots and replacement guide; clean-profile release journey passed. Human/hosted/jam acceptance and author upload remain separate. |

## Earlier completed work — planning (historical)

- Read the entire `README.md` and inspected repository contents. At initial inspection only the README was a visible project file; it was untracked. The README was subsequently updated at the user’s request; see the phase log.
- Asked and incorporated combat mode, starting elements, post-floor-10 structure, and hero-control decisions.
- Created `BUILD_PLAN.md` with sequential phases, measurable gates, gameplay/economy defaults, original named variants, and browser-first validation.
- Checked upstream love.js and itch.io HTML5 documentation; links are in the build plan. No exporter has been installed or verified here.
- Validation: documentation scope and decision consistency reviewed. No game tests were run because no implementation exists.

## Next steps for the implementing session

1. Use `release/ART_REPLACEMENT.md` to add the author's final artwork; keep generated source portraits excluded unless expressly chosen. Rebuild and refresh release media after asset changes.
2. Complete the human checks in `release/PLAYTEST_CHECKLIST.md`; do not infer manual acceptance from automated tests.
3. Follow `release/UPLOAD_CHECKLIST.md` when the author chooses to upload. Obtain the real jam URL/deadline/rules and perform hosted verification then.
4. Preserve the pinned runtime/save adapter. Use `npm test`, `npm run build`, browser/Firefox/release/management tests and `python3 scripts/verify-release.py` after changes.

## Verified commands and artifacts

- Native: `love .` (LÖVE 11.5); startup smoke: `timeout 5s env XDG_DATA_HOME=/tmp/cinders-native-data love .` ran without errors and exited via the expected timeout (124).
- Install: `npm install --cache /tmp/cinders-npm`; lockfile supports `npm ci` for clean installs. Dependencies: love.js 11.4.1, Playwright 1.56.1, StyLua 2.6.0.
- Tests: `npm test` / `luajit tests/run.lua` — 33 scenario groups passed. `lua tests/run.lua` also passed under Lua 5.5.
- Formatting: `npm run format:check` passes. `git diff --check` clean (original documents and all new work are untracked; no commits made).
- Build: `npm run build` — native and web packages produced, root entries and excluded test files asserted. Two consecutive builds had identical SHA-256 sums.
- Serve: `npm run serve` serves `dist/web` at http://localhost:8000. The browser test harness independently serves the same files on loopback port 8123.
- Browser: `luajit tests/fixtures.lua`, `node scripts/browser-test.cjs`, `node scripts/browser-test.cjs --firefox`. Chromium 153.0.8010.12: 19 UI/runtime scenario groups, including all 20 encounter renders and an actual Empty Throne victory/Infinity Key/Hell flow; Firefox 150.0.2: draft/combat/input/persistence smoke. Console error lists empty.
- Artifacts: `dist/gate-to-hell.love`, `dist/gate-to-hell-web.zip`, `dist/web/`, `dist/SHA256SUMS`.
- Reports/screenshots: `.test-results/browser.json`, `.test-results/firefox.json`, `.test-results/*.png` (generated, ignored, not packaged).
- Release journey: `node scripts/browser-test.cjs --release-only` — ten floors → Infinity Key → Hell → natural defeat → restart, all through real UI and earned purchases.
- Keyboard management: `node scripts/browser-test.cjs --management-only` — replacement/confirmations/equip/unequip/sales/inventory/reroll passed.
- Package validation: `python3 scripts/verify-release.py`; listing/cover/screenshots/replacement guide in `release/`; bundle with `python3 scripts/package-release.py`.
- Hosted itch.io URL / submission: none.

## Open information and risks

- Need jam URL, deadline/timezone, and submission rules before committing a schedule or submitting.
- Final title: **Gate to Hell**.
- User wants publication files with most assets left for replacement. Default geometric presentation and original synthesized audio are implemented; jam asset/AI restrictions are unknown.
- Browser runtime compatibility, audio startup, storage, resizing, fullscreen and local embedding have automated coverage. Audible quality and hosted behavior remain unverified. See final release notes for bounded headless performance observations.
- All 18 offered placeholder kits now function and pass solo floor-one simulation. Human balance testing remains essential. Eighteen heroes and twenty boss configurations are substantial jam content. Build reusable data/pattern systems, but do not silently drop promised content; flag schedule conflicts when a deadline becomes known.
- Hosted tests need an itch.io project/account path. Publishing has not been requested or performed.

## Required update procedure after every phase

1. Set the completed phase status only if its acceptance gate passed. Otherwise mark In progress or Blocked and identify the failing gate.
2. Update the date, current state, next phase, and concrete next action.
3. List changed files/modules and the behavior delivered; link any builds or relevant commits that actually exist.
4. Record commands run and their outcomes, manual browser scenarios, browser/version, and material limitations. Never treat native-only success as web verification.
5. Record decisions, changed tuning, deviations from the plan, and known defects. Update `BUILD_PLAN.md` if scope or phase gates change; preserve the distinction between user requirements and tuning defaults. Keep `GAME_CONTENT.md` synchronized with content changes.
6. Add an entry to the phase log below. Preserve previous phase history; keep this file useful for a fresh session without relying on chat context.

### Phase log template

```markdown
### YYYY-MM-DD — Phase N: name
- Status: Complete / In progress / Blocked
- Delivered:
- Files changed:
- Commands and automated results:
- Manual/browser checks and environment:
- Artifact paths / hosted URL:
- Decisions or plan changes:
- Known issues / failed or unavailable checks:
- Exact next action:
```

## Phase log

### 2026-10-12 — Pixel-art sprite assets (DreamLayer)

- Status: Delivered, automated checks pass; visual acceptance pending human review.
- Delivered: 18 hero portraits + the Ash Bailiff generated as 16-bit pixel art via DreamLayer `text_to_image` (1 credit each), cleaned with `background_remove` (1 credit each), trimmed/resized to 256px transparent sprites, and wired into hero cards (draft/preview/shop/team) and the arena as nearest-neighbour billboards. Missing assets degrade to the previous procedural placeholders.
- Credits: promotional balance started at 100; 57 spent (probe, an initial buggy batch, the 19-image v2 batch, and 19 background removes); 43 remain (~0.17 USD/credit).
- Files changed: added `src/render/sprites.lua`; rewrote card/arena drawing in `src/ui/draw.lua`; `main.lua` small-card HP text width; new `scripts/dreamlayer-assets.py`, `scripts/dreamlayer-nobg.py`, `scripts/process-assets.sh`; shipped sprites under `assets/heroes/` + `assets/bosses/`; large sources in `art-src/` (git-ignored); HANDOFF/README status.
- Commands and automated results: `npm test` all 18 scenario groups pass; `npm run build` packages 19 sprites with no `art-src/` leak; `node scripts/browser-test.cjs` (Chromium 153) — all 16 UI scenarios pass with sprites loaded; LÖVE 11.5 smoke launch clean; screenshot harness in `/tmp` confirmed sprites render (29,670 vs 1,707 card pixels with/without assets).
- Manual/browser checks: sprites render in native and web builds; hero pink/purple palettes (nullable, oracle, volt) retain interior colour after cutout.
- Artifacts: `dist/gate-to-hell.love`, `dist/gate-to-hell-web.zip`, `assets/heroes/*.png` (18), `assets/bosses/bailiff.png`, `art-src/previews/{contact-sheet,art-title-cards,art-arena}.png`.
- Decisions / notes: `background_remove` chosen over local chroma-keying (gradient magenta backgrounds leaked into characters); sources kept out of the shipped package; the Ash Bailiff sprite is used on every floor because later distinct bosses are still Phase 6.
- Exact next action: visually inspect `art-src/previews/`; if the art direction is approved, extend to item icons (weapons/Curios/consumables) and the other nine bosses when Phase 6 lands.

### 2026-10-11 — Planning

- Status: Complete.
- Delivered: build phases, content proposals, acceptance gates, and ongoing handoff procedure.
- Files changed: added `BUILD_PLAN.md` and `HANDOFF.md`; README unchanged.
- Validation: checked the pitch and all four user decisions against the plan; implementation checks are not applicable yet.
- Artifacts: planning documents only.
- Known limitations: no installed runtime verification, game code, build, hosted test, or submission.
- Exact next action: begin Phase 0 when the user requests implementation.

### 2026-10-11 — Rules accepted; one-hero draft and content catalog

- Status: Planning update complete; no implementation phase completed.
- Delivered: start with one free hero selected from four distinct full-roster offers, with confirmed per-offer rarity odds of 65/25/8/2. All other recommended rules accepted.
- Files changed: updated `BUILD_PLAN.md` and `HANDOFF.md`; added `GAME_CONTENT.md` with heroes, bosses/Hell variants, types, rarities, weapons, Curios, consumables, reactions, acquisition, controls, and first-playable scope. README retained as the historical pitch; newer rules take precedence.
- Implementation consequences: Phase 2 includes all 18 working placeholder kits and required reactions; the opening fight must work solo for every starter. First shop guarantees an affordable unowned Common. Empty hero slots do not count as defeated heroes. The demo ends after a stronger Ash Bailiff rematch.
- Tuning defaults clarified: free starter has zero resale value, owned duplicates blocked, separate draft RNG, and no draft reroll button. Numerical combat balancing remains flexible.
- Validation: reviewed all three documents for obsolete three-starter rules, catalog counts, rarity availability, and phase consistency. No game tests apply yet.
- Artifacts: documentation only.
- Exact next action: begin Phase 0 when implementation starts; progress through Phases 1–2 for the browser-playable demo.

### 2026-10-11 — README synchronized

- Status: Documentation update complete; implementation has not started.
- Delivered: README now covers the confirmed one-hero draft and odds, real-time combat, three-hero cap, shop management, ten floors and endless Hell, controls, first-playable scope, and project-document links.
- Files changed: `README.md`; synchronized README references in `BUILD_PLAN.md`, `GAME_CONTENT.md`, and this handoff. Earlier log entries describe the state at the time they were written.
- Validation: checked local document links and consistency with the accepted draft, roster limits, and implementation status. No game tests apply to this documentation-only update.
- Exact next action: Phase 0 runtime and browser proof when implementation starts.

### 2026-10-11 — Phase 0: runtime/export checkpoint
- Delivered: LÖVE skeleton, reproducible source archive, pinned npm exporter, browser shell, generated tone, and filesystem-to-localStorage persistence adapter.
- Versions: native LÖVE 11.5; npm love.js 11.4.1 embeds LÖVE 11.4, so conf.lua targets 11.4 APIs. Compatibility mode, 64 MiB initial memory. Upstream master advertises 11.5 but the published npm runtime is older; this distinction is intentional.
- Commands: `npm install --cache /tmp/cinders-npm`, `npm run build`, `node scripts/browser-test.cjs`. Browser/server execution needs sandbox approval here.
- Artifacts: dist/gate-to-hell.love, dist/gate-to-hell-web.zip, dist/web/index.html.
- Chromium 153 loads and draws the Lua runtime. Further persistence/input checks recorded below; audible quality and hosted iframe verification require human review. Phase remains in progress until all acceptance checks pass; proceeding with the authorized implementation while retaining those gates.

### 2026-10-11 — Phase 1: combat foundation checkpoint
- Delivered: world-space arena, invertible isometric projection, screen-relative controls, projectile collision, bounded arena, dodge, basic/skill cooldowns, shields, individual hero state, switching/auto-switching, pause/focus handling, Ash Bailiff lane/slam telegraphs, damage labels and HUD. Temporary main.lua supports a three-hero fixture and Enter to restart.
- Files: src/core/util.lua, src/render/iso.lua, src/combat/{arena,damage}.lua, src/ui/draw.lua, main.lua. Hero/reaction data introduced alongside combat to keep the central pipeline coherent.
- Automated check: two-hero damage scenario auto-switches, then produces defeat; passed with LuaJIT.
- Status: implementation checkpoint; browser alignment/playability acceptance awaits integrated browser checks. Phase 0 proof corrected browser save root and a multi-return tonumber issue; no exporter incompatibility remains.
- Next: replace fixture with draft, preview, reward/shop, and rematch flow; exercise every hero and ordered reaction pair.

### 2026-10-11 — Phase 2: first-playable implementation checkpoint
- Delivered: title, weighted four-offer draft, all 18 named placeholder kits/passives, nine elements, symmetric reaction table with bounded triggered effects, preview, arena, rewards, shop inspection/recruitment/sales/explicit replacement, initial four items, two-fight demo, defeat/restart. Full run option anticipates Phase 3.
- Files: main.lua, src/data/{heroes,reactions,items}.lua, src/run/model.lua; expanded arena and UI.
- Automated check: seeded draft -> solo entry -> reward exactly once -> guaranteed Common recruitment -> rematch -> demo-complete; passed with LuaJIT.
- Phase status: implementation present; full roster, matrix, browser flow and solo-viability checks pending. No claim of human playtest acceptance.
- Known scope: geometric placeholder art, repeated Ash Bailiff, no final audiovisual polish. Extra consumable definitions are present but shop stock remains the Phase 2 item set.
- Next: versioned safe saves, Continue, run-replacement warning, complete progression/economy regression tests and integrated web checks.


### 2026-10-11 — Phase 3: progression, management and final verification
- Status: implementation delivered, automated checks pass. Explicit human/manual acceptance portions of the phase gates remain pending; no fresh-player or audible-quality claim.
- Delivered: deterministic run seeds and independent draft/shop/combat/visual RNG state; ten-floor progression, floor-10 Infinity Key and Finish/Enter Hell choice, Hell cycle labels/scaling, statistics, repeat-safe rewards, complete initial-item inventory management, guarded atomic purchases/sales/replacements/equip/unequip/rerolls, save boundaries and Continue.
- Saves: version 1 data-only JSON codec (no Lua evaluation); structure/content/timer/boundary validation; draft, stock and RNG persist; mid-fight reload restores entry snapshot; corrupt/future/absent/blocked-storage behavior covered; explicit existing-run replacement confirmation. Browser shell synchronously mirrors the three save/settings files on close; a reentrancy guard prevents read-close recursion. Native uses the LÖVE save directory.
- Tests: 18 automated scenario groups include 10,000 seeded drafts, 81 ordered pairs, every hero's skill, all 18 solo wins without damage/invulnerability cheats, passives, damage/shields, switch/death, inventory bounds, transaction rollback, 30-floor progression, save failures and reload integrity. LuaJIT and Lua 5.5 passed.
- Browser checks: actual mouse/keyboard-driven two-fight loop; recruitment; reload in draft/combat/shop; reward/purchase integrity; Finish Run; Enter Hell; full inventory; insufficient gold; defeat/restart; settings persistence; 900×650 and 1280×800 viewports; fullscreen; iframe load; audio-buffer playback after gesture; unavailable-storage warning. Screenshots reviewed for title, arena and shop. These are automated scenarios and agent visual review, not human user testing.
- Firefox smoke passes with zero captured errors. Native startup runs without errors. No measured sustained 60-FPS claim.
- Files: main.lua/conf.lua; src/core/{util,codec,save}.lua; src/combat/{arena,damage}.lua; src/data/{heroes,reactions,items}.lua; src/run/model.lua; src/render/iso.lua; src/ui/draw.lua; scripts/{build.py,browser-test.cjs}; tests/{run,fixtures}.lua; web/index.html; package.json/lock; assets attribution/licenses; documentation.
- Scope/tuning: later bosses intentionally reuse Ash Bailiff lane, slam and aimed-cinder patterns. Initial shop contains only Blank Scepter, Loaded Die, Spare Ace and Red Flask. Other items/boss designs remain later phases. Geometric actor/card placeholders, orbit visuals, bounded hit sparks and damage breakdown added; aiming over the raised boss silhouette resolves to its ground anchor.
- Build tooling note: npm reports two moderate advisories through love.js -> uuid <11.1.1 (GHSA-w5hq-g745-h8pq). The exporter calls UUID v4 with no buffer; the reported vulnerable v3/v5/v6 buffer APIs are not used here. This is build-only tooling, not a runtime web dependency. No incompatible forced upgrade was applied.
- Known limits: audible quality and independent fresh-player/balance review pending; no hosted itch.io access/test or submission; menus currently require mouse (keyboard menu navigation belongs to Phase 4); remaining settings/content/presentation follow Phases 4–8.
- Exact next action: human-play the demo and record the remaining acceptance observations, then proceed to Phase 4 when authorized.

### 2026-10-12 — Phase 4: UI and player flow checkpoint
- Status: Implementation delivered; automated rule/build checks pass, browser regression in progress; human readability/feel acceptance pending.
- Delivered: keyboard focus for menus/modals, Tab/arrows and Enter activation; animated rarity-framed cards with stats; offer comparisons; settings for volume/mute, reduced motion, shake, large text, fullscreen and action-key rebinding; replayable/skippable help through F1, settings through F2; entry fade and transaction feedback.
- Files: main.lua, src/ui/draw.lua, src/core/settings.lua, src/combat/arena.lua.
- Commands: npm run format, npm test (18 scenarios), npm run build passed. Browser loop running against actual exported artifact.
- Limitations: independent human acceptance remains open; no hosting or audible review claimed.
- Next: implement all catalog items and deterministic effect tests for Phase 5; finish integrated browser verification.

### 2026-10-12 — Phase 5: heroes, reactions and full item catalog
- Status: Implementation delivered; 23 automated scenario groups pass. Human balance acceptance pending.
- Delivered: all 8 weapons, 12 Curios and 3 consumables in deterministic shops; numerical tooltips; centralized equipment modifiers for direct/reaction/periodic damage, both aura orders, healing, shields, stagger, movement, clear gold and maximum HP; bounded effects and valid-use guards.
- Files: src/data/items.lua, src/combat/{arena,equipment}.lua, src/run/model.lua, src/core/save.lua, tests/{content,run,fixtures}.lua.
- Commands: npm run format and npm test passed (23 groups, including all items acquired/saved/equipped, both-order periodic reactions, shield caps, Glass Ticket purchase/sale/reward, dead-owner projectiles).
- Browser finding/fix from Phase 4: love.js can stop on reading a nonexistent settings file; added getInfo guard. Subsequent browser loop advances normally. Native smoke with null audio driver exited via expected timeout 124.
- Final audit: persistent skill fields apply aura only on the first connecting tick. Later ticks cannot react; Thorn Bow, Copper Coil and Green Receipt also boost matching periodic skill damage. Dedicated tests cover this invariant.
- Decisions: item bonuses multiply once per defined event; periodic effects snapshot reaction modifiers, never generate new auras. Glass Ticket changes current HP only by clamping when acquired/sold and does not heal on sale. Existing v1 saves remain supported.
- Next: ten distinct normal and Hell encounters, source-only developer controls, 100-floor Hell simulation; complete browser/UI validation.

### 2026-10-12 — Phase 6: distinct encounters and endless Hell
- Status: Implementation delivered; automated headless and integrated browser checks pass; manual acceptance pending.
- Delivered: the ten catalog bosses, ten Hell variants, unique hazard combinations, phase changes, signaled Sun stances, ring gaps, wind pressure/sweeps, collidable pillars/eruptions, growing/ignited patches, delayed ice shatter, lightning grid corridors, gravity escape/reversal and three-phase Throne. Preview/HUD names and rules match encounters. No full-run Bailiff reuse remains.
- Developer lab: source-only `devtools.lua`, opened with F3; floor/seed/hero/item selection, normal/Hell toggle, invulnerability, 0.5/1/2/4x speed, repeatable fight reset. Lab fights never overwrite saves. Packaging asserts the file is absent from `.love`; browser exports the same archive.
- Tests: 30 groups pass on LuaJIT and Lua 5.5. New checks cover 20 distinct seeded pattern signatures, warning bounds, safe space, phase transitions, ring/sweep geometry, pillar collision, gravity escape, 100 Hell floors at 40 simulated seconds each across phase states, and floor 1,000,000 scaling. The stress test uses invulnerability for hazard lifecycle coverage; the separate 20 encounter victories use actual attack/skill/switch/dodge controls with three Common heroes, no invulnerability or damage cheats. The floor-10 simulation awards the actual Infinity Key and enters Hell.
- Files: src/data/bosses.lua; src/combat/{patterns,arena}.lua; src/render/sprites.lua; src/ui/draw.lua; src/run/model.lua; main.lua; devtools.lua; scripts/{build.py,browser-test.cjs}; tests/{bosses,ui,run,fixtures}.lua; web/index.html; package manifests; README, BUILD_PLAN, GAME_CONTENT and attribution.
- Native source-lab smoke: temporary checkout wrapper opened F3, started a fight, toggled invulnerability and 2x speed, captured screenshots and exited successfully with LAB_SMOKE_OK. Screenshots reviewed; test files remain under /tmp and are not packaged.
- Browser fixes: canvas owns Tab while focused; menu actions queue across redraws so rapid Tab/Enter/Esc cannot activate stale modal buttons; missing optional sprites are checked with getInfo before attempting to load in love.js. Settings/help large-text screenshots inspected by agent. A Lua 5.5 atan2 compatibility difference was fixed.
- Decisions: preserve existing sprites; later boss art remains intentionally geometric for Phase 6. No new asset credits spent. Boss elements identify patterns without imposing hard elemental immunities. HP/speed/hazard limits remain bounded; all warning times are at least 1.05s. The short demo remains the documented two-Bailiff slice.
- Known limits: automated victory and safe-space tests do not replace human encounter clears or prove every possible path/pacing decision. Manual all-20 clears, late-Hell pacing, fresh-player/balance/audio and hosted verification remain open.
- Exact next action: human acceptance review using the encounter lab; Phase 7 remains outside this request.

### 2026-10-12 — Final verification notes (Phase 4–6)
- Headless: 30 scenario groups pass under both LuaJIT and Lua 5.5; formatting and whitespace checks pass.
- Native: normal source startup exits through the expected timeout without errors (null audio driver, so no audible review). The scripted source-only lab smoke exits 0 and exercises start, invulnerability and speed controls; screenshots inspected.
- Build: native and web artifacts reproduce byte-for-byte once input files are stable. Eight directional Bailiff PNGs appeared/changed under `assets/bosses/bailiff/` during this session from work outside this implementation. They were preserved and included by the existing asset packager; gameplay still uses `assets/bosses/bailiff.png`. Do not attribute generation of those new directional files to this phase or claim their provenance was reviewed. Their changes explained an initial checksum mismatch; subsequent consecutive builds matched.
- Focused Chromium checks: keyboard flow, settings, rebinding and all twenty encounter renders pass with no captured console errors. Settings/help and representative wave/pillar/gravity screenshots inspected by agent; these are not human playtests.
- Browser fixture correction: deleting only localStorage before reload was undone by the pagehide save adapter. Clean-profile tests now remove both runtime save files and localStorage before reload; normal save behavior remains unchanged.
- Final Chromium 153.0.8010.12 regression: all 19 groups pass, zero captured errors. Includes original demo/economy/save/audio-start/resize/fullscreen/iframe/storage checks, keyboard menus/settings/rebinding, all twenty boss renders, and a real browser Empty Throne clear with three Common heroes followed by Infinity Key award and Enter Hell. No fight cheat was used in that browser clear.
- Firefox 150.0.2: draft/combat/input/reload smoke passed with zero captured errors on the final package.
- Reports: `.test-results/browser.json`, `.test-results/firefox.json`; images include `boss-1.png` through `boss-20.png`, `settings-large.png`, `help-large.png`, `real-throne-victory.png`. Agent screenshot review is separate from human playtesting.
- Final artifacts: `dist/gate-to-hell.love`, `dist/gate-to-hell-web.zip`, `dist/web`, `dist/SHA256SUMS`. SHA-256: native `1ea9c9b5d60b332e52b0fe060a1c8bf1aa7499478c60383327f8d0e89b6c6ddc`; web ZIP `689b070ee2cf2f913f30491cff307614938aa862ffc8b8908a0b75763ded31d6`.
- Remaining acceptance: manually clear all twenty normal/Hell encounters with cheats off, review early/late Hell pacing and fresh-player readability, and conduct audible/hosted checks. No publication or Phase 7–8 work was performed.

### 2026-10-12 — Requested phase-completion audit
- Verdict: do not mark all phases complete. Detailed evidence and remaining requirements are in `PHASE_AUDIT.md`.
- Fresh verification: 30 scenario groups pass in LuaJIT and Lua 5.5; formatting/whitespace checks pass. Packaged runtime exactly matches source; artifact checksums, browser root entry and exclusion of developer tools/tests verified.
- Prior browser evidence reviewed: Chromium 19 groups and Firefox smoke passed. Browsers were not rerun in this audit; no runtime code changed.
- New finding: Phase 4 element icons are absent despite the plan explicitly requiring icons plus text/color. Existing browser navigation evidence does not cover every keyboard-only management path.
- Unmet gates: independent fresh-player demo acceptance, explicitly manual progression checks, all twenty manual encounter clears, early/late Hell pacing and remaining readability/audio review. Automated and simulated results remain distinct from those requirements.
- Next action: close the Phase 4 implementation/coverage gaps, then record the required human acceptance evidence. No phase gates were waived.

### 2026-10-12 — Phase 7 implementation checkpoint
- Delivered: nine element icons, coherent geometric portrait defaults, synthesized looping music and nine sound cues, persistent music/effects mix, credits, clearer purchase/consumable feedback, bounded reusable spark/label pools.
- Validation: 33 LuaJIT scenario groups pass, including eight naturally funded full ten-floor runs, sustained pool reuse and 60 late-Hell restart/switch stress cases. Default native/web packages build successfully without portrait PNGs. Browser regression follows on final release shell.
- User decision: prepare publication-ready upload files; most assets will be replaced by the user. Preserve existing art but exclude it from default packages. No upload requested.
- Pacing observation: deterministic expert bot clears total combat in 50–51 seconds across ten floors by rapidly cycling skills. This is a lower bound, excludes shopping/learning, and does not establish human run length. Do not claim the initial 20–35-minute target is met. Human balance/audio acceptance remains open.
- Next: Phase 8 release shell, listing/cover/screenshots/replacement guide and final exported-browser verification.

### 2026-10-12 — Phase 7 final verification
- Implementation delivered; human acceptance remains open. 33 scenario groups pass under LuaJIT and Lua 5.5, including eight full normal runs, 60 late-Hell restarts/rapid-switch cases and bounded visual pool reuse. Existing 100-floor stress and 20 simulated encounter clears still pass.
- Chromium 153.0.8010.12: all 19 regression groups pass with no runtime errors, including all20 encounter renders, actual Throne victory, persistence, audio startup, resize/fullscreen, settings, keyboard flow, iframe and denied storage. Firefox 150.0.2 final smoke passes.
- Added keyboard-only management coverage for full-team replacement/confirmation, equip/unequip, item/hero sale/confirmation, inventory and reroll; all pass. Geometric draft, full-team offer, credits and representative Hell screenshots inspected by agent.
- Short foreground floor-five profiling: 180 rAF intervals, median16.7ms / p9516.8ms; JS heap8.6MB and WASM64MiB. Machine: Linux x64, Intel i5-12450HX, headless Chromium/SwiftShader. This limited sample does not prove sustained universal60FPS.
- Native final startup with null audio exits124 at5seconds, no errors. Audible quality is not verified.
- No balance values silently changed. Automated expert combat is much faster than the initial duration target; human pacing remains an explicit open gate.

### 2026-10-12 — Phase 8 upload preparation
- Status: implementation/local release preparation delivered; author art replacement, human acceptance, hosted/jam checks and actual upload remain pending. Nothing published.
- Delivered: version0.8.0, release web shell with loading/failure/fullscreen feedback, default art-free deterministic packaging, exact source/package/license/exclusion verification, upload instructions, listing copy, controls/credits, 630×500 SVG/PNG cover, actual gameplay screenshots and art replacement guide.
- Fresh-context browser release journey: ordinary draft, all ten natural combat victories, earned-gold recruitment/equipment purchases, Infinity Key, Enter Hell, natural defeat and restart. No injected fixture/run, god mode, damage override or extra currency. Team: Madame Match / Flint Rook / Gale Knave. Report `.test-results/release.json`. Music/effects controls persist; credits checked.
- Final builds reproduce byte-for-byte; `python3 scripts/verify-release.py` passes. Default `.love` contains no PNGs; optional `--include-art` includes top-level portraits only after the author enables them. Preserved directional Bailiff files are not shipped or used.
- Artifacts: `dist/gate-to-hell.love`, `dist/gate-to-hell-web.zip`, `dist/SHA256SUMS`, `dist/gate-to-hell-0.8.0-release-kit.zip`. Listing/media/guides in `release/`; native download requires installed LÖVE11.4/11.5.
- Final SHA-256: native `5a655f609e600ea78d571b506de785eb82f3891b2ff99e17b69e5ebbf12036e9`; web `5ef682026affb3c4b924bd8c63b05092d3b1aa256d7b1c233dd583ad1a60e095`.
- User scope: ready for their upload, most assets to be replaced by them. No jam URL/deadline/rules or itch.io project supplied. Hosted test and jam compliance cannot be claimed. Official HTML5 upload guidance checked; source link is in release/UPLOAD_CHECKLIST.md.
- Exact next action: author replaces art following release/ART_REPLACEMENT.md, repeats final checks/media capture, completes release/PLAYTEST_CHECKLIST.md and tests the hosted draft before choosing publication.

### 2026-10-12 — Requested Blender Ash Bailiff refinement (v0.8.1)
- User request: improve existing 2D assets using Blender, make isometric sprite sheets, start with the boss. This authorizes the Bailiff atlas in the default game; other portraits remain excluded.
- Source inspected: `assets/bosses/bailiff.png`, older 128px eight-direction sheets, and the live Blender model `/tmp/opencode/bailiff.blend`. Saved an untouched working snapshot at `art-src/blender/bailiff-original.blend`; the original portrait/sheets are preserved.
- Refined source: `art-src/blender/bailiff-isometric.blend`, with layered beveled charcoal armor, bronze edges, hollow hood, ember mask, molten chest seal and new idle/attack/walk/hurt/death actions. These are actual 3D geometry, not rotated image planes. Modeling/render pipeline in `scripts/blender/`.
- Export: eight transparent 2048×1280 PNG atlases under `assets/bosses/bailiff_iso/`, each40 frames of256×256. Fixed ground anchor128,204; orthographic45° azimuth /30° elevation matches the game's2:1 diamond. JSON and runtime Lua metadata declare linear animation offsets. `preview.html` inspects the real sheets.
- Integration: normal/demo/Infernal Bailiff face the player; idle/attack/hurt/death render with a two-direction texture cache. Attack impact follows the hazard warning; victory plays a1second death sequence before a single reward, skipped in reduced motion. Walk is exported but this stationary boss does not walk. Remaining heroes/bosses retain previous rendering.
- Validation/results: see final notes below after export/browser checks. No full phase acceptance or human art approval inferred from these checks.

#### Blender refinement — final verification and deliverables
- All eight sheets /320 frames passed `python3 scripts/verify-bailiff.py`: correct2048×1280 RGBA atlases, animated frame variation, matching anchor128,204, no clipping; minimum transparent margin20px.
- `npm test` and `lua tests/run.lua`: all35 scenario groups pass; `npm run format:check` passes.
- `node scripts/browser-test.cjs --bailiff-only`: Chromium153.0.8010.12 uploads actual2048×1280 textures to WebGL, renders idle/cast/player-facing/Infernal Bailiff, keeps at most2 resident sheet textures, and completes death/victory with exactly1 reward. No captured runtime errors. Report `.test-results/bailiff-browser.json`.
- Final Firefox150.0.2 draft/combat/reload smoke passed with the new atlas build and no captured errors. Agent inspected in-game idle/death, animation contact images and the live Blender source; human art acceptance remains separate.
- `npm run build` and `python3 scripts/verify-release.py` pass. Default package policy is now a precise whitelist of8 Bailiff sheets plusJSON, runtime code/licenses; other portraits, the old directional files, .blend/raw frames and test/preview tools remain excluded.
- Asset/editing kit: `dist/ash-bailiff-isometric-assets.zip` includes all8 sheets, JSON/Lua metadata, animation viewer/previews, refined .blend, original source snapshot/reference and reproducible modeling/rendering scripts. `assets/bosses/bailiff_iso/preview.html` previews the sheets; `turnaround.png` and `idle-preview.webp` show directions/animation.
- Updated game artifacts: `dist/gate-to-hell.love` and `dist/gate-to-hell-web.zip` (v0.8.1). Native SHA256 `17771d40a040af432e1f7000ff0930d359dd329fd94aa0141c76a0ab8b3c4fea`; web `07a0ada4a42c71927f49ad130c7dfe7cff5caa8b43c21cbf80b337c816e424f5`.
- Earlier v0.8.0 full release-journey/19-group browser evidence is historical; focused asset tests and Firefox above are current. No new human playtest or publication claim.
- Next: author reviews the boss style; apply the same Blender pipeline to other characters when requested.

### UI icons, overview guide and elemental particle polish

- Added 24 Blender symbols with existing animated coin/key icons and item/element medallions. Menu actions, resource prices, the persistent gold counter, hero health/attack/skill stats, party shields/cooldowns, equipment and combat supplies now carry icons alongside text.
- Replaced the old control list with four F1/How to Play pages: run overview, combat, elements/reactions, team/shop. Controls follow saved key bindings, including large-text mode. Closing the guide retains tutorial settings; explicitly selecting “Got it / skip prompts” disables prompts.
- Added twelve rendered frames for each of nine elements, including distinct flame, ripple, wind, stone, leaf, ice, lightning, orbit and fracture geometry. Connected to semantic elemental casts/hits, boss impacts, projectiles and persistent fields, without changing damage, cooldowns, collision or combat RNG. Reduced motion uses a fixed dimmed frame. Existing bounded feedback records carry the cosmetic element ID; texture cache is restricted to nine valid sheets.
- Editable source: `art-src/blender/element-effects.blend`; generator: `scripts/blender/build_polish.py`; local animation viewer: `assets/effects/preview.html`. Source/reference/preview files remain outside runtime archives.
- Verification: 45 Lua scenario groups; nine actual particle WebGL uploads during live skills; all four guide pages at standard/large text; reduced motion, pause, shop and offer rendering. `scripts/verify-polish.py` checks 108 distinct RGBA animation cells and transparent borders; release verification checks exact current source/asset archive contents. Focused report `.test-results/polish-browser.json`.
- Broader packaged browser UI regression also passed: keyboard-only draft/preview/pause, rebinding, large text, all 20 normal/Hell encounter screens, Empty Throne → Infinity Key → Hell, iframe loading and unavailable-storage reporting. Native SDL launch ran for the five-second smoke interval without an application error. Final native/web builds pass exact release verification.

### 2026-10-12 — Complete missing visual artwork with Blender

- Read the README asset checklist and completed its visual tasks: nine base bosses, ten Hell costumes, four extra Throne phase appearances (184 directional sheets / 7,360 frames), 91 dedicated combat effect sheets (728 frames), ten arena props and four screen illustrations. Existing heroes/UI/floors and normal Bailiff preserved. Authored audio remains open. No DreamLayer/API key used.
- Integrated boss selection, stagger/recovery/death timing, phase costumes, portraits, all skill/reaction/status/consumable art, masked hazard artwork and props. Existing combat rules/RNG are preserved; procedural fallbacks and bounded texture caches remain.
- Original editable geometry/animation libraries in `art-src/blender/`; generators and source verifiers in `scripts/blender/`. Offline gallery: `assets/art-preview.html`. Delivery/rebuild instructions: `ART_DELIVERY.md`. New cover: `release/cover-blender.png`.
- Final full image checks pass all 23 appearances, 91 effect sheets, alpha borders, frame variation and scenery. Blender source libraries reopen and validate. All 49 Lua scenario groups, formatting and exact source/archive/checksum checks pass. Web loader/build memory increased from 64 to 256 MiB for the expanded asset library.
- Current downloads: `dist/gate-to-hell.love`, `dist/gate-to-hell-web.zip`, and editable asset kit `dist/gate-to-hell-blender-art.zip`. Human art/audio acceptance, playtesting and hosted upload remain separate; nothing published.
- Final Chromium art checks pass all 20 fights, 18 skills, reduced motion, pause, new screen illustrations and all Throne costumes in the gallery with real texture uploads and no captured errors. Current media: `release/screenshots/art-*.png`. Report: `.test-results/missing-art-browser.json`. Native five-second startup passed with expected timeout 124.
- Firefox 150.0.2 final draft/combat/input/persistence smoke passes with no captured errors.
- Focused Chromium finale check passes live Empty Throne phases/death, Infinity Key and Hell entry without captured errors (`.test-results/art-finale.json`).

### Tactical balance + Run Info

Added floor-3 guard/resistance, reaction/stagger/cast openings, shared basic/dodge
recovery and a 1.25s switch commitment (death switches bypass it). Increased depth
scaling again and made floor-5 pursuit occur every cast. Current formula and
player-facing rules are in README.md. Three-hero camping now loses against late
bosses; ordinary avoidance controls still clear full runs. Added route previews
with boss portraits/hints/resistance to Run Info and removed the persistent Done
success message. Verified 55 Lua scenarios, Chromium --tactics-only, formatting,
and release package verification. New packages are in dist/; nothing published.
