"""Task-scoped official Resolve operations. Imports have no application side effects."""
import json,hashlib,sys
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
PROJECT='大码枕头'
EPISODES={7,8,9,12,13,14,15}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(p)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def connect():
    sys.path.insert(0,'/Users/zc/.codex/skills/davinci-resolve/scripts')
    from resolve_bootstrap import get_resolve
    r=get_resolve();m=r.GetProjectManager();p=m.GetCurrentProject()
    assert p.GetName()==PROJECT
    return r,m,p,p.GetMediaPool()
def timelines(p):return [p.GetTimelineByIndex(i) for i in range(1,p.GetTimelineCount()+1)]
def inventory(p):
    return [{'index':i,'name':t.GetName(),'id':t.GetUniqueId(),'fps':float(t.GetSetting('timelineFrameRate')),
             'start':t.GetStartFrame(),'end':t.GetEndFrame(),'vtracks':t.GetTrackCount('video'),
             'atracks':t.GetTrackCount('audio'),'stracks':t.GetTrackCount('subtitle')}
             for i,t in enumerate(timelines(p),1)]
def child(pool,parent,name):
    c=[x for x in parent.GetSubFolderList() or [] if x.GetName()==name];assert len(c)<=1
    f=c[0] if c else pool.AddSubFolder(parent,name);assert f;return f
def media(folder):
    out={}
    for x in folder.GetClipList() or []:
        path=x.GetClipProperty('File Path')
        if path:out.setdefault(path,x)
    for f in folder.GetSubFolderList() or []:out.update(media(f))
    return out
def load_plan(path):
    p=read(path);assert p['project']==PROJECT and p['fps']==24 and p['status']=='READY_FOR_NATIVE_ASSEMBLY'
    inv=read(BASE/'素材盘点.json');allowed={}
    for e in inv['episodes']:
        allowed[e['episode']]={'video':{v for g in e['video_groups'] for v in g['paths_in_version_order']},'narration':set(e['narration_paths_in_order'])}
    for e in p['episodes']:
        assert e['episode'] in EPISODES
        assert e['timeline_name'].startswith('大码_女版_EP%02d_'%e['episode'])
        for kind in ['video','narration']:
            last=0;ranges={}
            assert e[kind]
            for c in e[kind]:
                assert c['path'] in allowed[e['episode']][kind],('wrong source',c['path'])
                assert Path(c['path']).is_file()
                s,z,r=[c[k] for k in ['source_start_frame','source_end_frame','record_frame']]
                assert all(isinstance(v,int) for v in [s,z,r]) and 0<=s<z and r>=last
                if kind=='video':assert r==last,('picture gap',e['episode'],last,r)
                assert c.get('speed_percent',100)==100
                c['duration_frames']=z-s
                last=r+z-s;assert last<=e['duration_frames']
                for a,b in ranges.setdefault(c['path'],[]):assert z<=a or s>=b,('repeated source',c)
                ranges[c['path']].append((s,z))
            if kind=='video':assert last==e['duration_frames']
        for ev in e['audio_events']:
            assert ev['canonical_text'].strip()
            if ev['kind'] in ['dialogue','sync_dialogue','character_dialogue']:
                # Voice-over is kept clear of every synchronized spoken delivery.
                a=ev['record_frame'];z=a+ev['source_end_frame']-ev.get('clip_source_start_frame',ev['source_start_frame'])
                for c in e['narration']:
                    ns=c['record_frame'];ne=ns+c['duration_frames']
                    assert max(a,ns)>=min(z,ne),('VO and dialogue overlap',e['episode'],ev,c)
    return p
def assert_clip(item,c):
    assert item.GetStart()==c['record_frame']
    assert item.GetEnd()==c['record_frame']+c['duration_frames']
    assert item.GetSourceStartFrame()==c['source_start_frame']
    assert item.GetMediaPoolItem().GetClipProperty('File Path')==c['path']
    assert item.GetClipEnabled()
def av(t):
    return {k:[{'index':i,'name':t.GetTrackName(k,i),'items':[
        {'id':x.GetUniqueId(),'path':x.GetMediaPoolItem().GetClipProperty('File Path'),'start':x.GetStart(),'end':x.GetEnd(),
         'source_start':x.GetSourceStartFrame(),'source_end':x.GetSourceEndFrame(),'enabled':x.GetClipEnabled(),
         'gain':x.GetProperties().get('AudioVolume'),'links':sorted(y.GetUniqueId() for y in x.GetLinkedItems() or [])}
        for x in t.GetItemListInTrack(k,i) or []]} for i in range(1,t.GetTrackCount(k)+1)] for k in ['video','audio']}
