from common_v15 import *
r,pm,p,mp,t=connect();assert pm.SaveProject();assert pm.CloseProject(p)
scratchname='学校_v15_角标交付验证_20261017';scratch=pm.CreateProject(scratchname);assert scratch
try:
 tmp=scratch.GetMediaPool().ImportTimelineFromFile(str(ROOT/'学校_大气开篇与书法动态角标_v15.drt'));assert tmp;assert scratch.SetCurrentTimeline(tmp)
 assert pm.SaveProject();assert pm.CloseProject(scratch);scratch=pm.LoadProject(scratchname);assert scratch;tmp=scratch.GetCurrentTimeline()
 expected=json.loads((OUT/'final_native_snapshot_v15.json').read_text());got=snap(tmp);diff=[]
 for kind in ['video','audio']:
  assert len(got[kind])==len(expected[kind])
  for a,b in zip(expected[kind],got[kind]):
   assert len(a['items'])==len(b['items'])
   for x,y in zip(a['items'],b['items']):
    for k in x:
     if k!='name' and x[k]!=y[k]:diff.append([kind,a['track'],x['start'],k,x[k],y[k]])
 assert not diff,diff
 gotgraphs=graphs(tmp);wantgraphs=json.loads((OUT/'final_graphs_v15.json').read_text());gd=[{'index':i,'expected':x,'actual':y} for i,(x,y) in enumerate(zip(wantgraphs,gotgraphs)) if x!=y];(OUT/'drt_graph_metadata_diff.json').write_text(json.dumps(gd,ensure_ascii=False,indent=2));assert [{k:v for k,v in x.items() if k!='version'} for x in gotgraphs]==[{k:v for k,v in x.items() if k!='version'} for x in wantgraphs],gd[:3]
 (OUT/'drt_reload_qa_v15.json').write_text(json.dumps({'all_native_ranges_and_properties_exact':True,'all_audio_exact':True,'all_color_graphs_exact':True,'fusion_comp_counts_exact':True,'first_source_in':tmp.GetItemListInTrack('video',1)[0].GetLeftOffset(),'source_340_in':next(x for x in tmp.GetItemListInTrack('video',1) if x.GetStart()==340).GetLeftOffset(),'native_custom_clip_names_omitted_by_resolve_drt_import':True},ensure_ascii=False,indent=2))
 print('DRT isolated project save/reopen verified original 340 in150 and every source range/property/audio/color graph')
finally:
 if scratch:pm.CloseProject(scratch)
 original=pm.LoadProject(PROJECT);assert original;assert original.GetCurrentTimeline().GetName()==TIMELINE
 assert pm.DeleteProject(scratchname);r.OpenPage('edit');original.GetCurrentTimeline().SetCurrentTimecode(tc(30));assert pm.SaveProject()
