"""Load the exact native subtitle Track preset through verified physical clicks.

Precondition: the current episode's ST header and Inspector Track tab are selected.
This uses the user's explicit AppleScript/JXA/CGEvent authorization.
"""
import argparse
import datetime
import json
from pathlib import Path
import re
import subprocess
import sys
import time

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
PRESET = '九州海外短剧 Preset 字幕 Preset'
CLICK = Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕/自动剪辑_女版16-19_21-26_28_20261020/准备/native_left_click.js')
sys.path.insert(0, '/Users/zc/.codex/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve

def osa(body):
    return subprocess.check_output(['osascript', '-e', body], text=True, encoding='utf-8', stderr=subprocess.PIPE).strip()

APP = '''tell application "System Events"
tell (first application process whose bundle identifier is "com.blackmagic-design.DaVinciResolve")
'''
END = '\nend tell\nend tell'

def click_point(raw):
    parts = re.fullmatch(r'(-?\d+(?:\.\d+)?),\s*(-?\d+(?:\.\d+)?)', raw)
    if not parts:
        raise RuntimeError('Unexpected live UI coordinates: ' + raw)
    point = [float(parts[1]), float(parts[2])]
    subprocess.run(['osascript', '-l', 'JavaScript', str(CLICK), *map(str, point)],
                   check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(.12)
    return point

def visible_menu_point(name):
    code = APP + '''repeat with wi from 1 to count of windows
if name of window wi is "" then
repeat with ci from 1 to count of UI elements of first UI element of window wi
if name of UI element ci of first UI element of window wi is "''' + name + '''" then
set xy to position of UI element ci of first UI element of window wi
set wh to size of UI element ci of first UI element of window wi
return {(item 1 of xy)+(item 1 of wh)/2, (item 2 of xy)+(item 2 of wh)/2}
end if
end repeat
end if
end repeat
error "Exact native menu item not visible"
''' + END
    for attempt in range(5):
        try:
            return osa(code)
        except subprocess.CalledProcessError:
            if attempt == 4:
                raise
            time.sleep(.1)

def style():
    raw = osa(APP + '''set episodeHeader to name of static text 1 of group 1 of window "大码枕头"
if value of checkbox 2 of group 1 of window "大码枕头" is not 1 then error "Top Track context is not selected"
if value of checkbox 2 of group 2 of group 1 of window "大码枕头" is not 1 then error "Subtitle Track style tab is not selected"
tell group 1 of group 2 of group 1 of window "大码枕头"
set outText to episodeHeader & linefeed & (name of combo box 1) & linefeed & (name of combo box 2) & linefeed
set fieldNames to get name of every static text
repeat with v in fieldNames
if contents of v is not missing value then set outText to outText & (contents of v as text) & tab
end repeat
set outText to outText & linefeed
set checkValues to get value of every checkbox
repeat with v in checkValues
if contents of v is not missing value then set outText to outText & (contents of v as text) & tab
end repeat
return outText
end tell''' + END)
    lines = raw.splitlines()
    return {'episode_header': lines[0], 'font': lines[1], 'weight': lines[2],
            'text_fields': lines[3].split('\t'),
            'checkbox_values': lines[4].split('\t') if len(lines) > 4 else []}

def cues(t):
    return [[int(c.GetStart()), int(c.GetEnd()), c.GetName()] for c in t.GetItemListInTrack('subtitle', 1)]

def av(t):
    return {kind: [[t.GetTrackName(kind, n), [[c.GetName(), int(c.GetStart()), int(c.GetEnd()),
                                             c.GetLeftOffset(), c.GetRightOffset()]
                                            for c in (t.GetItemListInTrack(kind, n) or [])]]
                   for n in range(1, t.GetTrackCount(kind) + 1)]
            for kind in ('video', 'audio')}

parser = argparse.ArgumentParser()
parser.add_argument('episode', type=int)
args = parser.parse_args()
manifest = json.loads((BASE / '字幕导入清单.json').read_text(encoding='utf-8'))
row = next(x for x in manifest if x['ep'] == args.episode)
r = get_resolve()
pm = r.GetProjectManager()
p = pm.GetCurrentProject()
assert p.GetName() == '大码枕头'
t = p.GetCurrentTimeline()
assert (t.GetUniqueId(), t.GetName()) == (row['timeline_id'], row['timeline'])
assert t.GetTrackCount('subtitle') == 1 and t.GetTrackName('subtitle', 1) == str(args.episode)
before_cues, before_av, before_style = cues(t), av(t), style()
assert before_style['episode_header'] == str(args.episode)
assert len(before_cues) == row['cue_count'], (len(before_cues), row)
osa('tell application id "com.blackmagic-design.DaVinciResolve" to activate')
time.sleep(.25)
button = osa(APP + '''set xy to position of first menu button of group 1 of window "大码枕头"
set wh to size of first menu button of group 1 of window "大码枕头"
return {(item 1 of xy)+(item 1 of wh)/2, (item 2 of xy)+(item 2 of wh)/2}''' + END)
points = [click_point(button)]
points.append(click_point(visible_menu_point(PRESET)))
points.append(click_point(visible_menu_point('加载预设')))
after_style = style()
assert after_style['episode_header'] == str(args.episode)
assert after_style['font'] == 'Noto Sans' and after_style['weight'] == 'SemiBold'
assert '40' in after_style['text_fields']
assert cues(t) == before_cues and av(t) == before_av
assert pm.SaveProject()
report = {'ep': args.episode, 'timeline': t.GetName(), 'timeline_id': t.GetUniqueId(),
          'preset': PRESET, 'native_load_clicked': True, 'click_points_from_current_ax': points,
          'before_style': before_style, 'after_style': after_style,
          'cue_count': len(before_cues), 'cues_unchanged': True, 'av_unchanged': True,
          'save_returned_true': True, 'saved_at': datetime.datetime.now().isoformat()}
out = BASE / '预设操作记录'
out.mkdir(exist_ok=True)
(out / f'EP{args.episode}.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'ep': args.episode, 'loaded': True, 'font': after_style['font'],
                  'weight': after_style['weight'], 'cue_count': len(before_cues),
                  'cues_unchanged': True, 'av_unchanged': True}, ensure_ascii=False))
