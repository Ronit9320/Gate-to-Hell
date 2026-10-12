local H = require('src.data.heroes')
local A = require('src.combat.arena')
local UI = require('src.ui.draw')
local I = require('src.render.iso')
local UTex = require('src.render.ui_textures')
local M = require('src.run.model')
local Items = require('src.data.items')
local Save = require('src.core.save')
local Settings = require('src.core.settings')
local Audio = require('src.core.audio')
local Dev
local app = { screen = 'title', paused = false, message = '', clock = 0, menuKeys = {} }
local function menuContext()
  return app.screen
    .. ':'
    .. tostring(app.paused)
    .. ':'
    .. (app.modal and app.modal.kind or '')
    .. ':'
    .. tostring(app.lab)
end
local function queueMenu(k)
  if
    k == 'tab'
    or k == 'up'
    or k == 'down'
    or k == 'left'
    or k == 'right'
    or k == 'return'
    or k == 'space'
  then
    if #app.menuKeys < 16 then
      app.menuKeys[#app.menuKeys + 1] = { k, love.keyboard.isDown('lshift', 'rshift') }
    end
    return true
  end
end
local function saveSettings()
  app.muted = app.settings.muted
  if not Settings.write(app.settings, love.filesystem) then
    app.saveWarning = 'Settings could not be saved.'
  end
end
local function mouse()
  local w, h = love.graphics.getDimensions()
  local s = math.min(w / 1280, h / 720)
  local x, y = love.mouse.getPosition()
  return (x - (w - 1280 * s) / 2) / s, (y - (h - 720 * s) / 2) / s
end
-- Mouse aim over the raised boss silhouette resolves to its ground anchor.
local function aim()
  local x, y = mouse()
  if app.arena then
    local bx, by = I.project(app.arena.boss.x, app.arena.boss.y)
    if math.abs(x - bx) < 44 and y >= by - 88 and y <= by + 20 then
      return app.arena.boss.x, app.arena.boss.y
    end
  end
  return I.inverse(x, y)
end
local function move()
  local x = (love.keyboard.isDown('d', 'right') and 1 or 0) - (love.keyboard.isDown('a', 'left') and 1 or 0)
  local y = (love.keyboard.isDown('s', 'down') and 1 or 0) - (love.keyboard.isDown('w', 'up') and 1 or 0)
  return I.screenVector(x, y)
end
local function persist()
  if app.devRun or not app.run then
    return
  end
  local ok, err = Save.write(app.run)
  app.saved = require('src.core.util').copy(app.run)
  if not ok then
    app.saveWarning = err
  end
end
local function sync()
  app.screen = app.run.stage
  app.modal = nil
  app.message = ''
  persist()
end
local function newRun(mode)
  app.devRun = false
  app.run = M.new(os.time(), mode)
  app.arena = nil
  app.paused = false
  sync()
end
local function action(fn, ...)
  local ok, err = fn(app.run, ...)
  if not ok then
    app.message = err or 'Action unavailable.'
  else
    app.message = ''
    persist()
  end
  return ok
end
local function enter()
  if M.enter(app.run) then
    persist()
    app.arena = A.new(app.run)
    app.screen = 'arena'
    app.paused = false
    app.transition = 0.45
  end
end
local function sound(name)
  Audio.play(name or 'ui', app.settings)
end
function love.load()
  if love.filesystem.getInfo('devtools.lua') then
    Dev = require('devtools')
  end
  app.saved, app.saveWarning = Save.read()
  app.settings = Settings.read(love.filesystem)
  app.muted = app.settings.muted
  love.graphics.setDefaultFilter('linear', 'linear')
  if not Audio.load() then
    app.message = 'Audio unavailable; you can still play.'
  end
end
function love.update(dt)
  Audio.update(dt, app.settings, app.paused or app.focusLost, app.screen == 'arena')
  if #app.menuKeys > 0 and UI.context == menuContext() then
    local key = table.remove(app.menuKeys, 1)
    if UI.navigate(key[1], key[2]) then
      sound()
    end
  end
  app.transition = math.max(0, (app.transition or 0) - dt)
  app.clock = app.clock + dt
  UI.time = app.clock
  UI.reducedMotion = app.settings.reducedMotion
  UTex.time = app.clock
  UTex.reducedMotion = app.settings.reducedMotion
  UI.largeText = app.settings.largeText
  UI.shake = app.settings.shake
  UI.itemKeys = app.settings.firstItemKey:upper() .. ' / ' .. app.settings.secondItemKey:upper()
  if app.screen == 'arena' and not app.paused and not app.modal and not app.lab then
    local damageBefore, reactionsBefore = app.arena.stats.damage, app.arena.stats.reactions
    local hurtBefore = app.arena.hurtSequence
    local impactBefore = app.arena.impactSequence
    local x, y = move()
    app.arena.debugInvulnerable = Dev and app.devRun and Dev.invulnerable or false
    local remaining = math.min(dt, 0.1) * (Dev and app.devRun and Dev.speed or 1)
    while remaining > 0 do
      local step = math.min(remaining, 0.025)
      app.arena:update(step, x, y)
      remaining = remaining - step
    end
    if love.mouse.isDown(1) then
      local tx, ty = aim()
      if app.arena:attack(tx, ty) then
        sound('attack')
      end
    end
    if app.arena.stats.reactions > reactionsBefore then
      sound('reaction')
    elseif app.arena.stats.damage > damageBefore then
      sound('hit')
    end
    if app.arena.impactSequence > impactBefore then
      sound('impact')
    end
    if app.arena.hurtSequence > hurtBefore then
      sound('hurt')
    end
    if app.arena.result then
      if
        app.arena.result == 'defeat'
        and require('src.data.presentation').heroSprites
        and not app.settings.reducedMotion
      then
        app.arena.heroDeathElapsed = (app.arena.heroDeathElapsed or 0) + dt
        app.arena.heroSpriteTime = app.arena.time + app.arena.heroDeathElapsed
        if app.arena.heroDeathElapsed < 0.75 then
          return
        end
      end
      if
        app.arena.result == 'victory'
        and (require('src.data.presentation').bossSprites or (app.arena.encounter.id == 'bailiff' and require(
          'src.data.presentation'
        ).bailiffSprites))
        and not app.settings.reducedMotion
      then
        app.arena.bossDeathElapsed = (app.arena.bossDeathElapsed or 0) + dt
        app.arena.spriteTime = app.arena.time + app.arena.bossDeathElapsed
        if app.arena.bossDeathElapsed < 1 then
          return
        end
      end
      sound(app.arena.result == 'victory' and 'victory' or 'defeat')
      if app.arena.result == 'victory' then
        app.arena.stats.time = app.arena.time
        M.reward(app.run, app.arena.stats)
      else
        M.lose(app.run)
      end
      sync()
    end
  end
end
local function requestNew(mode)
  if app.saved and app.saved.stage ~= 'defeat' and app.saved.stage ~= 'complete' then
    app.modal = { kind = 'newrun', mode = mode }
  else
    newRun(mode)
  end
end
local function title()
  UI.text('A ROGUELIKE BOSS BATTLER', 80, 95, 14, { 0.73, 0.63, 0.42 })
  UI.text('HOUSE OF\nCINDERS', 76, 143, 78, { 0.96, 0.88, 0.69 }, 750)
  UI.text('One hero. Ten floors. A house that never folds.', 82, 355, 23, { 0.57, 0.73, 0.69 }, 650)
  UI.text(
    'Draft your hand. Master the elements.\nRecruit a team and challenge the endless House.',
    82,
    405,
    18,
    nil,
    640
  )
  UI.button('New run', 82, 500, 265, 52, function()
    requestNew('run')
  end)
  UI.button('Two-fight demo', 365, 500, 265, 52, function()
    requestNew('demo')
  end)
  if app.saved and app.saved.stage ~= 'complete' and app.saved.stage ~= 'defeat' then
    UI.button('Continue saved run', 82, 562, 548, 40, function()
      app.devRun = false
      app.run = Save.resume(app.saved)
      app.paused = false
      app.arena = nil
      sync()
    end)
  end
  UI.button(app.muted and 'Sound: OFF' or 'Sound: ON', 900, 550, 260, 40, function()
    app.settings.muted = not app.settings.muted
    saveSettings()
  end)
  UI.button('Settings / controls', 900, 600, 260, 36, function()
    app.modal = { kind = 'settings' }
  end)
  UI.button('How to play', 900, 646, 260, 36, function()
    app.modal = { kind = 'help' }
  end)
  UI.button('Credits · v0.9.0', 82, 651, 548, 35, function()
    app.modal = { kind = 'credits' }
  end)
  UI.card('jack', 900, 155, 260, 365)
  UI.text(
    'WASD / arrows move · mouse aims · click attacks\nE / right click skill · Space dodge · Esc pause',
    82,
    600,
    16,
    { 0.53, 0.67, 0.65 },
    730
  )
end
local function team(y)
  for i = 1, 3 do
    local x = 50 + (i - 1) * 395
    local h = app.run.team[i]
    if h then
      UI.card(h.id, x, y, 375, 112, true)
      UI.stat('heart', math.ceil(h.hp) .. ' / ' .. h.maxhp .. ' HP', x + 16, y + 64, 14, nil, 245)
      UI.stat('attack', h.weapon and Items[h.weapon].name or 'No weapon', x + 16, y + 85, 13, nil, 245)
    else
      if not UTex.skin('slot', x, y, 375, 112) then
        UI.panel(x, y, 375, 112)
      end
      UTex.sprite('cardback', x + 344, y + 56, 42)
      UI.text('EMPTY SLOT ' .. i, x + 20, y + 30, 18, { 0.41, 0.55, 0.52 }, 280)
      UI.text('Recruit a hero at the next shop.', x + 20, y + 62, 14, nil, 280)
    end
  end
end
local function preview()
  local floor, boss = M.floorInfo(app.run)
  UI.text(floor, 50, 128, 16, { 0.83, 0.66, 0.4 })
  UI.text(boss, 50, 166, 38, nil, 1150)
  UI.text(require('src.data.bosses').get(app.run).hint, 50, 233, 20, { 0.58, 0.74, 0.7 }, 1150)
  UI.stat('gold', 'Reward: ' .. (8 + app.run.floor) .. ' gold + full team heal', 50, 277, 18, nil, 1150)
  local encounter, hell = require('src.data.bosses').get(app.run)
  UI.sprite(require('src.render.sprites').boss(encounter.id, hell), 1125, 285, 140)
  if hell then
    require('src.render.scenery').draw('hell_entry', 870, 294, 105, 0.75)
    UI.text('HELL RULE: ' .. encounter.modifier, 50, 307, 16, { 1, 0.57, 0.4 }, 1150)
  end
  local difficulty = require('src.data.bosses').difficulty(app.run)
  UI.stat(
    'attack',
    string.format(
      'THREAT  /  %.0f HP  /  %.0f base damage  /  %.0f%% tempo',
      math.min(8400, 308 * require('src.data.bosses').scale(app.run)),
      difficulty.damage,
      100 / difficulty.cadence
    ),
    50,
    326,
    13,
    { 1, 0.65, 0.4 },
    900
  )
  UI.inspect(
    50,
    322,
    830,
    22,
    'Floor difficulty',
    'From floor 3: bosses guard between openings and resist their own element. Reactions break guard for 2.5s. From floor 5: every cast adds an aimed follow-up. Scout Run Info before shopping.'
  )
  team(345)
  UI.text(
    #app.run.team > 1 and '1 / 2 / 3 switches living heroes. Combine different skills for reactions.'
      or 'Your solo hero can clear this fight. Recruit allies after the first victory.',
    50,
    491,
    18,
    nil,
    1150
  )
  UI.button('Enter Floor', 930, 583, 300, 60, enter)
end
local function shop()
  UI.text('THE NIGHT MARKET', 50, 110, 30)
  UI.text(
    'Inspect an offer to buy. Recruit up to three heroes. Sold offers stay empty.',
    50,
    153,
    16,
    { 0.58, 0.74, 0.7 }
  )
  for i, o in ipairs(app.run.stock) do
    local x = 50 + (i - 1) * 238
    UI.panel(x, 196, 224, 205)
    local data = o.kind == 'hero' and H.byId[o.id] or Items[o.id]
    if o.kind == 'hero' then
      UTex.element(data.element, x + 29, 221, 29)
    else
      UI.item(o.id, x + 29, 221, 34)
    end
    UI.inspect(
      x + 8,
      235,
      208,
      112,
      data.name,
      o.kind == 'hero' and (data.skill .. '\n' .. data.passive) or data.description
    )
    UI.text(o.kind:upper(), x + 53, 213, 12, { 0.76, 0.62, 0.41 }, 155)
    UI.text(data.name, x + 15, 240, 22, nil, 194)
    UI.text(
      o.kind == 'hero' and (data.element .. ' · ' .. H.rarities[data.rarity])
        or (data.description:sub(1, 42) .. (#data.description > 42 and '...' or '')),
      x + 15,
      301,
      14,
      { 0.58, 0.74, 0.7 },
      194
    )
    UI.button(o.sold and 'SOLD' or ('Inspect · ' .. o.price .. ' gold'), x + 12, 354, 200, 34, function()
      app.modal = { kind = 'offer', index = i }
    end, o.sold)
  end
  team(426)
  for i, h in ipairs(app.run.team) do
    UI.button('Manage hero ' .. i, 50 + (i - 1) * 395, 548, 375, 32, function()
      app.modal = { kind = 'hero', index = i }
    end)
  end
  UI.button('Inventory', 50, 620, 240, 44, function()
    app.modal = { kind = 'inventory' }
  end)
  UI.button('Reroll · ' .. app.run.rerollCost .. ' gold', 310, 620, 240, 44, function()
    action(M.reroll)
  end)
  UI.button('Next floor', 970, 620, 260, 44, function()
    M.next(app.run)
    sync()
  end)
end
local function modal()
  local m = app.modal
  love.graphics.setColor(0, 0, 0, 0.8)
  love.graphics.rectangle('fill', 0, 0, 1280, 720)
  UI.buttons = {}
  UI.panel(260, 110, 760, 510)
  UI.button('Close', 867, 127, 132, 34, function()
    app.modal = nil
  end)
  if m.kind == 'settings' then
    UI.text('SETTINGS', 286, 150, 30)
    local rows = {
      {
        'Audio: ' .. (app.settings.muted and 'muted' or 'on'),
        function()
          app.settings.muted = not app.settings.muted
        end,
      },
      {
        'Volume: ' .. math.floor(app.settings.volume * 100) .. '%',
        function()
          app.settings.volume = (math.floor(app.settings.volume * 10 + 0.5) + 1) % 11 / 10
        end,
      },
      {
        'Reduced motion: ' .. tostring(app.settings.reducedMotion),
        function()
          app.settings.reducedMotion = not app.settings.reducedMotion
        end,
      },
      {
        'Screen shake: ' .. tostring(app.settings.shake),
        function()
          app.settings.shake = not app.settings.shake
        end,
      },
      {
        'Text size: ' .. (app.settings.largeText and 'large' or 'standard'),
        function()
          app.settings.largeText = not app.settings.largeText
        end,
      },
      {
        'Tutorial prompts: ' .. tostring(app.settings.tutorial),
        function()
          app.settings.tutorial = not app.settings.tutorial
        end,
      },
    }
    for i, row in ipairs(rows) do
      UI.button(row[1], 286, 208 + (i - 1) * 48, 690, 40, function()
        row[2]()
        saveSettings()
      end)
    end
    UI.button('Fullscreen', 286, 506, 336, 40, function()
      local ok, result = pcall(love.window.setFullscreen, not love.window.getFullscreen())
      if not ok or not result then
        app.message = 'Use the browser Fullscreen button above the game.'
      end
    end)
    UI.button('Controls / replay help', 640, 506, 336, 40, function()
      app.modal = { kind = 'help' }
    end)
    UI.button('Audio mix', 640, 556, 336, 40, function()
      app.modal = { kind = 'mix' }
    end)
    UI.button('Rebind controls', 286, 556, 336, 40, function()
      app.modal = { kind = 'controls' }
    end)
  elseif m.kind == 'runinfo' then
    UI.text('RUN INFO', 286, 153, 30)
    local route = M.route(app.run)
    for i, entry in ipairs(route) do
      local y, boss = 202 + (i - 1) * 99, entry.boss
      UI.panel(282, y, 694, 93)
      UI.sprite(require('src.render.sprites').boss(boss.id, entry.hell), 324, y + 46, 73)
      UI.text(
        entry.label .. ' / ' .. (entry.hell and ('HELL ' .. (entry.floor - 10)) or ('FLOOR ' .. entry.floor)),
        373,
        y + 6,
        12,
        { 0.95, 0.73, 0.4 },
        580
      )
      UI.text(entry.hell and boss.hellName or boss.name, 373, y + 25, 20, H.colors[boss.element], 580)
      UI.text(boss.hint, 373, y + 51, 14, nil, 580)
      UI.inspect(
        282,
        y,
        694,
        93,
        boss.element .. ' defense',
        entry.floor >= 3
            and ('Resists ' .. boss.element .. ' damage by 40%. Trigger a compatible two-element reaction to break guard for 2.5s. Solo heroes can punish the opening before each cast.')
          or 'Opening encounters have no guard or elemental resistance. Learn their attack warnings.'
      )
    end
    if #route == 0 then
      UI.text('This run has ended. Start a new run to scout its bosses.', 286, 224, 20, nil, 690)
    end
    UI.text(
      'FROM FLOOR 3: break guard with reactions; burst during openings.\nSwitching locks for 1.25s. Attack / dodge recovery is shared.\nHover a boss for its resistance. Run Info pauses combat.',
      286,
      512,
      16,
      { 0.76, 0.83, 0.76 },
      690
    )
  elseif m.kind == 'credits' then
    UI.text('HOUSE OF CINDERS', 286, 158, 30)
    UI.text(
      'Version 0.9.0 · Single-player boss battler\n\nGame systems, synthesized music and sounds:\nthis project. Heroes, UI and animated arena scenery:\noriginal geometry modeled and rendered in Blender.\nHero models inspired by the preserved 2D references.\nAll bosses, Hell costumes and combat effects: Blender.\nBailiff sprites: provided rig, refined in Blender.\nFlat source portraits: DreamLayer; excluded by default.\nRuntime: LÖVE 11.4 / 11.5; love.js 11.4.1 (MIT).\nSee packaged attribution and license files for details.',
      286,
      220,
      19,
      nil,
      690
    )
  elseif m.kind == 'mix' then
    UI.text('AUDIO MIX', 286, 158, 30)
    for i, key in ipairs({ 'musicVolume', 'effectsVolume' }) do
      UI.button(
        (i == 1 and 'Music: ' or 'Effects: ') .. math.floor(app.settings[key] * 100) .. '%',
        286,
        260 + (i - 1) * 65,
        690,
        48,
        function()
          app.settings[key] = (math.floor(app.settings[key] * 10 + 0.5) + 1) % 11 / 10
          saveSettings()
        end
      )
    end
    UI.text(
      'Master volume and mute apply to both. Audio starts after your first input.',
      286,
      420,
      18,
      nil,
      690
    )
  elseif m.kind == 'controls' then
    UI.text('CONTROLS', 286, 154, 30)
    UI.text(
      'Select an action, then press a key. Esc cancels.\nMovement: WASD / arrows. Aim: mouse. Attack: left click.',
      286,
      206,
      19,
      nil,
      690
    )
    for i, spec in ipairs({
      { 'Skill', 'skillKey' },
      { 'Dodge', 'dodgeKey' },
      { 'Consumable 1', 'firstItemKey' },
      { 'Consumable 2', 'secondItemKey' },
    }) do
      UI.button(spec[1] .. ': ' .. app.settings[spec[2]], 286, 300 + (i - 1) * 53, 690, 45, function()
        app.binding = spec[2]
        app.message = 'Press a key for ' .. spec[1]
      end)
    end
  elseif m.kind == 'help' then
    require('src.ui.help').draw(UI, UTex, m, app.settings, function()
      app.settings.tutorial = false
      saveSettings()
      app.modal = nil
    end)
  elseif m.kind == 'newrun' then
    UI.text('Replace your saved run?', 286, 195, 32, nil, 690)
    UI.text('Your current heroes, gold, items and progress will be lost.', 286, 274, 21, nil, 690)
    UI.button('Replace run and draft again', 286, 465, 690, 52, function()
      newRun(m.mode)
    end)
  elseif m.kind == 'offer' then
    local o = app.run.stock[m.index]
    local d = o.kind == 'hero' and H.byId[o.id] or Items[o.id]
    if o.kind == 'hero' then
      UTex.element(d.element, 947, 188, 40)
    else
      UI.item(o.id, 947, 188, 48)
    end
    UI.text(d.name, 286, 145, 30, nil, 550)
    UI.text(
      o.kind == 'hero'
          and (d.element .. ' / ' .. H.rarities[d.rarity] .. ' / ' .. d.style .. '\n' .. d.skill .. '\n' .. d.passive)
        or d.description,
      286,
      208,
      20,
      nil,
      690
    )
    UI.stat('gold', 'Price: ' .. o.price .. ' gold', 286, 339, 22)
    if o.kind == 'hero' then
      local current = H.byId[app.run.team[1].id]
      UI.stat(
        'heart',
        d.hp .. ' HP (' .. string.format('%+d', d.hp - current.hp) .. ' vs hero 1)',
        286,
        369,
        15,
        nil,
        350
      )
      UI.stat('attack', d.basic .. ' ATK', 640, 369, 15, nil, 150)
      UI.stat('skill', d.cooldown .. 's skill', 795, 369, 15, nil, 181)
    elseif o.kind == 'weapon' then
      UI.stat(
        'attack',
        'Equip from Manage hero after purchase. Current: '
          .. (app.run.team[1].weapon and Items[app.run.team[1].weapon].name or 'none'),
        286,
        380,
        15,
        nil,
        690
      )
    end
    if o.kind == 'hero' and #app.run.team == 3 then
      UI.text('Replace a hero (weapon returns to storage):', 286, 399, 16, nil, 690)
      for i, h in ipairs(app.run.team) do
        local sale = math.floor(h.paid / 2)
        UI.button(
          H.byId[h.id].name .. ' · sell ' .. sale .. ' · resulting gold ' .. (app.run.gold + sale - o.price),
          286,
          422 + (i - 1) * 47,
          690,
          40,
          function()
            app.modal = { kind = 'replace', index = m.index, hero = i }
          end
        )
      end
    else
      UI.button('Buy · ' .. o.price .. ' gold', 286, 470, 690, 50, function()
        if action(M.buy, m.index) then
          app.modal = nil
        end
      end)
    end
  elseif m.kind == 'replace' then
    local h = app.run.team[m.hero]
    local o = app.run.stock[m.index]
    UI.stat('team', 'Confirm replacement', 286, 160, 30)
    UI.text(
      'Sell '
        .. H.byId[h.id].name
        .. ' for '
        .. math.floor(h.paid / 2)
        .. ' gold\nBuy '
        .. H.byId[o.id].name
        .. ' for '
        .. o.price
        .. ' gold\nReturned weapon: '
        .. (h.weapon and Items[h.weapon].name or 'none')
        .. '\nResulting gold: '
        .. (app.run.gold + math.floor(h.paid / 2) - o.price),
      286,
      230,
      21,
      nil,
      690
    )
    UI.button('Confirm transaction', 286, 485, 690, 48, function()
      if action(M.buy, m.index, m.hero) then
        app.modal = nil
      end
    end)
  elseif m.kind == 'hero' then
    local h = app.run.team[m.index]
    UI.text(H.byId[h.id].name, 286, 160, 30)
    UI.text(H.byId[h.id].passive, 286, 218, 20, nil, 690)
    UI.button('Sell hero · ' .. math.floor(h.paid / 2) .. ' gold', 286, 303, 690, 44, function()
      app.modal = { kind = 'sellhero', index = m.index }
    end)
    UI.button('Unequip weapon', 286, 358, 690, 44, function()
      action(M.unequip, m.index)
    end, not h.weapon)
    for i, id in ipairs(app.run.weapons) do
      UI.button(
        'Equip ' .. Items[id].name,
        286 + ((i - 1) % 2) * 349,
        425 + math.floor((i - 1) / 2) * 45,
        336,
        38,
        function()
          action(M.equip, i, m.index)
        end
      )
    end
  elseif m.kind == 'sellhero' then
    local h = app.run.team[m.index]
    UI.text('Sell ' .. H.byId[h.id].name .. '?', 286, 205, 28, nil, 690)
    UI.stat(
      'gold',
      'Return weapon to storage. Gain ' .. math.floor(h.paid / 2) .. ' gold.',
      286,
      265,
      20,
      nil,
      690
    )
    UI.button('Confirm sale', 286, 470, 690, 50, function()
      if action(M.sellHero, m.index) then
        app.modal = nil
      end
    end)
  elseif m.kind == 'inventory' then
    UI.stat('bag', 'Team inventory', 286, 158, 30)
    local y = 220
    for _, kind in ipairs({ 'weapons', 'curios', 'consumables' }) do
      UI.stat(
        kind == 'weapons' and 'attack' or kind == 'curios' and 'reaction' or 'bag',
        kind:upper() .. ' ' .. #app.run[kind] .. ' / ' .. ({ weapons = 6, curios = 3, consumables = 2 })[kind],
        286,
        y,
        15,
        { 0.83, 0.67, 0.43 }
      )
      y = y + 29
      for i, id in ipairs(app.run[kind]) do
        local ix = (i - 1) % 3
        local iy = math.floor((i - 1) / 3)
        UI.button(
          Items[id].name .. ' · sell ' .. math.floor(Items[id].price / 2),
          286 + ix * 234,
          y + iy * 35,
          225,
          30,
          function()
            app.modal = { kind = 'sellitem', list = kind, index = i }
          end
        )
      end
      y = y + math.max(1, math.ceil(#app.run[kind] / 3)) * 35 + 12
    end
  elseif m.kind == 'sellitem' then
    local id = app.run[m.list][m.index]
    UI.text('Sell ' .. Items[id].name .. '?', 286, 205, 30, nil, 690)
    UI.text(Items[id].description, 286, 265, 20, nil, 690)
    UI.button('Confirm sale · ' .. math.floor(Items[id].price / 2) .. ' gold', 286, 470, 690, 50, function()
      if action(M.sellItem, m.list, m.index) then
        app.modal = { kind = 'inventory' }
      end
    end)
  end
end
function love.draw()
  local w, h = love.graphics.getDimensions()
  local s = math.min(w / 1280, h / 720)
  love.graphics.clear(0.027, 0.045, 0.052)
  love.graphics.push()
  love.graphics.translate((w - 1280 * s) / 2, (h - 720 * s) / 2)
  love.graphics.scale(s)
  UTex.backdrop(
    app.screen == 'arena' and 'bg_arena' or app.screen == 'title' and 'bg_title' or 'bg_screen',
    1280,
    720
  )
  if app.screen ~= 'arena' then
    UTex.ambience(app.screen == 'title')
  end
  local focusContext = menuContext()
  if UI.context ~= focusContext then
    UI.focus = nil
    UI.context = focusContext
  end
  UI.buttons = {}
  UI.hoverTip = nil
  UI.mx, UI.my = mouse()
  UTex.sprite('ember_seal', 73, 43, 35)
  UI.text('HOUSE OF CINDERS', 135, 35, 14, { 0.53, 0.68, 0.65 })
  if app.run and app.screen ~= 'title' then
    UI.text(
      'SEED ' .. app.run.seed .. '    ' .. M.floorInfo(app.run),
      620,
      33,
      15,
      { 0.66, 0.75, 0.70 },
      450,
      'right'
    )
    UTex.icon('floor', 1090, 43, 25)
    UI.stat('gold', app.run.gold .. ' GOLD', 1120, 33, 15, { 0.95, 0.78, 0.45 }, 130)
  end
  UI.rule(50, 1230, 75)
  if app.screen == 'title' then
    title()
  elseif app.screen == 'draft' then
    UI.text('CHOOSE YOUR OPENING HAND', 50, 107, 32)
    UI.text(
      'One free hero. Four distinct offers. No rerolls. Every hero can win the opening fight.',
      50,
      155,
      17,
      { 0.58, 0.74, 0.7 }
    )
    for i, id in ipairs(app.run.offers) do
      local x = 50 + (i - 1) * 300
      UI.card(id, x, 205, 280, 355)
      UI.button('Choose ' .. H.byId[id].name, x, 584, 280, 50, function()
        M.choose(app.run, i)
        sync()
      end)
    end
  elseif app.screen == 'preview' then
    preview()
  elseif app.screen == 'arena' then
    UI.arena(app.arena)
    UI.text(
      'WASD move · click attack · '
        .. app.settings.skillKey:upper()
        .. ' skill · '
        .. app.settings.dodgeKey:upper()
        .. ' dodge · 1–3 switch · Esc pause',
      230,
      558,
      15,
      { 0.65, 0.76, 0.7 },
      920,
      'center'
    )
    if app.paused then
      love.graphics.setColor(0, 0, 0, 0.8)
      love.graphics.rectangle('fill', 0, 0, 1280, 720)
      UI.text('PAUSED', 400, 240, 42, nil, 480, 'center')
      UI.button('Resume', 440, 330, 400, 50, function()
        app.paused = false
      end)
      UI.button('Title', 440, 395, 400, 50, function()
        app.screen = 'title'
        app.paused = false
      end)
    end
  elseif app.screen == 'shop' then
    shop()
  elseif app.screen == 'rewards' then
    require('src.render.scenery').draw('reward', 1100, 270, 220)
    UI.text('THE HOUSE PAYS OUT', 50, 147, 48)
    UI.stat('gold', '+' .. app.run.lastReward .. ' GOLD', 50, 234, 40, { 0.88, 0.71, 0.4 })
    UI.stat('heart', 'All heroes revived and fully healed.', 50, 302, 21)
    team(365)
    UI.button('Visit the shop', 930, 583, 300, 60, function()
      M.shop(app.run)
      sync()
    end)
  elseif app.screen == 'victory' then
    require('src.render.scenery').draw('victory', 1110, 365, 220)
    UI.text('THE INFINITY KEY', 50, 152, 54, { 0.95, 0.78, 0.45 })
    UI.text('Ten floors cleared. The door below is open.', 50, 242, 25)
    UI.stat('gold', 'Bonus gold: ' .. app.run.lastBonus .. ' · A Legendary awaits in the shop.', 50, 302, 20)
    UI.button('Finish Run', 50, 472, 420, 60, function()
      M.finish(app.run)
      sync()
    end)
    UI.button('Enter Hell · visit shop', 500, 472, 620, 60, function()
      M.shop(app.run)
      sync()
    end)
  elseif app.screen == 'defeat' or app.screen == 'complete' then
    require('src.render.scenery').draw(app.screen == 'defeat' and 'defeat' or 'victory', 1080, 365, 290)
    UI.text(
      app.screen == 'defeat' and 'THE HOUSE WINS'
        or app.run.mode == 'demo' and 'DEMO COMPLETE'
        or 'YOU BEAT THE HOUSE',
      50,
      150,
      52
    )
    UI.text(
      'Floors cleared: '
        .. app.run.stats.clears
        .. '   |   Damage: '
        .. math.floor(app.run.stats.damage)
        .. '   |   Reactions: '
        .. app.run.stats.reactions,
      50,
      264,
      23
    )
    UI.button('New run', 50, 435, 360, 60, function()
      newRun(app.run.mode)
    end)
    UI.button('Title', 440, 435, 360, 60, function()
      app.screen = 'title'
    end)
  end
  if app.run and app.screen ~= 'title' then
    UI.button('Run Info', 445, 26, 160, 34, function()
      app.modal = { kind = 'runinfo' }
      app.message = ''
    end, false, 'floor')
  end
  if app.settings.tutorial and app.screen ~= 'title' and app.screen ~= 'arena' then
    UI.text(
      'F1: help / skip prompts   F2: settings   Tab + Enter: menu controls',
      50,
      680,
      14,
      nil,
      1180,
      'center'
    )
  end
  if (app.transition or 0) > 0 and not app.settings.reducedMotion then
    love.graphics.setColor(0.02, 0.06, 0.07, app.transition / 0.45)
    love.graphics.rectangle('fill', 0, 0, 1280, 720)
  end
  if app.modal then
    UI.hoverTip = nil
    modal()
  end
  if Dev then
    UI.text(
      app.devRun and 'LAB RUN / NOT SAVED / F3 controls' or 'F3 encounter lab',
      930,
      8,
      11,
      { 0.7, 0.6, 0.4 },
      300,
      'right'
    )
    if app.lab then
      Dev.draw(app, function(r)
        app.run = r
        app.devRun = true
        app.modal = nil
        enter()
      end)
    end
  end
  if app.saveWarning then
    UI.text(app.saveWarning, 50, 702, 12, { 1, 0.65, 0.4 }, 1180, 'center')
  end
  if app.message ~= '' then
    UI.panel(270, 666, 740, 37, { 0.24, 0.12, 0.09 })
    UI.text(app.message, 282, 674, 15, { 1, 0.76, 0.58 }, 714, 'center')
  end
  if not app.lab then
    UI.tooltip()
  end
  love.graphics.pop()
end
function love.mousepressed(_, _, b)
  Audio.unlock()
  if b == 1 then
    local x, y = mouse()
    if UI.click(x, y) then
      sound()
    end
  elseif b == 2 then
    love.keypressed(app.settings.skillKey)
  end
end
function love.keypressed(k)
  Audio.unlock()
  if Dev and k == 'f3' then
    app.lab = not app.lab
    UI.focus = nil
    return
  end
  if app.lab then
    if k == 'escape' then
      app.lab = false
    else
      queueMenu(k)
    end
    return
  end
  if app.binding then
    if k ~= 'escape' then
      local reserved = {
        w = true,
        a = true,
        s = true,
        d = true,
        up = true,
        down = true,
        left = true,
        right = true,
        tab = true,
        ['return'] = true,
        f1 = true,
        f2 = true,
        ['1'] = true,
        ['2'] = true,
        ['3'] = true,
      }
      local conflict = reserved[k] or k:match('^f%d+$')
      for _, field in ipairs({ 'skillKey', 'dodgeKey', 'firstItemKey', 'secondItemKey' }) do
        if field ~= app.binding and app.settings[field] == k then
          conflict = true
        end
      end
      if conflict then
        app.message = 'Key already used. Choose another key.'
        return
      end
      app.settings[app.binding] = k
      saveSettings()
    end
    app.binding = nil
    app.message = ''
    return
  end
  if k == 'f1' or k == 'f2' then
    app.modal = { kind = k == 'f1' and 'help' or 'settings' }
    return
  end
  if app.screen ~= 'arena' or app.paused or app.modal then
    if queueMenu(k) then
      return
    end
  end
  if k == 'escape' then
    app.menuKeys = {}
    UI.buttons = {}
    UI.focus = nil
    if app.modal then
      app.modal = nil
    elseif app.screen == 'arena' then
      app.paused = not app.paused
    end
    return
  end
  if app.screen == 'arena' and not app.paused and not app.modal and not app.lab then
    if tonumber(k) then
      if app.arena:switch(tonumber(k)) then
        sound('switch')
      end
    elseif k == app.settings.skillKey then
      local x, y = aim()
      if app.arena:attack(x, y, true) then
        sound('skill')
      end
    elseif k == app.settings.dodgeKey then
      if app.arena:hero().dodgeCd <= 0 then
        sound('dodge')
      end
      app.arena:dodgeStart(move())
    elseif k == app.settings.firstItemKey then
      if not app.arena:consume(1) then
        app.message = 'Consumable 1 cannot be used now.'
      else
        app.message = ''
      end
    elseif k == app.settings.secondItemKey then
      if not app.arena:consume(2) then
        app.message = 'Consumable 2 cannot be used now.'
      else
        app.message = ''
      end
    end
  end
end
function love.focus(f)
  app.focusLost = not f
  if not f and app.screen == 'arena' then
    app.paused = true
  end
end
