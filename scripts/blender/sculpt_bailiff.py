"""Rebuild Bailiff with continuous curved armor/anatomy and sculpted cloth.
blender -b art-src/blender/bailiff-isometric.blend -t 4 -P scripts/blender/sculpt_bailiff.py
The earlier models stay preserved; the existing rig/export contract is reused.
"""
import bpy, math, pathlib, subprocess
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[2]
source=(ROOT/'scripts/blender/build_bailiff.py').read_text()
exec(source[:source.index('# Layered cuirass')])
collection.name='Ash Bailiff — sculpted RPG forms'
for o in list(scene.objects):
    if o.type in ('MESH','CURVE'):
        o.hide_render=True
        o.hide_set(True)

def surface(name,verts,faces,mat,bone,sub=1,thickness=0):
    o=mesh(name,verts,faces,mat,bone)
    for p in o.data.polygons:p.use_smooth=True
    if sub:
        m=o.modifiers.new('Sculpted surface subdivision','SUBSURF');m.levels=sub;m.render_levels=sub
    if thickness:
        m=o.modifiers.new('Forged shell thickness','SOLIDIFY');m.thickness=thickness
    return o

def loft(name,profiles,mat,bone,segments=32,sub=1):
    # Each cross section: z, width, depth, x centre, y centre.
    v=[]
    for z,w,d,cx,cy in profiles:
        for i in range(segments):
            a=i*math.tau/segments
            v.append((cx+math.sin(a)*w,cy-math.cos(a)*d,z))
    f=[tuple(range(segments-1,-1,-1))]
    for j in range(len(profiles)-1):
        for i in range(segments):
            f.append((j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i))
    f.append(tuple((len(profiles)-1)*segments+i for i in range(segments)))
    return surface(name,v,f,mat,bone,sub)

