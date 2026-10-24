"""Verify every boss/effect frame, transparency, variation and source deliverable."""
import argparse, hashlib, json, pathlib, subprocess
R=pathlib.Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--partial',action='store_true');args=p.parse_args()
def validate(path,w,h,cols,rows,clips):
 info=subprocess.check_output(['magick','identify','-format','%w %h %[channels]',str(path)],text=True).split()
 assert list(map(int,info[:2]))==[w*cols,h*rows] and 'a' in info[2],(path,info)
 raw=subprocess.check_output(['magick',str(path),'-alpha','extract','-depth','8','gray:-'])
 hashes=[]
 for f in range(cols*rows):
  x,y=f%cols*w,f//cols*h;cell=b''.join(raw[(y+j)*w*cols+x:(y+j)*w*cols+x+w] for j in range(h))
  assert max(cell)>128,(path,f,'empty frame')
  edges=cell[:w*3]+cell[-w*3:]+b''.join(cell[j*w:j*w+3]+cell[(j+1)*w-3:(j+1)*w] for j in range(h))
  assert max(edges)<=4,(path,f,'clipped edge')
  hashes.append(hashlib.sha256(cell).hexdigest())
 for name,spec in clips.items():
  cells=hashes[spec['offset']:spec['offset']+spec['frames']]
  assert len(set(cells))>1,(path,name,'static animation')
 return len(hashes)
folder=R/'assets/bosses/isometric'
if args.partial:
 names=[d.name for d in folder.iterdir() if d.is_dir() and len(list(d.glob('boss_y*.png')))==8]
else:
 meta=json.loads((folder/'bosses.json').read_text());names=meta['bosses'];assert len(names)==len(set(names))==23
 assert (meta['anchor_x'],meta['anchor_y'],meta['scale'])==(96,146,.85)
clips={};off=0
for name,frames in [('idle',8),('attack',10),('hurt',4),('death',10),('stagger',4),('recovery',4)]:clips[name]={'offset':off,'frames':frames};off+=frames
frames=0
for name in names:
 signatures=set()
 for d in range(0,360,45):
  path=folder/name/('boss_y%03d.png'%d);frames+=validate(path,192,192,8,5,clips);signatures.add(hashlib.sha256(path.read_bytes()).hexdigest())
 assert len(signatures)==8,(name,'directions repeat')
 assert (folder/name/'portrait.png').is_file(),name
print('PASS',len(names),'boss appearances /',frames,'anchored animated RGBA frames with clear borders',flush=True)
folder=R/'assets/effects/combat';meta=json.loads((folder/'combat.json').read_text());assert len(meta['effects'])==93
for id in meta['effects']:validate(folder/(id+'.png'),128,128,4,2,{'effect':{'offset':0,'frames':8}})
print('PASS 93 dedicated effects / 744 RGBA frames, animation and transparent borders',flush=True)
for id in ['bailiff','undertow','kite','bedrock','bramble','regent','static','sun','kings','throne']:
 assert (R/'assets/scenery'/('prop_'+id+'.png')).is_file()
for id in ['reward','victory','defeat','hell_entry']:assert (R/'assets/scenery'/(id+'.png')).is_file()
for src in ['bosses-complete.blend','combat-effects.blend','scenery-and-illustrations.blend']:assert (R/'art-src/blender'/src).is_file()
print('PASS ten scenery props, four screen illustrations and editable Blender sources')
