from common_v14 import *
r,pm,p,mp,t=connect();folder=next(x for x in mp.GetRootFolder().GetSubFolderList() if x.GetName()=='v14_旁白气口精修');media=next(x for x in folder.GetClipList() if x.GetClipProperty('File Path').endswith('01_完整旁白_气口精修_v14_48k24.wav'));fps=float(media.GetClipProperty('FPS'));print('MEDIA_FPS',fps,flush=True)
scratch=mp.CreateEmptyTimeline('v14_音频源时钟校验_临时');assert scratch and p.SetCurrentTimeline(scratch);assert scratch.SetSetting('useCustomSettings','1');assert scratch.SetSetting('timelineFrameRate','25');rows=[]
try:
 for i,(start,N) in enumerate([(1580,58),(2136,37),(6478,57)]):
  a=start/25*fps;b=(start+N)/25*fps-1;items=mp.AppendToTimeline([{'mediaPoolItem':media,'startFrame':a,'endFrame':b,'recordFrame':i*100,'trackIndex':1,'mediaType':2}]);assert items and len(items)==1;it=items[0]
  row={'input_source_frames':[a,b],'target_source_seconds':[start/25,(start+N)/25],'target_record_frames':[i*100,i*100+N],'actual_record_frames':[it.GetStart(True),it.GetEnd(True)],'left_offset':it.GetLeftOffset(True),'source_start_frame':it.GetSourceStartFrame(),'source_end_frame':it.GetSourceEndFrame(),'source_start_time':it.GetSourceStartTime(),'source_end_time':it.GetSourceEndTime()};rows.append(row);print(json.dumps(row),flush=True)
 assert scratch.Export(str(OUT/'音频源时钟校验.fcpxml'),r.EXPORT_FCPXML_1_10)
finally:
 assert p.SetCurrentTimeline(t);assert mp.DeleteTimelines([scratch])
(OUT/'audio_native_clock_probe_v14.json').write_text(json.dumps({'source_fps':fps,'target_fps':25,'rows':rows},ensure_ascii=False,indent=2));assert pm.SaveProject()
