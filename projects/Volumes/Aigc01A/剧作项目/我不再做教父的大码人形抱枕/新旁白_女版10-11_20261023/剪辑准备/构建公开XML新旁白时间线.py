# -*- coding: utf-8 -*-
"""Build only new task-local FCPXML files. Never connects to Resolve or changes sources."""
from pathlib import Path
from fractions import Fraction as Q
from copy import deepcopy
from lxml import etree as E
import json,re,hashlib,io,urllib.parse,datetime
P=Path(__file__).resolve().parent
PLAN=P/'paragraph_conform_plan.json'
D=json.loads(PLAN.read_text(encoding='utf-8'))
DTDMD=(P/'FCPXML1.10_AppleDTD.md').read_text(encoding='utf-8')
DTDSTR=re.search(r'```swift\n(.*?)\n```',DTDMD,re.S).group(1)
(P/'FCPXMLv1_10.dtd').write_text(DTDSTR,encoding='utf-8')
DTD=E.DTD(io.StringIO(DTDSTR))
def sec(x):
 if x is None:return Q(0)
 return Q(x[:-1]) if isinstance(x,str) and x.endswith('s') else Q(str(x)).limit_denominator(24000000)
def st(x):
 x=sec(x);return f'{x.numerator}/{x.denominator}s'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def sourcepath(a):return Path(urllib.parse.unquote(urllib.parse.urlparse(a.find('media-rep').get('src')).path))
