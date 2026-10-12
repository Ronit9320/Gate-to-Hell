"""Reopen source libraries and validate the editable pose/material data."""
import bpy,pathlib,sys
sys.path.insert(0,str(pathlib.Path(__file__).parent));import build_missing_bosses as B
R=B.ROOT
bpy.ops.wm.open_mainfile(filepath=str(R/'art-src/blender/bosses-complete.blend'))
scenes=[s for s in bpy.data.scenes if s.get('boss_id')];assert len(scenes)==23,len(scenes)
for s in scenes:
 assert list(s['ground_anchor'])==[96,146]
 assert s.camera and s.camera.data.type=='ORTHO'
 assert any(o.animation_data for o in s.objects),s.name
infernal=next(s for s in scenes if s.get('boss_id')=='bailiff')
bank=B.frozen_bank(infernal,[o for o in infernal.objects if o.type in ('MESH','CURVE')])
assert len(bank)==40 and all(len(m.vertices)>100 for m in bank)
for m in bank:bpy.data.meshes.remove(m)
print('PASS editable 23 boss scenes and all 40 Infernal pose/material evaluations',flush=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art-src/blender/combat-effects.blend'))
scenes=[s for s in bpy.data.scenes if s.get('effect_id')];assert len(scenes)==91,len(scenes)
assert any('Bloom pollen' in o.name for o in bpy.data.scenes['reaction_bloom'].objects)
print('PASS editable 91 effect scenes including Bloom seed/burst refinement',flush=True)
bpy.ops.wm.open_mainfile(filepath=str(R/'art-src/blender/scenery-and-illustrations.blend'))
assert len([s for s in bpy.data.scenes if s.get('boss_id')])==14
print('PASS editable ten props and four illustrations',flush=True)
