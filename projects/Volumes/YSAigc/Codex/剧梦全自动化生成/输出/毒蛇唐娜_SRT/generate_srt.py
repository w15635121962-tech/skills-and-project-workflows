from pathlib import Path
import re, zipfile, xml.etree.ElementTree as ET, json
src=Path('/Volumes/YSAigc/Claude/毒蛇唐娜继父版/完整剧本/EN毒蛇唐娜继父版(1).docx')
base=Path(__file__).resolve().parent
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
root=ET.fromstring(zipfile.ZipFile(src).read('word/document.xml'))
chapters={}
chapter=None
for p in root.findall('.//w:p',ns):
    s=''.join(t.text or '' for t in p.findall('.//w:t',ns)).strip()
    m=re.fullmatch(r'Chapter\s+(\d+)',s)
    if m:
        chapter=int(m[1]); chapters[chapter]=[]
    elif chapter and s:
        chapters[chapter].append(s.replace('【卡】','').strip())
def split(s):
    words=s.split()
    out=[]
    while words:
        n=min(8,len(words))
        if len(words)>8:
            # Prefer punctuation near the end of the allowed window.
            ends=[i for i in range(3,n+1) if re.search(r'[.!?,;:][\"”\x27]*$',words[i-1])]
            if ends: n=ends[-1]
        out.append(' '.join(words[:n]));words=words[n:]
    return out
def stamp(ms):
    h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'
def block(i,start,end,s):
    return f'{i}\n{stamp(start)} --> {stamp(end)}\n{s}\n\n'
merged=base/'按章合并版_每条最多8词'
separate=base/'独立文件版_每文件最多8词'
merged.mkdir(exist_ok=True);separate.mkdir(exist_ok=True)
stats=[]
for ch,paras in chapters.items():
    chunks=[c for p in paras for c in split(p)]
    assert ' '.join(chunks)==' '.join(' '.join(paras).split())
    folder=separate/f'Chapter_{ch:02}'
    folder.mkdir(exist_ok=True)
    now=0;blocks=[]
    for i,s in enumerate(chunks,1):
        assert len(s.split())<=8
        duration=max(1000,round(len(s.split())/2.5*1000))
        blocks.append(block(i,now,now+duration,s))
        (folder/f'Chapter_{ch:02}_{i:04}.srt').write_text(block(1,0,duration,s),encoding='utf-8-sig')
        now+=duration+120
    (merged/f'Chapter_{ch:02}.srt').write_text(''.join(blocks),encoding='utf-8-sig')
    stats.append({'chapter':ch,'cues':len(chunks),'words':sum(len(c.split()) for c in chunks),'estimated_duration_ms':now-120})
readme='''原文：EN毒蛇唐娜继父版(1).docx，共25章。

独立文件版：每个SRT文件仅含一条字幕，字幕正文不超过8个英文单词。每个文件时间轴从00:00:00,000开始，文件名记录章节及先后顺序。
按章合并版：每章一个SRT文件，每条字幕正文不超过8个英文单词，各章时间轴从零开始。

包含英文叙述与对白，保持原文顺序、用词和标点；未收录开头标题、人员信息、Chapter标题及【卡】编辑标记。跨章重复的原文予以保留。
词数按空白分隔计算，缩写和连字符连接词算一个词；SRT序号、时间码不计入字幕正文词数。
时间轴为估算：每秒2.5词，每条至少1秒，合并版条目间隔0.12秒。未提供音视频，尚未进行实际语音对齐。
'''
(base/'使用说明.txt').write_text(readme,encoding='utf-8')
(base/'校验统计.json').write_text(json.dumps(stats,indent=2,ensure_ascii=False),encoding='utf-8')
for folder,name in [(separate,'独立文件版_每文件最多8词.zip'),(merged,'按章合并版_每条最多8词.zip')]:
    with zipfile.ZipFile(base/name,'w',zipfile.ZIP_DEFLATED) as z:
        z.write(base/'使用说明.txt','使用说明.txt')
        for p in sorted(folder.rglob('*.srt')):z.write(p,p.relative_to(base))
print(json.dumps({'chapters':len(stats),'srt_single_files':sum(x['cues'] for x in stats),'words':sum(x['words'] for x in stats),'max_words':max(len(c.split()) for ps in chapters.values() for p in ps for c in split(p)),'output':str(base)},ensure_ascii=False))
