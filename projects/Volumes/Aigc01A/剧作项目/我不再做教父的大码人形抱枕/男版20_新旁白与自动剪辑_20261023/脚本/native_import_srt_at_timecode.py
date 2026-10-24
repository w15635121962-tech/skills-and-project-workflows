from pathlib import Path
import subprocess,json,time,sys
from native_common import *
from insert_srt import parse_srt,native_cues
r,m,p,pool=connect();row=read(BASE/'Resolve_组装实读.json')['episodes'][0];t=p.GetCurrentTimeline();assert t.GetUniqueId()==row['id'] and not native_cues(t) and t.GetTrackCount('subtitle')==1
assert t.GetEndFrame()==1594;before=av(t)
subprocess.run(['osascript','-e','tell application id "com.blackmagic-design.DaVinciResolve" to activate'],check=True)
subprocess.run(['osascript','-l','JavaScript',str(Path(__file__).with_name('native_right_click.js')),'378','164'],check=True,capture_output=True,text=True)
trace=[]
for name in ['将所选字幕插入到…','使用时间码的时间线']:
 result=None
 for trial in range(5):
  q=subprocess.run([sys.executable,str(Path(__file__).with_name('click_visible_native_menu.py')),name],capture_output=True,text=True)
  if q.returncode==0:result=json.loads(q.stdout);break
  time.sleep(.1)
 assert result,('Native exact menu unavailable',name,q.stderr)
 trace.append(result)
write(BASE/'字幕/原生菜单按时间码点击记录.json',{'timeline_id':t.GetUniqueId(),'steps':trace})
now=native_cues(t);expected=parse_srt(BASE/'字幕/EP20.srt')
write(BASE/'字幕/原生菜单导入后即时回读.json',{'expected':expected,'actual':now,'count':len(now),'matches':now==expected})
assert now==expected and av(t)==before and t.GetEndFrame()==1594
assert m.SaveProject();print(json.dumps({'native_menu_imported':len(now),'exact_source_frame_times':True,'av_unchanged':True},ensure_ascii=False))
