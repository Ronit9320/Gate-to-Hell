"""Merge the refined seed/burst timing into the complete editable library."""
import bpy,pathlib
R=pathlib.Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(R/'art-src/blender/combat-effects.blend'))
for id in ['reaction_bloom','status_bloom']:
 s=bpy.data.scenes.get(id)
 if s:
  for o in list(s.objects):bpy.data.objects.remove(o,do_unlink=True)
  bpy.data.scenes.remove(s)
with bpy.data.libraries.load(str(R/'art-src/blender/combat-effects-reaction_bloom-status_bloom.blend'),link=False) as (source,target):target.scenes=['reaction_bloom','status_bloom']
bpy.context.window.scene=bpy.data.scenes['reaction_bloom'];bpy.ops.wm.save_as_mainfile(filepath=str(R/'art-src/blender/combat-effects.blend'))
print('FINALIZED_COMBAT_SOURCE',len([s for s in bpy.data.scenes if s.get('effect_id')]),flush=True)
