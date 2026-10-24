import json
from pathlib import Path
base=Path('/Volumes/YSAigc/2026-2027/自动剪辑')
v8=json.loads((base/'20261017_人物动态与缓推精修_v8/工作文件/edit_plan_v8.json').read_text())
aligned=json.loads((base/'20261017_旁白精修/工作文件/narration_aligned.json').read_text())
out=base/'20261017_双图包装与全片调色_v9/工作文件/图片分组旁白.json'
task_paths={x['output']:x['path'] for x in v8['photo_tasks']}
ph=[x for x in v8['shots'] if x.get('is_photo')]
topics={
1871:('历史档案：初心与传承','同属历史沿革的真实档案，建议2000年毕业典礼配另一张历史校园/校庆档案，勿将2000年图片误标1997。','岁月·初心'),
1980:('集团成立：教育沃土与办学新局','集团揭牌与同期校园/教师群像配对，保留集团校牌可读。','教育沃土'),
2183:('四校合力：各校集团揭牌','保留另一校门揭牌照片，可配未使用的集团/成员学校园照片，学校身份清楚。','聚四校之力'),
2347:('建校起点：1997年','原1997开学典礼为主，配真实建校初期校园档案；另一张不标未经核定年份。','1997 · 初心启航'),
3749:('文汇中学校别：科创领航','两张都选文汇中学学生科创活动；保留原科创领航校别标题，不使用其他成员校照片。','文汇中学 · 科创领航'),
4051:('四校各美其美：合唱舞台','直接合并原4051和4101连续单图，保留文汇小学与金台书院小学两张合唱照片，各校完整构图，110帧双图卡不补第三张。','各美其美 · 美美与共'),
4234:('教改与贯通：教师共同研修','原跨校专题培训配另张教研研修；此处用过的原P11到6470必须换新。','共同研修'),
4544:('体系化办学：真实德育教研','原德育研讨与另张教师研讨情境配对；不叠加未经证实的政策成果。','体系共建'),
4671:('民生期盼与教育发展：家校共同育人','原母女同台真实照片首次保留，配同次活动未使用的学生/教师，后段重复P25全部改新照片。','共同成长'),
5214:('教师仁爱：陪伴学生阅读','原金台师生阅读照片配另一张真实同主题师生交流，保持关怀、阅读、陪伴语义。','以仁爱为光'),
6017:('九年贯通：小学阅读与成长','原文汇小学读书节配未使用的小学阅读/学校生活图片；无需新增‘九年贯通活动’事实标签。','成长有路径'),
6470:('师资共享与全程护航','替换重复P11，建议真实校长与青年教师座谈+另一张未使用教师交流。只写全程护航/共同成长，不将未证据校长照片标为跨校活动。','全程护航'),
6982:('学子启航：毕业与成长','替换重复历史P02，选另一张真实学生成长/毕业/学子群像；不能把2000届档案反复用作当前学生。','逐梦远方'),
7086:('师生砥砺：科创荣光','原科技创新大赛获奖与另一张真实科创成果/活动图；奖项名称只按有证据的原文件，包装尽量不另加奖项文案。','砥砺前行'),
7509:('集团师资统筹：校长引领与师徒成长','优先1虞校长.jpg与8中学德育师徒.JPG配对；独立照片不遮挡后段同期讲话口型。','师者同行'),
7728:('教师队伍：校际教研互通','原青年教师AI研讨与新入职校长寄语/青年教师座谈，可承接所在长句名师引领、骨干赋能、青年精进，避免新增‘某校共同培训’事实。','研修共进'),
8284:('科创赋能：学生动手实践','原焊接电路板与另一张未使用科技实践图配对。','科创赋能'),
8396:('体艺浸润：工笔画与艺术素养','原工笔画与另一张未使用版画/陶艺/沙画课程实照配对。','体艺浸润'),
8870:('社会认可与良好口碑：家校校园活动','替换重复母女P25，选另一张真实校园集体活动/家校互动，避免使用陌生领导照片推断其身份。','共同见证'),
9378:('四校同心：集群共生','替换重复集团揭牌P03，选真实未使用不同成员学校园/集体活动各一张；不将某一校活动说成四校同时在场。','四校同心 · 聚力共生'),
9960:('创新办学与教育品牌：真实实践','替换重复P13电子小车，使用未使用的科技/项目实践两张。','创新育人'),
10372:('社会认可、时代需要：育人成果','替换第三次母女P25，使用未使用的学生集体/艺术/综合实践图，承接教育成果，不添加无来源数据。','面向未来'),
}
groups=[]
seen=set()
for c in ph:
 r=c['record_frame']
 if r==4101:continue
 members=[c]
 if r==4051:members.append(next(x for x in ph if x['record_frame']==4101))
 duration=sum(x['length_frames'] for x in members)
 a=r/25;b=(r+duration)/25
 words=[w for s in aligned['sentences'] for w in s['words'] if w['end']>a and w['start']<b]
 sentences=[{'id':s['id'],'start':s['start'],'end':s['end'],'text':s['text']} for s in aligned['sentences'] if s['end']>a and s['start']<b]
 paths=[x.get('source_photo') or task_paths[x['path']] for x in members]
 duplicates=[p for p in paths if p in seen]
 seen.update(paths)
 topic,advice,label=topics[r]
 group={'group_id':f'G{len(groups)+1:02d}','record_frame':r,'duration_frames':duration,'start_seconds':a,'end_seconds':b,'original_record_frames':[x['record_frame'] for x in members],
 'original_photo_paths':paths,'source_photo_paths':paths+([None] if len(paths)==1 else []),'source_assignment_status':'awaiting_photo_assets_v9',
 'narration_theme':topic,'actual_words_during_card':''.join(w['word'] for w in words),'narration_sentences':sentences,
 'grouping_advice':advice,'optional_label':label,'use_optional_label':r in [1871,2347,3749,4051],
 'replace_repeated_original_paths':duplicates,'preserve_original_record_duration':True,'audio_unchanged':True,
 'native_layout_requirement':'两张原图独立加载和可编辑；完整保护人脸、校牌、奖状等关键证据；可用深暖灰底、细金线、克制阴影和错层双图；每张缓推2%-3%，不使用AI换图。'}
 groups.append(group)
