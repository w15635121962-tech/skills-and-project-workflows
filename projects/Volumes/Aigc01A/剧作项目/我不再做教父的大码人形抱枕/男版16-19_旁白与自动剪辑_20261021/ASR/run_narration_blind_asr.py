#!/usr/bin/env python3
"""Local blind ASR of downloaded male EP16–19 narration; never reads the script.

Filename/episode labels are metadata only. Audio is decoded at its original speed.
Recognition receives audio and generic English transcription options, no script,
expected text, vocabulary, prompt, hotwords or forced transcript.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import traceback

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
PROJECT = BASE.parent
OLD_ASR = PROJECT / '配音制作_前3集/制作资料/音频内容与顺序核验_20261018/ASR'
COMPAT = PROJECT / '达芬奇剪辑_EP21-25_20261020/转录/runtime_compatible'
FFMPEG = '/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin'
PYTHON = '/Users/zc/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3.12'
sys.path[:0] = [str(COMPAT), str(OLD_ASR / '.venv/lib/python3.12/site-packages')]
os.environ['PATH'] = FFMPEG + os.pathsep + os.environ.get('PATH', '')
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN'] = '1'
EXPECTED_COUNTS = {16: 9, 17: 6, 18: 7, 19: 5}
PARAMETERS = dict(language='en', task='transcribe', temperature=0.0,
                  condition_on_previous_text=False, initial_prompt=None,
                  word_timestamps=True, fp16=True, verbose=None)


def stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def default(value):
    if hasattr(value, 'item'):
        return value.item()
    if hasattr(value, 'tolist'):
        return value.tolist()
    return str(value)


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=default) + '\n', encoding='utf-8')
    tmp.replace(path)


def srt_time(value):
    ms = max(0, round(float(value) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'


def sidecars(record, path):
    path.with_suffix('.txt').write_text(record['text'].strip() + '\n', encoding='utf-8')
    path.with_suffix('.segments.srt').write_text('\n'.join(f"{n}\n{srt_time(s['start'])} --> {srt_time(s['end'])}\n{s['text'].strip()}\n" for n, s in enumerate(record['segments'], 1)), encoding='utf-8-sig')
    with path.with_suffix('.words.tsv').open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f, delimiter='\t')
        w.writerow(['source_word_index', 'source_start_seconds', 'source_end_seconds', 'word', 'probability'])
        for n, word in enumerate(record['words']):
            w.writerow([n, word['start'], word['end'], word['word'], word.get('probability')])


def probe(path):
    proc = subprocess.run([str(Path(FFMPEG) / 'ffprobe'), '-v', 'error', '-show_format', '-show_streams', '-of', 'json', str(path)], capture_output=True, text=True, encoding='utf-8')
    if proc.returncode:
        raise RuntimeError('ffprobe rejected audio: ' + proc.stderr)
    return json.loads(proc.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--episodes', type=int, nargs='+', default=[16, 17, 18, 19])
    parser.add_argument('--only-existing', action='store_true', help='Transcribe only currently downloaded files, and report expected missing files.')
    parser.add_argument('--check-runtime', action='store_true', help='Verify local engine/model files without transcribing audio.')
    args = parser.parse_args()
    if not set(args.episodes) <= set(EXPECTED_COUNTS):
        raise SystemExit('Allowed scope: male EP16–19 only')

    import mlx.core as mx
    import mlx_whisper
    from mlx_whisper.audio import load_audio, SAMPLE_RATE
    provenance = json.loads((OLD_ASR / 'models/large-v3-turbo/provenance.json').read_text(encoding='utf-8'))
    model = OLD_ASR / 'models/large-v3-turbo/weights'
    for item in provenance['files']:
        if digest(model / item['path']) != item['sha256']:
            raise RuntimeError('Local model provenance mismatch: ' + item['path'])
    meta = dict(started_at_utc=stamp(), python_executable=sys.executable, required_python=PYTHON,
                python_version=sys.version, engine='mlx-whisper', engine_version=importlib.metadata.version('mlx-whisper'),
                mlx_version=importlib.metadata.version('mlx'), mlx_device=str(mx.default_device()),
                local_model_path=str(model), model_provenance=provenance, decode_parameters=PARAMETERS,
                audio_leaves_machine=False, blind_transcription=True, expected_script_supplied_to_model=False,
                source_text_manifest_read_by_recognizer=False, hotwords_supplied_to_model=False, forced_transcript=False,
                human_listening_validation=False, speed=1.0, audio_files_modified=False,
                timing_basis='Unretimed source-relative seconds; no timeline offset or artificial speed change.')
    if args.check_runtime:
        save(OUT / 'runtime_preflight.json', {**meta, 'runtime_preflight_only': True, 'audio_transcribed': False})
        print(json.dumps({k: meta[k] for k in ['python_executable', 'engine_version', 'mlx_device', 'local_model_path']}, ensure_ascii=False), flush=True)
        return

    rows, missing = [], []
    for ep in sorted(args.episodes):
        for seq in range(1, EXPECTED_COUNTS[ep] + 1):
            path = BASE / '音频' / f'第{ep:02d}集' / f'大码男版枕头{ep:02d}-{seq:02d}-01.mp3'
            row = dict(path=path, episode=ep, narration_sequence=seq, take=1)
            (rows if path.is_file() else missing).append(row)
    if missing and not args.only_existing:
        raise RuntimeError('Missing expected narration downloads: ' + ', '.join(r['path'].name for r in missing))
    if not rows:
        raise RuntimeError('No downloaded narration audio found; no ASR started')
    meta.update(selected_episodes=sorted(args.episodes), selected_input_count=len(rows),
                expected_missing_files=[str(r['path']) for r in missing])
    save(OUT / 'run_metadata.json', meta)
    index = {**meta, 'completed': 0, 'errors': [], 'files': []}
    for n, row in enumerate(rows, 1):
        path = row['path']
        target = OUT / 'raw_large-v3-turbo' / f"EP{row['episode']}" / 'narration' / (path.stem + '.json')
        started = time.monotonic()
        try:
            source_hash = digest(path)
            if target.exists():
                record = json.loads(target.read_text(encoding='utf-8'))
                if record.get('source_sha256') != source_hash or record.get('decode_parameters') != PARAMETERS:
                    raise RuntimeError('Existing ASR refers to different source audio or parameters; refusing stale reuse/overwrite')
            else:
                source_probe = probe(path)
                audio = load_audio(str(path))
                if not len(audio) or not bool((abs(audio) > 1e-7).any()):
                    raise RuntimeError('Empty or silent decoded audio')
                raw = mlx_whisper.transcribe(audio, path_or_hf_repo=str(model), **PARAMETERS)
                if digest(path) != source_hash:
                    raise RuntimeError('Source audio changed during ASR')
                segs = raw.get('segments', [])
                words = [w for s in segs for w in s.get('words', [])]
                duration = len(audio) / SAMPLE_RATE
                flags = []
                if not words:
                    flags.append('no_recognized_words')
                if any(w.get('probability', 1) < .6 for w in words):
                    flags.append('low_confidence_word')
                if any(s.get('avg_logprob', 0) < -.8 for s in segs):
                    flags.append('low_segment_logprob')
                if any(s.get('no_speech_prob', 0) > .5 for s in segs):
                    flags.append('high_no_speech_probability')
                if any(w['start'] < 0 or w['end'] > duration + .1 or w['end'] < w['start'] for w in words):
                    flags.append('word_time_out_of_source_bounds')
                if any(float(b['start']) < float(a['start']) for a, b in zip(words, words[1:])):
                    flags.append('nonmonotonic_word_starts')
                record = dict(source_path=str(path), source_relative_path=str(path.relative_to(PROJECT)),
                              source_sha256=source_hash, source_probe=source_probe, episode=row['episode'],
                              narration_sequence=row['narration_sequence'], take=row['take'], kind='narration',
                              decoded_duration_seconds=duration, decoded_sample_rate=SAMPLE_RATE,
                              recognized_at_utc=stamp(), engine='mlx-whisper', model='large-v3-turbo',
                              model_revision=provenance['revision'], decode_parameters=PARAMETERS,
                              blind_transcription=True, expected_script_supplied_to_model=False,
                              source_text_manifest_read_by_recognizer=False, speed=1.0,
                              human_listening_validation=False, text=raw.get('text', ''),
                              language=raw.get('language'), segments=segs, words=words,
                              quality_flags=flags, raw_result=raw, runtime_seconds=time.monotonic() - started)
                save(target, record)
            sidecars(record, target)
            summary = {k: record[k] for k in ['source_path', 'source_sha256', 'episode', 'narration_sequence', 'take', 'decoded_duration_seconds', 'text', 'quality_flags']}
            summary.update(json_path=str(target), source_word_tsv_path=str(target.with_suffix('.words.tsv')),
                           segment_count=len(record['segments']), word_count=len(record['words']))
            index['files'].append(summary)
            index['completed'] += 1
            save(OUT / '转录索引.json', index)
            print(json.dumps({'completed': n, 'total_available': len(rows), 'file': path.name, 'text': record['text'], 'flags': record['quality_flags']}, ensure_ascii=False), flush=True)
        except Exception as error:
            item = dict(source_path=str(path), error=str(error), traceback=traceback.format_exc())
            index['errors'].append(item)
            save(target.with_suffix('.error.json'), item)
            save(OUT / '转录索引.json', index)
            print(json.dumps(item, ensure_ascii=False), flush=True)
    index['finished_at_utc'] = stamp()
    index['all_selected_expected_downloads_present'] = not missing
    save(OUT / '转录索引.json', index)
    for ep in args.episodes:
        subset = [r for r in index['files'] if r['episode'] == ep]
        if subset:
            (OUT / f'EP{ep:02d}_旁白原始盲听写.txt').write_text('\n\n'.join(f"[{Path(r['source_path']).name}]\n{r['text'].strip()}" for r in subset) + '\n', encoding='utf-8')
    print(json.dumps({'finished': True, 'completed': index['completed'], 'errors': len(index['errors']), 'missing_downloads': len(missing)}, ensure_ascii=False), flush=True)
    if index['errors']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
