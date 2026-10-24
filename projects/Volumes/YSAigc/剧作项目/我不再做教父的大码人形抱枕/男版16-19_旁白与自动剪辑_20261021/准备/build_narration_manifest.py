from pathlib import Path
import hashlib
import json
import re
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / '性转版/没有你我睡不着（大码性转）-EN.docx'
ORDER = [16, 17, 18, 19]
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
TAG = '{' + NS['w'] + '}'
WORD = re.compile(r"[A-Za-z0-9]+(?:[’'\-][A-Za-z0-9]+)*")


def sha(value):
    return hashlib.sha256(value.encode('utf-8') if isinstance(value, str) else value).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, ensure_ascii=False, indent=2) + '\n' if not isinstance(value, str) else value
    if path.exists():
        assert path.read_text(encoding='utf-8') == text, 'Refusing conflicting overwrite: ' + str(path)
    else:
        path.write_text(text, encoding='utf-8')
    assert path.read_text(encoding='utf-8') == text


original_hash = sha(SOURCE.read_bytes())
with zipfile.ZipFile(SOURCE) as z:
    tree = ET.fromstring(z.read('word/document.xml'))
paras = []
for index, p in enumerate(tree.findall('.//w:body/w:p', NS), 1):
    raw = ''.join((e.text or '') if e.tag == TAG + 't' else '\n' if e.tag in [TAG + 'br', TAG + 'cr'] else '\t' if e.tag == TAG + 'tab' else '' for e in p.iter())
    paras.append({'docx_paragraph': index, 'raw_source_text': raw, 'text': raw.strip()})

episodes = {}
current = None
for row in paras:
    if re.fullmatch(r'\d{1,2}', row['text']):
        current = int(row['text'])
        if current in ORDER:
            episodes[current] = {'heading_docx_paragraph': row['docx_paragraph'], 'blocks': [], 'excluded_nonspoken': []}
        continue
    if current not in ORDER:
        continue
    text = row['text']
    reason = 'blank_source_paragraph' if not text else 'Chinese_visual_direction' if re.search(r'[\u3400-\u9fff]', text) else 'scene_divider' if re.fullmatch(r'[-–—_.=\s]+', text) else None
    if reason:
        episodes[current]['excluded_nonspoken'].append({**row, 'reason': reason})
    else:
        episodes[current]['blocks'].append(row)

manifest = {
    'project': '我不再做教父的大码人形抱枕',
    'version': '男版',
    'scope_episode_order': ORDER,
    'source_docx': str(SOURCE),
    'source_docx_sha256': original_hash,
    'reference_voice': '/Users/zc/Downloads/男版.wav',
    'output_kind': 'English original narration only; dialogue in paired double quotes excluded',
    'naming_rule': '大码男版枕头EE-SS-01: EE = original male episode; SS = sequential narration segment, not asserted Jumeng storyboard number; 01 = first take.',
    'naming_evidence': str(ROOT / '对标音色旁白制作_20261020/文本核验/manifest.json'),
    'episode_mapping': 'Male English document numeric headings 16–19 directly match male EP16–EP19 media folders; no female episode offset is used.',
    'generation_char_limit': 200,
    'extraction_rules': [
        'Preserve original English words, punctuation, case and order.',
        'Exclude titles, blank source paragraphs, Chinese visual notes and paired double-quoted character/message dialogue.',
        'Do not discard unquoted reporting clauses; preserve exactly and group with later complete narration as in previous narration workflow.',
        'Retain original paragraph separators in source_text; generation_text only trims segment outer whitespace.',
        'Group contiguous complete narration units to at most 200 input characters; do not rewrite.',
    ],
    'episodes': [],
    'groups': [],
}

