"""Fail if the default release differs from source, leaks development files, or is incomplete."""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile

root = Path(__file__).resolve().parents[1]
out = root / 'dist'
parser = argparse.ArgumentParser()
parser.add_argument('--include-art', action='store_true')
args = parser.parse_args()
version = json.loads((root / 'package.json').read_text())['version']
assert 'v' + version in (root / 'web/index.html').read_text()
assert "version = '" + version + "'" in (root / 'src/data/presentation.lua').read_text()
with zipfile.ZipFile(out / 'house-of-cinders.love') as z:
    expected = {'main.lua', 'conf.lua'}
    expected.update(p.relative_to(root).as_posix() for p in (root / 'src').rglob('*.lua'))
    expected.update(p.relative_to(root).as_posix() for p in (root / 'assets').glob('*.txt'))
    expected.update('assets/bosses/bailiff_iso/bailiff_y%03d.png' % angle for angle in range(0, 360, 45))
    expected.add('assets/bosses/bailiff_iso/bailiff.json')
    expected.add('assets/bosses/bailiff_iso/portrait.png')
    boss_dir = root / 'assets/bosses/isometric'
    expected.add('assets/bosses/isometric/bosses.json')
    for boss in json.loads((boss_dir / 'bosses.json').read_text())['bosses']:
        expected.update('assets/bosses/isometric/' + boss + '/boss_y%03d.png' % angle for angle in range(0, 360, 45))
        expected.add('assets/bosses/isometric/' + boss + '/portrait.png')
    expected.update(p.relative_to(root).as_posix() for p in (root / 'assets/ui').glob('*.png'))
    expected.update(p.relative_to(root).as_posix() for p in (root / 'assets/effects').glob('*.png'))
    expected.update(p.relative_to(root).as_posix() for p in (root / 'assets/scenery').glob('*.png'))
    expected.add('assets/effects/effects.json')
    combat_dir = root / 'assets/effects/combat'
    expected.add('assets/effects/combat/combat.json')
    expected.update('assets/effects/combat/' + name + '.png' for name in json.loads((combat_dir / 'combat.json').read_text())['effects'])
    hero_dir = root / 'assets/heroes/isometric'
    expected.add('assets/heroes/isometric/heroes.json')
    for hero in json.loads((hero_dir / 'heroes.json').read_text())['heroes']:
        expected.update('assets/heroes/isometric/' + hero + '/hero_y%03d.png' % angle for angle in range(0, 360, 45))
        expected.add('assets/heroes/isometric/' + hero + '/portrait.png')
    if args.include_art:
        for folder in ['heroes', 'bosses']:
            expected.update(p.relative_to(root).as_posix() for p in (root / 'assets' / folder).glob('*.png'))
    assert set(z.namelist()) == expected, 'Release contents do not match the selected asset mode'
    for name in expected:
        assert z.read(name) == (root / name).read_bytes(), name
with zipfile.ZipFile(out / 'house-of-cinders-web.zip') as z:
    expected = {'index.html', 'game.js', 'game.data', 'love.js', 'love.wasm', 'LOVE-LICENSE.txt', 'LOVEJS-LICENSE.txt'}
    assert set(z.namelist()) == expected
    for name in expected:
        assert z.read(name) == (out / 'web' / name).read_bytes(), name
    assert z.read('game.data') == (out / 'house-of-cinders.love').read_bytes()
    assert z.read('index.html') == (root / 'web/index.html').read_bytes()
for line in (out / 'SHA256SUMS').read_text().splitlines():
    digest, name = line.split('  ')
    assert hashlib.sha256((out / name).read_bytes()).hexdigest() == digest, name
print('PASS version, exact source/archive match, browser dependencies, licenses, exclusions and checksums')
