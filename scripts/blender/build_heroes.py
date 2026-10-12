"""Model reference-inspired articulated heroes and render true isometric atlases.

blender -b -t 4 -P scripts/blender/build_heroes.py
Optional: -- --heroes jack penny --preview (model and render an inspection image).
Render batches put evaluated animated geometry into camera-aligned cells: each
direction is one render, not 42 separate renders. No flat reference is projected
onto the model. The original portraits are packed into the editable source.
"""
import argparse
import bpy
import json
import math
import pathlib
import subprocess
import sys
import numpy as np
from mathutils import Vector, Matrix

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets/heroes/isometric'
PREVIEW = ROOT / 'art-src/previews/heroes'
OUT.mkdir(parents=True, exist_ok=True)
PREVIEW.mkdir(parents=True, exist_ok=True)
IDS = ['jack','match','penny','dealer','gale','zephyr','flint','mason','clover',
       'briar','frost','whiteout','volt','count','crown','oracle','null','laugh']
ELEMENTS = ['Pyro','Pyro','Hydro','Hydro','Anemo','Anemo','Geo','Geo','Dendro',
            'Dendro','Cryo','Cryo','Electro','Electro','Gravity','Gravity','Antimatter','Antimatter']
MELEE = {'jack','gale','flint','mason','frost','volt','laugh'}
COLORS = {'Pyro':(1,.16,.035),'Hydro':(.03,.48,.95),'Anemo':(.06,.68,.45),
          'Geo':(.9,.51,.10),'Dendro':(.22,.56,.035),'Cryo':(.3,.73,1),
          'Electro':(.48,.11,.9),'Gravity':(.33,.06,.65),'Antimatter':(.85,.05,.4)}
PALETTES = {
 'jack':((.20,.07,.025),(.48,.18,.045),(.08,.1,.11)),
 'match':((.025,.015,.025),(.23,.015,.035),(.005,.008,.014)),
 'penny':((.015,.40,.44),(.025,.18,.48),(.045,.035,.07)),
 'dealer':((.018,.025,.065),(.045,.085,.17),(.01,.012,.024)),
 'gale':((.016,.22,.12),(.44,.26,.10),(.62,.23,.035)),
 'zephyr':((.016,.22,.54),(.05,.54,.7),(.015,.40,.46)),
 'flint':((.24,.28,.32),(.08,.1,.14),(.045,.055,.08)),
 'mason':((.51,.22,.025),(.26,.08,.02),(.24,.07,.018)),
 'clover':((.025,.23,.045),(.15,.38,.09),(.045,.03,.022)),
 'briar':((.008,.12,.065),(.018,.26,.13),(.012,.016,.023)),
 'frost':((.08,.29,.55),(.25,.6,.86),(.31,.65,.87)),
 'whiteout':((.26,.56,.78),(.65,.83,.95),(.65,.81,.91)),
 'volt':((.095,.02,.21),(.35,.10,.49),(.13,.025,.21)),
 'count':((.47,.13,.035),(.15,.045,.025),(.12,.026,.02)),
 'crown':((.085,.016,.16),(.25,.045,.42),(.035,.008,.065)),
 'oracle':((.025,.018,.07),(.27,.06,.32),(.02,.01,.045)),
 'null':((.045,.014,.10),(.19,.025,.30),(.03,.008,.055)),
 'laugh':((.36,.008,.085),(.08,.01,.09),(.24,.015,.075)),
}
ANIMS = [('idle',6,10,True),('walk',6,12,True),('attack',6,18,False),
         ('skill',6,12,False),('dodge',6,24,False),('hurt',6,20,False),('death',6,8,False)]
SCENE = None
PARTS = []
PIVOTS = {}
MATS = {}


def material(name, color, metallic=0, glow=0):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Metallic'].default_value=metallic
    p.inputs['Roughness'].default_value=.45 if metallic else .8
    p.inputs['Emission Color'].default_value=(*color,1)
    p.inputs['Emission Strength'].default_value=glow
    return m


def attach(ob, key, pivot):
    for coll in list(ob.users_collection):
        coll.objects.unlink(ob)
    SCENE.collection.objects.link(ob)
    ob.data.materials.clear()
    ob.data.materials.append(MATS[key])
    bpy.context.view_layer.update()
    world=ob.matrix_world.copy()
    ob.parent=PIVOTS[pivot]
    ob.matrix_parent_inverse=ob.parent.matrix_world.inverted()
    ob.matrix_world=world
    PARTS.append(ob)
    return ob


def box(name, loc, size, key='cloth', pivot='chest', bevel=.025):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    ob=bpy.context.object
    ob.name=name
    ob.scale=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        mod=ob.modifiers.new('Tailored edge','BEVEL');mod.width=bevel;mod.segments=2
        ob.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return attach(ob,key,pivot)


def sphere(name, loc, scale, key='skin', pivot='head', smooth=True):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=1,location=loc)
    ob=bpy.context.object;ob.name=name;ob.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if smooth:
        for p in ob.data.polygons:p.use_smooth=True
    return attach(ob,key,pivot)


