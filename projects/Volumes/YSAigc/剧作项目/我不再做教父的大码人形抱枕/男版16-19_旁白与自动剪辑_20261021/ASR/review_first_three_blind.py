#!/usr/bin/env python3
"""Secondary blind recognition of the first three actual downloads, no script."""
import importlib.util
from pathlib import Path
import json
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('blind_runtime', HERE / 'run_narration_blind_asr.py')
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
import mlx_whisper
from mlx_whisper.audio import load_audio, SAMPLE_RATE

OUT = HERE / '第二次盲复核_前三段'
OUT.mkdir(exist_ok=True)
model_base = runtime.OLD_ASR / 'models'
models = {'small.en': model_base / 'small.en/weights', 'large-v3-turbo': model_base / 'large-v3-turbo/weights'}
for name in models:
    provenance = json.loads((model_base / name / 'provenance.json').read_text(encoding='utf-8'))
    for item in provenance['files']:
        assert runtime.digest(models[name] / item['path']) == item['sha256']

crops = {1: [(8.7, 12.95)], 2: [(6.4, 11.0)], 3: [(0.0, 2.8), (3.2, 6.5), (7.0, 10.5)]}
results = []
for seq in [1, 2, 3]:
    source = runtime.BASE / '音频/第16集' / f'大码男版枕头16-{seq:02d}-01.mp3'
    source_hash = runtime.digest(source)
    audio = load_audio(str(source))
    duration = len(audio) / SAMPLE_RATE
    cases = [('small.en', 0.0, duration)] + [('large-v3-turbo', a, min(z, duration)) for a, z in crops[seq]]
    for name, start, end in cases:
        target = OUT / f'{source.stem}_{name}_{start:.2f}-{end:.2f}.json'
        if target.exists():
            record = json.loads(target.read_text(encoding='utf-8'))
            assert record['source_sha256'] == source_hash
        else:
            started = time.monotonic()
            raw = mlx_whisper.transcribe(audio[int(start * SAMPLE_RATE):int(end * SAMPLE_RATE)], path_or_hf_repo=str(models[name]), **runtime.PARAMETERS)
            assert runtime.digest(source) == source_hash
            record = {'source_path': str(source), 'source_sha256': source_hash, 'source_clip_start_seconds': start, 'source_clip_end_seconds': end,
                      'model': name, 'decode_parameters': runtime.PARAMETERS, 'blind_transcription': True,
                      'expected_text_or_hotwords_supplied': False, 'source_speed': 1.0,
                      'text': raw.get('text', ''), 'words': [w for s in raw.get('segments', []) for w in s.get('words', [])],
                      'raw_result': raw, 'runtime_seconds': time.monotonic() - started}
            runtime.save(target, record)
        results.append({**{k: record[k] for k in ['source_path', 'model', 'source_clip_start_seconds', 'source_clip_end_seconds', 'text']}, 'json_path': str(target)})
        print(json.dumps(results[-1], ensure_ascii=False), flush=True)
runtime.save(OUT / '第二次盲识别索引.json', {'files': results, 'source_files_modified': False, 'human_listening_performed': False, 'expected_text_supplied': False})
