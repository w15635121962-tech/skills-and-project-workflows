exec(open(str(__import__('pathlib').Path(__file__).with_name('scan.py'))).read().split('for idx in range')[0])
C=[('002','A002C019',3.0),('007','C0016',9.0),('007','C0017',12.0)]
RESULT=[]
for g,n,t in C:
 x=next(x for x in D if x['group']==g and x['name'].startswith(n+'_')); frames=list(range(round(t*x['fps']),round((t+3)*x['fps']),max(1,round(3*x['fps']/8))));frames=frames[:9]
 if len(frames)<9:frames.append(round((t+3)*x['fps'])-1)
 sheet=Image.new('RGB',(3*480,3*298),(10,14,18));draw=ImageDraw.Draw(sheet)
 with av.open(x['path']) as c:
  st=c.streams.video[0];cur=0;c.seek(int(t/st.time_base),stream=st)
  for f in c.decode(st):
   fn=round(float(f.time)*x['fps'])
   if cur>=len(frames):break
   if fn<frames[cur]:continue
   im=f.to_image();im.thumbnail((480,270));px=(cur%3)*480;py=(cur//3)*298;sheet.paste(im,(px,py));draw.text((px+3,py+272),f'{g}_{n} f{fn} ({fn/x["fps"]:.2f}s)',fill='white',font=F);cur+=1
 p=ROOT/(g+'_'+n+'_3sec_9frames.jpg');sheet.save(p,quality=92);print(p,flush=True)
 RESULT.append({'group':g,'name':x['name'],'path':x['path'],'fps':x['fps'],'source_in_frame':round(t*x['fps']),'source_out_frame_exclusive':round((t+3)*x['fps']),'contact_sheet':str(p),'used_whole_source':x['path'] in used})
json.dump(RESULT,open(ROOT/'detail_architecture_replacement_manifest.json','w'),ensure_ascii=False,indent=2)
