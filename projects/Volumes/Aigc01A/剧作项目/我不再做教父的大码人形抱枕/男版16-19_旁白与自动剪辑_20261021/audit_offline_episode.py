"""Independent offline source/word/gain/SRT audit; never touches Resolve or source media."""
import argparse
import collections
import json
from pathlib import Path
from native_common import BASE, normalize_clip, read_json, selected_narration, write_json
from subtitle_tools import parse_srt, continuous_source_windows


def audit(ep, events_path=None):
    inventory = read_json(BASE / '准备/media_inventory.json')
    videos = {x['path']: x for e in inventory['episodes'] for x in e['videos']}
    levels = {x['source_path']: x for x in read_json(BASE / 'ASR/source_levels.json')['files']}
    selected, pending = selected_narration(True)
    timings = [x for x in read_json(BASE / 'ASR/旁白逐词与源段落锚点_采用版本.json')['files'] if x['episode'] == ep['episode']]
    observations = []
    normalized = {kind: [normalize_clip(x) for x in ep[kind]] for kind in ['video', 'narration']}
    for kind, clips in normalized.items():
        end = 0
        used = collections.defaultdict(list)
        for index, clip in enumerate(clips):
            path = clip['path']
            assert Path(path).is_file()
            assert clip['record_frame'] >= end
            if kind == 'video':
                assert clip['record_frame'] == end, ('Picture gap', index)
                assert path in videos and videos[path]['has_embedded_audio']
                assert clip['source_end_frame'] <= int(videos[path]['video_streams'][0]['nb_frames'])
                if videos[path]['episode_group_segment'][0] != ep['episode']:
                    assert len(clip.get('source_episode_override_reason', '')) >= 12
                assert clip['gain_db'] in [levels[path]['suggested_speech_gain_db'], levels[path]['suggested_ambience_under_vo_gain_db']]
            else:
                assert path in selected.values()
                assert '/音频/第%d集/' % ep['episode'] in path
                assert clip['gain_db'] == levels[path]['suggested_speech_gain_db']
            for a, b in used[path]:
                assert clip['source_end_frame'] <= a or clip['source_start_frame'] >= b, ('Repeated source', path)
            used[path].append((clip['source_start_frame'], clip['source_end_frame']))
            end = clip['record_frame'] + clip['duration_frames']
            assert end <= ep['duration_frames']
        if kind == 'video':
            assert end == ep['duration_frames']
    word_report = []
    for timing in timings:
        clips = continuous_source_windows(normalized['narration'], timing['source_path'])
        assert clips, ('Missing narration segment', timing['source_path'])
        words = []
        for index, word in enumerate(timing['source_words']):
            a, b = word['start'] * 24, word['end'] * 24
            containers = [c for c in clips if c['source_start_frame'] - .51 <= a and b <= c['source_end_frame'] + .51]
            assert len(containers) == 1, ('Observed voiced word is cut/missing/duplicated', timing['basename'], index, word)
            words.append({'word': word['word'], 'source_start_seconds': word['start'], 'source_end_seconds': word['end'],
                          'record_start_frame_rounded': round(a) - containers[0]['source_start_frame'] + containers[0]['record_frame'],
                          'one_original_speed_interval_covers_word': True})
        word_report.append({'logical_basename': timing['basename'], 'adopted_path': timing['source_path'],
                            'observed_word_count': len(words), 'observed_words': words,
                            'all_observed_words_once_at_original_speed': True})
    report = {'episode': ep['episode'], 'duration_frames': ep['duration_frames'],
              'video_clips': len(normalized['video']), 'narration_clips': len(normalized['narration']),
              'picture_no_gaps': True, 'source_ranges_valid_and_not_repeated': True,
              'all_observed_narration_words_retained': True, 'gain_values_match_measured_safe_suggestions': True,
              'narration_coverage': word_report, 'mutations': False,
              'scope_limit': '逐词覆盖以现有独立盲转写时码为证据，非完整正常速度人工听验；单词时码保留最多半帧量化误差。'}
    if ep.get('subtitle_srt'):
        cues = parse_srt(ep['subtitle_srt'])
        assert cues and all(0 <= a < b <= ep['duration_frames'] for a, b, _ in cues)
        report.update(srt_cues=len(cues), srt_max_lines=max(len(x[2].splitlines()) for x in cues),
                      srt_max_characters_per_line=max(len(line) for x in cues for line in x[2].splitlines()))
        if events_path:
            event_file = read_json(events_path)
            events = event_file['events'] if 'events' in event_file else next(x['events'] for x in event_file['episodes'] if x['episode'] == ep['episode'])
            assert [x['word'] for x in sorted(events, key=lambda x: (x['start_frame'], x['end_frame']))] == ' '.join(x[2].replace('\n', ' ') for x in cues).split()
            events_by_paragraph = collections.defaultdict(list)
            for event in events:
                events_by_paragraph[event['docx_paragraph']].append(event['word'])
            original = next(x for x in read_json(BASE / '准备/narration_manifest.json')['episodes'] if x['episode'] == ep['episode'])
            for paragraph in original['original_paragraphs_and_retained_narration']:
                expected = paragraph['text'].strip('"“”').split()
                actual = events_by_paragraph[paragraph['docx_paragraph']]
                assert actual == expected, ('Subtitle original text mismatch', paragraph['docx_paragraph'], expected, actual)
            report['srt_original_narration_and_written_messages_all_words_exact'] = True
            dialogue_events = [x for x in events if x.get('kind') == 'sync_dialogue']
            narrator_events = [x for x in events if x.get('kind') == 'narration' or (x.get('source_path') and '/音频/' in x['source_path'])]
            for dialogue in dialogue_events:
                assert not any(max(dialogue['start_frame'], word['start_frame']) < min(dialogue['end_frame'], word['end_frame']) for word in narrator_events), ('VO overlaps spoken dialogue', dialogue)
                candidates = [c for c in normalized['video'] if c['path'] == dialogue['source_path'] and max(c['record_frame'], dialogue['start_frame']) < min(dialogue['end_frame'], c['record_frame'] + c['duration_frames'])]
                assert candidates
                assert candidates[0]['record_frame'] <= dialogue['start_frame'] and candidates[-1]['record_frame'] + candidates[-1]['duration_frames'] >= dialogue['end_frame']
                assert all(a['record_frame'] + a['duration_frames'] == b['record_frame'] and a['source_end_frame'] == b['source_start_frame'] for a, b in zip(candidates, candidates[1:])), 'Spoken dialogue crosses removed/reordered source'
                assert all(c['gain_db'] == levels[dialogue['source_path']]['suggested_speech_gain_db'] for c in candidates), 'True dialogue was ducked as environment'
            report.update(original_sync_dialogue_word_count=len(dialogue_events), no_narration_word_overlaps_sync_dialogue=True)
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--episode-plan', required=True)
    parser.add_argument('--word-events')
    parser.add_argument('--srt')
    args = parser.parse_args()
    source = read_json(args.episode_plan)
    rows = source['episodes'] if 'episodes' in source else [source]
    assert not args.word_events or len(rows) == 1
    for ep in rows:
        if args.srt:
            ep = dict(ep, subtitle_srt=str(Path(args.srt).resolve()))
        result = audit(ep, args.word_events)
        out = BASE / '准备' / ('EP%d_独立原生计划核验.json' % ep['episode'])
        write_json(out, result)
        print(json.dumps(dict(result, narration_coverage='see saved report', output=str(out)), ensure_ascii=False), flush=True)


if __name__ == '__main__':
    main()
