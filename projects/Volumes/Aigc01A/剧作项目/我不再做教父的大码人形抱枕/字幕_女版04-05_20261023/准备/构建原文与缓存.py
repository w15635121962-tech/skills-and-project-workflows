# -*- coding: utf-8 -*-
from pathlib import Path
import collections,datetime as dt,hashlib,json,re,subprocess,zipfile,xml.etree.ElementTree as ET
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1];SRC=ROOT/'完整剧本/我不再做教父的大码人形抱枕EN.docx'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def save(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert sha(SRC)=='f7929afa92104c692296732fb0c165378f5cbedc9fb43c98557c284a70f2888d'
priorpath=ROOT/'女版04-06_新旁白_20261023/文本核验/manifest.json';prior=read(priorpath);assert prior['source_docx_sha256']==sha(SRC)
with zipfile.ZipFile(SRC)as z:tree=ET.fromstring(z.read('word/document.xml'))
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};TAG='{'+NS['w']+'}'
ps=[''.join((n.text or'')if n.tag==TAG+'t'else'\n'if n.tag in(TAG+'br',TAG+'cr')else'\t'if n.tag==TAG+'tab'else''for n in p.iter())for p in tree.findall('.//w:body/w:p',NS)]
heads={int(m.group(1)):i for i,t in enumerate(ps,1)if(m:=re.fullmatch(r'Episode\s+(\d+)',t.strip()))}
roles={118:'Eliza',126:'Matteo Bellandi',127:'Matteo Bellandi',131:'Eliza',142:'Eliza',143:'Matteo Bellandi',145:'Matteo Bellandi',146:'Matteo Bellandi',151:'Matteo Bellandi',152:'Matteo Bellandi',154:'Eliza',156:'Matteo Bellandi',157:'Matteo Bellandi',159:'Matteo Bellandi',163:'Vincent',164:'Vincent',165:'Vincent',174:'Matteo Bellandi',179:'Eliza',180:'Eliza'}
made=[]
for ep in(4,5):
 old=next(e for e in prior['episodes']if e['episode']==ep);recordmap={r['docx_paragraph']:r for r in old['original_paragraphs_and_retained_narration']};segments=[];paragraphs=[]
 for pn in range(heads[ep]+1,heads[ep+1]):
  raw=ps[pn-1];items=[]
  if not raw.strip():paragraphs.append(dict(paragraph=pn,kind='empty',text_raw=raw));continue
  if re.search(r'[\u3400-\u9fff]',raw):items=[dict(kind='stage_direction',text=raw,speaker=None,subtitle_included=False,language='zh',source_text_span=[0,len(raw)],text_raw_exact=raw)]
  else:
   rec=recordmap[pn];assert rec['raw_source_text']==raw
   n=rec['narration_retained_text']
   if n.strip():
    # EP04/05 have no mixedactorquotes outside auditednarrative-term paragraphs.
    a=raw.index(n);items.append(dict(kind='narration',text=n.strip(),speaker='Eliza (narrator)',subtitle_included=True,language='en',source_text_span=[a,a+len(n)],text_raw_exact=n))
    if pn in(138,176,177):items[-1]['embedded_quoted_narrative_terms']=[m.group(1)for m in re.finditer(r'"([^\"]*)"',n)]
   for q in old['quoted_spans']:
    if pn not in q['docx_paragraphs']or not q['action'].startswith('exclude'):continue
    qt=q['text'];a=raw.index(qt)+1;t=qt[1:-1];items.append(dict(kind='character_dialogue',text=t,speaker=roles[pn],subtitle_included=True,language='en',source_text_span=[a,a+len(t)],text_raw_exact=t,source_quoted_text_exact=qt))
   items.sort(key=lambda s:s['source_text_span'][0]);assert items
  for i,s in enumerate(items,1):
   s.update(id=f'EP{ep:02d}-P{pn:03d}-{s["kind"]}-{i:02d}',episode=ep,source_docx_paragraph=pn,start_seconds=None,end_seconds=None,media_path=None,word_timing_source=None)
   a,b=s['source_text_span'];assert raw[a:b]==s['text_raw_exact'];segments.append(s)
  target=raw if pn in(138,176,177)else raw.replace('"','');assert ''.join(s['text_raw_exact']for s in items).strip()==target.strip()
  paragraphs.append(dict(paragraph=pn,text_raw=raw,kind='mixed'if len(items)>1 else items[0]['kind'],segment_ids=[s['id']for s in items],outer_whitespace_retained_in_paragraph_evidence=True))
 counts=collections.Counter(s['kind']for s in segments);narr=[s for s in segments if s['kind']=='narration'];assert [s['source_docx_paragraph']for s in narr]==old['retained_narration_docx_paragraphs']
 english=[s for s in segments if s['subtitle_included']]
 report=dict(status='CANONICAL_FEMALE_SOURCE_READY_ORIGINAL_PICTURE_TIMING_PENDING',episode=ep,version='female_original',source_docx=str(SRC),source_docx_sha256=sha(SRC),source_paragraph_numbering='1-basedword/document.xml body/w:p includingempties',source_heading_paragraph=heads[ep],source_paragraph_range=[heads[ep]+1,heads[ep+1]-1],target_timeline=f'大码_女版_EP{ep:02d}',excluded_target='newnarrationoriginalspeedaudioonlytesttimeline',target_timeline_fps=None,target_timeline_start_frame=None,subtitle_language='en',maximum_lines_per_futurecue=3,summary=dict(english_subtitle_segments=len(english),narration_segments=counts['narration'],character_dialogue_segments=counts['character_dialogue'],stage_directions_excluded=counts['stage_direction'],english_whitespace_words=sum(len(s['text'].split())for s in english)),previous_verified_narration_manifest=str(priorpath),previous_manifest_sha256=sha(priorpath),all_narration_matches_previous_authoritative_source=True,all_original_English_words_punctuation_order_preserved=True,source_outer_whitespace_policy='Exactoriginalrawparagraphretained; subtitlecontenttrimsonlyouterwhitespaceanddialoguequotewrappers.',paragraphs=paragraphs,segments=segments,narration=narr,spoken_dialogue=[s for s in segments if s['kind']=='character_dialogue'],notes=['P138diaryMatteo/I love youandP176/177Mercer/my pilloware narrativequotedobjects; notactorutterances.','P174EllieisactualMatteodialogue; presentinsubtitlecanonicalbutexcludedfromnarrationTTS.','NoASR/newaudiodecode/UI/Resolve/API/sourcechangeshere.','ExistingnewVOwordtimesareonlysourceclockandcannotbedirectlyappliedtooriginalpicturetimeline.'],source_modified=False)
 jp=OUT/f'episode{ep}_canonical.json';save(jp,report)
 lines=[f'# 女版第{ep}集字幕原文','',f'目标：原画面 `大码_女版_EP{ep:02d}`，不使用新旁白音频测试时间线时钟。',f'旁白{counts["narration"]}段，人物对白{counts["character_dialogue"]}段；中文画面备注{counts["stage_direction"]}段不入英文字幕。','时码等待Root当前时间线映射；未来每条最多三行。','']
 for s in segments:lines.extend([f'P{s["source_docx_paragraph"]} [{s["kind"]} / {s["speaker"]}]',s['text'],''])
 (OUT/f'episode{ep}_canonical.md').write_text('\n'.join(lines),encoding='utf-8');made.append(dict(episode=ep,path=str(jp),sha256=sha(jp),summary=report['summary']))
