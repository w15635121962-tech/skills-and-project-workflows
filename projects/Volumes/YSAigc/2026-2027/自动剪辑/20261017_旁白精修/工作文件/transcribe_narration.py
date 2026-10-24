import json,subprocess,soundfile as sf
from pathlib import Path
from faster_whisper import WhisperModel
OUT=Path(__file__).parent
src=Path('/Volumes/YSAigc/2026-2027/文汇中学/配音/文汇学校配音.mp3')
wav=OUT/'narration_16k.wav'
if not wav.exists():subprocess.run(['/Users/xuan/.local/bin/ffmpeg','-v','error','-i',str(src),'-vn','-ac','1','-ar','16000','-y',str(wav)],check=True)
audio,sr=sf.read(wav,dtype='float32')
model=WhisperModel('small',device='cpu',compute_type='int8',download_root='/Users/xuan/.local/share/promo-audio/models',cpu_threads=5,local_files_only=True)
prompt='文汇中学教育集团，文汇小学，前门外国语学校，金台书院小学。汇启新章，共育未来。东城文脉厚积，育人薪火赓续。沃土计划，脱颖计划。九年一贯，守正笃行，科创领航，固本培元，文脉传承。'
segments,info=model.transcribe(audio,language='zh',beam_size=5,word_timestamps=True,vad_filter=True,initial_prompt=prompt)
rows=[]
for s in segments:
 r={'start':round(s.start,3),'end':round(s.end,3),'text':s.text,'words':[{'start':round(w.start,3),'end':round(w.end,3),'word':w.word,'p':round(w.probability,4)} for w in (s.words or [])]}
 rows.append(r)
 (OUT/'narration_raw.partial.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 print(json.dumps({k:r[k] for k in ('start','end','text')},ensure_ascii=False),flush=True)
data={'source':str(src),'duration':len(audio)/sr,'language':info.language,'model':'faster-whisper small CPU int8','word_timestamp_accuracy':'automatic; generally approximate; not phoneme-validated','segments':rows}
(OUT/'narration_raw.json').write_text(json.dumps(data,ensure_ascii=False,indent=2))
