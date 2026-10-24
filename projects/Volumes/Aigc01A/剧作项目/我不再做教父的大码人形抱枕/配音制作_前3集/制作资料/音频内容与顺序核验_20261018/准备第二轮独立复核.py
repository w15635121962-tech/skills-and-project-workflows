#!/usr/bin/env python3
"""Read fixed large-v3-turbo checkpoints; never run or select an ASR model."""
from pathlib import Path
import hashlib,json,re

BASE=Path(__file__).resolve().parent
LARGE=BASE/'ASR/transcripts_large-v3-turbo'


def words(text):
    # Preserve Unicode letters, including ñ: Vareña must remain one name token.
    return re.findall(r"[^\W_]+(?:'[^\W_]+)*",text.lower().replace('’',"'"),re.UNICODE)


def edits(expected,heard):
    a,b=words(expected),words(heard)
    costs=[[0]*(len(b)+1) for _ in range(len(a)+1)]
    for i in range(len(a)+1):costs[i][0]=i
    for j in range(len(b)+1):costs[0][j]=j
    for i in range(1,len(a)+1):
        for j in range(1,len(b)+1):
            costs[i][j]=min(costs[i-1][j]+1,costs[i][j-1]+1,costs[i-1][j-1]+(a[i-1]!=b[j-1]))
    i,j=len(a),len(b);ops=[]
    while i or j:
        if i and j and a[i-1]==b[j-1] and costs[i][j]==costs[i-1][j-1]:i-=1;j-=1
        elif i and j and costs[i][j]==costs[i-1][j-1]+1:
            ops.append({'type':'substitute','expected':a[i-1],'heard_asr':b[j-1],'reference_index':i-1,'hypothesis_index':j-1});i-=1;j-=1
        elif i and costs[i][j]==costs[i-1][j]+1:
            ops.append({'type':'delete','expected':a[i-1],'reference_index':i-1,'hypothesis_index':j});i-=1
        else:
            ops.append({'type':'insert','heard_asr':b[j-1],'reference_index':i,'hypothesis_index':j-1});j-=1
    return list(reversed(ops))


def main():
    first=json.loads((BASE/'第一轮盲转写逐词对比.json').read_text(encoding='utf-8'))
    independent=json.loads((BASE/'源剧本独立核验.json').read_text(encoding='utf-8'))
    classification=json.loads((BASE/'第一轮识别差异独立分类.json').read_text(encoding='utf-8'))
    fixed_priority={r['name'] for r in classification['rows'] if r['requires_actual_audio_review']}
    assert len(fixed_priority)==15
    source_by_name={r['name']:r for r in independent['groups']}
    rows=[];pending=[]
    for r in first['rows']:
        expected=source_by_name[r['name']]['independently_derived_expected_text']
        assert expected==r['expected_text']
        path=LARGE/r['version']/(r['name']+'.json')
        try:
            raw=path.read_bytes();second=json.loads(raw)
        except (FileNotFoundError,json.JSONDecodeError,UnicodeDecodeError):
            pending.append(r['name']);continue
        large_text=second['text']
        checks={'fixed_large_model':'large-v3-turbo' in second.get('model',''),
                'same_audio_hash':second.get('sha256')==r['sha256'],
                'blind':second.get('blind_transcription') is True,
                'no_expected_prompt':second.get('expected_script_supplied_to_model') is False}
        large_ops=edits(expected,large_text)
        rows.append({'name':r['name'],'version':r['version'],'episode':r['episode'],
            'preselected_priority_15':r['name'] in fixed_priority,
            'expected_text':expected,'small_text':r['asr_text'],'large_text':large_text,
            'first_round_operations':r['difference_operations'],'large_operations':large_ops,
            'first_strict_words_identical':r['normalized_words_identical'],
            'large_strict_words_identical':not large_ops,
            'two_models_words_conflict':words(r['asr_text'])!=words(large_text),
            'checkpoint':str(path),'checkpoint_sha256':hashlib.sha256(raw).hexdigest(),
            'model':second.get('model'),'model_revision':second.get('model_revision'),
            'decode_parameters':second.get('decode_parameters'),'provenance_checks':checks})
    ready_priority=sum(r['preselected_priority_15'] for r in rows)
    report={'scope':'Fixed preselected large-v3-turbo evidence; no best-match model selection.',
        'tokenization':'Unicode letters and digits preserved; curly apostrophes normalized; no diacritics stripped.',
        'observed_large_checkpoint_count':len(rows),'observed_priority_15_count':ready_priority,
        'pending_count':len(pending),'pending_names':pending,
        'large_strict_match_count':sum(r['large_strict_words_identical'] for r in rows),
        'large_difference_count':sum(not r['large_strict_words_identical'] for r in rows),
        'two_models_conflict_count':sum(r['two_models_words_conflict'] for r in rows),
        'provenance_anomalies':[{'name':r['name'],'checks':r['provenance_checks']} for r in rows if not all(r['provenance_checks'].values())],
        'rows':rows}
    if rows:
        (BASE/'第二轮独立复核_对比准备.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='rows'},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
