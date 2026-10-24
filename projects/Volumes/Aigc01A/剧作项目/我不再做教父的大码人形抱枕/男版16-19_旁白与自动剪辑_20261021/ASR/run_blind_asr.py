#!/usr/bin/env python3
"""Offline blind transcription of all male EP16-19 sources.

No script, expected text, hotwords or dialogue is supplied to recognition.
The episode/file labels are metadata and never passed into the model.
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

OUT=Path(__file__).resolve().parent
PROJECT=OUT.parent.parent
OLD_ASR=PROJECT/'配音制作_前3集/制作资料/音频内容与顺序核验_20261018/ASR'
COMPAT=PROJECT/'达芬奇剪辑_EP21-25_20261020/转录/runtime_compatible'
sys.path[:0]=[str(COMPAT),str(OLD_ASR/'.venv/lib/python3.12/site-packages')]
FFMPEG='/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin'
os.environ['PATH']=FFMPEG+os.pathsep+os.environ.get('PATH','')
os.environ['HF_HUB_OFFLINE']='1'
os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
os.environ['HF_HUB_DISABLE_IMPLICIT_TOKEN']='1'
PARAMETERS=dict(language='en',task='transcribe',temperature=0.0,
                condition_on_previous_text=False,initial_prompt=None,
                word_timestamps=True,fp16=True,verbose=None)

def stamp():return dt.datetime.now(dt.timezone.utc).isoformat()
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def default(x):
    if hasattr(x,'item'):return x.item()
    if hasattr(x,'tolist'):return x.tolist()
    return str(x)
def save(p,d):
    p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_name(p.name+'.tmp')
    tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2,default=default)+'\n',encoding='utf-8')
    tmp.replace(p)
def srt_time(t):
    ms=max(0,round(float(t)*1000));h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'
def sidecars(record,p):
    segs=record['segments']
    p.with_suffix('.segments.srt').write_text('\n'.join(f"{n}\n{srt_time(s['start'])} --> {srt_time(s['end'])}\n{s['text'].strip()}\n" for n,s in enumerate(segs,1)),encoding='utf-8-sig')
    with p.with_suffix('.words.tsv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f,delimiter='\t');w.writerow(['segment','source_start_seconds','source_end_seconds','word','probability'])
        for n,s in enumerate(segs,1):
            for word in s.get('words',[]):w.writerow([n,word['start'],word['end'],word['word'],word.get('probability')])
    p.with_suffix('.txt').write_text(record['text'].strip()+'\n',encoding='utf-8')
def rollups(index):
    for ep in range(16,20):
        rows=sorted((x for x in index['files'] if x['episode']==ep),key=lambda x:(0 if x['kind']=='video' else 1,x['order_key']))
        (OUT/f'EP{ep}_原始盲听写.txt').write_text('\n\n'.join(f"[{r['kind']}] {Path(r['source_path']).name}\n{r['text'].strip()}" for r in rows)+'\n',encoding='utf-8')

def main():
    import mlx.core as mx
    import mlx_whisper
    from mlx_whisper.audio import load_audio,SAMPLE_RATE
    provenance=json.loads((OLD_ASR/'models/large-v3-turbo/provenance.json').read_text(encoding='utf-8'))
    model=OLD_ASR/'models/large-v3-turbo/weights'
    for item in provenance['files']:
        if digest(model/item['path'])!=item['sha256']:raise RuntimeError('Local model provenance mismatch')
    inventory_path=OUT.parent/'准备/media_inventory.json'
    inventory=json.loads(inventory_path.read_text(encoding='utf-8'))
    rows=[]
    for ep in inventory['episodes']:
        for kind,key in [('video','videos')]:
            for row in ep[key]:
                rows.append(dict(path=row['path'],episode=ep['episode'],kind=kind,duration_seconds=row['duration_seconds'],order_key=row['episode_group_segment']))
    assert len(rows)==48
    # Resolve the two filename ambiguities early, without prompting recognition.
    def priority(r):
        name=Path(r['path']).name
        early=(r['kind']=='narration' and r['episode']==21 and name.startswith('男版21-5-')) or (r['kind']=='video' and r['episode']==24 and name in ('男版4-7-1.mp4','男版24-7-2.mp4'))
        return (0 if early else 1,r['episode'],0 if r['kind']=='video' else 1,r['order_key'])
    rows.sort(key=priority)
    meta=dict(started_at_utc=stamp(),python_executable=sys.executable,python_version=sys.version,
              engine='mlx-whisper',engine_version=importlib.metadata.version('mlx-whisper'),mlx_version=importlib.metadata.version('mlx'),mlx_device=str(mx.default_device()),
              local_model_path=str(model),model_provenance=provenance,decode_parameters=PARAMETERS,
              audio_leaves_machine=False,blind_transcription=True,expected_script_supplied_to_model=False,
              hotwords_supplied_to_model=False,forced_transcript=False,human_listening_validation=False,
              timing_basis='source-relative seconds, not timeline times',source_inventory_path=str(inventory_path),input_count=len(rows),
              source_kind_counts={'video':48,'narration':0})
    save(OUT/'run_metadata.json',meta)
    index=dict(**meta,completed=0,errors=[],files=[])
    for n,row in enumerate(rows,1):
        p=Path(row['path']);target=OUT/'raw_large-v3-turbo'/f"EP{row['episode']}"/row['kind']/(p.stem+'.json')
        started=time.monotonic()
        try:
            sha=digest(p)
            if target.exists():
                record=json.loads(target.read_text(encoding='utf-8'))
                if record.get('source_sha256')!=sha or record.get('decode_parameters')!=PARAMETERS:raise RuntimeError('Existing output does not match source or parameters')
            else:
                audio=load_audio(str(p))
                raw=mlx_whisper.transcribe(audio,path_or_hf_repo=str(model),**PARAMETERS)
                if digest(p)!=sha:raise RuntimeError('Source changed during transcription')
                segments=raw.get('segments',[]);words=[w for s in segments for w in s.get('words',[])]
                dur=len(audio)/SAMPLE_RATE;flags=[]
                if not words:flags.append('no_recognized_words')
                if any(w.get('probability',1)<0.6 for w in words):flags.append('low_confidence_word')
                if any(s.get('avg_logprob',0)<-0.8 for s in segments):flags.append('low_segment_logprob')
                if any(s.get('no_speech_prob',0)>0.5 for s in segments):flags.append('high_no_speech_probability')
                if any(w['start']<0 or w['end']>dur+0.1 or w['end']<w['start'] for w in words):flags.append('word_time_out_of_source_bounds')
                record=dict(source_path=str(p),source_relative_path=str(p.relative_to(PROJECT)),source_sha256=sha,
                            episode=row['episode'],kind=row['kind'],order_key=row['order_key'],source_probe_duration=row['duration_seconds'],
                            decoded_duration_seconds=dur,decoded_sample_rate=SAMPLE_RATE,recognized_at_utc=stamp(),
                            engine='mlx-whisper',model='large-v3-turbo',model_revision=provenance['revision'],decode_parameters=PARAMETERS,
                            blind_transcription=True,expected_script_supplied_to_model=False,human_listening_validation=False,
                            text=raw.get('text',''),language=raw.get('language'),segments=segments,words=words,
                            quality_flags=flags,raw_result=raw,runtime_seconds=time.monotonic()-started)
                save(target,record)
            sidecars(record,target)
            summary={k:record[k] for k in ('source_path','source_relative_path','source_sha256','episode','kind','order_key','decoded_duration_seconds','text','quality_flags')}
            summary.update(json_path=str(target),source_segment_srt_path=str(target.with_suffix('.segments.srt')),source_word_tsv_path=str(target.with_suffix('.words.tsv')),segment_count=len(record['segments']),word_count=len(record['words']))
            index['files'].append(summary);index['completed']+=1
            save(OUT/'转录索引.json',index);rollups(index)
            print(json.dumps(dict(completed=n,total=len(rows),file=p.name,text=record['text'],flags=record['quality_flags'],runtime_seconds=round(time.monotonic()-started,2)),ensure_ascii=False),flush=True)
        except Exception as e:
            error=dict(source_path=str(p),error=str(e),traceback=traceback.format_exc())
            index['errors'].append(error);save(target.with_suffix('.error.json'),error);save(OUT/'转录索引.json',index)
            print(json.dumps(error,ensure_ascii=False),flush=True)
    index['finished_at_utc']=stamp();save(OUT/'转录索引.json',index);rollups(index)
    print(json.dumps(dict(finished=True,completed=index['completed'],errors=len(index['errors'])),ensure_ascii=False),flush=True)
    if index['errors']:raise SystemExit(1)

if __name__=='__main__':main()