def cord(name,points,radius,mat,bone):
    # Curves become editable meshes before rest-space skinning.
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=radius;c.bevel_resolution=3
    sp=c.splines.new('BEZIER');sp.bezier_points.add(len(points)-1)
    for p,co in zip(sp.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    o=bpy.data.objects.new(name,c);collection.objects.link(o)
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
    bpy.ops.object.convert(target='MESH')
    return attach(bpy.context.object,mat,bone)

def horn(name,points,radii,mat,bone):
    verts=[];n=12
    for j,p in enumerate(points):
        p=Vector(p);t=Vector(points[min(j+1,len(points)-1)])-Vector(points[max(0,j-1)])
        q=t.to_track_quat('Z','Y')
        for k in range(n):
            a=k*math.tau/n;verts.append(tuple(p+q@Vector((radii[j]*math.cos(a),radii[j]*math.sin(a),0))))
    faces=[tuple(range(n-1,-1,-1))]
    faces += [(j*n+k,j*n+(k+1)%n,(j+1)*n+(k+1)%n,(j+1)*n+k) for j in range(len(points)-1) for k in range(n)]
    faces.append(tuple((len(points)-1)*n+k for k in range(n)))
    return surface(name,verts,faces,mat,bone,1)

def worn_material(name,color,metal=.5,rough=.5,fabric=False):
    m=material(name,color,metal,rough)
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    ns=m.node_tree.nodes;ls=m.node_tree.links
    tex=ns.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=5;tex.inputs['Detail'].default_value=3
    ramp=ns.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.22;ramp.color_ramp.elements[0].color=(*(c*.65 for c in color),1)
    ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(*(min(1,c*1.35) for c in color),1)
    ls.new(tex.outputs['Fac'],ramp.inputs[0]);ls.new(ramp.outputs[0],p.inputs['Base Color'])
    grain=ns.new('ShaderNodeTexNoise');grain.inputs['Scale'].default_value=160 if fabric else 70
    bump=ns.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16 if fabric else .12;bump.inputs['Distance'].default_value=.012
    ls.new(grain.outputs['Fac'],bump.inputs['Height']);ls.new(bump.outputs[0],p.inputs['Normal'])
    if fabric:p.inputs['Sheen Weight'].default_value=.28
    return m

iron=worn_material('RPG | blue black forged iron',(.065,.10,.13),.72,.42)
brass=worn_material('RPG | aged warm brass',(.40,.24,.095),.64,.46)
edges=worn_material('RPG | bright worn steel',(.32,.38,.40),.75,.36)
soot=worn_material('RPG | charcoal burgundy cloth',(.041,.016,.022),0,.96,True)
lining=worn_material('RPG | hood shadow lining',(.012,.009,.014),0,.98,True)
hide=worn_material('RPG | dark leather',(.07,.037,.022),0,.82)
bone=worn_material('RPG | scorched ivory death mask',(.28,.265,.20),.22,.62)
fire=material('RPG | furnace vermilion',(1,.075,.006),.1,.5,2)
gold=material('RPG | furnace golden core',(1,.31,.035),.1,.4,2.4)
dark=material('RPG | furnace depth',(.004,.008,.009),.1,.8)

# Anatomy: tapered pelvis, broad pectoral form, narrow armored waist.
loft('Anatomical padded torso',[(1.01,.18,.14,0,.015),(1.05,.22,.155,0,.01),(1.26,.235,.17,0,0),(1.5,.33,.21,0,0),(1.67,.32,.18,0,.01),(1.76,.21,.13,0,.02),(1.79,.12,.10,0,.02)],hide,'chest')
loft('Curved execution cuirass',[(1.19,.17,.16,0,-.02),(1.23,.23,.19,0,-.02),(1.42,.30,.225,0,-.02),(1.59,.34,.225,0,-.01),(1.69,.30,.17,0,0),(1.72,.23,.13,0,.015)],iron,'chest',40,2)
for sign in [-1,1]:
    cord('Sweeping brass breastplate edge',[(0,-.16,1.72),(sign*.16,-.20,1.69),(sign*.29,-.17,1.63),(sign*.29,-.19,1.45),(sign*.17,-.21,1.24)],.012,brass,'chest')
    cord('Forged pectoral ridge',[(sign*.025,-.265,1.59),(sign*.14,-.25,1.64),(sign*.26,-.20,1.61)],.014,edges,'chest')
    for j in range(4):ball('Chest rim rivet',(sign*(.16+j*.027),-.218+j*.015,1.29+j*.09),(.012,.009,.012),brass,'chest')
# Curved articulated abdominal bands, rather than flat shield-shaped slabs.
for j in range(3):
    z=1.18-j*.075
    loft('Overlapping rounded belly lame',[(z-.055,.19-j*.014,.15,0,0),(z-.04,.225-j*.014,.175,0,0),(z+.035,.235-j*.014,.17,0,0),(z+.05,.215-j*.014,.145,0,0)],iron,'hips',32,1)
loft('Leather waist belt',[(1.0,.235,.174,0,0),(1.02,.25,.19,0,0),(1.065,.25,.19,0,0),(1.08,.235,.174,0,0)],hide,'hips')
ball('Belt office seal',(0,-.201,1.035),(.058,.025,.059),brass,'hips')

# Furnace lens in a deeply recessed cast brass socket, not a glowing badge.
ball('Furnace dark socket',(0,-.267,1.455),(.147,.045,.17),dark,'chest')
ball('Recessed molten chamber',(0,-.295,1.455),(.112,.028,.137),fire,'chest')
for r,minor,mat in [(.155,.018,brass),(.127,.009,edges)]:
    bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=12,major_radius=r,minor_radius=minor,location=(0,-.303,1.455),rotation=(math.pi/2,0,0))
    o=bpy.context.object;o.name='Cast furnace socket';o.scale.z=1.08;attach(o,mat,'chest')
for x in [-.075,-.037,0,.037,.075]:
    cord('Convex furnace grate',[(x,-.316,1.35),(x,-.34,1.455),(x,-.316,1.56)],.011,iron,'chest')
for k in range(8):
    a=k*math.tau/8;ball('Furnace flange stud',(math.cos(a)*.154,-.315,1.455+math.sin(a)*.166),(.010,.010,.010),brass,'chest')

