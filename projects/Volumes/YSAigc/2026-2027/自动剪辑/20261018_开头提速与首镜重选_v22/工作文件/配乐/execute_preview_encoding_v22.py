"""Execute only confirmed complete offline native capture. Never connects Resolve."""
from pathlib import Path
import json, subprocess, time, re, hashlib
import numpy as np
import av
from PIL import Image

W=Path(__file__).resolve().parent
R=W.parents[1]
PLAN=W/'开篇预览编码计划_v22.json'
p=json.loads(PLAN.read_text())
D=Path(p['source_frames']['dir'])
images=sorted(x for x in D.iterdir() if re.fullmatch(r'\d{4}\.jpg',x.name))
assert [x.name for x in images]==[f'{i:04d}.jpg' for i in range(667)]
for im in images:
 with Image.open(im) as a:assert a.size==(1920,1080)
before=[(f.name,f.stat().st_size,f.stat().st_mtime_ns) for f in images]
rows=[]
for step in p['commands']:
 argv=step['argv'][:]
 print('BEGIN',step['step'],step['name'],flush=True)
 start=time.time()
 proc=subprocess.run(argv,capture_output=True,text=True)
 Path(step['stdout_json']).write_text(proc.stdout)
 err=W/f"预览编码步骤{step['step']}_{step['name']}.stderr.txt"
 err.write_text(proc.stderr)
 row={'step':step['step'],'name':step['name'],'argv':argv,'returncode':proc.returncode,'wall_seconds':time.time()-start,'stdout_json':step['stdout_json'],'stderr':str(err)}
 rows.append(row)
 (W/'开篇预览_实际命令记录_v22.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
 print('END',step['step'],proc.returncode,flush=True)
 if proc.returncode:
  print(proc.stdout[-4000:],proc.stderr[-4000:],flush=True)
  raise AssertionError(f"Step {step['name']} exited {proc.returncode}; no parameters were changed")

final=Path(p['outputs']['final_preview'])
probe=json.loads(Path(p['commands'][-1]['stdout_json']).read_text())
count=0;wanted={30,260,587};comparisons=[]
with av.open(str(final)) as c:
 v=c.streams.video[0];audio=c.streams.audio[0]
 assert v.average_rate==25 and v.codec_context.width==1920 and v.codec_context.height==1080
 assert audio.codec_context.sample_rate==48000 and len(audio.codec_context.layout.channels)==2 and audio.codec_context.name=='aac'
 assert v.frames==667
 duration=float(v.duration*v.time_base);assert abs(duration-26.68)<.001
 for frame in c.decode(v):
  if count in wanted:
   a=frame.to_ndarray(format='rgb24').astype(np.float64)
   src=D/f'{count:04d}.jpg';b=np.array(Image.open(src).convert('RGB'),np.float64)
   diff=a-b;mad=float(abs(diff).mean());rmse=float(np.sqrt(np.mean(diff*diff)));psnr=float(20*np.log10(255/rmse))
   comparisons.append({'frame':count,'source':str(src),'decoded_RGB_MAD':mad,'decoded_RGB_RMSE':rmse,'decoded_RGB_PSNR_dB':psnr,'max_channel_error':float(np.max(abs(diff))),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
  count+=1
assert count==667 and len(comparisons)==3
assert all(c['decoded_RGB_MAD']<4 and c['decoded_RGB_PSNR_dB']>30 for c in comparisons),comparisons
after=[(f.name,f.stat().st_size,f.stat().st_mtime_ns) for f in images];assert before==after
check=json.loads(Path(p['commands'][4]['stdout_json']).read_text())
assert not any(x['status']=='FAIL' for x in check['checks'])
qa={'status':'encoded_mechanical_checks_passed_pending_visual_view','source_numeric_jpegs':667,'source_frames_unchanged':True,'video_decoded_frames':count,'fps':25,'resolution':[1920,1080],'video_duration_seconds':26.68,'container_duration_seconds':probe.get('probe',{}).get('duration'),'audio_codec':'aac','sample_rate':48000,'audio_channels':2,'preview':str(final),'preview_bytes':final.stat().st_size,'contact_sheet':p['outputs']['contact_sheet'],'actual_commands':rows,'official_checks':check['checks'],'pixel_comparisons':comparisons,'lossy_H264_picture_difference_expected':True,'no_audio_parameters_changed':True,'no_Resolve_connection':True,'visual_view_completed':False}
(W/'开篇预览_离线编码QA_v22.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2))
print(json.dumps(qa,ensure_ascii=False,indent=2),flush=True)
