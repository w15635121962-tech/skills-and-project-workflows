#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Blind local Whisper ASR. Expected script text is never passed to a model."""
from __future__ import annotations

import argparse
import datetime
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import sys
import time
import traceback
from pathlib import Path

BASE = Path(__file__).resolve().parent
PROJECT_DATA = BASE.parent.parent
DEFAULT_MANIFEST = PROJECT_DATA / '已下载音频清单.json'
MODELS = {
    'small.en': 'mlx-community/whisper-small.en-mlx',
    'medium.en': 'mlx-community/whisper-medium.en-mlx',
    'large-v3-turbo': 'mlx-community/whisper-large-v3-turbo',
}
PARAMETERS = {
    'language': 'en', 'task': 'transcribe', 'temperature': 0.0,
    'condition_on_previous_text': False, 'initial_prompt': None,
    'word_timestamps': True, 'fp16': True, 'verbose': None,
}


def stamp():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def json_default(value):
    if hasattr(value, 'item'):
        return value.item()
    if hasattr(value, 'tolist'):
        return value.tolist()
    return str(value)


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + f'.{os.getpid()}.tmp')
    with temp.open('w', encoding='utf-8') as stream:
        json.dump(data, stream, ensure_ascii=False, indent=2, default=json_default)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    temp.replace(path)


def emit(**data):
    print(json.dumps(data, ensure_ascii=False, default=json_default), flush=True)