# Rounded shoulders: asymmetric overlapping domed shells with swept horns.
for sign,side in [(1,'L'),(-1,'R')]:
    cx=sign*.355
    ball('Deltoid anatomy',(cx,.01,1.64),(.15,.145,.20),hide,'upper_arm.'+side)
    for layer in range(3):
        verts=[];faces=[];n=36;rows=8
        wide=(.265 if side=='L' else .225)-layer*.022
        for row in range(rows):
            phi=.04+(row/(rows-1))*1.74
            for k in range(n):
                a=k*math.tau/n;flute=1+.035*math.cos(a*6)
                verts.append((cx+sign*math.cos(a)*wide*math.sin(phi)*flute,.01+math.sin(a)*.205*math.sin(phi),1.78-layer*.073+.13*math.cos(phi)+.012*math.cos(a*3)))
        for row in range(rows-1):
            for k in range(n):faces.append((row*n+k,row*n+(k+1)%n,(row+1)*n+(k+1)%n,(row+1)*n+k))
        surface('Scalloped vaulted pauldron '+side,verts,faces,iron,'upper_arm.'+side,1,.018)
        edgepoints=[verts[(rows-1)*n+k] for k in range(n)]+[verts[(rows-1)*n]]
        cord('Pauldron rolled brass edge',edgepoints,.008,brass,'upper_arm.'+side)
    for k in range(2 if side=='R' else 3):
        x=cx+sign*(.04+k*.055);y=.05+k*.042
        horn('Swept shoulder talon',[(x,y,1.86),(x+sign*.045,y+.015,1.94),(x+sign*.10,y+.03,2.015-k*.025),(x+sign*.155,y+.05,2.02-k*.02)],[.048,.038,.022,.001],edges,'upper_arm.'+side)
    # Sculpted flutes sweep across the top shell, breaking up the dome.
    for k in range(5):
        a=-2.5+k*.38
        width=.265 if side=='L' else .225
        cord('Pauldron radial forged flute',[(cx+sign*math.cos(a)*width*u,.01+math.sin(a)*.205*u,1.784+.13*math.sqrt(1-u*u)+.012*math.cos(a*3)) for u in [.28,.47,.65,.80]],.007,brass,'upper_arm.'+side)
    # Full tapered arm and sculpted cuff.
    loft('Sleeved upper arm '+side,[(1.31,.095,.095,sign*.42,0),(1.37,.125,.11,sign*.41,0),(1.53,.145,.125,sign*.38,0),(1.64,.14,.12,sign*.36,0)],soot,'upper_arm.'+side)
    ball('Exposed elbow hinge',(sign*.445,0,1.3),(.092,.11,.11),iron,'forearm.'+side)
    loft('Tapered forged vambrace '+side,[(.965,.075,.075,sign*.48,-.01),(.99,.09,.095,sign*.48,-.01),(1.14,.13,.135,sign*.465,-.01),(1.25,.135,.12,sign*.45,0),(1.29,.11,.10,sign*.445,0)],iron,'forearm.'+side,32,2)
    cord('Vambrace raised spine',[(sign*.48,-.10,.98),(sign*.465,-.153,1.12),(sign*.45,-.136,1.27)],.012,brass,'forearm.'+side)
    ball('Leather gauntlet palm',(sign*.49,-.018,.89),(.085,.071,.105),hide,'hand.'+side)
    ball('Curved dorsal hand plate',(sign*.49,-.071,.905),(.081,.043,.08),iron,'hand.'+side)
    for k in range(4):
        x=sign*.49+(k-1.5)*.032
        ball('Rounded armored finger',(x,-.031,.812),(.019,.035,.045),iron,'hand.'+side)
        ball('Finger knuckle',(x,-.073,.875),(.020,.022,.026),edges,'hand.'+side)
    ball('Opposing armored thumb',(sign*.415,-.052,.866),(.03,.036,.051),iron,'hand.'+side)

