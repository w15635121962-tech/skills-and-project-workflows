#!/usr/bin/env python3
"""Offline blind English ASR, with source-relative segment and word times.

No scripts, expected dialogue, prompts, or hotwords enter recognition.
Original media and all alternative takes remain untouched.
"""
from __future__ import annotations

import csv
import datetime as dt
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import re
import sys
import time
import traceback

OUT = Path(__file__).resolve().parent
PROJECT = OUT.parent.parent
OLD_ASR = PROJECT / '配音制作_前3集/制作资料/音频内容与顺序核验_20261018/ASR'
sys.path[:0] = [str(OUT / 'runtime_compatible'),
                str(OLD_ASR / '.venv/lib/python3.12/site-packages')]
FFMPEG_DIR = '/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin'
os.environ['PATH'] = FFMPEG_DIR + os.pathsep + os.environ.get('PATH', '')
os.environ['HF_HUB_OFFLINE'] = '1'
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN'] = '1'

PARAMETERS = dict(language='en', task='transcribe', temperature=0.0,
                  condition_on_previous_text=False, initial_prompt=None,
                  word_timestamps=True, fp16=True, verbose=None)


def stamp():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def digest(p):
    h = hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()


def json_default(x):
    if hasattr(x, 'item'):
        return x.item()
    if hasattr(x, 'tolist'):
        return x.tolist()
    return str(x)


def save(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2,
                              default=json_default)+'\n', encoding='utf-8')
    tmp.replace(p)


def natural(s):
    return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', s)]


