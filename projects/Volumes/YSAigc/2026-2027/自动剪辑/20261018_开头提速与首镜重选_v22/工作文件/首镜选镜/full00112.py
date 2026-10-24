exec(open(str(__import__('pathlib').Path(__file__).with_name('scan_v22.py'))).read().split('for idx in range')[0])
A=[x for x in D if (x['group']=='001' and x['name'].startswith('20260924_C0012_'))]
for x in A:
 times=[x['duration']*v/10 for v in range(1,10)];out=Image.new('RGB',(1440,3*298),(12,16,20));dr=ImageDraw.Draw(out)
 for j,t in enumerate(times):
  with av.open(x['path']) as c:
   st=c.streams.video[0];c.seek(int(t/st.time_base),stream=st)
   for f in c.decode(st):
    if float(f.time)>=t:
     im=f.to_image();im.thumbnail((480,270));xx=(j%3)*480;yy=(j//3)*298;out.paste(im,(xx,yy));dr.text((xx+4,yy+272),x['name']+f' {f.time:.2f}s',font=F,fill='white');break
 q=ROOT/(x['name']+'_fulltime.jpg');out.save(q);print(q,flush=True)
