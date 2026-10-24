from common_v19 import *
r,pm,p,mp,t=connect();baseline=json.loads((OUT/'live_before_v19.json').read_text());before=baseline['snapshot']
voice_links=json.loads((ROOT/'旁白与配乐/采访原生时钟/五人采访_25fps原生回装清单_v19.json').read_text())['interviews']
for row in voice_links:
 start=row['record_start_frame'];a=next(x for x in t.GetItemListInTrack('audio',2) if x.GetMediaPoolItem().GetClipProperty('File Path')==row['container_path'])
 v=next(x for x in t.GetItemListInTrack('video',1 if start==12055 else 3) if x.GetStart()==start);members=[v,a]
 if start!=12055:members.append(next(x for x in t.GetItemListInTrack('video',4) if x.GetStart()==start))
 assert t.SetClipsLinked(members,True)
 for member in members:assert {x.GetUniqueId() for x in members if x.GetUniqueId()!=member.GetUniqueId()}<={x.GetUniqueId() for x in member.GetLinkedItems()}
after=snap(t);oldgraphs=json.loads((OUT/'live_graphs_before_v19.json').read_text());newgraphs=graphs(t)
SHIFT=1013;SPLIT=11042;END=12520
assert t.GetStartFrame()==0 and t.GetEndFrame()==END
assert [len(x['items']) for x in after['video']]==[171,25,33,27,2]
for index in range(4):
 actual={x['start']:x for x in after['video'][index]['items']}
 for old in before['video'][index]['items']:
  shifted=old['start']>=SPLIT;want={**old,'start':old['start']+(SHIFT if shifted else 0),'end':old['end']+(SHIFT if shifted else 0)}
  assert actual[want['start']]==want,('old picture changed',index+1,old['start'])
 for k,v in before['video'][index].items():
  if k!='items':assert after['video'][index][k]==v
assert after['audio'][0]==before['audio'][0]
assert after['audio'][1]['items'][:2]==before['audio'][1]['items'][:2]
ng={(x['track'],x['start']):x for x in newgraphs}
for old in oldgraphs:
 want={**old,'start':old['start']+(SHIFT if old['track']<=4 and old['start']>=SPLIT else 0)}
 assert ng[(want['track'],want['start'])]==want,('old grade graph/version changed',old)
opening=json.loads((OUT/'opening_applied_v19.json').read_text())['new_shots']
for row in opening:
 it=next(x for x in after['video'][2]['items'] if x['start']==row['start']);assert it['path']==row['path'] and it['end']==row['end'] and it['offset']==row['in'] and it['enabled']
voice=json.loads((ROOT/'旁白与配乐/采访原生时钟/五人采访_25fps原生回装清单_v19.json').read_text())['interviews'];assert len(voice)==5
for row in voice:
 it=next(x for x in after['audio'][1]['items'] if x['path']==row['container_path']);assert it['enabled'] and it['end']==row['record_end_frame_exclusive']
music=json.loads((ROOT/'旁白与配乐/配乐每40秒/配乐每40秒_原生回装清单_v19.json').read_text());assert len(music['cues'])==13
assert [x['core_start_frame'] for x in music['cues']]==list(range(0,12001,1000));assert all(a['track_id']!=b['track_id'] for a,b in zip(music['cues'],music['cues'][1:]))
assert len(after['audio'][2]['items'])+len(after['audio'][3]['items'])==13
paths={x['path'] for kind in ['video','audio'] for tr in after[kind] for x in tr['items'] if x['path']};assert all(Path(x).exists() for x in paths)
assert not any('/25帧时钟封装/' in x['path'] or '/采访原生时钟/' in x['path'] for tr in after['video'] for x in tr['items'])
coverage=json.loads((OUT/'采访最终方案/final_interview_coverage_audit_v19.json').read_text());capture=json.loads((OUT/'native_capture_complete_v19.json').read_text());mix=json.loads((OUT/'fresh_native_mix_qa_v19.json').read_text())
assert coverage['substantive_interview_speaker_count']==5 and coverage['pending_source_candidate_reviews']==0 and sum(coverage['group_counts'].values())==1427
assert mix['duration_frames']==END and mix['current_native_audio_items_reconstructed']==43 and mix['independent_four_track_sum_bit_exact_to_full_mix'] and mix['native_A3_A4_sum_bit_exact_to_prepared_music_bus'] and mix['official_check_ok']
parent=next(p.GetTimelineByIndex(k) for k in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(k).GetName()==baseline['timeline']);assert p.SetCurrentTimeline(parent);assert snap(parent)==before;assert graphs(parent)==oldgraphs;assert p.SetCurrentTimeline(t)
assert t.SetCurrentTimecode(tc(0));r.OpenPage('edit');assert pm.SaveProject()
(OUT/'final_native_snapshot_v19.json').write_text(json.dumps(after,ensure_ascii=False,indent=2));(OUT/'final_graphs_v19.json').write_text(json.dumps(newgraphs,ensure_ascii=False,indent=2))
file=ROOT/'学校_样片节奏与全员采访精修_v19.drp';assert pm.ExportProject(PROJECT,str(file))
report={'active_project':PROJECT,'active_timeline':TIMELINE,'fps':25,'resolution':[1920,1080],'duration_frames':END,'duration_seconds':END/25,'added_interview_seconds':SHIFT/25,'requested_three_opening_sources_present':True,'substantive_interview_speaker_count':5,'all_1427_sources_audited':True,'complete_original_narration_and_slogans_preserved':True,'all_original_picture_clips_preserved_with_tail_shift_only':True,'all_original_color_graphs_and_versions_preserved':True,'original_user_timeline_preserved_exactly':True,'music_cue_count':13,'music_change_interval_seconds':40,'music_adjacent_recordings_different':True,'all_media_online':True,'clock_carrier_video_never_on_picture_tracks':True,'full_project_export':str(file),'export_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'reference_video_full_watch_available':False,'normal_speed_listening_available':False,'native_capture':capture,'mix_qa_path':str(OUT/'fresh_native_mix_qa_v19.json')}
assert pm.CloseProject(p);scratch='学校_v19_完整工程核验_20261018';assert pm.ImportProject(str(file),scratch)
try:
 test=pm.LoadProject(scratch);assert test;tl=test.GetCurrentTimeline();assert tl.GetName()==TIMELINE;assert snap(tl)==after;assert graphs(tl)==newgraphs;r.OpenPage('edit')
 for f in [146,11135,11647,12470,12519]:
  path=PRE/f'完整工程重新导入核验_{f}.jpg';cap(test,tl,f,path,wait=.05)
  original=PRE/f'原生核验_{f:05d}.jpg'
  if original.exists():
   a=np.array(Image.open(original).convert('RGB'),float);b=np.array(Image.open(path).convert('RGB'),float);assert abs(a-b).mean()<.2,('roundtrip image changed',f,float(abs(a-b).mean()))
 report['full_project_isolated_import_verified']=True
finally:
 current=pm.GetCurrentProject()
 if current:assert pm.CloseProject(current)
 p=pm.LoadProject(PROJECT);assert p;t=p.GetCurrentTimeline();assert t.GetName()==TIMELINE;assert snap(t)==after;assert graphs(t)==newgraphs;assert pm.DeleteProject(scratch)
 assert t.SetCurrentTimecode(tc(0));r.OpenPage('edit');assert pm.SaveProject()
(OUT/'final_delivery_qa_v19.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='native_capture'},ensure_ascii=False,indent=2),flush=True)
