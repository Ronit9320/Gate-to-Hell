local B = { list = {} }
local rows = {
  {
    'bailiff',
    'The Ash Bailiff',
    'Pyro',
    'Infernal Bailiff',
    'Leave amber lanes; dodge the slow slam.',
    'Alternating flame lanes',
  },
  {
    'undertow',
    'Duchess Undertow',
    'Hydro',
    'Drowned Duchess',
    'Walk through the marked gap in each expanding ring.',
    'Offset returning waves',
  },
  {
    'kite',
    'The Brass Kite',
    'Anemo',
    'Razor Kite',
    'Move off the wind blade; pressure pushes toward the edge.',
    'Intersecting wind sweeps',
  },
  {
    'bedrock',
    'Baron Bedrock',
    'Geo',
    'Obsidian Baron',
    'Pillars block movement. Sidestep aimed shockwaves.',
    'Pillars erupt after warning',
  },
  {
    'bramble',
    'Mother Bramble',
    'Dendro',
    'Cinderbloom Mother',
    'Avoid growing patches. Keep the open route to the south.',
    'Warned patches ignite',
  },
  {
    'regent',
    'The Glass Regent',
    'Cryo',
    'Black-Ice Regent',
    'Ice lanes shatter after a delay. Attack during recovery.',
    'Alternating shatter sequences',
  },
  {
    'static',
    'Saint Static',
    'Electro',
    'Arc Saint',
    'Find the open grid corridor; leave targeted strike circles.',
    'Grid gaps change each cast',
  },
  {
    'sun',
    'The Crooked Sun',
    'Pyro',
    'Eclipsed Sun',
    'Fire stance spirals; wind stance sweeps. Watch the stance label.',
    'Faster signaled stance cycles',
  },
  {
    'kings',
    'The Weight of Kings',
    'Gravity',
    'Hollow King',
    'Leave the pull field through its gap; avoid falling masses.',
    'Gravity reverses between casts',
  },
  {
    'throne',
    'The Empty Throne',
    'Antimatter',
    'Throne of Nothing',
    'Three phases: lanes, waves, then void zones. Watch each warning.',
    'Bounded combinations of learned patterns',
  },
}
for i, r in ipairs(rows) do
  B.list[i] =
    { id = r[1], name = r[2], element = r[3], hellName = r[4], hint = r[5], modifier = r[6], index = i }
end
function B.get(run)
  local floor = run.mode == 'demo' and 1 or ((run.floor - 1) % 10 + 1)
  local d = B.list[floor]
  local hell = run.floor > 10
  local cycle = hell and math.ceil((run.floor - 10) / 10) or 0
  return d, hell, cycle
end
function B.scale(run)
  local hell = math.max(0, run.floor - 10)
  local depth = math.min(9, math.max(0, run.floor - 1))
  return math.min(30, 1 + depth * 0.45 + depth * depth * 0.055 + hell * 0.55)
end
-- Keep the opening solo fight accessible; pressure increases with progression.
function B.difficulty(run)
  local depth = math.max(0, run.floor - 1)
  return {
    damage = math.min(64, 18 + depth * 3),
    cadence = math.max(0.62, 1 - depth * 0.025),
    pursuit = run.floor >= 5,
    tactics = run.floor >= 3,
  }
end
return B