# Legs and boots follow calf/ankle/foot anatomy instead of rectangular blocks.
for sign,side in [(1,'L'),(-1,'R')]:
    x=sign*.17
    loft('Trouser thigh '+side,[(.52,.09,.10,x,0),(.61,.13,.12,x,0),(.83,.15,.14,x,0),(1.015,.16,.15,x,0)],soot,'thigh.'+side)
    loft('Sculpted calf greave '+side,[(.16,.075,.08,x,0),(.19,.095,.095,x,0),(.32,.12,.13,x,.01),(.46,.125,.115,x,.02),(.55,.10,.10,x,0),(.58,.09,.085,x,0)],iron,'shin.'+side,32,2)
    ball('Rounded cupped kneecap',(x,-.095,.58),(.11,.08,.11),edges,'shin.'+side)
    cord('Greave brass ridge',[(x,-.09,.18),(x,-.133,.32),(x,-.12,.50)],.009,brass,'shin.'+side)
    # Ring profiles sculpt the swept toe, instep and heel as one surface.
    loft('Anatomical sabaton '+side,[(.025,.075,.15,x,-.075),(.04,.105,.19,x,-.09),(.10,.112,.195,x,-.085),(.17,.105,.17,x,-.05),(.22,.085,.105,x,.0),(.25,.073,.085,x,0)],iron,'foot.'+side,32,2)
    cord('Toe brass piping',[(x-.086,-.18,.09),(x,-.275,.095),(x+.086,-.18,.09)],.007,brass,'foot.'+side)

# Shoulder cloak and hanging skirt: dense, continuous fabric with broad folds.
verts=[];faces=[];n=64;rows=18
for row in range(rows):
    t=row/(rows-1);z=1.08-.86*t;r=.245+.16*t
    for k in range(n+1):
        a=-.94+k/n*(math.tau-1.88);fold=.022*math.sin(a*11+.4*t)+.011*math.sin(a*23-t)
        verts.append((math.sin(a)*(r+fold),-math.cos(a)*(r*.80+fold)+.015,z+(.024*math.sin(a*14)+.012*math.sin(a*23))*t**6))
for row in range(rows-1):
    for k in range(n):faces.append((row*(n+1)+k,row*(n+1)+k+1,(row+1)*(n+1)+k+1,(row+1)*(n+1)+k))
surface('Continuous fluted execution skirt',verts,faces,soot,'hips',1,.012)
for sign in [-1,1]:
    cord('Scorched skirt opening seam',[(sign*.21,-.13,1.075),(sign*.27,-.17,.79),(sign*.32,-.215,.50),(sign*.34,-.23,.25)],.009,brass,'hips')
# Split front tabard, shaped like hanging cloth rather than a rigid panel.
for sign in [-1,1]:
    v=[];f=[];cols=10;rows=18
    for row in range(rows):
        t=row/(rows-1)
        for k in range(cols+1):
            u=k/cols;x=sign*(.045+u*(.10-.02*t))
            v.append((x,-.197-.035*t+.018*math.sin(u*math.tau*1.5)*math.sin(t*math.pi),1.0-.64*t+.04*u*t**6))
    for row in range(rows-1):
        for k in range(cols):f.append((row*(cols+1)+k,row*(cols+1)+k+1,(row+1)*(cols+1)+k+1,(row+1)*(cols+1)+k))
    surface('Split draped tabard',v,f,soot,'hips',1,.009)

# Back mantle: a continuous drape, graded skin weights down to the pelvis.
v=[];f=[];n=40;rows=20
for row in range(rows):
    t=row/(rows-1)
    for k in range(n+1):
        u=k/n;a=-1.28+u*2.56;width=.285+.13*t
        fold=.026*math.sin(u*math.tau*6)*(0.25+.75*t)
        v.append((math.sin(a)*(width+fold),.10+math.cos(a)*(.17+.11*t)+fold,1.76-1.42*t+.035*math.sin(u*math.tau*9)*t**8))
for row in range(rows-1):
    for k in range(n):f.append((row*(n+1)+k,row*(n+1)+k+1,(row+1)*(n+1)+k+1,(row+1)*(n+1)+k))
