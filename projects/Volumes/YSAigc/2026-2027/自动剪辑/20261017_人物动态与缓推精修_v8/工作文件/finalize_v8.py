import sys,json,hashlib,zipfile
from pathlib import Path
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件'
plan=json.loads((OUT/'edit_plan_v8.json').read_text());build=json.loads((OUT/'native_build_v8.json').read_text());before=json.loads((OUT/'live_before_v8.json').read_text());qa=json.loads((OUT/'native_verification_v8.json').read_text());preview=json.loads((OUT/'motion_preview_verification_v8.json').read_text());titleqa=json.loads((OUT/'title_readability_v8.json').read_text())
assert json.loads((OUT/'motion_prototype_pixel_verification_v8.json').read_text())['passed'] and json.loads((OUT/'pull_pixel_verification_v8.json').read_text())['passed']
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();mp=p.GetMediaPool();t=p.GetCurrentTimeline()
def snap(tl):
    return {typ:[{'track':k,'enabled':tl.GetIsTrackEnabled(typ,k),'locked':tl.GetIsTrackLocked(typ,k),'name':tl.GetTrackName(typ,k),'items':[{'name':it.GetName(),'start':it.GetStart(),'end':it.GetEnd(),'offset':it.GetLeftOffset(),'path':it.GetMediaPoolItem().GetClipProperty('File Path') if it.GetMediaPoolItem() else None,'properties':it.GetProperty(),'enabled':it.GetClipEnabled(),'fusion_count':it.GetFusionCompCount()} for it in tl.GetItemListInTrack(typ,k)]} for k in range(1,tl.GetTrackCount(typ)+1)] for typ in ['video','audio']}
assert p.GetName()=='学校' and t.GetName()==plan['name'] and snap(t)==build['snapshot']
base=next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==before['timeline'])
try:
    assert p.SetCurrentTimeline(base);assert snap(p.GetCurrentTimeline())==before['snapshot']
finally:assert p.SetCurrentTimeline(t)
assert build['snapshot']['audio']==before['snapshot']['audio']
for typ in ['video','audio']:
    for k in range(1,t.GetTrackCount(typ)+1):
        assert t.GetIsTrackEnabled(typ,k)
        for v in t.GetItemListInTrack(typ,k):
            m=v.GetMediaPoolItem();assert m and Path(m.GetClipProperty('File Path')).exists()
            if typ=='video':assert m.GetClipProperty('Online Status')=='Online'
title=next(v for v in t.GetItemListInTrack('video',2) if v.GetStart()==340).GetFusionCompByIndex(1)
assert title.FindTool('Template').GetInput('StyledText')=='汇启新章 · 共育未来'
assert title.FindTool('Text1').GetInput('StyledText')=='文汇中学教育集团'
assert abs(title.FindTool('Text3').GetInput('Alpha1',140)-.72)<1e-7
assert t.GetEndFrame()==11507 and len(t.GetItemListInTrack('video',1))==188
assert r.OpenPage('edit') and t.SetCurrentTimecode('00:00:00:20') and pm.SaveProject()
drt=ROOT/'学校_人物动态与缓推精修_v8.drt';drp=ROOT/'学校_人物动态与缓推精修_v8.drp';assert not drt.exists() and not drp.exists()
assert t.Export(str(drt),r.EXPORT_DRT);print('V8_TIMELINE_EXPORTED',flush=True)
assert pm.ExportProject(p.GetName(),str(drp),True);print('V8_PROJECT_EXPORTED',flush=True)
archives=[]
for path in [drt,drp]:
    assert path.stat().st_size>10000 and zipfile.is_zipfile(path)
    with zipfile.ZipFile(path) as z:assert z.testzip() is None
    archives.append({'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'zip_integrity_passed':True})
record={'project':p.GetName(),'active_timeline':t.GetName(),'duration_timecode':'00:07:40:07','duration_seconds':460.28,'fps':25,'resolution':'1920x1080','picture_count':188,'video_track_2_items':7,'audio_tracks':4,'audio_items':10,'source_replacements':14,'editable_camera_motions':38,'pushes':27,'pulls':11,'motion_scale_amplitudes':'2.5% to 3.5%; fixed center, smoothstep','affected_picture_shots':qa['affected_main_shots'],'affected_picture_and_title_stills':qa['unique_affected_actual_stills'],'additional_title_readability_stills':len(titleqa['samples']),'representative_continuous_25fps_push_frames':60,'representative_continuous_25fps_pull_frames':50,'continuous_motion_pixel_checks_passed':True,'all_native_motion_frame_values_verified':True,'all_audio_exactly_preserved':True,'prior_v7_preserved':True,'all_media_online':True,'no_gaps_or_ripple':True,'whole_film_exported':False,'continuous_manual_whole_film_watch_or_listen':False,'motion_preview':preview,'archives':archives}
(OUT/'final_delivery_v8.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
report='''文汇中学教育集团宣传片｜人物动态与缓推精修 v8

已在“学校”工程中完成时间线“学校_人物动态与缓推精修_v8_20261017”。保持188个主画面、7分40秒7帧（25fps，460.28秒）、完整旁白及原有教师口号、群体口号、校长原声和配乐。v7及此前版本保留。

本轮14处换用动作更清楚的真实素材：学生起身回应、手指固定展示卡、图书馆自然运镜与读者、真实揭牌红绸下降、学生板书、教师书写与转身讲解、小学生坐到站起、学生拿材料交流、典礼发言、学生行进脚步和阳光下慢跑。每个原有占位和切点保持，新增源区间与现有画面查重通过。

38个适合的实拍镜头加入独立可调整的画面运动，其中27处缓推、11处轻拉远。幅度约2.5%至3.5%，中心固定，起止速度放缓，保留人物头顶、手部、器材及作品边缘。体育起跳、挥手、实际操作等已有明显运动的画面保留自然动势；档案图已有的轻推进保留。片名在第三幅树光背景加强了文字阴影，内容、字体、位置和原有淡出保持。

已检查52处改动画面的首中尾，共163张真实达芬奇输出，另补5张片名字标明暗复核。全部38处运动的每帧曲线值与中心均已读回核对。另以25fps逐帧取得60帧缓推和50帧拉远的实际输出，与同帧未加效果画面对比，拟合画面缩放并检查相邻帧，未检出运动跳变或相邻重复帧。此项针对两个代表样段，未声称连续完整播放或试听全片。

已保存可编辑DRP与时间线DRT，并通过压缩包完整性检查。附4.4秒、25fps无声推拉对比预览（左为原构图，右为v8），用于查看运动幅度，并非全片导出。原有约3分55秒“绚丽／顺利”的词音疑问维持原录音及复核标记。
'''
path=ROOT/'人物动态与缓推精修说明.txt';assert not path.exists();path.write_text(report)
print('V8_FINAL_DELIVERY_READY',json.dumps({k:v for k,v in record.items() if k not in ['archives','motion_preview']},ensure_ascii=False),flush=True)
