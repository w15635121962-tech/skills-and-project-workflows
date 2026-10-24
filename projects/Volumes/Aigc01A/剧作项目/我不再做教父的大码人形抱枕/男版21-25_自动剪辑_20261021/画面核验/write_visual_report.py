import json,pathlib,datetime
B=pathlib.Path(__file__).resolve().parent
sheets=json.loads((B/'contact_sheet_manifest.json').read_text());clips=[c|{'episode':s['episode'],'contact_sheet':s['contact_sheet']} for s in sheets for c in s['clips']]
N={
'男版21-1-1.mp4':('医院床边，Oliver坐椅看手机；起身伸展，随后向床边俯身。','组1主镜，承接旁白从陪床到起身。','retain_primary'),
'男版21-2-1.mp4':('Vittoria闭眼蹙眉；Oliver从床边重新坐下；她睁眼，他手边仍在床沿。','组2主镜，配合被抓住手腕/必须坐回去，不要改成起身离开。','retain_primary'),
'男版21-3-1.mp4':('Oliver床旁站起转向门，Vittoria抓住T恤下摆；尾段她从被下取出折皱纸卡。','完整保留抓衣摆的动作因果；接出示愿望卡。','retain_primary'),
'男版21-4-1.mp4':('纸卡/Oliver手持卡片/她伸卡/男主脸特写。男主出现敞开浅色衬衫外搭。','与4-2同一出示卡情节重叠；对白优先，白T连续性不足时仅择纸卡/女主镜。','overlap_select_segments'),
'男版21-4-2.mp4':('白T Oliver举ONE WISH笑脸卡；Vittoria低头；男主正脸近景。','同组补卡片和面部；不能当后续再次收卡，需与4-1择段。','overlap_select_segments'),
'男版21-5-1.mp4':('宫殿走廊童年闪回：男孩蹲写ONE WISH笑脸，起身安慰少女，举卡。','按剧本记忆段保留；男孩视觉年龄明显偏小，原文13岁存在年龄一致性风险。','retain_flashback_age_caveat'),
'男版21-6-1.mp4':('返回病房手持卡，男主床旁说话，Vittoria落泪，男主低头。男主有浅色衬衫外搭。','与6-2重复同场卡片对话构型，需按ASR分句选择；避免外搭反复消失。','overlap_select_segments'),
'男版21-6-2.mp4':('白T Oliver在病床旁握卡，Vittoria泪眼请求，切回男主握卡。','对白可用的主连续性方案；和6-1按台词互补，不两次重复请求。','overlap_select_segments'),
'男版21-7-1.mp4':('男主不回应，Vittoria伸手请求，男主说话，尾段女主独卧。','结尾请求/拒绝对话主镜；四点未捕获撕卡动作，须查完整素材或与对白计划核实。','retain_primary_check_missing_tear'),
'男版22-1-1.mp4':('男主把碎纸扔入垃圾桶，走向门口；Vittoria床上叫他，男主到门。','承接上一集撕卡结果；如EP21尾未见撕卡需父任务处置连贯。','retain_primary'),
'男版22-2-1.mp4':('Vittoria从床上奋力撑起说话，切门边男主半脸停顿。','叫住/告白主镜。','retain_primary'),
'男版22-2-2.mp4':('过男主背看Vittoria从床上俯近、抬头说话，到失落停住。','同段补女主对白角度，可能是替代/补镜；与2-1按ASR互补，不能重复台词。','overlap_dialogue_angle'),
'男版22-3-1.mp4':('门边男主侧脸，Vittoria近景后伸手急切说话，尾段男主转回。','后续请求搬去Aldwick/挽留一类主镜，确切句位由ASR决定。','retain_primary'),
'男版22-4-1.mp4':('门边男主转头，Vittoria含泪并坐起说话，切男主坚定脸。','公寓被戳穿后的对话/反应主镜。','retain_primary'),
'男版22-5-1.mp4':('男主站门口正面持续说话；随后背转开门离去；尾段留空门与病床远景。','最后劝告及真正离开主镜；保留转身与空场的终态。','retain_primary'),
'男版22-6-1.mp4':('飞机舷窗夜至晨；男主望窗，天际云层，日光照男主，末尾航机在云上。','结尾离开/新生活蒙太奇主镜，覆盖剧情完整。','retain_primary'),
'男版22-6-2.mp4':('同男主机舱望窗与窗外晨曦云层，无独立新事件。','6-1的短版/同内容补景；不要主镜后整段再重复窗景，可择机舱坐姿替换。','same_event_short_alternate'),
'男版23-1-1.mp4':('Vittoria窗边桌前查书写字，喝水，翻开的书页。','叙述高中选大学回忆起段。','retain_primary'),
'男版23-2-1.mp4':('Vittoria抱书经过走廊，看见Oliver与母亲在书房说话，门缝听话后转身离开。','偷听承诺与误会形成主镜。','retain_primary'),
'男版23-2-2.mp4':('抱书的双手慢慢收紧；门缝前女主惊愕停住。','2-1同事件情绪插入，适合放在承诺句之后/离去前，非整段再次偷听。','reaction_insert'),
'男版23-3-1.mp4':('夜晚书桌Oliver写字，Vittoria逼问，眼神极近，男主垂头。','抓腕质问起段主镜，先核对白定位。','retain_primary'),
'男版23-3-2.mp4':('Oliver疼痛蹙眉；女主抓腕/脸部，约4.7秒和尾部双眼明显发红发光。','不建议使用红眼段；3-3提供同类自然表演，应优先3-3。','reject_red_glowing_eyes'),
'男版23-3-3.mp4':('Oliver被抓腕，疼痛垂眼，女主正常眼部特写和冷淡正脸。','3-2自然眼睛替代版，优先此片；不将两段相似抓腕反应完整重复。','preferred_replacement_of_23_3_2'),
'男版23-4-1.mp4':('女主独自翻看桌上日记，页面手写I love her. Vittoria.，她神情复杂后离室。','发现日记后回避主镜。','retain_primary'),
'男版23-5-1.mp4':('夜间醉酒女主靠西装顾问，顾问询问并拿手机；女主倚靠闭眼。','醉酒顾问询问主镜，男顾问不同于白T Oliver。','retain_primary'),
'男版23-6-1.mp4':('顾问拿手机，女主抬头说话，顾问听后看向另一边，尾部汽车开走。','应把手机被压住插镜放在离去车镜之前，不能车已走再回到拦手机。','retain_primary_with_insert_before_exit'),
'男版23-6-2.mp4':('手机特写，女主纹身手按住顾问拿手机的手；切女主坚持表情。','关键按住打电话手部补镜，宜嵌6-1中，尾部重复表情按需要缩短。','action_insert_before_23_6_1_car'),
'男版24-1-1.mp4':('卧室晨光双人卧床；Vittoria闭眼，Oliver在她颈侧；她半醒，床头手机特写。','承接放纵一夜后的清晨和来电。','retain_primary'),
'男版24-2-1.mp4':('女主接电话，Oliver醒来，女主看他笑说，末段男主紧握床单。','羞辱提问/受伤反应主镜。','retain_primary'),
'男版24-2-2.mp4':('Oliver睡衣坐起僵住，垂眼，手握床单。','2-1同事件受伤反应补镜；放提问后择一完整反应，勿重复两次抓床单。','reaction_insert'),
'男版24-3-1.mp4':('女主放下手机看Oliver，Oliver扣好睡衣，女主近景困惑。','没有复仇快感的反应接续。','retain_primary'),
'男版24-4-1.mp4':('女主与女性朋友聚会/夜景露台；女主笑；之后回现代套房坐着倦怠。','回忆其他恋人/当下失去兴趣蒙太奇，按旁白时间可压短。','retain_montage'),
'男版24-5-1.mp4':('金发耳饰男Evan穿黑三件套在床边整理领带，冷笑说话，切女主反应。','Evan与Oliver外貌衣服明显不同，保留驱逐对峙。','retain_primary'),
'男版24-6-1.mp4':('Evan正面长对白，双人床边全景，尾段女主一人套房远景。','长控诉主镜；6-2现金离开动作应插尾段独处远景之前。','retain_primary'),
'男版24-6-2.mp4':('女主冷硬/蹙眉反应，Evan手持现金转身出门。','现金离开为独立有用动作，不应只当替代版丢弃；嵌6-1长对白后/空床广角前。','action_insert_before_empty_room'),
'男版4-7-1.mp4':('同女主黑袍在同现代套房，坐床沿手按胸，近景落泪，窗边蜷坐。','目录EP24且人物/袍装/床房天际线承接24-6，判为错命名24-7-1，保留作反省段。','accept_as_episode24_group7_1'),
'男版24-7-2.mp4':('女主近景咬唇，转身蜷坐窗边；中途眼周突显红斑。','与7-1最后哭泣/窗边动作重叠，优先7-1，按旁白必要取正常脸/背影；避免突兀红斑。','same_event_short_alternate_artifact_caveat'),
'男版25-1-1.mp4':('女主在飞机上失眠，手攥扶手，窗外降落地景，落地后站英国街角。','找Oliver开场主镜。','retain_primary'),
'男版25-2-1.mp4':('远处Oliver与女孩同行，女主街角看见，握衣服，近景眼红欲哭。','远处见到他人与自己克制反应主镜。','retain_primary'),
'男版25-2-2.mp4':('纹身手紧攥衣服，女主一侧脸前景，背景Oliver和女孩。','2-1攥衣补细节，反应关系清楚，可用但不重复攥衣起势。','reaction_insert'),
'男版25-3-1.mp4':('女主街角朝Oliver方向迈步，脚步停在转角，抬手却停住，切脚部。','想冲过去但不能的中间动作主镜。','retain_primary'),
'男版25-4-1.mp4':('Oliver捧花笑，女主脸迎强日光，随后退到砖墙后窥望。约5.0s一只眼出现极亮金色反光。','此片承担发现笑容/退缩的因果；金亮眼镜头疑生成异常，可选10s后正常脸或4-2替代。','retain_primary_eye_highlight_caveat'),
'男版25-4-2.mp4':('女主贴砖墙抬头失落，远景Oliver与女孩站在对街。','4-1的同事件短反应/对视对象补镜；可替换异常眼段，勿把退墙动作重新做一次。','reaction_alternate'),
'男版25-5-1.mp4':('年轻Oliver阳光下微笑，切女主站街角由傍晚入夜、最后离开空街。','过去也曾灿烂笑容与不敢打扰的等待蒙太奇。','retain_montage'),
'男版25-6-1.mp4':('女主进入隔壁空公寓，手贴共享墙，独自躺床贴墙闭眼。','买邻居公寓/隔墙睡关键动作主镜。','retain_primary'),
'男版25-7-1.mp4':('深夜豪宅办公室女主独坐，桌上手机，抬头担忧。','得知Oliver夜不归宿后回Veriston场景。','retain_primary'),
'男版25-8-1.mp4':('同办公室长桌广角，她撑桌、手攥紧，面部痛楚。','猜忌对方是否与别人上床的内心反应，配旁白。','retain_primary'),
'男版25-9-1.mp4':('女主惊觉眼神，泪眼双手捧脸，最终开门离开办公室。','意识到Oliver以前同样痛苦，出办公室接旧卧室。','retain_primary'),
'男版25-10-1.mp4':('旧卧室桌面/女主手，拿杯服药，拉被躺床闭眼。','第一次睡眠药入梦，后续不能先到医院。','retain_primary'),
'男版25-11-1.mp4':('金色梦境年轻Oliver仰望微笑说话，女主伸手，末切暗处泪眼醒来。','梦境求学对白必须保留实际同期声，梦醒切回现实。','retain_dream_dialogue'),
'男版25-12-1.mp4':('女主床上惊醒、按头，手握药瓶/药片，手无力垂落；11.875s起黑场到末。','剧情服药再次入梦；删画面黑尾11.875–13.0s，保留前段可见行动，音频需父任务核对再裁。','trim_black_tail'),
'男版25-13-1.mp4':('女主病容闭眼，病房中Oliver拿纸卡，女主醒着看他；尾部视线朝空门。','医院醒来/他走开主镜，13-2撕卡插镜应在空门之前。','retain_primary'),
'男版25-13-2.mp4':('Oliver病床旁看卡，然后双手将ONE WISH纸卡撕碎。','明确撕卡动作补镜，必须按剧情嵌入13-1，非可直接丢弃的重复版。','essential_tear_insert'),
'男版25-14-1.mp4':('女主医院含泪近景，输液手，侧面落泪闭眼，最后空旷病房大远景。','全剧失去爱情/无尽失眠结尾，适合作旁白收尾。','retain_ending')}
assert len(N)==54,len(N)
cut={x['filename']:x for x in json.loads((B/'source_cut_and_black_candidates.json').read_text())}
for c in clips:
 desc,note,kind=N[c['filename']];c['observed_visual_sequence']=desc;c['editorial_recommendation']=note;c['classification']=kind;c['scene_change_candidates_seconds']=cut[c['filename']]['scene_change_candidate_seconds'];c['black_intervals']=cut[c['filename']]['black_intervals'];c['inspection_basis']='Actual view_image inspection of four stills per clip at begin, 1/3, 2/3, tail; scene/black detection only for candidate timing. No full-motion or audio listening claim.'
