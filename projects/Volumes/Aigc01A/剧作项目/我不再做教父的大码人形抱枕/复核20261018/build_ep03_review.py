import json,re,copy,hashlib
from pathlib import Path
from datetime import datetime
P=Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕')
B=P/'提示词3.0_逐镜复刻_前3集/EP03'; O=P/'复核20261018'; E=O/'EP03动态证据'
source=json.loads((B/'source_shots.json').read_text())
versions={v:json.loads((B/v/'groups.json').read_text()) for v in ['女版','性转男版']}
changes=[
 {'id':'EP03-C01','source_shot':1,'category':'source_table_omitted_real_cut','severity':'P1','source_quote':'男主垂眸近距离凝视着身下的女主…随后缓缓闭上双眼将头埋向她颈窝','current_quote':'【Matteo】先垂眸凝视Eliza，随后缓缓闭眼、把头靠向Eliza颈侧','observed':'媒体0.160为男主过肩近景，0.200已硬切女主面部大特写；女主先睁眼看向右近处，随后闭眼，至媒体2.080才切回男主。原表第01行内部漏记反打；现提示词继承了原表遗漏。','suggestion':'原镜01拆成起始过肩近景0.04秒及女主反打大特写1.86秒，两版均补，保留原0–1.9秒区间；不把男主随后闭眼动作提前塞入起始一帧。','evidence':['critical_0.160s.png','critical_0.200s.png','opening_0.400s.png','frame_1.860s.png','critical_2.080s.png'],'cut_media_seconds':.20,'cut_video_relative_seconds':.04,'next_cut_media_seconds':2.08,'timing_note':'原表TC仅一位小数；实测下一切镜video-relative1.92，分配仍保留原表01的1.9秒。新两段为.04+1.86，不因舍入把镜2边界整体平移。'},
 {'id':'EP03-C09','source_shot':9,'category':'rewrite_initial_state_clarification','severity':'P3','source_quote':'13岁少年男主紧闭双眼…头部微微颤动','current_quote':'【少年Matteo】闭眼后双眉拧紧，呼吸急促起伏，面部肌肉微微抽动','observed':'首帧已经闭眼，全段维持闭眼；眉头随后紧蹙、头部微颤。','suggestion':'明确开镜已经紧闭双眼，维持闭眼并加回头部微颤，不另加从睁到闭的前置动作。','evidence':['frame_13.350s.png','frame_15.860s.png']},
 {'id':'EP03-C16','source_shot':16,'category':'source_table_gaze_direction_error','severity':'P2','source_quote':'眼神怯生生地斜望向画面左下方','current_quote':'先低垂小脸，再怯生生斜看画面左下','observed':'实际推镜中童年主角低头后抬眼，视线偏画面右侧，未斜看左下；双手始终局促交握。','suggestion':'低头后抬眼偏向画面右前方，保留局促疲倦与家长前景遮挡。','evidence':['critical_26.660s.png','对齐视频首帧/frame_27.720s.png']},
 {'id':'EP03-C19','source_shot':19,'category':'source_table_hand_pose_error','severity':'P2','source_quote':'双手插在西裤口袋里迈步走出大门','current_quote':'少年Matteo双手插兜走出，在台阶顶端站定','observed':'实际少年从门内走出，双手在身侧随步幅轻摆；停在高台时两手仍垂在身侧，未插兜。','suggestion':'双手自然垂在身侧走出并站定；保镖仍左右分立，门关闭→向内开→出场→站定的时机不变。','evidence':['critical_34.560s.png','critical_35.900s.png','critical_36.600s.png']},
 {'id':'EP03-C20','source_shot':20,'category':'source_table_scan_direction_error','severity':'P1','source_quote':'眼珠从画面左侧缓慢向右侧横向移动扫视','current_quote':'眼珠从画面左向右扫过人群','observed':'媒体36.680开镜瞳孔偏画面右，媒体38.200落点偏画面左；实际从右向左扫视，与下一镜向左摇至熟睡主角的视线一致。','suggestion':'眼珠从画面右向左扫过人群，最后停在画面左侧角落方向，保持头部基本不动。','evidence':['critical_36.680s.png','critical_38.200s.png']},
 {'id':'EP03-C23','source_shot':23,'category':'source_table_eyeline_error_and_rewrite_under_specified','severity':'P2','source_quote':'头微向右倾，目光斜视右下方','current_quote':'脸微侧，目光落向角落里的童年Eliza','observed':'实际头微向画面左倾、眼神朝画面左下方，与22右手在画面左下示意及21熟睡主角的角落衔接。现句未写错方向，但仍缺乏左右锁定，原表方向写反。','suggestion':'锁定头向画面左略倾，目光偏左下熟睡主角；Her./Him.各保留对应项目原句，只说一次。','evidence':['对齐视频首帧/frame_41.660s.png','对齐视频首帧/frame_42.020s.png']},
 {'id':'EP03-C33','source_shot':33,'category':'source_table_incomplete_blink_result','severity':'P2','source_quote':'随后她缓缓闭上双眼','current_quote':'先睁眼逼视，再缓缓闭眼…保留从睁眼到闭眼的先后变化','observed':'实际是睁眼逼视→短暂闭眼/慢眨→再睁眼继续审视，切到主角前眼睛已重新睁开。','suggestion':'补足短暂闭合后再次睁眼、继续冷视的落点。','evidence':['frame_51.600s.png','hands_blink_51.700s.png','hands_blink_51.900s.png','hands_blink_52.440s.png']},
 {'id':'EP03-C41','source_shot':41,'category':'source_table_transition_type_error','severity':'P2','source_quote':'女主侧影淡出，画面浮现主卧大床…叠化转场','current_quote':'先保留Eliza渐暗的左向侧影，再叠化到主卧里Matteo与Alessia相拥的轮廓','observed':'实际先把夜厅侧影淡到黑，出现极短纯黑，再从黑显出床头双人；没有清楚可见的两场人物双重曝光。','suggestion':'明确淡出经黑场再淡入床景，保留同一0.2秒原行，不另增黑场镜。','evidence':['frame_58.760s.png','对齐视频首帧/frame_58.860s.png','对齐视频首帧/frame_58.920s.png']},
 {'id':'EP03-C47','source_shot':47,'category':'source_table_incomplete_reaction_result','severity':'P2','source_quote':'随即不耐烦地闭上双眼、眉头紧锁、咬肌绷紧','current_quote':'眼神骤冷，随后不耐烦闭眼、眉头拧紧…保留斜睨到闭眼的烦躁变化','observed':'实际先朝门口（画面左）斜看并抬眉，后不耐烦闭眼皱眉，最后又睁眼朝左斜睨、压紧嘴唇/咬紧下颌。64.440/64.480/64.520是连续表演，非新切镜。','suggestion':'补回睁眼斜睨与紧抿嘴唇/下颌收紧的最后反应，保留首尾门口视线方向；不拆出误检候选。','evidence':['validate_63.160s.png','validate_63.400s.png','validate_64.440s.png','validate_64.480s.png','validate_64.520s.png','validate_64.960s.png']}
]

