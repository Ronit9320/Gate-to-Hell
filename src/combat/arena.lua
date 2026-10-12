local U = require('src.core.util')
local H = require('src.data.heroes')
local R = require('src.data.reactions')
local D = require('src.combat.damage')
local I = require('src.render.iso')
local Items = require('src.data.items')
local E = require('src.combat.equipment')
local B = require('src.data.bosses')
local P = require('src.combat.patterns')
local Pool = require('src.core.pool')
local A = {}
A.__index = A
function A.new(run)
  E.refresh(run)
  local encounter, hell, cycle = B.get(run)
  local scale = B.scale(run)
  local self = setmetatable({
    run = run,
    encounter = encounter,
    hell = hell,
    cycle = cycle,
    phase = 1,
    time = 0,
    x = 0,
    y = 220,
    active = 1,
    heroVisuals = {},
    invuln = 0,
    dodge = 0,
    projectiles = {},
    enemyProjectiles = {},
    sparks = {},
    sparkPool = Pool.new(80),
    labelPool = Pool.new(40),
    visualRng = { seed = 8191 },
    fields = {},
    labels = {},
    effects = {},
    feedback = {},
    swings = {},
    attackSequence = 0,
    impactSequence = 0,
    hurtSequence = 0,
    hazards = {},
    attackTimer = 2,
    pattern = 0,
    stats = { damage = 0, reactions = 0 },
    rng = { seed = run.encounterSeed or run.seed },
    boss = {
      x = 0,
      y = -100,
      hp = math.min(8400, 308 * scale),
      maxhp = math.min(8400, 308 * scale),
      shield = 0,
      stagger = 0,
      stun = 0,
      immune = 0,
    },
    incoming = B.difficulty(run).damage,
    difficulty = B.difficulty(run),
    firstSkill = true,
  }, A)
  for _, h in ipairs(run.team) do
    self.heroVisuals[h.id] = { dx = 0, dy = -1, walking = false }
    local data = H.byId[h.id]
    h.ammo = h.ammo or data.magazine
    h.reload = h.reload or 0
    h.recovery = 0
  end
  return self
