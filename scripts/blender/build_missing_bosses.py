"""Original articulated bosses, Hell costumes and Throne phases; Blender-only art.
blender -b -t 4 -P scripts/blender/build_missing_bosses.py [-- --ids undertow --preview]
Each direction is a camera-aligned atlas render, with evaluated mesh poses.
"""
import argparse, json, math, pathlib, subprocess, sys
import bpy
from mathutils import Vector, Matrix
ROOT=pathlib.Path(__file__).resolve().parents[2]
OUT=ROOT/'assets/bosses/isometric'; OUT.mkdir(parents=True,exist_ok=True)
PRE=ROOT/'art-src/previews/bosses'; PRE.mkdir(parents=True,exist_ok=True)
IDS=['undertow','kite','bedrock','bramble','regent','static','sun','kings','throne']
COLORS={'bailiff':(1,.18,.025),'undertow':(.03,.55,.85),'kite':(.08,.73,.48),'bedrock':(.85,.49,.08),'bramble':(.24,.6,.035),'regent':(.26,.74,1),'static':(.58,.18,1),'sun':(1,.34,.015),'kings':(.42,.12,.9),'throne':(.96,.05,.4)}
ANIMS=[('idle',8,12,True),('attack',10,12,False),('hurt',4,12,False),('death',10,10,False),('stagger',4,8,True),('recovery',4,12,False)]
S=None; PARTS=[]; PIV={}; MAT={}
def material(name,c,metal=0,glow=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1);m.use_nodes=True
 n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');n.inputs['Base Color'].default_value=(*c,1);n.inputs['Metallic'].default_value=metal;n.inputs['Roughness'].default_value=.38 if metal else .64;n.inputs['Emission Color'].default_value=(*c,1);n.inputs['Emission Strength'].default_value=glow;return m
def pivot(name,loc,parent=None):
 o=bpy.data.objects.new(name,None);S.collection.objects.link(o);o.location=loc
 if parent:o.parent=PIV[parent];o.matrix_parent_inverse=PIV[parent].matrix_world.inverted()
 PIV[name]=o;bpy.context.view_layer.update();return o
def attach(o,key,p='body'):
 o.data.materials.append(MAT[key]);bpy.context.view_layer.update();world=o.matrix_world.copy();o.parent=PIV[p];o.matrix_parent_inverse=PIV[p].matrix_world.inverted();o.matrix_world=world;PARTS.append(o);return o
def box(name,loc,size,key='dark',p='body',bev=.035):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.scale=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 if bev:m=o.modifiers.new('Chiseled edge','BEVEL');m.width=bev;m.segments=2;o.modifiers.new('Normals','WEIGHTED_NORMAL')
 return attach(o,key,p)
def gem(name,loc,size,key='element',p='body'):
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=loc);o=bpy.context.object;o.name=name;o.scale=size;return attach(o,key,p)
def cone(name,loc,r1,r2,depth,key='cloth',p='body',verts=12):
 bpy.ops.mesh.primitive_cone_add(vertices=verts,radius1=r1,radius2=r2,depth=depth,location=loc);o=bpy.context.object;o.name=name;return attach(o,key,p)
def rod(name,a,b,r=.035,key='gold',p='body',verts=8):
 v=Vector(b)-Vector(a);o=cone(name,(Vector(a)+Vector(b))/2,r,r,v.length,key,p,verts);o.rotation_euler=v.to_track_quat('Z','Y').to_euler();return o
def curve(name,points,r=.025,key='gold',p='body'):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=1;sp=c.splines.new('POLY');sp.points.add(len(points)-1)
 for v,co in zip(sp.points,points):v.co=(*co,1)
 o=bpy.data.objects.new(name,c);S.collection.objects.link(o);return attach(o,key,p)
def ring(name,loc,r,key='gold',p='body',vertical=False,width=.025):
 points=[(loc[0]+r*math.cos(i*math.tau/32),loc[1]+(0 if vertical else r*math.sin(i*math.tau/32)),loc[2]+(r*math.sin(i*math.tau/32) if vertical else 0)) for i in range(33)];return curve(name,points,width,key,p)
