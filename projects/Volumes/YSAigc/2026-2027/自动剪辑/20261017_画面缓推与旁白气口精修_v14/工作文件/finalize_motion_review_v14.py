from pathlib import Path
import json,hashlib,collections,datetime
R=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_画面缓推与旁白气口精修_v14/工作文件');O=R/'源画面运动审阅'
snapshot_path=R/'live_before_v14.json';live=json.loads(snapshot_path.read_text());rows=json.loads((R/'source_motion_diagnostics_v14.json').read_text());idx={(x['track'],x['start']):x for x in rows}
chosen=[60,234,340,942,1067,2263,2595,3003,3675,4161,4609,4854,5717,6260,6370,6420,6909,7965,9045,9092,9175,9243,9627,9690,10162,10622,10850]
strong={942,3003,3675,6260,9092}
framing_order=[60,234,340,942,1067,1819,2263,2595,3003,3675,4161,4609,4854,5717,6260,6370,6420,6909,7965,9045,9092,9175,9243,9627,9690,10162,10622,10850]
notes={
60:('笔尖与手指书写动作细微，机位稳定；缓推可将注意力收束到阅读和批注。','笔尖、手指与书页主体在2.5%模拟终点完整；采用2%保留手部空间。'),
234:('教师与学生围读，机位近于固定；小幅推进突出陪伴与人文气息。','教师脸部、学生主要面部与书本安全；右前景头顶原已出画，2%不会新增切脸。'),
340:('文汇中学校名建筑为稳定低角度构图，缓推增强开篇的庄重感。','2.5%模拟仍保留校名全部字符；采用2%保留建筑与校名余量。V2开篇标题独立，不随画面推近。'),
942:('教学楼全景机位稳定，轻微光影变化；克制推进增加空间纵深。','建筑主体和主要线条均有安全余量。'),
1067:('学生从书本前微微抬头，背景稳定；缓推承接人物情绪。','首中尾五官在2.5%模拟均完整；原人物近景头顶偏紧，采用2%保留抬头余量，不裁额头或五官。'),
2263:('学生安静阅读、教师在旁，场景动作小；缓推强调真实课堂陪伴。','阅读学生脸部和书页完整；左侧前景头部原有裁边不额外强化，采用2%。'),
2595:('两名学生在黑板前，机位基本稳定；小幅推进聚焦自主学习。','两名学生主要面部与举起的手在2.5%模拟仍保留；短镜用2%。'),
3003:('户外合唱队为静机位集体场面，只有自然表情变化；适合轻推凝聚集体感。','主要合唱成员脸部和队形均有余量。'),
3675:('集团牌前集体站立，机位稳定，人物微表情为主；轻推增加仪式感。','集团牌与主要人物脸部在2.5%模拟完整。'),
4161:('学生已站定回答，人物只有嘴部和上身小动作；固定中心缓推可突出专注。','主体学生面部、头顶完整；底部原前景头部不作为新裁切目标。'),
4609:('蓝衣教师在黑板前讲授，机位稳定；细微推进强化讲课状态。','教师面部与手势在2.5%模拟均安全。'),
4854:('课堂中景机位稳定，教师板书动作清楚；缓推增加观察感。','教师身体、板书手与课堂主体完整，保留原教学空间。'),
5717:('沙画手指作轻微笔触，机位稳定；轻推聚焦实践细节。','手指和沙画主体在2.5%模拟完整；1.8秒短镜只用2%。'),
6260:('小学教室后排全景机位稳定，人物动作细微；轻推引导视线向教师。','教师、课堂主要人物及前方教学区均有安全余量。'),
6370:('男生安静书写，背景稳定，只有面部和笔尖小动作；适合缓推。','主脸部和书写区域在2.5%模拟完整；原近景头顶已出画，2%只轻微加紧头发边缘，不裁额头或面部。'),
6420:('写字手部与书页细节，机位稳定；缓推补充学习氛围。','笔尖、手指及书页主体在2.5%模拟完整。'),
6909:('奖杯陈列为近静止画面；轻推增强成果段落的层次。','右侧主奖杯及底座完整；远左原本局部出画的小奖杯保持原有边缘关系，采用2%。'),
7965:('白衣教师讲课，机位基本稳定，手势动作小；缓推强调教学交流。','教师面部和主要手势在2.5%模拟内安全。'),
9045:('典礼大场面为稳定全景，只有自然人群微动；小幅推进增加临场感。','舞台及主要人群完整；1.88秒短镜采用2%。'),
9092:('黑衣教师在黑板前平稳讲课，机位稳定且时长3.32秒；适合轻推。','教师脸部、肩部与讲课手势均有充分余量。'),
9175:('教师与学生围绕英语材料交流，机位只有很小自然抖动；缓推聚焦互动。','教师面部、学生主要面部和纸张在2.5%模拟完整；采用2%。'),
9243:('学生阅读后抬眼，机位稳定；微推承接人物神态变化。','首中尾主要学生脸部和头顶在2.5%模拟均完整。'),
9627:('课堂集体中景机位稳定，适合小幅推进强调课堂秩序与参与。','左前方教师头顶原已偏紧，但面部在2.5%模拟未被切；限定2%，不使用2.5%。'),
9690:('窗边学生安静书写，机位稳定；缓推突出专注神态和自然光。','主要面部与书写手部在2.5%模拟完整。'),
10162:('学生微笑交流，机位稳定，3.4秒足以形成克制缓推；以人物情绪丰富尾段。','多名主要学生脸部与书本在2.5%模拟均完整。'),
10622:('学生群像只有微笑和轻微表情变化，机位稳定；3.68秒适合缓推。','前后排主要学生面部在2.5%模拟均保留。'),
10850:('教师个人口号为固定机位，人物表情和末尾握拳动作较小；细推增强精神面貌。','面部及末尾举起的拳头在2.5%模拟均安全；采用2%，保持原声同步。')}
camera={782,1002,1204,2641,4365,4736,4976,5959,6080,6195,6530,6575,6625,6675,6847,7345,7461,7840,8332,8768,8923,8997,9452,9530,9579,9752,9910,10010,10109,10310,10432,10935,11407}
large={175,561,667,727,1340,2075,2931,3228,3288,3347,3406,3456,3514,5807,5854,6315,8220,9310,10492,10557,10782}
close={117,508,614,889,1273,1397,1523,1584,2407,2503,2689,2786,2886,3078,3178,4788,5035,5096,5157,5328,5382,5435,5489,5543,5645,5762,6730,6785,7036,7278,7669,8027,8075,8171,8507,8563,8665,8819,9806,10714}
selected=[];not_selected=[]
for i,x in enumerate(rows):
 key=(x['track'],x['start']);start=x['start'];sheet=str(O/f'七点源帧_{i//9+1:02d}.jpg')
 common={'track':x['track'],'start':start,'end':x['end'],'length_frames':x['length_frames'],'duration_seconds':x['length_frames']/25,'source':x['path'],'source_offset_frames':x['offset'],'source_in_seconds':x['source_time_seconds'],'source_frame_paths':[a['path'] for a in x['samples']],'source_sample_times':[a['actual_time'] for a in x['samples']],'contact_sheet':sheet,'source_frames_actually_viewed':True,'original_edit_intent':x.get('intent','')}
 if key[0]==1 and start in chosen:
  common.update(amplitude=0.025 if start in strong else 0.02,center=[0.5,0.5],motion='push',size_start=1.0,size_end=1.025 if start in strong else 1.02,reason=notes[start][0],title_and_face_safety=notes[start][1],framing_2_5_percent_check={'viewed':True,'first_middle_last_safe':True,'contact_sheet':str(O/f'候选2.5%构图核查_{framing_order.index(start)//6+1}.jpg'),'method':'浮点仿射：固定中心放大1.025倍，分别模拟源段首/中/尾；已查看原构图与终点并排图。'},native_render_qa_required=True)
  selected.append(common)
 else:
  if start==1819: reason='书法“痛快地游戏”左侧笔画原已贴边；2.5%推近会继续裁掉左侧文字，保护完整笔画，本轮不推。';category='text_crop_risk'
  elif x['track']==2: reason='采访覆盖画面较短，已有讲课/手部/身体动作或主体靠边；保留原生动作及覆盖节奏。';category='short_interview_broll'
  elif start in camera: reason='源段已有可见横移、跟随、俯仰或轻微机位变化，保留原机位运动，本轮不叠加缓推。';category='existing_source_camera_motion'
  elif start in large: reason='跑动、球类、体操、升旗或集体动作已经形成动势；保留动作完整与原有视觉节奏。';category='clear_subject_motion'
  elif start in close: reason='近景中的手部/人物动作已经可见，或构图头部、手势及教学物件接近边缘；保留动作与空间。';category='subject_action_or_tight_framing'
  else: reason='源段已有自然人物活动或画面变化，作为本轮静与动节奏的保留段；不批量追加推近。';category='keep_native_rhythm'
  common.update(reason=reason,decision='keep_unchanged',category=category)
  if start==7461: common['manual_offset_preservation']='fresh现场offset=55，按用户最新调整保留，不使用旧v8 offset=50。'
  not_selected.append(common)
