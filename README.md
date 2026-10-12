# House of Cinders

Working title for a single-player roguelike boss battler, built with **LÖVE 2D and Lua** for a **browser-based itch.io game jam release**. Combine Balatro-inspired hero cards and shop management with real-time combat in isometric arenas. Elemental skills and reactions drive team synergies, with visible damage numbers and readable boss attack telegraphs.

**Status:** Version 0.9.0 implements the game through Phase 8 and prepares the native/browser upload packages and listing materials. All 18 heroes, 23 items, ten normal bosses and ten Hell variants are playable; settings, elemental icons, synthesized music/SFX and credits are included. The UI uses original Blender frames, medallions, resource/action icons, animated objects and nine element-themed stone arenas. A four-page How to Play guide explains the run, combat, reactions and team building. All nine elements have Blender particle animations connected to casts, impacts, projectiles and fields. All 18 heroes now have reference-inspired Blender isometric models and seven animations in eight directions; the Ash Bailiff also uses Blender isometric animations. All ten bosses now use Blender isometric sprites, with ten distinct Hell costumes, stagger/recovery poses and three Empty Throne phase appearances. A dedicated library of 91 animated effect sheets covers attacks, skills, reactions, statuses and hazards. Ten boss scenery props and four screen illustrations are integrated. Original flat portraits are preserved but excluded by default. See [release/UPLOAD_CHECKLIST.md](release/UPLOAD_CHECKLIST.md) and [release/ART_REPLACEMENT.md](release/ART_REPLACEMENT.md). Human acceptance, authored audio replacements and hosted/jam checks remain open; nothing has been published.

## Pending asset checklist

Updated against the Blender artwork and current render/audio code on **12 October 2026**. Open `assets/art-preview.html` for the new animation gallery; see [boss exports](assets/bosses/isometric/README.md), [combat artwork](assets/effects/combat/README.md), and [scenery](assets/scenery/README.md). Unchecked entries are production tasks: **Missing** means no dedicated asset exists; **Replacement/polish** means gameplay already has a procedural or shared implementation. These are asset tasks, not missing combat mechanics. Optional additions are listed separately.

### Already available

- All **18 heroes** have isometric portraits and eight-direction idle, walk, attack, skill, dodge, hurt and death animations in `assets/heroes/isometric/`.
- **Ash Bailiff** has eight-direction idle, attack, walk, hurt and death sheets in `assets/bosses/bailiff_iso/`, used in normal and demo fights. Infernal Bailiff has a dedicated export in `assets/bosses/isometric/bailiff_hell/`.
- All **nine elements** have generic animated particle sheets in `assets/effects/`, used for casts, impacts, projectiles and fields. Dedicated skill/reaction shapes are also available in `assets/effects/combat/`.
- UI frames, button states, backgrounds, card backs, resource/action symbols, nine element medallions, all **23 item icons**, nine elemental arena floors and decorative animation loops already exist in `assets/ui/`.
- Damage numbers, reaction labels, aura/shield indicators, swing arcs, muzzle flashes, trails, sparks, hit flashes, shockwaves, shake and hit pauses are implemented. Damage text remains live text; it does not need a sprite sheet.
- Audio currently includes **11 synthesized cues** (`ui`, `attack`, `impact`, `hit`, `hurt`, `skill`, `dodge`, `switch`, `reaction`, `victory`, `defeat`) and one synthesized music loop in `src/core/audio.lua`. There are no authored audio files in the current asset tree.

### Boss artwork — completed

Each base boss has an articulated isometric model, eight-direction idle, attack wind-up/release, hurt, death, stagger and recovery sheets, and a preview portrait. These stationary bosses do not need locomotion clips. The shared renderer supports all bosses, Hell costumes and Throne phase appearances with at most two resident direction textures.

