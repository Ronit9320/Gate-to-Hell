-- Deliberately ignores warnings while cycling three heroes and spamming damage.
-- Uses ordinary controls; useful for proving that recruitment alone cannot win.
return function(a)
  a:attack(a.boss.x, a.boss.y, true)
  a:attack(a.boss.x, a.boss.y)
  if a:hero().cd > 1 then
    for i, h in ipairs(a.run.team) do
      if h.hp > 0 and h.cd <= 0 then
        a:switch(i)
        break
      end
    end
  end
  a:update(0.05, 0, 0)
end
