return function(test)
  local A = require('src.render.atlas')
  local meta = require('src.data.bailiff_sprite')
  test('hero animation priority, facing events, switching and save isolation', function()
    local H = require('src.data.heroes')
    local M = require('src.run.model')
    local Arena = require('src.combat.arena')
    local r = M.new(88)
    M.choose(r, 1)
    r.team = { H.instance('jack'), H.instance('penny') }
    M.enter(r)
    local arena = Arena.new(r)
    assert(A.heroPose(arena:visualHero(), 0) == 'idle')
    arena:update(0.025, 1, 0)
    assert(A.heroPose(arena:visualHero(), arena.time) == 'walk')
    assert(arena:visualHero().dx == 1 and arena:visualHero().dy == 0)
    assert(arena:attack(arena.x, arena.y - 100, false))
    local at = arena:visualHero().attackAt
    assert(A.heroPose(arena:visualHero(), arena.time) == 'attack')
    assert(not arena:attack(arena.x, arena.y - 100, false))
    assert(arena:visualHero().attackAt == at, 'Rejected attacks cannot restart the animation')
    assert(arena:switch(2))
    assert(arena:attack(arena.x + 100, arena.y, true))
    assert(A.heroPose(arena:visualHero(), arena.time) == 'skill')
    arena:damageHero(1)
    assert(A.heroPose(arena:visualHero(), arena.time) == 'hurt')
    arena:dodgeStart(0, 1)
    assert(A.heroPose(arena:visualHero(), arena.time) == 'dodge')
    assert(A.heroPose(arena:visualHero(), arena.time, true) == 'idle')
    assert(arena:switch(1))
    assert(arena:visualHero().attackAt == at, 'Visual states belong to individual heroes')
    arena.invuln = 0
    arena:damageHero(100000)
    local dead = arena.heroVisuals.jack
    assert(dead.deathAt and dead.deathX == arena.x and dead.deathY == arena.y)
    assert(A.heroPose(dead, arena.time) == 'death' and arena.active == 2)
    local pose, elapsed = A.heroPose(dead, arena.time, true)
    local hm = require('src.data.hero_sprites')
    local x, y = A.cell(hm, pose, elapsed)
    assert(x == 800 and y == 1152, 'Reduced motion must show the final fallen pose')
    for _, hero in ipairs(r.team) do
      assert(hero.attackAt == nil and hero.deathAt == nil, 'Visual events cannot enter roster saves')
    end
    for name, spec in pairs(hm.animations) do
      for _, t in ipairs({ 0, 0.1, 1000 }) do
        x, y = A.cell(hm, name, t)
        assert(x >= 0 and x + 160 <= 960 and y >= 0 and y + 192 <= 1344)
      end
    end
  end)
  test('hero directional textures stay bounded across roster changes and missing art', function()
    local old = love
    local releases, draws = 0, 0
    love = { filesystem = {
      getInfo = function()
        return {}
      end,
    }, graphics = {} }
    love.graphics.newImage = function()
      return {
        setFilter = function() end,
        getDimensions = function()
          return 960, 1344
        end,
        release = function()
          releases = releases + 1
        end,
      }
    end
    love.graphics.newQuad = function(x, y, w, h)
      return { x = x, y = y, w = w, h = h }
    end
    love.graphics.setColor = function() end
    love.graphics.draw = function(_, q, _, _, _, _, _, ax, ay)
      assert(q.w == 160 and q.h == 192 and ax == 80 and ay == 154)
      draws = draws + 1
    end
    package.loaded['src.render.sprites'] = nil
    local S = require('src.render.sprites')
    local H = require('src.data.heroes')
    for index, hero in ipairs(H.list) do
      for direction = 0, 7 do
        local angle = direction * math.pi / 4
        local arena = {
          time = index,
          heroVisuals = { [hero.id] = { dx = math.sin(angle), dy = math.cos(angle), walking = true } },
        }
        assert(S.drawHero(hero.id, 640, 345, arena, false))
        local count = 0
        for _ in pairs(S.heroSheets) do
          count = count + 1
        end
        assert(count <= 4, 'All hero directions must share the same four-texture budget')
      end
    end
    assert(draws == 144 and releases == 140)
    love.filesystem.getInfo = function()
      return nil
    end
    assert(not S.drawHero('jack', 0, 0, { time = 0 }, false))
    love = old
    package.loaded['src.render.sprites'] = nil
  end)
  test('isometric facing, packed rows, one-shot bounds and reduced motion', function()
    local vectors = { { 0, 1 }, { 1, 1 }, { 1, 0 }, { 1, -1 }, { 0, -1 }, { -1, -1 }, { -1, 0 }, { -1, 1 } }
    for i, v in ipairs(vectors) do
      assert(A.direction(v[1], v[2]) == i - 1)
    end
    assert(A.direction(0, 0) == 0)
    for name, animation in pairs(meta.animations) do
      for _, time in ipairs({ 0, 0.2, 1, 10000 }) do
        local x, y = A.cell(meta, name, time)
        assert(x >= 0 and x + meta.width <= meta.columns * meta.width)
        assert(y >= 0 and y + meta.height <= meta.rows * meta.height)
      end
      local x, y = A.cell(meta, name, 9999, true)
      assert(x == animation.offset % meta.columns * meta.width)
      assert(y == math.floor(animation.offset / meta.columns) * meta.height)
    end
    local x, y = A.cell(meta, 'death', 9999)
    assert(x == 7 * 256 and y == 4 * 256)
    local b = { hp = 100, spriteAttackAt = 1, spriteHurtAt = 1.2 }
    assert(A.pose(b, 1.3) == 'attack')
    assert(A.pose(b, 2) == 'idle')
    b.spriteAttackDuration = 1.1
    local name, elapsed = A.pose(b, 2.1)
    local impactX, impactY = A.cell(meta, name, elapsed + 0.00001)
    assert(name == 'attack' and impactX == 7 * 256 and impactY == 256)
    b.spriteAttackAt = nil
    b.spriteHurtAt = 2
    assert(A.pose(b, 2.1) == 'hurt')
    b.hp = 0
    b.spriteDeathAt = 2
    assert(A.pose(b, 3) == 'death')
  end)
  test('directional atlas cache stays bounded and missing files keep fallback', function()
    local old = love
    local releases, draws = 0, 0
    love = { filesystem = {
      getInfo = function()
        return {}
      end,
    }, graphics = {} }
    love.graphics.newImage = function()
      return {
        setFilter = function() end,
        getDimensions = function()
          return 2048, 1280
        end,
        release = function()
          releases = releases + 1
        end,
      }
    end
    love.graphics.newQuad = function(x, y, w, h)
      return { x = x, y = y, w = w, h = h }
    end
    love.graphics.setColor = function() end
    love.graphics.draw = function(_, q, _, _, _, _, _, ax, ay)
      assert(q.w == 256 and q.h == 256 and ax == 128 and ay == 204)
      draws = draws + 1
    end
    package.loaded['src.render.sprites'] = nil
    local S = require('src.render.sprites')
    for i = 0, 31 do
      local angle = i * math.pi / 4
      local arena =
        { x = math.sin(angle), y = math.cos(angle), time = i * 0.1, boss = { x = 0, y = 0, hp = 100 } }
      assert(S.drawBoss('bailiff', 640, 345, arena, false))
      local count = 0
      for _ in pairs(S.sheets) do
        count = count + 1
      end
      assert(count <= 2)
    end
    assert(draws == 32 and releases >= 29)
    love.filesystem.getInfo = function()
      return nil
    end
    assert(
      not S.drawBoss('bailiff', 0, 0, { x = 0, y = 1, time = 4, boss = { x = 0, y = 0, hp = 100 } }, false)
    )
    love = old
    package.loaded['src.render.sprites'] = nil
  end)
end