for number in ORDER:
    ep = episodes[number]
    blocks = ep['blocks']
    full = '\n'.join(b['text'] for b in blocks)
    cursor = 0
    for b in blocks:
        b['source_start'] = cursor
        b['source_end_exclusive'] = cursor + len(b['text'])
        cursor = b['source_end_exclusive'] + 1

    quotes = []
    opened = None
    for i, char in enumerate(full):
        if opened is None:
            if char in ['"', '“']:
                opened = (char, i)
            elif char == '”':
                raise ValueError(('Unmatched quote', number, i))
        elif (opened[0] == '"' and char == '"') or (opened[0] == '“' and char == '”'):
            a, z = opened[1], i + 1
            quotes.append({'source_start': a, 'source_end_exclusive': z, 'text': full[a:z], 'docx_paragraphs': [b['docx_paragraph'] for b in blocks if b['source_start'] < z and b['source_end_exclusive'] > a], 'action': 'exclude_role_or_message_dialogue'})
            opened = None
    assert opened is None
    mask = [True] * len(full)
    for q in quotes:
        mask[q['source_start']:q['source_end_exclusive']] = [False] * (q['source_end_exclusive'] - q['source_start'])
    narration = ''.join(c for i, c in enumerate(full) if mask[i])
    assert not re.search(r'[\u3400-\u9fff]', narration)

    records = []
    units, pending, pending_paragraphs = [], '', []
    for b in blocks:
        a, z = b['source_start'], b['source_end_exclusive']
        retained = ''.join(full[i] for i in range(a, z) if mask[i])
        piece = retained + ('\n' if z < len(full) else '')
        records.append({**b, 'narration_retained_text': retained, 'narration_with_original_separator': piece})
        if not piece.strip() and not pending and units:
            units[-1]['source_text'] += piece
            continue
        pending += piece
        pending_paragraphs.append(b['docx_paragraph'])
        if piece.strip() and re.search(r'[.!?]["”]?\s*$', piece):
            units.append({'source_text': pending, 'source_docx_paragraphs': pending_paragraphs})
            pending, pending_paragraphs = '', []
    if pending.strip():
        raise ValueError(('Incomplete ending', number, pending))
    if pending:
        units[-1]['source_text'] += pending
    assert ''.join(u['source_text'] for u in units) == narration

    prepared, text, indices = [], '', []
    for u in units:
        assert len(u['source_text'].strip()) <= 200, ('Long indivisible sentence', number, u)
        if text and len((text + u['source_text']).strip()) > 200:
            prepared.append({'source_text': text, 'generation_text': text.strip(), 'source_docx_paragraphs': list(dict.fromkeys(indices))})
            text, indices = '', []
        text += u['source_text']
        indices += u['source_docx_paragraphs']
    if text:
        prepared.append({'source_text': text, 'generation_text': text.strip(), 'source_docx_paragraphs': list(dict.fromkeys(indices))})
    assert ''.join(g['source_text'] for g in prepared) == narration

    for seq, g in enumerate(prepared, 1):
        basename = f'大码男版枕头{number:02d}-{seq:02d}-01'
        text_file = OUT / '分段' / f'{basename}.txt'
        save(text_file, g['generation_text'])
        manifest['groups'].append({**g, 'episode': number, 'narration_sequence': seq, 'take': 1, 'basename': basename, 'planned_audio_filename': basename + '.mp3', 'planned_audio_path': str(OUT.parent / '音频' / f'第{number:02d}集' / (basename + '.mp3')), 'text_file': str(text_file), 'characters': len(g['generation_text']), 'words': len(WORD.findall(g['generation_text'])), 'generation_text_sha256': sha(g['generation_text']), 'source_text_sha256': sha(g['source_text']), 'status': 'text_verified_not_generated', 'original_storyboard_number': None})

    text_file = OUT / f'男版_EP{number:02d}_英文纯旁白.txt'
    save(text_file, narration)
    ep_numbered = '\n'.join(f"P{b['docx_paragraph']:04d}\t{b['text']}" for b in blocks) + '\n'
    save(OUT / f'男版_EP{number:02d}_源段落证据.txt', ep_numbered)
    manifest['episodes'].append({'episode': number, 'heading_docx_paragraph': ep['heading_docx_paragraph'], 'source_path': str(SOURCE), 'source_body_docx_paragraphs': [b['docx_paragraph'] for b in blocks], 'output_path': str(text_file), 'output_sha256': sha(narration), 'narration_characters': len(narration), 'narration_words': len(WORD.findall(narration)), 'segment_count': len(prepared), 'excluded_dialogue_quote_count': len(quotes), 'quoted_spans': quotes, 'original_paragraphs_and_retained_narration': records, 'excluded_nonspoken_source_paragraphs': ep['excluded_nonspoken'], 'source_reconstruction_verbatim': True, 'generation_only_trims_segment_outer_whitespace': True})

manifest['totals'] = {'episode_count': len(ORDER), 'segment_count': len(manifest['groups']), 'narration_words': sum(e['narration_words'] for e in manifest['episodes']), 'narration_characters': sum(e['narration_characters'] for e in manifest['episodes']), 'generation_characters': sum(g['characters'] for g in manifest['groups']), 'excluded_dialogue_quote_count': sum(e['excluded_dialogue_quote_count'] for e in manifest['episodes']), 'source_docx_unchanged': sha(SOURCE.read_bytes()) == original_hash}
save(OUT / 'narration_manifest.json', manifest)
print(json.dumps({'manifest': str(OUT / 'narration_manifest.json'), 'totals': manifest['totals'], 'episodes': [{k: e[k] for k in ['episode', 'narration_words', 'segment_count', 'excluded_dialogue_quote_count']} for e in manifest['episodes']]}, ensure_ascii=False, indent=2))
