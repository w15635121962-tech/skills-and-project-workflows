from common_v14 import *
r,pm,p,mp,t=connect();baseline=snap(t);nodes=graphs(t);plan=json.loads((OUT/'native_segments_v14.json').read_text());aaf=ROOT/'音频交换文件'/'旁白气口_A1_25fps精确回装_v14.aaf';scratch=t.DuplicateTimeline('v14_旁白精确回装核验_临时');assert scratch and p.SetCurrentTimeline(scratch);rows=[];report={'imported':False}
try:
 assert snap(scratch)==baseline;old=scratch.GetItemListInTrack('audio',1);assert len(old)==1;assert scratch.DeleteClips(old,False)
 options={'autoImportSourceClipsIntoMediaPool':True,'ignoreFileExtensionsWhenMatching':False,'linkToSourceCameraFiles':False,'useSizingInfo':False,'importMultiChannelAudioTracksAsLinkedGroups':False,'insertAdditionalTracks':False,'insertWithOffset':'00:00:00:00'}
 ok=scratch.ImportIntoTimeline(str(aaf),options);report['imported']=ok;print('AAF_IMPORTED',ok,flush=True)
 now=snap(scratch);report['tracks']={'video':len(now['video']),'audio':len(now['audio'])};report['video_preserved']=now['video']==baseline['video'];report['other_audio_tracks_preserved']=now['audio'][1:]==baseline['audio'][1:];report['color_preserved']=graphs(scratch)==nodes
 for tr in range(1,scratch.GetTrackCount('audio')+1):
  for it in scratch.GetItemListInTrack('audio',tr):
   if tr!=1:continue
   rows.append({'start':it.GetStart(True),'end':it.GetEnd(True),'offset':it.GetLeftOffset(True),'source_start_time':it.GetSourceStartTime(),'source_end_time':it.GetSourceEndTime(),'path':it.GetMediaPoolItem().GetClipProperty('File Path') if it.GetMediaPoolItem() else None,'audio_mapping':it.GetSourceAudioChannelMapping()})
 report['a1_items']=rows;report['expected_segments']=len(plan['native_segments']);errors=[]
 if len(rows)!=23:errors.append('a1_clip_count')
 for row,want in zip(sorted(rows,key=lambda x:x['start']),plan['native_segments']):
  for name,actual,expected in [('record_start',row['start'],want['record_start_frame']),('record_end',row['end'],want['record_end_frame_exclusive']),('source_time',row['source_start_time'],want['source_start_frame']/25)]:
   if abs(actual-expected)>1e-6:errors.append({'field':name,'actual':actual,'expected':expected})
  if row['path']!=plan['path']:errors.append({'path':row['path']})
 report['errors']=errors;report['passed']=ok and not errors and all(report[x] for x in ['video_preserved','other_audio_tracks_preserved','color_preserved']);assert scratch.Export(str(OUT/'AAF回装临时核验.fcpxml'),r.EXPORT_FCPXML_1_10)
 print(json.dumps({k:v for k,v in report.items() if k!='a1_items'},ensure_ascii=False),flush=True)
finally:
 (OUT/'native_aaf_import_probe_v14.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));assert p.SetCurrentTimeline(t);assert mp.DeleteTimelines([scratch]);assert pm.SaveProject()
