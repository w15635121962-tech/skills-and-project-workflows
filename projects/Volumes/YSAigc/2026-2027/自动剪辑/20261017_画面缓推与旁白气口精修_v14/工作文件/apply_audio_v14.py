from common_v14 import *
import soundfile as sf
r,pm,p,mp,t=connect();before=json.loads((OUT/'live_before_v14.json').read_text());plan=json.loads((OUT/'native_segments_v14.json').read_text());audioqa=json.loads((OUT/'audio_edit_map_v14.json').read_text());motion=json.loads((OUT/'native_motion_applied_v14.json').read_text());clock=json.loads((OUT/'pcm_clock_container_probe_v14.json').read_text());assert clock['status']=='passed' and clock['pcm_values_bit_identical'];native_path=clock['path'];assert audioqa['all_nonzero_stereo_sample_frame_order_and_values_exactly_equal'];assert len(plan['native_segments'])==23 and len(plan['intentional_A1_gaps'])==11
current=snap(t);assert current['audio']==before['snapshot']['audio'];video_unchanged(t,before,{(x['track'],x['start']) for x in motion});assert graphs(t)==before['graphs']
old=t.GetItemListInTrack('audio',1);assert len(old)==1;original_media=old[0].GetMediaPoolItem();assert original_media
previous_folder=mp.GetCurrentFolder();rootfolder=mp.GetRootFolder();folder=next((x for x in rootfolder.GetSubFolderList() if x.GetName()=='v14_旁白气口精修'),None) or mp.AddSubFolder(rootfolder,'v14_旁白气口精修');assert folder and mp.SetCurrentFolder(folder)
newmedia=next((x for x in folder.GetClipList() if x.GetClipProperty('File Path')==native_path),None)
if not newmedia:
 imported=mp.ImportMedia([native_path]);assert imported and len(imported)==1;newmedia=imported[0]
assert newmedia.GetClipProperty('File Path')==native_path;properties=newmedia.GetClipProperty();assert abs(float(properties['FPS'])-25)<.0001,properties
assert mp.SetCurrentFolder(previous_folder);assert pm.SaveProject()
assert t.Export(str(ROOT/'学校_缓推完成_旁白回装前备份.drt'),r.EXPORT_DRT);recovery=t.DuplicateTimeline('学校_v14_旁白回装前_27处缓推完成');assert recovery;assert p.SetCurrentTimeline(t)
infos=[{'mediaPoolItem':newmedia,'startFrame':x['source_start_frame'],'endFrame':x['source_end_frame_exclusive'],'recordFrame':x['record_start_frame'],'trackIndex':1,'mediaType':2} for x in plan['native_segments']]
try:
 assert t.DeleteClips(old,False)
 added=mp.AppendToTimeline(infos);assert added and len(added)==len(infos)
 assert t.SetTrackName('audio',1,'旁白主线_气口精修_v14')
 items=sorted(t.GetItemListInTrack('audio',1),key=lambda x:x.GetStart());assert len(items)==23;actual=[]
 assembled=np.zeros((10842*1920,2),dtype=np.int32);expected,sr=sf.read(plan['path'],dtype='int32',always_2d=True);assert sr==48000
 for it,want in zip(items,plan['native_segments']):
  row={'start':it.GetStart(),'end':it.GetEnd(),'offset':it.GetLeftOffset(),'source_start_time':it.GetSourceStartTime(),'precise_start':it.GetStart(True),'precise_end':it.GetEnd(True),'path':it.GetMediaPoolItem().GetClipProperty('File Path'),'enabled':it.GetClipEnabled(),'audio_mapping':it.GetSourceAudioChannelMapping()}
  assert row['start']==want['record_start_frame'] and row['end']==want['record_end_frame_exclusive'] and row['offset']==want['source_start_frame'] and row['path']==native_path and row['enabled'],(row,want)
  assert abs(row['source_start_time']-want['source_start_frame']/25)<1/48000/2 and abs(row['precise_start']-want['record_start_frame'])<1e-6 and abs(row['precise_end']-want['record_end_frame_exclusive'])<1e-6
  a,b,s=int(row['start']*1920),int(row['end']*1920),int(row['offset']*1920);assembled[a:b]=expected[s:s+b-a];actual.append(row)
 assert np.array_equal(assembled,expected[:len(assembled)])
 gaps=[{'start':int(a.GetEnd()),'end':int(b.GetStart())} for a,b in zip(items,items[1:]) if b.GetStart()>a.GetEnd()]
 assert gaps==[{k:g[k] for k in ['start','end']} for g in plan['intentional_A1_gaps']]
 assert snap(t)['audio'][1:]==before['snapshot']['audio'][1:]
 video_unchanged(t,before,{(x['track'],x['start']) for x in motion});assert graphs(t)==before['graphs'];assert t.GetEndFrame()-t.GetStartFrame()==11507;assert pm.SaveProject()
except Exception:
 assert p.SetCurrentTimeline(recovery);assert pm.SaveProject();raise
(OUT/'native_audio_applied_v14.json').write_text(json.dumps({'active_timeline':t.GetName(),'media_properties':properties,'media_audio_mapping':newmedia.GetAudioMapping(),'prepared_pcm_wav':plan['path'],'native_clock_container':native_path,'wav_and_container_pcm_bit_identical':True,'a1_segments':actual,'intentional_gaps':gaps,'native_a1_reconstructed_pcm_matches_prepared_wav':True,'other_audio_tracks_unchanged':True,'video_sources_cuts_manual_offsets_and_color_preserved':True,'clock_carrier_video_never_added_to_picture_tracks':True,'sample_level_centered_2frame_equal_gain_crossfades_baked_only_in_digital_silence':11,'native_fairlight_transition_objects_added':False,'audition_available':False},ensure_ascii=False,indent=2));print('V14_NATIVE_AUDIO_APPLIED',len(actual),len(gaps),flush=True)
