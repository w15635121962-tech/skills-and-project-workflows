import runpy,json,re,hashlib
from pathlib import Path
NS=runpy.run_path(str(Path(__file__).with_name('适配源稿.py')));ROOT=NS['ROOT'];OUT=NS['OUT'];SRC=NS['SRC'];rows=[NS['adapt'](r) for e in [7,8,9] for r in NS['fields'](e)]
locks={}
for fn in ['position_asset_locks_EP07_01-10.json','position_asset_locks_EP07_all.json','position_asset_locks_EP08_all.json','position_asset_locks_EP09_all.json','position_asset_locks.json']:
 p=OUT/fn
 if p.exists():
  d=json.loads(p.read_text(encoding='utf-8'))
  if isinstance(d,dict):d=d.get('shots',d.get('locks',[]))
  for x in d:locks[x['ep'],x['shot']]=x

def clean(p,ep,n,sc):
 for a,b in [(r'\brobes?\b','garment'),(r'\bpajamas\b','clothing'),(r'\bsuits?\b','clothing'),(r'\bshirts?\b','clothing'),(r'\bskirts?\b','clothing'),(r'\bcardigan\b','clothing'),(r'\bslender\b','plus-size')]:p=re.sub(a,b,p,flags=re.I)
 p=p.replace('white small-floral pajamas with pink lace','designated clothing').replace('dark blazer, white clothing, striped necktie, plaid clothing and knee-high socks','designated clothing')
 p=re.sub(r'深色校服西装/白衬衫/条纹领带/格纹裙/长袜','本镜指定18岁资产衣物',p)
 p=re.sub(r'女主穿[^,，;；。\n]*(?:套装|开衫|连衣裙|睡衣|衬衫|长袜)', '女主按指定资产衣着',p)
 # Bedding remains a physical prop, but its appearance follows this room's actual asset.
 for a in ['pink checkered duvet','pink-white checkered duvet','pink fluffy blanket','pink bedding','pink cover','粉色格纹被单','粉白格纹被单','粉色毛绒毯','粉色被单','粉色被子','白色床单']:
  p=p.replace(a,'asset-matched bedding' if a[0].isascii() else '场景资产中的被面')
 for a in ['white small plush toy','white plush rabbit','white plush bunny','white bunny','plush bunny','small white fluffy toy','white fluffy toy','白色小毛绒玩具','白毛绒兔','白毛绒玩具']:
  p=p.replace(a,'designated old teddy bear' if a[0].isascii() else '既定旧熊玩偶')
 if 'L1' in sc or 'L2' in sc:
  p=p.replace('light-wood headboard',"established headboard from the Eliza bedroom asset").replace('浅木小床照片墙','既定小床与照片墙').replace('浅木床头','既定床头')
  p=p.replace('a photo wall and night-window bokeh behind her',"the asset's fixed photo arrangement and existing window softly defocused in their actual room locations")
  p=p.replace('a warm bedside lamp glows on the left',"the bedside lamp stays on the bed's actual right cabinet, its screen position derived from this camera")
  p=p.replace('warm key from the lamp at frame-left',"warm key from the bed's actual right-cabinet lamp")
  p=p.replace('台灯在左','台灯固定实际床右柜，画面位置随机位推导')
 if 'L3' in sc:
  p=p.replace('wine-red velvet tufted, gold-carved mansion bed',"established mansion bed from the Matteo bedroom asset").replace('wine-red velvet tufted, gold-carved headboard',"established upholstered headboard from the Matteo bedroom asset")
  p=p.replace('酒红丝绒拉扣+金雕花床头','Matteo卧室既定软包床头').replace('酒红丝绒拉扣+金雕花','既定软包床头').replace('gold-carved headboard','established upholstered headboard')
 if 'L4' in sc:
  p=p.replace('fireplace','existing warm practical lamps').replace('壁炉火光','既有实景暖灯').replace('壁炉','既有实景暖灯')
  p=p.replace('Dante','Matteo')
 if 'L7' in sc:
  p=p.replace('a floor-to-ceiling window shows the city skyline',"the established entrance door and fixed furnishings remain in the positions shown in the living-room-and-entrance asset")
  p=p.replace('floor-to-ceiling window and city lights','established entrance and room furnishings').replace('落地窗夜景','既定入户门与两侧家具').replace('落地窗城市夜景','既定入户门与两侧家具')
 if ep==7:
  p=re.sub(r'\b(?:baby|babe)\b','ALLIE',p,flags=re.I)
 if ep==7 and n==15:
  p=p.replace('she stares straight upward toward the camera','she looks upward toward the space just above Matteo, off-lens').replace('Eliza looking straight up at lens','Eliza looking upward off-lens')
  p=re.sub(r'NOTE: this is the ONLY shot[^\n]*',"NOTE: retain the stunned open-eyed reaction but keep the dramatic eyeline just off-lens; do not address the viewer. Head-to-feet direction stays unchanged.",p)
 p=p.replace('small light-wood bed', 'established small bed from the Eliza bedroom asset').replace('white plush toy','designated old teddy bear').replace('pink duvet','asset-matched duvet')
 p=p.replace('soft fire crackle','quiet room ambience').replace('quiet fire crackle','quiet room ambience').replace('faint fire crackle','quiet room ambience').replace('soft fire','quiet room ambience')
 p=p.replace('EMPLOYMENT RENEWAL AGREEMENT','CONTRACT RENEWAL AGREEMENT').replace('EMPLOYMENT AGREEMENT','CONTRACT RENEWAL AGREEMENT')
 if ep==7 and n==25:p=p.replace('his words leave her pensive','his closeness leaves her pensive')
 if ep==7 and n==45:p=p.replace('he nods and gives a short, amused reply into the phone','he nods with a short, amused breath while listening to the phone')
 if ep==8 and n==53:p=p.replace('he asks his question','he notices the tension, visibly puzzled')
 if ep==9:
  p=p.replace('black coffee','tea').replace('coffee','tea').replace('咖啡','茶')
  if n==6:p=p.replace('medium shot from behind; Matteo bends to tap the phone to answer, then rises', 'medium shot from his front-side as in the source HEAD: Matteo is seated at the shared table after the preceding time-ellipsis; he bends to tap and take the phone, then rises')
  if n==11:
   p=p.replace('女主站着,夫人抬眼看','女主仍坐着,夫人抬眼看向她').replace('夫人抬眼向上看(站着的女主)','夫人抬眼看向仍坐着的女主').replace('she looks upward because Eliza now stands','she lifts her gaze to the still-seated Eliza').replace('she raises her eyes to the standing Eliza','she raises her eyes to the still-seated Eliza').replace('upward, demeaning stare','level, demeaning stare').replace('Serafina looking up, delivering the cruel line','Serafina holding the source warning gaze toward seated Eliza while delivering the line')
  if n==12:p=p.replace('the standing Eliza','the still-seated Eliza')
  if n==15:
   p=p.replace('she bends slightly to be level with her', 'she makes the source small respectful bow while remaining standing; their natural standing-versus-seated eye heights stay different').replace('she clasps her hands and speaks politely, dignified','she clasps her hands with the source polite, dignified expression, remaining silent').replace('courteous, level gaze','courteous downward gaze toward the seated woman').replace('speaking politely to Serafina','keeping the polite expression toward Serafina without repeating any dialogue')
  if n==18:
   p=p.replace('empty wine-red leather tufted chair-back','back of a separate existing empty red chair in the foreground, with Serafina still seated on her original red chair').replace('empty wine-red tufted chair-back','foreground back of the separate empty red chair; Serafina remains seated on her original chair').replace('empty chair-back','separate foreground chair-back').replace('空酒红皮椅背','另一张既有空红椅的靠背').replace('空皮椅背','前景另一张既有空红椅靠背')
  if n==19:
   p=p.replace('台历MADDAS红圈数字7,下方续约合同EMPLOYMENT也被圈','台历作为剩余7天的功能提示，仅保留明确数字7；下方是既定续约合同')
   p=p.replace('a standing desk calendar reads "MADDAS" with the number 7 circled in red; below it lies an "CONTRACT RENEWAL AGREEMENT" with the word "EMPLOYMENT" circled in red','a simple desk countdown marker clearly shows 7 days remaining, with no copied AI gibberish; below it lies the designated CONTRACT RENEWAL AGREEMENT')
  if n==20:p=p.replace('she speaks from the chair while Eliza stands still and listens','she holds the source stern gaze from the chair while Eliza stands still and watches')
  if n==21:p=p.replace('she speaks through slightly clenched teeth, warning and firm','she lightly clenches her teeth with the source warning, firm expression, without speaking')
  if n==23:
   p=p.replace('亮屏手机(honey)/','Matteo取走手机后留下的桌面空位/').replace('a smartphone glowing with an incoming "honey" call, and the renewal contract lie on the wood','the cleared tabletop place where Matteo removed his phone, and the renewal contract remain on the wood').replace('her hand steadies there as the phone glows','her hand steadies at the same table edge; Matteo still has his phone off-scene').replace('the tea cup, glowing "honey" phone and contract','the tea cup, cleared former phone position and contract').replace('a faint phone vibration, quiet room tone','quiet room tone and a faint hand contact on the table')
 if ep==7 and n==3:
  p=p.replace('环抱→被单下手','环抱→被沿上方可见双手').replace('场景资产中的被面下男主','场景资产中的被沿上方被面上，男主').replace('hands under the asset-matched bedding','visible hands above the duvet edge on the asset-matched bedding')
 if ep==7 and n==6:
  p=p.replace('略仰(女主视角)','右通道近枕外侧的客观略仰机位').replace("slight low angle (Eliza's POV)","slight low angle from the right aisle just outside her pillow; an objective two-shot, not a literal character POV")
 if ep==7 and n==9:
  p=p.replace('台灯、粉色雏菊、粉蜡烛、打火机静物','实际右柜既有台灯、小钟、盆栽静物').replace('a small warm lamp, pink daisies in a little vase, a pink candle, a metal lighter, arranged on the wood','the existing small warm lamp, little clock and potted plant in their exact asset positions on the actual right bedside cabinet').replace('a soft candle/light flicker','a very soft fluctuation of the lamp light')
 if ep==7:
  p=p.replace('white plush toy','designated old teddy bear').replace('plush rabbit','designated old teddy bear').replace('毛绒兔','既定旧熊玩偶')
  p=re.sub(r'(?<![A-Za-z])(?:baby|babe)(?![A-Za-z])','ALLIE',p,flags=re.I)
  p=p.replace('daylight through blinds','daylight through the established curtained window').replace('blind shadows','existing-window light and curtain shadows').replace('百叶窗自然光','既有窗帘窗口自然光')
  if n==13:p=p.replace('wine-red velvet tufted headboard with gold carving', 'established upholstered headboard and fixed bed furniture from the Matteo bedroom asset').replace('wine-red velvet tufted','asset-matched upholstered')
  if n==45:p=p.replace('answers the phone warmly, again and again','listens to the phone, silently nodding and smiling').replace('responding warmly to the phone','listening warmly to the phone').replace('answers her warmly again and again','listens and nods warmly without speaking')
  if n==46:
   p=p.replace('女主背对镜头在左,男主在右','床尾正视机位下女主近侧偏右背对镜头、男主里侧偏左').replace("Eliza's back is left, Matteo on the right", "Eliza's back is on the near right, Matteo on the far left").replace('Eliza back-to-camera on the left, Matteo on the right','Eliza back-to-camera on the near right, Matteo on the far left').replace('her back left, him right','her back near-right, him far-left')
 if ep==9 and n==11:p=p.replace('she looks up at Eliza','she looks toward the seated Eliza')
 if ep==9 and n==23:
  p=p.replace('BLOCKING: cup, phone, contract and her hand.','BLOCKING: the same cup, contract, her hand and the cleared former phone space; no device returns.').replace('LIGHTING: cool-warm light, phone screen glow.','LIGHTING: the established cool window light and warm practical lamps; no screen glow.')
 p=p.replace('ivory outfit','designated clothing')
 if ep in [7,8]:
  p=p.replace('through blinds','through the established curtained window').replace('blind shadows','curtain-filtered window shadows')
 if ep==7 and n==45:p=p.replace('laughing softly as he answers the caller again and again','smiling and softly exhaling while he listens and nods to the caller without speaking')
 if ep==7 and n==46:p=p.replace('Eliza on the left with her back to camera, Matteo on the right','Eliza on the near right with her back to camera, Matteo on the far left')
 if ep==8:
  p=p.replace('distant fire crackle','faint room ambience').replace('the fire flickers','the practical lamp reflections shift softly').replace('fire flickers','practical lamp reflections shift softly')
  if n in [15,16]:
   p=p.replace('a warm floor lamp glows','the existing practical lamps glow').replace('small against the city lights','framed by the established entrance-room furnishings').replace('warm floor lamp key, cool city-night bokeh through the window','warm key from the established practical lamps, with the entrance and fixed furniture softly out of focus').replace('Eliza alone on the sofa, city lights behind her','Eliza alone on the sofa, with the fixed entrance-room background behind her').replace('warm floor lamp from one side, cool window bokeh behind','warm existing practical lamp from one side, with the fixed entrance-room background softly out of focus')
 if ep==9:
  if n==3:p=p.replace('background fire','background practical lamp reflections').replace('fire glows','practical lamps glow')
  if n==9:p=p.replace('fire glow','existing practical lamp glow')
  if n==15:p=p.replace('leans slightly down so she is eye-level with the seated Serafina','makes the source small bow, looking naturally downward toward seated Serafina; she does not fold her torso into an impossible equal-eye-height pose')
  if n==16:
   p=p.replace('carved double wooden doors','existing left archway and its wood framing').replace('carved double doors','existing left archway and wood framing').replace('the doors and marble floor','the existing archway, wood framing and marble floor').replace('across the doors and marble','across the existing wood framing and marble')
  if n==19:
   p=p.replace('the red circles clearly marking the deadline and the document','the same clear 7-day countdown marker and the designated document remaining unchanged').replace('the calendar with the red-circled 7 above the red-circled renewal agreement','the same simple 7-day countdown marker above the unchanged designated renewal agreement')
 if ep in [7,8]:p=re.sub(r'\bblinds\b','existing curtains',p)
 if ep==8 and n==14:
  p=p.replace('side shot of the empty bed','side shot of the occupied bed, with Eliza curled beneath the bedding').replace('空床中景','不露女主脸的被面中景').replace('切空床','切女主仍缩在被下的床面')
 if ep==9 and n==15:
  p=p.replace('女主微微俯身与坐着的夫人平视','女主站着小幅礼貌鞠躬，视线自然向下看坐着的夫人，不强求相同眼高').replace('礼貌开口道谢','保留礼貌感激的神情与鞠躬，不再开口说话')
 if ep==9 and n==16:p=p.replace('女主对夫人说话','女主面对夫人礼貌沉默的关系延续')
 if ep==9 and n==20:p=p.replace('夫人开口','夫人以严厉目光强调界线，保持沉默')
 if ep==9 and n==16:p=p.replace('豪宅雕花双开木门','同场景既有左侧拱门及木框').replace('切空走廊木门','切同场景既有左拱门与木框的空镜')
 if ep==8 and n in [8,51]:p=p.replace('女主说话;切','女主承接上一句收尾后合唇，不重复前句;切')
 if ep==7 and n in [43,44,45]:p=p.replace('讲电话','听电话并无声保持源笑意')
 return p

