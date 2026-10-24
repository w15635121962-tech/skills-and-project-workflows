import sys,json,zipfile,hashlib,copy
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import xml.etree.ElementTree as ET
sys.path.insert(0,'/Volumes/YSAigc/2026-2027/自动剪辑/20261017_双图包装与全片调色_v9/工作文件')
from common_v9 import connect,snap,capture,tc
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'调色预览';BASE=ROOT.parent/'20261017_双图包装与全片调色_v9';NAME='学校_人文自然调色_v10_20261017'
r,pm,p,mp,t=connect();assert t.GetName()==NAME
before=json.loads((OUT/'live_before_v10.json').read_text());graded=json.loads((OUT/'native_color_v10.json').read_text());assert not graded['flags']
independent=json.loads((OUT/'独立调色复核.json').read_text());assert independent['status']=='passed'
assert snap(t)==before['snapshot']
original=next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==before['timeline'])
try:
    assert p.SetCurrentTimeline(original) and snap(original)==before['snapshot']
    for row in before['graphs']:
        it=next(v for v in original.GetItemListInTrack('video',row['track']) if v.GetStart()==row['start']);g=it.GetNodeGraph()
        assert it.GetCurrentVersion()==row['current_version'] and g.GetNumNodes()==row['nodes'] and [g.GetLUT(j) for j in range(1,g.GetNumNodes()+1)]==row['luts']
finally:assert p.SetCurrentTimeline(t)
for row in graded['records']:
    it=next(v for v in t.GetItemListInTrack('video',1) if v.GetStart()==row['start'])
    assert it.GetCurrentVersion()==row['active_version'] and row['prior_version']['versionName'] in it.GetVersionNameList(0) and it.GetNodeGraph().GetLUT(1)==row['lut']
prior=json.loads((BASE/'工作文件/native_color_applied_v9.json').read_text())
for row in prior['records']:
    it=next(v for v in t.GetItemListInTrack('video',row['track']) if v.GetStart()==row['start'])
    assert it.GetCurrentVersion()==row['active_version'] and [it.GetNodeGraph().GetLUT(j) for j in range(1,it.GetNodeGraph().GetNumNodes()+1)]==row['preserved_luts']
for typ in ['video','audio']:
    for k in range(1,t.GetTrackCount(typ)+1):
        assert t.GetIsTrackEnabled(typ,k)
        for it in t.GetItemListInTrack(typ,k):
            m=it.GetMediaPoolItem();assert m and Path(m.GetClipProperty('File Path')).exists()
            if typ=='video':assert m.GetClipProperty('Online Status')=='Online'
assert t.GetEndFrame()==11507 and len(t.GetItemListInTrack('video',1))==187
assert r.OpenPage('color')
# Current native captures at the same timecodes as the original grade baseline.
examples=[]
for st,frame,caption in [(5035,5065,'课堂辅导 · 人物明暗'),(6575,6600,'科学课堂 · 白衣与肤色')]:
    after=PRE/f'当前调色_{st}.jpg';capture(p,t,frame,after,.15)
    examples.append({'start':st,'frame':frame,'caption':caption,'before':str(BASE/'精修预览/调色前'/f'1_{st:05d}.jpg'),'after':str(after)})
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',23);sheet=Image.new('RGB',(1920,1180),(242,239,230));draw=ImageDraw.Draw(sheet)
for j,row in enumerate(examples):
    for k,key in enumerate(['before','after']):
        im=Image.open(row[key]).convert('RGB');im.thumbnail((960,540));sheet.paste(im,(k*960,j*590));draw.text((k*960+20,j*590+547),row['caption']+'  ·  '+('基础校色前' if k==0 else '当前调色版'),font=font,fill=(25,40,33))
preview=PRE/'人文自然调色_实际前后对比.jpg';sheet.save(preview,quality=95)
combined=prior['records']+graded['records'];asc=ET.Element('ColorCorrectionCollection',xmlns='urn:ASC:CDL:v1.2')
for row in combined:
    c=ET.SubElement(asc,'ColorCorrection',id=f"V{row['track']}_{row['start']}");sop=ET.SubElement(c,'SOPNode')
    for key in ['Slope','Offset','Power']:ET.SubElement(sop,key).text=row['cdl'][key]
    sat=ET.SubElement(c,'SatNode');ET.SubElement(sat,'Saturation').text=row['cdl']['Saturation']
