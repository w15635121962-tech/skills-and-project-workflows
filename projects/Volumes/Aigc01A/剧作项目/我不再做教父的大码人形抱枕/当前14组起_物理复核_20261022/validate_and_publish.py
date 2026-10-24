from pathlib import Path
from decimal import Decimal
import json,re,hashlib,copy,shutil
R=Path(__file__).resolve().parent;C=R.parent/'\u590d\u523b\u5168\u96c6_FormatC_V25_20261022'
old=json.loads((R/'\u4fee\u6539\u524d_\u590d\u523b\u5168\u96c6_FormatC_V25_\u5168\u90e8\u63d0\u793a\u8bcd.json').read_text())
new=json.loads((R/'\u7269\u7406\u4fee\u8ba2\u540e_22\u7ec4\u5f85\u56de\u5199.json').read_text())
live=json.loads((R/'\u5e73\u53f0\u7b2c14\u81f322\u7ec4_\u4fee\u8ba2\u540e\u91cd\u5f00\u56de\u8bfb.json').read_text());by={x['position']:x for x in live}
before=json.loads((R/'\u4fee\u6539\u524d_\u5e73\u53f0\u7b2c14\u81f322\u7ec4.json').read_text());bb={x['position']:x for x in before}
patches=json.loads((R/'\u5168\u90e8\u7269\u7406\u4fee\u8ba2_\u7cbe\u786e\u8865\u4e01.json').read_text())
source=Path('/Users/zc/.codex/skills/short-drama-prompts-v3/references/format-c-v2.5-source.md').read_text()
quality=next(x for x in source.splitlines() if x.startswith('\u5199\u5b9e\u7167\u7247\u7ea7\u3001'));skin=next(x for x in source.splitlines() if x.startswith('\u5f3a\u5236\u8981\u6c42\uff1a \u4eba\u7269\u76ae\u80a4\u987b'))
fields=['\u53d9\u4e8b\u4efb\u52a1\uff08Narrative Task\uff09','\u955c\u5934','\u753b\u9762','\u89c6\u89c9\u5f15\u5bfc\uff08Visual Flow\uff09','\u5fae\u8868\u6f14\uff08Micro-Performance\uff09','\u5bf9\u767d\u53cd\u5e94\uff08Dialogue Reaction\uff09','\u4eba\u7269\u80cc\u666f\u878d\u5408\uff08Subject-Background Integration\uff09','\u5149\u5f71\u7ec6\u8282\uff08Lighting Detail\uff09','\u97f3\u9891\uff08Audio\uff09','\u8fd0\u52a8\u5f3a\u5ea6\uff08Motion Intensity\uff09','\u8d1f\u9762\u63d0\u793a\u8bcd\uff08Negative Prompt\uff09']
norm=lambda x:re.sub(r'\s+','',x)
plain=lambda x:re.sub(r'\xa7ASSET:([^\xa7]+)\xa7',r'\1',x)
assert len(new['groups'])==len(old['groups'])==22
assert set(by)==set(range(14,23));assert len(patches)==46
results=[]
for a,b in zip(old['groups'],new['groups']):
 pos=b['timeline_position'];p=b['prompt']
 for k in ['index','episode','title','duration','dialogue_lines','timeline_position','source_paragraphs','platform_url','storyboard_id']:
  assert a.get(k)==b.get(k),(pos,k)
 assert re.findall(r'^\u97f3\u9891\uff08Audio\uff09\uff1a.*$',a['prompt'],re.M)==re.findall(r'^\u97f3\u9891\uff08Audio\uff09\uff1a.*$',p,re.M),(pos,'audio')
 assert re.findall(r'\xa7ASSET:[^\xa7]+\xa7',a['prompt'])==re.findall(r'\xa7ASSET:[^\xa7]+\xa7',p)
 assert re.findall(r'duration:\s*([\d.]+)s',a['prompt'])==re.findall(r'duration:\s*([\d.]+)s',p)
 if pos<14:assert a['prompt']==p,(pos,'unauthorized_change')
 if pos!=21:assert re.findall(r'\u3010shot[^\u3011]+\u3011',a['prompt'])==re.findall(r'\u3010shot[^\u3011]+\u3011',p)
 else:
  assert b['shots'][2]['size']=='LS'
  assert '\u3010shot 3\uff5c\u770b\u6e05\u5750\u4e0b\u7684\u627f\u6258\u8fc7\u7a0b\uff5c\u5168\u666f\uff08LS\uff09' in p
 assert p.count(quality)==p.count(skin)==p.count('\u56fa\u5b9a\u753b\u8d28\u8bcd\uff08Fixed Quality Descriptor\uff09')
 assert len(p)<15000
 durations=re.findall(r'duration:\s*([\d.]+)s',p)
 assert sum((Decimal(x) for x in durations),Decimal(0))==Decimal(str(b['duration']))
 for block in re.split(r'\u3010shot\s+\d+[^\u3011]*\u3011',p)[1:]:
  for f in fields:assert len(re.findall('^'+re.escape(f)+'\uff1a',block,re.M))==1,(pos,f)
 if pos in by:
  r=by[pos];assert norm(r['text'])==norm(plain(p)),(pos,'live_body')
  assert [x['text'] for x in r['cards']]==re.findall(r'\xa7ASSET:([^\xa7]+)\xa7',p)
  assert r['cards']==bb[pos]['cards'],(pos,'asset_source')
  assert r['params']==bb[pos]['params'],(pos,'generation_settings')
  assert r['url']==bb[pos]['url']==b['platform_url']
  b['native_asset_status']='saved_and_reopened_verified'
  results.append({'position':pos,'body_reopened_exact':True,'native_cards_and_sources_preserved':True,'settings_preserved':True,'patches':sum(x['timeline_position']==pos for x in patches)})
