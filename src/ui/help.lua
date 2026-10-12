local Help = {}
local tabs = { 'The run', 'Combat', 'Elements', 'Your team' }
function Help.draw(UI, T, modal, settings, done)
  modal.page = modal.page or 1
  UI.stat('help', 'HOW TO PLAY', 286, 153, 30)
  for i, name in ipairs(tabs) do
    UI.button(name, 286 + (i - 1) * 176, 205, 162, 35, function()
      modal.page = i
      UI.focus = nil
    end, false, ({ 'floor', 'attack', 'reaction', 'team' })[i])
    if modal.page == i then
      love.graphics.setColor(0.95, 0.72, 0.35)
      love.graphics.rectangle('fill', 295 + (i - 1) * 176, 243, 144, 2)
    end
  end
  local function row(icon, title, body, y)
    UI.stat(icon, title, 286, y, 19, { 0.98, 0.80, 0.49 }, 690)
    UI.text(body, 320, y + 29, 17, nil, 654)
  end
  if modal.page == 1 then
    row(
      'play',
      'Draft a hero. Beat the house.',
      'Choose one free hero from four cards. Start with 10 gold.\nFight one boss at a time in an isometric arena.',
      264
    )
    row(
      'shop',
      'Fight → reward → shop → next floor',
      'Every clear pays gold and revives / fully heals your team.\nBuy heroes and gear, then prepare for the next boss.',
      359
    )
    row(
      'key',
      'Clear ten floors to claim the Infinity Key',
      'Finish your run, or enter endless Hell with tougher encounters.\nIf every hero falls, the run ends. A new run starts fresh.',
      454
    )
  elseif modal.page == 2 then
    row(
      'attack',
      'Move, aim, attack',
      'WASD / arrows move. Mouse aims. Left click attacks.\nMelee needs range; ranged heroes reload after five shots.',
      264
    )
    row(
      'dodge',
      'Read amber warnings and escape before red',
      settings.dodgeKey:upper()
        .. ' dodges with brief invulnerability. Attacks slow movement.\nDodge cancels an unfinished melee swing. Find safe gaps.',
      359
    )
    row(
      'skill',
      'Use skills while basic attacks recover',
      settings.skillKey:upper()
        .. ' / right click: elemental skill. 1 / 2 / 3: switch living heroes.\n'
        .. settings.firstItemKey:upper()
        .. ' / '
        .. settings.secondItemKey:upper()
        .. ': consumables. Esc pauses. F2 opens settings.',
      454
    )
  elseif modal.page == 3 then
    local elements = { 'Pyro', 'Hydro', 'Anemo', 'Geo', 'Dendro', 'Cryo', 'Electro', 'Gravity', 'Antimatter' }
    for i, element in ipairs(elements) do
      local cx = 321 + (i - 1) * 76
      T.element(element, cx, 290, 38)
      UI.text(element, cx - 36, 316, 11, nil, 72, 'center')
    end
    row(
      'reaction',
      'Apply one element, then a different one',
      'Skills leave a timed aura. Compatible element pairs react\nin either order. Neutral basic attacks do not apply an aura.',
      351
    )
    row(
      'shield',
      'Reactions add bursts, damage over time or defense',
      'From floor 3, reactions break boss guard for 2.5s.\nBosses resist their own element. Scout them with Run Info.',
      450
    )
  else
    row(
      'team',
      'Build a team of up to three heroes',
      'Only your active hero fights. Off-field cooldowns recover.\nFrom floor 3, switching locks for 1.25s; dodge recovery is shared.',
      264
    )
    row(
      'bag',
      'Choose equipment that supports your team',
      'One weapon per hero; six weapons in storage. Three unique\nteam-wide curios. Two consumable charges, used with your item keys.',
      359
    )
    row(
      'gold',
      'Inspect shop offers before spending gold',
      'At three heroes, choose whom to replace. Selling returns half\nthe paid price. Continue restores the last saved boundary.',
      454
    )
  end
  UI.text(
    tostring(modal.page) .. ' / 4 · Tab / arrows focus menus; Enter selects. F1 reopens this guide.',
    286,
    553,
    13,
    { 0.65, 0.76, 0.71 },
    690,
    'center'
  )
  UI.button('Got it / skip prompts', 286, 579, 690, 30, done)
end
return Help
