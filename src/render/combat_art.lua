-- Dedicated Blender sheets; cosmetic state never consumes combat randomness.
local C = { images = {}, quads = {}, clock = 0 }
local I = require('src.render.iso')
local H = require('src.data.heroes')
local meta = require('src.data.combat_art')
local Authored = require('src.render.authored_fx')
function C.frame(progress, reducedMotion)
  return reducedMotion and 3 or math.min(7, math.max(0, math.floor(progress * 8)))
end
function C.draw(id, x, y, size, progress, reducedMotion, opacity, rotation, height)
  if
    not meta[id]
    or not require('src.data.presentation').combatArt
    or not love
    or not love.graphics
    or not love.graphics.draw
  then
    return false
  end
  local G = love.graphics
  local entry = C.images[id]
  if not entry then
    local path = 'assets/effects/combat/' .. id .. '.png'
    if not love.filesystem.getInfo(path) then
      return false
    end
    local ok, img = pcall(G.newImage, path)
    if not ok then
      return false
    end
    img:setFilter('linear', 'linear')
    entry = { image = img, quads = {} }
    C.images[id] = entry
  end
  C.clock = C.clock + 1
  entry.used = C.clock
  local count = 0
  for _ in pairs(C.images) do
    count = count + 1
  end
  if count > 16 then
    local oldest, age
    for key, e in pairs(C.images) do
      if key ~= id and (not age or e.used < age) then
        oldest, age = key, e.used
      end
    end
    C.images[oldest].image:release()
    C.images[oldest] = nil
  end
  local f = C.frame(progress or 0, reducedMotion)
  if not entry.quads[f] then
    entry.quads[f] = G.newQuad(f % 4 * 128, math.floor(f / 4) * 128, 128, 128, entry.image:getDimensions())
  end
  G.setColor(1, 1, 1, (opacity or 1) * (reducedMotion and 0.65 or 1))
  G.draw(entry.image, entry.quads[f], x, y, rotation or 0, size / 128, (height or size) / 128, 64, 64)
  return true
end
function C.angle(dx, dy)
  return (math.atan2 or math.atan)(0.39 * (dx + dy), 0.78 * (dx - dy))
end
function C.reaction(name)
  return 'reaction_' .. name:lower():gsub(' ', '_')
end
function C.feedback(f, reducedMotion)
  local x, y = I.project(f.x, f.y)
  local p = 1 - f.t / f.life
  local progress = f.art == 'reaction_bloom' and (f.kind == 'reaction' and p * 0.55 or 0.55 + p * 0.45) or p
  local id = f.art
    or ({ shock = 'slam', hit = 'hit', slash = 'slash', muzzle = 'muzzle', dodge = 'dodge', cast = 'phase' })[f.kind]
    or f.kind
  local size = f.kind == 'slash' and f.radius * 2.5
    or f.kind == 'shock' and math.min(260, f.radius * 2.3)
    or f.kind == 'cast' and 105
    or f.kind == 'phase' and 180
    or f.kind == 'defeat' and 230
    or 85
  local angle = (f.kind == 'slash' or f.kind == 'muzzle' or f.kind == 'dodge') and C.angle(f.dx, f.dy) or 0
  local selected = f.kind == 'shock' and 'shock' or id
  if
    require('src.data.presentation').combatArt
    and Authored.draw(
      selected,
      x,
      y - (f.kind == 'shock' and 0 or 25),
      selected == 'critical' and 110 or size,
      p,
      reducedMotion,
      angle
    )
  then
    return true
  end
  if f.kind == 'shock' then
    C.draw('dust', x, y, math.min(200, f.radius * 2), p, reducedMotion, 0.4 * (1 - p))
  end
  return C.draw(
    id,
    x,
    y - (f.kind == 'shock' and 0 or 25),
    size,
    progress,
    reducedMotion,
    math.min(1, (1 - p) * 2),
    angle
  )
end
function C.projectile(p, time, reducedMotion, enemy)
  local x, y = I.project(p.x, p.y)
  local id = p.art
    or (enemy and 'hazard_' .. ({
      Pyro = 'flame',
      Hydro = 'water',
      Anemo = 'wind',
      Geo = 'rock',
      Dendro = 'bramble',
      Cryo = 'ice',
      Electro = 'grid',
      Gravity = 'mass',
      Antimatter = 'void',
    })[p.element or 'Pyro'])
    or (p.element and 'skill_' .. H.byId[p.hero or 'jack'].id)
    or 'projectile'
  if not enemy then
    local tx, ty = I.project(p.x - p.dx * 0.05, p.y - p.dy * 0.05)
    C.draw('trail', tx, ty - 14, 45, time * 2 % 1, reducedMotion, 0.4, C.angle(p.dx, p.dy))
  end
  return C.draw(
    id,
    x,
    y - 14,
    enemy and 56 or p.element and 60 or 40,
    time * 2 % 1,
    reducedMotion,
    1,
    C.angle(p.dx, p.dy)
  )
