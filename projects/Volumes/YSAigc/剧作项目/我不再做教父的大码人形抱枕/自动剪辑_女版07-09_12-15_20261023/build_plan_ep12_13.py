from pathlib import Path
import json, math

W = Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕/自动剪辑_女版07-09_12-15_20261023')
INV = json.loads((W/'素材盘点.json').read_text())
ROOT = Path(INV['source_root'])
FPS = 24
MEDIA = {r['path']:r for r in INV['files']}

def F(sec): return round(sec*FPS)
def path(ep, name, kind='video'):
    folder = '视频' if kind=='video' else '旁白'
    ext = 'mp4' if kind=='video' else 'mp3'
    return str(ROOT/folder/f'EP{ep:02d}'/f'女版{ep}-{name}.{ext}')

class Plan:
    def __init__(self,ep,source):
        self.ep=ep;self.source=source;self.cursor=0
        self.video=[];self.narr=[];self.events=[];self.limits=[]
    def clip(self,name,a,b,gain,tag,kind='visual',text='',speaker=None,record=None):
        start,end=F(a),F(b)
        if record is None: record=self.cursor
        row={'path':path(self.ep,name),'source_start_frame':start,'source_end_frame':end,
             'source_start_seconds':start/FPS,'source_end_seconds':end/FPS,
             'record_frame':record,'record_end_frame':record+end-start,
             'gain_db':gain,'speed_percent':100,'kind':kind,'canonical_text':text,'tag':tag,
             'reason':tag,'sync_contract':'V1 and A1 use the identical source path, source in/out and record in/out; source end is exclusive.'}
        self.video.append(row)
        if record==self.cursor:self.cursor += end-start
        return row
    def dialogue(self,name,a,b,text,speaker,tag):
        row=self.clip(name,a,b,0,tag,'character_dialogue',text,speaker)
        self.events.append({'kind':'character_dialogue','speaker':speaker,'canonical_text':text,
                            'source_path':row['path'],'source_start_frame':row['source_start_frame'],
                            'source_end_frame':row['source_end_frame'],
                            'source_start_seconds':row['source_start_seconds'],
                            'source_end_seconds':row['source_end_seconds'],
                            'record_frame':row['record_frame'],'record_end_frame':row['record_end_frame'],
                            'source_script_episode':self.source,'reason':tag,
                            'word_timing_source':str(W/'ASR/raw_large-v3-turbo'/f'EP{self.ep:02d}'/'video'/f'女版{self.ep}-{name}.json')})
    def vo(self,name,a,b,text,visuals,tag,paragraphs=None):
        st,en=F(a),F(b)
        en=min(en,math.floor(MEDIA[path(self.ep,name,'narration')]['duration_seconds']*FPS))
        length=en-st;record=self.cursor
        capacity=sum(F(v[2])-F(v[1]) for v in visuals)
        if capacity < length:raise ValueError(f'EP{self.ep} {tag}: video shortage {length-capacity} frames')
        remain=length
        for n,va,vb,why in visuals:
            if remain<=0:break
            vf,ve=F(va),F(vb);count=min(remain,ve-vf)
            self.clip(n,vf/FPS,(vf+count)/FPS,-18,why+' | natural synchronous audio retained below narration','narration_coverage')
            remain-=count
        row={'path':path(self.ep,name,'narration'),'source_start_frame':st,'source_end_frame':en,
             'source_start_seconds':st/FPS,'source_end_seconds':en/FPS,
             'record_frame':record,'record_end_frame':record+length,'gain_db':0,
             'speed_percent':100,'kind':'narration','canonical_text':text,'tag':tag,'reason':tag}
        self.narr.append(row)
        self.events.append({'kind':'narration','speaker':'Eliza Mercer','canonical_text':text,
                            'source_path':row['path'],'source_start_frame':st,'source_end_frame':en,
                            'source_start_seconds':st/FPS,'source_end_seconds':en/FPS,
                            'record_frame':record,'record_end_frame':record+length,
                            'source_script_episode':self.source,'source_docx_paragraphs':paragraphs,
                            'reason':tag,'word_timing_source':str(W/'ASR/raw_large-v3-turbo'/f'EP{self.ep:02d}'/'narration'/f'女版{self.ep}-{name}.json')})
    def document(self):
        return {'episode':self.ep,'source_script_episode':self.source,
                'timeline_name':f'大码_女版_EP{self.ep:02d}_原速旁白_剧情顺序_自动剪辑_20261023_v1',
                'duration_frames':self.cursor,'duration_seconds':self.cursor/FPS,
                'video':self.video,'narration':self.narr,'audio_events':self.events,
                'limitations':self.limits,
                'media_selection_evidence':['素材盘点.json','画面联系图/索引.json',f'ASR/EP{self.ep:02d}_complete.json',f'ASR/EP{self.ep:02d}_dialogue_candidates.md'],
                'review_status':'Offline proposed cut; native assembly and playback have not been performed.'}

