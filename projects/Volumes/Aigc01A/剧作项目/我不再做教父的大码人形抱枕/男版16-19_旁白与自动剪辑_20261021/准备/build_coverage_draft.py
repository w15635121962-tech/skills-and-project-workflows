from pathlib import Path
import json
BASE=Path(__file__).resolve().parent
TASK=BASE.parent
inv=json.loads((BASE/'media_inventory.json').read_text(encoding='utf-8'))
cut=json.loads((TASK/'画面核验/源视频切点候选.json').read_text(encoding='utf-8'))
asr=json.loads((TASK/'ASR/同期对白与音轨候选.json').read_text(encoding='utf-8'))
byname={r['filename']:r for e in inv['episodes'] for r in e['videos']}
cutby={r['filename']:r for r in cut['files']}
asrby={r['filename']:r for r in asr['files']}
# Source paragraph ranges were compared with the four-frame-per-video contact
# sheets, never fed to ASR. These are coverage candidates, not final edit times.
groups=[
 (16,1,[451,455],'到Aldwick租房、整理玩偶与小床','男版16-1-1.mp4',[], '旁白全新生活起段；按租房→布置→小床终态顺序，不提前露出瘦身终态。'),
 (16,2,[456,458],'花店买花、独居自由','男版16-2-1.mp4',[], '接实验室/回家顺路花店；花束动作连续。'),
 (16,3,[459,461],'运动和体重变化、镜中瘦身','男版16-3-1.mp4',[], '原片跑步胖→瘦、洗漱镜中瘦身；这是剧情要求的时间变化，不能误当资产不一致剪掉。逐切中点已确认游泳[58,90)与饮食[90,120)帧，后段[177,385)为瘦身后镜中脸和下颌；四时刻抽样曾漏见，现更正。'),
 (16,4,[462,464],'找到旧日记、密码锁、坐地翻阅','男版16-4-1.mp4',[], '取箱→日记→翻页，和后续撕页衔接。'),
 (16,5,[465,468],'日记提Vittoria、撕页、感受已淡','男版16-5-1.mp4',[], '近景/全景再到撕裂页，保持纸张归属。'),
 (16,6,[469,469],'合上日记、密码归零、上楼收存','男版16-6-1.mp4',['男版16-8-1.mp4'], '16-8-1也是日记+密码锁补充覆盖，不是新的剧情；可选锁特写替换6中同一动作，勿重复合本/拨锁。'),
 (16,7,[470,472],'新朋友、新爱好、换手机号、没有被寻找','男版16-7-1.mp4',[], '朋友聊天→阳台花→新手机/远望。原稿最后推测Evan治好失眠仅旁白承载，不能凭空加入女版床戏。'),
 (17,1,[475,478],'房东聊天、隔壁卖出、神秘邻居','男版17-1-1.mp4',['男版17-1-2.mp4'], '17-1-2为房东脸+楼阳台补充，替换/插入局部即可；避免聊天结束再重启同次招呼。'),
 (17,2,[479,481],'阳台每日鲜花、口味相同','男版17-2-1.mp4',[], '主角端杯看花，按早晨闻香展开。'),
 (17,3,[482,484],'邻居常不在、暗屋和每日花束','男版17-3-1.mp4',[], '日夜与花束蒙太奇，过渡到新朋友。'),
 (17,4,[485,487],'认识研究生、猫咖、离店她叫住他','男版17-4-1.mp4',['男版17-4-2.mp4'], '17-4-2为同场女学生羞怯+路灯下回身补镜，可为邀请前铺垫，不能两次离店/回头循环。'),
 (17,5,[488,490],'女生猫后空翻邀请、羞红、男主接受','男版17-5-1.mp4',[], '原声对白约0.94–11.46秒，中间含表演停顿；必须给对白独立空档；旁白17-05-01跨此处，需要在句边拆旁白。后段羞怯笑、男主接受可供旁白489–490覆盖。'),
 (17,6,None,'对面窗帘后窥视/手抓帘的悬念补镜','男版17-6-1.mp4',['男版17-6-2.mp4'], '原稿EP17没有新增这段明确台词；仅少量视觉悬念过桥或不选，不新增旁白解释人物身份。两版同一动作选一。'),
 (18,1,[493,495],'邻居消失、花逐渐枯萎','男版18-1-1.mp4',[], '阳台新鲜→枯花、落叶可承载七天跨度。'),
 (18,2,[496,498],'开会时陌生短信、放下手机','男版18-2-1.mp4',['男版18-2-3.mp4'], '两版均会议→手机提醒→主角搁置，不是连续两次提醒。缺-2文件名不证明缺剧情。2-1手机一度屏幕朝上/朝下改变，2-3倒扣手机蓝光提醒较连贯，可选2-3整体。短信Mr. Carter是文字，不据低置信嗯声假造可辨对白。'),
 (18,3,[499,505],'好友申请、母亲头像、惊讶与旧事浮现','男版18-3-3.mp4',['男版18-3-1.mp4','男版18-3-2.mp4','男版18-3-4.mp4','男版18-3-5.mp4','男版18-3-6.mp4'], '3-1与3-3为同一厨房惊讶情节重做版，勿顺拼两个完整版本；3-4手拿手机为起段插入，3-2/3-5完全相同SHA256，最多选一次；3-6头像更清楚，可替换重复头像镜。'),
 (18,4,[506,509],'母亲迅速回复、要求回Veriston','男版18-4-3.mp4',['男版18-4-1.mp4','男版18-4-2.mp4','男版18-4-4.mp4','男版18-4-5.mp4'], '4-1与4-3同为厨房回忆/看手机重做，4-2与4-4完全同文件，最多一次；4-2手机输入可补接受请求。文字内容需单独画面辨读，不把ASR的baby套话当台词。'),
 (18,5,[510,511],'疑惑、想起顶尖医疗资源','男版18-5-1.mp4',[], '医书/疑惑/短暂思考与旁白匹配。'),
 (18,6,[512,518],'礼貌回复、回想恩情与誓言、再次询问病情','男版18-6-3.mp4',['男版18-6-1.mp4','男版18-6-2.mp4','男版18-6-4.mp4','男版18-6-5.mp4'], '6-1与6-2视觉切点几乎一致且动作相同；6-3同剧情另一重做；仅选一主版，再按需6-4输入/6-5反应。原文短信不得另配叙述者声音。'),
 (18,7,[519,519],'收到医生无能为力、需要你回来的请求','男版18-7-2.mp4',['男版18-7-1.mp4'], '同一惊讶→窗边沉思重做，选一；两版都有从看手机跳至窗边，不顺拼重复动作。'),
 (19,1,[522,524],'护士领路、电梯、Oliver问病情','男版19-1-1.mp4',[], '原声What happened to her约7.16–8.08秒；旁白先覆盖带路，再留问句。'),
 (19,2,[525,530],'护士低声解释、两句议论、走到病房','男版19-2-1.mp4',['男版19-2-2.mp4'], '2-2只重复护士第一句，没有后两句，适合作第一句的替换特写。2-1必须保留7.54–9.74和10.76–11.86秒后两句，否则原稿缺台词。旁白529–530应在护士对白后。'),
 (19,3,[531,533],'门缝听母亲贬低他、Vittoria沉默','男版19-3-2.mp4',['男版19-3-1.mp4'], '两版说同一整段贬低对白，不可重复。3-1开头有拉把手/露缝和后段Oliver反应，3-2主体母亲与病床、插Oliver闭眼反应；当前原稿此时门是微开，正式推门在536，避免提前剪成完全进入。'),
 (19,4,[535,536],'母亲不耐烦、Oliver推门','男版19-4-2.mp4',['男版19-4-1.mp4','男版19-4-3.mp4'], '4-2原声母亲完整两句0.9–4.74秒，后接4-3推门；4-1可替换含前段病床+门外Oliver，不能把母亲话和推门重复两遍。'),
 (19,5,[537,540],'入病房、众人抬眼、Vittoria打量瘦身后的他','男版19-5-1.mp4',[], '背影进门→床/母亲关系→腰肩身体细节→脸，结束在被认不出的目光与主角稳定站姿。')]
