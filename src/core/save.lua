local C = require('src.core.codec')
local U = require('src.core.util')
local H = require('src.data.heroes')
local Items = require('src.data.items')
local E = require('src.combat.equipment')
local S = { version = 1 }
local stages = {
  draft = true,
  preview = true,
  arena = true,
  rewards = true,
  shop = true,
  victory = true,
  complete = true,
  defeat = true,
}
local function number(v, min, max)
  return type(v) == 'number' and v == v and v >= min and v <= max
end
local function integer(v, min, max)
  return number(v, min, max) and v == math.floor(v)
end
local function array(t, max)
  if type(t) ~= 'table' or #t > max then
    return false
  end
  local n = 0
  for k in pairs(t) do
    if not integer(k, 1, #t) then
      return false
    end
    n = n + 1
  end
  return n == #t
end
function S.validate(r)
  if type(r) ~= 'table' or r.version ~= S.version then
    return false, 'Save version is unsupported.'
  end
  if
    not stages[r.stage]
    or not integer(r.floor, 1, 1000000)
    or not integer(r.gold, 0, 1000000000)
    or not integer(r.seed, 1, 2147483646)
  then
    return false, 'Invalid run data.'
  end
  if r.mode ~= 'demo' and r.mode ~= 'run' then
    return false, 'Invalid run mode.'
  end
  if not integer(r.rewarded, 0, r.floor) or type(r.key) ~= 'boolean' or (r.floor > 10 and not r.key) then
    return false, 'Invalid progression.'
  end
  if not integer(r.encounterSeed, 1, 2147483646) or not integer(r.rerollCost, 2, 1000000) then
    return false, 'Invalid generator state.'
  end
  for _, name in ipairs({ 'draftRng', 'shopRng' }) do
    if type(r[name]) ~= 'table' or not integer(r[name].seed, 1, 2147483646) then
      return false, 'Invalid random state.'
    end
  end
  if
    not array(r.team, 3)
    or (r.stage ~= 'draft' and #r.team == 0)
    or (r.stage == 'draft' and #r.team ~= 0)
  then
    return false, 'Invalid roster.'
  end
  local seen = {}
  for _, h in ipairs(r.team) do
    if
      type(h) ~= 'table'
      or not H.byId[h.id]
      or seen[h.id]
      or not number(h.maxhp, math.floor(H.byId[h.id].hp * 0.8), H.byId[h.id].hp)
      or not number(h.hp, 0, h.maxhp)
      or not integer(h.paid, 0, 35)
    then
      return false, 'Invalid hero.'
    end
    if h.ammo ~= nil and not integer(h.ammo, 0, H.byId[h.id].magazine) then
      return false, 'Invalid ammunition.'
    end
    seen[h.id] = true
    for _, k in ipairs({ 'cd', 'basicCd', 'dodgeCd', 'healCd', 'shield', 'shieldTime', 'charge' }) do
      if not number(h[k], 0, 1000) then
        return false, 'Invalid hero timers.'
      end
    end
    for _, k in ipairs({ 'haste', 'switchBuff', 'reload', 'recovery' }) do
      if h[k] ~= nil and not number(h[k], 0, 1000) then
        return false, 'Invalid passive timer.'
      end
    end
    for _, k in ipairs({ 'charged', 'hydroApplied', 'refunded' }) do
      if h[k] ~= nil and type(h[k]) ~= 'boolean' then
        return false, 'Invalid passive state.'
      end
    end
    if h.weapon and (not Items[h.weapon] or Items[h.weapon].kind ~= 'weapon') then
      return false, 'Unknown equipment.'
    end
  end
  for _, spec in ipairs({
    { 'weapons', 6, 'weapon' },
    { 'curios', 3, 'curio' },
    {
      'consumables',
      2,
      'consumable',
    },
  }) do
    local list = r[spec[1]]
    if not array(list, spec[2]) then
      return false, 'Invalid inventory.'
    end
    local unique = {}
    for _, id in ipairs(list) do
      if not Items[id] or Items[id].kind ~= spec[3] or (spec[1] == 'curios' and unique[id]) then
        return false, 'Unknown or duplicate item.'
      end
      unique[id] = true
    end
  end
  for _, h in ipairs(r.team) do
    if h.maxhp ~= E.health(r, h) then
      return false, 'Invalid maximum HP.'
    end
  end
  if not array(r.offers, 4) or #r.offers ~= 4 then
    return false, 'Invalid draft.'
  end
  seen = {}
  for _, id in ipairs(r.offers) do
    if not H.byId[id] or seen[id] then
      return false, 'Invalid draft hero.'
    end
    seen[id] = true
  end
  if type(r.stats) ~= 'table' then
    return false, 'Invalid statistics.'
  end
  for _, k in ipairs({ 'clears', 'damage', 'reactions', 'time' }) do
    if not number(r.stats[k], 0, 1e14) then
      return false, 'Invalid statistics.'
    end
  end
  if r.stage ~= 'draft' and r.selected and not H.byId[r.selected] then
    return false, 'Invalid selected hero.'
  end
  local after = r.stage == 'rewards' or r.stage == 'shop' or r.stage == 'victory' or r.stage == 'complete'
  if r.rewarded ~= (after and r.floor or r.floor - 1) then
    return false, 'Inconsistent reward boundary.'
  end
  if r.stage == 'shop' then
    if not array(r.stock, 5) or #r.stock ~= 5 then
      return false, 'Invalid shop stock.'
    end
    for _, o in ipairs(r.stock) do
      if
        type(o) ~= 'table'
        or not integer(o.price, 0, 1000)
        or (o.sold ~= nil and type(o.sold) ~= 'boolean')
      then
        return false, 'Invalid offer.'
      end
      if o.kind == 'hero' then
        if not H.byId[o.id] then
          return false, 'Unknown shop hero.'
        end
      elseif not Items[o.id] or Items[o.id].kind ~= o.kind then
        return false, 'Unknown shop item.'
      end
    end
  end
  if (r.stage == 'rewards' or r.stage == 'victory') and not integer(r.lastReward, 0, 1000010) then
    return false, 'Invalid reward.'
  end
  if r.stage == 'victory' and (r.floor ~= 10 or not integer(r.lastBonus, 0, 35)) then
    return false, 'Invalid victory.'
  end
  return true
end
function S.encode(r)
  local ok, err = S.validate(r)
  assert(ok, err)
  return C.encode(r)
end
function S.decode(raw)
  local ok, r = pcall(C.decode, raw)
  if not ok then
    return nil, 'Save is corrupt; start a new run to recover.'
  end
  local valid, err = S.validate(r)
  if not valid then
    return nil, err
  end
  return r
end
function S.write(r, fs)
  fs = fs or love.filesystem
  local ok, raw = pcall(S.encode, r)
  if not ok then
    return false, 'Unable to encode progress.'
  end
  local worked, result = pcall(fs.write, 'run.sav', raw)
  if not worked or not result then
    return false, 'Storage unavailable. Progress is session-only.'
  end
  return true
end
function S.read(fs)
  fs = fs or love.filesystem
  local ok, exists = pcall(fs.getInfo, 'run.sav')
  if not ok then
    return nil, 'Storage unavailable.'
  end
  if not exists then
    return nil
  end
  local worked, raw = pcall(fs.read, 'run.sav')
  if not worked or not raw then
    return nil, 'Unable to read saved run.'
  end
  return S.decode(raw)
end
function S.resume(r)
  local copy = U.copy(r)
  if copy.stage == 'arena' then
    copy.stage = 'preview'
  end
  return copy
end
return S