p=Plan(12,11)
p.vo('1',0,10.208333,
     "Seven days wasn't much time. I started preparing my application materials while packing up my things. On the second night, Matteo came to my apartment as usual.",
     [('1-2',0,4,'Application preparation and packing insert'),('1-1',3.5,10,'Continue packing into Matteo arrival')],
     'Original paragraphs 330–332; retain natural 100% narration speed',[330,331,332])
p.vo('2',0,4.416667,
     'He opened the closet and immediately noticed two of my pajama tops were missing.',
     [('2-4',0,4.416667,'Closet opening and empty hangers, before the question')],
     'VO2 first sentence only; stop before closet question',[333])
p.dialogue('2-1',6.208333,7.875,'Where are the two I like?','Matteo Bellandi','Main take question, with word-edge handles; do not use silent closet supplements as spoken substitutes')
p.dialogue('2-1',10.041667,12.416667,'They were old. I threw them away.','Eliza Mercer','Main take reply once, preserve synchronous picture and voice')
p.vo('2',4.625,13.916667,
     "He didn't ask any more questions. Once we were in bed, he instinctively wrapped an arm around my waist. I flinched in pain.",
     [('2-1',12.5,16,'Silent reaction after the closet answer'),('3-1',0,6,'In-bed waist touch and Eliza flinch before speaking')],
     'Resume the same VO2 file after the intervening two dialogue lines',[336,337,338])
p.vo('3',0,6.791667,
     'The finger-shaped bruises from that night still marked the soft skin around my waist. Matteo frowned.',
     [('3-1',5.791667,9.5,'Flinch reaction into Matteo frown, before his spoken question'),('4-1',0,3.2,'Bruise detail connects the narrated cause without repeating an action')],
     'Bruise detail and frown precede the question; no VO narration of role lines',[339,340])
p.dialogue('3-1',9.583333,11.166667,'Why are you pulling away?','Matteo Bellandi','Complete main take question')
p.dialogue('3-1',11.333333,13.416667,"It's nothing. Go to sleep.",'Eliza Mercer','Complete main take answer with no chopped final sleep')
p.vo('4',0,13.25,
     'Instead, he pulled up my shirt. Overlapping bruises covered my lower back. Matteo knelt beside the bed, gently touching the bruises, regret flickering across his face for the first time.',
     [('4-1',3.083333,12.583333,'Continue the main bruise reveal to kneeling concern before the line'),('4-2',0,4,'Same-scene kneeling and careful touch insert, no extra dialogue')],
     'Physical examination and regret; sentence order follows paragraphs 343–346',[343,344,345,346])
p.dialogue('4-1',12.583333,16.666667,"You always say it's nothing. You're wincing—who are you trying to fool?",'Matteo Bellandi','Retain full original sentence; ASR writes wincing as waning, canonical spelling from original script, pronunciation needs listening QC')
p.vo('5',0,8.166667,
     "He bought ointment downstairs, gently working it into my bruises with his own hands. We hadn't been this peaceful with each other in a long time.",
     [('5-1',0,8.166667,'Ointment application detail into quiet Eliza reaction')],
     'Ointment and temporary calm, original speed',[348,349])
p.vo('6',0,5.708333,
     'His belated concern still made my eyes sting, but I no longer dared mistake habit for love.',
     [('5-1',8.166667,14,'Continue Eliza reaction after the ointment without repeating the rub')],
     'Only the first sentence of VO6; contract question has not happened yet',[350])
