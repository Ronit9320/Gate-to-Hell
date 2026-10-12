# Phase 0–8 status — v0.8.1

Updated 2026-10-12. **Implementation and local release preparation are delivered through Phase 8. Full human acceptance is not signed off.** The user requested upload-ready files with most assets left for their replacement; default packages now include the author-approved Blender Ash Bailiff atlases, while other portrait PNGs stay excluded. No publication was requested or performed.

| Phase | Current evidence | Remaining acceptance |
| --- | --- | --- |
| 0 | Native startup; Chromium/Firefox runtime, audio-start, persistence, fullscreen, local iframe | Audible review and hosted iframe |
| 1 | Live combat, movement, dodge, switching/death, bounded hazards/effects | Human feel/readability |
| 2 | Two-fight browser demo; every starter wins opening simulation | Independent fresh-player test |
| 3 | Transactions/save tests; actual browser full normal run, Hell, natural loss and restart | Explicit manual player review |
| 4 | Nine element icons now implemented; keyboard-only replacement, equip/unequip, item/hero sales, inventory and reroll now pass; settings/help/credits | Human readability at supported sizes |
| 5 | All 18 heroes, 81 elemental pairs and 23 items; full-run simulations from four Commons and four higher-rarity starters | Human balance |
| 6 | Ten normal and ten Hell encounters; 20 bot clears, 100-floor bounded stress, real browser floor-10 victory | All twenty manual clears and early/late Hell pacing |
| 7 | Synthesized music/9 SFX, mix settings, consistent geometric defaults, effect pools, full-run/restart stress, browser profiling | Human pacing/audio; no 20–35-minute duration claim |
| 8 | Reproducible native/browser packages; listing, cover, screenshots, credits, upload and art replacement guides; clean-profile full release journey | Final author artwork; human checklist; hosted verification and jam compliance; author upload |

## Final automated evidence

- 33 headless scenario groups pass on LuaJIT and Lua 5.5; formatting passes.
- Chromium 153.0.8010.12: 19 regression groups, full release journey, keyboard management; no captured runtime errors. Final Firefox 150.0.2 draft/combat/reload smoke passes.
- Release journey starts without a save or injected fixtures, buys with earned gold, clears floors 1–10, enters Hell, naturally loses, and restarts. Its three-hero team was Madame Match / Flint Rook / Gale Knave; combat time was 48.68 simulated seconds. This fast automated control sequence does not establish human pacing.
- The separate keyboard-management test uses a valid stocked-shop fixture to reach capacity-sensitive transactions. The all-20 render check also uses boundary fixtures. These are not fresh-profile natural runs.
- Eight deterministic bot runs total 50–51 seconds of combat; no injected gold, HP or damage in those runs. Stress tests explicitly use invulnerability to exercise bounded lifecycles.
- A short 180-frame floor-five sample measured median 16.7 ms, p95 16.8 ms, ~8.6 MB JS heap, 64 MiB WASM memory on Linux x64 / Intel i5-12450HX / headless Chromium with SwiftShader. This is a short automated sample, not sustained hardware-GPU or universal 60-FPS evidence.
- Default archives match source exactly, include licenses and browser dependencies, exclude other portrait PNGs/debug tools/tests/saves, and reproduce byte-for-byte. Native startup with null audio exits by expected timeout with no errors.

Use `release/PLAYTEST_CHECKLIST.md` to close the human gates. The historical audit below is retained to show which omissions were subsequently fixed; its “missing icons” and “not started” observations are superseded by the table above.

---

# Historical Phase 0–6 completion audit

Date: 2026-10-12. Scope: verify the existing implementation against BUILD_PLAN.md, not redefine its exit gates.

**Verdict: implementation is broadly present through Phase 6, but all phases cannot be signed off as complete.** Automated results do not satisfy explicitly required fresh-player/manual acceptance. Phase 4 also has an identifiable implementation omission.

| Phase | Verified evidence | Remaining requirement / verdict |
| --- | --- | --- |
| 0 — Runtime/browser proof | Pinned runtimes; package entry points and checksums valid; prior Chromium audio-start/input/storage/fullscreen/iframe checks pass. | Technical evidence passes. Audible-quality review remains unrecorded; unavailable hosted verification is explicitly allowed to remain pending by this gate. |
| 1 — Combat foundation | Live browser combat evidence; projection round trips; cooldown/state preservation; automatic death switching; defeat/restart; collision and dodge tests. | Core technical checks pass. Existing resized-browser check exercises menus rather than proving every combat telegraph at each size; visual alignment/feel acceptance remains limited. |
| 2 — First playable | Browser demo completes with recruitment; all 18 starters win solo simulations; seeded rarity/distinctness, team limits and atomic transactions pass. | **Not signed off:** no independent fresh player has completed the loop and demonstrated understanding of switching/reactions. |
| 3 — Progression/management | Thirty-floor progression and save tests; prior browser Finish, Continue, Hell, defeat, inventory, insufficient-gold and reload scenarios pass. | **Not signed off:** these are automated browser scenarios; the explicitly requested manual browser acceptance is not recorded. |
| 4 — UI/player flow | Shared keyboard focus, queued input, settings, rebinding, help, card styling, comparison text, large text and reduced motion exist. Browser evidence covers a subset of menu paths and selected screenshots. | **Incomplete:** dedicated element icons required by the plan are absent; cards/HUD use element text/color. Complete keyboard-only shop/equipment/replacement/sale paths and exhaustive critical-text/readability checks are not demonstrated by the current browser suite. |
| 5 — Heroes/reactions/items | 18 kits; 81 ordered pairs; 8 weapons, 12 Curios and 3 consumables; acquisition, modifiers, periodic/nonrecursive events, caps, ownership and save tests; all heroes/items selectable through the source lab. | Core technical checks pass. Human balancing is not established. Starter evidence proves opening-floor viability, not full-run viability for every starter; broad full-run balance testing also belongs to Phase 7. |
| 6 — Bosses/Hell | Ten normal and ten Hell identities/pattern configurations; bounded warnings/effects; source-only lab; 20 simulated combat victories; 100 Hell-floor stress cases; actual browser Throne clear awards the Infinity Key and enters Hell. | **Not signed off:** no manual clears of all twenty encounters and no manual early/late Hell pacing review. The 100-floor stress test uses invulnerability and scripted HP transitions; it proves bounded simulation, not 100 natural victories or human pacing. |

