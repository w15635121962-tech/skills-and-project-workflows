#!/usr/bin/env python3
"""Source-preserving quote exclusion and <=200-character complete narration groups."""
from pathlib import Path
import hashlib
import json
import re

BASE = Path(__file__).resolve().parent
MAX_CHARS = 200
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[’'\-][A-Za-z0-9]+)*")
EXISTING_PLATFORM_TEXT = 'Mafia don Matteo Bellandi suffered from insomnia. So I became his human pillow.'


def sha(text):
    return hashlib.sha256(text.encode('utf-8') if isinstance(text, str) else text).hexdigest()


def word_count(text):
    return len(WORD_RE.findall(text))


def exclude_quotes(text):
    quotes = []
    unmatched = []
    opened = None
    for index, char in enumerate(text):
        if opened is None:
            if char in ['"', '“']:
                opened = (char, index)
            elif char == '”':
                unmatched.append({'character': char, 'offset': index, 'reason': 'closing_quote_without_opening'})
        else:
            opener, start = opened
            if (opener == '"' and char == '"') or (opener == '“' and char == '”'):
                quotes.append({'quote_index': len(quotes) + 1, 'quote_type': 'straight_double' if opener == '"' else 'curly_double', 'source_start': start, 'source_end_exclusive': index + 1, 'excluded_text': text[start:index + 1]})
                opened = None
    if opened:
        unmatched.append({'character': opened[0], 'offset': opened[1], 'reason': 'opening_quote_without_closing'})
    mask = [False] * len(text)
    for quote in quotes:
        mask[quote['source_start']:quote['source_end_exclusive']] = [True] * (quote['source_end_exclusive'] - quote['source_start'])
    indices = [i for i, removed in enumerate(mask) if not removed]
    return ''.join(text[i] for i in indices), indices, quotes, unmatched, mask


all_groups = []
all_episodes = []
audits = []
for version in ['女版', '性转版']:
    manifest = json.loads((BASE / version / f'{version}_前3集_配音清单.json').read_text())
    assert sha(Path(manifest['english_source_path']).read_bytes()) == manifest['english_source_sha256'], 'DOCX source changed'
    for episode in manifest['episodes']:
        number = episode['episode']
        source_path = BASE / version / f'{version}_第{number:02d}集_纯英文全文.txt'
        original = source_path.read_text().removesuffix('\n')
        assert original == '\n'.join(p['text'] for p in episode['segments'])
        narration, kept_indices, quotes, unmatched, mask = exclude_quotes(original)
        paragraph_ranges = []
        cursor = 0
        for index, p in enumerate(episode['segments']):
            block = p['text'] + ('\n' if index + 1 < len(episode['segments']) else '')
            start, end = cursor, cursor + len(block)
            piece = ''.join(original[i] for i in range(start, end) if not mask[i])
            paragraph_ranges.append({'source_paragraph': p['source_paragraph'], 'original_spoken_paragraph_index': p['paragraph'], 'source_start': start, 'source_end_exclusive': end, 'retained_text': piece, 'original_text': p['text']})
            cursor = end
        assert cursor == len(original)
        assert ''.join(p['retained_text'] for p in paragraph_ranges) == narration
        for q in quotes:
            q['source_docx_paragraphs'] = [p['source_paragraph'] for p in paragraph_ranges if p['source_start'] < q['source_end_exclusive'] and p['source_end_exclusive'] > q['source_start']]
        # Complete paragraph sentences stay whole; clauses without terminal
        # punctuation merge with following source paragraphs without rewriting.
        units = []
        pending = None
        fragments = []
        for p in paragraph_ranges:
            piece = p['retained_text']
            if not piece:
                continue
            if not piece.strip():
                if pending is not None:
                    pending['text'] += piece
                elif units:
                    units[-1]['text'] += piece
                else:
                    pending = {'text': piece, 'source_docx_paragraphs': [], 'original_spoken_paragraph_indices': []}
                continue
            if pending is None:
                pending = {'text': '', 'source_docx_paragraphs': [], 'original_spoken_paragraph_indices': []}
            pending['text'] += piece
            pending['source_docx_paragraphs'].append(p['source_paragraph'])
            pending['original_spoken_paragraph_indices'].append(p['original_spoken_paragraph_index'])
            if re.search(r'[.!?]\s*$', piece):
                pending['unit_index'] = len(units) + 1
                units.append(pending)
                pending = None
            else:
                fragment_type = 'dialogue_reporting_lead_in' if re.search(r'\b(?:said|added|asked|whispered|murmured)\s*[, :]\s*$', piece) else 'original_cross_paragraph_sentence'
                fragments.append({'source_docx_paragraph': p['source_paragraph'], 'original_text': p['original_text'], 'retained_text': piece, 'type': fragment_type, 'action': 'preserved_verbatim_and_merged_with_following_narration_paragraph'})
        incomplete = []
        if pending is not None:
            if pending['text'].strip():
                incomplete.append(pending)
            elif units:
                units[-1]['text'] += pending['text']
        assert ''.join(u['text'] for u in units) + ''.join(u['text'] for u in incomplete) == narration
        long_units = [{'unit_index':u['unit_index'], 'character_count':len(u['text']), 'text':u['text'], 'source_docx_paragraphs':u['source_docx_paragraphs']} for u in units if len(u['text']) > MAX_CHARS]
        batches = []
        remaining = list(units)
        if version == '女版' and number == 1:
            assert len(remaining) >= 2
            first_batch = remaining[:2]
            first_text = ''.join(u['text'] for u in first_batch)
            assert re.sub(r'\s+', ' ', first_text).strip() == EXISTING_PLATFORM_TEXT
            batches.append(first_batch)
            remaining = remaining[2:]
        current = []
        length = 0
        for unit in remaining:
            if current and length + len(unit['text']) > MAX_CHARS:
                batches.append(current)
                current, length = [], 0
            current.append(unit)
            length += len(unit['text'])
        if current:
            batches.append(current)
        valid = not unmatched and not long_units and not incomplete
        group_records = []
        narration_cursor = 0
        for group_index, batch in enumerate(batches, 1):
            text = ''.join(u['text'] for u in batch)
            start, end = narration_cursor, narration_cursor + len(text)
            assert text == narration[start:end]
            name = f'大码{number:02d}-01-{group_index:02d}'
            txt_dir = BASE / '200字旁白分段' / version
            txt_dir.mkdir(parents=True, exist_ok=True)
            txt = txt_dir / f'{name}.txt'
            if valid:
                if txt.exists():
                    assert txt.read_text() == text, f'Conflicting existing narration TXT {txt}'
                else:
                    with txt.open('x', encoding='utf-8', newline='') as f:
                        f.write(text)
            reuse = version == '女版' and number == 1 and group_index == 1
            group = {
                'version': version, 'episode': number, 'group_index': group_index,
                'name': name, 'status': 'prepared' if valid else 'requires_review',
                'naming_status': 'planned_not_applied',
                'narration_text': text, 'text': text,
                'char_count': len(text), 'word_count': word_count(text),
                'real_lf_count': text.count('\n'), 'source_sha256': sha(text),
                'narration_start': start, 'narration_end_exclusive': end,
                'source_docx_paragraphs': list(dict.fromkeys(p for u in batch for p in u['source_docx_paragraphs'])),
                'source_english_segment_indices': list(dict.fromkeys(p for u in batch for p in u['original_spoken_paragraph_indices'])),
                'complete_sentence_units': batch,
                'text_file': str(txt), 'source_full_english_txt': str(source_path),
                'reused_existing_platform_first_generation': reuse,
                'submit_generation': not reuse,
                'download_one_result_only': True,
                'result_selection': 'shortest_duration_among_results_with_complete_narration_text',
                'platform_voice_asset': '大码女版' if version == '女版' else None,
            }
            if reuse:
                group['existing_platform_workspace_id'] = '23561838050060'
                group['existing_platform_text'] = EXISTING_PLATFORM_TEXT
                group['existing_platform_text_whitespace_equivalent'] = True
                group['existing_platform_candidate_count'] = 2
                group['existing_platform_displayed_duration_seconds'] = [6,6]
                group['existing_platform_reuse_note'] = 'Reuse the existing first generation; source LF preserved here, platform text uses one space between the same two source sentences. Choose the shortest actual-duration complete candidate; no new submission.'
            group_records.append(group)
            narration_cursor = end
        for index, group in enumerate(group_records):
            a = 0 if index == 0 else kept_indices[group['narration_start']]
            b = len(original) if index + 1 == len(group_records) else kept_indices[group_records[index+1]['narration_start']]
            group['original_source_interval_start'] = a
            group['original_source_interval_end_exclusive'] = b
            group['excludedquote_details'] = [q for q in quotes if a <= q['source_start'] < b]
        reconstructed = ''.join(g['narration_text'] for g in group_records)
        assert reconstructed == narration
        assert all(len(g['text']) <= MAX_CHARS for g in group_records) or long_units
        if valid:
            assert sum(len(g['text']) for g in group_records) == len(narration)
            assert sum(len(g['excludedquote_details']) for g in group_records) == len(quotes)
            assert all('"' not in g['text'] and '“' not in g['text'] and '”' not in g['text'] for g in group_records)
        episode_summary = {
            'version': version, 'episode': number, 'status': 'prepared' if valid else 'requires_review',
            'narration_character_count': len(narration), 'narration_word_count': word_count(narration),
            'group_count': len(group_records), 'max_group_characters': max(g['char_count'] for g in group_records),
            'excluded_quote_count': len(quotes), 'excluded_character_count_including_quotes': sum(len(q['excluded_text']) for q in quotes),
            'unmatched_quotes': unmatched, 'over_200_complete_sentence_units': long_units,
            'incomplete_terminal_units': incomplete, 'merged_fragments': fragments,
            'source_txt': str(source_path), 'source_sha256': sha(original),
            'narration_sha256': sha(narration), 'reconstructed_sha256': sha(reconstructed),
            'reconstruction_verbatim_verified': reconstructed == narration,
            'narration_full_text': narration,
        }
        all_groups.extend(group_records)
        all_episodes.append(episode_summary)
        audits.append({**episode_summary, 'excludedquote_details': quotes, 'retained_paragraphs': paragraph_ranges})

prepared = all(e['status'] == 'prepared' for e in all_episodes)
plan = {
    'scope': '女版及性转版完整前3集，仅双引号外英文旁白。双引号内全部排除，单引号缩写保留。',
    'status': 'prepared' if prepared else 'requires_review', 'model': 'seedtts',
    'maximum_input_characters': MAX_CHARS,
    'character_count_definition': 'len(narration_text), including spaces, punctuation and original real LF. No added whitespace or rewritten words.',
    'quote_exclusion_rule': 'Remove all matched straight double-quote or curly double-quote spans including opening and closing delimiters. Match across original paragraph boundaries. Apostrophes are not quote delimiters.',
    'grouping_rule': 'Keep complete original narration paragraphs together, merge original cross-paragraph clauses and dialogue-reporting fragments with following narration, then greedily combine contiguous complete units to <=200 characters. Do not split a sentence. Female EP1 group1 is locked to the first two source sentences for reuse.',
    'reconstruction_rule': 'Concatenate each episode groups[].narration_text in order with no added separators; equals the full source TXT without its final LF after removal of matched dialogue quote spans only. All outside-quote whitespace is preserved.',
    'download_rule': 'Download exactly one complete result per group: choose the candidate with shortest measured duration among those containing the complete narration_text. An incomplete candidate is not eligible. No complete candidate means regenerate.',
    'naming_rule': '大码EE-01-SS, where EE is episode and SS is the narration-group number. Versions use separate output folders. Names are planned until applied to actual downloads.',
    'total_group_count': len(all_groups),
    'existing_group_reuse_count': sum(g['reused_existing_platform_first_generation'] for g in all_groups),
    'planned_new_generation_count': sum(g['submit_generation'] for g in all_groups),
    'total_narration_characters': sum(e['narration_character_count'] for e in all_episodes),
    'total_narration_words': sum(e['narration_word_count'] for e in all_episodes),
    'max_group_characters': max(g['char_count'] for g in all_groups),
    'total_excluded_quote_count': sum(e['excluded_quote_count'] for e in all_episodes),
    'all_episodes_reconstruct_verbatim': all(e['reconstruction_verbatim_verified'] for e in all_episodes),
    'unmatched_quote_count': sum(len(e['unmatched_quotes']) for e in all_episodes),
    'over_200_complete_sentence_count': sum(len(e['over_200_complete_sentence_units']) for e in all_episodes),
    'episodes': all_episodes, 'groups': all_groups,
}
(BASE / '200字旁白生成计划.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
(BASE / '台词排除核验.json').write_text(json.dumps({'status':plan['status'], 'source_whitespace_preserved':True, 'total_excluded_quote_count':plan['total_excluded_quote_count'], 'unmatched_quote_count':plan['unmatched_quote_count'], 'over_200_complete_sentence_count':plan['over_200_complete_sentence_count'], 'episodes':audits}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
old = BASE / '200字分段生成计划.json'
if old.exists():
    old_data = json.loads(old.read_text())
    old_data['status'] = 'superseded_do_not_submit'
    old_data['superseded_reason'] = 'Latest user instruction excludes all dialogue within double quotes and requires complete sentences.'
    old_data['replacement_plan'] = str(BASE / '200字旁白生成计划.json')
    old.write_text(json.dumps(old_data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({k:v for k,v in plan.items() if k not in ['episodes','groups']}, ensure_ascii=False, indent=2))
for e in all_episodes:
    print(e['version'],e['episode'],'groups',e['group_count'],'chars',e['narration_character_count'],'words',e['narration_word_count'],'max',e['max_group_characters'],'fragments',len(e['merged_fragments']))
