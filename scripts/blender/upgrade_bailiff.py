"""Detailed first-boss art pass. Run with bailiff-isometric.blend as input."""
import bpy, math, pathlib, subprocess
from mathutils import Vector
ROOT = pathlib.Path(__file__).resolve().parents[2]
# Reuse the proven rigid skinning helpers, without rebuilding the base model.
source = (ROOT/'scripts/blender/build_bailiff.py').read_text()
exec(source[:source.index('# Layered cuirass')])
collection.name = 'Ash Bailiff — executioner detail'

def textured(mat, color, metal, rough):
    p = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value = (*color, 1)
    p.inputs['Metallic'].default_value = metal
    p.inputs['Roughness'].default_value = rough
    noise = mat.node_tree.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 85
    bump = mat.node_tree.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = .22
    bump.inputs['Distance'].default_value = .025
    mat.node_tree.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    mat.node_tree.links.new(bump.outputs['Normal'], p.inputs['Normal'])

for m in bpy.data.materials:
    if m.name == 'Refined | charcoal steel': textured(m, (.065,.075,.085), .82, .39)
    if m.name == 'Refined | worn bronze': textured(m, (.32,.19,.075), .72, .44)
textured(armor, (.06,.07,.08), .8, .38)
textured(edge, (.34,.20,.08), .72, .4)
ash = material('Executioner | exposed edge', (.38,.40,.39), .8, .42)
leather = material('Executioner | haft leather', (.065,.027,.014), 0, .9)
# Hide the old glowing abdomen strips: concentrate heat in the furnace.
for o in bpy.data.objects:
    if o.name.startswith('Abdominal ember seam'): o.hide_render = True

# Iron furnace grate over the glowing chest seal.
for x in [-.085,-.042,0,.042,.085]:
    link('Furnace cast iron grate', (x,-.395,1.39), (x,-.395,1.59), .013, armor, 'chest')
for x in [-.21,.21]:
    for z in [1.4,1.62]: ball('Cuirass hammered rivet',(x,-.274,z),(.016,.012,.016),edge,'chest')
for sign,side in [(-1,'R'),(1,'L')]:
    for j in range(3):
        x=sign*(.34+j*.052);z=1.73-j*.08
        for dx in [-.10,.10]:ball('Shoulder fastening',(x+dx,-.19,z),(.014,.012,.014),edge,'upper_arm.'+side)
        link('Shoulder chipped edge',(x-.10,-.186,z+.046),(x+.08,-.186,z+.046),.008,ash,'upper_arm.'+side)
    for k in range(4):
        x=sign*.46+(k-1.5)*.035
        box('Articulated knuckle',(x,-.13,.875),(.029,.046,.067),steel,'hand.'+side,.008)
    # Fine scoring in the plates, subdued enough to survive downsampling.
    for j in range(3):
        x=sign*.46+j*.018
        link('Gauntlet battle scoring',(x,-.149,1.18+j*.025),(x+.035,-.149,1.24+j*.025),.004,ash,'forearm.'+side)
    for j in range(5):
        x=sign*(.10+j*.023)
        link('Mask iron teeth',(x,-.219,1.96),(x*.8,-.22,1.89),.009,steel,'head')

# Draped back mantle, alternating broad folds and jagged singed hem.
verts=[];n=18
for row in range(4):
    for j in range(n+1):
        u=j/n;a=math.pi*.10+u*math.pi*.8
        width=[.30,.36,.40,.44][row]
        z=[1.8,1.27,.72,.22][row]
        if row==3:z+=.055*math.sin(j*2.4)
        verts.append((math.cos(a)*width, .12+math.sin(a)*(.15+row*.025)+.025*math.cos(j*math.pi),z))
faces=[(r*(n+1)+j,r*(n+1)+j+1,(r+1)*(n+1)+j+1,(r+1)*(n+1)+j) for r in range(3) for j in range(n)]
cape=mesh('Scorched execution mantle',verts,faces,cloth,'hips')
solid=cape.modifiers.new('Mantle thickness','SOLIDIFY');solid.thickness=.012
# Chains draped across the back, individual interlocked links.
for j in range(17):
    x=-.25+j*.031;z=1.63-.15*math.sin(j/16*math.pi)
    bpy.ops.mesh.primitive_torus_add(major_segments=12,minor_segments=6,major_radius=.024,minor_radius=.005,location=(x,.34,z),rotation=(math.pi/2,0,j%2*math.pi/2))
    o=bpy.context.object;o.name='Office chain link';attach(o,edge,'chest')
plate('Back stamped debt seal',0,.39,1.32,.16,.23,.024,edge,'chest')

# Execution hammer attached in the right hand's rest space.
# Head remains compact enough to fit every direction and attack pose.
x=-.49;y=-.09
link('Execution hammer haft',(x,y,.30),(x,y,1.18),.035,leather,'hand.R')
for z in [.35,.42,.49,.56,.63,.70,.77,.84]:
    link('Haft brass wrap',(x-.038,y,z),(x+.038,y,z+.02),.009,edge,'hand.R')
box('Execution hammer forged head',(x,y,1.18),(.46,.25,.28),armor,'hand.R',.04)
for hx in [x-.19,x+.19]:
    box('Hammer reinforcing band',(hx,y,1.18),(.046,.27,.30),edge,'hand.R',.012)
box('Hammer molten striking face',(x-.242,y,1.18),(.014,.18,.19),ember,'hand.R',.005)
for z in [1.13,1.19,1.25]:
    link('Hammer face grille',(x-.255,y-.07,z),(x-.255,y+.07,z),.009,steel,'hand.R')
for hx in [x-.19,x+.19]:
    for z in [1.1,1.25]:ball('Hammer peened bolt',(hx,y-.145,z),(.015,.012,.015),ash,'hand.R')

rig.animation_data_create();rig.animation_data.action=bpy.data.actions['Refined_Idle']
scene.frame_set(1)
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=4
scene['art_direction']='ART_DIRECTION.md — Ash Bailiff first review'
scene['revision']='Executioner detail pass, 2026-10-13'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art-src/blender/bailiff-executioner.blend'))
scene.render.resolution_x=1024;scene.render.resolution_y=1024
scene.render.filepath=str(ROOT/'art-src/previews/bailiff-executioner.png')
bpy.ops.render.render(write_still=True)
subprocess.run(['magick',scene.render.filepath,'-resize','256x256',str(ROOT/'assets/bosses/bailiff_iso/portrait.png')],check=True)
print('EXECUTIONER_READY',len(parts),flush=True)
