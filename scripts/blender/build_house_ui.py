"""Gate to Hell: editable Blender UI/scenery and looping sprite exports.

Run: blender -b -t 4 -P scripts/blender/build_house_ui.py
Optional after --: names of assets to rebuild (e.g. arena_floor coin).
All artwork is modeled geometry. ImageMagick only packs rendered frames.
"""
import bpy
import math
import pathlib
import random
import subprocess
import sys
from mathutils import Vector

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/ui'
FRAMES = ROOT / 'art-src/ui-frames'
OUT.mkdir(parents=True, exist_ok=True)
FRAMES.mkdir(parents=True, exist_ok=True)
C = {
    'ink': (0.018, 0.033, 0.043), 'felt': (0.025, 0.085, 0.084),
    'teal': (0.045, 0.16, 0.155), 'stone': (0.065, 0.105, 0.115),
    'stone2': (0.085, 0.13, 0.135), 'gold': (0.65, 0.38, 0.12),
    'bright': (0.95, 0.7, 0.3), 'ember': (1, 0.24, 0.035),
    'bone': (0.7, 0.67, 0.53), 'muted': (0.12, 0.16, 0.17),
    'Pyro': (1, 0.24, 0.1), 'Hydro': (0.13, 0.6, 0.95),
    'Anemo': (0.22, 0.8, 0.55), 'Geo': (0.9, 0.62, 0.15),
    'Dendro': (0.33, 0.65, 0.12), 'Cryo': (0.4, 0.82, 0.95),
    'Electro': (0.6, 0.28, 0.95), 'Gravity': (0.48, 0.2, 0.8),
    'Antimatter': (0.95, 0.24, 0.53),
}
S = None
ANIM = []
MATERIALS = {}


def mat(key, glow=False):
    cache = (key, glow)
    if cache in MATERIALS:
        return MATERIALS[cache]
    m = bpy.data.materials.new(key + (' Glow' if glow else ''))
    dark = key in ('ink', 'felt', 'teal', 'stone', 'stone2', 'muted') or key.startswith('slab_')
    color = tuple(v * .18 for v in C[key]) if dark else C[key]
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    n = m.node_tree.nodes.get('Principled BSDF')
    n.inputs['Base Color'].default_value = (*color, 1)
    n.inputs['Roughness'].default_value = 0.4 if key in ('gold', 'bright') else 0.8
    n.inputs['Metallic'].default_value = 0.65 if key in ('gold', 'bright') else 0.1
    n.inputs['Emission Color'].default_value = (*color, 1)
    n.inputs['Emission Strength'].default_value = 1.4 if glow else 0.17
    MATERIALS[cache] = m
    return m


def link(ob, key):
    for coll in list(ob.users_collection):
        coll.objects.unlink(ob)
    S.collection.objects.link(ob)
    ob.data.materials.append(mat(key))
    return ob


def box(name, size, loc=(0, 0, 0), key='ink', bevel=0.025):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = link(bpy.context.object, key)
    ob.name = name
    ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = ob.modifiers.new('Machined edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 2
        ob.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return ob


def disc(name, radius, loc=(0, 0, 0), key='gold', depth=0.08, sides=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=sides, radius=radius, depth=depth, location=loc)
    ob = link(bpy.context.object, key)
    ob.name = name
    b = ob.modifiers.new('Coin rim bevel', 'BEVEL')
    b.width = 0.015
    b.segments = 2
    ob.modifiers.new('Weighted normals', 'WEIGHTED_NORMAL')
    return ob


def gem(name, radius, loc=(0, 0, 0), key='ember', glow=True):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=radius, location=loc)
    ob = link(bpy.context.object, key)
    ob.name = name
    ob.data.materials[0] = mat(key, glow)
    return ob


def line(name, points, key='gold', width=0.012, closed=False, glow=False):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = width
    curve.bevel_resolution = 1
    spline = curve.splines.new('POLY')
    spline.points.add(len(points) - 1)
    for p, co in zip(spline.points, points):
        p.co = (*co, 1)
    spline.use_cyclic_u = closed
    ob = bpy.data.objects.new(name, curve)
    S.collection.objects.link(ob)
    curve.materials.append(mat(key, glow))
    return ob


