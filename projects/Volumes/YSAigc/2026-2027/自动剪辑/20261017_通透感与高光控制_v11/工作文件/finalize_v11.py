import sys,json,copy,hashlib,zipfile
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import xml.etree.ElementTree as ET
sys.path.insert(0,'/Volumes/YSAigc/2026-2027/自动剪辑/20261017_双图包装与全片调色_v9/工作文件')
from common_v9 import connect,snap,tc
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'调色预览';NAME='学校_通透感与高光控制_v11_20261017'
r,pm,p,mp,t=connect();assert t.GetName()==NAME
before=json.loads((OUT/'live_before_v11.json').read_text());qa=json.loads((OUT/'native_color_qa_v11.json').read_text());assert len(qa['records'])==22 and not qa['flags'] and snap(t)==before['snapshot']
settings=p.GetSetting();assert {k:settings[k] for k in before['color_settings']}==before['color_settings']
for name in ['高光最终QA.json','层次最终QA.json']:
    report=json.loads((OUT/name).read_text());assert report['status']=='passed',(name,report)
original=next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==before['timeline'])
try:
    assert p.SetCurrentTimeline(original) and snap(original)==before['snapshot']
    for row in before['graphs']:
        it=next(v for v in original.GetItemListInTrack('video',row['track']) if v.GetStart()==row['start']);g=it.GetNodeGraph()
        assert it.GetCurrentVersion()==row['version'] and g.GetNumNodes()==row['nodes'] and [g.GetLUT(i) for i in range(1,g.GetNumNodes()+1)]==row['luts']
finally:assert p.SetCurrentTimeline(t)
targets={(x['track'],x['start']):x for x in qa['records']}
for row in before['graphs']:
    it=next(v for v in t.GetItemListInTrack('video',row['track']) if v.GetStart()==row['start']);g=it.GetNodeGraph();key=(row['track'],row['start'])
    assert g.GetNumNodes()==row['nodes'] and [g.GetLUT(i) for i in range(1,g.GetNumNodes()+1)]==row['luts']
    if key in targets:
        rec=targets[key];assert it.GetCurrentVersion()==rec['active_version'] and rec['prior_version']['versionName'] in it.GetVersionNameList(0)
    else:assert it.GetCurrentVersion()==row['version']
for typ in ['video','audio']:
    for k in range(1,t.GetTrackCount(typ)+1):
        assert t.GetIsTrackEnabled(typ,k)
        for it in t.GetItemListInTrack(typ,k):
            m=it.GetMediaPoolItem();assert m and Path(m.GetClipProperty('File Path')).exists()
            if typ=='video':assert m.GetClipProperty('Online Status')=='Online'
assert t.GetEndFrame()==11507 and len(t.GetItemListInTrack('video',1))==187 and len(t.GetItemListInTrack('video',3))==len(t.GetItemListInTrack('video',4))==22
assert snap(t)['audio']==before['snapshot']['audio']
v1=t.GetItemListInTrack('video',1);assert all(a.GetEnd()==b.GetStart() for a,b in zip(v1,v1[1:]))
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',22);sheet=Image.new('RGB',(1920,1770),(242,239,230));draw=ImageDraw.Draw(sheet)
choices=[(117,'迎校老师 · 控制偏亮白衣'),(4365,'窗边朗读 · 收亮并保留肤色'),(396,'开篇庭院 · 改善楼体层次')]
for i,(st,label) in enumerate(choices):
    row=targets[1,st]
    for j,key in enumerate(['before_stable','after_stable']):
        im=Image.open(row[key]).convert('RGB');im.thumbnail((960,540));x=j*960;y=i*590;sheet.paste(im,(x,y));draw.text((x+18,y+548),label+'  ·  '+('调整前 v10' if j==0 else '通透控高光 v11'),font=font,fill=(25,40,33))
preview=PRE/'通透感与高光控制_实际前后对比.jpg';sheet.save(preview,quality=95)
prior=json.loads((ROOT.parent/'20261017_双图包装与全片调色_v9/工作文件/native_color_applied_v9.json').read_text())['records']+json.loads((ROOT.parent/'20261017_人文自然调色_v10/工作文件/native_color_v10.json').read_text())['records']
all_records={(x['track'],x['start']):x for x in prior};existing_refined=len(set(all_records)&set(targets));all_records.update(targets)
asc=ET.Element('ColorCorrectionCollection',xmlns='urn:ASC:CDL:v1.2')
for key,row in sorted(all_records.items()):
    c=ET.SubElement(asc,'ColorCorrection',id=f'V{key[0]}_{key[1]}');sop=ET.SubElement(c,'SOPNode')
    for name in ['Slope','Offset','Power']:ET.SubElement(sop,name).text=row['cdl'][name]
    sat=ET.SubElement(c,'SatNode');ET.SubElement(sat,'Saturation').text=row['cdl']['Saturation']