paths=[Path(p)for p in subprocess.run(['rg','--files','.'],capture_output=True,text=True,encoding='utf-8',check=True).stdout.splitlines()];rx=re.compile(r'(?:^|[^a-z0-9])EP0?[45](?:[^0-9]|$)',re.I)
srts=[p for p in paths if p.suffix.lower()=='.srt'and not re.search('男版|性转',str(p))and(rx.search(p.name)or re.search(r'女版(?:枕头)?0?[45](?:[-_.]|$)',p.name))]
selected=read(ROOT/'女版04-06_新旁白_20261023/最终采用清单.json');caches=[]
for f in selected['files']:
 if f['episode']not in(4,5):continue
 p=ROOT/'女版04-06_新旁白_20261023/ASR/raw_large-v3-turbo/narration'/f"{f['basename']}.json";a=read(p);assert a['source_sha256']==f['sha256']
 caches.append(dict(episode=f['episode'],basename=f['basename'],asr_path=str(p),asr_sha256=sha(p),audio_source_path=a['source_path'],audio_source_sha256=a['source_sha256'],selected_delivery_path=f['audio_file'],word_count=len(a['words']),clock='per-sourceMP3relative0',content_scope='newfemaleoriginalspeednarrationonly_noactordialogue',direct_original_picture_timeline_reuse=False,reason='Requirecurrentoriginalpicturemedia/rate/trimmap; newVOtesttimingdiffersandlacksactordialogue.'))
