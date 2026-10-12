-- Original Blender bosses. Fixed ground anchors and shared clip offsets.
local B = {
  path = 'assets/bosses/isometric/',
  width = 192,
  height = 192,
  columns = 8,
  rows = 5,
  anchorX = 96,
  anchorY = 146,
  scale = 0.85,
  animations = {
    idle = { offset = 0, frames = 8, fps = 12, loop = true },
    attack = { offset = 8, frames = 10, fps = 12, loop = false },
    hurt = { offset = 18, frames = 4, fps = 12, loop = false },
    death = { offset = 22, frames = 10, fps = 10, loop = false },
    stagger = { offset = 32, frames = 4, fps = 8, loop = true },
    recovery = { offset = 36, frames = 4, fps = 12, loop = false },
  },
}
function B.appearance(id, hell, phase)
  local name = id .. (hell and '_hell' or '')
  if id == 'throne' and (phase or 1) > 1 then
    name = name .. '_phase' .. math.min(3, phase)
  end
  return name
end
return B
