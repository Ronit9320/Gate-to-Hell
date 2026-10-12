local R = {
  matrix = {},
  elements = { 'Pyro', 'Hydro', 'Anemo', 'Geo', 'Dendro', 'Cryo', 'Electro', 'Gravity', 'Antimatter' },
}
local function pair(a, b, name, effect, power)
  R.matrix[a .. ':' .. b] = { name = name, effect = effect, power = power }
  R.matrix[b .. ':' .. a] = R.matrix[a .. ':' .. b]
end
pair('Pyro', 'Hydro', 'Steam Burst', 'burst', 25)
pair('Pyro', 'Cryo', 'Thaw', 'burst', 28)
pair('Hydro', 'Cryo', 'Frostbind', 'stagger', 38)
pair('Hydro', 'Electro', 'Live Wire', 'dot', 8)
pair('Pyro', 'Electro', 'Flashover', 'burst', 24)
pair('Dendro', 'Pyro', 'Kindling', 'dot', 7)
pair('Dendro', 'Hydro', 'Bloom', 'delay', 32)
pair('Dendro', 'Electro', 'Overgrowth', 'vulnerable', 0.25)
for _, e in ipairs({ 'Pyro', 'Hydro', 'Dendro', 'Cryo', 'Electro' }) do
  pair('Anemo', e, 'Crosswind', 'burst', 18)
  pair('Geo', e, 'Gilded Guard', 'shield', 22)
  pair('Gravity', e, 'Collapse', 'collapse', 23)
end
for _, e in ipairs(R.elements) do
  if e ~= 'Antimatter' and e ~= 'Gravity' then
    pair('Antimatter', e, 'Annihilation', 'burst', 38)
  end
end
pair('Gravity', 'Antimatter', 'Event Horizon', 'horizon', 60)
function R.apply(target, element, now)
  if not element then
    return
  end
  if target.auraEnd and target.auraEnd <= now then
    target.aura = nil
  end
  local reaction = target.aura and R.matrix[target.aura .. ':' .. element]
  if reaction and (reaction.effect ~= 'horizon' or now >= (target.horizonReady or 0)) then
    target.aura = nil
    target.auraEnd = 0
    if reaction.effect == 'horizon' then
      target.horizonReady = now + 8
    end
    return reaction
  end
  target.aura = element
  target.auraEnd = now + 6
end
return R
