from common_v15 import *
import zipfile,re
r,pm,p,mp,t=connect()
source=OUT/'duration_probe.drt';target=OUT/'native_full_duration_overlay_v15.drt'
changed=0
with zipfile.ZipFile(source) as src,zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as dst:
 for item in src.infolist():
  data=src.read(item.filename)
  if item.filename.startswith('SeqContainer/'):
   text=data.decode('utf8');text,n=re.subn(r'(<Name>角标透明占位.png</Name>\s*<Start>0</Start>\s*<Duration>)125(</Duration>)',r'\g<1>11507\2',text);changed+=n;data=text.encode('utf8')
  dst.writestr(item,data)
assert changed==1,changed
assert t.SetName('学校_v15_角标长度测试保留')
new=mp.ImportTimelineFromFile(str(target),{'timelineName':TIMELINE});assert new
assert new.SetName(TIMELINE);assert p.SetCurrentTimeline(new)
a=json.loads((OUT/'live_before_v15.json').read_text());b=snap(new)
assert b['audio']==a['audio'];assert b['video'][:4]==a['video'];assert len(b['video'])==5
assert b['video'][4]['items'][0]['start']==0 and b['video'][4]['items'][0]['end']==11507,b['video'][4]
assert graphs(new)[:-1]==json.loads((OUT/'live_graphs_before_v15.json').read_text())
(OUT/'full_length_roundtrip_qa.json').write_text(json.dumps({'original_tracks_and_audio_exact':True,'overlay_track':b['video'][4]},ensure_ascii=False,indent=2))
assert pm.SaveProject();print('native still overlay full duration',b['video'][4]['items'][0]['end'])
