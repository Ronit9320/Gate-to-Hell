local U = require('src.core.util')
local H = require('src.data.heroes')
local R = require('src.data.reactions')
local M = require('src.run.model')
local A = require('src.combat.arena')
local D = require('src.combat.damage')
local S = require('src.core.save')
local C = require('src.core.codec')
local I = require('src.render.iso')
local total = 0
local function test(name, fn)
  local ok, e = pcall(fn)
  if not ok then
    error(name .. ': ' .. tostring(e))
  end
  total = total + 1
  print('PASS ' .. name)
end
local function run(id)
  local r = M.new(417)
  M.choose(r, 1)
  r.team = { H.instance(id or 'jack') }
  return r
end
local function shop()
  local r = run()
  M.enter(r)
  M.reward(r)
  M.shop(r)
  return r
end
local function snapshot(r)
  return C.encode(r)
end
local function unchanged(r, fn)
  local before = snapshot(r)
  assert(not fn())
  assert(snapshot(r) == before, 'failed transaction mutated run')
end

test('seeded draft distinct and exact rarity boundaries', function()
  local a, b = M.new(104), M.new(104)
  assert(snapshot(a) == snapshot(b))
  local count = { 0, 0, 0, 0 }
  for seed = 1, 10000 do
    local r = M.new(seed * 199)
    local seen = {}
    for _, id in ipairs(r.offers) do
      assert(not seen[id])
      seen[id] = true
      local h = H.byId[id]
      count[h.rarity] = count[h.rarity] + 1
      assert((h.element ~= 'Gravity' and h.element ~= 'Antimatter') or h.rarity == 4)
    end
  end
  local expected = { 0.65, 0.25, 0.08, 0.02 }
  for i = 1, 4 do
    assert(math.abs(count[i] / 40000 - expected[i]) < 0.015)
  end
end)
test('projection roundtrips and movement direction', function()
  for x = -300, 300, 60 do
    for y = -300, 300, 60 do
      local sx, sy = I.project(x, y)
      local rx, ry = I.inverse(sx, sy)
      assert(math.abs(rx - x) < 1e-8 and math.abs(ry - y) < 1e-8)
    end
  end
  local x, y = I.screenVector(1, 0)
  local sx, sy = I.project(x, y)
  assert(sx > 640 and math.abs(sy - 345) < 1e-8)
end)
test('damage clamp, ordering and actual shield absorption', function()
  assert(D.amount(10, 5, 2, 1.5, 0.2) == 36)
  local h = { hp = 10, shield = 8 }
  local actual, abs = D.apply(h, 40)
  assert(actual == 10 and abs == 8 and h.hp == 0 and h.shield == 0)
end)
local basic = { Pyro = true, Hydro = true, Dendro = true, Cryo = true, Electro = true }
local named = {
  ['Hydro:Pyro'] = 'Steam Burst',
  ['Cryo:Pyro'] = 'Thaw',
  ['Cryo:Hydro'] = 'Frostbind',
  ['Electro:Hydro'] = 'Live Wire',
  ['Electro:Pyro'] = 'Flashover',
  ['Dendro:Pyro'] = 'Kindling',
  ['Dendro:Hydro'] = 'Bloom',
  ['Dendro:Electro'] = 'Overgrowth',
}
local function expected(a, b)
  if a == b then
    return nil
  end
  if a == 'Antimatter' or b == 'Antimatter' then
    return (a == 'Gravity' or b == 'Gravity') and 'Event Horizon' or 'Annihilation'
  end
  for _, s in ipairs({ { 'Gravity', 'Collapse' }, { 'Geo', 'Gilded Guard' }, { 'Anemo', 'Crosswind' } }) do
    if (a == s[1] and basic[b]) or (b == s[1] and basic[a]) then
      return s[2]
    end
  end
  return named[a .. ':' .. b] or named[b .. ':' .. a]