def nodetime(n,k,default=0):return sec(n.get(k,str(default)+'s'))
FILL={
10:[
 {'start':Q(475,24),'end':Q(635,24),'sources':[('抱枕女-10-02-01.mp4',Q(0),Q(36,24)),('抱枕女-10-02-01.mp4',Q(77,24),Q(41,24)),('抱枕女-10-02-01.mp4',Q(140,24),Q(48,24)),('抱枕女-10-02-01.mp4',Q(270,24),Q(35,24))], 'reason':'Cold mother close-up, contract/hands insert, mother seated, Eliza closed-mouth reaction; same sitting room, inspected contact sheet EP10_03.'},
 {'start':Q(1194,24),'end':Q(1247,24),'sources':[('抱枕女-10-04-01.mp4',Q(275,24),Q(53,24))], 'reason':'Professor behind desk, letter handover flashback during narration about research recommendation; contact EP10_07 at12s.'},
 {'start':Q(1838,24),'end':Q(1882,24),'sources':[('抱枕女10-06-01.mp4',Q(288,24),Q(44,24))], 'reason':'Eliza turns away outside estate, existing nighttime end-scene, contact EP10_09 at12-13.84s.'},
],
11:[
 {'start':Q(757,24),'end':Q(845,24),'sources':[('抱枕女 11-04-01.mp4',Q(72,24),Q(50,24)),('抱枕女 11-03-01.mp4',Q(185,24),Q(38,24))], 'reason':'Existing waist bruise insert then Eliza reacting in the same bed before Matteo frowns. Contact sheets EP11_05 at4s andEP11_04 at8s.'}
]}
reports=[]
for ep in D['episodes']:
 n=ep['episode'];src=P/f'原时间线_EP{n}.fcpxml/Info.fcpxml';root=E.parse(str(src)).getroot();res=root.find('resources');project=root.find('.//project');seq=project.find('sequence');core=deepcopy(seq);sp=core.find('spine');allassets={a.get('id'):a for a in res.findall('asset')};byn={a.get('name'):a for a in res.findall('asset') if a.get('hasVideo')=='1'};coreend=sec(ep['program_core_end_seconds']);duration=Q(ep['proposed_total_frames'],24)
 removed=[];music=[]
 # Strip only known old narrator files and original music instance, never actor/SMS MP4 audio.
 old=re.compile(r'^抱枕女\s*'+str(n)+r'-\s*\(\d+\)\.mp3$')
 def strip(p):
  for c in list(p):
   name=c.get('name','')
   if c.tag in ('asset-clip','audio','clip') and (old.match(name) or name=='andriih-sad-sad-music-601661.mp3'):
    if name.startswith('andriih'):music.append(deepcopy(c))
    removed.append({'name':name,'ref':c.get('ref'),'kind':'music' if name.startswith('andriih') else 'old_narration','duration':c.get('duration')});p.remove(c);continue
   strip(c)
   if c.tag=='spine' and len(c)==0:p.remove(c)
 strip(core)
 # Reset only primary story coordinate origin; children remain in their source-local domains.
 for c in list(sp):
  oldoffset=nodetime(c,'offset')-Q(3600);c.set('offset',st(oldoffset))
  if oldoffset>=coreend:sp.remove(c);continue
  if oldoffset+nodetime(c,'duration')>coreend:c.set('duration',st(coreend-oldoffset))
 core.set('tcStart','0/1s');core.set('duration',st(coreend))
 fills=[]
 for fill in FILL[n]:
  # A final gap may have been clipped to the program core end above.
  matches=[c for c in sp if c.tag=='gap' and nodetime(c,'offset')==fill['start']]
  assert len(matches)==1,(n,fill,matches)
  g=matches[0];assert nodetime(g,'duration')==fill['end']-fill['start'];ix=list(sp).index(g);sp.remove(g);cursor=fill['start']
  for name,start,dur in fill['sources']:
   a=byn[name];assert start>=0 and start+dur<=nodetime(a,'duration')
   c=E.Element('asset-clip',name=name,ref=a.get('id'),offset=st(cursor),start=st(start),duration=st(dur),srcEnable='video',enabled='1',format=a.get('format'))
   E.SubElement(c,'adjust-transform',anchor='0 0',scale='1 1',position='0 0');sp.insert(ix,c);ix+=1
   fills.append({'old_core_start_seconds':float(cursor),'old_core_end_seconds':float(cursor+dur),'source_path':str(sourcepath(a)),'source_start_seconds':float(start),'source_end_seconds':float(start+dur),'audio':'video_only_no_invented_dialogue','reason':fill['reason']});cursor+=dur
  assert cursor==fill['end']
 # No gaps remain in the program's primary video and no editorial Text+ is introduced.
 assert not [x for x in sp if x.tag=='gap'],(n,'unexpected primary picture gap')
 coreid=f'core_ep{n}';med=E.SubElement(res,'media',id=coreid,name=f'EP{n}_原生画面与同期声_去旧旁白')
 med.append(core)
 outformat=E.SubElement(res,'format',id=f'portrait_ep{n}',name='FFVideoFormatRateUndefined',width='1080',height='1920',frameDuration='1/24s')
 project.set('name',f'大码_女版_EP{n}_新旁白原速剪辑_20261023')
 project.remove(seq)
 newseq=E.SubElement(project,'sequence',format=outformat.get('id'),duration=st(duration),tcStart='3600/1s',tcFormat='NDF',audioLayout='stereo',audioRate='48k')
 newsp=E.SubElement(newseq,'spine');base=E.SubElement(newsp,'gap',name='原速旁白与原生同期声拼接',offset='3600/1s',start='0/1s',duration=st(duration))
 # Outer gap keeps 100% VO outside the retimed reference clip's local clock.
 voassets={};coverage={};eventreport=[]
 for ev in ep['events']:
  dur=Q(ev['proposed_duration_frames'],24);pos=Q(ev['proposed_record_relative_frame'],24);a=sec(ev['old_core_start_seconds']);b=sec(ev['old_core_end_seconds_exclusive'])
  ref=E.SubElement(base,'ref-clip',lane='1',name=f"{ev['event_id']}_{ev['kind']}",ref=coreid,offset=st(pos),start='0/1s',duration=st(dur),srcEnable='all')
  tm=E.SubElement(ref,'timeMap',frameSampling='optical-flow' if ev['kind'].startswith('narration') else 'floor',preservesPitch='1')
  E.SubElement(tm,'timept',time='0/1s',value=st(a),interp='linear');E.SubElement(tm,'timept',time=st(dur),value=st(b),interp='linear')
  E.SubElement(ref,'adjust-conform',type='fill')
  if ev['kind'] in ('character_dialogue','written_message'):assert b-a==dur,(n,ev['event_id'],'protected 1:1 violation',b-a,dur)
  for voice in ev.get('new_narration',[]):
   path=Path(voice['source_path']);key=str(path)
   if key not in voassets:
    ident=f'voice_{n}_{len(voassets)+1}';item=next(x for x in ep['new_source_files'] if x['path']==key)
    assert sha(path)==item['sha256'];aelem=E.SubElement(res,'asset',id=ident,name=path.name,hasVideo='0',hasAudio='1',audioSources='1',audioChannels='1',audioRate='24000',start='0/1s',duration=st(item['duration_seconds']))
    E.SubElement(aelem,'media-rep',kind='original-media',src=path.as_uri());voassets[key]=ident;coverage[key]=[]
   so=sec(voice['source_start_seconds']);se=sec(voice['source_end_seconds_exclusive']);vp=sec(voice['proposed_record_start_seconds']);vd=se-so
   c=E.SubElement(base,'asset-clip',lane='-2',name=path.name,ref=voassets[key],offset=st(vp),start=st(so),duration=st(vd),audioRole='dialogue.narration',srcEnable='audio',enabled='1')
   E.SubElement(c,'adjust-volume',amount=f"{voice['gain_recommendation_db']:.2f}dB")
   coverage[key].append([float(so),float(se)]);assert vp>=pos and vp+vd<=pos+dur
  eventreport.append({'event_id':ev['event_id'],'kind':ev['kind'],'new_start':float(pos),'new_duration':float(dur),'core_start':float(a),'core_end':float(b),'picture_speed':float((b-a)/dur),'protected_1_to_1':ev['kind'] in ('character_dialogue','written_message'),'new_narration_segments':len(ev.get('new_narration',[]))})
 if music:
  m=music[0];m.set('lane','-3');m.set('offset','0/1s');m.set('duration',st(duration));m.set('start','0/1s');m.set('srcEnable','audio');m.set('audioRole','music')
  av=E.SubElement(m,'adjust-volume',amount='0dB');pa=E.SubElement(av,'param',name='volume',value='0dB');E.SubElement(pa,'fadeIn',duration='1/1s',type='easeIn');E.SubElement(pa,'fadeOut',duration='1/1s',type='easeOut');base.append(m)
 for x in ep['new_source_files']:
  cov=sorted(coverage[x['path']]);assert abs(cov[0][0])<1e-7 and abs(cov[-1][1]-x['duration_seconds'])<1e-7
  assert all(abs(a[1]-b[0])<1e-7 for a,b in zip(cov,cov[1:])),('source partitions',cov)
 # Remove unused narrator resource declarations to avoid accidental relink/import ambiguity.
 used={x.get('ref') for x in root.iter() if x.get('ref')}
 for a in list(res):
  if a.tag=='asset' and a.get('id') not in used:res.remove(a)
 sourcechecks=[{'name':a.get('name'),'path':str(sourcepath(a)),'exists':sourcepath(a).exists()} for a in res.findall('asset')]
 assert all(x['exists'] for x in sourcechecks)
 outfile=P/f'新时间线_EP{n}.fcpxml'
 E.indent(root,space='    ')
 valid=DTD.validate(root)
 (P/f'EP{n}_XML_DTD校验.txt').write_text(str(DTD.error_log),encoding='utf-8')
 assert valid,(n,str(DTD.error_log))
 E.ElementTree(root).write(str(outfile),encoding='UTF-8',xml_declaration=True,doctype='<!DOCTYPE fcpxml>',pretty_print=True)
 report={'status':'FILE_BUILT_DTD_VALID_NOT_YET_NATIVE_IMPORTED','episode':n,'target_name':project.get('name'),'path':str(outfile),'sha256':sha(outfile),'plan_sha256':sha(PLAN),'outer_duration_seconds':float(duration),'outer_duration_frames':int(duration*24),'core_duration_seconds':float(coreend),'native_core_primary_items':len(sp),'outer_picture_event_count':len(eventreport),'new_voice_file_count':len(voassets),'new_voice_segments':sum(x['new_narration_segments'] for x in eventreport),'all_new_voice_source_samples_partitioned_once':True,'voice_rate_percent':100,'voice_gain':'Only constant gain recommendation toward -18LUFS from measured source; no time stretch','source_checks':sourcechecks,'removed_inner_instances':removed,'gap_fills':fills,'events':eventreport,'source_coverage':coverage,'notes':['No original timeline or source file mutated.','Public XML core preserves original supported J/L edits, source transforms, retime/timeMap and synchronous actor/video audio.','All original narrator instances removed; new VO placed as independent outer-gap audio, not under picture timeMap.','All6Text+ editor notes remain excluded, as omitted by native public XML export.','OriginalEP10music normal speed0dB, native1s fade recreated plus1s endfade; EP11does not add BGM.','Portrait outer1080x1920; original core format kept, ref clip adjust-conform fill. Native import/retime/framing/audio must be checked by root.']}
 (P/f'EP{n}_新时间线XML报告.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');reports.append(report)
 print(json.dumps({k:report[k] for k in ['episode','path','sha256','outer_duration_seconds','native_core_primary_items','outer_picture_event_count','new_voice_segments']},ensure_ascii=False),flush=True)
(P/'新时间线XML汇总.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2),encoding='utf-8')
