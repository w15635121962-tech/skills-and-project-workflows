from common_v13 import *
r,pm,p,mp,t=connect();assert t.GetName()==PARENT
last=json.loads((ROOT.parent/'20261017_曲线与二级精调_v12/工作文件/final_native_snapshot_v12.json').read_text());assert snap(t)==last
before={'project':p.GetName(),'timeline':t.GetName(),'snapshot':snap(t),'graphs':graphs(t),'page':r.GetCurrentPage(),'timecode':t.GetCurrentTimecode()}
(OUT/'live_before_v13.json').write_text(json.dumps(before,ensure_ascii=False,indent=2));assert pm.SaveProject();assert t.Export(str(ROOT/'学校_图片包装调整前_v12备份.drt'),r.EXPORT_DRT);assert pm.ExportProject(PROJECT,str(ROOT/'学校_图片包装调整前_完整工程备份.drp'))
new=t.DuplicateTimeline(TIMELINE);assert new and p.SetCurrentTimeline(new) and snap(new)==before['snapshot'];assert graphs(new)==before['graphs'];assert r.OpenPage('edit');records=[]
for i,g in enumerate(GROUPS,1):
 it=next(x for x in new.GetItemListInTrack('video',1) if x.GetStart()==g['start']);assert it.GetDuration()==g['length'] and it.GetFusionCompCount()==1;assert it.ExportFusionComp(str(ROOT/'原生包装备份'/f"{g['start']}.comp"),1)
 path=PRE/'调整前'/f"{g['start']}.jpg";cap(p,new,g['start']+g['length']//2,path);records.append({'start':g['start'],'length':g['length'],'frame':g['start']+g['length']//2,'before':str(path),'title':g['title']})
 if i%6==0:print('V13_BEFORE_PACKAGES',i,flush=True)
(OUT/'package_baselines_v13.json').write_text(json.dumps(records,ensure_ascii=False,indent=2));assert pm.SaveProject();print('V13_BASELINE_READY',len(records),flush=True)