def ring(name, radius, z=0.12, key='gold', width=0.012, loc=(0, 0)):
    return line(name, [(loc[0]+radius*math.cos(i*math.tau/64),
                       loc[1]+radius*math.sin(i*math.tau/64), z) for i in range(64)], key, width, True)


def scene(name, width, height, ortho, iso=False, opaque=False):
    global S, ANIM
    ANIM = []
    S = bpy.data.scenes.new(name)
    bpy.context.window.scene = S
    S.render.engine = 'CYCLES'
    S.cycles.samples = 16
    S.cycles.use_denoising = True
    S.render.threads_mode = 'FIXED'
    S.render.threads = 4
    S.render.resolution_x, S.render.resolution_y = width, height
    S.render.resolution_percentage = 100
    S.render.film_transparent = not opaque
    S.render.image_settings.file_format = 'PNG'
    S.render.image_settings.color_mode = 'RGBA'
    S.render.image_settings.compression = 85
    S.view_settings.view_transform = 'Standard'
    S.world = bpy.data.worlds.new(name+' World')
    S.world.use_nodes = True
    S.world.node_tree.nodes['Background'].inputs[0].default_value = (0.12, 0.18, 0.22, 1)
    S.world.node_tree.nodes['Background'].inputs[1].default_value = 0.4
    cd = bpy.data.cameras.new(name+' Camera')
    cd.type, cd.ortho_scale = 'ORTHO', ortho
    cam = bpy.data.objects.new(name+' Camera', cd)
    S.collection.objects.link(cam)
    cam.location = (8, 8, math.sqrt(128/3)) if iso else (0, 0, 10)
    cam.rotation_euler = (Vector((0, 0, 0))-cam.location).to_track_quat('-Z', 'Y').to_euler()
    S.camera = cam
    for loc, power, color, size in [((-3, -4, 7), 850, (1, 0.82, 0.6), 5),
                                     ((4, 3, 6), 500, (0.3, 0.75, 0.85), 4)]:
        ld = bpy.data.lights.new('Softbox', 'AREA')
        ld.energy, ld.color, ld.size = power, color, size
        ob = bpy.data.objects.new('Softbox', ld)
        S.collection.objects.link(ob)
        ob.location = loc
        ob.rotation_euler = (-ob.location).to_track_quat('-Z', 'Y').to_euler()
    S.frame_start, S.frame_end = 1, 9
    S.render.fps = 8


def frame(w=2, h=2, state='normal'):
    key = 'muted' if state == 'disabled' else 'bright' if state == 'hover' else 'gold'
    box('Obsidian casting', (w, h, .1), key='ink', bevel=.065)
    box('Brass rim', (w-.06, h-.06, .04), (0, 0, .07), key, .045)
    box('Recessed velvet', (w-.13, h-.13, .04), (0, 0, .095),
        'muted' if state == 'disabled' else 'teal' if state == 'hover' else 'felt', .035)
    # Small corner ornaments fit the runtime's fixed nine-slice corners.
    for x in (-w/2+.11, w/2-.11):
        for y in (-h/2+.11, h/2-.11):
            ob = box('Diamond brass rivet', (.06, .06, .025), (x, y, .14), key, .006)
            ob.rotation_euler.z = math.pi/4
    return key


