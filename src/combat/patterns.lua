local U = require('src.core.util')
local P = { cap = 12, minWarning = 1.05 }
local pi = math.pi
local function angle(y, x)
  return (math.atan2 or math.atan)(y, x)
end
function P.inGap(h, x, y)
  local a = angle(y - h.y, x - h.x)
  return math.abs((a - h.gap + pi) % (2 * pi) - pi) < (h.gapWidth or 0.65)
end
function P.inside(h, x, y, padding)
  padding = padding or 0
  if h.kind == 'lane' then
    return math.abs((h.axis == 'x' and x or y) - h.center) <= h.r + padding
  end
  if h.kind == 'slam' or h.kind == 'pillar' or h.kind == 'patch' then
    return U.dist(x, y, h.x, h.y) <= h.r + padding
  end
  if h.kind == 'ring' then
    return math.abs(U.dist(x, y, h.x, h.y) - h.r) <= h.width + padding and not P.inGap(h, x, y)
  end
  if h.kind == 'sweep' then
    local dx, dy = x - h.x, y - h.y
    return math.abs(dx * h.dy - dy * h.dx) <= h.r + padding and math.abs(dx * h.dx + dy * h.dy) <= 700
  end
  return false
end
local function add(a, h)
  if #a.hazards >= P.cap then
    return
  end
  h.t = math.max(P.minWarning, h.t or 1.2)
  h.warning = h.t
  h.active = h.active or 0.28
  a.hazards[#a.hazards + 1] = h
end
local function lane(a, axis, center, delay, width)
  add(a, { kind = 'lane', axis = axis, center = center, r = width or 40, t = delay })
end
local function slam(a, x, y, r, delay)
  add(a, { kind = 'slam', x = x, y = y, r = r or 90, t = delay })
end
local function bolt(a, rotation)
  local dx, dy = U.norm(a.x - a.boss.x, a.y - a.boss.y)
  local c, s = math.cos(rotation or 0), math.sin(rotation or 0)
  add(a, {
    kind = 'bolt',
    x = a.boss.x,
    y = a.boss.y,
    dx = dx * c - dy * s,
    dy = dx * s + dy * c,
    r = 18,
    t = 1.2,
    active = 0.05,
  })
end
local function ring(a, x, y, gap, returning, delay)
  add(a, {
    kind = 'ring',
    x = x,
    y = y,
    gap = gap,
    gapWidth = 0.7,
    r = returning and 450 or 40,
    width = 23,
    speed = returning and -100 or 100,
    t = delay or 1.25,
    active = 3.8,
  })
end
local function sweep(a, theta, delay)
  add(a, {
    kind = 'sweep',
    x = 0,
    y = 0,
    dx = math.cos(theta),
    dy = math.sin(theta),
    r = 32,
    t = delay or 1.3,
    active = 0.35,
  })
end
local function patches(a, ignite)
  -- Fixed separated islands leave a 140-unit southern corridor and channels between patches.
  local positions = { { -210, -180 }, { 120, -190 }, { -150, 70 }, { 170, 40 } }
  for i = 1, (a.phase >= 2 and 4 or 3) do
    local p = positions[(i + a.pattern - 2) % 4 + 1]
    add(a, {
      kind = 'patch',
      x = p[1],
      y = p[2],
      r = 40,
      maxr = 78,
      growth = 12,
      t = 1.3 + (i - 1) * 0.15,
      active = ignite and 3.2 or 2.6,
      ignite = ignite,
    })
  end
end
function P.cast(a)
  local n, hell = a.encounter.index, a.hell
  local turn = a.pattern
  local phase = a.phase
  a.attackTimer = math.max(2.2, 3.2 - (phase - 1) * 0.25 - (hell and 0.2 or 0))
  if n == 1 then
    a.attackTimer = phase >= 2 and 2.4 or 2.6
    if turn % 3 == 0 then
      bolt(a)
    elseif turn % 2 == 0 then
      slam(a, a.x, a.y, 105, 1.15)
      if turn % 4 == 0 then
        slam(a, a.boss.x, a.boss.y, 150, 1.45)
      end
    else
      lane(a, turn % 4 == 1 and 'x' or 'y', turn % 4 == 1 and a.x or a.y, 1.05, 43)
    end
    if hell and turn % 2 == 1 then
      lane(a, turn % 4 == 1 and 'y' or 'x', -180, 1.65, 35)
    end
  elseif n == 2 then
    local gap = angle(a.y - a.boss.y, a.x - a.boss.x)
    ring(a, 0, -100, gap, false)
    if phase >= 2 then
      a.hazards[#a.hazards].speed = 115
    end
    a.attackTimer = 5.4
    if hell then
      ring(a, 70, -70, gap, true, 2.1)
      a.attackTimer = 6.3
    end
  elseif n == 3 then
    local theta = (turn % 4) * pi / 4
    sweep(a, theta)
    add(a, {
      kind = 'pressure',
      x = 0,
      y = 0,
      dx = math.cos(theta + pi / 2),
      dy = math.sin(theta + pi / 2),
      r = 350,
      t = 1.3,
      active = 1.3,
    })
    if hell then
      sweep(a, theta + pi / 2, 2.1)
    end
  elseif n == 4 then
    if turn % 2 == 1 then
      for _, x in ipairs({ -155, 155 }) do
        add(a, { kind = 'pillar', x = x, y = -20, r = 46, t = 1.4, active = 4.2, eruption = hell })
      end
    else
      bolt(a)
      if phase >= 2 then
        bolt(a, 0.35)
      end
    end
  elseif n == 5 then
    patches(a, hell)
    a.attackTimer = 5.2
  elseif n == 6 then
    local axis = turn % 2 == 0 and 'x' or 'y'
    lane(a, axis, -140, 1.3, 38)
    lane(a, axis, 140, 1.3, 38)
    lane(a, axis, 0, hell and 2.0 or 2.35, 44)
    if phase >= 2 then
      slam(a, a.x, a.y, 68, 3.1)
    end
    a.attackTimer = 4.8
    -- Long recovery and extra stagger vulnerability reward reading the delayed shatter.
    a.boss.iceOpening = 3.8
  elseif n == 7 then
    local gap = hell and ((turn % 3) - 1) * 180 or 0
    for _, pos in ipairs({ -180, 0, 180 }) do
      if pos ~= gap then
        lane(a, turn % 2 == 0 and 'x' or 'y', pos, 1.35, 32)
      end
    end
    slam(a, a.x, a.y, 65, 2.15)
    a.attackTimer = 3.9
  elseif n == 8 then
    a.stance = (turn % 2 == 1) and 'FIRE / SPIRAL' or 'WIND / SWEEP'
    a:label(a.stance, a.boss.x, a.boss.y - 70)
    a:feedbackAt(
      'phase',
      a.boss.x,
      a.boss.y,
      nil,
      nil,
      nil,
      nil,
      nil,
      turn % 2 == 1 and 'hazard_spiral' or 'hazard_wind'
    )
    if turn % 2 == 1 then
      for j = 0, 4 do
        bolt(a, (j - 2) * 0.6 + turn * 0.18)
      end
    else
      sweep(a, turn * pi / 5)
      if phase >= 2 then
        sweep(a, turn * pi / 5 + pi / 2, 2.2)
      end
    end
    a.attackTimer = hell and 3.4 or 4.4
  elseif n == 9 then
    local gap = angle(a.y + 100, a.x)
    add(a, {
      kind = 'gravity',
      x = 0,
      y = -100,
      r = 290,
      gap = gap,
      gapWidth = 0.65,
      t = 1.5,
      active = 2.4,
      force = hell and turn % 2 == 0 and -75 or 65,
    })
    slam(a, a.x, a.y, 85, 2.0)
    if phase >= 2 then
      slam(a, -a.x, -a.y, 65, 2.6)
    end
    a.attackTimer = 4.8
  else
    if phase == 1 then
      lane(a, turn % 2 == 0 and 'x' or 'y', turn % 2 == 0 and a.x or a.y, 1.3, 48)
      if hell then
        slam(a, -a.x, -a.y, 75, 2.0)
      end
    elseif phase == 2 then
      ring(a, 0, -100, angle(a.y + 100, a.x), false)
      if hell then
        lane(a, 'x', a.x > 0 and -230 or 230, 2.0, 35)
      end
      a.attackTimer = 5.5
    else
      slam(a, a.x, a.y, 90, 1.5)
      add(a, { kind = 'patch', x = -180, y = -140, r = 55, maxr = 85, growth = 10, t = 1.5, active = 3.0 })
      add(a, { kind = 'patch', x = 180, y = -140, r = 55, maxr = 85, growth = 10, t = 1.5, active = 3.0 })
      if hell then
        sweep(a, turn * pi / 3, 2.5)
      end
      a.attackTimer = 5.0
    end
  end
  local difficulty = a.difficulty or require('src.data.bosses').difficulty(a.run)
  a.attackTimer = math.max(2.2, a.attackTimer * difficulty.cadence)
  -- A delayed strike punishes camping without tracking the player after the tell.
  -- Leave the first four floors for learning the boss vocabulary.
  if difficulty.pursuit then
    slam(a, a.x, a.y, 72, 1.85)
  end
end
function P.update(a, dt)
  for i = #a.hazards, 1, -1 do
    local h = a.hazards[i]
    h.t = h.t - dt
    if h.t <= 0 then
      if not h.activated then
        h.activated = true
        if h.kind == 'slam' or h.kind == 'pillar' then
          a:impact(h.x, h.y, h.r)
        elseif h.kind == 'lane' or h.kind == 'sweep' then
          a:feedbackAt(
            'shock',
            h.x or (h.axis == 'x' and h.center or 0),
            h.y or (h.axis == 'y' and h.center or 0),
            nil,
            nil,
            nil,
            65
          )
        end
      end
      if h.kind == 'ring' then
        h.r = math.max(0, h.r + h.speed * dt)
      end
      if h.kind == 'patch' then
        h.r = math.min(h.maxr, h.r + h.growth * dt)
      end
      if h.kind == 'pillar' then
        local dist = U.dist(a.x, a.y, h.x, h.y)
        if dist < h.r + 14 then
          local dx, dy = U.norm(a.x - h.x, a.y - h.y)
          a.x, a.y = h.x + dx * (h.r + 14), h.y + dy * (h.r + 14)
        end
        if h.eruption and h.t < -2.4 and h.t > -2.9 and U.dist(a.x, a.y, h.x, h.y) < h.r + 42 then
          a:damageHero(a.incoming)
        end
      elseif
        h.kind == 'gravity'
        and U.dist(a.x, a.y, h.x, h.y) < h.r
        and not P.inGap(h, a.x, a.y)
        and a.dodge <= 0
      then
        local dx, dy = U.norm(h.x - a.x, h.y - a.y)
        a.x, a.y = a.x + dx * h.force * dt, a.y + dy * h.force * dt
      elseif h.kind == 'pressure' and a.dodge <= 0 then
        a.x, a.y = a.x + h.dx * 38 * dt, a.y + h.dy * 38 * dt
      elseif h.kind == 'bolt' and not h.spawned then
        h.spawned = true
        if #a.enemyProjectiles < 12 then
          a.enemyProjectiles[#a.enemyProjectiles + 1] = {
            x = h.x,
            y = h.y,
            dx = h.dx * 210,
            dy = h.dy * 210,
            t = 4,
            element = a.encounter.element,
            art = a.encounter.id == 'sun' and 'hazard_spiral' or nil,
          }
        end
      end
      if P.inside(h, a.x, a.y) and (not h.hit or (h.kind == 'patch' and a.time >= (h.nextHit or 0))) then
        a:damageHero(a.incoming * (h.kind == 'slam' and 1.3 or h.ignite and 1.15 or 1))
        h.hit = true
        h.nextHit = a.time + 0.8
      end
      if h.t <= -h.active then
        table.remove(a.hazards, i)
      end
    end
  end
  a.x, a.y = U.clamp(a.x, -350, 350), U.clamp(a.y, -350, 350)
end
return P
