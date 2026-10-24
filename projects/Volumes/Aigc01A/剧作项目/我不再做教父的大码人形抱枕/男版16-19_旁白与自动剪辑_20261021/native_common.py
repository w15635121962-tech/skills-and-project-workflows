"""Offline plan validation and official Resolve helpers for male EP16--19.

All edit coordinates are integer 24 fps frames; source_end_frame is exclusive.
This module does not connect to Resolve or mutate the project on import.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
FPS = 24
EPISODES = {16, 17, 18, 19}
PROJECT = '大码枕头'
TASK_FOLDER = BASE.name


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1048576), b''):
            digest.update(chunk)
    return digest.hexdigest()


def connect():
    sys.path.insert(0, '/Users/zc/.codex/skills/davinci-resolve/scripts')
    from resolve_bootstrap import get_resolve
    resolve = get_resolve()
    manager = resolve.GetProjectManager()
    project = manager.GetCurrentProject()
    assert project and project.GetName() == PROJECT, 'Unexpected active project'
    return resolve, manager, project, project.GetMediaPool()


def timelines(project):
    rows = [project.GetTimelineByIndex(i) for i in range(1, project.GetTimelineCount() + 1)]
    assert all(rows)
    return rows


def timeline_inventory(project, include_items=True):
    """Avoid activating other timelines or trusting their cold track-enable state."""
    result = []
    for timeline in timelines(project):
        row = {'id': timeline.GetUniqueId(), 'name': timeline.GetName(),
               'start': timeline.GetStartFrame(), 'end': timeline.GetEndFrame(), 'tracks': {}}
        for kind in ['video', 'audio', 'subtitle']:
            row['tracks'][kind] = []
            for index in range(1, timeline.GetTrackCount(kind) + 1):
                items = timeline.GetItemListInTrack(kind, index) or []
                track = {'index': index, 'name': timeline.GetTrackName(kind, index), 'count': len(items)}
                if include_items:
                    track['items'] = []
                    for item in items:
                        media = item.GetMediaPoolItem()
                        props = item.GetProperties() or {}
                        track['items'].append({
                            'id': item.GetUniqueId(), 'name': item.GetName(),
                            'start': item.GetStart(), 'end': item.GetEnd(),
                            'source_start': item.GetSourceStartFrame() if media else None,
                            'source_end': item.GetSourceEndFrame() if media else None,
                            'path': media.GetClipProperty('File Path') if media else None,
                            'enabled': item.GetClipEnabled(),
                            'gain_db': props.get('AudioVolume'),
                            'linked_ids': sorted(x.GetUniqueId() for x in item.GetLinkedItems() or []),
                        })
                row['tracks'][kind].append(track)
        result.append(row)
    return result


def walk_media(folder):
    found = {}
    for item in folder.GetClipList() or []:
        path = item.GetClipProperty('File Path')
        if path:
            found.setdefault(str(Path(path)), item)
    for child in folder.GetSubFolderList() or []:
        for path, item in walk_media(child).items():
            found.setdefault(path, item)
    return found


def child_folder(media_pool, parent, name):
    candidates = [f for f in parent.GetSubFolderList() or [] if f.GetName() == name]
    assert len(candidates) <= 1, 'Ambiguous media folder: ' + name
    folder = candidates[0] if candidates else media_pool.AddSubFolder(parent, name)
    assert folder
    return folder


def selected_narration(require_all=False):
    state = read_json(BASE / '制作与剪辑进度.json')
    items = state['items']
    assert len(items) == 27 and {x['episode'] for x in items} == EPISODES
    adopted_path = BASE / 'ASR/旁白采用清单.json'
    adopted = {}
    if adopted_path.exists():
        adopted = {x['logical_basename']: x['selected_audio_path']
                   for x in read_json(adopted_path).get('selections', [])}
    selected = {}
    pending = []
    for item in items:
        path = adopted.get(item['basename']) or item.get('selected_audio_file') or item.get('audio_file') or item['planned_audio_file']
        if item['status'] != 'downloaded' or not Path(path).is_file():
            pending.append(item['basename'])
        selected[item['basename']] = str(Path(path))
    if require_all:
        assert not pending, 'Narration must be completed before any timeline edit: ' + ', '.join(pending)
        assert state.get('narration_speed_percent') == 100
    return selected, pending


def frame_value(clip, field, seconds_field):
    if field in clip:
        value = clip[field]
        assert isinstance(value, int) and not isinstance(value, bool), (field, value)
        return value
    value = float(clip[seconds_field]) * FPS
    assert abs(value - round(value)) < 0.0001, ('Seconds are not frame aligned', seconds_field, value)
    return round(value)


def normalize_clip(clip):
    item = dict(clip)
    item['path'] = str(Path(clip['path']))
    item['source_start_frame'] = frame_value(clip, 'source_start_frame', 'src0')
    item['source_end_frame'] = frame_value(clip, 'source_end_frame', 'src1')
    item['record_frame'] = frame_value(clip, 'record_frame', 'record')
    assert 0 <= item['source_start_frame'] < item['source_end_frame']
    assert item['record_frame'] >= 0
    assert item.get('speed_percent', item.get('native_speed_percent', 100)) == 100
    assert item.get('kind', 'video') != 'still', 'No automatic freeze-frame extensions in this task'
    item['duration_frames'] = item['source_end_frame'] - item['source_start_frame']
    item['gain_db'] = float(item.get('gain_db', 0))
    assert -60 <= item['gain_db'] <= 0, 'Do not blindly amplify source audio'
    return item


def load_plan(path, require_all=True):
    plan = read_json(path)
    assert plan.get('fps', 24) == FPS
    assert plan.get('project', PROJECT) == PROJECT
    assert plan.get('status') == 'READY_FOR_NATIVE_ASSEMBLY', 'Frameworks and incomplete plans cannot be executed'
    expected_narration, pending = selected_narration(require_all)
    inventory = read_json(BASE / '准备/media_inventory.json')
    sources = {x['path']: x for ep in inventory['episodes'] for x in ep['videos']}
    used_audio = set()
    seen_episodes = set()
    for ep in plan['episodes']:
        episode = ep['episode']
        assert episode in EPISODES and episode not in seen_episodes
        seen_episodes.add(episode)
        ep.setdefault('timeline_name', '大码_男版_EP%d_新男版音色_原速旁白_自动剪辑_v1' % episode)
        assert re.search(r'男版_EP0?%d(?:_|$)' % episode, ep['timeline_name']), ep['timeline_name']
        if 'duration_frames' not in ep:
            ep['duration_frames'] = round(ep['duration_seconds'] * FPS)
        assert isinstance(ep['duration_frames'], int) and ep['duration_frames'] > 0
        for kind in ['video', 'narration']:
            ep[kind] = [normalize_clip(x) for x in ep[kind]]
            assert ep[kind], (episode, kind)
            assert ep[kind] == sorted(ep[kind], key=lambda x: x['record_frame'])
            last_end = 0
            ranges = {}
            for clip in ep[kind]:
                path_string = clip['path']
                path_obj = Path(path_string)
                assert path_obj.is_absolute() and path_obj.is_file() and path_obj.stat().st_size > 0
                assert clip['record_frame'] >= last_end, 'Overlapping audio/video items'
                if kind == 'video':
                    assert clip['record_frame'] == last_end, 'Picture gap is not allowed'
                    assert path_string in sources
                    if sources[path_string]['episode_group_segment'][0] != episode:
                        assert len(clip.get('source_episode_override_reason', '').strip()) >= 12, 'Explain same-story cross-episode coverage'
                    source = sources[path_string]
                    assert source['has_embedded_audio'], 'Every picture must carry source sync audio'
                    stream = source['video_streams'][0]
                    assert stream['avg_frame_rate'] == '24/1'
                    assert clip['source_end_frame'] <= int(stream['nb_frames'])
                else:
                    assert path_string in expected_narration.values(), 'Unexpected narration or wrong take'
                    assert '/音频/第%d集/' % episode in path_string, 'Wrong-episode narration'
                    used_audio.add(path_string)
                for start, end in ranges.setdefault(path_string, []):
                    assert clip['source_end_frame'] <= start or clip['source_start_frame'] >= end, 'Repeated source material'
                ranges[path_string].append((clip['source_start_frame'], clip['source_end_frame']))
                last_end = clip['record_frame'] + clip['duration_frames']
                assert last_end <= ep['duration_frames']
            if kind == 'video':
                assert last_end == ep['duration_frames'], 'Picture must cover complete timeline'
    assert seen_episodes == EPISODES, 'All four episodes must be planned before assembly'
    if require_all:
        assert set(expected_narration.values()) == used_audio, 'Missing completed narration segments in edit plan'
    return plan


def clip_info(clip, media, track_index, media_type):
    return {'mediaPoolItem': media[clip['path']], 'startFrame': clip['source_start_frame'],
            'endFrame': clip['source_end_frame'], 'recordFrame': clip['record_frame'],
            'trackIndex': track_index, 'mediaType': media_type}


def assert_clip(item, clip):
    assert item.GetStart() == clip['record_frame']
    assert item.GetEnd() == clip['record_frame'] + clip['duration_frames']
    assert item.GetSourceStartFrame() == clip['source_start_frame']
    assert item.GetEnd() - item.GetStart() == clip['duration_frames'], 'Speed/duration changed'
    assert item.GetClipEnabled()
    assert item.GetMediaPoolItem().GetClipProperty('File Path') == clip['path']