| Base boss | Asset ID | Attack visuals to support |
| --- | --- | --- |
| Duchess Undertow | `undertow` | Expanding and returning water waves with visible safe gaps |
| The Brass Kite | `kite` | Wind blades, intersecting sweeps and wind pressure |
| Baron Bedrock | `bedrock` | Pillar rise/eruption, rock debris and aimed shockwaves |
| Mother Bramble | `bramble` | Growing bramble patches and ignited growth |
| The Glass Regent | `regent` | Ice lanes, delayed shatter and recovery opening |
| Saint Static | `static` | Electric grid lanes and targeted lightning strikes |
| The Crooked Sun | `sun` | Fire spirals, wind sweeps and fire/wind stance changes |
| The Weight of Kings | `kings` | Pull/push fields and falling masses |
| The Empty Throne | `throne` | Void lanes, waves, zones and three phase appearances |

- [x] Make and integrate the nine base boss sets above; they use their dedicated Blender sets.
- [x] Make distinct Hell appearance variants: **Infernal Bailiff, Drowned Duchess, Razor Kite, Obsidian Baron, Cinderbloom Mother, Black-Ice Regent, Arc Saint, Eclipsed Sun, Hollow King and Throne of Nothing**. All have separate material treatments, modeled attachments and eight-direction exports; animation rigs are reused where appropriate.
- [x] Add clear boss phase-change, stagger/recovery and defeat effects. Dedicated animations/effects accompany live labels; normal-motion defeat plays for one second before rewards.

### Damage, hits and basic attacks — completed artwork

- [x] Neutral melee swing/slash effects for **Cinder Jack, Gale Knave, Flint Rook, The Gilt Mason, Frost Jester, Volt Page and The Last Laugh**. Actor attack animations exist; dedicated slash sheets replace the swing arcs.
- [x] Neutral ranged projectile, muzzle flash, travel trail and impact assets for the other **11 heroes**. Shared neutral projectile, trail, muzzle and impact sheets cover these heroes.
- [x] Dedicated normal-hit and critical-hit bursts, with clearly different strength/readability.
- [x] Player damage impact and shield absorption/break effects; retain the existing hurt animation and readable HP feedback.
- [x] Heavy slam impact, ground cracks, dust/debris and shockwave art to replace generic impact rings.
- [x] Damage-over-time tick feedback distinct from direct hits; keep damage numbers and critical/reaction labels as readable live text.
- [x] Dodge trail/afterimage and hero-switch arrival/departure effects. Dodge animations and procedural feedback already exist.
- [x] Reload start/completion visual cue for ranged heroes; ammunition and reload bars already work.

### Hero elemental attacks — completed dedicated shapes

Dedicated `skill_<hero>` sheets now cover casts, travel/fields and impacts for every existing skill. Generic elemental bursts remain available as fallbacks.

- [x] **Pyro:** Cinder Jack's fan of embers; Madame Match's delayed fire ring.
- [x] **Hydro:** Penny Rill's water lance; The Blue Dealer's returning wave.
- [x] **Anemo:** Gale Knave's gust line; Zephyr Belle's moving cyclone.
- [x] **Geo:** Flint Rook's stone strike; The Gilt Mason's rock eruption.
- [x] **Dendro:** Clover Hex's thorn volley; Briar Duchess's bramble field.
- [x] **Cryo:** Frost Jester's ice fan; Lady Whiteout's frost zone.
- [x] **Electro:** Volt Page's lightning spear; The Copper Count's delayed thunder marks.
- [x] **Gravity:** The Heavy Crown's singularity field; Orbit Oracle's orbiting projectiles.
- [x] **Antimatter:** Null Harlequin's void lance; The Last Laugh's delayed void detonation.

### Reactions and status effects — completed artwork

All thirteen reactions have named animation sheets and event hooks. Live labels remain readable alongside the artwork.

