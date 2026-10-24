import json,re,subprocess,concurrent.futures
from pathlib import Path
import soundfile as sf,numpy as np
from faster_whisper import WhisperModel
O=Path(__file__).parent;A=O/'ASR完整';A.mkdir(exist_ok=True)
R=json.loads((O/'full_scan_manifest.json').read_text())
def num(r):return int(re.search(r'C(\d+)',r['name']).group(1))
S=[r for r in R if (r['group']=='001' and num(r) in [139,140,162,163,164,165]) or (r['group']=='003' and num(r) in list(range(141,144))+list(range(232,237)))]
(O/'formal_candidates.json').write_text(json.dumps(S,ensure_ascii=False,indent=2))
def extract(r):
 w=A/(r['key']+'_channels.wav')
 if not w.exists():subprocess.run(['/Users/xuan/.local/bin/ffmpeg','-v','error','-i',r['path'],'-vn','-ar','16000','-y',str(w)],check=True)
 x,sr=sf.read(w,dtype='float32',always_2d=True);rms=np.sqrt(np.mean(x*x,axis=0));peak=np.max(np.abs(x),axis=0)
 j=int(np.argmax(rms));print('AUDIO',r['key'],'rms',rms.tolist(),'peak',peak.tolist(),'choose',j,flush=True)
 return {'r':r,'w':str(w),'channel':j,'rms':rms.tolist(),'peak':peak.tolist()}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex: E=list(ex.map(extract,S))
(O/'formal_audio_channels.json').write_text(json.dumps(E,ensure_ascii=False,indent=2))
m=WhisperModel('small',device='cpu',compute_type='int8',download_root='/Users/xuan/.local/share/promo-audio/models',cpu_threads=4,local_files_only=True)
for e in E:
 r=e['r'];target=A/(r['key']+'.json')
 if target.exists():continue
 x,sr=sf.read(e['w'],dtype='float32',always_2d=True);audio=x[:,e['channel']]
 seg,info=m.transcribe(audio,language='zh',beam_size=5,word_timestamps=True,vad_filter=True,initial_prompt='文汇中学教育集团，党委坚持为党育人、为国育才。党建引领铸魂固本。和而不同，和实生物，各美其美，美美与共。一校一品，特色办学。心智、多元、开放、成长。文行兼修的君子品格，汇通中西的开放视野，胜任未来的创新能力。')
 ss=[{'start':s.start,'end':s.end,'text':s.text,'words':[{'start':w.start,'end':w.end,'word':w.word,'p':w.probability} for w in (s.words or [])]} for s in seg]
 d={'key':r['key'],'path':r['path'],'duration':r['duration'],'channel':e['channel'],'channel_rms':e['rms'],'segments':ss,'asr_note':'Local faster-whisper small. Text is ASR and requires source verification for exact orthography. Times relative to source.'}
 target.write_text(json.dumps(d,ensure_ascii=False,indent=2));print('ASR',r['key'],[(s['start'],s['end'],s['text']) for s in ss],flush=True)
