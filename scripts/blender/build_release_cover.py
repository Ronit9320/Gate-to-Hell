"""Non-destructive 630x500 Blender cover featuring the new boss geometry."""
import bpy, math, pathlib
from mathutils import Vector, Matrix
R=pathlib.Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(R/'art-src/blender/bosses-complete.blend'))
cover=bpy.data.scenes.new('House of Cinders cover');cover.render.engine='CYCLES';cover.cycles.samples=24;cover.cycles.use_denoising=True;cover.render.threads_mode='FIXED';cover.render.threads=4;cover.render.resolution_x=630;cover.render.resolution_y=500;cover.render.resolution_percentage=100;cover.render.image_settings.file_format='PNG';cover.render.film_transparent=False;cover.view_settings.view_transform='Standard'
cover.world=bpy.data.worlds.new('Cover world');cover.world.use_nodes=True;bg=next(n for n in cover.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.02,.043,.048,1);bg.inputs[1].default_value=.7
cam=bpy.data.objects.new('Cover camera',bpy.data.cameras.new('Cover camera'));cover.collection.objects.link(cam);target=Vector((0,0,1.4));cam.location=target+Vector((6,-6,math.sqrt(24)));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=5.3;cam.data.sensor_fit='HORIZONTAL';cover.camera=cam
right=cam.rotation_euler.to_matrix()@Vector((1,0,0));up=cam.rotation_euler.to_matrix()@Vector((0,1,0));normal=cam.rotation_euler.to_matrix()@Vector((0,0,1))
for i,id in enumerate(['undertow','kings','bramble']):
 source=bpy.data.scenes[id];bpy.context.window.scene=source;source.frame_set(1);deps=bpy.context.evaluated_depsgraph_get()
 for p in source.objects:
  if p.type not in ('MESH','CURVE') or p.hide_render:continue
  ev=p.evaluated_get(deps);mesh=bpy.data.meshes.new_from_object(ev);o=bpy.data.objects.new(id+' cover mesh',mesh);cover.collection.objects.link(o)
  o.matrix_world=Matrix.Translation(right*((i-1)*1.40)+up*(-.42))@Matrix.Scale(.73,4)@ev.matrix_world
bpy.context.window.scene=cover
for label,rot,energy,color in [('Key',(25,-20,-35),2.3,(1,.86,.67)),('Fill',(50,0,145),.8,(.55,.73,1)),('Rim',(-40,15,20),1.3,(.8,.85,1))]:
 d=bpy.data.lights.new(label,'SUN');d.energy=energy;d.color=color;d.angle=.15;o=bpy.data.objects.new(label,d);cover.collection.objects.link(o);o.rotation_euler=tuple(math.radians(a)for a in rot)
def mat(name,col,glow):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');n.inputs['Base Color'].default_value=(*col,1);n.inputs['Emission Color'].default_value=(*col,1);n.inputs['Emission Strength'].default_value=glow;return m
gold=mat('Cover gold',(.93,.65,.22),.5);pale=mat('Cover ivory',(.58,.77,.74),.6)
def text(label,y,size,material):
 c=bpy.data.curves.new(label,'FONT');c.body=label;c.align_x='CENTER';c.size=size;c.extrude=.003;c.space_character=1.1;o=bpy.data.objects.new(label,c);cover.collection.objects.link(o);o.location=target+up*y+normal*2;o.rotation_euler=cam.rotation_euler;o.data.materials.append(material)
text('HOUSE OF',1.18,.42,gold);text('CINDERS',.58,.62,gold);text('BUILD YOUR HAND. BREAK THE HOUSE.',.20,.125,pale);text('18 HEROES  /  10 BOSSES  /  ENDLESS HELL',-1.88,.115,pale)
source=R/'art-src/blender/release-cover.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source));cover.render.filepath=str(R/'release/cover-blender.png');bpy.ops.render.render(write_still=True)
