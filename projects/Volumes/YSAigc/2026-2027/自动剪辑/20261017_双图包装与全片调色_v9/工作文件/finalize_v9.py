from common_v9 import *
from package_tools_v9 import PAPER
from PIL import Image,ImageDraw,ImageFont
import hashlib,zipfile,copy
r,pm,p,mp,t=connect();assert t.GetName()==NAME
before=json.loads((OUT/'live_before_v9.json').read_text());packages=json.loads((OUT/'native_packages_v9.json').read_text());color=json.loads((OUT/'native_color_applied_v9.json').read_text());qa=json.loads((OUT/'native_color_qa_v9.json').read_text());motion=json.loads((OUT/'pair_motion_preview_verified_v9.json').read_text())
assert not qa['automated_flags'] and json.loads((OUT/'final_color_qa_v9.json').read_text())['status']=='passed'
for fn in ['包装原生QA_前半.json','包装原生QA_后半.json']:
    z=json.loads((OUT/'图片候选'/fn).read_text());assert 'pass' in json.dumps(z,ensure_ascii=False).lower()
assert snap(t)==packages['snapshot'] and snap(t)['audio']==before['snapshot']['audio']
base=next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==before['timeline'])
try:
    assert p.SetCurrentTimeline(base);assert snap(base)==before['snapshot']
    for g in before['graphs']:
        it=next(x for x in base.GetItemListInTrack('video',g['track']) if x.GetStart()==g['start']);graph=it.GetNodeGraph()
        assert it.GetCurrentVersion()==g['current_version'] and graph.GetNumNodes()==g['nodes'] and [graph.GetLUT(i) for i in range(1,g['nodes']+1)]==g['luts']
finally:assert p.SetCurrentTimeline(t)
all_media=[]
for typ in ['video','audio']:
    for track in range(1,t.GetTrackCount(typ)+1):
        assert t.GetIsTrackEnabled(typ,track)
        for it in t.GetItemListInTrack(typ,track):
            m=it.GetMediaPoolItem();assert m;path=m.GetClipProperty('File Path');assert Path(path).exists()
            if typ=='video':assert m.GetClipProperty('Online Status')=='Online'
            all_media.append(path)
for row in color['records']:
    it=next(x for x in t.GetItemListInTrack('video',row['track']) if x.GetStart()==row['start'])
    assert it.GetCurrentVersion()==row['active_version'] and row['prior_version']['versionName'] in it.GetVersionNameList(0)
    assert [it.GetNodeGraph().GetLUT(i) for i in range(1,it.GetNodeGraph().GetNumNodes()+1)]==row['preserved_luts']
for group in packages['groups']:
    for j,track in enumerate([3,4]):
        it=next(x for x in t.GetItemListInTrack('video',track) if x.GetStart()==group['start']);c=it.GetFusionCompByIndex(1);xf=c.FindTool('V9_PhotoGentleMotion');assert xf and not xf.GetAttrs()['TOOLB_PassThrough']
        m=group['photo_motion'][j];a,z=m['source_clock'];assert z-a+1==group['length']
        for f in range(a,z+1):
            u=(f-a)/(z-a);expected=m['size_start']+(m['size_end']-m['size_start'])*u*u*(3-2*u);assert abs(xf.GetInput('Size',f)-expected)<1e-7
        pos=xf.GetInput('Center');assert pos[1]==.5 and pos[2]==.5
    bg=next(x for x in t.GetItemListInTrack('video',1) if x.GetStart()==group['start']);c=bg.GetFusionCompByIndex(1)
    assert c.FindTool('主题题签').GetInput('StyledText')==group['title']
assert len(t.GetItemListInTrack('video',1))==187 and t.GetEndFrame()==11507
v1=t.GetItemListInTrack('video',1);assert all(a.GetEnd()==b.GetStart() for a,b in zip(v1,v1[1:]))
assert len(t.GetItemListInTrack('video',3))==len(t.GetItemListInTrack('video',4))==22
# Remove only our unused format-conversion probes; all original assets stay.
probe_paths=[ROOT/'画面包装'/n for n in ['原图G06L.JPG','G06L_original.png','G06L_original_004051.png']]
probes=[m for m in walk(mp.GetRootFolder()) if m.GetClipProperty('File Path') in {str(x) for x in probe_paths}]
assert all(m.GetClipProperty('File Path') not in all_media and int(m.GetClipProperty('Usage') or 0)==0 for m in probes)
if probes:assert mp.DeleteClips(probes)
for path in probe_paths:
    if path.exists():path.unlink()
