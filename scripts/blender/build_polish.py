"""Render geometry-based UI symbols and nine animated elemental particle bursts.
blender -b -t 4 -P scripts/blender/build_polish.py
Editable animation scenes are saved in art-src/blender/element-effects.blend.
"""
import bpy, math, pathlib, subprocess, json
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[2]
OUT=R/'assets/effects'; OUT.mkdir(parents=True,exist_ok=True)
TMP=R/'art-src/effect-frames'; TMP.mkdir(parents=True,exist_ok=True)
COLORS={'Pyro':(1,.23,.025),'Hydro':(.04,.55,1),'Anemo':(.12,.95,.64),'Geo':(1,.65,.1),'Dendro':(.35,.85,.08),'Cryo':(.35,.85,1),'Electro':(.64,.24,1),'Gravity':(.47,.22,.95),'Antimatter':(1,.12,.55)}
bpy.ops.wm.read_factory_settings(use_empty=True)
def mat(name,col,glow=.6):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;n=m.node_tree.nodes.get('Principled BSDF');n.inputs['Base Color'].default_value=(*col,1);n.inputs['Metallic'].default_value=.2;n.inputs['Roughness'].default_value=.4;n.inputs['Emission Color'].default_value=(*col,1);n.inputs['Emission Strength'].default_value=glow;return m
GOLD=mat('Brass',(.95,.64,.22),.25); RED=mat('Health enamel',(1,.22,.24),.3);TEAL=mat('Teal enamel',(.15,.8,.7),.3)
def scene(name,size=192):
 s=bpy.data.scenes.new(name);bpy.context.window.scene=s;s.render.engine='CYCLES';s.cycles.samples=6;s.cycles.use_denoising=True;s.render.resolution_x=size;s.render.resolution_y=size;s.render.resolution_percentage=100;s.render.film_transparent=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGBA';s.view_settings.view_transform='Standard';s.world=bpy.data.worlds.new(name+' world');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.23,.25,.28,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.8
 cam=bpy.data.objects.new('Orthographic export camera',bpy.data.cameras.new(name+' camera'));s.collection.objects.link(cam);cam.location=(0,-8,5);cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=4;cam.data.sensor_fit='HORIZONTAL';s.camera=cam
 light=bpy.data.objects.new('Softbox',bpy.data.lights.new(name+' light','AREA'));s.collection.objects.link(light);light.location=(-3,-4,7);light.data.energy=400;light.data.size=5;s.frame_start=1;s.frame_end=12;s.render.fps=20;return s

def gem(name,loc,scale,m,kind='ico'):
 if kind=='cone':bpy.ops.mesh.primitive_cone_add(vertices=5,radius1=1,radius2=0,depth=2,location=loc)
 else:bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=loc)
 o=bpy.context.object;o.name=name;o.scale=scale;o.data.materials.append(m);return o

def tube(name,points,m,width=.025):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=width;c.bevel_resolution=2;sp=c.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(name,c);bpy.context.scene.collection.objects.link(o);o.data.materials.append(m);return o

def animate(o,loc,scale,phase,gravity=False):
 for frame in range(1,13):
  t=(frame-1)/11;a=phase+t*(1.1 if gravity else .25);r=(1.25-1.0*t if gravity else .18+1.05*t)
  o.location=(math.cos(a)*r,math.sin(a)*r,(.08+math.sin(phase*3)*.18+t*.55))
  fade=math.sin(math.pi*(.07+.88*t))*(1-.7*t)
  o.scale=tuple(v*fade for v in scale);o.rotation_euler=(t*2,phase,t*3)
  o.keyframe_insert(data_path='location',frame=frame);o.keyframe_insert(data_path='scale',frame=frame);o.keyframe_insert(data_path='rotation_euler',frame=frame)
