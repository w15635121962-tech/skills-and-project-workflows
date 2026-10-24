from pathlib import Path
import json,re,sys
BASE=Path(__file__).resolve().parent
TASK=BASE.parent
sys.path.insert(0,str(TASK))
from subtitle_tools import original_words_on_timeline,cues_from_events,write_srt
plan=json.loads((BASE/'EP17_native_edit_plan.json').read_text(encoding='utf-8'))
ep=plan['episodes'][0]
manifest=json.loads((BASE/'narration_manifest.json').read_text(encoding='utf-8'))
anchors=json.loads((TASK/'ASR/旁白逐词与源段落锚点_采用版本.json').read_text(encoding='utf-8'))
anchorby={x['basename']:x for x in anchors['files']}
source_ep=next(e for e in manifest['episodes'] if e['episode']==17)
def norm(text):return re.sub('[^a-z0-9]','',text.lower())
def canonical_timed(canonical,raw):
    result=[];cursor=0;evidence=[]
    for word in canonical:
        end=None
        for count in range(1,4):
            if norm(''.join(w['word'] for w in raw[cursor:cursor+count]))==norm(word):end=cursor+count;break
        assert end is not None,('Original/ASR lexical mismatch',word,cursor,raw[cursor:cursor+3])
        ws=raw[cursor:end]
        result.append({'original_word':word,'start':ws[0]['start'],'end':ws[-1]['end']})
        if len(ws)>1:evidence.append({'original_word':word,'source_word_indices':list(range(cursor,end)),'raw_asr_words':[w['word'] for w in ws],'source_start_seconds':ws[0]['start'],'source_end_seconds':ws[-1]['end'],'reason':'Original hyphen/em-dash preserved; ASR used separate timed words, merged without rewriting source text.'})
        cursor=end
    assert cursor==len(raw)
    return result,evidence

vo_events=[];merge_evidence=[]
for g in manifest['groups']:
    if g['episode']!=17:continue
    a=anchorby[g['basename']];canonical=g['generation_text'].split()
    timed,evidence=canonical_timed(canonical,a['source_words'])
    merge_evidence.extend(dict(x,audio_basename=a['actual_audio_basename']) for x in evidence)
    events=original_words_on_timeline(timed,a['source_path'],ep['narration'])
    off=0
    for p in source_ep['original_paragraphs_and_retained_narration']:
        if p['docx_paragraph'] not in g['source_docx_paragraphs']:continue
        text=p['narration_retained_text'].strip()
        if not text:continue
        n=len(text.split());part=events[off:off+n]
        assert [x['word'] for x in part]==text.split()
        for index,event in enumerate(part):event.update(kind='narration',docx_paragraph=p['docx_paragraph'],boundary_before=index==0)
        vo_events.extend(part);off+=n
    assert off==len(events)

unit=ep['mandatory_dialogue_units'][0]
quote=source_ep['quoted_spans'][0]['text'][1:-1]
raw=json.loads((TASK/'ASR/raw_large-v3-turbo/EP17/video/男版17-5-1.json').read_text(encoding='utf-8'))
timed,evidence=canonical_timed(quote.split(),raw['words']);merge_evidence.extend(dict(x,source='男版17-5-1.mp4') for x in evidence)
dialogue=original_words_on_timeline(timed,unit['path'],ep['video'])
for index,event in enumerate(dialogue):
    event.update(kind='sync_dialogue',docx_paragraph=488,dialogue_id=unit['id'],boundary_before=index==0)
    assert not any(max(event['start_frame'],w['start_frame'])<min(event['end_frame'],w['end_frame']) for w in vo_events),'Narration overlaps dialogue'
events=sorted(vo_events+dialogue,key=lambda x:(x['start_frame'],x['end_frame']))
expected=[]
for p in source_ep['original_paragraphs_and_retained_narration']:
    if p['docx_paragraph']==488:expected.extend(quote.split())
    else:expected.extend(p['narration_retained_text'].split())
assert [x['word'] for x in events]==expected,'Original source text/order changed'
paragraph_order=[]
for event in events:
    if not paragraph_order or paragraph_order[-1]!=event['docx_paragraph']:paragraph_order.append(event['docx_paragraph'])
assert paragraph_order==list(range(475,491)),paragraph_order
cues=cues_from_events(events,ep['duration_frames'])
dest=TASK/'字幕/EP17.srt';write_srt(dest,cues)
ep['subtitle_srt']=str(dest)
(BASE/'EP17_native_edit_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
eventfile=BASE/'EP17_original_word_events.json'
eventfile.write_text(json.dumps({'fps':24,'episodes':[{'episode':17,'duration_frames':ep['duration_frames'],'events':events}]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
audit={'episode':17,'duration_frames':ep['duration_frames'],'duration_seconds':ep['duration_frames']/24,'video_clips':len(ep['video']),'narration_clips':len(ep['narration']),
    'source_paragraph_order':paragraph_order,'original_word_sequence_exact':True,'original_narration_words':len(vo_events),'original_dialogue_words':len(dialogue),'total_original_words':len(events),
    'raw_asr_word_join_evidence':merge_evidence,'all_original_dialogue_preserved_once':True,'dialogue_never_masked_by_narration':True,
    'cues':len(cues),'maximum_lines':max(len(c['text'].splitlines()) for c in cues),'maximum_characters_per_line':max(len(l) for c in cues for l in c['text'].splitlines()),
    'minimum_cue_duration_frames':min(c['end_frame']-c['start_frame'] for c in cues),'source_files_unchanged':True,'audio_speed_percent':100,'no_resolve_mutation':True,
    'limitations':['原片英语口音/Um与喘息边界来自盲ASR，尚未宣称人工逐句听验。','invitation中原文的backflips—way为单个空白词，按两个原始ASR词的联合时间保留原文标点。']}
(BASE/'EP17_剪辑与字幕核验.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'plan':str(BASE/'EP17_native_edit_plan.json'),'srt':str(dest),'events':str(eventfile),'audit':audit},ensure_ascii=False))
