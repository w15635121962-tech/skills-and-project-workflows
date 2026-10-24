# -*- coding: utf-8 -*-
import json,re,math,hashlib,functools,collections,copy
from pathlib import Path
B=Path(__file__).resolve().parent.parent
OUT=Path(__file__).resolve().parent
assembly_path=B/'Resolve_组装实读.json'
assembly=json.loads(assembly_path.read_text())
index=json.loads((B/'ASR/转录索引.json').read_text())
mapdoc=json.loads((B/'剧本与素材主序对应.json').read_text())
files={x['source_path']:x for x in index['files']}
raws={p:json.loads(Path(x['json_path']).read_text()) for p,x in files.items()}
source_map={x['source_path']:x for e in mapdoc['episodes'] for x in e['narration_files_in_original_order']}
script={e['episode']:e['original_paragraphs'] for e in mapdoc['episodes']}
FPS=24
replaces={'vatoria':'Vittoria',
  'viteria':'Vittoria',
  'victoria':'Vittoria',
  'aldic':'Aldwick',
  'alderwick':'Aldwick',
  'verston':'Veriston',
  'raddiston':'Veriston',
  'alderwood':'Oliver',
  'evren': 'Evan',
  'gelped':'gulped'}
corrections=[]

def normalized(path,idx,w):
    s=w['word'].strip().replace('’',"'")
    old=s
    def sub(m):
        v=m.group();return replaces.get(v.lower(),v)
    s=re.sub(r"[A-Za-z]+",sub,s)
    stem=Path(path).stem
    if stem=='男版22-5':
        if idx==1:s='blue'
        if idx==3:s='amber'
    if stem=='男版21-4' and s=='13':s='thirteen'
    if stem=='男版25-9' and s=='17':s='seventeen'
    if stem=='男版25-9' and s=='17-year-old':s='seventeen-year-old'
    if stem=='男版21-3-1' and s=='Wait!':s='Wait.'
    if stem=='男版21-6-2' and s=='please.':s='please?'
    if stem=='男版21-3':
        if idx==40:s=s # One Free Wish casing set below by direct phrase indices.
    if old!=s:
        corrections.append({'source_path':path,
  'asr_word_index':idx,
  'raw':old,
  'display':s,
  'basis':'男版英文原稿及原音词义；不增加词'})
    return s

# Canonical case and punctuation only; no unspoken/source-missing clauses inserted.
for path,r in raws.items():
    for j,w in enumerate(r['words']):
        w['_display']=normalized(path,j,w)
    if Path(path).stem=='男版21-3':
        for j in range(len(r['words'])-2):
            ww=r['words'][j:j+3]
            if [re.sub(r'[^a-z]','',w['_display'].lower()) for w in ww]==['one','free','wish']:
                for k,ss in enumerate(['One','Free','Wish.']):
                    
                    if ww[k]['_display']!=ss:corrections.append({'source_path':path,
  'asr_word_index':j+k,
  'raw':ww[k]['word'].strip(),
  'display':ss,
  'basis':'男版原文 One Free Wish 卡片短语大小写'})
                    ww[k]['_display']=ss

bad_end={'a','an','the','and','or','to','of','for','with','from','in','at','on','my','his','her','their','your','our','that','this','as','if','but','by','had','was','were','have','has','is','are','be'}

def render(words):
    return re.sub(r'\s+(-[A-Za-z])',r'\1',' '.join(words))

protected_pairs={('crumpled','slip'),('slip','of'),('believed','her'),('entire','life'),('five','days'),('handful','of'),('again','and'),('and','again'),('cutting','in')}

def clean_word(s):return re.sub(r'[^A-Za-z0-9]','',s).lower()

def wrap_words(words):
    if not words:return None
    text=render(words)
    if len(text)<=30:return [text]
    options=[]
    for k in range(1,len(words)):
        a=render(words[:k]);b=render(words[k:])
        if words[k].startswith('-'):continue
        if len(a)>30 or len(b)>30:continue
        last=re.sub(r'\W','',words[k-1]).lower()
        penalty=abs(len(a)-len(b))*.08
        if last in bad_end:penalty+=1.4
        if re.search(r'[,;:]$',words[k-1]):penalty-=1
        if words[k].lower() in {'and','but','yet','because','until','so','then','while'}:penalty-=.5
        options.append((penalty,[a,b]))
    return min(options,key=lambda x:x[0])[1] if options else None

