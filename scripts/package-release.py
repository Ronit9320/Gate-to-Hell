"""Bundle upload files and reviewable listing material after release verification."""
from pathlib import Path
import argparse
import hashlib
import json
import zipfile
import subprocess

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--include-art', action='store_true')
args = parser.parse_args()
subprocess.run(['python3', 'scripts/verify-release.py'] + (['--include-art'] if args.include_art else []), cwd=root, check=True)
for name in ['cover.png', 'screenshots/draft.png', 'screenshots/arena.png', 'screenshots/shop.png', 'screenshots/victory.png']:
    assert (root / 'release' / name).is_file(), 'Missing media: ' + name
for name in ['browser', 'firefox', 'release', 'management']:
    assert (root / '.test-results' / (name + '.json')).is_file(), 'Missing verification: ' + name
version = json.loads((root / 'package.json').read_text())['version']
files = list((root / 'release').rglob('*'))
files += [root / 'dist' / name for name in ['house-of-cinders.love', 'house-of-cinders-web.zip', 'SHA256SUMS']]
target = root / 'dist' / ('house-of-cinders-' + version + '-release-kit.zip')
with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in sorted(files):
        if p.is_file():
            info = zipfile.ZipInfo(p.relative_to(root).as_posix(), (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, p.read_bytes())
(target.with_suffix('.sha256')).write_text(hashlib.sha256(target.read_bytes()).hexdigest() + '  ' + target.name + '\n')
print('Prepared ' + str(target.relative_to(root)))
