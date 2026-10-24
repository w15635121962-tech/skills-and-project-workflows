from pathlib import Path
from fractions import Fraction as Q
from lxml import etree as E
import hashlib,json
P=Path(__file__).resolve().parent
PLAN=P/'paragraph_conform_plan_冻结_40cbc08b8e24.json';expected='40cbc08b8e244d122500a048537899757710aff26af8a6e6951a82614d1a23de'
assert hashlib.sha256(PLAN.read_bytes()).hexdigest()==expected
D=json.loads(PLAN.read_text(encoding='utf-8'))
def sec(x):return Q(str(x)).limit_denominator(24000000)
def st(x):x=Q(x);return f'{x.numerator}/{x.denominator}s'
dtd=E.DTD(str(P/'FCPXMLv1_10.dtd'))
for ep in D['episodes']:
 n=ep['episode'];r=E.parse(str(P/f'新时间线_EP{n}.fcpxml')).getroot();proj=r.find('.//project');proj.set('name',f'大码_女版_EP{n}_新旁白原速剪辑_修正版_20261023');refs=proj.findall('.//ref-clip');assert len(refs)==len(ep['events'])
 coreend=sec(ep['program_core_end_seconds']);checks=[]
 for c,ev in zip(refs,ep['events']):
  assert c.get('name').startswith(ev['event_id']+'_')
  a=Q(ev['old_core_start_frame'],24);b=Q(ev['old_core_end_frame_exclusive'],24);dur=Q(ev['proposed_duration_frames'],24);rate=(b-a)/dur
  oldmap=c.find('timeMap');c.remove(oldmap)
  if rate==1:
   c.set('start',st(a));virtual_start=a;method='directSourceStart_noTimeMap'
  else:
   virtual_start=a/rate;c.set('start',st(virtual_start));tm=E.Element('timeMap',frameSampling='optical-flow' if rate<1 else 'nearest-neighbor',preservesPitch='1');E.SubElement(tm,'timept',time='0s',value='0s',interp='linear');E.SubElement(tm,'timept',time=st(coreend/rate),value=st(coreend),interp='linear');c.insert(0,tm);method='zeroOriginFullSourceMap_virtualStart'
  assert virtual_start*rate==a and (virtual_start+dur)*rate==b
  checks.append({'event':ev['event_id'],'kind':ev['kind'],'start':st(virtual_start),'duration':st(dur),'rate':float(rate),'actual_source_start':float(a),'actual_source_end':float(b),'method':method})
 assert dtd.validate(r),str(dtd.error_log)
 out=P/f'新时间线_EP{n}_兼容修正版.fcpxml';E.indent(r,space='    ');E.ElementTree(r).write(str(out),encoding='UTF-8',xml_declaration=True,doctype='<!DOCTYPE fcpxml>',pretty_print=True)
 rr={'status':'CANDIDATE_DTD_VALID_NATIVE_COMPATIBILITY_TEST_PENDING','file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'plan_sha256':expected,'target_name':proj.get('name'),'duration_frames':ep['proposed_total_frames'],'source_offset_mathematically_checked':True,'events':checks}
 (P/f'EP{n}_兼容修正版报告.json').write_text(json.dumps(rr,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(rr,ensure_ascii=False)[:650])
