from common_v15 import *
r,pm,p,mp,t=connect();assert pm.SaveProject()
# The timeline-only exchange export omits local grade versions on this build.
# Deliver the full project; move the exchange test out of final outputs.
path=ROOT/'学校_大气开篇与书法动态角标_v15.drt'
if path.exists():path.rename(OUT/'DRT测试文件_未保留全部调色版本_不用于交付.drt')
assert pm.CloseProject(p)
name='学校_v15_完整工程交付核验_20261017';assert pm.ImportProject(str(ROOT/'学校_大气开篇与书法动态角标_v15.drp'),name)
try:
 test=pm.LoadProject(name);assert test;tl=test.GetCurrentTimeline();assert tl.GetName()==TIMELINE
 before=json.loads((OUT/'final_native_snapshot_v15.json').read_text());after=snap(tl);assert before==after,'Full project roundtrip changed snapshot'
 g=graphs(tl);assert g==json.loads((OUT/'final_graphs_v15.json').read_text()),'Full project roundtrip lost grade versions'
 assert tl.GetItemListInTrack('video',1)[0].GetFusionCompCount()==1 and tl.GetItemListInTrack('video',5)[0].GetFusionCompCount()==1
 font=active_comp(tl.GetItemListInTrack('video',5)[0]).FindTool('V15_书法校名');assert font.GetInput('Font')=='Ma Shan Zheng'
 r.OpenPage('edit');cap(test,tl,30,PRE/'完整工程重新导入_开篇核验.jpg')
 (OUT/'full_project_import_qa_v15.json').write_text(json.dumps({'format':'DRP','imported_into_isolated_project':True,'all_native_ranges_and_properties_exact':True,'all_audio_exact':True,'all_color_graphs_and_version_names_exact':True,'native_corner_bug_font_and_comp_exact':True,'full_project_delivery':str(ROOT/'学校_大气开篇与书法动态角标_v15.drp'),'timeline_exchange_not_delivered':'On this build DRT omits current local grade versions; use the verified full DRP project.'},ensure_ascii=False,indent=2))
 print('FULL DRP import PASS: exact native timeline, full current color versions, all audio, editable font/animation')
finally:
 test=pm.GetCurrentProject()
 if test:pm.CloseProject(test)
 original=pm.LoadProject(PROJECT);assert original;tl=original.GetCurrentTimeline();assert tl.GetName()==TIMELINE
 assert graphs(tl)==json.loads((OUT/'final_graphs_v15.json').read_text())
 assert snap(tl)==json.loads((OUT/'final_native_snapshot_v15.json').read_text())
 assert pm.DeleteProject(name);r.OpenPage('edit');tl.SetCurrentTimecode(tc(30));assert pm.SaveProject()
 report=json.loads((OUT/'final_delivery_qa_v15.json').read_text());report['exports']=[x for x in report['exports'] if x['file'].endswith('.drp')];report['timeline_only_exchange_delivered']=False;report['full_project_import_verified']=(OUT/'full_project_import_qa_v15.json').exists();(OUT/'final_delivery_qa_v15.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
