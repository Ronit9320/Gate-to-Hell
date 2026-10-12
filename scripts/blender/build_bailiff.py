"""Refine the preserved Bailiff rig into an original, animated isometric model.
Run in Blender: blender -b art-src/blender/bailiff-original.blend --python scripts/blender/build_bailiff.py
"""
import bpy, math, pathlib
from mathutils import Vector
ROOT=pathlib.Path(__file__).resolve().parents[2]
scene=bpy.context.scene
rig=bpy.data.objects['BailiffRig']
rig.animation_data_clear()
rig.rotation_euler=(0,0,0)
for b in rig.pose.bones:
    b.rotation_mode='XYZ'; b.rotation_euler=(0,0,0); b.location=(0,0,0); b.scale=(1,1,1)
for name in ['Body','BailiffArmor']:
    bpy.data.objects[name].hide_render=True
    bpy.data.objects[name].hide_set(True)
collection=bpy.data.collections.new('Ash Bailiff — refined armor')
scene.collection.children.link(collection)
parts=[]
def material(name,color,metal=0,rough=.5,emission=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
    p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emission
    m.diffuse_color=(*color,1)
    return m
armor=material('Refined | charcoal steel',(.045,.055,.065),.72,.3)
edge=material('Refined | worn bronze',(.28,.13,.045),.68,.34)
steel=material('Refined | ash silver',(.19,.22,.24),.8,.34)
cloth=material('Refined | soot cloth',(.025,.018,.018),0,.86)
black=material('Refined | face darkness',(.004,.006,.008),.1,.6)
ember=material('Refined | orange ember',(.95,.085,.006),.15,.4,2.4)
hot=material('Refined | yellow core',(1,.38,.018),.1,.3,3)
def attach(o,mat,bone):
    for c in list(o.users_collection):c.objects.unlink(o)
    collection.objects.link(o)
    bpy.context.view_layer.objects.active=o;o.select_set(True)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.clear();o.data.materials.append(mat)
    # Bake each primitive into rest-space, then rigidly bind it to its armor bone.
    world=o.matrix_world.copy()
    for v in o.data.vertices:v.co=world@v.co
    o.matrix_world.identity()
    g=o.vertex_groups.new(name=bone);g.add(list(range(len(o.data.vertices))),1,'REPLACE')
    o.parent=rig
    mod=o.modifiers.new('Rigid armor skin','ARMATURE');mod.object=rig
    o.select_set(False);parts.append(o)
    return o

def box(name,loc,size,mat,bone,bevel=.035):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.name=name;o.scale=size
    attach(o,mat,bone)
    m=o.modifiers.new('Forged edges','BEVEL');m.width=bevel;m.segments=2
    return o

def ball(name,loc,size,mat,bone):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1,location=loc)
    o=bpy.context.object;o.name=name;o.scale=size
    for p in o.data.polygons:p.use_smooth=True
    return attach(o,mat,bone)

def link(name,a,b,r,mat,bone,r2=None):
    a,b=Vector(a),Vector(b);v=b-a
    bpy.ops.mesh.primitive_cone_add(vertices=10,radius1=r,radius2=r if r2 is None else r2,depth=v.length,location=(a+b)/2)
    o=bpy.context.object;o.name=name;o.rotation_euler=v.to_track_quat('Z','Y').to_euler()
    return attach(o,mat,bone)

def mesh(name,verts,faces,mat,bone):
    d=bpy.data.meshes.new(name);d.from_pydata(verts,[],faces);d.update()
    o=bpy.data.objects.new(name,d);collection.objects.link(o)
    return attach(o,mat,bone)

def plate(name,x,y,z,w,h,depth,mat,bone):
    outline=[(-w*.5,h*.35),(0,h*.5),(w*.5,h*.35),(w*.45,-h*.15),(0,-h*.5),(-w*.45,-h*.15)]
    vs=[(x+px,y+dy,z+pz) for dy in [-depth/2,depth/2] for px,pz in outline]
    fs=[tuple(range(5,-1,-1)),tuple(range(6,12))]+[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)]
    o=mesh(name,vs,fs,mat,bone);m=o.modifiers.new('Plate bevel','BEVEL');m.width=.012;m.segments=2
    return o
# Layered cuirass with bronze edge silhouette and a dark central breastplate.
ball('Torso under-armor',(0,0,1.47),(.27,.19,.32),cloth,'chest')
plate('Breastplate bronze rim',0,-.175,1.53,.55,.48,.1,edge,'chest')
plate('Breastplate charcoal',0,-.236,1.53,.5,.43,.045,armor,'chest')
plate('Back plate',0,.185,1.53,.5,.43,.075,armor,'chest')
for z,w in [(1.26,.45),(1.14,.42),(1.04,.38)]:
    plate('Layered abdominal plate',0,-.17,z,w,.19,.075,armor,'hips')
    link('Abdominal ember seam',(-w*.34,-.214,z),(0,-.23,z-.06),.009,ember,'hips')
    link('Abdominal ember seam',(w*.34,-.214,z),(0,-.23,z-.06),.009,ember,'hips')
