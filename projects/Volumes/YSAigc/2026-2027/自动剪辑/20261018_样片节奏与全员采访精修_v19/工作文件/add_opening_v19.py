from common_v19 import *
r,pm,p,mp,t=connect(False);before=json.loads((OUT/'live_before_v19.json').read_text());assert t.GetName()==before['timeline'];assert snap(t)==before['snapshot'];assert graphs(t)==json.loads((OUT/'live_graphs_before_v19.json').read_text())
assert not any(p.GetTimelineByIndex(k).GetName()==TIMELINE for k in range(1,p.GetTimelineCount()+1))
new=t.DuplicateTimeline(TIMELINE);assert new and p.SetCurrentTimeline(new);t=new
base=Path('/Volumes/YSAigc/2026-2027/文汇中学/拍摄素材转码')
plan=[
 {'path':str(base/'004/Proxies/A001C034_260921WP_Proxy.mov'),'start':117,'end':175,'in':288,'out':346,'label':'开篇新选｜广育群才 · 书院文脉','donor_start':31*25},
 {'path':str(base/'005/Proxies/20260921_D0428_Proxy.mov'),'start':234,'end':287,'in':62,'out':115,'label':'开篇新选｜校园风采 · 成长记忆','donor_start':340},
 {'path':str(base/'006/Proxies/C0156_Proxy.mov'),'start':561,'end':614,'in':140,'out':193,'label':'开篇新选｜师者风华 · 育人传承','donor_start':561}
]
media=mp.ImportMedia([x['path'] for x in plan]);assert len(media)==3;paths={x.GetClipProperty('File Path'):x for x in media}
for x in plan:
 assert not any(i['path']==x['path'] for tr in before['snapshot']['video'] for i in tr['items'])
 assert not any(it.GetStart()<x['end'] and it.GetEnd()>x['start'] for it in t.GetItemListInTrack('video',3))
 assert float(paths[x['path']].GetClipProperty('FPS'))==25
items=mp.AppendToTimeline([{'mediaPoolItem':paths[x['path']],'startFrame':x['in'],'endFrame':x['out'],'recordFrame':x['start'],'trackIndex':3,'mediaType':1} for x in plan]);assert len(items)==3
for it,x in zip(items,plan):
 assert (it.GetStart(),it.GetEnd(),it.GetLeftOffset())==(x['start'],x['end'],x['in']);assert it.SetName(x['label']);assert it.SetClipColor('Blue')
 it.GetCurrentVersion();it.GetVersionNameList(0);it.GetNodeGraph().GetNumNodes()
r.OpenPage('color');time.sleep(.6)
for it,x in zip(items,plan):
 donors=t.GetItemListInTrack('video',1)
 donor=next((d for d in donors if d.GetStart()==x['donor_start'] and d.GetNodeGraph().GetNumNodes()==1),None)
 if donor is None:donor=next(d for d in donors if d.GetStart()==561 and d.GetNodeGraph().GetNumNodes()==1)
 assert donor.CopyGrades([it])
r.OpenPage('edit')
for it,x in zip(items,plan):
 for f in [x['start'],(x['start']+x['end'])//2,x['end']-1]:cap(p,t,f,PRE/f'开篇_新素材_{f:05d}.jpg')
after=snap(t);assert after['audio']==before['snapshot']['audio']
for index in [0,1,3,4]:assert after['video'][index]==before['snapshot']['video'][index]
assert [x for x in after['video'][2]['items'] if x['start']>=614]==before['snapshot']['video'][2]['items']
(OUT/'opening_applied_v19.json').write_text(json.dumps({'timeline':TIMELINE,'track':3,'new_shots':plan,'original_picture_and_audio_preserved':True},ensure_ascii=False,indent=2))
assert t.SetCurrentTimecode(tc(117));assert pm.SaveProject();print('OPENING_ADDED',json.dumps(plan,ensure_ascii=False),flush=True)