def crown(loc,r=.28,key='gold',p='head'):
 ring('Crown circlet',loc,r,key,p,width=.035)
 for i in range(7):
  a=i*math.tau/7;cone('Crown spire',(loc[0]+r*math.cos(a),loc[1]+r*math.sin(a),loc[2]+.12),.07,0,.27,key,p,5)
def eyes(z=1.95,p='head',y=-.24):
 for sign in (-1,1):gem('Luminous eye',(sign*.09,y,z),(.05,.026,.03),'core',p)
def setup(name,id,hell):
 global S,PARTS,PIV,MAT
 S=bpy.data.scenes.new(name);bpy.context.window.scene=S;PARTS=[];PIV={}
 S.render.engine='CYCLES';S.cycles.samples=6;S.cycles.use_denoising=True;S.render.threads_mode='FIXED';S.render.threads=4;S.render.film_transparent=True;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGBA';S.render.image_settings.compression=85;S.render.resolution_percentage=100;S.view_settings.view_transform='Standard'
 S.world=bpy.data.worlds.new(name+' world');S.world.use_nodes=True;bg=next(n for n in S.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.22,.27,.34,1);bg.inputs[1].default_value=.5
 for label,rot,energy,col in [('Key',(25,-20,-35),2.3,(1,.87,.7)),('Fill',(50,0,145),.9,(.55,.74,1)),('Rim',(-40,15,20),1.3,(.8,.85,1))]:
  d=bpy.data.lights.new(label,'SUN');d.energy=energy;d.color=col;d.angle=.15;o=bpy.data.objects.new(label,d);S.collection.objects.link(o);o.rotation_euler=tuple(math.radians(a) for a in rot)
 cam=bpy.data.objects.new('Isometric camera',bpy.data.cameras.new(name+' camera'));S.collection.objects.link(cam);cam.data.type='ORTHO';cam.data.sensor_fit='HORIZONTAL';cam.data.ortho_scale=4.2
 target=Vector((0,0,1.27));cam.location=target+Vector((6,-6,math.sqrt(24)));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();S.camera=cam
 c=COLORS[id];dark=(.027,.018,.04) if hell else (.055,.085,.12)
 MAT={'dark':material(name+' charcoal',dark,.35),'cloth':material(name+' royal cloth',tuple(v*(.16 if hell else .30) for v in c)), 'element':material(name+' enamel',c,.3,.28),'core':material(name+' luminous core',tuple(.48+.52*v for v in c),.15,1.1),'gold':material(name+' metal',(.45,.12,.09) if hell else (.85,.52,.17),.72), 'stone':material(name+' stone',(.06,.04,.095) if hell else (.3,.32,.35),.18),'white':material(name+' ivory',(.23,.19,.31) if hell else (.62,.8,.86),.3),'thorn':material(name+' bark',(.19,.045,.017) if hell else (.16,.25,.06))}
 pivot('root',(0,0,0));pivot('body',(0,0,1.1),'root');pivot('head',(0,0,1.95),'body');pivot('left',(-.48,0,1.45),'body');pivot('right',(.48,0,1.45),'body');pivot('halo',(0,0,1.6),'root')
 S['boss_id']=id;S['hell']=hell;S['ground_anchor']=[96,146];S['projection']='azimuth 45 elevation 30'
