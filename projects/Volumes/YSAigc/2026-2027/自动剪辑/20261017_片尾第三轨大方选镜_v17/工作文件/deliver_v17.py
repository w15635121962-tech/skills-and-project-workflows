from common_v17 import *
r,pm,p,mp,t=connect();before=json.loads((OUT/'live_before_v17.json').read_text());after=snap(t);oldg=json.loads((OUT/'live_graphs_before_v17.json').read_text());g=graphs(t)
assert t.GetStartFrame()==0 and t.GetEndFrame()==11507
assert after['audio']==before['audio'],'audio modified'
assert len(after['video'])==len(before['video'])==5
assert after['video'][0]==before['video'][0],'base edits changed'
for index in range(5):
 assert {k:v for k,v in after['video'][index].items() if k!='items'}=={k:v for k,v in before['video'][index].items() if k!='items'},('track metadata changed',index+1)
original_title=next(x for x in before['video'][1]['items'] if x['start']==11407)
assert after['video'][1]['items']==[x for x in before['video'][1]['items'] if x['start']!=11407]
assert [x for x in after['video'][2]['items'] if x['start']<11150]==before['video'][2]['items'],'existing V3 user edits changed'
assert [x for x in after['video'][3]['items'] if x['start']<11150]==before['video'][3]['items'],'existing V4 user edits changed'
newtitle=next(x for x in after['video'][3]['items'] if x['start']==11407);assert newtitle==original_title,'title properties changed'
assert after['video'][4]==before['video'][4],'corner bug modified'
new=[x for x in after['video'][2]['items'] if x['start']>=11150]
assert [(x['start'],x['end'],x['offset']) for x in new]==[(11150,11242,100),(11242,11318,390),(11318,11407,450),(11407,11507,10)]
oldmap={(x['track'],x['start']):x for x in oldg};newmap={(x['track'],x['start']):x for x in g}
for key,old in oldmap.items():
 if key==(2,11407):continue
 assert newmap[key]==old,('old color graph changed',key)
assert {k:v for k,v in newmap[(4,11407)].items() if k!='track'}=={k:v for k,v in oldmap[(2,11407)].items() if k!='track'}
# The original hand-adjusted timeline is preserved exactly, including intentionally disabled photos.
parent=next(p.GetTimelineByIndex(k) for k in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(k).GetName()=='学校_恢弘校园开篇_v16_20261017')
assert p.SetCurrentTimeline(parent);assert snap(parent)==before;assert graphs(parent)==oldg;assert p.SetCurrentTimeline(t)
paths=sorted({x['path'] for kind in ['video','audio'] for tr in after[kind] for x in tr['items'] if x['path']});assert all(Path(x).exists() for x in paths)
assert t.SetCurrentTimecode(tc(11150));r.OpenPage('edit');assert pm.SaveProject()
(OUT/'final_native_snapshot_v17.json').write_text(json.dumps(after,ensure_ascii=False,indent=2));(OUT/'final_graphs_v17.json').write_text(json.dumps(g,ensure_ascii=False,indent=2))
file=ROOT/'学校_片尾第三轨大方选镜_v17.drp';assert pm.ExportProject(PROJECT,str(file))
report={'active_timeline':TIMELINE,'fps':25,'dimensions':[1920,1080],'duration_frames':11507,'duration_seconds':460.28,'requested_range_frames':[11150,11507],'new_picture_track':3,'new_picture_count':4,'new_ranges':[[x['start'],x['end']] for x in new],'all_new_sources_previously_unused':True,'original_title_preserved_on_track':4,'all_audio_exact':True,'all_existing_manual_edits_preserved':True,'original_timeline_preserved':True,'all_original_color_graphs_preserved':True,'all_paths_online':True,'native_compositions_reopened_verified':True,'export':{'file':str(file),'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()},'native_preview':json.loads((OUT/'native_preview_qa_v17.json').read_text())}
assert pm.CloseProject(p);name='学校_v17_完整工程核验_20261017';assert pm.ImportProject(str(file),name)
try:
 test=pm.LoadProject(name);assert test;tl=test.GetCurrentTimeline();assert tl.GetName()==TIMELINE
 assert snap(tl)==after;assert graphs(tl)==g
 r.OpenPage('edit');cap(test,tl,11280,PRE/'完整工程重新导入_尾段核验.jpg');report['full_project_import_verified']=True
finally:
 current=pm.GetCurrentProject()
 if current:assert pm.CloseProject(current)
 p=pm.LoadProject(PROJECT);assert p;t=p.GetCurrentTimeline();assert t.GetName()==TIMELINE
 assert snap(t)==after;assert graphs(t)==g;assert pm.DeleteProject(name)
 assert t.SetCurrentTimecode(tc(11150));r.OpenPage('edit');assert pm.SaveProject()
(OUT/'final_delivery_qa_v17.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['native_preview']},ensure_ascii=False,indent=2))
