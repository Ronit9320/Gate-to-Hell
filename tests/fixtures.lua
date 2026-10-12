-- Generated files are ignored and never packaged.
os.execute('mkdir -p .test-results')
local M = require('src.run.model')
local H = require('src.data.heroes')
local S = require('src.core.save')
local function write(name, r)
  local f = assert(io.open('.test-results/fixture-' .. name .. '.json', 'w'))
  f:write(S.encode(r))
  f:close()
end
local function run()
  local r = M.new(2026)
  M.choose(r, 1)
  r.team = { H.instance('jack') }
  return r
end
local r = run()
for i = 1, 10 do
  M.enter(r)
  M.reward(r)
  if i < 10 then
    M.shop(r)
    M.next(r)
  end
end
write('victory', r)
r = run()
M.enter(r)
M.reward(r)
M.shop(r)
r.gold = 100
r.weapons = { 'scepter', 'scepter', 'scepter', 'scepter', 'scepter', 'scepter' }
r.curios = { 'die', 'ace', 'tab' }
r.consumables = { 'flask', 'flask' }
write('full', r)
r.gold = 0
write('poor', r)
r = run()
r.team[1].hp = 1
write('death', r)

for floor = 1, 20 do
  r = run()
  r.floor = floor
  r.rewarded = floor - 1
  r.key = floor > 10
  r.team = { H.instance('jack'), H.instance('penny'), H.instance('flint') }
  write('boss-' .. floor, r)
end

r = run()
r.team = { H.instance('jack', 8), H.instance('penny', 8), H.instance('flint', 8) }
M.enter(r)
M.reward(r)
M.shop(r)
r.gold = 100
r.weapons = { 'scepter', 'scepter' }
r.curios = { 'die' }
r.consumables = { 'flask' }
r.stock[1] = { kind = 'hero', id = 'gale', price = 8, sold = false }
write('management', r)

for _, hero in ipairs(H.list) do
  r = run()
  r.team = { H.instance(hero.id) }
  write('hero-' .. hero.id, r)
end
r = run()
r.team = { H.instance('jack'), H.instance('penny'), H.instance('flint') }
r.team[1].hp = 1
write('hero-fallen-team', r)
