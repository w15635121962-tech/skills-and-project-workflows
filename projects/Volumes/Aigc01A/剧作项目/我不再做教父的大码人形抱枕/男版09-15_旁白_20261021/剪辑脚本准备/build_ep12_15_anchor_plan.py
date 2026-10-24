"""Reviewed source-picture selections and canonical prose anchors, not final record timing.
No Resolve/browser calls and no changes to source audio/video.
"""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parent.parent
OUT=Path(__file__).resolve().parent
inv=json.loads((OUT/'media_inventory_native.json').read_text())
audit=json.loads((ROOT/'ASR/同期对白与原带音轨核查.json').read_text())
manifest=json.loads((ROOT/'准备/narration_manifest.json').read_text())
source={v['filename']:v for ep in inv['episodes'] for v in ep['videos']}
byunit={u['id']:u for u in audit['dialogue_units']}
byep={e['episode']:e for e in manifest['episodes']}
plan={'status':'SOURCE_SELECTION_AND_ORIGINAL_PROSE_ANCHORS_REVIEWED_WAIT_NEW_NARRATION_TIMING','project':'大码枕头','fps':24,'episodes':[],'execution_allowed':False,'verification_scope':'58 source MP4s reviewed through232 actual still frames (4timepoints/file), plus cut detection and blind2-model audio evidence for flagged variants. This is not continuous playback or human listening. No new VO or final record time is invented.','source_media_modified':False,'resolve_used':False,'browser_used':False}

def r(name,a,b,action,note=''):
    v=source[name];assert 0<=a<b<=int(v['video_streams'][0]['nb_frames'])
    return {'path':v['path'],'source_start_frame':a,'source_end_frame':b,'record_frame':None,'duration_frames':b-a,'gain_db':next(f['source_audio_gain_suggestions']['suggested_ambience_under_vo_gain_db'] for f in audit['files'] if f['filename']==name),'speed_percent':100,'tag':action,'source_visual_action':action,'review_note':note,'same_source_linked_sync_audio_required':True}

def n(label,pp,*ranges,note=''):
    return {'kind':'narration_story_block','label':label,'original_docx_paragraphs':list(pp),'source_ranges':list(ranges),'timeline_start_frame':None,'timeline_end_frame':None,'note':note}

def d(ep,p,q,name,a,b,note=''):
    uid=f'EP{ep:02d}_P{p:04d}_Q{q}';u=byunit[uid]
    candidates=[c for c in u['source_candidates'] if Path(c['source_path']).name==name];assert len(candidates)==1
    c=candidates[0];assert not c['substantive_content_variant'];assert a<=c['source_in_frame'] and b>=c['source_out_frame_exclusive']
    s=r(name,a,b,'完整原文同期对白 '+uid,note)
    s['gain_db']=next(f['source_audio_gain_suggestions']['suggested_speech_gain_db'] for f in audit['files'] if f['filename']==name)
    s['contains_protected_original_dialogue']=True;s['dialogue_unit_id']=uid
    return {'kind':'protected_external_dialogue','label':uid,'original_docx_paragraphs':[p],'dialogue_unit_id':uid,'original_text':u['original_text'],'source_ranges':[s],'observed_word_events':c['word_events'],'source_sha256':c['source_sha256'],'word_safe_minimum_source_range':[c['source_in_frame'],c['source_out_frame_exclusive']],'timeline_start_frame':None,'timeline_end_frame':None,'narration_must_not_overlap_dialogue':True,'note':note}

