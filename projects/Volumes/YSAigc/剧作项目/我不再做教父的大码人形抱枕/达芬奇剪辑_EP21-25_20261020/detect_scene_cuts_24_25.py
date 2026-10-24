from pathlib import Path
import subprocess,json,re
from concurrent.futures import ThreadPoolExecutor
base=Path('达芬奇剪辑_EP21-25_20261020');a=json.loads((base/'素材盘点.json').read_text());ff=a['ffmpeg_path'];rows=[r for r in a['files'] if r['kind']=='video' and r['episode'] in (24,25)]
def one(r):
 p=Path(r['path']);cmd=[ff,'-hide_banner','-loglevel','info','-nostdin','-i',str(p),'-an','-vf',"select='gt(scene,0.25)',showinfo",'-fps_mode','vfr','-f','null','-']
 q=subprocess.run(cmd,capture_output=True,text=True,timeout=60)
 ts=[float(v) for v in re.findall(r'pts_time:([0-9.]+)',q.stderr)]
 return {'source':str(p),'scene_cut_times_seconds_threshold_025':ts,'returncode':q.returncode,'note':'Image-change detector only; not a confirmed edit cut or audio boundary.'}
with ThreadPoolExecutor(max_workers=4) as ex:d=list(ex.map(one,rows))
(base/'画面核验/场景切换定位_EP24-25.json').write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
for r in d:
 if Path(r['source']).stem in ['女版25-2-2','女版25-4-1','女版25-4-2','女版25-5-1','女版25-6-1','女版24-4-1','女版24-8-1']:print(Path(r['source']).name,r['scene_cut_times_seconds_threshold_025'])
