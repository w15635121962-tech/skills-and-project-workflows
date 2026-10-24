from pathlib import Path
import sys,json,time,hashlib
root=Path.cwd()
sys.path.insert(0,str(root/'达芬奇剪辑_EP21-25_20261020/转录'))
import run_local_asr as b
import mlx_whisper
from mlx_whisper.audio import load_audio,SAMPLE_RATE
out=Path(__file__).resolve().parent/'ASR';out.mkdir(exist_ok=True)
model=b.OLD_ASR/'models/large-v3-turbo/weights'
meta=json.loads((b.OLD_ASR/'models/large-v3-turbo/provenance.json').read_text())
files=sorted([*Path('剧梦生成视频片段/女版/EP26').glob('*.mp4'),*Path('剧梦生成视频片段/女版/EP28').glob('*.mp4')])
index={'model':'large-v3-turbo','blind':True,'human_listening_verified':False,'expected_script_supplied':False,'files':[]}
for p in files:
 t=time.monotonic();target=out/(p.stem+'.json');sha=b.digest(p)
 if target.exists():rec=json.loads(target.read_text())
 else:
  au=load_audio(str(p));raw=mlx_whisper.transcribe(au,path_or_hf_repo=str(model),**b.PARAMETERS)
  rec={'source':str(p.resolve()),'source_sha256':sha,'duration':len(au)/SAMPLE_RATE,'text':raw.get('text',''),'segments':raw.get('segments',[]),'blind':True,'human_listening_verified':False,'model':'large-v3-turbo','decode_parameters':b.PARAMETERS}
  b.save(target,rec)
 assert sha==b.digest(p)
 index['files'].append({'source':str(p.resolve()),'json':str(target),'text':rec['text']});b.save(out/'index.json',index)
 print(p.name,round(time.monotonic()-t,2),rec['text'],flush=True)
