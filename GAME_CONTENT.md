# Game content catalog — House of Cinders

Status: Implementation through Phase 6. All 18 heroes, nine elements, the full reaction matrix, 23 items, ten normal bosses and ten Hell variants are functional. Distinct later bosses use geometric placeholder art. Numerical tuning, human balance acceptance, and final audiovisual finish remain open. This file owns content identities; runtime data files below own exact values. `HANDOFF.md` records verification and remaining gates.

## Starting draft and rarity

At a new run, generate **four distinct hero offers from the full roster**. Choose **one free hero**; discard the other offers. Start with two empty team slots and 10 gold. Additional heroes come from shops; the total roster cap is three.

| Rarity | Chance per starting offer | Initial shop price | Identity |
| --- | --- | --- | --- |
| Common | 65% | 8 gold | Straightforward, reliable kits. |
| Uncommon | 25% | 14 gold | More specialized synergies. |
| Rare | 8% | 22 gold | Stronger build-defining mechanics. |
| Legendary | 2% | 35 gold | Gravity or Antimatter kits with bounded powerful effects. |

Roll rarity separately for each offer, then choose uniformly from heroes of that rarity not already offered. Do not force one of each rarity. Multiple offers may share a rarity or element, but not a named hero. These percentages are per offer, not the chance that the entire draft contains that rarity. The full roster currently has at least four heroes in every rarity, so four distinct offers are always possible without changing rarity weights. Use a dedicated seeded draft RNG stream; once saving is implemented, store offers and selection so reloading does not reroll them. No draft reroll button initially; starting a new run creates a new draft.

The chosen starter costs zero and has zero resale value; purchased heroes sell for half their actual purchase price, rounded down. Never sell the last owned hero. At capacity, preview and commit a replacement as one transaction. No duplicate named hero ownership; different heroes of one element are permitted.

## Elements / types

| Type | Theme and role | Hero availability |
| --- | --- | --- |
| Pyro | Fire, burst, burns | Common / Rare |
| Hydro | Water, setup, sustain | Common / Uncommon |
| Anemo | Wind, mobility, reaction hits | Common / Rare |
| Geo | Stone, shields, survivability | Common / Uncommon |
| Dendro | Plants, persistent damage, delayed bursts | Uncommon / Rare |
| Cryo | Ice, stagger, timing windows | Uncommon / Rare |
| Electro | Lightning, damage over time, charged hits | Uncommon / Rare |
| Gravity | Pull fields, stagger, Collapse | Legendary only |
| Antimatter | Void damage, delayed detonations, Annihilation | Legendary only |

Availability describes this roster, not a requirement to create every element/rarity combination. Boss elements describe attacks and resistance themes; they do not automatically give the boss a permanent reactive aura. Neutral damage is an attack category, not a tenth hero element. Weapons never change a hero's element or unlock Legendary elements for other heroes.

## Hero kit and team rules

Every hero has a neutral basic attack, an elemental skill, and a passive. All heroes must be independently capable of beating the opening boss, including kits whose passives become more useful after recruiting teammates. Passive synergy is a bonus, never a prerequisite for dealing damage.

Melee basic attacks: Cinder Jack, Gale Knave, Flint Rook, The Gilt Mason, Frost Jester, Volt Page, and The Last Laugh. Other heroes use ranged basics. Swings have a 0.09s windup, a 122-unit reach plus boss body radius, and a directional arc; dodging cancels the pending swing. Flint’s skill is a 165-unit melee stone strike. Basics briefly slow movement (0.22s melee, 0.12s ranged). Automatic reloads persist through switches, off-field reload timers advance, and skills can be used during reload after basic recovery.

Control one living hero; up to two owned heroes remain off-field. Each keeps individual HP, cooldowns, and equipment. Switching is immediate at the same position, offers no invulnerability, and does not reset state. Off-field cooldowns advance during combat; off-field heroes neither attack nor regenerate. Empty/dead slots cannot be selected. Death switches to another living hero if available; no living owned hero means defeat, including when the run still has only one hero. Victory revives and fully heals all owned heroes.

