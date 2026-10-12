-- Deliberately data-only: saves never compile or execute Lua.
local C = {}
function C.encode(v)
  local t = type(v)
  if t == 'nil' then
    return 'null'
  elseif t == 'boolean' then
    return tostring(v)
  elseif t == 'number' then
    assert(v == v and math.abs(v) < 1e15, 'non-finite value')
    return string.format('%.14g', v)
  elseif t == 'string' then
    return '"'
      .. v:gsub('[%z\1-\31\\"]', function(c)
        local m = { ['"'] = '\\"', ['\\'] = '\\\\', ['\n'] = '\\n', ['\r'] = '\\r', ['\t'] = '\\t' }
        return m[c] or string.format('\\u%04x', c:byte())
      end)
      .. '"'
  elseif t == 'table' then
    local out = {}
    local keys = {}
    for k in pairs(v) do
      keys[#keys + 1] = k
    end
    table.sort(keys, function(a, b)
      return tostring(a) < tostring(b)
    end)
    for _, k in ipairs(keys) do
      out[#out + 1] = C.encode(tostring(k)) .. ':' .. C.encode(v[k])
    end
    return '{' .. table.concat(out, ',') .. '}'
  end
  error('unsupported type')
end
function C.decode(s)
  assert(type(s) == 'string' and #s < 1000000, 'save too large')
  local p = 1
  local function ws()
    local _, j = s:find('^[ \n\r\t]*', p)
    p = (j or p - 1) + 1
  end
  local parse
  local function str()
    assert(s:sub(p, p) == '"')
    p = p + 1
    local out = {}
    while p <= #s do
      local c = s:sub(p, p)
      p = p + 1
      if c == '"' then
        return table.concat(out)
      end
      if c == '\\' then
        local e = s:sub(p, p)
        p = p + 1
        local m =
          { ['"'] = '"', ['\\'] = '\\', ['/'] = '/', n = '\n', r = '\r', t = '\t', b = '\b', f = '\f' }
        if e == 'u' then
          local h = s:sub(p, p + 3)
          assert(h:match('^%x%x%x%x$'))
          local n = tonumber(h, 16)
          assert(n < 128, 'unsupported escape')
          c = string.char(n)
          p = p + 4
        else
          c = assert(m[e], 'invalid escape')
        end
      end
      out[#out + 1] = c
    end
    error('unterminated string')
  end
  parse = function(depth)
    assert(depth < 24, 'save too deep')
    ws()
    local c = s:sub(p, p)
    if c == '{' then
      p = p + 1
      local t = {}
      ws()
      if s:sub(p, p) == '}' then
        p = p + 1
        return t
      end
      while true do
        ws()
        local k = str()
        if k:match('^[1-9]%d*$') then
          k = tonumber(k)
        end
        ws()
        assert(s:sub(p, p) == ':')
        p = p + 1
        assert(t[k] == nil, 'duplicate key')
        t[k] = parse(depth + 1)
        ws()
        c = s:sub(p, p)
        p = p + 1
        if c == '}' then
          return t
        end
        assert(c == ',')
      end
    elseif c == '"' then
      return str()
    elseif s:sub(p, p + 3) == 'true' then
      p = p + 4
      return true
    elseif s:sub(p, p + 4) == 'false' then
      p = p + 5
      return false
    elseif s:sub(p, p + 3) == 'null' then
      p = p + 4
      return nil
    else
      local n = s:match('^-?%d+%.?%d*[eE]?[+-]?%d*', p)
      assert(n, 'invalid token')
      p = p + #n
      local v = assert(tonumber(n))
      assert(v == v and math.abs(v) < 1e15)
      return v
    end
  end
  local v = parse(0)
  ws()
  assert(p > #s, 'trailing content')
  return v
end
return C
