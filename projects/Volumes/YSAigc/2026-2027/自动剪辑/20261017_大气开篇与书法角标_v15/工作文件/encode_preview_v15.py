from pathlib import Path
import subprocess,json,sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'精修预览';ff='/Users/xuan/.local/bin/ffmpeg'
loop=OUT/'角标原生循环逐帧';opening=OUT/'开篇原生逐帧'
assert all((loop/f'{f:04d}.jpg').exists() for f in range(251))
assert all((opening/f'{f:04d}.jpg').exists() for f in range(175))
# The two exports are independent, stable native rendered frames for every 1/25 second.
loop0=np.array(Image.open(loop/'0000.jpg'),float);loop250=np.array(Image.open(loop/'0250.jpg'),float)
roi=(slice(55,180),slice(1550,1850));seam=float(np.abs(loop0-loop250)[roi].mean());assert seam<.15,seam
mid=np.array(Image.open(loop/'0125.jpg'),float);delta=float(np.abs(loop0-mid)[roi].mean());assert delta>.005,delta
outside=loop0.copy();outside[40:190,1540:1860]=0;assert outside.max()<8,'not isolated transparent bug'
# A presentation-sized crop makes the subtle line sweep easy to inspect.
commands=[
 [ff,'-hide_banner','-loglevel','error','-framerate','25','-i',str(loop/'%04d.jpg'),'-frames:v','251','-vf','crop=420:220:1490:25,scale=840:440:flags=lanczos','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(PRE/'书法角标_十秒原生循环_v15.mp4')],
 [ff,'-hide_banner','-loglevel','error','-framerate','25','-i',str(opening/'%04d.jpg'),'-i',str(ROOT.parent/'20261017_画面缓推与旁白气口精修_v14/旁白与混音/03_完整混音_气口精修_v14.wav'),'-t','7','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-af','afade=t=out:st=6.8:d=0.2','-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart',str(PRE/'大气开篇与书法角标_配画预览_v15.mp4')]
]
for cmd in commands:
 if not Path(cmd[-1]).exists():subprocess.run(cmd,check=True)
import av
probes=[]
for cmd in commands:
 path=Path(cmd[-1]);container=av.open(str(path));v=container.streams.video[0];count=sum(1 for _ in container.decode(v));probes.append({'path':str(path),'bytes':path.stat().st_size,'duration':container.duration/av.time_base,'width':v.width,'height':v.height,'fps':float(v.average_rate),'frames':count,'audio_streams':len(container.streams.audio)});container.close()
assert probes[0]['frames']==251 and probes[1]['frames']==175
report={'native_loop_seam_mad':seam,'native_animation_pixel_delta':delta,'all_25fps_frames_native_export':True,'files':probes}
(OUT/'native_motion_qa_v15.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
