"""Audio-only external-media AAF25 + FCPXML1.10, never connects Resolve."""
from pathlib import Path
from fractions import Fraction
import hashlib
import importlib.metadata
import json
import struct
import urllib.parse
import wave
import xml.etree.ElementTree as ET
import aaf2
from aaf2.ama import get_wave_fmt,create_network_locator

ROOT=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_画面缓推与旁白气口精修_v14')
WORK=ROOT/'工作文件';OUT=ROOT/'音频交换文件';OUT.mkdir(exist_ok=True)
PLAN=json.loads((WORK/'native_segments_v14.json').read_text())
WAV=Path(PLAN['path']).resolve();SEGMENTS=PLAN['native_segments'];GAPS=PLAN['intentional_A1_gaps']
FPS,SR,SPF=25,48000,1920
AAF=OUT/'旁白气口_A1_25fps精确回装_v14.aaf'
XML=OUT/'旁白气口_A1_25fps精确回装_v14.fcpxml'
assert not AAF.exists() and not XML.exists()
before_hash=hashlib.sha256(WAV.read_bytes()).hexdigest()
with wave.open(str(WAV),'rb') as w:
    assert w.getparams()[:3]==(2,3,SR);samples=w.getnframes()
events=[{'type':'clip','start':r['record_start_frame'],'end':r['record_end_frame_exclusive'],
         'source_start':r['source_start_frame'],'index':r['index']} for r in SEGMENTS]
events +=[{'type':'filler','start':r['start'],'end':r['end'],'pair_id':r['pair_id']} for r in GAPS]
events.sort(key=lambda r:r['start']);assert len(events)==34
cursor=0
for e in events:assert e['start']==cursor;cursor=e['end']
assert cursor==10842

with aaf2.open(str(AAF),'w') as f:
    physical=f.create.SourceMob(WAV.name)
    f.content.mobs.append(physical)
    file_slot=physical.create_empty_slot(SR,media_kind='sound',slot_id=1)
    file_slot.name='External 48kHz 24bit stereo PCM WAV'
    file_slot.segment.length=samples
    file_slot['PhysicalTrackNumber'].value=1
    descriptor=f.create.WAVEDescriptor()
    descriptor['SampleRate'].value=SR
    descriptor['Length'].value=samples
    descriptor['Summary'].value=get_wave_fmt(str(WAV))
    descriptor['ContainerFormat'].value=f.dictionary.lookup_containerdef('AAF')
    descriptor['Locator'].append(create_network_locator(f,str(WAV)))
    physical.descriptor=descriptor
    master=f.create.MasterMob(WAV.name)
    f.content.mobs.append(master)
    ms=master.create_timeline_slot(SR,slot_id=1)
    ms.name='Stereo PCM full source at 48000 samples per second'
    ms['PhysicalTrackNumber'].value=1
    ms.segment=physical.create_source_clip(1,start=0,length=samples,media_kind='sound')
    comp=f.create.CompositionMob('旁白气口_A1_25fps精确回装_v14')
    comp.usage='Usage_TopLevel';f.content.mobs.append(comp)
    a1=comp.create_sound_slot(FPS);a1.name='A1 旁白_23语义块_11气口'
    a1['PhysicalTrackNumber'].value=1
    sequence=a1.segment
    for e in events:
        n=e['end']-e['start']
        if e['type']=='filler':
            component=f.create.Filler(media_kind='sound',length=n)
        else:
            # AAF SourceClip.StartTime/Length are in the OWNING slot's units:
            # composition25 here. The referenced 48000Hz master/file slot
            # converts each frame exactly to 1920 PCM samples (AAF spec).
            component=master.create_source_clip(1,start=e['source_start'],length=n,media_kind='sound')
        sequence.components.append(component)
    sequence.length=10842

