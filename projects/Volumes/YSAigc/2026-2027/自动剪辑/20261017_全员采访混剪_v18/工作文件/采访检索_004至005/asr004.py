import json,pathlib,av,numpy as np,time
from faster_whisper import WhisperModel
ROOT=pathlib.Path(__file__).resolve().parent;(ROOT/'ASR').mkdir(exist_ok=True)
D=json.loads(pathlib.Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_学校粗剪/工作文件/footage.json').read_text())
A=[x for x in D if x['group']=='004' and (55<=int(x['name'][5:8])<=69 or 169<=int(x['name'][5:8])<=216)]
priority=[68,69,179,191,192,65,175,178,213,215,216];A.sort(key=lambda x:(priority.index(int(x['name'][5:8])) if int(x['name'][5:8]) in priority else 100+int(x['name'][5:8])))
m=WhisperModel('/Users/xuan/.local/share/promo-audio/models/models--Systran--faster-whisper-small/snapshots/536b0662742c02347bc0e980a01041f333bce120',device='cpu',compute_type='int8',cpu_threads=3,num_workers=1)
for x in A:
 o=ROOT/'ASR'/(x['key']+'.json')
 if o.exists():continue
 with av.open(x['path']) as c:
  s=c.streams.audio[0];res=av.AudioResampler(format='flt',layout='mono',rate=16000);v=[];ener=[]
  for f in c.decode(s):
   a=f.to_ndarray();ener.append(np.mean(np.square(a.astype('float64')),axis=1))
   for z in res.resample(f):v.append(z.to_ndarray().flatten())
  for z in res.resample(None):v.append(z.to_ndarray().flatten())
 audio=np.concatenate(v).astype('float32');segments,info=m.transcribe(audio,language='zh',beam_size=5,word_timestamps=True,vad_filter=True,condition_on_previous_text=False)
 segments=[{'start':q.start,'end':q.end,'text':q.text,'avg_logprob':q.avg_logprob,'words':[{'start':w.start,'end':w.end,'word':w.word,'probability':w.probability} for w in q.words]} for q in segments]
 data={'source':x['path'],'duration':x['duration'],'model':'faster-whisper-small local int8','audio_channels':s.codec_context.channels,'input_method':'native 4ch mono mix','segments':segments,'text':''.join(z['text'] for z in segments)}
 o.write_text(json.dumps(data,ensure_ascii=False,indent=2));print(x['name'],data['text'],flush=True)
