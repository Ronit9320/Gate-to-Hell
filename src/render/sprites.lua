-- Pixel-art sprite loader. Missing files degrade to procedural placeholders.
local S = { heroes = {}, bosses = {}, sheets = {}, heroSheets = {} }
local Atlas = require('src.render.atlas')
local function load(path)
  if not require('src.data.presentation').usePortraits then
    return false
  end
  if not love.filesystem.getInfo(path) then
    return false
  end
  local ok, img = pcall(love.graphics.newImage, path)
  if not ok or not img then
    return false
  end
  img:setFilter('nearest', 'nearest')
  return img
end
function S.hero(id)
  if not (love.filesystem and love.graphics.newImage) then
    return nil
  end
  if S.heroes[id] == nil then
    local path = 'assets/heroes/isometric/' .. id .. '/portrait.png'
    if require('src.data.presentation').heroSprites and love.filesystem.getInfo(path) then
      local ok, img = pcall(love.graphics.newImage, path)
      if ok and img then
        img:setFilter('linear', 'linear')
        S.heroes[id] = img
      end
    end
    if S.heroes[id] == nil then
      S.heroes[id] = load('assets/heroes/' .. id .. '.png')
    end
  end
  return S.heroes[id] or nil
end
-- Four resident directional atlases cover an active hero and fallen teammates.
function S.drawHero(id, x, y, arena, reducedMotion)
  if not require('src.data.presentation').heroSprites or not (love.filesystem and love.graphics.draw) then
    return false
  end
  local meta = require('src.data.hero_sprites')
  local state = arena.heroVisuals and arena.heroVisuals[id] or {}
  local direction = Atlas.direction(state.dx or 0, state.dy or 1)
  local key = id .. ':' .. direction
  local path = meta.path .. id .. '/' .. string.format('hero_y%03d.png', direction * 45)
  if not love.filesystem.getInfo(path) then
    return false
  end
  local cached = S.heroSheets[key]
  if not cached then
    local ok, img = pcall(love.graphics.newImage, path)
    if not ok or not img then
      return false
    end
    img:setFilter('linear', 'linear')
    cached = { image = img, quads = {} }
    S.heroSheets[key] = cached
  end
  S.heroClock = (S.heroClock or 0) + 1
  cached.used = S.heroClock
  local count = 0
  for _ in pairs(S.heroSheets) do
    count = count + 1
  end
  if count > 4 then
    local oldest, age
    for k, entry in pairs(S.heroSheets) do
      if k ~= key and (not age or entry.used < age) then
        oldest, age = k, entry.used
      end
    end
    S.heroSheets[oldest].image:release()
    S.heroSheets[oldest] = nil
  end
  local pose, elapsed = Atlas.heroPose(state, arena.heroSpriteTime or arena.time, reducedMotion)
  local cx, cy = Atlas.cell(meta, pose, elapsed, reducedMotion and pose ~= 'death')
  local cellKey = cx .. ':' .. cy
  if not cached.quads[cellKey] then
    cached.quads[cellKey] =
      love.graphics.newQuad(cx, cy, meta.width, meta.height, cached.image:getDimensions())
  end
  love.graphics.setColor(1, 1, 1, 1)
  love.graphics.draw(
    cached.image,
    cached.quads[cellKey],
    x,
    y,
    0,
    meta.scale,
    meta.scale,
    meta.anchorX,
    meta.anchorY
  )
  return true
end
function S.boss(id, hell, phase)
  id = id or 'bailiff'
  local appearance = require('src.data.boss_sprites').appearance(id, hell, phase)
  if S.bosses[appearance] == nil then
    local path = id == 'bailiff' and not hell and 'assets/bosses/bailiff_iso/portrait.png'
      or 'assets/bosses/isometric/' .. appearance .. '/portrait.png'
    if require('src.data.presentation').bossSprites and love.filesystem.getInfo(path) then
      local ok, img = pcall(love.graphics.newImage, path)
      if ok and img then
        img:setFilter('linear', 'linear')
        S.bosses[appearance] = img
      end
    end
    if S.bosses[appearance] == nil then
      S.bosses[appearance] = load('assets/bosses/' .. id .. '.png')
    end
  end
  return S.bosses[appearance] or nil
end
-- Load only the requested direction and one neighbor; large atlases stay bounded.
function S.drawBoss(id, x, y, arena, reducedMotion)
  local presentation = require('src.data.presentation')
  local legacy = id == 'bailiff' and not arena.hell
  if (legacy and not presentation.bailiffSprites) or (not legacy and not presentation.bossSprites) then
    return false
  end
  local meta = require(legacy and 'src.data.bailiff_sprite' or 'src.data.boss_sprites')
  local appearance = require('src.data.boss_sprites').appearance(id, arena.hell, arena.phase)
  local direction = Atlas.direction(arena.x - arena.boss.x, arena.y - arena.boss.y)
  local key = appearance .. ':' .. direction
  local path = legacy and (meta.path .. string.format('bailiff_y%03d.png', direction * 45))
    or (meta.path .. appearance .. '/' .. string.format('boss_y%03d.png', direction * 45))
  if not love.filesystem.getInfo(path) then
    return false
  end
  local cached = S.sheets[key]
  if not cached then
    local ok, img = pcall(love.graphics.newImage, path)
    if not ok then
      return false
    end
    img:setFilter('linear', 'linear')
    cached = { image = img, quads = {}, used = arena.time }
    S.sheets[key] = cached
    local count = 0
    for _ in pairs(S.sheets) do
      count = count + 1
    end
    if count > 2 then
      local oldest, age
      for d, entry in pairs(S.sheets) do
        if d ~= key and (not age or entry.used < age) then
          oldest, age = d, entry.used
        end
      end
      S.sheets[oldest].image:release()
      S.sheets[oldest] = nil
    end
  end
  S.sheetClock = (S.sheetClock or 0) + 1
  cached.used = S.sheetClock
  local name, elapsed = Atlas.pose(arena.boss, arena.spriteTime or arena.time, reducedMotion, meta)
  if reducedMotion and name == 'death' then
    elapsed = 10
  end
  local cx, cy = Atlas.cell(meta, name, elapsed, reducedMotion and name ~= 'death')
  local key = cx .. ':' .. cy
  if not cached.quads[key] then
    cached.quads[key] = love.graphics.newQuad(cx, cy, meta.width, meta.height, cached.image:getDimensions())
  end
  love.graphics.setColor(1, 1, 1, 1)
  love.graphics.draw(
    cached.image,
    cached.quads[key],
    x,
    y,
    0,
    meta.scale,
    meta.scale,
    meta.anchorX,
    meta.anchorY
  )
  return true
end
return S
