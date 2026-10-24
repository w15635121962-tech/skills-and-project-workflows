from common_v14 import *
r,pm,p,mp,t=connect();folder=next(x for x in mp.GetRootFolder().GetSubFolderList() if x.GetName()=='v14_旁白气口精修');media=next(x for x in folder.GetClipList() if x.GetClipProperty('File Path').endswith('01_完整旁白_气口精修_v14_48k24.wav'));old=media.GetClipProperty('FPS');changed=media.SetClipProperty('FPS','25');fps=media.GetClipProperty('FPS');print('FPS_WRITE',old,changed,fps,flush=True)
scratch=mp.CreateEmptyTimeline('v14_音频帧率边界校验_临时');assert scratch and p.SetCurrentTimeline(scratch);assert scratch.SetSetting('useCustomSettings','1');assert scratch.SetSetting('timelineFrameRate','25');rows=[]
try:
 for i,(a,b) in enumerate([(1580,1638),(1580,1637),(2136,2173),(6478,6535)]):
  items=mp.AppendToTimeline([{'mediaPoolItem':media,'startFrame':a,'endFrame':b,'recordFrame':i*100,'trackIndex':1,'mediaType':2}]);assert items and len(items)==1;it=items[0]
  row={'input':[a,b],'record':[it.GetStart(True),it.GetEnd(True)],'offset':it.GetLeftOffset(True),'source_time':[it.GetSourceStartTime(),it.GetSourceEndTime()]};print(json.dumps(row),flush=True);rows.append(row)
finally:
 assert p.SetCurrentTimeline(t);assert mp.DeleteTimelines([scratch])
(OUT/'audio_fps_set_and_endpoint_probe_v14.json').write_text(json.dumps({'old_fps':old,'write_result':changed,'readback_fps':fps,'rows':rows},ensure_ascii=False,indent=2));assert pm.SaveProject()
