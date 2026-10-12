return function(test, run)
  local A = require('src.combat.arena')
  local B = require('src.data.bosses')
  local P = require('src.combat.patterns')
  local M = require('src.run.model')
  local H = require('src.data.heroes')
  local U = require('src.core.util')
  local C = require('src.core.codec')
  local S = require('src.core.save')
  local function encounter(floor)
    local r = run('jack')
    r.floor = floor
    r.rewarded = floor - 1
    r.key = floor > 10
    return r
  end
  test('difficulty climbs through normal and Hell floors; pursuit locks to the warned position', function()
    local previousHP, previousDamage = 0, 0
    for floor = 1, 110 do
      local a = A.new(encounter(floor))
      assert(a.boss.maxhp >= previousHP and a.incoming >= previousDamage)
      previousHP, previousDamage = a.boss.maxhp, a.incoming
    end
    local first, final = A.new(encounter(1)), A.new(encounter(10))
    assert(first.boss.maxhp == 308 and first.incoming == 18)
    assert(final.boss.maxhp > 1150 and final.incoming > 32)
    final.pattern = 2
    final.x, final.y = 140, 210
    P.cast(final)
    local pursuit = final.hazards[#final.hazards]
    assert(pursuit.kind == 'slam' and pursuit.r == 72 and pursuit.warning == 1.85)
    final.x, final.y = -140, -210
    assert(pursuit.x == 140 and pursuit.y == 210, 'warning must never chase the player')
    assert(final.attackTimer >= 2.2 and final.attackTimer < 3.2)
    local early = A.new(encounter(4))
    assert(not early.difficulty.pursuit)
  end)
  test('guard, resistance, reaction breaks and timed solo openings', function()
    local a = A.new(encounter(10))
    local function damage(element)
      local hp = a.boss.hp
      a:hit(1, 100, element)
      return hp - a.boss.hp
    end
    assert(a:guarded() and damage(nil) == 45)
    assert(damage('Antimatter') == 27, 'matching the boss element is resisted')
    a.boss.aura = nil
    a.boss.guardBreak = 0
    a:hit(1, 10, 'Pyro')
    a:hit(1, 10, 'Hydro')
    assert(a.boss.guardBreak == 2.5 and not a:guarded())
    assert(damage(nil) == 100)
    a.boss.guardBreak = 0
    a.attackTimer = 0.7
    assert(not a:guarded() and damage(nil) == 100, 'solo heroes have a timed opening')
    a.attackTimer = 2
    a.boss.stun = 1
    assert(not a:guarded() and damage(nil) == 130)
    a.boss.stun = 0
    assert(a:guarded(), 'guard returns after the opening')
  end)
  test('switching cannot reset attack or dodge recovery; death still selects a survivor', function()
    local r = encounter(10)
    r.team = { H.instance('jack'), H.instance('penny'), H.instance('flint') }
    local a = A.new(r)
    assert(a:attack(0, -100))
    a:dodgeStart(1, 0)
    assert(a:switch(2))
    assert(not a:switch(3))
    a.dodge = 0
    assert(not a:attack(0, -100), 'shared basic recovery survives switching')
    a:dodgeStart(0, 1)
    assert(a.dodge == 0 and r.team[2].dodgeCd == 0, 'fresh hero cannot bypass shared dodge recovery')
    a.invuln = 0
    r.team[2].hp = 1
    a:damageHero(5)
    assert(a.active ~= 2 and a:hero().hp > 0 and not a.result)
    a.hitstop = 0
    for i = 1, 30 do
      a:update(0.05, 0, 0)
    end
    assert(a:switch(3), 'switch lock must recover')
  end)
  test('three heroes cannot face-tank late bosses, but warning-aware play wins', function()
    for _, floor in ipairs({ 8, 10, 20 }) do
      for _, mode in ipairs({ 'camping', 'bot' }) do
        local r = encounter(floor)
        r.team = { H.instance('jack'), H.instance('penny'), H.instance('flint') }
        local a = A.new(r)
        a.x, a.y = 0, 0
        for i = 1, 12000 do
          require('tests.' .. mode)(a)
          if a.result then
            break
          end
        end
        assert(a.result == (mode == 'camping' and 'defeat' or 'victory'), mode .. ' floor ' .. floor)
      end
    end
  end)
  test('run route previews correct bosses without mutating progress or RNG', function()
    local r = encounter(9)
    local before = C.encode(r)
    local route = M.route(r)
    assert(route[1].floor == 9 and route[2].boss.id == 'throne' and route[3].hell)
    assert(C.encode(r) == before)
    r.stage = 'shop'
    assert(M.route(r)[1].floor == 10)
    r.floor, r.stage = 10, 'victory'
    assert(M.route(r)[1].boss.hellName == 'Infernal Bailiff')
    r.mode, r.floor, r.stage = 'demo', 1, 'shop'
    assert(#M.route(r) == 1 and M.route(r)[1].boss.id == 'bailiff')
    r.stage = 'complete'
    assert(#M.route(r) == 0)
  end)
  test('20 named encounters, deterministic patterns and phase changes', function()
    local names, signatures = {}, {}
    for floor = 1, 20 do
      local r = encounter(floor)
      local a, b = A.new(r), A.new(U.copy(r))
      local name = a.hell and a.encounter.hellName or a.encounter.name
      assert(not names[name])
      names[name] = true
      local sequence = {}
      for phase = 1, (floor % 10 == 0 and 3 or 2) do
        a.phase, b.phase = phase, phase
        for turn = 1, 6 do
          a.pattern, b.pattern = turn, turn
          a.hazards, b.hazards = {}, {}
          P.cast(a)
          P.cast(b)
          assert(C.encode(a.hazards) == C.encode(b.hazards))
          assert(#a.hazards <= 12 and a.attackTimer >= 2.2)
          for _, h in ipairs(a.hazards) do
            assert(h.warning >= 1.05)
          end
          sequence[#sequence + 1] = C.encode({ hazards = a.hazards, interval = a.attackTimer })
          -- Every combination leaves space for a hero, not a full-arena unavoidable hit.
          local safe = 0
          for x = -300, 300, 50 do
            for y = -300, 300, 50 do
              local blocked = false
              for _, h in ipairs(a.hazards) do
                if P.inside(h, x, y, 16) then
                  blocked = true
                end
              end
              if not blocked then
                safe = safe + 1
              end
            end
          end
          assert(safe >= 10, 'no safe space: ' .. name)
        end
      end
      local signature = table.concat(sequence)
      assert(not signatures[signature], 'duplicate encounter patterns: ' .. name)
      signatures[signature] = true
      a = A.new(encounter(floor))
      a.boss.hp = a.boss.maxhp * 0.3
      a:update(0.02, 0, 0)
      assert(a.phase == (floor % 10 == 0 and 3 or 2))
    end
  end)
  test('ring gaps, sweep geometry, pillar collision and gravity escape', function()
    local h = { kind = 'ring', x = 0, y = 0, r = 100, width = 20, gap = 0, gapWidth = 0.7 }
    assert(not P.inside(h, 100, 0))
    assert(P.inside(h, -100, 0))
    assert(not P.inside(h, 0, 0))
    assert(P.inside({ kind = 'sweep', x = 0, y = 0, dx = 1, dy = 0, r = 32 }, 100, 10))
    local a = A.new(encounter(4))
    a.x, a.y = 0, 0
    a.hazards = { { kind = 'pillar', x = 0, y = 0, r = 46, t = 0, active = 4 } }
    P.update(a, 0.05)
    assert(U.dist(a.x, a.y, 0, 0) >= 60)
    a.hazards =
      { { kind = 'gravity', x = 0, y = 0, r = 290, gap = 0, gapWidth = 0.65, force = 65, t = 0, active = 3 } }
    a.x, a.y = 150, 0
    P.update(a, 0.05)
    assert(a.x == 150)
    a.x, a.y = -150, 0
    P.update(a, 0.05)
    assert(a.x > -150)
  end)
  test('100 Hell floors: bounded hazards, speed, damage, HP and save boundaries', function()
    for floor = 11, 110 do
      local r = encounter(floor)
      M.enter(r)
      local a = A.new(r)
      a.debugInvulnerable = true
      for step = 1, 800 do
        if step == 260 then
          a.boss.hp = a.boss.maxhp * 0.49
        end
        if step == 520 then
          a.boss.hp = a.boss.maxhp * 0.25
        end
        a:update(0.05, math.sin(step * 0.01), math.cos(step * 0.01))
        assert(#a.hazards <= 12 and #a.enemyProjectiles <= 12 and #a.labels <= 40)
        assert(a.x == a.x and a.y == a.y and math.abs(a.x) <= 350 and math.abs(a.y) <= 350)
        assert(a.boss.maxhp <= 8400 and a.incoming <= 64)
      end
      assert(M.reward(r))
      assert(S.decode(S.encode(r)))
    end
    local a = A.new(encounter(1000000))
    assert(a.boss.maxhp == 8400 and a.incoming == 64)
  end)
  -- Avoidance agent uses the same controls/cooldowns/hit pipeline as a player.
  local bot = require('tests.bot')
  test('normal and first-cycle Hell encounters beatable through live combat controls', function()
    for floor = 1, 20 do
      local r = encounter(floor)
      r.team = { H.instance('jack'), H.instance('penny'), H.instance('flint') }
      M.enter(r)
      local a = A.new(r)
      for step = 1, 6000 do
        bot(a)
        if a.result then
          break
        end
      end
      assert(
        a.result == 'victory',
        a.encounter.name .. ' floor ' .. floor .. ' result ' .. tostring(a.result)
      )
      assert(M.reward(r, a.stats))
      if floor == 10 then
        assert(r.key and r.stage == 'victory')
        M.shop(r)
        M.next(r)
        assert(r.floor == 11)
      end
    end
  end)
end
