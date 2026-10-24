#!/usr/bin/env python3
"""EP19 offline native edit plan. Does not connect to Resolve or alter sources."""
from pathlib import Path
import json
import math
import re
import sys

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
from native_common import read_json, write_json, FPS, sha256
from subtitle_tools import original_words_on_timeline, cues_from_events, write_srt

manifest = read_json(BASE / '准备/narration_manifest.json')
selected = read_json(BASE / 'ASR/旁白采用清单.json')
selections = {r['narration_sequence']: r for r in selected['selections'] if r['episode'] == 19}
assert len(selections) == 5 and selected['all_27_take_selections_complete']
groups = {r['narration_sequence']: r for r in manifest['groups'] if r['episode'] == 19}
source_episode = next(e for e in manifest['episodes'] if e['episode'] == 19)
framework = read_json(BASE / '准备/男版16-19_自动剪辑计划框架.json')
dialogues = {r['id']: r for r in framework['mandatory_dialogue_units'] if r['episode'] == 19}
levels_doc = read_json(BASE / 'ASR/source_levels.json')
levels = {r['path']: r for r in levels_doc['files']}
inventory = next(e for e in read_json(BASE / '准备/media_inventory.json')['episodes'] if e['episode'] == 19)
sources = {r['filename']: r for r in inventory['videos']}

video, narration, stages = [], [], []
cursor = 0


def v(filename, first, last, tag, mode='ambience'):
    global cursor
    source = sources[filename]
    path = source['path']
    assert 0 <= first < last <= int(source['video_streams'][0]['nb_frames'])
    gain = levels[path]['suggested_speech_gain_db' if mode == 'dialogue' else 'suggested_ambience_under_vo_gain_db']
    row = {'path': path, 'source_start_frame': first, 'source_end_frame': last,
           'record_frame': cursor, 'gain_db': gain, 'tag': tag,
           'source_speed_percent': 100, 'same_source_same_bounds_linked_sync_audio': True,
           'audio_role': mode}
    video.append(row)
    cursor += last - first
    return row


def vo(sequence, first, last, record, tag):
    row = selections[sequence]
    path = row['selected_audio_path']
    assert sha256(path) == row['selected_audio_sha256']
    assert 0 <= first < last <= math.ceil(row['selected_audio_duration_seconds'] * FPS)
    narration.append({'path': path, 'source_start_frame': first, 'source_end_frame': last,
                      'record_frame': record, 'gain_db': levels[path]['suggested_speech_gain_db'],
                      'tag': tag, 'source_speed_percent': 100, 'logical_basename': row['logical_basename']})


# P522–524: question remains in the original picture/audio; VO stops before it.
stages.append({'id': 'arrival_and_question', 'record_frame': cursor})
v('男版19-1-1.mp4', 0, 168, 'P522–523 elevator and guide; VO ambience')
v('男版19-1-1.mp4', 168, 199, 'P524 full original What happened to her?', 'dialogue')
v('男版19-1-1.mp4', 199, 241, 'Question reaction into nurse leaning in')
v('男版19-2-1.mp4', 84, 133, 'P525 listener reaction; avoid already-covered first nurse line')
assert cursor == 290
vo(1, 0, 172, 0, 'P522–523 before original question; no words cut')
vo(1, 172, 260, 201, 'P525 after original question; original same VO file continued')

# P526–528: nurse first sentence only from the safer close-up alternate; then
# original second and third exchanges from the longer source, exactly once.
stages.append({'id': 'nurse_report_and_exchange', 'record_frame': cursor})
v('男版19-2-2.mp4', 0, 121, 'P526 full nurse report; no repeat from19-2-1', 'dialogue')
v('男版19-2-1.mp4', 177, 293, 'P527–528 both original nurse follow-up sentences', 'dialogue')
assert cursor == 527

# P529–530: unused reaction and walking source, then door-handle approach.
# These source frames have not appeared earlier. No loop/freeze/speed change.
stages.append({'id': 'insomnia_and_room_approach', 'record_frame': cursor})
v('男版19-2-1.mp4', 133, 177, 'P529 unused listening reaction after nurse dialogue')
v('男版19-2-1.mp4', 293, 481, 'P529–530 brow, walk and arrival at private room')
v('男版19-3-1.mp4', 0, 30, 'P530 hand arrives at door; no entry yet')
assert cursor == 789
vo(2, 0, 262, 527, 'P529–530; retain every spoken word, trim only ending silence')

