"""Create a new PCM edit using verified digital-zero pauses only. Offline."""
from pathlib import Path
import copy
import hashlib
import json
import wave
import numpy as np

ROOT=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_画面缓推与旁白气口精修_v14')
WORK=ROOT/'工作文件'; AUDIO=ROOT/'旁白与混音'; LISTEN=ROOT/'气口试听'
AUDIO.mkdir(exist_ok=True); LISTEN.mkdir(exist_ok=True)
PLAN=json.loads((WORK/'旁白气口精修建议_v14.json').read_text())
SOURCE=Path(PLAN['sources']['current_native_a1'])
OUTPUT=AUDIO/'01_完整旁白_气口精修_v14_48k24.wav'
SR,FPS,SPF,BPF=48000,25,1920,6
assert not OUTPUT.exists(), OUTPUT

def pcm24_decode(raw):
    b=np.frombuffer(raw,np.uint8).reshape(-1,3).astype(np.int32)
    z=b[:,0]|b[:,1]<<8|b[:,2]<<16
    return np.where(z&0x800000,z-0x1000000,z).reshape(-1,2)

def pcm24_encode(z):
    z=np.asarray(z,np.int32).reshape(-1)
    b=np.column_stack((z&255,(z>>8)&255,(z>>16)&255)).astype(np.uint8)
    return b.tobytes()

def write_wav(path,raw):
    assert not path.exists(), path
    with wave.open(str(path),'wb') as h:
        h.setnchannels(2);h.setsampwidth(3);h.setframerate(SR);h.writeframes(raw)

with wave.open(str(SOURCE),'rb') as h:
    params=h.getparams();assert params[:3]==(2,3,SR)
    original=h.readframes(h.getnframes())
full_samples=len(original)//BPF
parts=[];mapping=[];actions=[];cursor=0;target=0
def retain(end):
    global cursor,target
    if end>cursor:
        parts.append(original[cursor*BPF:end*BPF])
        mapping.append({'kind':'retained_original_samples','source_start_sample':cursor,
                        'source_end_sample':end,'target_start_sample':target,
                        'target_end_sample':target+end-cursor,'speed':1.0,'gain':1.0})
        target+=end-cursor;cursor=end

for recommendation in PLAN['actions']:
    a=copy.deepcopy(recommendation);s=a['source_start_sample'];e=a['source_end_sample']
    retain(s)
    a['actual_new_timeline_frame']=target//SPF
    a['actual_new_timeline_seconds']=target/SR
    a['actual_new_timeline_sample']=target
    if a['delta_frames']<0:
        assert e-s==-a['delta_samples']
        assert not any(original[(s-SPF)*BPF:(e+SPF)*BPF]), a['id']
        mapping.append({'kind':'removed_digital_zero','source_start_sample':s,
                        'source_end_sample':e,'target_join_sample':target})
        cursor=e
    else:
        assert not any(original[(s-240)*BPF:(s+240)*BPF]), a['id']
        n=a['delta_samples'];parts.append(bytes(n*BPF))
        mapping.append({'kind':'inserted_digital_zero','source_cut_sample':s,
                        'target_start_sample':target,'target_end_sample':target+n})
        a['actual_new_gap_start_frame']=target//SPF
        a['actual_new_gap_end_frame']=(target+n)//SPF
        target+=n
    actions.append(a)
