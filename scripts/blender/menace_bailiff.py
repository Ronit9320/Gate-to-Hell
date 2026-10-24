"""Menacing detail and mechanically closed hammer grip, using the sculpted base.
blender -b art-src/blender/bailiff-isometric.blend -t 4 -P scripts/blender/menace_bailiff.py
"""
import bpy, math, pathlib, subprocess, json
from mathutils import Vector, Matrix
ROOT=pathlib.Path(__file__).resolve().parents[2]
src=(ROOT/'scripts/blender/sculpt_bailiff.py').read_text()
exec(src[:src.index('rig.animation_data_create();')])
collection.name='Ash Bailiff — menacing executioner and closed grip'

def hide_parts(prefixes):
    for o in parts:
        if any(o.name.startswith(p) for p in prefixes):o.hide_render=True;o.hide_set(True)

# Rebuild the right hand and maul together in one shared skeletal space.
hide_parts(['Leather wrapped maul haft','Spiral haft wrap','Sculpted fluted execution maul head','Maul flange worn brass lip','Molten maul striking face','Maul striking grate','Maul curved counterweight'])
for o in parts:
    if o.vertex_groups.get('hand.R') and any(o.name.startswith(p) for p in ['Leather gauntlet palm','Curved dorsal hand plate','Rounded armored finger','Finger knuckle','Opposing armored thumb']):
        o.hide_render=True;o.hide_set(True)
hx=-.49;hy=-.068;gz=.875
ball('Closed grip palm',(hx,-.01,gz),(.078,.053,.079),hide,'hand.R')
ball('Closed grip dorsal armor',(hx,.028,gz+.005),(.085,.035,.081),iron,'hand.R')
for k in range(4):
    z=.827+k*.029
    points=[(hx-.063,-.017,z),(hx-.073,-.065,z),(hx-.048,-.108,z),(hx+.005,-.114,z),(hx+.044,-.083,z),(hx+.034,hy,z)]
    cord('Curled gripping finger '+str(k),points,.0135,hide,'hand.R')
    ball('Gripping finger armored knuckle',(hx-.061,-.065,z),(.020,.019,.019),iron,'hand.R')
    cord('Finger segment band',[(hx-.042,-.115,z),(hx-.009,-.126,z),(hx+.020,-.112,z)],.006,brass,'hand.R')
cord('Opposed thumb wrapped over grip',[(hx+.06,.0,.924),(hx+.072,-.058,.919),(hx+.045,-.105,.905),(hx+.014,-.108,.902)],.020,hide,'hand.R')
ball('Thumb armored joint',(hx+.065,-.058,.917),(.025,.023,.023),iron,'hand.R')
# Haft passes through the closed fingers; pommel and head establish its weight.
loft('Gripped hammer shaft',[(.32,.018,.018,hx,hy),(.35,.029,.029,hx,hy),(.99,.029,.029,hx,hy),(1.19,.035,.035,hx,hy),(1.25,.027,.027,hx,hy)],hide,'hand.R',24,1)
ball('Hammer cast pommel',(hx,hy,.33),(.045,.045,.055),brass,'hand.R')
for k in range(14):
    z=.36+k*.048
    cord('Hammer leather spiral binding',[(hx+.030*math.sin(a),hy+.030*math.cos(a),z+j*.006) for j,a in enumerate([j*math.tau/12 for j in range(13)])],.0035,brass,'hand.R')
v=[];f=[];n=48;headz=1.235
sections=[(-.245,.105),(-.23,.168),(-.20,.185),(-.17,.166),(-.12,.152),(.08,.152),(.13,.17),(.17,.181),(.20,.157),(.218,.10)]
for dx,r in sections:
    for k in range(n):
        a=k*math.tau/n;flute=1+.075*math.cos(a*8)
        v.append((hx+dx,hy+math.cos(a)*r*flute,headz+math.sin(a)*r*flute))
f=[tuple(range(n-1,-1,-1))]+[(row*n+k,row*n+(k+1)%n,(row+1)*n+(k+1)%n,(row+1)*n+k) for row in range(len(sections)-1) for k in range(n)]+[tuple((len(sections)-1)*n+k for k in range(n))]
surface('Heavy sculpted furnace maul',v,f,iron,'hand.R',2)
for dx in [-.205,.165]:
    cord('Hammer cast brass reinforcing collar',[(hx+dx,hy+math.cos(a)*.182,headz+math.sin(a)*.182) for a in [k*math.tau/48 for k in range(49)]],.011,brass,'hand.R')
