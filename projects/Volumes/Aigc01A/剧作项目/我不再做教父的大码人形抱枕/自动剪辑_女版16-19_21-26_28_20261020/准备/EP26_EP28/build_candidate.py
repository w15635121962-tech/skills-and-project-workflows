from pathlib import Path
import json,datetime,zipfile,xml.etree.ElementTree as ET
root=Path.cwd();out=Path(__file__).resolve().parent
probes=json.loads((out/'素材probe.json').read_text());probe={Path(r['file']).stem:r for r in probes}
obs={
'女版26-1-1':('研究所外景、女主持文件穿过楼内、办公桌翻阅文件、导师将纸放在桌上并说话。', 'G1完整主版本，唯一含导师原句；V2只是走入研究所补镜。'),
'女版26-1-2':('女主持文件走入研究所大厅，再转实验室/走廊。','仅开场补镜，不代替G1全部及导师对白。'),
'女版26-2-1':('笔尖签字、女主坐办公桌前放松、傍晚公寓中逗猫与同Evan吃饭。','对应签名、无附加条件、逗猫、共同晚餐；ASR反复杂语不列对白。'),
'女版26-3-1':('女主近脸、双手握杯、Evan近脸、女主说话、Evan回应。','两句齐全，但开场均紧景，空间建立不如V2。'),
'女版26-3-2':('起段同沙发双人中景，女主持杯、Evan与猫；接女主手杯、双方侧近景，先女主说话，后Evan微笑回应。','此组视觉首选；两句原文齐全。'),
'女版26-3-3':('从女主肩后拍Evan近脸，Evan由看她到微笑，再中景与猫。','只有Evan答句；不能用最高尾号整体代替V1/V2。'),
'女版26-4-1':('走廊有人搬箱入户，空栏杆/街景，女主独自在床上安睡、短暂睁眼再睡。','新邻居与安睡；没有旧男主在墙外倾听。'),
'女版26-5-1':('女主拿未拆信封、脸部犹豫收定、将信放桌面后离开，尾端进入花店。','未拆信清楚；接触表未见完整邮寄退回操作，不可声称画面完整演出退信。'),
'女版26-6-1':('女主在花店镜前看自己，插一次灰色大码旧日形象，回到现在梳理头发并微笑、拿花离开。','当下/旧我对照可承载一年后与自我价值；灰色大码形象仅作回忆插入。'),
'女版28-1-1':('床上男子痛苦侧卧、近脸与抓衣，门口男子出现，夜窗床上独坐、床头玩偶与拿手机。','较多痛苦与门口动作，不完整呈现逐步独睡成功；可作前期痛苦备选，不与所有替代条全拼。'),
'女版28-1-2':('男主仰卧眼睛睁开，随后同床较宽景闭眼，手部放在身前。','短睡眠补镜，可承载逐渐入睡；不独立代替整个开场。'),
'女版28-1-3':('男主在门口示意另一男子离开并合门，床头把玻璃杯/药瓶收进抽屉。','对应不再让员工门外守候、不依靠酒药；收进抽屉不是扔掉，不改写原剧情。'),
'女版28-1A-1':('男主床沿闭眼平复，侧卧抓紧衣料、近脸睁眼、胸前手、整夜独睡宽景、把杯/药物收进抽屉。','可作开场睡眠由痛苦到平稳主段；未见治疗师、病历或数字10min/1h，不凭这些素材声称已视觉展示治疗记录。'),
'女版28-2-1':('夜床边独坐、空床单手部、侧躺脸、再坐起，空枕上一册旧书。','作为熄灯后摸空床/无人读书主段；手触床面与空书清楚。'),
'女版28-2-2':('门口男主向持档案男子示意、手机近景、夜床独坐、躺下摸身旁空枕、空枕旧书。','与V1覆盖重叠，有门口/手机补充但卧室后景变为木墙；不全部重复。'),
'女版28-2-3':('夜色男主床边侧脸、玩偶与未拆封信在后、空枕旧书。','短反应补镜，不含V1摸空床的完整动作。'),
'女版28-3-1':('男主床沿前倾垂头、双掌抬起看手、侧脸抬眼、坐直闭眼。','对应承认依赖与权力的顿悟；单条动作由低到高完整，作主段。'),
'女版28-3-2':('男主床边垂头，双掌展开停留，侧脸朝窗，坐直。','与V1语义重复；当替代选项，不连续重复同次开掌。'),
'女版28-4-1':('女主抱自购鲜花出公寓，花束与面部近景，Evan挥手，群友招手，女主笑着跑。','完整开门—看朋友—笑—跑，可作主段；跑步后对手位置须在实际运动再确认。'),
'女版28-4-2':('Evan侧身挥手、朋友群像、女主侧脸由静到笑、抱花跑。','缺开门起点，只作替换/补镜；不能整条替换主段而丢出公寓。'),
'女版28-4-3':('女主出门与看花，Evan正脸挥手、朋友微笑、女主笑、抱花侧面跑。','完整主段备选，和V1重复同一事件，不两次出门/挥手/跑。'),
'女版28-4-4':('女主花束与后脑在前景，远处Evan挥手；随后女主背后望向朋友群像。','视线空间建立最明确的补镜，可覆盖主段挥手，但不要连续重复两次挥手。'),
'女版28-5-1':('女主抱花街头跑与笑，交切男主夜床玩偶、独躺、愿望券ONE WISH、眼神。','双线结尾蒙太奇完整；愿望券会与G6重复，可后续按旁白对位去重。'),
'女版28-5-2':('女主抱花跑、男主夜床伸手灯旁与独睡、女主融入朋友、仰脸阳光、男主闭眼。','较短双线版本，无愿望券特写，接G6更少重复；可作G5主版本。'),
'女版28-6-1':('床头玩偶与愿望券，手按ONE WISH，男主仰卧近脸，切女主与朋友迎光并肩走。','结尾愿望券—男主—自我生活因果清楚，主段。'),
'女版28-6-2':('女主与朋友群体背向镜头朝日光走远。','终态补镜，接G6V1迎面走后作背向远去，不重演前段。')}
selected={26:[('女版26-1-1','回纽约留任、独立生活、导师递正式雇用合同'),('女版26-2-1','签名、无附加条件、与Evan逗猫和晚餐'),('女版26-3-2','慢慢开始：女主提出慢一点，Evan接受'),('女版26-4-1','隔壁换新邻居，女主安稳独睡'),('女版26-5-1','Serafina未拆的道歉信与退回决定；时间跳至花店'),('女版26-6-1','一年后镜中自我、旧大码回忆、自我价值')],28:[('女版28-1A-1','创伤治疗后的独睡进展与停止借酒药逃避'),('女版28-1-3','不再要员工守门，并收起酒药；前段动作顺序需在最终旁白对位时微调'),('女版28-2-1','夜里摸空床，无人轻读，独坐旧物旁'),('女版28-3-1','承认把依赖当权力、把爱当无尽合同'),('女版28-4-1','纽约晨光抱花出门、Evan及朋友挥手、笑着跑去'),('女版28-5-2','十年人形抱枕与真正醒来，冷暖双线对照'),('女版28-6-1','过期的愿望券与十年之爱，转向女主新生活'),('女版28-6-2','与朋友背向镜头走远的稳定结局')]}
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
def paras(fn):
 rt=ET.fromstring(zipfile.ZipFile(fn).read('word/document.xml'))
 return [''.join(t.text or '' for t in p.findall('.//w:t',ns)) for p in rt.findall('.//w:p',ns)]
