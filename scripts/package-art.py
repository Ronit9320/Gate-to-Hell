"""Bundle new runtime art, editable sources, metadata, gallery and generators."""
import pathlib, zipfile, hashlib
R=pathlib.Path(__file__).resolve().parents[1];out=R/'dist';out.mkdir(exist_ok=True)
files=[R/'assets/art-preview.html',R/'assets/ATTRIBUTION.txt',R/'ART_DELIVERY.md',R/'release/cover-blender.png']
for folder in ['assets/bosses/isometric','assets/effects/combat','assets/scenery']:files.extend(p for p in (R/folder).rglob('*') if p.is_file())
for name in ['bosses-complete.blend','combat-effects.blend','scenery-and-illustrations.blend','release-cover.blend','bailiff-isometric.blend','bosses-bailiff_hell.blend','combat-effects-reaction_bloom-status_bloom.blend']:files.append(R/'art-src/blender'/name)
for name in ['build_missing_bosses.py','build_combat_art.py','build_finishing_art.py','build_release_cover.py','finalize_boss_library.py','finalize_combat_source.py','verify_art_sources.py']:files.append(R/'scripts/blender'/name)
files.extend(R/p for p in ['scripts/verify-art.py','scripts/package-art.py','src/data/boss_sprites.lua','src/data/combat_art.lua','src/render/combat_art.lua','src/render/scenery.lua'])
target=out/'gate-to-hell-blender-art.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(set(files)):
  assert p.is_file(),p
  info=zipfile.ZipInfo(p.relative_to(R).as_posix(),(2026,10,12,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,p.read_bytes())
(target.with_suffix('.sha256')).write_text(hashlib.sha256(target.read_bytes()).hexdigest()+'  '+target.name+'\n')
print('Packaged',target.relative_to(R),'(',len(set(files)),'files)')
