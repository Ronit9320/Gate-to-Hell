-- Original deterministic synthesis, no downloaded samples or runtime network access.
local A = { ready = false, unlocked = false, clock = 0, last = {}, voices = {} }
local rate = 22050
local function source(seconds, sample)
  local n = math.floor(seconds * rate)
  local d = love.sound.newSoundData(n, rate, 16, 1)
  for i = 0, n - 1 do
    d:setSample(i, math.max(-0.85, math.min(0.85, sample(i / rate, seconds))))
  end
  return love.audio.newSource(d, 'static')
end
function A.load()
  local ok = pcall(function()
    for name, spec in pairs({
      ui = { 660, 0.08 },
      attack = { 250, 0.085 },
      impact = { 45, 0.28 },
      hit = { 180, 0.07 },
      hurt = { 75, 0.16 },
      skill = { 440, 0.18 },
      dodge = { 300, 0.09 },
      switch = { 520, 0.07 },
      reaction = { 880, 0.22 },
      victory = { 660, 0.65 },
      defeat = { 110, 0.7 },
    }) do
      local f, duration = spec[1], spec[2]
      local s = source(duration, function(t, d)
        local env = math.min(1, t / 0.005) * (1 - t / d) ^ 2
        return (math.sin(2 * math.pi * f * t) + 0.3 * math.sin(2 * math.pi * f * 1.5 * t)) * 0.16 * env
      end)
      A.voices[name] = { s, s:clone(), index = 1 }
    end
    local notes = {
      57,
      64,
      69,
      72,
      67,
      64,
      60,
      64,
      53,
      60,
      65,
      69,
      67,
      60,
      57,
      60,
      55,
      62,
      67,
      71,
      69,
      62,
      59,
      62,
      52,
      59,
      64,
      67,
      64,
      59,
      55,
      59,
    }
    A.music = source(12.8, function(t)
      local index = math.floor(t / 0.4) % 32 + 1
      local localTime = t % 0.4
      local f = 440 * 2 ^ ((notes[index] - 69) / 12)
      local env = math.min(1, localTime / 0.012) * math.exp(-localTime * 10)
      local root = notes[math.floor((index - 1) / 8) * 8 + 1] - 24
      local bass = 440 * 2 ^ ((root - 69) / 12)
      local bt = t % 3.2
      local fade = math.min(1, bt / 0.03, (3.2 - bt) / 0.06)
      return math.sin(t * f * 2 * math.pi) * env * 0.11 + math.sin(t * bass * 2 * math.pi) * fade * 0.035
    end)
    A.music:setLooping(true)
  end)
  A.ready = ok
  return ok
end
function A.unlock()
  A.unlocked = true
end
function A.play(name, settings)
  if not A.ready or not A.unlocked or settings.muted then
    return
  end
  if A.clock - (A.last[name] or -100) < (name == 'hit' and 0.1 or 0.05) then
    return
  end
  local v = A.voices[name]
  if not v then
    return
  end
  A.last[name] = A.clock
  local s = v[v.index]
  v.index = v.index % 2 + 1
  s:stop()
  s:setVolume(settings.volume * (settings.effectsVolume or 0.8))
  s:play()
end
function A.update(dt, settings, paused, combat)
  A.clock = A.clock + dt
  if not A.ready then
    return
  end
  if not A.unlocked or settings.muted or paused or settings.musicVolume == 0 then
    A.music:pause()
  else
    A.music:setVolume(settings.volume * (settings.musicVolume or 0.35) * (combat and 1 or 0.65))
    if not A.music:isPlaying() then
      A.music:play()
    end
  end
  if settings.muted or paused then
    for _, v in pairs(A.voices) do
      v[1]:stop()
      v[2]:stop()
    end
  end
end
return A
