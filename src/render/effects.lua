-- Blender-rendered cosmetic particles. No RNG or combat state is consumed here.
local E = { images = {}, failed = {}, quads = {} }
local elements = {
  Pyro = true,
  Hydro = true,
  Anemo = true,
  Geo = true,
  Dendro = true,
  Cryo = true,
  Electro = true,
  Gravity = true,
  Antimatter = true,
}
function E.frame(progress, reducedMotion)
  return reducedMotion and 4 or math.min(11, math.max(0, math.floor(progress * 12)))
end
function E.draw(element, x, y, size, progress, reducedMotion, opacity)
  if not elements[element] or not love or not love.graphics or not love.graphics.draw then
    return false
  end
  if not require('src.data.presentation').useBackdrops then
    return false
  end
  local img = E.images[element]
  if not img then
    local path = 'assets/effects/' .. element:lower() .. '.png'
    if E.failed[element] or not love.filesystem.getInfo(path) then
      return false
    end
    local ok, loaded = pcall(love.graphics.newImage, path)
    if not ok then
      E.failed[element] = true
      return false
    end
    img = loaded
    img:setFilter('linear', 'linear')
    E.images[element] = img
    E.quads[element] = {}
  end
  local frame = E.frame(progress, reducedMotion)
  local quad = E.quads[element][frame]
  if not quad then
    local iw, ih = img:getDimensions()
    quad = love.graphics.newQuad(frame % 6 * 192, math.floor(frame / 6) * 192, 192, 192, iw, ih)
    E.quads[element][frame] = quad
  end
  love.graphics.setColor(1, 1, 1, (opacity or 1) * (reducedMotion and 0.55 or 1))
  love.graphics.draw(img, quad, x - size / 2, y - size / 2, 0, size / 192, size / 192)
  return true
end
return E
