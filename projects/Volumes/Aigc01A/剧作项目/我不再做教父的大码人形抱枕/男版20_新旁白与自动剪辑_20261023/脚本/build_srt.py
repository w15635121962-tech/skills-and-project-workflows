"""Align script-authoritative English to blind observed words and native 24fps edits."""
import argparse,re,math,functools,difflib,textwrap
from native_common import *
def norm(s):
    s=s.lower().replace('eighteen','18').replace('twenty-eight','28')
    return re.sub(r'[^a-z0-9]','',s)
def align(cw,ww):
    @functools.lru_cache(None)
    def dp(i,j):
        if i==len(cw) and j==len(ww):return 0,()
        if i==len(cw) or j==len(ww):return 10000,()
        opts=[]
        for nc,na in [(1,1),(1,2),(1,3),(2,1),(3,1)]:
            if i+nc>len(cw) or j+na>len(ww):continue
            a=norm(''.join(cw[i:i+nc]));b=norm(''.join(x['word'] for x in ww[j:j+na]))
            cost=0 if a==b else 1+(nc+na-2)*.5+(1-difflib.SequenceMatcher(None,a,b).ratio())
            tail,path=dp(i+nc,j+na);opts.append((cost+tail,((i,i+nc,j,j+na),)+path))
        return min(opts,key=lambda x:x[0])
    cost,rows=dp(0,0);assert cost<10000,(cw,ww)
    mapped=[]
    for ci,ce,ai,ae in rows:
        start,end=ww[ai]['start'],ww[ae-1]['end']
        weights=[max(1,len(norm(x))) for x in cw[ci:ce]];total=sum(weights);cursor=start
        for word,weight in zip(cw[ci:ce],weights):
            edge=cursor+(end-start)*weight/total
            mapped.append({'word':word,'start':cursor,'end':edge,'observed':' '.join(x['word'] for x in ww[ai:ae])});cursor=edge
    return mapped,cost
def words(j):return j.get('words') or [w for s in j.get('segments',[]) for w in s.get('words',[])]
def wrap(seq):return textwrap.wrap(' '.join(seq),width=26,break_long_words=False,break_on_hyphens=False)
def chunks(events):
    out=[];cur=[]
    for n,w in enumerate(events):
        trial=cur+[w]
        if cur and len(wrap([x['word'] for x in trial]))>3:out.append(cur);cur=[]
        cur.append(w)
        if re.search(r'[.!?]["”]?$|[,;:]$',w['word']) and len(' '.join(x['word'] for x in cur))>=18:
            out.append(cur);cur=[]
    if cur:out.append(cur)
    # Keep a tiny sentence tail with its phrase, rather than orphaning one word.
    for i in range(1,len(out)):
        left,right=out[i-1],out[i]
        if len(' '.join(x['word'] for x in right))<18 and not re.search(r'[.!?]$',left[-1]['word']):
            if len(wrap([x['word'] for x in left+right]))<=3:
                out[i-1]=[];out[i]=left+right
            else:
                moved=[]
                while len(left)>4 and len(' '.join(x['word'] for x in moved+right))<24:
                    moved.insert(0,left.pop())
                if len(wrap([x['word'] for x in moved+right]))<=3:out[i]=moved+right
                else:left.extend(moved)
    out=[g for g in out if g]
    return out
def tc(frame):
    ms=round(frame*1000/24);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'
def main():
    a=argparse.ArgumentParser();a.add_argument('--plan',default=str(BASE/'final_native_plan.json'));a.add_argument('--subtitle-directory',default='字幕');args=a.parse_args();plan=load_plan(args.plan)
    report=[]
    for ep in plan['episodes']:
        wevents=[];audits=[];groups=[]
        for number,event in enumerate(ep['audio_events']):
            path=event['source_path'];kind='narration' if event['kind']=='narration' else 'video'
            rawpath=Path(event.get('word_timing_source') or asr_path(path,kind))
            assert rawpath.is_file(),('Missing current-source blind ASR',rawpath)
            raw=read(rawpath)
            assert raw['source_path']==path and raw['source_sha256']==sha(path),('ASR/source mismatch',path)
            sw=words(raw)
            sa,sz=event['source_start_frame']/24,event['source_end_frame']/24
            selected=[w for w in sw if w['end']>sa+.002 and w['start']<sz-.002]
            crossing=[w for w in selected if w['start']<sa-.06 or w['end']>sz+.06]
            assert not crossing,('word crossing source cut',ep['episode'],number,crossing)
            cw=event['canonical_text'].replace('“','').replace('”','').strip().split();mapped,cost=align(cw,selected)
            assert cost<=max(5,len(cw)*.28),('alignment needs review',ep['episode'],number,cost,event['canonical_text'],[w['word'] for w in selected])
            offset=event['record_frame']-event.get('clip_source_start_frame',event['source_start_frame'])
            rows=[]
            for w in mapped:
                st=max(event['record_frame'],math.floor(w['start']*24)+offset);en=max(st+1,math.ceil(w['end']*24)+offset)
                row=dict(w,start_frame=st,end_frame=en,kind=event['kind'],speaker=event['speaker'],source_path=path,event_index=number)
                rows.append(row);wevents.append(row)
            groups.extend(chunks(rows))
            audits.append({'event_index':number,'path':path,'canonical':event['canonical_text'],'observed':' '.join(w['word'] for w in selected),'alignment_cost':cost,'word_count':len(cw),'source_range':[sa,sz]})
        groups.sort(key=lambda x:x[0]['start_frame']);cues=[]
        for i,g in enumerate(groups):
            start=g[0]['start_frame'];nextstart=groups[i+1][0]['start_frame'] if i+1<len(groups) else ep['duration_frames']
            end=min(nextstart,max(x['end_frame'] for x in g)+3,ep['duration_frames']);assert 0<=start<end<=nextstart
            lines=wrap([x['word'] for x in g]);assert len(lines)<=3
            cues.append({'start_frame':start,'end_frame':end,'text':'\n'.join(lines)})
        assert [norm(x) for c in cues for x in c['text'].split()]==[norm(x['word']) for g in groups for x in g]
        out=BASE/args.subtitle_directory/f'EP{ep["episode"]:02}.srt';out.parent.mkdir(parents=True,exist_ok=True)
        text='\n\n'.join(f'{i}\n{tc(c["start_frame"])} --> {tc(c["end_frame"])}\n{c["text"]}' for i,c in enumerate(cues,1))+'\n'
        out.write_text(text,encoding='utf-8-sig')
        ep['subtitle_srt']=str(out);ep['subtitle_cue_count']=len(cues)
        write(BASE/'字幕'/f'EP{ep["episode"]:02}_词码与原文对齐.json',{'episode':ep['episode'],'words':wevents,'events':audits,'cues':cues,'normal_speed_human_listening':False})
        report.append({'episode':ep['episode'],'srt':str(out),'cue_count':len(cues),'max_lines':max(len(c['text'].splitlines()) for c in cues),'original_authoritative_words':sum(len(g) for g in groups),'alignment_cost':sum(x['alignment_cost'] for x in audits)})
    output=Path(args.plan).with_name(Path(args.plan).stem+'_含SRT.json');write(output,plan)
    print(json.dumps({'plan_with_srt':str(output),'episodes':report},ensure_ascii=False))
if __name__=='__main__':main()
