"""Validate rendered particle cells and icon margins without image dependencies."""
import pathlib,json,subprocess,hashlib
R=pathlib.Path(__file__).resolve().parents[1];out=R/'assets/effects'
meta=json.loads((out/'effects.json').read_text());assert len(set(meta['elements']))==9
signatures=[]
for element in meta['elements']:
 p=out/(element.lower()+'.png')
 size=subprocess.check_output(['magick','identify','-format','%w %h %[channels]',str(p)],text=True).split()
 assert size[:2]==['1152','384'] and 'a' in size[2],(element,size)
 cells=[]
 for f in range(12):
  raw=subprocess.check_output(['magick',str(p),'-crop',f'192x192+{f%6*192}+{f//6*192}','+repage','-depth','8','RGBA:-'])
  alpha=raw[3::4];assert max(alpha)>0,(element,f,'Empty cell')
  # Eight transparent pixels on every cell edge protect linear filtering.
  for y in range(192):
   for x in range(192):
    if x<8 or x>=184 or y<8 or y>=184:assert alpha[y*192+x]==0,(element,f,'Clipped particles')
  cells.append(hashlib.sha256(raw).hexdigest())
 assert len(set(cells))==12,(element,'Static animation')
 signatures.append(hashlib.sha256(p.read_bytes()).hexdigest())
assert len(set(signatures))==9
assert (R/'art-src/blender/element-effects.blend').is_file()
p=R/'assets/ui/icons.png'
assert subprocess.check_output(['magick','identify','-format','%wx%h',str(p)],text=True)=='768x288'
print('PASS 24 Blender icons and nine 12-frame particle animations: RGBA, distinct frames, transparent margins, editable source')
