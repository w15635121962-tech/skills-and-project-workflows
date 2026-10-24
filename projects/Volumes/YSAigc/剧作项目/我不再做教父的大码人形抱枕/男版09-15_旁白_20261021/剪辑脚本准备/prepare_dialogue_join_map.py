"""Offline original-prose join map. No audio timing is invented and no media is edited."""
from pathlib import Path
import json,re
BASE=Path(__file__).resolve().parent.parent
OUT=Path(__file__).resolve().parent
m=json.loads((BASE/'准备/narration_manifest.json').read_text())
result={'scope':'Original male prose only; all source-relative audio times and video selection remain pending actual ASR/waveform/visual review.','source_docx':m['source_docx'],'source_docx_sha256':m['source_docx_sha256'],'episodes':[]}
for ep in m['episodes']:
    blocks=ep['original_paragraphs_and_retained_narration']
    full='\n'.join(x['text'] for x in blocks)
    mask=[True]*len(full)
    for q in ep['quoted_spans']:
        if q['action']=='exclude_role_or_message_dialogue':mask[q['source_start']:q['source_end_exclusive']]=[False]*(q['source_end_exclusive']-q['source_start'])
    narrative=''.join(c for i,c in enumerate(full) if mask[i])
    assert narrative==Path(ep['output_path']).read_text()
    spans=[];cursor=0
    for g in [g for g in m['groups'] if g['episode']==ep['episode']]:
        spans.append((cursor,cursor+len(g['source_text']),g));cursor+=len(g['source_text'])
    assert cursor==len(narrative)
    tokens=list(re.finditer(r'\S+',narrative))
    def anchor(token):
        if token is None:return None
        offset=token.start();matching=[(a,b,g) for a,b,g in spans if a<=offset<b];assert len(matching)==1
        a,b,g=matching[0];trim=len(g['source_text'])-len(g['source_text'].lstrip())
        return {'logical_basename':g['basename'],'original_token':token.group(),'narration_global_char_start':token.start(),'narration_global_char_end_exclusive':token.end(),'generation_text_char_start':token.start()-a-trim,'generation_text_char_end_exclusive':token.end()-a-trim,'source_docx_paragraphs_of_segment':g['source_docx_paragraphs'],'source_audio_start_seconds':None,'source_audio_end_seconds':None}
    units=[]
    for q in ep['quoted_spans']:
        if q['action']!='exclude_role_or_message_dialogue':continue
        pos=sum(mask[:q['source_start']])
        previous=next((t for t in reversed(tokens) if t.end()<=pos),None)
        following=next((t for t in tokens if t.start()>=pos),None)
        before,after=anchor(previous),anchor(following)
        contexts=[]
        for b in blocks:
            if any(abs(b['docx_paragraph']-p)<=2 for p in q['docx_paragraphs']):contexts.append({'docx_paragraph':b['docx_paragraph'],'original_text':b['text']})
        units.append({'unit_id':'EP%02d_D%02d'%(ep['episode'],len(units)+1),'source_docx_paragraphs':q['docx_paragraphs'],'original_quoted_text':q['text'],'narration_char_position_after_external_quote_removal':pos,'previous_narration_token_anchor':before,'next_narration_token_anchor':after,'same_tts_segment_requires_native_split_for_dialogue':bool(before and after and before['logical_basename']==after['logical_basename']),'nearby_original_context':contexts,'source_video_path':None,'source_video_in_frame':None,'source_video_out_frame_exclusive':None,'timeline_record_frame':None,'sync_audio_rule':'Choose reviewed source video carrying this original dialogue; place its video and embedded audio at identical source/record bounds, at100% and linked. Split TTS only in confirmed nonspeech between anchor words; do not overlap dialogue and VO.'})
    result['episodes'].append({'episode':ep['episode'],'external_dialogue_units':units,'retained_internal_monologue':[q for q in ep['quoted_spans'] if q['action']=='retain_narrated_internal_self_talk']})
result['dialogue_unit_count']=sum(len(e['external_dialogue_units']) for e in result['episodes'])
result['same_segment_dialogue_insertions']=sum(u['same_tts_segment_requires_native_split_for_dialogue'] for e in result['episodes'] for u in e['external_dialogue_units'])
assert result['dialogue_unit_count']==40
p=OUT/'同期对白与旁白接续点_仅原文待实测时码.json';p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'output':str(p),'dialogue_units':result['dialogue_unit_count'],'same_tts_segment_insertions':result['same_segment_dialogue_insertions'],'audio_and_video_timing_invented':False},ensure_ascii=False))
