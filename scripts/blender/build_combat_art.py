"""Dedicated animated visual vocabulary. Original keyed Blender geometry.
blender -b -t 4 -P scripts/blender/build_combat_art.py [-- --ids hit critical]
Exports eight-frame transparent sheets, and editable per-effect scenes.
"""
import bpy, math, pathlib, json, sys, argparse, subprocess
from mathutils import Vector
R=pathlib.Path(__file__).resolve().parents[2];OUT=R/'assets/effects/combat';OUT.mkdir(parents=True,exist_ok=True)
C={'neutral':(.96,.79,.45),'pyro':(1,.24,.035),'hydro':(.06,.57,1),'anemo':(.1,.8,.52),'geo':(.83,.51,.11),'dendro':(.27,.65,.04),'cryo':(.27,.77,1),'electro':(.6,.18,1),'gravity':(.43,.17,.83),'antimatter':(.96,.08,.42),'red':(1,.13,.13),'shield':(.14,.72,.94),'heal':(.3,.95,.48)}
# id -> geometry family, palette, duration, loop. Field skills retain unique shapes.
SPECS={}
def add(id,family,color='neutral',duration=.48,loop=False):SPECS[id]={'family':family,'color':color,'duration':duration,'loop':loop}
for id,fam,col in [('slash','slash','neutral'),('projectile','lance','neutral'),('muzzle','burst','neutral'),('trail','gust','neutral'),('hit','burst','neutral'),('critical','critical','neutral'),('hurt','critical','red'),('shield_create','shield','shield'),('shield_absorb','shield','shield'),('shield_break','shatter','shield'),('slam','slam','geo'),('dust','steam','geo'),('dot','tick','neutral'),('dodge','gust','shield'),('switch_out','collapse','shield'),('switch_in','orbit','shield'),('reload_start','reload','neutral'),('reload_complete','reload','heal'),('phase','orbit','antimatter'),('stagger','binding','neutral'),('recovery','orbit','neutral'),('defeat','shatter','antimatter'),('heal','heal','heal'),('cooldown','orbit','anemo')]:add(id,fam,col,.7 if id in ('phase','defeat','slam') else .48)
SKILLS={'jack':('fan','pyro'),'match':('ring','pyro'),'penny':('lance','hydro'),'dealer':('wave','hydro'),'gale':('gust','anemo'),'zephyr':('cyclone','anemo'),'flint':('slam','geo'),'mason':('eruption','geo'),'clover':('thorns','dendro'),'briar':('bramble','dendro'),'frost':('fan','cryo'),'whiteout':('frost','cryo'),'volt':('lightning','electro'),'count':('marks','electro'),'crown':('collapse','gravity'),'oracle':('orbit','gravity'),'null':('lance','antimatter'),'laugh':('detonation','antimatter')}
for id,(fam,col) in SKILLS.items():add('skill_'+id,fam,col,.65,True)
REACTIONS={'steam_burst':('steam','hydro'),'thaw':('shatter','pyro'),'frostbind':('binding','cryo'),'live_wire':('lightning','electro'),'flashover':('critical','pyro'),'kindling':('flame','pyro'),'bloom':('bloom','dendro'),'overgrowth':('bramble','dendro'),'crosswind':('cyclone','anemo'),'gilded_guard':('shield','geo'),'collapse':('collapse','gravity'),'annihilation':('shatter','antimatter'),'event_horizon':('horizon','antimatter')}
for id,(fam,col) in REACTIONS.items():add('reaction_'+id,fam,col,.8)
for col in ('pyro','hydro','anemo','geo','dendro','cryo','electro','gravity','antimatter'):add('aura_'+col,'orbit',col,1.2,True)
for id,fam,col in [('burn','flame','pyro'),('electric','lightning','electro'),('vulnerable','bramble','dendro'),('shield','shield','shield'),('stagger','binding','cryo'),('bloom','bloom','dendro')]:add('status_'+id,fam,col,1.2,True)
for id,fam,col in [('flame','flame','pyro'),('water','wave','hydro'),('wind','gust','anemo'),('pillar','pillar','geo'),('rock','slam','geo'),('bramble','bramble','dendro'),('ignition','flame','pyro'),('ice','frost','cryo'),('shatter','shatter','cryo'),('grid','lightning','electro'),('strike','marks','electro'),('spiral','cyclone','pyro'),('pull','collapse','gravity'),('push','orbit','gravity'),('mass','slam','gravity'),('void','detonation','antimatter'),('wave_void','wave','antimatter'),('zone','horizon','antimatter')]:add('hazard_'+id,fam,col,.8,True)
for id,fam,col in [('flask','heal','heal'),('aegis','shield','shield'),('wind','orbit','anemo')]:add('consume_'+id,fam,col,.65)
S=None;PARTS=[];M={}
def mat(name,col,glow=.7):
 m=bpy.data.materials.new(name);m.use_nodes=True;n=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');n.inputs['Base Color'].default_value=(*col,1);n.inputs['Roughness'].default_value=.4;n.inputs['Emission Color'].default_value=(*col,1);n.inputs['Emission Strength'].default_value=glow;return m
