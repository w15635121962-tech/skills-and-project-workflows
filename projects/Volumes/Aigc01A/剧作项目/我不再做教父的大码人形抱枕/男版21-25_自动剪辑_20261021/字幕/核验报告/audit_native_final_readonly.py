"""Audit persisted native captions and frozen AV. No Resolve mutations or UI switches.

Default: validate local inputs only, without even importing the Resolve bootstrap.
Connect only after the parent has saved/reopened the project, using:
  python audit_native_final_readonly.py --run-after-save-reopen
"""
import argparse
import datetime
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import sys

REPORT_DIR = Path(__file__).resolve().parent
SUB_DIR = REPORT_DIR.parent
EXPECTED_COUNTS = {21: 35, 22: 39, 23: 31, 24: 31, 25: 61}
FPS = 24


def sha(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':')).encode('utf-8')).hexdigest()


def clean_text(value):
    return value.replace('\u2028', '\n').replace('\r\n', '\n').replace('\r', '\n').strip()


def tc_frame(value):
    match = re.fullmatch(r'(\d+):(\d{2}):(\d{2}),(\d{3})', value)
    if not match:
        raise ValueError(f'Invalid SRT time: {value!r}')
    hour, minute, second, ms = map(int, match.groups())
    if minute >= 60 or second >= 60:
        raise ValueError(f'Invalid SRT time: {value!r}')
    millis = ((hour * 60 + minute) * 60 + second) * 1000 + ms
    return round(Fraction(millis * FPS, 1000))


def parse_srt(path):
    content = path.read_text(encoding='utf-8-sig').replace('\r\n', '\n').replace('\r', '\n').strip()
    rows = []
    for block in re.split(r'\n\s*\n', content):
        lines = block.splitlines()
        if len(lines) < 3:
            raise ValueError(f'Invalid SRT block in {path}: {block!r}')
        number = int(lines[0])
        a, b = lines[1].split(' --> ')
        text = clean_text('\n'.join(lines[2:]))
        row = {'number': number, 'start': tc_frame(a), 'end': tc_frame(b), 'text': text}
        if number != len(rows) + 1 or not text or row['start'] >= row['end']:
            raise ValueError(f'Invalid cue {number} in {path}')
        if len(text.splitlines()) > 3:
            raise ValueError(f'More than three explicit lines: {path.name} cue {number}')
        if rows and row['start'] < rows[-1]['end']:
            raise ValueError(f'Overlapping SRT cues: {path.name} cue {number}')
        rows.append(row)
    return rows


def diff_values(expected, actual, path=''):
    """Exact value comparison, keeping every AV property/key and source boundary."""
    out = []
    if isinstance(expected, dict) and isinstance(actual, dict):
        for key in sorted(set(expected) | set(actual)):
            at = f'{path}.{key}' if path else str(key)
            if key not in expected:
                out.append({'path': at, 'kind': 'unexpected_key', 'actual': actual[key]})
            elif key not in actual:
                out.append({'path': at, 'kind': 'missing_key', 'expected': expected[key]})
            else:
                out.extend(diff_values(expected[key], actual[key], at))
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            out.append({'path': path, 'kind': 'length', 'expected': len(expected), 'actual': len(actual)})
        for index, (a, b) in enumerate(zip(expected, actual)):
            out.extend(diff_values(a, b, f'{path}[{index}]'))
    elif expected != actual:
        out.append({'path': path, 'kind': 'value', 'expected': expected, 'actual': actual})
    return out


def av_item(item):
    media = item.GetMediaPoolItem()
    return {'id': item.GetUniqueId(), 'name': item.GetName(),
            'start': item.GetStart(True), 'end': item.GetEnd(True),
            'duration': item.GetDuration(True),
            'source_start': item.GetSourceStartFrame(), 'source_end': item.GetSourceEndFrame(),
            'source_start_seconds': item.GetSourceStartTime(),
            'source_end_seconds': item.GetSourceEndTime(),
            'source_path': media.GetClipProperty('File Path') if media else None,
            'enabled': item.GetClipEnabled(), 'speed': item.GetSpeed(),
            'linked_ids': sorted(x.GetUniqueId() for x in item.GetLinkedItems() or []),
            'properties': item.GetProperties()}


