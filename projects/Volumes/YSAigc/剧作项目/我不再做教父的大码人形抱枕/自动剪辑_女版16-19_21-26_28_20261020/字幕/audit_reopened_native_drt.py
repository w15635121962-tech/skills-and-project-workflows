from pathlib import Path
import datetime,hashlib,json,re,xml.etree.ElementTree as ET,zipfile

SUB=Path(__file__).resolve().parent
ARCH=SUB/'保存重开后_原生预设时间线'
SRT=SUB/'SRT'
scope=[16,17,18,19,21,22,23,24,25,26,28]

def sha_bytes(b):return hashlib.sha256(b).hexdigest()
def sha_file(p):return sha_bytes(p.read_bytes())
def norm(s):
 s=re.sub(r'<br\s*/?>',' ',s,flags=re.I)
 for sep in ('\\u2028','\\u2029','\u2028','\u2029','\\r\\n','\\n'):s=s.replace(sep,' ')
 return re.sub(r'\s+',' ',s).strip()
def parse_srt(p):
 def fr(t):
  h,m,s,ms=map(int,re.split('[:,]',t));return round(((h*3600+m*60+s)*1000+ms)*24/1000)
 result=[]
 for block in re.split(r'\n[ \t]*\n',p.read_text(encoding='utf-8-sig').replace('\r\n','\n').strip()):
  lines=block.split('\n');a,b=lines[1].split(' --> ')
  result.append({'cue':int(lines[0]),'start':fr(a),'end':fr(b),'text':norm('\n'.join(lines[2:]))})
 return result

documents=[];raw_track_blobs={};errors=[]
for ep in scope:
 p=ARCH/f'EP{ep}_字幕预设已载入.drt'
 assert p.exists(),p
 file_hash=sha_file(p);found=[];xmlnames=[]
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None, f'ZIP CRC failure: {p}'
  for name in z.namelist():
   if not name.endswith('.xml'):continue
   xml=z.read(name).decode('utf-8-sig');xmlnames.append(name)
   if not name.startswith('SeqContainer/'):continue
   # Parse the explicit subtitle subtree only. project.xml has qualified type names
   # such as ListMgt::LmPowerNodeList, so no private document/schema repair is attempted.
   m=re.search(r'<SubtitleTrackVec>([\s\S]*?)</SubtitleTrackVec>',xml)
   if not m:continue
   root=ET.fromstring(m.group(0))
   for tr in root.findall('./Element/Sm2TiTrack'):
    if tr.findtext('UserDefinedName')!=str(ep):continue
    blob=tr.findtext('FieldsBlob') or ''
    raw_track_blobs[ep]=blob
    captions=tr.findall('./Items/Element/Sm2TiGenerator')
    style_tags=[];caption_overrides=[];flag_sets={};html_tags=set();cues=[]
    for tag in tr.iter():
     if re.search(r'font|typeface|weight|size|position|scale|shadow|color|alignment|tracking|spacing|outline|stroke|style',tag.tag,re.I):
      style_tags.append({'tag':tag.tag,'value':tag.text or ''})
    for n,cap in enumerate(captions,1):
     text=cap.findtext('Name') or '';start=int(cap.findtext('Start') or '0');duration=int(cap.findtext('Duration') or '0')
     cues.append({'cue':n,'start':start,'end':start+duration,'text':norm(text)})
     html_tags.update(re.findall(r'<\s*/?\s*([a-zA-Z][a-zA-Z0-9]*)\b',text))
     flags={}
     for key in ('RenderTextEnabled','RenderTextGanged','RenderTextPrefixed','Flags','PriorityIndex'):
      val=cap.findtext(key);flags[key]=val;flag_sets.setdefault(key,set()).add(val)
     explicit=[]
     for node in cap.iter():
      if re.search(r'font|typeface|weight|size|position|scale|shadow|color|alignment|tracking|spacing|outline|stroke|style',node.tag,re.I):explicit.append({'tag':node.tag,'value':node.text or ''})
     if re.search(r'(style\s*=|<\s*(?:font|span|b|i|u)\b)',text,re.I):explicit.append({'tag':'Name_rich_text_style_markup','value':text})
     if explicit:caption_overrides.append({'cue':n,'explicit_fields':explicit})
    srtpath=SRT/(f'EP{ep}.srt' if ep<20 else f'EP{ep}_当前轨道_三行以内.srt' if ep<=25 else 'EP26_含预排旁白.srt' if ep==26 else 'EP28_预排旁白.srt')
    source_cues=parse_srt(srtpath);diff=[]
    if len(cues)!=len(source_cues):diff.append({'kind':'cue_count','drt':len(cues),'srt':len(source_cues)})
    for native,src in zip(cues,source_cues):
     for key in ('text','start','end'):
      if native[key]!=src[key]:diff.append({'cue':native['cue'],'kind':key,'drt':native[key],'srt':src[key]})
    row={'episode':ep,'archive':str(p.resolve()),'archive_sha256':file_hash,'zip_crc_valid':True,'xml_documents_read':xmlnames,'selected_sequence_xml':name,'selected_track_context':'SeqContainer XML / SubtitleTrackVec / Element / Sm2TiTrack; UserDefinedName matches episode','native_track_name':tr.findtext('UserDefinedName'),'cue_count':len(captions),'track_FieldsBlob_characters':len(blob),'track_FieldsBlob_sha256_of_verbatim_utf8_text':sha_bytes(blob.encode('utf-8')),'opaque_track_payload_decoded':False,'explicit_native_track_fields':{key:tr.findtext(key) for key in ('Type','SubType','Flags','FusionCompHolderItems','LayersVec')},'plaintext_style_fields':style_tags,'caption_explicit_flag_value_sets':{k:sorted(v,key=str) for k,v in flag_sets.items()},'caption_Name_html_tag_names':sorted(html_tags),'explicit_caption_style_override_fields':caption_overrides,'opaque_caption_FieldsBlob_count':sum(bool(c.findtext('FieldsBlob')) for c in captions),'source_SRT':str(srtpath.resolve()),'source_SRT_sha256':sha_file(srtpath),'cue_text_and_frame_differences_vs_SRT':diff,'prearranged_narration':ep in (26,28)}
    found.append(row)
 assert len(found)==1,(ep,len(found))
 assert file_hash==sha_file(p),f'Archive changed while reading: {p}'
 documents.append(found[0])
 if found[0]['cue_text_and_frame_differences_vs_SRT']:errors.append({'episode':ep,'cue_differences':found[0]['cue_text_and_frame_differences_vs_SRT']})