summary={'groups_reviewed':9,'positions':list(range(14,23)),'paragraph_patches':46,'group_count':22,'shots':sum(len(g['shots']) for g in new['groups']),'planned_seconds':sum(g['duration'] for g in new['groups']),'dialogue_lines':sum(len(g['dialogue_lines']) for g in new['groups']),'audio_fields_unchanged':True,'source_assets_unchanged':True,'timings_unchanged':True,'groups_1_to_13_unchanged':True,'reopened_all_9':True,'only_shot_size_change':'G21 shot3 MS to LS for full support chain','existing_video_review':{'position':14,'duration':8.064,'sampled_times':[0,2.4,6.4,8.0],'posture_continuity_passed':False,'findings':['2.4\u79d2\u4e0e\u672b\u6001\u7537\u4e3b\u4e0a\u8eab\u7ad6\u8d77\u3001\u5934\u672a\u538b\u6795\uff0c\u504f\u79bb\u539f\u4fa7\u5367\u627f\u6258','\u5973\u4e3b6.4\u79d2\u4e0e\u672b\u6001\u95ed\u773c\uff1b\u5f53\u524d\u5e94\u4ec5\u5782\u773c\uff0c\u4e0b\u4e00\u7ec4\u624d\u95ed\u773c\u88c5\u7761'],'video_replaced':False,'full_dynamic_and_lipsync_review_claimed':False},'later_videos_status':'\u7b2c15\u201322\u7ec4\u4e3a\u672a\u751f\u6210\u7a7a\u69fd\uff1b\u672c\u6b21\u4ec5\u63d0\u793a\u8bcd\u7269\u7406\u53ef\u6267\u884c\u6027\u5ba1\u6838','generation_submitted':False,'findings':['14\u201316\u9010\u955c\u9501\u5b9a\u8eaf\u5e72\u6cbf\u5e8a\u957f\u5e73\u884c\u5e8a\u9762\u3001\u7537\u4e3b\u5de6\u4fa7\u5934\u80a9\u9acb\u627f\u6258\uff0c\u9632\u6b62\u5750\u8d77','14\u5973\u4e3b\u5782\u773c\u4f46\u4e0d\u63d0\u524d\u88c5\u7761\uff0c15\u88c5\u7761\uff0c16\u7537\u4e3b\u771f\u7761\uff0c17\u5973\u4e3b\u59cb\u7ec8\u6e05\u9192\u540e\u7741\u773c','17\u5973\u4e3b\u7528\u81ea\u5df1\u7684\u5de6\u638c\u548c\u53f3\u8098\u81ea\u6491\uff0c\u5934\u80a9\u79bb\u6795\u540e\u4e0d\u80fd\u518d\u8bf4\u5934\u4ecd\u538b\u6795','17\u7537\u4e3b\u677e\u5f1b\u5de6\u638c\u4ec5\u88ab\u52a8\u77ed\u5e45\u6ed1\u79bb\u539f\u4e0a\u80cc\u63a5\u70b9\u5230\u65c1\u4fa7\u5e8a\u9762\uff0c\u4e0d\u65e0\u8def\u5f84\u6ed1\u5230\u8170\u80cc','16\u4e0e18\u5c40\u90e8\u53d6\u666f\u4e0d\u786c\u585e\u753b\u5916\u773c\u7751\u6216\u80a9\u7ebf','19\u201320\u6587\u4ef6\u6cbf\u53ef\u8fbe\u684c\u9762\u8f6c\u5411/\u6ed1\u9001\uff0c\u4e0d\u8d8a\u8fc7\u4e2d\u592e\u6446\u4ef6\u8de8\u684c\u9012\u4ea4','21\u5b8c\u6574\u5750\u5730\u8fc7\u7a0b\u7528\u5168\u666f\u4fdd\u7559\u811a\u3001\u638c\u3001\u5750\u9aa8\u843d\u70b9\uff1b\u56fa\u5b9a\u5899\u5730\u627f\u6258\u4e14\u907f\u95e8\u6247','22\u4fdd\u9556\u7559\u540e\u4fa7\uff0c\u89c6\u7ebf\u4e0e\u53f3\u624b\u6307\u5411\u53ef\u89c1\uff0c\u53f3\u624b\u4e0d\u7b49\u540c\u9760\u5899\u4fa7'],'results':results,'passed_prompt_scope':True}
(R/'\u5b8c\u6210\u6838\u9a8c.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
new['physics_review_report']=str((R/'\u5b8c\u6210\u6838\u9a8c.json').resolve())
(C/'\u590d\u523b\u5168\u96c6_FormatC_V25_\u5168\u90e8\u63d0\u793a\u8bcd.json').write_text(json.dumps(new,ensure_ascii=False,indent=2))
(C/'\u590d\u523b\u5168\u96c6_FormatC_V25_\u5168\u90e8\u63d0\u793a\u8bcd.md').write_text('\n\n---\n\n'.join(g['prompt'] for g in new['groups']))
(C/'\u5f53\u524d22\u7ec4\u7248\u672c\u8bf4\u660e.md').write_text('\u5f53\u524d\u6743\u5a01\u7a3f\u4e3a22\u7ec4\uff0c\u5df2\u8865\u76d6\u88ab\u73af\u7ed5\u7ec4\uff08\u7b2c7\u7ec4\uff09\uff0c\u672c\u6b21\u7b2c14\u201322\u7ec4\u7269\u7406\u590d\u6838\u5df2\u56de\u5199\u4e0e\u91cd\u5f00\u9a8c\u8bc1\u3002\n\n\u539f21\u7ec4\u5206\u7247\u53ca\u8865\u76d6\u88ab\u5f52\u6863\u662f\u5386\u53f2\u5feb\u7167\uff0c\u4e0d\u5f97\u76f4\u63a5\u6c47\u603b\u8986\u76d6\u5f53\u524d\u7a3f\u3002\u6700\u65b0\u6838\u9a8c\u89c1 ../\u5f53\u524d14\u7ec4\u8d77_\u7269\u7406\u590d\u6838_20261022/\u5b8c\u6210\u6838\u9a8c.json \u3002\u539f\u5bf9\u767d\u3001\u8d44\u4ea7\u4e0e\u8ba1\u5212\u65f6\u957f\u4e0d\u53d8\u3002\u7b2c14\u7ec4\u65e78\u79d2\u6210\u7247\u4ecd\u6709\u5750\u59ff\u504f\u5dee\uff0c\u672c\u8f6e\u53ea\u4fee\u63d0\u793a\u8bcd\uff0c\u672a\u91cd\u65b0\u751f\u6210\u3002\n')
(R/'\u4fee\u8ba2\u540e_\u6743\u5a0122\u7ec4.json').write_text(json.dumps(new,ensure_ascii=False,indent=2))
md=['# \u7b2c14\u201322\u7ec4\u4eba\u7269\u72b6\u6001\u4e0e\u7269\u7406\u590d\u6838','\u5df2\u5bf99\u7ec4\u5e73\u53f0\u6b63\u6587\u3001\u8d44\u4ea7\u4e0e\u8bbe\u7f6e\u56de\u8bfb\u300246\u5904\u6bb5\u843d\u4fee\u8ba2\uff1b\u539f\u53f0\u8bcd\u3001\u65f6\u957f\u3001\u8d44\u4ea7\u548c\u5267\u60c5\u987a\u5e8f\u4fdd\u7559\u3002','\n\u672c\u6b21\u4fee\u6b63\uff1a']+['- '+x for x in summary['findings']]+['\n\u7b2c14\u7ec4\u5df2\u67098.064\u79d2\u89c6\u9891\u7684\u5173\u952e\u5e27\u6838\u5bf9\uff1a']+['- '+x for x in summary['existing_video_review']['findings']]+['\n\u8be5\u89c6\u9891\u5e76\u672a\u66ff\u6362\u3002\u672c\u6b21\u672a\u63d0\u4ea4\u751f\u6210\uff1b15\u201322\u7ec4\u53ea\u5b8c\u6210\u63d0\u793a\u8bcd\u5ba1\u6838\uff0c\u4e0d\u58f0\u79f0\u6210\u7247\u7269\u7406\u901a\u8fc7\u3002','\n\u53c2\u8003\u8bc1\u636e\uff1a','- [\u7b2c14\u7ec42.4\u79d2\u6210\u7247](\u7b2c14\u7ec4_\u6210\u7247_2.4\u79d2.png)','- [\u7b2c14\u7ec4\u672b\u6001](\u7b2c14\u7ec4_\u6210\u7247_\u672b\u5e27.png)','- [\u7b2c17\u7ec4\u4fee\u8ba2\u56de\u8bfb](\u5267\u68a6_\u7b2c17\u7ec4_\u638c\u8098\u627f\u91cd\u4fee\u8ba2_\u56de\u8bfb.png)']
(R/'\u6838\u9a8c\u7ed3\u8bba.md').write_text('\n'.join(md)+'\n')
# Guard the historical 21-group builder against overwriting current 22-group work.
p=C/'validate_prompts.py';s=p.read_text();oldmsg='\u5f53\u524d\u6743\u5a01\u7a3f\u4e3a22\u7ec4\uff1b\u6b64\u811a\u672c\u4ec5\u9a8c\u8bc1\u5386\u53f221\u7ec4\uff0c\u5df2\u963b\u6b62\u8986\u76d6\u3002\u8bf7\u4f7f\u7528\u8865\u76d6\u88ab\u4e0e\u88ab\u5185\u73af\u7ed5_20261022/merge_blanket_archive.py\u4e0e\u5e73\u53f0\u6700\u7ec8\u56de\u8bfb_22\u7ec4.json\u3002'
s=s.replace(oldmsg,'\u5f53\u524d\u6743\u5a01\u7a3f\u4e3a22\u7ec4\u4e14\u5df2\u66f4\u65b0\u7b2c14\u201322\u7ec4\u7269\u7406\u5173\u7cfb\uff1b\u6b64\u811a\u672c\u4ec5\u9a8c\u8bc1\u5386\u53f221\u7ec4\uff0c\u5df2\u963b\u6b62\u8986\u76d6\u3002\u5f53\u524d\u6838\u9a8c\u4f4d\u4e8e \u5f53\u524d14\u7ec4\u8d77_\u7269\u7406\u590d\u6838_20261022/\u5b8c\u6210\u6838\u9a8c.json\u3002')
p.write_text(s)
print(json.dumps({'passed':True,'groups_reopened':9,'patches':46,'audio_assets_durations_preserved':True,'old_video_replaced':False,'sha256':hashlib.sha256((C/'\u590d\u523b\u5168\u96c6_FormatC_V25_\u5168\u90e8\u63d0\u793a\u8bcd.json').read_bytes()).hexdigest()},ensure_ascii=False))
