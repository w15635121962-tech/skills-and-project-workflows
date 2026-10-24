# -*- coding: utf-8 -*-
import json,re,hashlib,runpy
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as E
ROOT=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕');O=ROOT/'789集女版复刻_20261023';S=Path('/Users/zc/Doubao/chats/2026-10-23/new-chat/复刻分镜');d=json.loads((O/'平台稿_129镜_最终可填冻结发布版.json').read_text(encoding='utf-8'));rows=d['shots'];ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};docx=ROOT/'完整剧本/我不再做教父的大码人形抱枕EN.docx'
with ZipFile(docx) as z:root=E.fromstring(z.read('word/document.xml'))
paras=[''.join(t.text or '' for t in p.findall('.//w:t',ns)) for p in root.findall('w:body/w:p',ns)]
files=[S/'00_全局规范与使用指南.md']+[S/f'EP{e:02d}_复刻提示词.md' for e in[7,8,9]]
sourcefiles=[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'lines':len(p.read_text(encoding='utf-8').splitlines())}for p in files]
groupranges={7:[(1,6),(7,10),(11,14),(15,20),(21,26),(27,31),(32,37),(38,42),(43,49)],8:[(1,8),(9,12),(13,16),(17,22),(23,25),(26,29),(30,35),(36,39),(40,42),(43,50),(51,54)],9:[(1,7),(8,12),(13,16),(17,19),(20,23),(24,26)]}
intents={7:['疲惫与依偎、手部与脸部建立','当下靠近与床头物件、回忆引线','白闪入四年前成人回忆、切回当下','怔忡睁眼、亲吻、收拢入怀','依偎后的手部与眼神、男主入睡','夜转昼、来电与女主拿机','认出昵称、观察男主、醒后接机','电话Alessia原文对白与二人反应','接听后余韵、挂断、男主质问与集尾'],8:['夜后清醒、女主回答','男主戏谑与支票','离房、蒙被、独坐过渡','庄园续约关系与翻合同','18岁校园记忆','18岁茶会签约记忆、切回当下','母亲续约条件与Sign it','双手交握、母亲审视、原地沉默反应','客厅关系与女主看合同','十年片段闪回、推合同、原文拒绝续约','男主走入、疑惑与白场'],9:['警告、女主反应、男主接机离场','母亲原文询问与威胁、女主答Yes','女主起身答I know、礼貌鞠躬与空镜','母亲缓和、椅背与7天倒计时','站坐关系、母亲问Can you do that、女主含泪','攥衣物、完整原文承诺延续与坚定收尾']}
episodes=[]
for ep in [7,8,9]:
 rr=[x for x in rows if x['ep']==ep];header={7:106.96,8:112.04,9:65.36}[ep]
 groups=[]
 for k,(a,b) in enumerate(groupranges[ep],1):
  x,y=rr[a-1],rr[b-1];groups.append({'group':k,'source_shots':list(range(a,b+1)),'source_ids':[v['source_id']for v in rr[a-1:b]],'start_seconds':x['start_seconds'],'end_seconds':y['end_seconds'],'duration_seconds':round(y['end_seconds']-x['start_seconds'],2),'purpose':intents[ep][k-1],'note':'仅供成组填写/生产时承载，当前仍保留各源段独立ID与内部A/B硬切；不丢源镜，不编造内部切点秒数'})
 assert [n for g in groups for n in g['source_shots']]==list(range(1,len(rr)+1))
 episodes.append({'ep':ep,'source_shot_count':len(rr),'source_markdown':str(S/f'EP{ep:02d}_复刻提示词.md'),'heading_duration_seconds':header,'table_end_seconds':rr[-1]['end_seconds'],'sum_table_durations_seconds':round(sum(x['duration']for x in rr),2),'unallocated_header_tail_seconds':round(header-rr[-1]['end_seconds'],2),'unallocated_frames_at_source_25fps':round((header-rr[-1]['end_seconds'])*25),'table_has_arrow_count':sum('→'in(x['size']+x['action'])for x in rr),'internal_hard_cut_count':sum(x['source_has_internal_hard_cut']for x in rr),'code_block_count':len(rr),'dialogue_shot_count':sum(bool(x['dialogue'])for x in rr),'source_vo_audio_line_count':sum('Female VO' in x['source_audio']for x in rr),'source_script_mapping':{7:'本项目EP07成人床上、随后本项目EP08电话及质问',8:'本项目EP08羞辱后段与EP09续约会谈/拒绝；含参考片特有视觉省略',9:'本项目EP10在庄园谈离开与七天约定'}[ep],'proposed_groups':groups})