def ep(num,blocks,notes,alternatives,excluded):
    m=byep[num];groups=[g for g in manifest['groups'] if g['episode']==num]
    used={};flatten=[]
    for bi,b in enumerate(blocks):
        b['story_order']=bi+1
        for c in b['source_ranges']:
            for a,z in used.setdefault(c['path'],[]):assert c['source_end_frame']<=a or c['source_start_frame']>=z,('Repeated proposed source',num,c,a,z)
            used[c['path']].append((c['source_start_frame'],c['source_end_frame']))
            flatten.append(dict(c,story_block_index=bi+1,original_docx_paragraphs=b['original_docx_paragraphs']))
    ids=[b['dialogue_unit_id'] for b in blocks if b['kind']=='protected_external_dialogue']
    expected=[u['id'] for u in audit['dialogue_units'] if u['episode']==num]
    assert len(ids)==len(set(ids)) and set(ids)==set(expected),(num,ids,expected)
    narrative={b['docx_paragraph'] for b in m['original_paragraphs_and_retained_narration'] if b['narration_retained_text'].strip()}
    mapped={p for b in blocks if b['kind']=='narration_story_block' for p in b['original_docx_paragraphs']}
    assert narrative<=mapped,(num,narrative-mapped)
    result={'episode':num,'timeline_name':f'大码_男版_EP{num:02d}_新男版音色_原速旁白_自动剪辑_v1','duration_frames':None,'video':flatten,'narration':[{'logical_basename':g['basename'],'path':g['planned_audio_path'],'source_start_frame':None,'source_end_frame':None,'record_frame':None,'speed_percent':100,'gain_db':None,'original_docx_paragraphs':g['source_docx_paragraphs'],'status':'WAIT_REAL_DOWNLOADED_VO_AND_REVIEWED_WORD_TIMING'} for g in groups],'subtitle_srt':str(ROOT/'字幕'/f'EP{num:02d}.srt'),'story_blocks':blocks,'dialogue_units_covered_once':len(ids),'original_narration_paragraphs_covered':sorted(narrative),'source_ranges_nonoverlapping':True,'source_picture_pool_frames':sum(v['duration_frames'] for v in flatten),'source_picture_pool_seconds':sum(v['duration_frames'] for v in flatten)/24,'pool_is_not_a_timeline_duration':True,'optional_alternatives':alternatives,'excluded_source_ranges_or_variants':excluded,'editorial_notes':notes,'limitations':['Record times, narration cuts and final duration remain unset until actual newly downloaded narration is recognized. No placeholders may be assembled.','Candidate picture pools must be trimmed to actual prose timing, not mechanically all appended; source actions and dialogue words remain protected.','Complete original dialogue is evidenced by canonical ASR source words and snapshot context, not by full human listening/lip-sync audition.']}
    plan['episodes'].append(result)