def build(id,hell,phase=1):
 if id=='undertow':
  cone('Tidal layered gown',(0,0,.62),.61,.24,1.10,'cloth');cone('Foam hem',(0,0,.16),.65,.6,.15,'white');gem('Pearl cuirass',(0,0,1.36),(.28,.24,.44),'element');gem('Veiled face',(0,-.035,1.95),(.23,.19,.25),'white','head');eyes();crown((0,0,2.18),.25)
  for i in range(9):
   a=i*math.tau/9;curve('Water gown embroidery',[(math.cos(a)*(.24+j*.048),math.sin(a)*(.24+j*.048),1.1-j*.1) for j in range(9)],.018,'core')
  rod('Trident shaft',(.68,0,.18),(.68,0,2.4),.035,'gold','right')
  for off in (-.16,0,.16):rod('Trident tine',(.68+off,0,2.05),(.68+off,0,2.43),.025,'core','right')
  gem('Shell pauldron',(-.42,0,1.6),(.3,.28,.18),'gold','left');ring('Tide hoop',(0,0,.23),.78,'element','halo')
 elif id=='kite':
  gem('Turbine body',(0,0,1.15),(.30,.28,.6),'dark');gem('Brass avian head',(0,-.08,1.87),(.25,.28,.29),'gold','head');gem('Swept beak',(0,-.39,1.85),(.13,.29,.10),'white','head');eyes(1.93,y=-.3)
  for sign,p in [(-1,'left'),(1,'right')]:
   rod('Wing spar',(sign*.25,0,1.55),(sign*1.12,0,1.22),.05,'gold',p)
   for j in range(6):
    x=sign*(.38+j*.14);o=box('Layered brass flight feather',(x,.02,1.24-j*.065),(.18,.11,.66-j*.035),'gold',p,.015);o.rotation_euler.y=sign*.5
    gem('Razor feather edge',(x,-.08,1.05-j*.06),(.06,.035,.28),'element',p)
   rod('Taloned foot',(sign*.16,0,.76),(sign*.2,-.12,.42),.035,'gold')
  ring('Turbine aperture',(0,-.285,1.34),.21,'core',vertical=True);cone('Tail fin',(0,.23,.72),.2,0,.55,'element',verts=4)
 elif id=='bedrock':
  for z,w in [(.36,.78),(.85,.93),(1.4,.83)]:box('Stratified basalt torso',(0,0,z),(w,.55,.45),'stone')
  for sign,p in [(-1,'left'),(1,'right')]:
   box('Monolith shoulder',(sign*.62,0,1.49),(.48,.61,.48),'stone',p);box('Pillar forearm',(sign*.72,0,.95),(.36,.4,.64),'gold',p);box('Foundation foot',(sign*.26,-.10,.12),(.36,.55,.25),'dark')
   gem('Quartz seam',(sign*.46,-.30,1.4),(.12,.03,.35),'core',p)
  box('Baron head',(0,0,2.02),(.50,.48,.48),'stone','head');eyes(2.05,y=-.26);crown((0,0,2.3),.24);gem('Faultline heart',(0,-.31,1.2),(.20,.07,.27),'core')
 elif id=='bramble':
  cone('Hollow trunk',(0,0,.8),.50,.24,1.5,'thorn',verts=8);gem('Moss shoulders',(0,.03,1.46),(.60,.38,.34),'cloth');gem('Wooden mother mask',(0,-.09,1.88),(.27,.22,.34),'thorn','head');eyes(1.95,y=-.3)
  for sign,p in [(-1,'left'),(1,'right')]:
   curve('Arched branch arm',[(sign*.3,0,1.4),(sign*.63,0,1.7),(sign*.9,-.08,1.4),(sign*.85,-.25,.9)],.08,'thorn',p)
   for j in range(4):cone('Branch thorn',(sign*(.55+j*.10),0,1.8-j*.07),.07,0,.25,'gold',p,5)
  for i in range(7):
   a=i*math.tau/7;curve('Root tentacle',[(math.cos(a)*.23,math.sin(a)*.23,.6),(math.cos(a)*.48,math.sin(a)*.48,.19),(math.cos(a)*.79,math.sin(a)*.79,.07)],.055,'thorn');gem('Cinder flower' if hell else 'Bloom petal',(math.cos(a)*.27,math.sin(a)*.27,2.2),(.15,.10,.16),'core','head')
  for i in range(8):a=i*math.tau/8;gem('Living leaf',(math.cos(a)*.50,math.sin(a)*.50,.95),(.18,.07,.27),'element')
 elif id=='regent':
  cone('Crystal royal robe',(0,0,.70),.52,.23,1.28,'white',verts=6);gem('Prismatic chest',(0,0,1.42),(.33,.24,.41),'element');gem('Glass mask',(0,0,1.97),(.22,.22,.31),'white','head');eyes(2,y=-.23);crown((0,0,2.23),.25,'core')
  for sign,p in [(-1,'left'),(1,'right')]:
   for j in range(3):gem('Ice pauldron',(sign*(.38+j*.10),.04,1.58+j*.05),(.12,.16,.27),'element',p)
   rod('Crystal arm',(sign*.48,0,1.55),(sign*.6,-.1,1.06),.09,'white',p)
  rod('Shatter scepter',(.66,-.1,.21),(.66,-.1,2.30),.025,'gold','right');gem('Scepter prism',(.66,-.1,2.21),(.15,.14,.33),'core','right')
  for i in range(6):a=i*math.tau/6;gem('Floating frost shard',(math.cos(a)*.69,math.sin(a)*.69,.65),(.07,.07,.23),'core','halo')
 elif id=='static':
  cone('Suspended vestments',(0,0,.78),.44,.25,1.05,'cloth',verts=8);box('Conductive chest',(0,0,1.47),(.49,.35,.46),'gold');gem('Saint mask',(0,0,2),(.23,.2,.29),'dark','head');eyes(2,y=-.21)
  ring('Tesla halo',(0,.10,2.05),.57,'gold','halo',True,.04)
  for i in range(8):a=i*math.tau/8;gem('Arc halo electrode',(.57*math.cos(a),.10,2.05+.57*math.sin(a)),(.07,.07,.09),'core','halo')
  for sign,p in [(-1,'left'),(1,'right')]:
   rod('Copper upper arm',(sign*.27,0,1.5),(sign*.63,0,1.16),.08,'gold',p);gem('Arc hand',(sign*.67,-.10,1.1),(.11,.13,.14),'core',p);curve('Electric braid',[(sign*.24,-.2,1.64),(sign*.15,-.24,1.4),(sign*.3,-.24,1.25),(sign*.1,-.22,.98)],.025,'core')
  for i in range(3):ring('Coil base',(0,0,.25+i*.12),.3+i*.06,'gold')
 elif id=='sun':
  gem('Crooked solar disc',(0,0,1.37),(.65,.16,.65),'gold');gem('Burning face',(0,-.19,1.37),(.45,.08,.45),'element');eyes(1.50,'body',-.28)
  curve('Crooked grin',[(-.2,-.28,1.27),(0,-.30,1.18),(.24,-.28,1.3)],.026,'dark')
  for i in range(11):
   a=i*math.tau/11;gem('Bent sun ray',(math.cos(a)*.81,0,1.37+math.sin(a)*.81),(.13,.09,.31),'core','halo').rotation_euler.y=-a
  for sign,p in [(-1,'left'),(1,'right')]:curve('Spiral limb',[(sign*.45,0,1.1),(sign*.70,0,.83),(sign*.6,-.2,.60)],.065,'gold',p)
  rod('Stilt left',(-.23,0,.94),(-.28,-.10,.15),.055,'dark');rod('Stilt right',(.23,0,.94),(.30,.03,.10),.055,'gold')
  if hell:gem('Eclipse disc',(0,-.29,1.40),(.35,.045,.35),'dark')
 elif id=='kings':
  gem('Royal singularity',(0,0,1.05),(.43,.43,.46),'dark');crown((0,0,1.58),.43,'gold','body');gem('Weight core',(0,-.42,1.06),(.20,.055,.21),'core')
  for i in range(3):
   a=i*math.tau/3;loc=(math.cos(a)*.79,math.sin(a)*.79,.83);gem('Orbiting royal mass',loc,(.20,.20,.24),'stone','halo');curve('Bound chain',[(loc[0]*t,loc[1]*t,.83+.22*math.sin(t*math.pi)) for t in [j/10 for j in range(11)]],.026,'gold','halo')
  ring('King orbit',(0,0,1.0),.87,'element','halo',width=.02)
  for sign in (-1,1):box('Floating mantle',(sign*.39,.1,.70),(.15,.23,.52),'cloth')
 elif id=='throne':
  box('Vacant royal seat',(0,0,.57),(.82,.70,.19),'dark');box('Throne back',(0,.27,1.45),(.78,.17,1.75),'stone');box('Void back inlay',(0,.16,1.55),(.54,.045,1.28),'cloth')
  for sign,p in [(-1,'left'),(1,'right')]:
   box('Armrest',(sign*.48,0,.93),(.16,.85,.14),'gold',p);box('Throne leg',(sign*.35,sign*.22,.28),(.13,.13,.56),'stone');gem('Crown finial',(sign*.40,.27,2.30),(.15,.13,.30),'gold','head')
  ring('Empty face',(0,.06,1.53),.25,'core','body',True,.026);crown((0,.10,2.35),.26,'gold')
  for i in range(phase*3):
   a=i*math.tau/(phase*3);gem('Phase fracture',(math.cos(a)*(.55+phase*.07),math.sin(a)*(.55+phase*.07),1.38+.27*math.sin(a*2)),(.045,.09,.22),'core','halo')
  if phase>=2:
   curve('Fractured seat',[(0,-.36,.60),(.12,-.39,.68),(-.08,-.38,.79),(.19,-.4,.89)],.025,'core')
  if phase==3:ring('Unbound void crown',(0,0,1.18),.94,'core','halo',width=.025);gem('Released heart',(0,-.16,1.44),(.15,.16,.23),'core')
 if hell:
  # Every Hell model changes materials AND has an additional modeled silhouette.
  for sign in (-1,1):
   o=cone('Hell crown horn',(sign*.35,.03,2.36),.12,0,.42,'gold','head',5);o.rotation_euler.y=sign*.45
  for i in range(5):a=i*math.tau/5;gem('Infernal floating cinder',(math.cos(a)*.62,math.sin(a)*.62,.35),(.045,.045,.15),'core','halo')
