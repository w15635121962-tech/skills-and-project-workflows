"""Reproduce EP12VO05 waveform evidence for the frozen actual116-frame cut.
Read-only inputs. This technical plot does not alter AV, SRT, progress or Resolve.
"""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np
from PIL import Image,ImageDraw
R=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕/男版09-15_旁白_20261021');O=Path(__file__).resolve().parent
source=R/'音频/第12集/大码男版枕头12-05-01.mp3'
protected=[R/'剩余两集已完成_20261022/final_native_plan.json',R/'剩余两集已完成_20261022/字幕/EP12.srt',R/'剩余两集已完成_20261022/字幕/EP15.srt',R/'剪辑脚本准备/剩余两集_20261022/EP12/EP12_真实帧剪辑计划.json',R/'剪辑脚本准备/剩余两集_20261022/EP12/EP12_原文词事件.json',source,R/'制作进度.json',R/'五集已完成_20261022/final_native_plan.json']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before={str(p):sha(p) for p in protected}
plan=json.loads(protected[0].read_text());ep=next(e for e in plan['episodes'] if e['episode']==12)
clips=sorted((c for c in ep['narration'] if c['path']==str(source)),key=lambda c:c['source_start_frame'])
actual=clips[0]['source_end_frame'];assert actual==116 and clips[1]['source_start_frame']==actual
ff='/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg'
y=np.frombuffer(subprocess.run([ff,'-v','error','-i',str(source),'-f','f32le','-ac','1','-ar','48000','-'],capture_output=True,check=True).stdout,dtype=np.float32)
a,z=3.4,5.4;sr=48000;W,H=1600,900;im=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(im);x0,x1,y0,y1=80,1540,80,320
for sec in np.arange(a,z+.0001,.1):
 x=x0+(sec-a)/(z-a)*(x1-x0);d.line((x,y0,x,y1),fill='#dddddd');d.text((x-15,y1+8),f'{sec:.1f}',fill='black')
for col in range(x0,x1):
 s=int((a+(col-x0)/(x1-x0)*(z-a))*sr);e=int((a+(col+1-x0)/(x1-x0)*(z-a))*sr);m=np.max(np.abs(y[s:e]));d.line((col,(y0+y1)/2-m*100,col,(y0+y1)/2+m*100),fill='#145c99')
win=1024;hop=128;seg=y[int(a*sr):int(z*sr)];frames=np.lib.stride_tricks.sliding_window_view(seg,win)[::hop]*np.hanning(win)
spec=20*np.log10(np.abs(np.fft.rfft(frames,axis=1))+1e-8);spec=spec[:,:172].T
v=((np.clip(spec,-65,0)+65)/65*255).astype('uint8');pic=Image.fromarray(np.flipud(v),'L').convert('RGB').resize((x1-x0,450));im.paste(pic,(x0,380));d=ImageDraw.Draw(im)
lines=[(4.26,'primary ASR boundary4.26s (reference only)','#df8000'),(actual/24,'ACTUAL116f=4.833333s (frozen plan cut)','#008840')]
for sec,label,col in lines:
 x=x0+(sec-a)/(z-a)*(x1-x0);d.line((x,y0,x,840),fill=col,width=3);d.text((x+6,40),label,fill=col)
d.text((80,10),'12-05 actual source waveform/spectrum: earnestly -> The butler. Final cut derived from frozen plan.',fill='black')
d.text((80,855),'Independent small.en: earnestly ends4.52s; The starts5.12s. Actual cut116f lies inside the retained real pause.',fill='black')
d.text((80,875),'No speed change or source modification. Normal-speed human audition is not claimed. No106f candidate line is shown.',fill='black')
output=O/'12-05_earnestly_The_实际波形频谱.png';im.save(output)
after={str(p):sha(p) for p in protected};assert before==after
print(json.dumps({'plot_path':str(output),'plot_sha256':sha(output),'actual_cut_frame':actual,'actual_cut_seconds':actual/24,'obsolete106f_line_removed':True,'protected_file_hashes_unchanged':True,'protected_files':after},ensure_ascii=False,indent=2))
