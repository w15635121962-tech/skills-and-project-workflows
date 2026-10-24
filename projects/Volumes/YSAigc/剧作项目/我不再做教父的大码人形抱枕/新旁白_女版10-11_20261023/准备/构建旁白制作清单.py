# -*- coding: utf-8 -*-
"""Exact femaleoriginal narration-only preparation; noTTS/UI/Resolve operations."""
from pathlib import Path
import hashlib,json,re,zipfile,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent;TASK=OUT.parent
SOURCE=ROOT/'完整剧本/我不再做教父的大码人形抱枕EN.docx'
PREVIOUS=ROOT/'女版04-06_新旁白_20261023/文本核验/manifest.json'
POLICY=ROOT/'对标音色旁白制作_20261020/文本核验/build_text_manifest.py'
SHA=lambda x:hashlib.sha256(x.encode('utf-8')if isinstance(x,str)else x).hexdigest()
WORD=re.compile(r"[A-Za-z0-9]+(?:[’'\-][A-Za-z0-9]+)*")
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};TAG='{'+NS['w']+'}'
source_bytes=SOURCE.read_bytes();assert SHA(source_bytes)=='f7929afa92104c692296732fb0c165378f5cbedc9fb43c98557c284a70f2888d'
prev=json.loads(PREVIOUS.read_text(encoding='utf-8'));assert prev['voice']=='对标女旁白_测试A_1020'and prev['model']=='Seed TTS'and prev['mode']=='文本朗读'and prev['speed_percent']==100
policytext=POLICY.read_text(encoding='utf-8');assert 'exclude character dialogue and quoted message dialogue'in policytext

def write(p,text):
 p=Path(p);assert p.resolve().is_relative_to(OUT.resolve())and not p.is_symlink()
 if p.exists():assert p.read_text(encoding='utf-8')==text,f'Existingdifferentoutputnot silentlyoverwritten:{p}'
 else:p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
 assert p.read_text(encoding='utf-8')==text

def save(p,x):write(p,json.dumps(x,ensure_ascii=False,indent=2)+'\n')
with zipfile.ZipFile(SOURCE)as z:tree=ET.fromstring(z.read('word/document.xml'))
eps={};ep=None
for pn,p in enumerate(tree.findall('.//w:body/w:p',NS),1):
 raw=''.join((e.text or'')if e.tag==TAG+'t'else'\n'if e.tag in(TAG+'br',TAG+'cr')else'\t'if e.tag==TAG+'tab'else''for e in p.iter());text=raw.strip()
 m=re.fullmatch(r'Episode\s+(\d+)',text,re.I)
 if m:ep=int(m.group(1));eps[ep]=dict(heading=text,heading_paragraph=pn,blocks=[],omitted=[]);continue
 if ep not in(10,11):continue
 reason='empty'if not text else'chinese_visual_direction'if re.search(r'[\u3400-\u9fff]',text)else'scene_divider'if re.fullmatch(r'[-–—_=\s]+',text)else None
 if reason:eps[ep]['omitted'].append(dict(paragraph=pn,text_raw=raw,reason=reason));continue
 eps[ep]['blocks'].append(dict(docx_paragraph=pn,raw_source_text=raw,english_text=text))
