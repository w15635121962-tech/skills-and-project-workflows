from common_v22 import *
base=json.loads((OUT/'live_before_v22.json').read_text());before=base['snapshot'];bg=json.loads((OUT/'live_graphs_before_v22.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p and p.GetName()==PROJECT;mp=p.GetMediaPool();parent=p.GetCurrentTimeline();assert parent.GetName()==base['timeline'];assert snap(parent)==before and graphs(parent)==bg
assert not any(p.GetTimelineByIndex(k).GetName()==TIMELINE for k in range(1,p.GetTimelineCount()+1))
t=parent.DuplicateTimeline(TIMELINE);assert t and p.SetCurrentTimeline(t);assert snap(t)==before
src=Path('/Volumes/YSAigc/2026-2027/文汇中学/拍摄素材转码')
# source, record in/out exclusive, source in, label, existing grade donor track/start.
rows=[
 ('002/Proxies/A002C008_260924Z5_Proxy.mov',0,40,75,'新首镜 · 教学楼仰拍后移',1,340),
 ('004/Proxies/A001C034_260921WP_Proxy.mov',40,81,202,'广育群才 · 书院文脉',3,60),
 ('007/Proxies/C0007_Proxy.mov',81,116,525,'晨光脚步 · 动作入场',3,98),
 ('006/Proxies/C0166_Proxy.mov',116,151,104,'学校班牌 · 保留手动选段',3,145),
 ('007/Proxies/C0002_Proxy.mov',151,185,375,'学生行进 · 延续手动顺序',4,207),
 ('003/Proxies/A003C139_260924UW_Proxy.mov',185,221,60,'书页扬起 · 运动过门',1,287),
 ('003/Proxies/A003C132_2609241J_Proxy.mov',221,254,300,'隔书架阅读 · 眼神与书香',3,254),
 ('003/Proxies/A003C200_260924PF_Proxy.mov',254,290,508,'女生拍掌 · 完整动作',1,508),
 ('004/Proxies/A001C035_260921KV_Proxy.mov',290,324,175,'晨光穿树 · 轻缓推进',3,324),
 ('007/Proxies/C0016_Proxy.mov',324,370,250,'校园透光 · 片名承接',3,370),
 ('005/Proxies/20260921_D0428_Proxy.mov',370,404,62,'校园风采 · 短插镜',3,416),
 ('006/Proxies/C0156_Proxy.mov',404,439,140,'师者风华 · 短插镜',3,462),
 ('003/Proxies/A003C221_26092473_Proxy.mov',439,475,1090,'抬眼微笑 · 青春温度',3,254),
 ('004/Proxies/A001C338_260921QR_Proxy.mov',475,511,125,'沙画指尖 · 艺术创造',1,561),
 ('004/Proxies/A001C214_260921LC_Proxy.mov',511,545,20,'机器人视差 · 科学空间',3,508),
 ('004/Proxies/A001C328_26092194_Proxy.mov',545,579,140,'双手拼搭 · 实践创造',3,554),
 ('002/Proxies/A002C039_2609246R_Proxy.mov',579,613,25,'滴管实验 · 同伴协作',3,601),
 ('007/Proxies/C0125_Proxy.mov',613,667,568,'群体向前 · 收束启航',3,98),
]
plan=[dict(path=str(src/a),start=b,end=c,source_in=d,source_out_exclusive=d+c-b,label=e,donor_track=f,donor_start=g) for a,b,c,d,e,f,g in rows]
assert plan[0]['start']==0 and plan[-1]['end']==667 and len(plan)==18 and all(a['end']==b['start'] for a,b in zip(plan,plan[1:]))
# Retain the fresh manual order: feet, school sign, then the walking students.
# The manual V4 student overlay is rebuilt in the faster sequence; title and corner stay untouched.
remove=[i for i in t.GetItemListInTrack('video',3) if i.GetStart()<667]
remove+= [i for i in t.GetItemListInTrack('video',4) if i.GetStart()==207]
assert len(remove)==14;assert t.DeleteClips(remove,False)
previous=mp.GetCurrentFolder();folder=mp.AddSubFolder(mp.GetRootFolder(),'v22_开头提速与首镜');assert folder and mp.SetCurrentFolder(folder)
media=mp.ImportMedia([x['path'] for x in plan]);assert len(media)==18;assert mp.SetCurrentFolder(previous);lookup={m.GetClipProperty('File Path'):m for m in media}
for x in plan:assert float(lookup[x['path']].GetClipProperty('FPS'))==25
items=mp.AppendToTimeline([dict(mediaPoolItem=lookup[x['path']],startFrame=x['source_in'],endFrame=x['source_out_exclusive'],mediaType=1,trackIndex=3,recordFrame=x['start']) for x in plan]);assert len(items)==18
for x,it in zip(plan,items):
 assert (it.GetStart(),it.GetEnd(),it.GetLeftOffset())==(x['start'],x['end'],x['source_in']);assert it.SetName('开头提速｜'+x['label']);assert it.SetClipColor('Blue');it.GetCurrentVersion();it.GetNodeGraph().GetNumNodes()
r.OpenPage('color');time.sleep(.5)
for x,it in zip(plan,items):
 donor=next(i for i in parent.GetItemListInTrack('video',x['donor_track']) if i.GetStart()==x['donor_start']);assert donor.GetNodeGraph().GetNumNodes()==1;assert donor.CopyGrades([it])
# Fresh source match, avoiding targeted selective grades from a different subject.
for start,slope,power in [(0,1.0,1.0),(185,1.0,1.0),(254,1.0,1.0),(439,1.0,1.0),(475,1.0,1.0),(613,1.0,1.0)]:
 it=next(i for i in items if i.GetStart()==start);assert it.SetCDL(dict(NodeIndex='1',Slope=' '.join([str(slope)]*3),Offset='0 0 0',Power=' '.join([str(power)]*3),Saturation='1'))
# Re-time the existing morning-light push to its new, shorter shot. No movie speed changes.
it=next(i for i in items if i.GetStart()==290);c=it.AddFusionComp();assert c;c.SetPrefs({'Comp.FrameFormat.Width':1920,'Comp.FrameFormat.Height':1080,'Comp.FrameFormat.Rate':25});mi=c.FindToolByID('MediaIn');mo=c.FindToolByID('MediaOut');xf=named(c,'Transform','V22_晨光缓推_2percent');assert xf.ConnectInput('Input',mi) and mo.ConnectInput('Input',xf);xf.SetInput('Center',{1:.5,2:.5});xf.SetInput('Pivot',{1:.5,2:.5});xf.Size=c.BezierSpline();a=int(c.GetAttrs()['COMPN_RenderStart']);z=int(c.GetAttrs()['COMPN_RenderEnd']);assert z-a+1==34
for f in range(a,z+1):
 u=(f-a)/(z-a);xf.Size[f]=1+.02*(3*u*u-2*u*u*u)
assert it.ExportFusionComp(str(OUT/'晨光_缩短后原生缓推_v22.comp'),1);assert it.ImportFusionComp(str(OUT/'晨光_缩短后原生缓推_v22.comp'));active_comp(it)
after=snap(t);g=graphs(t);assert after['audio']==before['audio'];assert after['video'][0]==before['video'][0] and after['video'][1]==before['video'][1] and after['video'][4]==before['video'][4]
assert [x for x in after['video'][2]['items'] if x['start']>=667]==[x for x in before['video'][2]['items'] if x['start']>=667]
assert after['video'][3]['items']==[x for x in before['video'][3]['items'] if x['start']!=207];assert t.GetEndFrame()==11507
assert p.SetCurrentTimeline(parent);assert snap(parent)==before and graphs(parent)==bg;assert p.SetCurrentTimeline(t)
(OUT/'opening_edit_plan_v22.json').write_text(json.dumps({'timeline':TIMELINE,'opening_range':[0,667],'fps':25,'old_shot_count':13,'new_shot_count':18,'old_average_shot_seconds':667/25/13,'new_average_shot_seconds':667/25/18,'mean_shot_duration_reduction_percent':(1-13/18)*100,'shots':plan,'all_audio_unchanged':True,'title_and_corner_unchanged':True,'fresh_manual_source_and_relative_order_preserved':True},ensure_ascii=False,indent=2))
r.OpenPage('edit');assert pm.SaveProject()
for x in plan:cap(p,t,(x['start']+x['end'])//2,PRE/f"原生初版_{x['start']:04d}.jpg",wait=.04)
(OUT/'picture_ready_snapshot_v22.json').write_text(json.dumps(snap(t),ensure_ascii=False,indent=2));(OUT/'picture_ready_graphs_v22.json').write_text(json.dumps(graphs(t),ensure_ascii=False,indent=2));assert t.SetCurrentTimecode(tc(0));assert pm.SaveProject();print('V22_18_SHOT_NATIVE_BUILD_READY',flush=True)
