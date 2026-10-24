from common_v15 import *
r,pm,p,mp,t=connect();before=json.loads((OUT/'live_before_v15.json').read_text());after=snap(t);g=graphs(t);oldg=json.loads((OUT/'live_graphs_before_v15.json').read_text())
assert t.GetEndFrame()==11507 and t.GetStartFrame()==0
assert after['audio']==before['audio'],'audio altered'
assert len(after['video'])==5
for n in range(4):
 x=before['video'][n];y=after['video'][n]
 assert {k:v for k,v in x.items() if k!='items'}=={k:v for k,v in y.items() if k!='items'}
 assert len(x['items'])==len(y['items'])
 for a,b in zip(x['items'],y['items']):
  if n==0 and a['start']==0:continue
  assert a==b,(n,a['start'],a,b)
assert g[1:-1]==oldg[1:],'original color graphs altered'
new=after['video'][0]['items'][0];assert new['start']==0 and new['end']==60 and new['offset']==200
assert new['path'].endswith('A001C240_260921JW_Proxy.mov')
newranges=[x for track in before['video'] for x in track['items'] if x['path']==new['path']];assert not newranges
corner=t.GetItemListInTrack('video',5)[0];assert corner.GetStart()==0 and corner.GetEnd()==11507 and corner.GetFusionCompCount()==1
c=active_comp(corner);font=c.FindTool('V15_书法校名');assert font.GetInput('Font')=='Ma Shan Zheng'
assert font.GetInput('StyledText')=='文汇中学';assert c.FindTool('V15_集团副标').GetInput('StyledText')=='教育集团'
loop=c.FindTool('V15_十秒循环流光');positions=[]
for f in [0,1,62,125,188,249,250,500,11000]:
 positions.append({'frame':f,'position':c.FindTool('V15_流光羽化').GetInput('Center',f),'opacity':loop.GetInput('Blend',f)})
assert abs(loop.GetInput('Blend',0)-loop.GetInput('Blend',250))<1e-6
assert c.FindTool('V15_片尾同步淡出').GetInput('Blend',11506)==0
# The parent v14 timeline remains a recoverable unmodified version.
parent=next(p.GetTimelineByIndex(k) for k in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(k).GetName()=='学校_画面缓推与旁白气口精修_v14_20261017')
assert p.SetCurrentTimeline(parent);assert snap(parent)==before;assert graphs(parent)==oldg;assert p.SetCurrentTimeline(t)
# Remove only the disposable prototype created in this turn.
protos=[p.GetTimelineByIndex(k) for k in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(k).GetName()=='学校_v15_角标长度测试保留']
if protos:assert mp.DeleteTimelines(protos)
# Confirm every clip path is available and no video/audio track was left disabled by QA.
paths=sorted({x['path'] for kind in ['video','audio'] for tr in after[kind] for x in tr['items'] if x['path']});missing=[x for x in paths if not Path(x).exists()];assert not missing
assert all(tr['enabled'] for kind in ['video','audio'] for tr in after[kind])
assert t.SetCurrentTimecode(tc(30));r.OpenPage('edit');assert pm.SaveProject()
finaldrp=ROOT/'学校_大气开篇与书法动态角标_v15.drp';finaldrt=ROOT/'学校_大气开篇与书法动态角标_v15.drt'
assert pm.ExportProject(p.GetName(),str(finaldrp));assert t.Export(str(finaldrt),r.EXPORT_DRT)
(OUT/'final_native_snapshot_v15.json').write_text(json.dumps(after,ensure_ascii=False,indent=2))
(OUT/'final_graphs_v15.json').write_text(json.dumps(g,ensure_ascii=False,indent=2))
report={'project':p.GetName(),'active_timeline':t.GetName(),'fps':25,'size':[1920,1080],'duration_frames':11507,'duration_seconds':11507/25,'changed_base_shots':1,'opening':new,'new_overlay_track':after['video'][4],'audio_exact_to_v14':True,'other_native_clips_exact':True,'other_color_graphs_exact':True,'v14_preserved':True,'all_paths_online':True,'source_paths':len(paths),'native_compositions_persist_after_reopen':True,'loop_samples':positions,'exports':[{'file':str(x),'bytes':x.stat().st_size,'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in [finaldrp,finaldrt]],'motion_qa':json.loads((OUT/'native_motion_qa_v15.json').read_text())}
(OUT/'final_delivery_qa_v15.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['opening','new_overlay_track','loop_samples','motion_qa']},ensure_ascii=False,indent=2))
