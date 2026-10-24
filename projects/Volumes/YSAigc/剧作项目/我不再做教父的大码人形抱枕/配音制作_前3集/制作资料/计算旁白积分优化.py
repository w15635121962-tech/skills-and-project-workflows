#!/usr/bin/env python3
"""Minimize estimated ceil(trimmed_chars/100) cost, then number of whole-sentence groups."""
from pathlib import Path
import hashlib
import json
import re

BASE=Path(__file__).resolve().parent
CURRENT=BASE/'200字旁白生成计划.json'
MAX_INPUT=200
BALANCE=79
WORD_RE=re.compile(r"[A-Za-z0-9]+(?:[’'\-][A-Za-z0-9]+)*")


def sha(value):
    return hashlib.sha256(value.encode('utf-8') if isinstance(value,str) else value).hexdigest()


def cost(text):
    return (len(text.strip())+99)//100


baseline_bytes=CURRENT.read_bytes()
current=json.loads(baseline_bytes)
audit=json.loads((BASE/'台词排除核验.json').read_text())
audit_map={(e['version'],e['episode']):e for e in audit['episodes']}
optimized=[]
comparisons=[]
for ep in current['episodes']:
    key=(ep['version'],ep['episode'])
    text=ep['narration_full_text']
    n=len(text)
    cuts={0,n}
    sentence_spans=[]
    previous=0
    for m in re.finditer(r'[.!?](?=\s|$)',text):
        start=previous
        while start<m.end() and text[start].isspace():start+=1
        sentence_spans.append({'sentence_index':len(sentence_spans)+1,'start':start,'end_exclusive':m.end(),'text':text[start:m.end()]})
        k=m.end();cuts.add(k)
        while k<n and text[k].isspace():
            k+=1;cuts.add(k)
        previous=k
    assert not text[previous:].strip()
    fixed=80 if key==('女版',1) else 0
    assert fixed in cuts
    positions=sorted(x for x in cuts if x>=fixed)
    # Each DAG edge is a legal complete-sentence group. No edge may be
    # whitespace-only, split a sentence or exceed 200 trimmed characters.
    dp={n:(0,0,[])}
    edge_count=0
    for start in positions[-2::-1]:
        best=None
        for end in positions:
            if end<=start:continue
            generation=text[start:end].strip()
            chars=len(generation)
            if chars>MAX_INPUT:break
            if not generation or end not in dp:continue
            edge_count+=1
            objective=(cost(generation)+dp[end][0],1+dp[end][1],-chars,end)
            if best is None or objective<best[0]:best=(objective,[(start,end)]+dp[end][2])
        if best:dp[start]=(best[0][0],best[0][1],best[1])
    assert fixed in dp
    intervals=([(0,fixed)] if fixed else [])+dp[fixed][2]
    assert ''.join(text[a:b] for a,b in intervals)==text
    previous_groups=[g for g in current['groups'] if (g['version'],g['episode'])==key]
    ae=audit_map[key]
    original=Path(ae['source_txt']).read_text().removesuffix('\n')
    removed=[False]*len(original)
    for q in ae['excludedquote_details']:
        for i in range(q['source_start'],q['source_end_exclusive']):removed[i]=True
    kept=[i for i,flag in enumerate(removed) if not flag]
    assert ''.join(original[i] for i in kept)==text
    para_ranges=[];cursor=0
    for para in ae['retained_paragraphs']:
        end=cursor+len(para['retained_text'])
        para_ranges.append((cursor,end,para))
        cursor=end
    episode_groups=[]
    for index,(start,end) in enumerate(intervals,1):
        source_text=text[start:end]
        generation_text=source_text.strip()
        reuse=key==('女版',1) and index==1
        src_start=0 if index==1 else kept[start]
        src_end=len(original) if index==len(intervals) else kept[intervals[index][0]]
        sentence_refs=[s for s in sentence_spans if start<=s['start'] and s['end_exclusive']<=end]
        assert sentence_refs
        assert all(not (s['start']<end and s['end_exclusive']>start) or (start<=s['start'] and s['end_exclusive']<=end) for s in sentence_spans)
        para_refs=[p for a,b,p in para_ranges if a<end and b>start and text[max(start,a):min(end,b)].strip()]
        g={
            'version':key[0],'episode':key[1],'group_index':index,
            'name':f'大码{key[1]:02d}-01-{index:02d}',
            'status':'candidate_pending_confirmation',
            'source_text':source_text,'generation_text':generation_text,
            'narration_text':generation_text,'text':generation_text,
            'source_char_count':len(source_text),'char_count':len(generation_text),
            'word_count':len(WORD_RE.findall(generation_text)),
            'estimated_credits':cost(generation_text),
            'source_sha256':sha(source_text),'generation_sha256':sha(generation_text),
            'narration_start':start,'narration_end_exclusive':end,
            'source_docx_paragraphs':list(dict.fromkeys(p['source_paragraph'] for p in para_refs)),
            'source_english_segment_indices':list(dict.fromkeys(p['original_spoken_paragraph_index'] for p in para_refs)),
            'complete_sentence_units':sentence_refs,
            'excludedquote_details':[q for q in ae['excludedquote_details'] if src_start<=q['source_start']<src_end],
            'reused_existing_platform_first_generation':reuse,
            'submit_generation':not reuse,
            'download_one_result_only':True,
            'result_selection':'shortest_duration_among_results_with_complete_generation_text',
        }
        if reuse:
            first=current['groups'][0]
            assert source_text==first['narration_text']
            g.update({k:v for k,v in first.items() if k.startswith('existing_platform_')})
            assert re.sub(r'\s+',' ',generation_text)==g['existing_platform_text']
            g['already_consumed_credits']=1
        assert 0<len(generation_text)<=MAX_INPUT
        assert len(WORD_RE.findall(source_text))==g['word_count']
        episode_groups.append(g)
    old_cost=sum(cost(g['text']) for g in previous_groups)
    new_cost=sum(g['estimated_credits'] for g in episode_groups)
    reused=sum(g.get('already_consumed_credits',0) for g in episode_groups)
    assert new_cost==dp[fixed][0]+reused
    comparisons.append({
        'version':key[0],'episode':key[1],
        'current_group_count':len(previous_groups),'current_estimated_credits':old_cost,
        'optimized_group_count':len(episode_groups),'optimized_estimated_credits':new_cost,
        'reused_existing_credits':reused,'pending_estimated_credits':new_cost-reused,
        'credits_saved':old_cost-new_cost,
        'max_generation_characters':max(g['char_count'] for g in episode_groups),
        'source_character_count':len(text),
        'generation_character_count':sum(g['char_count'] for g in episode_groups),
        'source_sha256':sha(text),
        'reconstructed_source_sha256':sha(''.join(g['source_text'] for g in episode_groups)),
        'source_reconstruction_verbatim':True,
        'complete_sentence_count':len(sentence_spans),
        'legal_boundary_count':len(positions),'dp_edge_count':edge_count,
        'optimization_objective':['minimum sum ceil(len(source_text.strip())/100)','minimum group count','prefer fuller earlier group for deterministic ties'],
    })
    optimized.extend(episode_groups)

