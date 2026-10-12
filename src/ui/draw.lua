local G = love.graphics
local H = require('src.data.heroes')
local I = require('src.render.iso')
local SP = require('src.render.sprites')
local Emblem = require('src.ui.elements')
local P = require('src.ui.pixel')
local T = require('src.render.ui_textures')
local FX = require('src.render.effects')
local Art = require('src.render.combat_art')
local ButtonIcons = require('src.ui.button_icons')
local UI = { fonts = {}, buttons = {}, mx = 0, my = 0 }
-- Hover regions are rebuilt each frame. The overlay never consumes clicks.
function UI.inspect(x, y, w, h, title, body, color)
  if UI.mx >= x and UI.mx <= x + w and UI.my >= y and UI.my <= y + h then
    UI.hoverTip = { title = title, body = body, color = color }
    G.setColor(color or { 0.95, 0.76, 0.4 })
    G.rectangle('line', x, y, w, h, 4, 4)
  end
end
function UI.tooltip()
  local tip = UI.hoverTip
  if not tip then
    UI.tipTitle = nil
    return
  end
  if UI.tipTitle ~= tip.title then
    UI.tipTitle, UI.tipSince = tip.title, UI.time or 0
  end
  if (UI.time or 0) - UI.tipSince < 0.2 then
    return
  end
  UI.font(16)
  local _, lines = G.getFont():getWrap(tip.body, 308)
  local height = 57 + #lines * G.getFont():getHeight() * 1.15
  local x = math.max(12, math.min(936, UI.mx + 18))
  local y = UI.my + 22
  if y + height > 704 then
    y = math.max(12, UI.my - height - 16)
  end
  UI.panel(x, y, 332, height)
  UI.rule(x + 12, x + 320, y + 4, tip.color or { 0.95, 0.76, 0.4 }, 2)
  UI.text(tip.title, x + 12, y + 12, 18, tip.color, 308)
  UI.text(tip.body, x + 12, y + 41, 16, nil, 308)
end
function UI.item(id, cx, cy, size)
  T.item(id, cx, cy, size)
  local item = require('src.data.items')[id]
  UI.inspect(cx - size / 2, cy - size / 2, size, size, item.name, item.description)
end
function UI.font(n)
  local face = n >= 22 and 'Cinzel' or 'AdwaitaSans'
  if UI.largeText and n < 20 then
    n = math.min(20, n + 2)
  end
  local key = face .. ':' .. n
  if not UI.fonts[key] then
    local path = 'assets/fonts/' .. face .. '.ttf'
    UI.fonts[key] = love.filesystem and love.filesystem.getInfo(path) and G.newFont(path, n) or G.newFont(n)
  end
  G.setFont(UI.fonts[key])
end
function UI.text(s, x, y, n, color, w, align)
  UI.font(n or 16)
  G.setColor(color or { 0.9, 0.87, 0.78 })
  G.printf(tostring(s), x, y, w or 1000, align or 'left')
end
function UI.panel(x, y, w, h, color)
  if not T.skin('panel', x, y, w, h) then
    P.frame(x, y, w, h, { fill = color or P.palette.slot, notch = P.notchFor(w, h), bevel = 1 })
  elseif color then
    P.ring(x + 4, y + 4, w - 8, h - 8, 2, 2, P.light(color, 0.3))
  end
end
function UI.bar(x, y, w, h, frac, color, track)
  if h <= 4 then
    G.setColor(track or { 0.05, 0.1, 0.11 })
    G.rectangle('fill', x, y, w, h)
    G.setColor(color)
    G.rectangle('fill', x, y, w * math.max(0, math.min(1, frac or 0)), h)
    return
  end
  if T.skin('bar_track', x, y, w, h) then
    P.bar(x + 2, y + 2, w - 4, h - 4, frac, color, track)
  else
    P.bar(x, y, w, h, frac, color, track)
  end
end
function UI.rule(x1, x2, y, color, thickness)
  P.rule(x1, x2, y, color, thickness)
end
function UI.stat(icon, label, x, y, n, color, w)
  local size = (n or 16) + 8
  T.icon(icon, x + size / 2, y + (n or 16) / 2 + 2, size)
  UI.text(label, x + size + 5, y, n, color, w and w - size - 5)