p.vo('6',6.083333,7.75,'Matteo suddenly asked.',
     [('6-1',0,1.666667,'Contract-discussion setup before his lips begin the question')],
     'Lead-in to contract dialogue, keep the following narration for after her interruption',[351])
p.dialogue('6-1',3.25,6.291667,"Isn't your contract almost up? Remember to renew.",'Matteo Bellandi','Main take contract question and reminder once; both original lines complete')
p.dialogue('6-2',2.5,4,'Matteo, I—','Eliza Mercer','Use the closer hand-to-face insert for her interrupted start; no duplicated starts from other takes')
p.vo('6',7.75,11.416667,
     "Before I could tell him I wasn't renewing, Alessia called.",
     [('6-1',10.5,14.166667,'Her unfinished answer gives way to the call, before remote dialogue begins')],
     'VO6 resumed after contract dialogue and the interrupted Matteo, I—',[355])
p.dialogue('6-1',15.375,21.25,
           "Matteo, I cut my hand packing our camping gear. I always mess things up… I'll send someone to handle the gear. Stay home. I'm coming over.",
           'Alessia Varenna / Matteo Bellandi','One continuous main take phone exchange; Alessia remote then Matteo answer, no double narration')
p.vo('7',0,5.791667,
     "He didn't even cap the ointment before pulling on his coat. At the door, he finally asked,",
     [('7-3',0,1.5,'Uncapped ointment detail'),('7-1',1.75,6.041667,'Coat and doorway movement before the spoken question')],
     'VO7 lead-in only; omit its accidentally narrated role question at 5.94–8.38 seconds',[361,362])
p.dialogue('7-1',6.375,8.208333,'By the way, what were you about to say?','Matteo Bellandi','Only the synchronous male question is used; the duplicate question in MP3 is excluded')
p.vo('7',8.5,10.083333,'I looked at his back.',
     [('7-1',8.708333,10.291667,'Eliza looks toward Matteo at the doorway before her answer')],
     'Resume VO7 after the quoted male question, retaining only narrator text',[363])
p.dialogue('7-1',10.5,13.041667,"Nothing. It doesn't matter anymore.",'Eliza Mercer','Full final reply, no premature cut after Nothing')
p.clip('7-1',13.041667,14.333333,-8,'Quiet reaction after the last line, same-source room tone','reaction')
p.limits=[
    'User-labelled EP12 matches original DOCX Episode 11 (paragraphs 330–364), not source Episode 12. Timeline remains EP12 to match user media labels.',
    'ASR word times and frame samples support these cuts; native lip-sync/word-tail playback is still required. No human listening pass is claimed.',
    'VO7 contains the male role question read by the narrator; that MP3 span is deliberately excluded to avoid duplicate dialogue.',
    'The main 12-4-1 word wincing is recognized as waning; canonical text follows the original, but the actual pronunciation needs listening verification.',
    'The phone exchange is very fast in the supplied clip, retained at 100% speed rather than manufacturing additional speech.',
    'Supplement 12-6-2 presents a slightly different shared-bed pose from the wider discussion take; it is used only for her brief interrupted answer. Main-thread continuity review advised.',
    'No visual duration shortage after incorporating the supplied silent inserts; no freeze frame, generated padding or speed change was introduced.'
]

# Retain one continuous V1/A1 phone clip, but expose each original speaker line
# separately to the downstream word-timed SRT builder.
phone=next(e for e in p.events if e['reason'].startswith('One continuous main take phone'))
p.events.remove(phone)
for a,b,speaker,text in [
    (15.375,17.875,'Alessia Varenna','Matteo, I cut my hand packing our camping gear.'),
    (17.875,18.916667,'Alessia Varenna','I always mess things up…'),
    (18.916667,20.041667,'Matteo Bellandi',"I'll send someone to handle the gear."),
    (20.041667,21.25,'Matteo Bellandi',"Stay home. I'm coming over.")]:
    sf,ef=F(a),F(b)
    e=dict(phone, speaker=speaker,canonical_text=text,
           source_start_frame=sf,source_end_frame=ef,
           source_start_seconds=sf/FPS,source_end_seconds=ef/FPS,
           record_frame=phone['record_frame']+sf-phone['source_start_frame'],
           record_end_frame=phone['record_frame']+ef-phone['source_start_frame'])
    p.events.append(e)