- [x] **Steam Burst:** steam explosion.
- [x] **Thaw:** melting ice burst.
- [x] **Frostbind:** ice binding/stagger effect.
- [x] **Live Wire:** sustained electric arcs and tick flashes.
- [x] **Flashover:** explosive fire/electric burst.
- [x] **Kindling:** sustained burning effect and ticks.
- [x] **Bloom:** delayed seed/bud buildup and burst.
- [x] **Overgrowth:** growth/vulnerability marker.
- [x] **Crosswind:** swirling elemental burst.
- [x] **Gilded Guard:** shield creation and absorption effect.
- [x] **Collapse:** implosion and stagger burst.
- [x] **Annihilation:** void disintegration burst.
- [x] **Event Horizon:** distinct large gravity/void burst.
- [x] Persistent aura/status overlays: elemental application/expiry, burn, electric damage over time, vulnerability, shield and stagger recovery. Existing text/icons/outlines can remain alongside these effects.
- [x] Consumable-use effects: **Red Flask** healing, **Pocket Aegis** shield and **Second Wind** cooldown recovery. Item icons already exist.

### Boss attacks and arena hazards — completed artwork

Dedicated hazard sheets render within stencils matching the existing polygons, rings and circles. Live warnings remain visible, and wave/gravity masks omit safe gaps with extra margin. Artwork never changes collision or damage timing.

- [x] Flame lanes and targeted/close-range Bailiff slam effects, including Hell alternating lanes.
- [x] Water wave/ring segments and returning-wave effects with open safe gaps.
- [x] Wind blade/sweep trails and directional pressure effects.
- [x] Rock pillar rise, sustained pillar, eruption and shockwave effects.
- [x] Bramble growth, persistent patches and Hell ignition effects.
- [x] Ice lane buildup, shatter bursts and shards.
- [x] Electric grid activation, targeted strike and enemy bolt artwork.
- [x] Crooked Sun fire spiral and wind stance attack effects.
- [x] Gravity pull/push field, escape-sector treatment and falling-mass impacts.
- [x] Throne void lanes, wave segments and persistent void-zone effects.
- [x] Consistent warning-to-active-to-expiry treatment for hazards, including Hell combinations; preserve collision boundaries and readable routes.

### Sound effects — authored replacements and missing cues

**Replacement/polish:** the corresponding synthesized cue already exists, but is shared or tonal.

- [ ] Melee swing and ranged firing sounds; replace the shared `attack` tone with suitable weapon families.
- [ ] Boss hit/contact sounds, with normal and critical variants; replace/extend `hit`.
- [ ] Player hurt sound and heavy impact/slam sound; replace `hurt` and `impact`.
- [ ] Elemental skill cast/travel/impact sounds for all nine elements; replace/extend shared `skill` and `hit` cues.
- [ ] Distinct reaction sounds for the **13 named reactions above**; replace/extend shared `reaction`.
- [ ] Dodge whoosh and hero-switch sound; replace `dodge` and `switch`.
- [ ] Menu focus/confirm sounds; replace the shared `ui` tone.
- [ ] Floor-clear/victory and run-defeat stingers; replace `victory` and `defeat`.

**Missing dedicated cues:** new assets and event hooks are needed.

- [ ] Reload start and completion.
- [ ] Shield creation, absorption and break/expiry.
- [ ] Healing, consumable use and cooldown restoration.
- [ ] Damage-over-time ticks and delayed Bloom/detonation buildup/release; keep repeated ticks quiet and rate-limited.
- [ ] Boss attack wind-up/warning and distinct attack releases for each hazard family above.
- [ ] Boss phase transition, Sun stance switch, stagger/recovery and boss death.
- [ ] Individual hero knockout, distinct from the whole-run defeat cue.
- [ ] Shop buy/sell, reroll, equip/unequip, recruitment and unavailable-action feedback.
- [ ] Gold reward, Infinity Key acquisition and entering Hell.

### Optional additional production assets

These expand the presentation; existing screens and music already function.

