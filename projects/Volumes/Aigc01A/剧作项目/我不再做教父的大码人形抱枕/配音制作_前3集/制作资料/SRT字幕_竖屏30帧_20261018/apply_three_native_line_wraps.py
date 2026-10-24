#!/usr/bin/env python3
"""Apply three UI-approved line-wrap changes without modifying words or times."""
from pathlib import Path
import collections
import copy
import hashlib
import json
import zipfile

HERE=Path(__file__).resolve().parent
MEDIA=HERE.parent.parent
SUB=MEDIA/'字幕'
MID=HERE/'句子半句_竖屏字幕中间方案.json'
FINAL=HERE/'30fps竖屏字幕_落帧完成与校验.json'
ACTIVE=HERE/'最终30fps字幕预设活动时间线清单.json'
RECORD=HERE/'三处原生三行换行修正记录.json'
BACK=HERE/'三处换行修正前备份'
OVERRIDES={
 ('女版',3,20):['After she died, the',"family's education trust",'funded my schooling,'],
 ('性转男版',3,10):['Dressed in threadbare','rags, I waited in the','crowd, utterly alone.'],
 ('性转男版',3,20):['I buried my feelings','so deep that nobody','ever caught on.'],
}


def read(p):return json.loads(p.read_text(encoding='utf-8'))
def digest(data):return hashlib.sha256(data).hexdigest()
def sha(p):return digest(p.read_bytes())
def writej(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def backup(path):
    target=BACK/path.name
    assert not target.exists(), 'Preserve existing backup: '+str(target)
    target.write_bytes(path.read_bytes())
    assert sha(target)==sha(path)
    return str(target)


def main():
    assert not RECORD.exists(), 'Already applied; inspect the existing change record instead of applying twice.'
    mid,final=read(MID),read(FINAL)
    before_mid,before_final=copy.deepcopy(mid),copy.deepcopy(final)
    current=[Path(t['srt_path']) for t in final['timelines']]
    old24=list((SUB/'女版').glob('*.srt'))+list((SUB/'性转男版').glob('*.srt'))
    assert len(current)==len(old24)==6
    before_srt={str(p):p.read_bytes() for p in current}
    old24_sha={str(p):sha(p) for p in old24}
    for t in final['timelines']:assert sha(Path(t['srt_path']))==t['srt_sha256']
    archive=SUB/'大码_两版前三集_竖屏30帧_分句SRT.zip'
    zip_manifest=HERE/'竖屏分句SRT压缩包核验清单.json'
    preview=HERE/'句子半句_人工核对预览.txt'
    builder=HERE/'build_semantic_caption_plan.py'
    assert not BACK.exists()
    BACK.mkdir()
    backups={str(p):backup(p) for p in [MID,FINAL,archive,zip_manifest,preview,builder]}
    changes=[]
    for t in final['timelines']:
        version=t['version'];episode=t['episode'];path=Path(t['srt_path'])
        blocks=before_srt[str(path)].decode('utf-8').strip().split('\n\n')
        changed=False
        for c in t['cues']:
            key=(version,episode,c['index'])
            if key not in OVERRIDES:continue
            lines=OVERRIDES[key]
            assert ' '.join(lines)==c['text']
            assert len(lines)==3 and max(map(len,lines))<=28
            prior=copy.deepcopy(c)
            block=blocks[c['index']-1].splitlines()
            assert block[2:]==c['lines'] and block[1]==c['srt_start']+' --> '+c['srt_end']
            blocks[c['index']-1]='\n'.join(block[:2]+lines)
            c['lines']=lines;c['line_char_counts']=list(map(len,lines))
            for field in set(c)-{'lines','line_char_counts'}:assert c[field]==prior[field]
            changes.append({'version':version,'episode':episode,'cue_index':c['index'],
                'srt_path':str(path),'before_lines':prior['lines'],'after_lines':lines,
                'before_char_counts':prior['line_char_counts'],'after_char_counts':c['line_char_counts'],
                'text':c['text'],'srt_start':c['srt_start'],'srt_end':c['srt_end'],
                'frame_start_30fps':c['frame_start_30fps'],'frame_end_30fps':c['frame_end_30fps'],
                'all_other_cue_fields_unchanged':True})
            changed=True
        if changed:
            backups[str(path)]=backup(path)
            out='\n\n'.join(blocks)+'\n'
            old_blocks=before_srt[str(path)].decode('utf-8').strip().split('\n\n')
            assert len(old_blocks)==len(blocks)
            for a,b in zip(old_blocks,blocks):
                aa,bb=a.splitlines(),b.splitlines()
                assert aa[:2]==bb[:2] and ' '.join(aa[2:])==' '.join(bb[2:])
            path.write_text(out,encoding='utf-8')
        t['srt_sha256']=sha(path)
    assert len(changes)==3
    for t in mid['timelines']:
        version='性转男版' if '性转' in t['timeline_name'] else '女版'
        import re
        ep=int(re.search(r'EP(\d+)',t['timeline_name']).group(1))
        for c in t['cues']:
            key=(version,ep,c['index'])
            if key in OVERRIDES:
                assert ' '.join(OVERRIDES[key])==c['text']
                c['lines']=OVERRIDES[key];c['line_char_counts']=list(map(len,c['lines']))
    histogram=collections.Counter(len(c['lines']) for t in mid['timelines'] for c in t['cues'])
    mid['summary']['line_count_histogram']=dict(histogram)
    for obj in [mid,final]:
        obj['line_wrap_correction_record']=str(RECORD)
        obj['native_active_timeline_manifest']=str(ACTIVE)
    writej(MID,mid)
    assert str(MID) in final['inputs_sha256']
    final['inputs_sha256'][str(MID)]=sha(MID)
    writej(FINAL,final)
    # Keep future rebuilds consistent with the native-pixel-approved line wraps.
    source=builder.read_text(encoding='utf-8')
    anchor='def wrap(text):\n    words = text.split()'
    assert source.count(anchor)==1
    source=source.replace(anchor,
        'def wrap(text):\n    reviewed_line_overrides = '+repr({c['text']:c['after_lines'] for c in changes})+'\n    if text in reviewed_line_overrides:\n        return reviewed_line_overrides[text]\n    words = text.split()')
    builder.write_text(source,encoding='utf-8')
    previews=[]
    for t in mid['timelines']:
        previews.extend([t['timeline_name'],f"旧{t['old_cue_count']}条 → 新{t['new_cue_count']}条"])
        for c in t['cues']:
            previews.append(f"{c['index']:03} | {c['audio_name']} | {c['duration_seconds_reference']:.3f}s | "+' / '.join(c['lines']))
        previews.append('')
    preview.write_text('\n'.join(previews)+'\n',encoding='utf-8')
    # Full field-level invariant check: only line arrays/counts and explicit metadata/hashes changed.
    for before,after in [(before_mid,mid),(before_final,final)]:
        for bt,at in zip(before['timelines'],after['timelines']):
            for bc,ac in zip(bt['cues'],at['cues']):
                for k in set(bc)-{'lines','line_char_counts'}:assert bc[k]==ac[k]
            assert len(bt['cues'])==len(at['cues'])
    assert sum(len(t['cues']) for t in final['timelines'])==159
    assert sum(before_srt[str(p)]!=p.read_bytes() for p in current)==2
    for p,h in old24_sha.items():assert sha(Path(p))==h
    members=[(p,p.relative_to(SUB).as_posix()) for p in current]+[(SUB/'使用说明.txt','使用说明.txt')]
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p,name in members:z.writestr(name,p.read_bytes())
    verified=[]
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None and len(z.infolist())==7
        assert set(z.namelist())=={name for _,name in members}
        for p,name in members:
            data=z.read(name);assert data==p.read_bytes();info=z.getinfo(name)
            cues=len(data.decode('utf-8').strip().split('\n\n')) if p.suffix=='.srt' else None
            verified.append({'archive_path':name,'source_path':str(p),'bytes':len(data),
                'sha256':digest(data),'crc32':f'{info.CRC:08x}','cue_count':cues,'byte_identical_to_source':True})
    assert sum(m['cue_count'] or 0 for m in verified)==159
    manifest={'archive_path':str(archive),'archive_bytes':archive.stat().st_size,
        'archive_sha256':sha(archive),'member_count':7,'srt_count':6,'readme_count':1,
        'cue_count':159,'zip_crc_test_passed':True,'all_members_byte_identical_to_sources':True,
        'six_old_24fps_SRTs_unchanged':True,
        'only_three_manual_line_wraps_changed':True,'all_SRT_words_punctuation_and_timestamps_unchanged':True,
        'line_wrap_correction_record':str(RECORD),'actual_snapshot_path':final['actual_snapshot_path'],
        'members':verified}
    writej(zip_manifest,manifest)
    record={'change':'Native-pixel-validated manual line breaks only',
        'authorization':'Root confirmed the female EP03 cue20 candidate renders as exactly three native Cinema lines and authorized all three accepted replacements.',
        'backups':backups,'changes':changes,'total_cues':159,'changed_SRT_files':2,
        'all_text_words_punctuation_times_frames_and_worddata_unchanged':True,
        'old_24fps_SRT_hashes_unchanged':old24_sha,
        'timing_reference_timeline_IDs_unchanged':True,'native_active_timeline_manifest':str(ACTIVE),
        'current_sha256':{str(p):sha(p) for p in [MID,FINAL,builder,preview,archive,zip_manifest]+current}}
    writej(RECORD,record)
    print(json.dumps({'record':str(RECORD),'zip':str(archive),'zip_sha256':sha(archive),
        'mid_plan_sha256':sha(MID),'final_plan_sha256':sha(FINAL),
        'changed_SRTs':[{'path':str(p),'before_sha256':digest(before_srt[str(p)]),'sha256':sha(p)} for p in current if before_srt[str(p)]!=p.read_bytes()]},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