episodes=[]
for ep in range(16,20):
    gs=[]
    for e,g,pars,content,primary,alts,note in groups:
        if e!=ep:continue
        candidates=[]
        for name in [primary]+alts:
            r=byname[name];cs=cutby[name]
            candidates.append({'filename':name,'path':r['path'],'source_fps':24,'source_in_frame':0,'source_out_frame_exclusive':cs['video_frames'],
                'source_in_seconds':0,'source_out_seconds':cs['video_duration_seconds'],'visual_role':'main_candidate' if name==primary else 'alternative_or_insert_not_append_all',
                'scene_cut_frames_candidates':cs['cut_frames_candidates'],'dialogue_ranges':asrby[name]['source_range_candidates']})
        gs.append({'episode':ep,'source_group':g,'source_docx_paragraph_range':pars,'coverage':content,'editing_note':note,'source_candidates':candidates,'final_record_time':None})
    episodes.append({'episode':ep,'source_script_episode':ep,'version':'male_gender_swap','groups':gs})
out={'status':'SOURCE_COVERAGE_DRAFT_NOT_EXECUTABLE_FINAL_EDIT_PLAN','new_narration_audio_available':False,
    'scope':'男版EP16–19，现有源片与原英文段落的对应，不生成/修改源内容，不操作Resolve。',
    'evidence':{'source_video_count':48,'contact_sheets_reviewed':11,'sampled_frames_reviewed':192,'cut_point_candidates':cut['shot_candidates'],'scene_midpoint_images_extracted':cut['shot_candidates'],
        'review_method':'本任务实际查看11张接触图，每片开头/1/3/2/3/尾四帧；225逐切中点已提取但不宣称全部逐帧播放验收。','blind_asr_completed':48,'blind_asr_errors':0,'human_audio_listening_validated':False,
        'transcript_index':str(TASK/'ASR/转录索引.json'),'sync_candidate_audit':str(TASK/'ASR/同期对白与音轨候选.json'),'source_cuts':str(TASK/'画面核验/源视频切点候选.json'),'contacts':str(TASK/'画面核验/contact_sheet_manifest.json')},
    'global_edit_rules':['依男版原文同集序，绝不复用女版集数偏移和人物。','所有选用画面必须附同源、同入出边界的嵌入同期声并链接；旁白100%，素材100%。','同组重做/补特写按动作连续选择，不把全部文件机械顺拼。','旁白段跨引号对白时，按旁白句边拆开，给原声对白/屏幕文字独立空间。','原片环境声/猫叫/衣料/短信声保留，可为旁白做音量避让；低置信ASR循环套话不得成为新台词/字幕。','新旁白生成后重做其逐词实测和响度、按实测长度填写最终record位置；本文不提供伪精确最终时码。'],
    'exact_duplicate_files':asr['exact_duplicate_files'],'episodes':episodes,
    'pending':['等新旁白27段实际下载与逐项改名、内容/原速核验后确定最终时间线。','需实际听辨原片环境音及对白剪点、混音峰值，当前只有ASR/能量/静帧证据。','EP18短信手机文字部分为生成字形，未逐字确认六条原文全部清楚可读；如缺文字，只可标待补，不擅自合成旁白冒充。','EP16-3-1逐切核验已补确认游泳与饮食镜，剪辑时纳入旁白对应。']}
