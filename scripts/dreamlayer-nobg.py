#!/usr/bin/env python3
"""Cut out the magenta backgrounds with DreamLayer's background_remove.

Uploads each assets/raw/<name>.png, runs background_remove, and saves the
transparent result as assets/raw/<name>_nobg.png. Idempotent and resumable via
assets/raw/.state-nobg.json.

Usage: DREAMLAYER_API_KEY=... python3 scripts/dreamlayer-nobg.py
"""
import json
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / 'art-src' / 'raw'
STATE = RAW / '.state-nobg.json'
API = 'https://api.dreamlayer.io'
KEY = os.environ.get('DREAMLAYER_API_KEY')
MAX_ACTIVE = 2
POLL = 3.0

NAMES = [
    'jack', 'match', 'penny', 'dealer', 'gale', 'zephyr', 'flint', 'mason',
    'clover', 'briar', 'frost', 'whiteout', 'volt', 'count', 'crown', 'oracle',
    'null', 'laugh', 'bailiff',
]
PROMPT = 'remove the flat magenta background; keep only the character, clean pixel-art edges'


def curl(args):
    return subprocess.run(['curl', '-s', '--max-time', '180'] + args, capture_output=True)


def http(path, body=None, method=None, hdrs=None, key=None):
    HDR = {'Authorization': 'Bearer ' + (KEY or ''), 'DreamLayer-Version': '1'}
    HDR.update(hdrs or {})
    cmd = ['-w', '\n%{http_code}']
    if body is not None:
        cmd += ['--data-binary', '@-']
    if method:
        cmd += ['-X', method]
    for k, v in HDR.items():
        cmd += ['-H', f'{k}: {v}']
    proc = subprocess.run(['curl', '-s', '--max-time', '120'] + cmd + [API + path],
                          input=json.dumps(body).encode() if body is not None else None,
                          capture_output=True)
    out = proc.stdout
    sep = out.rfind(b'\n')
    if sep == -1:
        return 0, b''
    return int(out[sep + 1:] or b'0'), out[:sep]


def upload(name):
    src = RAW / f'{name}.png'
    proc = curl(['-w', '\n%{http_code}', '-X', 'POST', API + '/v1/input-assets',
                 '-H', 'Authorization: Bearer ' + KEY, '-H', 'DreamLayer-Version: 1',
                 '-F', f'file=@{src};type=image/png'])
    out = proc.stdout
    sep = out.rfind(b'\n')
    code = int(out[sep + 1:] or b'0')
    if code != 201:
        print(f'  ! {name}: upload {code} {out[:160]}')
        return None
    return json.loads(out[:sep])['input_asset_id']


def submit(name, asset_id):
    body = {'operation': 'background_remove', 'input_asset_id': asset_id,
            'prompt': PROMPT, 'max_credits': 1}
    code, out = http('/v1/execute', body, 'POST',
                     {'Idempotency-Key': 'cinders-bgremove-' + name,
                      'Accept': 'application/json', 'Content-Type': 'application/json'})
    if code == 0:
        return None
    if code != 202:
        print(f'  ! {name}: submit {code} {out[:200]}')
        return ''
    eid = json.loads(out)['execution_id']
    print(f'  + {name}: queued {eid}')
    return eid


def status(eid):
    code, out = http('/v1/executions/' + eid)
    if code == 0:
        return None
    if code != 200:
        return {'status': 'failed', 'error': out[:200]}
    return json.loads(out)


def download(name, url):
    tmp = RAW / f'{name}_nobg.png.part'
    proc = curl(['-fsL', '-H', 'Authorization: Bearer ' + KEY, '-o', str(tmp), url])
    if proc.returncode != 0 or not tmp.exists() or tmp.stat().st_size == 0:
        print(f'  ! {name}: download failed: {proc.stderr.decode()[:160]}')
        return False
    size = tmp.stat().st_size
    tmp.replace(RAW / f'{name}_nobg.png')
    print(f'  - {name}: downloaded {size} bytes')
    return True


def state_load():
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def main():
    if not KEY:
        print('DREAMLAYER_API_KEY is not set'); sys.exit(1)
    st = state_load()
    done = st.get('done') or []
    running = st.get('running') or {}
    assets = st.get('assets') or {}
    queue = [n for n in NAMES if n not in done and n not in running]
    print(f'{len(NAMES)} assets; {len(done)} done, {len(running)} running, {len(queue)} queued')

    def save():
        STATE.write_text(json.dumps({'done': done, 'running': running, 'assets': assets}))

    def start(n):
        aid = assets.get(n)
        if not aid:
            aid = upload(n)
            if not aid:
                return None
            assets[n] = aid
        eid = submit(n, aid)
        if eid:
            running[n] = eid
        save()
        return eid

    while len(running) < MAX_ACTIVE and queue:
        n = queue.pop(0)
        if start(n) is None:
            queue.append(n)
            break
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
                if download(n, fa[0]['download_url']):
                    del running[n]
                    done.append(n)
                save()
            elif stat in ('failed', 'cancelled') or e.get('error'):
                print(f'  x {n}: {e.get("error") or stat}')
                del running[n]
                done.append(n)
                save()
        while len(running) < MAX_ACTIVE and queue:
            n = queue.pop(0)
            if start(n) is None:
                queue.append(n)
                break
    print(f'batch finished: {len(done)} assets')


if __name__ == '__main__':
    main()