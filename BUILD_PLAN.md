# Build plan — Gate to Hell

## Purpose and status

Build a complete, single-player roguelike boss battler in **LÖVE 2D and Lua**, playable in a browser on itch.io. This document is the implementation roadmap. Phases 0–6 now have a playable implementation; acceptance evidence and remaining checks are recorded in HANDOFF.md. Source: `README.md` and the user's decisions on 2026-10-11. The README summarizes the current confirmed design.

**After every phase, update `HANDOFF.md` before starting the next phase.** Record actual changes, checks, problems, decisions, and the exact next step. A phase is complete only when its acceptance criteria pass; record incomplete or blocked work honestly.

## Confirmed requirements

- Real-time, isometric boss arenas. Control one hero at a time and switch instantly; the other owned heroes stay off-field (up to two).
- Generate four distinct offers from the full hero roster and choose **one free starter**. Each offer rolls 65% Common, 25% Uncommon, 8% Rare, or 2% Legendary, then selects an unoffered hero of that rarity. Recruit up to two more heroes in shops.
- Own at most **three heroes total**, including off-field heroes. No reserve roster that bypasses this limit.
- Buy and sell heroes, and buy weapons and buffs between floors; team building should have the appeal of Balatro's Joker management.
- Elements: Pyro, Hydro, Anemo, Geo, Dendro, Cryo, Electro, Gravity, and Antimatter. Gravity and Antimatter heroes are Legendary only.
- Four hero rarities: Common, Uncommon, Rare, Legendary. Named variants with different play styles.
- Ten floors with distinct elemental bosses. Clear floor 10 to receive the Infinity Key and optionally continue into endless, increasingly difficult Hell floors.
- Visible numerical damage and elemental reactions.
- Balatro-inspired card management, typography hierarchy, animated feedback, and shop presentation, followed by an explicit transition into the floor arena. Use original names, layouts, art, and audio.
- First playable build uses placeholders for heroes, bosses, scenery, and cards. Small effects and particles can already be implemented.
- Deliver a functional run loop, progression, presentation, settings, onboarding, and a tested itch.io web package.

## Accepted gameplay rules and tunable balance

The user accepted the recommended ruleset, with the one-hero randomized draft amendment. Names and gameplay direction are settled for the first playable. Exact stats, prices, cooldowns, and shop weights remain tunable; the starting-draft probabilities were explicitly confirmed. Record balance changes in the handoff.

### Run flow and controls

Title / Continue / Settings / Credits → draft one hero from four offers → floor preview → Enter Floor → fight → rewards → shop / manage team → next preview. Floor 10 rewards include the Infinity Key and a victory screen with **Finish Run** or **Enter Hell**; entering Hell goes through the floor-10 shop. Every Hell clear also awards rewards and a shop visit. Defeat shows statistics and Restart / Title.

- WASD or arrows: screen-relative movement; mouse: aim; left click: basic attack; right click or E: elemental skill; Space: dodge; 1/2/3: switch hero; Esc: pause. Offer rebinding and keyboard-accessible menus. Desktop browsers are the first release target; touch controls and gamepad support are optional later work.
- One basic attack, one skill, and one passive per hero. Basic attacks are low-damage neutral attacks; skills apply elements. Exceptions must be explicit in content data. Off-field heroes retain their own HP and equipment; cooldowns continue while combat runs, but they do not attack or heal automatically.
- Switching is immediate at the same valid arena position; it does not reset attacks, cooldowns, debuffs, or grant invulnerability. Cancel the outgoing attack's uncommitted windup. Already spawned projectiles remain and retain their original owner's damage context.
- A defeated hero is unavailable until the floor ends; automatically switch to a living hero. No living owned heroes means run over, even with only one or two recruited. Pause and loss of focus freeze combat timers. No selling, shopping, or equipment changes in combat.
- On victory, revive and fully heal the team. This is the initial pacing rule; damage avoidance still matters within each fight. No persistent stat grind is required between runs.
- Boss attacks have visible windup, active, and recovery states. Collision and dodge invulnerability must agree with the telegraphs. Bosses must remain beatable with every offered starting hero, including a Common solo starter; no mandatory elemental immunity counter.

