from pathlib import Path
import datetime,importlib.metadata,json,sys,time

ROOT=Path.cwd()
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'达芬奇剪辑_EP21-25_20261020/转录'))
import run_local_asr as b
import mlx.core as mx,mlx_whisper
from mlx_whisper.audio import load_audio,SAMPLE_RATE

def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()

MODEL=b.OLD_ASR/'models/large-v3-turbo/weights'
manifest=ROOT/'对标音色旁白制作_20261020/制作与下载进度.json'
progress=json.loads(manifest.read_text())
items=sorted([x for x in progress['items'] if x['episode'] in (1,2,3)],key=lambda x:(x['episode'],x['narration_sequence']))
assert len(items)==24
assert {e:sum(x['episode']==e for x in items) for e in (1,2,3)}=={1:8,2:7,3:9}
old_asr=b.OLD_ASR/'transcripts_large-v3-turbo/女版'
old_base=ROOT/'配音制作_前3集/音频/女版'

idx={'started_at_utc':stamp(),'status':'running','model':'large-v3-turbo','model_local_path':str(MODEL),'python_executable':sys.executable,'python_version':sys.version,'mlx_version':importlib.metadata.version('mlx'),'mlx_whisper_version':importlib.metadata.version('mlx-whisper'),'device':str(mx.default_device()),'blind_transcription':True,'expected_script_supplied_to_model':False,'initial_prompt':None,'decode_parameters':b.PARAMETERS,'network_used':False,'source_media_modified':False,'human_listening_verified':False,'source_clock':'original source seconds, decoded at16kHz without retime','generation_text_manifest':str(manifest),'generation_text_manifest_sha256':b.digest(manifest),'target_new_count':24,'target_reused_old_EP01_count':8,'completed_new':0,'completed_reused_old':0,'errors':[],'files':[],'existing_old_word_ASR_available':[]}

# Report all known old sources without rerunning inference outside the authorized8.
for ep in (1,2,3):
 for p in sorted((old_base/f'第{ep:02d}集').glob('*.mp3')):
  ap=old_asr/(p.stem+'.json')
  if not ap.exists():continue
  old=json.loads(ap.read_text());h=b.digest(p)
  ok=h==old['sha256'] and bool(old.get('decode_parameters',{}).get('word_timestamps')) and all('words' in s for s in old['segments'])
  idx['existing_old_word_ASR_available'].append({'episode':ep,'source':str(p.resolve()),'source_sha256':h,'existing_ASR':str(ap.resolve()),'hash_and_word_timestamps_verified':ok})

for seq in range(1,9):
 p=old_base/'第01集'/f'大码女版01-01-{seq:02d}.mp3';ap=old_asr/(p.stem+'.json');old=json.loads(ap.read_text());h=b.digest(p)
 assert h==old['sha256'],p
 assert old['decode_parameters']['word_timestamps'] and all('words' in s for s in old['segments'])
 rec={'source':str(p.resolve()),'source_sha256':h,'kind':'old_EP01_narration','episode':1,'narration_sequence':seq,'duration':old['decoded_duration_seconds'],'text':old['text'],'segments':old['segments'],'blind':old['blind_transcription'],'human_listening_verified':False,'model':old['model'],'decode_parameters':old['decode_parameters'],'reused_existing_ASR':str(ap.resolve()),'reused_existing_ASR_sha256':b.digest(ap),'rerun_inference':False,'expected_script_supplied_to_model':old['expected_script_supplied_to_model']}
 target=OUT/(p.stem+'.json');b.save(target,rec);b.write_sidecars(rec,target)
 idx['files'].append({'episode':1,'sequence':seq,'kind':'old_EP01_narration','source':str(p.resolve()),'source_sha256':h,'json':str(target),'word_count':sum(len(s['words']) for s in rec['segments']),'duration':rec['duration'],'text':rec['text']});idx['completed_reused_old']+=1
b.save(OUT/'index.json',idx)
print('Reused8 hash-matched oldEP01 word-ASR records; additional existing oldEP02/03 paths indexed.',flush=True)

prov_path=b.OLD_ASR/'models/large-v3-turbo/provenance.json'
prov=json.loads(prov_path.read_text())
for m in prov['files']:
 p=MODEL/m['path'];assert b.digest(p)==m['sha256'],f'Model hash mismatch: {p}'
idx['model_provenance_path']=str(prov_path);idx['model_provenance_sha256']=b.digest(prov_path);idx['model_files_hash_verified']=True;b.save(OUT/'index.json',idx)

for item in items:
 p=Path(item['audio_file']);assert p.exists();h=b.digest(p);assert h==item['audio_sha256']
 target=OUT/(p.stem+'.json');t=time.monotonic()
 try:
  if target.exists():
   rec=json.loads(target.read_text());assert rec['source_sha256']==h
  else:
   audio=load_audio(str(p))
   raw=mlx_whisper.transcribe(audio,path_or_hf_repo=str(MODEL),**b.PARAMETERS)
   rec={'source':str(p.resolve()),'source_sha256':h,'kind':'new_benchmark_female_narration','episode':item['episode'],'narration_sequence':item['narration_sequence'],'duration':len(audio)/SAMPLE_RATE,'text':raw.get('text',''),'segments':raw.get('segments',[]),'blind':True,'human_listening_verified':False,'model':'large-v3-turbo','decode_parameters':b.PARAMETERS,'expected_script_supplied_to_model':False,'recognized_at_utc':stamp(),'generation_text_after_recognition_only':item['generation_text'],'generation_text_not_used_in_inference':True,'canonical_generation_text_sha256':item['generation_text_sha256']}
   b.save(target,rec)
  assert h==b.digest(p)
  assert all('words' in s for s in rec['segments'])
  b.write_sidecars(rec,target)
  idx['files'].append({'episode':item['episode'],'sequence':item['narration_sequence'],'kind':'new_benchmark_female_narration','source':str(p.resolve()),'source_sha256':h,'json':str(target),'word_count':sum(len(s['words']) for s in rec['segments']),'duration':rec['duration'],'canonical_generation_text':item['generation_text'],'text':rec['text']});idx['completed_new']+=1
  b.save(OUT/'index.json',idx)
  print(f"{idx['completed_new']:02d}/24 {p.name} {time.monotonic()-t:.2f}s {rec['text']}",flush=True)
 except Exception as exc:
  idx['errors'].append({'source':str(p),'error':repr(exc)});b.save(OUT/'index.json',idx);raise

idx['status']='complete';idx['completed_at_utc']=stamp();b.save(OUT/'index.json',idx)
print('COMPLETE new24+reusedold8, word-timed, original media unchanged, no listening acceptance claimed.',flush=True)