### Heroes: 18 variants

| Element | Variant / rarity | Skill and passive identity |
| --- | --- | --- |
| Pyro | Cinder Jack / Common | Fan of embers; next basic hit benefits after a reaction. |
| Pyro | Madame Match / Rare | Delayed fire ring; burns last longer. |
| Hydro | Penny Rill / Common | Water lance; reacting grants a small heal on cooldown. |
| Hydro | The Blue Dealer / Uncommon | Returning wave; rewards switching after applying Hydro. |
| Anemo | Gale Knave / Common | Gust line; faster movement briefly after a dodge. |
| Anemo | Zephyr Belle / Rare | Moving cyclone; Crosswind lowers skill cooldown within a cap. |
| Geo | Flint Rook / Common | Stone strike; grants a small shield after a skill hit. |
| Geo | The Gilt Mason / Uncommon | Rock eruption; shielded hits gain damage. |
| Dendro | Clover Hex / Uncommon | Thorn volley; improves Bloom bursts. |
| Dendro | Briar Duchess / Rare | Bramble field; rewards maintaining damage over time. |
| Cryo | Frost Jester / Uncommon | Ice fan; improves stagger against chilled targets. |
| Cryo | Lady Whiteout / Rare | Frost zone; bonus damage after a boss recovers from stagger. |
| Electro | Volt Page / Uncommon | Lightning spear; charged basic hit after switching in. |
| Electro | The Copper Count / Rare | Delayed thunder marks; improves Live Wire ticks. |
| Gravity | The Heavy Crown / Legendary | Singularity field; improved Collapse stagger. |
| Gravity | Orbit Oracle / Legendary | Orbiting projectiles; reacting grants a brief protective orbit. |
| Antimatter | Null Harlequin / Legendary | Void lance; stored reaction charge improves Annihilation. |
| Antimatter | The Last Laugh / Legendary | Delayed void detonation; execute bonus capped against bosses. |

### Ten bosses and Hell variations

| Floor | Boss / element | Distinct attack challenge | Hell variant |
| --- | --- | --- | --- |
| 1 | The Ash Bailiff / Pyro | Telegraphs lanes of flame and a slow slam; teaches dodge. | Infernal Bailiff: alternating lane patterns. |
| 2 | Duchess Undertow / Hydro | Expanding wave rings with safe gaps. | Drowned Duchess: offset returning waves. |
| 3 | The Brass Kite / Anemo | Sweeping wind blades and directional pressure. | Razor Kite: intersecting sweeps. |
| 4 | Baron Bedrock / Geo | Rock pillars reshape movement; aimed shockwaves. | Obsidian Baron: timed pillar eruptions. |
| 5 | Mother Bramble / Dendro | Growing hazard patches with safe routes. | Cinderbloom Mother: patches ignite after warning. |
| 6 | The Glass Regent / Cryo | Ice lanes, delayed shatter, stagger windows. | Black-Ice Regent: alternating shatter sequences. |
| 7 | Saint Static / Electro | Telegraphs a lightning grid and targeted strikes. | Arc Saint: moving grid gaps. |
| 8 | The Crooked Sun / Pyro + Anemo | Clearly signaled alternating stances; spiral projectiles. | Eclipsed Sun: shorter but readable stance cycles. |
| 9 | The Weight of Kings / Gravity | Pull fields and falling masses; safe escape corridors. | Hollow King: reversing gravity fields. |
| 10 | The Empty Throne / Antimatter | Multi-phase fight combining learned patterns and void zones. | Throne of Nothing: new combinations, bounded overlap. |

Hell cycles these ten variants, with a displayed cycle number and deterministic modifiers. Increase HP/damage by data-driven curves, but cap attack speed, simultaneous hazards, and particles. Every pattern must retain a traversable safe route; do not scale telegraph times toward zero. Guard numeric overflow and show large values legibly. The Infinity Key unlocks Hell for the current run; permanent unlocks are optional future work.

