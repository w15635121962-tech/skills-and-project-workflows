from pathlib import Path
import json,copy,av,math
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件'
old=json.loads((ROOT.parent/'20261017_全片复核精修_v4/工作文件/refined_plan_v4.json').read_text());inventory=json.loads((ROOT.parent/'20261017_学校粗剪/工作文件/footage.json').read_text())
def src(group,token):
 found=[s for s in inventory if s['group']==group and token in s['name']];assert len(found)==1;return found[0]
proposals=[
 ([0,52],'004','A001C049_',.60,'古树、檐廊与庭院从容建立学校空间；以一镜4.68秒的可进入感承接书香沃土'),
 ([508],'003','A003C199_',15.0,'同伴拍手互动：青春在温暖真实的日常关系中展开'),
 ([587],'003','A003C229_',5.2,'少年抬头倾听：以平静明亮的目光承接每一份憧憬'),
 ([1135],'003','A003C134_',6.0,'真实图书馆阅读代替静态照片，书架纵深、书页与读者完整停留'),
 ([1397,1462],'003','A003C097_',7.0,'教师辅导到微笑回应完整停留5.04秒，让学习专注与生活温度在同一师生关系中完成'),
 ([1523],'004','A001C037_',3.0,'石雕泉水与绿意承接人文和自然；与后续沙画的手部触感形成材质呼应'),
]
groups=[];shots=copy.deepcopy(old['shots'])
for starts,g,token,a,intent in proposals:
 prior=[s for s in old['shots'] if s['record_frame'] in starts];assert len(prior)==len(starts)
 assert all(x['record_frame']+x['length_frames']==y['record_frame'] for x,y in zip(prior,prior[1:]))
 item=src(g,token);s=copy.deepcopy(prior[0]);length=sum(x['length_frames'] for x in prior)
 s.update({'path':item['path'],'name':item['name'],'fps':item['fps'],'length_frames':length,'in':a,'out':a+length/25,'speed':1,'is_photo':False,'log':True,'intent':intent,'title':None,'asset_id':None,'source_photo':None,'revision_v5':True,'narration_sentence_ids':sorted(set(i for p in prior for i in p['narration_sentence_ids']))})
 assert s['out']<=item['duration']
 for k in ['revision_v4']:s.pop(k,None)
 shots=[z for z in shots if z['record_frame'] not in starts]+[s]
 groups.append({'old_record_frames':starts,'start':prior[0]['record_frame'],'end':prior[-1]['record_frame']+prior[-1]['length_frames'],'old':prior,'new':s})
shots.sort(key=lambda s:s['record_frame'])
for i,s in enumerate(shots,1):s['index']=i
assert shots[0]['record_frame']==0 and shots[-1]['record_frame']+shots[-1]['length_frames']==11507
assert all(a['record_frame']+a['length_frames']==b['record_frame'] for a,b in zip(shots,shots[1:]))
plan=copy.deepcopy(old);plan.update({'name':'学校_开篇向往感精修_v5_20261017','base_timeline':'学校_全片复核精修_v4_20261017','shots':shots,'scope_end_frame':1767,'opening_style_v5':'先建立古树庭院的安定感，再让观众进入同伴与师生关系；朴素真实的向往感、宋体片名与阳光留白','title_v5':{'record_frame':340,'length_frames':168,'main':'汇启新章 · 共育未来','sub':'文汇中学教育集团','fade_frames':18}})
(OUT/'opening_plan_v5.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
(OUT/'picture_change_groups_v5.json').write_text(json.dumps(groups,ensure_ascii=False,indent=2))
print('PLAN_V5',len(shots),'opening',len([s for s in shots if s['record_frame']<1767]),'groups',len(groups))