blocks12=[
 n('闭口示意接电话、电话另一端情人声音出现',[351,352],r('男版12-1-1.mp4',0,194,'Oliver俯卧、Vittoria拿起手机反应','裁在原片8.08s；不进入后半hard变体对白')),
 d(12,353,1,'男版12-1-2.mp4',0,145,'采用bad完整版本；对方从电话传来，画面是Vittoria听电话。不得再追加12-1-1的同句。'),
 n('Vittoria皱眉站起',[354],r('男版12-2-1.mp4',0,67,'Vittoria在床旁站起接电话')),
 d(12,355,1,'男版12-2-1.mp4',67,144),
 n('挂断电话、穿回外衣',[356],r('男版12-2-1.mp4',144,337,'电话结束、Oliver伏枕反应、Vittoria穿外衣','144–157结束动作；157–226男主反应；226–337穿衣，可按实测VO保留动作内切点')),
 n('未盖药膏与临出门回望',[357,358],r('男版12-3-1.mp4',0,224,'药膏前景、Oliver床上抬眼、门口Vittoria回望')),
 d(12,359,1,'男版12-3-1.mp4',224,271),
 n('门口冷暗的她与灯下独坐的他',[360,361],r('男版12-3-2.mp4',50,125,'门口Vittoria的无对白中近景','替代镜只取原话开始前的稳定门口姿态，最终须核对无转身倒回'),r('男版12-3-1.mp4',271,313,'Oliver听完门口的话后静坐'),r('男版12-4-1.mp4',50,134,'Oliver坐床上抬眼看门口')),
 d(12,362,1,'男版12-4-1.mp4',134,199),
 n('第六夜、搬空衣柜',[363,364],r('男版12-5-1.mp4',0,213,'空房与衣柜、移出的行李','0–156房间；156–213衣柜。不要再接12-5-2相同衣柜动作重演')),
 n('交换名额与文件',[365],r('男版12-5-1.mp4',257,361,'Oliver查看录取文件')),
 n('管家来电，他知道母亲正在听',[366,367],r('男版12-6-1.mp4',0,174,'接电话前的手机和Oliver独处反应')),
 d(12,368,1,'男版12-6-1.mp4',174,405),
 n('管家挂断、只剩床上物品',[369,370],r('男版12-5-1.mp4',213,257,'已经收好的行李锁扣','补行李细节，无新增收拾剧情'),r('男版12-7-1.mp4',0,116,'小床、枕头与玩偶仍在原处')),
 n('两个枕头和不能缺的玩偶',[371,372],r('男版12-7-1.mp4',116,337,'Oliver看向小床和玩偶，保持最后一夜的布置')),
 n('十年最后一夜、离开卧室等在客厅',[373,374],r('男版12-8-1.mp4',0,361,'床上手与玩偶细节、他起身离开卧室、暗客厅等待','实际源是一条延续移动；根据VO取连续动作，不与12-8-2重复起身')),
 n('等到凌晨、接起手机',[375,376],r('男版12-9-1.mp4',0,337,'手表和手机、拿起手机到耳边、等待的脸')),
 d(12,377,1,'男版12-10-1.mp4',0,72),
 n('熟悉的十年语气、等待电话里先传来的Evan声音',[378,379],r('男版12-10-1.mp4',72,289,'Oliver静听、眼神转冷，客厅留白','Evan烟花对白留给下一集开头；不提前叠加13-1的重复对白')),
]
ep(12,blocks12,['12-1-1前段动作与12-1-2正确bad音轨组合；每个实际选段的V/A1仍同源同剪，不使用换音假口型。','12-3/4两份子镜是重复原句的替代角度，不应两遍播放；本方案只选一遍对白，其余只取无说话的对应姿态。','第六夜从冷夜床上黑睡衣切到白衬衫收拾房间，按原文时间跳转，不在同一瞬间无因换装。'],[{'filename':'男版12-3-2.mp4','reason':'门口原句替代：129–185可整体替换12-3-1对应对白，不可重复追加。'},{'filename':'男版12-4-2.mp4','reason':'70–141原句替代近景；只有实际轴线更顺时才整体替换。'},{'filename':'男版12-8-2.mp4','reason':'男主看小床/离开卧室的紧景，可替换主版对应动作，不得再完整重演。'}],[{'path':source['男版12-1-1.mp4']['path'],'source_start_frame':194,'source_end_frame':385,'reason':'后段包含同句hard内容变体及回到床边；用正确bad版后不保留重复音轨。'}])

blocks13=[
 d(13,382,1,'男版13-1-2.mp4',0,121,'完整烟花告白只出现一次，电话所听内容；不再追加13-1-1前110帧同句'),
 n('她笑着准备接电话',[383],r('男版13-1-1.mp4',113,240,'Evan得意近景与Vittoria在烟花下的含笑关系','从原话结束后取反应，不再出现同句声音')),
 d(13,384,1,'男版13-2-1.mp4',10,85,'女主在电话另一端说，镜内Oliver听电话'),
 d(13,385,1,'男版13-2-2.mp4',50,152,'Evan电话外音完整挽留句；不另播13-2-1后半同句'),
 n('她轻笑改口',[386],r('男版13-3-2.mp4',0,81,'烟花下Vittoria听对方后的浅笑')),
 d(13,387,1,'男版13-3-2.mp4',81,145),
 n('Oliver沉默听完，最后一点留恋消失',[388,389],r('男版13-3-1.mp4',141,289,'Oliver将手机移开，视线落下'),r('男版13-4-1.mp4',49,117,'夜窗前静下来的Oliver')),
 n('普通清晨，机场登机',[390],r('男版13-4-1.mp4',117,265,'机场拉箱到机舱落座','不先用飞机再倒回机场；13-4-2只作替代')),
 n('忆起十三岁独自去庄园',[391,392],r('男版13-5-1.mp4',0,261,'庄园建立、胖少年在人群中、少年走向庄园','此处是明确回忆，不把少年混入现在机舱')),
 n('少年在心里给自己打气',[393],r('男版13-5-2.mp4',0,121,'少年抿嘴抬眼近景','原文引号是内心话，由新男版旁白承载，不新增儿童口型对白')),
 n('回到二十三岁的机舱',[394],r('男版13-5-1.mp4',261,313,'回忆结束后切回成年Oliver机舱脸部'),r('男版13-6-1.mp4',0,128,'成年Oliver窗边与机翼外的晨光')),
 n('旧SIM换新卡',[395],r('男版13-6-1.mp4',128,241,'手机和换卡手部动作','只完成一次换卡，不再播13-7-1开头另一遍抽卡')),
 n('心里的声音、不再回头',[396,397],r('男版13-7-1.mp4',58,265,'成年Oliver机舱侧脸、窗外云层与新的远望','同样是内心旁白，保留原文，不做对外说话')),
]
ep(13,blocks13,['13-2两版都是Oliver听电话的角度，电话另一端男女声音不等于镜内男主开口。','13-4-1机场→机舱和13-5回忆少年必须保留时间层次，不能按目录把少年镜与成年人电话混剪。','13-6/7换SIM是同一事件不同覆盖，采用13-6后半完整一次；13-7只取后面的脸与云。'],[{'filename':'男版13-4-2.mp4','reason':'机场/机舱近景替代，按同一动作阶段替换，不能重复登机。'}],[{'path':source['男版13-1-1.mp4']['path'],'source_start_frame':0,'source_end_frame':113,'reason':'与已采用13-1-2同一句烟花告白重复。'},{'path':source['男版13-7-1.mp4']['path'],'source_start_frame':0,'source_end_frame':58,'reason':'换卡插入镜作为备用，主选13-6已完成动作，不再重演。'}])