## Weapons

Each hero has one weapon slot. All weapons provide a neutral attack benefit and an optional synergy; any hero can equip any weapon. Unequipped storage holds six weapons. Sold/replaced heroes return weapons to storage; block transactions that would overflow it. Specify numerical modifiers in content data and reflect them in tooltips.

| Weapon | Synergy / intended effect |
| --- | --- |
| Ember Wand | Neutral attack bonus; improves Pyro skill damage. |
| Tide Needle | Neutral attack bonus; improves Hydro skill damage. |
| Gale Sling | Neutral attack bonus; improves Anemo skill damage. |
| Quarry Hammer | Neutral attack bonus; improves Geo shield strength. |
| Thorn Bow | Neutral attack bonus; improves Dendro damage over time. |
| Rime Spear | Neutral attack bonus; improves Cryo stagger contribution. |
| Copper Coil | Neutral attack bonus; improves Electro damage over time. |
| Blank Scepter | General neutral attack bonus; rewards switching with a short bounded skill bonus. |

## Curios — team-wide passive buffs

Three slots total; no duplicate named Curios initially. Effects apply only while equipped. Values, caps, and trigger cooldowns are tuning data. Triggered damage cannot recursively trigger itself.

| Curio | Effect |
| --- | --- |
| Loaded Die | Adds bounded critical-hit chance. |
| Spare Ace | Boosts the first elemental skill hit of each encounter. |
| House Tab | Adds gold to floor-clear rewards. |
| Velvet Fuse | Increases reaction damage. |
| Glass Ticket | Increases damage at the cost of maximum HP. |
| Lucky Ash | Boosts Pyro damage. |
| Rain Check | Improves Hydro hero healing effects. |
| Tailwind Token | Grants brief movement speed after an Anemo skill. |
| Stone Seal | Improves Geo-generated shields. |
| Green Receipt | Improves Dendro damage over time and Bloom damage. |
| Cold Read | Improves Cryo stagger buildup. |
| Copper Smile | Improves Electro reaction damage. |

## Consumables

Two slots, one charge per item, usable during combat. Initial bindings: Q and R. Duplicate consumables may occupy separate slots. Invalid use does not consume the item; cooldown recovery cannot reduce timers below zero.

| Consumable | Effect |
| --- | --- |
| Red Flask | Heals the active living hero; cannot revive or exceed maximum HP. |
| Pocket Aegis | Grants a temporary shield; refresh/cap instead of unlimited stacking. |
| Second Wind | Reduces the active hero's remaining skill cooldown by a bounded amount. |

## Reactions and status effects

One aura per target. Elemental skills apply it; neutral attacks leave it intact. Same-element hits refresh duration. A reaction consumes the aura; a nonmatching incoming element replaces it. The following pairs are symmetric unless explicitly stated. For these rules, **basic aura** means Pyro, Hydro, Dendro, Cryo, or Electro; Anemo and Geo do not react with each other.

| Pair | Reaction | Effect |
| --- | --- | --- |
| Pyro + Hydro | Steam Burst | Bonus burst damage. |
| Anemo + basic aura | Crosswind | Extra damage hit. |
| Geo + basic aura | Gilded Guard | Shield for the triggering hero. |
| Pyro + Cryo | Thaw | Bonus burst damage. |
| Hydro + Cryo | Frostbind | Boss stagger buildup. |
| Hydro + Electro | Live Wire | Damage over time. |
| Pyro + Electro | Flashover | Area explosion. |
| Dendro + Pyro | Kindling | Burn damage over time. |
| Dendro + Hydro | Bloom | Delayed burst. |
| Dendro + Electro | Overgrowth | Temporary skill-damage vulnerability. |
| Gravity + basic aura | Collapse | Bonus damage and stagger. |
| Antimatter + any other elemental aura except Gravity | Annihilation | Bounded burst damage. |
| Gravity + Antimatter | Event Horizon | Powerful burst with an internal cooldown. |

