"""Short real transport checks; no claim of full human listening or lip-sync acceptance."""
import time,subprocess,datetime
from native_common import *
import apply_track_presets as ui
def frame(tc):
    a=list(map(int,tc.split(':')));return ((a[0]*60+a[1])*60+a[2])*24+a[3]
def tc(f):return f'{f//86400:02}:{f//1440%60:02}:{f//24%60:02}:{f%24:02}'
r,m,p,pool=connect();plan=load_plan(BASE/'final_native_plan.json');rows=[]
assert ui.live_window_bounds()==[88,25,2300,1250], 'Reobserve playback geometry after window moves'
for e in plan['episodes']:
    t=next(x for x in timelines(p) if x.GetName()==e['timeline_name']);assert p.SetCurrentTimeline(t)
    d=next(x for x in e['audio_events'] if x['kind']!='narration');f=max(0,d['record_frame']+d['source_start_frame']-d.get('clip_source_start_frame',d['source_start_frame'])-12)
    assert t.SetCurrentTimecode(tc(f));assert t.SetCurrentTimecode(tc(f));start=t.GetCurrentTimecode()
    ui.osa('tell application id "com.blackmagic-design.DaVinciResolve" to activate')
    try:
        ui.real_click([1719.5,429]);time.sleep(4)
    finally:
        ui.real_click([1690.5,429])
    # Resolve's synchronous scripting calls may block during playback. Read only
    # after the native stop event so transport is always stopped after four seconds.
    end=t.GetCurrentTimecode()
    stopped=t.GetCurrentTimecode();time.sleep(.3);stable=t.GetCurrentTimecode()
    assert frame(end)>frame(start),(e['episode'],start,end)
    assert stopped==stable,(e['episode'],'transport not stopped',stopped,stable)
    row={'episode':e['episode'],'timeline':t.GetName(),'start':start,'end':end,'advanced_frames':frame(end)-frame(start),
         'stopped_timecode':stopped,'stop_frame_stable':True,'requested_wall_seconds':4,
         'video_audio_subtitles_enabled':all(t.GetIsTrackEnabled(k,i) for k,i in [('video',1),('audio',1),('audio',2),('subtitle',1)]),
         'scope':'Actual transport progression, stable stop and enabled tracks. Not complete human listening or lip-sync judgement.'}
    rows.append(row);write(BASE/'短段实际播放核验.json',rows);print(row,flush=True)
assert m.SaveProject()
