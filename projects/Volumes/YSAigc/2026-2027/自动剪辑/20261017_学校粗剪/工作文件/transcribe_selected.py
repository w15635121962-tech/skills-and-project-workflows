import json,re,sys,subprocess,soundfile as sf
from pathlib import Path
from faster_whisper import WhisperModel
OUT=Path(__file__).parent
rows=json.loads((OUT/'footage.json').read_text())
specs=json.loads(sys.argv[1]);sel=[]
for group,nums in specs:
 for n in nums:
  matches=[r for r in rows if r['group']==group and re.search(r'C0*'+str(n)+r'(?:_|\.)',r['name'])]
  if len(matches)==1:sel.append(matches[0])
  else:print('MATCH ERROR',group,n,len(matches),flush=True)
model=WhisperModel('small',device='cpu',compute_type='int8',download_root='/Users/xuan/.local/share/promo-audio/models',cpu_threads=6,local_files_only=True)
(OUT/'speech').mkdir(exist_ok=True)
for r in sel:
 target=OUT/'speech'/(r['key']+'.json')
 if target.exists():continue
 wav=OUT/'speech'/(r['key']+'.wav')
 subprocess.run(['/Users/xuan/.local/bin/ffmpeg','-v','error','-i',r['path'],'-vn','-ac','1','-ar','16000','-y',str(wav)],check=True)
 audio,sr=sf.read(wav,dtype='float32')
 assert sr==16000
 segments,info=model.transcribe(audio,language='zh',beam_size=5,word_timestamps=True,vad_filter=True,initial_prompt='文汇中学教育集团，金台书院小学，前门外国语学校。教育宣传片，教师口号，校长采访。')
 ss=[]
 for s in segments:
  ss.append({'start':s.start,'end':s.end,'text':s.text,'words':[{'start':w.start,'end':w.end,'word':w.word,'p':w.probability} for w in (s.words or [])]})
 data={'key':r['key'],'path':r['path'],'segments':ss}
 target.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
 print(r['key'],json.dumps([{'start':s['start'],'end':s['end'],'text':s['text']} for s in ss],ensure_ascii=False),flush=True)