## Checks performed during this audit

- `npm test`: all 30 scenario groups passed under LuaJIT.
- `lua tests/run.lua`: all 30 groups passed under Lua 5.5.
- `npm run format:check` and `git diff --check`: passed.
- Compared `main.lua`, `conf.lua` and every `src/**/*.lua` file with the packaged `.love`: no mismatches.
- Confirmed `devtools.lua` and tests are absent from `.love`; browser ZIP has root `index.html`, matching `web/index.html`.
- Recomputed both artifact hashes: match `dist/SHA256SUMS`.
- Reviewed existing browser reports from the preceding implementation run: Chromium 153.0.8010.12, 19 scenario groups, zero captured errors; Firefox 150.0.2 combat/input/reload smoke, zero captured errors. **Browsers were not rerun for this audit.** No runtime code changed during the audit.

## Concrete work before full sign-off

1. Add the Phase 4 element icons and verify them alongside text/color.
2. Exercise every management path using keyboard only, including full-team replacement, equipment, sales, inventory and confirmations. Check standard/large text at supported viewport sizes, including combat telegraphs and full-team offer layout.
3. Record independent fresh-player completion of the demo and manual progression/save/economy acceptance.
4. Manually defeat each of the ten normal and ten Hell encounters with cheats off, then assess early and late Hell pacing and safe-route readability.
5. Record audible review; keep hosted testing explicitly pending until hosting is available.

Geometric boss art is permitted at this stage; final art/music and release publication are not Phase 6 completion requirements. No acceptance criteria were relaxed and no missing manual evidence was inferred from automated tests.

## Blender asset follow-up — v0.8.1

The author requested improved Blender isometric boss sheets. The Ash Bailiff now has eight directional256px atlases, five animations and a fixed ground anchor, made by refining the existing supplied rig with actual3D geometry and new actions. A small viewer and editable Blender source accompany the export. Runtime integration covers facing, idle/cast/hurt/death and bounded texture caching; other characters are unchanged.

Two new scenario groups cover facing orientation, packed frame addressing, one-shot clamping, reduced motion and two-sheet cache eviction. Final asset/frame/browser validation is recorded in the handoff. Older v0.8.0 full-run/browser evidence remains historical; newer focused tests verify the asset change.

Final Blender follow-up evidence:35 LuaJIT/Lua5.5 scenario groups pass. All320 frames have RGBA alpha, correct atlas dimensions, animation variation and at least20px unclipped margin. Current Chromium confirms real GPU atlas uploads, facing/cast/Hell rendering, ≤2 resident sheets and exactly1 reward after death. Current Firefox smoke passes. See HANDOFF.md for exact artifact paths/hashes and the distinction from older v0.8.0 full-run evidence.

## Post-release combat refinement — v0.9.0

Seven melee kits, finite ranged magazines/reloads, stronger boss HP/damage and Bailiff smash, bounded attack/hit/shockwave FX, hitstop, impact frames, stable HUD and accessibility settings implemented. Current checks: 41 LuaJIT scenarios and focused Chromium combat rendering/input check pass; native/web artifacts rebuilt. Browser journey scripts now approach melee range, but the full journeys have not been rerun with current combat. Historical stationary ranged victories do not establish current browser journey acceptance. Human feel, pacing and audible review remain open.

## Isometric hero artwork follow-up — v0.9.0

All 18 heroes now have actual articulated Blender models inspired by their
preserved flat portraits, seven animation states and eight directions. The
6,048 frames are integrated into combat; isometric portraits appear on cards.
Visual event state stays outside saves/RNG, GPU residency is bounded at four
hero sheets, and reduced motion selects static idle/fallen poses. Fallen
teammates remain visible during automatic switching; final defeat displays a
0.75s collapse animation before the results screen.

Current verification: 44 LuaJIT scenarios; 144 atlas/6,048 frame validation with
RGBA, distinct poses/directions and minimum 20px alpha margin; Chromium real
WebGL/input/render checks for every hero and reduced-motion/death/switching
behavior; offline preview controls; formatting; exact native/browser package
and checksum verification. These automated art checks do not close the existing
human playtest, balancing or jam/hosting acceptance gates. See HANDOFF.md for
editable source, viewers, screenshots and exact commands.
