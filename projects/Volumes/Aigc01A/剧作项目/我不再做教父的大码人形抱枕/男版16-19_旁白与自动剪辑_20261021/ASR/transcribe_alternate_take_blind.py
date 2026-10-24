#!/usr/bin/env python3
"""Blind ASR for an explicitly downloaded alternate narration take, no script input."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('blind_runtime', HERE / 'run_narration_blind_asr.py')
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('basename')
ap.add_argument('--allow-primary', action='store_true', help='Reuse existing primary ASR and add an independent small.en pass, preserving original output.')
args = ap.parse_args()
match = re.fullmatch(r'大码男版枕头(16|17|18|19)-(\d{2})-(\d{2})', args.basename)
assert match, 'Explicit male EP16–19 narration alternate take required'
ep, seq, take = map(int, match.groups())
assert take > 1 or args.allow_primary
source = runtime.BASE / '音频' / f'第{ep}集' / (args.basename + '.mp3')
assert source.is_file()

import mlx_whisper
from mlx_whisper.audio import load_audio, SAMPLE_RATE

source_hash = runtime.digest(source)
audio = load_audio(str(source))
duration = len(audio) / SAMPLE_RATE
assert len(audio) and bool((abs(audio) > 1e-7).any())
probe = runtime.probe(source)
results = []
for name in ['large-v3-turbo', 'small.en']:
    model_base = runtime.OLD_ASR / 'models' / name
    model = model_base / 'weights'
    provenance = json.loads((model_base / 'provenance.json').read_text(encoding='utf-8'))
    for item in provenance['files']:
        assert runtime.digest(model / item['path']) == item['sha256']
    target = HERE / ('raw_large-v3-turbo' if name == 'large-v3-turbo' else '第二次盲复核_替代次') / f'EP{ep}' / 'narration' / (args.basename + '.json')
    started = time.monotonic()
    if target.exists():
        record = json.loads(target.read_text(encoding='utf-8'))
        assert record['source_sha256'] == source_hash and record['decode_parameters'] == runtime.PARAMETERS
    else:
        raw = mlx_whisper.transcribe(audio, path_or_hf_repo=str(model), **runtime.PARAMETERS)
        assert runtime.digest(source) == source_hash
        segs = raw.get('segments', [])
        words = [w for s in segs for w in s.get('words', [])]
        flags = []
        if not words:
            flags.append('no_recognized_words')
        if any(w.get('probability', 1) < .6 for w in words):
            flags.append('low_confidence_word')
        if any(w['start'] < 0 or w['end'] < w['start'] or w['end'] > duration + .1 for w in words):
            flags.append('word_time_out_of_source_bounds')
        record = dict(source_path=str(source), source_relative_path=str(source.relative_to(runtime.PROJECT)),
                      source_sha256=source_hash, source_probe=probe, episode=ep, narration_sequence=seq,
                      take=take, kind='narration', decoded_duration_seconds=duration, decoded_sample_rate=SAMPLE_RATE,
                      recognized_at_utc=runtime.stamp(), engine='mlx-whisper', model=name,
                      model_revision=provenance['revision'], decode_parameters=runtime.PARAMETERS,
                      blind_transcription=True, expected_script_supplied_to_model=False,
                      source_text_manifest_read_by_recognizer=False, speed=1.0, human_listening_validation=False,
                      text=raw.get('text', ''), language=raw.get('language'), segments=segs, words=words,
                      quality_flags=flags, raw_result=raw, runtime_seconds=time.monotonic() - started)
        runtime.save(target, record)
    runtime.sidecars(record, target)
    results.append({'model': name, 'text': record['text'], 'quality_flags': record['quality_flags'], 'json_path': str(target)})
    print(json.dumps(results[-1], ensure_ascii=False), flush=True)
runtime.save(HERE / (args.basename + '_替代次双模型盲识别.json'), {'source_path': str(source), 'source_sha256': source_hash, 'duration_seconds': duration, 'speed': 1.0, 'files': results, 'source_audio_modified': False, 'expected_text_supplied_to_recognition': False})
