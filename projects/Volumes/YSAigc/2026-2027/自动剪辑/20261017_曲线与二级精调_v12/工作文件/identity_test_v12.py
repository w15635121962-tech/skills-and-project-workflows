import sys,time,json
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0,'/Volumes/YSAigc/2026-2027/自动剪辑/20261017_双图包装与全片调色_v9/工作文件')
from common_v9 import connect,snap,tc
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件'
r,pm,p,mp,t=connect();assert t.GetName()=='学校_曲线与二级精调_v12_20261017'
assert r.OpenPage('edit')
def cap(f,name):
 out=ROOT/'调色预览'/name;check=out.with_name(out.stem+'_check.jpg');assert t.SetCurrentTimecode(tc(f));time.sleep(.65);assert p.ExportCurrentFrameAsStill(str(out));time.sleep(.35);assert p.ExportCurrentFrameAsStill(str(check));a=np.array(Image.open(out).convert('RGB'),float);b=np.array(Image.open(check).convert('RGB'),float);assert abs(a-b).mean()<.1;return a
before=cap(146,'identity_before.jpg');it=next(x for x in t.GetItemListInTrack('video',1) if x.GetStart()==117);v=it.GetCurrentVersion();assert ('v12_原生节点往返验证' in it.GetVersionNameList(0) or it.AddVersion('v12_原生节点往返验证',0)) and it.LoadVersionByName('v12_原生节点往返验证',0)
try:
 g=it.GetNodeGraph();assert g.ApplyGradeFromDRX(str(ROOT/'原生调色文件/identity_preserve117.drx'),0);g=it.GetNodeGraph();assert g.GetNumNodes()==2
 after=cap(146,'identity_after.jpg');delta=float(abs(before-after).mean());maximum=float(abs(before-after).max());print('IDENTITY',delta,maximum,flush=True)
 out={'mean_pixel_delta':delta,'max_pixel_delta':maximum,'nodes':g.GetNumNodes(),'node1_lut':g.GetLUT(1),'tools':[g.GetToolsInNode(i) for i in [1,2]],'original_version':v,'passed':delta<.15 and maximum<5}
 (OUT/'native_identity_roundtrip_v12.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));assert out['passed'],out
finally:
 assert it.LoadVersionByName(v['versionName'],v['versionType']);assert pm.SaveProject()
