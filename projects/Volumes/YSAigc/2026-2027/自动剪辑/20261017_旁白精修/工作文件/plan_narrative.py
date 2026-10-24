import json,re,math
from pathlib import Path
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件'
OLD=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_学校粗剪/工作文件')
footage=json.loads((OLD/'footage.json').read_text());assets={a['id']:a for a in json.loads((OUT/'asset_recommendations.json').read_text())['assets']}
narr=json.loads((OUT/'narration_aligned.json').read_text());shots=[];pos=0
assets['B01']={'id':'B01','type':'video','path':'/Volumes/YSAigc/2026-2027/自动剪辑/20261017_学校粗剪/画面补充/篮球活动_5_推近.mp4','subject':'校内篮球比赛照片的克制推近','in':0,'out':4.6}
def clip(group,num):
 matches=[r for r in footage if r['group']==group and re.search(r'[CD]0*'+str(num)+r'(?:_|\.)',r['name'])]
 assert len(matches)==1,(group,num);return matches[0]
def add(end,ref,src_in=0,note='',speed=1,title=None):
 global pos
 endfr=round(end*25);length=endfr-pos;assert length>0,(end,ref,pos)
 if isinstance(ref,str):
  a=assets[ref];is_photo=a['type']=='image';path=a['path'];fps=25;source_duration=None;log=path.startswith('/Volumes/YSAigc/2026-2027/文汇中学/拍摄素材转码')
  if is_photo:src_in=0
  elif src_in==0:src_in=a['in']
  name=a['subject']
 else:
  a=clip(*ref);is_photo=False;path=a['path'];fps=a['fps'];source_duration=a['duration'];log=True;name=a['name']
 source_in=round(src_in*fps)/fps
 source_out=source_in+length/25*speed
 if source_duration:assert source_out<source_duration-.02,(name,source_out,source_duration)
 section=next((c['name'] for c in narr['chapters'] if c['start']<=pos/25+.6<c['end']+.7),narr['chapters'][-1]['name'])
 overlap=[s['id'] for s in narr['sentences'] if s['start']<endfr/25 and s['end']>pos/25]
 shots.append({'index':len(shots)+1,'record_frame':pos,'length_frames':length,'in':source_in,'out':source_out,'speed':speed,'path':path,'name':name,'fps':fps,'is_photo':is_photo,'asset_id':ref if isinstance(ref,str) else None,'log':log,'chapter':section,'narration_sentence_ids':overlap,'narration_excerpt':' '.join(s['text'] for s in narr['sentences'] if s['id'] in overlap),'intent':note,'title':title,'source_photo':path if is_photo else None})
 pos=endfr
