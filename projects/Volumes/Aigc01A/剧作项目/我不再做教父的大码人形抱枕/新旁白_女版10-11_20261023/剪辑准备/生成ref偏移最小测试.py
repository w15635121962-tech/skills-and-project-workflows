from pathlib import Path
from lxml import etree as E
from fractions import Fraction as Q
from copy import deepcopy
import io,re,json,hashlib
P=Path(__file__).resolve().parent;T=P/'兼容测试';T.mkdir(exist_ok=True)
root=E.parse(str(P/'新时间线_EP11.fcpxml')).getroot();res=root.find('resources');p=root.find('.//project');s=p.find('sequence');p.remove(s);p.set('name','女版EP11_ref偏移最小测试_ABCD_20261023')
s=E.SubElement(p,'sequence',format='portrait_ep11',tcStart='3600s',duration='20s',tcFormat='NDF');sp=E.SubElement(s,'spine')
def st(v):
 v=Q(v);return f'{v.numerator}/{v.denominator}s'
def ref(name,offset,start,duration,points=None):
 n=E.SubElement(sp,'ref-clip',name=name,ref='core_ep11',offset=st(3600+Q(offset)),start=st(start),duration=st(duration),srcEnable='all')
 if points:
  t=E.SubElement(n,'timeMap',frameSampling='floor',preservesPitch='1')
  for x,y in points:E.SubElement(t,'timept',time=st(x),value=st(y),interp='linear')
 E.SubElement(n,'adjust-conform',type='fill')
ref('A_noTimeMap_source60to63',0,60,3)
ref('B_globalMap_halfSpeed_source60to63',3,120,6,[(0,0),(Q(198+1,1),Q(199,2))])
ref('C_start60_map60to63',9,60,6,[(0,0),(60,60),(66,63),(Q(198+1,1),Q(199,2))])
ref('D_noTimeMap_source30to35',15,30,5)
# Eliminate unreferenced outer narration assets; core refs remain.
used={n.get('ref') for n in root.iter() if n.get('ref')}
for a in list(res):
 if a.tag=='asset' and a.get('id') not in used:res.remove(a)
dtd=E.DTD(str(P/'FCPXMLv1_10.dtd'));assert dtd.validate(root),str(dtd.error_log)
out=T/'EP11_ref偏移_ABCD_20秒.fcpxml';E.indent(root,space='  ');E.ElementTree(root).write(str(out),encoding='UTF-8',xml_declaration=True,pretty_print=True,doctype='<!DOCTYPE fcpxml>')
report={'file':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'DTD_valid':True,'segments':[{'name':'A','timeline':[0,3],'source':[60,63],'method':'start=60, no timeMap'},{'name':'B','timeline':[3,9],'source':[60,63],'method':'start=120, global0to0 half-speedMap'},{'name':'C','timeline':[9,15],'source':[60,63],'method':'start=60, map60to60,66to63'},{'name':'D','timeline':[15,20],'source':[30,35],'method':'start=30, no timeMap'}],'no_original_or_frozen_source_changed':True}
(T/'测试说明.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False))