(BASE/'同期对白_画面覆盖与源范围草案.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md=['男版EP16–19源素材覆盖核验（离线准备，尚非最终剪辑）','',
 '48段盲ASR完成，逐源词时码/SRT已落盘；11张接触图共192抽样帧已查看。225段源镜候选及中点图片已提取，未宣称完整播放/人工听验。','',
 'EP18-2缺号结论：2-1和2-3都表现同一会议室手机提醒后放下，属于重做候选。没有证据证明缺-2导致剧情断档；选择一个版本承载P496–498即可。','',
 'SHA256完全重复：18-3-2=18-3-5；18-4-2=18-4-4。另18-6-1/6-2切点与动作近同，均作为替代版处理。','',
 '对白候选仅8个源文件，含重复表演版；主要是17-5-1邀请、19-1-1问句、19-2-1三句护士对话、19-3母亲贬低、19-4母亲不耐烦。其他40源的低置信循环套话/非语言声不认可为对白；同期环境音仍必须随画面同剪。','',
 '19-2-2只含护士第一句，不能用它替换整个19-2-1而漏掉后两句。17-05-01旁白跨邀请，需要在原文句边拆开留对白空档。EP18为文字消息，不擅自给叙述者补读。','']
for ep in episodes:
    md.extend([f"EP{ep['episode']}",''])
    for g in ep['groups']:md.append(f"- 组{g['source_group']}：{g['coverage']}。{g['editing_note']}")
    md.append('')
md.extend(['后续：27段新旁白到位后逐词实测，建立同源AV链接/原速旁白最终剪辑计划；当前未改Resolve、未导入或生成视频。'])
(TASK/'画面核验/男版16-19_覆盖与版本核验.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print(json.dumps({'plan':str(BASE/'同期对白_画面覆盖与源范围草案.json'),'report':str(TASK/'画面核验/男版16-19_覆盖与版本核验.md'),'groups':sum(len(e['groups']) for e in episodes)},ensure_ascii=False))