changes.extend([
 {'id':'EP03-C35','source_shot':35,'category':'source_table_transition_start_under_specified','severity':'P3','source_quote':'整体色调柔和偏暗…闭眼低头的正面近景定格帧','current_quote':'同一正脸和参考图衣服被柔暗光包裹…作为短暂定格','observed':'原镜35截图以及媒体54.080起，闭眼画面已开始泛起白雾，非全程维持正常暗调。','suggestion':'保留闭眼定格，但明确本短镜开始薄白雾，为原36强白过渡起点。','evidence':['frame_53.950s.png','对齐视频首帧/frame_54.110s.png']},
 {'id':'EP03-C51','source_shot':51,'category':'source_table_transition_end_under_specified','severity':'P3','source_quote':'回忆结束闪白峰值：全画幅高光白雾…接近纯白的闪白转场帧','current_quote':'强白光覆盖整幅门缝画面，只留极淡脸部及衣领轮廓…人物保持上一镜静止结果','observed':'原51的0.2秒内先到白峰，随后白雾退去；媒体66.660/66.720已经重新看清门缝人物，下一原52才进入彻底退白与轻微色散。','suggestion':'本镜写清白峰后迅速退白显出门缝脸部的过程，不把0.2秒整段保持纯白。','evidence':['frame_66.500s.png','对齐视频首帧/frame_66.660s.png','对齐视频首帧/frame_66.720s.png']}
])

