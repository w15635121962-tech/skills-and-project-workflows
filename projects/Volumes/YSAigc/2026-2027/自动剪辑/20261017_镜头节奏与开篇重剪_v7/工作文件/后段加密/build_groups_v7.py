import json,math,copy,subprocess,io,concurrent.futures,statistics
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
W=Path(__file__).parent
BASE=json.loads((W.parent/'base_plan_v6.json').read_text())
OLD={x['record_frame']:x for x in BASE['shots']}
CAT=json.loads(Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_学校粗剪/工作文件/footage.json').read_text())
SENT=json.loads(Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_旁白精修/工作文件/narration_aligned.json').read_text())['sentences']
def resolve(prefix):
 m=[x for x in CAT if x['key'].startswith(prefix+'_')]
 assert len(m)==1,(prefix,len(m))
 return m[0]
GROUPS=[]
def group(old_records,spec,reason):
 old=[OLD[x] for x in old_records];start=old[0]['record_frame'];length=sum(x['length_frames'] for x in old)
 assert all(a['record_frame']+a['length_frames']==b['record_frame'] for a,b in zip(old,old[1:]))
 g={'id':'tail_%05d'%start,'old_record_frames':old_records,'record_frame':start,'length_frames':length,'reason':reason,'segments':[]}
 at=start
 for src,src_in,n,intent in spec:
  template=next((x for x in old if x['record_frame']<=at<x['record_frame']+x['length_frames']),old[0]);x=copy.deepcopy(template)
  for k in ['source_start_frame','source_count_frames','in_requested','source_out_exclusive','revision_v4','revision_v5','revision_v6','title']:
   x.pop(k,None)
  if isinstance(src,int):
   origin=OLD[src];x.update({k:copy.deepcopy(origin.get(k)) for k in ['path','name','fps','is_photo','asset_id','log','source_photo','resolution']});x['derived_from_old_record_frame']=src
  else:
   z=resolve(src);x.update(path=z['path'],name=z['name'],fps=z['fps'],is_photo=False,asset_id=None,log=True,source_photo=None,resolution=[z['video']['width'],z['video']['height']]);x['new_source_key']=z['key']
  x.update(record_frame=at,length_frames=n,speed=1,intent=intent,revision_v7=True,picture_only=True,source_audio_import=False)
  x['in']=round(src_in*x['fps'])/x['fps'];x['out']=x['in']+n/25
  x.update(source_start_frame=round(x['in']*x['fps']),source_count_frames=round(n/25*x['fps']),source_out_exclusive=x['out'],in_requested=src_in)
  overlaps=[s for s in SENT if s['start']<(at+n)/25 and s['end']>at/25]
  x['narration_sentence_ids']=[s['id'] for s in overlaps];x['narration_excerpt']=' '.join(s['text'] for s in overlaps)
  x['title']=None;x['evidence']={'first_middle_last_viewed':False}
  g['segments'].append(x);at+=n
 assert at==start+length,(start,at,length)
 GROUPS.append(g)
group([6982],[(6982,0,54,'历史毕业合影保留2.16秒，明确学子从这里启航的真实档案证据。'),('006_C0281',5,50,'切到当下学生翻阅学习材料的自然近景，连接逐梦远方；不标为历史影像。')],'毕业档案到当下学生，去掉长静照停留。')
group([7086],[(7086,0,65,'科技成果档案保留2.60秒，奖项证据完整可辨。'),('005_20260921_D0500',2,60,'真实工程课教师指向小车项目，呈现持续育人的行动；不将课堂冒充该奖项现场。')],'成果证据后接真实课程，避免照片停满5秒。')
group([7211,7304],[(7211,1,67,'保留师生制作传统手工的动作，承接特色兴校。'),('006_C0290',4,67,'改用自然听课的学生反应，不沿用原直视镜头摆拍笑脸。'),('007_C0110',2,68,'典礼现场学生真实鼓掌，给奋斗成就辉煌一个有动作的落点。')],'两条长镜重排为手工、学生反应、真实鼓掌三镜。')
group([7413],[(7413,7,48,'教师持书讲解，保留强师兴教的主体。'),('006_C0272',2,48,'自然侧目看老师的学生近景，形成教师与学生的回应关系。')],'教师到学习反应，避免单一讲台镜头过长。')
group([7509],[(7509,0,55,'师徒结对档案保留2.20秒，作为教师成长平台的证据。'),('006_C0182',2,46,'真实教师俯身指导学生，回到名师引领服务学生的行动。')],'师资档案与指导实景相接。')
group([7610],[(7610,1,59,'真实教师讲解的手势段。'),('006_C0273',3,59,'学生举手参与课堂，用主动学习回应教师成长。')],'老师讲解接学生举手，替代4.72秒单一讲台。')
group([7728],[(7728,0,60,'专题研讨档案保留2.40秒，青年教师精进证据不删。'),('006_C0254',2,52,'老师在小组中指导，学生围桌回应；只描述日常教学实践。')],'研讨证据后回到师生实践，减小静照停顿。')
group([7840,7935],[(7840,1,62,'教师面向学生讲解，保留原学科现场。'),('006_C0223',8,63,'学生笔尖书写近景，补充学与教的细节层次。'),(7935,10,62,'另一位教师自然讲解和手势，回应有情怀有专业有担当。')],'两条连续讲台长镜重排为教师、笔尖、教师三层景别。')
group([8027,8132],[(8027,12,48,'工程课学生协作装配，保留真实课程操作。'),('004_A001C230',2,48,'不同机位的结构件与手部连接细节。'),(8132,20,48,'保留学生互相传递展示条目的动作，不引入未核实的学科标签；避开原8秒处弯腰捡纸。'),('006_C0242',8,49,'同次展示的近景，学生伸手整理展示条目。')],'课程总景和动作细节交替，193帧由两镜变四镜。')
group([8396,8473],[(8396,0,56,'工笔画师生辅导档案保留2.24秒，完整衔接外语段后的体艺浸润。'),(8473,1,55,'陶塑课程工具与指尖操作，保留真实质感。'),('005_20260921_D0578',2,56,'另一机位的陶塑线条与工具细节，近景补触觉动作。')],'保留艺术资料证据，用两条不同陶塑视角减小停顿；8332英语节不动。')
group([8563,8655],[(8563,10,51,'老师举起手工作品讲解的自然动作。'),('004_A001C325',1,51,'作品被双手转动的细节，展示结构与颜色。'),(8655,10,51,'学生动手拼装的原近景。'),('004_A001C322',1,52,'老师在另一位学生身旁指导，形成讲解、作品、操作、关怀四镜。')],'205帧由两条长镜改为四条真实不同机位，不靠数字裁切。')
group([8768],[(8768,4,51,'真实优秀集体表彰全景，荣誉事件保留。'),('007_C0066',2,51,'同次表彰中向学生颁发奖杯的真实动作，避开C0069横移段的运动模糊。')],'同一真实荣誉事件的全景与颁奖动作。')
group([8997],[(8997,4,48,'典礼来宾席人物保留，避免擅自给人物新增身份。'),('007_C0035',5,47,'同类典礼现场广角，交代学校与各方共同参与。')],'保留领导关怀语义，以现场全景避免人物长停。')
group([9243],[(9243,14,67,'学生从书本抬头的自然学习动作。'),('006_C0296',5,68,'阳光下学生队伍跑步，回应锐意进取和不断努力，不改旁白。')],'学习到体育行动，打破5.4秒低头连续。')
group([9530],[(9530,3,49,'保留原文汇中学教育集团校门与校牌。'),('002_A002C005',2,48,'校内激情智慧创新文化墙，与校门建立内外关系；不冒称另一校区。')],'校门长镜缩短，接校内文化墙，避免两条校门近似角度。')
group([9627],[(9627,1,63,'真实课堂师生全景，保留办学语境。'),('006_C0177',2,62,'不同机位学生边看边记的近景，落在教育生态中的学习者。')],'教室全景到学生动作，5秒变两镜。')
group([9752],[(9752,1,54,'老师与学生交流的原侧近景。'),('006_C0268',2,54,'学生在黑板前书写与解释，展示被支持后的主动表达。')],'教师关怀接学生自主表达，4.32秒变两镜。')
group([9860],[(9860,6,50,'古树庭院保留2秒，为深耕教育沃土留出短暂呼吸。'),('005_20260921_D0499',2,50,'工程课教师微笑俯身指导，返回人文关怀和创新课堂。')],'静态庭院缩短，接真实师生动作。')
group([9960],[(9960,0,50,'科学探究档案保留2秒，照片证据本身不重标学校。'),('005_20260921_D0502',2,46,'当下工程课堂教师观察学生制作，体现创新办学的持续行动。')],'科创档案后接教学动作，不以课堂替代获奖证据。')
group([10056],[(10056,1,53,'小学课堂真实全景，保留贯通的学段关系。'),('005_20260921_D0434',2,53,'小学音乐课真实琴键和演奏手部，体现融合育人，非空镜。')],'小学课堂与艺术动作相接，减少4.24秒同机位。')
group([10247],[(10247,45,63,'校园和城市楼宇同框，保留立足东城的真实空间。'),('002_A002C010',2,62,'同一中学校舍立面书法与入口的下移取景，增加建筑层次。')],'城市空间到校园文化近景，5秒变两种空间尺度。')
group([10372],[(10372,0,60,'家校同台档案保留2.40秒，原文件明确学生与母亲，不删去家校真实证据。'),('007_C0084',3,60,'典礼现场参与者的自然表情反应；缺少校方身份注释，不标为家长、老师、领导或母女，也不声称与档案为同一天。')],'家校证据照后接身份未标注的典礼参与者，缩短4.8秒照片；家长关系仅由原P25档案证明。')
group([10492],[(10492,5,65,'保留真实师生集体面孔2.60秒，减少长时间合影停留。'),('007_C0111',2,65,'学生在典礼现场鼓掌的自然近景，为贡献文汇力量给出动作回应。')],'原5.2秒合影式镜头缩短，落在真实学生动作上。')
replaced={r for g in GROUPS for r in g['old_record_frames']}
retained=[s for s in BASE['shots'] if s['record_frame'] not in replaced]+BASE.get('interview_overlays_v6',[])
segments=[s for g in GROUPS for s in g['segments']]
conflicts=[];inherited=[]
for s in segments:
 for old in retained:
  if s['path']==old['path'] and max(s['in'],old['in'])<min(s['out'],old['out'])-1e-7:
   row={'new_record_frame':s['record_frame'],'old_record_frame':old['record_frame'],'path':s['path'],'new_source':[s['in'],s['out']],'old_source':[old['in'],old['out']]}
   if s['is_photo'] and 'derived_from_old_record_frame' in s:inherited.append(row)
   else:conflicts.append(row)
for i,a in enumerate(segments):
 for b in segments[i+1:]:
  if not a['is_photo'] and a['path']==b['path'] and max(a['in'],b['in'])<min(a['out'],b['out'])-1e-7:conflicts.append({'new_records':[a['record_frame'],b['record_frame']],'path':a['path']})
assert not conflicts,conflicts
full=sorted([s for s in BASE['shots'] if s['record_frame'] not in replaced]+segments,key=lambda s:s['record_frame'])
assert all(a['record_frame']+a['length_frames']==b['record_frame'] for a,b in zip(full,full[1:]))
assert full[-1]['record_frame']+full[-1]['length_frames']==BASE['duration_frames']
span_before=[s for s in BASE['shots'] if 6909<=s['record_frame']<10850];span_after=[s for s in full if 6909<=s['record_frame']<10850]
report={'groups':len(GROUPS),'old_replaced':len(replaced),'new_segments':len(segments),'added_shots':len(segments)-len(replaced),'span_old_shots':len(span_before),'span_new_shots':len(span_after),'span_frames':10850-6909,'span_seconds':(10850-6909)/25,'span_before_over_3_15':sum(s['length_frames']>78.75 for s in span_before),'span_after_over_3_15':sum(s['length_frames']>78.75 for s in span_after),'new_duration_min_seconds':min(s['length_frames'] for s in segments)/25,'new_duration_max_seconds':max(s['length_frames'] for s in segments)/25,'new_shot_median_seconds':statistics.median(s['length_frames']/25 for s in segments),'new_source_conflicts':conflicts,'inherited_photo_reuse':inherited,'audio_unchanged':True,'english_f8332_unchanged':OLD[8332]==next(x for x in full if x['record_frame']==8332),'scope_end_10850_preserved':all(x in full for x in BASE['shots'] if x['record_frame']>=10850),'full_duration_frames':BASE['duration_frames']}
(W/'groups_v7.json').write_text(json.dumps(GROUPS,ensure_ascii=False,indent=2))
(W/'plan_validation_v7.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
