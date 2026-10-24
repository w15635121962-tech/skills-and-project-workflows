from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,re,subprocess
BASE=Path(__file__).resolve().parent
ROOT=BASE.parent
FF='/Users/zc/Library/Application Support/TRAE SOLO CN/ModularData/ai-agent/vm/tools/opt/ffmpeg/8.1.2/bin/ffmpeg'
D=json.loads((ROOT/'准备/media_inventory.json').read_text(encoding='utf-8'))
def scan(row):
    src=Path(row['path']);v=row['video_streams'][0];frames=int(v['nb_frames']);fps=24;dur=frames/fps
    cp=subprocess.run([FF,'-hide_banner','-threads','2','-i',str(src),'-an','-vf',"select='gt(scene,0.25)',showinfo",'-fps_mode','vfr','-f','null','-'],capture_output=True,text=True,encoding='utf-8',timeout=90)
    if cp.returncode:raise RuntimeError(cp.stderr[-1000:])
    hits=[float(s) for s in re.findall(r'pts_time:([\d.]+)',cp.stderr)]
    cut_frames=[]
    for t in hits:
        f=round(t*fps)
        if 4<f<frames-4 and (not cut_frames or f-cut_frames[-1]>=5):cut_frames.append(f)
    bounds=[0]+cut_frames+[frames]
    shots=[]
    for i,(a,b) in enumerate(zip(bounds,bounds[1:]),1):
        t=(a+b)/2/fps
        dest=BASE/'逐切中点'/f'{src.stem}_{i:02}_{t:.3f}.jpg';dest.parent.mkdir(exist_ok=True)
        if not dest.exists():
            subprocess.run([FF,'-v','error','-ss',str(t),'-i',str(src),'-frames:v','1','-vf','scale=320:-2','-q:v','2',str(dest)],capture_output=True,check=True)
        shots.append({'shot_candidate':i,'source_in_frame':a,'source_out_frame_exclusive':b,'source_in_seconds':a/fps,'source_out_seconds':b/fps,'midpoint_seconds':t,'midpoint_image':str(dest)})
    return {'source_path':str(src),'filename':src.name,'episode_group_segment':row['episode_group_segment'],'source_fps':fps,'video_frames':frames,'video_duration_seconds':dur,'threshold':.25,'cut_frames_candidates':cut_frames,'shots':shots,'method_limit':'场景差分阈值可将快速运动/闪光误判为剪点，也可漏掉溶解；需结合接触图审查。'}
rows=[x for e in D['episodes'] for x in e['videos']]
with ThreadPoolExecutor(max_workers=4) as pool:data=list(pool.map(scan,rows))
out={'scope':'男版EP16–19仅源视频，不改源文件或Resolve','scene_threshold':.25,'source_count':len(data),'shot_candidates':sum(len(x['shots']) for x in data),'files':data}
(BASE/'源视频切点候选.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sources':len(data),'shot_candidates':out['shot_candidates'],'output':str(BASE/'源视频切点候选.json')},ensure_ascii=False))
