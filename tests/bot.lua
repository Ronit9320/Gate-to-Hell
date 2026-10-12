local U = require('src.core.util')
local P = require('src.combat.patterns')
local H = require('src.data.heroes')
local function bot(a)
  local bx, by = a.boss.x, a.boss.y
  a:attack(bx, by, true)
  a:attack(bx, by)
  if a:hero().cd > 1 then
    for i, h in ipairs(a.run.team) do
      if h.hp > 0 and h.cd <= 0 then
        a:switch(i)
        break
      end
    end
  end
  local function danger(x, y, future)
    local cost = 0
    for _, h in ipairs(a.hazards) do
      local t = h.t - future
      if t <= 0.3 and t >= -h.active then
        local z = h
        if h.kind == 'ring' or h.kind == 'patch' then
          z = U.copy(h)
          local activeTime = math.max(0, future - math.max(0, h.t))
          z.r = h.kind == 'ring' and math.max(0, h.r + h.speed * activeTime)
            or math.min(h.maxr, h.r + h.growth * activeTime)
        end
        if P.inside(z, x, y, 24) then
          cost = cost + 100
        end
      end
    end
    for _, p in ipairs(a.enemyProjectiles) do
      if U.dist(x, y, p.x + p.dx * future, p.y + p.dy * future) < 55 then
        cost = cost + 100
      end
    end
    return cost
  end
  local targetRange = H.byId[a:hero().id].style == 'Melee' and 95 or 190
  local dx, dy, best = 0, 0, math.huge
  for i = 0, 16 do
    local x, y = 0, 0
    if i > 0 then
      x, y = math.cos(i * math.pi / 8), math.sin(i * math.pi / 8)
    end
    local cost = 0
    for _, t in ipairs({ 0.15, 0.4, 0.8 }) do
      local px, py = U.clamp(a.x + x * 185 * t, -330, 330), U.clamp(a.y + y * 185 * t, -330, 330)
      cost = cost + danger(px, py, t)
      if math.abs(a.x + x * 185 * t) > 340 or math.abs(a.y + y * 185 * t) > 340 then
        cost = cost + 10
      end
      cost = cost + math.abs(U.dist(px, py, bx, by) - targetRange) * 0.01
    end
    if cost < best then
      best, dx, dy = cost, x, y
    end
  end
  if danger(a.x, a.y, 0.08) > 0 then
    a:dodgeStart(dx, dy)
  end
  a:update(0.05, dx, dy)
end

return bot
