from native_common import *
r,m,p,pool=connect();new=p.GetCurrentTimeline();assert new.GetName()==TIMELINE
old=next(t for t in timelines(p) if t.GetName()=='大码_女版_EP03')
def sample(t):
 x=(t.GetItemListInTrack('audio',4) or [])[0]
 return {'timeline':t.GetName(),'track_enabled':[t.GetIsTrackEnabled('video',1),t.GetIsTrackEnabled('audio',4),t.GetIsTrackEnabled('subtitle',1)],'properties_keys':list((x.GetProperty() or {}).keys()),'clip_id':x.GetUniqueId(),'clip_start':x.GetStart(),'clip_end':x.GetEnd()}
report={'inactive_before':sample(old)}
try:
 assert p.SetCurrentTimeline(old)
 report['active_readback']=sample(old)
finally:
 assert p.SetCurrentTimeline(new)
report['inactive_after_restore']=sample(old)
write(BASE/'诊断/活动与非活动时间线上下文回读差异.json',report)
print(json.dumps(report,ensure_ascii=False))
