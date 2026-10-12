-- Headless input/render contract tests; browser suite covers actual raster output.
return function(test)
  test('Blender UI keeps corner dimensions, atlas rows, loop bounds and reduced motion', function()
    local old = love
    local calls, loads = {}, 0
    love = {
      filesystem = {
        getInfo = function(path)
          return not path:find('missing')
        end,
      },
      graphics = {
        setColor = function() end,
        newImage = function(path)
          loads = loads + 1
          local w, h = 128, 128
          if path:find('coin') then
            w, h = 768, 96
          end
          if path:find('elements') then
            w, h = 768, 192
          end
          if path:find('items') then
            w, h = 768, 288
          end
          return {
            setFilter = function() end,
            getDimensions = function()
              return w, h
            end,
          }
        end,
        newQuad = function(...)
          return { ... }
        end,
        draw = function(...)
          calls[#calls + 1] = { ... }
        end,
      },
    }
    local T = dofile('src/render/ui_textures.lua')
    assert(T.skin('panel', 10, 20, 760, 510))
    assert(#calls == 9)
    assert(calls[1][6] == 1 and calls[1][7] == 1, 'Corners must retain their authored pixel size')
    assert(calls[9][3] == 758 and calls[9][4] == 518, 'Bottom right must meet the requested bounds')
    calls = {}
    T.skin('panel', 0, 0, 18, 9)
    for _, c in ipairs(calls) do
      assert(c[6] > 0 and c[7] > 0)
    end
    assert(loads == 1, 'Skin images must be cached')
    calls = {}
    T.sprite('coin', 100, 100, 96, 0.875)
    assert(calls[1][2][1] == 672, 'Last animation cell must be in bounds')
    T.sprite('coin', 100, 100, 96, 1)
    assert(calls[2][2][1] == 0, 'One-second loop must wrap')
    T.reducedMotion = true
    T.sprite('coin', 100, 100, 96, 0.875)
    assert(calls[3][2][1] == 0, 'Reduced motion must freeze the asset')
    T.element('Antimatter', 100, 100, 96)
    assert(calls[4][2][1] == 0 and calls[4][2][2] == 96, 'Ninth element lives in row two')
    T.item('wind', 100, 100, 96)
    assert(calls[5][2][1] == 576 and calls[5][2][2] == 192, 'Last item lives in row three')
    assert(not T.skin('missing', 0, 0, 100, 100))
    love = old
  end)
  local Settings = require('src.core.settings')
  local C = require('src.core.codec')
  test('settings default, migration, roundtrip and storage failures', function()
    local fs = {
      getInfo = function()
        return nil
      end,
      read = function()
        error('must not read missing files')
      end,
    }
    assert(Settings.read(fs).volume == 0.7)
    fs.getInfo = function()
      return {}
    end
    fs.read = function()
      return '{"muted":true}'
    end
    assert(Settings.read(fs).muted and Settings.read(fs).skillKey == 'e')
    assert(Settings.read(fs).musicVolume == 0.35 and Settings.read(fs).effectsVolume == 0.8)
    fs.read = function()
      return '{"volume":2,"musicVolume":-1,"effectsVolume":4}'
    end
    assert(
      Settings.read(fs).volume == 1
        and Settings.read(fs).musicVolume == 0
        and Settings.read(fs).effectsVolume == 1
    )
    fs.read = function()
      return 'bad save'
    end
    assert(Settings.read(fs).tutorial)
    local cfg = Settings.defaults()
    cfg.reducedMotion = true
    cfg.largeText = true
    cfg.skillKey = 't'
    fs.write = function(_, raw)
      fs.read = function()
        return raw
      end
      return true
    end
    assert(Settings.write(cfg, fs))
    assert(C.encode(Settings.read(fs)) == C.encode(cfg))
    fs.write = function()
      error('storage unavailable')
    end
    assert(not Settings.write(cfg, fs))
  end)
  test('menu focus wraps, skips disabled controls and consumes activation once', function()
    local old = love
    love = { graphics = {} }
    local g = love.graphics
    for _, name in ipairs({ 'setColor', 'rectangle', 'setFont', 'printf', 'setLineWidth' }) do
      g[name] = function() end
    end
    g.newFont = function()
      return {}
    end
    g.getFont = function()
      return {
        getHeight = function()
          return 18
        end,
      }
    end
    local UI = require('src.ui.draw')
    local count = 0
    local function draw()
      UI.buttons = {}
      UI.button('disabled', 0, 0, 100, 40, function()
        error('disabled activated')
      end, true)
      UI.button('one', 0, 50, 100, 40, function()
        count = count + 1
      end)
      UI.button('two', 0, 100, 100, 40, function()
        count = count + 10
      end)
    end
    draw()
    UI.focus = nil
    UI.navigate('tab')
    assert(UI.focus == 1)
    UI.navigate('up')
    assert(UI.focus == 2)
    UI.navigate('return')
    assert(count == 10 and #UI.buttons == 0)
    assert(not UI.navigate('return'))
    draw()
    UI.click(50, 65)
    assert(count == 11 and #UI.buttons == 0)
    love = old
    package.loaded['src.ui.draw'] = nil
    package.loaded['src.ui.pixel'] = nil
  end)
  test('pixel skin frames are hard-edged notched rectangles', function()
    local old = love
    local calls = {}
    love = {
      graphics = {
        setColor = function() end,
        rectangle = function(mode, x, y, w, h)
          calls[#calls + 1] = { mode, x, y, w, h }
        end,
      },
    }
    package.loaded['src.ui.pixel'] = nil
    local P = require('src.ui.pixel')
    assert(P.light({ 0, 0, 0 }, 0.5)[1] == 0.5 and P.dark({ 1, 1, 1 }, 0.5)[1] == 0.5)
    calls = {}
    P.frame(10, 20, 100, 50, { fill = { 0.1, 0.2, 0.3 }, notch = 4, bevel = 1 })
    assert(#calls > 0)
    for _, c in ipairs(calls) do
      assert(c[1] == 'fill', 'pixel frames must only draw filled rectangles')
      assert(c[2] == math.floor(c[2]) and c[3] == math.floor(c[3]), 'pixel frames must snap to whole pixels')
    end
    assert(calls[1][2] == 14 and calls[1][4] == 92, 'top band must be inset by the corner notch')
    calls = {}
    P.ring(0, 0, 50, 10, 2, 2, { 1, 1, 1 })
    P.bar(0, 0, 100, 12, 0.5, { 1, 0, 0 })
    P.rule(0, 100, 5)
    for _, c in ipairs(calls) do
      assert(c[1] == 'fill')
    end
    love = old
    package.loaded['src.ui.pixel'] = nil
  end)
  test('Element particles clamp frames, freeze reduced motion and cache only valid elements', function()
    local old = love
    local draws, loads = {}, 0
    love = {
      filesystem = {
        getInfo = function()
          return true
        end,
      },
      graphics = {
        setColor = function() end,
        newImage = function()
          loads = loads + 1
          return {
            setFilter = function() end,
            getDimensions = function()
              return 1152, 384
            end,
          }
        end,
        newQuad = function(...)
          return { ... }
        end,
        draw = function(...)
          draws[#draws + 1] = { ... }
        end,
      },
    }
    local FX = dofile('src/render/effects.lua')
    assert(FX.frame(-1, false) == 0 and FX.frame(100, false) == 11)
    assert(FX.frame(0, true) == FX.frame(1, true))
    assert(not FX.draw('Neutral', 0, 0, 80, 0.5, false))
    for _, element in ipairs({
      'Pyro',
      'Hydro',
      'Anemo',
      'Geo',
      'Dendro',
      'Cryo',
      'Electro',
      'Gravity',
      'Antimatter',
    }) do
      for frame = 0, 11 do
        assert(FX.draw(element, 0, 0, 80, frame / 12, false))
      end
    end
    assert(loads == 9, 'Element textures must load once, independent of particle count')
    for _, call in ipairs(draws) do
      local q = call[2]
      assert(q[1] >= 0 and q[1] + q[3] <= 1152 and q[2] + q[4] <= 384)
    end
    love = old
  end)
  test('hover inspection delays, wraps, clamps to screen and never consumes clicks', function()
    local old = love
    local font = {
      getWrap = function()
        return 300, { 'a', 'b', 'c' }
      end,
      getHeight = function()
        return 20
      end,
    }
    love = {
      graphics = {
        setColor = function() end,
        rectangle = function() end,
        newFont = function()
          return font
        end,
        setFont = function() end,
        getFont = function()
          return font
        end,
      },
    }
    local UI = dofile('src/ui/draw.lua')
    local bars = {}
    love.graphics.rectangle = function(mode, x, y, w, h)
      bars[#bars + 1] = { mode, x, y, w, h }
    end
    UI.bar(10, 20, 100, 3, 0.5, { 1, 0, 0 })
    assert(#bars == 2 and bars[2][4] == 50 and bars[2][5] == 3, 'thin meters must keep a visible fill')
    local panels = {}
    UI.panel = function(x, y, w, h)
      panels[#panels + 1] = { x, y, w, h }
    end
    UI.text, UI.rule = function() end, function() end
    UI.mx, UI.my, UI.time = 1270, 700, 0
    UI.inspect(1240, 680, 40, 40, 'Item', 'A long item description')
    UI.tooltip()
    assert(#panels == 0 and #UI.buttons == 0)
    UI.time = 0.3
    UI.tooltip()
    assert(#panels == 1)
    local p = panels[1]
    assert(p[1] >= 0 and p[2] >= 0 and p[1] + p[3] <= 1280 and p[2] + p[4] <= 720)
    UI.hoverTip = nil
    UI.mx = 0
    UI.inspect(1240, 680, 40, 40, 'Item', 'Description')
    UI.tooltip()
    assert(UI.tipTitle == nil and #panels == 1, 'leaving the target dismisses the tooltip')
    love = old
  end)
end