blocks14=[
 n('Evan哄睡失败，她仍醒着，他拉近领口',[400,401],r('男版14-1-2.mp4',20,121,'Vittoria侧躺睁眼、Evan靠近','去掉片头两模型识别到What did you do?的0–0.58s，留0.25s额外边界'),r('男版14-1-1.mp4',101,313,'Vittoria疲倦反应、Evan贴近颈侧拉领','去掉片头0–3.94s非剧本疑似声，保留其后完整动作；不得字幕化那些词')),
 d(14,402,1,'男版14-2-2.mp4',0,95,'本地仅此2-2，但原文完整，不因为缺2-1编号而补写或漏句'),
 n('Vittoria看他，带着一点兴味',[403],r('男版14-2-2.mp4',167,313,'Vittoria的反应近景')),
 n('Evan张扬，与Oliver相反',[404,405],r('男版14-2-2.mp4',95,167,'Evan贴近时的正脸','此段是无台词反打覆盖，剪辑后需确认动作没有倒回'),r('男版14-3-1.mp4',0,62,'床上两人近距关系中的Evan')),
 n('她走神，想到这个时间Oliver总在读书',[406,407],r('男版14-3-1.mp4',62,173,'Vittoria目光飘开、失神反应'),r('男版14-3-2.mp4',0,72,'Oliver在小床读书的回忆')),
 n('她眼中的无趣与总会回应的拥抱',[408,409],r('男版14-4-1.mp4',0,229,'书页、Oliver读书、她夺书拉近、他环住她','这是Oliver记忆段；回到Evan套房时显式切回，不改变两人身份')),
 n('回到当夜，她开手机，笑意冻结在空白聊天',[410,411,412],r('男版14-5-1.mp4',0,140,'床上看手机的笑、脸部细节转冷')),
 n('立刻拨号，三分钟无人接听的焦灼',[413,414],r('男版14-5-1.mp4',140,346,'Vittoria拨打等待，Evan在侧后方','三分钟由原旁白浓缩，不能无因循环这段或变速')),
 n('Evan再次凑近',[415],r('男版14-5-1.mp4',346,385,'Evan向她侧脸贴近')),
 d(14,416,1,'男版14-6-1.mp4',68,114),
 n('她压住慌意、冷脸关掉屏幕',[417],r('男版14-6-1.mp4',114,337,'手机等待、Vittoria眼神、压唇、屏幕翻扣关闭')),
 n('不再打电话，转回Evan身边',[418],r('男版14-7-1.mp4',0,110,'夜晚床上她靠回Evan，手臂环近')),
 n('第二天仍无回音，她终于失控',[420],r('男版14-7-1.mp4',110,313,'白天Evan在床上、Vittoria看手机和起身','场景在110帧进入次日；不要从日景再倒回夜间')),
 n('无视Evan，离开套房开车',[421],r('男版14-8-1.mp4',56,245,'Evan被留在床上、Vittoria走出、日间驾车','只取两模型非剧本Just any two?结束后0.59s起的区域，保留动作与其原音')),
 n('原密码仍有效，开门进入',[422],r('男版14-8-1.mp4',245,289,'公寓门锁密码特写'),r('男版14-9-1.mp4',0,66,'从门口开入空房')),
 n('空荡公寓，她的错愕',[423],r('男版14-9-1.mp4',66,313,'空房、Vittoria震惊近景、走入无人房间')),
]
ep(14,blocks14,['14-1-1疑似话音两模型内容不一致，不能据此确认具体词；本方案直接裁掉0–3.94s及余量，没有字幕或替换原角色台词。','14-1-2、14-8-1、14-8-2片头两模型一致的非原文人声候选均不纳入成片；仍保留裁后源片A1，不整条静音。','14-2-2与14-6-1的两句原剧对白均完整保留，未为新旁白压掉。','回忆Oliver读书/环抱→现实Vittoria与Evan→次日离开，按原文三层时间组织，避免混床/混人。'],[{'filename':'男版14-8-2.mp4','source_start_frame':51,'source_end_frame':121,'reason':'仅作安静出门角度替代；两模型Wait it...到1.9s，建议≥2.125s开始。不得再接主版同一出门动作。'},{'filename':'男版14-9-2.mp4','reason':'空屋与Vittoria脸部反应的替代；不重复开门和重新发现空屋。'}],[{'path':source['男版14-1-1.mp4']['path'],'source_start_frame':0,'source_end_frame':101,'reason':'两模型均在0–3.94s捕捉到非剧本疑似声，文本不一致。'},{'path':source['男版14-1-2.mp4']['path'],'source_start_frame':0,'source_end_frame':20,'reason':'两模型What did you do?至0.58s，附余量裁掉。'},{'path':source['男版14-8-1.mp4']['path'],'source_start_frame':0,'source_end_frame':56,'reason':'两模型Just any two?最晚1.74s结束；从新场面56帧起保留动作。'},{'path':source['男版14-8-2.mp4']['path'],'source_start_frame':0,'source_end_frame':51,'reason':'两模型Wait it...最晚1.9s结束，裁至2.125s；本版暂不采用。'}])