Unlisted pairs cause no reaction and use the replacement rule. While Event Horizon is on cooldown, its pair also uses the replacement rule. Periodic damage and reaction hits do not apply auras or generate new reactions. Bosses use stagger buildup and a recovery immunity window instead of permanent freeze/stun. Non-boss pull effects never make arena escape paths unusable. Display actual damage numerically, reaction labels, shield absorption, and visible aura/status indicators.

Tune aura duration, skill cooldowns, damage, stagger thresholds, healing, and status limits through playtesting. Encode every ordered pair in tests, including nonreactions; never infer behavior from color or ability name alone.

## Shops, rewards, and progression

- Start with 10 gold. Initial clear reward is 8 + floor number. Prices: heroes 8/14/22/35; item prices are tuning data. Initial reroll cost is 2, increasing by 1 within a shop and resetting next floor.
- Five offers per shop: two heroes, one weapon, one Curio, one consumable. Bought offers remain empty until reroll or the next shop. Inspect before purchasing.
- First shop guarantees at least one unowned Common hero at 8 gold, so the first clear makes a second hero affordable without requiring a reroll or selling the starter. It does not force recruitment; solo play remains possible.
- Other hero offers roll Common/Uncommon/Rare/Legendary using 75/23/2/0 on floors 1–3, 50/35/14/1 on floors 4–6, 30/40/25/5 on floors 7–10, and 20/35/35/10 in Hell. These are initial balance values, separate from the confirmed starting-draft odds.
- The floor-10 shop guarantees an unowned Legendary offer and enough bonus gold to make it affordable. Still respect the three-hero cap and explicit replacement.
- Ten normal floors, each followed by rewards and a shop if continuing. Floor 10 grants the **Infinity Key**, a run-only progression item with no inventory slot. Choose Finish Run or Enter Hell.
- Hell cycles the ten named variants with increasing HP/damage and bounded speed/hazard density. Show cycle and floor; preserve readable safe paths. Defeat ends the run. No permanent stat upgrades; a new run resets heroes, gold, gear, and the key.
- Autosave at safe boundaries and after shop transactions. Reload during combat restarts the encounter's saved entry state; never duplicate rewards or reroll stock.

## Screens, controls, and presentation

Title, hero draft, floor preview, isometric arena, rewards, shop/team management, pause/settings, victory/defeat results, help, and credits. Balatro-inspired dark card-table menus use original card designs, strong numbers, rarity borders, and animated feedback. Show one occupied hero card and two empty recruit slots at the start. Keep element and rarity visually distinct using text/icons as well as color.

Desktop browser first. WASD/arrows move; mouse aims; left click attacks; E/right click uses skill; Space dodges; 1–3 switches owned heroes; Q/R uses consumables; Esc pauses. Pause on focus loss. Settings include action-key rebinding, volume/mute, reduced motion, shake, large text, and fullscreen. F1 replays help; F2 opens settings; Tab/arrows and Enter navigate menus. Large assets begin as placeholders, with particles and simple sound feedback allowed.

## First playable content and completion

The changed draft requires functional heroes from **all four rarities and the full roster**, including Legendary skills. Phase 2 therefore includes all 18 placeholder hero kits and the reaction behavior they rely on; Phase 5 expands items and hardens/balances these systems rather than first introducing usable hero kits.

First playable: four randomized offers → choose one → solo Ash Bailiff → reward → shop/recruit/manage → stronger Ash Bailiff rematch → demo-complete screen. Defeat/restart works at either fight. Use Blank Scepter, Loaded Die, Spare Ace, and Red Flask for the initial item set. Include card-style management, visible damage, control hints, pause, effects, and a browser build. Teach switching/reactions once a second hero is acquired. The other nine bosses, Hell, full saves, expanded items, and complete presentation arrive in later phases.

No final combat/item numbers or finished assets are claimed by this catalog. Content IDs, stats, costs, cooldowns, and tooltips must be reflected here or in a linked data reference once implemented.


## Implemented tuning reference (Phase 0–6)

