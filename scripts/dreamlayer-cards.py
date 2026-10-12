#!/usr/bin/env python3
"""Throwaway DreamLayer test: generate sample hero cards, one per rarity.

Not wired into the game. Writes raws and cut-outs to release/cards-dreamlayer/.
Idempotent and resumable via .cards-state.json.

Usage: DREAMLAYER_API_KEY=... python3 scripts/dreamlayer-cards.py [--raw-only]
"""
import json
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / 'release' / 'cards-dreamlayer'
RAW = OUT / 'raw'
STATE = OUT / '.cards-state.json'
API = 'https://api.dreamlayer.io'
KEY = os.environ.get('DREAMLAYER_API_KEY')
POLL = 4.0
MAX_ACTIVE = 2
RAW_ONLY = '--raw-only' in sys.argv

BASE = ('game UI asset: one single empty vertical card frame, hollow completely '
        'empty transparent center with absolutely no content inside, only an '
        'ornate border, centered, isolated on a flat solid magenta #FF00FF '
        'background, painted, crisp edges, no text, no letters, no watermark')

JOBS = [
    ('frame_common',
     'common rarity card frame: plain worn iron and dark stone border, muted '
     'grey-teal trim, no gems, simple and cheap, empty middle'),
    ('frame_uncommon',
     'uncommon rarity card frame: polished border with emerald-green enamel trim '
     'and a single small gem at the top, empty middle'),
    ('frame_rare',
     'rare rarity card frame: elaborate violet-purple filigree border with '
     'glowing amethyst gems at the corners, empty middle'),
    ('frame_legendary',
     'legendary rarity card frame: lavish radiant gold border with crown motifs '
     'and multiple glowing gems, divine glow, empty middle'),
]

DESCS = {n: d for n, d in JOBS}

HDR = {
    'Authorization': 'Bearer ' + (KEY or ''),
    'DreamLayer-Version': '1',
    'Content-Type': 'application/json',
}


def http(path, body=None, method=None, hdrs=None):
    data = json.dumps(body).encode() if body is not None else None
    cmd = ['curl', '-s', '--max-time', '120', '-w', '\n%{http_code}']
    if data is not None:
        cmd += ['--data-binary', '@-']
    if method:
        cmd += ['-X', method]
    for k, v in (hdrs or HDR).items():
        cmd += ['-H', f'{k}: {v}']
    proc = subprocess.run(cmd + [API + path], input=data, capture_output=True)
    out = proc.stdout
    sep = out.rfind(b'\n')
    if sep == -1:
        return 0, b''
    return int(out[sep + 1:] or b'0'), out[:sep]


def submit_text(name):
    body = {'operation': 'text_to_image', 'prompt': f'{DESCS[name]}, {BASE}',
            'aspect_ratio': '1:1', 'max_credits': 1}
    hdrs = dict(HDR)
    hdrs['Idempotency-Key'] = 'gate-to-hell-cards-' + name
    hdrs['Accept'] = 'application/json'
    code, out = http('/v1/execute', body, 'POST', hdrs)
    if code == 0:
        return None
    if code != 202:
        print(f'  ! {name}: submit {code} {out[:200].decode(errors="replace")}')
        return ''
    eid = json.loads(out).get('execution_id')
    print(f'  + {name}: queued {eid}')
    return eid


def upload(name):
    src = RAW / f'{name}.png'
    proc = subprocess.run(
        ['curl', '-s', '--max-time', '180', '-w', '\n%{http_code}', '-X', 'POST',
         API + '/v1/input-assets', '-H', 'Authorization: Bearer ' + KEY,
         '-H', 'DreamLayer-Version: 1', '-F', f'file=@{src};type=image/png'],
        capture_output=True)
    out = proc.stdout
    sep = out.rfind(b'\n')
    code = int(out[sep + 1:] or b'0')
    if code != 201:
        print(f'  ! {name}: upload {code} {out[:160].decode(errors="replace")}')
        return None
    return json.loads(out[:sep])['input_asset_id']