retain(full_samples)
edited=bytearray(b''.join(parts));assert len(edited)==len(original)
crossfades=[]
for a in actions:
    if a['delta_frames']>=0:continue
    s,e=a['source_start_sample'],a['source_end_sample']
    join=a['actual_new_timeline_sample'];n=2*SPF
    left=pcm24_decode(original[(s-SPF)*BPF:(s+SPF)*BPF])
    right=pcm24_decode(original[(e-SPF)*BPF:(e+SPF)*BPF])
    assert not np.any(left) and not np.any(right)
    incoming=np.linspace(0.,1.,n);outgoing=1.-incoming
    mixed=np.rint(left*outgoing[:,None]+right*incoming[:,None]).astype(np.int32)
    assert not np.any(mixed)
    edited[(join-SPF)*BPF:(join+SPF)*BPF]=pcm24_encode(mixed)
    crossfades.append({'action_id':a['id'],'pair_id':a['pair_id'],
                      'type':'linear_equal_gain_0dB','center_target_frame':join//SPF,
                      'duration_frames':2,'duration_samples':n,'duration_seconds':.08,
                      'target_start_sample':join-SPF,'target_end_sample':join+SPF,
                      'outgoing_original_source_sample_range':[s-SPF,s+SPF],
                      'incoming_original_source_sample_range':[e-SPF,e+SPF],
                      'outgoing_and_incoming_all_exact_zero':True,
                      'linear_gain_sum_error_max':float(np.max(np.abs(outgoing+incoming-1))),
                      'additional_duration_change_samples':0})
write_wav(OUTPUT,edited)

# Verify actual newly written PCM, in order, with direct array equality rather
# than an energy proxy or recognizer. Chunk boundaries do not affect matching.
def nonzero_blocks(path):
    with wave.open(str(path),'rb') as h:
        while True:
            raw=h.readframes(SR*10)
            if not raw:break
            rows=np.frombuffer(raw,np.uint8).reshape(-1,BPF)
            kept=rows[np.any(rows!=0,axis=1)]
            if len(kept):yield kept

old_iter,new_iter=iter(nonzero_blocks(SOURCE)),iter(nonzero_blocks(OUTPUT))
old=next(old_iter,None);new=next(new_iter,None);compared=0
old_hash,new_hash=hashlib.sha256(),hashlib.sha256()
while old is not None and new is not None:
    n=min(len(old),len(new));assert np.array_equal(old[:n],new[:n]),'Nonzero PCM changed'
    old_hash.update(old[:n].tobytes());new_hash.update(new[:n].tobytes());compared+=n
    old=old[n:];new=new[n:]
    if not len(old):old=next(old_iter,None)
    if not len(new):new=next(new_iter,None)
assert old is None and new is None
with wave.open(str(OUTPUT),'rb') as h:
    assert h.getparams()==params
    reread=h.readframes(h.getnframes())
    assert reread==edited
clip_end=10842
gaps=[{'start':a['actual_new_gap_start_frame'],'end':a['actual_new_gap_end_frame'],
       'pair_id':a['pair_id'],'action_id':a['id']} for a in actions if a['delta_frames']>0]
remove_joins=[a['actual_new_timeline_frame'] for a in actions if a['delta_frames']<0]
boundaries=sorted(set([0,clip_end,*remove_joins,*[p for g in gaps for p in (g['start'],g['end'])]]))
native=[]
for start,end in zip(boundaries,boundaries[1:]):
    if any(g['start']<=start and end<=g['end'] for g in gaps):continue
    native.append({'index':len(native)+1,'path':str(OUTPUT),'source':str(OUTPUT),
                   'source_start_frame':start,'source_end_frame_exclusive':end,
                   'record_start_frame':start,'record_end_frame_exclusive':end,
                   'duration_frames':end-start,'track':1,
                   'audio_sample_start':start*SPF,'audio_sample_end_exclusive':end*SPF,
                   'speed':1.0,'gain':1.0})
assert len(native)==23 and native[0]['record_start_frame']==0 and native[-1]['record_end_frame_exclusive']==10842
assert sum(n['duration_frames'] for n in native)+sum(g['end']-g['start'] for g in gaps)==10842

def remap_sample(t):
    p=t*SR;delta=0
    for a in actions:
        s,e=a['source_start_sample'],a['source_end_sample']
        if a['delta_frames']<0:
            if s<=p<e:return (s+delta)
            if p>=e:delta+=a['delta_samples']
        elif p>=s:delta+=a['delta_samples']
    return p+delta

