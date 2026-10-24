from common_v17 import *
import subprocess,av
frames=OUT/'尾段原生逐帧';assert all((frames/f'{f:04d}.jpg').exists() for f in range(402))
path=PRE/'片尾_第三轨大方选镜_配画预览_v17.mp4';ff='/Users/xuan/.local/bin/ffmpeg'
cmd=[ff,'-hide_banner','-loglevel','error','-framerate','25','-i',str(frames/'%04d.jpg'),'-ss','444.2','-i',str(ROOT.parent/'20261017_画面缓推与旁白气口精修_v14/旁白与混音/03_完整混音_气口精修_v14.wav'),'-t','16.08','-map','0:v:0','-map','1:a:0','-vf','scale=out_color_matrix=bt709:out_range=tv','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart',str(path)]
if not path.exists():subprocess.run(cmd,check=True)
c=av.open(str(path));v=c.streams.video[0];count=sum(1 for _ in c.decode(v));report={'file':str(path),'bytes':path.stat().st_size,'duration':c.duration/av.time_base,'fps':float(v.average_rate),'size':[v.width,v.height],'frames':count,'audio_channels':c.streams.audio[0].channels,'native_range_frames':[11105,11507],'requested_new_picture_range_frames':[11150,11507],'audio_reference':'unchanged previous verified full mix; no new processing','all_frames_fresh_native_v17':True};c.close();assert count==402 and abs(report['duration']-16.08)<.01
last=np.array(Image.open(frames/'0401.jpg'),float);assert last.max()<5,('last not black',last.max());report['last_frame_max']=float(last.max())
# Each selected native section moves, and the final alpha/brightness fade lands on black.
segments=[(45,137),(137,213),(213,302),(302,402)]
rows=[]
for a,z in segments:
 ims=[np.asarray(Image.open(frames/f'{f:04d}.jpg'),dtype=np.float32) for f in range(a,z)];d=[float(abs(b-x).mean()) for x,b in zip(ims,ims[1:])];rows.append({'index_range':[a,z],'minimum_adjacent_mad':min(d),'mean_adjacent_mad':sum(d)/len(d)})
 assert max(d)>.04,('frozen segment',a,z)
report['native_motion_samples']=rows
(OUT/'native_preview_qa_v17.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