end
test('all 81 ordered element pairs, neutral, expiry, horizon cooldown', function()
  for _, a in ipairs(R.elements) do
    for _, b in ipairs(R.elements) do
      local t = { aura = a, auraEnd = 10 }
      local r = R.apply(t, b, 1)
      assert((r and r.name) == expected(a, b), a .. '/' .. b)
      assert(t.aura == (r and nil or b) or (r and t.aura == nil))
    end
  end
  local t = { aura = 'Pyro', auraEnd = 10 }
  assert(not R.apply(t, nil, 1))
  assert(t.aura == 'Pyro')
  assert(not R.apply(t, 'Hydro', 11))
  assert(t.aura == 'Hydro')
  t = { aura = 'Gravity', auraEnd = 10 }
  assert(R.apply(t, 'Antimatter', 1).name == 'Event Horizon')
  R.apply(t, 'Gravity', 2)
  assert(not R.apply(t, 'Antimatter', 3))
  assert(t.aura == 'Antimatter')
  R.apply(t, 'Antimatter', 8)
  assert(R.apply(t, 'Gravity', 9).name == 'Event Horizon')
end)
test('switch cooldown, off-field HP, death and dead slots', function()
  local r = run()
  r.team[2] = H.instance('penny')
  local a = A.new(r)
  a:hero().cd = 3
  a:hero().hp = 50
  assert(a:switch(2))
  a:update(0.05, 0, 0)
  assert(r.team[1].hp == 50 and r.team[1].cd < 3)
  assert(not a:switch(3))
  a:damageHero(999)
  assert(a.active == 1)
  assert(not a:switch(2))
  a.invuln = 0
  a:damageHero(999)
  assert(a.result == 'defeat')
end)
test('dodge cooldown and world bounds', function()
  local a = A.new(run())
  a:dodgeStart(1, 0)
  local hp = a:hero().hp
  a:damageHero(100)
  assert(a:hero().hp == hp)
  for i = 1, 200 do
    a:update(0.02, 1, 0)
  end
  assert(a.x <= 350 and a.x >= -350 and a.y <= 350)
end)
test('projectiles retain owner on switch', function()
  local r = run()
  r.team[2] = H.instance('penny')
  local a = A.new(r)
  a:attack(0, -100, true)
  a:switch(2)
  for i = 1, 50 do
    a:update(0.02, 0, 0)
  end
  assert(a.boss.hp < a.boss.maxhp)
  assert(a.boss.aura == 'Pyro')
end)
test('every starter wins floor one solo using live combat', function()
  for _, h in ipairs(H.list) do
    local a = A.new(run(h.id))
    for step = 1, 3000 do
      require('tests.bot')(a)
      if a.result then
        break
      end
    end
    assert(a.result == 'victory', h.name .. ' failed: ' .. tostring(a.result))
    assert(a:hero().hp > 0)
  end
end)
test('all skill shapes produce elemental damage', function()
  for _, h in ipairs(H.list) do
    local a = A.new(run(h.id))
    a.x = 0
    a.y = 0
    a:attack(0, -100, true)
    for i = 1, 150 do
      a:update(0.02, 0, 0)
    end
    assert(a.boss.hp < a.boss.maxhp, h.id)
    assert(a.boss.aura == h.element, h.id)
  end
end)
test('hero passives and bounded reactions', function()
  local function arena(id)
    local a = A.new(run(id))
    a.boss.hp = 10000
    a.boss.maxhp = 10000
    return a
  end
  local a = arena('jack')
  a.boss.aura = 'Hydro'
  a.boss.auraEnd = 10
  a:hit(1, 1, 'Pyro')
  assert(a:hero().charged)
  a = arena('penny')
  a:hero().hp = 50
  a.boss.aura = 'Pyro'
  a.boss.auraEnd = 10
  a:hit(1, 1, 'Hydro')
  assert(a:hero().hp == 58)
  a.boss.aura = 'Pyro'
  a.boss.auraEnd = 10
  a:hit(1, 1, 'Hydro')
  assert(a:hero().hp == 58)
  a = arena('flint')
  a:hit(1, 1, 'Geo')
  assert(a:hero().shield == 12)
  a = arena('gale')
  a:dodgeStart(1, 0)
  assert(a:hero().haste == 2)
  a = arena('zephyr')
  a:hero().cd = 4
  a.boss.aura = 'Pyro'
  a.boss.auraEnd = 10
  a:hit(1, 1, 'Anemo')
  assert(a:hero().cd == 3)
  a = arena('crown')
  a.boss.aura = 'Pyro'
  a.boss.auraEnd = 10
  a:hit(1, 1, 'Gravity')
  assert(a.boss.stagger == 56)
  a = arena('oracle')
  a.boss.aura = 'Pyro'
  a.boss.auraEnd = 10
  a:hit(1, 1, 'Gravity')
  assert(a:hero().shield == 16)
  a = arena('null')
  a:hero().charge = 3
  a.boss.aura = 'Pyro'
  a.boss.auraEnd = 10
  a:hit(1, 1, 'Antimatter')
  assert(a:hero().charge == 0)
  assert(a.boss.hp == 9931)
  a = arena('clover')
  a.boss.aura = 'Hydro'
  a.boss.auraEnd = 10
  a:hit(1, 1, 'Dendro')
  assert(a.effects[1].damage == 48)
  a = arena('count')
  a.boss.aura = 'Hydro'
  a.boss.auraEnd = 10
  a:hit(1, 1, 'Electro')
  assert(a.effects[1].damage == 12)
  a = arena('match')
  a.boss.aura = 'Dendro'
  a.boss.auraEnd = 10
  a:hit(1, 1, 'Pyro')
  assert(a.effects[1].ticks == 6)
  a = arena('dealer')
  a.run.team[2] = H.instance('volt')
  a:hit(1, 1, 'Hydro')
  a:switch(2)
  assert(a:hero().charged and a:hero().switchBuff == 4)
  a = arena('mason')
  a:hero().shield = 10
  a:hit(1, 10)
  assert(a.boss.hp == 9988)
  a = arena('whiteout')
  a.boss.immune = 3
  a:hit(1, 20)
  assert(a.boss.hp == 9975)
  a = arena('briar')
  a.effects = { {} }
  a:hit(1, 20, 'Dendro')
  assert(a.boss.hp == 9976)
  a = arena('laugh')
  a.boss.hp = 2000
  a:hit(1, 100)
  assert(a.boss.hp == 1885)
end)
test('first shop guaranteed unowned affordable Common', function()
  for seed = 1, 500 do
    local r = M.new(seed)
    M.choose(r, 1)
    M.enter(r)
    M.reward(r)
    M.shop(r)
    assert(H.byId[r.stock[1].id].rarity == 1)
    assert(r.stock[1].id ~= r.team[1].id and r.gold >= r.stock[1].price)
  end
end)
test('atomic purchases, replacement, sales and inventory overflow', function()
  local r = shop()
  r.gold = 200
  assert(M.buy(r, 1))
  unchanged(r, function()
    return M.buy(r, 1)
  end)
  assert(M.buy(r, 2))
  assert(#r.team == 3)
  M.reroll(r)
  unchanged(r, function()
    return M.buy(r, 1)
  end)
  r.team[1].weapon = 'scepter'
  r.weapons = { 'scepter', 'scepter', 'scepter', 'scepter', 'scepter', 'scepter' }
  unchanged(r, function()
    return M.buy(r, 1, 1)
  end)
  unchanged(r, function()
    return M.sellHero(r, 1)
  end)
  table.remove(r.weapons)
  local oldGold = r.gold
  local oldPaid = r.team[1].paid
  assert(M.buy(r, 1, 1))
  assert(#r.team == 3 and #r.weapons == 6)
  assert(r.gold == oldGold - r.stock[1].price + math.floor(oldPaid / 2))
  assert(M.sellHero(r, 3))
  assert(M.sellHero(r, 2))
  unchanged(r, function()
    return M.sellHero(r, 1)
  end)
  r.gold = 0
  unchanged(r, function()
    return M.reroll(r)
  end)
  unchanged(r, function()
    return M.buy(r, 4)
  end)
end)
test('equipment swap and capacities', function()
  local r = shop()
  r.weapons = { 'scepter' }
  assert(M.equip(r, 1, 1))
  assert(#r.weapons == 0)
  r.weapons = { 'scepter' }
  assert(M.equip(r, 1, 1))
  assert(#r.weapons == 1)
  assert(M.unequip(r, 1))
  assert(#r.weapons == 2)
  r.consumables = { 'flask', 'flask' }
  unchanged(r, function()
    return M.buy(r, 5)
  end)
  r.curios = { 'die' }
  r.stock[4].id = 'die'
  unchanged(r, function()
    return M.buy(r, 4)
  end)
  r.stage = 'arena'
  unchanged(r, function()
    return M.equip(r, 1, 1)
  end)
end)
test('consumables do not waste invalid uses', function()
  local r = run()
  r.consumables = { 'flask', 'wind' }
  local a = A.new(r)
  assert(not a:consume(1))
  assert(not a:consume(2))
  a:hero().hp = 80
  assert(a:consume(1))
  assert(a:hero().hp == 110 and #r.consumables == 1)
  a:hero().cd = 1
  assert(a:consume(1))
  assert(a:hero().cd == 0)
end)
test('ten floors and two complete Hell cycles with saves', function()
  local r = run()
  for floor = 1, 30 do
    assert(r.floor == floor)
    assert(M.enter(r))
    local saved = S.encode(r)
    local entry = assert(S.decode(saved))
    assert(S.resume(entry).stage == 'preview')
    r.team[1].hp = 1
    assert(M.reward(r, { damage = 100, time = 10, reactions = 2 }))
    local gold = r.gold
    assert(not M.reward(r))
    assert(r.gold == gold and r.team[1].hp == r.team[1].maxhp)
    if floor == 10 then
      assert(r.key and r.stage == 'victory')
      local finished = U.copy(r)
      assert(M.finish(finished))
      assert(finished.stage == 'complete')
    end
    assert(M.shop(r))
    if floor == 10 then
      assert(H.byId[r.stock[1].id].rarity == 4 and r.gold >= r.stock[1].price)
    end
    local before = S.encode(r)
    r = assert(S.decode(before))
    assert(S.encode(r) == before)
    assert(M.next(r))
  end
  assert(r.stats.clears == 30 and r.floor == 31 and r.key)
end)
test('corrupt, future, malicious, absent and unavailable saves', function()
  assert(not S.decode('{bad'))
  assert(not S.decode('os.execute("echo nope")'))
  local r = run()
  r.version = 2
  assert(not S.decode(C.encode(r)))
  r = run()
  r.team[1].id = 'unknown'
  assert(not S.decode(C.encode(r)))
  r = run()
  r.team[1].cd = 'bad'
  assert(not S.decode(C.encode(r)))
  assert(not S.read({
    getInfo = function()
      return nil
    end,
  }))
  local _, err = S.read({
    getInfo = function()
      error('blocked')
    end,
  })
  assert(err)
  local ok = S.write(run(), {
    write = function()
      return false
    end,
  })
  assert(not ok)
end)
test('save boundary restarts exact entry and does not reroll stock', function()
  local r = run()
  M.enter(r)
  local saved = S.encode(r)
  r.team[1].hp = 10
  r.consumables = {}
  local loaded = S.resume(assert(S.decode(saved)))
  assert(loaded.team[1].hp == 110 and loaded.stage == 'preview')
  M.enter(loaded)
  M.reward(loaded)
  M.shop(loaded)
  local stock = snapshot(loaded.stock)
  local copy = assert(S.decode(S.encode(loaded)))
  assert(snapshot(copy.stock) == stock and copy.shopRng.seed == loaded.shopRng.seed)
end)
test('demo, restart resets and draft separation', function()
  local r = M.new(77, 'demo')
  M.choose(r, 1)
  for i = 1, 2 do
    M.enter(r)
    M.reward(r)
    if i == 1 then
      M.shop(r)
      M.next(r)
    end
  end
  assert(r.stage == 'complete')
  local n = M.new(77, 'run')
  assert(n.gold == 10 and #n.team == 0 and not n.key and n.floor == 1)
  local draft = snapshot(n.offers)
  U.random(n.shopRng)
  assert(snapshot(n.offers) == draft)
end)
require('tests.combat')(test, run)
require('tests.content')(test, run, shop)
require('tests.bosses')(test, run)
require('tests.ui')(test)
require('tests.reliability')(test)
require('tests.sprites')(test)
require('tests.art')(test)
print(('ALL %d SCENARIOS PASSED'):format(total))