for c in changes:c['evidence']=[str((E/x).resolve()) for x in c['evidence']]
change_by_shot={}
for c in changes:change_by_shot.setdefault(c['source_shot'],[]).append(c['id'])
revised={}
for v,data in versions.items():
 out=[]
 for group in data['groups']:
  prompt=group['prompt']; anchors=list(re.finditer(r'(?m)^Shot\d+:',prompt));headers=list(re.finditer(r'(?m)^出场角色：',prompt))
  for shot in group['shots']:
   n=shot['source_shot'];a=next(x for x in anchors if x.group()==f'Shot{n:02d}:');h=[x for x in headers if x.start()<a.start()][-1];first_after=next(x for x in anchors if x.start()>h.start());header=prompt[h.start():first_after.start()].strip()
   t=source['shots'][n-1]['timing'];start=float(t['start_seconds_decimal']);end=float(t['end_seconds_decimal']);dur=shot['duration_seconds'];fields=copy.deepcopy(shot['fields']);fields['时长']=f'{dur:g}秒'
   f=(v=='女版'); hero='Eliza' if f else '性转男主';boss='Matteo' if f else 'Vittoria';young='少年Matteo' if f else '少女Vittoria';kid='童年Eliza' if f else '童年性转男主';lover='Alessia' if f else '性转男情人'
   if n==9:
    fields['人物角色和运动']=f'{young}端坐暗处，正面脸部居中，开镜双眼已经闭合，肩颈紧绷，头部微微颤动。'
    fields['人物表演']=f'【{young}】维持紧闭双眼，双眉逐渐拧紧，呼吸急促起伏，面部肌肉微微抽动，表现创伤后无法安睡的痛苦。'
   if n==16:
    fields['人物表演']=f'【{kid}】先低垂小脸，再疲倦地抬眼，目光偏向画面右前方，神情局促；【前景贵妇】昂首看向前方，对{kid}没有回应。'
   if n==19:
    fields['人物角色和运动']=f'开镜双开门关闭；随后门向内推开，{young}双手垂在身体两侧、随步幅轻摆地走出，在台阶顶端站定，站定后双手仍在身侧；两名保镖紧随，最后分立左右。'
   if n==20:
    fields['人物角色和运动']=f'{young}站在台阶顶端，头部基本不动，眼珠从画面右向左扫过人群，最后停在画面左侧角落方向。'
    fields['人物表演']=f'【{young}】微眯眼、眉头轻蹙，嘴角略下压；眼神由画面右侧横扫至左侧，以挑剔与抗拒的目光衔接下一镜的左摇视点。'
   if n==23:
    fields['人物角色和运动']=f'{young}保持台阶上的选人姿势，头向画面左略倾，目光落向画面左下方角落里的{kid}。'
   if n==33:
    fields['人物表演']='【Serafina】先睁眼逼视，眼帘短暂缓缓下压闭合，随即重新睁眼继续冷冷审视；眉心微蹙、嘴唇始终绷紧。'
    fields['画面内容']='五官占满画幅的大特写，保留睁眼审视、短暂闭合、重新睁眼的慢眨过程及最后的冷视落点；五官发型依共用母亲参考图。'
   if n==41:
    fields['摄像机运动']='固定镜头（淡出至黑，再从黑淡入）'
    fields['人物角色和运动']=f'{hero}渐暗的左向侧影先淡出至黑，经过极短全黑画面，再从黑场显出主卧床头{boss}与{lover}相拥的暗轮廓。'+('成年Eliza保持大码体型、米白针织开衫及浅碎花连衣裙。' if f else '成年性转男主保持大码体型、白衬衫及米色短裤。')
    fields['人物表演']=f'【{hero}】侧影随暗化消失；【{boss}与{lover}】床景从黑显现后才出现近距离相对姿态。'
    fields['画面内容']='夜厅侧影、短暂全黑、卧室床头双人暗影依次呈现；不把两场人物叠为可见双重曝光，白色回忆晕影仍在。'
   if n==47:
    fields['人物角色和运动']=f'{boss}在主卧内听到门外敲击，脸部正对摄影机，目光先斜向画面左侧房门方向。'
    fields['人物表演']=f'【{boss}】嘴微张、呼吸未稳，先抬眉朝画面左侧斜看，随后不耐烦闭眼、眉头拧紧；最后重新睁眼斜睨左侧门口，压紧嘴唇、收紧下颌，停在明显厌烦的表情上。'
    fields['画面内容']=f'正脸与对应日常服装领口占画幅，机位固定；完整保留向左斜看、闭眼皱眉、再次睁眼斜睨并抿唇的反应过程。'
   if n==35:
    fields['环境氛围']='回忆场景：庄园会客厅，柔暗背景上开始泛起一层薄白雾，白色回忆晕影变亮，衔接下一镜强闪白。'
    fields['画面内容']='同一闭眼低头的正面近景短暂停住，脸和参考图衣服仍清楚；薄白雾从正常暗调上开始叠入，为下一镜强白过渡提供起点。'
   if n==51:
    fields['人物角色和运动']=f'{hero}在同一门缝中保持静止，开镜被强白光遮掩，随后白雾迅速减弱，脸部与衣领逐渐重新显露。'+('成年Eliza保持大码体型、米白针织开衫及浅碎花连衣裙。' if f else '成年性转男主保持大码体型、白衬衫及米色短裤。')
    fields['人物表演']=f'【{hero}】保持前镜闭口静止的凝望；【转场】白峰短暂留白后开始退去。'
    fields['画面内容']='从接近纯白的峰值迅速退成半透明白雾，逐渐看清同一门缝中央的脸和衣领；结尾仍有退白残雾，不把本镜全段锁成纯白定格。'
   common={'original_source_shot':n,'split_part':1,'split_total':1,'start_seconds':start,'end_seconds':end,'duration_seconds':dur,'fields':fields,'header_text':header,'asset_names':shot['asset_names'],'change_ids':change_by_shot.get(n,[]),'old_full_id':shot['full_name'],'original_source_TC':shot['source_TC']}
   if n==1:
    common['split_total']=2; common['end_seconds']=.04;common['duration_seconds']=.04;common['fields']['时长']='0.04秒'
    common['fields']['摄像机运动']='固定镜头（仅保留起始一帧，随后硬切反打）'
    common['fields']['人物表演']=f'【{boss}】睁眼近距离凝视{hero}；【{hero}】保持左下前景的仰卧侧颜。本段只有起始一帧，不提前完成闭眼或埋头入睡动作。'
    common['fields']['画面内容']=f'左下{hero}侧颜及肩部微虚焦作前景，右上{boss}睁眼的脸部清楚，暖调床品在后；保留原片开头这一帧后立即硬切。'
    out.append(common)
    part=copy.deepcopy(common);part.update({'split_part':2,'start_seconds':.04,'end_seconds':1.9,'duration_seconds':1.86})
    part['fields']={'时长':'1.86秒','环境氛围':f'{hero}公寓卧室床榻，暖黄柔和光影，延续同一床铺的静谧私密夜间气氛。','景别':'大特写(ECU)','拍摄角度':f'平视微俯的卧姿反打；{hero}面部几乎充满竖屏，眼睛位于上半部，鼻梁与双唇清楚。','摄像机运动':'固定镜头（由上一镜过肩画面硬切至Eliza面部反打）' if f else '固定镜头（由上一镜过肩画面硬切至性转男主面部反打）','人物角色和运动':f'{hero}仰卧枕上，脸微朝画面右侧，与近处{boss}保持同一距离；不抬头起身，{boss}仅以画面边缘暗色衣料作为空间延续。','人物表演':f'【{hero}】开镜双眼睁开，望向画面右侧近处的{boss}，随后缓缓闭上双眼；双唇轻合，闭眼后安静停留，呼吸轻柔。','画面内容':f'反打只突出{hero}的眼睛、鼻梁、双唇与暖光中的脸部，额边发丝及枕边柔焦；由睁眼到闭眼的反应占满本镜，五官、发型、体型及睡衣保持原参考图。'}
    # 同一床上双人关系仍需保留两张角色参考，避免反打时换脸换衣。
    out.append(part)
   else:out.append(common)
 revised[v]=out