blocks15=[
 n('惊慌从脸、手、手机浮出，她打给consigliere',[426,427],r('男版15-1-1.mp4',0,265,'Vittoria侧脸、握手、拿起手机')),
 d(15,428,1,'男版15-2-1.mp4',9,53),
 n('电话另一端没反应过来',[429],r('男版15-3-2.mp4',0,30,'Vittoria等待回答的侧脸','对方是电话外音，不能把本镜内Vittoria标成consigliere')),
 d(15,430,1,'男版15-2-1.mp4',69,144),
 d(15,431,1,'男版15-3-1.mp4',0,28),
 n('对方迟疑，她握紧等答复',[432],r('男版15-3-1.mp4',28,130,'手部和等待的Vittoria')),
 d(15,433,1,'男版15-3-1.mp4',130,193),
 d(15,434,1,'男版15-4-1.mp4',0,69),
 n('她厉声打断',[434],r('男版15-4-1.mp4',69,95,'Vittoria发火的句间动作','仅承载保留的旁白reporting clause Vittoria snapped.，不把引号台词再读一遍')),
 d(15,434,2,'男版15-4-1.mp4',95,157),
 n('电话转给对方回应前的原始呼吸与反应',[],r('男版15-4-1.mp4',157,175,'句间反应','无新增旁白；18帧同期停顿可与前后原速连续合并')),
 d(15,435,1,'男版15-4-1.mp4',175,312),
 n('转至庄园，她到来，母亲仍在修花',[437,438],r('男版15-5-1.mp4',101,157,'Blackwood庄园外观'),r('男版15-6-1.mp4',0,78,'Vittoria步入花园桌旁'),r('男版15-5-1.mp4',157,259,'母亲修花、放缓手中动作','不使用5-1开头公寓门内镜来假作已到庄园')),
 d(15,439,1,'男版15-5-1.mp4',259,313),
 n('Vittoria盯住母亲',[440],r('男版15-6-3.mp4',0,60,'Vittoria近景维持直视')),
 d(15,441,1,'男版15-6-1.mp4',89,157),
 n('母亲轻慢地停下手、带笑回应',[442],r('男版15-6-1.mp4',170,241,'母亲的听后反应'),r('男版15-7-1.mp4',0,78,'母亲在花园桌旁放低手中物、轻笑','源快照能确认花园桌旁手部和笑；完整放剪、掸手细节仍需实际连续回放，不能伪称已完整看到')),
 d(15,443,1,'男版15-7-1.mp4',78,307),
 n('Vittoria皱眉，只问一句',[444],r('男版15-8-2.mp4',0,73,'Vittoria近景眼神收紧')),
 d(15,445,1,'男版15-8-2.mp4',73,100),
 d(15,446,1,'男版15-8-1.mp4',125,192),
 n('母亲毫不在意，仍认定她很快会忘记',[447,448],r('男版15-9-1.mp4',0,187,'母亲低头继续整理花束'),r('男版15-9-1.mp4',273,313,'庄园花园的空间留白','避开187–238的Vittoria走开主体动作，原文未交代她离开；末段是否含背影需最终逐帧裁到空景273后')),
]
ep(15,blocks15,['电话中consigliere均为画外原音；Vittoria在镜内听，不要让她假作说出对方台词。','15-4三句原话来自一条源片，中间Vittoria snapped.保留原旁白短插口，源停顿够不够须按新VO实测；不切进角色单词。','公寓至花园只用庄园建立、Vittoria进入、母亲修花，保持身份和时间因果。','15-6、15-7替代镜不可再重复同句；优先整段原声、一遍完整母亲长句。'],[{'filename':'男版15-6-2.mp4','source_start_frame':14,'source_end_frame':84,'reason':'Who gave you permission...的替代，主版已经完整用6-1，不再重复。'},{'filename':'男版15-7-2.mp4','source_start_frame':64,'source_end_frame':239,'reason':'母亲长句替代快版，只可整体替换7-1，不能两段接成重复。'},{'filename':'男版15-8-1.mp4','source_start_frame':85,'source_end_frame':115,'reason':'Where is he?替代；本方案用8-2近景，只从8-1母亲反打取另一句。'}],[{'path':source['男版15-9-1.mp4']['path'],'source_start_frame':187,'source_end_frame':273,'reason':'Vittoria走开主体动作不是当前原文交代的新增事件，暂不采用。'}])

