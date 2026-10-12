local U = {}
function U.copy(t)
  if type(t) ~= 'table' then
    return t
  end
  local r = {}
  for k, v in pairs(t) do
    r[k] = U.copy(v)
  end
  return r
end
function U.clamp(x, a, b)
  return math.max(a, math.min(b, x))
end
function U.dist(x, y, a, b)
  return math.sqrt((x - a) ^ 2 + (y - b) ^ 2)
end
function U.norm(x, y)
  local d = math.sqrt(x * x + y * y)
  if d < 0.001 then
    return 1, 0
  end
  return x / d, y / d
end
-- Park-Miller: products remain exactly representable in Lua doubles.
function U.random(r, n)
  r.seed = (r.seed * 16807) % 2147483647
  local f = (r.seed - 1) / 2147483646
  return n and math.floor(f * n) + 1 or f
end
function U.weighted(r, w)
  local f = U.random(r) * 100
  for i, v in ipairs(w) do
    f = f - v
    if f < 0 then
      return i
    end
  end
  return #w
end
return U
