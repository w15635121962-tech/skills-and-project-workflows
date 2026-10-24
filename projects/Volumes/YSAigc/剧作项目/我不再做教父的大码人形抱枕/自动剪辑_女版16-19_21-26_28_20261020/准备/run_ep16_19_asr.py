from pathlib import Path
import sys,json,time
root=Path.cwd();sys.path.insert(0,str(root/'达芬奇剪辑_EP21-25_20261020/转录'))
import run_local_asr as b
import mlx_whisper
from mlx_whisper.audio import load_audio,SAMPLE_RATE
out=Path(__file__).resolve().parent/'EP16-19_ASR';out.mkdir(exist_ok=True)
model=b.OLD_ASR/'models/large-v3-turbo/weights'
vbase=root/'剧梦生成视频片段/大码枕头EP16-19/大码枕头/视频分镜'
abase=root/'对标音色旁白制作_20261020/音频'
files=[]
for ep in [16,17,18,19]:
 files.extend(sorted((vbase/f'{ep}集').glob('*.mp4')))
for ep in [16,17,18,19]:
 files.extend(sorted((abase/f'第{ep:02d}集').glob('*.mp3')))
index={'model':'large-v3-turbo','blind':True,'human_listening_verified':False,'expected_script_supplied':False,'files':[]}
for p in files:
 t=time.monotonic();target=out/(p.stem+'.json');sha=b.digest(p)
 if target.exists():rec=json.loads(target.read_text())
 else:
  au=load_audio(str(p));raw=mlx_whisper.transcribe(au,path_or_hf_repo=str(model),**b.PARAMETERS)
  rec={'source':str(p.resolve()),'source_sha256':sha,'duration':len(au)/SAMPLE_RATE,'text':raw.get('text',''),'segments':raw.get('segments',[]),'blind':True,'human_listening_verified':False,'model':'large-v3-turbo','decode_parameters':b.PARAMETERS};b.save(target,rec)
 assert sha==b.digest(p)
 index['files'].append({'source':str(p.resolve()),'json':str(target),'text':rec['text']});b.save(out/'index.json',index)
 print(p.name,round(time.monotonic()-t,2),rec['text'],flush=True)
