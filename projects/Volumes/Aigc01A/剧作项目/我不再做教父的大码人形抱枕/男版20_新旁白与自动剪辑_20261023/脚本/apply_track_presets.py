"""Authorized native preset clicks, guarded by NEW screenshot/AX geometry evidence.

No old ST coordinates are embedded or accepted as defaults. Write a fresh geometry
JSON after inspecting the current Resolve screenshot and AX. The authorized EP20 SRT must
already match their native tracks before this script performs any UI operation.
"""
import argparse
import datetime
import json
from pathlib import Path
import re
import subprocess
import sys
import time
sys.path.insert(0, str(Path(__file__).resolve().parent))
from native_common import BASE, EPISODES, connect, read as read_json, sha as sha256, timelines, write as write_json, assert_baseline
OUTPUT_DIR=BASE
from insert_srt import parse_srt

PRESET = '九州海外短剧 Preset 字幕 Preset'
CLICK = Path(__file__).resolve().parent / 'native_left_click.js'
APP = 'tell application "System Events"\ntell (first application process whose bundle identifier is "com.blackmagic-design.DaVinciResolve")\n'
END = '\nend tell\nend tell'


def osa(body):
    return subprocess.check_output(['osascript', '-e', body], text=True, encoding='utf-8', stderr=subprocess.PIPE).strip()


def numbers(text):
    assert re.fullmatch(r'\s*-?\d+(?:\.\d+)?(?:,\s*-?\d+(?:\.\d+)?)+\s*', text), text
    return [float(value.strip()) for value in text.split(',')]