def animate():
 rest={k:(o.location.copy(),o.rotation_euler.copy(),o.scale.copy()) for k,o in PIV.items()};offset=0
 for pose,count,fps,loop in ANIMS:
  S.timeline_markers.new(pose,frame=offset+1)
  for i in range(count):
   t=i/(count-1);wave=math.sin(t*math.tau);hit=math.sin(t*math.pi)
   for k,o in PIV.items():o.location,o.rotation_euler,o.scale=rest[k][0].copy(),rest[k][1].copy(),rest[k][2].copy()
   PIV['body'].location.z+=.025*wave;PIV['halo'].rotation_euler.z=.08*wave
   if pose=='attack':
    # Wind-up through index 6, release at index 7: renderer aligns warning.
    drive=-.32*(i/6) if i<=6 else .35*(1-(i-7)/3)
    PIV['body'].rotation_euler.x=drive;PIV['left'].rotation_euler.x=-.95*hit;PIV['right'].rotation_euler.x=-1.10*hit;PIV['halo'].rotation_euler.z=.38*hit
   elif pose=='hurt':PIV['body'].rotation_euler.x=-.20*hit;PIV['head'].rotation_euler.x=-.13*hit
   elif pose=='death':
    ease=t*t*(3-2*t);PIV['root'].location.z=-.13*ease;PIV['body'].scale=(1-.24*ease,1-.24*ease,1-.63*ease);PIV['body'].rotation_euler.x=.30*ease;PIV['halo'].scale=(1-.65*ease,)*3
   elif pose=='stagger':PIV['body'].rotation_euler.x=.23;PIV['head'].rotation_euler.x=.22;PIV['left'].rotation_euler.x=.25;PIV['right'].rotation_euler.x=.25
   elif pose=='recovery':PIV['body'].rotation_euler.x=.23*(1-t);PIV['halo'].scale=(1+.15*hit,)*3
   for o in PIV.values():
    for prop in ('location','rotation_euler','scale'):o.keyframe_insert(data_path=prop,frame=offset+i+1)
  offset+=count
 S.frame_start=1;S.frame_end=offset;S.frame_set(1)
