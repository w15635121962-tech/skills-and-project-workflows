from common_v16 import *
import subprocess,av
frames=OUT/'开篇原生逐帧';assert all((frames/f'{f:04d}.jpg').exists() for f in range(175))
path=PRE/'全校方阵_恢弘开场预览_v16.mp4';ff='/Users/xuan/.local/bin/ffmpeg'
cmd=[ff,'-hide_banner','-loglevel','error','-framerate','25','-i',str(frames/'%04d.jpg'),'-i',str(ROOT.parent/'20261017_画面缓推与旁白气口精修_v14/旁白与混音/03_完整混音_气口精修_v14.wav'),'-t','7','-vf','scale=out_color_matrix=bt709:out_range=tv','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-color_range','tv','-af','afade=t=out:st=6.8:d=0.2','-c:a','aac','-b:a','256k','-ar','48000','-movflags','+faststart',str(path)]
if not path.exists():subprocess.run(cmd,check=True)
c=av.open(str(path));v=c.streams.video[0];count=sum(1 for _ in c.decode(v));report={'file':str(path),'bytes':path.stat().st_size,'duration':c.duration/av.time_base,'fps':float(v.average_rate),'size':[v.width,v.height],'frames':count,'audio_channels':c.streams.audio[0].channels,'all_frames_fresh_native_v16':True};c.close();assert count==175 and report['duration']==7
# Fresh native continuous-frame differences catch a held or cached still in the new opener.
ims=[np.asarray(Image.open(frames/f'{f:04d}.jpg'),dtype=np.float32) for f in range(80)];diffs=[float(abs(b-a).mean()) for a,b in zip(ims,ims[1:])];assert min(diffs)>.03,min(diffs)
report['first_shot_79_adjacent_frame_mad']={'minimum':min(diffs),'maximum':max(diffs),'mean':sum(diffs)/len(diffs)}
(OUT/'native_preview_qa_v16.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
