-- Loads the Blender-rendered UI art (assets/ui/*.png). Everything degrades to
-- the code-drawn pixel skin when a file is missing or the flag is off, so the
-- headless test stubs (which have no love.filesystem or love.graphics.draw)
-- keep working unchanged.
local T = { images = {}, failed = {}, slices = {}, cells = {}, time = 0, reducedMotion = false }
local presentation = require('src.data.presentation')
local function path(name)
  return 'assets/ui/' .. name .. '.png'
end
function T.enabled()
  return presentation.useBackdrops ~= false
end
function T.get(name)
  if T.images[name] ~= nil then
    return T.images[name] or nil
  end
  if T.failed[name] or not (love and love.filesystem and love.graphics and love.graphics.draw) then
    return nil
  end
  if not love.filesystem.getInfo(path(name)) then
    T.failed[name] = true
    return nil
  end
  local ok, img = pcall(love.graphics.newImage, path(name))
  if not ok or not img then
    T.failed[name] = true
    return nil
  end
  img:setFilter('linear', 'linear')
  T.images[name] = img
  return img
end
-- Fixed corners and stretched edges keep brass bevels consistent at every size.
function T.skin(name, x, y, w, h)
  if not T.enabled() or w <= 0 or h <= 0 then
    return false
  end
  local img = T.get(name)
  if not img then
    return false
  end
  local iw, ih = img:getDimensions()
  local border = 12
  local b = math.min(border, w / 3, h / 3)
  if not T.slices[name] then
    local quads = {}
    local xs, ys = { 0, border, iw - border }, { 0, border, ih - border }
    local widths, heights = { border, iw - border * 2, border }, { border, ih - border * 2, border }
    for row = 1, 3 do
      for col = 1, 3 do
        quads[#quads + 1] = {
          love.graphics.newQuad(xs[col], ys[row], widths[col], heights[row], iw, ih),
          widths[col],
          heights[row],
        }
      end
    end
    T.slices[name] = quads
  end
  local xs, ys = { x, x + b, x + w - b }, { y, y + b, y + h - b }
  local widths, heights = { b, w - b * 2, b }, { b, h - b * 2, b }
  love.graphics.setColor(1, 1, 1, 1)
  for row = 1, 3 do
    for col = 1, 3 do
      local q = T.slices[name][(row - 1) * 3 + col]
      love.graphics.draw(img, q[1], xs[col], ys[row], 0, widths[col] / q[2], heights[row] / q[3])
    end
  end
  return true
end

local animated = {
  coin = { 96, 96, 8 },
  infinity_key = { 96, 96, 8 },
  brazier = { 96, 96, 8 },
  ember_seal = { 96, 96, 8 },
  crystal = { 96, 96, 8 },
  cardback = { 160, 208, 8 },
  floor_rune = { 256, 128, 8 },
}
local elements =
  { Pyro = 0, Hydro = 1, Anemo = 2, Geo = 3, Dendro = 4, Cryo = 5, Electro = 6, Gravity = 7, Antimatter = 8 }
local items = {}
for i, name in ipairs({
  'scepter',
  'ember',
  'tide',
  'gale',
  'quarry',
  'thorn',
  'rime',
  'coil',
  'die',
  'ace',
  'tab',
  'fuse',
  'glass',
  'ash',
  'rain',
  'tailwind',
  'stone',
  'green',
  'cold',
  'copper',
  'flask',
  'aegis',
  'wind',
}) do
  items[name] = i - 1
end

function T.cell(name, index, fw, fh, columns, x, y, w, h, tint)
  if not T.enabled() then
    return false
  end
  local img = T.get(name)
  if not img then
    return false
  end
  local key = name .. ':' .. index
  if not T.cells[key] then
    local iw, ih = img:getDimensions()
    T.cells[key] =
      love.graphics.newQuad(index % columns * fw, math.floor(index / columns) * fh, fw, fh, iw, ih)
  end
  love.graphics.setColor(tint or { 1, 1, 1, 1 })
  love.graphics.draw(img, T.cells[key], x, y, 0, w / fw, h / fh)
  return true
end
function T.sprite(name, cx, cy, size, time, tint)
  local spec = animated[name]
  if not spec then
    return false
  end
  local index = T.reducedMotion and 0 or math.floor((time or T.time) * 8) % spec[3]
  local h = size * spec[2] / spec[1]
  return T.cell(name, index, spec[1], spec[2], spec[3], cx - size / 2, cy - h / 2, size, h, tint)
end
function T.element(element, cx, cy, size)
  local index = elements[element]
  return index ~= nil and T.cell('elements', index, 96, 96, 8, cx - size / 2, cy - size / 2, size, size)
end
function T.item(id, cx, cy, size)
  local index = items[id]
  return index ~= nil and T.cell('items', index, 96, 96, 8, cx - size / 2, cy - size / 2, size, size)
end
-- Draw a background to fill the logical screen, preserving the authored aspect.
function T.backdrop(name, w, h)
  if not T.enabled() then
    return false
  end
  local img = T.get(name)
  if not img then
    return false
  end
  local iw, ih = img:getDimensions()
  local s = math.max(w / iw, h / ih)
  love.graphics.setColor(1, 1, 1, 1)
  love.graphics.draw(img, (w - iw * s) / 2, (h - ih * s) / 2, 0, s, s)
  return true
end
-- Decorative motion stays out of the text areas and never consumes game RNG.
function T.ambience(title)
  T.sprite('brazier', title and 1190 or 32, title and 430 or 600, title and 100 or 42)
  T.sprite('brazier', title and 758 or 1248, title and 648 or 600, title and 62 or 42, T.time + 0.375)
  if T.reducedMotion then
    return
  end
  for i = 1, 12 do
    local phase = (T.time * 0.035 + i * 0.0833) % 1
    local x = i % 2 == 0 and 20 + i * 3 or 1210 + i * 3
    T.sprite('ember_seal', x + math.sin(T.time + i) * 4, 650 - phase * 530, 5, T.time + i)
  end
end
function T.floor(element, hell, time)
  if not T.enabled() then
    return false
  end
  local img = T.get('arena_floor_' .. element:lower()) or T.get('arena_floor')
  if not img then
    return false
  end
  love.graphics.setColor(1, 1, 1, 1)
  -- Camera centres the plane at 360; iso.project centres it at 345.
  love.graphics.draw(img, 0, -15)
  local I = require('src.render.iso')
  local tint = require('src.data.heroes').colors[element]
  T.sprite('floor_rune', 640, 345, 290, time, { tint[1], tint[2], tint[3], 0.12 })
  for i, p in ipairs({ { -375, 375 }, { 375, -375 } }) do
    local x, y = I.project(p[1], p[2])
    T.sprite('brazier', x, y - 13, 62, time + i * 0.375)
  end
  for i, p in ipairs({ { -390, 0 }, { 0, -390 }, { 390, 0 }, { 0, 390 } }) do
    local x, y = I.project(p[1], p[2])
    T.sprite('crystal', x, y - 8, 30, time + i * 0.25, hell and { 1, 0.3, 0.25 } or tint)
  end
  return true
end
local iconNames = {
  'heart',
  'shield',
  'attack',
  'skill',
  'dodge',
  'ammo',
  'bag',
  'team',
  'shop',
  'reroll',
  'door',
  'help',
  'settings',
  'sound',
  'save',
  'trophy',
  'death',
  'check',
  'close',
  'pause',
  'play',
  'back',
  'floor',
  'reaction',
}
local iconIndices = {}
for i, name in ipairs(iconNames) do
  iconIndices[name] = i - 1
end
function T.icon(name, cx, cy, size, tint)
  if name == 'gold' then
    return T.sprite('coin', cx, cy, size, nil, tint)
  end
  if name == 'key' then
    return T.sprite('infinity_key', cx, cy, size, nil, tint)
  end
  if items[name] ~= nil then
    return T.item(name, cx, cy, size)
  end
  local index = iconIndices[name]
  if index == nil then
    return false
  end
  return T.cell('icons', index, 96, 96, 8, cx - size / 2, cy - size / 2, size, size, tint)
end
return T
