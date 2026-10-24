import sys,time,json
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
sys.path.insert(0,'/Volumes/YSAigc/2026-2027/自动剪辑/20261017_双图包装与全片调色_v9/工作文件')
from common_v9 import snap,tc
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'调色预览';PROJECT='学校_曲线二级精修_v12';TIMELINE='学校_曲线与二级精调_v12_20261017';BASELINE='学校_本轮开始前完整保留_v11_20261017'
def connect():
 r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p and p.GetName()==PROJECT,p.GetName() if p else None
 return r,pm,p,p.GetMediaPool(),p.GetCurrentTimeline()
def stable_cap(p,t,f,path):
 path=Path(path);path.parent.mkdir(exist_ok=True,parents=True);check=path.with_name(path.stem+'_check.jpg')
 if f>t.GetStartFrame():assert t.SetCurrentTimecode(tc(f-1));time.sleep(.05)
 assert t.SetCurrentTimecode(tc(f));time.sleep(.6);assert p.ExportCurrentFrameAsStill(str(path));prev=np.asarray(Image.open(path).convert('RGB'),dtype=float)
 for attempt in range(4):
  time.sleep(.28);assert p.ExportCurrentFrameAsStill(str(check));now=np.asarray(Image.open(check).convert('RGB'),dtype=float);d=float(np.abs(prev-now).mean())
  if d<.1:
   if attempt:path.write_bytes(check.read_bytes())
   return Image.open(path).convert('RGB')
  prev=now;path.write_bytes(check.read_bytes())
 raise AssertionError(('Unstable native frame',f,d))
def stats(im):
 a=np.asarray(im,dtype=float)/255;y=.2126*a[:,:,0]+.7152*a[:,:,1]+.0722*a[:,:,2]
 return {'quantiles':np.quantile(y,[.01,.1,.5,.9,.95,.99]).tolist(),'black008':float(np.mean(np.all(a<.008,axis=2))),'white98':float(np.mean(np.all(a>.98,axis=2))),'channel995':float(np.mean(a.max(2)>.995))}