ET.indent(asc);ET.ElementTree(asc).write(ROOT/'通透与高光控制参数_v11.ccc',encoding='utf-8',xml_declaration=True)
plan=copy.deepcopy(json.loads((ROOT.parent/'20261017_人文自然调色_v10/工作文件/edit_plan_v10.json').read_text()));plan['name']=NAME;plan['revision_v11']={'scope':'color only','targeted_items':22,'highlight_control':9,'tonal_separation':13,'existing_color_refinements':existing_refined,'newly_corrected_footage_items':22-existing_refined,'photos_untouched':True,'prior_versions_recoverable':True,'grade_record':str(OUT/'native_color_qa_v11.json'),'all_editing_graphics_audio_and_duration_unchanged':True};(OUT/'edit_plan_v11.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
(OUT/'final_native_snapshot_v11.json').write_text(json.dumps(snap(t),ensure_ascii=False,indent=2))
free=next(f for f in range(1,25) if f not in t.GetMarkers());assert t.AddMarker(free,'Green','v11 通透与控高光','22处针对性色彩调整：9处收亮，13处明暗层次；保持声音、剪辑与双图包装。',1,'v11-clarity-and-highlight-control')
assert t.SetCurrentTimecode(tc(146)) and r.OpenPage('color') and pm.SaveProject()
drt=ROOT/'学校_通透感与高光控制_v11.drt';drp=ROOT/'学校_通透感与高光控制_v11.drp';assert not drt.exists() and not drp.exists()
assert t.Export(str(drt),r.EXPORT_DRT);print('V11_TIMELINE_EXPORTED',flush=True)
assert pm.ExportProject(p.GetName(),str(drp),True);print('V11_PROJECT_EXPORTED',flush=True)
archives=[]
for path in [drt,drp]:
    assert zipfile.is_zipfile(path) and path.stat().st_size>10000
    with zipfile.ZipFile(path) as z:assert z.testzip() is None
    archives.append({'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'zip_integrity_passed':True})
result={'project':p.GetName(),'active_timeline':NAME,'scope':'color only','targeted_items':22,'highlight_control_items':9,'tonal_separation_items':13,'existing_color_refinements':existing_refined,'newly_corrected_items':22-existing_refined,'total_current_graded_video_items':sum(k[0]<3 for k in all_records),'total_current_graded_photo_items':sum(k[0]>=3 for k in all_records),'all_original_photos_and_layout_untouched':True,'all_audio_editing_and_duration_exactly_preserved':True,'all_media_online':True,'prior_v10_unchanged':True,'local_prior_versions_recoverable':True,'original_technical_luts_and_color_management_preserved':True,'fps':25,'duration_frames':11507,'duration_seconds':460.28,'duration_timecode':'00:07:40:07','resolution':[1920,1080],'main_picture_items':187,'fresh_full_film_representative_frames':193,'target_mid_before_stable_samples':22,'after_first_middle_last_frames':66,'target_frame_exports_repeated_until_stable':True,'independent_visual_qa_passed':True,'new_clipping_flags':[],'white_sky_detail_reconstruction_claimed':False,'preview':str(preview),'archives':archives,'whole_film_exported':False,'continuous_manual_full_watch_or_listen':False}
(OUT/'final_delivery_v11.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
(ROOT/'通透感与高光控制说明.txt').write_text('文汇中学教育集团宣传片｜通透感与高光控制 v11\n\n本轮只调整色彩与密度，保留全部剪辑、双图包装、44张唯一照片、缓推、文字与声音，以及7分40秒7帧总长。\n\n在当前v10原生画面基础上复查193个代表帧，针对22处精修：9处收亮部密度/白点，13处轻定黑位并加强中低调分离。重点是迎校老师白外套、窗边小学生朗读、日照白校服、科技教师与典礼讲话；校园逆光、树影及校长采访适度增加层次，保护面部明度和自然肤色。室内暗脸、前轮已调整的逆光辅导、双图照片与设计纸底保留，不一概压暗。\n\n使用原生CDL和可恢复本地颜色版本，不另套创意LUT，不改原有技术转换。对原本已无可见纹理的太阳芯或白天幕，仅收敛过亮白点，未声称恢复已丢失的细节；本轮没有采用跟踪窗或限定高光的二级操作。\n\n22处调整前画面按原时间码稳定复核，调整后首/中/尾共66帧采用重复原生输出确认帧稳定，再检查前后效果；独立视觉复核与新增明显高光/暗部损坏统计检查均通过。保留v10完整工程与原生备份，新增v11独立颜色版本。\n\n达芬奇已启用v11并停在迎校老师的调色页；可编辑工程DRP、时间线DRT、ASC CDL参数及实际前后对比图已保存。全片成片视频尚未另行导出，也没有把静帧核对表述为全片连续观看或试听。\n')
print('V11_FINAL_DELIVERY_READY',json.dumps({k:v for k,v in result.items() if k not in ['archives']},ensure_ascii=False),flush=True)
