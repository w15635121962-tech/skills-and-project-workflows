from pathlib import Path
import zipfile, xml.etree.ElementTree as ET, re, json, hashlib

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / '完整剧本/我不再做教父的大码人形抱枕EN.docx'
ORDER = [16, 17, 18, 19, 7, 8, 1, 2, 3]
EXPECTED = {1:234, 2:187, 3:223, 7:220, 8:102, 16:194, 17:244, 18:200, 19:207}
NS = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
TAG = '{' + NS['w'] + '}'
WORD = re.compile(r"[A-Za-z0-9]+(?:[’'\-][A-Za-z0-9]+)*")
SHA = lambda v: hashlib.sha256(v.encode('utf-8') if isinstance(v,str) else v).hexdigest()
EXCEPTIONS = {
    248: 'The screen showed "ALLIE"—Alessia\'s private nickname.',
    249: 'The "Ellie" he\'d slurred last night suddenly sounded a lot more like "Allie."',
    505: 'Every page had "Mr. Bellandi" written on it.',
}

def write_checked(path, text):
    if path.exists():
        assert path.read_text() == text, f'Conflicting existing file: {path}'
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('x', encoding='utf-8', newline='') as f:
            f.write(text)
    assert path.read_text() == text

with zipfile.ZipFile(SOURCE) as z:
    tree = ET.fromstring(z.read('word/document.xml'))
episodes = {}
current = None
for ix, p in enumerate(tree.findall('.//w:body/w:p', NS), 1):
    raw = ''.join((e.text or '') if e.tag == TAG+'t' else '\n' if e.tag in [TAG+'br',TAG+'cr'] else '\t' if e.tag == TAG+'tab' else '' for e in p.iter())
    text = raw.strip()
    m = re.fullmatch(r'Episode\s+(\d+)', text, re.I)
    if m:
        current = int(m.group(1))
        episodes[current] = {'header':text, 'header_docx_paragraph':ix, 'blocks':[], 'omitted':[]}
        continue
    if current not in ORDER:
        continue
    reason = 'blank_source_paragraph' if not text else 'Chinese_visual_direction' if re.search(r'[\u3400-\u9fff]', text) else 'scene_divider' if re.fullmatch(r'[-–—_=\s]+', text) else None
    if reason:
        if reason == 'Chinese_visual_direction':
            assert text.startswith('【') and text.endswith('】'), (ix,text)
        episodes[current]['omitted'].append({'docx_paragraph':ix,'text':raw,'reason':reason})
        continue
    episodes[current]['blocks'].append({'docx_paragraph':ix,'raw_source_text':raw,'english_text':text})

old_audit_path = ROOT / '配音制作_前3集/制作资料/台词排除核验.json'
old_plan_path = ROOT / '配音制作_前3集/制作资料/200字旁白生成计划.json'
old_audit = {e['episode']:e for e in json.loads(old_audit_path.read_text())['episodes'] if e['version']=='女版'}
old_plan = json.loads(old_plan_path.read_text())
manifest = {
    'project':'我不再做教父的大码人形抱枕', 'version':'女版',
    'scope_episode_order':ORDER, 'source_docx':str(SOURCE), 'source_docx_sha256':SHA(SOURCE.read_bytes()),
    'output_kind':'English narration only; exclude character dialogue and quoted message dialogue',
    'extraction_rules':[
        'Preserve narration English words, punctuation, order, paragraph separators and manual line breaks.',
        'Trim only outer source-paragraph whitespace, matching existing EP01–03 preparation.',
        'Exclude headings, blank source paragraphs, scene dividers and Chinese visual directions.',
        'Remove paired double-quoted role and message dialogue, preserving whitespace outside removed spans.',
        'Preserve narrative quoted names/labels in source paragraphs 248, 249 and 505.',
        'Retain reporting fragments verbatim; combine with following original narration for TTS without rewriting.',
        'EP01–03 reuse existing narration segment texts; other episodes group contiguous complete narration units up to 200 input characters.',
    ],
    'prior_policy_sources':[str(ROOT/'配音制作_前3集/使用说明.txt'),str(old_audit_path),str(old_plan_path)],
    'naming_rule':'大码女版枕头EE-SS-01; EE is episode, SS is this narration sequence, 01 is first take. SS is NOT an asserted original Jumeng storyboard number.',
    'episodes':[], 'groups':[],
}