for element,col in COLORS.items():
 s=scene(element+' | particle burst');m=mat(element+' luminous',col,1.1);bright=mat(element+' core',tuple(.65+.35*c for c in col),1.2)
 for i in range(16):
  angle=i*math.tau/16
  shape='cone' if element in ('Pyro','Hydro','Cryo','Antimatter') else 'ico'
  size=(.10,.10,.25) if element in ('Pyro','Hydro','Cryo') else (.19,.095,.025) if element=='Dendro' else (.15,.15,.15)
  if element=='Antimatter':size=(.16,.025,.1)
  o=gem(element+' particle %02d'%i,(0,0,0),size,m if i%3 else bright,shape);animate(o,(0,0,0),size,angle,element=='Gravity')
 # Element-specific silhouettes: rings, wind ribbons, bolts, thorn stems, ice stars.
 for k in range(3):
  pts=[]
  for j in range(25):
   a=j/24*math.tau
   if element=='Electro':r=.8+(.16 if j%2 else -.16);pts.append((math.cos(a)*r,math.sin(a)*r,.05+.12*math.sin(a*3)))
   elif element=='Anemo':pts.append((math.cos(a+k)*(.35+j*.025),math.sin(a+k)*(.35+j*.025),j*.018))
   elif element=='Pyro':pts.append((math.cos(k*2.1)*(.4+.25*math.sin(a)), math.sin(k*2.1)*(.4+.25*math.sin(a)), .1+j*.035))
   elif element=='Dendro':pts.append((math.cos(a)*.35+math.cos(k*2.1)*.65, math.sin(a)*.15+math.sin(k*2.1)*.65, .1+.1*math.sin(a)))
   elif element=='Cryo':
    r=.85 if j%4==0 else .25;pts.append((math.cos(a)*r,math.sin(a)*r,.08))
   elif element=='Geo':
    a=math.floor(j/6)*math.pi/2;pts.append((math.cos(a)*(.5+k*.15),math.sin(a)*(.5+k*.15),.1))
   elif element=='Antimatter':pts.append((math.cos(a)*(.7 if j%8 else 1.1),math.sin(a)*(.7 if j%8 else 1.1),.12))
   else:pts.append((math.cos(a)*(.55+k*.18),math.sin(a)*(.55+k*.18),.03+k*.025))
  o=tube(element+' energy ribbon '+str(k),pts,m,.018 if element in ('Hydro','Gravity','Anemo') else .025)
  for frame in range(1,13):
   t=(frame-1)/11;scale=(1.2-t*.8 if element=='Gravity' else .15+t*.9);o.scale=(scale,scale,scale);o.rotation_euler.z=t*1.5+k;o.keyframe_insert(data_path='scale',frame=frame);o.keyframe_insert(data_path='rotation_euler',frame=frame)
 s.timeline_markers.new('Impact / cast start',frame=1);s.timeline_markers.new('Peak',frame=5);s.timeline_markers.new('Dissipate',frame=12)
 frames=[]
 for f in range(1,13):
  s.frame_set(f);p=TMP/(element.lower()+'-%02d.png'%f);s.render.filepath=str(p);bpy.ops.render.render(write_still=True);frames.append(str(p))
 rows=[]
 for row in range(2):
  p=TMP/(element.lower()+'-row'+str(row)+'.png');subprocess.run(['magick',*frames[row*6:row*6+6],'+append',str(p)],check=True);rows.append(str(p))
 subprocess.run(['magick',*rows,'-append','-background','none','-alpha','background','-define','png:compression-level=9',str(OUT/(element.lower()+'.png'))],check=True)
 print('EXPORTED',element,flush=True)
