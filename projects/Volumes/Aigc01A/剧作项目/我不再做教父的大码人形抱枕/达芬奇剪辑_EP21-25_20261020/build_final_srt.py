#!/usr/bin/env python3
"""Map selected frozen ASR words onto EP21–25 timeline subtitle cues.

Run only after 剪辑执行计划.json is ready. This script does not call ASR,
change media, or operate Resolve. It writes UTF-8 BOM SRT and an evidence audit.

Optional audio-row fields:
  words_override: [{word, start, end}, ...] in ORIGINAL SOURCE SECONDS;
    or {words: [...], timebase: "source_seconds"}. These must be timed words,
    never a free-text script to align or synthesize.
  exclude_word_intervals: [[source_start_seconds, source_end_seconds], ...],
    or [{start, end, reason}], or [{start_frame, end_frame_exclusive, reason}].
Words are selected/excluded by their source-time midpoint. Ranges in the plan
and all timeline evidence use an exclusive end frame.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import datetime as dt
from functools import lru_cache
import hashlib
import json
import math
from pathlib import Path
import re
import sys

BASE = Path(__file__).resolve().parent
DEFAULT_PLAN = BASE/'剪辑执行计划.json'
AUDIT = BASE/'字幕映射与校验.json'
ASR_INDEX = BASE/'转录/转录索引.json'
CANONICAL = BASE/'剧情顺序.json'
MAX_LINE = 42
MAX_CUE_SECONDS = 5.0
EPS = 1e-7
WEAK_ENDINGS = {'a','an','the','to','of','and','or','for','with','in','at','on',
                'i','he','she','it','we','they','you','my','your','his','her',
                'our','their','its','that','this','these','those','but',
                'had','have','has','was','were','is','are','am','will','would',
                'should','could','can','did','do','does','beside','from','through',
                'after','before','until','into','without','as','than','about',
                'by','who','which','whether','when','where','how','all','even'}
LINKED_PAIRS = {('new','york'),('east','wing'),('medical','research'),
                ('research','center'),('paid','employee'),('fresh','flowers'),
                ('pale','sheets'),('red-rimmed','eyes'),('human','pillow'),
                ('same','place'),('outstretched','hand'),('used','to'),
                ('beside','me'),('moment','on'),('next','door'),('even','more'),
                ('looking','like'),('all','those')}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name+'.tmp')
    temp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    temp.replace(path)


def normalize_path(value):
    p = Path(value).expanduser()
    return str((p if p.is_absolute() else BASE.parent/p).resolve())


def lexical(value):
    return bool(re.search(r'[A-Za-z0-9]', value))


def join_words(words):
    text = ' '.join(w['word'].strip() for w in words)
    text = re.sub(r'\s+([,.;:!?])',r'\1',text)
    text = re.sub(r'\s+([-’\'])',r'\1',text)
    return re.sub(r'\s+',' ',text).strip()


def two_lines(text):
    """Prefer a balanced break, without exceeding two approximately 42-char lines."""
    if len(text)<=MAX_LINE:
        return [text]
    positions=[m.start() for m in re.finditer(' ',text)]
    candidates=[]
    for position in positions:
        left,right=text[:position].rstrip(),text[position+1:].lstrip()
        if len(left)<=MAX_LINE and len(right)<=MAX_LINE:
            score=abs(len(left)-len(right))
            if left.endswith((',', ';', ':')):score-=7
            last=left.split()[-1].lower().strip('.,;:!?')
            first=right.split()[0].lower().strip('.,;:!?')
            if last in WEAK_ENDINGS:score+=24
            if (last,first) in LINKED_PAIRS:score+=100
            candidates.append((score,[left,right]))
    return min(candidates,key=lambda item:item[0])[1] if candidates else None


def canonical_names(episode_text):
    return {name for name in ['Matteo','Alessia','Bellandi','Eliza','Vincent']
            if re.search(r'\b'+re.escape(name)+r'\b',episode_text)}


def proper_name_corrections(words, allowed, corrections):
    """Correct only project names, preserving original words and source timing."""
    aliases={
        'Matteo':{'mateo','matteo','mattel','matel','mattelio'},
        'Alessia':{'alessia','alicia'},
        'Bellandi':{'bellandi','bolandi','belandi','baletti'},
        'Eliza':{'eliza','elisa','aliza'},
    }
    result=[];i=0
    while i<len(words):
        w=deepcopy(words[i])
        # The existing two-model VO24 recognition "The tail looked..." is
        # the canonical Matteo looked... name. Restrict the phrase correction
        # to that exact known narration source, not arbitrary English prose.
        if (i+1<len(words) and 'Matteo' in allowed
            and Path(w['source_path']).name=='女版24-2.mp3'
            and w['word'].strip().lower()=='the'
            and words[i+1]['word'].strip().lower().rstrip('.,;:!?')=='tail'):
            second=words[i+1]
            w['word']='Matteo'
            w['end']=second['end'];w['end_frame']=second['end_frame']
            w['timeline_end_frame_exact']=second['timeline_end_frame_exact']
            w['source_word_evidence']+=deepcopy(second['source_word_evidence'])
            w['constituent_ids']+=second['constituent_ids']
            corrections.append(dict(audio_id=w['audio_id'],before='The tail',after='Matteo',
                                    reason='canonical proper name at the same narrated action',
                                    source_start=w['start'],source_end=w['end']))
            result.append(w);i+=2;continue
        value=w['word'].strip()
        match=re.match(r"^([^A-Za-z]*)([A-Za-z]+)((?:['’]s)?)([^A-Za-z]*)$",value)
        if match:
            prefix,core,possessive,suffix=match.groups()
            if ('Bellandi' in allowed and core.lower()=='bologna' and i+1<len(words)
                and words[i+1]['word'].strip().lower().rstrip('.,;:!?')=='family'):
                corrections.append(dict(audio_id=w['audio_id'],before=value,
                                        after=prefix+'Bellandi'+possessive+suffix,
                                        reason='canonical Bellandi family at the exact family-name phrase',
                                        source_start=w['start'],source_end=w['end']))
                w['word']=prefix+'Bellandi'+possessive+suffix
                result.append(w);i+=1;continue
            for name,variants in aliases.items():
                if name in allowed and core.lower() in variants:
                    fixed=prefix+name+possessive+suffix
                    if fixed!=value:
                        corrections.append(dict(audio_id=w['audio_id'],before=value,after=fixed,
                                                reason='canonical proper-name spelling only',
                                                source_start=w['start'],source_end=w['end']))
                        w['word']=fixed
                    break
        result.append(w);i+=1
    return result


def interval_seconds(value, fps):
    if isinstance(value,(list,tuple)) and len(value)==2:
        return float(value[0]),float(value[1]),'plan exclusion'
    if not isinstance(value,dict):raise ValueError('Invalid exclude_word_intervals entry')
    if 'start_frame' in value:
        start=float(value['start_frame'])/fps
        end=float(value.get('end_frame_exclusive',value.get('end_frame')))/fps
    else:
        start=float(value.get('start',value.get('source_start')))
        end=float(value.get('end',value.get('source_end')))
    return start,end,value.get('reason','plan exclusion')


def partition_utterance(words, fps):
    """DP partitions at word boundaries, rewarding grammatical sentence ends."""
    n=len(words)
    @lru_cache(None)
    def solve(i):
        if i==n:return 0.0,()
        best=None
        for j in range(i+1,min(n,i+45)+1):
            selected=words[i:j]
            value=join_words(selected);lines=two_lines(value)
            if lines is None:
                if j==i+1:lines=[value]
                else:break
            start=selected[0]['start_frame'];end=max(w['end_frame'] for w in selected)
            duration=(end-start)/fps
            if duration>MAX_CUE_SECONDS and j>i+1:break
            suffix=selected[-1]['word'].strip()
            terminal=suffix.endswith(('.', '?', '!'))
            score=12.0
            # When a long sentence needs two cues, avoid choosing an arbitrary
            # three-word fragment merely because all legal split scores tie.
            score+=abs(len(value)-46)*.075
            if terminal:score-=7
            elif suffix.endswith((',', ';', ':')):score-=2
            if duration<1 and not terminal:score+=(1-duration)*10
            if duration>MAX_CUE_SECONDS:score+=(duration-MAX_CUE_SECONDS)*10
            cps=len(value)/max(duration,.1)
            if cps>22:score+=(cps-22)*.6
            last_word=suffix.lower().strip('.,;:!?')
            if last_word in WEAK_ENDINGS:score+=12
            if j<n:
                next_word=words[j]['word'].strip().lower().strip('.,;:!?')
                if (last_word,next_word) in LINKED_PAIRS:score+=100
            tail,path=solve(j)
            candidate=(score+tail,((i,j,lines),)+path)
            if best is None or candidate[0]<best[0]:best=candidate
        if best is None:raise ValueError('Cannot partition subtitle words')
        return best
    return solve(0)[1]


def cues_for_audio(words, fps):
    if not words:return []
    runs=[];current=[]
    for word in words:
        if current and ((word['start_frame']-current[-1]['end_frame'])/fps>.65
                        or current[-1]['word'].strip().endswith(('.', '?', '!'))):
            runs.append(current);current=[]
        current.append(word)
    if current:runs.append(current)
    cues=[]
    for run in runs:
        for first,last,lines in partition_utterance(run,fps):
            selected=run[first:last]
            cues.append(dict(start_frame=selected[0]['start_frame'],
                             end_frame=max(w['end_frame'] for w in selected),
                             lines=lines,words=selected,
                             audio_ids=sorted({w['audio_id'] for w in selected})))
    return cues


def srt_time(frame, fps):
    ms=round(frame*1000/fps)
    h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',type=Path,default=DEFAULT_PLAN)
    args=parser.parse_args()
    plan=json.loads(args.plan.read_text())
    canonical=json.loads(CANONICAL.read_text())
    index=json.loads(ASR_INDEX.read_text())
    indexed={normalize_path(x['source_path']):x for x in index['files']}
    # Narration exists in two local directories with byte-identical copies.
    # Reuse the same frozen ASR for a verified identical alias, without ASR.
    by_sha={x['source_sha256']:x for x in index['files']}
    inventory_path=BASE/'素材盘点.json'
    if inventory_path.exists():
        for item in json.loads(inventory_path.read_text()).get('files',[]):
            if item.get('sha256') in by_sha:
                indexed.setdefault(normalize_path(item['path']),by_sha[item['sha256']])
    canon={x['episode']:x for x in canonical['episodes']}
    audit=dict(created_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
               plan_path=str(args.plan.resolve()),plan_sha256=sha(args.plan),
               canonical_path=str(CANONICAL),canonical_sha256=sha(CANONICAL),
               timing='selected source ASR seconds mapped by source frames to timeline frames; all ends exclusive',
               source_audio_uploaded=False,new_asr_performed=False,resolve_modified=False,
               raw_asr_frozen=True,episodes=[],errors=[],warnings=[])
    pending=[];raw_hashes={}
    for ep in plan['episodes']:
        episode=int(ep['episode']);fps=float(ep.get('fps',24));duration=int(ep['duration_frames'])
        if episode not in range(21,26):
            audit['errors'].append(f'Unexpected episode {episode}');continue
        if fps<=0 or duration<=0:
            audit['errors'].append(f'Invalid timeline timebase EP{episode}');continue
        text=' '.join(x['text_verbatim'] for x in canon[episode]['source_en_items'])
        allowed=canonical_names(text)
        evidence=dict(episode=episode,fps=fps,duration_frames=duration,
                      selected_audio=[],excluded_audio=[],excluded_words=[],name_corrections=[],cues=[])
        all_cues=[];selected_ids=[]
        for number,audio in enumerate(ep.get('audio',[])):
            audio_id=f'EP{episode}_A{number:03}'
            if not audio.get('subtitle',False):
                evidence['excluded_audio'].append(dict(audio_id=audio_id,source_path=audio['source_path'],
                                                       tag=audio.get('tag'),reason='subtitle:false'))
                continue
            path=normalize_path(audio['source_path'])
            if path not in indexed:
                audit['errors'].append(f'Missing frozen ASR for {path}');continue
            source=indexed[path];asr_path=Path(source['json_path']);raw_hashes[str(asr_path)]=sha(asr_path)
            raw=json.loads(asr_path.read_text())
            alias=normalize_path(raw['source_path'])!=path
            if alias and sha(Path(path))!=source['source_sha256']:
                audit['errors'].append(f'Identical-copy alias changed bytes: {path}');continue
            source_first=int(audio['source_start_frame']);source_last=int(audio['source_end_frame_exclusive'])
            record=int(audio['record_frame'])
            if source_last<=source_first or source_first<0 or record<0 or record+source_last-source_first>duration:
                audit['errors'].append(f'Invalid selected audio bounds {audio_id}');continue
            original=deepcopy(raw['words']);origin='frozen ASR'
            override=audio.get('words_override')
            if override is not None:
                if isinstance(override,dict):
                    if override.get('timebase','source_seconds')!='source_seconds':
                        raise ValueError('words_override must use original source seconds')
                    override=override['words']
                if not isinstance(override,list):raise ValueError('words_override must be timed word objects')
                original=deepcopy(override);origin='explicit plan words_override'
                for w in original:
                    if not all(k in w for k in ['start','end']) or ('word' not in w and 'text' not in w):
                        raise ValueError('Untimed words_override is forbidden')
                    w['word']=w.get('word',w.get('text'))
            intervals=[interval_seconds(x,fps) for x in audio.get('exclude_word_intervals',[])]
            mapped=[]
            for wi,w in enumerate(original):
                start=float(w['start']);end=float(w['end']);value=str(w['word'])
                if end<start or start<0:raise ValueError(f'Invalid word time {audio_id}:{wi}')
                midpoint=(start+end)/2
                if not source_first/fps-EPS<=midpoint<source_last/fps-EPS:continue
                removal=None
                if not lexical(value):removal='punctuation-only ASR token'
                if value.strip().lower().strip('.,;:!?')=='dot':removal='unwanted spoken punctuation dot, excluded by request'
                for a,b,reason in intervals:
                    if a<=midpoint<b:removal=reason
                if removal:
                    evidence['excluded_words'].append(dict(audio_id=audio_id,word_index=wi,
                                                           word=value,start=start,end=end,reason=removal));continue
                exact_start=record+max(start*fps,source_first)-source_first
                exact_end=record+min(end*fps,source_last)-source_first
                start_frame=max(record,math.floor(exact_start+EPS))
                end_frame=min(record+source_last-source_first,math.ceil(exact_end-EPS))
                uid=f'{audio_id}_W{wi:04}'
                row=dict(audio_id=audio_id,track=audio.get('track'),tag=audio.get('tag'),
                         source_path=path,word=value,start=start,end=end,probability=w.get('probability'),
                         source_start_frame=source_first,source_end_frame_exclusive=source_last,record_frame=record,
                         start_frame=start_frame,end_frame=end_frame,
                         timeline_start_frame_exact=exact_start,timeline_end_frame_exact=exact_end,
                         constituent_ids=[uid],source_word_evidence=[dict(index=wi,word=value,start=start,end=end,origin=origin)])
                mapped.append(row);selected_ids.append(uid)
                if end==start:audit['warnings'].append(f'Zero-duration ASR word {uid} {value!r}')
                if start*fps<source_first-EPS or end*fps>source_last+EPS:
                    audit['warnings'].append(f'Selected clip trims a word boundary {uid}')
            mapped=proper_name_corrections(mapped,allowed,evidence['name_corrections'])
            evidence['selected_audio'].append(dict(audio_id=audio_id,source_path=path,
                                                   source_start_frame=source_first,source_end_frame_exclusive=source_last,
                                                   record_frame=record,track=audio.get('track'),tag=audio.get('tag'),
                                                   raw_asr_json=str(asr_path),raw_asr_sha256=raw_hashes[str(asr_path)],
                                                   byte_identical_source_alias=alias,
                                                   word_origin=origin,selected_word_count=sum(len(w['constituent_ids']) for w in mapped),
                                                   source_quality_flags=source.get('quality_flags',[])))
            if not mapped:audit['warnings'].append(f'No lexical subtitle words in selected {audio_id}')
            all_cues+=cues_for_audio(mapped,fps)
        all_cues.sort(key=lambda x:(x['start_frame'],x['end_frame'],x['audio_ids']))
        for i,cue in enumerate(all_cues):
            if cue['end_frame']<=cue['start_frame']:
                cue['end_frame']=min(duration,cue['start_frame']+1)
                audit['warnings'].append(f'One-frame display for zero-duration EP{episode} cue {i+1}')
            if i and all_cues[i-1]['end_frame']>cue['start_frame']:
                previous=all_cues[i-1]
                overlap=previous['end_frame']-cue['start_frame']
                exact_previous=max(w['timeline_end_frame_exact'] for w in previous['words'])
                exact_current=min(w['timeline_start_frame_exact'] for w in cue['words'])
                if overlap<=2 and exact_previous<=exact_current+EPS:
                    boundary=round((exact_previous+exact_current)/2)
                    boundary=max(previous['start_frame']+1,min(boundary,cue['end_frame']-1))
                    previous['end_frame']=boundary;cue['start_frame']=boundary
                    audit['warnings'].append(f'Rounding-only cue edge adjusted EP{episode} cue {i+1}')
                else:
                    audit['errors'].append(f'Actual overlapping selected subtitle speech EP{episode} cue {i}/{i+1}; fix audio plan rather than dropping words')
            cue['number']=i+1
            cue['start_seconds']=cue['start_frame']/fps;cue['end_seconds']=cue['end_frame']/fps
            if cue['start_frame']<0 or cue['end_frame']>duration or cue['end_frame']<=cue['start_frame']:
                audit['errors'].append(f'Out-of-bounds subtitle EP{episode} cue {i+1}')
            if len(cue['lines'])>2:audit['errors'].append(f'More than two lines EP{episode} cue {i+1}')
            if any(len(line)>MAX_LINE for line in cue['lines']):audit['warnings'].append(f'Unbreakable line over {MAX_LINE} chars EP{episode} cue {i+1}')
            if (cue['end_frame']-cue['start_frame'])/fps>MAX_CUE_SECONDS:
                audit['warnings'].append(f'Intrinsic single-word cue over 5 seconds EP{episode} cue {i+1}')
        # A rounding adjustment can change the preceding cue as well.
        for cue in all_cues:
            cue['start_seconds']=cue['start_frame']/fps
            cue['end_seconds']=cue['end_frame']/fps
        used=[uid for cue in all_cues for word in cue['words'] for uid in word['constituent_ids']]
        if Counter(used)!=Counter(selected_ids):audit['errors'].append(f'Selected word coverage mismatch EP{episode}')
        evidence['cues']=all_cues
        evidence['validation']=dict(cue_count=len(all_cues),selected_source_word_count=len(selected_ids),
                                    represented_source_word_count=len(used),selected_word_coverage_matches=Counter(used)==Counter(selected_ids),
                                    max_lines=max((len(c['lines']) for c in all_cues),default=0),
                                    max_line_characters=max((len(s) for c in all_cues for s in c['lines']),default=0),
                                    end_within_episode=all(c['end_frame']<=duration for c in all_cues),
                                    no_overlaps=all(a['end_frame']<=b['start_frame'] for a,b in zip(all_cues,all_cues[1:])))
        audit['episodes'].append(evidence)
        chunks=[f"{c['number']}\n{srt_time(c['start_frame'],fps)} --> {srt_time(c['end_frame'],fps)}\n"+'\n'.join(c['lines'])+'\n' for c in all_cues]
        pending.append((BASE/'SRT'/f'EP{episode}.srt','\n'.join(chunks)))
    actual_episodes=[x['episode'] for x in audit['episodes']]
    if sorted(actual_episodes)!=list(range(21,26)) or len(actual_episodes)!=len(set(actual_episodes)):
        audit['errors'].append('Plan must contain EP21–25 exactly once')
    audit['raw_asr_hashes_unchanged']=all(sha(Path(p))==h for p,h in raw_hashes.items())
    if not audit['raw_asr_hashes_unchanged']:audit['errors'].append('Frozen ASR changed during subtitle mapping')
    audit['valid']=not audit['errors']
    audit['output_encoding']='UTF-8 with BOM'
    audit['written_srt_files']=[]
    if audit['valid']:
        for path,text in pending:
            path.parent.mkdir(parents=True,exist_ok=True)
            temp=path.with_name(path.name+'.tmp')
            temp.write_text(text,encoding='utf-8-sig');temp.replace(path)
            audit['written_srt_files'].append(str(path))
    save_json(AUDIT,audit)
    print(json.dumps(dict(valid=audit['valid'],outputs=audit['written_srt_files'],
                          errors=audit['errors'],warning_count=len(audit['warnings'])),ensure_ascii=False))
    if not audit['valid']:raise SystemExit(1)


if __name__=='__main__':
    main()
