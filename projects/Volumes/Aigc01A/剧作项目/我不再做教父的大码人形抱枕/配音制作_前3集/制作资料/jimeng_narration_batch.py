#!/usr/bin/env python3
"""Drive observed Jimeng UI through OpenCLI; never use private mutation APIs."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLAN = ROOT / '制作资料/200字旁白生成计划.json'
MANIFEST = ROOT / '制作资料/已下载音频清单.json'
JOURNAL = ROOT / '制作资料/即梦提交与下载记录.json'
PROBE = '/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/probe.py'
SESSION = 'dama-current'


def save(path, data):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    temp.replace(path)


def cli(*args, timeout=35):
    r = subprocess.run(['opencli', 'browser', SESSION, *map(str, args)], capture_output=True,
                       text=True, encoding='utf-8', timeout=timeout)
    if r.returncode:
        raise RuntimeError(r.stdout.strip() + '\n' + r.stderr.strip())
    try:
        value = json.loads(r.stdout)
    except json.JSONDecodeError:
        return r.stdout.strip()
    if isinstance(value, dict) and value.get('error'):
        raise RuntimeError(json.dumps(value, ensure_ascii=False))
    return value


def evaluate(js):
    return cli('eval', js)


def norm(text):
    return ' '.join(text.split())


def snapshot():
    return evaluate('''(() => ({url:location.href, text:document.body.innerText,
      records:Array.from(document.querySelectorAll('[data-generated-record-key]')).map(e=>({
        key:e.getAttribute('data-generated-record-key'),
        handoff:e.getAttribute('data-generated-record-handoff-key'),text:e.innerText,
        cards:Array.from(e.querySelectorAll('.audio-card-container-x_138k')).map(c=>c.innerText)
      }))}))()''')


def visible_ref(selector):
    result = cli('find', '--css', selector, '--limit', '40', '--text-max', '60')
    entries = [e for e in result.get('entries', []) if e.get('visible')]
    if len(entries) != 1:
        raise RuntimeError(f'Expected one visible control for {selector}: {len(entries)}')
    return str(entries[0]['ref'])


def durations(card_texts):
    result = []
    for txt in card_texts:
        values = [int(a) * 60 + int(b) for a, b in re.findall(r'(\d+):(\d{2})', txt)]
        result.append(max(values, default=0))
    return result


def probe(path):
    r = subprocess.run([sys.executable, PROBE, str(path), '--json'], check=True,
                       capture_output=True, text=True, encoding='utf-8')
    data = json.loads(r.stdout)
    if not data.get('audio') or data.get('video') or data.get('duration', 0) <= 0:
        raise RuntimeError(f'Invalid downloaded audio: {path}')
    return data


def download_candidate(record_key, candidate_index):
    selector = f'[data-generated-record-key="{record_key}"] .audio-card-container-x_138k .left-section-Phe0vo'
    pager = None
    for attempt in range(2):
        if attempt:
            check = evaluate(f'''(() => ({{cards:document.querySelectorAll({json.dumps(selector)}).length,
              open:!!document.querySelector('.page-number-YYNlfP')}}))()''')
            if check['open']:
                break
            if check['cards'] < 2:
                raise RuntimeError('Generated cards disappeared before opening detail viewer.')
        cli('click', selector, '--nth', candidate_index)
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            pager = evaluate("(() => document.querySelector('.page-number-YYNlfP')?.innerText || '')()")
            if pager:
                break
            time.sleep(0.6)
        if pager:
            break
    if not pager:
        raise RuntimeError('Audio detail viewer did not open after observing stable generated cards.')
    pager = cli('get', 'text', '.page-number-YYNlfP')['value']
    if int(pager.split('/')[0]) != candidate_index + 1:
        raise RuntimeError(f'Detail viewer selected unexpected candidate: {pager}')
    download_ref = visible_ref('button.left-button-dckY70')
    before = time.time()
    cli('click', download_ref)
    result = cli('wait', 'download', '.mp3', '--timeout', '15000')
    path = Path(result['filename'])
    if result.get('state') != 'complete' or not path.is_file():
        raise RuntimeError(f'Download did not complete: {result}')
    if path.stat().st_mtime < before - 3:
        raise RuntimeError(f'Download response refers to an older file: {path}')
    data = probe(path)
    back = visible_ref('button.back-button-Msd9gi')
    cli('click', back)
    return {'candidate': candidate_index + 1, 'download_path': str(path),
            'download_id': result.get('id'), 'duration_seconds': data['duration'],
            'bytes': path.stat().st_size, 'sample_rate': data['audio']['sample_rate'],
            'channels': data['audio']['channels']}


def run_group(group, voice, journal, manifest):
    text = group.get('generation_text', group['text']).strip()
    if not text or len(text) > 200 or any(q in text for q in ['"', '“', '”']):
        raise RuntimeError('Generation text violates narration/200 character contract.')
    if text[-1] not in '.!?':
        raise RuntimeError(f'Generation text is not a complete sentence: {text[-45:]}')
    key = f"{group['version']}/{group['name']}"
    existing = next((r for r in manifest['clips'] if r['version'] == group['version']
                     and r['name'] == group['name']), None)
    if existing:
        if not Path(existing['local_path']).is_file():
            raise RuntimeError('Manifest refers to missing downloaded audio.')
        return 'skipped'
    state = snapshot()
    if 'workspace=23561838050060' not in state['url']:
        raise RuntimeError('Unexpected workspace; refusing to submit.')
    entry = journal.setdefault(key, {})
    record_key = entry.get('record_key')
    if not record_key:
        if entry.get('status') == 'submitting':
            candidates = [r for r in state['records'] if r['key'] not in entry['before_keys']
                          and norm(text) in norm(r['text'])]
            if len(candidates) != 1:
                raise RuntimeError('Previous submission uncertain; refusing duplicate credit use.')
            record_key = candidates[0]['key']
        else:
            ref = visible_ref('textarea.prompt-textarea-U6goqo')
            cli('fill', f'[data-opencli-ref="{ref}"]', text)
            ref = visible_ref('textarea.prompt-textarea-U6goqo')
            if cli('get', 'value', f'[data-opencli-ref="{ref}"]')['value'] != text:
                raise RuntimeError('Text readback differs from verified source.')
            form = evaluate(f'''(() => document.querySelector('[data-opencli-ref="{ref}"]')
                .closest('[data-generate-content-generator]').innerText)()''')
            if voice not in form or 'Seed TTS' not in form or '文本朗读' not in form:
                raise RuntimeError(f'Unexpected voice/model controls: {form}')
            before_keys = [r['key'] for r in state['records']]
            entry.update(status='submitting', text=text, character_count=len(text), voice=voice,
                         before_keys=before_keys)
            save(JOURNAL, journal)
            submit = visible_ref('button[data-generator-submit-available="true"]')
            cli('click', submit)
            deadline = time.monotonic() + 45
            while time.monotonic() < deadline:
                state = snapshot()
                if '积分不足' in state['text'] or '余额不足' in state['text']:
                    raise RuntimeError('Jimeng reports insufficient credits.')
                candidates = [r for r in state['records'] if r['key'] not in before_keys]
                if len(candidates) == 1:
                    record_key = candidates[0]['key']
                    break
                if len(candidates) > 1:
                    raise RuntimeError('Multiple new records; needs inspection.')
                time.sleep(1.5)
            if not record_key:
                raise RuntimeError('New generation record did not appear.')
        entry.update(record_key=record_key, status='submitted')
        save(JOURNAL, journal)
        print(json.dumps({'submitted':key, 'characters':len(text), 'record_key':record_key}, ensure_ascii=False), flush=True)
    deadline = time.monotonic() + 240
    ready = None
    while time.monotonic() < deadline:
        state = snapshot()
        if '积分不足' in state['text'] or '余额不足' in state['text']:
            raise RuntimeError('Jimeng reports insufficient credits.')
        rec = next((r for r in state['records'] if r['key'] == record_key), None)
        if rec and len(rec['cards']) >= 2 and all(v > 0 for v in durations(rec['cards'])):
            if norm(text) not in norm(rec['text']) or voice not in rec['text']:
                raise RuntimeError('Generated record prompt/voice differs from the requested source.')
            ready = rec
            break
        if rec and any(x in rec['text'] for x in ['生成失败', '审核未通过']):
            raise RuntimeError(f'Generation failed: {rec["text"][:300]}')
        time.sleep(2)
    if not ready:
        raise RuntimeError('Generation has not finished within the bounded wait; safe to resume.')
    shown = durations(ready['cards'])
    tied = [i for i, value in enumerate(shown) if value == min(shown)]
    entry.update(status='ready', displayed_durations=shown, handoff=ready['handoff'])
    save(JOURNAL, journal)
    candidates = []
    for idx in tied:
        candidate = download_candidate(record_key, idx)
        candidates.append(candidate)
        entry['downloaded_candidates'] = candidates
        save(JOURNAL, journal)
    selected = min(candidates, key=lambda c: c['duration_seconds'])
    source = Path(selected['download_path'])
    out = Path(group['output_dir']) / (group['name'] + '.mp3')
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.read_bytes() != source.read_bytes():
        raise RuntimeError(f'Refusing to replace different audio: {out}')
    if not out.exists():
        shutil.copy2(source, out)
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    if digest != hashlib.sha256(source.read_bytes()).hexdigest():
        raise RuntimeError('Copied audio hash differs from downloaded file.')
    row = {'version':group['version'], 'episode':group['episode'], 'name':group['name'],
           'local_path':str(out), 'status':'downloaded', 'model':'Seed TTS', 'voice_name':voice,
           'text':text, 'character_count':len(text), 'workspace':'23561838050060',
           'record_key':record_key, 'handoff':ready['handoff'],
           'displayed_candidate_seconds':shown, 'downloaded_candidates':candidates,
           'selected_candidate':selected['candidate'], 'duration_seconds':selected['duration_seconds'],
           'sha256':digest, 'selection_rule':'minimum display duration; tied outputs compared by measured duration',
           'speech_word_coverage':'generation text verified; offline ASR unavailable'}
    manifest['clips'].append(row)
    save(MANIFEST, manifest)
    entry.update(status='downloaded', local_path=str(out), selected_candidate=selected['candidate'])
    save(JOURNAL, journal)
    print(json.dumps({'saved':key, 'seconds':selected['duration_seconds'],
                      'displayed_candidates':shown, 'candidate':selected['candidate'],
                      'downloaded_total':len(manifest['clips'])}, ensure_ascii=False), flush=True)
    return 'downloaded'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', choices=['女版','性转版'], required=True)
    parser.add_argument('--voice', required=True)
    parser.add_argument('--limit', type=int, default=1)
    args = parser.parse_args()
    plan = json.loads(PLAN.read_text())
    manifest = json.loads(MANIFEST.read_text())
    manifest['expected_clip_count'] = plan['total_group_count']
    manifest['generation_plan'] = str(PLAN)
    journal = json.loads(JOURNAL.read_text()) if JOURNAL.exists() else {}
    done = 0
    for group in plan['groups']:
        if group['version'] != args.version or group.get('submit_generation') is False:
            continue
        result = run_group(group, args.voice, journal, manifest)
        if result == 'downloaded':
            done += 1
        if done >= args.limit:
            break
    print(json.dumps({'batch_finished':True, 'new_downloads':done,
                      'downloaded_total':len(manifest['clips'])}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(json.dumps({'stopped':str(exc)}, ensure_ascii=False), flush=True)
        raise SystemExit(1)
