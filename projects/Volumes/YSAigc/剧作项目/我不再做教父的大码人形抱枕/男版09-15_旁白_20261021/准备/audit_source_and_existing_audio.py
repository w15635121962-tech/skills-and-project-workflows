from pathlib import Path
import csv,hashlib,json,re,zipfile,xml.etree.ElementTree as ET
root=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕')
out=root/'男版09-15_旁白_20261021/准备'
m=json.loads((out/'narration_manifest.json').read_text())
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with zipfile.ZipFile(m['source_docx']) as z:tree=ET.fromstring(z.read('word/document.xml'))
paras={i:''.join(x.text or '' for x in p.findall('.//w:t',ns)).strip() for i,p in enumerate(tree.findall('.//w:body/w:p',ns),1)}
sha=lambda b:hashlib.sha256(b).hexdigest()
checks=[]
for e in m['episodes']:
 expected='\n'.join(paras[i] if i in (393,397) else re.sub(r'"[^\"]*"|“[^”]*”','',paras[i]) for i in e['source_body_docx_paragraphs'])
 # Every retained source paragraph carries its original newline, including quote-only blocks.
 actual=(out/f"男版_EP{e['episode']:02d}_英文纯旁白.txt").read_text()
 assert expected==actual,(e['episode'],repr(expected),repr(actual))
 gs=[g for g in m['groups'] if g['episode']==e['episode']]
 assert ''.join(g['source_text'] for g in gs)==expected
 assert all(g['generation_text']==g['source_text'].strip() and len(g['generation_text'])<=200 and Path(g['text_file']).read_text()==g['generation_text'] for g in gs)
 checks.append({'episode':e['episode'],'source_heading_paragraph':e['heading_docx_paragraph'],'source_paragraph_start':min(e['source_body_docx_paragraphs']),'source_paragraph_end':max(e['source_body_docx_paragraphs']),'generation_segment_count':len(gs),'generation_characters':sum(g['characters'] for g in gs),'max_segment_characters':max(g['characters'] for g in gs),'words':e['narration_words'],'exact_retained_source_text_and_order':True,'all_segment_files_readback_match':True,'excluded_external_dialogue_quotes':e['excluded_dialogue_quote_count'],'retained_internal_monologue_quotes':e['retained_internal_monologue_quote_count']})
existing=[]
audio_extensions={'.mp3','.wav','.m4a','.aac','.aiff','.flac'}
for p in sorted(root.rglob('*')):
 if not p.is_file() or p.suffix.lower() not in audio_extensions:continue
 ep=None
 if '旁白/男版/EP' in str(p):
  a=re.search(r'/旁白/男版/EP(\d+)/',str(p))
  if a:ep=int(a.group(1))
 elif '男版' in p.name:
  a=re.search(r'男版(?:枕头)?0?(9|1[0-5])[-_]',p.name)
  if a:ep=int(a.group(1))
 if ep in range(9,16):existing.append({'episode':ep,'path':str(p),'filename':p.name,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes()),'voice_identity':'unverified older recording; not assumed 男版新音色','is_new_task_filename':bool(re.fullmatch(r'大码男版枕头(?:09|1[0-5])-\d{2}-\d{2}\.mp3',p.name))})
result={'scope':'Local source text and existing-file audit only; no browser, generation, paid action or Resolve operations','source_docx':m['source_docx'],'source_sha256_unchanged':sha(Path(m['source_docx']).read_bytes())==m['source_docx_sha256'],'episodes':checks,'total_generation_segments':len(m['groups']),'total_generation_characters':sum(g['characters'] for g in m['groups']),'total_narration_words':sum(e['narration_words'] for e in m['episodes']),'EP13_internal_monologue_evidence':[{'docx_paragraph':393,'lead_in_paragraph':392,'lead_in':paras[392],'retained_text':paras[393],'legacy_narration_reference':'剧梦生成视频片段/大码人形抱枕/旁白/男版/旁白示意.docx P103–104'},{'docx_paragraph':397,'lead_in_paragraph':396,'lead_in':paras[396],'retained_text':paras[397],'legacy_narration_reference':'剧梦生成视频片段/大码人形抱枕/旁白/男版/旁白示意.docx P107–108'}],'additional_classification_notes':[{'docx_paragraph':437,'text':paras[437],'classification':'Unquoted short location-transition sentence retained verbatim, also present in legacy male narration reference P148.'}],'existing_audio_count':len(existing),'existing_audio':existing}
(out/'旁白文本独立核验.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
with (out/'生成下载命名清单.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.writer(f);w.writerow(['集','旁白顺序','版本次','计划音频名','字符数','词数','原稿段落','男版新音色','速度百分比','英文原文'])
 for g in m['groups']:w.writerow([g['episode'],g['narration_sequence'],g['take'],g['planned_audio_filename'],g['characters'],g['words'],','.join(map(str,g['source_docx_paragraphs'])),'男版新音色',100,g['generation_text']])
md=['# 男版09–15集旁白原文对照','',f"来源：`{m['source_docx']}`；SHA-256 `{m['source_docx_sha256']}`。",'', '仅制作男版英文旁白；音色「男版新音色」，100%正常语速。每段不超过200字符。SS为旁白顺序，不声称等同平台镜号。','', '|集|段数|生成字符|英文词|原稿正文段落|','|---|---:|---:|---:|---|']
for c in checks:md.append(f"|{c['episode']:02d}|{c['generation_segment_count']}|{c['generation_characters']}|{c['words']}|P{c['source_paragraph_start']:04d}–P{c['source_paragraph_end']:04d}|")
md+=['',f"总计44段、7000生成字符、1235英文词。40处外部说话对白剔除；EP13两处明确内心自我鼓励保留原引号。",'', 'EP13证据：P0392写“in my head”，故保留P0393；P0396写“A voice inside murmured.”，故保留P0397。既有男版《旁白示意.docx》P103–108也保留两句。','', 'P0437 “The Blackwood estate.”作为无引号的简短地点转场句保留，旧男版旁白示意P148也有该句。','', f'既有旧男版旁白音频：{len(existing)}个；音色身份未核实，不作为本轮新男版音色已完成文件。','']
for e in m['episodes']:
 md += [f"## 第{e['episode']:02d}集",'']
 for g in m['groups']:
  if g['episode']!=e['episode']:continue
  md += [f"### {g['planned_audio_filename']}（{g['characters']}字符）",'', '源段落：'+', '.join(f'P{i:04d}' for i in g['source_docx_paragraphs']), '', '```text',g['generation_text'],'```','']
(out/'男版09-15_旁白原文对照.md').write_text('\n'.join(md)+'\n')
print(json.dumps({'checks':checks,'existing_audio_by_episode':{str(ep):sum(x['episode']==ep for x in existing) for ep in range(9,16)},'existing_audio_total':len(existing),'new_task_audio_found':sum(x['is_new_task_filename'] for x in existing)},ensure_ascii=False,indent=2))