# P531: actual cracked-door introduction before mother speaks. Borrow the
# passive hospital-bed view, not the mother watch action or another push/entry.
stages.append({'id': 'door_cracked_and_inside_voice', 'record_frame': cursor})
v('男版19-3-1.mp4', 30, 102, 'P531 handle and cracked view before first original mother word')
v('男版19-4-1.mp4', 0, 52, 'P531 passive Vittoria hospital-bed view; no watch or push action')
assert cursor == 913
vo(3, 0, 124, 789, 'P531 only; split before P532 mother original dialogue')

stages.append({'id': 'mother_devalues', 'record_frame': cursor})
v('男版19-3-2.mp4', 0, 241, 'P532 complete original mother line, all three clauses once', 'dialogue')
assert cursor == 1154

# P533–534: no reply from Vittoria, Oliver receives the insult, then mother
# checks her watch. Avoid another occurrence of the source mother utterance.
stages.append({'id': 'silence_and_watch', 'record_frame': cursor})
v('男版19-3-1.mp4', 358, 409, 'P533 unused Oliver reaction after source mother voice has ended')
v('男版19-4-1.mp4', 53, 106, 'P533–534 door relation and mother watch; stop before duplicate impatient words')
assert cursor == 1258
vo(3, 136, 240, 1154, 'P533 only; split before P535 impatient mother original dialogue')

stages.append({'id': 'mother_impatient', 'record_frame': cursor})
v('男版19-4-2.mp4', 17, 121, 'P535 complete impatient line; skip repeated initial watch motion', 'dialogue')
assert cursor == 1362

stages.append({'id': 'actual_push_open', 'record_frame': cursor})
v('男版19-4-3.mp4', 0, 97, 'P536 true push-open action only here, then doorway arrival')
assert cursor == 1459
vo(3, 240, 313, 1362, 'P536 after mother finishes, original push-open narration')

stages.append({'id': 'entry_and_recognition', 'record_frame': cursor})
v('男版19-5-1.mp4', 0, 433, 'P537–540 entry, room reaction, shoulder/waist/face look and stable end')
assert cursor == 1892
vo(4, 0, 216, 1459, 'P537–539 eyes shift, room silent and frozen Vittoria')
vo(5, 0, 173, 1681, 'P540 shoulders to waist to face; full source sentence at original speed')

ep = {'episode': 19, 'timeline_name': '大码_男版_EP19_新男版音色_原速旁白_自动剪辑_v1',
      'duration_frames': cursor, 'duration_seconds': cursor / FPS,
      'video': video, 'narration': narration, 'stages': stages,
      'narration_source_take_order': [selections[i]['selected_audio_basename'] for i in range(1, 6)],
      'dialogue_ids': list(dialogues),
      'constraints': {'all_original_speed_percent': 100, 'linked_picture_sync_audio': True,
                      'no_freeze_loop_or_generated_coverage': True, 'no_repeated_source_frame_ranges': True,
                      'no_extra_dialogue_or_narration': True}}

# Check frame coverage, original-speed durations, no source repeats and native
# synchronous spoken words covered exactly once without VO masking.
for kind, clips in [('video', video), ('narration', narration)]:
    last_record_end = 0
    spans = {}
    for clip in clips:
        first, last, record = clip['source_start_frame'], clip['source_end_frame'], clip['record_frame']
        assert record >= last_record_end
        if kind == 'video':
            assert record == last_record_end
        last_record_end = record + last - first
        assert last_record_end <= cursor
        for a, z in spans.setdefault(clip['path'], []):
            assert last <= a or first >= z, ('Repeated source', kind, clip)
        spans[clip['path']].append((first, last))
    if kind == 'video':
        assert last_record_end == cursor

vo_events, dialogue_events, dialogue_audit = [], [], []
paragraph_event_order = []
for sequence in range(1, 6):
    group, selection = groups[sequence], selections[sequence]
    path = selection['selected_audio_path']
    raw = read_json(BASE / 'ASR/raw_large-v3-turbo/EP19/narration' / (selection['selected_audio_basename'] + '.json'))
    canonical = group['generation_text'].split()
    native = raw['words']
    assert len(canonical) == len(native)
    normalize = lambda x: re.sub(r"[^a-z0-9']", '', x.lower().replace('’', "'"))
    assert all(normalize(a) == normalize(w['word']) for a, w in zip(canonical, native)), selection['selected_audio_basename']
    words = [{'original_word': text, 'start': w['start'], 'end': w['end']} for text, w in zip(canonical, native)]
    events = original_words_on_timeline(words, path, narration)
    # Assign each source paragraph in source order, preserving punctuation.
    offset = 0
    for record in source_episode['original_paragraphs_and_retained_narration']:
        if record['docx_paragraph'] not in group['source_docx_paragraphs'] or not record['narration_retained_text'].strip():
            continue
        count = len(record['narration_retained_text'].split())
        part = events[offset:offset + count]
        assert [e['word'] for e in part] == record['narration_retained_text'].split()
        for index, event in enumerate(part):
            event.update(kind='narration', docx_paragraph=record['docx_paragraph'], boundary_before=index == 0)
        vo_events += part
        offset += count
    assert offset == len(events)

