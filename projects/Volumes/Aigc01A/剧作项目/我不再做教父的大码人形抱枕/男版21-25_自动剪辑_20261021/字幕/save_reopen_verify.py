import sys,json,hashlib,zipfile,datetime
from pathlib import Path
import xml.etree.ElementTree as ET
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).resolve().parent
rows=json.loads((OUT/'五集字幕导入清单.json').read_text(encoding='utf-8'))
folder=OUT/'原生字幕时间线';folder.mkdir(exist_ok=True)
def style_hash(path):
 with zipfile.ZipFile(path) as z:
  seq=ET.fromstring(z.read(next(n for n in z.namelist() if n.startswith('SeqContainer/') and n.endswith('.xml'))))
  track=seq.find('.//SubtitleTrackVec/Element/Sm2TiTrack');assert track is not None
  value=track.findtext('FieldsBlob');assert value
  return hashlib.sha256(value.encode('utf-8')).hexdigest()
def get_timelines(p):return {p.GetTimelineByIndex(i).GetUniqueId():p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)}
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='大码枕头'
assert pm.SaveProject();before_ts=get_timelines(p);count=p.GetTimelineCount()
report={'project':p.GetName(),'saved_at':datetime.datetime.now().isoformat(),'timeline_count':count,'episodes':[]}
for row in rows:
 t=before_ts[row['timeline_id']];assert t.GetTrackName('subtitle',1)==str(row['ep'])
 assert len(t.GetItemListInTrack('subtitle',1) or [])==row['cue_count']
 path=folder/f'EP{row["ep"]}_男版_含SRT字幕.drt'
 assert t.Export(str(path),r.EXPORT_DRT)
 report['episodes'].append({'ep':row['ep'],'drt':str(path),'track_fields_hash_before':style_hash(path),'cues':row['cue_count']})
backup=OUT/'大码枕头_男版21-25_含SRT字幕预设_完成.drp'
assert pm.ExportProject(p.GetName(),str(backup)) and backup.stat().st_size>0
report['project_export']=str(backup)
assert pm.CloseProject(p)
p=pm.LoadProject('大码枕头');assert p and p.GetTimelineCount()==count
now=get_timelines(p)
for row,e in zip(rows,report['episodes']):
 t=now[row['timeline_id']];assert t.GetName()==row['timeline']
 assert p.SetCurrentTimeline(t)  # Resolve returns false track-enable values for cold inactive timelines after reopen.
 assert t.GetTrackCount('subtitle')==1 and t.GetTrackName('subtitle',1)==str(row['ep'])
 assert t.GetIsTrackEnabled('subtitle',1) and len(t.GetItemListInTrack('subtitle',1) or [])==row['cue_count']
 after=folder/f'EP{row["ep"]}_保存重开回读.drt'
 assert t.Export(str(after),r.EXPORT_DRT)
 e['track_fields_hash_reopened']=style_hash(after)
 e['track_style_payload_persisted']=e['track_fields_hash_before']==e['track_fields_hash_reopened']
 assert e['track_style_payload_persisted']
 print(row['ep'],row['cue_count'],'native track and style persisted',flush=True)
report.update(save_reopen_verified=True,subtitle_total=sum(x['cue_count'] for x in rows),opaque_style_payload_unchanged=True)
(OUT/'保存重开回读.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('SAVED_REOPENED',report['subtitle_total'],flush=True)
