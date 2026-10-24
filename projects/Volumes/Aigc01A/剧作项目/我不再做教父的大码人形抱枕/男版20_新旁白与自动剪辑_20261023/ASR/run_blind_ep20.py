#!/usr/bin/env python3
"""Inventory-only male EP20 source-video blind ASR. Default is NO recognition.

Supply --inventory <completed explicit inventory.json> to validate; add --execute
only when that inventory has been reviewed. Never opens UI or connects Resolve.
No source script, dialogue, initial prompt or hotword enters the recognizer.
"""
from pathlib import Path
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import re
import sys
import time
import traceback

HERE = Path(__file__).resolve().parent
TASK = HERE.parent
PROJECT = TASK.parent
PARAMETERS = dict(language='en', task='transcribe', temperature=0.0,
                  condition_on_previous_text=False, initial_prompt=None,
                  word_timestamps=True, fp16=True, verbose=None)

def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()

def default(x):
    if hasattr(x, 'item'):
        return x.item()
    if hasattr(x, 'tolist'):
        return x.tolist()
    return str(x)

def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name+'.tmp')
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=default)+'\n', encoding='utf-8')
    tmp.replace(path)

def source_rows(inventory):
    """Known explicit inventory schemas only. No filesystem discovery or guessing."""
    if isinstance(inventory.get('files'), list):
        videos = [x for x in inventory['files'] if x.get('kind')=='video']
        assert videos and {x.get('episode') for x in videos}=={20}, 'Flat inventory must explicitly identify male EP20 videos'
        episodes = [dict(episode=20,files=videos)]
    elif isinstance(inventory.get('episodes'), list):
        episodes = inventory['episodes']
        assert episodes and {e['episode'] for e in episodes} == {20}, 'Inventory must be male EP20 only'
    else:
        assert inventory.get('episode') == 20 or inventory.get('scope_episodes') == [20], 'Explicit EP20 inventory scope required'
        episodes = [inventory]
    rows = []
    for episode in episodes:
        if 'files' in episode:
            rows.extend(dict(x) for x in episode['files'] if x.get('kind') == 'video')
        elif 'video_groups' in episode:
            for group in episode['video_groups']:
                paths = group['paths_in_version_order']
                for i, path in enumerate(paths):
                    row = dict(path=path, group=group['group'])
                    if i < len(group.get('versions', [])):
                        row['take'] = group['versions'][i]
                    rows.append(row)
        elif 'videos' in episode:
            for video in episode['videos']:
                rows.append(dict(video) if isinstance(video, dict) else dict(path=video))
        elif 'video_files' in episode:
            for video in episode['video_files']:
                rows.append(dict(video) if isinstance(video, dict) else dict(path=video))
        else:
            raise AssertionError('Unsupported inventory schema; explicitly adapt after reading the actual inventory')
    assert rows, 'No inventoried source video'
    output = []
    for row in rows:
        raw_path = row.get('path') or row.get('source_path')
        assert raw_path, row
        path = Path(raw_path)
        assert path.is_absolute() and path.is_file() and path.stat().st_size > 0, str(path)
        assert path.suffix.lower() in {'.mp4','.mov','.m4v','.mkv'}, 'Video inventory only'
        assert row.get('episode',20) == 20, 'Wrong episode row'
        # Version is given by explicit inventory/root review, not inferred from a generic directory label.
        if row.get('version'):
            assert row['version'] in {'male','\u7537\u7248','\u6027\u8f6c\u7248'}
        output.append(dict(source_path=str(path), input_metadata=row))
    assert len({x['source_path'] for x in output}) == len(output), 'Duplicate inventoried source path'
    return output

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--inventory', required=True)
    parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    inventory_path = Path(args.inventory).resolve()
    inventory = json.loads(inventory_path.read_text(encoding='utf-8'))
    rows = source_rows(inventory)
    if not args.execute:
        print(json.dumps(dict(status='INVENTORY_VALIDATED_ASR_NOT_STARTED',episode=20,video_count=len(rows),inventory=str(inventory_path),source_files_modified=False),ensure_ascii=False))
        return
    # Import local compatibility/runtime only AFTER explicit execution stage.
    old_script = PROJECT / '\u7537\u724809-15_\u65c1\u767d_20261021/ASR/run_blind_asr.py'
    spec = importlib.util.spec_from_file_location('existing_blind_runtime', old_script)
    runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runtime)
    import mlx_whisper
    from mlx_whisper.audio import load_audio,SAMPLE_RATE
    model_base = runtime.OLD_ASR/'models/large-v3-turbo'
    model = model_base/'weights'
    provenance = json.loads((model_base/'provenance.json').read_text(encoding='utf-8'))
    for item in provenance['files']:
        assert digest(model/item['path']) == item['sha256'], 'Local model checksum mismatch'
    index = dict(episode=20,kind='male_source_video',input_count=len(rows),completed=0,
                 inventory_path=str(inventory_path),inventory_sha256=digest(inventory_path),
                 started_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
                 python_executable=sys.executable,engine='mlx-whisper',model='large-v3-turbo',
                 model_revision=provenance['revision'],local_model_path=str(model),
                 decode_parameters=PARAMETERS,expected_script_supplied_to_model=False,
                 hotwords_supplied=False,audio_leaves_machine=False,
                 source_files_modified=False,resolve_connected=False,
                 human_listening_verified=False,files=[],errors=[])
    save(HERE/'run_metadata.json',{k:v for k,v in index.items() if k not in ['files','errors']})
    for row in rows:
        source = Path(row['source_path'])
        target = HERE/'raw_large-v3-turbo'/'video'/(source.stem+'.json')
        try:
            sha = digest(source)
            expected = row['input_metadata'].get('sha256') or row['input_metadata'].get('source_sha256')
            if expected:
                assert expected == sha, 'Inventoried source hash changed'
            started = time.monotonic()
            if target.exists():
                rec = json.loads(target.read_text(encoding='utf-8'))
                assert rec['source_sha256'] == sha and rec['decode_parameters'] == PARAMETERS, 'Cache source/parameter mismatch'
            else:
                audio = load_audio(str(source));duration = len(audio)/SAMPLE_RATE
                assert duration > 0
                result = mlx_whisper.transcribe(audio,path_or_hf_repo=str(model),**PARAMETERS)
                assert digest(source) == sha, 'Source changed during ASR'
                segments = result.get('segments',[])
                words = [w for s in segments for w in s.get('words',[])]
                flags=[]
                if not words: flags.append('no_recognized_words')
                if any(w.get('probability',1)<.6 for w in words): flags.append('low_confidence_word')
                if any(s.get('avg_logprob',0)<-.8 for s in segments): flags.append('low_segment_logprob')
                if any(s.get('no_speech_prob',0)>.5 for s in segments): flags.append('high_no_speech_probability')
                if any(s.get('compression_ratio',0)>2.4 for s in segments): flags.append('high_repetition_possible_hallucination')
                if any(w['end']<=w['start'] for w in words): flags.append('zero_duration_word_timing')
                if any(w['start']<0 or w['end']<w['start'] or w['end']>duration+.1 for w in words): flags.append('word_time_out_of_bounds')
                rec=dict(**row,source_sha256=sha,episode=20,kind='video',text=result.get('text',''),
                         decoded_duration_seconds=duration,decoded_sample_rate=SAMPLE_RATE,
                         segments=segments,words=words,quality_flags=flags,raw_result=result,
                         model='large-v3-turbo',model_revision=provenance['revision'],decode_parameters=PARAMETERS,
                         expected_script_supplied_to_model=False,human_listening_verified=False,
                         runtime_seconds=time.monotonic()-started)
                save(target,rec)
            runtime.sidecars(rec,target)
            index['files'].append(dict(source_path=str(source),source_sha256=sha,json_path=str(target),
                                       text=rec['text'],word_count=len(rec['words']),quality_flags=rec['quality_flags']))
            index['completed']+=1
            save(HERE/'index.json',index)
            print(json.dumps(dict(completed=index['completed'],total=len(rows),file=source.name,text=rec['text'],quality_flags=rec['quality_flags']),ensure_ascii=False),flush=True)
        except Exception as exc:
            error=dict(source_path=str(source),error=str(exc),traceback=traceback.format_exc())
            index['errors'].append(error);save(target.with_suffix('.error.json'),error);save(HERE/'index.json',index)
            print(json.dumps(error,ensure_ascii=False),flush=True)
    index['finished_at_utc']=dt.datetime.now(dt.timezone.utc).isoformat()
    save(HERE/'index.json',index)
    if index['errors']:
        raise SystemExit(1)

if __name__=='__main__':
    main()
