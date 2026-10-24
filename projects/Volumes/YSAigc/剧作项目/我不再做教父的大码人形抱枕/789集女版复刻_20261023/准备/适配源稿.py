import json,re,hashlib
from pathlib import Path
ROOT=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕');OUT=ROOT/'789集女版复刻_20261023';SRC=Path('/Users/zc/Doubao/chats/2026-10-23/new-chat/复刻分镜')
D={}
def add(ep,n,speaker,text,p,continuation=None,delivery='in_scene'):
 D.setdefault((ep,n),[]).append({'speaker':speaker,'text':text,'source_docx_paragraph':p,'source_script_episode':7 if p<=249 else 8 if p<=276 else 9 if p<=298 else 10,'delivery':delivery,**({'continuation_of':continuation} if continuation else {})})
add(7,18,'Matteo','Don\'t leave.',242)
add(7,38,'Alessia','Matteo, I heard you raced like a maniac for three sleepless nights.',254,delivery='telephone_offscreen')
add(7,39,'Alessia','Just to cool my anger?',255,delivery='telephone_offscreen')
add(7,40,'Alessia',"Since you're trying this hard,",256,delivery='telephone_offscreen')
add(7,41,'Alessia','I guess I can forgive you.',256,'EP07-S40','telephone_offscreen')
add(7,42,'Alessia',"Tonight, whatever you want, I'm game.",257,delivery='telephone_offscreen')
add(7,48,'Matteo','Why was it you last night?',261)
add(8,6,'Eliza','It was me.',263)
add(8,7,'Eliza','Who did you think it was?',263,'EP08-S06')
add(8,9,'Matteo',"You really can't stay away from me",265)
add(8,10,'Matteo','now, can you?',265,'EP08-S09')
add(8,11,'Matteo','You were very obedient last night.',267)
add(8,12,'Matteo','This should be enough.',267,'EP08-S11')
add(8,13,'Matteo','Stay in your place as my pillow.',276)
add(8,14,'Matteo','Stop imagining any other role beside me.',276,'EP08-S13','offscreen_after_exit')
add(8,32,'Serafina','Alessia says she can help Matteo sleep too.',280)
add(8,33,'Serafina',"Maybe we won't need you in his room",281,delivery='offscreen_on_Eliza_reaction')
add(8,34,'Serafina','all night anymore.',281,'EP08-S33')
add(8,35,'Serafina','Sign it.',284,delivery='offscreen_on_contract')
add(8,47,'Eliza','Thank you for the Bellandi',294)
add(8,48,'Eliza','family’s support over the years.',294,'EP08-S47')
add(8,49,'Eliza',"But I won't renew.",295)
add(8,50,'Eliza','My job ends here.',298)
add(9,8,'Serafina','Have you thought this through?',304)
add(9,9,'Eliza','Yes.',305)
add(9,11,'Serafina',"Don't threaten me with quitting.",306)
add(9,12,'Serafina','Matteo can do without you.',306,'EP09-S11')
add(9,13,'Eliza','I know.',307)
add(9,22,'Serafina','Can you do that?',311,delivery='offscreen_on_Eliza_reaction')
add(9,24,'Eliza','I can.',314)
add(9,24,'Eliza',"I won't cling to him,",315)
add(9,25,'Eliza',"and I won't use this job",315,'EP09-S24')
add(9,26,'Eliza','to get anything for myself.',315,'EP09-S25')

