#!/usr/bin/env python3
"""Local, cached, blind word-timed transcription of this task's exact inventory.

No script text, expected dialogue, hotword or initial prompt is read or supplied.
No Resolve connection, source mutation, network upload, or generation.
"""
from pathlib import Path
import datetime as dt
import hashlib
import importlib.metadata
import importlib.util
import json
import os
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
TASK = HERE.parent
PROJECT = TASK.parent
RUNTIME_SCRIPT = PROJECT / '\u7537\u724809-15_\u65c1\u767d_20261021/ASR/run_blind_asr.py'
spec = importlib.util.spec_from_file_location('blind_existing_runtime', RUNTIME_SCRIPT)
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import mlx_whisper
from mlx_whisper.audio import load_audio, SAMPLE_RATE

PARAMETERS = dict(language='en', task='transcribe', temperature=0.0,
                  condition_on_previous_text=False, initial_prompt=None,
                  word_timestamps=True, fp16=True, verbose=None)

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def default(value):
    if hasattr(value, 'item'):
        return value.item()
    if hasattr(value, 'tolist'):
        return value.tolist()
    return str(value)

def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + '.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=default) + '\n', encoding='utf-8')
    tmp.replace(path)

def main():
    model_base = runtime.OLD_ASR / 'models/large-v3-turbo'
    model = model_base / 'weights'
    provenance = json.loads((model_base / 'provenance.json').read_text(encoding='utf-8'))
    for item in provenance['files']:
        assert digest(model / item['path']) == item['sha256'], 'Local model provenance mismatch'
    inventory_path = TASK / '\u7d20\u6750\u76d8\u70b9.json'
    inventory = json.loads(inventory_path.read_text(encoding='utf-8'))
    episodes = sorted(inventory['episodes'], key=lambda x: x['episode'])
    assert [x['episode'] for x in episodes] == [7, 8, 9, 12, 13, 14, 15]
    rows = []
    for episode in episodes:
        ep = episode['episode']
        for group in episode['video_groups']:
            for version, path, duration in zip(group['versions'], group['paths_in_version_order'], group['durations_seconds']):
                rows.append(dict(episode=ep, kind='video', order=[group['group'], version], source_path=path, source_duration_seconds=duration))
        for seq, (path, duration) in enumerate(zip(episode['narration_paths_in_order'], episode['narration_durations_in_order']), 1):
            rows.append(dict(episode=ep, kind='narration', order=[seq, 1], source_path=path, source_duration_seconds=duration))
    assert len(rows) == 123 and sum(x['kind'] == 'video' for x in rows) == 85
    metadata = dict(started_at_utc=now(), python_executable=sys.executable, python_version=sys.version,
                    engine='mlx-whisper', engine_version=importlib.metadata.version('mlx-whisper'),
                    model='large-v3-turbo', local_model_path=str(model), model_revision=provenance['revision'],
                    decode_parameters=PARAMETERS, audio_leaves_machine=False,
                    expected_script_supplied_to_model=False, hotwords_supplied=False,
                    blind_transcription=True, human_listening_validation=False,
                    source_files_modified=False, inventory_path=str(inventory_path),
                    inventory_sha256=digest(inventory_path), total_files=len(rows))
    save(HERE / 'run_metadata.json', metadata)
    index = dict(**metadata, files=[], errors=[], completed=0, episodes_completed=[])
    for episode in episodes:
        ep = episode['episode']
        for row in [r for r in rows if r['episode'] == ep]:
            source = Path(row['source_path'])
            target = HERE / 'raw_large-v3-turbo' / ('EP%02d' % ep) / row['kind'] / (source.stem + '.json')
            started = time.monotonic()
            try:
                sha = digest(source)
                if target.exists():
                    rec = json.loads(target.read_text(encoding='utf-8'))
                    assert rec['source_sha256'] == sha and rec['decode_parameters'] == PARAMETERS, 'Cached source/parameters mismatch'
                else:
                    audio = load_audio(str(source))
                    decoded_duration = len(audio) / SAMPLE_RATE
                    assert decoded_duration > 0
                    raw = mlx_whisper.transcribe(audio, path_or_hf_repo=str(model), **PARAMETERS)
                    assert digest(source) == sha, 'Source changed during transcription'
                    segments = raw.get('segments', [])
                    words = [w for s in segments for w in s.get('words', [])]
                    flags = []
                    if not words:
                        flags.append('no_recognized_words')
                    if any(w.get('probability', 1) < .6 for w in words):
                        flags.append('low_confidence_word')
                    if any(s.get('avg_logprob', 0) < -.8 for s in segments):
                        flags.append('low_segment_logprob')
                    if any(s.get('no_speech_prob', 0) > .5 for s in segments):
                        flags.append('high_no_speech_probability')
                    if any(w['start'] < 0 or w['end'] < w['start'] or w['end'] > decoded_duration + .1 for w in words):
                        flags.append('word_time_out_of_source_bounds')
                    rec = dict(**row, source_sha256=sha, decoded_duration_seconds=decoded_duration,
                               decoded_sample_rate=SAMPLE_RATE, recognized_at_utc=now(),
                               engine='mlx-whisper', model='large-v3-turbo', model_revision=provenance['revision'],
                               decode_parameters=PARAMETERS, blind_transcription=True,
                               expected_script_supplied_to_model=False, human_listening_validation=False,
                               text=raw.get('text', ''), segments=segments, words=words,
                               quality_flags=flags, raw_result=raw, runtime_seconds=time.monotonic()-started)
                    save(target, rec)
                runtime.sidecars(rec, target)
                summary = {k: rec[k] for k in ['episode', 'kind', 'order', 'source_path', 'source_sha256', 'decoded_duration_seconds', 'text', 'quality_flags']}
                summary.update(json_path=str(target), word_count=len(rec['words']))
                index['files'].append(summary)
                index['completed'] += 1
                save(HERE / '\u8f6c\u5f55\u7d22\u5f15.json', index)
                print(json.dumps(dict(completed=index['completed'], total=len(rows), episode=ep, kind=row['kind'], file=source.name, text=rec['text'], flags=rec['quality_flags'], runtime_seconds=round(time.monotonic()-started, 2)), ensure_ascii=False), flush=True)
            except Exception as exc:
                error = dict(**row, error=str(exc), traceback=traceback.format_exc(), failed_at_utc=now())
                index['errors'].append(error)
                save(target.with_suffix('.error.json'), error)
                save(HERE / '\u8f6c\u5f55\u7d22\u5f15.json', index)
                print(json.dumps(error, ensure_ascii=False), flush=True)
        subset = [x for x in index['files'] if x['episode'] == ep]
        errors = [x for x in index['errors'] if x['episode'] == ep]
        report = dict(episode=ep, files=subset, errors=errors,
                      video_count=sum(x['kind'] == 'video' for x in subset),
                      narration_count=sum(x['kind'] == 'narration' for x in subset),
                      no_recognized_words=[Path(x['source_path']).name for x in subset if 'no_recognized_words' in x['quality_flags']],
                      expected_script_supplied_to_model=False, human_listening_validation=False)
        save(HERE / ('EP%02d_complete.json' % ep), report)
        (HERE / ('EP%02d_raw_transcript.txt' % ep)).write_text('\n\n'.join('[%s] %s\n%s' % (x['kind'], Path(x['source_path']).name, x['text']) for x in subset) + '\n', encoding='utf-8')
        index['episodes_completed'].append(ep)
        save(HERE / '\u8f6c\u5f55\u7d22\u5f15.json', index)
        print(json.dumps(dict(episode_complete=ep, files=len(subset), video_count=report['video_count'], narration_count=report['narration_count'], errors=len(errors)), ensure_ascii=False), flush=True)
    index['finished_at_utc'] = now()
    save(HERE / '\u8f6c\u5f55\u7d22\u5f15.json', index)
    if index['errors']:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