def real_click(point):
    assert len(point) == 2
    subprocess.run(['osascript', '-l', 'JavaScript', str(CLICK), *map(str, point)],
                   check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(.18)
    return point


def live_window_bounds():
    return numbers(osa(APP + '''tell window "大码枕头"
set xy to position
set wh to size
return {(item 1 of xy), (item 2 of xy), (item 1 of wh), (item 2 of wh)}
end tell''' + END))


def exact_menu_point(name):
    assert name in [PRESET, '加载预设']
    body = APP + '''repeat with wi from 1 to count of windows
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
            return numbers(osa(body))
        except subprocess.CalledProcessError:
            if attempt == 4:
                raise
            time.sleep(.12)


def style():
    raw = osa(APP + '''set headerText to name of static text 1 of group 1 of window "大码枕头"
if value of checkbox 2 of group 1 of window "大码枕头" is not 1 then error "Top Track context not selected"
if value of checkbox 2 of group 2 of group 1 of window "大码枕头" is not 1 then error "Inner Track style context not selected"
tell group 1 of group 2 of group 1 of window "大码枕头"
set outText to headerText & linefeed & (name of combo box 1) & linefeed & (name of combo box 2) & linefeed
repeat with v in (get name of every static text)
if contents of v is not missing value then set outText to outText & (contents of v as text) & tab
end repeat
set outText to outText & linefeed
repeat with v in (get value of every checkbox)
if contents of v is not missing value then set outText to outText & (contents of v as text) & tab
end repeat
return outText
end tell''' + END)
    lines = raw.splitlines()
    assert len(lines) >= 4
    return {'episode_header': lines[0], 'font': lines[1], 'weight': lines[2],
            'text_fields': lines[3].split('\t'), 'checkboxes': lines[4].split('\t') if len(lines) > 4 else []}


def native_cues(timeline):
    return [[int(x.GetStart()), int(x.GetEnd()), x.GetName().replace('\u2028', '\n').replace('\r\n', '\n').strip()]
            for x in timeline.GetItemListInTrack('subtitle', 1) or []]


def av(timeline):
    return {kind: [[timeline.GetTrackName(kind, index),
                    [[x.GetUniqueId(), x.GetStart(), x.GetEnd(), x.GetSourceStartFrame(), x.GetSourceEndFrame(),
                      x.GetMediaPoolItem().GetClipProperty('File Path'), x.GetClipEnabled(),
                      x.GetProperties().get('AudioVolume'), sorted(y.GetUniqueId() for y in x.GetLinkedItems() or [])]
                     for x in timeline.GetItemListInTrack(kind, index) or []]]
                   for index in range(1, timeline.GetTrackCount(kind) + 1)] for kind in ['video', 'audio']}


def validate_geometry(path):
    geometry = read_json(path)
    assert geometry['verified_from_current_screenshot'] is True
    assert geometry['verified_from_current_ax'] is True
    assert geometry['inspector_ax_group_paths_verified'] is True, 'Re-check inspector AX paths from current UI before use'
    screenshot = Path(geometry['screenshot_path'])
    assert screenshot.is_file() and sha256(screenshot) == geometry['screenshot_sha256']
    observed = datetime.datetime.fromisoformat(geometry['observed_at_utc'].replace('Z', '+00:00'))
    assert observed.tzinfo is not None
    age = (datetime.datetime.now(datetime.timezone.utc) - observed).total_seconds()
    assert -30 <= age <= 1200, 'Screenshot/geometry stale: reobserve the current UI'
    assert len(geometry['window_bounds']) == 4 and len(geometry['st_blank_point']) == 2
    x, y, width, height = geometry['window_bounds']
    px, py = geometry['st_blank_point']
    assert x < px < x + width and y < py < y + height
    return geometry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--geometry', required=True)
    parser.add_argument('--episodes', type=int, nargs='+', default=sorted(EPISODES))
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--use-current-track-context', action='store_true', help='One episode only; preserve subtitle context selected from fresh CUA screenshot instead of reusing canvas coordinates')
    args = parser.parse_args()
    geometry = validate_geometry(args.geometry)
    if args.use_current_track_context:
        assert len(args.episodes) == 1, 'Current UI context can cover only one observed episode'
    assert set(args.episodes) <= EPISODES
    rows = read_json(OUTPUT_DIR / '字幕/SRT_原生入轨回读.json')
    assert {row['episode'] for row in rows} == EPISODES, 'Import the authorized EP20 SRT before loading any preset'
    if not args.execute:
        print('Fresh screenshot geometry and EP20-SRT report validated. No UI clicks or Resolve mutation.')
        return
    resolve, manager, project, pool = connect()
    assert_baseline(project)
    by_id = {t.GetUniqueId(): t for t in timelines(project)}
    # Read every imported caption set before making the first UI click.
    for row in rows:
        timeline = by_id[row['id']]
        assert timeline.GetName() == row['timeline']
        assert timeline.GetTrackCount('subtitle') == 1 and timeline.GetTrackName('subtitle', 1) == str(row['episode'])
        assert native_cues(timeline) == [list(x) for x in parse_srt(row['srt'])]
        assert len(native_cues(timeline)) == row['cue_count']
    assert resolve.OpenPage('edit')
    for row in sorted(rows, key=lambda x: x['episode']):
        if row['episode'] not in args.episodes:
            continue
        timeline = by_id[row['id']]
        assert project.SetCurrentTimeline(timeline)
        assert timeline.GetName() == row['timeline'] and project.GetCurrentTimeline().GetUniqueId() == row['id']
        osa('tell application id "com.blackmagic-design.DaVinciResolve" to activate')
        time.sleep(.25)
        assert live_window_bounds() == list(map(float, geometry['window_bounds'])), 'Window moved/resized: fresh screenshot required'
        before_av, before_cues = av(timeline), native_cues(timeline)
        # The point is supplied only from the just-verified current screenshot.
        points = [] if args.use_current_track_context else [real_click(geometry['st_blank_point'])]
        def live_control_point(expression):
            return numbers(osa(APP + "set xy to position of " + expression + "\nset wh to size of " + expression + "\nreturn {(item 1 of xy)+(item 1 of wh)/2, (item 2 of xy)+(item 2 of wh)/2}" + END))
        context = osa(APP + 'return name of static text 1 of group 1 of window "大码枕头"' + END)
        # Blank-track clicks can clear clip selection on Resolve21.1. Select a
        # currently visible caption only to establish subtitle context, then
        # explicitly activate the native Track controls using their LIVE AX bounds.
        # No subtitle text, times, AV media or existing preset is changed here.
        if context not in [str(row['episode']), 'Subtitle - 字幕'] and '字幕' not in context:
            assert not args.use_current_track_context, 'Fresh CUA selection is not a subtitle context'
            assert 'subtitle_clip_point' in geometry, 'Fresh visible-caption point required'
            points.append(real_click(geometry['subtitle_clip_point']))
        top = 'checkbox 2 of group 1 of window "大码枕头"'
        if osa(APP + 'return value of ' + top + END) != '1':
            points.append(real_click(live_control_point(top)))
        context = osa(APP + 'return name of static text 1 of group 1 of window "大码枕头"' + END)
        assert context == str(row['episode']), ('Wrong subtitle inspector context', context)
        inner = 'checkbox 2 of group 2 of group 1 of window "大码枕头"'
        if osa(APP + 'return value of ' + inner + END) != '1':
            points.append(real_click(live_control_point(inner)))
        assert osa(APP + 'return value of ' + inner + END) == '1'
        before_style = style()
        assert before_style['episode_header'] == str(row['episode'])
        point = numbers(osa(APP + '''set xy to position of first menu button of group 1 of window "大码枕头"
set wh to size of first menu button of group 1 of window "大码枕头"
return {(item 1 of xy)+(item 1 of wh)/2, (item 2 of xy)+(item 2 of wh)/2}''' + END))
        points.append(real_click(point))
        points.append(real_click(exact_menu_point(PRESET)))
        points.append(real_click(exact_menu_point('加载预设')))
        after_style = style()
        assert after_style['episode_header'] == str(row['episode'])
        assert after_style['font'] == 'Noto Sans' and after_style['weight'] == 'SemiBold'
        assert all(value in after_style['text_fields'] for value in ['40', '540.000', '575.000', '0.960'])
        assert av(timeline) == before_av and native_cues(timeline) == before_cues
        assert_baseline(project)
        assert manager.SaveProject()
        report = {'episode': row['episode'], 'timeline': timeline.GetName(), 'id': timeline.GetUniqueId(),
                  'preset': PRESET, 'native_load_clicked': True, 'click_points_from_fresh_geometry_and_live_ax': points,
                  'geometry_proof': str(Path(args.geometry).resolve()), 'screenshot_sha256': geometry['screenshot_sha256'],
                  'before_style': before_style, 'after_style': after_style, 'cue_count': len(before_cues),
                  'cue_text_and_times_unchanged': True, 'av_sources_bounds_gain_links_unchanged': True,
                  'save_returned_true': True, 'saved_at': datetime.datetime.now().isoformat(),
                  'preview_and_reopen_verification': 'PENDING_ROOT_PREVIEW_AND_VERIFY_SAVE_REOPEN'}
        write_json(OUTPUT_DIR / '字幕/预设操作记录' / ('EP%d.json' % row['episode']), report)
        print(json.dumps({'episode': row['episode'], 'preset_loaded': True, 'cue_count': len(before_cues),
                          'cue_and_av_unchanged': True}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
