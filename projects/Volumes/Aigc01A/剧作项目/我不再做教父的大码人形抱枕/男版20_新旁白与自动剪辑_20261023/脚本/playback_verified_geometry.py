"""Short native transport check. All clicks require fresh observed geometry.

No Resolve calls or GUI actions occur on import or without --execute.
Playback progression is evidence of transport only, not full listening or lip-sync.
"""
import argparse,time,datetime
from native_common import *
import apply_track_presets as ui

def frame(tc):
    a=list(map(int,tc.split(':')))
    return ((a[0]*60+a[1])*60+a[2])*24+a[3]
def tc(f):return f'{f//86400:02}:{f//1440%60:02}:{f//24%60:02}:{f%24:02}'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--plan',default=str(BASE/'final_native_plan.json'))
    parser.add_argument('--geometry',required=True)
    parser.add_argument('--seconds',type=float,default=4)
    parser.add_argument('--execute',action='store_true')
    args=parser.parse_args()
    plan=load_plan(args.plan)
    geometry=ui.validate_geometry(args.geometry)
    assert 1<=args.seconds<=8
    for key in ['play_button_point','stop_button_point']:
        assert key in geometry and len(geometry[key])==2,('Reobserve live transport controls',key)
        x,y,w,h=geometry['window_bounds'];px,py=geometry[key]
        assert x<px<x+w and y<py<y+h
    if not args.execute:
        print('Offline playback plan/geometry validated. No app connection or UI action.')
        return
    r,m,p,pool=connect();assert_baseline(p)
    journal=read(BASE/'Resolve_组装实读.json')
    own={e['episode']:e for e in journal['episodes']}
    rows=[]
    assert ui.live_window_bounds()==list(map(float,geometry['window_bounds'])),'Window moved; capture fresh geometry'
    for e in plan['episodes']:
        row=own[e['episode']]
        t=next(x for x in timelines(p) if x.GetUniqueId()==row['id'])
        assert t.GetName()==TIMELINE and p.SetCurrentTimeline(t)
        d=next(x for x in e['audio_events'] if x['kind'] in ['character_dialogue','sync_dialogue','dialogue'])
        first,_=event_record_range(d);f=max(0,first-12)
        assert t.SetCurrentTimecode(tc(f));start=t.GetCurrentTimecode()
        ui.osa('tell application id "com.blackmagic-design.DaVinciResolve" to activate')
        assert ui.live_window_bounds()==list(map(float,geometry['window_bounds']))
        try:
            ui.real_click(geometry['play_button_point']);time.sleep(args.seconds)
        finally:
            ui.real_click(geometry['stop_button_point'])
        end=t.GetCurrentTimecode();stopped=t.GetCurrentTimecode();time.sleep(.3);stable=t.GetCurrentTimecode()
        assert frame(end)>frame(start),(start,end)
        assert stopped==stable,'Transport did not remain stopped'
        result={'episode':20,'timeline':t.GetName(),'start':start,'end':end,
                'advanced_frames':frame(end)-frame(start),'stopped_timecode':stable,
                'stop_frame_stable':True,'requested_wall_seconds':args.seconds,
                'geometry_proof':str(Path(args.geometry).resolve()),
                'video_audio_subtitles_enabled':all(t.GetIsTrackEnabled(k,i) for k,i in [('video',1),('audio',1),('audio',2),('subtitle',1)]),
                'scope':'Actual short transport progression and stable stop only. Full human listening and visual/lip-sync review remain separate.'}
        rows.append(result);write(BASE/'短段实际播放核验.json',rows)
        print(json.dumps(result,ensure_ascii=False),flush=True)
    assert_baseline(p);assert m.SaveProject()

if __name__=='__main__':main()
