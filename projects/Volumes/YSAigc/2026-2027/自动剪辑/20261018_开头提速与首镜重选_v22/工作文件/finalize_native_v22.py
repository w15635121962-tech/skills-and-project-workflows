from common_v22 import *
r,pm,p,mp,t=connect();base=json.loads((OUT/'live_before_v22.json').read_text());before=base['snapshot'];oldg=json.loads((OUT/'live_graphs_before_v22.json').read_text());after=snap(t);g=graphs(t);plan=json.loads((OUT/'opening_edit_plan_v22.json').read_text())
assert t.GetEndFrame()==11507 and float(t.GetSetting('timelineFrameRate'))==25
assert [len(x['items']) for x in after['video']]==[171,25,44,24,1]
assert after['audio']==before['audio']
for tr in [0,1,4]:assert after['video'][tr]==before['video'][tr]
assert [x for x in after['video'][2]['items'] if x['start']>=667]==[x for x in before['video'][2]['items'] if x['start']>=667]
assert after['video'][3]['items']==[x for x in before['video'][3]['items'] if x['start']!=207]
gm={(x['track'],x['start']):x for x in g}
for x in oldg:
 if (x['track']==3 and x['start']<667) or (x['track']==4 and x['start']==207):continue
 assert gm[(x['track'],x['start'])]==x
items=[i for i in t.GetItemListInTrack('video',3) if i.GetStart()<667];assert len(items)==18 and items[0].GetStart()==0 and items[-1].GetEnd()==667;assert all(a.GetEnd()==b.GetStart() for a,b in zip(items,items[1:]))
for x,i in zip(plan['shots'],items):assert (i.GetStart(),i.GetEnd(),i.GetLeftOffset(),i.GetMediaPoolItem().GetClipProperty('File Path'))==(x['start'],x['end'],x['source_in'],x['path']);assert Path(x['path']).is_file()
assert items[0].GetMediaPoolItem().GetClipProperty('File Path')!=before['video'][2]['items'][0]['path']
parent=next(p.GetTimelineByIndex(k) for k in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(k).GetName()==base['timeline']);assert p.SetCurrentTimeline(parent);assert snap(parent)==before and graphs(parent)==oldg;assert p.SetCurrentTimeline(t)
assert t.SetCurrentTimecode(tc(0));r.OpenPage('edit');assert pm.SaveProject();(OUT/'final_native_snapshot_v22.json').write_text(json.dumps(after,ensure_ascii=False,indent=2));(OUT/'final_graphs_v22.json').write_text(json.dumps(g,ensure_ascii=False,indent=2))
file=ROOT/'学校_开头提速与首镜重选_v22.drp';assert not file.exists();print('EXPORT_STARTED',flush=True);assert pm.ExportProject(PROJECT,str(file));print('EXPORT_COMPLETE',file.stat().st_size,flush=True)
report={'active_timeline':TIMELINE,'duration_frames':11507,'duration_seconds':460.28,'fps':25,'resolution':[1920,1080],'opening_range':[0,667],'opening_shots':18,'prior_shots':13,'mean_shot_seconds':667/25/18,'mean_shot_reduction_percent':(1-13/18)*100,'first_shot_replaced':True,'fresh_manual_source_and_relative_order_preserved':True,'all_audio_exact_to_fresh_parent':True,'title_and_corner_unchanged':True,'outside_opening_picture_and_grades_unchanged':True,'parent_timeline_preserved':True,'export':str(file),'export_bytes':file.stat().st_size,'export_sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
assert pm.CloseProject(p);scratch='学校_v22_提速工程核验_20261018';assert pm.ImportProject(str(file),scratch)
try:
 test=pm.LoadProject(scratch);assert test;tl=test.GetCurrentTimeline();assert tl.GetName()==TIMELINE and snap(tl)==after and graphs(tl)==g;r.OpenPage('edit');checks=[]
 for f in [20,272,306,457,493,640]:
  path=PRE/f'工程重导核验_{f:04d}.jpg';cap(test,tl,f,path,wait=.05);a=np.array(Image.open(path).convert('RGB'),float);b=np.array(Image.open(OUT/f'开篇_原生逐帧/{f:04d}.jpg').convert('RGB'),float);mad=float(abs(a-b).mean());assert mad<.2,(f,mad);checks.append({'frame':f,'native_to_reimport_MAD':mad})
 report.update(full_project_isolated_import_verified=True,native_frame_reimport_checks=checks)
finally:
 cur=pm.GetCurrentProject()
 if cur:assert pm.CloseProject(cur)
 p=pm.LoadProject(PROJECT);assert p;t=p.GetCurrentTimeline();assert t.GetName()==TIMELINE and snap(t)==after and graphs(t)==g;assert pm.DeleteProject(scratch);assert t.SetCurrentTimecode(tc(0));r.OpenPage('edit');assert pm.SaveProject()
(OUT/'native_delivery_qa_v22.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
