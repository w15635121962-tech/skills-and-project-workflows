from pathlib import Path
import sys,json,subprocess
import soundfile as sf
import av
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'精修预览';SK=Path('/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts');ENC=OUT/'预览编码';ENC.mkdir(exist_ok=True)
full=ROOT/'旁白与配乐/03_完整混音_样片节奏与全员采访_v19.wav'
def call(script,args,tag):
 p=subprocess.run([sys.executable,str(SK/script),*map(str,args)],capture_output=True,text=True)
 (ENC/(tag+'.log')).write_text(p.stdout+'\n'+p.stderr)
 if p.returncode:raise RuntimeError((tag,p.returncode,p.stdout[-1600:],p.stderr[-1600:]))
 return p.stdout
ranges=[{'name':'开篇','start':0,'end':667,'title':'开篇_三素材与强配乐_预览_v19'}, {'name':'全员采访与尾声','start':10992,'end':12520,'title':'五人采访混剪与片尾_预览_v19'}]
if len(sys.argv)>1:ranges=[x for x in ranges if x['name']==sys.argv[1]]
reports=[]
for row in ranges:
 folder=OUT/(row['name']+'_原生逐帧');n=row['end']-row['start'];assert all((folder/f'{i:04d}.jpg').exists() for i in range(n))
 silent=ENC/(row['name']+'_无声.mp4');audio=ENC/(row['name']+'_实际混音.wav');dest=PRE/(row['title']+'.mp4')
 with sf.SoundFile(full) as f:
  assert f.samplerate==48000 and f.channels==2;f.seek(row['start']*1920);a=f.read(n*1920,dtype='int32',always_2d=True);assert len(a)==n*1920
 sf.write(audio,a,48000,subtype='PCM_24')
 args=['--dir',folder,'--pattern','%04d.jpg','--fps','25','--quality','18','--preset','fast','-o',silent]
 if not silent.exists():
  call('sequence.py',args+['--dry-run','--json'],row['name']+'_sequence_plan');call('sequence.py',args+['--json'],row['name']+'_sequence_result')
 if not dest.exists():call('audio.py',[silent,'--replace',audio,'--bitrate','256k','-o',dest,'--json'],row['name']+'_mux_result')
 c=av.open(str(dest));v=c.streams.video[0];count=sum(1 for _ in c.decode(v));assert count==n and v.width==1920 and v.height==1080 and float(v.average_rate)==25 and len(c.streams.audio)==1
 report={'path':str(dest),'bytes':dest.stat().st_size,'duration':c.duration/av.time_base,'fps':25,'width':v.width,'height':v.height,'frames':count,'requested_frames':n,'source_native_range':[row['start'],row['end']],'audio_source':'fresh_native_source_clock_reconstruction','audio_channels':c.streams.audio[0].layout.nb_channels,'sample_rate':c.streams.audio[0].rate};assert abs(report['duration']-n/25)<.05;c.close()
 call('look.py',[dest,'--tiles','4x3','-o',PRE/(row['name']+'_动态预览检查.png')],row['name']+'_look')
 check=call('check.py',[dest,'--platform','custom','--aspect','16:9','--max-duration',str(n/25+.05),'--no-loudness','--content','--json'],row['name']+'_check');report['check_output']=check
 reports.append(report);print(json.dumps(report,ensure_ascii=False),flush=True)
(OUT/('preview_encoding_qa_v19_'+(sys.argv[1] if len(sys.argv)>1 else '全部')+'.json')).write_text(json.dumps(reports,ensure_ascii=False,indent=2))