ball('Hammer recessed molten striking disk',(hx-.247,hy,headz),(.015,.116,.116),fire,'hand.R')
for k in range(4):
    z=headz-.09+k*.06
    cord('Hammer iron striking grille',[(hx-.262,hy-.085,z),(hx-.268,hy,z),(hx-.262,hy+.085,z)],.010,iron,'hand.R')
horn('Hammer hooked counterweight',[(hx+.18,hy,headz),(hx+.25,hy,headz),(hx+.28,hy,headz-.06),(hx+.255,hy,headz-.135)],[.065,.053,.026,.001],edges,'hand.R')
for k in range(8):
    a=k*math.tau/8
    cord('Hammer head forged ridge',[(hx-.165,hy+math.cos(a)*.163,headz+math.sin(a)*.163),(hx+.10,hy+math.cos(a)*.163,headz+math.sin(a)*.163)],.005,brass,'hand.R')
    ball('Hammer collar bolt',(hx-.20,hy+math.cos(a)*.191,headz+math.sin(a)*.191),(.010,.010,.010),edges,'hand.R')

# Dark iron death mask, deeply slanted eyes, serrated jaw and scarred face.
char=worn_material('Executioner | blackened mask iron',(.035,.046,.051),.58,.56)
mask=bpy.data.objects['Sculpted iron death mask'];mask.data.materials.clear();mask.data.materials.append(char)
hide_parts(['Deep angular eye socket','Narrow molten eye','Stern sculpted brow','Mask brow engraving','Carved death mask fang'])
for sign in [-1,1]:
    cord('Severe hollow eye socket',[(sign*.021,-.253,2.075),(sign*.075,-.261,2.06),(sign*.133,-.221,2.087)],.020,dark,'head')
    cord('Slanted furnace eye core',[(sign*.025,-.269,2.075),(sign*.075,-.274,2.06),(sign*.124,-.24,2.083)],.0065,gold,'head')
    cord('Blade brow overhang',[(sign*.013,-.25,2.104),(sign*.07,-.268,2.095),(sign*.14,-.211,2.12)],.022,char,'head')
    horn('Executioner jaw fang',[(sign*.085,-.218,1.981),(sign*.072,-.238,1.942),(sign*.055,-.226,1.875)],[.019,.013,.001],edges,'head')
    cord('Mask face scored scar',[(sign*.11,-.228,2.035),(sign*.093,-.252,2.01),(sign*.077,-.245,1.992)],.004,brass,'head')
    cord('Broken mask ember fissure',[(sign*.032,-.244,1.989),(sign*.038,-.238,1.967),(sign*.017,-.232,1.95)],.003,fire,'head')
# Narrow, pointed crown studs emerge from the hood rather than cartoon horns.
for sign in [-1,1]:
    horn('Hood execution crown blade',[(sign*.18,.06,2.17),(sign*.21,.10,2.24),(sign*.195,.135,2.32),(sign*.145,.15,2.37)],[.029,.026,.015,.001],char,'head')

# Chased shoulder plaques, fastenings, ridge wear and a larger swept talon.
for sign,side in [(-1,'R'),(1,'L')]:
    cx=sign*.355;wide=.225 if side=='R' else .265
    for k in range(9):
        a=-2.9+k*.34
        ball('Pauldron perimeter rivet',(cx+sign*math.cos(a)*wide,.01+math.sin(a)*.205,1.756+.012*math.cos(a*3)),(.011,.011,.011),brass,'upper_arm.'+side)
    # Embossed flame/debt crest follows the forward curve of the pauldron.
    crest=[(cx,-.198,1.80),(cx-sign*.028,-.178,1.847),(cx-sign*.016,-.13,1.876),(cx+sign*.025,-.171,1.854),(cx+sign*.04,-.195,1.813)]
    cord('Pauldron embossed execution crest',crest,.007,edges,'upper_arm.'+side)
    cord('Pauldron damaged edge',[(cx-sign*.095,-.18,1.765),(cx-sign*.068,-.188,1.764),(cx-sign*.04,-.193,1.76)],.004,edges,'upper_arm.'+side)
    horn('Dominant rear pauldron scythe',[(cx+sign*.04,.13,1.88),(cx+sign*.11,.16,1.98),(cx+sign*.16,.19,2.075),(cx+sign*.12,.22,2.13)],[.045,.038,.023,.001],char,'upper_arm.'+side)
    # Bracer plate ridges, narrow runes and hinged cuff bolts.
    for k in range(3):
        z=1.04+k*.062;x=sign*(.475-.01*k)
        cord('Vambrace overlapping forged band',[(x-.072,-.085,z),(x,-.148,z+.025),(x+.072,-.085,z)],.009,edges,'forearm.'+side)
    for k in range(2):
        x=sign*.465+(k-.5)*.05
        cord('Bracer glowing incised rune',[(x,-.154,1.20),(x+.011,-.155,1.175),(x-.008,-.155,1.153)],.003,fire,'forearm.'+side)
    ball('Bracer hinge bolt',(sign*.55,-.02,1.22),(.022,.018,.022),brass,'forearm.'+side)
    # Breastplate scars sit directly on the curved surface.
    cord('Cuirass sword scoring',[(sign*.19,-.23,1.57),(sign*.16,-.25,1.54),(sign*.14,-.265,1.51)],.0035,edges,'chest')
    cord('Breastplate embossed office scroll',[(sign*.14,-.248,1.625),(sign*.12,-.265,1.6),(sign*.16,-.258,1.58),(sign*.18,-.24,1.6)],.005,brass,'chest')