en=paras('完整剧本/我不再做教父的大码人形抱枕EN.docx');zh=paras('完整剧本/我不再做教父的大码人形抱枕.docx')
eps=[]
for ep in (26,28):
 snippets=en[739:766] if ep==26 else en[768:792]
 (out/f'女版EP{ep}_权威英文原稿.txt').write_text('\n'.join(snippets)+'\n')
 (out/f'女版EP{ep}_权威中文原稿.txt').write_text('\n'.join(zh[605:625] if ep==26 else zh[626:642])+'\n')
 clips=[];cursor=0
 for number,(stem,purpose) in enumerate(selected[ep],1):
  r=probe[stem];fps=r['video']['fps'];frames=r['video']['nb_frames'];dur=frames/fps
  asr=json.loads((out/'ASR'/f'{stem}.json').read_text())
  ds=[]
  if stem in ['女版26-1-1','女版26-3-2']:
   for s in asr['segments']:
    ds.append({'speaker':'professor' if stem.endswith('1-1') else ('Eliza' if s['text'].strip().startswith('I need') else 'Evan'),'original_english':s['text'].strip(),'asr_speech_start_seconds':s['start'],'asr_speech_end_seconds':s['end'],'recommended_audio_protection_in_seconds':max(0,s['start']-.15),'recommended_audio_protection_out_seconds':min(dur,s['end']+.2),'timing_evidence':'blind ASR; margin is planning allowance, not waveform/listening-certified boundary','do_not_cut_words':True})
  clips.append({'order':number,'source_path':r['file'],'source_in_seconds':0,'source_out_seconds_exclusive':dur,'source_in_frame':0,'source_out_frame_exclusive':frames,'source_fps':fps,'picture_track':1,'source_audio_track':1,'timeline_in_seconds_provisional':cursor,'timeline_out_seconds_provisional':cursor+dur,'narrative_role':purpose,'picture_observation':obs[stem][0],'sync_audio':{'mode':'same source, same offsets and duration as picture; linked audio retained','gain_dB':0,'separate_narration_track':2,'recognized_original_dialogue':ds,'other_asr_text_not_accepted_as_dialogue':not bool(ds),'human_listening_verified':False,'fine_lip_sync_verified':False,'note':'Preserve original embedded sound. Do not subtitle low-confidence/repetitious ASR. VO is missing; do not claim original ambience is full narration or mute it to conceal the gap.'},'sheet':str((out/f'{stem}_sheet.png').resolve()),'asr_json':str((out/'ASR'/f'{stem}.json').resolve()),'verification':'6 evenly spaced frames per source were visually inspected; no full-motion watch or human listening performed','status':'provisional editable assembly candidate, full source range, pending VO-driven final timing'})
  cursor+=dur
 eps.append({'episode_local_chinese':ep,'english_docx_episode':25 if ep==26 else 26,'mapping_basis':'Compared complete Chinese story content and complete English chapter text, not chapter numbers alone. Chinese source skips 11 and 27.','provisional_picture_duration_seconds':cursor,'narration_status':'No corresponding old or new local narration discovered by parent inventory; this plan does not generate VO.','script_english_file':str((out/f'女版EP{ep}_权威英文原稿.txt').resolve()),'script_chinese_file':str((out/f'女版EP{ep}_权威中文原稿.txt').resolve()),'clips':clips,'missing_audio':[{'kind':'female Eliza English narration','original_text':x} for x in snippets if x.strip() and not x.startswith('【') and not x.startswith('"') and not (ep==26 and x.startswith('I told him,'))],'notes':['EP26 has three scripted character dialogue sentences; EP28 has no scripted character dialogue.','Full source ranges are conservative assembly defaults to avoid truncating speech; this is not a final rhythm cut.','Keep any new VO on its own named audio track and preserve existing synchronized source audio.','No obligation to include every numbered version; alternatives below are references only.']})
