#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read only: compare six live 30fps subtitle timelines with the approved plan.

No Resolve mutation, project/timeline/page selection, export, import or save call.
The only write is a new independent JSON verification record.
"""

from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re
import sys


HERE = Path(__file__).resolve().parent
BOOTSTRAP = Path('/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
STAMP = re.compile(r'^(\d{2,}):([0-5]\d):([0-5]\d),(\d{3})$')
WORDS = re.compile(r"[^\W_]+(?:['’][^\W_]+)*", re.UNICODE)
TOLERANCE = 1e-6


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def compact(text):
    return ' '.join(str(text).split())


def lexical(text):
    return [w.casefold().replace('’', "'") for w in WORDS.findall(text)]


def lines(text):
    return str(text).replace('\u2028', '\n').replace('\u2029', '\n').replace('\r\n', '\n').split('\n')


def time_ms(text):
    match = STAMP.fullmatch(text)
    if not match:
        raise ValueError(f'Invalid SRT timestamp {text!r}')
    h, m, s, ms = map(int, match.groups())
    return ((h * 60 + m) * 60 + s) * 1000 + ms


def parse_srt(path):
    text = Path(path).read_text(encoding='utf-8-sig').replace('\r\n', '\n')
    cues = []
    for i, block in enumerate(re.split(r'\n[ \t]*\n', text.strip()), 1):
        parts = block.split('\n')
        if len(parts) < 3 or parts[0] != str(i):
            raise ValueError(f'Invalid index/body in {path}, cue {i}')
        stamps = parts[1].split(' --> ')
        if len(stamps) != 2:
            raise ValueError(f'Invalid time line in {path}, cue {i}')
        start, end = map(time_ms, stamps)
        if end <= start or not compact(' '.join(parts[2:])):
            raise ValueError(f'Nonpositive/empty cue {i} in {path}')
        cues.append({'index': i, 'start_ms': start, 'end_ms': end, 'lines': parts[2:],
                     'text': compact(' '.join(parts[2:]))})
    return cues


def gui_state(resolve, project):
    timeline = project.GetCurrentTimeline()
    return {'page': resolve.GetCurrentPage(),
            'current_timeline_id': timeline.GetUniqueId() if timeline else None,
            'current_timecode': timeline.GetCurrentTimecode() if timeline else None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, default=HERE / '30fps竖屏字幕_落帧完成与校验.json')
    parser.add_argument('--snapshot', type=Path, default=HERE / '30fps竖屏实际时间线快照_修尾后.json')
    parser.add_argument('--output', type=Path, default=HERE / '30fps原生字幕最终独立只读核验.json')
    args = parser.parse_args()
    if args.output.exists():
        raise RuntimeError(f'Refusing to overwrite an existing QC record: {args.output}')
    plan, snapshot = load(args.plan), load(args.snapshot)
    binding_path = HERE / '30fps六时间线47复合源绑定速度及尾音核验_修尾后.json'
    binding = load(binding_path)
    expected_timelines = {t['id']: t for t in snapshot['timelines']}
    failures, timeline_rows, input_hashes = [], [], {}

    def check(ok, name, detail):
        if not ok:
            failures.append({'check': name, 'detail': detail})
        return bool(ok)

    for path in [args.plan, args.snapshot, binding_path]:
        input_hashes[str(path.resolve())] = sha(path)
    check(sha(args.snapshot) == plan['actual_snapshot_sha256'] == binding['snapshot_sha256'],
          'approved_repaired_snapshot_identity', str(args.snapshot))
    check(len(plan['timelines']) == len(expected_timelines) == 6, 'six_target_timelines', len(expected_timelines))
    check(binding['all_source_paths_hashes_and_linear_110_verified'] is True and binding['clip_count'] == 47,
          'prior_native_drt_binding_evidence_available', str(binding_path))

    # Use the bundled public API bootstrap. Importing this script never connects.
    sys.path.insert(0, str(BOOTSTRAP))
    from resolve_bootstrap import get_resolve
    resolve = get_resolve()
    manager = resolve.GetProjectManager()
    project = manager.GetCurrentProject() if manager else None
    if project is None or project.GetUniqueId() != snapshot['id']:
        raise RuntimeError('Expected project is not currently open; nothing was selected or changed.')
    before = gui_state(resolve, project)
    native = {}
    for index in range(1, int(project.GetTimelineCount()) + 1):
        timeline = project.GetTimelineByIndex(index)
        if timeline is not None:
            native[timeline.GetUniqueId()] = timeline

    all_audio_ids = []
    for target in plan['timelines']:
        tid = target['timeline_id']
        baseline = expected_timelines[tid]
        timeline = native.get(tid)
        if not check(timeline is not None, 'target_timeline_id_exists', tid):
            continue
        fps = float(timeline.GetSetting('timelineFrameRate'))
        width = int(timeline.GetSetting('timelineResolutionWidth'))
        height = int(timeline.GetSetting('timelineResolutionHeight'))
        start_frame, end_frame = float(timeline.GetStartFrame()), float(timeline.GetEndFrame())
        check((fps, width, height) == (30.0, 1080, 1920), 'native_30fps_1080x1920',
              {'timeline': tid, 'actual': [fps, width, height]})
        check(timeline.GetName() == baseline['name'] == target['timeline_name'], 'timeline_identity_name', tid)
        check(abs(start_frame - baseline['start_frame']) < TOLERANCE
              and abs(end_frame - baseline['end_frame']) < TOLERANCE, 'timeline_bounds_preserved', tid)
        srt_path = Path(target['srt_path'])
        input_hashes[str(srt_path)] = sha(srt_path)
        check(sha(srt_path) == target['srt_sha256'], 'approved_srt_hash', str(srt_path))
        srt = parse_srt(srt_path)
        expected_cues = target['cues']
        check(len(srt) == len(expected_cues) == target['cue_count'], 'planned_srt_cue_count', tid)

        # Verify complete sentences or two explicitly authored semantic halves.
        semantic = []
        cursor = 0
        while cursor < len(expected_cues):
            first = expected_cues[cursor]
            count = first['parts_in_sentence']
            group = expected_cues[cursor:cursor + count] if count in (1, 2) else []
            ok = count in (1, 2) and len(group) == count and first['part_in_sentence'] == 1
            ok = ok and all(c['parent_sentence'] == first['parent_sentence']
                            and c['audio_name'] == first['audio_name']
                            and c['part_in_sentence'] == j + 1
                            and c['parts_in_sentence'] == count for j, c in enumerate(group))
            ok = ok and lexical(' '.join(c['text'] for c in group)) == lexical(first['parent_sentence'])
            reason = 'complete_corrected_sentence' if count == 1 else 'explicit_semantic_clause_boundary'
            ok = ok and all(c['segmentation_reason'] == reason for c in group)
            check(ok, 'complete_sentence_or_two_explicit_halves', {'timeline': tid, 'cue': first['index']})
            semantic.append({'first_cue': first['index'], 'parts': count, 'passed': bool(ok)})
            cursor += count if count in (1, 2) else 1

        audio_rows = []
        expected_audio = [i for tr in baseline['audio_tracks'] for i in tr['items']]
        current_audio = []
        for track in range(1, int(timeline.GetTrackCount('audio')) + 1):
            for item in timeline.GetItemListInTrack('audio', track) or []:
                media = item.GetMediaPoolItem()
                properties = (media.GetClipProperty() or {}) if media else {}
                current_audio.append({'id': item.GetUniqueId(), 'name': item.GetName(), 'track': track,
                                      'start': float(item.GetStart(True)), 'end': float(item.GetEnd(True)),
                                      'duration': float(item.GetDuration(True)), 'left_offset': float(item.GetLeftOffset(True)),
                                      'source_path': properties.get('File Path', ''),
                                      'source_wrapper_type': properties.get('Type', ''),
                                      'media_pool_unique_id': media.GetUniqueId() if media else None})
        current_audio.sort(key=lambda a: (a['start'], a['track']))
        check([a['id'] for a in current_audio] == [a['id'] for a in expected_audio], 'all_audio_ids_order_and_count_preserved', tid)
        for expected, actual in zip(expected_audio, current_audio):
            unchanged = actual['id'] == expected['id'] and actual['name'] == expected['name']
            unchanged = unchanged and all(abs(actual[k] - float(expected[k])) < TOLERANCE for k in ('start', 'end', 'left_offset'))
            unchanged = unchanged and abs(actual['duration'] - (float(expected['end']) - float(expected['start']))) < TOLERANCE
            unchanged = unchanged and actual['source_path'] == expected['source_path'] and actual['source_wrapper_type'] == expected['source_wrapper_type']
            check(unchanged, 'audio_item_placement_duration_and_wrapper_preserved', {'timeline': tid, 'id': expected['id']})
            audio_rows.append({**actual, 'matches_repaired_snapshot': bool(unchanged),
                               'prior_drt_bound_original_mp3': expected['expected_original_mp3_path']})
        all_audio_ids.extend(a['id'] for a in current_audio)

        subtitle_tracks = []
        nonempty = []
        for index in range(1, int(timeline.GetTrackCount('subtitle')) + 1):
            items = timeline.GetItemListInTrack('subtitle', index) or []
            items.sort(key=lambda item: item.GetStart())
            row = {'index': index, 'name': timeline.GetTrackName('subtitle', index),
                   'enabled': timeline.GetIsTrackEnabled('subtitle', index),
                   'cues': [{'id': item.GetUniqueId(), 'text': item.GetName(),
                             'lines': lines(item.GetName()), 'start': float(item.GetStart()),
                             'end': float(item.GetEnd()), 'duration': float(item.GetDuration())} for item in items]}
            subtitle_tracks.append(row)
            if items:
                nonempty.append(row)
        check(len(subtitle_tracks) == len(nonempty) == 1, 'exactly_one_nonempty_subtitle_track_no_empty_tracks', tid)
        actual_cues = nonempty[0]['cues'] if len(nonempty) == 1 else []
        check(bool(nonempty) and nonempty[0]['enabled'] is True, 'subtitle_track_enabled', tid)
        check(len(actual_cues) == len(expected_cues), 'native_cue_count_matches_plan', tid)
        cue_rows = []
        for ordinal, (expected, actual, disk) in enumerate(zip(expected_cues, actual_cues, srt), 1):
            exact_text = compact(actual['text']) == compact(expected['text']) == disk['text']
            exact_lines = actual['lines'] == expected['lines'] == disk['lines']
            exact_frames = abs(actual['start'] - start_frame - expected['frame_start_30fps']) < TOLERANCE
            exact_frames = exact_frames and abs(actual['end'] - start_frame - expected['frame_end_30fps']) < TOLERANCE
            disk_frames = round(disk['start_ms'] * 30 / 1000) == expected['frame_start_30fps'] and round(disk['end_ms'] * 30 / 1000) == expected['frame_end_30fps']
            inside = [a for a in current_audio if actual['start'] >= a['start'] - TOLERANCE and actual['end'] <= a['end'] + TOLERANCE]
            source_ok = len(inside) == 1 and inside[0]['id'] == expected['actual_audio_item_id']
            layout_ok = 1 <= len(actual['lines']) <= 3 and all(0 < len(line) <= 28 for line in actual['lines'])
            timing_ok = actual['end'] > actual['start'] and (ordinal == 1 or actual['start'] >= actual_cues[ordinal - 2]['end'])
            detail = {'timeline': tid, 'cue': ordinal}
            for ok, label in [(exact_text, 'native_full_text_matches'), (exact_lines, 'native_explicit_linebreaks_match'),
                              (exact_frames and disk_frames, 'native_and_srt_frames_match'), (source_ok, 'cue_inside_own_source_item'),
                              (layout_ok, 'explicit_max3_lines_max28chars'), (timing_ok, 'cue_positive_and_no_overlap')]:
                check(ok, label, detail)
            cue_rows.append({'index': ordinal, **actual, 'expected_start': expected['frame_start_30fps'],
                             'expected_end': expected['frame_end_30fps'], 'source_item_id': expected['actual_audio_item_id'],
                             'text_match': exact_text, 'explicit_lines_match': exact_lines, 'frame_match': exact_frames and disk_frames,
                             'within_own_source_item': source_ok, 'layout_passed': layout_ok, 'timing_passed': timing_ok})
        check(lexical(' '.join(c['text'] for c in actual_cues)) == lexical(' '.join(c['text'] for c in expected_cues)),
              'native_all_words_preserved_in_order', tid)
        timeline_rows.append({'name': timeline.GetName(), 'id': tid, 'fps': fps, 'width': width, 'height': height,
                              'start_frame': start_frame, 'end_frame': end_frame, 'audio': audio_rows,
                              'subtitle_tracks': [{'index': tr['index'], 'name': tr['name'], 'enabled': tr['enabled'], 'count': len(tr['cues'])} for tr in subtitle_tracks],
                              'cue_count': len(actual_cues), 'cues': cue_rows, 'sentence_or_semantic_half_checks': semantic})

    check(len(all_audio_ids) == len(set(all_audio_ids)) == 47, '47_unique_audio_item_ids', len(all_audio_ids))
    check(sum(t['cue_count'] for t in timeline_rows) == 159, '159_total_native_cues', sum(t['cue_count'] for t in timeline_rows))
    source_rows = []
    for row in binding['clips']:
        path = row['source_path']
        actual_hash = sha(path)
        check(actual_hash == row['source_sha256'], 'original_mp3_sha_preserved', path)
        source_rows.append({'path': path, 'sha256': actual_hash, 'unchanged': actual_hash == row['source_sha256'],
                            'prior_drt_compound_id': row['compound_id'], 'prior_drt_original_media_id': row['original_media_id']})
    after = gui_state(resolve, project)
    for path, expected_hash in input_hashes.items():
        check(sha(path) == expected_hash, 'input_file_stable_during_check', path)
    result = {'checked_at': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
              'success': not failures, 'failure_count': len(failures), 'failures': failures,
              'method': 'Public API read-only existing timelines by ID, plus approved SRT/plan/repaired snapshot and prior DRT binding proof.',
              'Resolve_mutation_calls_performed': False, 'timeline_page_or_playhead_selection_calls_performed': False,
              'project_id': project.GetUniqueId(), 'project_name': project.GetName(), 'gui_before': before, 'gui_after': after,
              'gui_state_observed_unchanged': before == after, 'timelines': timeline_rows,
              'source_mp3_integrity': source_rows, 'inputs_sha256': input_hashes,
              'summary': {'timelines': len(timeline_rows), 'native_cues': sum(t['cue_count'] for t in timeline_rows),
                          'unique_audio_items': len(set(all_audio_ids)), 'original_mp3s_hashed': len(source_rows)},
              'limitations': ['Current compound descendants are not freshly exported or traversed. Source binding relies on prior native DRT evidence plus unchanged live item IDs/placement/wrapper; all original MP3 hashes are freshly checked.',
                              'Explicit line breaks and line count are verified; font, bounding box and visible screen layout require the parent UI/final DRT audit.',
                              'Sentence halves use the already reviewed semantic plan; speech/word times remain ASR estimates and no new listening is performed.',
                              'GUI before/after differences can reflect concurrent user activity; this script never selects or restores GUI state.']}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'success': result['success'], 'failure_count': len(failures), 'failures': failures,
                      'summary': result['summary'], 'gui_state_observed_unchanged': before == after,
                      'output': str(args.output.resolve())}, ensure_ascii=False, indent=2))
    return 0 if not failures else 1


if __name__ == '__main__':
    raise SystemExit(main())
