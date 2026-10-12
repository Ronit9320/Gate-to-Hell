local U = require('src.core.util')
local H = require('src.data.heroes')
local Items = require('src.data.items')
local E = require('src.combat.equipment')
local M = {}
local function owns(r, id)
  for _, h in ipairs(r.team) do
    if h.id == id then
      return true
    end
  end
  return false
end
local function offerHero(r, rng, weights, exclude, rarity)
  rarity = rarity or U.weighted(rng, weights)
  local pool = {}
  for _, h in ipairs(H.list) do
    if h.rarity == rarity and not exclude[h.id] then
      pool[#pool + 1] = h.id
    end
  end
  if #pool == 0 then
    for _, h in ipairs(H.list) do
      if not exclude[h.id] then
        pool[#pool + 1] = h.id
      end
    end
  end
  return pool[U.random(rng, #pool)]
end
function M.new(seed, mode)
  seed = math.floor(tonumber(seed) or 1) % 2147483646 + 1
  local r = {
    version = 1,
    seed = seed,
    draftRng = { seed = seed },
    shopRng = { seed = (seed + 9173) % 2147483646 + 1 },
    encounterSeed = (seed + 731) % 2147483646 + 1,
    stage = 'draft',
    mode = mode or 'run',
    floor = 1,
    gold = 10,
    team = {},
    weapons = {},
    curios = {},
    consumables = {},
    offers = {},
    key = false,
    stats = { clears = 0, damage = 0, reactions = 0, time = 0 },
    rewarded = 0,
    rerollCost = 2,
  }
  local used = {}
  for i = 1, 4 do
    local id = offerHero(r, r.draftRng, { 65, 25, 8, 2 }, used)
    used[id] = true
    r.offers[i] = id
  end
  return r
end
function M.choose(r, i)
  if r.stage ~= 'draft' or not r.offers[i] then
    return false, 'Choose a draft card.'
  end
  r.team = { H.instance(r.offers[i]) }
  r.selected = r.offers[i]
  r.stage = 'preview'
  return true
end
function M.enter(r)
  if r.stage ~= 'preview' then
    return false
  end
  r.stage = 'arena'
  return true
end
function M.reward(r, stats)
  if r.stage ~= 'arena' or r.rewarded >= r.floor then
    return false
  end
  r.rewarded = r.floor
  r.stats.clears = r.stats.clears + 1
  for _, k in ipairs({ 'damage', 'reactions', 'time' }) do
    r.stats[k] = r.stats[k] + ((stats or {})[k] or 0)
  end
  r.lastReward = 8 + r.floor + (E.has(r, 'tab') and 3 or 0)
  r.gold = r.gold + r.lastReward
  for i, h in ipairs(r.team) do
    local fresh = H.instance(h.id, h.paid)
    fresh.weapon = h.weapon
    fresh.maxhp = E.health(r, fresh)
    fresh.hp = fresh.maxhp
    r.team[i] = fresh
  end
  if r.mode == 'demo' and r.floor == 2 then
    r.stage = 'complete'
  elseif r.floor == 10 then
    r.key = true
    r.stage = 'victory'
    r.lastBonus = math.max(0, 35 - r.gold)
    r.gold = r.gold + r.lastBonus
  else
    r.stage = 'rewards'
  end
  return true
end
function M.stock(r, first)
  local f = r.floor
  local weights = f > 10 and { 20, 35, 35, 10 }
    or f > 6 and { 30, 40, 25, 5 }
    or f > 3 and { 50, 35, 14, 1 }
    or { 75, 23, 2, 0 }
  local excluded = {}
  for _, h in ipairs(r.team) do
    excluded[h.id] = true
  end
  local a = offerHero(r, r.shopRng, weights, excluded, first and (f == 1 and 1 or f == 10 and 4) or nil)
  excluded[a] = true
  local b = offerHero(r, r.shopRng, weights, excluded)
  local function item(kind)
    local pool = {}
    for id, d in pairs(Items) do
      if d.kind == kind then
        pool[#pool + 1] = id
      end
    end
    table.sort(pool)
    local id = pool[U.random(r.shopRng, #pool)]
    return { kind = kind, id = id, price = Items[id].price }
  end
  r.stock = {
    { kind = 'hero', id = a, price = H.prices[H.byId[a].rarity] },
    { kind = 'hero', id = b, price = H.prices[H.byId[b].rarity] },
    item('weapon'),
    item('curio'),
    item('consumable'),
  }
end
function M.shop(r)
  if r.stage ~= 'rewards' and r.stage ~= 'victory' then
    return false
  end
  r.stage = 'shop'
  r.rerollCost = 2
  M.stock(r, true)
  return true
end
function M.next(r)
  if r.stage ~= 'shop' then
    return false
  end
  r.floor = r.floor + 1
  r.encounterSeed = (r.encounterSeed * 16807) % 2147483647
  r.stage = 'preview'
  return true
end
function M.finish(r)
  if r.stage ~= 'victory' then
    return false
  end
  r.stage = 'complete'
  return true
end
function M.lose(r)
  if r.stage ~= 'arena' then
    return false
  end
  r.stage = 'defeat'
  return true
end
function M.reroll(r)
  if r.stage ~= 'shop' then
    return false, 'Only in the shop.'
  end
  if r.gold < r.rerollCost then
    return false, 'Not enough gold.'
  end
  r.gold = r.gold - r.rerollCost
  r.rerollCost = r.rerollCost + 1
  M.stock(r, false)
  return true
end
function M.buy(r, index, replace)
  if r.stage ~= 'shop' then
    return false, 'Only in the shop.'
  end
  local o = r.stock[index]
  if not o or o.sold then
    return false, 'Offer already purchased.'
  end
  local cost = o.price
  local old
  if o.kind == 'hero' then
    if owns(r, o.id) then
      return false, 'You already own this hero.'
    end
    if #r.team >= 3 then
      if not replace or not r.team[replace] then
        return false, 'Choose a hero to replace.'
      end
      old = r.team[replace]
      cost = cost - math.floor(old.paid / 2)
      if old.weapon and #r.weapons >= 6 then
        return false, 'Weapon storage is full.'
      end
    elseif replace then
      return false, 'Replacement is unnecessary.'
    end
  elseif o.kind == 'weapon' and #r.weapons >= 6 then
    return false, 'Weapon storage is full (6).'
  elseif o.kind == 'curio' then
    if #r.curios >= 3 then
      return false, 'Curio slots are full (3).'
    end
    for _, id in ipairs(r.curios) do
      if id == o.id then
        return false, 'You already own this Curio.'
      end
    end
  elseif o.kind == 'consumable' and #r.consumables >= 2 then
    return false, 'Consumable slots are full (2).'
  end
  if r.gold < cost then
    return false, 'Not enough gold.'
  end
  r.gold = r.gold - cost
  o.sold = true
  if o.kind == 'hero' then
    if old then
      if old.weapon then
        r.weapons[#r.weapons + 1] = old.weapon
      end
      r.team[replace] = H.instance(o.id, o.price)
    else
      r.team[#r.team + 1] = H.instance(o.id, o.price)
    end
  elseif o.kind == 'weapon' then
    r.weapons[#r.weapons + 1] = o.id
  elseif o.kind == 'curio' then
    r.curios[#r.curios + 1] = o.id
  else
    r.consumables[#r.consumables + 1] = o.id
  end
  E.refresh(r)
  return true
end
function M.sellHero(r, i)
  if r.stage ~= 'shop' then
    return false, 'Only in the shop.'
  end
  local h = r.team[i]
  if not h then
    return false, 'No hero selected.'
  end
  if #r.team <= 1 then
    return false, 'You cannot sell your last hero.'
  end
  if h.weapon and #r.weapons >= 6 then
    return false, 'Weapon storage is full.'
  end
  if h.weapon then
    r.weapons[#r.weapons + 1] = h.weapon
  end
  r.gold = r.gold + math.floor(h.paid / 2)
  table.remove(r.team, i)
  return true
end
function M.equip(r, wi, hi)
  if r.stage ~= 'shop' then
    return false, 'Only in the shop.'
  end
  local h = r.team[hi]
  local id = r.weapons[wi]
  if not h or not id then
    return false, 'Select a weapon and hero.'
  end
  local old = h.weapon
  h.weapon = id
  if old then
    r.weapons[wi] = old
  else
    table.remove(r.weapons, wi)
  end
  return true
end
function M.unequip(r, hi)
  if r.stage ~= 'shop' then
    return false, 'Only in the shop.'
  end
  local h = r.team[hi]
  if not h or not h.weapon then
    return false, 'No equipped weapon.'
  end
  if #r.weapons >= 6 then
    return false, 'Weapon storage is full.'
  end
  r.weapons[#r.weapons + 1] = h.weapon
  h.weapon = nil
  return true
end
function M.sellItem(r, kind, i)
  if r.stage ~= 'shop' then
    return false, 'Only in the shop.'
  end
  local list = r[kind]
  if not list or not Items[list[i]] then
    return false, 'No item selected.'
  end
  r.gold = r.gold + math.floor(Items[list[i]].price / 2)
  table.remove(list, i)
  E.refresh(r)
  return true
end
function M.floorInfo(r)
  local b, hell = require('src.data.bosses').get(r)
  local name = (hell and b.hellName or b.name) .. ' · ' .. b.element
  if r.mode == 'demo' and r.floor == 2 then
    name = name .. ' / rematch'
  end
  if hell then
    return 'HELL ' .. (r.floor - 10) .. ' · CYCLE ' .. math.ceil((r.floor - 10) / 10), name
  end
  return 'FLOOR ' .. r.floor .. ' / 10', name
end
-- Run information is read-only and never advances the encounter or shop RNG.
function M.route(r)
  local B = require('src.data.bosses')
  if r.stage == 'complete' or r.stage == 'defeat' then
    return {}
  end
  local cleared = r.stage == 'shop' or r.stage == 'rewards' or r.stage == 'victory'
  local first = r.floor + (cleared and 1 or 0)
  local route = {}
  for floor = first, first + 2 do
    if r.mode == 'demo' and floor > 2 then
      break
    end
    local boss, hell = B.get({ floor = floor, mode = r.mode })
    route[#route + 1] = {
      floor = floor,
      boss = boss,
      hell = hell,
      label = floor == r.floor and (r.stage == 'arena' and 'FIGHTING NOW' or 'UP NEXT')
        or (floor == first and 'UP NEXT' or 'THEN'),
    }
  end
  return route
end
return M