related=[]
for ep in(4,5):
 for p,kind in[(ROOT/f'剧梦生成视频片段/媒体打包/女版人形抱枕/女版/女版人形抱枕/EP{ep}.drt','historicalpicturetimeline'),(ROOT/f'达芬奇_女版04-06旁白剪辑_20261023/备份/大码_女版_EP{ep:02d}_操作前.drt','originalpicturetimelinebackupbeforeaudioonlytests'),(ROOT/f'达芬奇_女版04-06旁白剪辑_20261023/大码_女版_EP{ep:02d}_新旁白原速测试_20261023.drt','EXCLUDED_audioonlytesttimeline')]:
  if not p.exists():continue
  with zipfile.ZipFile(p)as z:xml='\n'.join(z.read(n).decode('utf-8','replace')for n in z.namelist()if n.endswith('.xml'))
  related.append(dict(episode=ep,path=str(p),sha256=sha(p),kind=kind,contains_srt_reference=bool(re.search(r'\.srt',xml,re.I)),contains_subtitle_track_marker='SubtitleTrackVec'in xml,usable_as_current_subtitle_timing=False,reason='Rootlivepicturetimelineinspectionrequired; snapshotisnotthecurrenttimingauthorityandtesttimelineisexcluded.'))
fresh=ROOT/'字幕_女版04-05_20261023/操作前实读.json'
if fresh.exists():related.append(dict(path=str(fresh),sha256=sha(fresh),kind='RootcurrentliveinspectionJSON',usable_as_current_subtitle_timing=False,reason='Rootwillconfirmthiscurrentclipmap; stillnospeechcueclockhere.'))
inv=dict(status='NO_CONFIRMED_EXISTING_FEMALE_EP04_EP05_SRT_SOURCE_NEWVO_WORDCACHES_REQUIRE_MAP',created_at_utc=dt.datetime.now(dt.timezone.utc).isoformat(),scope='Female4/5originalpicturetimelinesonly',search_root=str(ROOT),search_method='rg--files; exactepisodebasenameorverifiedmetadata; campaign04-06dirnamealoneisnotepisodeproof.',confirmed_female_SRT_count=len(srts),SRT_candidates=[dict(path=str(p.resolve()),sha256=sha(p),current_timeline_match_unconfirmed=True)for p in srts],selected_newVO_wordcache_count=len(caches),selected_newVO_wordcaches=caches,related_timeline_caches=related,canonical_outputs=made,source_text_helpers=[str(priorpath),str(ROOT/'达芬奇_女版04-06旁白剪辑_20261023/原文对白占位.json')],excluded_sources=['Allmale/genderswapfiles','AudioonlynewVOtesttimelineclock','EP01-04orEP02-05storyboardnumbersarenotepisode4/5'],ASR_performed=False,audio_decoded=False,UI_or_Resolve_API=False,source_modified=False)
ip=OUT/'可用缓存目录清单.json';save(ip,inv)
md=['# 女版4、5集字幕缓存','','- 未找到已证实可直接复用的女版4/5集SRT。','- 有15个已采用新旁白的源词码（4集8段，5集7段；05-03采用02）。仅为源MP3时钟、无演员对白，不可套到原画面。','- 原画面DRT/操作前备份可作映射参考；新旁白原速音频测试及其时间码明确排除。','- 等Root当前原画面媒体/rate/trim映射，必要时原生隔离混音；当前未ASR/未解码/未UI/API。','','原文文件：','']
for f in made:md.append(f'- 第{f["episode"]}集：`{f["path"]}`，SHA `{f["sha256"]}`。')
md+=['','P138的Matteo/I love you与P176/177的Mercer/my pillow均为叙述内引号内容；P174“Ellie.”是男主真实对白，必须区分。',''];(OUT/'可用缓存目录清单.md').write_text('\n'.join(md),encoding='utf-8')
print(json.dumps(dict(canonical=made,confirmed_female_SRT_count=len(srts),selected_newVO_wordcaches=len(caches),inventory=str(ip),inventory_sha256=sha(ip)),ensure_ascii=False,indent=2))