# UI symbols: model silhouettes with beveled round metal strokes. Camera faces X/Z plane.
names=['heart','shield','attack','skill','dodge','ammo','bag','team','shop','reroll','door','help','settings','sound','save','trophy','death','check','close','pause','play','back','floor','reaction']
s=scene('UI icon library',768);s.render.resolution_y=288;s.camera.location=(0,-10,0);s.camera.rotation_euler=(math.pi/2,0,0);s.camera.data.ortho_scale=16
paths={
'heart':[[(-.65,.22),(-.6,.5),(-.32,.65),(0,.4),(.32,.65),(.6,.5),(.65,.22),(0,-.65),(-.65,.22)]],
'shield':[[(-.6,.55),(.6,.55),(.5,-.2),(0,-.65),(-.5,-.2),(-.6,.55)]],
'attack':[[(-.55,-.6),(.48,.58),(.62,.65),(.64,.4),(-.4,-.65)],[(-.6,-.12),(-.1,-.6)]],
'skill':[[(-.1,.7),(-.5,-.05),(.05,-.05),(-.15,-.7),(.55,.18),(0,.18),(-.1,.7)]],
'dodge':[[(-.6,.4),(.15,.4),(.6,0),(.15,-.4),(-.6,-.4)],[(-.6,0),(.4,0)]],
'ammo':[[(-.25,-.6),(-.25,.3),(0,.65),(.25,.3),(.25,-.6),(-.25,-.6)],[(-.25,-.3),(.25,-.3)]],
'bag':[[(-.6,-.6),(-.55,.35),(.55,.35),(.6,-.6),(-.6,-.6)],[(-.3,.35),(-.3,.65),(.3,.65),(.3,.35)]],
'shop':[[(-.6,-.6),(-.6,.3),(.6,.3),(.6,-.6),(-.6,-.6)],[(-.7,.3),(-.5,.7),(.5,.7),(.7,.3)],[(-.1,-.6),(-.1,0),(.3,0),(.3,-.6)]],
'door':[[(-.55,-.65),(-.55,.65),(.55,.65),(.55,-.65)],[(-.4,-.6),(.2,-.45),(.2,.5),(-.4,.6),(-.4,-.6)],[(.05,0),(.14,0)]],
'help':[[(-.45,.4),(-.3,.65),(.3,.65),(.45,.4),(.35,.1),(0,-.1),(0,-.25)],[(0,-.55),(0,-.65)]],
'save':[[(-.6,-.6),(-.6,.6),(.4,.6),(.6,.4),(.6,-.6),(-.6,-.6)],[(-.3,.6),(-.3,.15),(.3,.15),(.3,.6)],[(-.3,-.6),(-.3,-.2),(.3,-.2),(.3,-.6)]],
'trophy':[[(-.4,.6),(.4,.6),(.3,-.05),(0,-.25),(-.3,-.05),(-.4,.6)],[(-.4,.4),(-.7,.4),(-.65,0),(-.3,-.1)],[(.4,.4),(.7,.4),(.65,0),(.3,-.1)],[(0,-.25),(0,-.6)],[(-.4,-.6),(.4,-.6)]],
'death':[[(-.6,.1),(-.5,.5),(0,.7),(.5,.5),(.6,.1),(.3,-.25),(.3,-.6),(-.3,-.6),(-.3,-.25),(-.6,.1)],[(-.3,.15),(-.18,.15)],[(.18,.15),(.3,.15)]],
'check':[[(-.6,0),(-.15,-.5),(.65,.55)]],'close':[[(-.5,-.5),(.5,.5)],[(-.5,.5),(.5,-.5)]],'pause':[[(-.25,-.6),(-.25,.6)],[(.25,-.6),(.25,.6)]],'play':[[(-.35,-.6),(.6,0),(-.35,.6),(-.35,-.6)]],'back':[[(-.6,0),(.6,0)],[(0,.6),(-.6,0),(0,-.6)]],'floor':[[(-.65,-.6),(-.65,-.2),(-.2,-.2),(-.2,.2),(.2,.2),(.2,.6),(.65,.6)]],
'sound':[[(-.6,-.2),(-.3,-.2),(.15,-.6),(.15,.6),(-.3,.2),(-.6,.2),(-.6,-.2)],[(.35,.4),(.55,.2),(.55,-.2),(.35,-.4)]],
}
for idx,name in enumerate(names):
 x=-7+(idx%8)*2;z=2-(idx//8)*2
 ps=paths.get(name)
 if ps is None:
  ps=[]
  if name=='team':
   for dx in (-.4,.4):ps.append([(dx+math.cos(j*math.tau/16)*.19,.35+math.sin(j*math.tau/16)*.19) for j in range(17)]);ps.append([(dx-.3,-.6),(dx-.25,-.1),(dx+.25,-.1),(dx+.3,-.6)])
  else:
   ps=[[(math.cos(j*math.tau/24)*.55,math.sin(j*math.tau/24)*.55) for j in range(25)]]
   if name=='settings':
    for j in range(8):a=j*math.tau/8;ps.append([(math.cos(a)*.45,math.sin(a)*.45),(math.cos(a)*.75,math.sin(a)*.75)])
   elif name=='reroll':ps.append([(.5,.6),(.7,.25),(.25,.25)])
   elif name=='reaction':ps.append([(-.5,-.5),(.5,.5)])
 for p in ps:tube(name,[(x+a,0,z+b) for a,b in p],RED if name=='heart' else TEAL if name in ('shield','dodge') else GOLD,.065)
s.render.filepath=str(R/'assets/ui/icons.png');bpy.ops.render.render(write_still=True)
(R/'art-src/blender').mkdir(parents=True,exist_ok=True)
bpy.context.window.scene=bpy.data.scenes['Pyro | particle burst'];bpy.ops.wm.save_as_mainfile(filepath=str(R/'art-src/blender/element-effects.blend'))
(OUT/'effects.json').write_text(json.dumps({'elements':list(COLORS),'cell':[192,192],'columns':6,'frames':12,'duration':.6,'source':'art-src/blender/element-effects.blend','icons':names},indent=2)+'\n')
