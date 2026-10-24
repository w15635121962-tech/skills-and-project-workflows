import sys,subprocess,json
from pathlib import Path
name=sys.argv[1];assert name in ['将所选字幕插入到…','使用时间码的时间线','九州海外短剧 Preset 字幕 Preset','加载预设']
s='''with timeout of 5 seconds
tell application "System Events"
tell (first application process whose bundle identifier is "com.blackmagic-design.DaVinciResolve")
repeat with wi from 1 to count of windows
if name of window wi is "" then
repeat with ci from 1 to count of UI elements of first UI element of window wi
if name of UI element ci of first UI element of window wi is "NAME" then
set xy to position of UI element ci of first UI element of window wi
set wh to size of UI element ci of first UI element of window wi
return {(item 1 of xy)+(item 1 of wh)/2, (item 2 of xy)+(item 2 of wh)/2}
end if
end repeat
end if
end repeat
error "Exact menu item not visible"
end tell
end tell
end timeout'''.replace('NAME',name)
xy=subprocess.check_output(['osascript','-e',s],text=True).strip();p=[float(x.strip()) for x in xy.split(',')];assert len(p)==2
out=subprocess.check_output(['osascript','-l','JavaScript',str(Path(__file__).with_name('native_left_click.js')),*map(str,p)],text=True)
print(json.dumps({'clicked_exact_visible_menu':name,'point':p,'result':out.strip()},ensure_ascii=False))
