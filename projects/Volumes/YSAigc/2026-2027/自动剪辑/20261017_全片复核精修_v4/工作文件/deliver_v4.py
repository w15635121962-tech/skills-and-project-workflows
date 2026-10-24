import sys,json,zipfile,hashlib,math,html
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'/Users/xuan/Codex_YS_Data/CodexHome/skills/davinci-resolve/scripts')
from resolve_bootstrap import get_resolve
ROOT=Path(__file__).parents[1];OUT=ROOT/'工作文件';PRE=ROOT/'精修预览';plan=json.loads((OUT/'refined_plan_v4.json').read_text());before=json.loads((OUT/'live_before_v4.json').read_text());verification=json.loads((OUT/'native_verification_v4.json').read_text());captions=json.loads((OUT/'caption_final_timing_v4.json').read_text())
r=get_resolve();pm=r.GetProjectManager();p=pm.GetCurrentProject();assert p.GetName()=='学校';mp=p.GetMediaPool();t=p.GetCurrentTimeline();assert t.GetName()==plan['name']
def clip(it):return {'name':it.GetName(),'start':it.GetStart(),'end':it.GetEnd(),'offset':it.GetLeftOffset(),'path':it.GetMediaPoolItem().GetClipProperty('File Path') if it.GetMediaPoolItem() else None,'properties':it.GetProperty(),'enabled':it.GetClipEnabled(),'fusion_count':it.GetFusionCompCount()}
audio=[{'track':k,'enabled':t.GetIsTrackEnabled('audio',k),'locked':t.GetIsTrackLocked('audio',k),'name':t.GetTrackName('audio',k),'items':[clip(it) for it in t.GetItemListInTrack('audio',k)]} for k in range(1,5)];assert audio==before['snapshot']['audio'];items=t.GetItemListInTrack('video',1);assert len(items)==121 and t.GetEndFrame()==11507
assert items[0].GetStart()==0 and all(a.GetEnd()==b.GetStart() for a,b in zip(items,items[1:]));assert len(t.GetItemListInTrack('video',2))==1
for s,v in zip(plan['shots'],items):assert v.GetStart()==s['record_frame'] and v.GetDuration()==s['length_frames'] and v.GetMediaPoolItem().GetClipProperty('File Path')==s['path'] and v.GetMediaPoolItem().GetClipProperty('Online Status')=='Online'
for rec in captions:
 v=next(v for v in items if v.GetStart()==rec['record_frame']);c=v.GetFusionCompByIndex(1);m=c.FindTool('Merge2');assert abs(m.GetInput('Blend',rec['fusion_start']))<1e-8 and abs(m.GetInput('Blend',rec['fusion_end']))<1e-8 and abs(m.GetInput('Blend',(rec['fusion_start']+rec['fusion_end'])/2)-1)<1e-8
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',16);overview=Image.new('RGB',(1440,6*230),(245,244,240));draw=ImageDraw.Draw(overview);by={v['record_frame']:v for v in verification['midpoint_frames']};selected=[0,52,234,340,1273,1462,2263,2641,2931,3749,3954,4289,5717,5901,7211,7610,7840,8220,8768,9627,10056,10492,11042,11407];shotby={s['record_frame']:s for s in plan['shots']}
for i,frame in enumerate(selected):
 s=shotby[frame];im=Image.open(by[frame]['path']).convert('RGB');im.thumbnail((360,203));x=i%4*360;y=i//4*230;overview.paste(im,(x,y));draw.text((x+5,y+206),f"{frame/25:.2f}s  {s['chapter'][:18]}",font=font,fill=(35,40,38))
overview.save(PRE/'全片复核精修总览.jpg',quality=94)
parts=['<!doctype html><meta charset="utf-8"><title>学校宣传片全片复核精修 v4</title><style>body{max-width:1440px;margin:auto;padding:28px;background:#f5f4ef;color:#25362d;font:18px system-ui}p{line-height:1.7}img{width:100%;height:auto}audio{width:min(600px,100%)}</style><h1>学校宣传片 · 全片复核精修 v4</h1><p>7分40秒 · 121个镜头 · 完整旁白保留<br>本页为实际达芬奇时间线静态画面索引，尚未导出MP4。</p><h2>3:55 字音待确认</h2><p>源稿为“绚丽绽放”，自动识别存在“顺利”歧义，原声保留。下面为3:50–4:00的原声10秒片段。</p><audio controls preload="metadata" src="../工作文件/配音复核/01_原声_绚丽待辨_03分50至04分00.wav"></audio>']
for i in range(1,7):parts.append(f'<h2>全片画面 {i}/6</h2><img src="全片实际画面_{i}.jpg" alt="实际画面索引{i}">')
(PRE/'全片复核画面索引.html').write_text('\n'.join(parts),encoding='utf-8')
assert t.SetCurrentTimecode('00:00:00:20');assert r.OpenPage('edit');assert pm.SaveProject();archives=[]
for kind,path in [('drt',ROOT/'学校_全片复核精修_v4.drt'),('drp',ROOT/'学校_全片复核精修_v4.drp')]:
 assert not path.exists(),path;ok=t.Export(str(path),r.EXPORT_DRT) if kind=='drt' else pm.ExportProject('学校',str(path),True);assert ok and path.exists() and path.stat().st_size>1000
 with zipfile.ZipFile(path) as z:assert z.testzip() is None
 archives.append({'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'zip_integrity':'passed'})
report={'timeline':t.GetName(),'duration_seconds':460.28,'fps':25,'timeline_resolution':[1920,1080],'picture_count':121,'picture_revisions':16,'revised_picture_segments':17,'refined_title_count':6,'all_picture_online':True,'picture_contiguous':True,'audio_snapshot_identical_to_v3':True,'narration_duration_seconds':433.6588125,'narration_timeline_end_seconds':433.68,'actual_midpoint_frames':121,'revised_picture_edge_frames':34,'final_caption_samples':30,'source_rate_caption_clocks_corrected':True,'rhythm_metrics':plan['rhythm_metrics'],'archives':archives,'versions_preserved':[p.GetTimelineByIndex(i).GetName() for i in range(1,p.GetTimelineCount()+1)],'voice_review_pending':{'frame':5880,'word':'绚丽/顺利','status':'unconfirmed; original preserved; optional user listening response pending'},'limitations':['No full perceptual audio listen or continuous final video watch-through','No final MP4 render','Mixed archive resolution and primarily 720p shooting proxies; reconnect original media for high resolution delivery']}
(OUT/'final_delivery_v4.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print('V4_DELIVERED',json.dumps({'timeline':report['timeline'],'seconds':460.28,'pictures':121,'archives':archives},ensure_ascii=False),flush=True)
