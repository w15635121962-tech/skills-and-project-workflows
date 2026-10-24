import json,copy,subprocess,concurrent.futures
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
B=Path('/Volumes/YSAigc/2026-2027/自动剪辑');O=B/'20261017_人物动态与缓推精修_v8/工作文件/中段动态';P=B/'20261017_人物动态与缓推精修_v8/工作文件/base_plan_v7.json';D=json.loads(P.read_text());C=json.loads((B/'20261017_学校粗剪/工作文件/footage.json').read_text());OLD={s['record_frame']:s for s in D['shots']};L='/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/look.py'
def find(g,t):
 a=[x for x in C if x['group']==g and any(x['name'].startswith(s) for s in [t+'_','20260924_'+t+'_','20260921_'+t+'_'])];assert len(a)==1;return a[0]
specs=[
(2075,'007','C0018',43.0,'同一真实集团揭牌事件，以红绸下降和领导拉绳的明确动作替换已揭牌后的合影停留；保留事件真实性，不改两侧档案证明。','原58–62.32主要站立合影，现选择实际揭牌运动中的4.32秒；不声称浓缩了整场仪式。'),
(2595,'006','C0267',6.0,'由静态班级全景转学生在黑板前真实板书，承接中学阶段主动学习。','画面人物为学生，保留中学学段；避免把在黑板前的学生误称教师。新窗避采访1–2.44。'),
(4854,'006','C0293',6.0,'静态粉笔盒改为教师用粉笔持续书写，直接回应一支粉笔写春秋。','不同文件与取景的真实板书动作，保留教师育人语义，不冒称连续同一次落笔。'),
(6315,'005','D0380',10.4,'金台小学同课堂学生由坐到站起回应，替换几乎静止的侧面听讲。','对应小学课堂之后的真实主动回应，不改为中学人物，不新增校名字幕。'),
(6530,'006','C0213',10.4,'教师由面向学生转身指向教学画面，替换双手静持话筒的停留。','仍为同一语文教师与课堂，换到未使用的手势动作窗，体现教研落地到课堂。'),
(6785,'006','C0263',8.0,'由面向镜头的笑脸转为学生举学习材料、侧向回应同伴的自然课堂互动。','人物为穿校服学生，不把同伴当教师；以主动交流回应规范化育人与稳步成长。')]
repls=[]
for rf,g,t,src,intent,reason in specs:
 f=find(g,t);s=copy.deepcopy(OLD[rf]);n=s['length_frames'];s.update(path=f['path'],name=f['name'],fps=float(f['fps']),log=True,is_photo=False,asset_id=None,title=None,source_photo=None,resolution=[f['video']['width'],f['video']['height']],**{'in':src,'out':round(src+n/25,8)},source_start_frame=round(src*f['fps']),source_count_frames=round(n*f['fps']/25),intent=intent,revision_v8=True,v8_reason=reason,v8_old={'path':OLD[rf]['path'],'in':OLD[rf]['in'],'out':OLD[rf]['out'],'intent':OLD[rf]['intent']});repls.append(s)
replaced={s['record_frame'] for s in repls};others=[s for s in D['shots'] if s['record_frame'] not in replaced]+D['interview_overlays_v7'];collisions=[]
for s in repls:
 for t in others+repls:
  if t is s or t['path']!=s['path']:continue
  overlap=max(0,min(s['out'],t['out'])-max(s['in'],t['in']))
  if overlap>1e-5:collisions.append({'record':s['record_frame'],'other_record':t['record_frame'],'overlap':overlap})
