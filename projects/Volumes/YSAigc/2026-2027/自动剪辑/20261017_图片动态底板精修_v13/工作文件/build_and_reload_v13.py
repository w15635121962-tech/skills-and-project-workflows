from common_v13 import *
from package_background_v13 import build
r,pm,p,mp,t=connect();assert t.GetName()==TIMELINE;before=json.loads((OUT/'live_before_v13.json').read_text());records=[]
for i,g in enumerate(GROUPS,1):
 it=next(x for x in t.GetItemListInTrack('video',1) if x.GetStart()==g['start']);c=it.GetFusionCompByIndex(1);c.Lock()
 try:row=build(c,g,t)
 finally:c.Unlock()
 assert it.ExportFusionComp(str(OUT/f"动态底板_{g['start']}.comp"),1);records.append(row)
 if i%5==0:print('V13_NATIVE_BUILD',i,flush=True)
assert snap(t)==before['snapshot'];assert graphs(t)==before['graphs'];assert pm.SaveProject()
(OUT/'package_native_build_v13.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));assert t.Export(str(ROOT/'学校_图片动态底板精修_v13.drt'),r.EXPORT_DRT);assert pm.ExportProject(PROJECT,str(ROOT/'学校_图片动态底板精修_v13.drp'))
assert pm.CloseProject(p);time.sleep(.5);p=pm.LoadProject(PROJECT);assert p and p.GetName()==PROJECT
t=p.GetCurrentTimeline();assert t.GetName()==TIMELINE and snap(t)==before['snapshot'];assert graphs(t)==before['graphs'];assert r.OpenPage('edit')
cap(p,t,6500,PRE/'重载复核_6470.jpg',1);assert pm.SaveProject();print('V13_RELOADED',flush=True)