- [ ] Separate title/shop, normal combat and Hell music loops; optional boss-specific themes and transition stingers. Currently one synthesized loop serves all screens.
- [ ] Arena ambience for fire, water, wind, stone, vegetation, ice, electricity, gravity and void encounters.
- [x] Unique boss arena scenery/props beyond the existing nine element-themed floors.
- [x] Bespoke reward, victory, defeat and Hell-entry illustrations or animated transitions.
- [x] Refresh the existing release cover and screenshots after final boss/effect art is integrated.

### Delivery and integration

- [x] Export transparent PNG sheets with documented frame order, dimensions, anchors, FPS and loop/one-shot behavior; follow the existing hero, Bailiff and effect metadata conventions.
- [ ] Deliver audio masters plus runtime SFX/music files, with looping points where needed. File-based audio needs loader/build integration because the current system synthesizes everything at startup.
- [x] Preserve editable Blender artwork sources, update `assets/ATTRIBUTION.txt` and credits, and include new runtime artwork in release packaging. Authored audio sources remain a separate production task.
- [ ] Review visual/audio timing in normal and Hell fights, reduced-motion behavior, telegraph readability and the sound mix; refresh release media once the assets are accepted.

The artwork pass is delivered. Remaining production work centers on authored audio and human visual/audio acceptance; the existing synthesized sound system still functions. References: [hero sheets](assets/heroes/isometric/README.md), [Bailiff sheets](assets/bosses/bailiff_iso/README.md), [element effects](assets/effects/README.md), [UI/scenery](assets/ui/README.md), and [art integration notes](release/ART_REPLACEMENT.md).

## Core loop

1. Choose **one free hero from four distinct random offers** drawn from the full roster.
2. Preview the floor and enter its isometric boss arena.
3. Defeat the boss, collect gold, and visit the shop to recruit heroes, buy equipment and buffs, or sell and replace team members.
4. Clear **10 floors**, each with a distinct elemental boss, to earn the **Infinity Key**.
5. Finish the run or enter **endless Hell floors** featuring boss variants and increasing difficulty.

Each starting offer independently rolls a rarity, then selects an available hero of that rarity. The four offers never repeat the same named hero; they are not guaranteed to include one of each rarity.

| Starting-offer rarity | Chance per offer |
| --- | --- |
| Common | 65% |
| Uncommon | 25% |
| Rare | 8% |
| Legendary | 2% |

## Heroes and combat

- Own **one to three heroes total**, with no reserve roster beyond that limit. Start with one and recruit more in shops.
- Directly control one hero at a time and switch between living team members. From floor 3, each switch commits you for 1.25 seconds and basic-attack/dodge recovery is shared across the team. Other owned heroes stay off-field; their cooldowns continue, but they do not attack or regenerate health.
- Seven heroes use directional melee basics: Cinder Jack, Gale Knave, Flint Rook, The Gilt Mason, Frost Jester, Volt Page, and The Last Laugh. Get close and aim the swing; dodge cancels an unfinished swing. Flint also has a melee elemental strike.
- Ranged heroes fire five-shot magazines with a 1.65-second automatic reload. Holding attack respects shot cooldowns and reloads; elemental skills remain available during reload. Each hero keeps their own ammunition when switching.
- Each hero has individual HP, a neutral basic attack, an elemental skill, and a passive. Combine elemental skills to trigger reactions such as bonus damage, shields, damage over time, and stagger.
- Elements: **Pyro, Hydro, Anemo, Geo, Dendro, Cryo, Electro, Gravity, and Antimatter**. Gravity and Antimatter heroes are **Legendary only** and can appear in the starting draft.
- Defeated heroes are unavailable for the rest of the fight. If no owned hero remains alive, the run ends. Clearing a floor revives and fully heals the team.
- Bosses have telegraphed attacks and stagger windows. The opening boss must be beatable solo with every possible starting hero.

## Shops and team building

Buy, sell, equip, and replace heroes between fights. At the three-hero limit, purchasing another hero requires an explicit replacement. You cannot sell your last hero or own duplicate copies of the same named hero; different heroes of the same element are allowed.

