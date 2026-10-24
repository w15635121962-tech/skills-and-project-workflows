from common_v20 import *
import shutil,soundfile as sf
r,pm,p,mp,t=connect();base=json.loads((OUT/'live_before_v20.json').read_text());before=base['snapshot'];current=snap(t);assert current['audio']==before['audio'];video=current['video'];oldgraph=json.loads((OUT/'live_graphs_before_v20.json').read_text())
plan=json.loads((ROOT/'旁白与配乐/开篇配乐_原生回装清单_v20.json').read_text());assert plan['container_pcm_bit_identical_to_wav'] and plan['new_cue_before39p2_pcm_bit_identical'] and plan['original_bgm_after40p8_pcm_bit_identical'];assert plan['omitted_old_native_subframe_tail']['all_digital_zero']
previous=mp.GetCurrentFolder();folder=mp.AddSubFolder(mp.GetRootFolder(),'v20_仅开篇配乐');assert folder and mp.SetCurrentFolder(folder);media=mp.ImportMedia([plan['container_path']]);assert len(media)==1 and float(media[0].GetClipProperty('FPS'))==25;assert mp.SetCurrentFolder(previous)
old=next(i for i in t.GetItemListInTrack('audio',3) if i.GetStart()==0);assert t.DeleteClips([old],False)
args={**plan['native_append'],'mediaPoolItem':media[0]};items=mp.AppendToTimeline([args]);assert len(items)==1;new=items[0];assert (new.GetStart(True),new.GetEnd(True),new.GetLeftOffset(True))==(0.0,2861.0,0.0);assert new.SetName(plan['name']);assert new.SetClipColor('Orange')
after=snap(t);g=graphs(t);assert after['video']==video
for tr in [0,1,3]:assert after['audio'][tr]==before['audio'][tr]
assert after['audio'][2]['items'][1:]==before['audio'][2]['items'][1:]
for tr in [0,1,3,4]:assert after['video'][tr]==before['video'][tr]
assert [x for x in after['video'][2]['items'] if x['start']>=614]==before['video'][2]['items'];assert [len(x['items']) for x in after['video']]==[171,25,29,23,1]
gm={(x['track'],x['start']):x for x in g}
for old in oldgraph:assert gm[(old['track'],old['start'])]==old
assert t.GetEndFrame()==11507
parent=next(p.GetTimelineByIndex(k) for k in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(k).GetName()==base['timeline']);assert p.SetCurrentTimeline(parent);assert snap(parent)==before and graphs(parent)==oldgraph;assert p.SetCurrentTimeline(t)
# Reuse the verified native sequence only after proving all v20 opening pixels and PCM match.
v19=ROOT.parent/'20261018_样片节奏与全员采访精修_v19';pictureqa=json.loads((OUT/'opening_picture_applied_v20.json').read_text());assert all(x['v19_verified_sequence_to_v20_native_MAD']<.15 for x in pictureqa['current_opening_pixels_match_previous_verified_native_sequence'])
a,sra=sf.read(plan['wav_path'],dtype='int32',always_2d=True,start=0,stop=667*1920);b,srb=sf.read(plan['new_strong_opening_cue'],dtype='int32',always_2d=True,start=0,stop=667*1920);assert sra==srb==48000 and np.array_equal(a,b)
src=v19/'精修预览/开篇_三素材与强配乐_预览_v19.mp4';preview=PRE/'开篇_三素材与强配乐_预览_v20.mp4';assert src.exists();shutil.copy2(src,preview);shutil.copy2(v19/'精修预览/开篇_动态预览检查.png',PRE/'开篇_动态预览检查.png')
assert hashlib.sha256(src.read_bytes()).digest()==hashlib.sha256(preview.read_bytes()).digest()
assert t.SetCurrentTimecode(tc(0));r.OpenPage('edit');assert pm.SaveProject();(OUT/'final_native_snapshot_v20.json').write_text(json.dumps(after,ensure_ascii=False,indent=2));(OUT/'final_graphs_v20.json').write_text(json.dumps(g,ensure_ascii=False,indent=2))
file=ROOT/'学校_开篇三素材与强配乐_v20.drp';assert pm.ExportProject(PROJECT,str(file))
report={'active_timeline':TIMELINE,'fps':25,'resolution':[1920,1080],'duration_frames':11507,'duration_seconds':460.28,'new_interviews_added':False,'requested_three_sources_added_in_opening':True,'original_timeline_preserved':True,'all_original_picture_preserved':True,'all_original_color_graphs_versions_preserved':True,'narration_and_live_speech_untouched':True,'other_music_clips_untouched':True,'music_after40p8_seconds_PCM_identical_to_original':True,'old_native_fractional_tail_only_digital_zero':True,'strong_opening_music_seconds':[0,40],'music_crossfade_seconds':[39.2,40.8],'preview':str(preview),'preview_duration_seconds':26.68,'preview_fps':25,'preview_frames':667,'preview_native_pixel_and_PCM_equivalence_verified':True,'export':str(file),'export_bytes':file.stat().st_size,'export_sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'reference_full_playback_available':False,'normal_speed_listening_available':False}
assert pm.CloseProject(p);scratch='学校_v20_开篇工程核验_20261018';assert pm.ImportProject(str(file),scratch)
try:
 test=pm.LoadProject(scratch);assert test;tl=test.GetCurrentTimeline();assert tl.GetName()==TIMELINE;assert snap(tl)==after and graphs(tl)==g;r.OpenPage('edit')
 for f in [146,587]:
  path=PRE/f'工程重新导入核验_{f}.jpg';cap(test,tl,f,path,wait=.05);a=np.array(Image.open(path).convert('RGB'),float);b=np.array(Image.open(PRE/f'v20开篇核验_{f}.jpg').convert('RGB'),float);assert abs(a-b).mean()<.2
 report['full_project_isolated_import_verified']=True
finally:
 cur=pm.GetCurrentProject()
 if cur:assert pm.CloseProject(cur)
 p=pm.LoadProject(PROJECT);assert p;t=p.GetCurrentTimeline();assert t.GetName()==TIMELINE;assert snap(t)==after and graphs(t)==g;assert pm.DeleteProject(scratch);assert t.SetCurrentTimecode(tc(0));r.OpenPage('edit');assert pm.SaveProject()
(OUT/'final_delivery_qa_v20.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)
