local U = require('src.core.util')
local D = {}
function D.amount(base, add, mult, reaction, resist)
  return math.floor(
    U.clamp(
      (base + (add or 0)) * (mult or 1) * (reaction or 1) * (1 - U.clamp(resist or 0, -1, 0.8)),
      0,
      1000000
    ) + 0.5
  )
end
function D.apply(target, n)
  local absorbed = math.min(target.shield or 0, n)
  target.shield = (target.shield or 0) - absorbed
  local actual = math.min(target.hp, n - absorbed)
  target.hp = math.max(0, target.hp - actual)
  return actual, absorbed
end
return D
