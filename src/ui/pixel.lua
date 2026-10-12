-- Pixel-art UI skin for House of Cinders.
-- Frames are assembled only from axis-aligned rectangles: hard corners, chunky
-- bevels and cut (notched) corners, so they read as pixel art and stay crisp
-- when the window is scaled. Coordinates are snapped to whole pixels. The
-- headless render stub used by the test suite provides setColor and rectangle,
-- which is all this module needs.
local G = love.graphics
local P = {}

P.palette = {
  ink = { 0.027, 0.045, 0.052 },
  slot = { 0.055, 0.115, 0.125 },
  slotHi = { 0.16, 0.26, 0.26 },
  gold = { 0.98, 0.87, 0.64 },
  amber = { 1, 0.83, 0.4 },
  muted = { 0.4, 0.47, 0.45 },
  danger = { 0.88, 0.3, 0.16 },
}

local function clamp01(v)
  if v < 0 then
    return 0
  elseif v > 1 then
    return 1
  end
  return v
end

local function rgba(c)
  return { c[1], c[2], c[3], c[4] or 1 }
end

-- Blend a colour toward white by amt (0..1); used for pixel highlights.
function P.light(c, amt)
  local o = rgba(c)
  for i = 1, 3 do
    o[i] = clamp01(o[i] + (1 - o[i]) * amt)
  end
  return o
end

-- Blend a colour toward black by amt (0..1); used for pixel shadows.
function P.dark(c, amt)
  local o = rgba(c)
  for i = 1, 3 do
    o[i] = clamp01(o[i] * (1 - amt))
  end
  return o
end

-- Fill a rectangle with its four corners cut back by n pixels (an octagon
-- assembled from three bands). n <= 0 yields a plain rectangle.
function P.oct(x, y, w, h, n, color)
  if w <= 0 or h <= 0 then
    return
  end
  x, y, w, h = math.floor(x + 0.5), math.floor(y + 0.5), math.floor(w + 0.5), math.floor(h + 0.5)
  n = math.max(0, math.floor(n or 0))
  if n * 2 >= w then
    n = math.floor((w - 1) / 2)
  end
  if n * 2 >= h then
    n = math.floor((h - 1) / 2)
  end
  G.setColor(color)
  if n <= 0 then
    G.rectangle('fill', x, y, w, h)
    return
  end
  G.rectangle('fill', x + n, y, w - 2 * n, n)
  G.rectangle('fill', x, y + n, w, h - 2 * n)
  G.rectangle('fill', x + n, y + h - n, w - 2 * n, n)
end

-- Draw an unfilled notched outline of thickness t along the four edges.
function P.ring(x, y, w, h, n, t, color)
  if w <= 0 or h <= 0 or t <= 0 then
    return
  end
  x, y, w, h = math.floor(x + 0.5), math.floor(y + 0.5), math.floor(w + 0.5), math.floor(h + 0.5)
  n = math.max(0, math.floor(n or 0))
  t = math.max(1, math.floor(t))
  G.setColor(color)
  G.rectangle('fill', x + n, y, w - 2 * n, t)
  G.rectangle('fill', x + n, y + h - t, w - 2 * n, t)
  G.rectangle('fill', x, y + n, t, h - 2 * n)
  G.rectangle('fill', x + w - t, y + n, t, h - 2 * n)
end

-- A pixel panel: coloured border, notched corners and a one/two-pixel bevel.
-- opts: fill, border, borderWidth, notch, bevel, light, shadow.
function P.frame(x, y, w, h, opts)
  opts = opts or {}
  if w <= 0 or h <= 0 then
    return
  end
  x, y, w, h = math.floor(x + 0.5), math.floor(y + 0.5), math.floor(w + 0.5), math.floor(h + 0.5)
  local fill = opts.fill or P.palette.slot
  local border = opts.border or P.dark(fill, 0.5)
  local bw = math.max(1, math.floor(opts.borderWidth or 1))
  local n = math.max(0, math.floor(opts.notch or 2))
  local bevel = math.max(0, math.floor(opts.bevel or 1))
  P.oct(x, y, w, h, n, border)
  local ix, iy, iw, ih = x + bw, y + bw, w - 2 * bw, h - 2 * bw
  if iw <= 0 or ih <= 0 then
    return
  end
  local inN = math.max(0, n - bw)
  P.oct(ix, iy, iw, ih, inN, fill)
  if bevel > 0 and iw > 2 * bevel + 2 * inN and ih > 2 * bevel + 2 * inN then
    local light = opts.light or P.light(fill, 0.22)
    local shadow = opts.shadow or P.dark(fill, 0.4)
    G.setColor(light)
    G.rectangle('fill', ix + inN, iy, iw - 2 * inN, bevel)
    G.rectangle('fill', ix, iy + inN, bevel, ih - 2 * inN)
    G.setColor(shadow)
    G.rectangle('fill', ix + inN, iy + ih - bevel, iw - 2 * inN, bevel)
    G.rectangle('fill', ix + iw - bevel, iy + inN, bevel, ih - 2 * inN)
  end
end

-- Choose a corner cut that stays proportionate to the element's height.
function P.notchFor(w, h)
  local small = math.min(w, h)
  return math.max(2, math.min(4, math.floor(small / 12)))
end

-- A pixel progress bar with a notched track and highlight-topped fill.
function P.bar(x, y, w, h, frac, color, track)
  frac = math.max(0, math.min(1, frac or 0))
  x, y, w, h = math.floor(x + 0.5), math.floor(y + 0.5), math.floor(w + 0.5), math.floor(h + 0.5)
  local n = math.max(1, math.min(2, math.floor(h / 6)))
  P.frame(x, y, w, h, { fill = track or { 0.05, 0.1, 0.11 }, notch = n, bevel = 1 })
  local ix, iy, iw, ih = x + 2, y + 2, w - 4, h - 4
  local fw = math.floor(iw * frac + 0.5)
  if fw > 0 and ih > 0 then
    local c = color or P.palette.danger
    P.oct(ix, iy, fw, ih, math.max(0, n - 1), c)
    G.setColor(P.light(c, 0.3))
    G.rectangle('fill', ix + 1, iy, math.max(0, fw - 2), 1)
  end
end

-- A chunky horizontal rule with end caps, for screen headers.
function P.rule(x1, x2, y, color, thickness)
  local c = color or { 0.21, 0.3, 0.29 }
  local t = thickness or 2
  x1, x2, y = math.floor(x1 + 0.5), math.floor(x2 + 0.5), math.floor(y + 0.5)
  G.setColor(c)
  G.rectangle('fill', x1, y, x2 - x1, t)
  G.setColor(P.dark(c, 0.45))
  G.rectangle('fill', x1, y + t, x2 - x1, 1)
  G.setColor(P.light(c, 0.25))
  G.rectangle('fill', x1, y - 1, 2, 1)
  G.rectangle('fill', x2 - 2, y - 1, 2, 1)
end

return P