end
function A:label(text, x, y, color)
  if #self.labels >= 40 then
    self.labelPool:release(table.remove(self.labels, 1))
  end
  local label = self.labelPool:take()
  label.text, label.x, label.y, label.t, label.color = text, x, y, 1.3, color or { 1, 0.88, 0.62 }
  self.labels[#self.labels + 1] = label
end
-- Visual events use a separate RNG and bounded storage; they never change combat rolls.
function A:feedbackAt(kind, x, y, color, dx, dy, radius, element, art)
  if #self.feedback >= 32 then
    table.remove(self.feedback, 1)
  end
  self.feedback[#self.feedback + 1] = {
    kind = kind,
    art = art,
    element = element,
    x = x,
    y = y,
    color = color or { 1, 0.88, 0.6 },
    dx = dx or 1,
    dy = dy or 0,
    radius = radius or 36,
    t = (require('src.data.combat_art')[art or kind] or {}).duration or (kind == 'shock' and 0.5 or 0.22),
    life = (require('src.data.combat_art')[art or kind] or {}).duration or (kind == 'shock' and 0.5 or 0.22),
  }
end
function A:impact(x, y, radius)
  self:feedbackAt('shock', x, y, H.colors[self.encounter.element], nil, nil, radius, self.encounter.element)
  self.shake = math.max(self.shake or 0, 0.32)
  self.shakePower = math.max(self.shakePower or 0, 9)
  self.impactFrame = 0.07
  self.hitstop = math.max(self.hitstop or 0, 0.065)
  self.impactSequence = self.impactSequence + 1
end
function A:updateFeedback(dt)
  for _, key in ipairs({ 'shake', 'impactFrame', 'heroHurt', 'bossFlash' }) do
    self[key] = math.max(0, (self[key] or 0) - dt)
  end
  if self.shake == 0 then
    self.shakePower = 0
  end
  for i = #self.feedback, 1, -1 do
    local f = self.feedback[i]
    f.t = f.t - dt
    if f.t <= 0 then
      table.remove(self.feedback, i)
    end
  end
end
function A:reloadStart()
  local h = self:hero()
  local data = H.byId[h.id]
  if data.style ~= 'Ranged' or h.reload > 0 or h.ammo >= data.magazine then
    return false
  end
  h.reload = data.reloadDuration
  self:label('RELOAD', self.x, self.y, H.colors[data.element])
  self:feedbackAt('reload_start', self.x, self.y)
  return true
end
function A:melee(owner, dx, dy, damage, element, reach)
  if #self.swings >= 6 then
    return
  end
  self.swings[#self.swings + 1] = {
    owner = owner,
    x = self.x,
    y = self.y,
    dx = dx,
    dy = dy,
    damage = damage,
    element = element,
    reach = reach or 122,
    delay = 0.09,
  }
  self:feedbackAt('slash', self.x, self.y, element and H.colors[element] or nil, dx, dy, reach or 122)
end
function A:hero()
  return self.run.team[self.active]
end
function A:visualHero()
  local id = self:hero().id
  if not self.heroVisuals[id] then
    self.heroVisuals[id] = { dx = 0, dy = -1, walking = false }
  end
  return self.heroVisuals[id]
end
function A:switch(i)
  local nextH = self.run.team[i]
  if not nextH or nextH.hp <= 0 or i == self.active then
    return false
  end
  local old = self:hero()
  if self.difficulty.tactics and old.hp > 0 and (self.switchLock or 0) > 0 then
    return false
  end
  self.switchLock = self.difficulty.tactics and 1.25 or 0
  if old.id == 'dealer' and old.hydroApplied then
    nextH.switchBuff = 4
    old.hydroApplied = false
  end
  self:feedbackAt('switch_out', self.x, self.y)
  self.active = i
  self:feedbackAt('switch_in', self.x, self.y)
  self:visualHero().walking = false
  if nextH.id == 'volt' then
    nextH.charged = true
  end
  if nextH.weapon == 'scepter' then
    nextH.switchBuff = 4
  end
  return true
end
function A:damageHero(n)
  if self.debugInvulnerable or self.invuln > 0 or self:hero().hp <= 0 then
    return
  end
  local h = self:hero()
  local actual, shield = D.apply(h, n)
  local visual = self:visualHero()
  visual.hurtAt = self.time
  self:label('-' .. actual, self.x, self.y, { 1, 0.4, 0.4 })
  if shield > 0 then
    self:label('Shield ' .. shield, self.x, self.y + 35, { 0.6, 0.85, 1 })
    self:feedbackAt(h.shield > 0 and 'shield_absorb' or 'shield_break', self.x, self.y)
  end
  self.hurtSequence = self.hurtSequence + 1
  self.heroHurt = 0.2
  self.hitstop = math.max(self.hitstop or 0, 0.055)
  self:feedbackAt('hurt', self.x, self.y, { 1, 0.35, 0.28 })
  self.shake = math.max(self.shake or 0, 0.18)
  self.shakePower = math.max(self.shakePower or 0, 5)
  self.invuln = 0.3
  if h.hp <= 0 then
    visual.deathAt, visual.deathX, visual.deathY = self.time, self.x, self.y
    visual.walking = false
    for i, v in ipairs(self.run.team) do
      if v.hp > 0 then
        self:switch(i)
        return
      end
    end
    self.result = 'defeat'
  end
end
function A:stagger(n)
  local b = self.boss
  if b.immune > 0 or b.stun > 0 then
    return
  end
  b.stagger = b.stagger + n * ((b.iceOpening or 0) > 0 and 1.5 or 1)
  if b.stagger >= 100 then
    b.stagger = 0
    b.stun = 2.1
    self.hazards = {}
    self:label('STAGGER', b.x, b.y)
    self:feedbackAt('stagger', b.x, b.y)
    self:impact(b.x, b.y, 100)
  end
end
function A:guarded()
  return self.difficulty.tactics
    and self.boss.stun <= 0
    and (self.boss.guardBreak or 0) <= 0
    and self.attackTimer > 0.75
end
function A:hit(owner, base, element, triggered, periodicSkill, visualArt)
  local b = self.boss
  if b.hp <= 0 then
    return
  end
  local h = self.run.team[owner]
  local mult = E.has(self.run, 'glass') and 1.25 or 1
  if periodicSkill then
    mult = mult * E.periodic(self.run, h, element)
  end
  if not triggered then
    mult = mult * E.direct(self.run, h, element)
    if h.id == 'mason' and h.shield > 0 then
      mult = mult * 1.2
    end
    if h.id == 'briar' and #self.effects > 0 and element then
      mult = mult * 1.2
    end
    if h.id == 'whiteout' and b.immune > 0 then
      mult = mult * 1.25
    end
    if element and (h.switchBuff or 0) > 0 then
      mult = mult * 1.25
    end
    if element and (b.vulnerable or 0) > 0 then
      mult = mult * 1.25
    end
    if element and self.firstSkill then
      self.firstSkill = false
      for _, id in ipairs(self.run.curios or {}) do
        if id == 'ace' then
          mult = mult * 1.5
        end
      end
    end
    for _, id in ipairs(self.run.curios or {}) do
      if id == 'die' and U.random(self.rng) < 0.15 then
        mult = mult * 1.5
      end
    end
  end
  if h.id == 'laugh' and b.hp / b.maxhp < 0.25 then
    base = base + math.min(15, base * 0.2)
  end
  if self.difficulty.tactics then
    if not triggered and self:guarded() then
      mult = mult * 0.45
    end
    if element == self.encounter.element then
      mult = mult * 0.6
    end
    if b.stun > 0 then
      mult = mult * 1.3
    end
  end
  local actual = D.apply(b, D.amount(base, 0, mult))
  if actual > 0 then
    b.spriteHurtAt = self.time
    self.bossFlash = 0.09
    if not periodicSkill then
      local art = visualArt or (mult >= 1.5 and 'critical' or element and 'skill_' .. h.id or 'hit')
      self:feedbackAt('hit', b.x, b.y, element and H.colors[element] or nil, nil, nil, nil, element, art)
      if triggered or (not element and H.byId[h.id].style == 'Melee') then
        self.hitstop = math.max(self.hitstop or 0, triggered and 0.045 or 0.035)
      end
    else
      self:feedbackAt('dot', b.x, b.y)
    end
    if b.hp <= 0 and not b.spriteDeathAt then
      b.spriteDeathAt = self.time
      self:feedbackAt('defeat', b.x, b.y)
    end
  end
  self.stats.damage = self.stats.damage + actual
  self.lastHit = {
    base = base,
    mult = mult,
    actual = actual,
    name = H.byId[h.id].name,
    kind = periodicSkill and 'periodic' or triggered and 'reaction' or element and 'skill' or 'basic',
  }
  for i = 1, 4 do
    if #self.sparks < 80 then
      local spark = self.sparkPool:take()
      spark.x, spark.y, spark.t = b.x, b.y, 0.35
      spark.dx = U.random(self.visualRng) * 160 - 80
      spark.dy = U.random(self.visualRng) * 160 - 80
      spark.color = element and H.colors[element] or { 1, 0.85, 0.5 }
      self.sparks[#self.sparks + 1] = spark
    end
  end
  self:label(
    tostring(actual),
    b.x + U.random(self.visualRng, 40) - 20,
    b.y,
    element and H.colors[element] or nil
  )
  if not triggered then
    if h.id == 'frost' and b.aura == 'Cryo' then
      self:stagger(10)
    end
    if element then
      self:stagger(E.stagger(self.run, h, 6, element == 'Cryo'))
      if h.id == 'flint' then
        E.shield(self.run, h, 12, 30, true)
        h.shieldTime = 6
        if owner == self.active then
          self:feedbackAt('shield_create', self.x, self.y)
        end
      end
      if h.id == 'dealer' then
        h.hydroApplied = true
      end
      local aura = b.aura
      local r = R.apply(b, element, self.time)
      if r then
        if self.difficulty.tactics then
          b.guardBreak = 2.5
          self:label('GUARD BROKEN', b.x, b.y - 85)
        end
        self.stats.reactions = self.stats.reactions + 1
        self:label(r.name, b.x, b.y - 55, H.colors[element])
        self:feedbackAt(
          'reaction',
          b.x,
          b.y,
          H.colors[element],
          nil,
          nil,
          70,
          element,
          'reaction_' .. r.name:lower():gsub(' ', '_')
        )
        local p = E.reaction(self.run, h, r, aura, element)
        if r.name == 'Annihilation' and h.id == 'null' then
          p = p + 10 * (h.charge or 0)
          h.charge = 0
        elseif h.id == 'null' then
          h.charge = math.min(3, (h.charge or 0) + 1)
        end
        if h.id == 'jack' then
          h.charged = true
        end
        if h.id == 'penny' and h.healCd <= 0 then
          E.heal(self.run, h, 8)
          h.healCd = 5
          if owner == self.active then
            self:feedbackAt('heal', self.x, self.y)
          end
        end
        if h.id == 'oracle' then
          h.shield = math.min(30, h.shield + 16)
          h.shieldTime = 4
        end
        if h.id == 'zephyr' and r.name == 'Crosswind' and not h.refunded then
          h.cd = math.max(0, h.cd - 1)
          h.refunded = true
        end
        if r.effect == 'shield' then
          E.shield(self.run, h, p, 40, true)
          h.shieldTime = 6
          if owner == self.active then
            self:feedbackAt('shield_create', self.x, self.y)
          end
        elseif r.effect == 'stagger' then
          self:stagger(E.stagger(self.run, h, p, aura == 'Cryo' or element == 'Cryo'))
        elseif r.effect == 'vulnerable' then
          b.vulnerable = 5
        elseif r.effect == 'dot' or r.effect == 'delay' then
          if #self.effects < 12 then
            self.effects[#self.effects + 1] = {
              owner = owner,
              damage = p
                * (
                  (r.name == 'Bloom' and h.id == 'clover' or r.name == 'Live Wire' and h.id == 'count')
                    and 1.5
                  or 1
                ),
              ticks = r.effect == 'delay' and 1 or (h.id == 'match' and 6 or 4),
              timer = r.effect == 'delay' and 1.2 or 1,
              element = element,
              reaction = r.name,
            }
          end
        else
          self:hit(owner, p, element, true)
          if r.effect == 'collapse' then
            self:stagger(h.id == 'crown' and 50 or 25)
          end
        end
      end
    end
  end
  if b.hp <= 0 then
    self.result = 'victory'
  end
end
function A:fire(owner, dx, dy, damage, element, speed, angle)
  if #self.projectiles >= 80 then
    return
  end
  local c, s = math.cos(angle or 0), math.sin(angle or 0)
  self.projectiles[#self.projectiles + 1] = {
    x = self.x,
    y = self.y,
    dx = (dx * c - dy * s) * (speed or 550),
    dy = (dx * s + dy * c) * (speed or 550),
    owner = owner,
    hero = self.run.team[owner].id,
    art = element and 'skill_' .. self.run.team[owner].id or 'projectile',
    damage = damage,
    element = element,
    t = 2,
  }
end
function A:attack(tx, ty, skill)
  if self.result or self.dodge > 0 or (self.hitstop or 0) > 0 then
    return false
  end
  local h = self:hero()
  local data = H.byId[h.id]
  local dx, dy = U.norm(tx - self.x, ty - self.y)
  if not skill then
    if h.basicCd > 0 or h.reload > 0 or (self.basicLock or 0) > 0 then
      return false
    end
    if data.style == 'Ranged' and h.ammo <= 0 then
      self:reloadStart()
      return false
    end
    h.basicCd = data.basicInterval
    self.basicLock = self.difficulty.tactics and data.basicInterval or 0
    h.recovery = data.style == 'Melee' and 0.22 or 0.12
    self.attackSequence = self.attackSequence + 1
    local visual = self:visualHero()
    visual.attackAt, visual.dx, visual.dy = self.time, dx, dy
    local n = data.basic + (Items[h.weapon] and Items[h.weapon].attack or 0)
    if h.charged then
      n = n + (h.id == 'volt' and 16 or 12)
      h.charged = false
    end
    if data.style == 'Melee' then
      self:melee(self.active, dx, dy, n, nil, data.reach)
    else
      self:fire(self.active, dx, dy, n)
      self:feedbackAt('muzzle', self.x, self.y, H.colors[data.element], dx, dy)
      h.ammo = h.ammo - 1
      if h.ammo == 0 then
        self:reloadStart()
      end
    end
    return true
  end
  if h.cd > 0 or h.recovery > 0 then
    return false
  end
  h.cd = data.cooldown
  local visual = self:visualHero()
  visual.skillAt, visual.dx, visual.dy = self.time, dx, dy
  self:feedbackAt('cast', self.x, self.y, H.colors[data.element], dx, dy, nil, data.element, 'skill_' .. h.id)
  h.refunded = false
  local shape = data.shape
  local n = data.damage
  local element = data.element
  if element == 'Anemo' and E.has(self.run, 'tailwind') then
    h.haste = 2
  end
  if shape == 'fan' or shape == 'volley' then
    for i = -1, 1 do
      self:fire(self.active, dx, dy, n * 0.65, element, 460, i * 0.17)
    end
  elseif shape == 'strike' then
    self:melee(self.active, dx, dy, n * 1.5, element, 165)
  elseif shape == 'lance' or shape == 'gust' then
    self:fire(self.active, dx, dy, n * 1.25, element, 650)
  elseif shape == 'wave' then
    if #self.fields >= 24 then
      return true
    end
    self:fire(self.active, dx, dy, n, element, 400)
    self.fields[#self.fields + 1] = {
      x = self.x + dx * 150,
      y = self.y + dy * 150,
      radius = 200,
      delay = 0.65,
      ticks = 1,
      owner = self.active,
      damage = n * 0.6,
      element = element,
      shape = shape,
      hero = h.id,
      art = 'skill_' .. h.id,
    }
  else
    if #self.fields < 24 then
      local dist = math.min(340, U.dist(self.x, self.y, tx, ty))
      local stationary = shape == 'orbit'
      local moving = shape == 'cyclone'
      self.fields[#self.fields + 1] = {
        x = stationary and self.x or (moving and self.x or self.x + dx * dist),
        y = stationary and self.y or (moving and self.y or self.y + dy * dist),
        dx = moving and dx * 130 or 0,
        dy = moving and dy * 130 or 0,
        radius = shape == 'orbit' and 180 or 125,
        delay = 0.65,
        ticks = (shape == 'detonation' or shape == 'eruption' or shape == 'ring') and 1 or 4,
        owner = self.active,
        damage = (shape == 'detonation' or shape == 'ring' or shape == 'eruption') and n * 1.5 or n * 0.55,
        element = element,
        shape = shape,
        hero = h.id,
        art = 'skill_' .. h.id,
      }
    end
  end
  return true
end
function A:dodgeStart(dx, dy)
  local h = self:hero()
  if h.dodgeCd > 0 or (self.dodgeLock or 0) > 0 then
    return
  end
  self.dodgeX, self.dodgeY = U.norm(dx, dy)
  local visual = self:visualHero()
  visual.dodgeAt = self.time
  if self.dodgeX ~= 0 or self.dodgeY ~= 0 then
    visual.dx, visual.dy = self.dodgeX, self.dodgeY
  end
  h.dodgeCd = 1.3
  self.dodgeLock = self.difficulty.tactics and 1.3 or 0
  h.recovery = 0
  for i = #self.swings, 1, -1 do
    if self.swings[i].owner == self.active then
      table.remove(self.swings, i)
    end
  end
  self.dodge = 0.2
  self:feedbackAt('dodge', self.x, self.y, H.colors[H.byId[h.id].element], self.dodgeX, self.dodgeY, 55)
  self.invuln = 0.25
  if h.id == 'gale' then
    h.haste = 2
  end
end
function A:consume(i)
  local id = self.run.consumables[i]
  local h = self:hero()
  if not id or h.hp <= 0 then
    return false
  end
  if id == 'flask' then
    if h.hp == h.maxhp then
      return false
    end
    E.heal(self.run, h, 45)
  elseif id == 'aegis' then
    if h.shield >= 40 and h.shieldTime >= 6 then
      return false
    end
    h.shield = math.min(40, h.shield + 30)
    h.shieldTime = 6
  elseif id == 'wind' then
    if h.cd <= 0 then
      return false
    end
    h.cd = math.max(0, h.cd - 3)
  end
  self:label(Items[id].name, self.x, self.y)
  self:feedbackAt('consume', self.x, self.y, nil, nil, nil, nil, nil, 'consume_' .. id)
  table.remove(self.run.consumables, i)
  return true
end
function A:update(dt, mx, my)
  dt = math.min(dt, 0.05)
  self:updateFeedback(dt)
  if (self.hitstop or 0) > 0 then
    self.hitstop = math.max(0, self.hitstop - dt)
    return
  end
  if self.result then
    return
  end
  dt = math.min(dt, 0.05)
  self.time = self.time + dt
  for _, key in ipairs({ 'switchLock', 'basicLock', 'dodgeLock' }) do
    self[key] = math.max(0, (self[key] or 0) - dt)
  end
  local b = self.boss
  b.guardBreak = math.max(0, (b.guardBreak or 0) - dt)
  local phase = b.hp / b.maxhp <= (self.encounter.index == 10 and 0.33 or 0) and 3
    or b.hp / b.maxhp <= (self.encounter.index == 10 and 0.67 or 0.5) and 2
    or 1
  if phase > self.phase then
    self.phase = phase
    self.hazards = {}
    self.enemyProjectiles = {}
    self.attackTimer = 1.8
    self:label('PHASE ' .. phase, b.x, b.y - 70)
    self:feedbackAt('phase', b.x, b.y)
  end
  b.iceOpening = math.max(0, (b.iceOpening or 0) - dt)
  self.invuln = math.max(0, self.invuln - dt)
  for _, h in ipairs(self.run.team) do
    for _, k in ipairs({
      'cd',
      'basicCd',
      'dodgeCd',
      'healCd',
      'haste',
      'switchBuff',
      'shieldTime',
      'recovery',
    }) do
      h[k] = math.max(0, (h[k] or 0) - dt)
    end
    if (h.reload or 0) > 0 then
      h.reload = math.max(0, h.reload - dt)
      if h.reload == 0 then
        h.ammo = H.byId[h.id].magazine
        if h == self:hero() then
          self:feedbackAt('reload_complete', self.x, self.y)
        end
      end
    end
    if h.shieldTime <= 0 then
      if h.shield > 0 and h == self:hero() then
        self:feedbackAt('shield_break', self.x, self.y)
      end
      h.shield = 0
    end
  end
  if b.stun > 0 then
    b.stun = math.max(0, b.stun - dt)
    if b.stun == 0 then
      b.immune = self.difficulty.tactics and 8 or 4
      b.spriteRecoveryAt = self.time
      self:feedbackAt('recovery', b.x, b.y)
    end
  else
    b.immune = math.max(0, b.immune - dt)
  end
  b.vulnerable = math.max(0, (b.vulnerable or 0) - dt)
  if b.aura and b.auraEnd and self.time >= b.auraEnd then
    self:feedbackAt('expiry', b.x, b.y, nil, nil, nil, nil, nil, 'aura_' .. b.aura:lower())
    b.aura = nil
  end
  local speed = (self:hero().haste or 0) > 0 and 250 or 185
  if self:hero().recovery > 0 then
    speed = speed * 0.65
  end
  if self.dodge > 0 then
    self.dodge = self.dodge - dt
    mx, my = self.dodgeX, self.dodgeY
    speed = 650
  end
  if mx ~= 0 or my ~= 0 then
    mx, my = U.norm(mx, my)
    local visual = self:visualHero()
    visual.walking = true
    if self.time - math.max(visual.attackAt or -1, visual.skillAt or -1) >= 0.5 then
      visual.dx, visual.dy = mx, my
    end
    self.x = U.clamp(self.x + mx * speed * dt, -350, 350)
    self.y = U.clamp(self.y + my * speed * dt, -350, 350)
  else
    self:visualHero().walking = false
  end
  local d = U.dist(self.x, self.y, b.x, b.y)
  if d < 48 then
    local x, y = U.norm(self.x - b.x, self.y - b.y)
    self.x = b.x + x * 48
    self.y = b.y + y * 48
  end
  for i = #self.swings, 1, -1 do
    local swing = self.swings[i]
    swing.delay = swing.delay - dt
    if swing.delay <= 0 then
      -- A committed swing retains its origin and direction; switching cannot retarget it.
      local vx, vy = b.x - swing.x, b.y - swing.y
      local distance = U.dist(swing.x, swing.y, b.x, b.y)
      if
        self.run.team[swing.owner].hp > 0
        and distance <= swing.reach + 30
        and (vx * swing.dx + vy * swing.dy) / math.max(1, distance) >= 0.45
      then
        self:hit(swing.owner, swing.damage, swing.element)
      end
      table.remove(self.swings, i)
    end
  end
  for i = #self.projectiles, 1, -1 do
    local p = self.projectiles[i]
    local ox, oy = p.x, p.y
    p.x = p.x + p.dx * dt
    p.y = p.y + p.dy * dt
    p.t = p.t - dt
    local vx, vy = p.x - ox, p.y - oy
    local t = U.clamp(((b.x - ox) * vx + (b.y - oy) * vy) / math.max(0.001, vx * vx + vy * vy), 0, 1)
    if U.dist(ox + vx * t, oy + vy * t, b.x, b.y) < 42 then
      self:hit(p.owner, p.damage, p.element)
      table.remove(self.projectiles, i)
    elseif p.t <= 0 then
      table.remove(self.projectiles, i)
    end
  end
  for i = #self.fields, 1, -1 do
    local f = self.fields[i]
    f.x = f.x + (f.dx or 0) * dt
    f.y = f.y + (f.dy or 0) * dt
    f.delay = f.delay - dt
    if f.delay <= 0 then
      if U.dist(f.x, f.y, b.x, b.y) <= f.radius + 30 then
        self:hit(f.owner, f.damage, f.element, f.applied, f.applied)
        f.applied = true
      end
      f.ticks = f.ticks - 1
      f.delay = 0.6
      if f.ticks <= 0 then
        table.remove(self.fields, i)
      end
    end
  end
  for i = #self.effects, 1, -1 do
    local e = self.effects[i]
    e.timer = e.timer - dt
    if e.timer <= 0 then
      self:hit(e.owner, e.damage, e.element, true, false, e.reaction == 'Bloom' and 'reaction_bloom' or 'dot')
      e.ticks = e.ticks - 1
      e.timer = 1
      if e.ticks <= 0 then
        table.remove(self.effects, i)
      end
    end
  end
  if b.stun <= 0 then
    self.attackTimer = self.attackTimer - dt
    if self.attackTimer <= 0 then
      self.pattern = self.pattern + 1
      b.spriteAttackAt = self.time
      local firstNewHazard = #self.hazards + 1
      P.cast(self)
      b.spriteAttackDuration = 1.2
      for i = firstNewHazard, #self.hazards do
        b.spriteAttackDuration = math.min(b.spriteAttackDuration, self.hazards[i].warning)
      end
    end
  end
  P.update(self, dt)
  for i = #self.enemyProjectiles, 1, -1 do
    local p = self.enemyProjectiles[i]
    p.x = p.x + p.dx * dt
    p.y = p.y + p.dy * dt
    p.t = p.t - dt
    if U.dist(self.x, self.y, p.x, p.y) < 28 then
      self:damageHero(self.incoming)
      table.remove(self.enemyProjectiles, i)
    elseif p.t <= 0 then
      table.remove(self.enemyProjectiles, i)
    end
  end
  for i = #self.sparks, 1, -1 do
    local p = self.sparks[i]
    p.t = p.t - dt
    p.x = p.x + p.dx * dt
    p.y = p.y + p.dy * dt
    if p.t <= 0 then
      self.sparkPool:release(table.remove(self.sparks, i))
    end
  end
  for i = #self.labels, 1, -1 do
    local l = self.labels[i]
    l.t = l.t - dt
    if l.t <= 0 then
      self.labelPool:release(table.remove(self.labels, i))
    end
  end
  if self.result ~= 'defeat' and b.hp <= 0 then
    self.result = 'victory'
  end
end
return A