def partition(ws):
    n=len(ws)
    @functools.lru_cache(None)
    def dp(i):
        if i==n:return 0,[]
        choices=[]
        for j in range(i+1,min(i+13,n)+1):
            words=[w['display'] for w in ws[i:j]]
            lines=wrap_words(words)
            if lines is None:continue
            duration=ws[j-1]['timeline_word_end']-ws[i]['timeline_word_start']
            if duration>4.35:continue
            chars=len(render(words));last=words[-1]
            if any(re.search(r'[.!?]$',w) for w in words[:-1]) and not re.search(r'[.!?]$',last):continue
            if j<n and (ws[j]['display'].startswith('-') or (clean_word(last),clean_word(ws[j]['display'])) in protected_pairs):continue
            cost=1.0+(chars-45)**2/1200
            if chars<14:cost+=1
            if duration<.8:cost+=.9
            if re.search(r'[.!?]$',last):cost-=1.4
            elif re.search(r'[,;:]$',last):cost-=.35
            bare=re.sub(r'\W','',last).lower()
            if bare in bad_end:cost+=3.0
            if j<n:
                if ws[j]['display'].lower() in {'her,','him,','me,','us,','it,'}:cost+=1.2
                gap=ws[j]['timeline_word_start']-ws[j-1]['timeline_word_end']
                cost-=min(gap,.6)*.9
                if ws[j]['display'].lower() in {'and','but','yet','until','so','then','while','before','after','when'}:cost-=.25
            # Do not hold one cue across a clearly separate long pause.
            if any(ws[k+1]['timeline_word_start']-ws[k]['timeline_word_end']>.8 for k in range(i,j-1)):cost+=2
            rest,tail=dp(j)
            choices.append((cost+rest,[(i,j,lines)]+tail))
        if not choices:raise AssertionError(('no subtitle partition',ws[i:]))
        return min(choices,key=lambda x:x[0])
    return dp(0)[1]

def srt_time(frame):
    ms=round(frame*1000/24);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'

manifest={'schema':'male-21-25-srt-word-map-v1',
  'timing_basis':'实际Resolve组装实读的start/end/source_start（24fps）；原速ASR词时码；不依赖GetSourceEndFrame的媒体尾帧取整值',
  'timeline_start_timecode':'00:00:00:00',
  'fps':24,
  'assembly_path':str(assembly_path),'assembly_sha256':hashlib.sha256(assembly_path.read_bytes()).hexdigest(),
  'source_english':mapdoc['source_en'],
  'line_limit':3,
  'layout':'优先一至二行；每行至多30英文字符；短语分cue',
  'dialogue_selection':'正式同期对白窗口（gain_db=0）的实际原音话语；另纳入EP21多次独立盲复核一致的低声Oliver呼名，使用双来源合并cue；无依据重复识别不作对白',
  'episodes':[],
  'text_corrections':corrections,
  'excluded_source_text_notes':['EP21男版21-5-2录音不存在，Did she want me back in Veriston?没有在现有时间线播放，不补字幕。',"安静原片中ASR重复 I am sorry / Hello / going to 等，无原剧本和实际对白依据，排除；现场呼吸及叹词不强写为英文句子。"],
  'known_spoken_variants':["字幕保留已播放旁白中的 into pieces、we’d never、brows、must have 等词形，不把台词改成未播放的英文词。",'数字thirteen与seventeen-year-old、One Free Wish大小写按原文；角色地名和明显拼写识别错误按男版原文修正。']}
