from common_v19 import *
r,pm,p,mp,t=connect();before=json.loads((OUT/'live_before_v19.json').read_text())['snapshot'];vbefore=snap(t)['video'];gbefore=graphs(t)
music=json.loads((ROOT/'旁白与配乐/配乐每40秒/配乐每40秒_原生回装清单_v19.json').read_text())
voices=json.loads((ROOT/'旁白与配乐/采访原生时钟/五人采访_25fps原生回装清单_v19.json').read_text())['interviews']
assert len(voices)==5 and len(music['cues'])==13 and t.GetEndFrame()==12520
assert snap(t)['audio']==before['audio']
root=mp.GetRootFolder();folder=mp.AddSubFolder(root,'v19_全员采访与40秒配乐');assert folder;previous=mp.GetCurrentFolder();assert mp.SetCurrentFolder(folder)
paths=[x['clock_container_path'] for x in music['cues']]+[x['container_path'] for x in voices]
media=mp.ImportMedia(paths);assert media and len(media)==18;by_path={x.GetClipProperty('File Path'):x for x in media};assert len(by_path)==18;assert all(float(x.GetClipProperty('FPS'))==25 for x in media);assert mp.SetCurrentFolder(previous)
old_principal=next(x for x in t.GetItemListInTrack('audio',2) if x.GetStart()==11042)
delete=[old_principal]+list(t.GetItemListInTrack('audio',3))+list(t.GetItemListInTrack('audio',4));assert t.DeleteClips(delete,False)
infos=[];wanted=[]
for x in music['cues']:
 infos.append({'mediaPoolItem':by_path[x['clock_container_path']],'startFrame':0,'endFrame':x['duration_frames'],'recordFrame':x['record_start_frame'],'trackIndex':x['track_index_recommended'],'mediaType':2})
 wanted.append({'track':x['track_index_recommended'],'start':x['record_start_frame'],'end':x['record_end_frame_exclusive'],'source_in':0,'source_path':x['clock_container_path'],'label':f"配乐{x['cue']:02d}｜每40秒换曲｜{Path(x['file']).stem}"})
for x in voices:
 infos.append({'mediaPoolItem':by_path[x['container_path']],'startFrame':x['source_in_frame'],'endFrame':x['source_out_frame_exclusive'],'recordFrame':x['record_start_frame'],'trackIndex':2,'mediaType':2})
 wanted.append({'track':2,'start':x['record_start_frame'],'end':x['record_end_frame_exclusive'],'source_in':x['source_in_frame'],'source_path':x['container_path'],'label':'全员采访原声｜'+x['speaker_key']})
added=mp.AppendToTimeline(infos);assert added and len(added)==18
for it,x in zip(added,wanted):
 expected_start=float(x['start'])
 if x['track']==2 and x['start']==11042:
  expected_start=next(a for a in t.GetItemListInTrack('audio',2) if a.GetStart()==10935).GetEnd(True)
 trim=expected_start-x['start']
 assert abs(it.GetStart(True)-expected_start)<1e-8 and abs(it.GetEnd(True)-x['end'])<1e-8 and abs(it.GetLeftOffset(True)-(x['source_in']+trim))<1e-8,(x,it.GetStart(True),it.GetEnd(True),it.GetLeftOffset(True))
 assert abs(it.GetSourceStartTime()-(x['source_in']+trim)/25)<1e-8
 assert it.SetName(x['label']);assert it.SetClipColor('Orange' if x['track']>=3 else 'Blue')
assert t.SetTrackName('audio',2,'现场口号与五人采访原声_v19');assert t.SetTrackName('audio',3,'配乐_每40秒换曲_第一组_v19');assert t.SetTrackName('audio',4,'配乐_每40秒换曲_第二组_v19')
after=snap(t);assert after['video']==vbefore;assert graphs(t)==gbefore;assert after['audio'][0]==before['audio'][0]
assert after['audio'][1]['items'][:2]==before['audio'][1]['items'][:2]
assert len(after['audio'][1]['items'])==7 and len(after['audio'][2]['items'])+len(after['audio'][3]['items'])==13
assert t.GetEndFrame()==12520;assert pm.SaveProject()
details=[]
for tr in range(1,5):
 for it in t.GetItemListInTrack('audio',tr):
  m=it.GetMediaPoolItem();details.append({'track':tr,'name':it.GetName(),'record_start_frame':it.GetStart(True),'record_end_frame_exclusive':it.GetEnd(True),'duration_frames':it.GetDuration(True),'source_start_seconds':it.GetSourceStartTime(),'path':m.GetClipProperty('File Path'),'media_fps':m.GetClipProperty('FPS'),'media_start_tc':m.GetClipProperty('Start TC'),'audio_mapping':it.GetSourceAudioChannelMapping(),'enabled':it.GetClipEnabled()})
(OUT/'native_audio_applied_v19.json').write_text(json.dumps({'status':'passed_native_positions_and_source_clock','fps':25,'duration_frames':12520,'duration_seconds':500.8,'music_cue_count':13,'all_five_speakers_audible_items_present':True,'complete_original_narration_and_slogans_preserved':True,'all_existing_picture_preserved_during_audio_work':True,'native_audio_items':details,'normal_speed_audition_available':False},ensure_ascii=False,indent=2))
assert t.SetCurrentTimecode(tc(0));r.OpenPage('edit');print('NATIVE_AUDIO_PASS','13 music cues','5 interviews','23 original VO segments',flush=True)