S=add
# Opening: establish place and people; room for the spoken title.
S(4.68,('002',1),2,'校门建立书香校园的空间，缓慢淡入')
S(9.36,('001',1),1,'青春启航：自然走进校园')
S(13.6,('004',307),20,'树影与晨光，呼应沃土和梦想')
S(20.32,('002',19),2,'明亮教学楼，片名与集团名',title='汇启新章 · 共育未来\n文汇中学教育集团')
S(23.6,('003',211),8,'学生笑脸承接憧憬')
S(26.68,('003',175),10,'真实学生目光，开篇落在人身上')
# Match the narration's flags, reading, buildings, library, science and sport.
S(29.6,('004',85),3,'旗帜段先呈现升旗大场面')
S(33.44,('004',90),6,'红旗与敬礼动作，留完整姿态')
S(37.68,('006',282),7,'书声：学生朗读与专注表情')
S(41.2,('006',328),30,'现代化教学楼全貌')
S(45.4,('006',168),4,'智慧课堂由建筑过渡到学习')
S(50.92,'P20',0,'图书馆旁白必须出现真实书架与阅读')
S(53.6,('002',43),4,'实验操作细节：探索未知')
S(56.0,('004',257),25,'运动舒展青春，短而完整的足球动作',speed=.8)
S(60.92,('003',97),5,'教师俯身辅导，落在生活温度')
S(64.8,('004',49),3,'古树与庭院：人文和自然')
S(70.68,'P18',0,'搭建永定门城楼实物，知识与生活共生')
# History and institutional development: identify archival material clearly.
S(74.84,('004',25),1,'百年学粹牌匾承接东城文脉')
S(79.2,'P02',0,'历史毕业典礼，明确2000年资料')
S(83.0,'P03',0,'真实教育集团揭牌，校牌完整可读')
S(87.32,('007',18),58,'揭牌实拍动作与合影，集团应势而立')
S(90.52,'P04',0,'另一校门集团揭牌，四校合力')
S(93.88,('007',19),3,'集团师生同框，承接育人新局')
S(98.12,'P01',0,'旁白说始建1997，准确呈现建校初期资料')
S(101.2,'V02',1009,'小学办学，随后接中学课堂形成贯通')
S(105.64,('006',204),8,'中学课堂，体现学段成长')
S(109.44,'P03',0,'集团校牌作为区域教育新局的实证')
S(113.44,('003',193),12,'不同学生互动，多元共生落在人身上')
# Parallel verbs are cut on the narration's meaning, without ad-style flashes.
S(117.24,('003',19),3,'课堂求索真知')
S(120.12,('004',301),31,'橄榄球赛场奋勇拼搏')
S(123.12,'P22',0,'舞台之上：金帆合唱团真实演出')
S(126.2,('004',229),6,'实践课学生动手')
S(129.12,('004',319),4,'手工课堂释放师生活力')
S(132.64,('003',247),25,'羽毛球动作舒展，克制慢动作',speed=.8)
S(136.24,'B01',0,'校内篮球比赛，德智体美劳多样性')
S(138.24,('003',255),18,'乒乓球专注击球，奋斗的瞬间')
S(140.56,('007',145),7,'跳绳的专注与坚持')
# Four schools: labels and identities locked to verified sources.
S(144.0,('004',88),8,'立德树人：敬礼与国旗')
S(147.0,('006',192),10,'守正笃行：课堂教师')
S(149.96,('007',19),7,'四校沉淀，集团人物合影')
S(153.28,'P13',0,'文汇中学科创：真实电子小车项目',title='文汇中学 · 科创领航')
S(155.64,'V01',873,'文汇小学校牌，校别明确',title='文汇小学 · 固本培元')
S(158.16,'V06',69.3,'前门外国语英语节交流，短用现有资料',title='前门外国语 · 融通中外')
S(162.04,('004',19),.8,'金台书院门匾直接证明身份',title='金台书院小学 · 文脉传承')
S(165.0,'P23',0,'小学合唱团，四校各美其美')
S(169.36,'P24',0,'金台合唱与统一活动舞台，凝聚育人根基')
S(174.6,'P11',0,'跨校联合教研，回应改革与资源共享')
S(177.56,'V02',1009,'小学阶段建立成长起点')
S(181.76,('006',222),8,'中学学生上课，成长衔接')
S(186.84,'P08',0,'教师研讨作为体系化办学实景')
S(191.52,'P25',0,'家长与学生同台，回应民生期盼')
# Teacher chapter: longer observation, reaction and shared work.
S(196.68,('006',294),10,'一支粉笔写春秋，保留书写动作')
S(201.4,('006',216),10,'教师讲解，稳住人文节奏')
S(206.28,('006',258),4,'把每个学生当成自己的孩子：俯身辅导')
S(210.0,('001',127),4,'教师倾听学生，先关系后技巧')
S(213.12,'P05',0,'师生共同阅读，以仁爱为光')
S(217.4,('006',234),10,'课堂循循善诱，讲解完整')
S(221.72,('003',97),7,'耐心答疑，教师与学生近景')
S(225.8,('003',193),30,'学生思考后的微笑，亦师亦友')
S(228.68,('004',361),8,'知行合一：学生亲手完成作品')
S(232.28,'P22',0,'合唱团素质教育成果')
S(236.04,('004',106),4,'体操集体大场面，教育之花绽放')
# Nine-year continuity: primary/secondary and shared faculty, avoid abstractions.
S(240.68,'V02',1008.6,'教育之道回到校园空间，小学阶段，避开1013.44秒原片硬切')
S(245.2,'P20',0,'小学阅读基础')
S(250.4,('003',133),6,'中学阅读与自主学习，同一学习动作衔接')
S(254.8,('004',73),3,'小学课堂，打通学段壁垒')
S(258.8,('006',186),8,'中学学生合作，课程梯度成长')
S(263.0,'P11',0,'师资共建共享，真实跨校研修')
S(267.0,('004',217),4,'探究课程，培养有路径')
S(271.4,('002',49),5,'教师细致照看实验，衔接有质量')
S(276.36,('003',217),12,'学生自信回望，以成长回应体系优势')
# Achievements and faculty development.
S(279.28,'V03',733,'奖杯陈列：收获已至')
S(283.44,'P02',0,'历届毕业生，明确历史年份')
S(288.44,'P14',0,'真实科技创新项目成果')
S(292.16,'V03',734,'荣誉作为质量的佐证，不夸大具体奖项')
S(296.52,('003',181),6,'学生自信与笑脸：奋斗成就辉煌')
S(300.36,('006',270),7,'强师兴教：教师专注讲解')
S(304.4,'P09',0,'师徒结对，名师引领与青年成长')
S(309.12,'P08',0,'教师围桌教研，骨干赋能')
S(313.6,'P10',0,'AI专题研讨，青年教师专业精进')
S(317.4,'P11',0,'跨校培训，资源共享优势互补')
S(321.08,('006',228),10,'回到真实课堂，师资建设服务每个学生')
# Curriculum: show science and the humanities as a coherent education.
S(325.28,('004',229),12,'以课程为核心，学生合作探究')
S(328.8,('006',240),8,'表达与展示，素养导向的成长课程')
S(331.36,('004',92),2,'思政铸魂：少年敬礼')
S(333.28,'P15',0,'科创赋能：电路焊接，非化学实验')
S(336.16,'V06',69.3,'外语特色：真实英语节交流')
S(338.92,'P16',0,'工笔画，体艺浸润人文素养')
S(342.52,('004',349),10,'不同课堂教学，特色项目')
S(346.2,('004',313),10,'手工传统文化的教学')
S(350.72,('004',319),10,'学生的作品与合作，拔节成长')
# Final chapter: acknowledge people, then return to four schools and the future.
S(354.8,'P14',0,'学校成绩对应学生真实成果')
S(356.92,'P25',0,'家校同心，社会口碑落在家长身上')
S(359.88,('007',31),5,'各级领导关心支持，活动现场，跟随旁白语义')
S(363.68,('007',49),4,'领导班子，真实典礼记录')
S(367.0,('006',192),18,'老师敬业奉献，继续教书育人')
S(369.72,('006',234),20,'精研教学，教师讲解的动作')
S(375.12,('006',282),14,'学生心怀家国，专注学习的行动')
S(378.08,'P03',0,'四校同心：集团揭牌')
S(381.2,'P04',0,'一脉相承，共赴新程')
S(385.08,('002',1),3,'从单点精品到集团，回看校门')
S(390.08,'P11',0,'多校资源相融，教育生态由人构成')
S(394.4,('001',127),7,'坚守育人初心，温暖师生细节')
S(398.4,('004',49),6,'深耕教育沃土，校园庭院呼吸')
S(402.24,'P13',0,'创新办学，学生科学探究')
S(406.48,'V02',1009,'贯通与融合，小学校园')
S(409.88,('003',193),45,'共生之态：同学交流与欢笑')
S(414.88,('006',328),45,'立足东城，校园全景与城市共框')
S(419.68,'P25',0,'百姓满意、社会认可：真实家校同台')
S(424.88,('007',25),12,'教育集团大场面，集体向未来，避开仰拍空树枝')
S(428.56,('003',211),15,'所有文汇人：学生群像与笑脸')
S(431.28,('004',229),15,'激活智慧、不断创新：学生动手')
S(434.0,('003',175),20,'完整保留旁白最后字尾到433.66秒')
# A short human coda replaces the former one-minute interview appendix.
S(437.4,('001',43),2.8,'教师完整口号，避开开拍指令')
S(441.68,('001',160),3.32,'师者群体完整口号，保留现场力量')
S(456.28,('001',163),47.88,'校长育人目标，句首句尾完整',title='育人目标\n文汇中学教育集团')
S(460.28,('002',19),4,'回到校园，片名收束',title='汇启新章 · 共育未来\n文汇中学教育集团')
for s in shots:
 if s['record_frame']>=434*25:s['chapter']='尾声：师者与育人目标'
