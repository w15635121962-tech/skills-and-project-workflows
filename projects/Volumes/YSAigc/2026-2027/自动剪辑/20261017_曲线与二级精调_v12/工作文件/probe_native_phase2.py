import sys,time,json
from pathlib import Path
from PIL import Image
import numpy as np
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
R=Path(__file__).resolve().parents[1];O=R/'工作文件';r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='_v12曲线二级兼容性测试_20261017';t=p.GetCurrentTimeline();it=t.GetItemListInTrack('video',1)[0]
def cap(label):
 assert r.OpenPage('edit');assert t.SetCurrentTimecode('00:00:00:02');time.sleep(.1);assert t.SetCurrentTimecode('00:00:01:04');time.sleep(.7);dest=R/'调色预览'/f'隔离实帧_{label}.jpg';assert p.ExportCurrentFrameAsStill(str(dest));time.sleep(.3);assert p.ExportCurrentFrameAsStill(str(dest));return np.array(Image.open(dest).convert('RGB'),float)
assert it.GetNodeGraph().ApplyGradeFromDRX(str(R/'原生调色文件/identity_preserve117.drx'),0);baseline=cap('baseline');results=[]
for s in json.loads((O/'probe_specs.json').read_text()):
 print('APPLY_BEGIN',s['name'],flush=True);assert it.GetNodeGraph().ApplyGradeFromDRX(s['path'],0);print('APPLY_RETURNED',flush=True);after=cap(s['name']);g=it.GetNodeGraph();d=float(abs(baseline-after).mean());results.append({'name':s['name'],'mean_delta':d,'tools':g.GetToolsInNode(2)});print('VERIFIED',s['name'],d,flush=True);(O/'native_feature_probe_phase2_v12.json').write_text(json.dumps(results,ensure_ascii=False,indent=2));assert pm.SaveProject()
print('NATIVE_FEATURE_PROBE_COMPLETE',flush=True)