### Damage and reactions

- Use a central damage pipeline: base damage → additive bonuses → multiplicative bonuses → reaction modifier → resistance → rounded final damage. Clamp values and display the actual HP damage; shields show separate absorption numbers. Define modifier ordering in code and tooltips.
- Start with one elemental aura per target, a configurable expiration time, and a data-driven incoming-element/aura table. A reaction consumes the aura; no matching rule replaces it with the incoming aura; same-element applications refresh it. Neutral attacks do not consume it.
- Core examples (full coverage in `GAME_CONTENT.md`): Pyro + Hydro = **Steam Burst** (bonus damage); Anemo + an existing basic aura = **Crosswind** (bonus hit); Geo + an existing basic aura = **Gilded Guard** (player shield).
- Full rules: Pyro + Cryo = **Thaw** (burst); Hydro + Cryo = **Frostbind** (boss stagger buildup); Hydro + Electro = **Live Wire** (damage over time); Pyro + Electro = **Flashover** (explosion); Dendro + Pyro = **Kindling** (burn); Dendro + Hydro = **Bloom** (delayed burst); Dendro + Electro = **Overgrowth** (skill damage vulnerability).
- Define the exact ordered pair matrix, damage coefficients, aura lifetime, refresh/stack rules, and status caps in Phase 2; harden and tune them in Phase 5. See `GAME_CONTENT.md` for exact pair coverage. Pairs above should work in either order unless clearly described otherwise. Remaining pairs do no reaction, without errors or hidden multipliers.
- Gravity combines with a basic aura for **Collapse**, increasing stagger and damage; Antimatter combines with other elements except Gravity for **Annihilation**, a bounded burst. These pairs work in either order as specified in the catalog. Gravity + Antimatter triggers **Event Horizon** with an internal cooldown. Legendary effects must not create recursive hits or infinite reaction loops.
- Boss crowd control uses a stagger meter and recovery immunity rather than permanent freeze/stun. Damage-over-time ticks and triggered hits do not apply new auras by default. Keep damage ownership and trigger provenance explicit.
- Damage numbers use element color plus labels/icons; show reaction names and a compact readable damage breakdown. Particles must not obscure enemy telegraphs.

### Team economy and equipment

- Three hero slots maximum at all times. A full roster cannot directly buy a fourth hero: allow an explicit atomic replacement showing sale value, purchase cost, returned equipment, and resulting gold before commitment. Cancel leaves everything unchanged.
- Allow selling down to one hero; block selling the last hero. Buying an identical named variant already owned is blocked initially. Distinct variants of the same element are allowed.
- Heroes carry one weapon each. Start with three team-wide **Curio** slots for passive Joker-like buffs, plus two consumable slots. These item slots do not increase hero capacity. Unequipped weapons have a six-slot inventory; block transactions that cannot safely return equipment.
- Selling a hero returns their weapon to inventory. Equipment swapping and replacing items are explicit, with no silent destruction. Buy, sell, reroll, and replacement transactions are atomic.
- Initial tuning: 10 starting gold, 8 + floor gold per clear, Common/Uncommon/Rare/Legendary hero prices 8/14/22/35, purchased-hero resale at half actual purchase price rounded down (free starter resale is zero), rerolls starting at 2 and increasing by 1 within the current shop. These are tuning seeds.
- Each shop offers two heroes, one weapon, one Curio, and one consumable; allow rerolls and item inspection. Sold stock does not instantly refill. Reroll price resets next floor. Seed the shop separately from combat effects and the starting draft. The first shop guarantees an unowned Common at 8 gold so recruiting a second hero is affordable after the first clear.
- Proposed hero rarity weights: floors 1–3: 75/23/2/0; 4–6: 50/35/14/1; 7–10: 30/40/25/5; Hell: 20/35/35/10. Floor-10 shop guarantees one affordable unowned Legendary offer by awarding sufficient bonus gold. All tables and prices live in data.
- Consumables are usable in combat with clear bindings and limits; effects such as healing, shielding, and cooldown recovery must not bypass death or progression rules.

