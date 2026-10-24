import copy, datetime, hashlib, json, sys, zipfile, struct, re
from pathlib import Path
from xml.etree import ElementTree as ET
from fractions import Fraction
import apply_safe_av as av
HERE=Path(__file__).resolve().parent
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
def read(n): return json.loads((HERE/n).read_text())
def same_props(actual, expected):
 for k,v in expected.items(): assert k in actual and av.near(actual[k],v),(k,actual.get(k),v)
def stable(row): return {k:v for k,v in row.items() if k!='id'}
def wav_seconds(path):
 with open(path,'rb') as f:
  head=f.read(12);assert head[:4]==b'RIFF' and head[8:]==b'WAVE'
  rate=align=size=None
  while True:
   h=f.read(8)
   if len(h)<8:break
   kind,n=struct.unpack('<4sI',h)
   if kind==b'fmt ':
    data=f.read(n);_,_,rate,_,align,_=struct.unpack('<HHIIHH',data[:16])
   elif kind==b'data':size=n;f.seek(n,1)
   else:f.seek(n,1)
   if n%2:f.seek(1,1)
  assert rate and align and size is not None
  return Fraction(size,align*rate)
def style_hash(drt):
 with zipfile.ZipFile(drt) as z:
  docs=[z.read(n) for n in z.namelist() if n.startswith('SeqContainer/') and n.endswith('.xml')]
  blobs=[b for doc in docs for area in re.findall(rb'<SubtitleTrackVec>(.*?)</SubtitleTrackVec>',doc,re.S) for b in re.findall(rb'<FieldsBlob>(.*?)</FieldsBlob>',area,re.S)][:1]
 assert len(blobs)==1,(drt,len(blobs))
 return hashlib.sha256(blobs[0]).hexdigest()
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='大码枕头'
ts={p.GetTimelineByIndex(i).GetName():p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)}
plan,snap,native,freeze=av.offline_inputs()
captions={e['episode']:e for e in read('字幕110逐条原生修正计划.json')['episodes']}
music={e['episode']:e for e in read('A4配乐导入计划.json')['episodes']}
applied={e['episode']:e for e in read('安全AV应用回读.json')['episodes']}
out=HERE/'最终交付';out.mkdir(exist_ok=True)
stage=sys.argv[1] if len(sys.argv)>1 else '保存前'
run_id=datetime.datetime.now().strftime('%H%M%S')
report={'time':datetime.datetime.now().isoformat(),'project':p.GetName(),'stage':stage,'episodes':[],'originals_unchanged':[]}
totals={'A1':0,'A2':0,'S1':0,'A4':0}
for e in plan['episodes']:
 ep=e['episode'];t=ts[e['timeline_name']];assert p.SetCurrentTimeline(t)
 assert (t.GetStartFrame(),t.GetEndFrame())==(0,e['duration_frames'])
 assert (t.GetTrackCount('video'),t.GetTrackCount('audio'),t.GetTrackCount('subtitle'))==(1,4,1)
 tracks=av.snapshot_tracks(t)
 assert all(tr['enabled'] for kind in tracks.values() for tr in kind)
 assert all(it['enabled'] for kind in tracks.values() for tr in kind for it in tr['items'])
 assert tracks['subtitle'][0]['name']==str(ep)
 for key,kind,idx in [('video','video',1),('audio_A1','audio',1),('audio_A3','audio',3)]:
  actual=t.GetItemListInTrack(kind,idx) or []; assert len(actual)==len(e[key])
  for a,b in zip(actual,e[key]):av.assert_item(a,b)
 # Preserve all exact live properties from the successful AV application,
 # except the four explicitly logged final gain adjustments.
 for key,kind,idx in [('video','video',1),('audio_A1','audio',1),('audio_A3','audio',3)]:
  expected=copy.deepcopy(applied[ep]['after_targets'][key])
  for q in expected:
   if ep==22 and idx==1 and kind=='audio' and q['start']==1098:q['properties']['AudioVolume']=0.17
   if ep==25 and idx==1 and kind=='audio' and q['start']==625:q['properties']['AudioVolume']=0.39
   if ep==21 and idx==3 and q['start'] in (432,566):q['properties']['AudioVolume']=-15
  for a,b in zip(tracks[kind][idx-1]['items'],expected):same_props(a['properties'],b['properties'])
 av.verify_coverage(e)
 a2=tracks['audio'][1]['items'];expected=read(f'EP{ep}_原生110旁白实读.json');assert len(a2)==len(expected)
 for a,b in zip(a2,expected):
  b=copy.deepcopy(b)
  special=ep==22 and b['start']==484
  if special:b['source_start']=244
  assert (a['name'],a['start'],a['end'],a['source_start'],a['source_end'])==(b['name'],b['start'],b['end'],b['source_start'],b['source_end']),(ep,a,b)
  if not special:assert a['source_path']==b['path']
  else:
   mi=next(i.GetMediaPoolItem() for i in t.GetItemListInTrack('audio',2) if i.GetStart()==484)
   assert mi.GetClipProperty('Type')=='复合' and mi.GetClipProperty('File Name')=='女版22-2.mp3'
  same_props(a['properties'],b['properties'])
 s1=tracks['subtitle'][0]['items'];assert len(s1)==len(captions[ep]['cues'])
 for a,b in zip(s1,captions[ep]['cues']):assert (a['name'],a['start'],a['end'])==(b['text'],b['start'],b['end'])
 a4=t.GetItemListInTrack('audio',4);assert len(a4)==len(music[ep]['cues'])
 for a,b in zip(a4,music[ep]['cues']):
  assert (a.GetStart(),a.GetEnd(),a.GetDuration(),a.GetSourceStartFrame())==(b['record_frame'],b['record_frame']+b['duration_frames'],b['duration_frames'],0)
  # Audio-only source frame getters can use a media timebase distinct from
  # the timeline. Verify exact WAV sample length and native record duration.
  assert wav_seconds(b['path'])==Fraction(b['duration_frames'],24)
  assert av.media_path(a)==b['path']
  assert av.props(a)['AudioVolume']==0
  assert hashlib.sha256(Path(b['path']).read_bytes()).hexdigest()==b['sha256']
 drt=out/f'EP{ep}_旁白110精修_{stage}_{run_id}.drt';xml=out/f'EP{ep}_旁白110精修_{stage}_{run_id}.fcpxml'
 assert t.Export(str(drt),r.EXPORT_DRT)
 assert t.Export(str(xml),r.EXPORT_FCPXML_1_10)
 root=ET.parse(xml/'Info.fcpxml').getroot();maps=root.findall('.//timeMap');slopes=[]
 for tm in maps:
  pts=tm.findall('timept');assert len(pts)==2
  def f(x):return Fraction(x.rstrip('s'))
  slope=(f(pts[1].get('value'))-f(pts[0].get('value')))/(f(pts[1].get('time'))-f(pts[0].get('time')))
  slopes.append(float(slope));assert abs(float(slope)-1.1)<1e-5
 assert len(maps)==len(a2),(ep,'native retime count',len(maps),len(a2))
 # The one compound is an editable source wrapper; verify its original MP3 resource.
 if ep==22:
  assets=[a.get('src','') for a in root.findall('.//media-rep')]
  from urllib.parse import unquote
  assert any('独白/EP22/女版22-2.mp3' in unquote(a) for a in assets)
 q={'episode':ep,'timeline':t.GetName(),'duration_frames':t.GetEndFrame(),'tracks':tracks,'native110_piece_count':len(a2),'native110_slopes':slopes,'subtitle_count':len(s1),'subtitle_style_hash':style_hash(drt),'exports':[str(drt),str(xml)]}
 report['episodes'].append(q)
 for k,n in [('A1',len(tracks['audio'][0]['items'])),('A2',len(a2)),('S1',len(s1)),('A4',len(a4))]:totals[k]+=n
 print(json.dumps({'episode':ep,'frames':t.GetEndFrame(),'A1':len(tracks['audio'][0]['items']),'A2':len(a2),'subtitles':len(s1),'A4':len(a4),'style_hash':q['subtitle_style_hash']},ensure_ascii=False),flush=True)
for base in snap['timelines']:
 t=ts[base['name']];assert p.SetCurrentTimeline(t)
 assert (t.GetStartFrame(),t.GetEndFrame())==(base['start'],base['end'])
 tracks=av.snapshot_tracks(t)
 for kind in tracks:
  for a,b in zip(tracks[kind],base['tracks'][kind]):
   assert (a['name'],a['enabled'],a['locked'])==(b['name'],b['enabled'],b['locked'])
   assert len(a['items'])==len(b['items'])
   for x,y in zip(a['items'],b['items']):
    for k in ['id','name','start','end','duration','source_start','source_end','source_path','enabled','fusion_count']:assert x[k]==y[k],(base['name'],k,x[k],y[k])
    same_props(x['properties'],y['properties'])
 report['originals_unchanged'].append(base['name'])
assert totals=={'A1':44,'A2':31,'S1':152,'A4':12},totals
hashes={e['subtitle_style_hash'] for e in report['episodes']};report['subtitle_style_hashes']=list(hashes)
report['totals']=totals;report['passed']=True
(out/f'最终核验_{stage}.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
assert p.SetCurrentTimeline(ts['大码_女版_EP21_精修_旁白110_v2'])
print('FINAL_VERIFY_PASSED',stage,totals,flush=True)