cape=surface('Sculpted weighted back mantle',v,f,soot,'hips',1,.012)
chestgroup=cape.vertex_groups.new(name='chest');hipgroup=cape.vertex_groups['hips']
for vertex in cape.data.vertices:
    w=max(0,min(1,(vertex.co.z-1.25)/.46))
    hipgroup.add([vertex.index],1-w,'REPLACE');chestgroup.add([vertex.index],w,'REPLACE')

# Deep hood: rounded skull volume, modeled opening and cascading fabric folds.
ball('Shadow head volume',(0,.005,2.01),(.17,.145,.21),lining,'head')
v=[];f=[];n=48;profiles=[(1.83,.255,.205),(1.86,.267,.225),(1.94,.26,.235),(2.07,.25,.235),(2.18,.205,.20),(2.27,.14,.15),(2.32,.055,.07),(2.335,.013,.018)]
for row,(z,w,d) in enumerate(profiles):
    for k in range(n+1):
        a=math.radians(-42+k/n*264);fold=.01*math.sin(a*8)*(1-row/9)
        v.append((math.cos(a)*(w+fold),math.sin(a)*(d+fold)+.04,z+.009*math.cos(a*4)))
for row in range(len(profiles)-1):
    for k in range(n):f.append((row*(n+1)+k,row*(n+1)+k+1,(row+1)*(n+1)+k+1,(row+1)*(n+1)+k))
surface('Sculpted hollow execution hood',v,f,soot,'head',2,.018)
for sign in [-1,1]:
    cord('Heavy hood rolled opening',[(sign*.20,-.13,1.84),(sign*.22,-.18,1.97),(sign*.18,-.18,2.15),(sign*.09,-.11,2.28),(0,-.045,2.32)],.015,hide,'head')
    cord('Hood stitch piping',[(sign*.205,-.145,1.87),(sign*.226,-.19,2.02),(sign*.165,-.17,2.19),(sign*.075,-.095,2.28)],.004,brass,'head')
# Curved skull-like mask with tapered jaw, pronounced cheekbones and dark sockets.
v=[];f=[];n=32
profiles=[(1.87,.043,.045),(1.9,.087,.065),(1.95,.115,.087),(2.00,.155,.105),(2.055,.158,.097),(2.10,.146,.081),(2.135,.108,.063)]
for z,w,d in profiles:
    for k in range(n+1):
        a=-math.pi/2+k/n*math.pi
        v.append((math.sin(a)*w,-.142-math.cos(a)*d,z))
for row in range(len(profiles)-1):
    for k in range(n):f.append((row*(n+1)+k,row*(n+1)+k+1,(row+1)*(n+1)+k+1,(row+1)*(n+1)+k))
surface('Sculpted iron death mask',v,f,bone,'head',2,.012)
for sign in [-1,1]:
    ball('Deep angular eye socket',(sign*.079,-.239,2.063),(.069,.014,.037),dark,'head')
    cord('Narrow molten eye',[(sign*.025,-.255,2.063),(sign*.067,-.256,2.06),(sign*.122,-.235,2.078)],.008,gold,'head')
    cord('Stern sculpted brow',[(sign*.012,-.24,2.105),(sign*.068,-.248,2.11),(sign*.14,-.204,2.12)],.018,iron,'head')
    cord('Curved cheekbone ridge',[(sign*.14,-.20,2.025),(sign*.10,-.235,1.99),(sign*.062,-.23,1.94)],.015,edges,'head')
    for k in range(3):
        x=sign*(.022+k*.021)
        cord('Death mask carved jaw vent',[(x,-.215,1.967),(x*.7,-.213,1.925)],.007,dark,'head')
horn('Mask sculpted nose',[(0,-.226,2.04),(0,-.252,2.01),(0,-.248,1.988)],[.024,.02,.005],iron,'head')
# Split angular jaw and hanging fangs reinforce the executioner's expression.
for sign in [-1,1]:
    horn('Carved death mask fang',[(sign*.052,-.218,1.951),(sign*.042,-.231,1.917),(sign*.023,-.226,1.872)],[.013,.011,.001],bone,'head')
    cord('Mask brow engraving',[(sign*.045,-.235,2.125),(sign*.10,-.219,2.134),(sign*.126,-.199,2.13)],.004,brass,'head')

