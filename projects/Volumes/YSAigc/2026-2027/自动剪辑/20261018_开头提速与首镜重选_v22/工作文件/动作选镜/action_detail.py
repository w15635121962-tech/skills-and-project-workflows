import av
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
R=Path('/Volumes/YSAigc/2026-2027/文汇中学/拍摄素材转码');O=Path(__file__).parent;font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',18)
plans=[('A003C200',list(range(500,601,5))),('A003C221',list(range(1040,1201,10))),('A001C338',list(range(45,101,5))),('A003C139',list(range(55,111,5))),('C0125',list(range(475,551,5)))]
for n,inds in plans:
 p=next(R.rglob(n+'*mov'));c=av.open(str(p));s=c.streams.video[0];fps=float(s.average_rate);sheet=Image.new('RGB',(1600,((len(inds)+3)//4)*245),(15,15,15));d=ImageDraw.Draw(sheet)
 for i,idx in enumerate(inds):
  c.seek(int(idx/fps/s.time_base),stream=s,backward=True)
  for f in c.decode(s):
   if round(f.time*fps)>=idx:break
  im=f.to_image();im.thumbnail((400,225));x=i%4*400;y=i//4*245;sheet.paste(im,(x,y));d.text((x+8,y+225),f'{p.stem}  fr {round(f.time*fps)}',font=font,fill='white')
 sheet.save(O/(p.stem+'_动作精查.jpg'),quality=92);c.close()
print('done')
