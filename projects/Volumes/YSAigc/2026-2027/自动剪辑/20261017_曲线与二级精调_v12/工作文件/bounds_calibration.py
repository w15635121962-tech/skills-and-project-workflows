import sys,time,json
from pathlib import Path
from PIL import Image
import numpy as np
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
R=Path(__file__).resolve().parents[1];O=R/'工作文件';r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert pm.SaveProject();p=pm.LoadProject('_v12原生曲线结构验证_20261017');assert p;t=p.GetCurrentTimeline();it=t.GetItemListInTrack('video',1)[0]
def cap(label):
 assert r.OpenPage('edit');assert t.SetCurrentTimecode('00:00:00:02');time.sleep(.08);assert t.SetCurrentTimecode('00:00:01:04');time.sleep(.6);dest=R/'调色预览'/f'色相校准_{label}.jpg';assert p.ExportCurrentFrameAsStill(str(dest));time.sleep(.25);assert p.ExportCurrentFrameAsStill(str(dest));return np.array(Image.open(dest).convert('RGB'),float)
assert it.GetNodeGraph().ApplyGradeFromDRX(str(R/'原生调色文件/identity_preserve117.drx'),0);baseline=cap('baseline');out=[]
for s in json.loads((O/'bounds_specs.json').read_text()):
 assert it.GetNodeGraph().ApplyGradeFromDRX(s['path'],0);after=cap(str(s['center']));d=abs(after-baseline);skin=float(d[280:430,700:830].mean());navy=float(d[650:850,1250:1400].mean());row={'center':s['center'],'all_delta':float(d.mean()),'skin_delta':skin,'navy_delta':navy,'affected_area':float((d.max(2)>2).mean())};out.append(row);print(row,flush=True);(O/'native_qualifier_bounds_calibration.json').write_text(json.dumps(out,ensure_ascii=False,indent=2))
assert pm.SaveProject()
