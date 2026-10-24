from common_v14 import *
import wave,subprocess
r,pm,p,mp,t=connect();plan=json.loads((OUT/'native_segments_v14.json').read_text());movie=ROOT/'旁白与混音'/'04_旁白精修_25帧无损PCM时钟封装_v14.mov';folder=next(x for x in mp.GetRootFolder().GetSubFolderList() if x.GetName()=='v14_旁白气口精修');previous=mp.GetCurrentFolder();assert mp.SetCurrentFolder(folder);media=mp.ImportMedia([str(movie)]);assert media and len(media)==1;media=media[0];assert mp.SetCurrentFolder(previous);props=media.GetClipProperty();assert float(props['FPS'])==25,props
with wave.open(plan['path']) as wav:pcm_sha=hashlib.sha256(wav.readframes(wav.getnframes())).hexdigest()
proc=subprocess.run(['/Users/xuan/.local/bin/ffmpeg','-v','error','-i',str(movie),'-map','0:a:0','-c:a','pcm_s24le','-f','hash','-hash','sha256','-'],capture_output=True,text=True,check=True);movie_sha=proc.stdout.strip().split('=')[-1].lower();assert movie_sha==pcm_sha
scratch=mp.CreateEmptyTimeline('v14_PCM时钟封装_临时精度验证');assert scratch and p.SetCurrentTimeline(scratch);assert scratch.SetSetting('useCustomSettings','1');assert scratch.SetSetting('timelineFrameRate','25');rows=[]
try:
 infos=[{'mediaPoolItem':media,'startFrame':x['source_start_frame'],'endFrame':x['source_end_frame_exclusive'],'recordFrame':x['record_start_frame'],'trackIndex':1,'mediaType':2} for x in plan['native_segments']]
 items=mp.AppendToTimeline(infos);assert items and len(items)==23
 for it,want in zip(sorted(scratch.GetItemListInTrack('audio',1),key=lambda x:x.GetStart()),plan['native_segments']):
  row={'start':it.GetStart(True),'end':it.GetEnd(True),'source_start_time':it.GetSourceStartTime(),'left_offset':it.GetLeftOffset(True),'source_end_time':it.GetSourceEndTime(),'target_source_start_seconds':want['source_start_frame']/25,'target_record_start':want['record_start_frame'],'target_record_end':want['record_end_frame_exclusive'],'audio_mapping':it.GetSourceAudioChannelMapping()};rows.append(row)
  assert abs(row['start']-row['target_record_start'])<1e-6 and abs(row['end']-row['target_record_end'])<1e-6 and abs(row['source_start_time']-row['target_source_start_seconds'])<1/48000/2,row
 assert not scratch.GetItemListInTrack('video',1)
finally:
 assert p.SetCurrentTimeline(t);assert mp.DeleteTimelines([scratch])
(OUT/'pcm_clock_container_probe_v14.json').write_text(json.dumps({'status':'passed','path':str(movie),'media_fps':25,'pcm_sha256_wav':pcm_sha,'pcm_sha256_mov_decoded':movie_sha,'pcm_values_bit_identical':True,'native_23_clip_source_and_record_clock_exact':True,'rows':rows,'video_carrier_never_placed_on_timeline':True,'properties':{k:props.get(k) for k in ['FPS','Audio Ch','Audio Codec','Audio Bit Depth','Sample Rate','Resolution','File Path']}},ensure_ascii=False,indent=2));assert pm.SaveProject();print('V14_PCM_MOV_CLOCK_PROBE_PASS',len(rows),flush=True)
