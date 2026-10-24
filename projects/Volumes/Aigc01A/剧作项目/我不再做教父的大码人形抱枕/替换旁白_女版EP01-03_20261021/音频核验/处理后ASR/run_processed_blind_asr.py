from pathlib import Path
import datetime,hashlib,json,sys,time
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent;BASE=OUT.parent.parent
sys.path.insert(0,str(ROOT/'达芬奇剪辑_EP21-25_20261020/转录'))
import run_local_asr as b
import mlx_whisper
from mlx_whisper.audio import load_audio,SAMPLE_RATE

MODEL=b.OLD_ASR/'models/large-v3-turbo/weights'
idx={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'running','blind':True,'expected_script_supplied_to_model':False,'word_timestamps':True,'model':'large-v3-turbo','model_path':str(MODEL),'decode_parameters':b.PARAMETERS,'network_used':False,'audio_modified':False,'human_listening_verified':False,'files':[]}
for ep in (1,2,3):
 p=OUT.parent/f'EP{ep:02d}_替换后旁白监听.wav';h=b.digest(p);target=OUT/f'EP{ep:02d}_处理后盲ASR.json';t=time.monotonic()
 if target.exists():
  rec=json.loads(target.read_text());assert rec['source_sha256']==h
 else:
  a=load_audio(str(p));raw=mlx_whisper.transcribe(a,path_or_hf_repo=str(MODEL),**b.PARAMETERS)
  rec={'episode':ep,'source':str(p.resolve()),'source_sha256':h,'duration':len(a)/SAMPLE_RATE,'text':raw.get('text',''),'segments':raw.get('segments',[]),'blind':True,'word_timestamps':True,'expected_script_supplied_to_model':False,'model':'large-v3-turbo','decode_parameters':b.PARAMETERS,'human_listening_verified':False,'runtime_seconds':time.monotonic()-t}
  b.save(target,rec)
 assert h==b.digest(p)
 b.write_sidecars(rec,target)
 idx['files'].append({'episode':ep,'source':str(p.resolve()),'source_sha256':h,'json':str(target),'duration':rec['duration'],'word_count':sum(len(s['words']) for s in rec['segments']),'text':rec['text']})
 b.save(OUT/'index.json',idx)
 print(f'EP{ep:02d} {time.monotonic()-t:.2f}s {rec["text"]}',flush=True)
idx['status']='complete';idx['completed_at_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();b.save(OUT/'index.json',idx)
