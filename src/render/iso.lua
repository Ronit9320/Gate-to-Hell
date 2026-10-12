local I = {}
function I.project(x, y)
  return 640 + (x - y) * 0.78, 345 + (x + y) * 0.39
end
function I.inverse(x, y)
  local a = (x - 640) / 0.78
  local b = (y - 345) / 0.39
  return (a + b) / 2, (b - a) / 2
end
function I.screenVector(x, y)
  return (x / 0.78 + y / 0.39) / 2, (y / 0.39 - x / 0.78) / 2
end
return I