# Tattered singed hems, repaired cloth seams and hanging chains/debt tags.
for name,cutoff in [('Continuous fluted execution skirt',.35),('Sculpted weighted back mantle',.48)]:
    o=bpy.data.objects[name]
    for vertex in o.data.vertices:
        co=vertex.co
        if co.z<cutoff:
            u=max(0,(cutoff-co.z)/(cutoff-.20))
            co.z+=u*(.035*math.sin(co.x*69)+.02*math.cos(co.x*121))
    o.data.update()
for sign in [-1,1]:
    for k in range(16):
        z=.40+k*.035;x=sign*(.115+(z-.40)*.04)
        cord('Tabard hand stitched seam',[(x-.005,-.235,z),(x+.006,-.236,z+.008)],.0023,brass,'hips')
    # Metal hem weights hang just above the torn lower cloth edge.
    for k in range(3):ball('Cloth hem iron weight',(sign*(.20+k*.055),-.15,.32+k*.012),(.014,.01,.021),char,'hips')
for k in range(12):
    t=k/11;loc=(.25+.035*math.sin(t*math.pi),-.14,.98-.23*t)
    bpy.ops.mesh.primitive_torus_add(major_segments=16,minor_segments=8,major_radius=.018,minor_radius=.004,location=loc,rotation=(math.pi/2,0,k%2*math.pi/2))
    o=bpy.context.object;o.name='Hanging debt chain';attach(o,brass,'hips')
ball('Scorched debt token',(.25,-.14,.73),(.031,.015,.044),char,'hips')
cord('Debt token stamped rune',[(.239,-.16,.74),(.257,-.16,.75),(.249,-.16,.715)],.003,brass,'hips')
# Repaired seams on the rear drape remain legible at close inspection.
for k in range(16):
    z=.66+k*.044
    cord('Mantle stitched repair',[(.16,.35,z),(.18,.35,z+.016)],.0025,brass,'hips' if z<1.2 else 'chest')

