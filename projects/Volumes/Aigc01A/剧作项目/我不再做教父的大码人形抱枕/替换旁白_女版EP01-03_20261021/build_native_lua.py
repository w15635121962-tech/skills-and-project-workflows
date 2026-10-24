import json
from pathlib import Path
b=Path(__file__).resolve().parent
f=json.loads((b/'替换前_完整时间线实读.json').read_text())
m=json.loads((b/'42段对齐WAV_制作结果.json').read_text())
def lua(x):
    if x is None:return 'nil'
    if x is True:return 'true'
    if x is False:return 'false'
    if isinstance(x,str):return json.dumps(x,ensure_ascii=False)
    if isinstance(x,(int,float)):return repr(x)
    if isinstance(x,list):return '{'+','.join(lua(v) for v in x)+'}'
    return '{'+','.join('['+lua(str(k))+']='+lua(v) for k,v in x.items())+'}'
config={'base':str(b),'clips':m['clips'],'timelines':[{'ep':t['ep'],'name':t['name'],'id':t['id'],'start':t['start'],'end':t['end'],'old_clips':[{k:c[k] for k in ('id','start','end','enabled','properties')} for c in t['tracks']['audio'][3]['items']]} for t in f['timelines']]}
(b/'apply_narration_replacement.lua').write_text('local cfg='+lua(config)+'\n'+(b/'native_template.lua').read_text())