def neutral(s):
 s=s.replace('Mrs. DeLuca','Serafina').replace('Mrs DeLuca','Serafina').replace('Deluca','Bellandi').replace('DeLuca','Bellandi').replace('Elena','Eliza').replace('Dante','Matteo')
 # Explicit source appearance/costume tags, never bedding or active actions.
 s=re.sub(r'\b(Eliza|Matteo|Serafina) \((?:slender|tall|black suit|ivory knit)[^)]*\)',r'\1 (appearance strictly from the designated character asset)',s)
 pairs=[('black-silk gold-trimmed cuff','garment sleeve'),('black gold-trimmed silk sleeve', 'garment sleeve'),('black gold-trimmed cuff','garment sleeve'),('gold-trimmed sleeve','garment sleeve'),('gold-trimmed cuff','garment sleeve'),('black silk robe with gold-trimmed lapels','garment'),('black robe','garment'),('black-robed','clothed'),('black-suited','clothed'),('silk robe','garment'),('white small-floral cuff','garment sleeve'),('in her pajamas','in her designated clothing'),('in their pajamas','in their designated clothing'),('pajama-pant legs','lower legs'),('his suit moving with him','his clothing moving with him'),('in a dark blazer, white shirt, striped necktie, plaid skirt and knee-high socks,','in her designated clothing,'),('in a dark blazer, white shirt, striped necktie, plaid skirt, and knee-high socks,','in her designated clothing,'),('fabric of her skirt','fabric of her clothing'),('her skirt','her clothing'),('the silk sheen','the garment folds'),('the silk','the garment fabric'),('silk/fabric','fabric'),('silk rustle','fabric rustle'),('soft silk','soft fabric'),('the gold trim','the garment folds'),('gold trim','garment folds'),('his dragon tattoo visible along neck and chest','his clothing fastened and chest covered'),('neck rose tattoo visible','appearance matching his asset'),('his neck dragon tattoo is visible','his appearance follows his asset'),('with a rose tattoo (Matteo\'s)','belonging to Matteo'),('the tattooed hand','the same hand'),('his tattooed hand','his same hand'),('his rose hand-tattoo and gold watch visible','their identity matching his designated asset'),('tattoo edges catching soft light','character and clothing contours catching soft light')]
 for a,b in pairs:s=s.replace(a,b)
 s=re.sub(r'(?i)\b(?:black|white|cream|ivory|wine-red|gold-trimmed|small-floral|pink-lace|silk|knit|collared|pleated)(?:[- ](?:black|white|cream|ivory|wine-red|gold-trimmed|small-floral|pink-lace|silk|knit|collared|pleated))* (robe|pajamas|suit|shirt|cardigan|blouse-dress|skirt|cuff|sleeve)\b',r'garment \1',s)
 s=s.replace('dragon tattoo','asset appearance').replace('rose tattoo','asset appearance').replace('bare chest','covered chest')
 # Chinese table costume terms to neutral action-bearing nouns.
 for a,b in [('白小碎花粉边睡衣','衣物'),('白碎花袖口','衣物袖部'),('白小碎花袖口','衣物袖部'),('白碎花睡衣','衣物'),('黑色睡袍金边衣袖','衣物袖部'),('黑睡袍金边袖口','衣物袖部'),('黑色睡袍衣袖','衣物袖部'),('黑色睡袍','衣物'),('黑睡袍','衣物'),('黑袖口','衣物袖部'),('黑金边丝绸睡袍','衣物'),('米白针织开衫+连衣裙','衣物'),('米白套装','衣物'),('黑西装酒红衬衫','衣物'),('黑西装+酒红衬衫','衣物'),('黑色西装','衣物'),('黑套装盘发','资产造型'),('黑套装','衣物'),('露颈胸龙形纹身','衣物保持扣合、胸口遮盖'),('颈玫瑰纹身','既定资产形象'),('颈龙纹身','既定资产形象'),('手背纹身、金表','既定资产形象'),('有玫瑰纹身的男人的手','男主的手'),('纹身手','男主的手'),('裙边','衣物边缘'),('睡裤的腿/脚','下腿/脚'),('女主穿睡衣','女主按资产衣着'),('男主黑睡袍','男主衣物')]:s=s.replace(a,b)
 s=s.replace('white plush bunny','designated old teddy bear').replace('white bunny','designated old teddy bear').replace('plush bunny','designated old teddy bear').replace('white fluffy toy','designated old teddy bear').replace('白毛绒兔','既定旧熊玩偶').replace('白色小毛绒玩具','既定旧熊玩偶')
 return s

def fields(ep):
 s=(SRC/f'EP{ep:02d}_复刻提示词.md').read_text(encoding='utf-8'); rows={}
 for ln,line in enumerate(s.splitlines(),1):
  if re.match(r'^\|\d+\|',line):
   v=line.strip('|').split('|');rows[int(v[0])]={'source_table_line':ln,'shot':int(v[0]),'time':v[1],'duration':float(v[2]),'size':v[3],'camera':v[4],'movement':v[5],'blocking':v[6],'action':v[7],'source_audio_summary':v[8]}
 out=[]
 for m in re.finditer(r'^### S(\d+)\s*｜\s*(.+?)\s*｜\s*(.+?)\n\*\*复刻要点\*\*：(.*?)\n```\n(.*?)\n```',s,re.M|re.S):
  n=int(m[1]);r=rows[n];a,b=map(float,r['time'].split('-'));pr=m[5];line=s[:m.start()].count('\n')+1
  r.update({'ep':ep,'source_id':f'EP{ep:02d}-S{n:02d}','title':m[3],'start_seconds':a,'end_seconds':b,'source_prompt':pr,'source_prompt_heading_line':line,'source_summary':m[4],'source_card':str(SRC/f'shots/ep{ep:02d}/S{n:02d}.jpg'),'source_markdown':str(SRC/f'EP{ep:02d}_复刻提示词.md')})
  out.append(r)
 return out

