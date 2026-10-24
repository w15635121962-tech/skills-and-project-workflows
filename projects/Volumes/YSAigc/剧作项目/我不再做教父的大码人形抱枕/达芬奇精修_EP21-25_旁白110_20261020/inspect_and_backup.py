import json, re, sys
from pathlib import Path
sys.path.insert(0, '/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).resolve().parent
r=get_resolve(); pm=r.GetProjectManager(); p=pm.GetCurrentProject()
assert p and p.GetName()=='大码枕头'
original=p.GetCurrentTimeline(); tc=original.GetCurrentTimecode()
assert pm.SaveProject()
backup=OUT/'大码枕头_旁白110精修前完整备份.drp'
assert not backup.exists()
assert pm.ExportProject(p.GetName(),str(backup))
report={'project':p.GetName(),'version':r.GetVersionString(),'current':original.GetName(),'timecode':tc,'backup':str(backup),'timelines':[]}
for i in range(1,p.GetTimelineCount()+1):
 t=p.GetTimelineByIndex(i)
 if not re.fullmatch(r'大码_女版_EP2[1-5]_剧情剪辑_v1',t.GetName()):continue
 assert p.SetCurrentTimeline(t)
 q={'name':t.GetName(),'id':t.GetUniqueId(),'start':t.GetStartFrame(),'end':t.GetEndFrame(),'settings':t.GetSettings(),'tracks':{}}
 for kind in ['video','audio','subtitle']:
  q['tracks'][kind]=[]
  for idx in range(1,t.GetTrackCount(kind)+1):
   tr={'track':idx,'name':t.GetTrackName(kind,idx),'enabled':t.GetIsTrackEnabled(kind,idx),'locked':t.GetIsTrackLocked(kind,idx),'items':[]}
   for item in t.GetItemListInTrack(kind,idx) or []:
    m=item.GetMediaPoolItem()
    tr['items'].append({'id':item.GetUniqueId(),'name':item.GetName(),'start':item.GetStart(),'end':item.GetEnd(),'duration':item.GetDuration(),'source_start':item.GetSourceStartFrame() if m else None,'source_end':item.GetSourceEndFrame() if m else None,'source_path':m.GetClipProperty('File Path') if m else None,'media_properties':m.GetClipProperty() if m else None,'properties':item.GetProperties(),'enabled':item.GetClipEnabled(),'fusion_count':item.GetFusionCompCount()})
   q['tracks'][kind].append(tr)
 for ext,typ in [('drt',r.EXPORT_DRT),('fcpxml',r.EXPORT_FCPXML_1_10),('otio',r.EXPORT_OTIO)]:
  f=OUT/(t.GetName()+'_精修前.'+ext)
  q['export_'+ext]=t.Export(str(f),typ)
 report['timelines'].append(q)
 print(json.dumps({'name':q['name'],'end':q['end'],'counts':{k:[len(v['items']) for v in q['tracks'][k]] for k in q['tracks']},'exports':{k:v for k,v in q.items() if k.startswith('export_')}},ensure_ascii=False),flush=True)
assert p.SetCurrentTimeline(original)
original.SetCurrentTimecode(tc)
(OUT/'Resolve_精修前实时实读.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('BACKUP_AND_SNAPSHOT_COMPLETE',flush=True)
