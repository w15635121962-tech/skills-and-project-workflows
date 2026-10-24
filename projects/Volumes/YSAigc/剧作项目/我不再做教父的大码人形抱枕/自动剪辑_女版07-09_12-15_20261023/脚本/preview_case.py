import argparse
from native_common import *
from insert_srt import parse_srt
a=argparse.ArgumentParser();a.add_argument('index',type=int);args=a.parse_args()
p=load_plan(BASE/'final_native_plan.json');cases=[]
for e in p['episodes']:
 cs=parse_srt(e['subtitle_srt'])
 for label,idx in [('first',0),('middle',len(cs)//2),('longest',max(range(len(cs)),key=lambda i:len(cs[i][2]))),('last',len(cs)-1)]:
  cue=cs[idx];frame=(cue[0]+cue[1])//2
  cases.append({'episode':e['episode'],'label':label,'frame':frame,'text':cue[2],'cue_index':idx+1,'timeline':e['timeline_name'],'path':str(BASE/'画面验收'/('EP%02d_%s.png'%(e['episode'],label)))})
case=cases[args.index];r,m,pr,pool=connect();t=next(t for t in timelines(pr) if t.GetName()==case['timeline']);assert pr.SetCurrentTimeline(t)
f=case['frame'];tc=f'{f//86400:02}:{f//1440%60:02}:{f//24%60:02}:{f%24:02}';assert t.SetCurrentTimecode(tc);assert t.SetCurrentTimecode(tc);assert t.GetCurrentTimecode()==tc
(BASE/'画面验收').mkdir(exist_ok=True);write(BASE/'画面验收/当前抽查.json',case);write(BASE/'画面验收/全部抽查位置.json',cases)
print(args.index,case['episode'],case['label'],tc)
