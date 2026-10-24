"""EP16 original captions through all existing 100% VO edits, including pause cuts.

No unobserved word is assigned a fabricated audio interval. Four reviewed ASR
spelling/tokenization differences use the actual corresponding observed words.
"""
import json
import re
from native_common import BASE, read_json, sha256, write_json
from subtitle_tools import original_words_on_timeline, cues_from_events, write_srt

component_path = BASE / '准备/EP16_native_edit_plan.json'
component_hash = sha256(component_path)
plan = read_json(component_path)
ep = next(x for x in plan['episodes'] if x['episode'] == 16)
timings = [x for x in read_json(BASE / 'ASR/旁白逐词与源段落锚点_采用版本.json')['files'] if x['episode'] == 16]
assert len(timings) == 9

# Explicit reviewed spelling/tokenization correspondences, not a generic missing
# word filler. Any unrecognized new difference stops the subtitle build.
reviewed = {
    ('大码男版枕头16-01-01', 'Aldwick'): ([4], ['Aldwyk,'], 'source proper-name spelling, observed ASR Aldwyk'),
    ('大码男版枕头16-07-01', 'Aldwick'): ([4], ['Aldueck,'], 'source proper-name spelling, observed ASR Aldueck'),
    ('大码男版枕头16-05-01', 'Unpacking'): ([0, 1], ['On', 'packing'], 'reviewed one original word / two ASR tokens'),
    ('大码男版枕头16-05-01', "should've"): ([14, 15], ['should', 'have'], 'reviewed original contraction / two ASR tokens'),
}

events = []
exceptions = []
for timing in timings:
    raw = timing['source_words']
    expected = timing['expected_tokens_with_exact_match_anchors']
    for paragraph in timing['source_paragraph_anchors']:
        source_words = []
        word_proof = []
        char_base = paragraph['generation_char_start']
        for match in re.finditer(r'\S+', paragraph['source_text']):
            start, end = char_base + match.start(), char_base + match.end()
            overlapping = [x for x in expected if x['char_start'] < end and start < x['char_end_exclusive']]
            assert overlapping
            source_indices = []
            for token in overlapping:
                if token.get('source_word_index') is not None:
                    source_indices.append(token['source_word_index'])
                else:
                    identity = (timing['basename'], token['text'])
                    assert identity in reviewed, ('Missing original word must not be forced into audio', identity)
                    indices, observed, note = reviewed[identity]
                    assert [raw[index]['word'].strip() for index in indices] == observed
                    source_indices.extend(indices)
                    exceptions.append({'logical_basename': timing['basename'], 'original_word': token['text'],
                                       'observed_source_words': observed, 'source_word_indices': indices, 'basis': note})
            source_indices = sorted(set(source_indices))
            assert source_indices
            source_words.append({'original_word': match.group(),
                                 'start': min(raw[index]['start'] for index in source_indices),
                                 'end': max(raw[index]['end'] for index in source_indices)})
            word_proof.append({'observed_source_word_indices': source_indices,
                               'observed_source_words': [raw[index]['word'].strip() for index in source_indices],
                               'timing_basis': 'actual observed source word interval, mapped through the existing native 100% cuts'})
        mapped = original_words_on_timeline(source_words, timing['source_path'], ep['narration'])
        for index, (event, proof) in enumerate(zip(mapped, word_proof)):
            event.update(proof)
            event.update(docx_paragraph=paragraph['docx_paragraph'], kind='narration', boundary_before=index == 0)
        events.extend(mapped)

events.sort(key=lambda x: (x['start_frame'], x['end_frame']))
source = next(x for x in read_json(BASE / '准备/narration_manifest.json')['episodes'] if x['episode'] == 16)
original = [word for paragraph in source['original_paragraphs_and_retained_narration']
            for word in paragraph['narration_retained_text'].split()]
assert [x['word'] for x in events] == original
cues = cues_from_events(events, ep['duration_frames'])
path = BASE / '字幕/EP16.srt'
write_srt(path, cues)
write_json(BASE / '字幕/EP16_原文词事件.json', {'episode': 16, 'duration_frames': ep['duration_frames'], 'events': events})
write_json(BASE / '字幕/EP16_原文字幕映射核验.json', {
    'episode': 16, 'narration_source_files': len(timings), 'native_narration_clips_unchanged': len(ep['narration']),
    'component_plan_sha256_unchanged': component_hash, 'all_original_words_in_order': True,
    'actual_observed_word_intervals_used': True, 'unobserved_words_fabricated': False,
    'reviewed_spelling_and_tokenization_differences': exceptions,
    'original_word_count_whitespace': len(original), 'subtitle_cues': len(cues),
    'minimum_cue_frames': min(x['end_frame'] - x['start_frame'] for x in cues),
    'max_lines': max(len(x['text'].splitlines()) for x in cues),
    'max_characters_per_line': max(len(line) for x in cues for line in x['text'].splitlines()),
    'native_plan_or_source_audio_changed': False, 'srt': str(path)})
assert sha256(component_path) == component_hash
print(json.dumps({'episode': 16, 'original_word_count': len(original), 'cues': len(cues),
                  'minimum_cue_frames': min(x['end_frame'] - x['start_frame'] for x in cues),
                  'reviewed_asr_spelling_tokenization_differences': len(exceptions),
                  'source_plan_unchanged': True, 'no_resolve_mutation': True}, ensure_ascii=False), flush=True)
