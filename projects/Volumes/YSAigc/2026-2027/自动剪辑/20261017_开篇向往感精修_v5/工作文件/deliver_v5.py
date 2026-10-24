import sys,json,hashlib,zipfile
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'开篇预览';plan=json.loads((OUT/'opening_plan_v5.json').read_text());build=json.loads((OUT/'native_build_v5.json').read_text());base=json.loads((OUT/'live_before_v5.json').read_text());qa=json.loads((OUT/'native_verification_v5.json').read_text());groups=json.loads((OUT/'picture_change_groups_v5.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert p.GetName()=='学校' and t.GetName()==plan['name']
def snap(t):
 return {typ:[{'track':k,'enabled':t.GetIsTrackEnabled(typ,k),'locked':t.GetIsTrackLocked(typ,k),'name':t.GetTrackName(typ,k),'items':[{'name':it.GetName(),'start':it.GetStart(),'end':it.GetEnd(),'offset':it.GetLeftOffset(),'path':it.GetMediaPoolItem().GetClipProperty('File Path') if it.GetMediaPoolItem() else None,'properties':it.GetProperty(),'enabled':it.GetClipEnabled(),'fusion_count':it.GetFusionCompCount()} for it in t.GetItemListInTrack(typ,k)]} for k in range(1,t.GetTrackCount(typ)+1)] for typ in ['video','audio']}
current=snap(t);assert current==build['snapshot'];assert current['audio']==base['snapshot']['audio'];assert t.GetEndFrame()==11507
assert [x for x in current['video'][0]['items'] if x['start']>=1767]==[x for x in base['snapshot']['video'][0]['items'] if x['start']>=1767]
assert len(qa['actual_picture_frames'])==54 and len(qa['title_checks'])==7
for rec in qa['actual_picture_frames']:assert Path(rec['path']).exists()
for g in groups:
 s=g['new'];v=next(v for v in t.GetItemListInTrack('video',1) if v.GetStart()==s['record_frame']);assert v.GetDuration()==s['length_frames'];assert v.GetLeftOffset()==round(s['in']*s['fps'])
title=t.GetItemListInTrack('video',2)[0];assert title.GetStart()==340 and title.GetEnd()==508 and title.GetFusionCompCount()==1
c=title.GetFusionCompByIndex(1);assert c.GetAttrs()['COMPN_RenderEnd']==167 and not c.FindToolByID('MediaIn');assert c.FindTool('Template').GetInput('Font')=='Songti SC'
fade=c.FindTool('Merge4');assert abs(fade.GetInput('Blend',0))<1e-8 and abs(fade.GetInput('Blend',84)-1)<1e-8 and abs(fade.GetInput('Blend',167))<1e-8
v4=next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()=='学校_全片复核精修_v4_20261017');v4title=v4.GetItemListInTrack('video',2)[0]
assert v4title.GetStart()==383 and v4title.GetFusionCompByIndex(1).FindTool('Template').GetInput('Font')=='Heiti SC','v4 must remain recoverable and unchanged'
assert r.OpenPage('edit');assert t.SetCurrentTimecode('00:00:00:20');assert pm.SaveProject()
archives=[]
for ext in ['drt','drp']:
 path=ROOT/f'学校_开篇向往感精修_v5.{ext}';assert not path.exists()
 assert (t.Export(str(path),r.EXPORT_DRT) if ext=='drt' else pm.ExportProject(p.GetName(),str(path),True))
 assert path.exists() and path.stat().st_size>1000
 with zipfile.ZipFile(path) as z:assert z.testzip() is None
 archives.append({'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'zip_integrity':'passed'})
report='''学校宣传片 · 开篇向往感精修 v5

当前时间线：学校_开篇向往感精修_v5_20261017
全片：7分40秒07帧，25fps，1920×1080。前70.68秒精修，后续画面与全部4条音轨10个音频片段逐项保留。

本轮完成
1. 0–4.68秒：取消原两处短切，用古树、檐廊、庭院的一镜缓缓打开学校，先给观众空间与安定感。保留12帧轻柔淡入。
2. 4.68–13.60秒：自然入校与师生围读，承接青春启航和点亮梦想，建立真实、可亲近的学校日常。
3. 13.60–20.32秒：片名提前与“汇启新章”同步；宋体主片名、暖白校名、细金线和阳光留白。独立可编辑Fusion文字，18帧渐入渐出，无大面积底板。
4. 20.32–26.68秒：由连续低头做题，改为真实同伴拍手互动和抬头倾听；保留平静目光与自然眨眼，让青春的向往落在人与人的关系中。
5. 45.40–50.92秒：静态阅读照片换成真实图书室阅读，书架纵深、书页和读者完整停留5.52秒。
6. 55.88–60.92秒：原两镜合成5.04秒教师辅导与自然微笑回应；源7.00–12.04秒避开此前横穿遮脸。
7. 60.92–63.72秒：以石景泉水承接人文与自然，随后接沙画的手部触感。

节奏
首70.68秒由20镜减为18镜；前20.32秒由5镜减为4镜，平均停留4.06秒提升为5.08秒。实验与运动保留在对应旁白位置，既保留求知与青春，也让师生关系有完整呼吸。

核验
已查看54张真实Resolve首中尾画面、7组片名与底片对照、3张开场淡入画面。片名首末帧均已退净，中段可读；全部119个画面片段在线且无间隙。配音、配乐、口号、校长讲话的文件、起止位置、偏移和属性与v4一致。v4及更早版本保留，备份与新drp/drt完整性通过。

本轮是可编辑工程及实际画面复核，未做全片连续播放听审，未导出最终MP4。原3:55字音疑点仍保留v4标记；本轮未改配音。现有素材以720p拍摄代理和混合分辨率档案为主，高清交付前应重连原始素材。
'''
(ROOT/'开篇向往感精修说明.txt').write_text(report,encoding='utf-8')
delivery={'timeline':t.GetName(),'duration_seconds':460.28,'opening_seconds':70.68,'opening_shots_before':20,'opening_shots_after':18,'picture_count':119,'changed_old_picture_items':8,'new_picture_segments':6,'title_start_seconds':13.6,'title_end_seconds':20.32,'editable_title':True,'all_audio_preserved':True,'picture_after_70_68_preserved':True,'v4_preserved':True,'actual_opening_review_frames':54,'title_comparison_pairs':7,'all_media_online':True,'archives':archives,'preview':str(PRE/'开篇向往感精修总览.jpg'),'limitations':['No full continuous playback/listen','No final MP4 render','Original v4 voice ambiguity at3:55 retained','Sources mostly720p proxies; reconnect originals for high resolution delivery']}
(OUT/'final_delivery_v5.json').write_text(json.dumps(delivery,ensure_ascii=False,indent=2));print('V5_DELIVERED',json.dumps(delivery,ensure_ascii=False),flush=True)