ET.indent(asc);ET.ElementTree(asc).write(ROOT/'人文自然校色参数_v10.ccc',encoding='utf-8',xml_declaration=True)
plan=copy.deepcopy(json.loads((BASE/'工作文件/edit_plan_v9.json').read_text()));plan['name']=NAME;plan['revision_v10']={'scope':'color only','additional_footage_grades':8,'total_footage_grades':57,'total_photo_grades':8,'color_record':str(OUT/'native_color_v10.json'),'all_edits_graphics_and_audio_preserved':True};(OUT/'edit_plan_v10.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2))
(OUT/'final_native_snapshot_v10.json').write_text(json.dumps(snap(t),ensure_ascii=False,indent=2))
free=next(f for f in range(1,25) if f not in t.GetMarkers());assert t.AddMarker(free,'Green','v10 人文自然调色','保留v9校色，补8处课堂镜间匹配；只调色，不动剪辑、包装和声音。',1,'v10-color-only')
assert t.SetCurrentTimecode(tc(5065)) and pm.SaveProject()
drt=ROOT/'学校_人文自然调色_v10.drt';drp=ROOT/'学校_人文自然调色_v10.drp';assert not drt.exists() and not drp.exists()
assert t.Export(str(drt),r.EXPORT_DRT);print('V10_TIMELINE_EXPORTED',flush=True)
assert pm.ExportProject(p.GetName(),str(drp),True);print('V10_PROJECT_EXPORTED',flush=True)
archives=[]
for path in [drt,drp]:
    assert zipfile.is_zipfile(path) and path.stat().st_size>10000
    with zipfile.ZipFile(path) as z:assert z.testzip() is None
    archives.append({'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
record={'active_timeline':NAME,'scope':'color only','additional_footage_grades':8,'total_footage_grades':57,'total_photo_grades':8,'all_edits_graphics_and_audio_preserved':True,'all_prior_color_versions_recoverable':True,'prior_v9_unchanged':True,'all_media_online':True,'duration_frames':11507,'fps':25,'duration_seconds':460.28,'resolution':[1920,1080],'after_first_middle_last_frames':24,'independent_visual_qa_passed':True,'new_color_clipping_flags':[],'current_page':'color','whole_film_exported':False,'continuous_manual_whole_film_watch_or_listen':False,'examples':examples,'preview':str(preview),'archives':archives}
(OUT/'final_delivery_v10.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
(ROOT/'人文自然调色说明.txt').write_text('文汇中学教育集团宣传片｜人文自然调色 v10\n\n本轮只调色，保留v9全部剪辑、22组44张双图、文字包装和声音，以及7分40秒7帧总长。\n\n在原49处视频、8张照片校色基础上，补做8处课堂镜头的中间调、轻微RGB平衡和同源镜头匹配，合计57处视频、8张照片。教室面部、白校服和纸张更清楚，保留木桌暖色、自然逆光与科学课堂中性环境。原技术转换与工程色彩管理保留，无重复叠加滤镜。\n\n使用已安装resolve-color流程及官方Resolve脚本接口，先看实际帧，再在可恢复的新本地颜色版本中校正，复核8镜首中尾24张原生输出及8组同时间码前后对照，未出现数值高光/暗部损坏警示，独立视觉检查通过。此为原生初级校色与镜间匹配，未声称实施限定肤色或跟踪窗等二级调色。\n\n达芬奇已启用v10并停在调色页。旧v9原样保留，工程DRP、时间线DRT和ASC CDL参数已保存。附实际调色前后对比图；全片成片视频尚未另行导出，本轮没有重新完整连续观看或试听全片。\n')
print('V10_FINAL_DELIVERY_READY',json.dumps({k:v for k,v in record.items() if k not in ['examples','archives']},ensure_ascii=False),flush=True)