# Read the saved AAF back from disk and traverse its actual objects/rates.
read_events=[];locator_urls=[]
with aaf2.open(str(AAF),'r') as f:
    comps=list(f.content.toplevel());assert len(comps)==1
    comp=comps[0];assert len(comp.slots)==1
    slot=comp.slots[0];assert slot.media_kind=='Sound' and Fraction(slot.edit_rate)==FPS
    cursor=0
    for component in slot.segment.components:
        n=int(component.length);row={'type':'filler' if isinstance(component,aaf2.components.Filler) else 'clip',
                                    'record_start_frame':cursor,'record_end_frame_exclusive':cursor+n,
                                    'duration_frames':n,'owning_edit_rate':str(slot.edit_rate)}
        if row['type']=='clip':
            assert isinstance(component,aaf2.components.SourceClip)
            master=component.mob;ms=component.slot
            assert isinstance(master,aaf2.mobs.MasterMob)
            source_offset=Fraction(component.start)*Fraction(ms.edit_rate)/Fraction(slot.edit_rate)
            link=ms.segment;physical=link.mob;file_slot=link.slot
            # The master slot is sample-clocked; StartTime on its source link
            # has that clock, and its zero offset preserves source identity.
            source_offset += Fraction(link.start)
            file_sample=source_offset*Fraction(file_slot.edit_rate)/Fraction(ms.edit_rate)
            d=physical.descriptor
            assert isinstance(d,aaf2.essence.WAVEDescriptor)
            assert Fraction(d['SampleRate'].value)==SR and int(d['Length'].value)==samples
            assert file_sample.denominator==1
            duration_samples=Fraction(n)*SR/FPS;assert duration_samples.denominator==1
            urls=[v['URLString'].value for v in d['Locator'].value]
            assert urls==[WAV.as_uri()]
            locator_urls.extend(urls)
            summary=bytes(d['Summary'].value)
            assert summary[:4]==b'RIFF' and summary[8:12]==b'WAVE' and summary[12:16]==b'fmt '
            fmt=struct.unpack('<HHIIHH',summary[20:36]);assert fmt==(1,2,SR,SR*6,6,24)
            row.update({'source_start_frame_25fps':int(component.start),
                        'source_start_sample':int(file_sample),
                        'source_end_sample_exclusive':int(file_sample+duration_samples),
                        'master_slot_edit_rate':str(ms.edit_rate),
                        'file_slot_edit_rate':str(file_slot.edit_rate),
                        'external_wav_path':str(WAV),'descriptor':'WAVEDescriptor',
                        'riff_channels':fmt[1],'riff_sample_rate':fmt[2],'riff_bits':fmt[5]})
        read_events.append(row);cursor+=n
    assert cursor==10842 and int(slot.segment.length)==10842
    assert len(list(f.content.essencedata))==0
    assert len(list(f.content.mobs))==3
    assert all(s.media_kind=='Sound' for m in f.content.mobs for s in m.slots)
for planned,read in zip(events,read_events):
    assert (planned['start'],planned['end'],planned['type'])==(read['record_start_frame'],read['record_end_frame_exclusive'],read['type'])
    if read['type']=='clip':assert read['source_start_sample']==planned['source_start']*SPF

def time_fraction(n,d):
    v=Fraction(n,d)
    return f'{v.numerator}/{v.denominator}s' if v.denominator!=1 else f'{v.numerator}s'

root=ET.Element('fcpxml',version='1.10')
resources=ET.SubElement(root,'resources')
ET.SubElement(resources,'format',id='r1',name='FFVideoFormat1080p25',frameDuration='1/25s',width='1920',height='1080')
asset=ET.SubElement(resources,'asset',id='r2',name=WAV.name,start='0s',duration=time_fraction(samples,SR),
                    hasVideo='0',hasAudio='1',audioSources='1',audioChannels='2',audioRate=str(SR),format='r1')
