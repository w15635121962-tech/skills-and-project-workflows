#!/usr/bin/env python3
"""Preserve existing Resolve timeline IDs/edits and incrementally add narration.

Default is a read-only preview. --apply is required for all Resolve mutations.
An incomplete manifest is rejected unless --allow-partial is explicitly supplied.
This script never creates a project or replaces/deletes an existing timeline.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import sys
import uuid
from pathlib import Path

import resolve_audio_timelines as common


BASE = Path(__file__).resolve().parent
PARTIAL_PATTERN = re.compile(r'_PARTIAL_未完成(?:_\d+of\d+|_\d+段)?$')


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write_json(path, value):
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


def episode_key(version, episode):
    return f'{version}/{episode}'


def new_timeline_name(entry, complete):
    version = '性转男版' if entry['version'] == '性转版' else entry['version']
    name = f'大码_{version}_EP{entry["episode"]:02d}_配音'
    if not complete:
        name += f'_PARTIAL_未完成_{entry["clip_count"]:02d}of{entry["expected_clip_count"]:02d}'
    return name


def remove_partial_suffix(name):
    return PARTIAL_PATTERN.sub('', name)


def partial_marker_id(entry):
    signature = hashlib.sha256(json.dumps(
        [(clip['name'], clip['sha256']) for clip in entry['clips']],
        ensure_ascii=False, separators=(',', ':'),
    ).encode('utf-8')).hexdigest()[:16]
    return f'dama-partial:v1:{entry["version"]}:{entry["episode"]}:{signature}'


def all_items(timeline):
    items = []
    for kind in ('video', 'audio', 'subtitle'):
        for track in range(1, int(timeline.GetTrackCount(kind)) + 1):
            for item in timeline.GetItemListInTrack(kind, track) or []:
                items.append((kind, track, item))
    return items


def item_snapshot(timeline):
    """Read existing item identity, placement, source trim, and clip properties."""
    result = {}
    for kind, track, item in all_items(timeline):
        media = item.GetMediaPoolItem()
        uid = common.require(item.GetUniqueId(), 'Cannot read timeline-item ID.')
        result[uid] = {
            'kind': kind, 'track': track, 'name': item.GetName(),
            'start': item.GetStart(True), 'end': item.GetEnd(True),
            'duration': item.GetDuration(True),
            'source_start': item.GetSourceStartTime(), 'source_end': item.GetSourceEndTime(),
            'media_path': common.media_path(media) if media else None,
            'properties': item.GetProperty(), 'markers': item.GetMarkers(),
        }
    return result


def verify_existing_items_preserved(before, timeline):
    after = item_snapshot(timeline)
    changed = [uid for uid, prior in before.items() if uid not in after or after[uid] != prior]
    if changed:
        raise RuntimeError(f'Existing timeline items changed unexpectedly in {timeline.GetName()}: {changed}')
    return len(before)


def marker_snapshot(timeline, owned_markers):
    return {str(frame): marker for frame, marker in (timeline.GetMarkers() or {}).items()
            if marker.get('customData') not in owned_markers}


def connect_existing_project(baseline, state):
    resolve = common.get_resolve()
    pm = common.require(resolve.GetProjectManager(), 'Cannot read Resolve project manager.')
    project = common.require(pm.GetCurrentProject(), 'Open the existing PARTIAL project first.')
    wanted = baseline['project_id']
    if state and state.get('project_id') != wanted:
        raise RuntimeError('Incremental state and baseline refer to different Resolve project IDs.')
    if project.GetUniqueId() != wanted:
        raise RuntimeError(f'Current project ID is {project.GetUniqueId()}; open the existing project {state.get("project_name", baseline["project_name"])} ({wanted}). No project was switched or created.')
    return resolve, pm, project


def baseline_state(baseline):
    managed = {}
    for entry in baseline['timelines']:
        if entry['version'] != '女版':
            continue
        key = episode_key(entry['version'], entry['episode'])
        managed[key] = {
            'version': entry['version'], 'episode': entry['episode'],
            'timeline_id': entry['timeline_id'], 'name': entry['name'],
            'imported_clips': {clip['name']: {'local_path': clip['local_path'], 'sha256': clip['sha256']}
                               for clip in entry['clips']},
            'owned_partial_markers': [entry['partial_marker_custom_data']] if entry.get('partial_marker_custom_data') else [],
        }
    if set(managed) != {'女版/1', '女版/2', '女版/3'}:
        raise RuntimeError('Baseline must identify all three existing female timelines.')
    return {
        'project_id': baseline['project_id'], 'project_name': baseline['project_name'],
        'managed': managed, 'pending_operation': None,
    }


def prepare(manifest_path, baseline_path, state_path, allow_partial):
    metadata, groups, fps = common.load_manifest(manifest_path, allow_partial=allow_partial)
    outline = common.plan(metadata, groups, fps)
    baseline = read_json(baseline_path)
    baseline_ids = {entry['timeline_id'] for entry in baseline['timelines'] if entry['version'] == '女版'}
    state = read_json(state_path) if state_path.exists() else baseline_state(baseline)
    if state.get('pending_operation'):
        raise RuntimeError('An interrupted incremental operation is recorded. Inspect it before retrying; automatic retry could duplicate audio.')
    resolve, pm, project = connect_existing_project(baseline, state)
    if abs(float(project.GetSetting('timelineFrameRate')) - float(fps)) > .0001:
        raise RuntimeError('Existing project frame rate differs from the verified manifest.')
    native = {}
    names = {}
    for index in range(1, int(project.GetTimelineCount()) + 1):
        timeline = common.require(project.GetTimelineByIndex(index), 'Cannot read a native timeline.')
        native[timeline.GetUniqueId()] = timeline
        names[timeline.GetName()] = timeline.GetUniqueId()
    if not baseline_ids.issubset(native):
        raise RuntimeError('An original female timeline ID is missing; refusing to rebuild or replace it.')
    current_entries = {episode_key(entry['version'], entry['episode']): entry for entry in outline['timelines']}
    for key, managed in state['managed'].items():
        entry = current_entries.get(key)
        if entry is None:
            raise RuntimeError(f'Manifest omits a previously imported episode: {key}')
        current_names = [clip['name'] for clip in entry['clips']]
        imported_names = list(managed['imported_clips'])
        if not set(imported_names).issubset(current_names):
            raise RuntimeError(f'Manifest omits previously imported audio in {key}; no native changes were made.')
        if len(current_names) > len(imported_names) and current_names[:len(imported_names)] != imported_names:
            raise RuntimeError(f'New audio in {key} is not a contiguous suffix; appending could change story order. No native changes were made.')
    complete = outline['coverage']['scope_status'] == 'complete'
    actions = []
    for entry in outline['timelines']:
        key = episode_key(entry['version'], entry['episode'])
        managed = state['managed'].get(key)
        if managed:
            timeline = native.get(managed['timeline_id'])
            if timeline is None:
                raise RuntimeError(f'Managed timeline ID is missing: {key}. It will not be recreated.')
            for clip in entry['clips']:
                prior = managed['imported_clips'].get(clip['name'])
                if prior and (prior['local_path'] != clip['local_path'] or prior['sha256'] != clip['sha256']):
                    raise RuntimeError(f'An already imported audio path/bytes changed: {key}/{clip["name"]}')
            added = [clip for clip in entry['clips'] if clip['name'] not in managed['imported_clips']]
            if entry['version'] == '女版' and added:
                raise RuntimeError('All female audio was already imported. Female timeline content will not be changed.')
            if complete:
                target_name = remove_partial_suffix(timeline.GetName())
            else:
                suffix = f'_PARTIAL_未完成_{entry["clip_count"]:02d}of{entry["expected_clip_count"]:02d}'
                target_name = PARTIAL_PATTERN.sub(suffix, timeline.GetName())
            action = 'append_new_male_audio' if added else 'preserve_existing_items'
        else:
            if entry['version'] != '性转版':
                raise RuntimeError('Refusing to create or duplicate a female timeline.')
            added = entry['clips']
            target_name = new_timeline_name(entry, complete)
            timeline = None
            action = 'create_nonempty_male_timeline'
        if target_name in names and (timeline is None or names[target_name] != timeline.GetUniqueId()):
            raise RuntimeError(f'Target name belongs to another timeline: {target_name}')
        actions.append({
            'key': key, 'entry': entry, 'action': action, 'new_clips': added,
            'timeline': timeline, 'target_name': target_name,
            'preserved_timeline_id': timeline.GetUniqueId() if timeline else None,
        })
    if not {'女版/1', '女版/2', '女版/3'}.issubset({item['key'] for item in actions}):
        raise RuntimeError('Manifest must retain the 24 previously imported female clips.')
    target_project_name = remove_partial_suffix(project.GetName()) if complete else project.GetName()
    if complete and target_project_name != project.GetName() and target_project_name in (pm.GetProjectListInCurrentFolder() or []):
        raise RuntimeError(f'Another project already uses the completed name: {target_project_name}')
    preview = {
        'mode': 'read_only_incremental_preview', 'project_name': project.GetName(),
        'project_id': project.GetUniqueId(), 'target_project_name': target_project_name,
        'coverage': outline['coverage'], 'original_female_timeline_ids': sorted(baseline_ids),
        'new_audio_clip_count': sum(len(item['new_clips']) for item in actions),
        'actions': [{
            'version': item['entry']['version'], 'episode': item['entry']['episode'],
            'action': item['action'], 'new_clip_count': len(item['new_clips']),
            'new_clip_names': [clip['name'] for clip in item['new_clips']],
            'preserved_timeline_id': item['preserved_timeline_id'], 'target_name': item['target_name'],
            'remove_only_owned_partial_markers': complete,
        } for item in actions],
        'will_create_project': False, 'will_replace_or_delete_timelines': False,
        'will_create_empty_timelines': False,
    }
    return resolve, pm, project, baseline_ids, state, outline, actions, preview


def import_audio(pool, folder, clips):
    common.require(pool.SetCurrentFolder(folder), 'Cannot select target male episode bin.')
    available = {common.media_path(item): item for item in (folder.GetClipList() or []) if common.media_path(item)}
    missing = [clip['local_path'] for clip in clips if clip['local_path'] not in available]
    if missing:
        for item in common.require(pool.ImportMedia(missing), 'Resolve audio import failed.'):
            available[common.media_path(item)] = item
    absent = [clip['local_path'] for clip in clips if clip['local_path'] not in available]
    if absent:
        raise RuntimeError(f'Audio files were not imported: {absent}')
    return [available[clip['local_path']] for clip in clips]


def check_new_items(items, expected, fps, minimum_start=None):
    if len(items) != len(expected):
        raise RuntimeError('Resolve returned the wrong number of new audio items.')
    placed = sorted(items, key=lambda item: item.GetStart(True))
    if [common.media_path(item.GetMediaPoolItem()) for item in placed] != [clip['local_path'] for clip in expected]:
        raise RuntimeError('New narration source order differs from the manifest.')
    previous = None
    for item, clip in zip(placed, expected):
        start, end = float(item.GetStart(True)), float(item.GetEnd(True))
        if minimum_start is not None and start < minimum_start - .001:
            raise RuntimeError('New audio overlaps the existing edited timeline.')
        if previous is not None and abs(start - previous) > .001:
            raise RuntimeError('Newly appended narration has a gap/overlap.')
        previous = end
        candidates = [clip['duration_seconds'], clip['container_duration_seconds']]
        if end <= start or min(abs((end - start) - duration * fps) for duration in candidates) > 1.1:
            raise RuntimeError(f'New audio duration verification failed: {clip["name"]}')
    return [item.GetUniqueId() for item in placed]


def apply(prepared, state_path, report_path, backup_folder):
    resolve, pm, project, baseline_ids, state, outline, actions, preview = prepared
    complete = outline['coverage']['scope_status'] == 'complete'
    backup_folder.mkdir(parents=True, exist_ok=True)
    stamp = datetime.datetime.now().strftime('%Y%m%dT%H%M%S')
    backup = backup_folder / f'增量前备份_{stamp}_{uuid.uuid4().hex[:6]}.drp'
    common.require(pm.SaveProject(), 'Cannot save existing project before incremental edit.')
    common.require(pm.ExportProject(project.GetName(), str(backup), False), 'Cannot export pre-edit project backup.')
    if not backup.is_file() or not backup.stat().st_size:
        raise RuntimeError('Pre-edit project backup was not written.')
    pool = common.require(project.GetMediaPool(), 'Cannot access the existing media pool.')
    root = common.require(pool.GetRootFolder(), 'Cannot access the media pool root.')
    old_folder = pool.GetCurrentFolder()
    old_timeline = project.GetCurrentTimeline()
    snapshots = {}
    other_markers = {}
    for action in actions:
        timeline = action['timeline']
        if timeline:
            snapshots[timeline.GetUniqueId()] = item_snapshot(timeline)
            owned = state['managed'][action['key']]['owned_partial_markers']
            other_markers[timeline.GetUniqueId()] = marker_snapshot(timeline, owned)
    report = {**preview, 'mode': 'incremental_apply', 'import_state': 'in_progress',
              'pre_edit_project_backup': str(backup), 'timelines': []}
    try:
        for action in actions:
            entry, timeline, added = action['entry'], action['timeline'], action['new_clips']
            key = action['key']
            if added:
                state['pending_operation'] = {
                    'episode': key, 'operation': action['action'], 'target_name': action['target_name'],
                    'timeline_id': timeline.GetUniqueId() if timeline else None,
                    'new_clip_names': [clip['name'] for clip in added],
                }
                write_json(state_path, state)
                version_bin = common.find_or_create_bin(pool, root, '性转男版')
                folder = common.find_or_create_bin(pool, version_bin, f'EP{entry["episode"]:02d}_旁白')
                audio = import_audio(pool, folder, added)
                if timeline is None:
                    timeline = common.require(pool.CreateTimelineFromClips(action['target_name'], audio), 'Cannot create nonempty male timeline.')
                    common.verify_timeline(timeline, added)
                    new_ids = [item.GetUniqueId() for item in (timeline.GetItemListInTrack('audio', 1) or [])]
                    timeline_id = common.require(timeline.GetUniqueId(), 'Cannot get created male timeline ID.')
                    state['managed'][key] = {
                        'version': entry['version'], 'episode': entry['episode'],
                        'timeline_id': timeline_id, 'name': timeline.GetName(),
                        'imported_clips': {}, 'owned_partial_markers': [],
                    }
                else:
                    before = snapshots[timeline.GetUniqueId()]
                    minimum_start = max((float(item['end']) for item in before.values()), default=float(timeline.GetStartFrame()))
                    common.require(project.SetCurrentTimeline(timeline), 'Cannot select existing male timeline for append.')
                    appended = common.require(pool.AppendToTimeline(audio), 'Resolve did not append new male audio.')
                    new_ids = check_new_items(appended, added, float(outline['fps']), minimum_start=minimum_start)
                    track_one_ids = {item.GetUniqueId() for item in (timeline.GetItemListInTrack('audio', 1) or [])}
                    if not set(new_ids).issubset(track_one_ids):
                        raise RuntimeError('Resolve did not append the new narration to audio track 1.')
                    verify_existing_items_preserved(before, timeline)
                for clip in added:
                    state['managed'][key]['imported_clips'][clip['name']] = {'local_path': clip['local_path'], 'sha256': clip['sha256']}
                state['pending_operation'] = None
                common.require(pm.SaveProject(), 'Cannot save appended male audio.')
                write_json(state_path, state)
            managed = state['managed'][key]
            if not complete:
                intended_marker = partial_marker_id(entry)
                if intended_marker not in managed['owned_partial_markers']:
                    managed['owned_partial_markers'].append(intended_marker)
                # Record ownership before deleting/adding markers. A resumed run can
                # distinguish an interrupted automation marker from user markers.
                write_json(state_path, state)
                for custom_data in managed['owned_partial_markers']:
                    if custom_data == intended_marker:
                        continue
                    if any(marker.get('customData') == custom_data for marker in (timeline.GetMarkers() or {}).values()):
                        common.require(timeline.DeleteMarkerByCustomData(custom_data), 'Cannot update the owned partial marker.')
                marker = common.ensure_partial_marker(timeline, entry, outline['coverage'])
                if marker != intended_marker:
                    raise RuntimeError('Partial marker identity differs from the persisted ownership intent.')
            if complete:
                for custom_data in managed['owned_partial_markers']:
                    if any(marker.get('customData') == custom_data for marker in (timeline.GetMarkers() or {}).values()):
                        common.require(timeline.DeleteMarkerByCustomData(custom_data), 'Cannot remove an owned partial marker.')
                    if any(marker.get('customData') == custom_data for marker in (timeline.GetMarkers() or {}).values()):
                        raise RuntimeError('An owned partial marker remains after deletion.')
            if timeline.GetName() != action['target_name']:
                common.require(timeline.SetName(action['target_name']), 'Cannot update the owned PARTIAL name suffix.')
            managed['name'] = timeline.GetName()
            original = snapshots.get(timeline.GetUniqueId())
            preserved = verify_existing_items_preserved(original, timeline) if original is not None else 0
            if timeline.GetUniqueId() in other_markers:
                if marker_snapshot(timeline, managed['owned_partial_markers']) != other_markers[timeline.GetUniqueId()]:
                    raise RuntimeError('A user timeline marker changed unexpectedly.')
            paths = [common.media_path(item.GetMediaPoolItem()) for kind, track, item in all_items(timeline)
                     if kind == 'audio' and item.GetMediaPoolItem()]
            missing_visible = [clip['name'] for clip in entry['clips'] if clip['local_path'] not in paths]
            report['timelines'].append({
                'version': entry['version'], 'episode': entry['episode'], 'name': timeline.GetName(),
                'timeline_id': timeline.GetUniqueId(), 'new_imported_clip_count': len(added),
                'previous_item_count_preserved': preserved, 'tracked_imported_clip_count': len(managed['imported_clips']),
                'source_audio_duration_seconds': entry['duration_seconds'],
                'source_paths_missing_after_user_edits': missing_visible,
            })
            common.require(pm.SaveProject(), 'Cannot save incremental timeline state.')
            state['project_name'] = project.GetName()
            state['coverage'] = outline['coverage']
            write_json(state_path, state)
            write_json(report_path, report)
        if complete and project.GetName() != preview['target_project_name']:
            common.require(project.SetName(preview['target_project_name']), 'Cannot remove project PARTIAL suffix.')
        if project.GetUniqueId() != state['project_id']:
            raise RuntimeError('Project ID changed unexpectedly.')
        actual_ids = {project.GetTimelineByIndex(index).GetUniqueId()
                      for index in range(1, int(project.GetTimelineCount()) + 1)}
        if not baseline_ids.issubset(actual_ids):
            raise RuntimeError('Original female timeline IDs were not retained.')
        if complete and len(state['managed']) != 6:
            raise RuntimeError('Completion requires all six managed episode timelines.')
        if sum(len(item['imported_clips']) for item in state['managed'].values()) != outline['coverage']['downloaded_clip_count']:
            raise RuntimeError('Tracked imported audio coverage differs from manifest coverage.')
        state['project_name'] = project.GetName()
        state['scope_status'] = outline['coverage']['scope_status']
        state['manifest_sha256'] = outline['manifest_sha256']
        common.require(pm.SaveProject(), 'Cannot save final incremental state.')
        report.update({'project_name': project.GetName(), 'import_state': 'verified',
                       'scope_status': state['scope_status'], 'original_female_timeline_ids_preserved': True,
                       'managed_timeline_count': len(state['managed']),
                       'total_project_timeline_count': project.GetTimelineCount()})
        write_json(state_path, state)
        write_json(report_path, report)
        return report
    finally:
        if old_folder:
            common.require(pool.SetCurrentFolder(old_folder), 'Cannot restore the selected bin.')
        if old_timeline:
            common.require(project.SetCurrentTimeline(old_timeline), 'Cannot restore the selected timeline.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--baseline', type=Path, default=BASE / '达芬奇导入结果_PARTIAL.json')
    parser.add_argument('--state', type=Path, default=BASE / '达芬奇增量导入状态.json')
    parser.add_argument('--report', type=Path, default=BASE / '达芬奇增量导入结果.json')
    parser.add_argument('--backup-folder', type=Path, default=BASE / '达芬奇项目备份')
    parser.add_argument('--allow-partial', action='store_true')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    prepared = prepare(args.manifest.resolve(strict=True), args.baseline.resolve(strict=True), args.state, args.allow_partial)
    result = apply(prepared, args.state, args.report, args.backup_folder) if args.apply else prepared[-1]
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        raise SystemExit(1)
