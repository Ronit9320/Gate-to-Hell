local Items = require('src.data.items')
local H = require('src.data.heroes')
local E = {}
function E.has(run, id)
  for _, v in ipairs(run.curios) do
    if v == id then
      return true
    end
  end
  return false
end
function E.health(run, h)
  return math.floor(H.byId[h.id].hp * (E.has(run, 'glass') and 0.8 or 1))
end
function E.refresh(run)
  for _, h in ipairs(run.team) do
    h.maxhp = E.health(run, h)
    h.hp = math.min(h.hp, h.maxhp)
  end
end
function E.heal(run, h, amount)
  if h.hp <= 0 then
    return
  end
  h.hp =
    math.min(h.maxhp, h.hp + amount * (H.byId[h.id].element == 'Hydro' and E.has(run, 'rain') and 1.5 or 1))
end
function E.direct(run, h, element)
  local w = Items[h.weapon] or {}
  return (w.element == element and w.skill and 1 + w.skill or 1)
    * (element == 'Pyro' and E.has(run, 'ash') and 1.2 or 1)
end
function E.periodic(run, h, element)
  local mult = 1
  if element == 'Dendro' then
    if h.weapon == 'thorn' then
      mult = mult * 1.25
    end
    if E.has(run, 'green') then
      mult = mult * 1.25
    end
  elseif element == 'Electro' and h.weapon == 'coil' then
    mult = mult * 1.25
  end
  return mult
end
function E.shield(run, h, amount, cap, geo)
  if geo then
    amount = amount * (h.weapon == 'quarry' and 1.3 or 1) * (E.has(run, 'stone') and 1.3 or 1)
  end
  h.shield = math.min(cap, h.shield + amount)
end
function E.stagger(run, h, amount, cryo)
  return amount * (cryo and h.weapon == 'rime' and 1.3 or 1) * (cryo and E.has(run, 'cold') and 1.3 or 1)
end
function E.reaction(run, h, r, a, b)
  if r.effect == 'shield' or r.effect == 'stagger' or r.effect == 'vulnerable' then
    return r.power
  end
  local dendro = a == 'Dendro' or b == 'Dendro'
  local electro = a == 'Electro' or b == 'Electro'
  local mult = E.has(run, 'fuse') and 1.25 or 1
  if electro and E.has(run, 'copper') then
    mult = mult * 1.25
  end
  if (r.name == 'Bloom' or (dendro and r.effect == 'dot')) and E.has(run, 'green') then
    mult = mult * 1.25
  end
  if r.effect == 'dot' and ((dendro and h.weapon == 'thorn') or (electro and h.weapon == 'coil')) then
    mult = mult * 1.25
  end
  return r.power * mult
end
return E
