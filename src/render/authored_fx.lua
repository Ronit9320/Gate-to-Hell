-- Selected author-provided DreamLayer cutouts. Animate at draw time without
-- touching simulation state; keep hazard masks and their warning art intact.
local F = { images = {} }
local names = { hit = 'hit', critical = 'critical', slash = 'slash', shock = 'shock' }
function F.draw(id, x, y, size, progress, reducedMotion, rotation)
  local name = names[id]
  if not name or not love or not love.filesystem or not love.graphics.draw then
    return false
  end
  local G = love.graphics
  if F.images[name] == nil then
    local path = 'assets/effects/authored/' .. name .. '.png'
    local ok, img = false, nil
    if love.filesystem.getInfo(path) then
      ok, img = pcall(G.newImage, path)
    end
    F.images[name] = ok and img or false
    if ok then
      img:setFilter('linear', 'linear')
    end
  end
  local img = F.images[name]
  if not img then
    return false
  end
  local p = math.max(0, math.min(1, progress))
  local scale = reducedMotion and 0.85 or (id == 'shock' and (0.4 + p * 0.85) or (0.7 + p * 0.4))
  local opacity = (1 - p) * (reducedMotion and 0.45 or 0.9)
  local iw, ih = img:getDimensions()
  -- The crescent opens to the right in the source image. Turn its leading edge
  -- toward the attack direction; the shockwave is already drawn in perspective.
  local angle = id == 'slash' and (rotation + math.pi + (reducedMotion and 0 or (p - 0.5) * 0.7)) or 0
  G.setColor(1, 1, 1, opacity)
  G.draw(img, x, y, angle, size * scale / iw, size * scale / ih, iw / 2, ih / 2)
  return true
end
return F
