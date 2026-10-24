exec(open(str(__import__('pathlib').Path(__file__).with_name('scan_v22.py'))).read().split('for idx in range')[0])
P=[('004','A001C308',125,171),('002','A002C008',75,121),('005','D0590',100,146)]
R=[]
for g,n,a,b in P:
 x=next(x for x in D if x['group']==g and n in x['name']);frames=[round(a+(b-1-a)*i/8) for i in range(9)];out=Image.new('RGB',(1440,894),(12,16,20));dr=ImageDraw.Draw(out);j=0
 with av.open(x['path']) as c:
  st=c.streams.video[0];c.seek(int(a/x['fps']/st.time_base),stream=st)
  for f in c.decode(st):
   if j>=len(frames):break
   fn=round(float(f.time)*x['fps'])
   if fn<frames[j]:continue
   im=f.to_image();im.thumbnail((480,270));xx=j%3*480;yy=j//3*298;out.paste(im,(xx,yy));dr.text((xx+3,yy+272),n+f' f{fn} {fn/x["fps"]:.2f}s',font=F,fill='white');j+=1
 q=ROOT/f'{g}_{n}_{a}-{b}_九帧.jpg';out.save(q,quality=95);print(q,flush=True);R.append({'name':x['name'],'path':x['path'],'group':g,'fps':x['fps'],'source_in_frame':a,'source_out_frame_exclusive':b,'duration_seconds':(b-a)/x['fps'],'contact_sheet':str(q)})
(ROOT/'首镜三候选_原始信息.json').write_text(json.dumps(R,ensure_ascii=False,indent=2))