for r in rows:
 ep,n=r['ep'],r['shot'];p=clean(r['adapted_prompt'],ep,n,r['scene_code'])
 # No common identity paragraph containing absent characters.
 p=re.sub(r'^IDENTITY / APPEARANCE:.*$',"IDENTITY / APPEARANCE: only the visible or locally visible people use their exact designated character assets. Preserve identity, adult age and body size; no source costume, makeup or tattoos are imposed. The male character's clothing remains fastened and chest covered. Source cards provide pose/composition only, never card layouts, labels or subtitles.",p,flags=re.M)
 if (ep,n) in locks:
  l=locks[ep,n];r['asset_names']=l['asset_names'];r['scene_code']=l['scene_code'];r['position_lock']=l['position_lock']
 else:
  # Temporary list from actual source interval only; authoritative per-shot locks will replace it.
  body=NS['neutral'](r['source_prompt'])+' '+NS['neutral'](r['blocking']+' '+r['action'])
  r['asset_names']=NS['assets'](ep,n,r['scene_code'],body)
  if ep==7:r['asset_names']=[x for x in r['asset_names'] if not x.startswith('Serafina')]
 if ep==7 and n==3 and r['position_lock']:r['position_lock']=r['position_lock'].replace('同一被沿下的两手交叠','同一被沿上方可见被面上的两手交叠')
 if ep==7 and n==6 and r['position_lock']:r['position_lock']=r['position_lock'].replace('摄影机沿右道高斜或床尾半区上空取侧脸，不能从左墙后拍所谓女主视点。','摄影机位于床右通道近枕外侧，镜头高度略低于两张脸，保留源略仰的客观双人近景；不是女主真POV，不改成高斜俯拍，不穿左墙。')
 if ep==7 and n==9 and r['position_lock']:r['position_lock']=r['position_lock'].replace('台灯、花瓶及小物相对次序取场景图','台灯、小钟、盆栽相对次序取场景图')
 if ep==7 and n==47 and '手机' not in r['asset_names']:r['asset_names'].append('手机')
 # Exclusion/off-screen mentions must not accidentally invoke native asset aliases.
 alias_exclusions={(7,49):{'手机':'phone'},(8,12):{'续约合同':'renewal contract'},(8,25):{'庄园走廊':'estate corridor'},(8,26):{'庄园大门':'estate gate'},(8,44):{'续约合同':'renewal contract'},(9,7):{'手机':'phone'},(9,23):{'手机':'phone'}}
 for old,new in alias_exclusions.get((ep,n),{}).items():
  p=p.replace(old,new)
  if r['position_lock']:r['position_lock']=r['position_lock'].replace(old,new)
 if ep==8 and (9<=n<=14 or 45<=n<=46) and r['position_lock']:
  r['position_lock']=r['position_lock'].replace('以站在床尾面向床头为准：Matteo固定床左靠墙里侧，Eliza固定床右通道近侧，头均朝原床头、脚向床尾，原枕不换；','起段若人物仍卧/坐床上，以站在床尾面向床头为准：Matteo占床左靠墙里侧，Eliza占床右近侧；离床后按本镜明确的收腿、落地、行走、站书桌或门边路线，不再强制卧姿与枕位；')
 # All unlisted native aliases in exclusions must be English, avoiding native one-click binding by substring.
 known=json.loads((ROOT/'资产图_飞书_正式/上传批次/上传清单.json').read_text(encoding='utf-8'))
 for alias in [a['asset_name'] for b in known['batches'] for a in b['assets']]:
  if alias in r['asset_names']:continue
  replacement={'庄园会客厅':'the alternate brown-sofa reception-room reference','手机':'phone','续约合同':'renewal contract','庄园走廊':'estate corridor','庄园大门':'estate gate','车内':'car interior'}.get(alias)
  if replacement:
   p=p.replace(alias,replacement)
   if r['position_lock']:r['position_lock']=r['position_lock'].replace(alias,replacement)
 if ep==9 and n==16 and r['position_lock']:r['position_lock']=r['position_lock'].replace('面对左红椅母亲继续说话','面对左红椅母亲延续上一镜礼貌沉默的状态')
 r['adapted_prompt']=p
 r['final_prompt']='参考资产：'+'；'.join('@'+x for x in r['asset_names'])+'\n'+('POSITION LOCK: '+r['position_lock']+'\n' if r['position_lock'] else '')+p
 r['changes'].extend(['场景、被品、床头、玩偶、功能来电名按既定项目资产/女版原文清理矛盾描述','每镜独立POSITION LOCK；只引用源区间实际出镜或局部角色，电话女声不绑成画内人物'])