def remap_records(records):
    out=[]
    for original_record in records:
        r=copy.deepcopy(original_record)
        for key in ('start','end'):
            if key in r:
                r['original_source_'+key]=r[key]
                r[key]=remap_sample(r[key])/SR
                r['new_timeline_'+key+'_frame']=r[key]*FPS
        if 'words' in r:r['words']=remap_records(r['words'])
        out.append(r)
    return out

reference=json.loads(Path(PLAN['sources']['word_reference']).read_text())
independent=json.loads(Path(PLAN['sources']['independent_noninterpolated_asr']).read_text())
chapters=remap_records(reference['chapters'])
for c,old_c in zip(chapters,reference['chapters']):
    assert c['start']==old_c['start'] and c['end']==old_c['end']
for g in gaps:assert not any(edited[g['start']*SPF*BPF:g['end']*SPF*BPF])
assert original[clip_end*SPF*BPF:]==edited[clip_end*SPF*BPF:]
native_path=WORK/'native_segments_v14.json'
native_path.write_text(json.dumps({'path':str(OUTPUT),'fps':FPS,'native_segments':native,'intentional_A1_gaps':gaps,
                                  'clip_end_frame':clip_end,'segments':len(native),'empty_gaps':len(gaps)},ensure_ascii=False,indent=2))
report={'status':'passed_signal_identity_not_auditioned','audition_available':False,
        'sources':PLAN['sources'],'output':str(OUTPUT),'fps':FPS,'sample_rate':SR,
        'channels':2,'sample_width_bits':24,'sample_frames':full_samples,
        'file_duration_seconds':full_samples/SR,'native_clip_duration_frames':clip_end,
        'tail_safety_handle_samples_preserved':full_samples-clip_end*SPF,
        'tail_safety_handle_seconds_preserved':(full_samples-clip_end*SPF)/SR,
        'same_total_sample_frames':True,'all_nonzero_stereo_sample_frames_directly_compared':compared,
        'all_nonzero_stereo_sample_frame_order_and_values_exactly_equal':True,
        'nonzero_stereo_frame_sha256_original':old_hash.hexdigest(),
        'nonzero_stereo_frame_sha256_new':new_hash.hexdigest(),
        'source_file_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'output_file_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
        'actions':actions,'source_to_target_sample_mapping':mapping,'crossfades':crossfades,
        'native_segments':native,'intentional_A1_gaps':gaps,'native_segments_file':str(native_path),
        'remapped_chapters':chapters,'all_chapter_reference_boundaries_unchanged':True,
        'A2_fixed_anchor_frames_unchanged':[10850,10935,11042],
        'remapped_58_sentences':remap_records(reference['sentences']),
        'remapped_193_phrases':remap_records(reference['phrases']),
        'remapped_independent_noninterpolated_asr_segments':remap_records(independent['segments']),
        'timestamp_note':'Reference alignment includes estimated/interpolated word times; independent ASR also may allocate a quiet span to a word. Remapped timestamps navigate retained original speech; they are not a fresh phoneme alignment.',
        'source_files_modified':False,'resolve_connected_or_modified':False,
        'gain_speed_denoise_compression_changes':False,
        'audio_audition_note':'Normal-speed direct listening is unavailable; provide the before/after audition files without claiming listening approval.'}
report_path=WORK/'audio_edit_map_v14.json';report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2))
for name,data in [('旁白气口_调整前_206至222秒.wav',original),('旁白气口_调整后_206至222秒.wav',edited)]:
    write_wav(LISTEN/name,data[206*SR*BPF:222*SR*BPF])
print(json.dumps({'status':'passed','new_wav':str(OUTPUT),'edit_map':str(report_path),'native_segments':str(native_path),
                  'segments':len(native),'gaps':len(gaps),'nonzero_sample_frames_exactly_compared':compared,
                  'full_wav_duration_seconds':full_samples/SR,'native_A1_duration_seconds':clip_end/FPS},ensure_ascii=False),flush=True)
