from common_v13 import *
import zipfile
r,pm,p,mp,t=connect();assert t.GetName()==TIMELINE;before=json.loads((OUT/'live_before_v13.json').read_text());built=json.loads((OUT/'package_native_build_v13.json').read_text());checks=[]
assert snap(t)==before['snapshot'] and graphs(t)==before['graphs']
for g in GROUPS:
 it=next(x for x in t.GetItemListInTrack('video',1) if x.GetStart()==g['start']);c=it.GetFusionCompByIndex(1);a=int(c.GetAttrs()['COMPN_RenderStart']);z=int(c.GetAttrs()['COMPN_RenderEnd']);row=next(x for x in built if x['start']==g['start']);noise=c.FindTool('V13_有机流光底');glow=c.FindTool('V13_暖光柔边')
 assert noise and glow and noise.Seethe.GetExpression()==row['noise_expression'];assert noise.GetInput('Seethe',z)>noise.GetInput('Seethe',a)
 assert abs(glow.GetInput('Center',z)[1]-glow.GetInput('Center',a)[1]-row['window_drift_pixels']/1920)<1e-7
 for text in row['text']:
  x=c.FindTool(text['name']);assert x.GetInput('StyledText')==text['text'];assert all(abs(x.GetInput(k)-v)<1e-7 for k,v in zip(['Red1','Green1','Blue1'],text['color']))
 checks.append({'start':g['start'],'native_background_and_motion_persisted':True,'title_and_captions_preserved':True})
parent=next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==PARENT);assert p.SetCurrentTimeline(parent);assert snap(parent)==before['snapshot'] and graphs(parent)==before['graphs']
for g in GROUPS:
 it=next(x for x in parent.GetItemListInTrack('video',1) if x.GetStart()==g['start']);c=it.GetFusionCompByIndex(1);assert not any(x.GetAttrs()['TOOLS_Name'].startswith('V13_') for x in c.GetToolList(False).values());assert abs(c.FindTool('主题题签').GetInput('Red1')-.105)<1e-6
assert p.SetCurrentTimeline(t);assert r.OpenPage('edit');assert t.SetCurrentTimecode(tc(7536));assert pm.SaveProject()
drt=ROOT/'学校_图片动态底板精修_v13.drt';drp=ROOT/'学校_图片动态底板精修_v13.drp';assert t.Export(str(drt),r.EXPORT_DRT);assert pm.ExportProject(PROJECT,str(drp))
artifacts=[]
for path in [drt,drp]:
 with zipfile.ZipFile(path) as archive:assert archive.testzip() is None
 artifacts.append({'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'archive_integrity_passed':True})
assert pm.CloseProject(p);time.sleep(.5);p=pm.LoadProject(PROJECT);assert p and p.GetName()==PROJECT;t=p.GetCurrentTimeline();assert t.GetName()==TIMELINE and snap(t)==before['snapshot'] and graphs(t)==before['graphs'];assert r.OpenPage('edit');actual=[]
for st in [1871,3749,7509,9960]:
 g=next(x for x in GROUPS if x['start']==st);path=PRE/'保存重开核验'/f'{st}.jpg';im=cap(p,t,st+g['length']//2,path,.8);baseline=Image.open(PRE/'精修后'/f'{st}.jpg').convert('RGB');d=float(abs(np.array(im,float)-np.array(baseline,float)).mean());assert d<.05,(st,d);actual.append({'start':st,'saved_reopened_native_rgb_mean_difference':d})
assert t.SetCurrentTimecode(tc(7536));assert pm.SaveProject();sources={x['path'] for family in ['video','audio'] for track in before['snapshot'][family] for x in track['items'] if x['path']};offline=[s for s in sources if not Path(s).is_file()];assert not offline,offline
(OUT/'final_delivery_qa_v13.json').write_text(json.dumps({'project':PROJECT,'active_timeline':TIMELINE,'timeline_frames':t.GetEndFrame()-t.GetStartFrame(),'fps':25,'native_dynamic_packages':checks,'parent_timeline_preserved':True,'all_timing_audio_and_grades_preserved':True,'all_sources_online':len(sources),'native_save_and_reopen_frames':actual,'artifacts':artifacts,'transient_photo_preview_cache_resolved_by_project_reload':True,'full_movie_rendered':False},ensure_ascii=False,indent=2));print('V13_SAVED_REOPENED_AND_VERIFIED',len(checks),len(sources),flush=True)
