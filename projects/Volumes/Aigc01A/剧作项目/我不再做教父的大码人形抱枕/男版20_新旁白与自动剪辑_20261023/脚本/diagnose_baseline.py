from native_common import *
r,m,p,pool=connect()
b=read(BASELINE_JSON);live={t.GetUniqueId():t for t in timelines(p)};changes=[]
def diff(a,z,path=''):
 if type(a)!=type(z):return [{'path':path,'before':a,'after':z}]
 if isinstance(a,dict):
  out=[]
  for k in a.keys()|z.keys():
   if k not in a or k not in z:out.append({'path':path+'/'+k,'before':a.get(k),'after':z.get(k)})
   else:out.extend(diff(a[k],z[k],path+'/'+k))
  return out
 if isinstance(a,list):
  if len(a)!=len(z):return [{'path':path+'/length','before':len(a),'after':len(z)}]
  return [d for i,(x,y) in enumerate(zip(a,z)) for d in diff(x,y,path+'/'+str(i))]
 return [] if a==z else [{'path':path,'before':a,'after':z}]
for old in b['timeline_states']:
 if old['name']!='大码_女版_EP07':continue
 now=timeline_state(live[old['id']]);changes=diff(old['state'],now)
write(BASE/'基线差异诊断_EP07.json',{'timeline':'大码_女版_EP07','differences':changes})
print(json.dumps(changes,ensure_ascii=False))