## Content catalog

`GAME_CONTENT.md` is the source of truth for all 18 heroes, nine elements, four rarities, 10 bosses and Hell variants, weapons, Curios, consumables, reactions, and draft/shop acquisition rules. Update that file when content changes rather than maintaining duplicate rosters here. The first playable now includes all 18 functional placeholder hero kits because any of them can appear in the starting draft.

## Presentation and architecture

The management screen is a moody card table: floor/currency/run information in a persistent rail, three prominent hero slots (one occupied initially), readable rarity borders, equipment and Curio rows, and a clear Enter Floor button. The preview shows boss element, special rule, and reward. Shops use the same visual language. Arena transitions reveal an isometric stage while retaining a compact three-card combat HUD with active hero, individual HP, cooldowns, and switch keys.

Use a logical 1280×720 canvas, aspect-preserving scaling, matching input coordinate conversion, and responsive letterboxing. Isometric projection is a rendering concern: keep movement/collision in world coordinates, invert projection for aiming, sort by ground depth, and anchor telegraphs to the ground. No platforming or complex elevation is needed. Placeholder silhouettes must differ by shape, label, and element; use animation, particles, brief hit stop, floating numbers, and optional screen shake for feel.

Suggested structure (create during implementation):

```text
main.lua, conf.lua
src/core/       state machine, input, settings, RNG, save schema, audio
src/states/     title, starter selection, preview, arena, rewards, shop, results
src/combat/     movement, collision, attacks, damage, auras, status, boss patterns
src/run/        team, inventory, economy, floor progression, Hell scaling
src/data/       heroes, bosses, items, reactions, balance tables
src/ui/         cards, buttons, tooltips, focus navigation, layouts
src/render/     camera, isometric transforms, particles, placeholder art
assets/         eventual art, fonts, audio, license records
tests/          headless Lua rule tests and scenario fixtures
scripts/        repeatable native/web packaging and validation
web/            browser shell and loading/error UI
```

Keep combat/economy/progression logic testable without rendering. Use stable content IDs, seeded RNG with separate streams for shops, encounters, and visuals, bounded event processing, and a versioned save schema. Avoid native extensions and runtime network dependencies. Test the actual browser Lua runtime; do not assume desktop LuaJIT behavior is portable.

## Build phases and acceptance gates

Phases are sequential. Each phase ends with a runnable checkpoint where applicable and a `HANDOFF.md` update. Fix a failed gate before declaring completion. No calendar estimates until the jam deadline, available time, and asset budget are known.

### Phase 0 — Runtime and browser proof

- Create the LÖVE skeleton, configuration, basic logging, logical canvas, and repository run/build instructions.
- Select and pin compatible native LÖVE and love.js versions. Start by evaluating LÖVE 11.5 and love.js compatibility mode; record exact versions and commands after successful verification.
- Build a tiny input/shape/audio/settings persistence demo. Produce a `.love` archive and an HTML5 ZIP with `index.html` at its root. Serve locally over HTTP and test embedded behavior; actual itch.io testing requires project access.
- Verify keyboard focus, mouse coordinate mapping, resizing/fullscreen, user-gesture audio startup, pause on blur, and save reload. Record browser/version and console errors. Pick the exporter mode based on evidence, including audio behavior.
- **Exit:** repeatable native and browser builds; input, sound, and storage tested, with any unavailable hosting check explicitly pending. Do not defer an exporter incompatibility to release week.

### Phase 1 — Real-time isometric combat foundation

- Implement screen-relative movement, mouse aiming, arena boundaries, collisions, dodge, attack/skill cooldowns, HP, death, and pause.
- Implement one-hero and multi-hero development fixtures, off-field state, switching, and one telegraphed test boss with projectiles and hazards.
- Establish the state machine and minimal HUD; keep input consumption consistent between menus and arena.
- **Exit:** playable browser fight; switching preserves per-hero state, one defeated hero auto-switches, all defeated produces a restartable loss, and attacks align with telegraphs across canvas sizes.