def remember(o,key='color',mode='expand',phase=0):
 o.data.materials.append(M[key]);PARTS.append((o,mode,phase));return o
def gem(name,loc,scale,key='color',mode='expand',phase=0,cone=False):
 if cone:bpy.ops.mesh.primitive_cone_add(vertices=5,radius1=1,radius2=0,depth=2,location=loc)
 else:bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=loc)
 o=bpy.context.object;o.name=name;o.scale=scale;return remember(o,key,mode,phase)
def line(name,pts,width=.025,key='color',mode='pulse',phase=0):
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=width;c.bevel_resolution=1;sp=c.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(name,c);S.collection.objects.link(o);return remember(o,key,mode,phase)
def ring(radius,z=0,key='color',mode='expand',start=0,end=math.tau):return line('Energy ribbon',[(math.cos(a)*radius,math.sin(a)*radius,z) for a in [start+(end-start)*i/40 for i in range(41)]],.035,key,mode)
def build(family):
 if family=='pillar':
  for i in range(5):
   a=i*math.tau/5;gem('Standing basalt column',(math.cos(a)*.35,math.sin(a)*.35,.32),(.23,.23,.65),'color','grow',a)
  for i in range(4):a=i*math.pi/2;line('Glowing pillar seam',[(math.cos(a)*.32,math.sin(a)*.32,.04),(math.cos(a)*.32,math.sin(a)*.32,.75)],.025,'core','grow')
  ring(.70,mode='grow')
 elif family in ('burst','critical','tick','shatter','slam','eruption','detonation'):
  n=16 if family in ('critical','shatter','detonation') else 8
  for i in range(n):
   a=i*math.tau/n;r=.4 if family=='tick' else .95;loc=(math.cos(a)*r,math.sin(a)*r,.1+(i%3)*.08)
   size=(.12,.06,.23) if family=='shatter' else (.085,.085,.11)
   if family in ('slam','eruption'):size=(.17,.17,.45 if family=='eruption' else .16)
   o=gem('Radiating impact shard',loc,size,'core' if i%3==0 else 'color','expand',a,True);o.rotation_euler.y=.7
   if family in ('critical','burst'):line('Impact streak',[(loc[0]*.5,loc[1]*.5,.08),(loc[0]*1.4,loc[1]*1.4,.08)],.032,'core','expand')
  if family in ('slam','eruption'):
   for i in range(6):a=i*math.tau/6;line('Ground fault',[(0,0,.015),(math.cos(a)*.45,math.sin(a)*.45,.015),(math.cos(a+.2)*.98,math.sin(a+.2)*.98,.015)],.018,'dark','pulse')
  ring(.68,key='core');ring(1.12,key='color')
 elif family in ('slash','lance','gust','fan','wave'):
  if family=='slash':
   for j in range(3):line('Sweeping blade arc',[(math.cos(a)*(1.1+j*.12),math.sin(a)*(1.1+j*.12),.15+j*.035) for a in [-1.1+i*2.2/28 for i in range(29)]],.035 if j==0 else .015,'core' if j==0 else 'color','sweep')
  elif family=='wave':
   for j in range(4):ring(.65+j*.16,z=.04+j*.10,start=-.2,end=math.pi+.2,key='core' if j==0 else 'color',mode='expand')
  elif family=='fan':
   for j in range(-2,3):a=j*.24;line('Fan ray',[(math.cos(a)*r,math.sin(a)*r,.08) for r in (.16,.48,1.15)],.035,'color','expand');gem('Fan spark',(math.cos(a)*1.15,math.sin(a)*1.15,.1),(.10,.07,.18),'core','expand')
  else:
   for j in range(3):line('Travel ribbon',[(-1.4+i*.13,(j-1)*.12,.08+.07*math.sin(i*.5+j)) for i in range(22)],.026 if j==1 else .012,'core' if j==1 else 'color','travel',j)
   gem('Projectile point',(1.18,0,.09),(.31,.09,.10),'core','pulse')
 elif family in ('cyclone','orbit','collapse','horizon','ring','reload'):
  for k in range(3 if family!='horizon' else 5):
   r=.62+k*.18
   if family=='cyclone':line('Cyclone helix',[(math.cos(a)*(.4+i*.025),math.sin(a)*(.4+i*.025),i*.017) for i,a in enumerate([k+i*math.tau/36 for i in range(37)])],.03,'color','spin')
   else:ring(r,z=k*.025,key='core' if k==0 else 'color',mode='contract' if family in ('collapse','horizon') else 'spin')
  if family in ('collapse','horizon'):gem('Singularity',(0,0,.10),(.24,.24,.15),'dark','pulse')
  for i in range(6):a=i*math.tau/6;gem('Orbital satellite',(math.cos(a)*1.13,math.sin(a)*1.13,.05),(.085,.085,.085),'core','spin',a)
 elif family in ('thorns','bramble','bloom','binding','frost','shield'):
  if family=='shield':
   # Upright shield shell, open interior: character remains visible.
   line('Shield outline',[(-.62,0,.62),(.62,0,.62),(.55,0,-.24),(0,0,-.74),(-.55,0,-.24),(-.62,0,.62)],.065,'core','pulse');ring(.92,mode='pulse')
  else:
   for i in range(6):
    a=i*math.tau/6;loc=(math.cos(a)*.70,math.sin(a)*.70,.04)
    if family=='bloom':gem('Seed bud',loc,(.16,.14,.24),'color','grow',a);gem('Bud centre',(0,0,.18),(.27,.27,.34),'core','grow')
    elif family in ('frost','binding'):gem('Ice binding shard',loc,(.12,.12,.44),'core' if i%2 else 'color','grow',a,True);line('Snowflake vein',[(loc[0]*.20,loc[1]*.20,.04),(loc[0]*1.4,loc[1]*1.4,.04)],.024,'color','grow')
    else:
     line('Thorn growth',[(loc[0]*.3,loc[1]*.3,.01),(loc[0],loc[1],.10),(loc[0]*1.3,loc[1]*1.3,.35)],.045,'color','grow');gem('Thorn',loc,(.08,.08,.25),'core','grow',a,True)
   ring(.9,mode='grow')
  if family=='bloom':
   for i in range(12):
    a=i*math.tau/12;gem('Bloom pollen burst',(math.cos(a)*.95,math.sin(a)*.95,.08),(.085,.085,.12),'core','bloom',a,True)
 elif family in ('lightning','marks'):
  for j in range(3):
   pts=[]
   for i in range(9):pts.append(((i-4)*.26,(.13 if i%2 else -.13)+(j-1)*.31,.10))
   line('Jagged arc',pts,.032,'core' if j==1 else 'color','flicker',j)
  if family=='marks':ring(.94,mode='grow');line('Target lightning',[(0,0,1.1),(-.18,0,.5),(.15,0,.5),(0,0,.05)],.065,'core','grow')
 elif family in ('steam','flame','heal'):
  for i in range(12):
   a=i*math.tau/12;loc=(math.cos(a)*.48,math.sin(a)*.48,.05)
   if family=='heal':line('Healing cross',[(loc[0]-.12,loc[1],.18),(loc[0]+.12,loc[1],.18)],.038,'core','rise',a);line('Healing cross',[(loc[0],loc[1],.06),(loc[0],loc[1],.30)],.038,'core','rise',a)
   elif family=='steam':gem('Steam puff',loc,(.18,.18,.22),'core','rise',a)
   else:gem('Flame tongue',loc,(.13,.11,.36),'core' if i%3==0 else 'color','rise',a,True)
  ring(.72,mode='grow')
 else:raise ValueError(family)
