from common_v20 import *
OUT.mkdir(parents=True,exist_ok=True);PRE.mkdir(exist_ok=True)
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p and p.GetName()==PROJECT;mp=p.GetMediaPool();draft=p.GetCurrentTimeline();assert draft.GetName()=='学校_样片节奏与全员采访精修_v19_20261018'
basepath=ROOT.parent/'20261018_样片节奏与全员采访精修_v19/工作文件';baseline=json.loads((basepath/'live_before_v19.json').read_text());before=baseline['snapshot']
(OUT/'暂缓采访草稿_现场保存.json').write_text(json.dumps({'timeline':draft.GetName(),'snapshot':snap(draft),'graphs':graphs(draft)},ensure_ascii=False,indent=2));assert pm.SaveProject();assert pm.ExportProject(PROJECT,str(OUT/'切回开篇工作前_含采访草稿备份.drp'))
parent=next(p.GetTimelineByIndex(k) for k in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(k).GetName()==baseline['timeline']);assert p.SetCurrentTimeline(parent);assert snap(parent)==before;assert graphs(parent)==json.loads((basepath/'live_graphs_before_v19.json').read_text())
t=parent.DuplicateTimeline(TIMELINE);assert t and p.SetCurrentTimeline(t);assert snap(t)==before and t.GetEndFrame()==11507
(OUT/'live_before_v20.json').write_text(json.dumps({'project':PROJECT,'timeline':parent.GetName(),'snapshot':before,'fps':25,'duration_frames':11507},ensure_ascii=False,indent=2));(OUT/'live_graphs_before_v20.json').write_text((basepath/'live_graphs_before_v19.json').read_text())
plan=json.loads((basepath/'opening_applied_v19.json').read_text())['new_shots'];donors=[next(i for i in draft.GetItemListInTrack('video',3) if i.GetStart()==x['start']) for x in plan]
items=mp.AppendToTimeline([{'mediaPoolItem':it.GetMediaPoolItem(),'startFrame':x['in'],'endFrame':x['out'],'recordFrame':x['start'],'mediaType':1,'trackIndex':3} for it,x in zip(donors,plan)]);assert len(items)==3
for it,donor,row in zip(items,donors,plan):
 assert (it.GetStart(),it.GetEnd(),it.GetLeftOffset())==(row['start'],row['end'],row['in']);assert it.SetName(row['label']);assert it.SetClipColor('Blue');it.GetCurrentVersion();it.GetNodeGraph().GetNumNodes()
r.OpenPage('color');time.sleep(.6)
for it,donor in zip(items,donors):assert donor.CopyGrades([it])
r.OpenPage('edit')
matches=[]
for f in [30,146,260,420,587]:
 path=PRE/f'v20开篇核验_{f}.jpg';cap(p,t,f,path,wait=.05);old=basepath/'开篇_原生逐帧'/f'{f:04d}.jpg'
 a=np.array(Image.open(old).convert('RGB'),float);b=np.array(Image.open(path).convert('RGB'),float);mad=float(abs(a-b).mean());assert mad<.15,(f,mad);matches.append({'frame':f,'v19_verified_sequence_to_v20_native_MAD':mad})
after=snap(t);assert after['audio']==before['audio']
for tr in [0,1,3,4]:assert after['video'][tr]==before['video'][tr]
assert [x for x in after['video'][2]['items'] if x['start']>=614]==before['video'][2]['items']
(OUT/'opening_picture_applied_v20.json').write_text(json.dumps({'active_timeline':TIMELINE,'duration_frames':11507,'requested_sources':plan,'new_interviews_applied':False,'original_14p6_second_principal_tail_retained':True,'current_opening_pixels_match_previous_verified_native_sequence':matches,'all_original_picture_preserved':True,'all_original_audio_preserved_at_this_stage':True},ensure_ascii=False,indent=2))
assert t.SetCurrentTimecode(tc(0));assert pm.SaveProject();print('OPENING_ONLY_V20_READY',len(items),t.GetEndFrame(),flush=True)