oldplan=json.loads((BASE/'edit_plan_v8.json').read_text());newplan=copy.deepcopy(oldplan);newplan['name']=NAME
group_map={g['start']:g for g in packages['groups']};photo_records={x for g in packages['groups'] for x in g['original_records']}
shots=[]
for s in oldplan['shots']:
    if s['record_frame'] not in photo_records:shots.append(s);continue
    if s['record_frame'] not in group_map:continue
    g=group_map[s['record_frame']];bg=next(it for it in v1 if it.GetStart()==g['start'])
    shots.append({'record_frame':g['start'],'length_frames':g['length'],'path':bg.GetMediaPoolItem().GetClipProperty('File Path'),'fps':25,'resolution':[1920,1080],'in':0,'out':g['length']/25,'is_photo':True,'native_still':True,'photo_pair':True,'source_photo':None,'source_photos':[g['left'],g['right']],'title':g['title'],'chapter':s.get('chapter'),'narration_sentence_ids':s.get('narration_sentence_ids'),'intent':'原生双图分屏；两张照片分别在V3/V4，可独立调整，包装底版V1。','log':False,'native_photo_tracks':[3,4]})
for i,s in enumerate(shots,1):s['index']=i
newplan['shots']=shots;newplan['total_picture_count']=187;newplan['photo_tasks']=[{'path':g[side],'track':3+j,'record_frame':g['start'],'length_frames':g['length'],'native_still':True} for g in packages['groups'] for j,side in enumerate(['left','right'])]
newplan['revision_v9']={'photo_groups':22,'unique_original_photos':44,'photo_frames':1428,'native_background_and_labels_track':1,'native_photo_tracks':[3,4],'source_photos_not_baked_to_video':True,'picture_count_change':'188 to 187; only the adjacent choir pair was consolidated','footage_grades':49,'photo_grades':8,'grade_record':'native_color_applied_v9.json','skill':'resolve-color','all_audio_preserved':True,'prior_v8_preserved':True};save('edit_plan_v9.json',newplan)
save('final_native_snapshot_v9.json',snap(t))
# Small final review sheet uses actual native results, including the principal.
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',23);sheet=Image.new('RGB',(1920,1160),PAPER);draw=ImageDraw.Draw(sheet)
choices=[('校长寄语 · 师徒传承',PRE/'调色后实际画面/3_07509_中.jpg'),('各美其美 · 双图合唱',PRE/'双图实际画面/04051_中.jpg'),('书香校园 · 双图阅读',PRE/'双图实际画面/06017_中.jpg'),('科学课堂 · 自然校色',PRE/'调色后实际画面/1_06575_中.jpg')]
for i,(label,path) in enumerate(choices):
    im=Image.open(path).convert('RGB');im.thumbnail((960,540));x=i%2*960;y=i//2*580;sheet.paste(im,(x,y));draw.text((x+20,y+545),label,font=font,fill=(27,42,34))
