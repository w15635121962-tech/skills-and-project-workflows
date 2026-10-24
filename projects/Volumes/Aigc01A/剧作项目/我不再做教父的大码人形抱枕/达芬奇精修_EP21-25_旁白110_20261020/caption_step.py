import json,sys
from pathlib import Path
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).resolve().parent
plan=json.loads((OUT/'字幕110逐条原生修正计划.json').read_text());ep=int(sys.argv[2]);e=next(a for a in plan['episodes'] if a['episode']==ep)
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();ts={p.GetTimelineByIndex(i).GetName():p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)}
def tc(fr):return f'{fr//86400:02}:{fr//1440%60:02}:{fr//24%60:02}:{fr%24:02}'
def compare(t,limit=None):
 actual=t.GetItemListInTrack('subtitle',1) or []
 assert len(actual)==len(e['cues'])
 for a,b in zip(actual[:limit],e['cues'][:limit]):assert (a.GetName(),a.GetStart(),a.GetEnd())==(b['text'],b['start'],b['end']),(ep,b['ordinal'],a.GetName(),a.GetStart(),a.GetEnd(),b)
 return actual
if sys.argv[1]=='prepare':
 base=ts[f'大码_女版_EP{ep}_剧情剪辑_v1'];n=base.DuplicateTimeline(e['prep']);assert n;p.SetCurrentTimeline(n)
 for k in ['video','audio']:
  for j in range(1,n.GetTrackCount(k)+1):
   n.SetTrackLock(k,j,False);items=n.GetItemListInTrack(k,j) or []
   if items:assert n.DeleteClips(items,False)
 n.SetTrackLock('subtitle',1,False);n.SetCurrentTimecode(tc((e['cues'][0]['old_start']+e['cues'][0]['old_end'])//2))
 print('CAPTION_PREP_READY',ep)
elif sys.argv[1]=='verify':
 t=ts[e['prep']];p.SetCurrentTimeline(t);compare(t,int(sys.argv[3]));print('CAPTION_PREFIX_VERIFIED',ep,sys.argv[3])
elif sys.argv[1]=='transfer':
 prep=ts[e['prep']];p.SetCurrentTimeline(prep);compare(prep)
 prep.Export(str(OUT/f'EP{ep}_原生SRT110精修.drt'),r.EXPORT_DRT)
 t=ts[e['working']];p.SetCurrentTimeline(t);t.SetTrackLock('subtitle',1,False)
 a=t.GetItemListInTrack('subtitle',1) or []
 if a:assert t.DeleteClips(a,False)
 t.SetCurrentTimecode(tc(e['cues'][0]['start']));print('CAPTION_READY_PASTE',ep)
elif sys.argv[1]=='verify_paste':
 t=ts[e['working']];p.SetCurrentTimeline(t);compare(t);assert t.GetTrackName('subtitle',1)==str(ep)
 print('NATIVE_SRT_PASTE_VERIFIED',ep,len(e['cues']));assert pm.SaveProject()
