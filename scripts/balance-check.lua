package.path = './?.lua;' .. package.path
local A, B, H, M =
  require('src.combat.arena'),
  require('src.data.bosses'),
  require('src.data.heroes'),
  require('src.run.model')
local report = {}
for _, floor in ipairs({ 1, 5, 8, 10, 20, 30 }) do
  local row = { floor = floor }
  for _, mode in ipairs({ 'camping', 'bot' }) do
    local r = M.new(71)
    r.floor, r.stage = floor, 'arena'
    r.team = { H.instance('jack'), H.instance('penny'), H.instance('flint') }
    local a = A.new(r)
    a.x, a.y = 0, 0
    for step = 1, 12000 do
      require('tests.' .. mode)(a)
      if a.result then
        break
      end
    end
    row[mode] = {
      bossHP = a.boss.maxhp,
      damage = a.incoming,
      seconds = math.floor(a.time * 10) / 10,
      result = a.result,
    }
  end
  report[#report + 1] = row
end
local json = require('src.core.codec').encode(report)
os.execute('mkdir -p .test-results')
local f = assert(io.open('.test-results/tactics-comparison.json', 'w'))
f:write(json)
f:close()
print(json)
