#!/usr/bin/env python3
"""Independent second-model blind ASR for low-confidence first-pass sources."""
import json
import re
import time
from pathlib import Path
import run_local_asr as base


def main():
    import mlx_whisper
    from mlx_whisper.audio import load_audio, SAMPLE_RATE
    out = base.OUT
    first = json.loads((out/'转录索引.json').read_text())
    rows = [x for x in first['files'] if x['quality_flags']]
    meta = json.loads((base.OLD_ASR/'models/small.en/provenance.json').read_text())
    model = base.OLD_ASR/'models/small.en/weights'
    for asset in meta['files']:
        if base.digest(model/asset['path'])!=asset['sha256']:
            raise RuntimeError('Second-model file hash mismatch')
    index = dict(model='small.en', model_provenance=meta,
                 decode_parameters=base.PARAMETERS, blind_transcription=True,
                 expected_script_supplied_to_model=False, human_listening_validation=False,
                 selection='all sources with nonempty large-v3-turbo quality flags',
                 audio_leaves_machine=False, selected_count=len(rows), completed=0, files=[])
    for row in rows:
        start = time.monotonic()
        source = Path(row['source_path'])
        sha = base.digest(source)
        if sha!=row['source_sha256']:raise RuntimeError('Changed source hash')
        audio = load_audio(str(source))
        raw = mlx_whisper.transcribe(audio, path_or_hf_repo=str(model), **base.PARAMETERS)
        segments = raw.get('segments', [])
        words = [w for seg in segments for w in seg.get('words', [])]
        record = dict(source_path=str(source), source_sha256=sha,
                      episode=row['episode'], kind=row['kind'], decoded_duration_seconds=len(audio)/SAMPLE_RATE,
                      model='small.en', model_revision=meta['revision'], decode_parameters=base.PARAMETERS,
                      blind_transcription=True, expected_script_supplied_to_model=False,
                      human_listening_validation=False, text=raw.get('text',''),
                      segments=segments, words=words, raw_result=raw,
                      first_pass_json=row['json_path'], first_pass_text=row['text'],
                      first_pass_quality_flags=row['quality_flags'], recognized_at_utc=base.stamp())
        target=out/'raw_small.en_review'/f"EP{row['episode']}"/row['kind']/(source.stem+'.json')
        base.save(target,record)
        base.write_sidecars(record,target)
        clean=lambda text:re.findall(r"[a-z]+(?:'[a-z]+)?",text.lower())
        from difflib import SequenceMatcher
        ratio=SequenceMatcher(None,clean(row['text']),clean(record['text']),autojunk=False).ratio()
        index['files'].append(dict(source_path=str(source),episode=row['episode'],kind=row['kind'],
                                   first_pass_text=row['text'],second_pass_text=record['text'],
                                   token_sequence_similarity=ratio, review_json=str(target),
                                   first_pass_quality_flags=row['quality_flags']))
        index['completed']+=1
        base.save(out/'第二模型复核索引.json',index)
        print(json.dumps(dict(completed=index['completed'],total=len(rows),source=source.name,
                              text=record['text'],similarity=round(ratio,3),
                              runtime=round(time.monotonic()-start,2)),ensure_ascii=False),flush=True)
    index['finished_at_utc']=base.stamp()
    base.save(out/'第二模型复核索引.json',index)


if __name__=='__main__':main()