obj={'status':'narration_verified_source_assignments_pending','source_plan':str(base/'20261017_人物动态与缓推精修_v8/工作文件/edit_plan_v8.json'),'narration_alignment_source':str(base/'20261017_旁白精修/工作文件/narration_aligned.json'),
 'verification_method':'只读已有字级转写和V8原生时间线音轨快照；非本轮重新人工复听。完整旁白0帧起，按25fps绝对时间匹配。',
 'fps':25,'original_photo_event_count':len(ph),'proposed_group_count':len(groups),'photo_total_frames':sum(x['length_frames'] for x in ph),'photo_total_seconds':sum(x['length_frames'] for x in ph)/25,
 'rules':['保持全片11507帧、4条音轨、旁白与同期讲话原时序。','只合并直接相邻的4051+4101，其他单图段原范围不扩张，不删除中间动态镜头。','两图同组各只用一次，替换P02/P03/P11/P13/P25的重复使用。','所有标签可选，2秒组不强加文字；校长身份按源文件可核定名称，不推断额外职位或年份。','11042–11407校长原声及原补画结构保持，不用照片盖住原主讲镜头。'],
 'principal_primary_placement':{'record_frame':7509,'duration_frames':55,'preferred_photo':str(Path('/Volumes/YSAigc/2026-2027/文汇中学/学校素材资料/4-教师队伍/4-2 拜师、培训，教研/1虞校长.jpg')),'reason':'集团统筹四校师资力量的旁白语义与校长引领、师徒传承相合，且与后段同期原声隔离。'},
 'groups':groups}
out.write_text(json.dumps(obj,ensure_ascii=False,indent=2))
print(out);print('groups',len(groups),'duration',obj['photo_total_frames'],'frames')
