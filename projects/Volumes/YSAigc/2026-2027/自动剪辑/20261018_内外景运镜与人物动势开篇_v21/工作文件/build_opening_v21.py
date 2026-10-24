from common_v21 import *
base=json.loads((OUT/'live_before_v21.json').read_text());before=base['snapshot'];oldgraphs=json.loads((OUT/'live_graphs_before_v21.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p and p.GetName()==PROJECT;mp=p.GetMediaPool();parent=p.GetCurrentTimeline();assert parent.GetName()==PARENT
assert snap(parent)==before and graphs(parent)==oldgraphs,'Fresh user edits must be re-inspected'
assert not any(p.GetTimelineByIndex(k).GetName()==TIMELINE for k in range(1,p.GetTimelineCount()+1))
t=parent.DuplicateTimeline(TIMELINE);assert t and p.SetCurrentTimeline(t);assert snap(t)==before
src=Path('/Volumes/YSAigc/2026-2027/文汇中学/拍摄素材转码')
rows=[
 ('004/Proxies/A001C070_260921XL_Proxy.mov',0,60,100,'红柱长廊 · 实拍横移',1.03,.99),
 ('004/Proxies/A001C034_260921WP_Proxy.mov',60,98,202,'广育群才 · 书院文脉',1.08,.97),
 ('007/Proxies/C0007_Proxy.mov',98,145,525,'晨光脚步 · 迈向青春',1.0,1.0),
 ('007/Proxies/C0002_Proxy.mov',145,207,375,'学生迎面行进 · 青春启航',1.0,1.0),
 ('006/Proxies/C0166_Proxy.mov',207,254,243,'进入明亮课堂 · 走廊横移',1.2,.98),
 ('003/Proxies/A003C132_2609241J_Proxy.mov',254,324,300,'隔书架翻书 · 书香浸润',1.0,1.0),
 ('004/Proxies/A001C048_2609212U_Proxy.mov',324,370,75,'树冠与书院庭院 · 真实缓摇',1.0,1.0),
 ('006/Proxies/C0327_Proxy.mov',370,416,300,'现代校园 · 楼宇展开',1.0,1.0),
 ('005/Proxies/20260921_D0428_Proxy.mov',416,462,62,'校园风采 · 成长记忆',1.0,1.0),
 ('006/Proxies/C0156_Proxy.mov',462,508,140,'师者风华 · 育人传承',1.35,.95),
 ('004/Proxies/A001C214_260921LC_Proxy.mov',508,554,20,'机器人视差 · 科学空间',1.06,.99),
 ('004/Proxies/A001C328_26092194_Proxy.mov',554,601,140,'双手转动拼搭 · 实践创造',1.0,1.0),
 ('002/Proxies/A002C039_2609246R_Proxy.mov',601,667,25,'滴管实验与笑容 · 求知温度',1.0,1.0),
]
plan=[dict(path=str(src/a),start=b,end=c,source_in=d,source_out_exclusive=d+c-b,label=e,slope=f,power=g) for a,b,c,d,e,f,g in rows]
assert plan[0]['start']==0 and plan[-1]['end']==667
assert all(x['end']==y['start'] for x,y in zip(plan,plan[1:]))
# Preserve the exact native transparent title, promoting it above the new picture layer.
oldtitle=next(x for x in t.GetItemListInTrack('video',2) if x.GetStart()==340)
assert oldtitle.GetEnd()==508 and oldtitle.GetFusionCompCount()==1
titlefile=OUT/'原开篇片名_保留样式与时序.comp';assert oldtitle.ExportFusionComp(str(titlefile),1)
assert not any(i.GetStart()<508 and i.GetEnd()>340 for i in t.GetItemListInTrack('video',4))
newtitle=mp.AppendToTimeline([dict(mediaPoolItem=oldtitle.GetMediaPoolItem(),startFrame=oldtitle.GetLeftOffset(),endFrame=oldtitle.GetLeftOffset()+168,mediaType=1,trackIndex=4,recordFrame=340)])[0]
assert newtitle.ImportFusionComp(str(titlefile));active_comp(newtitle);newtitle.GetCurrentVersion();newtitle.GetNodeGraph().GetNumNodes()
r.OpenPage('color');time.sleep(.5);assert oldtitle.CopyGrades([newtitle]);assert newtitle.SetName(oldtitle.GetName())
assert t.DeleteClips([oldtitle],False)
# Only replace opening overlays in this duplicate. Parent and all underlying footage remain intact.
oldopening=[i for i in t.GetItemListInTrack('video',3) if i.GetStart()<667]
assert [(i.GetStart(),i.GetEnd()) for i in oldopening]==[(117,175),(234,287),(561,614)]
assert t.DeleteClips(oldopening,False)
folder0=mp.GetCurrentFolder();folder=mp.AddSubFolder(mp.GetRootFolder(),'v21_内外景与人物动作开篇');assert folder and mp.SetCurrentFolder(folder)
media=mp.ImportMedia([x['path'] for x in plan]);assert len(media)==len(plan);assert mp.SetCurrentFolder(folder0)
lookup={m.GetClipProperty('File Path'):m for m in media}
for x in plan:assert float(lookup[x['path']].GetClipProperty('FPS'))==25
items=mp.AppendToTimeline([dict(mediaPoolItem=lookup[x['path']],startFrame=x['source_in'],endFrame=x['source_out_exclusive'],mediaType=1,trackIndex=3,recordFrame=x['start']) for x in plan]);assert len(items)==len(plan)
for x,it in zip(plan,items):
 assert (it.GetStart(),it.GetEnd(),it.GetLeftOffset())==(x['start'],x['end'],x['source_in'])
 assert it.SetName('开篇精选｜'+x['label']);assert it.SetClipColor('Blue');it.GetCurrentVersion();it.GetNodeGraph().GetNumNodes()
r.OpenPage('color');time.sleep(.5)
neutral=next(i for i in t.GetItemListInTrack('video',1) if i.GetStart()==340);assert neutral.GetNodeGraph().GetNumNodes()==1
for x,it in zip(plan,items):
 assert neutral.CopyGrades([it]);assert it.SetCDL(dict(NodeIndex='1',Slope=' '.join([str(x['slope'])]*3),Offset='0 0 0',Power=' '.join([str(x['power'])]*3),Saturation='1'))
# The requested plaque and wall shots keep their existing approved native grades.
for start,track,oldstart in [(60,3,117),(416,3,234),(462,3,561)]:
 donor=next(i for i in parent.GetItemListInTrack('video',track) if i.GetStart()==oldstart)
 target=next(i for i in items if i.GetStart()==start);assert donor.CopyGrades([target])
# Same unchanged VO and all live speech. Replace only the first music item with the checked PCM carrier.
audio=json.loads((ROOT/'旁白与配乐/开篇配乐_原生回装清单_v21.json').read_text());assert audio['container_pcm_bit_identical_to_wav'] and audio['original_bgm_after40p8_pcm_bit_identical']
m=mp.ImportMedia([audio['container_path']]);assert len(m)==1 and float(m[0].GetClipProperty('FPS'))==25
oldmusic=next(i for i in t.GetItemListInTrack('audio',3) if i.GetStart()==0);assert t.DeleteClips([oldmusic],False)
newmusic=mp.AppendToTimeline([{**audio['native_append'],'mediaPoolItem':m[0]}])[0];assert (newmusic.GetStart(),newmusic.GetEnd())==(0,2861);assert newmusic.SetName(audio['name']);assert newmusic.SetClipColor('Orange')
r.OpenPage('edit');assert pm.SaveProject()
after=snap(t);assert after['video'][0]==before['video'][0] and after['video'][4]==before['video'][4]
assert [x for x in after['video'][1]['items'] if x['start']!=340]==[x for x in before['video'][1]['items'] if x['start']!=340]
assert [x for x in after['video'][2]['items'] if x['start']>=667]==[x for x in before['video'][2]['items'] if x['start']>=667]
assert [x for x in after['video'][3]['items'] if x['start']!=340]==before['video'][3]['items']
assert next(x for x in after['video'][3]['items'] if x['start']==340)==next(x for x in before['video'][1]['items'] if x['start']==340)
for tr in [0,1,3]:assert after['audio'][tr]==before['audio'][tr]
assert after['audio'][2]['items'][1:]==before['audio'][2]['items'][1:]
assert t.GetEndFrame()==11507
assert p.SetCurrentTimeline(parent);assert snap(parent)==before and graphs(parent)==oldgraphs;assert p.SetCurrentTimeline(t)
(OUT/'opening_edit_plan_v21.json').write_text(json.dumps({'timeline':TIMELINE,'range':[0,667],'fps':25,'shots':plan,'original_native_title_range':[340,508],'title_track':4,'real_people_action_shots':5,'first_music_changed_only':[0,40.8],'old_timeline_preserved':True,'narration_and_live_speech_unchanged':True},ensure_ascii=False,indent=2))
for x in plan:cap(p,t,(x['start']+x['end'])//2,PRE/f"初版原生_{x['start']:04d}.jpg",wait=.05)
assert t.SetCurrentTimecode(tc(0));assert pm.SaveProject();print('V21_NATIVE_BUILT',len(items),t.GetEndFrame(),flush=True)
