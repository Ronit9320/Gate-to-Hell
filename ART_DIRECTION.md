# Gate to Hell — art direction

## Visual target

### Refined target — sculpted RPG characters

The author's reference is Dota 2: expressive, anatomically shaped fantasy
characters with continuous curved surfaces and clear silhouettes. The first
detail pass retained too much rectangular construction; the revision rebuilds
the main forms instead of decorating that construction. Armor should wrap a
body: domed overlapping pauldrons, a curved tapered cuirass, rounded elbow/knee
guards, fitted vambraces, fingers and shaped feet. The hood must have cloth
volume and a deep opening around an expressive carved death mask. Use broad
natural folds, split hanging tabards and a weighted back drape.

Follow [Valve's character art principles](https://help.steampowered.com/en/faqs/view/0688-7692-4D5A-1935):
readable silhouette, large coherent color regions, areas of visual rest, and
contrast concentrated toward the face/upper body. Blue-black forged steel,
burgundy soot cloth, aged brass and scorched ivory form the Bailiff's palette.
Warm furnace light is a restrained focal accent. Material breakup should imply
worn surfaces without hiding sculpted form. This is an original executioner
design using those art principles, with no copied Dota character assets.

A dark, theatrical isometric world: scorched iron, worn brass, carved stone,
heavy cloth and dangerous elemental light. Characters should feel like crafted
fantasy figures with convincing construction, rather than stacks of primitives.
Keep the card-table game's strong silhouettes and readable elemental colors.
The camera remains orthographic, 45° azimuth and 30° elevation; assess every
asset at its actual 1280 × 720 gameplay size as well as in close-up.

Use three levels of detail: silhouette (hood, shoulders, weapon), construction
(overlapping plates, articulated joints, folds), and wear (rivets, chipped edges,
scratches, soot). Reserve the brightest values for eyes, furnace openings and
attack cores. Broad dark surfaces give those details room to read. Avoid covering
the whole body in equally bright neon lines.

## First review: The Ash Bailiff

The floor-one Pyro boss is a condemned executioner enforcing the House's debts.
He should look heavy, hostile and ancient: a deep hood over an iron death mask,
slanted furnace eyes, a grated chest furnace, layered executioner's armor,
oversized asymmetric shoulders, scorched hanging cloth and an execution hammer.
The hammer has a sculpted fluted head, brass reinforcement, a molten striking face
and a wrapped haft. Chains and stamped seals suggest his office without turning
him into a generic horned demon. Blackened steel dominates; worn bronze and pale
edge damage describe construction; ember red and amber identify Pyro.

Model details as editable Blender geometry and material nodes. Scratches and
roughness should break up broad surfaces, while bevels catch the isometric key
light. Back views need cloth folds, armor seams and chains rather than an empty
box. All attachments must follow the skeletal rig in all eight directions.

## Motion and attacks

### Threat and grip refinement

The next revision pushes the executioner further: blackened death-mask iron,
deep slanted ember eyes, blade brows, fanged jaw, crown blades and swept shoulder
talons. Detail follows construction: cast flange bolts, shoulder crests, bracer
bands and hinges, incised runes, sword scoring, stitched repairs, ragged hems,
weighted cloth and hanging debt-chain/token hardware.

The right hand must visibly close around the hammer's cylindrical haft. Four
curled fingers and an opposed thumb surround the shaft, with the gauntlet on
the back of the hand. Hand and weapon share one skeletal attachment. The arm
holds the head clear of the chest. A new one-handed wind-up uses wrist control
to keep the heavy maul oriented correctly, followed by a forward release and
settling pose. Inspect a grip close-up and the actual keyed attack frames before
accepting the full directional export. Surface detail cannot compensate for an
incorrect grip or a weightless weapon pose.

- Idle: controlled breathing, hunched menace, weapon held heavily; furnace glow
  and small ember details imply heat.
- Wind-up: lift the hammer and open the chest posture; a long, readable held
  threat precedes release. Attack contact follows the existing warning timer.
- Flame lanes / beams: floor-bound streams of fire with a hot narrow core,
  broken flame ribbons, darker outer tongues and embers. Amber outlines show
  the full danger area during warning; active fire fits that exact footprint.
- Targeted slam: stamped circular impact, branching molten cracks, a low
  expanding fire ring and chunks of dark slag. The existing target locks when
  warning starts. Close-range smash uses the same language at its larger radius.
- Hurt: brief upper-body recoil; preserve the weapon's weight.
- Death: furnace gutters out as the executioner folds into a heavy kneeling
  collapse. Rewards still follow the existing death sequence.

"Beams" describe the existing flame-lane presentation; this pass adds no new
laser attack or combat rule. Normal floor one and its demo rematch are the first
review target. The Infernal costume and other characters follow after approval.

## Readability and delivery

Existing collision, damage, RNG, warning lengths, safe routes and pause behavior
remain authoritative. Effects use the existing hazard stencils. Reduced motion
uses fixed readable frames with lower effect opacity. Render transparent sprites
with the existing 256px cells, eight directions, 40 frames per direction and
ground anchor (128, 204), so the new model fits the established runtime contract.

Deliver an editable versioned Blender scene, reproducible build script, upgraded
runtime atlases, a close-up beauty render, direction/pose review images and an
offline viewer. Preserve the earlier Blender model for comparison. Review the
silhouette, material detail, hammer motion, flame lanes and slam in game before
extending the treatment to heroes or other bosses.