- **Weapons:** one equipped per hero, with six spaces for unequipped weapons.
- **Curios:** three team-wide passive buff slots, serving a similar team-building role to Balatro's Jokers.
- **Consumables:** two slots for items such as healing flasks and temporary shields.
- **Recruitment:** the first shop guarantees an affordable, unowned Common hero so the player can expand their team.

A new run resets heroes, gold, equipment, and the Infinity Key. There are no permanent stat upgrades. Autosaves preserve progress between floors and after shop transactions; reloading during a fight restarts that encounter from its saved entry state.

## Presentation and controls

Dark card-table management screens, animated hero cards, clear rarity styling, and prominent numbers lead into an isometric arena through an **Enter Floor** action. Names, visuals, and audio are original or appropriately licensed. The current game uses original Blender art for heroes, bosses, Hell appearances, scenery, cards and dedicated combat feedback; procedural fallbacks remain available.

Desktop browsers are the initial target.

| Action | Default control |
| --- | --- |
| Move | WASD / arrow keys |
| Aim | Mouse |
| Basic attack | Left click |
| Elemental skill | E / right click |
| Dodge | Space |
| Switch hero | 1 / 2 / 3 |
| Use consumables | Q / R |
| Pause | Esc |

## First playable milestone

A browser-playable loop: **four-offer draft → one starter → Ash Bailiff fight → rewards and shop → stronger boss rematch → demo-complete screen**, with defeat and restart available throughout.

The full-roster draft requires all **18 placeholder hero kits** and their supporting reactions to function in this milestone. Initial shop items are Blank Scepter, Loaded Die, Spare Ace, and Red Flask. The full run now includes the remaining bosses, Hell variants, expanded items, and saves. Synthesized music, sound effects and Blender presentation are implemented. Human balance review remains open.

## Project documents

- [BUILD_PLAN.md](BUILD_PLAN.md) — implementation phases, architecture, acceptance checks, and browser release requirements.
- [GAME_CONTENT.md](GAME_CONTENT.md) — the content catalog: 18 heroes, nine elements, four rarities, 10 bosses and their Hell variants, eight weapons, 12 Curios, three consumables, and reaction rules.
- [HANDOFF.md](HANDOFF.md) — current progress, decisions, verification results, and the next action. **Update after every build phase.**

## Run and build

Verified on Linux with native LÖVE 11.5, LuaJIT 2.1, Node 26, npm, and Python 3. The pinned love.js 11.4.1 package embeds LÖVE 11.4; the game deliberately targets that shared API. Dependencies are locked in `package-lock.json`.

```sh
npm ci
love .
npm test
npm run build
npm run serve
```

Open `http://localhost:8000` after starting the server. `dist/house-of-cinders.love` runs with LÖVE; `dist/house-of-cinders-web.zip` contains the browser package with root `index.html`. `dist/SHA256SUMS` records checksums. Two consecutive builds were byte-identical. No network is required by the exported game.

The title offers **New run**, **Two-fight demo**, and **Continue saved run** when available. The full run includes ten distinct elemental floors, their Hell variants, and the full item catalog. Starting a new run asks before replacing saved progress. Continue after leaving a fight restores its entry snapshot. A storage warning means progress may last only for the current session.

```sh
npm run test:browser
node scripts/browser-test.cjs --combat-only
node scripts/browser-test.cjs --firefox
npm run format:check
python3 scripts/verify-art.py
node scripts/browser-test.cjs --missing-art-only
```

Browser tests need a Playwright-compatible browser installed. This workspace uses Chromium 153 and Firefox from its existing Playwright cache; set `CINDERS_CHROMIUM` or `CINDERS_FIREFOX` to another compatible executable. Browser launch and local HTTP serving need permission in restricted sandboxes. Test reports and screenshots are written to `.test-results/`, outside release packages. `npm test` covers all starters, all 23 items, reactions, combat invariants, transactions, save integrity, 30-floor progression, 20 encounter victories through simulated player controls, and 100 Hell floors of stress testing. Stress tests use invulnerability to inspect hazard lifecycles; the 20 victory simulations do not.