def srt_time(t):
    ms = max(0, round(float(t)*1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'


def write_sidecars(record, path):
    segments = record['segments']
    srt = []
    for n, seg in enumerate(segments, 1):
        srt.append(f"{n}\n{srt_time(seg['start'])} --> {srt_time(seg['end'])}\n{seg['text'].strip()}\n")
    path.with_suffix('.segments.srt').write_text('\n'.join(srt), encoding='utf-8-sig')
    with path.with_suffix('.words.tsv').open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['segment', 'start', 'end', 'word', 'probability'])
        for n, seg in enumerate(segments, 1):
            for word in seg.get('words', []):
                writer.writerow([n, word['start'], word['end'], word['word'], word.get('probability')])


def main():
    import mlx.core as mx
    import mlx_whisper
    from mlx_whisper.audio import load_audio, SAMPLE_RATE
    model_meta = json.loads((OLD_ASR/'models/large-v3-turbo/provenance.json').read_text())
    model = OLD_ASR / 'models/large-v3-turbo/weights'
    for item in model_meta['files']:
        p = model/item['path']
        if digest(p) != item['sha256']:
            raise RuntimeError(f'Model hash mismatch: {p}')
    inventory_path = OUT.parent/'素材盘点.json'
    inventory = json.loads(inventory_path.read_text())
    rows = [x for x in inventory['files'] if x['kind']=='video'
            or '/女版/独白/' in x['relative_path']]
    rows.sort(key=lambda x: (x['episode'], 0 if x['kind']=='video' else 1,
                             natural(Path(x['path']).name)))
    if len(rows)!=82:
        raise RuntimeError(f'Expected 82 canonical sources; got {len(rows)}')
    metadata = dict(started_at_utc=stamp(), python_executable=sys.executable,
                    python_version=sys.version, engine='mlx-whisper',
                    engine_version=importlib.metadata.version('mlx-whisper'),
                    mlx_version=importlib.metadata.version('mlx'),
                    mlx_device=str(mx.default_device()),
                    local_model_path=str(model), model_provenance=model_meta,
                    decode_parameters=PARAMETERS, audio_leaves_machine=False,
                    blind_transcription=True, expected_script_supplied_to_model=False,
                    hotwords_supplied_to_model=False, forced_transcript=False,
                    human_listening_validation=False,
                    timing_basis='source-relative seconds from ASR alignment; not timeline time',
                    source_inventory_path=str(inventory_path), input_count=len(rows))
    save(OUT/'run_metadata.json', metadata)
    index = dict(**metadata, completed=0, errors=[], files=[])
    for n, row in enumerate(rows, 1):
        path = Path(row['path'])
        kind = 'video' if row['kind']=='video' else 'narration'
        target = OUT/'raw_large-v3-turbo'/f"EP{row['episode']}"/kind/(path.stem+'.json')
        try:
            started = time.monotonic()
            sha = digest(path)
            if sha != row['sha256']:
                raise RuntimeError('Source media differs from inventory SHA256')
            if target.exists():
                record = json.loads(target.read_text())
                if record.get('source_sha256')!=sha or record.get('decode_parameters')!=PARAMETERS:
                    raise RuntimeError('Existing output does not match source or options')
            else:
                audio = load_audio(str(path))
                raw = mlx_whisper.transcribe(audio, path_or_hf_repo=str(model), **PARAMETERS)
                if digest(path)!=sha:
                    raise RuntimeError('Source bytes changed during recognition')
                segments = raw.get('segments', [])
                words = [w for seg in segments for w in seg.get('words', [])]
                duration = len(audio)/SAMPLE_RATE
                flags = []
                if not words: flags.append('no_recognized_words')
                if any(w.get('probability',1)<0.6 for w in words): flags.append('low_confidence_word')
                if any(s.get('avg_logprob',0)<-0.8 for s in segments): flags.append('low_segment_logprob')
                if any(s.get('no_speech_prob',0)>0.5 for s in segments): flags.append('high_no_speech_probability')
                if any(w['end']>duration+0.1 or w['start']<0 or w['end']<w['start'] for w in words): flags.append('word_time_out_of_source_bounds')
                record = dict(source_path=str(path), source_relative_path=row['relative_path'],
                              source_sha256=sha, episode=row['episode'], kind=kind,
                              source_probe_duration=row['duration_seconds'], decoded_duration_seconds=duration,
                              decoded_sample_rate=SAMPLE_RATE, recognized_at_utc=stamp(),
                              engine='mlx-whisper', model='large-v3-turbo',
                              model_revision=model_meta['revision'], decode_parameters=PARAMETERS,
                              blind_transcription=True, expected_script_supplied_to_model=False,
                              human_listening_validation=False, text=raw.get('text',''),
                              language=raw.get('language'), segments=segments, words=words,
                              quality_flags=flags, raw_result=raw,
                              runtime_seconds=time.monotonic()-started)
                save(target, record)
            write_sidecars(record, target)
            summary = {k:record[k] for k in ['source_path','source_relative_path','source_sha256',
                       'episode','kind','decoded_duration_seconds','text','quality_flags']}
            summary.update(json_path=str(target), source_segment_srt_path=str(target.with_suffix('.segments.srt')),
                           source_word_tsv_path=str(target.with_suffix('.words.tsv')),
                           segment_count=len(record['segments']), word_count=len(record['words']))
            index['files'].append(summary)
            index['completed']+=1
            save(OUT/'转录索引.json',index)
            with (OUT/f"EP{row['episode']}_原始听写.txt").open('a', encoding='utf-8') as f:
                f.write(f"\n[{kind}] {path.name}\n{record['text'].strip()}\n")
            print(json.dumps(dict(completed=n,total=len(rows),file=path.name,
                                  text=record['text'],flags=record['quality_flags'],
                                  runtime=round(time.monotonic()-started,2)),ensure_ascii=False),flush=True)
        except Exception as exc:
            error=dict(source_path=str(path),error=str(exc),traceback=traceback.format_exc())
            index['errors'].append(error)
            save(target.with_suffix('.error.json'),error)
            save(OUT/'转录索引.json',index)
            print(json.dumps(error,ensure_ascii=False),flush=True)
    index['finished_at_utc']=stamp()
    save(OUT/'转录索引.json',index)
    print(json.dumps(dict(finished=True,completed=index['completed'],errors=len(index['errors'])),ensure_ascii=False),flush=True)
    if index['errors']:raise SystemExit(1)


if __name__=='__main__':
    main()