def backdrop(title=False, arena=False):
    box('Table', (16, 9, .12), key='ink' if arena else 'felt', bevel=0)
    # Quiet centre, layered architectural decoration at the periphery.
    for w, h in [(15.2, 8.95), (14.98, 8.82)]:
        line('Table inlay', [(-w/2,-h/2,.09),(w/2,-h/2,.09),(w/2,h/2,.09),(-w/2,h/2,.09)],
             'gold', .015, True)
    rng = random.Random(12)
    for i in range(150):
        x, y = rng.uniform(-7.4,7.4), rng.uniform(-4,4)
        # Tiny sculpted felt stitches, subdued enough for text overlay.
        box('Felt grain', (.014,.05,.006), (x,y,.09), 'teal', 0)
    for x in (-7.25, 7.25):
        for y in (-4.2, 4.2):
            ring('Corner flourish', .20, .1, 'gold', .014, (x,y))
            ob = box('Corner suit', (.12,.12,.03),(x,y,.13),'gold')
            ob.rotation_euler.z = math.pi/4
    if title:
        # A fan of real beveled playing cards, placed away from the title copy.
        for i in range(5):
            x,y = 3.4+i*.28, .4+i*.11
            ob = box('House deck', (1.5,2.3,.06),(x,y,.13+i*.07),'gold',.06)
            ob.rotation_euler.z = -.3+i*.14
            inner = box('Card back felt', (1.38,2.18,.025),(x,y,.18+i*.07),'teal',.04)
            inner.rotation_euler.z = ob.rotation_euler.z
        for x,y in [(6.5,2.8),(5.9,-1.8)]:
            disc('Scattered chips', .37,(x,y,.2),'gold')
            disc('Chip centre', .27,(x,y,.25),'ink')
        ring('House sigil', 1.15,.65,'gold',.025,(4.1,1.0))
    if arena:
        for x in (-7.2,7.2):
            for y in (-2,0,2):
                ob=box('Gallery paving',(.8,.8,.05),(x,y,.15),'stone')
                ob.rotation_euler.z=math.pi/4


def floor(element=None):
    # Coordinates / 100 match iso.lua exactly: orthographic 2:1 projection.
    box('Floating obsidian plinth', (7.14,7.14,.3),(0,0,-.19),'ink',.06)
    box('Brass foundation band',(7.08,7.08,.08),(0,0,-.1),'gold',.025)
    box('Stone edging',(7.0,7.0,.06),(0,0,-.035),'stone',.01)
    rng=random.Random(19)
    keys = ['stone', 'stone2']
    if element:
        keys = ['slab_'+element, 'slab_'+element+'_light']
        for key, base in zip(keys, ['stone', 'stone2']):
            C[key] = tuple(v * .72 + c * .045 for v,c in zip(C[base],C[element]))
    for i in range(10):
        for j in range(10):
            box('Slab %02d %02d'%(i,j),(.686,.686,.055),
                (-3.15+i*.7,-3.15+j*.7,-.028), keys[1] if rng.random()<.3 else keys[0],.009)
    # No decorative objects inside the playable square and no collision changes.
    for size in (6.96,6.80):
        v=size/2
        line('Perimeter brass inlay',[(-v,-v,.007),(v,-v,.007),(v,v,.007),(-v,v,.007)],'gold',.009,True)
    ring('Quiet central seal',1.25,.008,'teal',.018)
    ring('Quiet central seal inner',1.16,.008,'teal',.008)
    for i in range(8):
        a=i*math.pi/4
        line('Seal ray',[(math.cos(a)*1.0,math.sin(a)*1.0,.009),
                         (math.cos(a)*1.13,math.sin(a)*1.13,.009)],'teal',.013)
    for x,y in [(-3.3,-3.3),(3.3,3.3),(-3.3,3.3),(3.3,-3.3)]:
        ob=box('Corner seal',(.17,.17,.015),(x,y,.012),'gold',.01)
        ob.rotation_euler.z=math.pi/4


