import json,copy,subprocess,concurrent.futures
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
B=Path('/Volumes/YSAigc/2026-2027/自动剪辑');O=B/'20261017_镜头节奏与开篇重剪_v7/工作文件/中段加密';P=B/'20261017_镜头节奏与开篇重剪_v7/工作文件/base_plan_v6.json';D=json.loads(P.read_text());C=json.loads((B/'20261017_学校粗剪/工作文件/footage.json').read_text());OLD={s['record_frame']:s for s in D['shots']};L='/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/look.py'
def find(g,t):
 a=[x for x in C if x['group']==g and any(x['name'].startswith(s) for s in [t+'_','20260924_'+t+'_','20260921_'+t+'_'])];assert len(a)==1,(g,t);return a[0]
groups=[]
def group(olds,parts,intent):
 rf=olds[0];size=sum(OLD[r]['length_frames'] for r in olds);assert sum(n for _,n,_,_,_ in parts)==size
 for a,b in zip(olds,olds[1:]):assert a+OLD[a]['length_frames']==b
 segs=[];pos=rf
 for template,n,code,src,why in parts:
  s=copy.deepcopy(OLD[template]);new=code is not None
  if new:
   meta=find(*code);s.update(path=meta['path'],name=meta['name'],fps=float(meta['fps']),in_=src,log=True,is_photo=False,asset_id=None,title=None,source_photo=None,resolution=[meta['video']['width'],meta['video']['height']]);s.pop('in_',None)
  else:src=s['in'] if src is None else src
  s.update(record_frame=pos,length_frames=n,**{'in':src,'out':round(src+n/25,8)},speed=1,intent=why,revision_v7=True,v7_new_source=new,v7_source_old_record=template)
  s['evidence']={'first_middle_last_viewed':False};segs.append(s);pos+=n
 groups.append({'old_record_frames':olds,'record_frame':rf,'length_frames':size,'intent':intent,'segments':segs})
