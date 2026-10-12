#!/usr/bin/env python3
"""Generate the Gate to Hell cover art via the DreamLayer execute API.

Submits one text_to_image job, polls the execution and downloads the finished
PNG. Resumable: the in-flight execution id is recorded in
art-src/raw/.cover-state.json so re-running resumes instead of paying again.

Usage: DREAMLAYER_API_KEY=... python3 scripts/dreamlayer-cover.py [output.png]
"""
import json
import os
import pathlib
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / 'art-src' / 'raw'
STATE = RAW / '.cover-state.json'
API = 'https://api.dreamlayer.io'
KEY = os.environ.get('DREAMLAYER_API_KEY')
POLL = 4.0
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'release' / 'cover-dreamlayer.png'

HDR = {
    'Authorization': 'Bearer ' + (KEY or ''),
    'DreamLayer-Version': '1',
    'Content-Type': 'application/json',
}

PROMPT = (
    'Cubism',  # placeholder, replaced below
)

KEY_VERSION = 'gate-to-hell-cover-v1'

PROMPT = (
    'Cover art for a fantasy roguelike boss battler video game. Dramatic '
    'isometric arena in a hellish cathedral. A trio of stylized heroes on the '
    'near side: a rugged soot-stained pyromancer hurling burning embers, an ice '
    'jester casting frost shards, and a young lightning mage raising a crackling '
    'spear. A towering armored boss looms across the arena. Fire, water, wind, '
    'rock, plant, ice, lightning, gravity and void magic swirl together, a glowing '
    'red-orange portal to Hell in the background. Painterly key art, rich saturated '
    'colors, strong contrast and rim lighting, cinematic composition, clear empty '
    'space at the top for an added title. No text, no letters, no watermark.'
)


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


def submit():
    body = {
        'operation': 'text_to_image',
        'prompt': PROMPT,
        'aspect_ratio': '4:3',
        'max_credits': 1,
    }
    hdrs = dict(HDR)
    hdrs['Idempotency-Key'] = KEY_VERSION
    hdrs['Accept'] = 'application/json'
    st, out = http('/v1/execute', body, 'POST', hdrs)
    if st == 0:
        print('submit transport error')
        return None
    if st != 202:
        print(f'submit {st}: {out[:400].decode(errors="replace")}')
        return ''
    j = json.loads(out)
    eid = j.get('execution_id') or j.get('id')
    print(f'queued {eid}')
    return eid


def status(eid):
    st, out = http('/v1/executions/' + eid)
    if st == 0:
        return None
    if st != 200:
        return {'status': 'failed', 'error': out[:400].decode(errors='replace')}
    return json.loads(out)


def download(url):
    tmp = RAW / 'cover-dreamlayer.png.part'
    proc = subprocess.run(
        ['curl', '-fsL', '--max-time', '120', '-H', 'Authorization: Bearer ' + KEY,
         '-o', str(tmp), url],
        capture_output=True,
    )
    if proc.returncode != 0 or not tmp.exists() or tmp.stat().st_size == 0:
        print('asset fetch failed:', proc.stderr.decode()[:200])
        return False
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tmp.replace(OUT)
    print(f'downloaded {OUT} ({OUT.stat().st_size} bytes)')
    return True


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {}


def save_state(st):
    STATE.write_text(json.dumps(st, indent=1))


def main():
    if not KEY:
        print('DREAMLAYER_API_KEY is not set')
        sys.exit(1)
    RAW.mkdir(parents=True, exist_ok=True)
    st0 = load_state()
    eid = st0.get('running')
    if not eid:
        eid = submit()
        if not eid:
            sys.exit(1)
        save_state({'running': eid})
    for _ in range(300):
        e = status(eid)
        if e is None:
            time.sleep(POLL)
            continue
        stat = e.get('status')
        if stat == 'completed':
            assets = (e.get('image_job') or {}).get('finished_assets') or []
            if not assets:
                print('completed but no finished assets')
                sys.exit(1)
            if download(assets[0]['download_url']):
                save_state({'done': True})
                return
            sys.exit(1)
        if stat in ('failed', 'cancelled'):
            print('job', stat, e.get('error'))
            save_state({})
            sys.exit(1)
        if stat == 'needs_input':
            print('needs input:', str(e.get('question'))[:300])
            sys.exit(1)
        time.sleep(POLL)
    print('timed out waiting for execution', eid)


if __name__ == '__main__':
    main()