def symbol(element, z=.18):
    def stroke(points, closed=False):
        return line(element+' glyph',[(x,y,z) for x,y in points],element,.035,closed,True)
    if element=='Pyro':
        stroke([(0,.42),(.29,.03),(.2,-.27),(0,-.38),(-.25,-.22),(-.28,.02),(-.1,.21),(-.07,-.07),(.1,.0)],True)
    elif element=='Hydro':
        stroke([(0,.43),(.24,.05),(.28,-.18),(.13,-.35),(-.13,-.35),(-.28,-.18),(-.24,.05)],True)
        stroke([(-.12,-.15),(0,-.22),(.12,-.15)])
    elif element=='Anemo':
        stroke([(-.38,.16),(.2,.16),(.32,.28),(.4,.16),(.28,.03)])
        stroke([(-.33,-.08),(.13,-.08),(.25,-.23),(.12,-.34)])
        stroke([(-.26,-.3),(-.02,-.3)])
    elif element=='Geo':
        stroke([(0,.4),(.35,0),(0,-.4),(-.35,0)],True)
        stroke([(0,.17),(.15,0),(0,-.17),(-.15,0)],True)
    elif element=='Dendro':
        stroke([(-.26,-.28),(-.29,.1),(-.06,.3),(.36,.36),(.29,-.06),(.09,-.29)],True)
        stroke([(-.34,-.36),(.2,.18)])
    elif element=='Cryo':
        for i in range(6):
            a=i*math.pi/3
            stroke([(0,0),(.4*math.cos(a),.4*math.sin(a))])
            gem('Snow node',.05,(.27*math.cos(a),.27*math.sin(a),z),element)
    elif element=='Electro':
        stroke([(.1,.42),(-.3,-.05),(-.02,-.05),(-.12,-.4),(.33,.1),(.07,.1)],True)
    elif element=='Gravity':
        for sx,sy in [(1,.4),(.4,1)]:
            stroke([(.4*sx*math.cos(i*math.tau/48),.4*sy*math.sin(i*math.tau/48)) for i in range(48)],True)
        gem('Gravity core',.085,(0,0,z),element)
    else:
        stroke([(0,.42),(.36,-.27),(-.36,-.27)],True)
        stroke([(0,-.42),(-.36,.27),(.36,.27)],True)


def animate(ob, kind):
    ANIM.append((ob, kind, ob.location.copy(), ob.scale.copy()))
    for f in range(1,10):
        phase=(f-1)*math.tau/8
        if kind=='spin':
            ob.rotation_euler.z=phase
            ob.keyframe_insert(data_path='rotation_euler', frame=f)
        else:
            factor=1+(.12 if kind=='flame' else .06)*math.sin(phase)
            ob.scale=tuple(v*factor for v in ANIM[-1][3])
            ob.keyframe_insert(data_path='scale', frame=f)
            if kind=='float':
                ob.location.z=ANIM[-1][2].z+.04*math.sin(phase)
                ob.keyframe_insert(data_path='location', frame=f)


def animated(name):
    if name=='floor_rune':
        ring('Awakening seal',.47,.0,'bone',.009)
        ring('Inner seal',.41,.0,'bone',.005)
        for i in range(8):
            a=i*math.pi/4
            line('Seal tick',[(math.cos(a)*.34,math.sin(a)*.34,0),
                              (math.cos(a)*.4,math.sin(a)*.4,0)],'bone',.008)
        root=bpy.data.objects.new('Animated floor seal',None)
        S.collection.objects.link(root)
        for ob in list(S.objects):
            if ob.type=='CURVE':
                ob.parent=root
        animate(root,'float')
    elif name=='coin':
        disc('Gold coin',.48,(0,0,0),'gold')
        ring('Milled rim',.40,.07,'bright',.024)
        disc('Obsidian coin inset',.33,(0,0,.06),'ink',.025)
        ob=box('House diamond',(.31,.31,.06),(0,0,.11),'bright',.02)
        ob.rotation_euler.z=math.pi/4
        animate(ob,'spin')
    elif name=='infinity_key':
        ring('Infinity left bow',.15,.10,'bright',.04,(-.32,.22))
        ring('Infinity right bow',.15,.10,'bright',.04,(-.07,.22))
        line('Key stem',[(-.05,.03,.1),(.35,-.37,.1),(.45,-.27,.1),(.35,-.17,.1)],'gold',.06)
        animate(gem('Key ember',.12,(-.22,.18,.12),'ember'),'float')
    elif name=='brazier':
        disc('Brazier foot',.27,(0,0,-.15),'ink',.18,8)
        disc('Brass bowl',.33,(0,0,0),'gold',.12,8)
        for x,y in [(-.09,0),(.09,0),(0,.07)]:
            ob=gem('Low poly flame',.23,(x,y,.24),'ember')
            ob.scale=(.55,.55,1.5)
            animate(ob,'flame')
        animate(gem('Flame heart',.13,(0,-.06,.19),'bright'),'flame')
    elif name=='ember_seal':
        ring('Seal bezel',.44,.05,'gold',.022)
        ob=box('Diamond setting',(.55,.55,.06),(0,0,.08),'gold')
        ob.rotation_euler.z=math.pi/4
        animate(gem('Cinder heart',.27,(0,0,.17),'ember'),'float')
    elif name=='cardback':
        frame(1.6,2.1)
        ring('Card seal',.46,.15,'gold',.022)
        for sy in (-1,1):
            line('Card filigree',[(-.45,sy*.66,.16),(0,sy*.86,.16),(.45,sy*.66,.16)],'gold',.015)
        animate(gem('Card ember',.25,(0,0,.23),'ember'),'float')
    else: # neutral, recolorable crystal for arena perimeter; never a warning color
        disc('Socket',.32,(0,0,-.1),'gold',.12,8)
        ob=gem('Element crystal',.32,(0,0,.17),'bone',False)
        ob.scale=(.65,.65,1.2)
        animate(ob,'float')