assert not collisions,collisions
motion_specs=[(1767,'push','牌匾建立文脉，克制接近核心文字；不碰历史年份底标'),(1931,'push','中学生读写时缓慢靠近专注状态'),(2453,'pull','小学教学楼轻拉远，为随后小学操作近景让出尺度对比'),(2549,'push','课堂听讲缓推，聚焦中间学生的注意力'),(2736,'push','学生自然交流保持完整关系并略加强亲近感'),(2836,'pull','从专注学生略向课堂环境展开，再接笔尖'),(3128,'push','工程教师俯身照看时轻缓靠近师生关系'),(3600,'push','教师板书讲解轻缓靠近，不放大背景空白'),(4289,'pull','化学实验课堂稍展开空间，突出共同探究'),(4439,'push','聆听学生保持固定中心，减少静止感'),(4917,'push','教师讲解时缓推，保留主要手势与面部'),(5271,'push','小学教师俯身指点，固定中心轻缓接近'),(5594,'push','学生起身回应时加强表达主体'),(5901,'pull','小学课堂从教师稍展开到班级关系'),(6130,'push','书架前阅读保留原翻页动作，轻缓靠近专注表情')]
motions=[]
for rf,kind,reason in motion_specs:
 s=OLD[rf];assert not s.get('is_photo');assert rf not in [3749,3832,3891,3954];assert rf not in replaced
 a,z=(1.04,1.07) if kind=='push' else (1.07,1.04);motions.append({'record_frame':rf,'kind':kind,'start_size':a,'end_size':z,'center_start':[.5,.5],'center_end':[.5,.5],'reason':reason,'length_frames':s['length_frames'],'path':s['path'],'scope':'V1 picture only','preserve_source_motion':True})
meta={'base_plan':str(P),'fps':25,'timeline_duration_frames':11507,'timeline_duration_seconds':460.28,'main_shot_count_preserved':188,'scope_start_frame':1767,'scope_end_frame_exclusive':6909,'source_review':'pending exact source first/middle/last visual review','all_audio_and_titles_preserved':True,'protected_fusion_identity_records':[3749,3832,3891,3954],'new_source_overlap_with_retained_v7_or_interview':collisions}
(O/'source_replacements_v8.json').write_text(json.dumps({**meta,'replacements':repls},ensure_ascii=False,indent=2));(O/'motion_suggestions_v8.json').write_text(json.dumps({**meta,'motion_count':len(motions),'motion':motions,'constraints':{'all_fixed_center':True,'no_photo_motion':True,'no_protected_identity_motion':True,'digital_size_range':[1.04,1.07],'absolute_size_change':.03,'relative_push_percent':(1.07/1.04-1)*100,'audio_changed':False}},ensure_ascii=False,indent=2))
def ev(s):
 rf=s['record_frame'];times=[round(s['in']+.04,3),round((s['in']+s['out'])/2,3),round(s['out']-.04,3)];stem=f'新增源_R{rf}';cmd=['python3',L,s['path']]
 for t in times:cmd+=['--at',str(t)]
 cmd+=['-o',str(O/(stem+'.png')),'--no-timecode','--json','--overwrite'];r=subprocess.run(cmd,capture_output=True,text=True);(O/(stem+'.log')).write_text(r.stdout+r.stderr);assert not r.returncode;s['evidence']={'source_times_seconds':times,'frames':[str(O/f'{stem}_{t:.3f}s.png') for t in times],'first_middle_last_viewed':False};return s
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p:repls=list(p.map(ev,repls))
font=ImageFont.truetype('/System/Library/Fonts/Hiragino Sans GB.ttc',20)
for page in range(2):
 its=repls[page*3:page*3+3];can=Image.new('RGB',(1440,len(its)*306),(25,25,25));draw=ImageDraw.Draw(can)
 for row,s in enumerate(its):
  for col,fn in enumerate(s['evidence']['frames']):
   im=Image.open(fn).convert('RGB');im.thumbnail((480,270));can.paste(im,(480*col,306*row+36));draw.text((480*col+5,306*row+6),f"R{s['record_frame']} {s['name']} {s['evidence']['source_times_seconds'][col]:.2f}",font=font,fill='white')
 can.save(O/f'新增动态源首中尾_{page+1:02d}.jpg',quality=94)
(O/'source_replacements_v8.json').write_text(json.dumps({**meta,'replacements':repls},ensure_ascii=False,indent=2));print(json.dumps({'replacements':len(repls),'motions':len(motions),'source_overlap':collisions},ensure_ascii=False))
