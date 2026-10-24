from pathlib import Path
import sys, subprocess, json
sys.path.insert(0, '/tmp/ep10-live-deps')
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

out = Path(__file__).parent / '后期字版_MOV'
out.mkdir(exist_ok=True)
ff = imageio_ffmpeg.get_ffmpeg_exe()
font_dir = Path('/System/Library/Fonts/Supplemental')
bold = str(font_dir / 'Arial Bold.ttf')
def make_plate(kind):
    im = Image.new('RGBA', (720, 1280), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if kind == '校报标题':
        d.text((360, 220), 'Cyber Twins', font=ImageFont.truetype(bold, 74), anchor='mm', fill=(17, 22, 29, 255))
    else:
        d.text((360, 275), 'ELENA', font=ImageFont.truetype(bold, 40), anchor='mm', fill=(26, 35, 47, 255))
        d.text((360, 570), 'C', font=ImageFont.truetype(bold, 210), anchor='mm', fill=(26, 35, 47, 255))
    return im

records = []
for kind in ['校报标题', '手机成绩']:
    im = make_plate(kind)
    im.save(out / (kind + '_透明字版.png'))
    preview = Image.new('RGBA', im.size, (241, 243, 245, 255))
    Image.alpha_composite(preview, im).convert('RGB').save(out / (kind + '_排版预览.jpg'))
    target = out / (kind + '_透明字版_ProRes4444.mov')
    proc = subprocess.Popen([ff, '-hide_banner', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pixel_format', 'rgba', '-video_size', '720x1280', '-framerate', '24', '-i', 'pipe:0', '-an', '-c:v', 'prores_ks', '-profile:v', '4', '-pix_fmt', 'yuva444p10le', str(target)], stdin=subprocess.PIPE)
    frame = im.tobytes()
    for _ in range(60):
        proc.stdin.write(frame)
    proc.stdin.close()
    assert proc.wait() == 0
    # Decode one frame to verify that the MOV retained nonopaque alpha.
    decoded = subprocess.run([ff, '-hide_banner', '-loglevel', 'error', '-i', str(target), '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgba', 'pipe:1'], capture_output=True, check=True).stdout
    assert len(decoded) == 720 * 1280 * 4
    alphas = decoded[3::4]
    assert min(alphas) == 0 and max(alphas) > 250
    records.append({'file': target.name, 'duration': 2.5, 'fps': 24, 'size': [720, 1280], 'alpha_verified': True, 'tracked_to_generated_video': False})

(out / '字版制作记录.json').write_text(json.dumps(records, ensure_ascii=False, indent=2))
(out / '使用说明.md').write_text('两份字版均为720×1280、24fps、2.5秒、透明ProRes4444 MOV，无音频。\n\n校报仅使用原文Cyber Twins；手机仅使用ELENA和C，不新增课程、成绩分数、名次或故事信息。\n\n这是可编辑合成素材，尚未叠入生成视频。校报字版需随O05页面的拉出做平面跟踪；手机字版需随O07屏幕做四角透视跟踪并遮罩，仅在正面屏幕内显示，在右拇指按侧键实际熄屏的那一帧切除，不能浮在手机外或背面。坐标仅为排版参考，最终位置以实际底片为准。\n\n按剪辑接续.md重排9镜后统一铺原英文旁白。现有13.512秒音频未做本次逐字听检与对齐，22.5秒开场是设计时长，不代表配音已完成同步。\n')
print(json.dumps(records, ensure_ascii=False))
