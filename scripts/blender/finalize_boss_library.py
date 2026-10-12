"""Keep the full source library's Infernal pose-bank materials on original IDs.
Run after the full export and selected Infernal export have completed.
"""
import bpy,pathlib,json
R=pathlib.Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(R/'art-src/blender/bosses-complete.blend'))
for s in list(bpy.data.scenes):
 if s.get('boss_id')=='bailiff' and s.get('hell'):
  for ob in list(s.objects):bpy.data.objects.remove(ob,do_unlink=True)
  bpy.data.scenes.remove(s)
with bpy.data.libraries.load(str(R/'art-src/blender/bosses-bailiff_hell.blend'),link=False) as (source,target):
 target.scenes=[name for name in source.scenes if name.startswith('bailiff_hell.')]
for s in bpy.data.scenes:
 if s.get('boss_id'):
  s['ground_anchor']=[96,146];s['display_scale']=.85
bpy.context.window.scene=bpy.data.scenes['undertow']
bpy.ops.wm.save_as_mainfile(filepath=str(R/'art-src/blender/bosses-complete.blend'))
p=R/'assets/bosses/isometric/bosses.json';meta=json.loads(p.read_text());meta['scale']=.85;p.write_text(json.dumps(meta,indent=2)+'\n')
print('FINALIZED_BOSS_SOURCE',len([s for s in bpy.data.scenes if s.get('boss_id')]),flush=True)
