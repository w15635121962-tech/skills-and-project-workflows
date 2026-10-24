import json,copy,subprocess,concurrent.futures,io
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
W=Path(__file__).parent
BASE=json.loads((W.parent/'base_plan_v7.json').read_text());OLD={x['record_frame']:x for x in BASE['shots']}
CAT=json.loads(Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_学校粗剪/工作文件/footage.json').read_text())
SPECS=[(7036,'006_C0246',2.0,'学生用手指固定展示线和条目的真实操作近景，替换原低头几乎不变的阅读近景，承接学子启航；不冒称毕业档案。'),(7278,'006_C0239',2.0,'两名学生边看材料边交流的自然双人近景，替换单人静态听课反应，呼应质量立校和学习合作。'),(10432,'007_C0085',3.0,'典礼现场人物持麦自然发言和表情变化，替换静候反应；人物身份未有校方材料证实，不标为家长、老师、领导或母女，保留前条P25家校实证。'),(10492,'007_C0114',8.0,'学生走跑队伍的真实脚步和操场线条近景，替换合影式直视镜头群像，承接持续贡献文汇力量；无源音频。'),(10782,'007_C0115',3.0,'学生在阳光下自然慢跑向前的中景，替换直视镜头笑脸，以真实步伐承接创造更美好的未来，旁白字尾完整保留。')]
REPS=[];probes={}
for record,prefix,start,intent in SPECS:
 matches=[x for x in CAT if x['key'].startswith(prefix+'_')];assert len(matches)==1,prefix
 z=matches[0];old=OLD[record];s=copy.deepcopy(old)
 for k in ['evidence','derived_from_old_record_frame','new_source_key','source_start_frame','source_count_frames','source_out_exclusive','in_requested']:
  s.pop(k,None)
 s.update(path=z['path'],name=z['name'],fps=z['fps'],resolution=[z['video']['width'],z['video']['height']],is_photo=False,asset_id=None,source_photo=None,log=True,title=None,speed=1,revision_v8=True,picture_only=True,source_audio_import=False,intent=intent,previous_v7_path=old['path'],previous_v7_source_in=old['in'],new_source_key=z['key'])
 s['in']=round(start*s['fps'])/s['fps'];s['out']=s['in']+s['length_frames']/25;s['source_start_frame']=round(s['in']*s['fps']);s['source_count_frames']=round(s['length_frames']/25*s['fps']);s['source_out_exclusive']=s['out'];s['in_requested']=start
 assert s['record_frame']==old['record_frame'] and s['length_frames']==old['length_frames']
 probes[s['path']]=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',s['path']]))
 v=next(v for v in probes[s['path']]['streams'] if v['codec_type']=='video');assert s['out']<=float(v.get('duration',probes[s['path']]['format']['duration']))
 REPS.append(s)
replace_records={s['record_frame'] for s in REPS};retained=[s for s in BASE['shots'] if s['record_frame'] not in replace_records]+BASE['interview_overlays_v7']
conflicts=[]
for s in REPS:
 for o in retained:
  if s['path']==o['path'] and max(s['in'],o['in'])<min(s['out'],o['out'])-1e-7:conflicts.append({'new_record_frame':s['record_frame'],'old_record_frame':o['record_frame'],'path':s['path']})
for i,s in enumerate(REPS):
 for o in REPS[i+1:]:
  if s['path']==o['path'] and max(s['in'],o['in'])<min(s['out'],o['out'])-1e-7:conflicts.append({'new_records':[s['record_frame'],o['record_frame']],'path':s['path']})
assert not conflicts,conflicts
FONT=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
def evidence(s):
 n=s['source_count_frames'];fr=[s['source_start_frame'],s['source_start_frame']+(n-1)//2,s['source_start_frame']+n-1];times=[f/s['fps'] for f in fr];paths=[]
 row=Image.new('RGB',(1080,230),'white');d=ImageDraw.Draw(row)
 for i,t in enumerate(times):
  b=subprocess.check_output(['ffmpeg','-v','error','-ss',str(t),'-i',s['path'],'-frames:v','1','-vf','scale=360:203','-f','image2pipe','-vcodec','mjpeg','-threads','1','-']);assert b
  im=Image.open(io.BytesIO(b)).convert('RGB');q=W/('final_%05d_%.3fs.jpg'%(s['record_frame'],t));im.save(q,quality=94);paths.append(str(q));row.paste(im,(i*360,0));d.text((i*360+3,205),'F%d %s @%.2fs'%(s['record_frame'],Path(s['path']).name[:24],t),font=FONT,fill='black')
 s['evidence']={'first_middle_last_viewed':False,'source_times_seconds':times,'source_frames':fr,'frames':paths,'probe_verified':True,'source_only_review':True}
 return row
rows=list(concurrent.futures.ThreadPoolExecutor(max_workers=4).map(evidence,REPS));sheet=Image.new('RGB',(1080,230*len(rows)),'white')
for i,r in enumerate(rows):sheet.paste(r,(0,230*i))
sheet.save(W/'source_replacements_v8_首中尾.jpg',quality=95)
M=[]
def motion(rec,kind,a,b,reason):
 s=OLD[rec];assert not s.get('is_photo') and rec!=8332 and 6909<=rec<10850;assert 0.025-1e-8<=abs(b-a)<=0.035+1e-8
 M.append({'record_frame':rec,'kind':kind,'start_size':a,'end_size':b,'center_start':[.5,.5],'center_end':[.5,.5],'reason':reason})
motion(7151,'push',1.0,1.03,'工程教师指向项目，轻推集中到教师与小车图示；保留屏幕主体和头顶空间。')
motion(7211,'push',1.0,1.025,'师生手工操作逐步集中到双手与作品，画面已有真实手部动作，缓推仅辅助。')
motion(7413,'push',1.0,1.025,'教师持书自然讲解，固定中心轻推加强人物温度，书本和手势保持可见。')
motion(7564,'push',1.0,1.035,'教师俯身指导的较宽构图，缓推靠近师生互动，前景与窗口保留层次。')
motion(7610,'push',1.0,1.025,'讲台教师与手势保持同框，微推使短镜更有呼吸，不改变人物横向位置。')
motion(7788,'pull',1.03,1.0,'从教师和学生互动微微放回完整小组关系，保留同学围桌回应。')
motion(7902,'push',1.0,1.025,'笔尖书写的真实动作，微推聚焦手与纸；不把静态文字作强裁切。')
motion(8123,'pull',1.03,1.0,'双人传递展示条时略放开，让两人和作品关系更完整，固定中心。')
motion(8452,'push',1.0,1.03,'陶塑纹理与手指动作位于中心，微推加强触觉细节，避免继续裁掉手指。')
motion(8614,'pull',1.03,1.0,'彩色手工作品被转动，轻拉远完整呈现作品与双手，不和原动作反向横移。')
motion(8716,'push',1.0,1.025,'学生与教师指导的近景，以最小微推强化学习表情和操作；不放大到仅剩面孔。')
motion(9860,'push',1.0,1.035,'古树庭院空间宽，居中微推带入校园纵深，承接教育沃土而不使用横向漂移。')
motion(10056,'push',1.0,1.025,'小学课堂全景轻推，让视线进入师生关系；保留课堂整体。')
motion(10247,'pull',1.03,1.0,'校园与城市同框，轻拉远打开空间，保留楼宇天际线，承接立足东城。')
assert len(M)==14
(W/'source_replacements_v8.json').write_text(json.dumps(REPS,ensure_ascii=False,indent=2));(W/'motion_suggestions_v8.json').write_text(json.dumps(M,ensure_ascii=False,indent=2));(W/'source_probes_v8.json').write_text(json.dumps(probes,ensure_ascii=False,indent=2))
(W/'validation_v8.json').write_text(json.dumps({'status':'DRAFT_AWAITING_EXACT_SOURCE_STILL_REVIEW','replacement_count':len(REPS),'motion_suggestion_count':len(M),'all_records_and_lengths_preserved':True,'source_conflicts_with_188_shots_and_5_v2':conflicts,'shot_count_preserved':len(BASE['shots']),'duration_frames_preserved':BASE['duration_frames'],'duration_seconds_preserved':BASE['duration_seconds'],'audio_untouched':True,'source_audio_import':False,'photo_motion_added':False,'english_24fps_untouched':True,'slogans_interviews_after_10850_untouched':True,'motion_center_fixed':True,'motion_max_horizontal_shift':0,'motion_scale_range':[1.0,1.035],'note':'缓推是待根代理实施的建议；源静帧不能证明原生运动平滑，需要实施后实际画面验证。'},ensure_ascii=False,indent=2))
print('prepared',len(REPS),'source replacements;',len(M),'motion suggestions')