all_use=collections.defaultdict(collections.Counter)
for ep in assembly['episodes']:
    en=ep['episode'];cues=[];empty=[];clip_inventory=[]
    clips=[('narration',c) for c in ep['narration']]+[('dialogue',c) for c in ep['sync_audio'] if c.get('gain_db')==0]
    for kind,c in clips:
        if not c.get('enabled',True):continue
        path=c['path'];r=raws[path];a=c['source_start']/24;dur=(c['end']-c['start'])/24;z=a+dur;t=c['start']/24
        ws=[]
        for j,w in enumerate(r['words']):
            midpoint=(w['start']+w['end'])/2
            if not(a<=midpoint<z):continue
            # Empty/nonlexical punctuation alone is not an English spoken word.
            if not re.search(r'[A-Za-z0-9]',w['_display']):continue
            row={'kind':kind,
  'source_word_index':j,
  'raw':w['word'].strip(),
  'display':w['_display'],
  'source_word_start_seconds':w['start'],
  'source_word_end_seconds':w['end'],
  'probability':w.get('probability'),
  'timeline_word_start':max(c['start']/24,t+w['start']-a),
  'timeline_word_end':min(c['end']/24,t+w['end']-a)}
            ws.append(row)
            if kind=='narration':all_use[path][j]+=1
        clip_inventory.append({'kind':kind,
  'source_path':path,
  'source_start_frame':c['source_start'],
  'record_start_frame':c['start'],
  'record_end_frame':c['end'],
  'actual_source_end_seconds_exclusive':z,
  'api_source_end_frame':c.get('source_end'),
  'word_count':len(ws),
  'clip_id':c['id'],
  'tag':c.get('tag')})
        if not ws:
            empty.append({'kind':kind,
  'path':path,
  'source_seconds':[a,z],
  'record_frames':[c['start'],c['end']],
  'reason':'保留反应/无可识别原文对白，未补字幕'})
            continue
        for i,j,lines in partition(ws):
            selected=ws[i:j]
            f0=max(c['start'],math.floor(selected[0]['timeline_word_start']*24+1e-7))
            speech_end=math.ceil(selected[-1]['timeline_word_end']*24-1e-7)
            f1=min(c['end'],max(speech_end+3,f0+12))
            source_paras=(source_map[path].get('source_paragraphs',[]) if kind=='narration' else [p['index'] for p in script[en] if Path(path).stem in p.get('dialogue_candidate_stems',[])])
            cues.append({'start_frame':f0,
  'end_frame':f1,
  'lines':lines,
  'text':'\n'.join(lines),
  'kind':kind,
  'source_path':path,
  'asr_json_path':files[path]['json_path'],'source_sha256':files[path]['source_sha256'],
  'source_script_paragraphs':source_paras,
  'actual_clip_id':c['id'],
  'actual_source_start_frame':c['source_start'],
  'actual_record_start_frame':c['start'],
  'actual_record_end_frame':c['end'],
  'words':selected})
    if en==21:
        # Native whisper under the narration: three independent blind excerpts agree.
        # Merge the overlap into one cue instead of overlapping two SRT events.
        host_index=next(i for i,c in enumerate(cues) if Path(c['source_path']).stem=='男版21-2' and c['words'][0]['source_word_index']==0)
        host=cues[host_index]
        assert len(host['words'])==10
        call_clip=next(c for c in ep['sync_audio'] if Path(c['path']).stem=='男版21-2-1' and c['source_start']==0 and c['start']==342)
        call_path=call_clip['path'];cw=raws[call_path]['words'][0]
        assert cw['_display']=='Oliver.' and cw['start']==2.2 and cw['end']==3.6
        left=copy.deepcopy(host);right=copy.deepcopy(host)
        left['words']=left['words'][:5]
        left['lines']=wrap_words([w['display'] for w in left['words']]);left['text']='\n'.join(left['lines'])
        right['words']=right['words'][5:]
        right['start_frame']=math.floor(right['words'][0]['timeline_word_start']*24+1e-7)
        left['end_frame']=right['start_frame']
        call_word={'kind':'dialogue',
  'source_path':call_path,
  'source_word_index':0,
  'raw':cw['word'].strip(),
  'display':'Oliver.',
  'source_word_start_seconds':cw['start'],
  'source_word_end_seconds':cw['end'],
  'probability':cw.get('probability'),
  'timeline_word_start':call_clip['start']/24+cw['start']-call_clip['source_start']/24,
  'timeline_word_end':call_clip['start']/24+cw['end']-call_clip['source_start']/24,
  'actual_source_start_frame':call_clip['source_start'],
  'actual_record_start_frame':call_clip['start'],
  'actual_record_end_frame':call_clip['end'],
  'actual_clip_id':call_clip['id'],
  'asr_json_path':files[call_path]['json_path'],'source_sha256':files[call_path]['source_sha256']}
        right['lines']=[render([w['display'] for w in right['words']]),'- Oliver.']
        right['text']='\n'.join(right['lines'])
        right['words'].append(call_word)
        right['kind']='narration_and_dialogue'
        right['additional_sources']=[{'kind':'dialogue',
  'source_path':call_path,
  'clip_id':call_clip['id'],
  'source_seconds':[2.2,3.6],
  'timeline_seconds':[16.45,17.85],
  'script_status':'源原稿无此口述；实际原片低声梦中呼名',
  'evidence':str(OUT/'核验报告/21_2_1_非原稿呼名_独立盲复核.json'),
  'validation':'3次独立无提示盲ASR + 原全片ASR一致；未宣称人工听辨'}]
        cues[host_index:host_index+1]=[left,right]
    cues.sort(key=lambda x:(x['start_frame'],x['end_frame']))
    for i,c in enumerate(cues):
        if i+1<len(cues):c['end_frame']=min(c['end_frame'],cues[i+1]['start_frame'])
        c['end_frame']=min(c['end_frame'],ep['duration_frames'])
        assert c['end_frame']>c['start_frame'],(en,i,c)
        assert len(c['lines'])<=3 and all(len(line)<=30 for line in c['lines'])
        assert c['start_frame']>=0 and c['end_frame']<=ep['duration_frames']
        assert i==0 or cues[i-1]['end_frame']<=c['start_frame']
        c['number']=i+1;c['start_srt']=srt_time(c['start_frame']);c['end_srt']=srt_time(c['end_frame'])
    text='\n\n'.join(f"{c['number']}\n{c['start_srt']} --> {c['end_srt']}\n{c['text']}" for c in cues)+'\n'
    output=OUT/f'EP{en}.srt';output.write_text(text,encoding='utf-8-sig')
    manifest['episodes'].append({'episode':en,
  'timeline_name':ep['timeline'],
  'timeline_id':ep['id'],
  'duration_frames':ep['duration_frames'],
  'duration_seconds':ep['duration_frames']/24,
  'srt_path':str(output),'srt_sha256':hashlib.sha256(output.read_bytes()).hexdigest(),
  'cue_count':len(cues),
  'narration_cues':sum('narration' in c['kind'] for c in cues),
  'dialogue_cues':sum('dialogue' in c['kind'] for c in cues),
  'max_lines':max(len(c['lines']) for c in cues),
  'max_line_characters':max(len(line) for c in cues for line in c['lines']),
  'clips':clip_inventory,
  'unsubtitled_reaction_clips':empty,
  'cues':cues})
