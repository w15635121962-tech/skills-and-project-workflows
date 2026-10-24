"""Short native Resolve transport check; this is not human auditory acceptance."""
import sys,time,datetime,json
from pathlib import Path
from native_common import *
OUTPUT_DIR=BASE
read_json=read
write_json=write
sys.path.insert(0,str(Path(__file__).parent/'字幕'))
import apply_track_presets as ui

def control(description):
 raw=ui.osa(ui.APP+'''tell group 1 of window "大码枕头"
repeat with c in checkboxes
if description of c is "'''+description+'''" then
set xy to position of c
set wh to size of c
return {(item 1 of xy)+(item 1 of wh)/2,(item 2 of xy)+(item 2 of wh)/2,value of c}
end if
end repeat
end tell
error "Native transport control missing"'''+ui.END)
 return ui.numbers(raw)
def frame(tc):
 a=list(map(int,tc.split(':')));return ((a[0]*60+a[1])*60+a[2])*24+a[3]
def tc(f):return f'{f//86400:02}:{f//1440%60:02}:{f//24%60:02}:{f%24:02}'
r,m,p,mp=connect();plan=load_plan(OUTPUT_DIR/'final_native_plan.json');j=read_json(OUTPUT_DIR/'Resolve_组装实读.json');byid={t.GetUniqueId():t for t in timelines(p)};report=[]
for ep in plan['episodes']:
 row=next(x for x in j['episodes'] if x['episode']==ep['episode']);t=byid[row['id']];assert p.SetCurrentTimeline(t);time.sleep(.25)
 role=[x for x in ep['audio_events'] if x['kind']!='narration'];d=role[0];f=max(0,d['record_frame']+d['source_start_frame']-d.get('clip_source_start_frame',d['source_start_frame'])-12)
 assert t.SetCurrentTimecode(tc(f));assert t.SetCurrentTimecode(tc(f));start=t.GetCurrentTimecode();ui.osa('tell application id "com.blackmagic-design.DaVinciResolve" to activate');ctl=control('播放');ui.real_click(ctl[:2]);active=control('播放')[2]
 if active!=1:
  # The Qt control may receive focus first. A fresh real press is allowed only
  # after the verified state says the first press did not start transport.
  ui.real_click(control('播放')[:2]);active=control('播放')[2]
 assert active==1,('Playback did not start',ep['episode'])
 began=datetime.datetime.now().isoformat();time.sleep(5);end=t.GetCurrentTimecode();advance=frame(end)-frame(start)
 ui.real_click(control('停止')[:2]);stopped=control('停止')[2];assert stopped==1 and advance>0,(ep['episode'],start,end,stopped)
 item={'episode':ep['episode'],'timeline':t.GetName(),'start_timecode':start,'end_timecode':end,'advanced_frames':advance,'native_play_control_active_observed':True,'native_stop_control_active_observed':True,'playback_requested_wall_seconds':5,'started_at':began,'video_audio_subtitle_tracks_enabled':all(t.GetIsTrackEnabled(k,n) for k,n in [('video',1),('audio',1),('audio',2),('subtitle',1)]),'verification_limit':'Transport progression and enabled tracks observed; not a full watch-through, lip-sync judgement or normal-speed human audio audition.'}
 report.append(item);write_json(OUTPUT_DIR/'短段实际播放核验.json',report);print(json.dumps(item,ensure_ascii=False),flush=True)
assert m.SaveProject()