end
function C.field(f, time, reducedMotion)
  if not f.hero and not f.art then
    return false
  end
  local x, y = I.project(f.x, f.y)
  local id = f.art or 'skill_' .. f.hero
  local progress = f.delay > 0 and 1 - math.min(1, f.delay / 0.65) or time % 1
  return C.draw(id, x, y, math.min(300, f.radius * 2.1), progress, reducedMotion, 0.65)
end
local function polygon(coords)
  local out = {}
  for j = 1, #coords, 2 do
    local x, y = I.project(coords[j], coords[j + 1])
    out[#out + 1] = x
    out[#out + 1] = y
  end
  love.graphics.polygon('fill', unpack(out))
end
function C.hazardId(a, h)
  if a.encounter.id == 'bailiff' and not a.hell then
    if h.kind == 'lane' then
      return 'bailiff_flame'
    elseif h.kind == 'slam' then
      return 'bailiff_slam'
    end
  end
  local element = h.element or a.encounter.element
  if a.encounter.id == 'sun' and (h.kind == 'sweep' or h.kind == 'pressure') then
    element = 'Anemo'
  end
  if h.kind == 'pillar' then
    return h.eruption and h.t < -2.4 and 'hazard_rock' or 'hazard_pillar'
  end
  if h.kind == 'gravity' then
    return h.force > 0 and 'hazard_pull' or 'hazard_push'
  end
  if h.kind == 'pressure' then
    return 'hazard_wind'
  end
  if h.kind == 'patch' then
    return element == 'Antimatter' and 'hazard_zone'
      or h.ignite and h.t <= 0 and 'hazard_ignition'
      or 'hazard_bramble'
  end
  if h.kind == 'slam' then
    return element == 'Electro' and 'hazard_strike'
      or element == 'Cryo' and 'hazard_shatter'
      or element == 'Gravity' and 'hazard_mass'
      or element == 'Antimatter' and 'hazard_void'
      or 'slam'
  end
  if h.kind == 'ring' then
    return element == 'Antimatter' and 'hazard_wave_void' or 'hazard_water'
  end
  return 'hazard_'
    .. ({
      Pyro = 'flame',
      Hydro = 'water',
      Anemo = 'wind',
      Geo = 'rock',
      Dendro = 'bramble',
      Cryo = 'ice',
      Electro = 'grid',
      Gravity = 'pull',
      Antimatter = 'void',
    })[element]
end
-- Artwork is stencilled to the existing collision shapes. Rings omit safe-gap
-- sectors with extra margin. Warnings retain their live outlines and labels.
function C.hazard(a, h, reducedMotion)
  local G = love.graphics
  if not G.stencil or not G.setStencilTest or not require('src.data.presentation').combatArt then
    return false
  end
  if h.kind == 'pressure' then
    for j = 1, 3 do
      local x, y = I.project(-260 + j * 150, 200)
      C.draw('hazard_wind', x, y, 85, a.time % 1, reducedMotion, h.t > 0 and 0.20 or 0.6, C.angle(h.dx, h.dy))
    end
    return true
  end
  local id = C.hazardId(a, h)
  local mode, value = G.getStencilTest()
  G.stencil(function()
    if h.kind == 'lane' then
      if h.axis == 'x' then
        polygon({ h.center - h.r, -350, h.center + h.r, -350, h.center + h.r, 350, h.center - h.r, 350 })
      else
        polygon({ -350, h.center - h.r, 350, h.center - h.r, 350, h.center + h.r, -350, h.center + h.r })
      end
    elseif h.kind == 'bolt' or h.kind == 'sweep' then
      local nx, ny = -h.dy * h.r, h.dx * h.r
      local back = h.kind == 'sweep' and -700 or 0
      local length = h.kind == 'sweep' and 700 or 650
      polygon({
        h.x + h.dx * back + nx,
        h.y + h.dy * back + ny,
        h.x + h.dx * back - nx,
        h.y + h.dy * back - ny,
        h.x + h.dx * length - nx,
        h.y + h.dy * length - ny,
        h.x + h.dx * length + nx,
        h.y + h.dy * length + ny,
      })
    elseif h.kind == 'ring' or h.kind == 'gravity' then
      local width = h.width or 8
      for j = 0, 71 do
        local t1, t2 = j * math.pi / 36, (j + 1) * math.pi / 36
        local mid = (t1 + t2) / 2
        if math.abs((mid - h.gap + math.pi) % (2 * math.pi) - math.pi) > (h.gapWidth + 0.06) then
          local inner = h.kind == 'gravity' and 0 or math.max(0, h.r - width)
          polygon({
            h.x + math.cos(t1) * inner,
            h.y + math.sin(t1) * inner,
            h.x + math.cos(t2) * inner,
            h.y + math.sin(t2) * inner,
            h.x + math.cos(t2) * (h.r + width),
            h.y + math.sin(t2) * (h.r + width),
            h.x + math.cos(t1) * (h.r + width),
            h.y + math.sin(t1) * (h.r + width),
          })
        end
      end
    else
      local x, y = I.project(h.x, h.y)
      G.ellipse('fill', x, y, h.r * 1.103, h.r * 0.552)
    end
  end, 'replace', 1)
  G.setStencilTest('equal', 1)
  local opacity = h.t > 0 and 0.18 or math.min(0.8, math.max(0.18, 1 + h.t / h.active))
  local progress = h.t > 0 and (1 - h.t / h.warning) * 0.5 or (-h.t / 0.8) % 1
  if h.kind == 'lane' then
    for j = -300, 300, 60 do
      local x, y = I.project(h.axis == 'x' and h.center or j, h.axis == 'x' and j or h.center)
      C.draw(
        id,
        x,
        y,
        130,
        progress,
        reducedMotion,
        opacity,
        C.angle(h.axis == 'x' and 0 or 1, h.axis == 'x' and 1 or 0)
      )
    end
  elseif h.kind == 'bolt' or h.kind == 'sweep' then
    for j = h.kind == 'sweep' and -600 or 0, 600, 65 do
      local wx, wy = h.x + h.dx * j, h.y + h.dy * j
      if math.abs(wx) <= 350 and math.abs(wy) <= 350 then
        local x, y = I.project(wx, wy)
        C.draw(id, x, y, 110, progress, reducedMotion, opacity, C.angle(h.dx, h.dy))
      end
    end
  elseif h.kind == 'ring' or h.kind == 'gravity' then
    for j = 0, 31 do
      local angle = j * math.pi / 16
      if math.abs((angle - h.gap + math.pi) % (2 * math.pi) - math.pi) > h.gapWidth + 0.1 then
        local radii = h.kind == 'gravity' and { h.r * 0.35, h.r * 0.7, h.r } or { h.r }
        for _, r in ipairs(radii) do
          local x, y = I.project(h.x + math.cos(angle) * r, h.y + math.sin(angle) * r)
          C.draw(
            id,
            x,
            y,
            math.max(65, r * 0.36),
            progress,
            reducedMotion,
            opacity,
            C.angle(-math.sin(angle), math.cos(angle))
          )
        end
      end
    end
  else
    local x, y = I.project(h.x, h.y)
    C.draw(id, x, y, math.min(260, h.r * 2.7), progress, reducedMotion, opacity)
  end
  G.setStencilTest(mode, value)
  -- Pillars stand above their ground footprint after rising.
  if h.kind == 'pillar' and h.t <= 0 then
    local x, y = I.project(h.x, h.y)
    C.draw('hazard_pillar', x, y - 20, 125, math.min(0.5, -h.t / 0.4), reducedMotion, 0.9)
  end
  return true
end
function C.status(a, reducedMotion)
  local x, y = I.project(a.boss.x, a.boss.y)
  local time = a.time
  if a.boss.aura then
    C.draw('aura_' .. a.boss.aura:lower(), x, y - 30, 115, time % 1, reducedMotion, 0.38)
  end
  if a.boss.vulnerable and a.boss.vulnerable > 0 then
    C.draw('status_vulnerable', x, y, 115, time % 1, reducedMotion, 0.5)
  end
  if a.boss.stun > 0 then
    C.draw('status_stagger', x, y - 35, 135, time % 1, reducedMotion, 0.5)
  end
  for _, e in ipairs(a.effects) do
    local id = e.reaction == 'Kindling' and 'status_burn'
      or e.reaction == 'Live Wire' and 'status_electric'
      or e.reaction == 'Bloom' and 'status_bloom'
    if id then
      local progress = e.reaction == 'Bloom' and 0.55 * math.max(0, 1 - e.timer / 1.2) or (1 - e.timer) % 1
      C.draw(id, x, y - 25, 90, progress, reducedMotion, 0.42)
    end
  end
  local hx, hy = I.project(a.x, a.y)
  if a:hero().shield > 0 then
    C.draw('status_shield', hx, hy - 23, 105, time % 1, reducedMotion, 0.50)
  end
end
return C
