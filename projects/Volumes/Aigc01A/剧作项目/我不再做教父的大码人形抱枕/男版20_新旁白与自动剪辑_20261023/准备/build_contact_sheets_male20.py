from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont
import json, subprocess, math, sys

work = Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕/男版20_新旁白与自动剪辑_20261023/准备')
inventory = json.loads((work/'素材盘点.json').read_text())
out = work/'画面联系图'
frames = out/'逐文件帧'
frames.mkdir(parents=True, exist_ok=True)
ffmpeg = Path(inventory['ffprobe_path']).with_name('ffmpeg')
eps = [int(x) for x in sys.argv[1:]] or [20]
font = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 24)
small = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 21)
title = ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf', 32)
W, H = 300, 534
CW, CH = 626, 612
GAP, HEAD = 18, 62
index_path = out/'索引.json'
index = json.loads(index_path.read_text()) if index_path.exists() else {'source_inventory': str(work/'素材盘点.json'), 'sampling_fractions':[0.20,0.75], 'pages':[], 'cards':[]}

def extract(row):
    result = []
    for fraction in (0.2,0.75):
        time = round(row['duration_seconds']*fraction, 6)
        name = f"EP{row['episode']:02d}_G{row['group_or_segment']:02d}_N{row['version_number']:02d}_{int(fraction*100)}pct.jpg"
        path = frames/name
        if not path.exists():
            cmd = [str(ffmpeg), '-nostdin','-hide_banner','-loglevel','error',
                   '-ss',str(time),'-i',row['path'],'-map','0:v:0','-frames:v','1',
                   '-vf',f'scale={W}:{H}:flags=lanczos','-q:v','2',str(path)]
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
            if p.returncode or not path.exists():
                raise RuntimeError(f'{row["filename"]}: {p.stderr}')
        with Image.open(path) as image:
            if image.size != (W,H): raise RuntimeError(f'Unexpected size {path}')
        result.append({'fraction':fraction,'time_seconds':time,'image_path':str(path)})
    return row,result

for ep in eps:
    rows = sorted([r for r in inventory['files'] if r['kind']=='video' and r['episode']==ep], key=lambda x:(x['group_or_segment'],x['version_number']))
    with ThreadPoolExecutor(max_workers=4) as pool:
        shots = list(pool.map(extract,rows))
    index['pages'] = [p for p in index['pages'] if p['episode'] != ep]
    index['cards'] = [c for c in index['cards'] if c['episode'] != ep]
    for offset in range(0,len(shots),12):
        chunk = shots[offset:offset+12]
        number = offset//12 + 1
        nrows = math.ceil(len(chunk)/3)
        sheet = Image.new('RGB',(GAP+3*(CW+GAP),HEAD+GAP+nrows*(CH+GAP)),(22,25,31))
        draw = ImageDraw.Draw(sheet)
        draw.text((GAP,12),f'Male EP{ep:02d} | Page {number} | 20% left / 75% right | source order by group / suffix',font=title,fill=(245,245,245))
        sheet_path = out/f'EP{ep:02d}_p{number}.jpg'
        page_cards = []
        for slot,(row,samples) in enumerate(chunk):
            x = GAP+(slot%3)*(CW+GAP)
            y = HEAD+GAP+(slot//3)*(CH+GAP)
            draw.rounded_rectangle((x,y,x+CW,y+CH),radius=8,fill=(42,47,57))
            label = f"EP{ep:02d} / G{row['group_or_segment']:02d} / N{row['version_number']:02d} / {row['duration_seconds']:.3f}s"
            draw.text((x+10,y+8),label,font=font,fill=(255,255,255))
            for side,sample in enumerate(samples):
                ix=x+9+side*(W+8)
                with Image.open(sample['image_path']) as image: sheet.paste(image,(ix,y+42))
                draw.text((ix,y+578),f"{int(sample['fraction']*100)}% @ {sample['time_seconds']:.2f}s",font=small,fill=(210,220,235))
            card={'episode':ep,'page':number,'card_number':slot+1,'grid_row':slot//3+1,'grid_column':slot%3+1,'group':row['group_or_segment'],'suffix':row['version_number'],'duration_seconds':row['duration_seconds'],'source_path':row['path'],'filename':row['filename'],'sheet_path':str(sheet_path),'card_bbox':[x,y,x+CW,y+CH],'samples':samples}
            index['cards'].append(card)
            page_cards.append(card['filename'])
        sheet.save(sheet_path,quality=94,subsampling=0)
        with Image.open(sheet_path) as image: dims = list(image.size)
        index['pages'].append({'episode':ep,'page':number,'path':str(sheet_path),'dimensions':dims,'card_count':len(chunk),'files_in_card_order':page_cards})
    index['pages'].sort(key=lambda x:(x['episode'],x['page']))
    index['cards'].sort(key=lambda x:(x['episode'],x['group'],x['suffix']))
    index_path.write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'episode':ep,'video_cards':len(shots),'pages':[p['path'] for p in index['pages'] if p['episode']==ep]},ensure_ascii=False),flush=True)
