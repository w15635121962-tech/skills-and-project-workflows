"""Phrase-aware original-text SRT cues, without an arbitrary4-second hard split.
Every explicit chunk is checked against the original event tokens in order.
All input times are nearest24fps integers; original voiced ends stay intact.
"""
from subtitle_tools import wrap_original

def phrase_cues(events,timeline_end,chunks_by_paragraph):
    events=sorted(events,key=lambda x:(x['start_frame'],x['end_frame']))
    groups=[];current=[]
    for e in events:
        if current and e.get('boundary_before'):
            groups.append(current);current=[]
        current.append(e)
    if current:groups.append(current)
    chunks=[]
    for group in groups:
        original=[e['word'] for e in group];number=group[0]['docx_paragraph']
        texts=chunks_by_paragraph.get(number)
        if texts is None:texts=[' '.join(original)]
        assert ' '.join(texts).split()==original,('Manual phrase boundary changed original words',number,texts,original)
        cursor=0
        for text in texts:
            words=text.split();take=group[cursor:cursor+len(words)];cursor+=len(words)
            lines=wrap_original(words);assert len(lines)<=3,(number,lines)
            chunks.append({'events':take,'text':'\n'.join(lines),'docx_paragraph':number})
        assert cursor==len(group)
    cues=[]
    for i,c in enumerate(chunks):
        start=c['events'][0]['start_frame'];voice_end=c['events'][-1]['end_frame']
        next_start=chunks[i+1]['events'][0]['start_frame'] if i+1<len(chunks) else timeline_end
        assert 0<=start<voice_end<=next_start<=timeline_end,(i,start,voice_end,next_start)
        end=min(next_start,voice_end+4)
        cues.append({'start_frame':start,'end_frame':end,'text':c['text']})
    assert ' '.join(c['text'].replace('\n',' ') for c in cues).split()==[e['word'] for e in events]
    return cues

CHUNKS_13={
383:['She seemed to murmur something with a chuckle','before picking up, oblivious.'],
384:["I'm not coming home tonight.","I'll swing by tomorrow."],
385:["No way, you promised you'd spend tomorrow with me.",'Let me try putting you to sleep again.'],
391:['I suddenly remembered heading to the Blackwood estate','alone ten years ago.'],
392:['At thirteen, shrinking back in the crowd,','I cheered myself on in my head.'],
394:["Now at twenty-three, facing what's next with hope and jitters,",'I was starting fresh overseas.'],
}
CHUNKS_14={
400:['The night I left, Evan tried putting Vittoria to sleep,','but it barely worked.'],
401:['Seeing that, Evan tugged at her collar,','whispering in her ear with a suggestive tone.'],
402:['Want to get a little physical?','It might knock you right out.'],
407:['While Evan whined and played coy,','it crossed her mind that at this hour,','I would normally be reading quietly.'],
409:['Whenever she snatched my book and yanked me in,','I never complained or resisted,','just wrapped my arms around her.'],
414:['It rang for three minutes, no pick-up.','She frowned.'],
417:['Vittoria ran her tongue along her lips,','fighting back a flicker of panic,','and clicked her screen off with a cold stare.'],
418:["She didn't call again;",'instead, she looked at Evan and threw her arms around his neck.'],
420:["But when I still didn't reply the following day,",'Vittoria finally lost her cool.'],
422:["The landlord hadn't changed the keypad code yet,",'so Vittoria let herself in.'],
423:['Once inside, the apartment was empty,','as if nobody had ever lived there.'],
}