ET.SubElement(asset,'media-rep',kind='original-media',src=WAV.as_uri())
library=ET.SubElement(root,'library');event=ET.SubElement(library,'event',name='旁白气口_A1精确回装_v14')
project=ET.SubElement(event,'project',name='旁白气口_A1_25fps精确回装_v14')
sequence=ET.SubElement(project,'sequence',format='r1',duration='10842/25s',tcStart='0s',tcFormat='NDF',audioLayout='stereo',audioRate='48k')
spine=ET.SubElement(sequence,'spine')
for e in events:
    common={'offset':time_fraction(e['start'],FPS),'duration':time_fraction(e['end']-e['start'],FPS)}
    if e['type']=='filler':
        ET.SubElement(spine,'gap',name='原生气口静音_'+e['pair_id'],start='0s',**common)
    else:
        ET.SubElement(spine,'asset-clip',ref='r2',name=f'旁白语义块_{e["index"]:02d}',
                      start=f'{e["source_start"]*SPF}/48000s',srcEnable='audio',audioRole='dialogue',format='r1',**common)
ET.indent(root,space='  ')
XML.write_bytes(b'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE fcpxml>\n'+ET.tostring(root,encoding='utf-8')+b'\n')

# Independent XML disk readback with exact rational-to-sample arithmetic.
xml=ET.parse(XML);assert xml.getroot().get('version')=='1.10'
clips=xml.findall('.//spine/asset-clip');fillers=xml.findall('.//spine/gap')
assert len(clips)==23 and len(fillers)==11
def seconds(v):return Fraction(v[:-1])
for a,b in zip(clips,SEGMENTS):
    assert seconds(a.get('offset'))*FPS==b['record_start_frame']
    assert seconds(a.get('start'))*SR==b['source_start_frame']*SPF
    assert seconds(a.get('duration'))*FPS==b['duration_frames']
assert seconds(xml.find('.//sequence').get('duration'))*FPS==10842
assert [r.get('src') for r in xml.findall('.//media-rep')]==[WAV.as_uri()]
assert not xml.findall('.//video')
assert hashlib.sha256(WAV.read_bytes()).hexdigest()==before_hash
report={'status':'passed_offline_readback_pending_Resolve_import_test','aaf':str(AAF),'fcpxml':str(XML),
        'pyaaf2_version':importlib.metadata.version('pyaaf2'),'installed_into':'/Users/xuan/.local/share/promo-audio/venv',
        'timeline_edit_rate':25,'audio_sample_rate':48000,'audio_channels':2,'audio_bits':24,
        'timeline_frames':10842,'timeline_seconds':433.68,'source_file_samples':samples,
        'source_file_seconds':samples/SR,'source_wav':str(WAV),'source_wav_sha256_unchanged':before_hash,
        'aaf_readback':{'composition_audio_tracks':1,'picture_tracks':0,'sourceclips':23,'fillers':11,
                        'external_wav_only':True,'embedded_essence_count':0,'buses_or_effects_added':False,
                        'events':read_events,'unique_locator_urls':sorted(set(locator_urls))},
        'fcpxml_readback':{'version':'1.10','asset_clips':len(clips),'gaps':len(fillers),
                           'all_source_samples_and_record_frames_exact':True,'external_wav_only':True},
        'critical_clock_note':'AAF SourceClip StartTime and Length use the owning slot edit rate (25fps composition), NOT the referenced 48000Hz slot. Conversion at reference traversal is exactly 1920 samples per frame. Master/File SourceMob slots retain the complete 48000Hz source sample clock.',
        'reference_sources':['https://aaf.sourceforge.net/docs/aafObjectModel.pdf',
                            'https://github.com/markreidvfx/pyaaf2',
                            'https://pyaaf.readthedocs.io/en/stable/api/aaf2.ama.html',
                            'https://developer.apple.com/documentation/professional-video-applications/creating-fcpxml-documents'],
        'resolve_connected_or_modified':False,'original_audio_modified':False,
        'import_test_completed':False,
        'limitation':'Offline object/rational/sample readback passed; Resolve import behavior and stereo track interpretation require the parent\'s temporary-timeline test.'}
(WORK/'audio_interchange_qa_v14.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'status':report['status'],'aaf':str(AAF),'fcpxml':str(XML),'qa':str(WORK/'audio_interchange_qa_v14.json'),
                  'frames':10842,'clips':23,'fillers':11,'audio_only':True},ensure_ascii=False),flush=True)
