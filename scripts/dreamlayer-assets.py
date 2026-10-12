#!/usr/bin/env python3
"""Batch pixel-art asset generation via the DreamLayer execute API.

Submits text_to_image jobs (idempotent, stable keys), polls executions,
downloads completed PNGs into assets/raw. Resumable: finished assets and
in-flight execution ids are recorded in assets/raw/.state.json.

Usage: DREAMLAYER_API_KEY=... python3 scripts/dreamlayer-assets.py
"""
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / 'art-src' / 'raw'
STATE = RAW / '.state.json'
API = 'https://api.dreamlayer.io'
KEY = os.environ.get('DREAMLAYER_API_KEY')
MAX_ACTIVE = 2
POLL = 3.0

HDR = {
    'Authorization': 'Bearer ' + (KEY or ''),
    'DreamLayer-Version': '1',
    'Content-Type': 'application/json',
}

KEY_VERSION = 'cinders-v2-'

# Pixel-art character assets, magenta background for local chroma keying.
STYLE = (
    'retro 16-bit pixel art game portrait, high contrast, crisp outlines, '
    'flat solid magenta #FF00FF background, character centered, full waist-up, '
    'no text, no watermark'
)
JOBS = [
    # -- Heroes (18) --
    ('jack', 'Cinder Jack', 'a rugged soot-stained coal miner hero wielding a fan of burning embers, pyrotechnic fire theme', STYLE),
    ('match', 'Madame Match', 'an elegant arsonist lady with a match between her fingers, pyrotechnic fire theme', STYLE),
    ('penny', 'Penny Rill', 'a cheerful river engineer with a water lance, blue aqua theme', STYLE),
    ('dealer', 'The Blue Dealer', 'a mysterious gambler dealing a returning wave of water, card-table blue theme', STYLE),
    ('gale', 'Gale Knave', 'a swashbuckling wind sailor with gust of wind, swift airy green theme', STYLE),
    ('zephyr', 'Zephyr Belle', 'a graceful wind dancer inside a small cyclone, swirling air theme', STYLE),
    ('flint', 'Flint Rook', 'a stoic stone knight with a rock strike stance, amber rock theme', STYLE),
    ('mason', 'The Gilt Mason', 'a gilded stonemason artisan with a rock eruption, golden earthen theme', STYLE),
    ('clover', 'Clover Hex', 'a wild herbalist casting a thorn volley, blooming plant theme', STYLE),
    ('briar', 'Briar Duchess', 'an elegant dethorned aristocrat surrounded by bramble, dark green plant theme', STYLE),
    ('frost', 'Frost Jester', 'a jolly ice jester flinging an ice fan, cyan frost theme', STYLE),
    ('whiteout', 'Lady Whiteout', 'a regal snow queen casting a frost zone, pale ice theme', STYLE),
    ('volt', 'Volt Page', 'an energetic scribe throwing a lightning spear, purple electric theme', STYLE),
    ('count', 'The Copper Count', 'a count in copper armor with delayed thunder marks, metallic electric theme', STYLE),
    ('crown', 'The Heavy Crown', 'a towering lord of gravity wearing a heavy crown, pulling darkness around, purple void theme', STYLE),
    ('oracle', 'Orbit Oracle', 'a mystic oracle with orbs orbiting her, gravitational rings theme', STYLE),
    ('null', 'Null Harlequin', 'a sinister harlequin juggling a void lance, antimatter purple-pink theme', STYLE),
    ('laugh', 'The Last Laugh', 'a grinning gambler with a delayed void detonation, antimatter pink theme', STYLE),
    # -- Boss (Ash Bailiff) --
    ('bailiff', 'The Ash Bailiff', 'an imposing soot-black armored summoner of fiery ash and ember lanes, smoldering cinders', STYLE),
]


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {}


def save_state(st):
    STATE.write_text(json.dumps(st, indent=1))