def animate(spec):
 for o,mode,phase in PARTS:
  loc=o.location.copy();scale=o.scale.copy();rot=o.rotation_euler.copy()
  for i in range(8):
   t=i/7;strength=.2+.8*math.sin(math.pi*(.12+.80*t));o.location=loc.copy();o.scale=scale.copy();o.rotation_euler=rot.copy()
   if mode=='expand':o.location.x*=.35+t*.95;o.location.y*=.35+t*.95;o.scale*=strength*(1-.48*t)
   elif mode=='contract':o.scale*=1.15-.72*t
   elif mode=='spin':o.rotation_euler.z+=t*1.0;o.scale*=.85+.13*math.sin(t*math.tau)
   elif mode=='grow':
    o.scale*=.2+.8*math.sin(math.pi*t*.80)
    if spec['family']=='bloom' and t>.6:o.scale*=1-.95*(t-.6)/.4
   elif mode=='bloom':
    u=max(0,(t-.55)/.45);o.location.x*=.25+u;o.location.y*=.25+u;o.scale*=max(.0001,math.sin(math.pi*u*.85))
   elif mode=='rise':o.location.z+=.5*t;o.scale*=strength*(1-.5*t);o.location.x+=.06*math.sin(t*5+phase)
   elif mode=='travel':o.location.x+=.06*math.sin(t*math.tau+phase);o.scale*=.78+.18*math.sin(t*math.pi)
   elif mode=='flicker':o.scale*=.45+(.5 if i%3 else .15);o.location.z+=.01*i
   elif mode=='sweep':o.rotation_euler.z+=-.50+t*.85;o.scale*=strength
   else:o.scale*=strength
   for prop in ('location','rotation_euler','scale'):o.keyframe_insert(data_path=prop,frame=i+1)
 S.frame_start=1;S.frame_end=8;S.render.fps=round(8/spec['duration']);S.frame_set(1)