Combat now includes swing arcs, muzzle flashes, projectile trails, hit bursts, brief impact pauses, slam shockwaves and stronger camera shake on heavy attacks. The HUD stays steady and displays reloads, attack recovery and dodge readiness. Reduced motion suppresses shake and screen flashes. Boss HP and damage have increased, and the Bailiff mixes targeted slams with a close-range smash.

Numbers, visual polish, and shop balance remain tunable. The jam link, deadline, and submission rules are still needed before release scheduling and submission. Nothing has been published.

## Phase 4–6 controls and development

- Menus: Tab / Shift+Tab or arrows focus actions; Enter activates; Esc closes dialogs.
- F1 opens replayable help; F2 opens settings, including volume/mute, reduced motion, screen shake, large text, fullscreen, and skill/dodge/consumable rebinding. Movement and mouse aiming retain their defaults.
- Source checkout only: F3 opens the encounter lab. Choose normal/Hell floor, reproducible seed, any hero, and any item; toggle invulnerability and 0.5–4x simulation speed. Start/reproduce never overwrites your ordinary save. Give-item replaces the oldest lab inventory item at capacity.
- `devtools.lua` is excluded from both packaged builds. F3 has no effect in the downloadable `.love` or browser ZIP.
- Boss tuning lives in `src/data/bosses.lua` and `src/combat/patterns.lua`; item values and descriptions live in `src/data/items.lua` and `src/combat/equipment.lua`.

All twenty encounters still require independent human clears and early/late Hell pacing review before the Phase 6 acceptance gate can be marked complete. Nothing has been published.

## Release verification and media

```sh
node scripts/browser-test.cjs --release-only
node scripts/browser-test.cjs --management-only
python3 scripts/verify-release.py
python3 scripts/package-release.py
```

The management test requires `luajit tests/fixtures.lua` first. The release journey starts with a clean browser context and uses ordinary UI actions and earned gold through ten floors, Hell, defeat and restart. Browser executables can be selected with `CINDERS_CHROMIUM` / `CINDERS_FIREFOX`. Test evidence is in `.test-results/`; listing material and current screenshots are in `release/`. The release-kit ZIP contains the upload packages and listing materials; upload the **web ZIP inside it**, not the whole kit.

The expert simulation clears combat rapidly; no 20–35-minute human run duration or universal 60-FPS guarantee is claimed. See `release/PLAYTEST_CHECKLIST.md` for remaining acceptance checks.

## Blender Ash Bailiff

Eight directional 256×256 animation sets for idle, attack, walk, hurt and death are in [assets/bosses/bailiff_iso](assets/bosses/bailiff_iso/README.md). Open [the animation viewer](assets/bosses/bailiff_iso/preview.html) to inspect them. Editable `.blend` sources are in `art-src/blender/`; reproducible modeling/rendering scripts are in `scripts/blender/`. These approved atlases are integrated into normal/demo/Hell Bailiff fights and included by default. Other bosses retain their existing geometric presentation; the hero library is described below.

## Blender UI and scenery

Open [the art library preview](assets/ui/preview.html) for all nine floor variants,
seven animation loops, button states, element medallions, item icons and backgrounds.
The editable library is `art-src/blender/house-ui.blend`; each asset has its own
scene, geometry, materials, camera and animation keyframes. [Asset notes](assets/ui/README.md)
describe the sheet layouts and projection. The game uses these PNGs by default
and freezes decorative motion when reduced motion is enabled.

```sh
blender -b -t 4 -P scripts/blender/build_house_ui.py
python3 scripts/verify-ui-art.py
npm test
npm run build
luajit tests/fixtures.lua
node scripts/browser-test.cjs --art-only
python3 scripts/verify-release.py
```

