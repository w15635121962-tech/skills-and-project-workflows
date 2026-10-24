# -*- coding: utf-8 -*-
"""Root-authorized blind small.en check of exact EP11-04-01, full + 6–11s.
No expected words, canonical script, prompt, audio changes or new TTS.
"""
from pathlib import Path
import importlib.util,json,sys,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('new_female_qc',HERE/'验收精确白名单.py')
q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
SOURCE=q.TASK/'音频/第11集/大码女版枕头11-04-01.mp3'
SOURCE_SHA='dab6413820d384a9c967487a572d9659a93f79513f1bded177fe6c95949469c5'
WHITE=HERE/'批次_EP11_03-04_冻结白名单.json'
WHITE_SHA='f8d5ac4d90abf6b0acbcd58f362e554760af7ac829bc3fe1c9874c2a7a780033'
assert q.digest(WHITE)==WHITE_SHA
wd=json.loads(WHITE.read_text(encoding='utf-8'))
f=next(x for x in wd['files']if x['source_path']==str(SOURCE))
assert f['sha256']==SOURCE_SHA and SOURCE.is_file() and not SOURCE.is_symlink()
assert SOURCE.resolve().is_relative_to(q.TASK.resolve())
assert q.digest(SOURCE)==SOURCE_SHA and SOURCE.stat().st_size==f['bytes']
before=SOURCE.stat()
engine,load_audio,sr,np,deps=q.runtime()
model=q.BASE/'models/small.en'
prov=json.loads((model/'provenance.json').read_text(encoding='utf-8'))
assert prov['revision']=='52a88bf6e98b114a210c21bb83e22d6e1505cb73'
for item in prov['files']:
    p=model/'weights'/item['path']
    assert p.is_file() and p.stat().st_size==item['bytes'] and q.digest(p)==item['sha256']
audio=load_audio(str(SOURCE));duration=len(audio)/sr
for label,start,end in [('full',0,duration),('06-11s',6,11)]:
    target=HERE/'secondary_small.en'/(SOURCE.stem+'_'+label+'.json')
    assert not target.exists(),'Never overwrite a blind secondary record'
    t0=time.monotonic()
    result=engine.transcribe(audio[round(start*sr):round(end*sr)],path_or_hf_repo=str(model/'weights'),**q.PARAMETERS)
    words=[]
    for s in result.get('segments',[]):
        for word in s.get('words',[]):
            words.append(dict(word,source_start_seconds=start+word['start'],source_end_seconds=start+word['end']))
    rec=dict(status='ROOT_AUTHORIZED_BLIND_SECONDARY_COMPLETE',source_path=str(SOURCE),source_sha256=SOURCE_SHA,whitelist=str(WHITE),whitelist_sha256=WHITE_SHA,source_range_seconds=[start,end],source_duration_seconds=duration,model='small.en',model_revision=prov['revision'],parameters=q.PARAMETERS,expected_text_supplied=False,canonical_script_loaded=False,initial_prompt=None,hotwords=None,text=result.get('text',''),segments=result.get('segments',[]),words=words,raw_result=result,source_audio_modified=False,human_listening_verified=False,runtime_seconds=time.monotonic()-t0)
    assert q.digest(SOURCE)==SOURCE_SHA and SOURCE.stat().st_size==before.st_size and SOURCE.stat().st_mtime_ns==before.st_mtime_ns
    q.save(target,rec)
    print(json.dumps(dict(path=str(target),text=rec['text'],source_range_seconds=[start,end],words=words),ensure_ascii=False),flush=True)
