"""Package the editable Blender model, runtime atlases, viewer and reproducible scripts."""
from pathlib import Path
import subprocess, zipfile, hashlib
root=Path(__file__).resolve().parents[1]
subprocess.run(['python3','scripts/verify-bailiff.py'],cwd=root,check=True)
files=[p for p in (root/'assets/bosses/bailiff_iso').iterdir() if p.is_file()]
files += [root/'assets/bosses/bailiff.png',root/'art-src/blender/bailiff-original.blend',root/'art-src/blender/bailiff-isometric.blend',root/'src/data/bailiff_sprite.lua',root/'scripts/blender/build_bailiff.py',root/'scripts/blender/render_bailiff.py',root/'scripts/verify-bailiff.py']
out=root/'dist/ash-bailiff-isometric-assets.zip';out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(files):
        info=zipfile.ZipInfo(p.relative_to(root).as_posix(),(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(info,p.read_bytes())
out.with_suffix('.sha256').write_text(hashlib.sha256(out.read_bytes()).hexdigest()+'  '+out.name+'\n')
print('Packaged '+str(out.relative_to(root)))