end
function UI.button(label, x, y, w, h, fn, disabled, icon)
  local focused = UI.keyboard and UI.focus == #UI.buttons + 1 and not disabled
  local hover = UI.mx >= x and UI.mx <= x + w and UI.my >= y and UI.my <= y + h
  local base
  if disabled then
    base = { 0.1, 0.14, 0.15 }
  elseif hover or focused then
    base = { 0.32, 0.38, 0.25 }
  else
    base = { 0.16, 0.24, 0.23 }
  end
  local notch = P.notchFor(w, h)
  local skin = disabled and 'button_disabled' or (hover or focused) and 'button_hover' or 'button'
  if not T.skin(skin, x, y, w, h) then
    P.frame(x, y, w, h, { fill = base, notch = notch, bevel = focused and 2 or 1 })
  elseif not disabled then
    local size = (hover or focused) and 10 or 7
    T.sprite('ember_seal', x + 7, y + h / 2, size)
    T.sprite('ember_seal', x + w - 7, y + h / 2, size, T.time + 0.25)
  end
  if focused then
    P.ring(x + 2, y + 2, w - 4, h - 4, math.max(0, notch - 2), 2, P.palette.amber)
  elseif hover then
    P.ring(x + 2, y + 2, w - 4, h - 4, math.max(0, notch - 2), 1, { 0.75, 0.72, 0.5 })
  end
  icon = icon or ButtonIcons.forLabel(label)
  local inset = icon and 32 or 8
  if icon then
    T.icon(icon, x + 21, y + h / 2, math.min(24, h - 10), disabled and { 0.5, 0.5, 0.5, 0.7 } or nil)
  end
  UI.font(16)
  UI.text(
    label,
    x + inset,
    y + (h - G.getFont():getHeight()) / 2,
    16,
    disabled and { 0.4, 0.47, 0.45 } or { 0.98, 0.87, 0.64 },
    w - inset - 8,
    'center'
  )
  if not disabled then
    UI.buttons[#UI.buttons + 1] = { x = x, y = y, w = w, h = h, fn = fn }
  end
end
function UI.navigate(k, reverse)
  local n = #UI.buttons
  if n == 0 then
    return false
  end
  if k == 'tab' or k == 'down' or k == 'right' or k == 'up' or k == 'left' then
    local delta = (reverse or k == 'up' or k == 'left') and -1 or 1
    UI.focus = ((UI.focus or (delta == 1 and 0 or 1)) - 1 + delta) % n + 1
    UI.keyboard = true
    return true
  elseif k == 'return' or k == 'space' then
    local b = UI.buttons[math.min(UI.focus or 1, n)]
    UI.keyboard = true
    UI.buttons = {}
    UI.focus = nil
    b.fn()
    return true
  end
end
function UI.click(x, y)
  UI.keyboard = false
  UI.focus = nil
  for _, b in ipairs(UI.buttons) do
    if x >= b.x and x <= b.x + b.w and y >= b.y and y <= b.y + b.h then
      UI.buttons = {}
      b.fn()
      return true
    end
  end
end
function UI.sprite(img, cx, cy, size)
  if not img then
    return false
  end
  local iw, ih = img:getDimensions()
  local s = size / math.max(iw, ih)
  G.setColor(1, 1, 1, 1)
  G.draw(img, cx - iw * s / 2, cy - ih * s / 2, 0, s, s)
  return true
end
function UI.card(id, x, y, w, h, small)
  local d = H.byId[id]
  local c = H.colors[d.element]
  if not small and not UI.reducedMotion then
    y = y + math.sin((UI.time or 0) * 2 + x) * 2
  end
  local rarity = ({ { 0.45, 0.55, 0.54 }, { 0.4, 0.78, 0.6 }, { 0.63, 0.48, 0.9 }, { 1, 0.76, 0.3 } })[d.rarity]
  local notch = P.notchFor(w, h)
  if not T.skin('card', x, y, w, h) then
    P.frame(x, y, w, h, {
      fill = { 0.06, 0.12, 0.13 },
      border = rarity,
      borderWidth = 2,
      notch = notch,
      bevel = 1,
    })
  end
  P.ring(x + 1, y + 1, w - 2, h - 2, notch, 2, rarity)
  P.ring(x + 4, y + 4, w - 8, h - 8, math.max(0, notch - 2), 1, P.dark(rarity, 0.35))
  P.oct(x + 2, y + 2, w - 4, 6, 1, c)
  UI.inspect(
    x,
    y,
    w,
    h,
    d.name,
    d.element .. ' / ' .. d.style .. '\n' .. d.skill .. ' · ' .. d.cooldown .. 's cooldown\n' .. d.passive,
    c
  )
  local portrait = SP.hero(d.id)
  if small then
    G.setColor(c)
    Emblem.draw(d.element, x + 25, y + 20, 8)
    UI.text(d.element:upper(), x + 42, y + 12, 12, c, w - 150)
    UI.text(d.name, x + 16, y + 34, 20, nil, w - 120)
    if not UI.sprite(portrait, x + w - 62, y + h / 2, h - 12) then
      G.setColor(c)
      Emblem.draw(d.element, x + w - 62, y + h / 2, 22)
    end
    return
  end
  G.setColor(c)
  Emblem.draw(d.element, x + 27, y + 25, 9)
  UI.text(d.element:upper(), x + 47, y + 18, 12, c, w - 63)
  UI.text(d.name, x + 16, y + 43, 25, nil, w - 32)
  if not UI.sprite(portrait, x + w / 2, y + 130, 122) then
    G.setColor(c)
    local cx, cy = x + w / 2, y + 138
    G.circle('line', cx, cy, 46, 48)
    local radius = 30 * (UI.reducedMotion and 1 or (1 + math.sin((UI.time or 0) * 2 + x) * 0.035))
    Emblem.draw(d.element, cx, cy, radius)
    G.setColor(c[1], c[2], c[3], 0.25)
    G.circle('line', cx, cy, 54, 12)
  end
  UI.text(H.rarities[d.rarity] .. ' / ' .. d.style, x + 16, y + 186, 14, { 0.86, 0.71, 0.44 }, w - 32)
  UI.text(d.skill, x + 16, y + 220, 18, nil, w - 32)
  UI.text(d.passive, x + 16, y + 252, 15, { 0.63, 0.75, 0.72 }, w - 32)
  local sw = (w - 32) / 3
  UI.stat('heart', d.hp .. ' HP', x + 12, y + h - 30, 12, nil, sw)
  UI.stat('attack', d.basic .. ' ATK', x + 12 + sw, y + h - 30, 12, nil, sw)
  UI.stat('skill', d.cooldown .. 's', x + 12 + sw * 2, y + h - 30, 12, nil, sw)
end
local function polygon(mode, coords)
  local out = {}
  for i = 1, #coords, 2 do
    local x, y = I.project(coords[i], coords[i + 1])
    out[#out + 1] = x
    out[#out + 1] = y
  end
  G.polygon(mode, unpack(out))
end
function UI.arena(a)
  G.push()
  if UI.shake and not UI.reducedMotion and (a.shake or 0) > 0 then
    local power = (a.shakePower or 3) * math.min(1, a.shake / 0.12)
    G.translate(math.sin((UI.time or 0) * 91) * power, math.cos((UI.time or 0) * 77) * power * 0.6)
  end
  if not T.floor(a.encounter.element, a.hell, a.time) then
    G.setColor(0.07, 0.16, 0.17)
    polygon('fill', { -350, -350, 350, -350, 350, 350, -350, 350 })
    G.setColor(0.14, 0.25, 0.25)
    G.setLineWidth(1)
    for i = -350, 350, 70 do
      local x, y = I.project(i, -350)
      local x2, y2 = I.project(i, 350)
      G.line(x, y, x2, y2)
      x, y = I.project(-350, i)
      x2, y2 = I.project(350, i)
      G.line(x, y, x2, y2)
    end
  end
  require('src.render.scenery').arena(a)
  local activeData = H.byId[a:hero().id]
  if activeData.style == 'Melee' then
    local x, y = I.project(a.x, a.y)
    G.setColor(0.85, 0.88, 0.68, 0.18)
    G.ellipse('line', x, y, activeData.reach * 1.103, activeData.reach * 0.552)
  end
  for _, h in ipairs(a.hazards) do
    G.setColor(h.t > 0 and { 1, 0.66, 0.22, 0.42 } or { 1, 0.22, 0.18, 0.65 })
    if h.kind == 'lane' then
      if h.axis == 'x' then
        polygon(
          'fill',
          { h.center - h.r, -350, h.center + h.r, -350, h.center + h.r, 350, h.center - h.r, 350 }
        )
      else
        polygon(
          'fill',
          { -350, h.center - h.r, 350, h.center - h.r, 350, h.center + h.r, -350, h.center + h.r }
        )
      end
    elseif h.kind == 'bolt' or h.kind == 'sweep' then
      local nx, ny = -h.dy * h.r, h.dx * h.r
      local back = h.kind == 'sweep' and -700 or 0
      local length = h.kind == 'sweep' and 700 or 650
      polygon('fill', {
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
        if math.abs((mid - h.gap + math.pi) % (2 * math.pi) - math.pi) > h.gapWidth then
          polygon('fill', {
            h.x + math.cos(t1) * (h.r - width),
            h.y + math.sin(t1) * (h.r - width),
            h.x + math.cos(t2) * (h.r - width),
            h.y + math.sin(t2) * (h.r - width),
            h.x + math.cos(t2) * (h.r + width),
            h.y + math.sin(t2) * (h.r + width),
            h.x + math.cos(t1) * (h.r + width),
            h.y + math.sin(t1) * (h.r + width),
          })
        end
      end
      local gx, gy = I.project(h.x + math.cos(h.gap) * h.r, h.y + math.sin(h.gap) * h.r)
      UI.text('GAP', gx - 30, gy - 8, 12, { 0.55, 1, 0.7 }, 60, 'center')
      if h.kind == 'gravity' then
        local x, y = I.project(h.x, h.y)
        UI.text(
          h.force > 0 and 'PULL / ESCAPE VIA GAP' or 'PUSH / ESCAPE VIA GAP',
          x - 150,
          y + 32,
          13,
          nil,
          300,
          'center'
        )
      end
    elseif h.kind == 'pressure' then
      local x, y = I.project(-260, 200)
      local ex, ey = I.project(-260 + h.dx * 65, 200 + h.dy * 65)
      G.setLineWidth(4)
      G.line(x, y, ex, ey)
      G.circle('fill', ex, ey, 5)
      G.setLineWidth(1)
      UI.text('WIND PRESSURE', x - 80, y + 15, 12, nil, 170)
    else
      local x, y = I.project(h.x, h.y)
      G.ellipse('fill', x, y, h.r * 1.103, h.r * 0.552)
      if h.t > 0 and h.kind == 'slam' then
        local progress = 1 - h.t / h.warning
        G.setColor(1, 0.85, 0.5, 0.8)
        G.ellipse('line', x, y, h.r * 1.103 * progress, h.r * 0.552 * progress)
        UI.text('SLAM', x - 40, y - 8, 12, nil, 80, 'center')
      end
      if h.kind == 'patch' and h.t > 0 then
        G.ellipse('line', x, y, h.maxr * 1.103, h.maxr * 0.552)
      end
      if h.kind == 'pillar' then
        if h.eruption then
          G.setColor(h.t < -2.4 and { 1, 0.2, 0.1, 0.7 } or { 1, 0.7, 0.2, 0.45 })
          G.ellipse('line', x, y, (h.r + 42) * 1.103, (h.r + 42) * 0.552)
        end
        if h.t <= 0 then
          G.setColor(0.5, 0.42, 0.28)
          if not require('src.data.presentation').combatArt then
            G.rectangle('fill', x - 22, y - 55, 44, 55)
          end
        end
      end
    end
    Art.hazard(a, h, UI.reducedMotion)
    if h.kind == 'pillar' and h.t <= 0 then
      local x, y = I.project(h.x, h.y)
      UI.text(h.eruption and 'ERUPTS' or 'ROCK', x - 40, y - 64, 11, nil, 80, 'center')
    end
  end
  for _, f in ipairs(a.fields) do
    local x, y = I.project(f.x, f.y)
    G.setColor(H.colors[f.element])
    G.ellipse('line', x, y, f.radius * 1.1, f.radius * 0.55)
    if not Art.field(f, a.time, UI.reducedMotion) then
      FX.draw(f.element, x, y - 8, math.min(190, f.radius * 1.6), (a.time * 0.8) % 1, UI.reducedMotion, 0.38)
    end
    UI.text(f.element, x - 60, y - 8, 12, H.colors[f.element], 120, 'center')
    if f.shape == 'orbit' then
      for j = 1, 3 do
        local angle = (UI.reducedMotion and 0 or a.time * 4) + j * math.pi * 2 / 3
        local ox, oy = I.project(f.x + math.cos(angle) * f.radius, f.y + math.sin(angle) * f.radius)
        G.circle('fill', ox, oy - 8, 7)
      end
    end
  end
  local function actor(x, y, boss)
    local sx, sy = I.project(x, y)
    G.setColor(0, 0, 0, 0.3)
    G.ellipse('fill', sx, sy + 5, boss and 38 or 20, boss and 17 or 10)
    local c = boss and H.colors[a.encounter.element] or H.colors[H.byId[a:hero().id].element]
    G.setColor(c)
    if boss then
      sy = sy - (UI.reducedMotion and 0 or math.sin(a.time * 4) * 2)
    end
    if boss then
      G.setColor(c[1], c[2], c[3], 0.25)
      G.ellipse('line', sx, sy + 4, 62, 27)
      G.setColor(c)
      Emblem.draw(a.encounter.element, sx, sy - 111, 12)
      if
        not SP.drawBoss(a.encounter.id, sx, sy, a, UI.reducedMotion)
        and not UI.sprite(SP.boss(a.encounter.id, a.hell, a.phase), sx, sy - 46, 120)
      then
        local n = a.encounter.index
        G.setColor(c)
        if n == 2 then
          G.polygon('fill', sx, sy - 90, sx - 38, sy - 8, sx + 38, sy - 8)
          G.ellipse('line', sx, sy - 40, 50, 17)
        elseif n == 3 then
          G.polygon('fill', sx, sy - 88, sx - 62, sy - 24, sx, sy - 42, sx + 62, sy - 24)
        elseif n == 4 then
          G.rectangle('fill', sx - 38, sy - 73, 76, 70, 5)
          G.rectangle('line', sx - 45, sy - 84, 90, 80, 5)
        elseif n == 5 then
          for j = 1, 6 do
            local t = j * math.pi / 3
            G.circle('line', sx + math.cos(t) * 26, sy - 45 + math.sin(t) * 25, 22, 5)
          end
          G.circle('fill', sx, sy - 45, 20, 5)
        elseif n == 6 then
          G.polygon('fill', sx, sy - 95, sx - 30, sy - 45, sx, sy - 5, sx + 30, sy - 45)
          G.line(sx - 40, sy - 75, sx + 40, sy - 15)
        elseif n == 7 then
          G.polygon(
            'fill',
            sx + 20,
            sy - 95,
            sx - 30,
            sy - 40,
            sx - 2,
            sy - 40,
            sx - 20,
            sy - 4,
            sx + 34,
            sy - 58,
            sx + 6,
            sy - 58
          )
        elseif n == 8 then
          G.circle('fill', sx, sy - 48, 30, 12)
          for j = 1, 8 do
            local t = j * math.pi / 4
            G.line(
              sx + math.cos(t) * 36,
              sy - 48 + math.sin(t) * 36,
              sx + math.cos(t) * 48,
              sy - 48 + math.sin(t) * 48
            )
          end
        elseif n == 9 then
          G.ellipse('line', sx, sy - 44, 52, 20)
          G.circle('fill', sx, sy - 44, 27, 6)
          G.polygon(
            'fill',
            sx - 28,
            sy - 64,
            sx - 34,
            sy - 91,
            sx - 10,
            sy - 76,
            sx,
            sy - 97,
            sx + 12,
            sy - 76,
            sx + 34,
            sy - 91,
            sx + 28,
            sy - 64
          )
        else
          G.rectangle('line', sx - 32, sy - 90, 64, 77, 4)
          G.rectangle('fill', sx - 44, sy - 44, 12, 44)
          G.rectangle('fill', sx + 32, sy - 44, 12, 44)
          G.rectangle('fill', sx - 32, sy - 23, 64, 13)
          G.circle('line', sx, sy - 59, 18, 8)
        end
        G.setColor(0.05, 0.08, 0.1)
        G.rectangle('fill', sx - 12, sy - 53, 24, 5)
      end
      if a.hell then
        G.setColor(1, 0.3, 0.2)
        G.circle('line', sx, sy - 45, 62, 10)
      end
    else
      local d = H.byId[a:hero().id]
      local modeled = SP.drawHero(d.id, sx, sy, a, UI.reducedMotion)
      local cy = sy - (modeled and 34 or 26)
      if not modeled and not UI.sprite(SP.hero(d.id), sx, cy, 58) then
        G.setColor(c)
        G.circle('fill', sx, sy - 20, 19, 3 + d.rarity)
        UI.text(d.element:sub(1, 2), sx - 20, sy - 29, 12, { 0.05, 0.1, 0.12 }, 40, 'center')
      end
      if a.invuln > 0 then
        G.setColor(c)
        G.ellipse('line', sx, cy, 28, modeled and 39 or 28)
      end
      if a:hero().shield > 0 then
        G.setColor(c)
        G.ellipse('line', sx, cy, 29, modeled and 42 or 36)
      end
    end
    local flash = boss and (a.bossFlash or 0) or (a.heroHurt or 0)
    if flash > 0 then
      G.setColor(1, boss and 0.96 or 0.35, boss and 0.8 or 0.25, math.min(0.8, flash * 6))
      G.setLineWidth(3)
      G.ellipse('line', sx, sy - (boss and 45 or 24), boss and 35 or 23, boss and 48 or 28)
      G.setLineWidth(1)
    end
    if not boss then
      local h = a:hero()
      G.setColor(0.03, 0.07, 0.08, 0.9)
      G.rectangle('fill', sx - 23, sy + 14, 46, 5)
      G.setColor(h.hp / h.maxhp < 0.3 and { 1, 0.3, 0.25 } or { 0.5, 0.9, 0.65 })
      G.rectangle('fill', sx - 22, sy + 15, 44 * h.hp / h.maxhp, 3)
    end
  end
  for _, hero in ipairs(a.run.team) do
    local visual = a.heroVisuals and a.heroVisuals[hero.id]
    if hero.hp <= 0 and hero ~= a:hero() and visual and visual.deathAt then
      local x, y = I.project(visual.deathX, visual.deathY)
      SP.drawHero(hero.id, x, y, a, UI.reducedMotion)
    end
  end
  if a.x + a.y < a.boss.x + a.boss.y then
    actor(a.x, a.y)
    actor(a.boss.x, a.boss.y, true)
  else
    actor(a.boss.x, a.boss.y, true)
    actor(a.x, a.y)
  end
  Art.status(a, UI.reducedMotion)
  for _, p in ipairs(a.projectiles) do
    if not Art.projectile(p, a.time, UI.reducedMotion, false) then
      local x, y = I.project(p.x, p.y)
      G.setColor(p.element and H.colors[p.element] or { 0.98, 0.9, 0.64 })
      local tx, ty = I.project(p.x - p.dx * 0.035, p.y - p.dy * 0.035)
      G.setLineWidth(p.element and 3 or 2)
      G.line(tx, ty - 14, x, y - 14)
      G.setLineWidth(1)
      G.circle('fill', x, y - 14, p.element and 6 or 4)
      if p.element then
        FX.draw(p.element, x, y - 14, 40, (a.time * 2) % 1, UI.reducedMotion, 0.65)
      end
    end
  end
  for _, p in ipairs(a.enemyProjectiles) do
    if not Art.projectile(p, a.time, UI.reducedMotion, true) then
      local x, y = I.project(p.x, p.y)
      G.setColor(1, 0.4, 0.18)
      G.circle('fill', x, y - 10, 11)
      G.setColor(1, 0.85, 0.4)
      G.circle('fill', x, y - 10, 5)
    end
  end
  for _, f in ipairs(a.feedback) do
    if not Art.feedback(f, UI.reducedMotion) then
      local x, y = I.project(f.x, f.y)
      local progress = 1 - f.t / f.life
      local c = f.color
      G.setColor(c[1], c[2], c[3], math.min(1, f.t / f.life * 1.5))
      G.setLineWidth(f.kind == 'slash' and 5 or 2)
      if f.kind == 'slash' then
        local theta = (math.atan2 or math.atan)(f.dy, f.dx)
        local coords = {}
        for j = 0, 20 do
          local angle = theta - 1.05 + j / 20 * 2.1
          local radius = f.radius * (UI.reducedMotion and 0.8 or (0.65 + progress * 0.35))
          local px, py = I.project(f.x + math.cos(angle) * radius, f.y + math.sin(angle) * radius)
          coords[#coords + 1], coords[#coords + 2] = px, py - 20
        end
        G.line(unpack(coords))
      elseif f.kind == 'hit' then
        local radius = UI.reducedMotion and 15 or 9 + progress * 22
        for j = 0, 7 do
          local theta = j * math.pi / 4
          G.line(
            x + math.cos(theta) * radius * 0.35,
            y - 30 + math.sin(theta) * radius * 0.35,
            x + math.cos(theta) * radius,
            y - 30 + math.sin(theta) * radius
          )
        end
        G.setColor(1, 1, 0.92, f.t / f.life)
        G.circle('fill', x, y - 30, 4 + f.t * 12, 4)
      elseif f.kind == 'muzzle' then
        local px, py = I.project(f.x + f.dx * 32, f.y + f.dy * 32)
        G.line(x, y - 22, px, py - 22)
        G.circle('line', px, py - 22, 5 + progress * 7, 4)
      elseif f.kind == 'dodge' then
        local px, py = I.project(f.x + f.dx * f.radius, f.y + f.dy * f.radius)
        G.line(x, y - 16, px, py - 16)
        G.ellipse('line', x, y, 20, 10)
      else
        local radius = f.radius * (UI.reducedMotion and 0.75 or (0.2 + progress))
        G.ellipse('line', x, y, radius * 1.103, radius * 0.552)
        if f.kind == 'shock' then
          G.ellipse('line', x, y, radius * 0.8, radius * 0.4)
        end
      end
      G.setLineWidth(1)
      if f.element then
        local size = f.kind == 'shock' and math.min(180, f.radius * 2) or f.kind == 'cast' and 92 or 76
        FX.draw(f.element, x, y - 16, size, progress, UI.reducedMotion, 0.8 * (1 - progress))
      end
    end
  end
  for _, p in ipairs(a.sparks) do
    local x, y = I.project(p.x, p.y)
    G.setColor(p.color)
    G.circle('fill', x, y - 30, 2 + p.t * 3)
  end
  for _, l in ipairs(a.labels) do
    local x, y = I.project(l.x, l.y)
    UI.text(
      l.text,
      x - 100,
      y - 60 - (UI.reducedMotion and 0 or (1.3 - l.t) * 35),
      18,
      l.color,
      200,
      'center'
    )
  end
  G.pop()
  if not UI.reducedMotion and (a.impactFrame or 0) > 0 then
    -- One short contrast frame, confined to the arena so HUD text remains stable.
    G.setColor(1, 0.86, 0.63, 0.08 * a.impactFrame / 0.07)
    G.rectangle('fill', 190, 210, 900, 335)
  end
  if a:hero().hp / a:hero().maxhp < 0.3 then
    G.setColor(0.8, 0.12, 0.08, 0.5)
    G.setLineWidth(3)
    G.rectangle('line', 5, 5, 1270, 710)
    G.setLineWidth(1)
  end
  UI.panel(358, 88, 564, 123)
  UI.text((a.hell and a.encounter.hellName or a.encounter.name):upper(), 390, 95, 22, nil, 500, 'center')
  UI.text(
    a.encounter.element .. ' / PHASE ' .. a.phase .. (a.stance and ' / ' .. a.stance or ''),
    360,
    191,
    13,
    H.colors[a.encounter.element],
    560,
    'center'
  )
  T.icon('heart', 374, 134, 21)
  UI.bar(390, 127, 500, 15, a.boss.hp / a.boss.maxhp, { 0.88, 0.3, 0.16 })
  UI.text(
    math.ceil(a.boss.hp)
      .. ' / '
      .. math.ceil(a.boss.maxhp)
      .. ' HP   '
      .. (a.boss.aura or 'No aura')
      .. '   Stagger '
      .. math.floor(a.boss.stagger)
      .. '%',
    390,
    148,
    13,
    nil,
    500,
    'center'
  )
  UI.inspect(
    358,
    88,
    564,
    123,
    a.hell and a.encounter.hellName or a.encounter.name,
    a.encounter.hint .. '\n100% stagger interrupts the boss. Different elements can trigger reactions.',
    H.colors[a.encounter.element]
  )
  UI.bar(390, 166, 500, 3, a.boss.stagger / 100, { 0.9, 0.72, 0.35 })
  UI.panel(45, 92, 245, 77)
  UI.stat('attack', 'THREAT / ' .. (a.hell and 'HELL' or tostring(a.run.floor)), 57, 102, 15, nil, 220)
  UI.text(
    string.format('%.0f damage · %.0f%% tempo', a.incoming, 100 / a.difficulty.cadence),
    59,
    133,
    14,
    nil,
    220
  )
  UI.inspect(
    45,
    92,
    245,
    77,
    'Encounter pressure',
    'Base hit damage. From floor 5, every cast adds an aimed follow-up to punish camping. Warnings stay fixed after appearing. Switches cannot reset shared attack or dodge recovery.'
  )
  if a.difficulty.tactics then
    local guarded = a:guarded()
    local color = guarded and { 0.75, 0.8, 0.86 } or { 0.45, 1, 0.64 }
    UI.panel(960, 143, 270, 96)
    UI.stat(
      guarded and 'shield' or 'attack',
      guarded and 'GUARDED / -55%' or 'OPEN / ATTACK NOW',
      972,
      152,
      15,
      color,
      245
    )
    UI.text('Resists ' .. a.encounter.element .. ' / 40%', 974, 180, 14, nil, 245)
    UI.text(
      (a.switchLock or 0) > 0 and string.format('Switch ready in %.1fs', a.switchLock)
        or 'Switch ready / 1–3',
      974,
      209,
      13,
      nil,
      245
    )
    UI.inspect(
      960,
      143,
      270,
      96,
      guarded and 'Break the guard' or 'Damage window',
      'Guard cuts direct damage by 55%. Compatible reactions open it for 2.5s. It also opens during stagger and the last 0.75s before the next cast. Stagger grants +30% damage. Avoid the boss element: it deals 40% less damage.',
      color
    )
  end
  if a.lastHit then
    local h = a.lastHit
    UI.text(
      h.name .. ' / ' .. h.kind:upper() .. ' / ' .. h.actual .. ' DAMAGE',
      390,
      172,
      12,
      { 0.61, 0.71, 0.66 },
      500,
      'center'
    )
  end
  for i = 1, 3 do
    local x = 45 + (i - 1) * 300
    local h = a.run.team[i]
    UI.panel(x, 599, 282, 89, i == a.active and { 0.15, 0.27, 0.25 } or nil)
    if h then
      local d = H.byId[h.id]
      G.setColor(H.colors[d.element])
      Emblem.draw(d.element, x + 259, 618, 10)
      UI.text(i .. '  ' .. d.name, x + 13, 608, 16, H.colors[d.element], 231)
      UI.bar(x + 13, 630, 256, 3, h.hp / h.maxhp, H.colors[d.element])
      UI.inspect(
        x + 8,
        603,
        265,
        50,
        d.name,
        d.passive
          .. '\n'
          .. (h.weapon and ('Weapon: ' .. require('src.data.items')[h.weapon].name) or 'No weapon equipped.')
          .. '\nShield absorbs damage before health. Fallen allies revive after a victory.',
        H.colors[d.element]
      )
      UI.stat(
        h.hp <= 0 and 'death' or 'heart',
        h.hp <= 0 and 'DEFEATED' or math.ceil(h.hp) .. '/' .. h.maxhp .. ' HP',
        x + 10,
        635,
        13,
        nil,
        160
      )
      if h.hp > 0 then
        UI.stat('shield', math.floor(h.shield), x + 183, 635, 13, nil, 87)
      end
      UI.stat(
        'skill',
        h.hp <= 0 and '—'
          or (
            (i == a.active and ((UI.skillKey or 'E') .. ' · ') or '')
            .. (h.cd <= 0 and 'READY' or string.format('%.1fs', h.cd))
          ),
        x + 10,
        659,
        13,
        nil,
        126
      )
      local dodgeCd = math.max(h.dodgeCd, a.dodgeLock or 0)
      UI.stat(
        'dodge',
        h.hp <= 0 and '—'
          or dodgeCd <= 0 and (i == a.active and (UI.dodgeKey or 'SPACE') or 'READY')
          or string.format('%.1fs', dodgeCd),
        x + 144,
        659,
        13,
        nil,
        126
      )
      UI.bar(x + 13, 681, 112, 3, h.hp > 0 and 1 - h.cd / d.cooldown or 0, H.colors[d.element])
      UI.bar(x + 147, 681, 112, 3, h.hp > 0 and 1 - dodgeCd / 1.3 or 0, { 0.6, 0.8, 0.9 })
      UI.inspect(
        x + 8,
        655,
        130,
        31,
        d.skill,
        d.element
          .. ' skill · '
          .. d.cooldown
          .. 's cooldown. Skills apply an elemental aura and can trigger reactions. Cooldowns recover while off field.',
        H.colors[d.element]
      )
      UI.inspect(
        x + 142,
        655,
        130,
        31,
        'Dodge',
        'Dodge through danger with brief invulnerability. With no movement held, dodge follows your facing. Cancels an unfinished melee swing. From floor 3, dodge recovery is shared across the team.'
      )
    else
      UI.text('Recruit an ally in the shop', x + 13, 630, 16, { 0.54, 0.66, 0.63 }, 256)
    end
  end
  local h = a:hero()
  local status = activeData.style == 'Melee'
      and ('MELEE / ' .. (math.max(h.basicCd, a.basicLock or 0) <= 0 and 'READY' or 'RECOVERING'))
    or (
      'RANGED / '
      .. (
        (h.reload or 0) > 0 and string.format('RELOADING %.1fs', h.reload)
        or ((h.ammo or activeData.magazine) .. ' / ' .. activeData.magazine .. ' SHOTS')
      )
    )
  T.icon(activeData.style == 'Melee' and 'attack' or 'ammo', 450, 532, 23)
  UI.text(status, 420, 524, 14, H.colors[activeData.element], 440, 'center')
  if (h.reload or 0) > 0 then
    G.setColor(0.2, 0.3, 0.3)
    G.rectangle('fill', 530, 546, 220, 4)
    G.setColor(H.colors[activeData.element])
    G.rectangle('fill', 530, 546, 220 * (1 - h.reload / activeData.reloadDuration), 4)
  end
  UI.inspect(
    420,
    524,
    440,
    28,
    activeData.style .. ' attacks',
    activeData.style == 'Melee'
        and 'Aim at the boss within melee range. Attacks slow movement; dodge cancels the swing.'
      or 'Five shots per magazine. Reload takes 1.65s. Your skill remains usable during reload.'
  )
  for i, id in ipairs(a.run.curios) do
    UI.item(id, 1180 - (i - 1) * 42, 116, 34)
  end
  T.icon('bag', 949, 618, 23)
  UI.text((UI.itemKeys or 'Q / R') .. '  consumables', 963, 610, 15, nil, 280)
  local names = {}
  for _, id in ipairs(a.run.consumables) do
    names[#names + 1] = require('src.data.items')[id].name
  end
  UI.text(table.concat(names, ' / '), 963, 638, 14, nil, 260)
  for i, id in ipairs(a.run.consumables) do
    UI.item(id, 980 + (i - 1) * 34, 677, 28)
  end
end
return UI