photo_max={}
for s in shots:
 if s['is_photo']:photo_max[s['asset_id']]=max(photo_max.get(s['asset_id'],0),s['length_frames']/25+.6)
photo_tasks=[{'id':aid,'path':assets[aid]['path'],'duration':dur,'label':('1997年 · 建校初期' if aid=='P01' else '2000年 · 首届毕业典礼' if aid=='P02' else ''),'output':str(ROOT/'画面资料'/f'{aid}_资料影像.mp4')} for aid,dur in photo_max.items()]
for s in shots:
 if s['is_photo']:
  s['path']=next(p['output'] for p in photo_tasks if p['id']==s['asset_id']);s['in']=0;s['out']=s['length_frames']/25;s['fps']=25;s['log']=False
plan={'name':'学校_旁白精修_人文科学_v2_20261017','fps':25,'width':1920,'height':1080,'duration_frames':pos,'duration_seconds':pos/25,'narration_source':narr['source'],'narration_full_duration':narr['duration'],'narration_timeline_end_frame':10842,'narration_words_preserved':True,'style':'人文醇厚、温暖真实、科学求知、节奏有呼吸；以解说语义和师生动作选切点','shots':shots,'photo_tasks':photo_tasks,'spoken_tail':[{'shot_index':i,'kind':'现场口号' if s['record_frame']<441.68*25 else '校长讲话','path':s['path'],'in':s['in'],'length_frames':s['length_frames'],'record_frame':s['record_frame']} for i,s in enumerate(shots) if 434*25<=s['record_frame']<456.28*25],'limitations':['拍摄素材为1280×720代理，档案视频与照片分辨率不一。','仰卧起坐仍无可确认素材，未将其他动作冒充此项。','旁白字词定位为源文辅助ASR，完整音频未删改；未烧录未经人工听审的逐字字幕。']}
(OUT/'narrative_edit_plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
print('SHOTS',len(shots),'PHOTO_FILES',len(photo_tasks),'DURATION',pos/25,'WORDS',len(narr['sentences']))
