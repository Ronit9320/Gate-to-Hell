local C = require('src.core.codec')
local S = {}
function S.defaults()
  return {
    muted = false,
    volume = 0.7,
    musicVolume = 0.35,
    effectsVolume = 0.8,
    reducedMotion = false,
    shake = true,
    largeText = false,
    tutorial = true,
    skillKey = 'e',
    dodgeKey = 'space',
    firstItemKey = 'q',
    secondItemKey = 'r',
  }
end
function S.read(fs)
  local out = S.defaults()
  local exists, info = pcall(fs.getInfo, 'settings.sav')
  if not exists or not info then
    return out
  end
  local ok, raw = pcall(fs.read, 'settings.sav')
  if ok and raw then
    local valid, t = pcall(C.decode, raw)
    if valid and type(t) == 'table' then
      for k, v in pairs(out) do
        if type(t[k]) == type(v) then
          out[k] = t[k]
        end
      end
      for _, k in ipairs({ 'volume', 'musicVolume', 'effectsVolume' }) do
        out[k] = math.max(0, math.min(1, out[k]))
      end
    end
  end
  return out
end
function S.write(settings, fs)
  local ok, result = pcall(fs.write, 'settings.sav', C.encode(settings))
  return ok and result
end
return S
