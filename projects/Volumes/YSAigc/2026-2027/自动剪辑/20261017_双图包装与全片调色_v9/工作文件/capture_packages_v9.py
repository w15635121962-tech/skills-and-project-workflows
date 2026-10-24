from common_v9 import *
from PIL import Image,ImageDraw,ImageFont
r,pm,p,mp,t=connect();assert t.GetName()==NAME and r.OpenPage('edit')
data=json.loads((OUT/'native_packages_v9.json').read_text());rows=[];records=[]
for g in data['groups']:
    triplet=[]
    for label,off in [('入',0),('中',g['length']//2),('出',g['length']-1)]:
        path=PRE/'双图实际画面'/f"{g['start']:05d}_{label}.jpg";im=capture(p,t,g['start']+off,path,.14)
        triplet.append(im);records.append({'start':g['start'],'frame':g['start']+off,'label':label,'path':str(path)})
    rows.append((g,triplet));print('PAIR_NATIVE_TRIPLET',g['start'],flush=True)
font=ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc',19)
for a in range(0,len(rows),4):
    part=rows[a:a+4];sheet=Image.new('RGB',(1920,len(part)*390),(242,239,230));d=ImageDraw.Draw(sheet)
    for j,(g,ims) in enumerate(part):
        for k,im in enumerate(ims):
            im=im.copy();im.thumbnail((640,360));sheet.paste(im,(640*k,j*390));d.text((640*k+7,j*390+363),f"{g['start']/25:.2f}s {['入','中','出'][k]} · {g['title']}",font=font,fill=(22,38,31))
    sheet.save(PRE/f'双图首中尾_{a//4+1}.jpg',quality=94)
save('package_actual_frames_v9.json',{'records':records,'groups':22,'actual_stills':66});print('ALL_PAIR_STILLS_READY',flush=True)