Runtime catalogs: `src/data/heroes.lua`, `src/data/reactions.lua`, `src/data/items.lua`, `src/data/bosses.lua`. Combat: `src/combat/{arena,equipment,patterns}.lua`. Economy: `src/run/model.lua`. These are the numerical tuning reference, including full item descriptions shown during inspection.

Base hero HP is 110 (Geo: 130), neutral melee attack 23 every 0.58s or ranged attack 14 every 0.46s with five shots and a 1.65s reload, base skill damage 32 and cooldown 4.5s; shapes adjust damage/timing. Aura duration is 6s; Event Horizon cooldown 8s. Stagger threshold 100, opening 2.1s, recovery immunity 4s. Boss identity never creates a permanent reactive aura or immunity; all starters can fight every boss.

All weapons add 4 neutral attack. Ember/Tide/Gale add 20% matching direct skill damage; Quarry boosts Geo-generated shields 30%; Thorn/Copper boost matching periodic skill and reaction damage 25%; Rime boosts Cryo stagger 30%; Scepter gives 25% skill damage for 4s after switching in. Element synergies never change a hero's element. Weapon prices: Scepter 7 gold, others 9.

Curios: Die 15% chance of 1.5x direct-hit damage; Ace +50% first direct skill hit per encounter; Tab +3 clear gold; Fuse +25% reaction damage; Glass +25% all damage and -20% max HP; Ash +20% direct Pyro skill; Rain +50% healing received by Hydro heroes; Tailwind grants 2s movement haste on Anemo casts; Stone +30% Geo-generated shields; Green +25% Dendro periodic skills/reactions and Bloom; Cold +30% Cryo stagger; Copper +25% Electro reaction damage. All cost 8 gold except Fuse/Glass at 10. Three unique slots prevent duplicate stacking. Multipliers multiply once per event. Both element orders count for reaction synergies. Periodic reaction effects snapshot the reaction bonus and cannot create auras or recurse. Persistent skill fields apply aura on their first connecting tick only; later ticks are periodic damage. Glass clamps HP on acquisition and does not heal on sale; floor rewards restore the modified maximum.

Consumables: Flask heals 45 (4 gold), Aegis adds 30 shield for 6s capped at 40 (5 gold), Second Wind reduces skill cooldown by up to 3s (5 gold). Invalid uses do not consume charges. All items appear in deterministic shops and can be selected in the source-only encounter lab.

Boss HP starts at 308 and remains capped at 8400; normal multiplier `1 + 0.15 × (floor − 1)`. Hell multiplier `min(30, 2.35 + 0.16 × hellFloor)`. Incoming base hits `min(32, 17 + floor)`; slams multiply this by 1.3, and ignited patches by 1.15. The Bailiff adds a 150-unit boss-centered smash every fourth cast alongside its targeted slam. Attack intervals are explicitly bounded by encounter data; no telegraph is shorter than 1.05s. Patterns never scale toward zero warning time. All normal bosses enter phase 2 at half HP; the Throne changes at 67% and 33%. Transitions clear hazards/projectiles and provide 1.8s before the next cast. Sun alternates visibly labeled fire/wind stances; the Hell stance interval is 3.4s instead of 4.4s. Regent gives extra stagger buildup during its shatter opening.

Hell modifiers follow the catalog above and repeat deterministically across cycles; HP increases until the cap. The two-fight demo alone retains the stronger Bailiff rematch. Effects are capped at 80 player projectiles, 12 enemy projectiles, 12 hazards, 24 fields, 12 periodic effects, 80 sparks, 40 labels, 32 visual feedback events, and six pending melee swings. Heavy slams/pillar landings trigger feedback once on activation even when the player avoids them. Hit pauses freeze combat for 35–65ms; visual feedback continues. World shake leaves the HUD steady; reduced motion removes shake and screen flashes. Rings have explicit safe gaps, grid attacks leave an open corridor, patches leave connected channels, and gravity has a force-free escape sector. Simulation tests inspect geometry and safe space; human route/readability acceptance remains pending.