def rod(name, a, b, radius, key='gold', pivot='chest', tip=None):
    a,b=Vector(a),Vector(b);v=b-a
    bpy.ops.mesh.primitive_cone_add(vertices=10,radius1=radius,
        radius2=radius if tip is None else tip,depth=v.length,location=(a+b)/2)
    ob=bpy.context.object;ob.name=name
    ob.rotation_euler=v.to_track_quat('Z','Y').to_euler()
    return attach(ob,key,pivot)


def jewel(name, loc, scale, key='element', pivot='chest'):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=loc)
    ob=bpy.context.object;ob.name=name;ob.scale=scale
    return attach(ob,key,pivot)


def ring(name, loc, radius, key='gold', pivot='chest', rotation=(0,0,0), minor=.015):
    bpy.ops.mesh.primitive_torus_add(major_segments=24,minor_segments=6,
        major_radius=radius,minor_radius=minor,location=loc,rotation=rotation)
    ob=bpy.context.object;ob.name=name
    return attach(ob,key,pivot)


def skirt(name, top, bottom, ztop, zbottom, key='cloth', pivot='hips', n=16):
    verts=[]
    for z,r in [(ztop,top),(zbottom,bottom)]:
        for i in range(n):
            a=i*math.tau/n;pleat=1.04 if i%2 else .96
            verts.append((math.cos(a)*r*pleat,math.sin(a)*r*.77*pleat,z))
    faces=[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    faces.append(tuple(range(n,2*n)))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new(name,mesh);SCENE.collection.objects.link(ob)
    return attach(ob,key,pivot)


def leaf(name, loc, size=.13, key='leaf', pivot='chest', angle=0):
    ob=jewel(name,loc,(size*.5,.035,size),key,pivot)
    ob.rotation_euler.y=angle
    return ob


def flower(loc, pivot='head'):
    for i in range(5):
        a=i*math.tau/5
        sphere('Flower petal',(loc[0]+.052*math.cos(a),loc[1],loc[2]+.052*math.sin(a)),
               (.044,.018,.045),'pink',pivot)
    jewel('Flower centre',(loc[0],loc[1]-.018,loc[2]),(.025,.022,.025),'gold',pivot)


def setup(name):
    global SCENE,PARTS,PIVOTS,MATS
    PARTS=[];PIVOTS={}
    SCENE=bpy.data.scenes.new(name)
    bpy.context.window.scene=SCENE
    SCENE.render.engine='CYCLES';SCENE.cycles.samples=8;SCENE.cycles.use_denoising=True
    SCENE.render.threads_mode='FIXED';SCENE.render.threads=4
    SCENE.render.film_transparent=True
    SCENE.render.image_settings.file_format='PNG';SCENE.render.image_settings.color_mode='RGBA'
    SCENE.render.image_settings.compression=85
    SCENE.view_settings.view_transform='Standard'
    SCENE.world=bpy.data.worlds.new(name+' World');SCENE.world.use_nodes=True
    SCENE.world.node_tree.nodes['Background'].inputs[0].default_value=(.23,.28,.33,1)
    SCENE.world.node_tree.nodes['Background'].inputs[1].default_value=.45
    for label,rotation,energy,color in [('Key',(25,-20,-35),2.2,(1,.9,.78)),
                                        ('Fill',(50,0,145),.8,(.55,.72,1)),
                                        ('Rim',(-40,15,20),1.2,(.74,.83,1))]:
        data=bpy.data.lights.new(name+' '+label,'SUN');data.energy=energy;data.color=color;data.angle=.15
        ob=bpy.data.objects.new(data.name,data);SCENE.collection.objects.link(ob)
        ob.rotation_euler=tuple(math.radians(a) for a in rotation)
    camera=bpy.data.cameras.new(name+' Camera');camera.type='ORTHO';camera.ortho_scale=3.2
    camera.sensor_fit='HORIZONTAL'
    cam=bpy.data.objects.new(camera.name,camera);SCENE.collection.objects.link(cam)
    target=Vector((0,0,1.34));cam.location=target+Vector((6,-6,math.sqrt(24)))
    cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();SCENE.camera=cam
    SCENE.render.resolution_x=160;SCENE.render.resolution_y=192;SCENE.render.resolution_percentage=100
    palette=PALETTES[name];element=ELEMENTS[IDS.index(name)]
    MATS={
        'cloth':material(name+' | main cloth',palette[0]),
        'accent':material(name+' | secondary cloth',palette[1]),
        'hair':material(name+' | hair',palette[2]),
        'skin':material(name+' | warm skin',(.65,.36,.23) if name in ('jack','mason') else (.8,.53,.39)),
        'gold':material(name+' | antique brass',(.59,.33,.085),.65),
        'steel':material(name+' | silver steel',(.26,.32,.39),.65),
        'dark':material(name+' | dark seams',(.012,.019,.028)),
        'white':material(name+' | ivory',(.82,.86,.9)),
        'element':material(name+' | elemental light',COLORS[element],.1,1.3),
        'leaf':material(name+' | leaves',(.024,.23,.065)),
        'pink':material(name+' | flower pink',(.82,.075,.31)),
        'rock':material(name+' | rock',(.34,.19,.055)),
    }
    positions={
        'root':((0,0,0),None),'hips':((0,0,.87),'root'),
        'chest':((0,0,1.24),'hips'),'head':((0,0,1.70),'chest'),
        'upper.L':((.3,0,1.40),'chest'),'upper.R':((-.3,0,1.40),'chest'),
        'fore.L':((.39,0,1.13),'upper.L'),'fore.R':((-.39,0,1.13),'upper.R'),
        'hand.L':((.45,0,.87),'fore.L'),'hand.R':((-.45,0,.87),'fore.R'),
        'thigh.L':((.14,0,.85),'hips'),'thigh.R':((-.14,0,.85),'hips'),
        'shin.L':((.14,0,.46),'thigh.L'),'shin.R':((-.14,0,.46),'thigh.R'),
        'foot.L':((.14,0,.14),'shin.L'),'foot.R':((-.14,0,.14),'shin.R'),
    }
    for key,(loc,parent) in positions.items():
        ob=bpy.data.objects.new(name+' | '+key,None);SCENE.collection.objects.link(ob)
        ob.empty_display_type='PLAIN_AXES';ob.empty_display_size=.1
        ob.location=loc;ob.rotation_mode='XYZ'
        if parent:
            ob.parent=PIVOTS[parent];ob.matrix_parent_inverse=ob.parent.matrix_world.inverted()
        PIVOTS[key]=ob
        bpy.context.view_layer.update()


def base(name):
    armored=name in ('flint','count','crown')
    gown=name in ('match','zephyr','whiteout','oracle')
    width=.32 if armored else .255
    sphere('Tailored torso',(0,0,1.22),(width,.17,.36),'cloth','chest')
    sphere('Hip silhouette',(0,0,.89),(.23,.145,.17),'accent','hips')
    box('Belt',(0,-.01,.94),(.45,.31,.08),'dark','hips',.012)
    box('Belt clasp',(0,-.18,.94),(.09,.035,.08),'gold','hips',.012)
    if gown:
        skirt('Pleated gown',.22,.39,1.02,.16)
        skirt('Contrasting gown hem',.39,.40,.23,.16,'accent')
    for sign,side in [(1,'L'),(-1,'R')]:
        x=sign*.14
        rod('Trouser thigh',(x,0,.87),(x,0,.49),.105,'accent','thigh.'+side)
        rod('Trouser shin',(x,0,.49),(x,0,.16),.083,'cloth','shin.'+side)
        box('Boot',(x,-.075,.115),(.18,.29,.20),'dark','foot.'+side,.035)
        rod('Sleeve upper',(sign*.28,0,1.40),(sign*.39,0,1.14),.105,'cloth','upper.'+side)
        rod('Sleeve lower',(sign*.39,0,1.14),(sign*.45,0,.90),.085,'accent','fore.'+side)
        sphere('Glove',(sign*.45,-.015,.86),(.087,.076,.11),
               'white' if name in ('dealer','frost','whiteout','oracle') else 'skin','hand.'+side)
    rod('Neck',(0,0,1.48),(0,0,1.68),.09,'skin','head')
    sphere('Face',(0,-.015,1.79),(.18,.16,.22),'skin','head')
    sphere('Hair cap',(0,.025,1.88),(.195,.16,.17),'hair','head')
    for sign in (-1,1):
        sphere('Ear',(sign*.174,.0,1.78),(.034,.046,.062),'skin','head')
        box('Eye',(sign*.071,-.168,1.805),(.049,.021,.022),'dark','head',.004)
        box('Brow',(sign*.071,-.166,1.847),(.067,.024,.018),'hair','head',.003)
    sphere('Nose',(0,-.176,1.765),(.036,.046,.045),'skin','head')
    box('Mouth',(0,-.156,1.696),(.075,.025,.011),'dark','head',.003)
    jewel('Element brooch',(0,-.18,1.28),(.063,.035,.079),'element','chest')


def coat(long=False):
    for sign in (-1,1):
        ob=box('Coat lapel',(sign*.09,-.169,1.40),(.085,.025,.28),'accent')
        ob.rotation_euler.y=sign*.27
        ob=box('Coat tail',(sign*.17,.10,.68 if long else .80),(.20,.06,.50 if long else .30),'cloth','hips')
        ob.rotation_euler.y=sign*.10


def crown(key='gold', height=.22):
    ring('Crown circlet',(0,0,1.985),.195,key,'head',minor=.028)
    for i in range(7):
        a=i*math.tau/7
        rod('Crown point',(.18*math.cos(a),.18*math.sin(a),1.99),
            (.21*math.cos(a),.21*math.sin(a),1.99+height),.045,key,'head',.005)
    jewel('Crown front jewel',(0,-.20,2.035),(.055,.025,.07),'element','head')


def staff(key='element', branch=False):
    rod('Casting staff',(-.45,-.07,.42),(-.45,-.07,1.82),.025,'hair' if branch else 'steel','hand.R')
    jewel('Staff focus',(-.45,-.07,1.86),(.085,.085,.18),key,'hand.R')
    if branch:
        for i in range(4):
            z=.85+i*.24
            rod('Thorn branch',(-.45,-.07,z),(-.64,-.07,z+.14),.012,'leaf','hand.R',0)
            leaf('Staff leaf',(-.63,-.07,z+.13),.095,pivot='hand.R',angle=-.7)


def blade(key='steel', short=False):
    rod('Sword grip',(-.45,-.08,.73),(-.45,-.08,.97),.035,'gold','hand.R')
    box('Sword guard',(-.45,-.08,.98),(.22,.065,.05),'gold','hand.R',.012)
    rod('Sword blade',(-.45,-.08,1.0),(-.45,-.08,1.50 if short else 1.76),.065,key,'hand.R',.002)


def fan(key='element'):
    for i in range(5):
        a=math.radians(-50+i*25)
        rod('Fan rib',(.45,-.06,.88),(.45+.29*math.sin(a),-.06,.88+.29*math.cos(a)),.012,'gold','hand.L')
        jewel('Fan element tip',(.45+.30*math.sin(a),-.06,.88+.30*math.cos(a)),(.037,.026,.08),key,'hand.L')


def dress(name):
    if name=='jack':
        coat()
        sphere('Miner steel helmet',(0,0,1.96),(.22,.20,.14),'steel','head')
        box('Helmet brim',(0,-.045,1.95),(.48,.39,.037),'steel','head')
        sphere('Headlamp bezel',(0,-.20,2.03),(.07,.037,.07),'gold','head')
        sphere('Headlamp',(0,-.233,2.03),(.05,.016,.05),'white','head')
        sphere('Rough beard',(0,-.085,1.66),(.13,.12,.11),'hair','head')
        for i in (-1,0,1):
            rod('Overall buckle strap',(i*.12,-.16,1.05),(i*.12,-.17,1.43),.018,'accent')
        fan();blade(short=True)
    elif name=='match':
        box('Bob fringe',(0,-.125,1.97),(.35,.095,.10),'hair','head')
        for sign in (-1,1):
            box('Bob sides',(sign*.17,.025,1.83),(.10,.23,.34),'hair','head')
            rod('Dress strap',(sign*.13,-.10,1.48),(sign*.13,-.17,1.30),.021,'cloth')
        jewel('Ruby pendant',(0,-.19,1.43),(.038,.023,.075),'pink')
        fan()
        ring('Kindling ring',(-.45,-.05,1.00),.19,'element','hand.R',rotation=(math.pi/2,0,0),minor=.012)
    elif name=='penny':
        sphere('Turquoise cap',(0,0,2.0),(.225,.20,.14),'cloth','head')
        box('Cap peak',(0,-.22,1.98),(.37,.22,.035),'cloth','head')
        box('Cap badge',(0,-.198,2.045),(.12,.032,.09),'white','head')
        box('Overall bib',(0,-.175,1.18),(.31,.035,.29),'accent')
        for sign in (-1,1):
            box('Overall strap',(sign*.13,-.18,1.37),(.052,.035,.22),'accent')
            jewel('Strap button',(sign*.13,-.203,1.32),(.025,.02,.025),'gold')
        staff()
    elif name=='dealer':
        coat(True)
        rod('Hat crown',(0,0,1.99),(0,0,2.27),.195,'cloth','head')
        rod('Fedora brim',(0,0,1.96),(0,0,2.0),.29,'cloth','head')
        ring('Hat band',(0,0,2.06),.197,'accent','head',minor=.023)
        box('White shirt',(0,-.179,1.40),(.16,.02,.28),'white')
        jewel('Silk tie',(0,-.199,1.38),(.035,.022,.15),'dark')
        for i in range(3):
            ob=box('Held playing card',(-.45+i*.04,-.11,.98+i*.015),(.13,.022,.20),'white','hand.R',.007)
            ob.rotation_euler.y=(i-1)*.25
            jewel('Card diamond',(-.45+i*.04,-.127,1.0+i*.015),(.032,.012,.042),'element','hand.R')
    elif name=='gale':
        coat(True)
        box('Cream waistcoat',(0,-.175,1.28),(.29,.035,.37),'white')
        sphere('Green hat',(0,0,2.02),(.25,.21,.10),'cloth','head')
        rod('Tricorn brim',(-.26,-.06,1.99),(.26,-.06,1.99),.05,'cloth','head')
        leaf('Hat feather',(.19,.03,2.19),.19,'white','head',-.5)
        for i in range(4):
            sphere('Orange hair locks',(-.14+i*.09,.12,1.77),(.05,.095,.16),'hair','head')
        blade();fan('white')
    elif name=='zephyr':
        for sign in (-1,1):
            sphere('Flowing teal hair',(sign*.19,.07,1.71),(.13,.15,.31),'hair','head')
            rod('Wind ribbon',(sign*.3,.13,1.21),(sign*.48,.20,1.02),.026,'white')
        ring('Wind waist orbit',(0,0,1.05),.39,'white','hips',minor=.01)
        ring('Wind shoulder orbit',(0,0,1.43),.42,'element',minor=.009)
        jewel('Wind charm',(-.45,-.04,.99),(.12,.08,.16),'element','hand.R')
    elif name=='flint':
        box('Knight cuirass',(0,-.02,1.23),(.62,.40,.53),'steel','chest',.055)
        box('Helmet',(0,0,1.87),(.40,.35,.43),'steel','head',.045)
        box('Dark visor',(0,-.192,1.85),(.31,.025,.057),'dark','head')
        box('Visor ridge',(0,-.21,1.82),(.045,.025,.22),'steel','head')
        for sign,side in [(1,'L'),(-1,'R')]:
            sphere('Broad pauldrons',(sign*.35,0,1.46),(.24,.22,.17),'steel','upper.'+side,False)
            box('Stone strike gauntlet',(sign*.46,0,.97),(.26,.28,.28),'steel','hand.'+side,.04)
            box('Armored greave',(sign*.14,-.015,.35),(.23,.25,.36),'steel','shin.'+side)
            jewel('Amber shoulder stone',(sign*.38,-.20,1.43),(.04,.025,.04),'element','upper.'+side)
    elif name=='mason':
        skirt('Mason leather apron',.24,.29,1.36,.45,'cloth')
        rod('Headband',(0,0,1.91),(0,0,1.98),.198,'cloth','head')
        sphere('Mason beard',(0,-.095,1.66),(.145,.12,.12),'hair','head')
        for sign,side in [(1,'L'),(-1,'R')]:
            for i in range(3):
                jewel('Floating quarry stone',(sign*(.31+i*.075),.05,1.38+i*.18),
                      (.09,.075,.12),'rock','upper.'+side)
            jewel('Stone fist',(sign*.45,-.02,.91),(.14,.13,.15),'rock','hand.'+side)
        box('Apron pocket',(0,-.21,1.04),(.22,.035,.16),'accent')
    elif name=='clover':
        for i in range(7):
            a=i*math.tau/7
            leaf('Flower crown leaf',(.19*math.cos(a),.15*math.sin(a),2.00),.09,pivot='head',angle=a)
        for loc in [(-.15,-.13,2.04),(.12,-.14,2.02),(0,-.185,2.06)]:flower(loc)
        for sign in (-1,1):
            for i in range(3):leaf('Leafy outfit',(sign*.17,-.16,1.08+i*.14),.10,angle=sign*.65)
        staff(branch=True)
        flower((.13,-.185,1.42),'chest')
    elif name=='briar':
        coat(True)
        box('Slick black hair',(0,.015,1.99),(.35,.27,.09),'hair','head')
        for sign in (-1,1):
            for i in range(3):leaf('Emerald coat foliage',(sign*(.20+i*.04),-.13,1.45+i*.04),.12,angle=sign*.75)
            rod('Gold coat piping',(sign*.14,-.178,1.1),(sign*.12,-.178,1.51),.008,'gold')
        staff(branch=True)
        jewel('Amethyst clasp',(0,-.196,1.48),(.05,.025,.07),'pink')
    elif name in ('frost','null'):
        key='accent';masked=name=='null'
        for sign in (-1,1):
            rod('Jester hat lobe',(sign*.07,.03,2.0),(sign*.27,.03,2.27),.11,key,'head',.018)
            rod('Jester drooping tip',(sign*.27,.03,2.27),(sign*.36,-.02,2.07),.045,key,'head',.003)
            jewel('Jester bell',(sign*.36,-.02,2.06),(.035,.035,.04),'element','head')
        for sign in (-1,1):
            jewel('Diamond collar',(sign*.16,-.18,1.51),(.13,.025,.11),'white' if not masked else 'accent')
        for z in (1.12,1.28,1.43):
            ob=box('Harlequin diamond',(0,-.187,z),(.09,.023,.09),'white' if masked else 'accent')
            ob.rotation_euler.y=math.pi/4
        if masked:
            sphere('Porcelain mask',(0,-.11,1.80),(.165,.09,.22),'white','head')
            for sign in (-1,1):
                ob=box('Mask dark eye',(sign*.065,-.197,1.84),(.071,.015,.027),'dark','head',.003)
                ob.rotation_euler.y=sign*.35
            rod('Mask smile',(-.07,-.198,1.73),(0,-.211,1.69),.012,'dark','head')
            rod('Mask smile',(0,-.211,1.69),(.07,-.198,1.73),.012,'dark','head')
            staff();blade('element',True)
        else:
            fan();blade('element',True)
    elif name=='whiteout':
        for sign in (-1,1):
            sphere('White hair cascade',(sign*.19,.08,1.70),(.13,.13,.36),'hair','head')
            jewel('Ice shoulder',(sign*.30,0,1.46),(.20,.14,.13),'white','upper.'+('L' if sign==1 else 'R'))
        crown('white',.18)
        for i in range(8):
            a=i*math.tau/8
            rod('Dress ice pleat',(.21*math.cos(a),.16*math.sin(a),.97),
                (.38*math.cos(a),.29*math.sin(a),.20),.012,'white','hips')
        jewel('Frost focus',(-.45,-.03,1.05),(.13,.10,.16),'element','hand.R')
    elif name=='volt':
        skirt('Purple split tunic',.22,.28,1.04,.71,'accent')
        for sign in (-1,1):
            sphere('Purple side hair',(sign*.17,.02,1.89),(.095,.16,.11),'hair','head')
            box('Page shoulder',(sign*.3,0,1.43),(.20,.26,.13),'accent','upper.'+('L' if sign==1 else 'R'))
        staff()
        rod('Spear wings',(-.58,-.07,1.79),(-.32,-.07,1.79),.022,'element','hand.R')
    elif name in ('count','crown'):
        box('Layered breastplate',(0,-.02,1.26),(.57,.36,.50),'cloth','chest',.045)
        for z in (1.02,1.15,1.29):
            box('Armor scale',(0,-.203,z),(.4,.045,.11),'accent')
        for sign,side in [(1,'L'),(-1,'R')]:
            jewel('Armored shoulder',(sign*.36,0,1.45),(.23,.19,.15),'accent','upper.'+side)
            box('Armored glove',(sign*.45,0,.96),(.20,.24,.22),'cloth','hand.'+side)
            box('Armored greave',(sign*.14,-.02,.35),(.21,.22,.34),'cloth','shin.'+side)
        coat(True)
        if name=='crown':
            crown('accent',.28)
            sphere('Violet king face',(0,-.115,1.8),(.17,.08,.21),'accent','head')
            for sign in (-1,1):
                box('Royal glowing eye',(sign*.065,-.194,1.84),(.05,.02,.018),'element','head',.003)
                rod('Crown armor spike',(sign*.35,.03,1.48),(sign*.54,.04,1.70),.05,'accent','upper.'+('L' if sign==1 else 'R'),0)
            jewel('Heavy gravity focus',(-.45,-.05,1.04),(.17,.14,.17),'element','hand.R')
        else:
            sphere('Copper helmet',(0,.03,1.96),(.22,.18,.20),'cloth','head')
            for sign in (-1,1):
                rod('Copper helmet horn',(sign*.18,.01,2.03),(sign*.22,-.02,2.24),.058,'accent','head',.004)
            jewel('Copper thunder palm',(-.45,-.1,.99),(.11,.10,.11),'element','hand.R')
            for sign in (-1,1):
                rod('Charged gauntlet seam',(sign*.44,-.11,1.0),(sign*.40,-.11,1.18),.009,'element','fore.'+('L' if sign==1 else 'R'))
    elif name=='oracle':
        sphere('Oracle hair veil',(0,.11,1.75),(.25,.13,.40),'hair','head')
        ring('Gold forehead circlet',(0,0,1.965),.194,'gold','head',minor=.014)
        jewel('Forehead ruby',(0,-.195,1.96),(.045,.03,.055),'pink','head')
        ring('Oracle collar',(0,0,1.49),.27,'gold','chest',minor=.025)
        ring('Planet orbit',(0,0,1.47),.64,'gold','chest',rotation=(.3,.15,0),minor=.01)
        for i,key in enumerate(['element','pink','white']):
            a=i*math.tau/3
            jewel('Orbiting planet',(.63*math.cos(a),.63*math.sin(a),1.48),(.085,.085,.085),key)
        for sign in (-1,1):
            rod('Gold gown piping',(sign*.15,-.178,1.46),(sign*.16,-.178,1.00),.008,'gold')
    elif name=='laugh':
        coat(True)
        box('Dark shirt',(0,-.183,1.37),(.16,.025,.31),'dark')
        jewel('Magenta tie',(0,-.202,1.37),(.028,.018,.15),'pink')
        for sign in (-1,1):
            for i in range(4):
                rod('Suit pinstripe',(sign*(.06+i*.045),-.18,1.06),(sign*(.06+i*.045),-.18,1.50),.003,'pink')
        for i in range(3):
            ob=box('Razor playing card',(-.45+i*.04,-.11,1.00+i*.01),(.14,.023,.21),'white','hand.R',.008)
            ob.rotation_euler.y=(i-1)*.22
            jewel('Razor card suit',(-.45+i*.04,-.128,1.00+i*.01),(.027,.015,.04),'pink','hand.R')
        for sign in (-1,1):
            rod('Wide grin',(sign*.09,-.17,1.70),(0,-.19,1.68),.014,'white','head')
        box('Slick magenta hair',(0,.01,1.99),(.35,.28,.09),'hair','head')


def animate(name):
    rests={k:p.location.copy() for k,p in PIVOTS.items()}
    for j,(pose,count,fps,loop) in enumerate(ANIMS):
        start=1+j*8
        SCENE.timeline_markers.new(pose.upper(),frame=start)
        for i in range(count+(1 if loop else 0)):
            u=i/count if loop else i/(count-1);pulse=math.sin(u*math.tau)
            for key,p in PIVOTS.items():
                p.location=rests[key];p.rotation_euler=(0,0,0)
            PIVOTS['upper.L'].rotation_euler.x=-.15
            PIVOTS['upper.R'].rotation_euler.x=-.20
            PIVOTS['fore.L'].rotation_euler.x=-.18
            PIVOTS['fore.R'].rotation_euler.x=-.25
            PIVOTS['root'].location.z=.012*pulse
            PIVOTS['chest'].rotation_euler.x=.018*pulse
            if pose=='walk':
                for sign,side in [(1,'L'),(-1,'R')]:
                    PIVOTS['thigh.'+side].rotation_euler.x=.40*pulse*sign
                    PIVOTS['shin.'+side].rotation_euler.x=-.26*max(0,pulse*sign)
                    PIVOTS['upper.'+side].rotation_euler.x=-.16-.28*pulse*sign
                PIVOTS['root'].location.z=.026*abs(pulse)
            elif pose=='attack':
                strength=math.sin(u*math.pi)
                if name in MELEE:
                    PIVOTS['chest'].rotation_euler.z=-.4*math.sin(u*math.tau)
                    PIVOTS['upper.R'].rotation_euler.x=-.25-1.1*strength
                    PIVOTS['upper.R'].rotation_euler.y=.7*math.sin(u*math.tau)
                    PIVOTS['fore.R'].rotation_euler.x=-.45*strength
                    PIVOTS['upper.L'].rotation_euler.x=-.25-.4*strength
                else:
                    PIVOTS['upper.R'].rotation_euler.x=-.20-1.15*strength
                    PIVOTS['fore.R'].rotation_euler.x=-.3-.25*strength
                    PIVOTS['chest'].rotation_euler.x=-.09*strength
            elif pose=='skill':
                strength=math.sin(u*math.pi)
                for sign,side in [(1,'L'),(-1,'R')]:
                    PIVOTS['upper.'+side].rotation_euler.x=-.2-.85*strength
                    PIVOTS['upper.'+side].rotation_euler.y=sign*.55*strength
                    PIVOTS['fore.'+side].rotation_euler.x=-.25-.4*strength
                PIVOTS['chest'].rotation_euler.x=-.12*strength
                PIVOTS['root'].location.z=.05*strength
            elif pose=='dodge':
                strength=math.sin(u*math.pi)
                PIVOTS['chest'].rotation_euler.x=.5*strength
                PIVOTS['hips'].location.z-=.16*strength
                PIVOTS['thigh.L'].rotation_euler.x=-.7*strength
                PIVOTS['thigh.R'].rotation_euler.x=.55*strength
                PIVOTS['upper.R'].rotation_euler.x=.5*strength
                PIVOTS['upper.L'].rotation_euler.x=.5*strength
            elif pose=='hurt':
                strength=math.sin(u*math.pi)
                PIVOTS['chest'].rotation_euler.x=-.3*strength
                PIVOTS['head'].rotation_euler.x=-.2*strength
                PIVOTS['upper.L'].rotation_euler.y=-.15*strength
                PIVOTS['upper.R'].rotation_euler.y=.15*strength
            elif pose=='death':
                ease=u*u*(3-2*u)
                # Collapse onto the knees; a prone full-height body would cross
                # neighboring sprite cells when viewed directly from the side.
                PIVOTS['root'].rotation_euler.x=-.20*ease
                PIVOTS['root'].location.z=-.08*ease
                PIVOTS['hips'].location.z-=.24*ease
                PIVOTS['thigh.L'].rotation_euler.x=-1.05*ease
                PIVOTS['thigh.R'].rotation_euler.x=-1.05*ease
                PIVOTS['shin.L'].rotation_euler.x=1.25*ease
                PIVOTS['shin.R'].rotation_euler.x=1.25*ease
                PIVOTS['chest'].rotation_euler.x=.65*ease
                PIVOTS['head'].rotation_euler.x=.40*ease
                PIVOTS['upper.L'].rotation_euler.y=-.15*ease
                PIVOTS['upper.R'].rotation_euler.y=.15*ease
            for p in PIVOTS.values():
                p.keyframe_insert(data_path='location',frame=start+i)
                p.keyframe_insert(data_path='rotation_euler',frame=start+i)
    SCENE.frame_start=1;SCENE.frame_end=54;SCENE.render.fps=12;SCENE.frame_set(1)


def pose_bank(source, parts):
    """Freeze evaluated articulated geometry once; share it between directions."""
    bank=[]
    bpy.context.window.scene=source
    for j,(pose,count,fps,loop) in enumerate(ANIMS):
        for i in range(count):
            source.frame_set(1+j*8+i)
            deps=bpy.context.evaluated_depsgraph_get()
            vertices=[];faces=[];slots=[];indices=[];smooth=[]
            for part in parts:
                evaluated=part.evaluated_get(deps)
                mesh=evaluated.to_mesh()
                world=evaluated.matrix_world
                offset=len(vertices)
                vertices.extend(tuple(world@v.co) for v in mesh.vertices)
                lookup=[]
                for material in mesh.materials:
                    if material not in slots:slots.append(material)
                    lookup.append(slots.index(material))
                for poly in mesh.polygons:
                    faces.append(tuple(offset+v for v in poly.vertices))
                    indices.append(lookup[poly.material_index]);smooth.append(poly.use_smooth)
                evaluated.to_mesh_clear()
            mesh=bpy.data.meshes.new(source.name+' | '+pose+' '+str(i))
            mesh.from_pydata(vertices,[],faces);mesh.update()
            for material in slots:mesh.materials.append(material)
            for poly,slot,is_smooth in zip(mesh.polygons,indices,smooth):
                poly.material_index=slot;poly.use_smooth=is_smooth
            bank.append([(mesh,Matrix.Identity(4),source.name+' | '+pose)])
    source.frame_set(1)
    return bank


def render_hero(name, source, parts, preview=False):
    folder=OUT/name;folder.mkdir(parents=True,exist_ok=True)
    if preview:
        source.render.resolution_x=480;source.render.resolution_y=576
        source.cycles.samples=32
        source.render.filepath=str(PREVIEW/(name+'-model.png'))
        bpy.context.window.scene=source
        bpy.ops.render.render(write_still=True)
        return
    bank=pose_bank(source,parts)
    right=source.camera.rotation_euler.to_matrix()@Vector((1,0,0))
    up=source.camera.rotation_euler.to_matrix()@Vector((0,1,0))
    for index,frozen in enumerate(bank):
        vertices=np.array([tuple(v.co) for v in frozen[0][0].vertices])
        for direction in range(8):
            rotation=np.array(Matrix.Rotation(direction*math.pi/4,3,'Z'))
            rotated=vertices@rotation.T
            xs=80+50*(rotated@np.array(right))
            ys=154-50*(rotated@np.array(up))
            margin=min(xs.min(),160-xs.max(),ys.min(),192-ys.max())
            if margin<3:
                raise ValueError(f'{name} pose {index} direction {direction}: {margin:.1f}px camera margin')
    sheet=bpy.data.scenes.new(name+' | export')
    sheet.world=source.world
    sheet.render.engine='CYCLES';sheet.cycles.samples=8;sheet.cycles.use_denoising=True
    sheet.render.threads_mode='FIXED';sheet.render.threads=4
    sheet.render.film_transparent=True
    sheet.render.image_settings.file_format='PNG';sheet.render.image_settings.color_mode='RGBA'
    sheet.render.image_settings.compression=85;sheet.view_settings.view_transform='Standard'
    sheet.render.resolution_x=960;sheet.render.resolution_y=1344;sheet.render.resolution_percentage=100
    camera=source.camera.copy();camera.data=source.camera.data.copy()
    camera.data.ortho_scale=19.2
    sheet.collection.objects.link(camera);sheet.camera=camera
    for light in source.objects:
        if light.type=='LIGHT':sheet.collection.objects.link(light.copy())
    right=camera.rotation_euler.to_matrix()@Vector((1,0,0))
    up=camera.rotation_euler.to_matrix()@Vector((0,1,0))
    roots=[]
    for index,frozen in enumerate(bank):
        col,row=index%6,index//6
        root=bpy.data.objects.new('Cell %02d'%index,None);sheet.collection.objects.link(root)
        root.location=right*((col+.5-3)*3.2)+up*((3.5-row-.5)*3.84)
        roots.append(root)
        for mesh,world,label in frozen:
            ob=bpy.data.objects.new(label+' | pose',mesh);sheet.collection.objects.link(ob)
            ob.parent=root;ob.matrix_basis=world
    bpy.context.window.scene=sheet
    for direction in range(8):
        for root in roots:root.rotation_euler.z=direction*math.pi/4
        sheet.render.filepath=str(folder/('hero_y%03d.png'%(direction*45)))
        bpy.ops.render.render(write_still=True)
        # Lossless re-encoding reduces browser preload size without quantizing
        # shading, changing alpha or throwing away any visible pixel colors.
        subprocess.run(['magick',sheet.render.filepath,'-background','none','-alpha','background',
                        '-define','png:compression-level=9',sheet.render.filepath],check=True)
        print('HERO_DIRECTION_DONE',name,direction,flush=True)
    subprocess.run(['magick',str(folder/'hero_y000.png'),'-crop','160x192+0+0',
                    '+repage','-trim','+repage','-bordercolor','none','-border','8',
                    str(folder/'portrait.png')],check=True)
    bpy.context.window.scene=source
    for ob in list(sheet.objects):
        if ob.type=='CAMERA':data=ob.data;bpy.data.objects.remove(ob,do_unlink=True);bpy.data.cameras.remove(data)
        else:bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.scenes.remove(sheet)
    for frozen in bank:
        for mesh,world,label in frozen:
            bpy.data.meshes.remove(mesh)
    print('HERO_DONE',name,flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--heroes',nargs='+',choices=IDS)
    parser.add_argument('--preview',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    names=args.heroes or IDS
    models={}
    for name in names:
        setup(name);base(name);dress(name);animate(name)
        reference=bpy.data.images.load(str(ROOT/'assets/heroes'/(name+'.png')),check_existing=True)
        reference.name='Reference | '+name;reference.pack()
        SCENE['reference']='assets/heroes/'+name+'.png'
        SCENE['element']=ELEMENTS[IDS.index(name)]
        SCENE['style']='Melee' if name in MELEE else 'Ranged'
        models[name]=(SCENE,list(PARTS))
        print('HERO_MODEL_DONE',name,len(PARTS),flush=True)
    bpy.context.window.scene=models[names[0]][0]
    source=ROOT/'art-src/blender'/('heroes-isometric.blend' if not args.heroes else 'heroes-'+'-'.join(names)+'.blend')
    bpy.ops.wm.save_as_mainfile(filepath=str(source))
    for name,(scene,parts) in models.items():
        render_hero(name,scene,parts,args.preview)
        (ROOT/'art-src/hero-render-progress.json').write_text(json.dumps({'hero':name,'completed':names.index(name)+1,'total':len(names)}))
    if not args.preview:
        metadata={'width':160,'height':192,'columns':6,'rows':7,'anchor_x':80,'anchor_y':154,
                  'scale':.70,'heroes':IDS,'direction_angles':list(range(0,360,45)),
                  'camera':{'elevation':30,'azimuth':45},'animations':{}}
        offset=0
        for name,count,fps,loop in ANIMS:
            metadata['animations'][name]={'offset':offset,'frames':count,'fps':fps,'loop':loop};offset+=count
        (OUT/'heroes.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print('HERO_LIBRARY_DONE',str(source),flush=True)


if __name__=='__main__':main()
