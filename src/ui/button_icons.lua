-- Ordered prefixes keep action icons predictable while retaining every text label.
local B = {}
local rules = {
  { 'Close', 'close' },
  { 'Confirm transaction', 'gold' },
  { 'Confirm sale', 'gold' },
  { 'Cancel', 'close' },
  { 'SOLD', 'check' },
  { 'Inspect', 'gold' },
  { 'Buy', 'gold' },
  { 'Sell', 'gold' },
  { 'Replace', 'team' },
  { 'Choose', 'check' },
  { 'New run', 'play' },
  { 'Demo', 'play' },
  { 'Continue', 'save' },
  { 'Resume', 'play' },
  { 'Title', 'back' },
  { 'Previous', 'back' },
  { 'Next', 'door' },
  { 'Enter', 'door' },
  { 'Finish', 'trophy' },
  { 'Visit', 'shop' },
  { 'Inventory', 'bag' },
  { 'Manage', 'team' },
  { 'Equip', 'attack' },
  { 'Unequip', 'bag' },
  { 'Use', 'bag' },
  { 'Discard', 'close' },
  { 'Reroll', 'reroll' },
  { 'How', 'help' },
  { 'Controls', 'help' },
  { 'Got it', 'check' },
  { 'Credits', 'help' },
  { 'Tutorial', 'help' },
  { 'Rebind', 'settings' },
  { 'Skill', 'skill' },
  { 'Dodge', 'dodge' },
  { 'Consumable', 'bag' },
  { 'Sound', 'sound' },
  { 'Audio', 'sound' },
  { 'Music', 'sound' },
  { 'Effects', 'sound' },
  { 'Volume', 'sound' },
  { 'Settings', 'settings' },
  { 'Fullscreen', 'settings' },
  { 'Reduced', 'settings' },
  { 'Screen', 'settings' },
  { 'Text', 'settings' },
}
function B.forLabel(label)
  for id, item in pairs(require('src.data.items')) do
    if label:sub(1, #item.name) == item.name or label:sub(1, #item.name + 6) == 'Equip ' .. item.name then
      return id
    end
  end
  for _, rule in ipairs(rules) do
    if label:sub(1, #rule[1]) == rule[1] then
      return rule[2]
    end
  end
  return 'check'
end
return B
