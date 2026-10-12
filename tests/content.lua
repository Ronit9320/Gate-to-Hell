return function(test, run, shop)
  local A = require('src.combat.arena')
  local E = require('src.combat.equipment')
  local H = require('src.data.heroes')
  local M = require('src.run.model')
  local S = require('src.core.save')
  local Items = require('src.data.items')
  local function arena(id, curios, weapon)
    local r = run(id)
    r.curios = curios or {}
    r.team[1].weapon = weapon
    local a = A.new(r)
    a.boss.hp, a.boss.maxhp = 10000, 10000
    return a
  end
  local function damage(id, curios, weapon, element, aura)
    local a = arena(id, curios, weapon)
    a.boss.aura, a.boss.auraEnd = aura, 100
    a:hit(1, 100, element)
    return a, 10000 - a.boss.hp
  end
  test('all 23 items obtainable, purchasable, equippable and saveable', function()
    local counts, seen = { weapon = 0, curio = 0, consumable = 0 }, {}
    for id, d in pairs(Items) do
      counts[d.kind] = counts[d.kind] + 1
      local r = shop()
      r.gold = 100
      r.stock[3] = { id = id, kind = d.kind, price = d.price }
      assert(M.buy(r, 3), id)
      if d.kind == 'weapon' then
        assert(M.equip(r, 1, 1))
        assert(r.team[1].weapon == id)
      end
      assert(S.decode(S.encode(r)))
    end
    assert(counts.weapon == 8 and counts.curio == 12 and counts.consumable == 3)
    local r = shop()
    for i = 1, 500 do
      M.stock(r, false)
      for j = 3, 5 do
        seen[r.stock[j].id] = true
      end
    end
    for id in pairs(Items) do
      assert(seen[id], id .. ' unavailable in shop')
    end
  end)
  test('weapons neutral bonuses, elemental skills, shields and stagger', function()
    for id, d in pairs(Items) do
      if d.kind == 'weapon' then
        local a = arena('jack', {}, id)
        a:attack(0, -100)
        assert(a.swings[1].damage == H.byId.jack.basic + d.attack, id)
        local ranged = arena('penny', {}, id)
        ranged:attack(0, -100)
        assert(ranged.projectiles[1].damage == H.byId.penny.basic + d.attack, id)
      end
    end
    for _, spec in ipairs({
      { 'jack', 'ember', 'Pyro' },
      { 'penny', 'tide', 'Hydro' },
      {
        'gale',
        'gale',
        'Anemo',
      },
    }) do
      local _, n = damage(spec[1], {}, spec[2], spec[3])
      assert(n == 120)
      local _, neutral = damage(spec[1], {}, spec[2])
      assert(neutral == 100)
    end
    local a = damage('flint', {}, 'quarry', 'Geo')
    assert(math.abs(a:hero().shield - 15.6) < 0.001)
    a = damage('frost', {}, 'rime', 'Cryo')
    assert(math.abs(a.boss.stagger - 7.8) < 0.001)
    a = arena('jack', {}, 'scepter')
    a.run.team[2] = H.instance('penny')
    a:switch(2)
    a:switch(1)
    a:hit(1, 100, 'Pyro')
    assert(a.lastHit.actual == 125)
    a:update(0.05, 0, 0)
    assert(a:hero().switchBuff < 4)
  end)
  test('reaction items respect both pair orders and never recurse', function()
    for _, spec in ipairs({ { 'thorn', 'Dendro', 'Pyro', 8.75 }, { 'coil', 'Electro', 'Hydro', 10 } }) do
      for order = 1, 2 do
        local a = arena('gale', {}, spec[1])
        local x, y = spec[2], spec[3]
        if order == 2 then
          x, y = y, x
        end
        a.boss.aura, a.boss.auraEnd = x, 100
        a:hit(1, 1, y)
        assert(a.effects[1].damage == spec[4])
        assert(a.stats.reactions == 1)
        for i = 1, 100 do
          a:update(0.05, 0, 0)
        end
        assert(a.stats.reactions == 1 and #a.effects == 0)
      end
    end
    local a = arena('gale', { 'fuse', 'green', 'copper' })
    a.boss.aura, a.boss.auraEnd = 'Dendro', 100
    a:hit(1, 1, 'Hydro')
    assert(a.effects[1].damage == 50) -- 32 * 1.25 * 1.25
    a = arena('gale', { 'copper', 'fuse' })
    a.boss.aura, a.boss.auraEnd = 'Electro', 100
    a:hit(1, 1, 'Pyro')
    assert(a.stats.reactions == 1 and a.lastHit.actual == 38)
    a = arena('gale', { 'green' })
    a.boss.aura, a.boss.auraEnd = 'Dendro', 100
    a:hit(1, 1, 'Pyro')
    assert(a.effects[1].damage == 8.75)
  end)
  test('persistent skill ticks apply aura only once and receive periodic equipment bonuses', function()
    local a = arena('briar', { 'green' }, 'thorn')
    a.x, a.y = 0, 0
    a:attack(0, -100, true)
    for i = 1, 14 do
      a:update(0.05, 0, 0)
    end
    assert(a.boss.aura == 'Dendro')
    a.boss.aura, a.boss.auraEnd = 'Pyro', 100
    local before = a.stats.reactions
    for i = 1, 13 do
      a:update(0.05, 0, 0)
    end
    assert(a.boss.aura == 'Pyro' and a.stats.reactions == before)
    assert(a.lastHit.kind == 'periodic' and math.abs(a.lastHit.mult - 1.5625) < 0.001)
    a = arena('count', {}, 'coil')
    a.x, a.y = 0, 0
    a:attack(0, -100, true)
    for i = 1, 27 do
      a:update(0.05, 0, 0)
    end
    assert(a.lastHit.kind == 'periodic' and a.lastHit.mult == 1.25)
  end)
  test('all Curio effects and sell/reward health invariants', function()
    local _, n = damage('jack', { 'ash' }, nil, 'Pyro')
    assert(n == 120)
    local a = damage('jack', { 'ace' }, nil, 'Pyro')
    assert(a.lastHit.actual == 150)
    a:hit(1, 100, 'Pyro')
    assert(a.lastHit.actual == 100)
    a = arena('jack', { 'die' })
    a.rng.seed = 1
    a:hit(1, 100)
    assert(a.lastHit.actual == 150)
    a = arena('penny', { 'rain' })
    a:hero().hp = 10
    a.boss.aura, a.boss.auraEnd = 'Pyro', 10
    a:hit(1, 1, 'Hydro')
    assert(a:hero().hp == 22)
    a.run.consumables = { 'flask' }
    a:consume(1)
    assert(a:hero().hp == 89.5)
    a = arena('gale', { 'tailwind' })
    a:attack(0, -100, true)
    assert(a:hero().haste == 2)
    a = damage('flint', { 'stone' }, nil, 'Geo')
    assert(math.abs(a:hero().shield - 15.6) < 0.001)
    a = damage('frost', { 'cold' }, nil, 'Cryo')
    assert(math.abs(a.boss.stagger - 7.8) < 0.001)
    a = arena('jack', { 'glass' })
    assert(a:hero().maxhp == 88)
    a:hit(1, 100)
    assert(a.lastHit.actual == 125)
    local r = shop()
    r.curios = { 'glass', 'tab' }
    E.refresh(r)
    assert(r.team[1].maxhp == 88)
    assert(S.decode(S.encode(r)))
    M.next(r)
    M.enter(r)
    M.reward(r)
    assert(r.lastReward == 13 and r.team[1].hp == 88)
    M.shop(r)
    assert(M.sellItem(r, 'curios', 1))
    assert(r.team[1].maxhp == 110 and r.team[1].hp == 88)
    assert(S.decode(S.encode(r)))
  end)
  test('shield cap, consumable validation and deferred hit death race', function()
    local a = arena('flint', { 'stone' }, 'quarry')
    for i = 1, 20 do
      a:hit(1, 1, 'Geo')
    end
    assert(a:hero().shield == 30)
    a.run.consumables = { 'aegis', 'aegis' }
    assert(a:consume(1))
    assert(a:hero().shield == 40)
    assert(not a:consume(1) and #a.run.consumables == 1)
    a.run.team[2] = H.instance('penny')
    a:attack(0, -100, true)
    a:damageHero(999)
    for i = 1, 50 do
      a:update(0.02, 0, 0)
    end
    assert(a.active == 2 and a.run.team[1].hp == 0 and not a.result)
  end)
end