# New poses: a one-handed raised maul cast, wrist compensation keeps the
# weapon upright through wind-up. Both the grip and shaft follow hand.R.
def animate_executioner(name,count):
    rig.animation_data_clear()
    for frame in range(1,count+1):
        u=(frame-1)/(count-1);pulse=math.sin(u*math.tau)
        for b in rig.pose.bones:
            b.rotation_mode='XYZ';b.rotation_euler=(0,0,0);b.location=(0,0,0);b.scale=(1,1,1)
        rig.pose.bones['upper_arm.R'].rotation_euler.x=-.22
        rig.pose.bones['upper_arm.R'].rotation_euler.z=.10
        rig.pose.bones['forearm.R'].rotation_euler.x=-.38
        rig.pose.bones['upper_arm.L'].rotation_euler.x=-.18
        rig.pose.bones['forearm.L'].rotation_euler.x=-.22
        rig.pose.bones['chest'].rotation_euler.x=.045+.016*pulse
        rig.pose.bones['head'].rotation_euler.x=.09
        rig.pose.bones['root'].location.z=.009*pulse
        wrist_angle=.08
        if name=='Attack':
            # Frames 1-6 wind-up; 7-8 release; 9-10 settle.
            wind=min(1,u/.55);wind=wind*wind*(3-2*wind)
            release=min(1,max(0,(u-.55)/.22));settle=min(1,max(0,(u-.77)/.23))
            lift=wind*(1-release)
            rig.pose.bones['upper_arm.R'].rotation_euler.x=-.22-1.05*lift
            rig.pose.bones['forearm.R'].rotation_euler.x=-.38-1.2*lift
            rig.pose.bones['upper_arm.R'].rotation_euler.z=.10+.05*lift
            rig.pose.bones['chest'].rotation_euler.x=.045-.10*lift+.16*math.sin(release*math.pi)*(1-settle)
            rig.pose.bones['head'].rotation_euler.x=.09-.08*lift
            rig.pose.bones['upper_arm.L'].rotation_euler.x=-.18-.55*lift
            rig.pose.bones['forearm.L'].rotation_euler.x=-.22-.30*lift
            rig.pose.bones['root'].location.z=-.08*math.sin(release*math.pi)
            wrist_angle=-.35*lift+.75*math.sin(release*math.pi)*(1-settle)
        elif name=='Walk':
            rig.pose.bones['thigh.L'].rotation_euler.x=.22*pulse;rig.pose.bones['thigh.R'].rotation_euler.x=-.22*pulse
            rig.pose.bones['root'].location.z=.018*abs(pulse)
        elif name=='Hurt':
            recoil=math.sin(u*math.pi);rig.pose.bones['chest'].rotation_euler.x=-.17*recoil;rig.pose.bones['head'].rotation_euler.x=-.14*recoil
            wrist_angle=-.12*recoil
        elif name=='Death':
            ease=u*u*(3-2*u)
            rig.pose.bones['root'].location.z=-.73*ease
            rig.pose.bones['hips'].rotation_euler.x=.6*ease;rig.pose.bones['chest'].rotation_euler.x=.75*ease
            for side in ['L','R']:
                rig.pose.bones['thigh.'+side].rotation_euler.x=-.8*ease;rig.pose.bones['shin.'+side].rotation_euler.x=1.1*ease
            wrist_angle=.08+.7*ease
        bpy.context.view_layer.update()
        hand=rig.pose.bones['hand.R'];pos=hand.matrix.translation.copy()
        hand.matrix=Matrix.Translation(pos)@Matrix.Rotation(wrist_angle,4,'X')@hand.bone.matrix_local.to_3x3().to_4x4()
        for b in rig.pose.bones:
            b.keyframe_insert('rotation_euler',frame=frame);b.keyframe_insert('location',frame=frame)
    action=rig.animation_data.action;action.name='Executioner_'+name;action.use_fake_user=True
    # Exporter uses these stable public clip names.
    old=bpy.data.actions.get('Refined_'+name)
    if old:old.name='Preserved_'+name
    action.name='Refined_'+name
for name,count in [('Idle',8),('Attack',10),('Walk',8),('Hurt',4),('Death',10)]:animate_executioner(name,count)
rig.animation_data.action=bpy.data.actions['Refined_Idle'];scene.frame_set(1)
scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
scene.view_settings.view_transform='AgX';scene.view_settings.exposure=.55
scene['revision']='Menacing executioner, closed hammer grip and new wrist-controlled attack'
scene['grip_center_rest']=[hx,hy,gz];scene['grip_bone']='hand.R'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'art-src/blender/bailiff-menacing.blend'))
scene.render.resolution_x=1024;scene.render.resolution_y=1024
scene.render.filepath=str(ROOT/'art-src/previews/bailiff-menacing.png');bpy.ops.render.render(write_still=True)
subprocess.run(['magick',scene.render.filepath,'-resize','256x256',str(ROOT/'assets/bosses/bailiff_iso/portrait.png')],check=True)
# A close grip crop is a camera render, so it exposes actual finger contact.
old_scale=scene.camera.data.ortho_scale;old_location=scene.camera.location.copy();old_rotation=scene.camera.rotation_euler.copy()
rig.animation_data.action=bpy.data.actions['Refined_Idle'];scene.frame_set(1);bpy.context.view_layer.update()
hand=rig.pose.bones['hand.R'];target=rig.matrix_world@hand.matrix@hand.bone.matrix_local.inverted()@Vector((hx,hy,gz))
scene.camera.location=target+Vector((1,-1,.65));scene.camera.rotation_euler=(target-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=.48
scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.filepath=str(ROOT/'art-src/previews/bailiff-menacing-grip.png');bpy.ops.render.render(write_still=True)
scene.camera.location=old_location;scene.camera.rotation_euler=old_rotation;scene.camera.data.ortho_scale=old_scale
print('MENACING_BAILIFF_READY',len(parts),flush=True)
