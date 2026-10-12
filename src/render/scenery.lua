-- Decorative meshes sit outside the walkable arena; they never imply collision.
local S = { images = {} }
function S.draw(id, x, y, size, opacity)
  if not require('src.data.presentation').useBackdrops then
    return false
  end
  local img = S.images[id]
  if not img then
    local path = 'assets/scenery/' .. id .. '.png'
    if not love.filesystem.getInfo(path) then
      return false
    end
    local ok, loaded = pcall(love.graphics.newImage, path)
    if not ok then
      return false
    end
    img = loaded
    img:setFilter('linear', 'linear')
    S.images[id] = img
  end
  love.graphics.setColor(1, 1, 1, opacity or 1)
  love.graphics.draw(img, x - size / 2, y - size / 2, 0, size / 256, size / 256)
  return true
end
function S.arena(a)
  S.draw('prop_' .. a.encounter.id, 139, 307, 130, 0.8)
  S.draw('prop_' .. a.encounter.id, 1141, 307, 130, 0.8)
end
return S