protected=[];counts=collections.Counter()
for x in live['fusion']:
 tools=x.get('tools',[]);key=(x['track'],x['start'])
 animated=any(t.get('type')=='Transform' and isinstance(t.get('size'),list) and len(t['size'])>=2 and max(t['size'])-min(t['size'])>1e-6 for t in tools)
 if x['track'] in [3,4]: cat='photo_track';reason='保留双图照片已有缓推，不重复叠运动。'
 elif x['track']==1 and x['name'].startswith('双图包装'): cat='native_photo_package';reason='保留v13原生动态图板、文字、边框与照片相对关系。'
 elif animated: cat='existing_animated_transform';reason='已有Transform首中尾Size变化，保留现有运动。'
 elif any(t.get('type')=='TextPlus' for t in tools): cat='title_or_identity_comp';reason='包含开篇/校别/校长身份文字合成，本轮排除以保护文字及布局。'
 else:
  assert key in idx, key
  continue
 counts[cat]+=1;protected.append({'track':x['track'],'start':x['start'],'name':x['name'],'category':cat,'reason':reason})
assert len(selected)==27 and len(not_selected)==101 and len(protected)==110
assert len({(x['track'],x['start']) for x in selected})==len(selected)
assert all(Path(q).is_file() for x in selected for q in x['source_frame_paths'])
result={'status':'READY_FOR_NATIVE_IMPLEMENTATION','review_scope':'只读源画面运动/构图审阅；未连接或操控Resolve，未修改原素材。','snapshot_path':str(snapshot_path),'snapshot_sha256':hashlib.sha256(snapshot_path.read_bytes()).hexdigest(),'timeline':live['timeline'],'fps':25,'timeline_resolution':live['timeline_resolution'],'reviewed_source_clip_count':len(rows),'reviewed_source_frame_count':sum(len(x['samples']) for x in rows),'all_source_contact_sheets_actually_viewed':True,'source_contact_sheets':[str(p) for p in sorted(O.glob('七点源帧_*.jpg'))],'simulation_contact_sheets':[str(p) for p in sorted(O.glob('候选2.5%构图核查_*.jpg'))],'simulation_candidate_count':28,'simulation_rejected_starts':[1819],'selected_count':len(selected),'selected_start_list':chosen,'amplitude_distribution':dict(collections.Counter(str(x['amplitude']) for x in selected)),'selection_distribution':{'opening_0_to_120s':sum(x['start']<3000 for x in selected),'middle_120_to_300s':sum(3000<=x['start']<7500 for x in selected),'later_300s_onward':sum(x['start']>=7500 for x in selected)},'implementation_contract':{'transform':'仅选定源视频增加固定中心克制缓推；不改source offset、in/out、时长、轨道和同步。','curve':'1 + amplitude * (3*u*u - 2*u*u*u), u=local_frame/(duration-1)，浮点连续缓入缓出。','existing_motion':'38段已有运动、22组动态图板、44张照片缓推与6项文字身份合成均排除。','color':'保留已有曲线与二级调色。','native_qa':'实施后还需实际原生首中尾和连续帧验证；本报告不是最终渲染验收。'},'protected_counts':dict(counts),'protected':protected,'selected':selected,'not_selected':not_selected,'limitations':['源帧为已使用素材区间的7点抽帧，实际已查看15页；稀疏抽帧不能替代完整实时播放。','源代理多为平灰画面，本轮不据此改变既有调色。','2.5%终点模拟仅验证构图，不验证Resolve插值及渲染。']}
(R/'motion_candidates_v14.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print(json.dumps({'path':str(R/'motion_candidates_v14.json'),'selected_count':len(selected),'amplitudes':result['amplitude_distribution'],'distribution':result['selection_distribution'],'protected_counts':dict(counts),'not_selected':len(not_selected),'selected_start_list':chosen},ensure_ascii=False,indent=2))
