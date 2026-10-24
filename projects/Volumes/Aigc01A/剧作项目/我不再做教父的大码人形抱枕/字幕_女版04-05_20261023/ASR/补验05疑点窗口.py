# -*- coding: utf-8 -*-
from pathlib import Path
import importlib.util,json,hashlib,time
p=Path(__file__).with_name('盲识别两集时间线混音.py');spec=importlib.util.spec_from_file_location('blindruntime',p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
engine,load,sr,np,deps=m.runtime();d,data=m.load_whitelist();f=next(x for x in d['files'] if x['episode']==5);source=Path(f['source_path']);assert m.digest(source)==f['sha256']
a=load(str(source));out=[]
for tag,st,en in [('APPENDED_HEAD',138.,153.),('ACTOR_TAIL',103.,118.0666667)]:
 target=m.HERE/'blind_windows'/f'EP05_{tag}.json'
 if target.exists():
  old=json.loads(target.read_text(encoding='utf-8'));assert old['source_sha256']==f['sha256'] and old['window_start_seconds']==st and old['window_end_seconds']==en;out.append({'tag':tag,'cached':True,'text':old['raw_result']['text']});continue
 x=a[round(st*sr):round(en*sr)];res=engine.transcribe(x,path_or_hf_repo=str(m.MODEL/'weights'),**m.PARAMETERS)
 ws=[dict(w,export_start_seconds=w['start']+st,export_end_seconds=w['end']+st) for s in res['segments'] for w in s.get('words',[])]
 m.save(target,dict(status='BLIND_WINDOW_NO_CANONICAL_PROMPT',source_path=str(source),source_sha256=f['sha256'],window_start_seconds=st,window_end_seconds=en,model='large-v3-turbo',parameters=m.PARAMETERS,expected_text_loaded=False,raw_result=res,words=ws,source_modified=False,human_listening_performed=False))
 out.append({'tag':tag,'cached':False,'text':res['text'],'words':ws})
assert m.WHITELIST.read_bytes()==data
print(json.dumps(out,ensure_ascii=False),flush=True)