ITEMS=['scepter','ember','tide','gale','quarry','thorn','rime','coil','die','ace',
       'tab','fuse','glass','ash','rain','tailwind','stone','green','cold','copper','flask','aegis','wind']
ELEMENTS=['Pyro','Hydro','Anemo','Geo','Dendro','Cryo','Electro','Gravity','Antimatter']


def item(name):
    key={'ember':'Pyro','tide':'Hydro','gale':'Anemo','quarry':'Geo','thorn':'Dendro',
         'rime':'Cryo','coil':'Electro','ash':'Pyro','rain':'Hydro','tailwind':'Anemo',
         'stone':'Geo','green':'Dendro','cold':'Cryo','copper':'Electro',
         'flask':'Pyro','wind':'Anemo'}.get(name,'bright')
    if name in ITEMS[:8]:
        line('Weapon shaft',[(-.25,-.35,.1),(.2,.3,.1)],'gold',.045)
        if name=='quarry':
            ob=box('Hammer head',(.48,.25,.15),(.15,.25,.16),'Geo')
            ob.rotation_euler.z=-.5
        elif name=='thorn':
            line('Bow limbs',[(-.32,-.32,.12),(-.34,.05,.12),(0,.38,.12),(.35,.34,.12)],key,.035)
            line('Bow string',[(-.32,-.32,.12),(.35,.34,.12)],'bone',.008)
        elif name=='gale':
            line('Sling',[(-.2,.32,.12),(0,.05,.12),(.35,.25,.12)],key,.045)
        elif name=='coil':
            for j in range(3):
                ring('Coil winding',.14,.14+j*.015,key,.028,(-.04+j*.06,.05+j*.06))
        else:
            gem('Weapon tip',.18,(.2,.3,.15),key)
    elif name=='die':
        box('Loaded die',(.66,.66,.16),key='bone',bevel=.07)
        for x,y in [(-.17,-.17),(0,0),(.17,.17)]:
            disc('Die pip',.055,(x,y,.105),'ink',.018,12)
    elif name in ('ace','tab','glass','green','cold'):
        box('Receipt card',(.53,.74,.08),key='gold')
        box('Receipt inset',(.45,.66,.02),(0,0,.06),'ink')
        if name=='ace':
            ob=box('Ace diamond',(.21,.21,.03),(0,0,.1),'bright')
            ob.rotation_euler.z=math.pi/4
        else:
            for i in range(3):
                line('Engraved receipt',[(-.14,.18-i*.16,.1),(.14,.18-i*.16,.1)],key,.015)
    elif name=='flask':
        disc('Red flask',.25,(0,-.1,.05),'Pyro',.14,12)
        box('Flask neck',(.18,.23,.12),(0,.2,.08),'Pyro')
        box('Flask stopper',(.24,.1,.1),(0,.35,.1),'gold')
    elif name=='aegis':
        line('Pocket shield',[(-.3,.3,.1),(.3,.3,.1),(.25,-.12,.1),(0,-.4,.1),(-.25,-.12,.1)],'gold',.055,True)
        gem('Shield stone',.15,(0,0,.12),'Geo')
    elif name=='fuse':
        line('Velvet fuse',[(-.3,-.2,.1),(-.22,.2,.1),(.12,.28,.1),(.3,-.05,.1)],'Pyro',.06)
        gem('Fuse spark',.1,(.3,-.05,.15),'ember')
    else:
        disc('Curio token',.37,(0,0,.03),'gold')
        disc('Token inset',.29,(0,0,.09),'ink',.03)
        element={'ash':'Pyro','rain':'Hydro','tailwind':'Anemo','stone':'Geo',
                 'copper':'Electro','wind':'Anemo'}.get(name)
        if element:
            symbol(element,.13)
        else:
            gem('Lucky ember',.19,(0,0,.14),key)