# Office chain follows curved neck and back; a wax debt seal hangs at the hip.
for k in range(22):
    a=-1.5+k/21*3.0;loc=(math.sin(a)*.27,math.cos(a)*.22+.04,1.70-.12*math.cos(a))
    bpy.ops.mesh.primitive_torus_add(major_segments=16,minor_segments=8,major_radius=.022,minor_radius=.0045,location=loc,rotation=(math.pi/2,0,k%2*math.pi/2))
    o=bpy.context.object;o.name='Interlocking neck chain';attach(o,brass,'chest')
ball('Debt wax seal',(.22,-.155,.90),(.056,.025,.067),brass,'hips')
cord('Seal leather tassel',[(.22,-.15,.88),(.24,-.15,.80),(.22,-.17,.73)],.018,soot,'hips')

# Sculpted execution maul: lobed hammer head with rounded flanges and curved beak.
x=-.49;y=-.015
loft('Leather wrapped maul haft',[(.30,.022,.023,x,y),(.33,.03,.03,x,y),(.83,.028,.028,x,y),(.99,.038,.038,x,y),(1.1,.035,.035,x,y)],hide,'hand.R')
for k in range(11):
    z=.36+k*.053
    cord('Spiral haft wrap',[(x+.03*math.sin(a),y+.03*math.cos(a),z+j*.009) for j,a in enumerate([j*math.tau/10 for j in range(11)])],.0045,brass,'hand.R')
# Axis-X cross sections, shaped as a cast cylindrical/slightly square maul.
v=[];f=[];n=40;sections=[(-.23,.085),(-.218,.145),(-.18,.158),(-.155,.13),(-.08,.126),(.08,.126),(.155,.13),(.18,.158),(.218,.145),(.23,.085)]
for dx,r in sections:
    for k in range(n):
        a=k*math.tau/n;flute=1+.05*math.cos(a*8)
        v.append((x+dx,y+math.cos(a)*r*flute,1.15+math.sin(a)*r*flute))
f=[tuple(range(n-1,-1,-1))]+[(row*n+k,row*n+(k+1)%n,(row+1)*n+(k+1)%n,(row+1)*n+k) for row in range(len(sections)-1) for k in range(n)]+[tuple((len(sections)-1)*n+k for k in range(n))]
surface('Sculpted fluted execution maul head',v,f,iron,'hand.R',2)
for dx in [-.178,.178]:
    cord('Maul flange worn brass lip',[(x+dx,y+math.cos(a)*.154,1.15+math.sin(a)*.154) for a in [k*math.tau/40 for k in range(41)]],.012,brass,'hand.R')
ball('Molten maul striking face',(x-.232,y,1.15),(.018,.092,.092),fire,'hand.R')
for k in range(3):
    z=1.105+k*.044
    cord('Maul striking grate',[(x-.254,y-.075,z),(x-.26,y,z),(x-.254,y+.075,z)],.009,iron,'hand.R')
horn('Maul curved counterweight',[(x+.19,y,1.15),(x+.25,y,1.15),(x+.29,y,1.11),(x+.29,y,1.065)],[.065,.055,.034,.002],brass,'hand.R')

rig.animation_data_create();rig.animation_data.action=bpy.data.actions['Refined_Idle'];scene.frame_set(1)
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.render.threads_mode='FIXED';scene.render.threads=4
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.7
scene['revision']='Sculpted RPG anatomy and curved armor — 2026-10-13'
scene['art_direction']='ART_DIRECTION.md; Valve character-art principles, original design'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art-src/blender/bailiff-sculpted.blend'))
scene.render.resolution_x=1024;scene.render.resolution_y=1024
scene.render.filepath=str(ROOT/'art-src/previews/bailiff-sculpted.png')
bpy.ops.render.render(write_still=True)
subprocess.run(['magick',scene.render.filepath,'-resize','256x256',str(ROOT/'assets/bosses/bailiff_iso/portrait.png')],check=True)
print('SCULPTED_BAILIFF_READY',len(parts),flush=True)