sheet.save(PRE/'v9双图包装与调色_效果总览.jpg',quality=95)
free=next(f for f in range(1,25) if f not in t.GetMarkers());assert t.AddMarker(free,'Green','v9 双图包装与人文校色','22组44张唯一原图，校长照片已加入；保留声音与7分40秒；49处视频与8张照片保守原生校色，恢复可用原颜色版本。',1,'v9-paired-photos-and-color')
assert r.OpenPage('edit') and t.SetCurrentTimecode(tc(7536)) and pm.SaveProject()
drt=ROOT/'学校_双图包装与人文调色_v9.drt';drp=ROOT/'学校_双图包装与人文调色_v9.drp';assert not drt.exists() and not drp.exists()
assert t.Export(str(drt),r.EXPORT_DRT);print('V9_NATIVE_TIMELINE_EXPORTED',flush=True)
assert pm.ExportProject(p.GetName(),str(drp),True);print('V9_NATIVE_PROJECT_EXPORTED',flush=True)
archives=[]
for path in [drt,drp]:
    assert zipfile.is_zipfile(path) and path.stat().st_size>10000
    with zipfile.ZipFile(path) as z:assert z.testzip() is None
    archives.append({'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'zip_integrity_passed':True})
record={'project':p.GetName(),'active_timeline':NAME,'duration_timecode':'00:07:40:07','duration_frames':11507,'duration_seconds':460.28,'fps':25,'resolution':[1920,1080],'v1_count':187,'v2_count':7,'photo_groups':22,'native_original_photos':44,'unique_original_photo_hashes':44,'photo_total_seconds':57.12,'principal_photo_frames':[7509,7728],'photo_motion':{'count':44,'amplitude':'1.8%','native_curves_verified':True,'representative_continuous_frames':110,'motion_preview':motion},'footage_grades':49,'photo_grades':8,'all_prior_color_versions_recoverable':True,'original_luts_preserved':True,'original_project_color_management_preserved':True,'audio_tracks':4,'audio_items':10,'all_audio_exactly_preserved':True,'prior_v8_preserved':True,'all_media_online':True,'no_gaps_or_ripples':True,'package_visual_sample_count':66,'color_after_frame_records':171,'color_automated_flags':[],'independent_visual_qa_passed':True,'skill_path':'/Users/xuan/Codex_YS_Data/CodexHome/skills/resolve-color','archives':archives,'whole_film_exported':False,'continuous_manual_full_watch_or_listen':False}
save('final_delivery_v9.json',record)
report='''文汇中学教育集团宣传片｜双图包装与人文调色 v9

已在达芬奇“学校”工程启用时间线“学校_双图包装与人文调色_v9_20261017”，播放头停在新增校长照片组。完整旁白、教师与群体口号、校长原声、配乐保持原位置、原时长、原声音处理，总长仍为7分40秒7帧（25fps，460.28秒）。v8和早前时间线保留，另有本轮v8原生备份。

图片段改成22组双图分屏，共44张不同原图；逐一核对文件哈希及近似画面，时间线没有重复使用同一照片。仅把相邻的文汇小学、金台书院小学合唱图片合为4.4秒一组，主画面数量由188变为187；其他图片占位及中间动态镜头不变，图片总占用57.12秒。师资段加入文件明确的校长讲话、校长寄语照片，保留后段校长采访口型。历史年份按每张图分别标注，校别、奖项和人脸均完整。

采用暖白底、细金线、深绿灰题签和独立图注。44张照片分别位于V3/V4，包装在V1，均为原生静帧，可单独移动、裁切、替换；不把双图整体烘焙为视频。两图各有1.8%的固定中心缓推或拉远，现有实拍动作与缓推保留。

按用户要求从GitHub安装resolve-color技能，来源samuelgursky/davinci-resolve-mcp固定提交90eba8cdf4df333beb4ce41fe0ab198b8fa7d125，MIT；补齐原样参考资料、校验哈希及技能格式。技能可在下一轮继续调用。本轮依据该流程通过现有官方Resolve Python接口执行，不额外安装MCP后台。

先查看全片194个代表合成帧，再对49处视频、8张照片分别做温和曝光、中间调、RGB平衡与饱和度校正。重点改善逆光辅导人物和科学教室白衣的黄绿偏色，校长采访采用等RGB轻调密度。其余已自然的逆光、树荫、暖光、舞台色彩保留。原Sony技术转换、工程色彩管理保持；颜色在新本地版本中，可恢复原版本，另附57项ASC CDL参数记录。本轮为原生初级校色与匹配，未声称实施限定肤色或跟踪窗等二级操作。

复核22组首中尾66张原生输出，以及57处颜色改动的171条首中尾帧记录（165个不同时间点），并独立检查57组前后同时间码对照。数值检查未出现新增明显高光/暗部损坏警示；实际视觉复核通过。双图代表段另抓取25fps连续110帧，检查左右画面缩放、固定中心及相邻重复帧，并生成4.4秒无声预览。该预览不是全片成片，未重新连续完整试听/观看460秒。

可编辑工程DRP、时间线DRT已保存并通过文件完整性检查。全片成片视频尚未另行导出。
'''
(ROOT/'双图包装与人文调色说明.txt').write_text(report)
print('V9_FINAL_DELIVERY_READY',json.dumps({k:v for k,v in record.items() if k not in ['photo_motion','archives']},ensure_ascii=False),flush=True)