for path,count in all_use.items():
    for j,w in enumerate(raws[path]['words']):
        assert count[j]==1,(path,j,w,count[j])
used_words={(w.get('source_path',c['source_path']),w['source_word_index']) for e in manifest['episodes'] for c in e['cues'] for w in c['words']}
manifest['text_corrections']=[x for x in corrections if (x['source_path'],x['asr_word_index']) in used_words]
final_use=collections.defaultdict(collections.Counter)
for e in manifest['episodes']:
    for c in e['cues']:
        for w in c['words']:
            wp=w.get('source_path',c['source_path'])
            if w['kind']=='narration':final_use[wp][w['source_word_index']]+=1
            anchor_source=w.get('actual_source_start_frame',c['actual_source_start_frame'])
            anchor_record=w.get('actual_record_start_frame',c['actual_record_start_frame'])
            calc=anchor_record/24+w['source_word_start_seconds']-anchor_source/24
            assert abs(calc-w['timeline_word_start'])<1/24+1e-6,(e['episode'],c['number'],w)
assert dict(final_use)==dict(all_use)

manifest['checks']={'all_34_narration_sources_covered':len(all_use)==34,
  'each_narration_asr_word_used_exactly_once':True,
  'all_cues_with_source_word_trace':True,'all_24fps_aligned':True,
  'overlapping_cues':0,
  'cues_beyond_timeline':0,
  'actual_soft_Oliver_call_included_after_independent_blind_crosscheck':True,
  'audio_video_mutated':False,
  'timeline_actual_readback_used':True}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
for e in manifest['episodes']:print(e['episode'],e['cue_count'],'N',e['narration_cues'],'D',e['dialogue_cues'],'maxlines',e['max_lines'],'maxchars',e['max_line_characters'])
print('34 VO sources exactly once; all cues bounded, no overlap.')
