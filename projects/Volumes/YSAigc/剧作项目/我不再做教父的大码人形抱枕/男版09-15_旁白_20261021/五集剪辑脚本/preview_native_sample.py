"""Select a reviewed subtitle sample using official API; never edits timeline data."""
import argparse,json,time
from pathlib import Path
from native_common import *
from subtitle_tools import parse_srt
out=OUTPUT_DIR/'最终画面抽查';out.mkdir(exist_ok=True)
plan=read_json(OUTPUT_DIR/'final_native_plan.json');rows=[]
for e in plan['episodes']:
 cues=parse_srt(e['subtitle_srt']); cand=[('片头',0),('中段',len(cues)//2),('片尾',len(cues)-1),('最长字幕',max(range(len(cues)),key=lambda i:len(cues[i][2])))]
 seen=set()
 for label,i in cand:
  if i in seen:continue
  seen.add(i);s,z,txt=cues[i];f=(s+z)//2
  rows.append({'sample_index':len(rows),'episode':e['episode'],'timeline':e['timeline_name'],'cue_index':i+1,'label':label,'frame':f,'expected_caption':txt,'full_screenshot':str(out/f'EP{e["episode"]:02d}_{label}_UI.jpg'),'viewer_crop':str(out/f'EP{e["episode"]:02d}_{label}_viewer.jpg')})
write_json(out/'抽查帧清单.json',rows)
a=argparse.ArgumentParser();a.add_argument('index',type=int);args=a.parse_args();row=rows[args.index]
r,m,p,mp=connect();journal=read_json(OUTPUT_DIR/'Resolve_组装实读.json');owned=next(x for x in journal['episodes'] if x['episode']==row['episode']);t=next(x for x in timelines(p) if x.GetUniqueId()==owned['id'])
assert t.GetName()==row['timeline']
if p.GetCurrentTimeline().GetUniqueId()!=t.GetUniqueId():
 assert p.SetCurrentTimeline(t);time.sleep(.25)
f=row['frame'];h=f//86400;mi=f//1440%60;sec=f//24%60;fr=f%24;tc=f'{h:02}:{mi:02}:{sec:02}:{fr:02}'
for _ in range(3):
 assert t.SetCurrentTimecode(tc)
 if t.GetCurrentTimecode()==tc:break
assert t.GetCurrentTimecode()==tc
row['actual_api_timecode']=tc;row['current_timeline_id']=t.GetUniqueId();write_json(out/'当前待截图.json',row);print(json.dumps(row,ensure_ascii=False))
