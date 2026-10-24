"""Boss-local fire ribbons and molten slam. Reuses the combat atlas exporter."""
import bpy, math, pathlib, json
R = pathlib.Path(__file__).resolve().parents[2]
src=(R/'scripts/blender/build_combat_art.py').read_text()
exec(src[:src.index('def main():')])
models={}
for id,family,loop in [('bailiff_flame','flame',True),('bailiff_slam','slam',False)]:
    spec={'family':family,'color':'pyro','duration':.8 if loop else .7,'loop':loop}
    s,_=scene(id,spec)
    # Replace the shared primitive burst with layered modeled ribbons.
    for o,_,_ in PARTS:bpy.data.objects.remove(o,do_unlink=True)
    PARTS=[]
    M['core']=mat(id+' molten gold',(1,.57,.075),1.8)
    M['color']=mat(id+' ember vermilion',(.9,.08,.008),1.1)
    M['dark']=mat(id+' black slag',(.045,.024,.014),0)
    if loop:
        for k in range(9):
            y=(k-4)*.12
            pts=[(-1.35+j*.10,y+.035*math.sin(j*.7+k),.05+.11*math.sin(j*.3+k)**2) for j in range(28)]
            line('Floor-bound flame beam',pts,.035 if k%3 else .055,'core' if k%3==0 else 'color','travel',k)
        for k in range(18):
            x=-1.2+(k%9)*.3;y=(-.28 if k<9 else .28)
            # Curving tongues with narrowing cross sections, not cone particles.
            verts=[]
            for j in range(7):
                z=j*.075;w=.065*(1-j/6)+.003
                cx=x+.09*math.sin(j*.55+k);cy=y+.04*math.sin(j*.6+k)
                verts.extend([(cx-w,cy,z),(cx+w,cy,z)])
            d=bpy.data.meshes.new('Tapered flame ribbon');d.from_pydata(verts,[],[(j*2,j*2+1,j*2+3,j*2+2) for j in range(6)]);d.update()
            o=bpy.data.objects.new('Licking flame ribbon',d);s.collection.objects.link(o);remember(o,'core' if k%4==0 else 'color','rise',k)
        for k in range(20):
            gem('Lane flying ember',(-1.3+(k%10)*.27,((k*7)%11-5)*.09,.12),(.016,.016,.028),'core','rise',k)
    else:
        for k in range(12):
            a=k*math.tau/12
            pts=[(math.cos(a)*r,math.sin(a)*r,.025) for r in [.08,.35,.48,.82,1.15]]
            pts[2]=(math.cos(a+.16)*.48,math.sin(a+.16)*.48,.025)
            line('Branching molten floor fracture',pts,.023,'color','expand',a)
            line('Hot fracture center',pts,.009,'core','expand',a)
            gem('Ejected slag',(math.cos(a)*.65,math.sin(a)*.65,.16),(.10,.08,.13),'dark','expand',a)
            gem('Impact ember',(math.cos(a)*.85,math.sin(a)*.85,.24),(.022,.018,.055),'core','rise',a)
        ring(.72,key='core');ring(.94,key='color')
        # Stamped executioner's seal with eight rays.
        ring(.36,key='dark',mode='pulse')
        for k in range(8):
            a=k*math.tau/8
            line('Impact seal ray',[(math.cos(a)*.22,math.sin(a)*.22,.03),(math.cos(a)*.42,math.sin(a)*.42,.03)],.024,'core','pulse')
    animate(spec);models[id]=(s,list(PARTS),spec)
bpy.context.window.scene=models['bailiff_flame'][0]
bpy.ops.wm.save_as_mainfile(filepath=str(R/'art-src/blender/bailiff-effects.blend'))
for id,(s,parts,spec) in models.items():render(id,s,parts)
metadata_path=OUT/'combat.json'
metadata=json.loads(metadata_path.read_text())
for id,(_,_,spec) in models.items():metadata['effects'][id]=spec
metadata_path.write_text(json.dumps(metadata,indent=2)+'\n')
lines=['-- Generated combat library, with scripts/blender/build_bailiff_fx.py overrides.','return {']
for id,spec in metadata['effects'].items():
    lines.append("  ['%s'] = { duration = %s, loop = %s }," % (id,spec['duration'],str(spec['loop']).lower()))
lines.append('}')
(R/'src/data/combat_art.lua').write_text('\n'.join(lines)+'\n')
# Keep the established main library unchanged; these are first-boss overrides.
print('BAILIFF_EFFECTS_READY',flush=True)
