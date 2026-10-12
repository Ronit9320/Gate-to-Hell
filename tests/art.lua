return function(test)
  test('selected cutout effects cache, fade, freeze motion and fall back safely', function()
    local old = love
    local uploads, calls, colors = 0, {}, {}
    love = {
      filesystem = {
        getInfo = function(path)
          return not path:find('critical')
        end,
      },
      graphics = {
        newImage = function()
          uploads = uploads + 1
          return {
            setFilter = function() end,
            getDimensions = function()
              return 2048, 2048
            end,
          }
        end,
        setColor = function(...)
          colors[#colors + 1] = { ... }
        end,
        draw = function(...)
          calls[#calls + 1] = { ... }
        end,
      },
    }
    local F = dofile('src/render/authored_fx.lua')
    assert(F.draw('hit', 10, 20, 85, 0.1, false, 0))
    assert(F.draw('hit', 10, 20, 85, 0.9, false, 0))
    assert(uploads == 1 and colors[1][4] > colors[2][4])
    F.draw('slash', 10, 20, 100, 0.1, true, 0.5)
    F.draw('slash', 10, 20, 100, 0.9, true, 0.5)
    assert(calls[3][4] == calls[4][4] and calls[3][5] == calls[4][5])
    assert(not F.draw('critical', 0, 0, 100, 0, false, 0))
    assert(not F.draw('hazard_flame', 0, 0, 100, 0, false, 0))
    assert(uploads == 2, 'missing and unselected art must use the existing renderer')
    love = old
  end)
  test('all boss appearances, stagger/recovery and shared cache stay bounded', function()
    local B = require('src.data.boss_sprites')
    local A = require('src.render.atlas')
    assert(B.appearance('throne', true, 3) == 'throne_hell_phase3')
    assert(A.pose({ hp = 10, stun = 1 }, 3, false, B) == 'stagger')
    assert(A.pose({ hp = 10, stun = 0, spriteRecoveryAt = 2 }, 2.1, false, B) == 'recovery')
    local old = love
    local uploads, releases = 0, 0
    love = { filesystem = {
      getInfo = function()
        return {}
      end,
    }, graphics = {} }
    local G = love.graphics
    G.newImage = function()
      uploads = uploads + 1
      return {
        setFilter = function() end,
        release = function()
          releases = releases + 1
        end,
        getDimensions = function()
          return 1536, 960
        end,
      }
    end
    G.newQuad = function(x, y, w, h)
      assert(x >= 0 and y >= 0 and x + w <= 1536 and y + h <= 960)
      return {}
    end
    G.setColor = function() end
    G.draw = function() end
    package.loaded['src.render.sprites'] = nil
    local S = require('src.render.sprites')
    for _, boss in ipairs(require('src.data.bosses').list) do
      for _, hell in ipairs({ false, true }) do
        if boss.id ~= 'bailiff' or hell then
          for phase = 1, boss.id == 'throne' and 3 or 1 do
            for d = 0, 7 do
              local angle = d * math.pi / 4
              local arena = {
                x = math.sin(angle),
                y = math.cos(angle),
                time = 1,
                hell = hell,
                phase = phase,
                boss = { x = 0, y = 0, hp = 10, stun = 0 },
              }
              assert(S.drawBoss(boss.id, 0, 0, arena, false))
              local count = 0
              for _ in pairs(S.sheets) do
                count = count + 1
              end
              assert(count <= 2)
            end
          end
        end
      end
    end
    assert(uploads == 184 and releases == 182)
    love = old
    package.loaded['src.render.sprites'] = nil
  end)
  test('dedicated effect frames, invalid assets and texture memory budget', function()
    local old = love
    love = { filesystem = {
      getInfo = function()
        return {}
      end,
    }, graphics = {} }
    local G = love.graphics
    local releases = 0
    G.newImage = function()
      return {
        setFilter = function() end,
        release = function()
          releases = releases + 1
        end,
        getDimensions = function()
          return 512, 256
        end,
      }
    end
    G.newQuad = function(x, y, w, h)
      assert(x >= 0 and y >= 0 and x + w <= 512 and y + h <= 256)
      return {}
    end
    G.setColor = function() end
    G.draw = function() end
    package.loaded['src.render.combat_art'] = nil
    local C = require('src.render.combat_art')
    assert(C.frame(-1, false) == 0 and C.frame(10, false) == 7 and C.frame(0.9, true) == 3)
    assert(not C.draw('missing', 0, 0, 80, 0, false))
    local count = 0
    for id in pairs(require('src.data.combat_art')) do
      assert(C.draw(id, 0, 0, 80, 0.5, false))
      count = count + 1
      local n = 0
      for _ in pairs(C.images) do
        n = n + 1
      end
      assert(n <= 16)
    end
    assert(count == 91 and releases == count - 16)
    love = old
    package.loaded['src.render.combat_art'] = nil
  end)
  test('hazard artwork masks exclude every point of the open ring gap', function()
    local old = love
    local polygons = {}
    local restored = false
    love = {
      graphics = {
        getStencilTest = function()
          return nil
        end,
        setStencilTest = function(mode)
          if mode == nil then
            restored = true
          end
        end,
        stencil = function(fn)
          fn()
        end,
        polygon = function(_, ...)
          polygons[#polygons + 1] = { ... }
        end,
      },
    }
    package.loaded['src.render.combat_art'] = nil
    local C = require('src.render.combat_art')
    local draw = C.draw
    C.draw = function()
      return true
    end
    local I = require('src.render.iso')
    local P = require('src.combat.patterns')
    for _, kind in ipairs({ 'ring', 'gravity' }) do
      polygons = {}
      restored = false
      local h = {
        kind = kind,
        x = 0,
        y = -100,
        r = 290,
        width = 23,
        gap = 0.3,
        gapWidth = 0.7,
        force = 65,
        t = -0.4,
        active = 3,
        warning = 1.2,
      }
      assert(C.hazard({ time = 1, encounter = { id = 'undertow', element = 'Hydro' } }, h, false))
      assert(#polygons > 0 and restored)
      for _, poly in ipairs(polygons) do
        for j = 1, #poly, 2 do
          local x, y = I.inverse(poly[j], poly[j + 1])
          local r = math.sqrt(x * x + (y + 100) ^ 2)
          if r > 1 then
            assert(not P.inGap(h, x, y), 'Art mask invaded a safe sector')
          end
        end
      end
    end
    C.draw = draw
    love = old
    package.loaded['src.render.combat_art'] = nil
  end)
  test('skill, reaction, reload, shield and consumable events select authored art', function()
    local H = require('src.data.heroes')
    local M = require('src.run.model')
    local Arena = require('src.combat.arena')
    local meta = require('src.data.combat_art')
    for _, hero in ipairs(H.list) do
      local r = M.new(8)
      r.team = { H.instance(hero.id) }
      r.stage = 'arena'
      r.encounterSeed = 8
      local a = Arena.new(r)
      assert(a:attack(0, -100, true))
      assert(a.feedback[1].art == 'skill_' .. hero.id and meta[a.feedback[1].art])
      for _, p in ipairs(a.projectiles) do
        assert(p.hero == hero.id and meta[p.art])
      end
      for _, f in ipairs(a.fields) do
        assert(f.hero == hero.id and meta[f.art])
      end
    end
    local r = M.new(8)
    r.team = { H.instance('penny') }
    r.stage = 'arena'
    r.encounterSeed = 8
    r.consumables = { 'flask', 'aegis', 'wind' }
    local a = Arena.new(r)
    a.boss.aura = 'Pyro'
    a.boss.auraEnd = 6
    a:hit(1, 1, 'Hydro')
    local seen = {}
    for _, f in ipairs(a.feedback) do
      if f.art then
        seen[f.art] = true
      end
    end
    assert(seen.reaction_steam_burst)
    local h = a:hero()
    h.ammo = 0
    a:reloadStart()
    assert(a.feedback[#a.feedback].kind == 'reload_start')
    h.reload = 0.01
    a.hitstop = 0
    a:update(0.02, 0, 0)
    assert(a.feedback[#a.feedback].kind == 'reload_complete')
    h.hp = h.maxhp - 10
    assert(a:consume(1))
    assert(a.feedback[#a.feedback].art == 'consume_flask')
    assert(a:consume(1))
    a.invuln = 0
    a:damageHero(100)
    seen = {}
    for _, f in ipairs(a.feedback) do
      seen[f.kind] = true
    end
    assert(seen.shield_break)
    h.cd = 5
    assert(a:consume(1))
    assert(a.feedback[#a.feedback].art == 'consume_wind')
  end)
end