manifest=dict(project='我不再做教父的大码人形抱枕',version='女版',scope_episode_order=[10,11],status='text_verified_not_generated',source_docx=str(SOURCE),source_docx_sha256=SHA(source_bytes),source_paragraph_numbering='1-basedword/document.xml body/w:p includingemptyparagraphs',output_kind='English narration only; exclude character dialogue and quoted message dialogue',voice=prev['voice'],model=prev['model'],mode=prev['mode'],speed=1.0,speed_percent=100,pitch_policy=prev['pitch_policy'],maximum_input_characters=200,voice_evidence=dict(inherited_authoritative_manifest=str(PREVIOUS),manifest_sha256=SHA(PREVIOUS.read_bytes()),source_voice_evidence=prev['voice_evidence'],current_account_or_voice_availability='Not verified here; RootownsJimengandpaidgeneration.'),prior_policy_sources=[str(PREVIOUS),str(POLICY)],extraction_rules=['Use authoritative originalfemaleDOCX, notactualeditedASR or repeatedoldtimelineaudio.','Trimsourceparagraphouterwhitespaceonly; preservealloriginalnarrativeEnglishwords,punctuation,internalnewlinesandparagraphseparators.','Excludeheadings/emptyparagraphs/Chinesestagedirections.','Removepairedquotedcharacterandmessagedialogueentirely, preservingwhitespaceoutsideremovedspans.','EP10writtenmessagequotesP322/P324excludedbyexplicitpriorTTSmessage-dialoguepolicy; originalreportingnarrationP321/P323retained. Noembeddeddiary/namequoteexceptionoccursinEP10/11.','Retainreportingfragmentswithoutrewriting,combinewithfollowingoriginalnarrationunit.','Greedygroupcompletecontiguousnarrativeunits<=200Unicodecharactersincludingretainednewlines.','generation_text=source_text.strip()only; groupedsource_textsreconstructentireextractednarrationverbatim.'],naming_rule='大码女版枕头EE-SS-01; EE=episode;SS=narrationsequenceinscriptorder;01=firsttake.NotassertedJumengstoryboardnumber.',episodes=[],groups=[])
coverage=[];messages=[]
for number in(10,11):
 e=eps[number];blocks=e['blocks'];full='\n'.join(b['english_text']for b in blocks);cursor=0
 for i,b in enumerate(blocks):b['source_start']=cursor;b['source_end_exclusive']=cursor+len(b['english_text']);cursor=b['source_end_exclusive']+(i+1<len(blocks))
 assert cursor==len(full);mask=[True]*len(full);quotes=[]
 for m in re.finditer(r'"[^\"]*"',full):
  a,z=m.span();touched=[b['docx_paragraph']for b in blocks if b['source_start']<z and b['source_end_exclusive']>a]
  kind='quoted_message_dialogue'if touched[0]in(322,324)else'character_spoken_dialogue'
  q=dict(source_start=a,source_end_exclusive=z,text=full[a:z],docx_paragraphs=touched,action='exclude_'+kind,reason='ExplicitauthoritativepriorTTSruleexcludesroleandquotedmessagedialogue.');quotes.append(q);mask[a:z]=[False]*(z-a)
  if kind=='quoted_message_dialogue':messages.append(dict(episode=number,source_docx_paragraph=touched[0],text=full[a+1:z-1],formal_generation=False,reason=q['reason'],source_reporting_narration_retained=True,policy_source=str(POLICY),optional_change_policy='OnlyifRootexplicitlyoverridesmessageexclusionbeforegeneration; do notsilentlyappendtomainchunks.'))
 assert full.count('"')==2*len(quotes)
 narration=''.join(ch for i,ch in enumerate(full)if mask[i]);records=[]
 for b in blocks:
  a,z=b['source_start'],b['source_end_exclusive'];kept=''.join(full[i]for i in range(a,z)if mask[i]);sep='\n'if z<len(full)else''
  records.append(dict(**b,narration_retained_text=kept,narration_with_original_separator=kept+sep,classification='narration_preserved'if kept.strip()else'quoted_dialogue_excluded'))
 assert ''.join(x['narration_with_original_separator']for x in records)==narration
 assert not re.search(r'[\u3400-\u9fff]',narration)and'"'not in narration
 units=[];pending='';ps=[]
 for r in records:
  piece=r['narration_with_original_separator']
  if not piece.strip()and not pending and units:units[-1]['source_text']+=piece;units[-1]['source_context_docx_paragraphs'].append(r['docx_paragraph']);continue
  pending+=piece;ps.append(r['docx_paragraph'])
  if piece.strip()and re.search(r'[.!?]\s*$',piece):
   units.append(dict(source_text=pending,source_context_docx_paragraphs=ps));pending='';ps=[]
 if pending.strip():raise ValueError(('Incompleteending',number,pending))
 if pending:units[-1]['source_text']+=pending;units[-1]['source_context_docx_paragraphs']+=ps
 assert ''.join(u['source_text']for u in units)==narration
 prepared=[];text='';context=[]
 for u in units:
  assert len(u['source_text'].strip())<=200,('Unit>200',number,u)
  if text and len((text+u['source_text']).strip())>200:prepared.append((text,context));text='';context=[]
  text+=u['source_text'];context+=u['source_context_docx_paragraphs']
 if text:prepared.append((text,context))
 assert ''.join(t for t,ps in prepared)==narration
 actual_pns=[r['docx_paragraph']for r in records if r['narration_retained_text'].strip()]
 episodegroups=[]
 for seq,(text,context)in enumerate(prepared,1):
  gen=text.strip();name=f'大码女版枕头{number:02d}-{seq:02d}-01';tp=OUT/'分段'/(name+'.txt');write(tp,gen)
  actual=[pn for pn in dict.fromkeys(context)if next(r for r in records if r['docx_paragraph']==pn)['narration_retained_text'].strip()]
  row=dict(source_text=text,generation_text=gen,source_docx_paragraphs=actual,source_context_docx_paragraphs=list(dict.fromkeys(context)),episode=number,narration_sequence=seq,take=1,basename=name,planned_audio_filename=name+'.mp3',planned_audio_path=str(TASK/'音频'/f'第{number:02d}集'/(name+'.mp3')),text_file=str(tp),characters=len(gen),words=len(WORD.findall(gen)),voice=prev['voice'],speed_percent=100,generation_text_sha256=SHA(gen),source_text_sha256=SHA(text),status='text_verified_not_generated',original_storyboard_number=None,sequence_mapping_basis='Authoritativeoriginalfemalenarrationparagraphorder; completeunits<=200chars')
  manifest['groups'].append(row);episodegroups.append(row)
 out=OUT/f'女版_EP{number:02d}_英文旁白.txt';write(out,narration)
 eout=dict(episode=number,source_heading=e['heading'],source_heading_docx_paragraph=e['heading_paragraph'],output_path=str(out),output_sha256=SHA(narration),narration_words=len(WORD.findall(narration)),narration_characters=len(narration),retained_narration_docx_paragraphs=actual_pns,retained_narration_paragraph_count=len(actual_pns),segment_count=len(episodegroups),excluded_actor_dialogue_quote_count=sum('character_spoken'in q['action']for q in quotes),excluded_quoted_message_count=sum('quoted_message'in q['action']for q in quotes),quoted_spans=quotes,original_paragraphs_and_retained_narration=records,excluded_nonspoken_source_paragraphs=e['omitted'],source_reconstruction_verbatim=True,generation_only_trims_segment_outer_whitespace=True)
 manifest['episodes'].append(eout)
 can= json.loads((ROOT/'字幕_女版10-11_20261023/原文'/f'episode{number}_canonical.json').read_text(encoding='utf-8'))
 expected=[s for s in can['segments']if s['kind']=='narration'];observed=' '.join(r['narration_retained_text'].strip()for r in records if r['narration_retained_text'].strip());assert re.sub(r'\s+',' ',observed)==re.sub(r'\s+',' ',' '.join(s['text']for s in expected))
 coverage.append(dict(episode=number,canonical_narration_count=len(expected),extracted_narration_paragraph_count=len(actual_pns),all_canonical_narration_once_in_source_order=True,canonical_narration_words_punctuation_exact=True,chunk_source_concat_verbatim=True,all_generation_inputs_max200=True,formal_groups=len(episodegroups),narration_words=eout['narration_words'],source_paragraphs=actual_pns,excluded_actor_quotes=eout['excluded_actor_dialogue_quote_count'],excluded_message_quotes=eout['excluded_quoted_message_count'],restored_original_narration_not_oldmix=number==11,actual_mix_extra_words_not_imported=True))