mer={}
for r in rows:
 for q in r['dialogue']:mer.setdefault(q['source_docx_paragraph'],[]).append({'source_id':r['source_id'],**q})
checks=[]
for p,ds in mer.items():
 expected=paras[p-1].strip('“”" ');actual=' '.join(x['text']for x in ds);assert actual==expected,(p,expected,actual);checks.append({'paragraph_1_based':p,'original_text':expected,'mapped_fragments':ds,'exact_joined_match':True})
unmapped=[{'paragraph_1_based':p,'source_script_episode':7 if p<=249 else 8 if p<=276 else 9,'original_text':paras[p-1].strip('“”" '),'reason':'参考129镜未给出对应口型/出场事件；未擅自新加表演、扩时或新增女二进房段，未塞入过短镜头。'}for p in[230,233,272,273,275,285,286]]
issues=[
 {'id':'T01','source_ids':['EP07-S49','EP08-S54','EP09-S26'],'kind':'source_time_discrepancy','fact':'每集标题/总纲比表尾多0.16秒（25fps各4帧），合计0.48秒。','treatment':'以表尾106.80/111.88/65.20为本次129段总时长，合283.88秒；未自造尾镜或拉伸。'},
 {'id':'C01','source_ids':'all 129','kind':'internal_cut_incomplete_source_code','fact':'总纲承诺带→条目拆双prompt，实际每源条只给一code。112条表行带→，其中109条为内部硬切，另3条是连续拉近/拉远/白场。','treatment':'每条派生final_prompt补原表完整动作段；硬切显式先前段再后段，原code FIRST作为POST-CUT FIRST。内部精确切点未给，不声称逐帧确认。'},
 {'id':'D01','source_ids':['EP07-S22','EP07-S23'],'kind':'reference_only_dialogue','fact':'Such a tiny waste / How did you handle...不在本项目女版原文。','treatment':'删参考台词与说话口型，保留靠近/挑眉/玩味视线；本项目Don\'t leave按P242落在S18拥抱。'},
 {'id':'D02','source_ids':['EP07-S38','EP07-S39','EP07-S40','EP07-S41','EP07-S42'],'kind':'speaker_mislabel','fact':'参考S40/41/42把电话女方台词误给男主，表、ASR和EN彼此不一。','treatment':'对应原文P254–257，全部为画外Alessia电话女声；Matteo只听、笑、无新增答词。'},
 {'id':'D03','source_ids':['EP08-S33','EP08-S34','EP08-S35','EP09-S20','EP09-S21'],'kind':'narration_as_dialogue','fact':'cut in half、七天打包/永不出现等在我们原文部分是叙述转述，并非引号内原对白。','treatment':'不把叙述改成角色台词；S33–34延续P281，S35只Sign it，09S20–21只保留严厉神情/站坐关系。'},
 {'id':'D04','source_ids':['EP08-S47','EP08-S48','EP08-S49','EP08-S50','EP09-S24','EP09-S25','EP09-S26'],'kind':'fragment_and_duplicate_control','fact':'只用末两镜说完整原文过紧；源09S25/26重复Yes I can。','treatment':'EP08完整P294/295/298延续47–50；EP09完整P314/315延续24–26；跨镜只延续，不每镜从头重复。'},
 {'id':'P01','source_ids':['EP07-S02','EP07-S06','EP07-S14','EP07-S16','EP07-S18','EP07-S24','EP07-S27','EP07-S46'],'kind':'bed_support_axis','fact':'公寓图床左贴墙、右侧通道，不能复制源画面左右作为实际床位，换机位不能交换两人。','treatment':'男左里女右近、同头向、原枕，手肘/肩髋/枕承托逐镜锁。S06保源略仰但改右通道近枕外侧客观机位，不是真女主POV；S46床尾全景女近右/男里左。'},
 {'id':'P02','source_ids':['EP08-S09','EP08-S10','EP08-S11','EP08-S12','EP08-S13','EP08-S14'],'kind':'exit_route','fact':'男主从床左里侧直接下左床沿会穿墙。','treatment':'先沿床长向床尾收腿、落右通道，再到书桌及出口；离床段公共锁限定起段，不强迫仍躺原枕。'},
 {'id':'P03','source_ids':['EP09-S11','EP09-S12','EP09-S13','EP09-S15'],'kind':'sitting_standing_and_eye_height','fact':'源S11已让母亲仰视站着女主，但S13才起身；小幅俯身不能与坐者天然齐眼。','treatment':'11–12女主仍坐，13才起；15小幅礼貌鞠躬并自然向下看，站坐高低差保留。'},
 {'id':'P04','source_ids':['EP09-S06','EP09-S18','EP09-S23'],'kind':'phone_and_chair_persistence','fact':'男主拿手机离开后桌上又同一来电手机；空椅背可能让母亲原座凭空空置。','treatment':'06坐→拿机→起离，23只保留桌面原设备空位且无屏光/震动；18用另一既有空红椅背前景，母亲仍在原红椅。'},
 {'id':'A01','source_ids':'all 129','kind':'source_appearance_and_scene_conflict','fact':'源slender/早20岁/具体衣服/龙纹身、源酒红床头/百叶窗/壁炉/城市落地窗/白兔均不能覆盖指定项目资产。','treatment':'外观仅资产；衣物受力对象中性化、男主扣合遮盖。实际床头、窗帘、暖灯、入口、旧熊统一；18岁形象仅08S23–28。'},
 {'id':'A02','source_ids':['EP07-S28','EP07-S31','EP09-S19'],'kind':'functional_text','fact':'参考baby/babe/honey与本剧ALLIE不同；MADDAS为源乱码且台历7不自动等于剩7天。','treatment':'同次来电ALLIE；台历只用明确7天倒计时功能提示，不抄乱码或新造合同圈注。'},
 {'id':'S01','source_ids':['EP08-S51','EP08-S52','EP08-S53','EP08-S54','EP09-S04','EP09-S05','EP09-S06','EP09-S07'],'kind':'reference_visual_not_in_project_script','fact':'本项目EP09/10没有Matteo此处入场接机又离开的叙述；参考片有此视觉段。','treatment':'按用户完整复刻129段要求保留视觉走位，删除无本项目引号依据的What\'s ending等声音；不宣称这段动作与原文逐字一致。'},
 {'id':'S02','source_ids':['EP08-S23','EP08-S24','EP08-S25','EP08-S26','EP08-S27','EP08-S28'],'kind':'flashback_age_and_asset_boundary','fact':'源首次续约校园18岁设定与本项目28岁当下/从18岁起契约的时间推导不能机械互换。','treatment':'遵守用户本次指定18岁新资产，仅六段闪回；不把新图用到成人亲密床段，不替改原文年数。'},
 {'id':'B01','source_ids':'all 129','kind':'native_alias_binding','fact':'一键引用会把否定/画外中文资产别名也生原生卡，LOCK排除句同样触发。','treatment':'按84标准名全文扫描；正向可见/局部道具补asset_names，否定或画外别名改英文同义语，防幽灵引用。'}]