def read_av(timeline, episode):
    row = {'episode': episode, 'id': timeline.GetUniqueId(), 'name': timeline.GetName(),
           'start': timeline.GetStartFrame(), 'end': timeline.GetEndFrame(),
           'start_timecode': timeline.GetStartTimecode(), 'tracks': {}}
    handles = {}
    for kind in ('video', 'audio'):
        row['tracks'][kind] = []
        for index in range(1, timeline.GetTrackCount(kind) + 1):
            items = timeline.GetItemListInTrack(kind, index) or []
            handles.update({x.GetUniqueId(): x for x in items})
            row['tracks'][kind].append({
                'index': index, 'name': timeline.GetTrackName(kind, index),
                'enabled': timeline.GetIsTrackEnabled(kind, index),
                'locked': timeline.GetIsTrackLocked(kind, index),
                'items': [av_item(x) for x in items]})
    return row, handles


def current_context(resolve, project):
    current = project.GetCurrentTimeline()
    return {'project': project.GetName(), 'page': resolve.GetCurrentPage(),
            'timeline_id': current.GetUniqueId() if current else None,
            'timeline_name': current.GetName() if current else None,
            'timecode': current.GetCurrentTimecode() if current else None}


def load_local_inputs():
    contract = json.loads((SUB_DIR / 'Resolve_AV冻结对照.json').read_text(encoding='utf-8'))
    full = json.loads((SUB_DIR / 'Resolve_字幕操作前完整基线.json').read_text(encoding='utf-8'))
    assert contract['project'] == full['project'] == '大码枕头'
    assert sorted(e['episode'] for e in contract['episodes']) == list(EXPECTED_COUNTS)
    cues = {}
    for ep in EXPECTED_COUNTS:
        cues[ep] = parse_srt(SUB_DIR / f'EP{ep}.srt')
        assert len(cues[ep]) == EXPECTED_COUNTS[ep], (ep, len(cues[ep]))
    return contract, full, cues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-after-save-reopen', action='store_true',
                        help='Parent has completed Save/Reopen; permit read-only Resolve connection.')
    args = parser.parse_args()
    contract, full, cues = load_local_inputs()
    if not args.run_after_save_reopen:
        print(json.dumps({'status': 'READY_NOT_CONNECTED', 'local_srt_counts': EXPECTED_COUNTS,
                          'total': sum(EXPECTED_COUNTS.values()),
                          'next': 'Wait for parent Save/Reopen notice; then add --run-after-save-reopen.'},
                         ensure_ascii=False, indent=2))
        return 0

    # Never connect before the explicit execution flag is supplied.
    sys.path.insert(0, '/Users/zc/.codex/skills/davinci-resolve/scripts')
    from resolve_bootstrap import get_resolve
    resolve = get_resolve()
    project = resolve.GetProjectManager().GetCurrentProject()
    assert project and project.GetName() == '大码枕头', 'Wrong project; abort read-only audit'
    before_context = current_context(resolve, project)
    timelines = {project.GetTimelineByIndex(i).GetUniqueId(): project.GetTimelineByIndex(i)
                 for i in range(1, project.GetTimelineCount() + 1)}
    report = {'checked_at': datetime.datetime.now().isoformat(), 'project': project.GetName(),
              'version': resolve.GetVersionString(), 'scope': 'Read-only; no Save, UI, timeline/page switch, or mutations.',
              'parent_reported_saved_and_reopened': True,
              'context_before': before_context, 'episodes': [],
              'style_scope': 'Track preset visibility/playback remains parent visual evidence; no undocumented style API guessed.'}
    snapshots = []
    full_by_ep = {e['episode']: e for e in full['episodes']}
    for expected in contract['episodes']:
        ep = expected['episode']
        timeline = timelines[expected['id']]
        actual, handles = read_av(timeline, ep)
        differences = diff_values({k: v for k, v in expected.items() if k != 'sha256'}, actual)
        offsets_differences = []
        extra_source_state = []
        for kind in ('video', 'audio'):
            for track in full_by_ep[ep]['tracks'][kind]:
                for old in track['items']:
                    item = handles.get(old['id'])
                    if item is None:
                        offsets_differences.append({'id': old['id'], 'kind': 'missing_item'})
                        continue
                    media = item.GetMediaPoolItem()
                    old_extra = {k: old[k] for k in ('left_offset', 'right_offset', 'media_pool_id')}
                    new_extra = {'left_offset': item.GetLeftOffset(True),
                                 'right_offset': item.GetRightOffset(True),
                                 'media_pool_id': media.GetUniqueId() if media else None}
                    offsets_differences.extend(diff_values(old_extra, new_extra, old['id']))
                    extra_source_state.append({'id': old['id'], **new_extra})
        tracks = []
        for index in range(1, timeline.GetTrackCount('subtitle') + 1):
            tracks.append({'index': index, 'name': timeline.GetTrackName('subtitle', index),
                           'enabled': timeline.GetIsTrackEnabled('subtitle', index),
                           'locked': timeline.GetIsTrackLocked('subtitle', index),
                           'items': [{'id': x.GetUniqueId(), 'start': x.GetStart(True),
                                      'end': x.GetEnd(True), 'text': clean_text(x.GetName()),
                                      'enabled': x.GetClipEnabled()} for x in
                                     timeline.GetItemListInTrack('subtitle', index) or []]})
        native = tracks[0]['items'] if len(tracks) == 1 else []
        native_cues = [{'number': i + 1, 'start': x['start'], 'end': x['end'], 'text': x['text']}
                      for i, x in enumerate(native)]
        caption_differences = diff_values(cues[ep], native_cues)
        subtitle_track_ok = (len(tracks) == 1 and tracks[0]['name'] == str(ep) and tracks[0]['enabled'])
        caption_lines = [len(x['text'].splitlines()) for x in native]
        subtitles_in_range = all(timeline.GetStartFrame() <= x['start'] < x['end'] <= timeline.GetEndFrame()
                                 for x in native)
        expected_srt = SUB_DIR / f'EP{ep}.srt'
        observed = {'episode': ep, 'timeline': timeline.GetName(), 'timeline_id': timeline.GetUniqueId(),
                    'fps': float(timeline.GetSettings()['timelineFrameRate']),
                    'video_clips': sum(len(t['items']) for t in actual['tracks']['video']),
                    'audio_clips': sum(len(t['items']) for t in actual['tracks']['audio']),
                    'av_sha256_before': expected['sha256'], 'av_sha256_now': sha(actual),
                    'av_all_fields_exact': not differences, 'av_differences': differences,
                    'source_offsets_and_pool_ids_exact': not offsets_differences,
                    'source_extra_differences': offsets_differences,
                    'subtitle_track_count': len(tracks),
                    'subtitle_track_name': tracks[0]['name'] if len(tracks) == 1 else None,
                    'subtitle_track_ok': subtitle_track_ok, 'expected_cues': EXPECTED_COUNTS[ep],
                    'actual_cues': len(native), 'text_and_frame_times_exact': not caption_differences,
                    'subtitle_differences': caption_differences,
                    'all_subtitle_clips_enabled': all(x['enabled'] for x in native),
                    'subtitles_within_timeline': subtitles_in_range,
                    'max_explicit_lines': max(caption_lines, default=0),
                    'explicit_three_line_cues': [i + 1 for i, n in enumerate(caption_lines) if n == 3],
                    'srt': str(expected_srt),
                    'srt_sha256': hashlib.sha256(expected_srt.read_bytes()).hexdigest()}
        observed['passed'] = (not differences and not offsets_differences and not caption_differences
                              and subtitle_track_ok and len(native) == EXPECTED_COUNTS[ep]
                              and all(x['enabled'] for x in native) and subtitles_in_range
                              and max(caption_lines, default=0) <= 3 and observed['fps'] == FPS)
        report['episodes'].append(observed)
        snapshots.append({'episode': ep, 'av': actual, 'av_extra_source_state': extra_source_state,
                          'subtitle_tracks': tracks})
    report['context_after'] = current_context(resolve, project)
    report['context_unchanged'] = report['context_after'] == before_context
    report['total_native_cues'] = sum(e['actual_cues'] for e in report['episodes'])
    report['all_passed'] = (all(e['passed'] for e in report['episodes'])
                            and report['context_unchanged'] and report['total_native_cues'] == 197)
    (REPORT_DIR / 'Resolve_字幕保存重开_原生实读.json').write_text(
        json.dumps(snapshots, ensure_ascii=False, indent=2), encoding='utf-8')
    report_path = REPORT_DIR / 'Resolve_字幕保存重开_最终审计.json'
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'report': str(report_path), 'all_passed': report['all_passed'],
                      'total_native_cues': report['total_native_cues'],
                      'context_unchanged': report['context_unchanged'],
                      'episodes': [{k: e[k] for k in ('episode', 'passed', 'av_all_fields_exact',
                                   'source_offsets_and_pool_ids_exact', 'actual_cues',
                                   'text_and_frame_times_exact', 'subtitle_track_name',
                                   'max_explicit_lines')} for e in report['episodes']]},
                     ensure_ascii=False, indent=2), flush=True)
    return 0 if report['all_passed'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
