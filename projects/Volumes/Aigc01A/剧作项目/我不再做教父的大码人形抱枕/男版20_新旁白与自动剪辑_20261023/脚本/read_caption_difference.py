from native_common import *
from insert_srt import parse_srt,native_cues
r,m,p,pool=connect();t=p.GetCurrentTimeline();assert t.GetName()==TIMELINE
plan=load_plan(BASE/'final_native_plan_含SRT.json');expected=parse_srt(plan['episodes'][0]['subtitle_srt']);actual=native_cues(t)
report={'timeline':t.GetName(),'id':t.GetUniqueId(),'expected':expected,'actual':actual,'differences':[{'index':i,'expected':a,'actual':b} for i,(a,b) in enumerate(zip(expected,actual)) if a!=b],'counts':[len(expected),len(actual)]}
write(BASE/'字幕/导入差异_首次实读.json',report)
print(json.dumps({k:report[k] for k in ['timeline','counts','differences']},ensure_ascii=False))
