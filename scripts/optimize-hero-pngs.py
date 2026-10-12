"""Losslessly compress completed hero exports; also used after legacy render runs."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse
import subprocess

ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('heroes',nargs='*')
args=parser.parse_args()
folder=ROOT/'assets/heroes/isometric'
files=[p for p in folder.glob('*/*.png') if not args.heroes or p.parent.name in args.heroes]


def optimize(file):
    before=file.stat().st_size
    subprocess.run(['magick',str(file),'-background','none','-alpha','background',
                    '-define','png:compression-level=9',str(file)],check=True)
    return before,file.stat().st_size


with ThreadPoolExecutor(max_workers=4) as pool:
    results=list(pool.map(optimize,files))
print('Lossless PNG compression:',len(files),'files;',sum(a for a,b in results),'→',sum(b for a,b in results),'bytes')