def submit_nobg(name, aid):
    body = {'operation': 'background_remove', 'input_asset_id': aid,
            'prompt': 'remove the flat magenta background, keep only the card, '
                      'clean crisp edges', 'max_credits': 1}
    hdrs = dict(HDR)
    hdrs['Idempotency-Key'] = 'gate-to-hell-cards-nobg-' + name
    hdrs['Accept'] = 'application/json'
    code, out = http('/v1/execute', body, 'POST', hdrs)
    if code == 0:
        return None
    if code != 202:
        print(f'  ! {name}: nobg submit {code} {out[:200].decode(errors="replace")}')
        return ''
    eid = json.loads(out).get('execution_id')
    print(f'  + {name}: nobg queued {eid}')
    return eid


def status(eid):
    code, out = http('/v1/executions/' + eid)
    if code == 0:
        return None
    if code != 200:
        return {'status': 'failed', 'error': out[:200].decode(errors='replace')}
    return json.loads(out)


def fetch(name, url, suffix=''):
    tmp = RAW / f'{name}{suffix}.png.part'
    proc = subprocess.run(
        ['curl', '-fsL', '--max-time', '180', '-H', 'Authorization: Bearer ' + KEY,
         '-o', str(tmp), url], capture_output=True)
    if proc.returncode != 0 or not tmp.exists() or tmp.stat().st_size == 0:
        print(f'  ! {name}: fetch failed {proc.stderr.decode()[:160]}')
        return False
    size = tmp.stat().st_size
    tmp.replace(RAW / f'{name}{suffix}.png')
    print(f'  - {name}{suffix}: {size} bytes')
    return True


def load_state():
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def save_state(st):
    OUT.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(st, indent=1))


def run_phase(state, key_name, start_fn, done_key, eligible=None):
    running = state.get(key_name) or {}
    done = state.get(done_key) or []
    queue = [n for n, _d in JOBS
             if n not in done and n not in running
             and (eligible is None or eligible(n))]

    def pump():
        while len(running) < MAX_ACTIVE and queue:
            n = queue.pop(0)
            eid = start_fn(n)
            if eid:
                running[n] = eid
            elif eid is None:
                queue.append(n)
                break
            else:
                done.append(n)
            state[key_name] = running
            state[done_key] = done
            save_state(state)

    pump()
    while running:
        time.sleep(POLL)
        for n, eid in list(running.items()):
            e = status(eid)
            if e is None:
                continue
            stat = e.get('status')
            if stat == 'completed':
                fa = (e.get('image_job') or {}).get('finished_assets') or []
                if not fa:
                    print(f'  ! {n}: no finished assets')
                    continue
                suffix = '' if key_name == 'running' else '_nobg'
                if fetch(n, fa[0]['download_url'], suffix):
                    del running[n]
                    done.append(n)
                save_state(state)
            elif stat in ('failed', 'cancelled') or e.get('error'):
                print(f'  x {n}: {e.get("error") or stat}')
                del running[n]
                done.append(n)
                save_state(state)
        pump()


def main():
    if not KEY:
        print('DREAMLAYER_API_KEY is not set')
        sys.exit(1)
    OUT.mkdir(parents=True, exist_ok=True)
    RAW.mkdir(parents=True, exist_ok=True)
    state = load_state()

    print('phase 1: text_to_image')
    run_phase(state, 'running', submit_text, 'done')
    if RAW_ONLY:
        print('raw only; stopping')
        return

    print('phase 2: background_remove')
    assets = state.get('assets') or {}

    def start_nobg(n):
        aid = assets.get(n)
        if not aid:
            aid = upload(n)
            if not aid:
                return None
            assets[n] = aid
            state['assets'] = assets
            save_state(state)
        return submit_nobg(n, aid)

    run_phase(state, 'running_nobg', start_nobg, 'done_nobg',
              eligible=lambda n: (RAW / f'{n}.png').exists())
    print('done ->', OUT)


if __name__ == '__main__':
    main()
