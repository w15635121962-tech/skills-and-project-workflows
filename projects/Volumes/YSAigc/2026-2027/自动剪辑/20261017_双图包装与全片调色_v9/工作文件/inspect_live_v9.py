from common_v9 import *
r,pm,p,mp,t=connect()
assert t.GetName()=='学校_人物动态与缓推精修_v8_20261017',t.GetName()
snapshot=snap(t)
prior=json.loads((BASE/'native_build_v8.json').read_text())
assert snapshot==prior['snapshot'],'User changes detected; inspect before mutating'
settings=p.GetSetting()
graphs=[]
for k in range(1,t.GetTrackCount('video')+1):
    for it in t.GetItemListInTrack('video',k):
        g=it.GetNodeGraph();n=g.GetNumNodes() if g else 0
        graphs.append({'track':k,'start':it.GetStart(),'name':it.GetName(),'nodes':n,'luts':[g.GetLUT(j) for j in range(1,n+1)],'labels':[g.GetNodeLabel(j) for j in range(1,n+1)],'versions':it.GetVersionNameList(0),'current_version':it.GetCurrentVersion()})
record={'project':p.GetName(),'timeline':t.GetName(),'snapshot':snapshot,'page':r.GetCurrentPage(),'timecode':t.GetCurrentTimecode(),'selected_pool':[x.GetName() for x in (mp.GetSelectedClips() or [])],'markers':t.GetMarkers(),'color_settings':{k:v for k,v in settings.items() if any(s in k.lower() for s in ['color','gamma','luminance','gamut','tone','input','output'])},'graphs':graphs}
save('live_before_v9.json',record)
assert pm.SaveProject()
backup=ROOT/'学校_双图包装前_v8备份.drt';assert not backup.exists()
assert t.Export(str(backup),r.EXPORT_DRT)
new=t.DuplicateTimeline(NAME);assert new and p.SetCurrentTimeline(new)
assert snap(new)==snapshot
assert pm.SaveProject()
print('V9_RECOVERABLE_TIMELINE_READY',NAME,record['color_settings'],flush=True)
print('LUT_COUNTS', {x:sum(1 for g in graphs if x in g['luts']) for x in sorted({str(x) for g in graphs for x in g['luts']})},flush=True)
