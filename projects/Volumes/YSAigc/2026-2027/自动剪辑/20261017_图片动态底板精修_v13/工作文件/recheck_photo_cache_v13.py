from common_v13 import *
r,pm,p,mp,t=connect();assert t.GetName()==TIMELINE;assert r.OpenPage('edit')
parent=next(p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1) if p.GetTimelineByIndex(i).GetName()==PARENT)
assert p.SetCurrentTimeline(parent);g=next(x for x in GROUPS if x['start']==9960)
for label,frame in [('first',9960),('mid',9960+g['length']//2),('last',9960+g['length']-1)]:
 cap(p,parent,frame,PRE/'原版保留检查'/f'9960_{label}.jpg',1)
assert p.SetCurrentTimeline(t);assert pm.SaveProject()