for ep in [7,8,9]:
 sub=[r for r in rows if r['ep']==ep];d={'status':'LOCAL_REVIEW_CANDIDATE','ep':ep,'source_shot_count':len(sub),'duration_seconds':sub[-1]['end_seconds'],'shots':sub}
 (OUT/f'EP{ep:02d}_平台稿.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
 if ep==7:
  path=OUT/'EP07_S01-10_可填写冻结版.json'
  if not path.exists():
   first={'status':'READY_FOR_NATIVE_BINDING','ep':7,'source_shot_count':10,'duration_seconds':20.52,'freeze_note':'首批10镜冻结后仅在向Root明确报diff后更新。','shots':sub[:10]}
   assert all(x['position_lock'] for x in first['shots']);path.write_text(json.dumps(first,ensure_ascii=False,indent=2),encoding='utf-8');print('FROZEN',path,hashlib.sha256(path.read_bytes()).hexdigest())
(OUT/'平台稿_129镜.json').write_text(json.dumps({'status':'LOCAL_REVIEW_CANDIDATE','source_shot_count':129,'authority_docx':str(ROOT/'完整剧本/我不再做教父的大码人形抱枕EN.docx'),'narration_policy':'删除全部旁白；仅本项目原文人物对白与允许的自然声','shots':rows},ensure_ascii=False,indent=2),encoding='utf-8')
print('Finalized content',len(rows),'locked',sum(bool(x['position_lock']) for x in rows))
