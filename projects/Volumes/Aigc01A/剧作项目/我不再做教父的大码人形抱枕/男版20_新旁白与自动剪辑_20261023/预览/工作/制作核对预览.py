import json, os, sys, subprocess, hashlib, wave, audioop, array, math
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
ROOT=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕/男版20_新旁白与自动剪辑_20261023')
OUT=ROOT/'预览'; WORK=OUT/'工作'; WORK.mkdir(parents=True,exist_ok=True)
SCRIPTS=Path('/Users/zc/.codex/skills/ffmpeg-skill/scripts')
ENV=dict(os.environ); ENV['PYTHONUTF8']='1'; ENV['PATH']='/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin:'+ENV.get('PATH','')
plan_path=ROOT/'final_native_plan_含SRT.json'; plan=json.loads(plan_path.read_text(encoding='utf-8')); e=plan['episodes'][0]; fps=plan['fps']; assert fps==24 and e['duration_frames']==1594 and len(e['video'])==21 and len(e['narration'])==9
paths=list(dict.fromkeys(c['path'] for c in e['video']+e['narration']))
def call(tool,args,log):
    r=subprocess.run([sys.executable,str(SCRIPTS/tool)]+[str(x) for x in args],env=ENV,capture_output=True,text=True,encoding='utf-8')
    (WORK/(log+'.stdout.json')).write_text(r.stdout,encoding='utf-8'); (WORK/(log+'.stderr.txt')).write_text(r.stderr,encoding='utf-8')
    if r.returncode: raise RuntimeError(f'{tool} {log} exit {r.returncode}: {r.stderr[-3000:]} {r.stdout[-1500:]}')
    return json.loads(r.stdout) if r.stdout.lstrip().startswith(('{','[')) else r.stdout
call('probe.py',paths+['--json'],'源文件实际探测')
def extract(item):
    i,p=item; target=WORK/f'PCM_{i:02d}.wav'; call('audio.py',[p,'-o',target,'--json'],f'PCM_{i:02d}'); return p,target
pcm=dict(ThreadPoolExecutor(max_workers=4).map(extract,enumerate(paths)))
print('decoded',len(pcm),'source audio files',flush=True)
# Decode once, resample each full source without changing timing; exact 48k samples map to 24fps (2000 samples/frame).
cache={}
for p,w in pcm.items():
    with wave.open(str(w),'rb') as f:
        raw=f.readframes(f.getnframes()); ch=f.getnchannels(); rate=f.getframerate(); width=f.getsampwidth()
    if width!=2: raw=audioop.lin2lin(raw,width,2)
    if ch==1: raw=audioop.tostereo(raw,2,1,1)
    else: assert ch==2
    if rate!=48000: raw,_=audioop.ratecv(raw,2,2,rate,48000,None)
    samples=array.array('h'); samples.frombytes(raw); cache[p]=samples
sample_frames=e['duration_frames']*2000; acc=array.array('f',[0.0])*(sample_frames*2)
checks=[]
for typ in ('video','narration'):
    last=0
    for n,c in enumerate(e[typ]):
        a=c['source_start_frame']*4000; b=c['source_end_frame']*4000; rec=c['record_frame']*4000
        assert c['speed_percent']==100 and len(cache[c['path']])>=b and b>a
        gain=10**(c['gain_db']/20)
        src=cache[c['path']]
        for j,k in enumerate(range(a,b)): acc[rec+j]+=src[k]*gain
        checks.append({'track':'A1' if typ=='video' else 'A2','path':c['path'],'source_frames':[c['source_start_frame'],c['source_end_frame']],'record_frames':[c['record_frame'],c['record_frame']+c['source_end_frame']-c['source_start_frame']],'gain_db':c['gain_db'],'speed_percent':100})
        if typ=='video': assert c['record_frame']==last; last=c['record_end_frame']
    if typ=='video': assert last==1594
peak=max(abs(x) for x in acc); assert peak<=32767, f'Unexpected clipping {peak}'
result=array.array('h',(round(x) for x in acc)); mixed=WORK/'同期声与新旁白_原速既定音量.wav'
with wave.open(str(mixed),'wb') as f: f.setnchannels(2); f.setsampwidth(2); f.setframerate(48000); f.writeframes(result.tobytes())
(OUT/'预览音频来源核对.json').write_text(json.dumps({'status':'PCM_MIX_READY','plan_path':str(plan_path),'plan_sha256':hashlib.sha256(plan_path.read_bytes()).hexdigest(),'duration_frames':1594,'fps':24,'duration_seconds':1594/24,'sample_rate':48000,'audio_sample_frames':sample_frames,'peak_dbfs':20*math.log10(peak/32768),'clipped_samples':0,'background_music':False,'clips':checks},ensure_ascii=False,indent=2),encoding='utf-8')
print('mixed exact',sample_frames,'samples/channel; peak',20*math.log10(peak/32768),flush=True)
proj={'output':str(OUT/'男版EP20_新旁白原速_核对预览.mp4'),'frame':{'width':480,'height':854,'fps':24},'clips':[{'src':c['path'],'in':c['source_start_frame']/24,'out':c['source_end_frame']/24} for c in e['video']],'transition':{'type':'none'},'captions':{'srt':e['subtitle_srt'],'font':'Arial','size':24,'position':'bottom','margin':68,'outline':2,'max_lines':2,'fit_size':'on','min_size':20},'audio':{'replace':str(mixed)},'check':{'platform':'custom','content':True}}
project=OUT/'核对预览制作.json';project.write_text(json.dumps(proj,ensure_ascii=False,indent=2),encoding='utf-8')
call('render.py',[project,'--fast','--dry-run','--json','--work',WORK/'渲染','--keep'],'预览制作_计划')
print('dry run complete; rendering',flush=True)
call('render.py',[project,'--fast','--json','--work',WORK/'渲染','--keep'],'预览制作_执行')
print('render completed',flush=True)
