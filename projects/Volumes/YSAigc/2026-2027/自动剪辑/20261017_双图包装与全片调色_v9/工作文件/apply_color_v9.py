from common_v9 import *
r,pm,p,mp,t=connect();assert t.GetName()==NAME
advice=json.loads((OUT/'色彩建议.json').read_text());prototype=json.loads((OUT/'native_color_prototype_v9.json').read_text())
proto={(x['track'],x['start']):x for x in prototype['samples']}
recipes={
 'priority_dim_teaching':([.988,.988,.996],[.002,.002,.002],[.94,.945,.934],.99),
 'priority_science_yellow_green':([1,.985,1.012],[0,0,0],[.992,1.002,.99],.99),
 'opening_warm_dim':([.996,.995,1.003],[0,0,0],[.973,.978,.965],.99),
 'library_density':([1,1,1],[0,0,0],[.958,.958,.958],.99),
 'later_dim_reading':([.995,.995,1.003],[0,0,0],[.951,.956,.943],.99),
 'outdoor_backlight':([1,1,1],[0,0,0],[.976,.976,.976],1.0),
}
targets={}
for group in advice['groups']:
    for x in group['targets']:
        key=(x['track'],x['record_frame']);targets[key]={'track':key[0],'start':key[1],'frame':x['examined_frame'],'recipe':recipes[group['id']],'reason':group['direction'],'group':group['id'],'before':x['image']}
for st in [5035,5096]:targets[1,st]['recipe']=([.986,.986,.994],[.003,.003,.003],[.90,.905,.894],.99)
targets[1,1067]['recipe']=([.994,.994,1.003],[0,0,0],[.955,.958,.947],.99)
for track,st,frame in [(2,11318,11340),(2,11362,11384)]:
    targets[track,st]={'track':track,'start':st,'frame':frame,'recipe':recipes['priority_science_yellow_green'],'group':'interview_science','reason':'同期讲话科学教室补画与前段同场白衣、白台面保持匹配','before':str(PRE/'调色前'/f'{track}_{st:05d}.jpg')}
targets[1,11042]={'track':1,'start':11042,'frame':11070,'recipe':([.998,.998,.998],[0,0,0],[.983,.983,.983],.99),'group':'principal_neutral','reason':'已见未覆盖校长主画面；只调明暗密度，取消通道偏色','before':proto[1,11042]['before']}
photo_recipes=[(3,3749,.97,.99),(4,1980,1.008,.99),(3,6470,.955,.99),(4,6470,.98,.99),(3,7509,.972,.98),(4,7728,.985,.99),(3,9378,.975,.99),(4,9378,.98,.99)]
for track,st,power,sat in photo_recipes:
    item=next(x for x in t.GetItemListInTrack('video',track) if x.GetStart()==st);frame=st+item.GetDuration()//2
    targets[track,st]={'track':track,'start':st,'frame':frame,'recipe':([1,1,1],[0,0,0],[power]*3,sat),'group':'photo_local_balance','reason':'单张照片轻调明暗与饱和度；不改变双图底版和另一照片','before':str(PRE/'双图实际画面'/f'{st:05d}_中.jpg')}
records=[];assert pm.SaveProject()
for key,s in sorted(targets.items()):
    it=next(x for x in t.GetItemListInTrack('video',s['track']) if x.GetStart()==s['start']);g=it.GetNodeGraph();n=g.GetNumNodes();assert n==1
    luts=[g.GetLUT(j) for j in range(1,n+1)];name='v9_自然人文校色'
    if key in proto:prior=proto[key]['prior_version'];assert it.GetCurrentVersion()['versionName']==name
    else:
        prior=it.GetCurrentVersion();assert name not in it.GetVersionNameList(0)
        assert it.AddVersion(name,0) and it.LoadVersionByName(name,0)
    slope,offset,power,sat=s['recipe'];cdl={'NodeIndex':'1','Slope':' '.join(map(str,slope)),'Offset':' '.join(map(str,offset)),'Power':' '.join(map(str,power)),'Saturation':str(sat)}
    assert it.SetCDL(cdl) and it.GetCurrentVersion()['versionName']==name
    assert [it.GetNodeGraph().GetLUT(j) for j in range(1,n+1)]==luts
    records.append(dict(s,prior_version=prior,active_version=it.GetCurrentVersion(),cdl=cdl,preserved_luts=luts))
save('native_color_applied_v9.json',{'records':records,'footage_graded':sum(x['track']<3 for x in records),'photos_graded':sum(x['track']>=3 for x in records),'frame_first':True,'prior_versions_recoverable':True,'original_luts_preserved':True})
snapshot=snap(t);packages=json.loads((OUT/'native_packages_v9.json').read_text());assert snapshot==packages['snapshot']
assert pm.SaveProject();print('V9_COLOR_APPLIED',len(records),'PICTURE_TIMING_AND_AUDIO_IDENTICAL',flush=True)
