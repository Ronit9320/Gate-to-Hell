"""Decorative boss scenery and screen illustrations, rendered from original meshes."""
import bpy, pathlib, sys, math, subprocess
sys.path.insert(0,str(pathlib.Path(__file__).parent));import build_missing_bosses as B
R=B.ROOT;OUT=R/'assets/scenery';OUT.mkdir(exist_ok=True)
models={}
for id in ['bailiff']+B.IDS:
 B.setup('Scenery '+id,id,False)
 B.box('Stone display plinth',(0,0,.12),(1.4,1,.22),'stone')
 if id=='bailiff':
  B.cone('Brazier bowl',(0,0,.48),.28,.42,.35,'gold');B.gem('Brazier flame',(0,0,.88),(.24,.24,.5),'core');B.rod('Pedestal',(0,0,.2),(0,0,.6),.13,'dark')
 elif id=='undertow':
  for sign in (-1,1):B.rod('Flooded arch pillar',(sign*.46,0,.2),(sign*.46,0,1.5),.08,'gold')
  B.curve('Tidal arch',[(.46*math.cos(a),0,1.5+.4*math.sin(a)) for a in [i*math.pi/20 for i in range(21)]],.065,'element');B.ring('Water basin',(0,0,.25),.52,'core')
 elif id=='kite':
  B.rod('Wind vane mast',(0,0,.2),(0,0,1.5),.05,'gold');B.gem('Directional pennant',(.33,0,1.4),(.45,.07,.16),'element');B.ring('Windmill hub',(0,0,1.16),.33,'gold',vertical=True)
 elif id=='bedrock':
  for i in range(3):B.box('Rune monolith',((i-1)*.36,0,.6+i*.13),(.26,.35,.9+i*.22),'stone');B.gem('Rune seam',((i-1)*.36,-.2,.8+i*.16),(.025,.02,.24),'core')
 elif id=='bramble':
  for i in range(5):a=i*math.tau/5;B.curve('Garden trellis',[(math.cos(a)*.4,math.sin(a)*.4,.2),(math.cos(a)*.5,math.sin(a)*.5,.8),(math.cos(a)*.3,math.sin(a)*.3,1.4)],.045,'thorn');B.gem('Garden flower',(math.cos(a)*.3,math.sin(a)*.3,1.4),(.12,.10,.15),'element')
 elif id=='regent':
  for i in range(5):a=i*math.tau/5;B.gem('Crystal outcrop',(math.cos(a)*.33,math.sin(a)*.33,.72),(.16,.16,.65),'element');B.ring('Frozen seal',(0,0,.25),.5,'white')
 elif id=='static':
  B.rod('Tesla tower',(0,0,.2),(0,0,1.42),.08,'gold')
  for i in range(4):B.ring('Copper coil',(0,0,.55+i*.18),.30,'gold')
  B.gem('Charged terminal',(0,0,1.48),(.25,.25,.16),'core')
 elif id=='sun':
  B.rod('Sun dial gnomon',(0,0,.2),(.25,0,1.4),.06,'gold');B.ring('Sun dial',(0,0,.26),.6,'element')
  for i in range(8):a=i*math.pi/4;B.gem('Dial hour',(math.cos(a)*.56,math.sin(a)*.56,.28),(.07,.07,.10),'gold')
 elif id=='kings':
  B.gem('Floating weight',(0,0,.93),(.38,.38,.38),'stone');B.ring('Gravity apparatus',(0,0,.35),.58,'core');B.crown((0,0,1.3),.27,'gold','body')
 else:
  for sign in (-1,1):B.box('Broken portal post',(sign*.4,0,.8),(.18,.28,1.4),'stone');B.gem('Portal fracture',(sign*.3,-.12,1.0),(.07,.05,.24),'core')
  B.box('Portal lintel',(0,0,1.54),(1.05,.3,.18),'gold');B.ring('Void aperture',(0,0,.92),.35,'core',vertical=True)
 models['prop_'+id]=B.S
for id,element in [('reward','geo'),('victory','gravity'),('defeat','antimatter'),('hell_entry','pyro')]:
 B.setup('Screen illustration '+id,'kings' if element=='gravity' else 'throne' if element=='antimatter' else 'bailiff',False)
 if id=='reward':
  B.box('Reward chest',(0,0,.66),(1.20,.68,.70),'gold');B.box('Chest lid',(0,0,1.10),(1.28,.75,.22),'dark');B.box('Chest clasp',(0,-.39,.85),(.18,.08,.40),'core')
  for i in range(8):B.gem('Winning coin',((i%4-1.5)*.28,-.32-(i//4)*.25,.21),(.15,.04,.15),'gold')
 elif id=='victory':
  for sign in (-1,1):B.box('Infinity gate',(sign*.7,0,1.02),(.22,.4,1.9),'gold')
  B.box('Gate arch',(0,0,2.04),(1.7,.42,.25),'gold')
  for sign in (-1,1):B.ring('Infinity key loop',(sign*.19,-.15,1.4),.25,'core',vertical=True)
  B.rod('Infinity key stem',(0,-.15,.30),(0,-.15,1.10),.055,'gold');B.rod('Infinity key tooth',(0,-.15,.42),(.3,-.15,.42),.055,'gold')
 elif id=='defeat':
  B.box('Cracked table',(0,0,.22),(1.6,1.1,.22),'stone');B.crown((0,0,.52),.50,'gold','body');B.gem('Broken crown jewel',(.65,-.38,.36),(.16,.12,.16),'core');B.curve('Crack',[(-.7,-.2,.35),(-.3,.1,.35),(0,-.2,.35),(.7,.3,.35)],.025,'core')
 else:
  for sign in (-1,1):B.box('Infernal doorway',(sign*.62,0,1.03),(.27,.45,2.0),'dark');B.cone('Doorway horn',(sign*.62,0,2.12),.16,0,.45,'gold')
  B.box('Infernal arch',(0,0,1.9),(1.6,.4,.25),'gold');B.gem('Opening ember',(0,.04,1.0),(.38,.13,.65),'core');B.curve('Broken chain',[(-.5,-.25,1.25),(-.20,-.27,.8),(.08,-.27,1.0),(.52,-.25,1.4)],.045,'gold')
 models[id]=B.S
bpy.context.window.scene=models['prop_bailiff'];source=R/'art-src/blender/scenery-and-illustrations.blend';bpy.ops.wm.save_as_mainfile(filepath=str(source))
for id,s in models.items():
 bpy.context.window.scene=s;s.render.resolution_x=256;s.render.resolution_y=256;s.cycles.samples=12;s.render.filepath=str(OUT/(id+'.png'));bpy.ops.render.render(write_still=True);subprocess.run(['magick',s.render.filepath,'-background','none','-alpha','background','-define','png:compression-level=9',s.render.filepath],check=True);print('SCENERY_DONE',id,flush=True)