Only the PNG exports ship in the game. Blender sources, intermediate frames and
the preview page remain local. The previous `build_ui.py` script reproduces the
older skin; use `build_house_ui.py` for the current artwork.

## Isometric heroes

All 18 heroes use Blender models inspired by their preserved 2D portraits.
[The hero viewer](assets/heroes/isometric/preview.html) compares each reference
with the new character and exposes eight directions and seven animations.
The new isometric portraits also appear on title, draft and team cards.
[Rendering notes](assets/heroes/isometric/README.md) describe the sheets,
editable controls, pose timing and runtime texture budget.

```sh
blender -b -t 4 -P scripts/blender/build_heroes.py
python3 scripts/verify-heroes.py
luajit tests/fixtures.lua
node scripts/browser-test.cjs --heroes-only
```

Editable library: `art-src/blender/heroes-isometric.blend`. `heroSprites` is
enabled by default independently of the older `usePortraits` option. Animation
uses combat events and respects pause/reduced motion; original portraits remain
preserved in `assets/heroes/` and are excluded from the default runtime.

## Icons, guide and elemental particles

Press **F1**, or choose **How to play** on the title screen, for the four-page overview.
The guide follows custom key bindings and supports large text. Gold, health, shields,
combat stats, equipment and menu actions have labeled icons.

Open [the animation library](assets/effects/preview.html) locally to inspect all nine
element particle sets and 24 Blender UI symbols. Editable particle animation scenes
are in `art-src/blender/element-effects.blend`. Rebuild using:

```sh
blender -b -t 4 -P scripts/blender/build_polish.py
python3 scripts/verify-polish.py
npm run build
node scripts/browser-test.cjs --polish-only
```

Particles use existing bounded feedback and draw fixed, dimmed frames in reduced
motion. They do not change combat RNG, collision, damage or cooldown timing.

### Difficulty and hover inspection

From floor 3, bosses guard between openings: direct damage is reduced by 55%.
Trigger a compatible two-element reaction to break guard for 2.5 seconds, or time
attacks during stagger / the final 0.75 seconds before the next cast. Stagger adds
30% damage and is followed by eight seconds of stagger immunity. Bosses resist
their own element by 40%, so scouting informs recruitment and skill choices.
Switching commits the active hero for 1.25 seconds; shared attack/dodge recovery
prevents cycling heroes to bypass recovery. Automatic replacement of fallen heroes
still works during a switch lock. These rules begin at floor 3.

Floor 10 has 2,928 displayed HP and 45 base hit damage. From floor 5, every cast adds
a delayed strike at your position when the warning begins; it does not follow you.
Warnings retain their 1.05-second minimum and attack intervals their 2.2-second
minimum. The opening fight retains its original health and damage. Hell damage
caps at 64; boss health remains capped at 8,400.

**Run Info** in the header shows the current/upcoming three encounters, including
Hell variants, attack hints and resistance tooltips. It pauses combat while open.
Shop/reward screens start the preview at the next uncleared floor. The persistent
“Done.” success message has been removed; transaction failures still show errors.

Hover over hero cards, shop offers/item icons, the boss panel, encounter threat,
team health, skills, dodge, ammunition, curios or consumables for inspection text.
Tooltips appear after a short delay, wrap to fit the viewport, and do not consume
clicks. Combat now shows team health bars, skill/dodge recovery tracks, a boss
stagger track and an encounter threat badge. Large text and reduced motion work
with the new HUD.

Run `luajit scripts/balance-check.lua` for a deterministic comparison of three heroes
standing still and spamming attacks versus reading warnings and dodging, or `node scripts/browser-test.cjs --hover-only` after building and
running `luajit tests/fixtures.lua` to check hover pixels and capture UI screenshots.

Run `node scripts/browser-test.cjs --tactics-only` for Run Info, combat guard UI,
large-text layout and removal of the success-message overlay.