ref=next(d for d in documents if d['episode']==18)
for d in documents:
 ep=d['episode']
 d['verbatim_track_FieldsBlob_identical_to_loaded_EP18_export']=raw_track_blobs[ep]==raw_track_blobs[18]
 d['explicit_track_flags_identical_to_EP18']=d['explicit_native_track_fields']==ref['explicit_native_track_fields']
 d['explicit_caption_flag_value_sets_identical_to_EP18']=d['caption_explicit_flag_value_sets']==ref['caption_explicit_flag_value_sets']

report={'created_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'status':'CONSISTENT_PERSISTED_NATIVE_TRACK_PAYLOAD_STYLE_VALUES_OPAQUE' if all(d['verbatim_track_FieldsBlob_identical_to_loaded_EP18_export'] for d in documents) and not errors else 'DIFFERENCES_REQUIRE_REVIEW','scope':scope,'official_SDK_exports_only':True,'no_UI_or_project_mutation':True,'no_app_database_or_private_preset_binary_access':True,'opaque_payloads_decoded':False,'reference_episode':18,'total_native_cues':sum(d['cue_count'] for d in documents),'all_track_payloads_verbatim_identical_to_EP18':all(d['verbatim_track_FieldsBlob_identical_to_loaded_EP18_export'] for d in documents),'all_explicit_track_flags_identical_to_EP18':all(d['explicit_track_flags_identical_to_EP18'] for d in documents),'all_explicit_caption_flag_value_sets_identical_to_EP18':all(d['explicit_caption_flag_value_sets_identical_to_EP18'] for d in documents),'requested_style_values_not_plaintext_verified':['NotoSans','SemiBold','40','position540/575','scale0.96/1','shadow6'],'precise_font_position_scale_shadow_values_verified_from_XML':False,'explicit_plaintext_caption_style_overrides_found':sum(len(d['explicit_caption_style_override_fields']) for d in documents),'per_caption_opaque_style_overrides_ruled_out':False,'errors':errors,'episodes':documents,'limits':['Exact matching subtitle-track FieldsBlob proves the same verbatim native track payload survived the saved/reopened exports; it does not decode or independently identify font, coordinates, scale or shadow values.','No explicit per-caption font/style tags or rich-text styling were found, but opaque caption FieldsBlob values were not decoded, so absence of hidden caption-specific style overrides is not asserted.','RenderTextEnabled/Ganged/Prefixed value equality is reported without inferring undocumented semantics.','Root visual/UI checks are needed for exact preset values, actual automatic wrapping, clipping, safe area and readability.']}
(SUB/'11集预设_重开后导出核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
lines=['11集预设重开后官方DRT导出核验','',f"11份DRT均完整可读、ZIP CRC有效；字幕轨名16–19、21–26、28，对应合计{report['total_native_cues']}条。重开后导出的正文及起止帧与本次目标SRT完全一致，差异{len(errors)}。",'',f"明确位于SubtitleTrackVec/Sm2TiTrack且集号匹配的轨道FieldsBlob：11份原始文本均为{ref['track_FieldsBlob_characters']}字符，与已载入EP18完全一致。SHA256：{ref['track_FieldsBlob_sha256_of_verbatim_utf8_text']}。未解码，未读取应用数据库或私有预设二进制。",'', '可确认：相同原生字幕轨payload已随保存/重开保存在各DRT；轨道Type/SubType/Flags及逐字幕RenderTextEnabled/Ganged/Prefixed等明文值集合均与EP18一致。', '', '无法从导出XML明文独立核验：NotoSans、SemiBold、40、位置540/575、缩放0.96/1、阴影6。未发现显式逐字幕font/style字段或Name富文本样式（仅br换行），但逐字幕FieldsBlob仍不透明，不能据此保证没有隐藏样式覆盖。', '', '精确预设数值、实际换行、裁切与可读性继续以根代理重开后的UI与画面抽查为依据；此文不声称完成视觉或回放验收。']
(SUB/'11集预设_重开后导出核验.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({k:report[k] for k in ['status','total_native_cues','all_track_payloads_verbatim_identical_to_EP18','all_explicit_track_flags_identical_to_EP18','all_explicit_caption_flag_value_sets_identical_to_EP18','precise_font_position_scale_shadow_values_verified_from_XML','explicit_plaintext_caption_style_overrides_found','errors']},ensure_ascii=False,indent=2))
