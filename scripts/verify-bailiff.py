"""Validate atlas dimensions, packing, alpha margins and animation variation."""
import hashlib, json, pathlib, re, subprocess, argparse
root=pathlib.Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--partial',action='store_true');args=parser.parse_args()
folder=root/'assets/bosses/bailiff_iso';raw=root/'art-src/bailiff-frames'
paths=sorted(folder.glob('bailiff_y*.png'))
if not args.partial:assert len(paths)==8, 'Eight directions are required'
seen=set();frames=0;minimum=256
for sheet in paths:
    info=subprocess.check_output(['magick','identify','-format','%w %h %[channels]',str(sheet)],text=True)
    assert info.startswith('2048 1280 srgba'),(sheet,info)
    digest=hashlib.sha256(sheet.read_bytes()).hexdigest();assert digest not in seen;seen.add(digest)
    for name,count in [('idle',8),('attack',10),('walk',8),('hurt',4),('death',10)]:
        hashes=set()
        for i in range(1,count+1):
            p=raw/sheet.stem.replace('bailiff_','')/(name+'_%02d.png'%i)
            assert p.is_file(),p
            hashes.add(hashlib.sha256(p.read_bytes()).hexdigest())
            bounds=subprocess.check_output(['magick',str(p),'-alpha','extract','-threshold','2%','-trim','-format','%wx%h%O','info:'],text=True)
            m=re.fullmatch(r'(\d+)x(\d+)\+(\d+)\+(\d+)',bounds);assert m,(p,bounds)
            w,h,x,y=map(int,m.groups());margin=min(x,y,256-x-w,256-y-h)
            assert margin>=2,('Clipped frame',str(p),bounds)
            minimum=min(minimum,margin);frames+=1
        assert len(hashes)>1,('Animation is static',name,sheet.name)
if not args.partial:
    meta=json.loads((folder/'bailiff.json').read_text());assert meta['anchor_x']==128 and meta['anchor_y']==204
    assert sum(a['frames'] for a in meta['animations'].values())==40
print(f'PASS {len(paths)} directional atlases / {frames} frames; alpha present; no clipped frames; minimum margin {minimum}px')