def scene(id,spec):
 global S,PARTS,M
 PARTS=[];S=bpy.data.scenes.new(id);bpy.context.window.scene=S;S.render.engine='CYCLES';S.cycles.samples=4;S.cycles.use_denoising=True;S.render.threads_mode='FIXED';S.render.threads=4;S.render.film_transparent=True;S.render.image_settings.file_format='PNG';S.render.image_settings.color_mode='RGBA';S.render.resolution_percentage=100;S.view_settings.view_transform='Standard'
 S.world=bpy.data.worlds.new(id+' world');S.world.use_nodes=True;bg=next(n for n in S.world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs[0].default_value=(.3,.3,.3,1);bg.inputs[1].default_value=.7
 col=C[spec['color']];M={'color':mat(id+' energy',col),'core':mat(id+' core',tuple(.35+.65*c for c in col),.6),'dark':mat(id+' fault',tuple(c*.25 for c in col),.1)}
 cam=bpy.data.objects.new('Effect camera',bpy.data.cameras.new(id+' camera'));S.collection.objects.link(cam);cam.data.type='ORTHO';cam.data.ortho_scale=4.2;cam.location=(0,-8,5);cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler();S.camera=cam
 d=bpy.data.lights.new('Softbox','SUN');d.energy=1.3;o=bpy.data.objects.new('Softbox',d);S.collection.objects.link(o);o.rotation_euler=(.4,-.3,-.5)
 build(spec['family']);animate(spec);S['effect_id']=id;S['duration']=spec['duration'];S['loop']=spec['loop'];return S,list(PARTS)
def render(id,source,parts):
 # Snapshot into 4x2 cells. All lighting is directional to keep cells identical.
 sh=bpy.data.scenes.new(id+' export');sh.world=source.world;sh.render.engine='CYCLES';sh.cycles.samples=4;sh.cycles.use_denoising=True;sh.render.threads_mode='FIXED';sh.render.threads=4;sh.render.film_transparent=True;sh.render.image_settings.file_format='PNG';sh.render.image_settings.color_mode='RGBA';sh.view_settings.view_transform='Standard';sh.render.resolution_x=512;sh.render.resolution_y=256;sh.render.resolution_percentage=100
 cam=source.camera.copy();cam.data=source.camera.data.copy();cam.data.ortho_scale=4.2*4;sh.collection.objects.link(cam);sh.camera=cam
 for l in source.objects:
  if l.type=='LIGHT':sh.collection.objects.link(l.copy())
 right=cam.rotation_euler.to_matrix()@Vector((1,0,0));up=cam.rotation_euler.to_matrix()@Vector((0,1,0));meshes=[]
 for f in range(8):
  bpy.context.window.scene=source;source.frame_set(f+1);deps=bpy.context.evaluated_depsgraph_get();shift=right*((f%4+.5-2)*4.2)+up*((1-f//4-.5)*4.2)
  for p,_,_ in parts:
   ev=p.evaluated_get(deps);mesh=bpy.data.meshes.new_from_object(ev);meshes.append(mesh);o=bpy.data.objects.new('Effect cell '+str(f),mesh);sh.collection.objects.link(o);o.matrix_world=ev.matrix_world.copy();o.location+=shift
 bpy.context.window.scene=sh;sh.render.filepath=str(OUT/(id+'.png'));bpy.ops.render.render(write_still=True)
 subprocess.run(['magick',sh.render.filepath,'-background','none','-alpha','background','-define','png:compression-level=9',sh.render.filepath],check=True)
 bpy.context.window.scene=source
 for o in list(sh.objects):bpy.data.objects.remove(o,do_unlink=True)
 bpy.data.scenes.remove(sh)
 for m in meshes:bpy.data.meshes.remove(m)
 print('EFFECT_DONE',id,flush=True)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--ids',nargs='+');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []);ids=args.ids or list(SPECS);models={}
 for id in ids:models[id]=scene(id,SPECS[id])
 source=R/'art-src/blender'/('combat-effects.blend' if not args.ids else 'combat-effects-'+'-'.join(ids)+'.blend');bpy.context.window.scene=models[ids[0]][0];bpy.ops.wm.save_as_mainfile(filepath=str(source))
 for id,(s,parts) in models.items():render(id,s,parts);(R/'art-src/combat-art-progress.json').write_text(json.dumps({'effect':id,'completed':ids.index(id)+1,'total':len(ids)}))
 (OUT/'combat.json').write_text(json.dumps({'width':128,'height':128,'columns':4,'rows':2,'frames':8,'anchor':[64,64],'effects':SPECS,'source':'art-src/blender/combat-effects.blend'},indent=2)+'\n')
 lines=['-- Generated by scripts/blender/build_combat_art.py.','return {']
 for id,spec in SPECS.items():lines.append("  ['%s'] = { duration = %s, loop = %s },"%(id,spec['duration'],str(spec['loop']).lower()))
 lines.append('}');(R/'src/data/combat_art.lua').write_text('\n'.join(lines)+'\n');print('COMBAT_ART_DONE',len(SPECS),flush=True)
if __name__=='__main__':main()