p.events.sort(key=lambda x:x['record_frame'])

doc={'status':'READY_FOR_NATIVE_ASSEMBLY','project':'大码枕头','fps':FPS,'scope':[12],
     'source_inventory':str(W/'素材盘点.json'),'source_script':str(W.parent/'完整剧本/我不再做教父的大码人形抱枕EN.docx'),
     'assembly_contract':{'exclusive_source_end':True,'narration_speed_percent':100,'video_speed_percent':100,
                          'V1_A1_same_source_same_in_out_same_record':True,
                          'record_timecode_base':'00:00:00:00 relative frames; importer adds timeline start',
                          'preserve_original_media':True,'no_resolve_operation_by_this_plan':True},
     'episodes':[p.document()]}
(W/'female_edit_plan_EP12.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
(W/'female_edit_plan_EP12-13.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
print('EP12',p.cursor,p.cursor/FPS,'video',len(p.video),'VO',len(p.narr),'events',len(p.events))

q=Plan(13,12)
q.vo('1',0,1.083333,'The next afternoon,',
     [('1-1',0,1.083333,'Arrival setup; beginning of continuous main establishing take')],
     'Opening narration clause at 100%; only a small silence after the comma is trimmed',[367])
q.vo('1',1.291667,5.625,
     "I returned to the Bellandi estate to pack the clothes I'd left in Matteo's suite.",
     [('1-1',1.083333,5.416667,'Eliza arrives with suitcase and sees the room')],
     'Continue original narration; remove only inter-clause silence, not speech',[367])
q.vo('1',6.041667,7.958333,'Alessia was there with a stylist,',
     [('1-1',5.416667,7.333333,'Reveal Alessia and stylist while remaining in the same opening take')],
     'Second original sentence lead-in; trim part of the preceding natural gap',[368])
q.vo('1',8.125,11.083333,'trying on outfits for the weekend family charity gala.',
     [('1-1',7.333333,10.291667,'Continue outfit-fitting room establishment')],
     'Finish original sentence at 100%; no clothing terms added or altered in spoken source',[368])
q.vo('2',0,5.125,
     "She saw my suitcase and deliberately yanked out Matteo's favorite oversized pajama top.",
     [('1-1',10.291667,12.041667,'Alessia notices the suitcase, finishing the establishing take'),
      ('2-1',0,3.375,'Garment pull and Eliza reaction before the first spoken insult')],
     'VO2 first sentence only, before the first role question',[369])
q.dialogue('2-1',4,6.5,'This is what he insists on holding every night?','Alessia Varenna',
           'Main take first insult once, with clean word-edge handles')
q.vo('2',5.125,8.208333,'She unfolded it in front of the staff and stylist.',
     [('2-1',6.5,8.958333,'Garment held open after the question, before the unwanted extra words'),
      ('2-1',3.375,4,'Brief previously unused stationary Eliza reaction cutaway; no repeated action')],
     'VO2 resumes between the two original role lines; silent reaction coverage bridges the short gap',[371])
q.dialogue('2-1',10,13.333333,
           'I thought this was a piece of clothing. Turns out it’s a camping tent.',
           'Alessia Varenna','Use the complete canonical comparison; exclude the noncanonical extra Camping tent at 9.08–9.70 seconds')
q.vo('2',8.25,10.75,'Muffled laughter broke out around us.',
     [('2-1',13.333333,15.833333,'Staff and stylist visibly laugh after the complete insult')],
     'Narrated laughter follows the camping-tent line, not before it',[373])
q.vo('2',10.875,14.083333,'Alessia dropped it on the floor and stepped on it with her heel.',
     [('3-2',0,3.208333,'Drop and heel insert from the supplied supplement')],
     'VO2 last sentence precedes the next two insults',[374])
q.dialogue('3-1',3.875,6.208333,"Don't blame me for taking Matteo from you.",'Alessia Varenna',
           'First complete taunt; no duplicate use of the garment action')
q.dialogue('3-1',7.166667,13.083333,
           "A man might sleep with a weighted blanket, but he won't take it to a gala, and he definitely won't marry it.",
           'Alessia Varenna','Retain all three clauses, only shorten the silence before the sentence')
q.vo('3',0,10.041667,
     "I reached down, but she ground her heel into the sleeve and wouldn't move. Just then, Matteo walked in. I looked at him. For the first time, I wanted him to defend me.",
     [('3-3',0,4.125,'Eliza reaches toward the trapped garment, hand and heel relationship visible'),
      ('4-1',0,5.916667,'Matteo enters in the first frame; staff and Eliza reactions follow')],
     'Original paragraphs 377–380; inspect supplementary contact sheet for the actual entrance',[377,378,379,380])
q.vo('4',0,8.208333,
     'When I was nineteen, he made vicious loan sharks kneel in the rain for me. Now, all he had to do was tell Alessia to move her foot.',
     [('4-2',0,8.208333,'Present-day Eliza hope and the heel/Matteo relationship; do not fabricate a flashback')],
     'Memory is carried by the existing original narration over present-day reaction coverage',[381,382])
q.clip('5-1',1.75,5.875,-6,'Show Matteo pulling the chair for Alessia before he dismisses Eliza; natural chair sound retained','visual_direction')
q.dialogue('5-1',5.875,7.375,"She's just joking.",'Matteo Bellandi',
           'Clean first line from the main take; stop before the stray repeated Scene fragment')
q.dialogue('5-2',0.333333,1.833333,"Eliza, don't make a scene.",'Matteo Bellandi',
           'Complete close two-person take replaces the main take stray Scene at 9.58–10.14; say the canonical line only once')
q.clip('5-2',1.833333,2.5,-8,'Brief aftermath without any repeated role line','reaction')
q.vo('5',0,4.875,
     'I bent down, picked up the shoe-stained pajama top, and slowly folded it.',
     [('6-1',0,4.875,'Garment, shoe mark and the beginning of the fold before her spoken response')],
     'VO5 first sentence only; the decision narration must come after Understood',[386])
q.dialogue('6-1',7.666667,9.291667,'Understood, Mr. Bellandi.','Eliza Mercer',
           'Keep the main take reply once, with intact final name; ASR proper-name spelling needs listening QC')
q.vo('5',5.166667,9.125,'In that moment, my last bit of hesitation vanished.',
     [('6-1',9.291667,13.25,'Stay with Eliza holding the folded garment after her answer')],
     'VO5 resumes only after the spoken response, preserving the original emotional turn',[388])
q.clip('6-3',2.5,4.5,-8,'Supplied wide aftermath as Eliza leaves the room, no extra narration or dialogue','reaction')
q.limits=[
    'User-labelled EP13 matches original DOCX Episode 12 (paragraphs 367–388). The source Episode 13 phone/departure material must not be inserted here.',
    'Opening VO1 has about 0.79 seconds of internal pauses trimmed to fit the existing establishment and wardrobe action; all spoken words remain at 100% speed.',
    'The first garment scene contains a noncanonical extra Camping tent before the full comparison; the 9.08–9.70-second source span is excluded.',
    'The main Matteo dismissal contains a stray Scene fragment before the full line; the clean 13-5-2 close take supplies the canonical line once.',
    'VO2 She unfolded is covered by the garment hold and a 0.625-second previously unused stationary Eliza reaction from slightly earlier in the same take; no repeated frame range or action is used.',
    'No historical loan-shark footage exists in these supplied directories. That sentence stays over present-day hope/heel reaction coverage rather than inventing a flashback.',
    'Understood, Mr. Bellandi has differing ASR name spellings; proper-name articulation and word tails require actual listening/playback QC.',
    'All audio remains original, with V1/A1 identical source cuts. No voice synthesis, speed change, freeze frame or new footage has been added.'
]
qd=dict(doc,scope=[13],episodes=[q.document()])
(W/'female_edit_plan_EP13.json').write_text(json.dumps(qd,ensure_ascii=False,indent=2)+'\n')
doc['scope']=[12,13]
doc['episodes']=[p.document(),q.document()]
(W/'female_edit_plan_EP12-13.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n')
print('EP13',q.cursor,q.cursor/FPS,'video',len(q.video),'VO',len(q.narr),'events',len(q.events))
