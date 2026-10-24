import sys,time,json,math,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
sys.path.insert(0,'/Volumes/YSAigc/2026-2027/自动剪辑/20261017_双图包装与全片调色_v9/工作文件')
from common_v9 import snap,tc
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'包装预览';PROJECT='学校_曲线二级精修_v12';TIMELINE='学校_图片动态底板精修_v13_20261017';PARENT='学校_曲线与二级精调_v12_20261017'
GROUPS=json.loads((ROOT.parent/'20261017_双图包装与全片调色_v9/工作文件/native_packages_v9.json').read_text())['groups']
def connect():
 r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p and p.GetName()==PROJECT,p.GetName() if p else None
 return r,pm,p,p.GetMediaPool(),p.GetCurrentTimeline()
def cap(p,t,f,path,wait=.55):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);check=path.with_name(path.stem+'_check.jpg');assert t.SetCurrentTimecode(tc(f));time.sleep(wait);assert p.ExportCurrentFrameAsStill(str(path));a=np.array(Image.open(path).convert('RGB'),float)
 for attempt in range(4):
  time.sleep(.22);assert p.ExportCurrentFrameAsStill(str(check));b=np.array(Image.open(check).convert('RGB'),float)
  if abs(a-b).mean()<.1:
   if attempt:path.write_bytes(check.read_bytes())
   return Image.open(path).convert('RGB')
  a=b;path.write_bytes(check.read_bytes())
 raise AssertionError(('Frame did not settle',f,float(abs(a-b).mean())))
def graphs(t):
 rows=[]
 for tr in range(1,t.GetTrackCount('video')+1):
  for it in t.GetItemListInTrack('video',tr):
   g=it.GetNodeGraph();rows.append({'track':tr,'start':it.GetStart(),'version':it.GetCurrentVersion(),'nodes':g.GetNumNodes(),'luts':[g.GetLUT(i) for i in range(1,g.GetNumNodes()+1)],'tools':[g.GetToolsInNode(i) for i in range(1,g.GetNumNodes()+1)]})
 return rows
