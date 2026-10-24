from common_v21 import *
r,pm,p,mp,t=connect();assert snap(t)==json.loads((OUT/'picture_ready_snapshot_v21.json').read_text());assert graphs(t)==json.loads((OUT/'picture_ready_graphs_v21.json').read_text())
path='/Volumes/YSAigc/2026-2027/文汇中学/拍摄素材转码/007/Proxies/C0016_Proxy.mov'
old=next(i for i in t.GetItemListInTrack('video',3) if i.GetStart()==370);assert old.GetEnd()==416;assert t.DeleteClips([old],False)
m=mp.ImportMedia([path]);assert len(m)==1;it=mp.AppendToTimeline([dict(mediaPoolItem=m[0],startFrame=250,endFrame=296,mediaType=1,trackIndex=3,recordFrame=370)])[0]
assert (it.GetStart(),it.GetEnd(),it.GetLeftOffset())==(370,416,250);assert it.SetName('开篇精选｜屋檐间透光 · 校园仰拍');assert it.SetClipColor('Blue')
it.GetCurrentVersion();it.GetNodeGraph().GetNumNodes();donor=next(i for i in t.GetItemListInTrack('video',1) if i.GetStart()==942);assert donor.GetNodeGraph().GetNumNodes()==1
r.OpenPage('color');time.sleep(.4);assert donor.CopyGrades([it]);assert it.SetCDL(dict(NodeIndex='1',Slope='1.02 1.02 1.02',Offset='0 0 0',Power='.96 .96 .96',Saturation='1'))
plan=json.loads((OUT/'opening_edit_plan_v21.json').read_text());row=next(x for x in plan['shots'] if x['start']==370);row.update(path=path,source_in=250,source_out_exclusive=296,label='屋檐间透光 · 校园仰拍',slope=1.02,power=.96,existing_whole_source_use=[{'timeline':[942,1002],'source':[175,235]}],same_source_range_repeated=False)
(OUT/'opening_edit_plan_v21.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2));r.OpenPage('edit')
for f in [370,393,415]:cap(p,t,f,PRE/f'原生终版_{f:04d}.jpg',wait=.05)
(OUT/'picture_ready_snapshot_v21.json').write_text(json.dumps(snap(t),ensure_ascii=False,indent=2));(OUT/'picture_ready_graphs_v21.json').write_text(json.dumps(graphs(t),ensure_ascii=False,indent=2));assert t.SetCurrentTimecode(tc(0));assert pm.SaveProject();print('CLEAN_CAMPUS_REPLACED',flush=True)