R={'checked_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),'scope':'male only EP21-25 all54 source videos','source_videos_modified':False,'resolve_or_ui_operated':False,'clips_inspected_count':54,'still_frames_inspected_count':216,'contact_sheets_inspected_count':12,'full_playback_performed':False,'dialogue_listening_performed':False,'time_boundary_caveat':'4 still samples establish visible event sequence; source cut timestamps are ffmpeg candidates, not final editorial in/out. Final dialogue boundaries require ASR/listening by parent.','high_priority_findings':['23-3-2 red glowing eyes; prefer23-3-3 natural-eye replacement.','EP24/男版4-7-1.mp4 belongs24 group7 by scene/content.','25-12-1 black tail11.875–13.000s; trim visible pictureout<=11.875.','25-13-2 is essential wish-card tear insert, not disposable duplicate.','24-6-2 cash-taking/exit insert should precede24-6-1 empty room tail.','23-6-2 hand stops phone insert should precede23-6-1 car exit.','21-4 and21-6 variants have shirt continuity differences; do not concatenate full alternates blindly.'],'clips':clips}
(B/'54片画面核验与同组版本判定.json').write_text(json.dumps(R,ensure_ascii=False,indent=2))
lines=['# 男版21–25集54片画面核验','', '已实际查看12张接触表，共216个关键帧；没有声称完成逐秒播放或同期声听辨。每片四点为开头、1/3、2/3、尾段。裁切候选须结合父任务ASR/对白后定稿。','', '末尾数字不能统一视为替代版：既有相同事件补角度，也有必需的新动作；以下按可见内容判定。','']
for ep in range(21,26):
 lines.extend([f'## EP{ep}',''])
 for c in [x for x in clips if x['episode']==ep]:
  lines.extend([f'**{c["filename"]}**（{c["duration_seconds"]:.3f}秒）',f'- 关键帧时间：'+', '.join(f'{x["time_seconds"]:.3f}s' for x in c['frames']),f'- 可见内容：{c["observed_visual_sequence"]}',f'- 剪辑建议：{c["editorial_recommendation"]}',f'- 源内切点候选：'+', '.join(str(x) for x in c['scene_change_candidates_seconds']),''])
(B/'54片画面核验与同组版本判定.md').write_text('\n'.join(lines))
print('54 written')