# A pleated, flared mantle/skirt with front opening and bronze hem.
n=20;vs=[]
for z,r in [(1.08,.25),(.7,.29),(.25,.36)]:
    for i in range(n):
        t=2*math.pi*i/n;r1=r*(1.055 if i%2 else .965)
        vs.append((math.cos(t)*r1,math.sin(t)*r1*.82+.045,z))
faces=[]
for row in range(2):
    for i in range(n):
        if i in [14,15]:continue
        faces.append((row*n+i,row*n+(i+1)%n,(row+1)*n+(i+1)%n,(row+1)*n+i))
mesh('Pleated soot mantle',vs,faces,cloth,'hips')
for i in range(n):
    if i in [14,15]:continue
    t1=2*math.pi*i/n;t2=2*math.pi*(i+1)/n
    link('Mantle bronze hem',(math.cos(t1)*.36,math.sin(t1)*.295+.045,.255),(math.cos(t2)*.36,math.sin(t2)*.295+.045,.255),.012,edge,'hips')
for side,x in [('L',.2),('R',-.2)]:
    box('Armored boot '+side,(x,-.07,.13),(.22,.35,.24),armor,'foot.'+side,.025)
    plate('Greave '+side,x,-.1,.4,.19,.4,.11,armor,'shin.'+side)
    plate('Knee guard '+side,x,-.12,.59,.2,.2,.1,steel,'shin.'+side)
    # Readable oversized pauldrons, overlapping scales, serrated crown spikes.
    for j in range(3):
        xx=x/abs(x)*(.34+j*.052)
        plate('Layered shoulder '+side,xx,-.015,1.73-j*.08,.31,.2,.33,armor,'upper_arm.'+side)
    for j in range(3):
        sign=x/abs(x);a=(sign*(.39+j*.085),.04,1.82-j*.055)
        b=(sign*(.48+j*.105),.06,2.02-j*.09)
        link('Shoulder spike '+side,a,b,.055,steel,'upper_arm.'+side,.002)
    for z in [1.54,1.39]:
        box('Arm band '+side,(x/abs(x)*.415,0,z),(.235,.255,.11),edge,'upper_arm.'+side,.02)
    box('Forearm gauntlet '+side,(x/abs(x)*.463,-.018,1.155),(.205,.25,.32),armor,'forearm.'+side,.025)
    link('Gauntlet ember seam '+side,(x/abs(x)*.463,-.15,1.08),(x/abs(x)*.463,-.15,1.27),.011,ember,'forearm.'+side)
    box('Hand '+side,(x/abs(x)*.49,-.022,.865),(.17,.2,.19),armor,'hand.'+side,.03)
# A hollow hood arch, rather than the old opaque pointed box.
vs=[];segments=18
for z,r in [(1.82,.28),(2.04,.28),(2.23,.2),(2.34,.035)]:
    for i in range(segments+1):
        t=math.radians(-35+250*i/segments)
        vs.append((math.cos(t)*r,math.sin(t)*r*.83+.015,z))
fs=[(row*(segments+1)+i,row*(segments+1)+i+1,(row+1)*(segments+1)+i+1,(row+1)*(segments+1)+i) for row in range(3) for i in range(segments)]
o=mesh('Hollow ash hood',vs,fs,cloth,'head');sol=o.modifiers.new('Heavy hood cloth','SOLIDIFY');sol.thickness=.025
plate('Dark visor',0,-.14,2.04,.36,.34,.07,black,'head')
plate('Steel executioner mask',0,-.185,1.98,.26,.22,.02,armor,'head')
for sign in [-1,1]:
    link('Hood silver edge',(sign*.23,-.105,1.84),(sign*.21,-.12,2.12),.012,steel,'head')
    link('Hood silver edge',(sign*.21,-.12,2.12),(0,-.06,2.3),.012,steel,'head')
    link('Ember eye slit',(sign*.035,-.188,2.07),(sign*.122,-.178,2.095),.014,hot,'head')
    link('Mask ember engraving',(sign*.08,-.203,2.015),(sign*.025,-.203,1.91),.007,ember,'head')
# Signature molten seal: stable, bright orange, with readable concentric rings.
ball('Molten seal core',(0,-.29,1.49),(.125,.062,.125),hot,'chest')
for radius,minor,mat in [(.17,.026,edge),(.145,.014,ember),(.1,.012,ember)]:
    bpy.ops.mesh.primitive_torus_add(major_segments=24,minor_segments=8,location=(0,-.326,1.49),major_radius=radius,minor_radius=minor,rotation=(math.pi/2,0,0))
    o=bpy.context.object;o.name='Concentric ember seal';attach(o,mat,'chest')
