"""Read-only timeline selection/progression record around native L/K transport keys."""
import argparse,datetime,time
from native_common import *
def frame(tc):
 h,m,s,f=map(int,tc.split(':'));return ((h*60+m)*60+s)*24+f
pser=argparse.ArgumentParser();pser.add_argument('action',choices=['prepare','finish']);pser.add_argument('episode',type=int,nargs='?');a=pser.parse_args();r,m,p,mp=connect();q=OUTPUT_DIR/'当前播放核验.json';report=OUTPUT_DIR/'短段实际播放核验.json'
if a.action=='prepare':
 ep=next(e for e in load_plan(OUTPUT_DIR/'final_native_plan.json')['episodes'] if e['episode']==a.episode);j=read_json(OUTPUT_DIR/'Resolve_组装实读.json');rec=next(e for e in j['episodes'] if e['episode']==a.episode);t=next(t for t in timelines(p) if t.GetUniqueId()==rec['id']);assert p.SetCurrentTimeline(t);time.sleep(.25);f=max(0,(ep.get('role_dialogue') or [{'record_start_frame':24}])[0]['record_start_frame']-24);tc=f'{f//86400:02}:{f//1440%60:02}:{f//24%60:02}:{f%24:02}';assert t.SetCurrentTimecode(tc);assert t.SetCurrentTimecode(tc);d={'episode':a.episode,'timeline':t.GetName(),'id':t.GetUniqueId(),'start_timecode':t.GetCurrentTimecode(),'prepared_at':datetime.datetime.now().isoformat()};write_json(q,d);print(d)
else:
 d=read_json(q);t=p.GetCurrentTimeline();assert t.GetUniqueId()==d['id'];end=t.GetCurrentTimecode();n=frame(end)-frame(d['start_timecode']);assert n>0,(d,end);ui=read_json(OUTPUT_DIR/'当前播放UI记录.json');assert ui['stopped_observed'] and ui['playing_not_active_observed'];d.update(end_timecode=end,advanced_frames=n,ui_control_observation=ui,all_av_subtitle_tracks_enabled=all(t.GetIsTrackEnabled(k,i) for k,i in [('video',1),('audio',1),('audio',2),('subtitle',1)]),verification_limit='Native transport progression, enabled picture/audio/subtitle tracks, stop state checked; no claim of full motion/lip-sync watch-through or human audio audition.');rows=read_json(report) if report.exists() else [];rows=[x for x in rows if x['episode']!=d['episode']]+[d];write_json(report,rows);print(d)
