-- Source-only encounter lab. This file is deliberately excluded from every package.
local M = require('src.run.model')
local H = require('src.data.heroes')
local Items = require('src.data.items')
local E = require('src.combat.equipment')
local UI = require('src.ui.draw')
local T = { floor = 1, seed = 2026, hero = 1, item = 1, invulnerable = false, speed = 1, ids = {} }
for id in pairs(Items) do
  T.ids[#T.ids + 1] = id
end
table.sort(T.ids)
function T.make()
  local r = M.new(T.seed)
  M.choose(r, 1)
  r.team = { H.instance(H.list[T.hero].id) }
  r.floor = T.floor
  r.key = T.floor > 10
  r.rewarded = T.floor - 1
  r.gold = 999
  return r
end
function T.draw(app, start)
  love.graphics.setColor(0, 0, 0, 0.9)
  love.graphics.rectangle('fill', 0, 0, 1280, 720)
  UI.buttons = {}
  UI.panel(180, 90, 920, 540)
  UI.text('ENCOUNTER LAB / SOURCE ONLY', 210, 115, 29)
  UI.text('Seed + floor + hero reproduce a fight. Lab runs never replace your save.', 210, 163, 17)
  local rows = {
    {
      'Floor: ' .. T.floor,
      function()
        T.floor = math.max(1, T.floor - 1)
      end,
      function()
        T.floor = math.min(1000000, T.floor + 1)
      end,
    },
    {
      'Seed: ' .. T.seed,
      function()
        T.seed = math.max(1, T.seed - 1)
      end,
      function()
        T.seed = T.seed % 2147483645 + 1
      end,
    },
    {
      H.list[T.hero].name,
      function()
        T.hero = (T.hero - 2) % #H.list + 1
      end,
      function()
        T.hero = T.hero % #H.list + 1
      end,
    },
    {
      Items[T.ids[T.item]].name,
      function()
        T.item = (T.item - 2) % #T.ids + 1
      end,
      function()
        T.item = T.item % #T.ids + 1
      end,
    },
  }
  for i, r in ipairs(rows) do
    local y = 205 + (i - 1) * 57
    UI.button('<', 210, y, 55, 44, r[2])
    UI.text(r[1], 285, y + 10, 20, nil, 500)
    UI.button('>', 790, y, 55, 44, r[3])
  end
  UI.button('Normal / Hell', 866, 205, 204, 44, function()
    T.floor = T.floor <= 10 and T.floor + 10 or (T.floor - 1) % 10 + 1
  end)
  UI.button('+100 floors', 866, 262, 204, 44, function()
    T.floor = math.min(1000000, T.floor + 100)
  end)
  UI.button('God: ' .. tostring(T.invulnerable), 866, 319, 204, 44, function()
    T.invulnerable = not T.invulnerable
  end)
  UI.button('Speed: ' .. T.speed .. 'x', 866, 376, 204, 44, function()
    T.speed = T.speed >= 4 and 0.5 or T.speed * 2
  end)
  UI.text(Items[T.ids[T.item]].description, 210, 438, 17, nil, 850)
  UI.button('Start / reproduce fight', 210, 513, 310, 46, function()
    start(T.make())
    app.lab = false
  end)
  UI.button('Give selected item', 537, 513, 275, 46, function()
    if not app.devRun then
      app.message = 'Start a lab fight first.'
      return
    end
    local id = T.ids[T.item]
    local d = Items[id]
    local r = app.run
    if d.kind == 'weapon' then
      r.team[app.arena.active].weapon = id
    elseif d.kind == 'curio' then
      if E.has(r, id) then
        app.message = 'Already equipped.'
        return
      end
      if #r.curios == 3 then
        table.remove(r.curios, 1)
      end
      r.curios[#r.curios + 1] = id
    else
      if #r.consumables == 2 then
        table.remove(r.consumables, 1)
      end
      r.consumables[#r.consumables + 1] = id
    end
    E.refresh(r)
    app.message = 'Given ' .. d.name
  end)
  UI.button('Close (F3)', 830, 513, 240, 46, function()
    app.lab = false
  end)
end
return T
