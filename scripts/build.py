"""Package only runtime assets; deterministic archives and a pinned web runtime."""
import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
OUT.mkdir(exist_ok=True)
parser = argparse.ArgumentParser()
parser.add_argument('--include-art', action='store_true', help='Include approved top-level hero/boss portraits; enable usePortraits in presentation.lua too')
args = parser.parse_args()

def archive(target, files, base):
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as package:
        for file in sorted(files):
            info = zipfile.ZipInfo(file.relative_to(base).as_posix(), (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            package.writestr(info, file.read_bytes())

files = [ROOT / 'main.lua', ROOT / 'conf.lua']
files += list((ROOT / 'src').rglob('*.lua'))
files += list((ROOT / 'assets').glob('*.txt'))
files += sorted((ROOT / 'assets/fonts').glob('*.ttf'))
files += sorted((ROOT / 'assets/fonts').glob('*.txt'))
files += sorted((ROOT / 'assets/effects/authored').glob('*.png'))
# Runtime Blender art requested by the author; source and previews never ship.
boss_dir = ROOT / 'assets/bosses/bailiff_iso'
approved_boss_files = [boss_dir / ('bailiff_y%03d.png' % angle) for angle in range(0, 360, 45)] + [boss_dir / 'bailiff.json', boss_dir / 'portrait.png']
assert all(p.is_file() for p in approved_boss_files), 'Finish the eight-direction Bailiff export before building'
files += approved_boss_files
new_boss_dir = ROOT / 'assets/bosses/isometric'
boss_metadata = new_boss_dir / 'bosses.json'
boss_names = json.loads(boss_metadata.read_text())['bosses']
assert len(set(boss_names)) == 23, 'Finish nine bosses, ten Hell appearances and four extra Throne phases'
new_boss_files = [boss_metadata]
for boss in boss_names:
    new_boss_files += [new_boss_dir / boss / ('boss_y%03d.png' % angle) for angle in range(0, 360, 45)]
    new_boss_files.append(new_boss_dir / boss / 'portrait.png')
assert all(p.is_file() for p in new_boss_files), 'Incomplete boss library'
files += new_boss_files
# The Blender-built UI backdrops/menus are approved runtime art.
ui_dir = ROOT / 'assets/ui'
approved_ui_files = sorted(ui_dir.glob('*.png'))
assert approved_ui_files, 'Render the UI art (scripts/blender/build_ui.py) before building'
files += approved_ui_files
files += sorted((ROOT / 'assets/scenery').glob('*.png'))
files += sorted((ROOT / 'assets/effects').glob('*.png'))
files.append(ROOT / 'assets/effects/effects.json')
combat_dir = ROOT / 'assets/effects/combat'
combat_meta = combat_dir / 'combat.json'
combat_files = [combat_dir / (name + '.png') for name in json.loads(combat_meta.read_text())['effects']]
assert all(p.is_file() for p in combat_files), 'Incomplete combat artwork'
files += combat_files + [combat_meta]
# Reference-inspired Blender heroes are independent of the optional old portraits.
hero_dir = ROOT / 'assets/heroes/isometric'
hero_meta = hero_dir / 'heroes.json'
assert hero_meta.is_file(), 'Render the hero library before building'
hero_ids = json.loads(hero_meta.read_text())['heroes']
assert len(hero_ids) == 18 and len(set(hero_ids)) == 18
hero_files = [hero_meta]
for hero in hero_ids:
    hero_files += [hero_dir / hero / ('hero_y%03d.png' % angle) for angle in range(0, 360, 45)]
    hero_files.append(hero_dir / hero / 'portrait.png')
assert all(p.is_file() for p in hero_files), 'Finish all 18 eight-direction hero exports before building'
files += hero_files
if args.include_art:
    files += list((ROOT / 'assets/heroes').glob('*.png'))
    files += list((ROOT / 'assets/bosses').glob('*.png'))
archive(OUT / 'gate-to-hell.love', files, ROOT)
subprocess.run([
    str(ROOT / 'node_modules/.bin/love.js'), str(OUT / 'gate-to-hell.love'),
    str(OUT / 'web'), '-c', '-t', 'Gate to Hell', '-m', '268435456',
], check=True, cwd=ROOT)
# Export the runtime filesystem for the synchronous, bounded save adapter.
# Guard the patch so a toolchain update cannot silently break persistence.
runtime = OUT / 'web/love.js'
source = runtime.read_text()
assert source.count('FS.staticInit();') == 1, 'Unexpected love.js runtime: review save adapter'
runtime.write_text(source.replace('FS.staticInit();', 'FS.staticInit();Module.cindersFS=FS;'))
# love.js uses a random preload-cache UUID. Content-address it for reproducibility.
loader = OUT / 'web/game.js'
digest = hashlib.sha256((OUT / 'gate-to-hell.love').read_bytes()).hexdigest()
loader_source = loader.read_text()
# A large IndexedDB cache write must not block the first playable frame. Some
# browser/storage combinations leave that transaction pending indefinitely.
cache_block = '''                    cacheRemotePackage(db, PACKAGE_PATH + PACKAGE_NAME, packageData, {uuid:PACKAGE_UUID}, processPackageData,
                      function(error) {
                        console.error(error);
                        processPackageData(packageData);
                      });'''
assert loader_source.count(cache_block) == 1, 'Unexpected preload cache: review nonblocking startup'
loader_source = loader_source.replace(cache_block, '''                    processPackageData(packageData);
                    try {
                      cacheRemotePackage(db, PACKAGE_PATH + PACKAGE_NAME, packageData, {uuid:PACKAGE_UUID}, function() {},
                        function(error) { console.warn('Optional game cache unavailable', error); });
                    } catch (error) { console.warn('Optional game cache unavailable', error); }''')
loader.write_text(re.sub(r'"package_uuid":"[^"]+"', '"package_uuid":"' + digest + '"', loader_source))
(OUT / 'web/index.html').write_bytes((ROOT / 'web/index.html').read_bytes())
(OUT / 'web/LOVEJS-LICENSE.txt').write_bytes((ROOT / 'node_modules/love.js/LICENSE').read_bytes())
(OUT / 'web/LOVE-LICENSE.txt').write_bytes((ROOT / 'assets/LOVE-LICENSE.txt').read_bytes())
web_files = [OUT / 'web' / name for name in ['index.html','game.js','game.data','love.js','love.wasm','LOVE-LICENSE.txt','LOVEJS-LICENSE.txt']]
archive(OUT / 'gate-to-hell-web.zip', web_files, OUT / 'web')
with zipfile.ZipFile(OUT / 'gate-to-hell-web.zip') as z:
    assert 'index.html' in z.namelist()
with zipfile.ZipFile(OUT / 'gate-to-hell.love') as z:
    assert 'main.lua' in z.namelist()
    if not args.include_art:
        allowed = ('assets/bosses/bailiff_iso/', 'assets/bosses/isometric/', 'assets/ui/', 'assets/heroes/isometric/', 'assets/effects/', 'assets/scenery/')
        assert not any(
            n.endswith('.png') and not n.startswith(allowed) for n in z.namelist()
        )
    assert 'devtools.lua' not in z.namelist(), 'Developer tools must never ship'
    assert not any(p.startswith(('tests/', '.git/', 'node_modules/')) for p in z.namelist())
artifacts = [OUT / 'gate-to-hell.love', OUT / 'gate-to-hell-web.zip']
(OUT / 'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.name + '\n' for p in artifacts))
print('Built dist/gate-to-hell.love and dist/gate-to-hell-web.zip')
