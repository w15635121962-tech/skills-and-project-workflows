from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
import json, hashlib, statistics

ROOT=Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_图片动态底板精修_v13')
MANIFEST=ROOT/'工作文件/package_native_build_v13.json'
FONT=Path('/System/Library/Fonts/STHeiti Light.ttc')

def timecode(frame):
    seconds, ff=divmod(int(frame),25)
    mm, ss=divmod(seconds,60)
    return f'{mm:02d}:{ss:02d}:{ff:02d}'

def inputs_for(g):
    start=g['start']; length=g['length']
    return [('入',start,ROOT/f'包装预览/进出画面核验/{start}_入.jpg'),
            ('中',start+length//2,ROOT/f'包装预览/精修后/{start}.jpg'),
            ('出',start+length-1,ROOT/f'包装预览/进出画面核验/{start}_出.jpg')]

def background_check(im):
    # Only the outer empty margins: exclude photos, captions and the gold rules.
    # This detects leftover light paper, not aesthetic quality or source-photo color errors.
    crops=[im.crop((12,12,im.width-12,40)),im.crop((12,im.height-25,im.width-12,im.height-8)),
           im.crop((10,45,35,im.height-35)),im.crop((im.width-35,45,im.width-10,im.height-35))]
    values=[]
    for c in crops:
        values.extend(c.resize((100,4)).get_flattened_data())
    white=sum(min(p)>215 and max(p)-min(p)<35 for p in values)
    return {'outer_margin_mean_rgb':[round(statistics.mean(p[i] for p in values),2) for i in range(3)],
            'outer_margin_light_neutral_ratio':white/len(values),
            'white_paper_residue_flag':white/len(values)>.10}

def main():
    groups=json.loads(MANIFEST.read_text())
    assert isinstance(groups,list) and len(groups)==22
    source_paths=[p for g in groups for _,_,p in inputs_for(g)]
    missing=[str(p) for p in source_paths if not p.is_file()]
    if missing:raise RuntimeError('Capture not complete; no sheets generated. Missing: '+', '.join(missing))
    records=[]
    for g in groups:
        for phase,frame,p in inputs_for(g):
            with Image.open(p) as src:
                src.load(); im=ImageOps.exif_transpose(src).convert('RGB')
            assert im.size==(1920,1080),(p,im.size)
            records.append({'start':g['start'],'title':g['title'],'phase':phase,'frame':frame,
                            'timecode':timecode(frame),'path':str(p),'size':list(im.size),
                            'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),**background_check(im)})
    out=ROOT/'包装预览/独立首中尾联系表';out.mkdir(parents=True,exist_ok=True)
    smallfont=ImageFont.truetype(str(FONT),24);bigfont=ImageFont.truetype(str(FONT),29)
    pages=[]
    for page_no,(lo,hi) in enumerate([(0,7),(7,14),(14,22)],1):
        batch=groups[lo:hi]; row_h=510
        canvas=Image.new('RGB',(2400,72+row_h*len(batch)),(12,22,25));draw=ImageDraw.Draw(canvas)
        draw.text((22,18),f'动态底板独立核验  {page_no}/3    入 / 中 / 出    25fps',font=bigfont,fill=(237,236,223))
        for row,g in enumerate(batch):
            y=72+row*row_h
            for col,(phase,frame,p) in enumerate(inputs_for(g)):
                x=800*col
                with Image.open(p) as src:im=src.convert('RGB').resize((800,450),Image.Resampling.LANCZOS)
                canvas.paste(im,(x,y))
                draw.text((x+12,y+458),f"R{g['start']}  {g['title']}  {phase} {timecode(frame)}",font=smallfont,fill=(225,232,224))
        path=out/f'动态底板_首中尾_独立QA_{page_no}.jpg';canvas.save(path,quality=95,subsampling=0);pages.append(str(path))
    report={'status':'CONTACT_SHEETS_READY_AWAIT_VISUAL_REVIEW','groups':22,'frames':66,'fps':25,
            'source_manifest':str(MANIFEST),'pages':pages,'records':records,
            'white_paper_flags':[r for r in records if r['white_paper_residue_flag']],
            'verification_limit':'Margin statistics only flag leftover light paper. They do not certify photo integrity, readable text, motion continuity or native Fusion acceptance; independent visual review remains required.'}
    p=ROOT/'工作文件/图片底板独立静帧检查_v13.json';p.write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps({'groups':22,'frames':66,'pages':pages,'white_paper_flags':len(report['white_paper_flags']),'report':str(p)},ensure_ascii=False))

if __name__=='__main__':main()
