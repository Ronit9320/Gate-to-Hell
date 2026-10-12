-- Pure sprite-sheet addressing. Directions match Blender's game-space export.
local A = {}
function A.direction(dx, dy)
  if math.abs(dx) + math.abs(dy) < 0.001 then
    return 0
  end
  local angle = math.atan2 and math.atan2(dx, dy) or math.atan(dx, dy)
  return math.floor(angle / (math.pi / 4) + 0.5) % 8
end
function A.cell(meta, name, elapsed, reducedMotion)
  local animation = meta.animations[name] or meta.animations.idle
  local frame = reducedMotion and 0 or math.floor(math.max(0, elapsed) * animation.fps)
  if animation.loop then
    frame = frame % animation.frames
  else
    frame = math.min(frame, animation.frames - 1)
  end
  local index = animation.offset + frame
  return index % meta.columns * meta.width, math.floor(index / meta.columns) * meta.height
end
function A.pose(boss, time, reducedMotion, meta)
  if boss.hp <= 0 then
    return 'death', math.max(0, time - (boss.spriteDeathAt or time))
  end
  if meta and meta.animations.stagger and (boss.stun or 0) > 0 then
    return 'stagger', reducedMotion and 0 or time
  end
  if
    meta
    and meta.animations.recovery
    and boss.spriteRecoveryAt
    and time - boss.spriteRecoveryAt < 4 / 12
  then
    return 'recovery', time - boss.spriteRecoveryAt
  end
  if boss.spriteAttackAt then
    local elapsed = time - boss.spriteAttackAt
    -- Frame eight is the impact pose: line it up with the first hazard's warning.
    local tempo = boss.spriteAttackDuration and 7 / (boss.spriteAttackDuration * 12) or 1
    if elapsed * tempo < 10 / 12 then
      return 'attack', elapsed * tempo
    end
  end
  if boss.spriteHurtAt and time - boss.spriteHurtAt < 4 / 12 then
    return 'hurt', time - boss.spriteHurtAt
  end
  return 'idle', reducedMotion and 0 or time
end
-- Each hero keeps visual state outside the saved roster and combat RNG.
function A.heroPose(state, time, reducedMotion)
  state = state or {}
  local meta = require('src.data.hero_sprites')
  if state.deathAt then
    return 'death', reducedMotion and 1 or math.max(0, time - state.deathAt)
  end
  if reducedMotion then
    return 'idle', 0
  end
  for _, pose in ipairs({ 'dodge', 'hurt', 'skill', 'attack' }) do
    local at = state[pose .. 'At']
    local spec = meta.animations[pose]
    if at and time - at >= 0 and time - at < spec.frames / spec.fps then
      return pose, time - at
    end
  end
  return state.walking and 'walk' or 'idle', time
end
return A