# （模板起点、帧长、新源(组,编号)或None、源入秒、画面目的）
group([1767],[(1767,52,None,None,'百年学粹牌匾先建立文脉'),(1767,52,('004','A001C075'),1,'由牌匾转读书游戏题词的近景，文脉落实为教育精神')],'文脉双角度：牌匾→题词，避免4.16秒同一空镜')
group([1871],[(1871,60,None,None,'保留2000年毕业典礼真实档案2.4秒及原年份标识'),(1871,49,('003','A003C130'),1,'当代中学生静心读写，承接时光沉淀品牌；不延续2000年档案字幕，不冒充历史同期画面')],'历史年份证据保留，毕业档案→当代读写学生')
group([2347],[(2347,60,None,None,'建校初期真实档案保留2.4秒，完整承接始建1997'),(2347,46,('002','A002C013'),1,'花枝前景与当代教学门廊，承接从单点办学到集团赋能，不冒充历史画面')],'建校史料→当代校园，不延长原4.24秒')
group([2453,2530],[(2453,50,None,None,'小学楼保留2秒学段标识'),(2453,46,('005','D0437'),1,'小学查字典手部，建筑之后看真实学习'),(2530,46,None,None,'中学学生听课近景'),(2530,46,('006','C0280'),1,'明亮中学课堂全景，形成低学段操作→高学段听课→班级的近远变化')],'原两镜7.52秒改四个真实角度，保留小学与中学顺序')
group([2641],[(2641,48,None,None,'实验协作全景先交代空间'),(2641,47,('002','A002C026'),1,'两名学生专注观察试管与滴管动作，换真实侧机位')],'实验全景→学生操作反应')
group([2736],[(2736,50,None,None,'保留自然互动表情'),(2736,50,('006','C0262'),1.6,'两名学生对照学习材料，右侧学生抬头交流；不把学生误称教师')],'多元共生从表情转为学习交流')
group([2836],[(2836,50,None,None,'求索真知先见课堂人物'),(2836,45,('003','A003C021'),1,'写字手部与清晰笔记，形成脸到笔尖的动作衔接')],'课堂求索：人物→记笔记细节')
group([3078,3155],[(3078,50,None,None,'工程实践先见学生动手'),(3078,50,('005','D0504'),1,'同类工程课堂教师俯身指导，真实另一机位'),(3155,50,('005','D0558'),1,'手工拼字手部和立体作品清楚，替换大面积前景手臂遮挡的旧A319源4–6秒')],'工程操作→教师关系→手工，原6秒改三角度')
group([3228,3316],[(3228,60,None,None,'羽毛球女生抬头挥拍保持自然速度'),(3316,59,None,None,'篮球接球投篮，保留人物发力'),(3316,59,('006','C0305'),31.6,'篮筐与篮球的仰拍真实动作，避免甩镜跟拍；作为运动蒙太奇，不宣称同次投篮')],'羽毛球→篮球人物→篮筐，原7.12秒改三角度')
group([4439],[(4439,53,None,None,'中学学生听课关系'),(4439,52,('006','C0224'),1,'笔尖写作业近景，学段衔接落在具体学习动作')],'中学课堂脸与手交替')
group([4671],[(4671,65,None,None,'家长学生同台真实活动照片保留2.6秒'),(4671,52,('006','C0275'),3,'中学学生专注读书，回应民生期盼落在真实成长，不冒称照片同一活动')],'亲子活动照片→日常课堂实践')
group([4788],[(4788,66,None,None,'保留教师写板书的真实动作2.64秒'),(4788,63,('006','C0219'),1,'彩色粉笔盒近景，直接回应一支粉笔写春秋')],'写板书→粉笔，人物与器物互相呼应')
group([4917],[(4917,59,None,None,'教师讲解保留主要手势'),(4917,59,('006','C0208'),1,'学生听讲与做笔记，换回课堂接收端')],'教师风采由讲述转到学生反应')
group([5035],[(5035,61,None,None,'绿色上衣教师俯身交流，保留温暖面部'),(5035,61,('006','C0257'),1,'同一课堂从学生方向看教师手势和认真视线，真实换机位')],'关怀关系正反角度，各停2.44秒')
group([5157,5250],[(5157,57,None,None,'教师倾听学生，保留关系'),(5250,57,None,None,'师生共同阅读真实照片保留2.28秒'),(5250,57,('004','A001C114'),1,'小学教师站在学生旁俯身指点，照片之后回到真实照看')],'原师生镜头与阅读照片共6.84秒改三层教学关系')
group([5328],[(5328,54,None,None,'英语课堂教师板书讲解'),(5328,53,('006','C0241'),1,'学生在展示区前表达与比划，呈现主动参与；不称教师，不指派未经证实的学校')],'教师启发→学生表达')
group([5435],[(5435,54,None,None,'黑板前一对一答疑先看关系'),(5435,54,('006','C0180'),1,'同次课堂另一机位的学生面部回应，教师侧影在场')],'一对一答疑由中景到真实回应近景')
group([5543],[(5543,51,None,None,'保留自然笑容'),(5543,51,('006','C0295'),2.4,'学生起身看向老师并回应，换表情和视线方向，不添加摆拍动作')],'温暖笑容→主动回应')
group([5717],[(5717,45,None,None,'指尖沙画纹理，保留1.8秒触觉细节'),(5717,45,('005','D0569'),3.6,'另一沙画图样与洒沙手部，真实不同源机位，交代艺术创作的层次')],'沙画两个真实作品角度，禁止切开同段连续素材凑镜数')
group([5807],[(5807,47,None,None,'集体体操大景1.88秒'),(5807,47,('006','C0316'),27.8,'队列脚步与晨光长影的低机位，换运动尺度，不再叠加慢速')],'集体大景→有节律的脚步')
group([5901],[(5901,58,None,None,'小学课堂全景保留学段'),(5901,58,('005','D0375'),1,'小学数学教师在算式前讲解，真实金台小学课堂参考来源，不换成中学')],'小学课堂全景→教师讲解')
group([6017],[(6017,63,None,None,'小学阅读档案照片保留2.52秒'),(6017,50,('005','D0441'),1,'小学男生捧语文书读书，照片后接对应真实学习')],'小学阅读照片→真实低年级读书')
group([6130],[(6130,65,None,None,'书架前中学生阅读2.6秒'),(6130,65,('003','A003C136'),1,'图书馆女生阅读面部近景，避开过亮虚焦书页初段')],'图书馆环境阅读→专注面部')
group([6260],[(6260,55,None,None,'保留小学课堂关系2.2秒'),(6260,55,('005','D0379'),1,'红色传统服装小学生认真听讲的面部近景，同为金台小学素材来源')],'小学学段课堂→学生聆听')
group([6370],[(6370,50,('006','C0205'),1,'中学生写作业面部与姿态，替换原收拾书包的错义画面'),(6370,50,('006','C0206'),1,'另一个真实机位的笔尖批注特写，呼应课程梯度与扎实学习')],'纠正收包错义，面部→笔尖两个新源')
group([6470],[(6470,60,None,None,'跨校联合研修真实档案保留2.4秒'),(6470,45,('006','C0213'),1,'语文教师在课堂讲授，体现教研落地，不冒称该画面是研修现场')],'师资共享档案→教学实践')
group([6575],[(6575,50,None,None,'工程教师先交代培养路径'),(6575,50,('004','A001C224'),1,'学生双手拼装工程框架，另一个近机位能看见结构部件')],'教师讲解→工程操作')
group([6675],[(6675,55,('002','A002C048'),1,'化学教师俯身讲解的近景2.2秒，替换旧A049中前景人头遮挡严重的中景'),(6675,55,('002','A002C038'),1,'男生举试管观察的侧面动作，换实验性别/角度，保持真实操作')],'细致照看→学生独立观察')
group([6785],[(6785,62,None,None,'保留学生自然自信的表情2.48秒'),(6785,62,('005','D0445'),1,'小学女生读书与教师指点，跨学段回扣成长全程护航，不制造同场连续性')],'学生自信→低学段真实陪伴，衔接下一段成绩')
# Full scope integrity and source collision audit. Retained archive photos may repeat exactly as already in v6.
covered={r for g in groups for r in g['old_record_frames']};unchanged=[copy.deepcopy(s) for s in D['shots'] if 1767<=s['record_frame']<6909 and s['record_frame'] not in covered];newsegs=[s for g in groups for s in g['segments']];scope=sorted(newsegs+unchanged,key=lambda s:s['record_frame']);pos=1767
for s in scope:assert s['record_frame']==pos,(pos,s['record_frame']);pos+=s['length_frames']
assert pos==6909
outside=[s for s in D['shots'] if s['record_frame'] not in covered]+D['interview_overlays_v6'];overlaps=[]
for s in newsegs:
 if not s['v7_new_source']:continue
 for other in outside+newsegs:
  if other is s or other['path']!=s['path']:continue
  v=max(0,min(s['out'],other['out'])-max(s['in'],other['in']))
  if v>.0001:overlaps.append({'record_frame':s['record_frame'],'other_record_frame':other['record_frame'],'overlap':v})