def natural(value):
    return [int(piece) if piece.isdigit() else piece for piece in re.split(r'(\d+)', value)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument('--model', choices=list(MODELS), default='small.en')
    parser.add_argument('--only', nargs='*', help='Optional exact audio names for an independent second-model review')
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    os.environ['HF_HOME'] = str(BASE / 'huggingface_cache')
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
    os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN'] = '1'
    # This system Python lacks its framework CA bundle; use the OS trust roots.
    # HTTPS certificate verification remains enabled for all model downloads.
    os.environ['SSL_CERT_FILE'] = '/etc/ssl/cert.pem'
    os.environ['REQUESTS_CA_BUNDLE'] = '/etc/ssl/cert.pem'
    from huggingface_hub import HfApi, snapshot_download
    import mlx.core as mx
    import mlx_whisper
    from mlx_whisper.audio import load_audio, SAMPLE_RATE

    repo = MODELS[args.model]
    model_meta_path = BASE / 'models' / args.model / 'provenance.json'
    model_dir = model_meta_path.parent / 'weights'
    if model_meta_path.is_file():
        model_meta = json.loads(model_meta_path.read_text(encoding='utf-8'))
        revision = model_meta['revision']
        if model_meta['repo_id'] != repo:
            raise RuntimeError('Saved model provenance does not match the selected model.')
    else:
        info = HfApi(token=False).model_info(repo)
        revision = info.sha
        emit(model_download_start=repo, revision=revision)
        snapshot_download(repo, revision=revision, local_dir=str(model_dir), token=False)
        model_meta = {
            'engine': 'mlx-whisper', 'model': args.model, 'repo_id': repo, 'revision': revision,
            'downloaded_at_utc': stamp(), 'local_model_path': str(model_dir),
            'engine_primary_documentation': 'https://github.com/ml-explore/mlx-examples/tree/main/whisper',
            'model_primary_source': f'https://huggingface.co/{repo}/tree/{revision}',
            'files': [{'path': str(p.relative_to(model_dir)), 'bytes': p.stat().st_size, 'sha256': digest(p)}
                      for p in sorted(model_dir.rglob('*')) if p.is_file() and '.cache' not in p.parts],
        }
        save(model_meta_path, model_meta)
    for item in model_meta['files']:
        path = model_dir / item['path']
        if not path.is_file() or digest(path) != item['sha256']:
            raise RuntimeError(f'Model file is missing/changed: {path}')
    packages = {}
    for package in ('mlx-whisper', 'mlx', 'mlx-metal', 'numpy', 'numba', 'huggingface-hub'):
        try:
            packages[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            pass
    runtime = {'python': sys.version, 'python_executable': sys.executable,
               'machine': platform.machine(), 'platform': platform.platform(),
               'mlx_default_device': str(mx.default_device()), 'packages': packages}
    manifest_bytes = args.manifest.read_bytes()
    source = json.loads(manifest_bytes)
    # Deliberately retain only file identity/order fields. Neither source dialogue
    # nor generation_text/text is used, stored in decode options, or sent to ASR.
    inputs = [{key: row[key] for key in ('version', 'episode', 'name', 'local_path', 'sha256')}
              for row in source['clips']]
    inputs.sort(key=lambda item: (0 if item['version'] == '女版' else 1,
                                 item['episode'], natural(item['name'])))
    if args.only:
        requested = set(args.only)
        inputs = [item for item in inputs if item['name'] in requested]
        if {item['name'] for item in inputs} != requested:
            raise RuntimeError('Some requested review filenames are absent from the manifest.')
    if args.limit is not None:
        inputs = inputs[:args.limit]
    output = BASE / f'transcripts_{args.model}'
    run_metadata = {'started_at_utc': stamp(), 'engine': runtime, 'model': model_meta,
                    'decode_parameters': PARAMETERS, 'blind_transcription': True,
                    'expected_script_supplied_to_model': False,
                    'hotwords_supplied_to_model': False, 'forced_transcript': False,
                    'manifest_path': str(args.manifest),
                    'manifest_sha256': hashlib.sha256(manifest_bytes).hexdigest(),
                    'input_count': len(inputs), 'inputs': inputs}
    save(output / 'run_metadata.json', run_metadata)
    progress = {'started_at_utc': stamp(), 'model': args.model, 'total': len(inputs),
                'completed': [], 'errors': []}
    for index, item in enumerate(inputs, 1):
        path = Path(item['local_path'])
        out = output / item['version'] / (item['name'] + '.json')
        actual = digest(path)
        if actual != item['sha256']:
            raise RuntimeError(f'Original audio SHA256 differs from manifest: {path}')
        if out.is_file():
            existing = json.loads(out.read_text(encoding='utf-8'))
            if existing.get('sha256') != actual or existing.get('model_revision') != revision or existing.get('decode_parameters') != PARAMETERS:
                raise RuntimeError(f'Existing ASR checkpoint does not match audio/model/options: {out}')
            progress['completed'].append({'name': item['name'], 'version': item['version'], 'path': str(out), 'resumed': True})
            save(output / 'progress.json', progress)
            emit(resumed=index, total=len(inputs), name=item['name'], path=str(out))
            continue
        try:
            started = time.monotonic()
            audio = load_audio(str(path))
            raw = mlx_whisper.transcribe(audio, path_or_hf_repo=str(model_dir), **PARAMETERS)
            if digest(path) != actual:
                raise RuntimeError('Original audio bytes changed during recognition.')
            record = {**item, 'sha256': actual, 'audio_bytes': path.stat().st_size,
                      'decoded_duration_seconds': len(audio) / SAMPLE_RATE,
                      'decoded_sample_rate': SAMPLE_RATE, 'engine': 'mlx-whisper',
                      'engine_version': packages['mlx-whisper'], 'model': args.model,
                      'model_repo_id': repo, 'model_revision': revision,
                      'decode_parameters': PARAMETERS, 'blind_transcription': True,
                      'expected_script_supplied_to_model': False,
                      'recognized_at_utc': stamp(), 'runtime_seconds': time.monotonic() - started,
                      'text': raw.get('text', ''), 'language': raw.get('language'),
                      'segments': raw.get('segments', []), 'raw_result': raw}
            save(out, record)
            progress['completed'].append({'name': item['name'], 'version': item['version'], 'path': str(out)})
            save(output / 'progress.json', progress)
            emit(completed=index, total=len(inputs), name=item['name'], path=str(out),
                 text=record['text'], runtime_seconds=round(record['runtime_seconds'], 3))
        except Exception as exc:
            failure = {'name': item['name'], 'version': item['version'], 'error': str(exc),
                       'traceback': traceback.format_exc(), 'failed_at_utc': stamp()}
            progress['errors'].append(failure)
            save(output / 'progress.json', progress)
            save(output / item['version'] / (item['name'] + '.error.json'), failure)
            emit(failed=item['name'], error=str(exc))
    progress['finished_at_utc'] = stamp()
    save(output / 'progress.json', progress)
    emit(asr_finished=True, completed=len(progress['completed']), errors=len(progress['errors']),
         output_dir=str(output))
    if progress['errors']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