def render(name, frames=1):
    paths=[]
    for i in range(frames):
        S.frame_set(i+1)
        p=(FRAMES/(name+'_%02d.png'%i)) if frames>1 else OUT/(name+'.png')
        S.render.filepath=str(p)
        bpy.ops.render.render(write_still=True)
        paths.append(str(p))
    if frames>1:
        subprocess.run(['magick','montage',*paths,'-background','none','-tile',str(frames)+'x1',
                        '-geometry','+0+0',str(OUT/(name+'.png'))],check=True)
    S.frame_set(1)
    print('ASSET_DONE',name,flush=True)


def main():
    selected=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    all_names=['button','button_hover','button_disabled','panel','card','slot','bar_track',
               'bg_screen','bg_title','bg_arena','arena_floor','coin','infinity_key',
               'brazier','ember_seal','cardback','crystal','floor_rune','elements','items']
    all_names += ['arena_floor_'+e.lower() for e in ELEMENTS]
    for name in all_names:
        if selected and name not in selected:
            continue
        if name.startswith('button'):
            scene(name,192,64,3)
            frame(3,1,name.split('_')[-1] if '_' in name else 'normal')
            render(name)
        elif name in ('panel','card','slot','bar_track'):
            scene(name,128,128,2)
            frame(state='disabled' if name=='slot' else 'normal')
            render(name)
        elif name.startswith('bg_'):
            scene(name,1280,720,16,opaque=True)
            backdrop(title=name=='bg_title',arena=name=='bg_arena')
            render(name)
        elif name.startswith('arena_floor'):
            scene(name,1280,720,1280/(78*math.sqrt(2)),iso=True)
            element=next((e for e in ELEMENTS if name=='arena_floor_'+e.lower()),None)
            floor(element)
            render(name)
        elif name in ('elements','items'):
            paths=[]
            for i,entry in enumerate(ELEMENTS if name=='elements' else ITEMS):
                scene(name+' '+entry,96,96,1.2)
                if name=='elements':
                    disc('Medallion brass',.49,key='gold')
                    disc('Medallion velvet',.435,(0,0,.06),'ink',.035)
                    ring('Inner bezel',.40,.10,'gold',.009)
                    symbol(entry)
                else:
                    item(entry)
                S.render.filepath=str(FRAMES/(name+'_%02d.png'%i))
                bpy.ops.render.render(write_still=True)
                paths.append(S.render.filepath)
            subprocess.run(['magick','montage',*paths,'-background','none','-tile','8x',
                            '-geometry','96x96+0+0',str(OUT/(name+'.png'))],check=True)
            print('ASSET_DONE',name,flush=True)
        else:
            is_card=name=='cardback'
            is_rune=name=='floor_rune'
            scene(name,256 if is_rune else 160 if is_card else 96,
                  128 if is_rune else 208 if is_card else 96,
                  1.2 if is_rune else 2.1 if is_card else 1.2,
                  iso=name in ('brazier','floor_rune'))
            animated(name)
            render(name,8)
    source=ROOT/'art-src/blender/house-ui.blend'
    # Partial rebuilds get separate sources, preserving the complete library.
    if selected:
        source=source.with_name('house-ui-'+'-'.join(selected)+'.blend')
    bpy.ops.wm.save_as_mainfile(filepath=str(source))
    print('LIBRARY_DONE',source,flush=True)


if __name__=='__main__':
    main()
