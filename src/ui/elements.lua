-- Original vector emblems: every element has a distinct silhouette, independent of color.
local E = {}
local T = require('src.render.ui_textures')
function E.draw(element, x, y, r)
  if T.element(element, x, y, r * 2.7) then
    return
  end
  local g = love.graphics
  g.push()
  g.translate(x, y)
  g.scale(r / 12)
  g.setLineWidth(1.7)
  if element == 'Pyro' then
    g.polygon('line', 0, -12, 8, -1, 6, 9, 0, 12, -8, 7, -9, 0, -3, -5, -2, 3, 3, 1)
  elseif element == 'Hydro' then
    g.polygon('line', 0, -12, 8, 0, 9, 6, 4, 11, -4, 11, -9, 6, -8, 0)
    g.line(-4, 5, 0, 7, 4, 5)
  elseif element == 'Anemo' then
    g.line(-12, -5, 5, -5, 9, -9, 12, -5, 9, -1)
    g.line(-10, 3, 4, 3, 8, 7, 4, 10)
    g.line(-8, 10, -1, 10)
  elseif element == 'Geo' then
    g.polygon('line', 0, -12, 11, 0, 0, 12, -11, 0)
    g.polygon('line', 0, -5, 5, 0, 0, 5, -5, 0)
  elseif element == 'Dendro' then
    g.polygon('line', -8, 8, -9, -3, -2, -9, 11, -11, 9, 2, 3, 9)
    g.line(-10, 11, 6, -5)
  elseif element == 'Cryo' then
    for i = 0, 5 do
      local a = i * math.pi / 3
      g.line(0, 0, math.cos(a) * 12, math.sin(a) * 12)
      g.circle('fill', math.cos(a) * 8, math.sin(a) * 8, 1.8)
    end
  elseif element == 'Electro' then
    g.polygon('line', 3, -12, -9, 2, -1, 2, -4, 12, 10, -3, 2, -3)
  elseif element == 'Gravity' then
    g.ellipse('line', 0, 0, 12, 5)
    g.ellipse('line', 0, 0, 5, 12)
    g.circle('fill', 0, 0, 3)
  elseif element == 'Antimatter' then
    g.polygon('line', 0, -12, 11, 8, -11, 8)
    g.polygon('line', 0, 12, -11, -8, 11, -8)
  end
  g.pop()
  g.setLineWidth(1)
end
return E
