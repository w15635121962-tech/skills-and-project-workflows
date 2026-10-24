import json
import numpy as np
from PIL import Image
from common_v12 import *
r,pm,p,mp,t=connect();assert t.GetName()==TIMELINE;assert r.OpenPage('edit');assert t.SetCurrentTimecode(tc(146));assert pm.SaveProject();assert pm.CloseProject(p);print('CLOSED_SAVED_PROJECT',flush=True)
p=pm.LoadProject(PROJECT);assert p;print('REOPENED_PROJECT',p.GetName(),flush=True);mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert t.GetName()==TIMELINE;assert snap(t)==json.loads((OUT/'live_before_v12.json').read_text())['snapshot'];qa=json.loads((OUT/'native_color_qa_v12.json').read_text());assert qa['count']==20 and qa['flags']==[];checks=[]
for s in qa['records']:
 it=next(x for x in t.GetItemListInTrack('video',s['track']) if x.GetStart()==s['start']);g=it.GetNodeGraph();assert it.GetCurrentVersion()==s['active_version'];assert g.GetNumNodes()==len(s['nodes']);assert [g.GetToolsInNode(i) for i in range(1,g.GetNumNodes()+1)]==s['actual_tools'];assert (g.GetLUT(1) or '')==s['lut'];checks.append({'track':s['track'],'start':s['start'],'version':it.GetCurrentVersion(),'nodes':g.GetNumNodes()})
assert r.OpenPage('edit');test=stable_cap(p,t,146,PRE/'工程重新打开_迎宾核对.jpg');ref=next(x for x in qa['records'] if x['track']==1 and x['start']==117)['frames'][1]['after'];delta=float(abs(np.array(test,float)-np.array(Image.open(ref).convert('RGB'),float)).mean());assert delta<.1,delta
(OUT/'native_reopen_qa_v12.json').write_text(json.dumps({'project':p.GetName(),'timeline':t.GetName(),'reopened_successfully':True,'all20_grade_versions_nodes_luts_tools_persisted':True,'native_frame_delta':delta,'clip_checks':checks,'snapshot_unchanged':True},ensure_ascii=False,indent=2));assert pm.SaveProject();print('REOPEN_PROOF_PASSED',len(checks),'FRAME_DELTA',delta,flush=True)
