from pathlib import Path
import json, numpy as np,soundfile as sf
from scipy.signal import resample_poly
from faster_whisper import WhisperModel
BASE=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_旁白精修/工作文件')
OUT=Path(__file__).parent
plan=json.loads((BASE/'audio_plan_v2.json').read_text())
model=WhisperModel('small',device='cpu',compute_type='int8',download_root='/Users/xuan/.local/share/promo-audio/models',cpu_threads=4,local_files_only=True)
outputs=[]
for index,item in enumerate(plan['speech'],1):
 path=Path(item['path']);audio,sr=sf.read(path,dtype='float32')
 if audio.ndim>1:audio=audio.mean(axis=1)
 usable=item['duration_frames']/25
 audio=audio[:round(usable*sr)]
 if sr!=16000:
  import math
  g=math.gcd(sr,16000);audio=resample_poly(audio,16000//g,sr//g).astype('float32')
 # Explicitly no initial_prompt and no reference text; use processed audio as heard in project.
 ss,info=model.transcribe(audio,language='zh',beam_size=5,word_timestamps=True,vad_filter=True,condition_on_previous_text=True)
 rows=[]
 for s in ss:
  row={'start':round(s.start,3),'end':round(s.end,3),'text':s.text,'avg_logprob':round(s.avg_logprob,4),'no_speech_prob':round(s.no_speech_prob,4),'words':[{'start':round(w.start,3),'end':round(w.end,3),'word':w.word,'p':round(w.probability,4)} for w in (s.words or [])]}
  rows.append(row)
  (OUT/f'voice_{index:02}_independent.partial.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
  print(index,json.dumps({k:row[k] for k in ('start','end','text')},ensure_ascii=False),flush=True)
 result={'source':str(path),'original_source':item['source'],'timeline_start':item['record_frame']/25,'timeline_duration':usable,'actual_analyzed_duration':len(audio)/16000,'model':'Systran faster-whisper small int8','method':'independent_no_initial_prompt_no_reference','reference_words_supplied':False,'segments':rows}
 (OUT/f'voice_{index:02}_independent.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
 outputs.append(result)
(OUT/'independent_asr_all.json').write_text(json.dumps(outputs,ensure_ascii=False,indent=2))