assert not overlaps,overlaps
reserved=[('006','C0267',1,2.44),('006','C0256',1.4,3.52),('005','D0501',1.24,3.04)]
for s in newsegs:
 if not s['v7_new_source']:continue
 for gr,cd,a,z in reserved:
  if s['path']==find(gr,cd)['path']:assert min(s['out'],z)<=max(s['in'],a)
meta={'base_plan':str(P),'fps':25,'scope_start_frame':1767,'scope_end_frame_exclusive':6909,'scope_duration_frames':5142,'timeline_duration_frames':11507,'narration_words_and_all_audio_preserved':True,'protected_records_unchanged':[3749,3832,3891,3954],'groups':groups,'unchanged_record_frames':[s['record_frame'] for s in unchanged],'net_added_shots':len(newsegs)-len(covered),'new_source_angles':sum(s['v7_new_source'] for s in newsegs),'new_source_overlaps_with_v6_and_interview_overlays':overlaps,'source_review':'pending exact first/middle/last final source-frame review'}
(O/'groups_v7.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));(O/'scope_result_segments.json').write_text(json.dumps(scope,ensure_ascii=False,indent=2))
# exact first/middle/last evidence for all modified-group segments, including retained picture windows
items=[]
for s in newsegs:
 times=[round(s['in']+.04,3),round(s['in']+s['length_frames']/50,3),round(s['out']-.04,3)];items.append({'record_frame':s['record_frame'],'path':s['path'],'new_source':s['v7_new_source'],'times':times,'intent':s['intent']})
def evidence(x):
 stem=f"final_R{x['record_frame']}";cmd=['python3',L,x['path']]
 for t in x['times']:cmd+=['--at',str(t)]
 cmd+=['-o',str(O/(stem+'.png')),'--no-timecode','--json','--overwrite'];r=subprocess.run(cmd,capture_output=True,text=True);(O/(stem+'.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,(x['record_frame'],r.stderr);x['frames']=[str(O/f'{stem}_{t:.3f}s.png') for t in x['times']];return x
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as p:items=list(p.map(evidence,items))
(O/'exact_source_evidence.json').write_text(json.dumps(items,ensure_ascii=False,indent=2));byrf={x['record_frame']:x for x in items}
for s in newsegs:s['evidence'].update(byrf[s['record_frame']])
(O/'groups_v7.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2));(O/'scope_result_segments.json').write_text(json.dumps(scope,ensure_ascii=False,indent=2))
font=ImageFont.truetype('/System/Library/Fonts/Hiragino Sans GB.ttc',20)
for page in range((len(items)+3)//4):
 its=items[page*4:page*4+4];can=Image.new('RGB',(1440,len(its)*306),(25,25,25));draw=ImageDraw.Draw(can)
 for row,x in enumerate(its):
  for col,fn in enumerate(x['frames']):
   im=Image.open(fn).convert('RGB');im.thumbnail((480,270));can.paste(im,(480*col,306*row+36));stem=Path(x['path']).stem
   if len(stem)>27:stem=stem[:27]
   draw.text((480*col+5,306*row+7),f"R{x['record_frame']} {'NEW' if x['new_source'] else 'KEEP'} {stem} {x['times'][col]:.2f}",font=font,fill='white')
 can.save(O/f'执行段精确首中尾_{page+1:02d}.jpg',quality=93)
print(json.dumps({k:meta[k] for k in ['net_added_shots','new_source_angles','scope_duration_frames','new_source_overlaps_with_v6_and_interview_overlays']},ensure_ascii=False));print('groups',len(groups),'segments',len(newsegs),'originals',len(covered),'sheets',(len(items)+3)//4)