reviews=[]
for stem,r in probe.items():
 asr=json.loads((out/'ASR'/f'{stem}.json').read_text());ob,reco=obs[stem]
 reviews.append({'source_path':r['file'],'duration_seconds':r['video']['nb_frames']/r['video']['fps'],'source_fps':r['video']['fps'],'source_size':[r['video']['width'],r['video']['height']],'has_audio_stream':bool(r.get('audio')),'pixels_inspected':True,'inspection_method':'six-frame contact sheet','observation':ob,'recommendation':reco,'asr_text':asr['text'],'asr_is_blind':True,'asr_not_forced_to_script':True,'human_listening_verified':False,'asr_json':str((out/'ASR'/f'{stem}.json').resolve()),'contact_sheet':str((out/f'{stem}_sheet.png').resolve())})
plan={'created_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'scope':'女版 EP26 and EP28 local source preparation only; no browser or Resolve mutations; no original media edits.','status':'picture and synchronized source-audio assembly ready; narration missing; not final playback acceptance','source_of_truth':{'chinese':str((root/'完整剧本/我不再做教父的大码人形抱枕.docx')),'english':str((root/'完整剧本/我不再做教父的大码人形抱枕EN.docx')),'warning':'视觉设计/画面设计和分镜/26.md is finale design corresponding to local EP28, not local EP26.'},'episodes':eps,'all_source_reviews':reviews,'uncertain_parts':['EP26 and EP28 Eliza narration not available locally; no complete final soundtrack can be certified.','ASR proves recognized text candidates and approximate timing only; no actual audio listening has been performed.','Source-original ambient/music content should be retained with source picture, but level/overlap/accidental vocalization needs final listening.','EP28 G1A and G1V3 both end by putting glass/medication away; avoid repeating the same action when fitting missing VO (can trim one after direct motion review).','EP28 G4 V1/V3 running destination must be reviewed in motion; use V4 OTS to clarify recipient positions if needed, replacing rather than repeating waving.','EP26 G5 sheet shows an unopened letter being set down; return mailing action is not independently visible.','Several EP28 bedroom takes change wall/headboard rendition; identify time passage by transition rather than claim strict continuous action.','No Resolve persistence, assembled playback, color, fine lip-sync, final audio loudness, subtitles or final delivery tested by this task.']}
(out/'剪辑候选_EP26_EP28.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
print(out/'剪辑候选_EP26_EP28.json');print([(e['episode_local_chinese'],e['provisional_picture_duration_seconds'],len(e['clips'])) for e in eps])
