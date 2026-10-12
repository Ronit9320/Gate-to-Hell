return function(test, run)
  local A = require('src.combat.arena')
  local H = require('src.data.heroes')
  local P = require('src.combat.patterns')
  local S = require('src.core.save')
  local function advance(a, seconds)
    for i = 1, math.ceil(seconds / 0.025) do
      a:update(0.025, 0, 0)
    end
  end
  test('neutral dodge follows facing, respects cooldown and stops after results', function()
    local a = A.new(run('jack'))
    local visual = a:visualHero()
    visual.dx, visual.dy = 1, 0
    assert(a:dodgeStart(0, 0))
    assert(a.dodgeX == 1 and a.dodgeY == 0)
    local x = a.x
    advance(a, 0.1)
    assert(a.x > x and not a:dodgeStart(-1, 0))
    a:hero().dodgeCd = 0
    a.result = 'victory'
    assert(not a:dodgeStart(0, 1))
  end)
  test('skill buffer survives short recovery, expires and clears on switch', function()
    local a = A.new(run('penny'))
    a:hero().recovery = 0.1
    assert(not a:requestSkill(0, -100))
    advance(a, 0.15)
    assert(a.skillSequence == 1 and not a.pendingSkill)
    advance(a, 0.1)
    assert(a.skillSequence == 1, 'buffer must fire only once')
    a:hero().cd = 0.5
    a:requestSkill(0, -100)
    advance(a, 0.6)
    assert(a.skillSequence == 1 and not a.pendingSkill, 'stale press must not auto-cast')
    a:hero().recovery = 0.1
    a:requestSkill(0, -100)
    a.run.team[2] = H.instance('jack')
    assert(a:switch(2) and not a.pendingSkill)
    advance(a, 0.2)
    assert(a.skillSequence == 1, 'switch must not transfer queued skill')
  end)
  test('melee basics require range and direction; dodge cancels windup', function()
    local count = 0
    for _, data in ipairs(H.list) do
      if data.style == 'Melee' then
        count = count + 1
        for _, spec in ipairs({ { 220, -100, false }, { 0, 300, false }, { 0, -100, true } }) do
          local a = A.new(run(data.id))
          a.y = spec[1]
          assert(a:attack(0, spec[2]))
          assert(#a.projectiles == 0 and a.boss.hp == a.boss.maxhp)
          advance(a, 0.15)
          assert((a.boss.hp < a.boss.maxhp) == spec[3], data.id)
          if spec[3] then
            assert((a.hitstop or 0) > 0 or a.bossFlash > 0)
          end
        end
      end
    end
    assert(count == 7)
    local a = A.new(run('jack'))
    a.y = 0
    a:attack(0, -100)
    a:dodgeStart(1, 0)
    assert(#a.swings == 0 and a:hero().recovery == 0)
    assert(not a:attack(0, -100))
    advance(a, 0.15)
    assert(a.boss.hp == a.boss.maxhp)
  end)
  test('every ranged kit has finite magazines and a real reload interval', function()
    for _, data in ipairs(H.list) do
      if data.style == 'Ranged' then
        local a = A.new(run(data.id))
        local h = a:hero()
        for shot = 1, data.magazine do
          assert(a:attack(350, 350), data.id)
          assert(not a:attack(350, 350), 'cooldown bypass')
          if shot < data.magazine then
            advance(a, data.basicInterval + 0.025)
          end
        end
        assert(h.ammo == 0 and h.reload == data.reloadDuration)
        advance(a, 0.8)
        assert(not a:attack(350, 350) and h.ammo == 0)
        assert(a:attack(0, -100, true), 'skills must remain usable while reloading')
        advance(a, 0.95)
        assert(h.ammo == data.magazine and h.reload == 0)
        assert(a:attack(350, 350))
      end
    end
  end)
  test('switching preserves ammunition and reload; older saves remain compatible', function()
    local r = run('penny')
    r.team[2] = H.instance('match')
    local a = A.new(r)
    a:attack(350, 350)
    assert(a:reloadStart())
    assert(a:switch(2) and a:switch(1))
    assert(a:hero().ammo == 4 and a:hero().reload > 0)
    a:switch(2)
    advance(a, 1.7)
    assert(r.team[1].ammo == 5 and r.team[1].reload == 0)
    r = run('penny')
    r.team[1].ammo, r.team[1].reload, r.team[1].recovery = nil, nil, nil
    r = assert(S.decode(S.encode(r)))
    a = A.new(r)
    assert(a:hero().ammo == 5 and a:hero().reload == 0)
    r.team[1].ammo = 6
    assert(not pcall(S.encode, r))
  end)
  test('massive impacts fire once on activation, including successful dodges', function()
    local a = A.new(run('penny'))
    a.hazards = { { kind = 'slam', x = 0, y = -100, r = 150, t = 0.1, warning = 0.1, active = 0.28 } }
    P.update(a, 0.05)
    assert(a.impactSequence == 0)
    a:dodgeStart(1, 0)
    local hp, time, cd = a:hero().hp, a.time, a:hero().dodgeCd
    P.update(a, 0.06)
    assert(a.impactSequence == 1 and a.shakePower == 9 and a.impactFrame > 0)
    assert(a:hero().hp == hp)
    a:update(0.025, 1, 0)
    assert(a.time == time and a:hero().dodgeCd == cd, 'impact pause must freeze combat')
    P.update(a, 0.05)
    assert(a.impactSequence == 1, 'impact repeated each active frame')
    advance(a, 0.7)
    assert(a.shake == 0 and a.impactFrame == 0 and #a.feedback == 0)
  end)
  test('attack and impact feedback stays bounded and uses no combat RNG', function()
    local a = A.new(run('penny'))
    local seed = a.rng.seed
    for i = 1, 500 do
      a:feedbackAt('hit', 0, 0)
      a:impact(0, -100, 150)
    end
    assert(#a.feedback == 32 and a.rng.seed == seed)
    advance(a, 1)
    assert(#a.feedback == 0)
  end)
end
