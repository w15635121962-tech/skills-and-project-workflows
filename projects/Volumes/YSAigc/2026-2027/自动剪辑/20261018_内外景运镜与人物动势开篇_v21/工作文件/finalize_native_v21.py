from common_v21 import *
import re
r,pm,p,mp,t=connect();base=json.loads((OUT/'live_before_v21.json').read_text());before=base['snapshot'];oldgraphs=json.loads((OUT/'live_graphs_before_v21.json').read_text());after=snap(t);g=graphs(t)
assert t.GetEndFrame()==11507 and float(t.GetSetting('timelineFrameRate'))==25
assert [len(x['items']) for x in after['video']]==[171,25,39,24,1]
assert after['video'][0]==before['video'][0] and after['video'][4]==before['video'][4]
assert [x for x in after['video'][1]['items'] if x['start']!=340]==[x for x in before['video'][1]['items'] if x['start']!=340]
assert [x for x in after['video'][2]['items'] if x['start']>=667]==[x for x in before['video'][2]['items'] if x['start']>=667]
assert [x for x in after['video'][3]['items'] if x['start']!=340]==before['video'][3]['items']
assert next(x for x in after['video'][3]['items'] if x['start']==340)==next(x for x in before['video'][1]['items'] if x['start']==340)
for tr in [0,1,3]:assert after['audio'][tr]==before['audio'][tr]
assert after['audio'][2]['items'][1:]==before['audio'][2]['items'][1:]
gm={(x['track'],x['start']):x for x in g}
for x in oldgraphs:
 if x['track']==3 and x['start']<667:continue
 y=dict(x,track=4) if x['track']==2 and x['start']==340 else x
 assert gm[(y['track'],y['start'])]==y
new=[i for i in t.GetItemListInTrack('video',3) if i.GetStart()<667];assert len(new)==13
assert new[0].GetStart()==0 and new[-1].GetEnd()==667 and all(a.GetEnd()==b.GetStart() for a,b in zip(new,new[1:]))
for it in new:assert Path(it.GetMediaPoolItem().GetClipProperty('File Path')).is_file()
c=active_comp(next(i for i in new if i.GetStart()==324));xf=c.FindTool('V21_晨光缓推_2p5percent');assert xf;a=int(c.GetAttrs()['COMPN_RenderStart']);z=int(c.GetAttrs()['COMPN_RenderEnd']);sizes=[xf.GetInput('Size',f) for f in [a,(a+z)//2,z]];assert abs(sizes[0]-1)<1e-5 and abs(sizes[-1]-1.025)<1e-5
title=next(i for i in t.GetItemListInTrack('video',4) if i.GetStart()==340);assert title.ExportFusionComp(str(OUT/'原片名_回装后核验.comp'),1)
def normalized_title(path):
 s=path.read_text();s=re.sub(r'(?m)^\s*CurrentID = \d+,\s*$','CurrentID = <session id>,',s)
 return re.sub(r'(?m)^\s*\["ResolveCaches:"\] = .*$', 'ResolveCaches = <per-clip cache path>,',s)
assert normalized_title(OUT/'原片名_回装后核验.comp')==normalized_title(OUT/'原开篇片名_保留样式与时序.comp'),'Native title composition altered'
parent=next(p.GetTimelineByIndex(k) for k in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(k).GetName()==PARENT);assert p.SetCurrentTimeline(parent);assert snap(parent)==before and graphs(parent)==oldgraphs;assert p.SetCurrentTimeline(t)
r.OpenPage('edit');assert t.SetCurrentTimecode(tc(0));assert pm.SaveProject()
(OUT/'final_native_snapshot_v21.json').write_text(json.dumps(after,ensure_ascii=False,indent=2));(OUT/'final_graphs_v21.json').write_text(json.dumps(g,ensure_ascii=False,indent=2))
file=ROOT/'学校_内外景运镜与人物动势开篇_v21.drp';assert not file.exists();assert pm.ExportProject(PROJECT,str(file))
report=dict(active_timeline=TIMELINE,duration_frames=11507,duration_seconds=460.28,fps=25,resolution=[1920,1080],opening_picture_range_frames=[0,667],opening_shots=13,native_morninglight_push_sizes=sizes,original_title_graph_layout_and_animation_identical=True,title_comparison_excluded_metadata=['CurrentID','ResolveCaches per-clip path'],original_title_track=4,parent_timeline_preserved=True,all_underlying_video_intact=True,all_picture_and_grades_outside_opening_intact=True,narration_and_original_live_speech_unchanged=True,new_interviews_added=False,music_after40p8_pcm_bit_identical_to_original=True,other_music_items_unchanged=True,export=str(file),export_bytes=file.stat().st_size,export_sha256=hashlib.sha256(file.read_bytes()).hexdigest(),normal_speed_listening_available=False)
assert pm.CloseProject(p);scratch='学校_v21_开篇工程回装核验_20261018';assert pm.ImportProject(str(file),scratch)
try:
 test=pm.LoadProject(scratch);assert test;tl=test.GetCurrentTimeline();assert tl.GetName()==TIMELINE;assert snap(tl)==after and graphs(tl)==g;r.OpenPage('edit')
 imagechecks=[]
 for f in [30,347,393,577,634]:
  path=PRE/f'工程重导核验_{f:04d}.jpg';cap(test,tl,f,path,wait=.05);a=np.asarray(Image.open(path).convert('RGB'),float);b=np.asarray(Image.open(PRE/f'原生终版_{f:04d}.jpg').convert('RGB'),float);mad=float(abs(a-b).mean());assert mad<.2,(f,mad);imagechecks.append(dict(frame=f,native_before_to_reimport_MAD=mad))
 report.update(full_project_isolated_import_verified=True,actual_native_frame_reimport_checks=imagechecks)
finally:
 cur=pm.GetCurrentProject()
 if cur:assert pm.CloseProject(cur)
 p=pm.LoadProject(PROJECT);assert p;t=p.GetCurrentTimeline();assert t.GetName()==TIMELINE;assert snap(t)==after and graphs(t)==g;assert pm.DeleteProject(scratch);assert t.SetCurrentTimecode(tc(0));r.OpenPage('edit');assert pm.SaveProject()
(OUT/'native_delivery_qa_v21.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