def http(path, body=None, method=None, hdrs=None):
    data = json.dumps(body).encode() if body is not None else None
    cmd = ['curl', '-s', '--max-time', '60', '-w', '\n%{http_code}']
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
    body_bytes, code = out[:sep], int(out[sep + 1:] or b'0')
    return code, body_bytes


def submit(name, prompt):
    body = {'operation': 'text_to_image', 'prompt': prompt, 'aspect_ratio': '1:1', 'max_credits': 1}
    hdrs = dict(HDR)
    hdrs['Idempotency-Key'] = KEY_VERSION + name
    hdrs['Accept'] = 'application/json'
    st, out = http('/v1/execute', body, 'POST', hdrs)
    if st == 0:
        print(f'  ! {name}: submit transport error (will retry)')
        return None
    if st != 202:
        print(f'  ! {name}: submit {st} {out[:200]}')
        return ''
    j = json.loads(out)
    eid = j.get('execution_id') or j.get('id')
    print(f'  + {name}: queued {eid}')
    return eid


def status(eid):
    st, out = http('/v1/executions/' + eid)
    if st == 0:
        return None  # transport error, retry later
    if st != 200:
        return {'status': 'failed', 'error': out[:200]}
    return json.loads(out)


def download(name, url):
    tmp = RAW / (name + '.png.part')
    proc = subprocess.run(
        ['curl', '-fsL', '--max-time', '120', '-H', 'Authorization: Bearer ' + KEY, '-o', str(tmp), url],
        capture_output=True,
    )
    if proc.returncode != 0 or not tmp.exists() or tmp.stat().st_size == 0:
        print(f'  ! {name}: asset fetch failed: {proc.stderr.decode()[:160]}')
        return False
    size = tmp.stat().st_size
    tmp.replace(RAW / (name + '.png'))
    print(f'  - {name}: downloaded {size} bytes')
    return True


def main():
    if not KEY:
        print('DREAMLAYER_API_KEY is not set'); sys.exit(1)
    st0 = load_state()
    done = st0.get('done') or []
    running = st0.get('running') or {}
    prompts = {n: f'{desc}, {style}' for n, _display, desc, style in JOBS}
    queue = [n for n, _d, _x, _s in JOBS if n not in done and n not in running]
    print(f'{len(JOBS)} assets; {len(done)} done, {len(running)} running, {len(queue)} queued')
    while len(running) < MAX_ACTIVE and queue:
        n = queue.pop(0)
        eid = submit(n, prompts[n])
        if eid:
            running[n] = eid
        elif eid is None:
            queue.append(n)
            break
        else:
            done.append(n)
        save_state({'done': done, 'running': running})
    while running:
        time.sleep(POLL)
        for n, eid in list(running.items()):
            e = status(eid)
            if e is None:
                continue
            stat = e.get('status')
            if stat == 'completed':
                assets = (e.get('image_job') or {}).get('finished_assets') or []
                if not assets:
                    print(f'  ! {n}: no finished assets')
                    continue
                ok = download(n, assets[0]['download_url'])
                if ok:
                    del running[n]
                    done.append(n)
                save_state({'done': done, 'running': running})
            elif stat in ('failed', 'cancelled'):
                err = e.get('error') or 'unknown'
                print(f'  x {n}: {err}')
                del running[n]
                done.append(n)
                save_state({'done': done, 'running': running})
            elif stat == 'needs_input':
                print(f'  ? {n}: needs input: {str(e.get("question"))[:200]}')
                del running[n]
                done.append(n)
                save_state({'done': done, 'running': running})
            elif e.get('error'):
                print(f'  x {n}: {e["error"]}')
                del running[n]
                done.append(n)
                save_state({'done': done, 'running': running})
        while len(running) < MAX_ACTIVE and queue:
            n = queue.pop(0)
            eid = submit(n, prompts[n])
            if eid:
                running[n] = eid
            elif eid is None:
                queue.append(n)
                break
            else:
                done.append(n)
            save_state({'done': done, 'running': running})
    print(f'batch finished: {len(done)} assets')


if __name__ == '__main__':
    main()