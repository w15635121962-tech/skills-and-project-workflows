import json,re,pathlib
root=pathlib.Path('/Volumes/YSAigc/剧作项目/我不再做教父的大码人形抱枕/去除衣服妆造描述_20261019')
data=json.loads((root/'EP02_编辑输入.json').read_text())
res=[]
for ep in data:
 female=ep['version']=='女版'
 a='Eliza' if female else 'Oliver'
 b='Matteo Bellandi' if female else 'Vittoria Blackwood'
 acl='米白宽松短袖睡裙' if female else '藏蓝白滚边长袖长裤睡衣'
 bcl='白滚边黑色丝质两件睡衣' if female else '黑色蕾丝边系带丝质睡袍'
 bed='粉米白' if female else '蓝灰'
 for g in ep['groups']:
  patches=[]
  def edit(i,j,new,reason='删除衣服妆造及外观描述，保留动作、空间与摄影'):
   old=g['paragraphs'][i][j]['text']
   if old!=new:patches.append({'paragraph_index':i,'segment_index':j,'old':old,'new':new,'reason':reason})
  def swap(i,j,oldpart,newpart,reason='删除衣服妆造及外观描述，保留动作、空间与摄影'):
   s=g['paragraphs'][i][j]['text']
   assert oldpart in s,(g['card_name'],i,j,oldpart,s)
   edit(i,j,s.replace(oldpart,newpart),reason)
  for j,s in enumerate(g['paragraphs'][0]):
   if s['kind']=='text':
    new=s['text']
    for des in ['；大码体态、身份长相及日常服装统一锁定资产','；米白宽松短袖睡裙，大码体态不改瘦','；白滚边黑色丝质两件睡衣','；藏蓝白滚边长袖长裤睡衣，大码体态不改瘦','；黑色蕾丝边系带丝质睡袍']:
     new=new.replace(des,'')
    edit(0,j,new,'删除出场角色后的衣服、体态及外观文字；保留角色及资产标识')
  n=g['group']
  if n==1:
   hair='棕色微卷长发沿枕面自然散开' if female else '棕色短卷发沿枕面自然散开'
   swap(13,0,'，'+hair,'')
   cloth='米白针织开衫与浅色碎花连衣裙领口' if female else '白色衬衫衣领'
   swap(22,0,'呼吸让'+cloth+'轻微起伏','呼吸轻微起伏')
   swap(23,0,'，'+cloth+'在画面下缘','')
   swap(43,0,'白枕和'+cloth+'保持前镜状态','白枕保持前镜状态')
  elif n==2:
   swap(32,0,'换好衣服准备走出','准备走出')
   swap(51,0,'穿'+bcl,'')
  elif n==3:
   swap(11,0,'赤脚从','从')
   swap(12,0,'赤足脚步','脚步')
   lowcloth='黑色丝质睡裤裤脚与' if female else '黑色长睡袍下摆与'
   s=g['paragraphs'][13][0]['text'].replace(lowcloth,'').replace('赤足接触','脚部接触')
   edit(13,0,s)
   s=g['paragraphs'][31][0]['text'].replace('，包含资产睡衣前襟与侧腰衣料','').replace('；衣领开合与身体覆盖保持真实资产','')
   edit(31,0,s)
   edit(32,0,f'人物表演：【{b}】肩胸放松，随呼吸抬落。')
   edit(33,0,f'画面内容：对角线俯拍胸腹，背景是{bed}床铺枕面；取景范围延续源胸腹局部。')
   s=g['paragraphs'][41][0]['text'].replace('和衣领状态','').replace('胸腹衣料','胸腹')
   edit(41,0,s)
   swap(43,0,'胸腹衣料局部','胸腹局部')
   swap(52,0,'开衣、','')
   edit(53,0,'画面内容：原表镜13的胸腹构图渐暗，用0.1秒衔接原表镜16的全景渐显。')
  elif n==4:
   s=g['paragraphs'][11][0]['text'].replace('穿'+acl+'与拖鞋','').replace('穿'+bcl,'')
   edit(11,0,s)
   swap(13,0,'床铺和两人衣服连续','床铺连续')
   edit(43,0,'画面内容：对角线手臂与腰背为主体；避开脸，用接触细节承接原表镜18的拥抱。')
  elif n==5:
   swap(11,0,'黑色睡衣衣襟','衣襟','删除衣襟颜色款式，保留抓握动作必要位置')
   swap(33,0,'黑色袖口和'+acl+'肩背','手臂和肩背')
   swap(43,0,'保持衣领和被边高度','保持被边高度')
  elif n==6:
   swap(51,0,'发丝与领口之间','发丝与颈部之间')
   swap(53,0,'发丝与衣领','发丝与肩部')
  elif n==7:
   swap(11,0,'领口和颈部','颈部')
   loc='米白短袖睡裙的圆形蕾丝边领口' if female else '藏蓝睡衣的白滚边翻领'
   swap(13,0,'，'+loc+'标明接触位置','')
   swap(41,0,'、耳垂与领口','与耳垂')
   swap(43,0,'耳垂至'+loc+'之间','耳垂至颈侧之间')
  elif n==8:
   oldappearance='Matteo资产中的下巴与浅胡茬依身份资产；领口可见部分连续' if female else 'Vittoria资产中的光洁下巴与颈部依身份资产；领口可见部分连续'
   swap(13,0,'，'+oldappearance,'')
  elif n==9:
   swap(13,0,acl+'肩部','肩部')
   swap(21,0,'、脖颈与衣领局部','与脖颈局部')
   loc='米白短袖睡裙的圆形蕾丝边领口' if female else '藏蓝睡衣的白滚边翻领'
   edit(23,0,'画面内容：固定中心微距取颈侧，保留随呼吸起伏的细节。')
   swap(43,0,'衣服和接触点','接触点')
   swap(53,0,'睡衣领口与已有纹身依各自资产，','')
  elif n==10:
   edit(23,0,'画面内容：微俯肩头特写，看清手与肩部受压的细节。')
   swap(31,0,'与领口上胸局部','与上胸局部')
   edit(33,0,'画面内容：对角线大特写集中嘴唇和下巴。')
   oldtail='，衣服与体型依大码/教父或教母资产；不为台词中的体型词改瘦人物'
   swap(43,0,oldtail,'')
  elif n==11:
   swap(13,0,'人物面部与衣领','人物面部')
   swap(33,0,'面部和领口','面部')
   swap(53,0,'衣服、光线和背景','光线和背景')
  elif n==12:
   swap(13,0,'及领口位置','')
  res.append({'card_name':g['card_name'],'patches':sorted(patches,key=lambda x:(x['paragraph_index'],x['segment_index']))})
assert len(res)==24
# All modifications address text, preserve complete quoted dialogue and all asset runs.
for ep in data:
 for g in ep['groups']:
  result=next(x for x in res if x['card_name']==g['card_name'])
  seen=set()
  for p in result['patches']:
   k=(p['paragraph_index'],p['segment_index']);assert k not in seen;seen.add(k)
   old=g['paragraphs'][k[0]][k[1]]
   assert old['kind']=='text' and old['text']==p['old']
   assert re.findall(r'"[^"\n]*"',p['old'])==re.findall(r'"[^"\n]*"',p['new']),(g['card_name'],p)
(root/'EP02_删改方案.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
print('groups',len(res),'patches',sum(len(x['patches'])for x in res))
for r in res:print(r['card_name'],len(r['patches']))