def scene(ep,n):
 if ep==7:return 'TRANSITION' if n==11 else 'L3' if n in [12,13] else 'L3→L1' if n==14 else 'L1' if n<=26 else 'L1→L2' if n==27 else 'L2'
 if ep==8:
  if n<=14:return 'L2'
  if n<=16:return 'L2→L7' if n==15 else 'L7'
  if n==17:return 'L7→L4'
  if n<=22:return 'L4'
  if n<=25:return 'L5'
  if n==26:return 'L5→L6'
  if n<=28:return 'L6'
  if n==29:return 'L6→L4'
  if n<=42:return 'L4'
  if n==43:return 'L4→庄园大门回忆'
  if n<=46:return 'L1回忆'
  if n==47:return 'L1回忆→L4'
  return 'L4'
 return 'L4' if n!=16 else 'L4→庄园走廊'

def assets(ep,n,sc,pr):
 names=[]
 if 'Eliza' in pr or '女主' in pr:
  names.append('大码女主_Eliza_18岁' if ep==8 and 23<=n<=28 else '大码女主_Eliza_睡衣' if ep==7 or ep==8 and (n<=16 or 44<=n<=46) else '大码女主_Eliza_日常')
 if 'Matteo' in pr or '男主' in pr:names.append('Matteo_成年_睡衣' if ep==7 or ep==8 and (n<=14 or 44<=n<=46) else 'Matteo_成年_日常')
 if 'Serafina' in pr or '夫人' in pr:names.append('Serafina_母亲_共用')
 if 'L1' in sc or 'L2' in sc:names.append('Eliza旧卧室')
 if 'L3' in sc:names.append('Matteo卧室')
 if 'L4' in sc:names.append('庄园客厅')
 if 'L7' in sc:names.append('客厅与入口')
 return list(dict.fromkeys(names))

