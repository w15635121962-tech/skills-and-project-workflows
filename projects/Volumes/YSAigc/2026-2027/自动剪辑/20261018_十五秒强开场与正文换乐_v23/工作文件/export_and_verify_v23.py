from common_v23 import *
r,pm,p,mp,t=connect();after=json.loads((OUT/'final_native_snapshot_v23.json').read_text());g=json.loads((OUT/'final_graphs_v23.json').read_text());assert snap(t)==after and graphs(t)==g
file=ROOT/'学校_十五秒强开场与正文换乐_v23.drp';assert not file.exists();assert pm.SaveProject();print('EXPORT_STARTED',flush=True);assert pm.ExportProject(PROJECT,str(file));print('EXPORT_COMPLETE',file.stat().st_size,flush=True)
report=json.loads((OUT/'native_apply_qa_v23.json').read_text());report.update(export=str(file),export_bytes=file.stat().st_size,export_sha256=hashlib.sha256(file.read_bytes()).hexdigest())
assert pm.CloseProject(p);scratch='学校_v23_十五秒换乐工程核验_20261018';assert pm.ImportProject(str(file),scratch)
try:
 test=pm.LoadProject(scratch);assert test;tl=test.GetCurrentTimeline();assert tl.GetName()==TIMELINE and snap(tl)==after and graphs(tl)==g
 tracks=tl.GetItemListInTrack('audio',3);assert [(i.GetStart(True),i.GetEnd(True),i.GetLeftOffset(True)) for i in tracks[:2]]==[(0.0,375.0,0.0),(375.0,2861.0,0.0)]
 report['full_project_isolated_import_verified']=True
finally:
 cur=pm.GetCurrentProject()
 if cur:assert pm.CloseProject(cur)
 p=pm.LoadProject(PROJECT);assert p;t=p.GetCurrentTimeline();assert t.GetName()==TIMELINE and snap(t)==after and graphs(t)==g;assert pm.DeleteProject(scratch);assert t.SetCurrentTimecode(tc(0));r.OpenPage('edit');assert pm.SaveProject()
(OUT/'native_delivery_qa_v23.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