assert all(len(x)==57 for x in revised.values())
assert all(abs(sum(y['duration_seconds'] for y in x)-67.4)<.0001 for x in revised.values())
assert all(set(y['original_source_shot'] for y in x)==set(range(1,57)) for x in revised.values())
# 对白单次出现且没有改动项目英文原句。
for v,items in revised.items():
 old='\n'.join(s['fields']['人物表演'] for g in versions[v]['groups'] for s in g['shots']);new='\n'.join(s['fields']['人物表演'] for s in items)
 assert re.findall(r'“([^”]+)”',old)==re.findall(r'“([^”]+)”',new),(v,'dialogue changed')
res={'episode':3,'old_source_count':56,'new_count_per_version':57,'user_decision':'按原样片补齐真实切镜并重新按5镜分组；保留各原表行映射，不删不合并短过渡行。','changes':changes,'versions':revised,'source_workbook_sha256':hashlib.sha256(Path(source['source_workbook']['path']).read_bytes()).hexdigest(),'generation_submitted':False,'status':'independent_review_revision_draft_for_root_publication','timing_policy':'总体保留原表每行一位小数时间范围；仅第01行内部按样片切点拆0.04+1.86。原片首视频PTS=.16，候选容器切点减.16才是video-relative；TC舍入±.04不误拆额外镜。'}
(O/'EP03_修订镜头.json').write_text(json.dumps(res,ensure_ascii=False,indent=2))
print('wrote',O/'EP03_修订镜头.json','counts',[(v,len(x))for v,x in revised.items()])