def adapt(r):
 ep,n=r['ep'],r['shot'];pr=neutral(r['source_prompt']);ds=D.get((ep,n),[]);srcau=next((l for l in pr.splitlines() if l.startswith('AUDIO:')),'')
 # Preserve natural source SFX before voice clause; every intelligible line comes solely from DOCX map.
 sfx=re.split(r'Female VO|(?:Matteo|Eliza|Serafina)(?:\s*\([^)]*\))?\s*[:,]|phone voice|a seductive female voice|A familiar, seductive female voice',srcau[6:],maxsplit=1,flags=re.I)[0]
 sfx=re.sub(r'No music\.|No subtitles\.', '',sfx).strip(' .;')
 if not ds:sfx=re.sub(r'(?i)(?:his low teasing murmur|low teasing voice, male, brow lifted|faint female chatter|faint phone chatter|Matteo responding warmly to the phone|soft male sigh)', 'quiet breath',sfx)
 sfx=re.sub(r'"[^"]*"','',sfx)
 if not sfx:sfx='Natural room ambience and the source-described breath, bedding, footstep or prop-contact sounds only'
 audio='AUDIO: '+sfx+'. '
 for d in ds:
  qual='telephone voice only; no visible character mouths this line' if d['delivery']=='telephone_offscreen' else 'off-screen dialogue' if d['delivery'].startswith('offscreen') else 'natural in-scene dialogue'
  audio+=f'{d["speaker"]} ({qual}): "{d["text"]}". '
  if d.get('continuation_of'):audio+=f'Continue the same utterance from {d["continuation_of"]}; do not restart or repeat earlier words. '
 audio+='No narration, no voice-over. No other intelligible speech, no music, no subtitles. '
 if not ds:audio+='No speech mouth movements; keep the original gaze, breathing, hand actions and reactions.'
 elif all(d['delivery']=='telephone_offscreen' for d in ds):audio+='Matteo only listens, smiles or reacts as described, and Eliza remains silent; do not give either visible actor the caller\'s words.'
 else:audio+='Only the listed speaker naturally articulates the listed words; all other visible actors stay silent.'
 pr='\n'.join(audio if l.startswith('AUDIO:') else l for l in pr.splitlines())
 if ep==7 and n==22:pr=pr.replace('he leans in close to murmur','he leans in close, silently')
 if ep==7 and n==23:pr=pr.replace('about to deliver a mocking line','a teasing impulse')
 if ep==7 and n==40:pr=pr.replace('the caller pleads','the caller speaks').replace('he speaks calmly, one shoulder relaxed','he listens calmly, one shoulder relaxed').replace('Matteo speaking calmly on the phone','Matteo listening calmly on the phone')
 if ep==7 and n==41:pr=pr.replace('he decides to forgive the caller','the caller offers forgiveness').replace('speaking cajolingly into the phone','listening to the phone')
 if ep==7 and n==42:pr=pr.replace('his sweet words to the other woman sting','the woman\'s intimate words through the phone sting')
 if ep==7 and n==15:pr=pr.replace('directly into the camera','toward the space just above Matteo, off-lens').replace('straight into lens','toward the space just above Matteo, off-lens').replace('looking straight at camera','looking toward the space just above Matteo, off-lens')
 # Restoring the table's first fragment is mandatory: source code usually describes only its post-cut shot.
 hard=('→' in r['size'] or '→' in r['action']) and ('硬切' in r['size'] or '切镜' in r['movement'] or '切' in r['action'])
 table=neutral(f"景别/变化：{r['size']}；机位/构图：{r['camera']}；运镜：{r['movement']}；站位/走位：{r['blocking']}；完整行动和反应：{r['action']}。")
 if ep==7 and n in [40,41]:table=table.replace('讲电话','听电话并保持源笑意').replace('说话','听对方说话')
 if hard:pr=pr.replace('FIRST FRAME:','POST-CUT FIRST FRAME (source code\'s latter view):',1)
 head=f'EP{ep:02d}-S{n:02d} | {r["time"]}s | duration {r["duration"]:g}s. Preserve the full source interval, not only the latter view.\n完整源时间轴（按原表前段→后段执行；相邻段起点是上一动作的接续，不重复从头演）：{table}\n'
 if hard:head+='INTERNAL CUT: perform the table\'s opening view first, then HARD CUT to its latter view. No morphing, teleporting or dissolving between bodies, cameras or rooms. Keep both fragments inside this source interval; do not discard the first fragment.\n'
 head+='IDENTITY / APPEARANCE: Eliza, Matteo and Serafina use only their designated assets; Eliza remains an adult plus-size woman (28 in the present; the separate 18-year asset only for EP08 S23–28). Preserve the asset\'s body size and identity, with no source-character costume, makeup or tattoos imposed. Matteo\'s clothing remains fastened and his chest covered. Reference cards provide composition/state only; do not render cards, multiple views, labels or source subtitles.\n'
 out={**r,'scene_code':scene(ep,n),'dialogue':ds,'narration_removed':True,'source_audio':srcau,'source_has_internal_hard_cut':hard,'adapted_prompt':head+pr,'changes':['原129源编号与表时长保留；表内前段→后段补齐，EN原结构保留','删除源VO/旁白；人物说话仅用本项目女版DOCX映射','身份改Eliza/Matteo/Serafina；服装与体型服从资产，受力动作中性化','位置与资产锁另依本任务资产报告合入'],'position_lock':None}
 out['asset_names']=assets(ep,n,out['scene_code'],out['adapted_prompt']);return out

def write():
 allrows=[]
 for ep in [7,8,9]:
  rows=[adapt(r) for r in fields(ep)];assert len(rows)=={7:49,8:54,9:26}[ep];allrows.extend(rows)
  d={'status':'DERIVED_CONTENT_READY_PENDING_POSITION_LOCKS','ep':ep,'source_shot_count':len(rows),'source_end_seconds':rows[-1]['end_seconds'],'shots':rows,'scope':'本地派生，不改源、不操作平台'}
  (OUT/f'EP{ep:02d}_平台稿.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
  if ep==7:(OUT/'EP07_S01-10_首批平台稿.json').write_text(json.dumps({**d,'source_shot_count':10,'shots':rows[:10],'source_end_seconds':20.52,'batch_frozen_until_notice':True},ensure_ascii=False,indent=2),encoding='utf-8')
 (OUT/'平台稿_129镜.json').write_text(json.dumps({'status':'DERIVED_CONTENT_READY_PENDING_POSITION_LOCKS','source_shot_count':129,'narration_policy':'删除全部旁白；只保留本项目女版原文对白与源现场声','authority_docx':str(ROOT/'完整剧本/我不再做教父的大码人形抱枕EN.docx'),'shots':allrows},ensure_ascii=False,indent=2),encoding='utf-8')
 print('written',len(allrows))
if __name__=='__main__':write()