old_total=sum(c['current_estimated_credits'] for c in comparisons)
new_total=sum(c['optimized_estimated_credits'] for c in comparisons)
reused_total=sum(c['reused_existing_credits'] for c in comparisons)
pending_total=new_total-reused_total
plan={
    'status':'candidate_pending_confirmation',
    'current_prepared_plan_unchanged':str(CURRENT),
    'current_prepared_plan_sha256':sha(baseline_bytes),
    'model':'seedtts','maximum_generation_characters':MAX_INPUT,
    'cost_model':'Estimate only: ceil(actual generation_text character count / 100). This is a text-grouping calculation; actual billing follows the platform UI.',
    'generation_text_rule':'generation_text = source_text.strip(); remove only each group leading/trailing whitespace. Preserve every narration word, punctuation mark and all internal whitespace exactly.',
    'source_reconstruction_rule':'For each episode, concatenate source_text fields directly to recover the exact original outside-double-quotes narration. source_text may exceed 200 only because its leading/trailing whitespace is excluded from generation_text.',
    'boundary_rule':'Use only full-sentence punctuation boundaries and any allocation point within following native whitespace; never cut a sentence or emit whitespace-only groups.',
    'optimization':'Exact acyclic shortest-path dynamic programming over all legal boundaries. Primary objective is estimated credits, secondary is group count. Episodes independent; female EP1 first 80-source-character group is fixed for existing-generation reuse.',
    'total_group_count':len(optimized),
    'planned_new_generation_count':sum(g['submit_generation'] for g in optimized),
    'current_estimated_credits_including_reuse':old_total,
    'optimized_estimated_credits_including_reuse':new_total,
    'already_consumed_reuse_credits':reused_total,
    'pending_estimated_credits':pending_total,
    'estimated_credits_saved':old_total-new_total,
    'reported_current_balance':BALANCE,
    'pending_fits_reported_balance':pending_total<=BALANCE,
    'estimated_shortfall':max(0,pending_total-BALANCE),
    'total_source_characters':sum(g['source_char_count'] for g in optimized),
    'total_generation_characters':sum(g['char_count'] for g in optimized),
    'total_narration_words':sum(g['word_count'] for g in optimized),
    'max_generation_characters':max(g['char_count'] for g in optimized),
    'all_sources_reconstruct_verbatim':True,
    'episodes':comparisons,'groups':optimized,
}
assert plan['total_source_characters']==current['total_narration_characters']
assert plan['total_narration_words']==current['total_narration_words']
(BASE/'200字旁白积分优化候选.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
comparison={k:v for k,v in plan.items() if k!='groups'}
(BASE/'200字旁白积分优化比较.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert CURRENT.read_bytes()==baseline_bytes,'Prepared plan was unexpectedly changed'
print(json.dumps({k:v for k,v in comparison.items() if k!='episodes'},ensure_ascii=False,indent=2))
for e in comparisons:print(e['version'],e['episode'],'groups',e['optimized_group_count'],'credits',e['optimized_estimated_credits'],'pending',e['pending_estimated_credits'],'old',e['current_estimated_credits'])