for number in ORDER:
    ep = episodes[number]
    blocks = ep['blocks']
    full = '\n'.join(b['english_text'] for b in blocks)
    cursor = 0
    for i,b in enumerate(blocks):
        b['source_start'] = cursor
        b['source_end_exclusive'] = cursor + len(b['english_text'])
        cursor = b['source_end_exclusive'] + (i+1 < len(blocks))
    assert cursor == len(full)
    quotes, opened = [], None
    for i,c in enumerate(full):
        if opened is None:
            if c in ['"','“']:
                opened = (c,i)
            elif c == '”':
                raise ValueError(('Unmatched quote',number,i))
        elif (opened[0]=='"' and c=='"') or (opened[0]=='“' and c=='”'):
            a,z = opened[1], i+1
            touched = [b for b in blocks if b['source_start'] < z and b['source_end_exclusive'] > a]
            keep = len(touched)==1 and touched[0]['docx_paragraph'] in EXCEPTIONS
            if keep:
                assert touched[0]['english_text'] == EXCEPTIONS[touched[0]['docx_paragraph']]
            quotes.append({'source_start':a,'source_end_exclusive':z,'text':full[a:z],'docx_paragraphs':[b['docx_paragraph'] for b in touched],'action':'retain_narrative_term' if keep else 'exclude_role_or_message_dialogue'})
            opened = None
    assert opened is None
    mask = [True]*len(full)
    for q in quotes:
        if q['action'].startswith('exclude'):
            mask[q['source_start']:q['source_end_exclusive']] = [False]*(q['source_end_exclusive']-q['source_start'])
    narration = ''.join(c for i,c in enumerate(full) if mask[i])
    assert len(WORD.findall(narration)) == EXPECTED[number]
    assert not re.search(r'[\u3400-\u9fff]', narration)
    records, queries = [], []
    for b in blocks:
        a,z = b['source_start'], b['source_end_exclusive']
        kept = ''.join(full[i] for i in range(a,z) if mask[i])
        separator = '\n' if z < len(full) else ''
        records.append({**b,'narration_retained_text':kept,'narration_with_original_separator':kept+separator})
        if kept.strip() and not re.search(r'[.!?]\s*$', kept):
            queries.append({'docx_paragraph':b['docx_paragraph'],'retained_text':kept,'reason':'Source clause or reporting lead-in lacks terminal punctuation; preserved verbatim, merged with following narration rather than rewritten.'})
    assert ''.join(p['narration_with_original_separator'] for p in records) == narration
    comparison = None
    if number <= 3:
        old_full = ROOT/f'配音制作_前3集/制作资料/女版/女版_第{number:02d}集_纯英文全文.txt'
        assert full == old_full.read_text().removesuffix('\n')
        assert narration == old_audit[number]['narration_full_text']
        previous = [g for g in old_plan['groups'] if g['version']=='女版' and g['episode']==number]
        assert ''.join(g['source_text'] for g in previous) == narration
        prepared = [{'source_text':g['source_text'],'generation_text':g.get('generation_text',g['text']),'source_docx_paragraphs':g['source_docx_paragraphs'],'previous_name':g['name'],'previous_text_file':g['text_file']} for g in previous]
        comparison = {'full_source_path':str(old_full),'full_source_exact_match':True,'narration_audit_path':str(old_audit_path),'narration_exact_match':True,'existing_segment_count':len(previous),'source_texts_reconstruct_verbatim':True,'generation_only_trims_chunk_outer_whitespace':all(g.get('generation_text',g['text'])==g['source_text'].strip() for g in previous)}
    else:
        units, pending, pending_paragraphs = [], '', []
        for p in records:
            piece = p['narration_with_original_separator']
            if not piece.strip() and not pending and units:
                units[-1]['source_text'] += piece
                continue
            pending += piece
            pending_paragraphs.append(p['docx_paragraph'])
            if piece.strip() and re.search(r'[.!?]["”]?\s*$', piece):
                units.append({'source_text':pending,'source_docx_paragraphs':pending_paragraphs})
                pending, pending_paragraphs = '', []
        if pending.strip():
            raise ValueError(('Incomplete narration ending',number,pending))
        if pending:
            units[-1]['source_text'] += pending
        assert ''.join(u['source_text'] for u in units) == narration
        prepared, text, ps = [], '', []
        for u in units:
            assert len(u['source_text'].strip())<=200, ('Single sentence unit exceeds limit',number,u)
            if text and len((text+u['source_text']).strip())>200:
                prepared.append({'source_text':text,'generation_text':text.strip(),'source_docx_paragraphs':list(dict.fromkeys(ps))})
                text, ps = '', []
            text += u['source_text']
            ps += u['source_docx_paragraphs']
        if text:
            prepared.append({'source_text':text,'generation_text':text.strip(),'source_docx_paragraphs':list(dict.fromkeys(ps))})
    assert ''.join(g['source_text'] for g in prepared) == narration
    episode_groups = []
    for seq,g in enumerate(prepared,1):
        name = f'大码女版枕头{number:02d}-{seq:02d}-01'
        text = g['generation_text']
        assert 0 < len(text) <= 200
        assert text == g['source_text'].strip()
        path = OUT/'分段'/f'{name}.txt'
        write_checked(path,text)
        row = {**g,'episode':number,'narration_sequence':seq,'take':1,'basename':name,'planned_audio_filename':name+'.mp3','text_file':str(path),'characters':len(text),'words':len(WORD.findall(text)),'generation_text_sha256':SHA(text),'source_text_sha256':SHA(g['source_text']),'status':'text_verified_not_generated','original_storyboard_number':None,'sequence_mapping_basis':'Existing female narration segment order' if number<=3 else 'Original English narration paragraph order, contiguous complete units <=200 characters'}
        episode_groups.append(row)
        manifest['groups'].append(row)
    full_path = OUT/f'女版_EP{number:02d}_英文旁白.txt'
    write_checked(full_path,narration)
    manifest['episodes'].append({'episode':number,'source_heading':ep['header'],'source_heading_docx_paragraph':ep['header_docx_paragraph'],'source_path':str(SOURCE),'output_path':str(full_path),'output_sha256':SHA(narration),'narration_characters':len(narration),'narration_words':len(WORD.findall(narration)),'segment_count':len(episode_groups),'excluded_dialogue_quote_count':sum(q['action'].startswith('exclude') for q in quotes),'retained_narrative_quote_count':sum(q['action'].startswith('retain') for q in quotes),'quoted_spans':quotes,'original_paragraphs_and_retained_narration':records,'excluded_nonspoken_source_paragraphs':ep['omitted'],'possible_queries':queries,'comparison_to_existing_EP01_03':comparison,'source_reconstruction_verbatim':True,'generation_only_trims_segment_outer_whitespace':True})

manifest['totals']={'episode_count':len(ORDER),'segment_count':len(manifest['groups']),'narration_words':sum(e['narration_words'] for e in manifest['episodes']),'narration_characters':sum(e['narration_characters'] for e in manifest['episodes']),'generation_characters':sum(g['characters'] for g in manifest['groups']),'excluded_dialogue_quote_count':sum(e['excluded_dialogue_quote_count'] for e in manifest['episodes']),'retained_narrative_quote_count':sum(e['retained_narrative_quote_count'] for e in manifest['episodes']),'all_text_files_readback_exact':True,'source_docx_unchanged':SHA(SOURCE.read_bytes())==manifest['source_docx_sha256']}
write_checked(OUT/'manifest.json',json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'manifest':str(OUT/'manifest.json'),'totals':manifest['totals'],'episodes':[{k:e[k] for k in ['episode','narration_words','narration_characters','segment_count']} for e in manifest['episodes']]},ensure_ascii=False,indent=2))