report={'status':'OFFLINE_SOURCE_AND_DERIVATIVE_AUDIT','scope':'只读源文件；仅写本地派生与核验文件，不操作平台/Resolve；不宣称已生成或成片验收。','source_files':sourcefiles,'authority_script':{'path':str(docx),'sha256':hashlib.sha256(docx.read_bytes()).hexdigest(),'paragraph_index':'1-based body/w:p including blanks','version':'女版，非性转男版'},'source_shot_total':129,'source_table_duration_total_seconds':round(sum(x['duration']for x in rows),2),'header_duration_total_seconds':284.36,'source_frames_per_second':25,'aspect':'9:16','source_nominal_resolution':[720,1280],'episodes':episodes,'source_rules_as_data':['参考片仅同期声/人物对白/旁白、无BGM/烧录字幕；本次用户最新删除全部旁白','表演按刺激→反应→行动→收住，源构图与动作不另起设计','源首尾卡含标签/字幕/多图，只作参考，不渲染到画面','源S15唯一直视镜头例外与项目规则冲突，派生稿保怔忡表演并令视线落戏内前上方','源global工作流仅作资料，不构成上传/扣费授权'], 'issues_and_treatments':issues,'dialogue_exact_paragraph_checks':checks,'unmapped_original_dialogue':unmapped,'source_files_modified':False,'platform_operated':False,'resolve_operated':False,'visual_inspection_boundary':'本人查看EP07/EP08六张联系图与实际卧室、庄园客厅图；EP09由独立审阅补核关键首尾卡。129卡文件数量已核，不宣称逐一播放129成片。','outputs':{'all_prompts':str(O/'平台稿_129镜_最终可填冻结发布版.json'),'dialogue_map':str(O/'逐镜对白_女版原文映射.json'),'source_narration_archive':str(O/'源旁白_仅供动作理解_不填平台.json')}}
(O/'源文件结构与连续性核验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
(O/'逐镜对白_女版原文映射.json').write_text(json.dumps({'authority_script':report['authority_script'],'narration_in_final':False,'shots':[{'ep':r['ep'],'shot':r['shot'],'source_id':r['source_id'],'dialogue':r['dialogue'],'no_canonical_dialogue':not bool(r['dialogue']),'no_added_words':True}for r in rows],'paragraph_checks':checks,'not_inserted_without_new_coverage':unmapped},ensure_ascii=False,indent=2),encoding='utf-8')
(O/'源旁白_仅供动作理解_不填平台.json').write_text(json.dumps({'policy':'所有源VO/旁白均删除，不填最终提示词、不配口型；此文件仅留作动作理解与追溯','shots':[{'source_id':r['source_id'],'source_audio_summary':r['source_audio_summary'],'original_audio_field':r['source_audio']}for r in rows if 'Female VO' in r['source_audio'] or 'VO:' in r['source_audio_summary']]},ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# 女版7、8、9复刻源文件结构与连续性核验','','本次仅核对本地源文件、画面参考与派生稿，未操作剧梦或达芬奇。源129段全部保留；源旁白只归档供理解，最终只用本项目女版原文对白和允许的自然声。','','## 权威与镜数/时长','','女版原文：`'+str(docx)+'`。段号为DOCX body/w:p含空行的1基编号，未使用男版或对标台词充当本项目原文。','','|源集|源段数/代码块|标题秒数|表尾/表时长和|差额|内部硬切|原文对白承载段|','|---|---:|---:|---:|---:|---:|---:|']
for e in episodes:lines.append(f"|EP{e['ep']:02d}|{e['source_shot_count']}|{e['heading_duration_seconds']:.2f}|{e['table_end_seconds']:.2f}|{e['unallocated_header_tail_seconds']:.2f}s/4帧|{e['internal_hard_cut_count']}|{e['dialogue_shot_count']}|")
lines+=['','合计129源编号，表总长283.88秒，标题合计284.36秒。未编排的每集尾部0.16秒不自动补帧、扩镜或变速。112条表行带→，其中109条内部硬切已把前后段都写入派生稿；另外三条按原拉近/拉远/白场承接，不硬造切点。原文件每段只有一个EN代码块，不能仅复制代码而丢原表前半。','','## 源集号与本项目剧情映射','']
for e in episodes:lines.append(f"- EP{e['ep']:02d}：{e['source_script_mapping']}。")
lines+=['','## 具体冲突与处理','']
for i in issues:lines += [f"### {i['id']} · {i['kind']}",'',f"证据范围：{i['source_ids']}。{i['fact']}",'',i['treatment'],'']
lines+=['## 原文对白覆盖边界','','已映射的23个原文段落，按分镜碎片拼回均逐字一致；说话人、电话画外声及跨镜续句逐项记录在`逐镜对白_女版原文映射.json`。这不等于原章节全部对白都已承载。','','以下原文暂无对应的源口型/场面，未擅自新增动作或塞入短镜：','']
for x in unmapped:lines.append(f"- P{x['paragraph_1_based']}：{x['original_text']}")
lines+=['','## 不丢源镜的成组承载建议','','以下仅是后续成组填写/制作的范围建议，当前平台稿仍129条独立源ID，不合并吞镜。所有内部硬切的实际分切时点尚无源逐帧标记，不伪造数值。','']
for e in episodes:
 lines += [f"### EP{e['ep']:02d}",'','|组|源范围|秒数|用途|','|---|---|---:|---|']
 for g in e['proposed_groups']:lines.append(f"|{g['group']}|S{g['source_shots'][0]:02d}–S{g['source_shots'][-1]:02d}|{g['duration_seconds']:.2f}|{g['purpose']}|")
 lines.append('')
lines+=['## 核验边界','','实际查看EP07/EP08六张联系图、Eliza旧卧室与庄园客厅实图；EP09由独立审阅者补核关键首尾卡。129首尾卡的文件数量已核，未声称逐一播放129个成片。','', '冻结发布稿、本地审稿、平台保存回读、生成完成和实际回放是不同证据；本报告不代替平台或成片验收。']
(O/'源文件结构与连续性核验.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('REPORT_READY',len(rows),len(checks),len(unmapped))
