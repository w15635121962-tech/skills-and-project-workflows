"""Move only the playhead through the public Resolve SDK; CUA edits captions."""
import json,time,sys
from pathlib import Path
sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
OUT=Path(__file__).resolve().parent
plan=json.loads((OUT/'字幕110逐条原生修正计划.json').read_text())
r=get_resolve();p=r.GetProjectManager().GetCurrentProject();last=None
def tc(fr):return f'{fr//86400:02}:{fr//1440%60:02}:{fr//24%60:02}:{fr%24:02}'
print('PUBLIC_API_POSITION_BROKER_READY',flush=True)
while True:
 try:
  req=json.loads((OUT/'caption_position_request.json').read_text())
  if req.get('stop'):break
  if req['token']!=last:
   e=next(e for e in plan['episodes'] if e['episode']==req['episode']);c=e['cues'][req['ordinal']]
   t=p.GetCurrentTimeline();assert t.GetName()==e['prep'],t.GetName()
   assert t.SetCurrentTimecode(tc((c['old_start']+c['old_end'])//2))
   last=req['token'];(OUT/'caption_position_response.json').write_text(json.dumps({'token':last,'ok':True}))
 except FileNotFoundError:pass
 except Exception as exc:
  (OUT/'caption_position_response.json').write_text(json.dumps({'token':req.get('token'),'ok':False,'error':str(exc)}));last=req.get('token')
 time.sleep(.05)