quote_by_paragraph = {q['docx_paragraphs'][0]: q['text'][1:-1] for q in source_episode['quoted_spans']}
for identity, unit in dialogues.items():
    canonical = quote_by_paragraph[unit['source_docx_paragraph']].split()
    assert len(canonical) == len(unit['words'])
    assert all(normalize(a) == normalize(w['word']) for a, w in zip(canonical, unit['words']))
    words = [{'original_word': text, 'start': w['start'], 'end': w['end']} for text, w in zip(canonical, unit['words'])]
    events = original_words_on_timeline(words, unit['source_path'], video)
    for index, event in enumerate(events):
        event.update(kind='sync_dialogue', dialogue_id=identity, docx_paragraph=unit['source_docx_paragraph'], boundary_before=index == 0)
        assert not any(max(event['start_frame'], w['start_frame']) < min(event['end_frame'], w['end_frame']) for w in vo_events), ('VO masks original dialogue', identity, event)
    dialogue_events += events
    dialogue_audit.append({'id': identity, 'docx_paragraph': unit['source_docx_paragraph'],
                           'original_text': quote_by_paragraph[unit['source_docx_paragraph']], 'word_count': len(events),
                           'timeline_start_frame': events[0]['start_frame'], 'timeline_end_frame': events[-1]['end_frame'],
                           'spoken_original_words_exactly_once': True, 'not_masked_by_narration': True})

events = sorted(vo_events + dialogue_events, key=lambda e: (e['start_frame'], e['end_frame']))
assert len(vo_events) == 127 and len(dialogue_events) == 80 and len(events) == 207
for event in events:
    if not paragraph_event_order or paragraph_event_order[-1] != event['docx_paragraph']:
        paragraph_event_order.append(event['docx_paragraph'])
assert paragraph_event_order == [522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 535, 536, 537, 538, 539, 540], paragraph_event_order

expected = []
for record in source_episode['original_paragraphs_and_retained_narration']:
    p = record['docx_paragraph']
    if p in quote_by_paragraph:
        expected += quote_by_paragraph[p].split()
    elif record['narration_retained_text'].strip():
        expected += record['narration_retained_text'].split()
assert [e['word'] for e in events] == expected, 'Source words missing, duplicated, reordered or punctuation changed'
cues = cues_from_events(events, cursor)
write_srt(BASE / '字幕/EP19.srt', cues)

plan = {'project': '大码枕头', 'fps': FPS, 'status': 'READY_FOR_NATIVE_ASSEMBLY',
        'scope': 'EP19 component only; merge into four-episode master plan before assembly',
        'source_end_frame_exclusive': True, 'all_speed_percent': 100, 'episodes': [ep]}
write_json(BASE / '准备/EP19_native_edit_plan.json', plan)
write_json(BASE / '准备/EP19_original_word_events.json', {'fps': FPS, 'episodes': [{'episode': 19, 'duration_frames': cursor, 'events': events}]})
report = {'episode': 19, 'duration_frames': cursor, 'duration_seconds': cursor / FPS,
          'video_clip_count': len(video), 'same_source_linked_sync_clip_count': len(video),
          'narration_cut_count': len(narration), 'narration_unique_files': 5,
          'original_speed_percent': 100, 'source_ranges_nonrepeated': True, 'picture_has_no_gap': True,
          'original_source_paragraph_order': paragraph_event_order, 'source_word_sequence_exact': True,
          'narration_original_word_count': len(vo_events), 'sync_dialogue_original_word_count': len(dialogue_events),
          'all_207_original_words_preserved_once': True, 'dialogue_units': dialogue_audit,
          'cues': len(cues), 'maximum_lines': max(len(c['text'].splitlines()) for c in cues),
          'maximum_characters_per_line': max(len(l) for c in cues for l in c['text'].splitlines()),
          'gain_basis': str(BASE / 'ASR/source_levels.json'), 'no_resolve_mutation': True,
          'no_new_media_or_speed_change_or_freeze': True,
          'visual_evidence': ['画面核验/EP19_contact_1.jpg', '画面核验/EP19_contact_2.jpg', '画面核验/男版16-19_覆盖与版本核验.md'],
          'limits': ['Offline source frame and speech timing review; not a claim of final native timeline playback or full human listening.']}
write_json(BASE / '准备/EP19_剪辑核验.json', report)
print(json.dumps(report, ensure_ascii=False, indent=2))