### Phase 2 — Placeholder vertical slice / first playable

- Implement the four-offer weighted draft across all 18 functional placeholder hero kits and all nine elements. Choose one free starter; display two empty recruitment slots. Include all reaction rules needed by those kits, with visible damage numbers. This is a deliberate expansion of Phase 2 to honor the full-roster draft.
- Complete a short loop: title → draft → preview → solo Ash Bailiff → reward → basic shop/recruitment → stronger Ash Bailiff rematch → demo-complete screen. Support defeat/restart throughout; label repeated content as a development slice.
- Support buy, sell, and atomic hero replacement; add Blank Scepter, Loaded Die, Spare Ace, Red Flask, and floor/currency UI. Teach switching after recruitment, not while only one hero is owned.
- Use only placeholder large assets, plus small effects and particles. Validate combat feel before commissioning final art.
- **Exit:** a fresh player completes the loop in a web build, can recruit and understand switching/reactions, and can never exceed three owned heroes. Every possible starter can defeat floor 1 alone; four draft cards are always distinct and rarity generation is covered by deterministic tests. Reward and purchase actions cannot be duplicated by repeated clicks.

### Phase 3 — Complete run structure and management

- Build the ten-floor progression scaffold, floor previews, reward accounting, inventory, complete shop transaction rules, rarity tables, rerolls, and equipment management.
- Add the floor-10 victory choice, Infinity Key, Hell cycle scaffold, results statistics, restart, and deterministic run seeds. Temporary boss reuse is allowed here and must be labeled in the handoff.
- Save at safe boundaries (before entering a floor and after rewards/transactions). Reloading mid-fight restarts that encounter from the saved entry state; prevent duplicate rewards. Persist RNG state and stock so reload does not freely reroll shops.
- Handle absent/corrupt/version-mismatched saves and unavailable browser storage gracefully. Warn before replacing an existing run.
- **Exit:** an automated progression scenario traverses floors 1–10 and two Hell cycles; manual browser checks cover Finish Run, Continue, defeat, inventory full, insufficient gold, and reload integrity.

### Phase 4 — Balatro-inspired UI and complete player flow

- Build reusable animated cards, card inspection, rarity styling, stat comparisons, shop layout, boss preview, transition into the isometric floor, and compact combat HUD.
- Add tutorial prompts for movement, dodge, skills, switching, reactions, and the first purchase. Allow skipping and replaying help.
- Complete settings: audio levels/mute, controls, reduced motion, screen shake, readable UI scale, and fullscreen where supported. Use element icons and text as well as colors.
- **Exit:** all actions have visible feedback and keyboard focus; no clipped critical text at tested sizes; full menus are navigable without a mouse; reduced motion keeps combat readable. Maintain placeholder art until the full loop is stable.

### Phase 5 — Full hero roster and reaction system

- Harden and balance the 18 hero variants, nine elements, reaction matrix, legendary restrictions, skills/passives, and descriptions first made functional in Phase 2.
- Implement all 8 weapons, 12 Curios, and 3 consumables with bounded stacking and explicit event trigger rules.
- Add deterministic rule tests for ordered reactions, damage modifiers, aura expiry, off-field cooldowns, death/switch races, ownership, and recursion prevention.
- **Exit:** every hero and item can be obtained and exercised via development tools; all documented effects work; pair-matrix and economy invariants pass. No starting hero needs a specific rare drop to progress.

### Phase 6 — Ten distinct bosses and endless Hell

- Replace all reused encounters with the ten named bosses, unique attack patterns, elemental identity, and phase transitions.
- Add all ten Hell variants and bounded scaling/modifiers. Introduce new combinations gradually and maintain safe paths.
- Build developer encounter selection, seeded reproduction, invulnerability toggle, and speed controls; disable cheats in release builds.
- **Exit:** manually beat every normal boss and every Hell variant; simulate at least 100 Hell floors for numeric/scaling failures; manually test early and late Hell pacing. Verify the Infinity Key flow through the real floor-10 fight.

### Phase 7 — Balance, audiovisual finish, and reliability

