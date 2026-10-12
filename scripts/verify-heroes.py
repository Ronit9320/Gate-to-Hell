"""Validate all reference-inspired hero sheets, cell margins and animation exports."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'assets/heroes/isometric'
parser=argparse.ArgumentParser()
parser.add_argument('--partial',action='store_true')
args=parser.parse_args()
meta=json.loads((OUT/'heroes.json').read_text())
assert (meta['width'],meta['height'],meta['columns'],meta['rows'])==(160,192,6,7)
assert (meta['anchor_x'],meta['anchor_y'])==(80,154)
assert sum(spec['frames'] for spec in meta['animations'].values())==42
minimum=192;frames=0;complete=0;clipped=[]
for hero in meta['heroes']:
    sheets=[OUT/hero/('hero_y%03d.png'%angle) for angle in range(0,360,45)]
    if args.partial and not all(p.is_file() for p in sheets):continue
    assert all(p.is_file() for p in sheets),hero
    assert (OUT/hero/'portrait.png').is_file(),hero
    directions=set()
    for sheet in sheets:
        info=subprocess.check_output(['magick','identify','-format','%w %h %[channels]',str(sheet)],text=True)
        assert info.startswith('960 1344 srgba'),(sheet,info)
        directions.add(hashlib.sha256(sheet.read_bytes()).hexdigest())
        bounds=subprocess.check_output(['magick',str(sheet),'-crop','160x192','+repage',
            '-alpha','extract','-threshold','2%','-trim','-format','%w %h %X %Y\n','info:'],text=True).splitlines()
        assert len(bounds)==42,(sheet,len(bounds))
        for index,line in enumerate(bounds):
            w,h,x,y=map(int,line.split())
            margin=min(x,y,160-x-w,192-y-h)
            if margin<2:clipped.append((hero,sheet.name,index,line))
            minimum=min(minimum,margin);frames+=1
        signatures=subprocess.check_output(['magick',str(sheet),'-crop','160x192','+repage',
            '-format','%#\n','info:'],text=True).splitlines()
        for pose,spec in meta['animations'].items():
            cells=signatures[spec['offset']:spec['offset']+spec['frames']]
            assert len(set(cells))>1,('Static animation',hero,pose,sheet.name)
    assert len(directions)==8,('Repeated direction',hero)
    complete+=1
if not args.partial:assert complete==18
if clipped:
    print('CLIPPED_CELLS',json.dumps(clipped))
assert not clipped,'Hero poses must fit their fixed cells with transparent margins'
assert (ROOT/'art-src/blender/heroes-isometric.blend').is_file()
print(f'PASS {complete} heroes / {complete*8} atlases / {frames} animated frames; all seven poses vary; RGBA, directions, portraits and anchors valid; minimum margin {minimum}px')
