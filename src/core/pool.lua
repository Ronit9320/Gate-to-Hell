-- Reuse short-lived visual records without retaining references between effects.
local P = {}
P.__index = P
function P.new(cap)
  return setmetatable({ free = {}, cap = cap, created = 0 }, P)
end
function P:take()
  local t = table.remove(self.free)
  if not t then
    t = {}
    self.created = self.created + 1
  end
  return t
end
function P:release(t)
  for k in pairs(t) do
    t[k] = nil
  end
  if #self.free < self.cap then
    self.free[#self.free + 1] = t
  end
end
return P
