from common_v16 import *
r,pm,p,mp,t=connect();before=json.loads((OUT/'live_before_v16.json').read_text());after=snap(t);oldg=json.loads((OUT/'live_graphs_before_v16.json').read_text());g=graphs(t)
assert t.GetStartFrame()==0 and t.GetEndFrame()==11507
assert after['audio']==before['audio'],'Audio changed'
assert len(after['video'])==len(before['video'])==5
assert len(after['video'][0]['items'])==187
assert after['video'][0]['items'][2:]==before['video'][0]['items'][2:],'Post opening clip differs'
for k in range(1,5):assert after['video'][k]==before['video'][k],('overlay/photo track changed',k+1)
assert g[2:]==oldg[2:],'post-opening grades changed'
assert {k:v for k,v in g[1].items() if k!='start'}=={k:v for k,v in oldg[1].items() if k!='start'},'book grade changed'
first,book=after['video'][0]['items'][:2]
assert (first['start'],first['end'],first['offset'])==(0,80,350)
assert (book['start'],book['end'],book['offset'])==(80,117,150)
items=after['video'][0]['items'];assert all(x['end']==y['start'] for x,y in zip(items,items[1:]));assert items[-1]['end']==11507
paths=sorted({x['path'] for kind in ['video','audio'] for tr in after[kind] for x in tr['items'] if x['path']});assert all(Path(x).exists() for x in paths)
parent=next(p.GetTimelineByIndex(k) for k in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(k).GetName()=='学校_大气开篇与书法动态角标_v15_20261017')
assert p.SetCurrentTimeline(parent);assert snap(parent)==before;assert graphs(parent)==oldg;assert p.SetCurrentTimeline(t)
assert t.SetCurrentTimecode(tc(40));r.OpenPage('edit');assert pm.SaveProject()
(OUT/'final_native_snapshot_v16.json').write_text(json.dumps(after,ensure_ascii=False,indent=2));(OUT/'final_graphs_v16.json').write_text(json.dumps(g,ensure_ascii=False,indent=2))
file=ROOT/'学校_恢弘校园开篇_v16.drp';assert pm.ExportProject(PROJECT,str(file))
report={'active_timeline':TIMELINE,'fps':25,'dimensions':[1920,1080],'duration_frames':11507,'duration_seconds':460.28,'first_shot':first,'book_detail':book,'audio_exact_to_v15':True,'all_after_frame_117_exact':True,'all_overlays_and_photo_tracks_exact':True,'v15_preserved':True,'all_paths_online':True,'native_book_push_reopened_verified':True,'export':{'file':str(file),'bytes':file.stat().st_size,'sha256':hashlib.sha256(file.read_bytes()).hexdigest()},'native_preview':json.loads((OUT/'native_preview_qa_v16.json').read_text())}
# Confirm the saved full project preserves local grades and native items when imported.
assert pm.CloseProject(p);name='学校_v16_完整工程核验_20261017';assert pm.ImportProject(str(file),name)
try:
 test=pm.LoadProject(name);assert test;tl=test.GetCurrentTimeline();assert tl.GetName()==TIMELINE
 assert snap(tl)==after;assert graphs(tl)==g
 r.OpenPage('edit');cap(test,tl,40,PRE/'完整工程重新导入_开场核验.jpg')
 report['full_project_import_verified']=True
finally:
 current=pm.GetCurrentProject()
 if current:assert pm.CloseProject(current)
 p=pm.LoadProject(PROJECT);assert p;t=p.GetCurrentTimeline();assert t.GetName()==TIMELINE
 assert snap(t)==after;assert graphs(t)==g;assert pm.DeleteProject(name)
 assert t.SetCurrentTimecode(tc(40));r.OpenPage('edit');assert pm.SaveProject()
(OUT/'final_delivery_qa_v16.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k not in ['first_shot','book_detail','native_preview']},ensure_ascii=False,indent=2))
