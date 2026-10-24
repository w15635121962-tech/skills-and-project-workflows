#!/usr/bin/env python3
"""Prepare semantic vertical captions without altering source media or old SRTs.

The current corrected SRT wording is authoritative for this edit. Whisper word
times are approximate evidence, not a new transcription or forced alignment.
"""
from pathlib import Path
import argparse
import collections
import hashlib
import itertools
import json
import math
import re

HERE = Path(__file__).resolve().parent
DATA = HERE.parent
OLD = DATA / 'SRT字幕制作_20261018'
AUDIT = DATA / '音频内容与顺序核验_20261018'
LEX = re.compile(r"[^\W_]+(?:'[^\W_]+)*", re.UNICODE)

# Explicit editorial boundaries, never a character-count slicing algorithm.
# Joining each entry with spaces restores the unchanged corrected sentence.
SPLITS = {
    'Mafia don Matteo Bellandi suffered from insomnia, so I became his human pillow.':
        ['Mafia don Matteo Bellandi suffered from insomnia,', 'so I became his human pillow.'],
    'No matter how wild it got, come late night, he tossed them from his bed.':
        ['No matter how wild it got, come late night,', 'he tossed them from his bed.'],
    "On renewal day, his mother slid me a half-pay contract, certain I wouldn't dare refuse.":
        ['On renewal day, his mother slid me a half-pay contract,', "certain I wouldn't dare refuse."],
    'Draped in a silk robe, Alessia Varenna sat bedside, cheeks still flushed.':
        ['Draped in a silk robe,', 'Alessia Varenna sat bedside, cheeks still flushed.'],
    'Alessia looked me up and down, from my oversized black tee to my fat waist.':
        ['Alessia looked me up and down,', 'from my oversized black tee to my fat waist.'],
    "I looked down and saw the lipstick mark on Matteo's neck, bright and glaring, like a mark staking a claim.":
        ["I looked down and saw the lipstick mark on Matteo's neck,", 'bright and glaring, like a mark staking a claim.'],
    "In ten years of sharing a bed, he'd never spent a night outside his security perimeter.":
        ['In ten years of sharing a bed,', "he'd never spent a night outside his security perimeter."],
    'Yet, half an hour later, a Bellandi car stopped outside my apartment building.':
        ['Yet, half an hour later,', 'a Bellandi car stopped outside my apartment building.'],
    'Matteo changed into his black pajamas and lay straight on my small pale bed.':
        ['Matteo changed into his black pajamas', 'and lay straight on my small pale bed.'],
    'He looked wildly out of place among my pale pink sheets, plush pillows, and plushies.':
        ['He looked wildly out of place', 'among my pale pink sheets, plush pillows, and plushies.'],
    'Picky as he was, he slept sounder here than on any luxury mattress at the Bellandi estate.':
        ['Picky as he was, he slept sounder here', 'than on any luxury mattress at the Bellandi estate.'],
    'Claiming to feel nothing for me, he still held me tight, leaving not an inch between us.':
        ['Claiming to feel nothing for me,', 'he still held me tight, leaving not an inch between us.'],
    'At 18, Matteo was kidnapped by rivals and locked in a basement for six whole days.':
        ['At 18, Matteo was kidnapped by rivals', 'and locked in a basement for six whole days.'],
    'Whenever the lights went out, he thought he was trapped down there again.':
        ['Whenever the lights went out,', 'he thought he was trapped down there again.'],
    'His therapist suggested that Bellandis find him a calm, stable companion his age.':
        ['His therapist suggested', 'that Bellandis find him a calm, stable companion his age.'],
    "After she died, the family's education trust funded my schooling, landing me on the candidate list.":
        ["After she died, the family's education trust funded my schooling,", 'landing me on the candidate list.'],
    'At the interview, in ill-fitting old clothes, I fell asleep, curled in the hallway corner.':
        ['At the interview, in ill-fitting old clothes,', 'I fell asleep, curled in the hallway corner.'],
    'Flanked by bodyguards, Matteo bypassed the crowd and pointed straight at me.':
        ['Flanked by bodyguards,', 'Matteo bypassed the crowd and pointed straight at me.'],
    'Her name was Vittoria Blackwood, and I was the only cure for her insomnia.':
        ['Her name was Vittoria Blackwood,', 'and I was the only cure for her insomnia.'],
    'By then, she had fallen for some other man, staying awake for three days straight just chasing after him.':
        ['By then, she had fallen for some other man,', 'staying awake for three days straight just chasing after him.'],
    "Madam Blackwood slid the renewal contract toward me, knowing I'd sign it.":
        ['Madam Blackwood slid the renewal contract toward me,', "knowing I'd sign it."],
    "When I arrived at the Penthouse Suite late that night, Vittoria's lover hadn't left yet.":
        ['When I arrived at the Penthouse Suite late that night,', "Vittoria's lover hadn't left yet."],
    'Vittoria leaned against the headboard, desires still burning in her eyes as she looked at me.':
        ['Vittoria leaned against the headboard,', 'desires still burning in her eyes as she looked at me.'],
    'I stood aside, waiting for him to take the cash and leave like all the others.':
        ['I stood aside, waiting for him to take the cash', 'and leave like all the others.'],
    'Vittoria twirled the check, a rare flicker of shock in her eyes before it vanished.':
        ['Vittoria twirled the check,', 'a rare flicker of shock in her eyes before it vanished.'],
    "Surprised, I couldn't fathom why she suddenly wanted to come to my place.":
        ["Surprised, I couldn't fathom", 'why she suddenly wanted to come to my place.'],
    'But after sharing a bed for 10 years, having her over felt natural enough.':
        ['But after sharing a bed for 10 years,', 'having her over felt natural enough.'],
    "Back at my apartment, Vittoria slipped into the pajamas I'd kept for her.":
        ['Back at my apartment,', "Vittoria slipped into the pajamas I'd kept for her."],
    'One leg tossed over mine, arms wrapped around my neck, like I was an actual pillow to her.':
        ['One leg tossed over mine, arms wrapped around my neck,', 'like I was an actual pillow to her.'],
    "Wide awake, she sniffed around until her nose grazed my sensitive Adam's apple.":
        ['Wide awake, she sniffed around', "until her nose grazed my sensitive Adam's apple."],
    'The doctors suggested a companion to calm her nerves, so the Blackwoods went hunting for candidates.':
        ['The doctors suggested a companion to calm her nerves,', 'so the Blackwoods went hunting for candidates.'],
    'Exhausted from working odd jobs the day before, I dozed off while waiting.':
        ['Exhausted from working odd jobs the day before,', 'I dozed off while waiting.'],
    'She scanned the crowd with irritation, then locked her eyes on one person, me, asleep in the corner.':
        ['She scanned the crowd with irritation,', 'then locked her eyes on one person, me, asleep in the corner.'],
    'Yet as I grew from a boy into a man, Madame Blackwood began keeping a wary eye on me.':
        ['Yet as I grew from a boy into a man,', 'Madame Blackwood began keeping a wary eye on me.'],
    'Before she was even done messing around, I would knock on the door like clockwork.':
        ['Before she was even done messing around,', 'I would knock on the door like clockwork.'],
}