def frozen_bank(source,parts):
 bank=[];bpy.context.window.scene=source
 for f in range(1,41):
  source.frame_set(f);deps=bpy.context.evaluated_depsgraph_get();verts=[];faces=[];slots=[];indices=[]
  for p in parts:
   ev=p.evaluated_get(deps);m=ev.to_mesh();world=ev.matrix_world;off=len(verts);verts.extend(tuple(world@v.co) for v in m.vertices);lookup=[]
   for mat in p.data.materials:
    if mat not in slots:slots.append(mat)
    lookup.append(slots.index(mat))
   for poly in m.polygons:faces.append(tuple(off+v for v in poly.vertices));indices.append(lookup[poly.material_index])
   ev.to_mesh_clear()
  m=bpy.data.meshes.new(source.name+' pose '+str(f));m.from_pydata(verts,[],faces);m.update()
  for mat in slots:m.materials.append(mat)
  for p,idx in zip(m.polygons,indices):p.material_index=idx
  bank.append(m)
 source.frame_set(1);return bank
def render(name,source,parts,preview,supplied_bank=None):
 folder=OUT/name;folder.mkdir(exist_ok=True)
 if preview:
  source.render.resolution_x=384;source.render.resolution_y=384;source.render.filepath=str(PRE/(name+'.png'));bpy.context.window.scene=source;bpy.ops.render.render(write_still=True);return
 bank=supplied_bank if supplied_bank is not None else frozen_bank(source,parts);sheet=bpy.data.scenes.new(name+' export');sheet.world=source.world;sheet.render.engine='CYCLES';sheet.cycles.samples=6;sheet.cycles.use_denoising=True;sheet.render.threads_mode='FIXED';sheet.render.threads=4;sheet.render.film_transparent=True;sheet.render.image_settings.file_format='PNG';sheet.render.image_settings.color_mode='RGBA';sheet.view_settings.view_transform='Standard';sheet.render.resolution_x=1536;sheet.render.resolution_y=960;sheet.render.resolution_percentage=100
 camera=source.camera.copy();camera.data=source.camera.data.copy();camera.data.ortho_scale=4.2*8;sheet.collection.objects.link(camera);sheet.camera=camera
 for light in source.objects:
  if light.type=='LIGHT':sheet.collection.objects.link(light.copy())
 right=camera.rotation_euler.to_matrix()@Vector((1,0,0));up=camera.rotation_euler.to_matrix()@Vector((0,1,0));roots=[]
 for i,m in enumerate(bank):
  root=bpy.data.objects.new('Cell '+str(i),None);sheet.collection.objects.link(root);root.location=right*((i%8+.5-4)*4.2)+up*((2.5-i//8-.5)*4.2);roots.append(root);o=bpy.data.objects.new('Frozen pose',m);sheet.collection.objects.link(o);o.parent=root
 bpy.context.window.scene=sheet
 for d in range(8):
  for r in roots:r.rotation_euler.z=d*math.pi/4
  sheet.render.filepath=str(folder/('boss_y%03d.png'%(d*45)));bpy.ops.render.render(write_still=True)
  subprocess.run(['magick',sheet.render.filepath,'-background','none','-alpha','background','-define','png:compression-level=9',sheet.render.filepath],check=True)
  print('BOSS_DIRECTION_DONE',name,d,flush=True)
 subprocess.run(['magick',str(folder/'boss_y000.png'),'-crop','192x192+0+0','+repage',str(folder/'portrait.png')],check=True)
 bpy.context.window.scene=source
 for o in list(sheet.objects):bpy.data.objects.remove(o,do_unlink=True)
 bpy.data.scenes.remove(sheet)
 for m in bank:bpy.data.meshes.remove(m)
 print('BOSS_DONE',name,flush=True)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--ids',nargs='+');parser.add_argument('--preview',action='store_true');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
 names=['bailiff_hell']+IDS+[i+'_hell' for i in IDS]+['throne_phase2','throne_phase3','throne_hell_phase2','throne_hell_phase3']
 selected=args.ids or names;models={}
 for name in selected:
  id=name.split('_')[0];hell='hell' in name;phase=3 if 'phase3' in name else 2 if 'phase2' in name else 1
  if id=='bailiff':
   # Preserve the approved Bailiff source and rig; give Hell its own armor/attachments.
   bpy.ops.wm.open_mainfile(filepath=str(ROOT/'art-src/blender/bailiff-isometric.blend'));source=bpy.context.scene;source.name=name
   for m in bpy.data.materials:
    if not m.use_nodes:continue
    n=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if n:
     c=n.inputs['Base Color'].default_value
     if max(c[:3])>.2:n.inputs['Base Color'].default_value=(c[0]*.6,c[1]*.18,c[2]*.35,1)
   source.render.resolution_x=256;source.render.resolution_y=256
   # Bake existing actions into the shared 40-frame clip layout.
   rig=bpy.data.objects['BailiffRig'];parts=[o for o in source.objects if o.type=='MESH' and not o.hide_render and len(o.data.materials)];bank=[]
   for pose,count,_,_ in ANIMS:
    action='Refined_'+({'stagger':'Hurt','recovery':'Idle'}.get(pose,pose.title()));rig.animation_data.action=bpy.data.actions[action]
    for f in range(1,count+1):
     source.frame_set(f);deps=bpy.context.evaluated_depsgraph_get();vs=[];fs=[];slots=[];mi=[]
     for p in parts:
      ev=p.evaluated_get(deps);mesh=ev.to_mesh();off=len(vs);vs.extend(tuple(ev.matrix_world@v.co) for v in mesh.vertices);lookup=[]
      for mat in p.data.materials:
       if mat not in slots:slots.append(mat)
       lookup.append(slots.index(mat))
      for poly in mesh.polygons:fs.append(tuple(off+v for v in poly.vertices));mi.append(lookup[poly.material_index])
      ev.to_mesh_clear()
     mesh=bpy.data.meshes.new('Infernal pose');mesh.from_pydata(vs,[],fs);mesh.update()
     for mat in slots:mesh.materials.append(mat)
     for poly,idx in zip(mesh.polygons,mi):poly.material_index=idx
     bank.append(mesh)
   # Build a source scene with shape-key poses, leaving the old .blend untouched.
   setup(name,id,True);o=bpy.data.objects.new('Infernal Bailiff armor',bank[0]);S.collection.objects.link(o);PARTS.append(o);o.shape_key_add(name='Basis')
   for i,m in enumerate(bank):
    key=o.shape_key_add(name='Pose '+str(i))
    for v,co in zip(key.data,m.vertices):v.co=co.co
    key.value=0;key.keyframe_insert(data_path='value',frame=max(0,i));key.value=1;key.keyframe_insert(data_path='value',frame=i+1);key.value=0;key.keyframe_insert(data_path='value',frame=i+2)
   # Original rig is retained in the saved source, plus the export pose bank.
   for sign in (-1,1):cone('Infernal shoulder spike',(sign*.42,0,1.98),.1,0,.38,'gold','body',5)
   animate()
   extra=frozen_bank(S,PARTS[1:])
   for base,spikes in zip(bank,extra):
    # Join modeled shoulder spikes into the evaluated armor pose.
    verts=[tuple(v.co) for v in base.vertices]+[tuple(v.co) for v in spikes.vertices];off=len(base.vertices);faces=[tuple(p.vertices) for p in base.polygons]+[tuple(off+v for v in p.vertices) for p in spikes.polygons]
    merged=bpy.data.meshes.new('Infernal armor with horns');merged.from_pydata(verts,[],faces);merged.update()
    for mat in list(base.materials)+list(spikes.materials):merged.materials.append(mat)
    for poly,old in zip(merged.polygons,list(base.polygons)+list(spikes.polygons)):poly.material_index=old.material_index+(len(base.materials) if poly.index>=len(base.polygons) else 0)
    bank[bank.index(base)]=merged
   models[name]=(S,list(PARTS),bank)
  else:setup(name,id,hell);build(id,hell,phase);animate();models[name]=(S,list(PARTS),None)
  print('BOSS_MODEL_DONE',name,len(PARTS),flush=True)
 source=ROOT/'art-src/blender'/('bosses-complete.blend' if not args.ids else 'bosses-'+'-'.join(selected)+'.blend');source.parent.mkdir(parents=True,exist_ok=True);bpy.context.window.scene=models[selected[0]][0];bpy.ops.wm.save_as_mainfile(filepath=str(source))
 for name,(s,parts,bank) in models.items():
  render(name,s,parts,args.preview,bank);(ROOT/'art-src/boss-render-progress.json').write_text(json.dumps({'boss':name,'completed':selected.index(name)+1,'total':len(selected)}))
 meta={'width':192,'height':192,'columns':8,'rows':5,'anchor_x':96,'anchor_y':146,'scale':.85,'bosses':names,'directions':list(range(0,360,45)),'animations':{}};offset=0
 for pose,count,fps,loop in ANIMS:meta['animations'][pose]={'offset':offset,'frames':count,'fps':fps,'loop':loop};offset+=count
 (OUT/'bosses.json').write_text(json.dumps(meta,indent=2)+'\n')
 print('BOSS_LIBRARY_DONE',flush=True)
if __name__=='__main__':main()
