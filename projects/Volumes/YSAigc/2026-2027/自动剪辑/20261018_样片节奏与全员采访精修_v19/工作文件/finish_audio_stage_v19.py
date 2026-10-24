from common_v19 import *
r,pm,p,mp,t=connect();before=json.loads((OUT/'live_before_v19.json').read_text())['snapshot'];vbefore=snap(t)['video'];gbefore=graphs(t)
music=json.loads((ROOT/'旁白与配乐/配乐每40秒/配乐每40秒_原生回装清单_v19.json').read_text());voices=json.loads((ROOT/'旁白与配乐/采访原生时钟/五人采访_25fps原生回装清单_v19.json').read_text())['interviews']
wanted=[]
for x in music['cues']:wanted.append({'track':x['track_index_recommended'],'start':x['record_start_frame'],'end':x['record_end_frame_exclusive'],'source_in':0,'source_path':x['clock_container_path'],'label':f"配乐{x['cue']:02d}｜每40秒换曲｜{Path(x['file']).stem}"})
for x in voices:wanted.append({'track':2,'start':x['record_start_frame'],'end':x['record_end_frame_exclusive'],'source_in':x['source_in_frame'],'source_path':x['container_path'],'label':'全员采访原声｜'+x['speaker_key']})
added=[next(i for i in t.GetItemListInTrack('audio',x['track']) if i.GetMediaPoolItem().GetClipProperty('File Path')==x['source_path']) for x in wanted]
source=(OUT/'apply_audio_v19.py').read_text();exec(compile(source[source.index('for it,x in zip(added,wanted):'):],str(OUT/'apply_audio_v19.py'),'exec'))
