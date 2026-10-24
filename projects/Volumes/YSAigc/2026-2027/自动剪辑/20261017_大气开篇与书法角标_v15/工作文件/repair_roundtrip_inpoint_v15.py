from common_v15 import *
r,pm,p,mp,t=connect();parent=next(p.GetTimelineByIndex(k) for k in range(1,p.GetTimelineCount()+1) if '气口精修_v14' in p.GetTimelineByIndex(k).GetName())
assert p.SetCurrentTimeline(parent);donor=next(x for x in parent.GetItemListInTrack('video',1) if x.GetStart()==340);assert donor.GetLeftOffset()==150
assert donor.ExportFusionComp(str(OUT/'保留原镜头340_缓推.comp'),1)
assert p.SetCurrentTimeline(t);old=next(x for x in t.GetItemListInTrack('video',1) if x.GetStart()==340);assert old.GetLeftOffset()==161
assert t.DeleteClips([old],False)
new=mp.AppendToTimeline([{'mediaPoolItem':donor.GetMediaPoolItem(),'startFrame':150,'endFrame':206,'recordFrame':340,'mediaType':1,'trackIndex':1}])[0]
assert new.GetStart()==340 and new.GetEnd()==396 and new.GetLeftOffset()==150
r.OpenPage('color');time.sleep(.5);assert donor.CopyGrades([new]);assert new.SetName(donor.GetName())
assert new.ImportFusionComp(str(OUT/'保留原镜头340_缓推.comp'));active_comp(new)
assert new.GetFusionCompCount()==1
assert pm.SaveProject();assert pm.CloseProject(p);p=pm.LoadProject(PROJECT);assert p;t=p.GetCurrentTimeline();assert t.GetName()==TIMELINE
new=next(x for x in t.GetItemListInTrack('video',1) if x.GetStart()==340);assert new.GetLeftOffset()==150,new.GetLeftOffset()
a=json.loads((OUT/'live_before_v15.json').read_text());b=snap(t)
assert b['audio']==a['audio']
for tr in range(4):
 for x,y in zip(a['video'][tr]['items'],b['video'][tr]['items']):
  if tr==0 and x['start']==0:continue
  assert x==y,(tr,x['start'],x,y)
assert graphs(t)[1:-1]==json.loads((OUT/'live_graphs_before_v15.json').read_text())[1:]
r.OpenPage('edit');cap(p,t,365,PRE/'原镜头340_入点恢复核验.jpg');t.SetCurrentTimecode(tc(30));assert pm.SaveProject()
print('repaired native 340 source 150..206; reopen verified all original ranges exact')
