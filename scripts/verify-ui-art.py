"""Check Blender exports: dimensions, alpha, animation variation and floor variants."""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/ui'


def identify(path):
    return subprocess.check_output(['magick', 'identify', '-format', '%w %h %[channels]', str(path)], text=True)


expected = {name: (192, 64) for name in ['button', 'button_hover', 'button_disabled']}
expected.update({name: (128, 128) for name in ['panel', 'card', 'slot', 'bar_track']})
expected.update({name: (1280, 720) for name in ['bg_title', 'bg_screen', 'bg_arena', 'arena_floor']})
elements = ['pyro', 'hydro', 'anemo', 'geo', 'dendro', 'cryo', 'electro', 'gravity', 'antimatter']
expected.update({'arena_floor_' + e: (1280, 720) for e in elements})
loops = {name: (96, 96) for name in ['coin', 'infinity_key', 'ember_seal', 'brazier', 'crystal']}
loops.update(cardback=(160, 208), floor_rune=(256, 128))
expected.update({name: (w * 8, h) for name, (w, h) in loops.items()})
expected.update(elements=(768, 192), items=(768, 288))
for name, (w, h) in expected.items():
    actual = identify(OUT / (name + '.png')).split()
    assert actual[:2] == [str(w), str(h)], (name, actual)
    assert 'a' in actual[2], (name, 'RGBA required')
for name, (w, h) in loops.items():
    signatures = []
    for index in range(8):
        signature = subprocess.check_output([
            'magick', str(OUT / (name + '.png')), '-crop', f'{w}x{h}+{index*w}+0',
            '+repage', '-format', '%#', 'info:'
        ], text=True)
        signatures.append(signature)
    assert len(set(signatures)) >= 4, (name, 'Animation must contain at least four distinct rendered poses')
    # Transparent sprite edges prevent adjacent cells leaking with linear filtering.
    alpha = subprocess.check_output([
        'magick', str(OUT / (name + '.png')), '-crop', '1x1+0+0', '+repage',
        '-format', '%[fx:a]', 'info:'
    ], text=True)
    assert float(alpha) == 0, (name, 'Sprite margin must remain transparent')
floor_signatures = [subprocess.check_output([
    'magick', str(OUT / ('arena_floor_' + e + '.png')), '-format', '%#', 'info:'
], text=True) for e in elements]
assert len(set(floor_signatures)) == 9, 'Each element must have a distinct floor export'
assert (ROOT / 'art-src/blender/house-ui.blend').is_file()
assert (OUT / 'preview.html').is_file()
print(f'PASS {len(expected)} Blender exports: dimensions/RGBA, seven varying loops, transparent margins, nine distinct floors and editable source')