- Tune time-to-kill, incoming damage, cooldowns, reaction value, economy, rarity, and switch-heavy team synergies from playthroughs. Initial target: a normal run takes roughly 20–35 minutes; revise using evidence.
- Add coherent original or licensed visuals, UI polish, music, and sound effects. Replace large placeholder assets where feasible; consistent intentional geometric art is acceptable if readable and release-ready. Track attribution and asset licenses.
- Pool effects, cap projectiles/particles/damage labels, and profile representative browsers. Initial target: smooth 60 FPS at 1280×720 on a documented test machine; record frame-time and memory observations rather than claiming universal performance.
- Complete settings persistence, loading/failure UI, credits, tutorial clarity, and bug triage. Test browser refresh, background tabs, resize, rapid switching, repeated restarts, long Hell sessions, and storage failure.
- **Exit:** solo opening fights succeed with every possible starter and full runs succeed from each of the four Common starts, plus representative higher-rarity starts; no known progression blockers or reproducible crashes; counters/effects remain bounded; Chromium and Firefox smoke passes recorded, with other browser support stated accurately.

Phase 7 observation (2026-10-12): eight expert-bot normal runs clear total combat in 50–51 seconds, excluding menu time; human duration is not established. Keep pacing as an open human acceptance item instead of advertising the initial 20–35-minute estimate. User-directed presentation for release is geometric placeholders, with portrait PNGs excluded pending replacement.

### Phase 8 — Release package and itch.io submission readiness

- Produce a clean reproducible `.love` and browser ZIP using documented commands and pinned tooling. Include required runtime files and licenses; exclude debug tools, tests, local saves, and repository internals.
- Verify root `index.html`, relative case-correct paths, no external asset dependency, loader feedback, and controls/audio/storage in the hosted iframe when access is available.
- Prepare title, concise description, controls, credits, screenshots, cover image, browser limitations, version number, and jam-specific compliance notes. Confirm the actual jam URL/deadline/rules before submission; do not invent them.
- Play a release build from a clean browser profile through normal victory, then enter Hell, lose, and restart. Record artifact paths and checksums.
- **Exit:** downloadable package and listing materials are ready; hosted verification and actual upload/submission are separately recorded. If account access or publication authorization is missing, mark that step pending rather than claiming submission.

Release scope clarification (2026-10-12): the user requests a publication-ready package, with most assets to be replaced by them. Prepare files and listing materials; actual publication is not requested. Existing manual acceptance gates remain recorded, not silently waived.

## Validation strategy and completion definition

Use focused headless Lua tests for progression, transactions, inventory capacity, three-hero cap, damage math, reaction ordering, save migrations, and seeded generation. Use integrated scenarios for victory/reward ordering, hero defeat during a switch, and reload boundaries. UI feel, telegraphs, audio, and isometric alignment require real playtesting; test the browser artifact throughout development, not only native LÖVE.

The game is functionally complete when all required phases pass, all specified content exists, a fresh browser player can learn the controls and finish ten floors, shops and team management work without exploits that break progression, Hell can continue with bounded complexity, loss/restart/save/settings work, and release artifacts and attribution are prepared. Optional work must not displace these requirements: multiplayer, mobile touch, gamepad support, daily challenges, achievements, leaderboards, permanent progression, and procedural level geometry are outside the initial scope.

## Browser build references and remaining information

Verified documentation on 2026-10-11: [love.js upstream](https://github.com/Davidobot/love.js) documents a compatibility-mode exporter and notes differences in threading, headers, and audio; this plan requires a runtime spike before committing to an export mode. [itch.io HTML5 documentation](https://itch.io/docs/creators/html5) requires a ZIP containing the entry-point `index.html` and game files. Use those primary sources when implementing; the pinned runtime versions are recorded in HANDOFF.md.

Non-blocking information to obtain before scheduling/release: jam name/link, submission deadline and timezone, asset/AI rules, final title, desired art/audio direction, and access to the itch.io project for hosted tests. This request authorizes planning; game implementation and any later publishing should follow the user's subsequent instructions.
