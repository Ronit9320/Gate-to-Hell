-- Generated art contract for scripts/blender/build_heroes.py.
return {
  path = 'assets/heroes/isometric/',
  width = 160,
  height = 192,
  columns = 6,
  rows = 7,
  anchorX = 80,
  anchorY = 154,
  scale = 0.70,
  animations = {
    idle = { offset = 0, frames = 6, fps = 10, loop = true },
    walk = { offset = 6, frames = 6, fps = 12, loop = true },
    attack = { offset = 12, frames = 6, fps = 18, loop = false },
    skill = { offset = 18, frames = 6, fps = 12, loop = false },
    dodge = { offset = 24, frames = 6, fps = 24, loop = false },
    hurt = { offset = 30, frames = 6, fps = 20, loop = false },
    death = { offset = 36, frames = 6, fps = 8, loop = false },
  },
}