manifest['totals']=dict(episode_count=2,segment_count=len(manifest['groups']),narration_words=sum(x['narration_words']for x in manifest['episodes']),maximum_actual_input_characters=max(g['characters']for g in manifest['groups']),excluded_actor_dialogue_spans=sum(e['excluded_actor_dialogue_quote_count']for e in manifest['episodes']),excluded_message_dialogue_spans=len(messages),source_narration_exact_once=True,all_text_readbacks_exact=True,all_source_reconstructions_exact=True,source_docx_unchanged=SOURCE.read_bytes()==source_bytes,platform_actions=False,audio_generation=False,existing_audio_files_touched=False)
save(OUT/'manifest.json',manifest);save(OUT/'短信原句_按旧规则排除的选择说明.json',dict(status='EXCLUDED_FROM_FORMAL_TTS_BY_EXISTING_POLICY',policy_file=str(POLICY),policy_sha256=SHA(POLICY.read_bytes()),policy_excerpt='English narration only; exclude character dialogue and quoted message dialogue',messages=messages,no_optional_audio_generated=True))
report=dict(status='PASS_TEXT_ONLY_EXACT_CANONICAL_NARRATION_NO_TTS',source_docx=str(SOURCE),source_docx_sha256=SHA(source_bytes),manifest_file=str(OUT/'manifest.json'),manifest_sha256=SHA((OUT/'manifest.json').read_bytes()),prior_manifest=str(PREVIOUS),prior_manifest_sha256=SHA(PREVIOUS.read_bytes()),prior_exclusion_policy=str(POLICY),episodes=coverage,totals=manifest['totals'],written_message_decision='ExcludeP322/P324standalonequotedmessagesbyexplicitpriorTTSrule; retainreportingnarrationP321/P323. NoadditionaluserconfirmationrequiredunlessRootchoosesoverride.',important_source_restorations=['EP11P343–346narrationretaineddespiteunreadinoldcut.','EP11P348/349eachonce,notoldcutduplicates.','EP11P350originaldaredmistake,notoldcutaddedto.','EP11P362narratorprefixretained;quotedMatteoquestionexcluded.'],source_inputs_modified=False,UI_or_Resolve_operations=False,paid_generation=False)
save(OUT/'源文覆盖核验.json',report)
lines=['# 女版10–11新旁白准备','','- 正式仅旁白；Seed TTS／文本朗读／对标女旁白_测试A_1020／100%原速，不做音高处理。','- 严格采用女版原DOCX，不沿用旧剪辑重复、漏句或ASR改词。','- 沿旧权威TTS规则排除人物对白与引号内消息对白；P322/P324短信两句未进入正式生成文本，叙述“我发消息/她回复”照留。',f'- 共{manifest["totals"]["segment_count"]}段、{manifest["totals"]["narration_words"]}词；每段最多{manifest["totals"]["maximum_actual_input_characters"]}字符（含换行），命名按集/序/次。','', '|集|段数|原旁白词|源段落数|排除人物对白|排除短信|','|---|---:|---:|---:|---:|---:|']
for e in manifest['episodes']:lines.append(f'|{e["episode"]}|{e["segment_count"]}|{e["narration_words"]}|{e["retained_narration_paragraph_count"]}|{e["excluded_actor_dialogue_quote_count"]}|{e["excluded_quoted_message_count"]}|')
lines+=['','原文完整性：','','- 第11集原343–346段恢复，348/349仅出现一次；dared mistake保留原词，不复制旧混音额外to。','- P362叙述引语前缀照留，只排男主引号对白；所有衣物描写属于原旁白，未照视频提示词清理规则改写。','- 分段source_text拼回完整提取旁白逐字符一致；generation_text仅去各分段外侧空白。','- 未操作浏览器、即梦、达芬奇或付费生成；未移动或覆盖现有音频。','',f'清单SHA：`{report["manifest_sha256"]}`。','']
write(OUT/'源文覆盖核验.md','\n'.join(lines))
assert SOURCE.read_bytes()==source_bytes
print(json.dumps(dict(manifest=str(OUT/'manifest.json'),manifest_sha256=report['manifest_sha256'],totals=manifest['totals'],episodes=[dict(episode=e['episode'],segments=e['segment_count'],words=e['narration_words'])for e in manifest['episodes']]),ensure_ascii=False,indent=2))
