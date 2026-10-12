return function(test)
  local M = require('src.run.model')
  local H = require('src.data.heroes')
  local S = require('src.core.save')
  local A = require('src.combat.arena')
  local bot = require('tests.bot')
  local C = require('src.core.codec')
  local function shopping(r)
    -- Spend earned gold through ordinary transactions; no injected currency/items.
    for i = 1, 2 do
      if #r.team < 3 and r.gold >= r.stock[i].price then
        M.buy(r, i)
      end
    end
    if r.gold >= r.stock[3].price then
      for hi, h in ipairs(r.team) do
        if not h.weapon then
          if M.buy(r, 3) then
            M.equip(r, #r.weapons, hi)
          end
          break
        end
      end
    end
    if r.gold >= r.stock[4].price then
      M.buy(r, 4)
    end
    if r.gold >= r.stock[5].price then
      M.buy(r, 5)
    end
  end
  test('full ten-floor runs from every Common and representative higher rarities', function()
    local report = {}
    for _, id in ipairs({ 'jack', 'penny', 'gale', 'flint', 'frost', 'whiteout', 'crown', 'null' }) do
      local r
      for seed = 1, 10000 do
        local candidate = M.new(seed)
        for i, offer in ipairs(candidate.offers) do
          if offer == id then
            M.choose(candidate, i)
            r = candidate
            break
          end
        end
        if r then
          break
        end
      end
      assert(r, 'starter unavailable')
      local seconds = 0
      for floor = 1, 10 do
        assert(M.enter(r))
        local a = A.new(r)
        for step = 1, 12000 do
          bot(a)
          if a:hero().hp < a:hero().maxhp * 0.5 then
            a:consume(1)
          end
          if a.result then
            break
          end
        end
        assert(a.result == 'victory', id .. ' floor ' .. floor .. ' ' .. tostring(a.result))
        seconds = seconds + a.time
        a.stats.time = a.time
        assert(M.reward(r, a.stats))
        assert(S.decode(S.encode(r)))
        if floor < 10 then
          assert(M.shop(r))
          shopping(r)
          assert(M.next(r))
        end
      end
      assert(r.key and r.stage == 'victory' and r.stats.clears == 10)
      report[#report + 1] = {
        starter = id,
        combatSeconds = math.floor(seconds),
        gold = r.gold,
        teamSize = #r.team,
        reactions = r.stats.reactions,
      }
    end
    os.execute('mkdir -p .test-results')
    local f = assert(io.open('.test-results/balance.json', 'w'))
    f:write(C.encode(report))
    f:close()
  end)
  test('visual pools reuse bounded records under sustained combat', function()
    local r = M.new(4)
    M.choose(r, 1)
    local a = A.new(r)
    a.debugInvulnerable = true
    a.boss.hp = 10000000
    a.boss.maxhp = 10000000
    for i = 1, 5000 do
      a:hit(1, 1)
      a:update(0.02, 0, 0)
      assert(#a.sparks <= 80 and #a.labels <= 40)
    end
    assert(a.sparkPool.created <= 80 and a.labelPool.created <= 40)
  end)
  test('rapid switching, restarts and late Hell remain bounded', function()
    for seed = 1, 60 do
      local r = M.new(seed)
      M.choose(r, 1)
      r.team = { H.instance('jack'), H.instance('penny'), H.instance('flint') }
      r.floor = 1010
      r.key = true
      r.rewarded = 1009
      local a = A.new(r)
      a.debugInvulnerable = true
      for step = 1, 1000 do
        a:switch(step % 3 + 1)
        a:attack(0, -100, true)
        a:update(0.02, math.sin(step), math.cos(step))
      end
      assert(#a.fields <= 24 and #a.effects <= 12 and #a.projectiles <= 80)
      assert(a.boss.hp == a.boss.hp)
    end
  end)
end
