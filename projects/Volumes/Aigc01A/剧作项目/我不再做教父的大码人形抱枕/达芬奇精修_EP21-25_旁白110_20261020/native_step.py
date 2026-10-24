import json,sys
from pathlib import Path
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).resolve().parent
plan=json.loads((OUT/'旁白原生110执行计划.json').read_text());ep=int(sys.argv[2]);e=next(a for a in plan['episodes'] if a['episode']==ep)
r=get_resolve();p=r.GetProjectManager().GetCurrentProject();ts={p.GetTimelineByIndex(i).GetName():p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)}
def frame_tc(fr):
 return f'{fr//86400:02}:{fr//1440%60:02}:{fr//24%60:02}:{fr%24:02}'
def rows(t):
 return [{'name':i.GetName(),'start':i.GetStart(),'end':i.GetEnd(),'source_start':i.GetSourceStartFrame(),'source_end':i.GetSourceEndFrame(),'path':i.GetMediaPoolItem().GetClipProperty('File Path'),'properties':i.GetProperties()} for i in t.GetItemListInTrack('audio',2) or []]
if sys.argv[1]=='transfer':
 prep=ts[e['prep']];p.SetCurrentTimeline(prep);actual=rows(prep)
 assert len(actual)==sum(len(g['parts']) for g in e['groups'])
 oldparts=[a for g in e['groups'] for a in g['parts']]
 assert all(a['end']-a['start'] < b['pre_record_end']-b['pre_record_start'] for a,b in zip(actual,oldparts))
 (OUT/f'EP{ep}_原生110旁白实读.json').write_text(json.dumps(actual,ensure_ascii=False,indent=2))
 prep.Export(str(OUT/f'EP{ep}_原生110旁白.drt'),r.EXPORT_DRT)
 t=ts[e['working']];p.SetCurrentTimeline(t)
 for k in ['video','audio','subtitle']:
  for j in range(1,t.GetTrackCount(k)+1):assert t.SetTrackLock(k,j,not(k=='audio' and j==2))
 items=t.GetItemListInTrack('audio',2) or []
 if items:assert t.DeleteClips(items,False)
 t.SetCurrentTimecode(frame_tc(actual[0]['start']))
 print('READY_TO_PASTE',ep,'count',len(actual),'first',actual[0]['start'],'last',actual[-1]['end'])
elif sys.argv[1]=='verify_next':
 t=ts[e['working']];p.SetCurrentTimeline(t);expected=json.loads((OUT/f'EP{ep}_原生110旁白实读.json').read_text());actual=rows(t)
 assert actual==expected,('Paste mismatch',ep)
 print('NATIVE_110_PASTE_VERIFIED',ep,len(actual))
 if ep<25:p.SetCurrentTimeline(ts[plan['episodes'][ep-20]['prep']])
 assert r.GetProjectManager().SaveProject()