for i in range(8):
    t=i*math.pi/4
    link('Seal rune',(math.cos(t)*.17,-.341,1.49+math.sin(t)*.17),(math.cos(t)*.204,-.34,1.49+math.sin(t)*.204),.012,ember,'chest')
# Match the game's 2:1 floor diamond: yaw45, elevation30, fixed orthographic scale.
cam=scene.camera;target=Vector((0,0,1.2));cam.location=(6,-6,1.2+math.sqrt(72)*math.tan(math.radians(30)))
cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=3.5
scene.render.resolution_x=256;scene.render.resolution_y=256;scene.render.resolution_percentage=100;scene.render.film_transparent=True
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
scene.world.color=(.11,.11,.11)
for o in scene.objects:
    if o.type=='LIGHT':
        o.data.energy=450 if 'Key' in o.name else 240;o.data.color=(1,.78,.57) if 'Key' in o.name else (.55,.7,1);o.data.shape='DISK';o.data.size=4
bpy.ops.object.light_add(type='AREA',location=(0,3,4));rim=bpy.context.object;rim.name='Refined rim';rim.data.energy=600;rim.data.color=(1,.28,.06);rim.data.size=3;rim.rotation_euler=(Vector((0,0,1.3))-rim.location).to_track_quat('-Z','Y').to_euler()
# Use a neutral display transform so orange emissive details do not clip to white.
try:scene.view_settings.view_transform='Standard'
except TypeError:pass
scene.view_settings.exposure=0;scene.view_settings.gamma=1
# New actions, rigid armor animation on the existing skeletal hierarchy.
def animate(name,count):
    rig.animation_data_clear()
    for frame in range(1,count+1):
        u=(frame-1)/(count-1);pulse=math.sin(u*math.tau)
        for b in rig.pose.bones:b.rotation_euler=(0,0,0);b.location=(0,0,0)
        rig.pose.bones['upper_arm.L'].rotation_euler.x=-.17
        rig.pose.bones['upper_arm.R'].rotation_euler.x=-.17
        rig.pose.bones['forearm.L'].rotation_euler.x=-.28
        rig.pose.bones['forearm.R'].rotation_euler.x=-.28
        rig.pose.bones['root'].location.z=.015*pulse
        rig.pose.bones['chest'].rotation_euler.x=.025*pulse
        if name=='Attack':
            wind=math.sin(min(1,u/.55)*math.pi/2);slam=max(0,(u-.55)/.22);recover=max(0,(u-.77)/.23)
            pose=wind*(1-min(1,slam))
            rig.pose.bones['chest'].rotation_euler.x=-.15*pose+.23*max(0,1-abs(u-.72)/.17)
            for side in ['L','R']:
                rig.pose.bones['upper_arm.'+side].rotation_euler.x=-.17-1.65*pose
                rig.pose.bones['forearm.'+side].rotation_euler.x=-.28-.32*pose
            rig.pose.bones['root'].location.z=-.12*max(0,1-abs(u-.74)/.16)
        elif name=='Walk':
            rig.pose.bones['thigh.L'].rotation_euler.x=.28*pulse;rig.pose.bones['thigh.R'].rotation_euler.x=-.28*pulse
            rig.pose.bones['root'].location.z=.035*abs(pulse)
        elif name=='Hurt':
            recoil=math.sin(u*math.pi)
            rig.pose.bones['chest'].rotation_euler.x=-.22*recoil;rig.pose.bones['head'].rotation_euler.x=-.18*recoil
        elif name=='Death':
            ease=u*u*(3-2*u)
            rig.pose.bones['root'].location.z=-.73*ease
            rig.pose.bones['hips'].rotation_euler.x=.6*ease;rig.pose.bones['chest'].rotation_euler.x=.75*ease
            rig.pose.bones['thigh.L'].rotation_euler.x=-.8*ease;rig.pose.bones['thigh.R'].rotation_euler.x=-.8*ease
            rig.pose.bones['shin.L'].rotation_euler.x=1.1*ease;rig.pose.bones['shin.R'].rotation_euler.x=1.1*ease
        for b in rig.pose.bones:
            b.keyframe_insert('rotation_euler',frame=frame);b.keyframe_insert('location',frame=frame)
    action=rig.animation_data.action;action.name='Refined_'+name;action.use_fake_user=True
for name,count in [('Idle',8),('Attack',10),('Walk',8),('Hurt',4),('Death',10)]:animate(name,count)
rig.animation_data.action=bpy.data.actions['Refined_Idle'];scene.frame_set(1);scene.frame_start=1;scene.frame_end=10
scene.render.filepath=str(ROOT/'art-src/previews/bailiff-refined.png')
(ROOT/'art-src/previews').mkdir(parents=True,exist_ok=True)
reference = bpy.data.images.load(str(ROOT/'assets/bosses/bailiff.png'), check_existing=True)
reference.name = 'Reference — original Ash Bailiff portrait'
reference.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art-src/blender/bailiff-isometric.blend'))
print('REFINED_BAILIFF_READY',len(parts),'armor parts')
