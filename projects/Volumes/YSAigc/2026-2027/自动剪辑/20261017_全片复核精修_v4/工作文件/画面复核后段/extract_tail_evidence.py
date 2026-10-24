from pathlib import Path
import concurrent.futures
import json
import subprocess

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent
ROOT = OUT.parents[2].parent / '20261017_旁白精修' / '工作文件'
ROOT = Path('/Volumes/YSAigc/2026-2027/自动剪辑/20261017_旁白精修/工作文件')
PLAN = json.loads((ROOT / 'narrative_edit_plan.json').read_text())
ALIGNED = json.loads((ROOT / 'narration_aligned.json').read_text())
SK = '/Users/xuan/Codex_YS_Data/CodexHome/skills/ffmpeg-skill/scripts/look.py'
FRAMES = OUT / '源帧'
LOGS = OUT / '提帧日志'
FRAMES.mkdir(exist_ok=True)
LOGS.mkdir(exist_ok=True)
shots = [s for s in PLAN['shots'] if s['record_frame'] + s['length_frames'] > 5901]


def extract(s):
    start = float(s['in'])
    duration = float(s['out']) - start
    times = [start + 0.04, start + duration / 2, start + duration - 0.08]
    dest = FRAMES / f"shot{s['index']:03d}.png"
    args = ['python3', SK, s['path'], '-o', str(dest), '--no-timecode', '--json']
    for at in times:
        args += ['--at', f'{at:.3f}']
    log = LOGS / f"shot{s['index']:03d}.json"
    if log.exists():
        result = json.loads(log.read_text())
    else:
        c = subprocess.run(args, capture_output=True, text=True)
        log.write_text(c.stdout)
        if c.returncode:
            raise RuntimeError(c.stdout[-500:] + c.stderr[-500:])
        result = json.loads(c.stdout)
    s = dict(s)
    s['evidence_frames'] = result['outputs']
    s['evidence_source_times'] = times
    s['sentence_details'] = [{k: x[k] for k in ['id', 'start', 'end', 'text']}
                             for x in ALIGNED['sentences']
                             if x['end'] > s['record_frame'] / 25
                             and x['start'] < (s['record_frame'] + s['length_frames']) / 25]
    return s


def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        result = list(pool.map(extract, shots))
    font = ImageFont.truetype('/System/Library/Fonts/Hiragino Sans GB.ttc', 20)
    small = ImageFont.truetype('/System/Library/Fonts/Hiragino Sans GB.ttc', 17)
    sheets = []
    for group in range(0, len(result), 7):
        subset = result[group:group + 7]
        canvas = Image.new('RGB', (1536, len(subset) * 346), (22, 25, 28))
        draw = ImageDraw.Draw(canvas)
        for row, s in enumerate(subset):
            y = row * 346
            label = f"镜{s['index']:03d}  {s['record_frame']/25:.2f}–{(s['record_frame']+s['length_frames'])/25:.2f}s  {s['name']}"
            draw.text((8, y+2), label[:86], font=font, fill='white')
            for col, f in enumerate(s['evidence_frames']):
                im = Image.open(f).convert('RGB')
                im.thumbnail((508, 286))
                canvas.paste(im, (col*512 + (508-im.width)//2, y + 32))
                draw.text((col*512+8, y+318), f"源 {s['evidence_source_times'][col]:.3f}s", font=small, fill=(220,220,220))
        dest = OUT / f'后段首中末_{group//7+1:02d}.jpg'
        canvas.save(dest, quality=88)
        sheets.append(str(dest))
    (OUT/'tail_evidence_manifest.json').write_text(json.dumps({'shots':result,'sheets':sheets,'scope':'236.04–460.28 seconds; v3 tail equals v2'}, ensure_ascii=False, indent=2))
    print(json.dumps({'shot_count':len(result),'frame_count':sum(len(s['evidence_frames']) for s in result),'sheets':sheets},ensure_ascii=False))


if __name__ == '__main__':
    main()
