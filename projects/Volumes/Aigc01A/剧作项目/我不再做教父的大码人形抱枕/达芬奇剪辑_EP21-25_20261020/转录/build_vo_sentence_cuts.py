#!/usr/bin/env python3
"""Sentence/beat cuts derived only from frozen real-audio ASR word times."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parent
EDIT=ROOT.parent

# Inclusive zero-based ASR word ranges and current canonical item orders.
CUTS={
 (21,1):[(0,2,[1]),(3,12,[2]),(13,16,[3])],
 (21,2):[(0,2,[5]),(3,10,[6]),(11,17,[8]),(18,35,[9])],
 (21,3):[(0,16,[11]),(17,26,[12]),(27,28,[12])],
 (21,4):[(0,12,[13]),(13,24,[13])],
 (21,5):[(0,15,[14]),(16,29,[15])],
 (21,6):[(0,6,[18]),(7,21,[19]),(22,43,[20])],
 (21,7):[(0,9,[22]),(10,13,[23]),(14,20,[24]),(21,27,[25]),(28,33,[26]),(34,44,[27])],
 (21,8):[(0,18,[28]),(19,24,[29])],
 (22,1):'auto_two',
 (22,2):[(0,5,[3]),(6,19,[4]),(20,25,[5]),(27,31,[7]),(32,38,[8])],
 (22,3):[(0,8,[11]),(9,10,[13]),(11,19,[14]),(20,26,[15]),(27,36,[21])],
 (23,1):[(0,5,[1]),(6,22,[8]),(23,25,[10]),(26,31,[11])],
 (24,1):[(0,3,[9])],
 (24,2):[(0,8,[26])],
 (25,1):[(0,3,[1]),(4,17,[2]),(18,31,[3])],
 (25,2):[(0,2,[11]),(3,8,[14]),(9,13,[15]),(14,27,[16])],
 (25,3):[(0,6,[20]),(7,16,[21]),(17,38,[22])],
 (25,4):[(0,6,[23]),(7,17,[24]),(18,23,[25])],
}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def text(words):
    value=''.join(w['word'] for w in words).strip()
    return re.sub(r'\s+-', '-', value)


def main():
    canonical_path=EDIT/'剧情顺序.json'
    canonical=json.loads(canonical_path.read_text())
    eps={x['episode']:x for x in canonical['episodes']}
    fragments=[]
    assemblies=[]
    before={}
    for (ep,vo),cuts in CUTS.items():
        p=ROOT/'raw_large-v3-turbo'/f'EP{ep}'/'narration'/f'女版{ep}-{vo}.json'
        before[str(p)]=sha(p)
        raw=json.loads(p.read_text());words=raw['words']
        if cuts=='auto_two':
            ranges=[];start=0
            for i,w in enumerate(words):
                if w['word'].strip().endswith(('.', '?', '!')):
                    ranges.append((start,i,[len(ranges)+1]));start=i+1
            assert len(ranges)==2 and start==len(words)
            cuts=ranges
        canon=eps[ep]['source_en_items'];byorder={x['order']:x for x in canon}
        local=[]
        covered=set()
        for part,(first,last,orders) in enumerate(cuts,1):
            selected=words[first:last+1];covered.update(range(first,last+1))
            prev=[x for x in canon if x['kind']=='dialogue' and x['order']<min(orders)]
            nxt=[x for x in canon if x['kind']=='dialogue' and x['order']>max(orders)]
            prev=prev[-1] if prev else None;nxt=nxt[0] if nxt else None
            anchor=lambda row:None if row is None else {k:row[k] for k in ['order','speaker','text_verbatim']}
            placement=(f"在{prev['text_verbatim']}之后" if prev else '本集首句对白之前')
            placement+=(f"、{nxt['text_verbatim']}之前" if nxt else '，本集最后一句对白之后继续收尾')
            record=dict(id=f'EP{ep}_VO{vo:02d}_S{part:02d}',episode=ep,vo=vo,sentence_order=part,
                        source_path=raw['source_path'],start=round(float(selected[0]['start']),3),
                        end=round(float(selected[-1]['end']),3),text=text(selected),
                        source_word_index_start=first,source_word_index_end=last,
                        source_timestamp_basis='frozen ASR word-alignment seconds; no new ASR or forced alignment',
                        raw_asr_json=str(p),raw_asr_sha256=before[str(p)],
                        canonical_match=dict(folder_episode=ep,english_episode=eps[ep]['numbering_map']['english_docx_episode'],
                                             item_orders=orders,texts_verbatim=[byorder[x]['text_verbatim'] for x in orders],
                                             basis='manual match to narrated event and exact current canonical sequence; raw ASR wording preserved'),
                        insertion=dict(after_dialogue=anchor(prev),before_dialogue=anchor(nxt),instruction=placement),
                        human_listening_validation=False)
            if ep==21 and vo==3 and part in [2,3]:record['continuity_note']='同一canonical第12条拆为说明与ONE WISH；顺序相接，不重复整条原文。'
            if ep==21 and vo==4:record['continuity_note']='同一canonical第13条的连续两句；保持本文件原先顺序。'
            if ep==21 and vo==7 and part in [1,2]:record['continuity_note']='两段在2.12秒相接，无停顿；无需插入对白，可重连为同一句。'
            if ep==21 and vo==6 and part==3:record['wording_note']='ASR为torn apart in my real feelings；canonical没有in，未在此擅自改动音频或原始听写。'
            if ep==24 and vo==2:record['wording_note']='两模型识别The tail，canonical是Matteo；此处按同一事件匹配，不把原始ASR改写成人名。'
            if ep==25 and vo==2 and part==1:record['wording_note']='ASR识别Mattel，canonical是Matteo；保留原识别并匹配男主发问动作。'
            if ep==24 and vo==1:record['edit_note']='应插在Only when…close my eyes.与Then one night…之间；若二者采用同一段视频对白，必须在两句之间切开承载本VO。'
            if ep==24 and vo==2:record['edit_note']='应插在You lived through that for ten years.之后，Eliza, I\'m sorry.之前。'
            if ep==22 and vo==2 and part==3:record['edit_note']='本段结束后先放女主Matteo, the wish coupon has expired.，再接本文件S04；不能把VO2整段放在该对白之前。'
            local.append(record);fragments.append(record)
        excluded=[dict(index=i,**w) for i,w in enumerate(words) if i not in covered]
        slots={(x['insertion']['after_dialogue']['order'] if x['insertion']['after_dialogue'] else None,
                x['insertion']['before_dialogue']['order'] if x['insertion']['before_dialogue'] else None) for x in local}
        assemblies.append(dict(episode=ep,vo=vo,source_path=raw['source_path'],fragment_ids=[x['id'] for x in local],
                               must_split_around_dialogue=len(slots)>1,distinct_dialogue_slots=len(slots),
                               excluded_raw_words=excluded))
    actual={ep:set() for ep in eps}
    for f in fragments:actual[f['episode']].update(f['canonical_match']['item_orders'])
    uncovered={ep:[x['order'] for x in data['source_en_items'] if x['kind']=='source_narration' and x['order'] not in actual[ep]] for ep,data in eps.items()}
    assert not any(uncovered.values()),uncovered
    assert all(x['end']>x['start']>=0 for x in fragments)
    assert all(sha(Path(p))==h for p,h in before.items())
    dot=dict(source_path=next(x['source_path'] for x in assemblies if x['episode']==22 and x['vo']==2),
             raw_asr_word_index=26,asr_word='dot',start=10.04,end=10.16,asr_probability=0.8798828125,
             canonical_match=None,proposed_edit='canonical无此词；候选剪辑在9.90结束midair，下一句从10.16的his开始，把该词独立排除。',
             acoustic_status='波形在约10.05–10.17秒有明显独立浊声音节，RMS约0.216，非静音；这反对将它直接视为静音幻听，但波形本身不能确认具体发音一定是dot。标作真实额外音节嫌疑，等待主观听音确认。',
             observed_voiced_event_seconds=[10.05,10.17],
             edit_boundary_note='ASR给出的his起点10.16处仍可能带上一音节极短尾部，实剪可配5–10毫秒音频淡入并验听；不在本交付中伪称已听过接头。',
             requires_subjective_listening=True,waveform_path=str(ROOT/'EP22_VO2_dot_波形.png'),
             energy_path=str(ROOT/'EP22_VO2_dot_波形能量.json'))
    output=dict(scope='18个实际VO，按句/可插入叙事单元拆成56段；原始ASR冻结',
                canonical_path=str(canonical_path),canonical_sha256=sha(canonical_path),
                numbering='本地EP21–25 = EN20–24 = 中文21–25',
                timing='start/end为源音频首末词的实际ASR对齐秒数，不是时间线时码，也未加剪辑留白；接头短淡化另行处理。',
                raw_asr_unchanged=True,new_transcription_performed=False,resolve_modified=False,
                source_audio_count=len(assemblies),fragment_count=len(fragments),canonical_narration_uncovered=uncovered,
                source_assemblies=assemblies,excluded_token_review=dot,fragments=fragments)
    (EDIT/'可剪辑旁白片段.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# 可剪辑旁白片段','本地EP21–25对应英文20–24。以下全部为源音频秒；未估算时间线秒数。','']
    for f in fragments:
        lines.extend([f"- {f['id']}：{f['start']:.3f}–{f['end']:.3f}｜{Path(f['source_path']).name}",
                      f"  {f['text']}",f"  {f['insertion']['instruction']}"])
    lines.extend(['','EP22 VO2的dot：ASR 10.04–10.16秒，canonical无此词；波形在约10.05–10.17秒呈明显独立浊声音节，倾向真实额外音节，但不能据此证明具体发音。候选剪辑排除该区间，需实际听音确认。'])
    (EDIT/'可剪辑旁白片段.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(dict(sources=len(assemblies),fragments=len(fragments),must_split=[(x['episode'],x['vo']) for x in assemblies if x['must_split_around_dialogue']],uncovered=uncovered),ensure_ascii=False))


if __name__=='__main__':main()