# Actual new-audio observations are added without forcing missing names/times.
new=ROOT/'ASR/new_narration/旁白逐词原文核验.json'
bylogical={}
if new.exists():
    for x in json.loads(new.read_text()).get('files',[]):bylogical.setdefault(x['logical_basename'],[]).append(x)
for e in plan['episodes']:
    e['observed_new_narration']=[]
    for g in [g for g in manifest['groups'] if g['episode']==e['episode']]:
        for f in bylogical.get(g['basename'],[]):
            e['observed_new_narration'].append({k:f.get(k) for k in ['logical_basename','actual_basename','source_path','source_sha256','decoded_duration_seconds','exact_normalized_original_words_in_order','differences','source_paragraph_anchors','source_asr_json','recommendation']})
    e['observed_new_narration_count']=len({x['logical_basename'] for x in e['observed_new_narration']})
plan['actual_new_vo_observation_source']=str(new)
plan['total_protected_dialogue_once']=sum(e['dialogue_units_covered_once'] for e in plan['episodes'])
assert plan['total_protected_dialogue_once']==24
p=OUT/'剪辑计划_EP12-15_锚点.json';p.write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'plan':str(p),'status':plan['status'],'episodes':[{'episode':e['episode'],'narration_segments':len(e['narration']),'actual_vo_observed':e['observed_new_narration_count'],'protected_dialogue':e['dialogue_units_covered_once'],'source_pool_seconds':round(e['source_picture_pool_seconds'],3)} for e in plan['episodes']]},ensure_ascii=False,indent=2))
