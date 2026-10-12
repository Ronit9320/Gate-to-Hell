local items = {}
local function add(id, name, kind, price, description, stats)
  local d = stats or {}
  d.id, d.name, d.kind, d.price, d.description = id, name, kind, price, description
  items[id] = d
end
add(
  'scepter',
  'Blank Scepter',
  'weapon',
  7,
  '+4 neutral attack. Switching in grants +25% skill damage for 4s.',
  { attack = 4 }
)
add(
  'ember',
  'Ember Wand',
  'weapon',
  9,
  '+4 neutral attack; +20% direct Pyro skill damage.',
  { attack = 4, element = 'Pyro', skill = 0.2 }
)
add(
  'tide',
  'Tide Needle',
  'weapon',
  9,
  '+4 neutral attack; +20% direct Hydro skill damage.',
  { attack = 4, element = 'Hydro', skill = 0.2 }
)
add(
  'gale',
  'Gale Sling',
  'weapon',
  9,
  '+4 neutral attack; +20% direct Anemo skill damage.',
  { attack = 4, element = 'Anemo', skill = 0.2 }
)
add(
  'quarry',
  'Quarry Hammer',
  'weapon',
  9,
  '+4 neutral attack; Geo-generated shields +30%, within shield caps.',
  { attack = 4 }
)
add(
  'thorn',
  'Thorn Bow',
  'weapon',
  9,
  '+4 neutral attack; Dendro periodic skill damage and Dendro reaction damage over time +25%.',
  { attack = 4 }
)
add(
  'rime',
  'Rime Spear',
  'weapon',
  9,
  '+4 neutral attack; Cryo skill and reaction stagger +30%.',
  { attack = 4 }
)
add(
  'coil',
  'Copper Coil',
  'weapon',
  9,
  '+4 neutral attack; Electro periodic skill damage and Electro reaction damage over time +25%.',
  { attack = 4 }
)
add('die', 'Loaded Die', 'curio', 8, '15% chance of 1.5x damage on direct hits.')
add('ace', 'Spare Ace', 'curio', 8, 'First elemental skill hit of each encounter deals 50% more.')
add('tab', 'House Tab', 'curio', 8, '+3 gold on each floor clear, awarded once.')
add('fuse', 'Velvet Fuse', 'curio', 10, '+25% reaction damage; no bonus to shields or stagger.')
add('glass', 'Glass Ticket', 'curio', 10, '+25% all damage; maximum hero HP reduced by 20%.')
add('ash', 'Lucky Ash', 'curio', 8, '+20% direct Pyro skill damage.')
add('rain', 'Rain Check', 'curio', 8, '+50% healing received by Hydro heroes, capped at maximum HP.')
add(
  'tailwind',
  'Tailwind Token',
  'curio',
  8,
  'Anemo skill casts grant 35% movement speed for 2s; refresh only.'
)
add('stone', 'Stone Seal', 'curio', 8, '+30% Geo-generated shields, within shield caps.')
add('green', 'Green Receipt', 'curio', 8, '+25% Dendro periodic skill/reaction damage and Bloom damage.')
add('cold', 'Cold Read', 'curio', 8, '+30% Cryo skill and reaction stagger.')
add('copper', 'Copper Smile', 'curio', 8, '+25% damage of reactions involving Electro.')
add('flask', 'Red Flask', 'consumable', 4, 'Restore 45 HP to the active hero. Cannot revive.')
add(
  'aegis',
  'Pocket Aegis',
  'consumable',
  5,
  '30 shield for 6s, capped at 40. Refreshes; no stacking beyond cap.'
)
add('wind', 'Second Wind', 'consumable', 5, 'Reduce remaining skill cooldown by 3s, never below zero.')
return items
