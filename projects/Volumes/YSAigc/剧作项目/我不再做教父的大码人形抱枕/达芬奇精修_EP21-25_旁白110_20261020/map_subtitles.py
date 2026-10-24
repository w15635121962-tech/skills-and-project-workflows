import json,re
from pathlib import Path
OUT=Path(__file__).resolve().parent
snap=json.loads((OUT/'Resolve_精修前实时实读.json').read_text())
native=json.loads((OUT/'原生110分组实测.json').read_text())
dest=OUT/'SRT_110精修';dest.mkdir(exist_ok=True)
def overlap(a,b,c,d):return max(0,min(b,d)-max(a,c))
def structural(x,gs):
 loss=0
 for g in gs:
  old=g['old']
  if x>=old['end']:loss+=g['removed_frames']
  elif x>old['start']:
   return g['new_start']+(x-old['start'])/max(1,old['end']-old['start'])*(g['new_end']-g['new_start'])
  else:break
 return x-loss
def vo_map(x,g):
 old=g['old'];src=old['source_start']+x-old['start']
 if x<old['start']:return g['new_start']+x-old['start']
 if x>old['end']:return g['new_end']+x-old['end']
 for part,actual in zip(g['parts'],g['native_110']):
  a=part['source_start'];b=part['source_end']
  if src<a:return actual['start']
  if src<=b:return min(actual['end'],actual['start']+(src-a)/1.1)
 return g['new_end']
def tc(fr,srt=False):
 sec=fr/24;ms=round(sec*1000)
 if srt:return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
 return f'{fr//86400:02}:{fr//1440%60:02}:{fr//24%60:02}:{fr%24:02}'
result={'episodes':[]}
for e,t in zip(native['episodes'],snap['timelines']):
 cues=[]
 for ix,c in enumerate(t['tracks']['subtitle'][0]['items']):
  speech=[]
  for g in e['groups']:speech.append((overlap(c['start'],c['end'],g['old']['start'],g['old']['end']),'VO',g))
  for a in t['tracks']['audio'][0]['items']:speech.append((overlap(c['start'],c['end'],a['start'],a['end']),'A1',a))
  amt,kind,target=max(speech,key=lambda a:a[0]);assert amt>0,(e['episode'],c)
  if kind=='VO':start,end=[round(vo_map(c[k],target)) for k in ['start','end']]
  else:start,end=[round(structural(c[k],e['groups'])) for k in ['start','end']]
  assert start>=0 and end>start,(e['episode'],ix,start,end)
  cues.append({'ordinal':ix,'text':c['name'],'old_start':c['start'],'old_end':c['end'],'start':start,'end':end,'start_tc':tc(start),'end_tc':tc(end),'speech':kind})
 for a,b in zip(cues,cues[1:]):assert a['end']<=b['start'],(e['episode'],a,b)
 q={'episode':e['episode'],'working':e['working'],'prep':f"EP{e['episode']}_字幕110准备_v2",'cues':cues}
 (dest/f"EP{e['episode']}.srt").write_text('\n\n'.join(f"{i+1}\n{tc(c['start'],True)} --> {tc(c['end'],True)}\n{c['text'].replace(chr(0x2028),chr(10))}" for i,c in enumerate(cues))+'\n',encoding='utf-8-sig')
 result['episodes'].append(q)
 print(e['episode'],len(cues),'VO',sum(c['speech']=='VO' for c in cues),'last',cues[-1]['end_tc'])
(OUT/'字幕110逐条原生修正计划.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
