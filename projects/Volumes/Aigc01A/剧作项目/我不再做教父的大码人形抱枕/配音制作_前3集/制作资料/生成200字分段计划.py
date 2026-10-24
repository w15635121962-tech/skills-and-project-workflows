#!/usr/bin/env python3
"""Prepare <=200-character TTS groups; preserve complete source by direct concatenation."""
from pathlib import Path
import hashlib
import json
import re

BASE = Path(__file__).resolve().parent
PROJECT_ROOT = BASE.parents[1]
MAX_CHARS = 200
WORD_RE = re.compile(r"[A-Za-z0-9]+(?:[’'\-][A-Za-z0-9]+)*")


def sha(data):
    if isinstance(data, str):
        data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()


def split_long_unit(text):
    # Current source paragraphs fit whole; this is a preserving fallback.
    parts = []
    while len(text) > MAX_CHARS:
        prefix = text[:MAX_CHARS]
        sentence_ends = list(re.finditer(r'''[.!?]["'”’]?\s+''', prefix))
        if sentence_ends:
            cut = sentence_ends[-1].end()
        else:
            boundaries = list(re.finditer(r'\s+', prefix))
            cut = boundaries[-1].end() if boundaries else MAX_CHARS
        assert 0 < cut <= MAX_CHARS
        parts.append(text[:cut])
        text = text[cut:]
    if text:
        parts.append(text)
    return parts


groups = []
episode_reports = []
for version in ['女版', '性转版']:
    manifest_path = BASE / version / f'{version}_前3集_配音清单.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for episode in manifest['episodes']:
        number = episode['episode']
        txt_path = BASE / version / f'{version}_第{number:02d}集_纯英文全文.txt'
        raw = txt_path.read_text(encoding='utf-8')
        original = raw.removesuffix('\n')
        paragraphs = episode['segments']
        assert original == '\n'.join(p['text'] for p in paragraphs)
        units = []
        source_offset = 0
        split_paragraphs = 0
        for index, paragraph in enumerate(paragraphs):
            unit = paragraph['text'] + ('\n' if index + 1 < len(paragraphs) else '')
            fragments = split_long_unit(unit)
            split_paragraphs += int(len(fragments) > 1)
            for fragment in fragments:
                units.append({
                    'text': fragment,
                    'source_paragraph': paragraph['source_paragraph'],
                    'original_paragraph_index': paragraph['paragraph'],
                    'start': source_offset,
                    'end': source_offset + len(fragment),
                })
                source_offset += len(fragment)
        assert source_offset == len(original)
        batches = []
        current = []
        current_length = 0
        for unit in units:
            if current and current_length + len(unit['text']) > MAX_CHARS:
                batches.append(current)
                current = []
                current_length = 0
            current.append(unit)
            current_length += len(unit['text'])
        if current:
            batches.append(current)
        episode_groups = []
        for index, batch in enumerate(batches, 1):
            source_text = ''.join(unit['text'] for unit in batch)
            assert 0 < len(source_text) <= MAX_CHARS
            basename = f'大码{number:02d}-01-{index:02d}'
            text_dir = BASE / '200字分段' / version
            text_dir.mkdir(parents=True, exist_ok=True)
            text_path = text_dir / f'{basename}.txt'
            encoded = source_text.encode('utf-8')
            # Never overwrite unrelated or conflicting same-name group files.
            if text_path.exists():
                assert text_path.read_bytes() == encoded, f'Conflicting existing group TXT: {text_path}'
            else:
                with text_path.open('xb') as f:
                    f.write(encoded)
            record = {
                'version': version,
                'episode': number,
                'group_index': index,
                'planned_basename': basename,
                'status': 'prepared',
                'naming_status': 'planned_not_applied',
                'source_text': source_text,
                'source_sha256': sha(source_text),
                'character_count': len(source_text),
                'word_count': len(WORD_RE.findall(source_text)),
                'real_lf_count': source_text.count('\n'),
                'source_char_start': batch[0]['start'],
                'source_char_end_exclusive': batch[-1]['end'],
                'source_docx_paragraphs': list(dict.fromkeys(unit['source_paragraph'] for unit in batch)),
                'original_spoken_paragraph_indices': list(dict.fromkeys(unit['original_paragraph_index'] for unit in batch)),
                'text_file': str(text_path),
                'source_full_txt': str(txt_path),
                'project_output_dir': str(BASE.parent / '音频' / version),
                'download_one_result_only': True,
                'result_selection': 'shortest_duration_among_results_with_complete_source_content',
            }
            assert source_text == original[record['source_char_start']:record['source_char_end_exclusive']]
            assert text_path.read_bytes() == encoded
            episode_groups.append(record)
            groups.append(record)
        recovered = ''.join(g['source_text'] for g in episode_groups)
        assert recovered == original
        assert sha(recovered) == sha(original)
        assert sum(g['character_count'] for g in episode_groups) == len(original)
        episode_reports.append({
            'version': version,
            'episode': number,
            'group_count': len(episode_groups),
            'max_group_characters': max(g['character_count'] for g in episode_groups),
            'source_character_count': len(original),
            'source_word_count': episode['word_count'],
            'source_full_txt': str(txt_path),
            'source_full_txt_sha256': sha(txt_path.read_bytes()),
            'source_text_sha256': sha(original),
            'reconstructed_source_sha256': sha(recovered),
            'reconstruction_verbatim_verified': True,
            'original_paragraphs_split_for_length': split_paragraphs,
        })

plan = {
    'scope': '女版与性转版完整前3集，每次英文输入严格不超过200字符，保留所有英文原文与原序。',
    'status': 'prepared',
    'model': 'seedtts',
    'max_characters_per_input': MAX_CHARS,
    'character_count_definition': 'Python len(source_text): includes all spaces, punctuation and real LF line breaks; no normalization or rewriting.',
    'grouping_rule': 'Greedily combine contiguous original paragraphs up to 200 characters. Original LF separators stay with the preceding paragraph. Split an individual over-limit paragraph only at sentence/word boundaries while preserving every character.',
    'reconstruction_rule': 'For each version+episode, concatenate groups[*].source_text in group_index order WITHOUT adding separators. Result equals full-English source TXT with only its final LF removed.',
    'download_rule': 'Each group downloads exactly one result: the shortest-duration result among candidates verified to contain the complete source_text in original order. If no candidate is complete, download none and regenerate.',
    'naming_rule': '大码EE-01-SS; EE is episode, SS is group_index. Version folders separate identical basenames. Planned names have not been applied to generated files.',
    'total_group_count': len(groups),
    'max_group_characters': max(g['character_count'] for g in groups),
    'total_source_characters': sum(e['source_character_count'] for e in episode_reports),
    'total_source_words': sum(e['source_word_count'] for e in episode_reports),
    'all_episodes_reconstruct_verbatim': all(e['reconstruction_verbatim_verified'] for e in episode_reports),
    'episodes': episode_reports,
    'groups': groups,
}
assert plan['total_source_characters'] == sum(g['character_count'] for g in groups)
assert len({(g['version'], g['planned_basename']) for g in groups}) == len(groups)
out_path = BASE / '200字分段生成计划.json'
out_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(out_path)
print(json.dumps({k:v for k,v in plan.items() if k not in ['groups']}, ensure_ascii=False, indent=2))