KEEP_PHRASES = ['don Matteo Bellandi', 'Alessia Varenna', 'Vittoria Blackwood',
                'Madam Blackwood', 'Madame Blackwood', 'Bellandi Hotel',
                'Bellandi estate', 'Blackwood heir', 'human pillow',
                'security perimeter', "Adam's apple", 'half-pay contract',
                '10-year contract', 'Penthouse Suite', 'three days straight',
                'the day before', 'black tee', "mob boss's", 'renewal contract',
                'just as', 'pulled me in', 'her head', 'black silk', 'too tense',
                'showed up', 'get any ideas', 'long legs', 'education trust',
                'No matter how wild it got']
WEAK_END = set('a an the of to in on at from for with by into than and but or so that had was would could'.split())


def read(p):
    return json.loads(p.read_text(encoding='utf-8'))


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def lexical(text):
    plain = text.replace('’', "'")
    return [{'text': text[m.start():m.end()], 'normalized': m.group().lower(),
             'char_start': m.start(), 'char_end': m.end()}
            for m in LEX.finditer(plain)]


def align(a, b):
    n, m = len(a), len(b)
    d = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1): d[i][0] = i
    for j in range(m + 1): d[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            d[i][j] = min(d[i-1][j]+1, d[i][j-1]+1,
                          d[i-1][j-1]+(a[i-1] != b[j-1]))
    i, j = n, m
    units = []
    while i or j:
        if i and j and a[i-1] == b[j-1] and d[i][j] == d[i-1][j-1]:
            units.append(([i-1], [j-1], 'match')); i -= 1; j -= 1
        elif i and j and d[i][j] == d[i-1][j-1]+1:
            units.append(([i-1], [j-1], 'recognized_word_differs')); i -= 1; j -= 1
        elif i and d[i][j] == d[i-1][j]+1:
            units.append(([i-1], [], 'delete_alignment_only')); i -= 1
        else:
            units.append(([], [j-1], 'insert_alignment_only')); j -= 1
    units.reverse()
    merged = []; k = 0
    while k < len(units):
        u = units[k]
        if k+1 < len(units) and u[2] == 'delete_alignment_only':
            v = units[k+1]
            if ([a[x] for x in u[0]+v[0]], [b[x] for x in v[1]]) == (['don', 'matteo'], ['donmeteo']):
                u = (u[0]+v[0], v[1], 'shared_name_interval'); k += 1
        merged.append(u); k += 1
    return merged


def wrap(text):
    words = text.split()
    protected = set()
    normalized = [w.strip('.,;:!?').lower() for w in words]
    for phrase in KEEP_PHRASES:
        p = phrase.lower().split()
        for i in range(len(words)-len(p)+1):
            if normalized[i:i+len(p)] == p:
                protected.update(range(i+1, i+len(p)))
    candidates = []
    for count in range(1, 4):
        for cuts in itertools.combinations(range(1, len(words)), count-1):
            if set(cuts) & protected: continue
            bounds = (0,) + cuts + (len(words),)
            lines = [' '.join(words[bounds[i]:bounds[i+1]]) for i in range(count)]
            if max(map(len, lines)) > 28: continue
            cost = count*60 + sum((len(line)-25)**2 for line in lines)
            cost += sum(400 for line in lines[:-1]
                        if line.split()[-1].strip('.,;:!?').lower() in WEAK_END)
            cost += 500 if count > 1 and len(lines[-1]) < 12 else 0
            candidates.append((cost, lines))
    if not candidates:
        raise ValueError('Needs an additional semantic boundary: '+text)
    return min(candidates, key=lambda x: x[0])[1]


def srt_text(path):
    chunks = re.split(r'\r?\n\s*\r?\n', path.read_text(encoding='utf-8-sig').strip())
    return ' '.join(' '.join(c.splitlines()[2:]) for c in chunks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, default=OLD/'字幕制作前快照.json')
    args = ap.parse_args()
    old = read(OLD/'SRT字幕校正与时间核验.json')
    snapshot = read(args.snapshot)
    comparison = read(AUDIT/'第二轮识别差异独立分类.json')
    by_name = {r['name']: r for r in comparison['rows']}
    snap_by_name = {t['name']: t for t in snapshot['timelines']}
    tracked = {str(Path(t['srt_path'])): digest(Path(t['srt_path'])) for t in old['timelines']}
    tracked[str(OLD/'SRT字幕校正与时间核验.json')] = digest(OLD/'SRT字幕校正与时间核验.json')
    timelines = []; flagged_short = []; wrapping_counts = collections.Counter()
    for t in old['timelines']:
        native_t = snap_by_name[t['timeline_name']]
        fps = float(native_t['fps'])
        clips = {Path(c['name']).stem: c for a in native_t['audio_tracks'] for c in a['items']}
        grouped = collections.OrderedDict()
        for cue in t['cues']:
            grouped.setdefault(Path(cue['audio_name']).stem, []).append(cue)
        assert ' '.join(c['text'] for c in t['cues']) == srt_text(Path(t['srt_path']))
        out = []; clip_entries = []
        for audio_name, original_cues in grouped.items():
            text = ' '.join(c['text'] for c in original_cues)
            clip = clips[audio_name]
            assert clip['left_offset'] == 0.0, 'Nonzero source-in requires explicit mapping review'
            r = by_name[audio_name]
            raw_path = Path(r['checkpoint']); tracked[str(raw_path)] = digest(raw_path)
            raw = read(raw_path)
            word_objects = [dict(w, segment_index=si, segment_word_index=wi)
                            for si, seg in enumerate(raw['segments'])
                            for wi, w in enumerate(seg.get('words', []))]
            dst = lexical(text)
            aw = [lexical(w['word'])[0]['normalized'] for w in word_objects]
            mappings = {}
            for di, ai, relation in align([x['normalized'] for x in dst], aw):
                assert di and ai, (audio_name, di, ai, relation)
                for k in di: mappings[k] = (ai, relation)
            assert len(mappings) == len(dst)
            source_duration = raw['decoded_duration_seconds']
            clip_start = clip['start']/fps
            clip_end = clip['end']/fps
            clip_length_source = (clip_end-clip_start)*1.1
            sentences = re.split(r'(?<=[.!?])\s+', text)
            semantic = []
            for sentence in sentences:
                parts = SPLITS.get(sentence, [sentence])
                assert ' '.join(parts) == sentence
                semantic.extend((part, sentence, i, len(parts)) for i, part in enumerate(parts))
            assert ' '.join(p[0] for p in semantic) == text
            local = []; cursor = 0
            for part, sentence, part_index, part_count in semantic:
                count = len(lexical(part))
                words = []
                for k in range(cursor, cursor+count):
                    ids, relation = mappings[k]
                    refs = [word_objects[i] for i in ids]
                    start = refs[0]['start']; end = refs[-1]['end']
                    words.append(dict(dst[k], canonical_clip_token_index=k,
                        asr_word_indices=ids, asr_raw_words=[w['word'] for w in refs],
                        source_mp3_start_seconds=start, source_mp3_end_seconds=end,
                        timeline_start_seconds_reference=clip_start+start/1.1,
                        timeline_end_seconds_reference=clip_start+end/1.1,
                        alignment_relation=relation,
                        shared_interval_without_internal_boundary=relation=='shared_name_interval'))
                cursor += count
                first = words[0]['source_mp3_start_seconds']
                last = words[-1]['source_mp3_end_seconds']
                lines = wrap(part)
                local.append({'index':len(out)+len(local)+1, 'audio_name':audio_name,
                    'audio_path':raw['local_path'], 'audio_sha256':raw['sha256'],
                    'text':part, 'lines':lines,
                    'line_char_counts':list(map(len, lines)),
                    'segmentation_reason':'complete_corrected_sentence' if part_count==1 else 'explicit_semantic_clause_boundary',
                    'parent_sentence':sentence, 'part_in_sentence':part_index+1,
                    'parts_in_sentence':part_count, 'source_word_start_seconds':first,
                    'source_word_end_seconds':last, 'words':words,
                    'prior_corrected_cue_indices':[c['index'] for c in original_cues],
                    'audio_review_remains_pending':r['requires_actual_audio_review'],
                    'audio_review_category':r['provisional_category'] if r['requires_actual_audio_review'] else None,
                    'frame_start_30fps':None, 'frame_end_30fps':None})
                wrapping_counts[len(lines)] += 1
            assert cursor == len(dst)
            assert ' '.join(c['text'] for c in local) == text
            # Padding occupies only real within-clip gaps; never another cue's speech.
            for i, c in enumerate(local):
                first, last = c['source_word_start_seconds'], c['source_word_end_seconds']
                prev_end = local[i-1]['source_word_end_seconds'] if i else 0.0
                next_start = local[i+1]['source_word_start_seconds'] if i+1<len(local) else min(source_duration,clip_length_source)
                earliest = 0.0 if not i else (prev_end+first)/2
                latest = min(source_duration,clip_length_source) if i+1==len(local) else (last+next_start)/2
                start = max(earliest,first-.04*1.1)
                end = min(latest,last+.08*1.1)
                # Try a minimum .8s timeline duration, constrained to real gaps.
                need = .8*1.1-(end-start)
                if need>0:
                    extra=min(need,max(0,latest-end));end+=extra;need-=extra
                    if need>0:start-=min(need,max(0,start-earliest))
                c.update(source_caption_start_seconds=start,
                    source_caption_end_seconds=end,
                    timeline_start_seconds_reference=clip_start+start/1.1,
                    timeline_end_seconds_reference=clip_start+end/1.1,
                    duration_seconds_reference=(end-start)/1.1,
                    speech_duration_seconds=(last-first)/1.1,
                    timing_reference_fps=fps,
                    requires_30fps_snapshot_rebase=fps!=30.0)
                if c['duration_seconds_reference'] < .8-1e-8:
                    flagged_short.append({'timeline':t['timeline_name'],'cue':c['index'],
                        'audio_name':audio_name,'text':c['text'],
                        'duration':c['duration_seconds_reference'],
                        'reason':'Not extended over adjacent speech or another MP3.'})
                assert 0 <= start <= first <= last <= end <= min(source_duration,clip_length_source)+1e-8, (audio_name,c['text'],first,last,start,end)
                assert i==0 or local[i-1]['source_caption_end_seconds']<=start+1e-8
            out.extend(local)
            clip_entries.append({'audio_name':audio_name,'canonical_text':text,
                'canonical_token_count':len(dst),'asr_word_count':len(word_objects),
                'source_duration_seconds':source_duration,
                'clip_start_seconds_reference':clip_start,'clip_end_seconds_reference':clip_end,
                'source_in_seconds':0.0,'speed':1.1,
                'reference_snapshot_clip':clip,'cue_indices':[c['index'] for c in local]})
        assert ' '.join(c['text'] for c in out) == srt_text(Path(t['srt_path']))
        timelines.append({'timeline_name':t['timeline_name'],'timeline_id_reference':native_t['id'],
            'fps_reference':fps,'target_fps':30,'old_srt_path':t['srt_path'],
            'old_srt_sha256':tracked[str(Path(t['srt_path']))],
            'old_cue_count':t['final_cue_count'],'new_cue_count':len(out),
            'full_word_order_unchanged':True,'no_cross_mp3_cues':True,
            'clips':clip_entries,'cues':out})
    for p,h in tracked.items():assert digest(Path(p))==h
    report={'schema_version':1,'status':'semantic_plan_prepared_pending_30fps_snapshot_and_UI_layout_review',
        'source_reference_snapshot':str(args.snapshot.resolve()),'source_reference_snapshot_sha256':digest(args.snapshot),
        'target_fps':30,'frame_quantization_performed':False,'old_SRTs_overwritten':False,
        'audio_or_Resolve_modified':False,'canonical_text_policy':'Exactly the current corrected six SRTs; no ordinary word or proper-name changes in this resegmentation.',
        'timing_policy':'Use actual per-clip timeline start + original MP3 seconds / 1.1. Current float seconds are reference only until a current 30fps snapshot confirms positions. Never accumulate original MP3 lengths. Word timings are ASR estimates, not manual phoneme verification.',
        'line_policy':{'max_lines':3,'target_characters_per_line':[22,28],
                       'implemented_max_characters_per_line':28,'preview_font':'Noto Sans, size 40; visual validation assigned to root',
                       'semantic_boundaries':'Sentence ends and explicitly reviewed comma/subordinate/coordinated clauses, not character slicing.',
                       'minimum_duration_target_seconds':.8,'cross_mp3_merge_allowed':False},
        'summary':{'timeline_count':len(timelines),'clip_count':sum(len(t['clips']) for t in timelines),
                   'old_cue_count':sum(t['old_cue_count'] for t in timelines),
                   'new_cue_count':sum(t['new_cue_count'] for t in timelines),
                   'line_count_histogram':dict(wrapping_counts),
                   'max_line_characters':max(max(c['line_char_counts']) for t in timelines for c in t['cues']),
                   'max_lines':max(len(c['lines']) for t in timelines for c in t['cues']),
                   'shorter_than_point8_count':len(flagged_short)},
        'short_duration_exceptions':flagged_short,'input_hashes':tracked,'timelines':timelines}
    output=HERE/'句子半句_竖屏字幕中间方案.json'
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    preview=[]
    for t in timelines:
        preview.extend([t['timeline_name'],f"旧{t['old_cue_count']}条 → 新{t['new_cue_count']}条"])
        for c in t['cues']:
            preview.append(f"{c['index']:03} | {c['audio_name']} | {c['duration_seconds_reference']:.3f}s | "+' / '.join(c['lines']))
        preview.append('')
    (HERE/'句子半句_人工核对预览.txt').write_text('\n'.join(preview)+'\n',encoding='utf-8')
    print(json.dumps({'output':str(output),'summary':report['summary'],'short_exceptions':flagged_short},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
