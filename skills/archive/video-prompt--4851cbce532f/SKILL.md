---
name: video-prompt
version: 3.0.0
description: |
  电影级视频提示词生成器 — 从分镜/Shot描述一键生成可直接投喂AIGC视频平台的提示词。
  
  核心能力：
  · 多镜头序列生成（景别递进弧线 + 运镜意图映射 + 特写情绪放大）
  · 情绪放大协议（抽象词→物理描述，SCOTT法则，HITCHCOCK碎片化）
  · 开场状态头部模板（环境·站位·角色·灯光四维锚定）
  · 技术规格锁定层（ARRI Alexa / 浅景深 / 发丝光 / SSS皮肤 / HDR）
  · 写实强制协议（眼泪物理 / 湿衣布料 / 水花物理 / 场景真实感）
  · Locked Core一致性系统（角色·环境·色调·技术规格跨镜头锁定）
  · 运镜叙事动机链（15类意图×7阶段×能量级别，来自camera-movement）
  · 焦段递进网格（16mm→微距9级张力曲线，来自focal-grid）
  · 画幅适配（9:16竖屏垂直运镜优先 / 16:9横屏水平运镜优先）
  
  支持平台：即梦/Seedance / Kling / Veo / Sora / Runway / Pika
  支持画幅：16:9 横屏 / 9:16 竖屏
  
  触发词：视频提示词 · video prompt · 生成视频 · 视频词 · 提示词优化 ·
  给我提示词 · 写提示词 · AI视频 · AIGC视频 · 文生视频 · Shot提示词 ·
  即梦提示词 · Kling提示词 · Veo提示词 · 分镜转提示词 · 镜头提示词 ·
  帮我写视频 · 视频生成词 · 电影感提示词
  
  不触发：分镜表生成（→storyboard-table）· 剧本诊断（→movie-story）
  · 运镜方案设计（→camera-movement）· 角色资产卡（→character-asset）
  · 表演画面描述（→performance-description）· 场景资产卡（→scene-asset）
  · 3×3焦段网格批量（→focal-grid）· 战斗多镜头序列（→multishot-cinematic）

agent_created: true
---

# Video Prompt Generator v3 — 电影级视频提示词生成器

> **Version 3.0.0** · 2026-06-18
> 从 movie-story / 9-16-movie-story / multishot-cinematic / storyboard-table /
> camera-movement / performance-description / focal-grid 七大技能提纯，
> 聚焦"分镜描述 → 可投喂视频平台的提示词"单一核心任务。

---

## 零、定位与边界

| 技能 | 职责 | 本技能 ❌ 不做 |
|------|------|---------------|
| `storyboard-table` | 分镜表格输出 | 分镜表 |
| `movie-story` | 剧本诊断+覆盖拍摄规划 | 剧本分析 |
| `camera-movement` | 运镜决策+映射+自检 | 独立运镜方案 |
| `performance-description` | 画面描述+表演设计+主题总结 | 独立表演描写 |
| `character-asset` | 角色外貌/服装/配饰卡 | 角色资产 |
| `scene-asset` | 场景空间/灯光/调色卡 | 场景资产 |
| `focal-grid` | 3×3焦段网格9格批量生成 | 9格批量 |
| `multishot-cinematic` | 战斗/动作多镜头序列 | 战斗专用序列 |
| **`video-prompt`** | **以上全部 → 融合为每条可投喂的视频提示词** | ✅ 只做这个 |

**用本技能当：** 已有分镜/Shot描述/剧情文本，需要生成可直接粘贴到即梦/Kling/Veo等平台的视频提示词。

---

## 一、三大铁律（不可绕过）

| # | 铁律 | 一句话 | 违规后果 |
|---|------|--------|---------|
| 1 | **景别变化** | 每组≥3级景别递进（全/中/特），同景别不连用>2次 | 平庸无节奏 |
| 2 | **特写必出** | 每组至少1个CU或ECU，情绪通过面部/细节传递 | 缺乏冲击力 |
| 3 | **情绪放大** | 抽象情绪词→物理/光线/身体描述，禁止"悲伤地看着" | AI无法理解 |

---

## 二、Locked Core 一致性系统

同场景所有镜头共享一个不可漂移的核心：

```
═══════════════════════════════════
Locked Core: [场景名]
═══════════════════════════════════

角色固定层:
  [角色A]：[年龄·体型·发型颜色款式·服装款式颜色·标志性视觉锚点]
  [角色B]：[同上]

环境基调: [场景·时间·光线基调·色温K值·氛围关键词]
色调锁定: [主色·辅色·对比色·饱和度倾向·阴影占比%]
技术规格: [摄影机·镜头·光圈·画幅·风格锁定词]（见第五章）
风格DNA:   [1-2句风格定性，如"冷硬写实压迫感"/"温暖怀旧金色暖调"/"高张力手持纪实"]
```

**一旦确定，以下元素在所有镜头中必须逐字一致：**
- ✅ 角色外貌描述（发型颜色、服装款式和颜色、体型特征）
- ✅ 环境基础设定（什么场景、什么时间、基本光源方向）
- ✅ 摄影机和镜头型号
- ✅ 风格锁定词（photorealistic等）
- ❌ 不锁定的：具体动作、表情、运镜方式、构图角度（这些每镜不同）

---

## 三、开场状态头部模板（首镜必用）

每组视频的第一个镜头必须包含完整的开场状态头部：

```
【开场状态】
环境：[场景全貌] · [时间] · [光线基调] · [色温K值] · [氛围关键词]
      · [空气中可见微粒/声音暗示]
站位关系：[主要角色位置关系] · [距离] · [朝向] · [谁高于/低于谁]
角色状态：[每个角色的身体姿态/服装细节/情绪基线/汗水/伤痕状态]
道具/关键元素：[首帧可见的关键物品及其状态]
灯光方案：[主光源方向+色温] · [辅光方向+色温] · [阴影占比%]
      · [轮廓光/发丝光来源] · [隐藏了什么(SPIELBERG)]
```

**实战案例（宫廷对峙）：**

```
【开场状态】
环境：皇家寝殿长廊（楼上），中午，冷白自然光束与昏暗暖黄光交织，
      空气中清晰可见浮动的微尘，冰冷灰调与贵族暗金色的冷暖碰撞，
      低饱和度，空旷长廊内的微回声。
站位关系：King George 蹲在 Agnes Hartwell 的面前，
         Agnes Hartwell 跌跪于中央地板上。
角色状态：Agnes 位于长廊中央地板上，低头垂眼，面朝长廊一侧，
         后背有流血的鞭伤痕迹，满身狼狈；
         King George 在 Agnes 面前蹲着，身体自然放松，面朝跪在地上的 Agnes。
灯光方案：主光为右上方长廊高窗透入的冷白自然光束，硬光覆盖长廊局部；
         无副光；实用光为墙壁两侧的青铜雕花壁灯，开启发出昏暗的暖黄光。
         隐藏了什么：长廊尽头的暗区——那里可能藏着第三个人。
```

---

## 四、景别体系

### 4.1 景别代码表

| 代码 | 景别 | 人物范围 | 叙事功能 | 时长地板 | 情绪功能 |
|------|------|---------|---------|---------|---------|
| ELS | 极远景 | 主体<15% | 定场/建立/孤独感 | 2.5s | 环境吞噬人物 |
| WS | 全景 | 全身+环境 | 空间关系/权力格局 | 2.0s | 关系定位 |
| MS | 中景 | 腰部以上 | 对话/动作/关系互动 | 3.5s | 关系动态 |
| MCU | 中近景 | 胸部以上 | 亲密/情感转折/对峙前奏 | 3.0s | 进入私人空间 |
| CU | 特写 | 面部 | 情绪峰值/隐藏/揭示 | 2.0s | 情绪直击 |
| ECU | 大特写 | 眼睛/嘴/手/细节 | 微表情/触觉/象征碎片 | 1.0s | 极致碎片 |
| INSERT | 插入镜头 | 物品/局部 | 信息传递/象征/伏笔 | 1.5s | 物即叙事 |
| FRAGMENT | 碎片镜头 | 一个感觉碎片 | 观众脑补拼合（HITCHCOCK） | 0.5s | 不完整更有力 |
| LINGER | 凝视驻留 | varies | 渴望/注视/研究/不舍 | 4.0s | 镜头驻留意图 |
| 金句定格 | 金句+字幕 | varies | 推文特有：静态定格+字幕叠加 | 3.0s | 文字即视觉 |

### 4.2 景别→叙事功能速查

| 你想表达 | 用什么景别 | 为什么 |
|---------|----------|-------|
| 两人的权力关系 | WS | 身体在空间中的位置=权力 |
| 对话/交锋 | MS | 能看到手势+面部反应 |
| 情感转折瞬间 | MCU | 胸部以上=进入私人领域 |
| 情绪爆发点 | CU/ECU | 面部/眼睛=情绪全部暴露 |
| 重要物品/象征 | INSERT | 物品本身承载叙事重量 |
| 孤立/渺小 | ELS | 环境压倒人物 |
| 不完整的碎片化冲击 | FRAGMENT | HITCHCOCK法则：碎片>全景 |

### 4.3 景别递进强制规则

一组多镜头必须遵循弧线，**不得在同一景别停留超过2个连续镜头**：

```
情感递进:  WS(建立) → MS(关系) → MCU(亲密) → CU(情绪) → ECU(极致) → INSERT/MS(余韵)
动作递进:  ELS(环境) → WS(全貌) → MS(动作) → CU(冲击) → ECU(触觉)
打斗递进:  WS(对峙) → MS(交手) → CU/ECU(撞击碎片) → WS(结果)
暧昧递进:  MS(距离) → MCU(靠近) → CU(凝视) → LINGER(失控) → 空镜(余韵)
推文特有:  MS(旁白建立) → MCU(情感切入) → CU(金句定格) → ECU(碎片) → 空镜(留白)
```

---

## 五、运镜体系（来自 camera-movement + focal-grid）

### 5.1 运镜词汇全表

| 运镜 | 中文名 | 叙事功能 | 禁止紧接 | 推荐后续 | 9:16竖屏适配 |
|------|--------|---------|---------|---------|-------------|
| Static | 静态固定 | 重量/权威/蓄势/归零 | 无动机快切 | 另一Static · Slow Push | ✅ 原样 |
| Slow Push In | 缓推 | 压迫/聚焦/揭示/亲密 | 紧接缓拉 | Hold · Linger | ✅ 优先纵向推 |
| Pull Back | 缓拉 | 孤立/失落/释放 | 紧接缓推 | Static · 空镜 | ✅ 优先纵向拉 |
| Handheld | 手持跟拍 | 紧迫/真实/临场/崩溃 | 紧接锁定静态 | 另一Handheld · 微漂移 | ✅ 有限空间内 |
| Crash Zoom | 急推/冲击 | 震惊/冲击/暴击 | 无≥0.5s恢复的一切 | Static ≥1.5s · ECU Freeze | ✅ 优先纵向急推 |
| Tilt Up | 上摇 | 权力/仰望/揭示 | 紧接下摇 | 高位保持 · Crane Up | ✅✅ 竖屏最佳 |
| Tilt Down | 下摇 | 羞耻/压迫/服从 | 紧接上摇 | 低位保持 · Settle | ✅✅ 竖屏最佳 |
| Crane Up | 升/摇臂上 | 升华/超越/全局 | 无特殊 | Static Hold | ✅✅ 竖屏最佳 |
| Crane Down | 降/摇臂下 | 沉入/揭示/细节 | 无特殊 | Static Hold | ✅✅ 竖屏最佳 |
| Dolly/Track | 横移 | 观察/平行力量 | 无动机反向 | 自然停顿切 · 静止 | ⚠️ 横向空间有限 |
| Micro-drift | 微漂移 | 恐惧/不安/亲密 | 加速 | 减速至静止 · Linger | ✅ |
| Whip Pan | 甩镜/急摇 | 紧迫/惊吓/转场 | 无特殊 | Settle · Static | ❌ 竖屏宽度不足 |
| Rack Focus | 焦点切换 | 信息揭示/注意力引导 | 无特殊 | Static · Slow Push | ✅ 原样 |
| Walk-and-Talk | 行走对话 | 伴随/见证/流畅 | 硬切中间句 | 自然停顿 · Settle | ⚠️ 前后纵向为主 |
| Linger Hold | 凝视保持 | 渴望/不舍/沉溺 | 快切 | Static · Slow Pull | ✅ |
| Empty Frame | 空镜保持 | 余韵/缺席/留白 | 快切 | Static · Slow Push In | ✅ |

### 5.2 叙事意图→运镜种子（来自 camera-movement）

| 叙事意图 | 含义 | 运镜种子 |
|---------|------|---------|
| RevealInformation | 揭示信息/秘密 | Slow Push In |
| HideInformation | 隐藏真相 | Static / Slow Lateral |
| BuildSuspense | 制造悬念 | Slow Push In |
| BuildEmotion | 强化情绪 | Motivated Push |
| ShiftPower | 权力变化 | Push In to Dominant |
| EstablishRelationship | 建立关系 | Static / Slow Track |
| CreateIsolation | 强调孤独 | Pull Out |
| CreateIntimacy | 强调亲密 | Static / Slow Push |
| CreateThreat | 制造威胁 | Slow Creep / Handheld |
| CreateRelief | 缓解压力 | Pull Out |
| Foreshadowing | 埋伏笔 | Static / Rack Focus |
| MisleadAudience | 误导 | Static (Blocked Composition) |
| BreakTrust | 信任破裂 | Axis Shift |
| MoralChoice | 道德选择 | Locked / Micro Push |
| ConfirmSuspicion | 确认怀疑 | Rack Focus to Evidence |

### 5.3 故事阶段→运镜基调

| 阶段 | 含义 | 运镜基调 | 剪辑速度 |
|------|------|---------|---------|
| Setup | 建立场景/关系 | Slow or Static | Slow |
| Development | 推进/互动 | Motivated Tracking | Moderate |
| Conflict | 冲突升级 | Push In / Handheld | Faster |
| Crisis | 被迫选择 | Locked / Slow Push | Delayed |
| Climax | 最高点 | Fast Push / Crash Zoom | Fastest |
| Resolution | 结果显现 | Pull Out | Slower |
| Aftermath | 余波/沉默 | Static | Long Hold |

### 5.4 能量级别→运镜强度

| 能量 | 值 | 运镜强度 | 推荐运镜 |
|------|---|---------|---------|
| 低 | 0.0-0.3 | 极低 | Static |
| 中 | 0.3-0.6 | 中 | Slow Push |
| 高 | 0.6-0.8 | 高 | Push / Handheld |
| 极高 | 0.8-1.0 | 极高 | Handheld / Fast Push / Crash Zoom |
| 骤降 | Peak→Drop | 归零 | Pull Out / Locked |

### 5.5 焦段递进网格（来自 focal-grid）

| 焦段位置 | 镜头mm | 景别 | 运镜逻辑 | 情绪张力 |
|---------|--------|------|---------|---------|
| [1,1] | 16-20mm | ELS/WS 极广角 | Subtle Push 搜索感 | 最低——建立 |
| [1,2] | 24-35mm | WS/MS 广角 | Slow Push 环绕 | 低——定位 |
| [1,3] | 35-50mm | MS 中广角 | Slow Push / Micro-drift | 低-中——对峙 |
| [2,1] | 50-85mm | MS/MCU 中景 | Motivated Push 身体张力 | 中——关系 |
| [2,2] | 85mm | MCU/CU 中近景 | Crash Zoom 锁定眼神 | 中-高——准备冲击 |
| [2,3] | 100-135mm | CU 近景 | Crash Zoom + Motion Blur | 高——攻击性 |
| [3,1] | 135mm+ | ECU 特写 | Micro-drift 微表情+汗珠 | 高-极高——碎片 |
| [3,2] | 微距 | 极特写纹理 | Micro-drift / Near-Static | 极高——触觉级 |
| [3,3] | 极端畸变 | 抽象碎片 | Motion Blur + Lens Distortion | 极高——破碎 |

### 5.6 禁止组合与桥接规则

| 禁止组合 | 原因 | 桥接方案 |
|---------|------|---------|
| 缓推 → 紧接缓拉 | 方向矛盾，观众割裂 | 插入 Static ≥2.0s 或 INSERT |
| 急推 → 急推 | 连续冲击无呼吸空间 | 急推后 ≥0.5s 恢复 Static |
| 手持 → 紧接锁定静态 | 观众眩晕断裂 | 先减速至微漂移，再至静止 |
| 上摇 → 下摇 | 方向矛盾 | 插入高位保持镜头 |
| 无动机运动 | 运镜无叙事目的 | 删除运动或补动机 |

**金句/落点句 → 运镜归零（纯静态），不管之前多剧烈。**

---

## 六、情绪放大协议

### 6.1 四条导演法则（来自 storyboard-table + performance-description）

| # | 法则 | 一句话 | 提示词应用 |
|---|------|--------|-----------|
| 1 | **HITCHCOCK** | 峰值时刻：展示碎片，而非全貌。不完整的画面更有力量。 | 情感爆发→ECU/FRAGMENT碎片，不用全景直述 |
| 2 | **SCOTT** | 具体到可以画出来、可以做出来。模糊=不合格。 | 提示词必须可"看到"，闭上眼能想象画面=合格 |
| 3 | **SPIELBERG** | 每个画面说明它隐藏了什么，以及为什么隐藏服务于故事。 | 提示词中的阴影区/遮挡有叙事意义 |
| 4 | **身体即情绪** | 禁止抽象情绪词。每个情绪词必须替换为身体动作/光线/物理。 | 见6.2替换表 |

### 6.2 禁止/替换词表

| ❌ 禁止（抽象情绪词） | ✅ 替换为（物理/视觉/身体规格） |
|---------------------|------------------------|
| 悲伤地看着 | 眼眶微红，下唇轻颤，手指无意识攥紧衣角 |
| 愤怒地转身 | 下颌咬紧，肩膀猛然绷直，转身时拳头未松 |
| 开心地笑着 | 嘴角上扬露出虎牙，双眼细成月牙，鼻翼轻微扇动 |
| 害怕地颤抖 | 双手细微颤动，胸腔起伏加速，瞳孔略微放大，视线锁住目标 |
| 紧张地等待 | 指尖在腿侧轻敲，下唇轻咬，不停扫视入口方向 |
| 情绪复杂 | **必须具体化**：眉头微蹙+嘴角下压+眼神短暂失焦 |
| 深情地注视 | 眼神专注落在对方眼睛，眨眼频率降低，嘴唇微微分开 |
| 崩溃了 | 眼睑迟滞一拍，一只手的指节开始泛白，肩膀猛然塌下 |
| 她很痛苦 | 脖颈后仰、喉结剧烈滚动，手指弯曲紧扣胸口 |
| 他很压抑 | 面部肌肉收紧但不动，嘴唇抿成一条线，呼吸刻意放缓 |
| 气氛紧张 | [光线]侧光硬光雕刻面部轮廓+背景阴影占比60%+呼吸声放大 |

### 6.3 情绪镜头五要素（CU以上景别必须包含）

1. **视向**：眼睛看向哪里？锁住/回避/失焦/下移？
2. **呼吸**：节奏快/慢/屏住/恢复/骤停0.5秒后长出？
3. **微表情**：至少一个具体面部肌肉动作（眼睑颤动/嘴角微抿/下颌咬紧/鼻翼扇动）
4. **手/身体**：与情绪对应的肢体反应（攥紧/松开/前倾/后退/肩膀端起/下沉）
5. **光线**：光线如何强化情绪

| 情绪 | 光线强化方案 |
|------|------------|
| 压迫/恐惧 | 侧光硬光雕刻面部轮廓，阴影放大负空间 |
| 亲密/温柔 | 柔光漫射，暖色低光，面部双面柔光 |
| 权威/威胁 | 低位逆光剪影，或高位冷白顶光压迫 |
| 悲伤/崩溃 | 侧光只照亮半脸，另一半沉入阴影 |
| 暗藏秘密 | Split lighting（一半明一半暗），眼睑处有阴影遮挡 |
| 真诚/敞开 | 正面柔光，面部均匀照亮，无遮挡 |

### 6.4 潜台词→表演→提示词映射（来自 performance-description）

| 潜台词 | 身体动作选择 | 提示词写法要点 |
|-------|-----------|-------------|
| suspicion | 视线在对方与地面来回，眉间微皱，嘴唇抿紧不表态 | 视向来回+面部微表情+嘴唇动作 |
| attraction | 眼线短暂接触后移开（0.3-0.5秒），嘴角微上扬后克制收回 | 视向短暂+嘴角变化+克制收回 |
| rejection | 身体微后移，视线快速转向他处，嘴唇闭合成线 | 身体后移+视向转开+嘴唇闭合 |
| guilt | 眼睫低垂，避免直视，手指无意识触碰自己（耳/颈/袖口） | 视向回避+手部自触碰 |
| superiority | 身体舒展占空间，下颌微抬，眼神稳定且居高临下 | 身体舒展+下颌抬高+视线稳定 |
| hidden_love | 眼线接触1秒后移开，嘴角先动后收回，手指轻颤 | 视向1秒+嘴角变化+手颤 |
| hidden_threat | 嘴角微弧但不笑，眼神冰冷稳定，身体前倾一点 | 嘴角假弧+视线冰冷+前倾 |
| surrender | 身体内缩，重心下沉，视线从上转下，肩膀放下 | 身体内缩+视向下移+肩下沉 |
| grief | 身体佝偻，呼吸长出气，眼眶红但强控不流泪 | 身体佝偻+呼吸模式+眼眶状态 |

### 6.5 推文/文学隐喻→视觉转译

| 隐喻原文 | 类型 | 画面描述 | 提示词写法 |
|---------|------|---------|-----------|
| "胸口像灌了水泥" | 压迫 | ECU：手紧握胸口区域 | 指节发白，呼吸短促变浅 |
| "嗓子眼里卡了鱼刺" | 哽咽 | MCU：喉部特写 | 喉结滚动，嘴角微微下撇 |
| "脑子里嗡嗡的" | 麻木 | CU：面部居中偏上 | 眼神失焦，瞳孔微缩 |
| "心脏像被攥了一把" | 心痛 | ECU：手按住左胸 | 手指微微颤抖，呼吸浅促 |
| "整个人像被抽空了" | 虚脱 | WS：角色居画面下方1/3 | 身体佝偻，四肢松弛 |
| "血往头上涌" | 愤怒/羞耻 | MCU→ECU：面部渐进 | 面部潮红从颈部蔓延 |
| "后背发凉" | 恐惧 | CU：肩膀区域 | 肩膀微缩，眼神警惕 |

---

## 七、技术规格锁定层

### 7.1 标准英文技术规格词（每条提示词必须包含）

```
shot on Arri Alexa 65 / Arri Alexa Mini LF（竖屏用Mini LF）,
[焦段]mm prime lens, T2.8,
shallow depth of field, extreme cinematic shallow focus,
foreground bokeh, subject razor-sharp,
hair light precisely defining individual hair strands and silhouette,
detailed realistic skin texture, visible skin pores and fine lines,
subsurface scattering (SSS), natural subtle skin redness,
no plastic skin, no waxy skin, no overly smooth skin, natural imperfections,
photorealistic, hyperrealistic, ultra photorealistic,
realistic live-action cinematic film still,
no cartoon, no anime, no manga, no illustration,
no stylized rendering, no comic style,
8K ultra HD, HDR high dynamic range, high contrast,
true-to-life color reproduction, maximum detail clarity,
cinematic color grading,
no subtitles, no watermarks, no music,
preserve voice and sound effects only
```

### 7.2 中文技术规格块（用于即梦/Kling等中文平台）

```
8K 超高清，好莱坞电影质感，写实风格，真人实景拍摄，阿莱 Alexa 65 摄影机拍摄，[焦段]mm 定焦电影镜头，极致相机浅景深，前景焦外虚化，主体锐度拉满，发丝光精准勾勒发丝轮廓；HDR 高动态范围，高对比度，色彩还原真实，画面细节拉满，电影级色彩分级。无字幕无水印，不要音乐，仅保留人声和音效。
```

**注意：焦段根据景别选择（见5.5焦段递进表）。**

### 7.3 画幅关键词

| 画幅 | 必加词 | 适用平台 |
|------|--------|---------|
| 16:9 横屏 | `16:9 widescreen, cinematic 2.39:1 aspect ratio` | Veo / Sora / Runway |
| 9:16 竖屏 | `vertical 9:16 composition, subject centered in frame, eyes at upper third` | Kling / 即梦 |

---

## 八、特殊场景写实协议

### 8.1 眼泪物理协议（哭泣/崩溃镜头必用）

中文版：
```
真实人类眼泪从内眼角缓慢溢出，半透明生理盐水质感，表面有细腻的环境光反射，顺着脸颊自然滑落，受重力影响呈不规则曲线，在颧骨处汇聚后滴落，打湿皮肤形成湿润反光，晕开少量睫毛膏，留下淡淡的泪痕，睫毛上挂着细小的泪珠。面部肌肉自然紧绷，嘴唇微微颤抖，整体情绪克制。
```

英文版：
```
realistic human tears slowly welling from inner corners of eyes, semi-translucent saline texture with delicate environmental light reflections on surface, trickling naturally down cheeks in irregular gravity-driven paths, pooling at cheekbones before dripping, leaving wet reflective skin and faintly smeared mascara traces, tiny teardrops clinging to eyelashes, natural facial muscle tension, slightly trembling lips, restrained emotion
```

### 8.2 湿衣写实协议（落水/雨戏必用）

正向：
```
realistic soaked fabric with semi-translucent wet areas clinging to skin, visible coarse fiber texture and rough textile surface details even when wet, natural water absorption making fabric darker and heavier with natural sagging folds, water droplets and streams running along wrinkles with broken specular highlights, damp matte areas mixed with subtle water sheen, intricate textile wrinkles and fabric physics, no uniform plastic shine or glossy rubber look, no latex texture, photorealistic wet fabric
```

负向：
```
plastic texture, rubber, latex, glossy uniform shine, smooth surface, artificial wet look, shiny film, waxy wet cloth, CGI wet fabric, overly reflective wet clothing, transparent plastic wrap effect
```

### 8.3 布料质感协议（有服装必用）

```
physically accurate fabric simulation, realistic cloth dynamics and inertia, natural tension and compression in folds and drapes, pronounced natural texture irregularities and roughness, visible individual fiber texture with clear yarn thickness variations, natural slubs, neps, thick-thin yarn variations and weave imperfections, high-frequency micro surface details, lived-in fabric with subtle patina, wear marks, raw authentic hand-feel with visible imperfections, no uniform plastic smoothness, no waxy artificial gloss, no CGI plastic texture
```

### 8.4 场景环境真实感（有场景必用）

正向：
```
photorealistic, ultra realistic, lived-in atmosphere, natural atmospheric perspective, subtle airborne dust and micro particles visible in light beams, volumetric god rays with realistic light scattering, soft diffused natural lighting, imperfect light falloff and natural shadows, realistic color grading with slight color cast, cinematic depth of field, subtle film grain, natural lens imperfections, slight chromatic aberration
```

负向：
```
clean, sterile, pristine, spotless, brand new, overly polished, perfect surfaces, smooth textures, plastic look, artificial, digital art, 3d render, cgi, unreal engine, showroom perfect, too clean, idealized
```

### 8.5 水花/水滴物理（水上乐园/泼水/溅水必用）

```
explosive water splash with photorealistic water physics, water droplets in various sizes suspended mid-air, natural caustic light refraction through water droplets creating micro-rainbow spectra, water droplets impacting lens surface creating realistic lens flare and temporary blur, water beads on skin surface with natural surface tension, water streams running down hair and clothing with gravity-accurate paths
```

### 8.6 手持DNA词（来自 focal-grid，需要手持纪实风格时必加）

```
raw handheld film sequence, shaky handheld camera style, organic breathing motion throughout, natural unstable framing, imperfect handheld composition, documentary-style handheld
```

---

## 九、色调基调词典

| 情绪 | 色调关键词 | 色温倾向 | 阴影占比 |
|------|----------|---------|---------|
| 温暖亲情 | golden warm tones, soft amber glow, sunlit warmth | 3200-4000K暖 | 10-20% |
| 宫廷权力 | cool glacial tones mixed with aristocratic deep gold, high contrast, low saturation | 5600K冷+2400K暖 | 50-60% |
| 悬疑压抑 | desaturated blue-grey, deep shadows, cold directional light, heavy vignette | 6500K+冷白 | 60-70% |
| 欢乐童年 | high saturation golden hour, vibrant primary colors, overexposed highlights, summer haze | 3500K暖金 | 5-15% |
| 离别悲伤 | muted teal-grey, soft diffused light, slight overexposure in memories, faded edges | 4500K冷灰 | 30-40% |
| 愤怒对峙 | high contrast, cool blue-white hardlight from above, dark shadows, shallow focus | 7000K冷白 | 50-65% |
| 暧昧柔情 | warm diffused low light, golden bokeh, soft skin tones, intimate focal length 85mm+ | 2800K暖金 | 15-25% |
| 黑暗绝望 | near-monochrome, heavy shadow 70%+, single cold light source, no fill | 8000K冷蓝 | 70-80% |
| 复仇觉醒 | warm amber edge light + cold interior shadow, split lighting | 暖4100K+冷6500K | 40-55% |
| 闪回回忆 | slight overexposure, faded warm tint, soft vignette edges, film grain enhanced | 3800K暖偏黄 | 10-20% |

---

## 十、工作流程（七步）

```
INPUT → PARSE → CORE → STRUCTURE → DRAFT → AMPLIFY → TECH → OUTPUT
```

### STEP 1 — PARSE（解析输入）

| 输入类型 | 识别特征 | 处理方式 |
|---------|---------|---------|
| 分镜描述（中文） | 含"全景/中景/特写"景别词 | 直接扩写+技术规格注入 |
| Shot list 表格 | 含镜号/景别/运镜列 | 逐行转化为视频提示词 |
| 剧情描述（无镜头语言） | 纯情节/画面叙述 | 先规划景别弧线，再生成各镜头 |
| 推文/文学文本 | 散文叙述+隐喻+感官描写 | 隐喻→视觉转译（6.5表），再规划景别 |
| 图片/截图参考 | 用户提供参考图 | 提取色调/构图/风格后注入提示词 |

### STEP 2 — CORE（建立 Locked Core）

从输入中提取角色、环境、色调，锁定不可漂移元素。

### STEP 3 — STRUCTURE（规划景别弧线 + 运镜链路）

1. 选择景别弧线类型（情感/动作/打斗/暧昧/推文）
2. 按叙事意图（5.2）选择运镜种子
3. 按故事阶段（5.3）确定运镜基调
4. 按能量级别（5.4）匹配运镜强度
5. 确认焦段递进（5.5）
6. 确认画幅适配（5.1竖屏列 / 7.3画幅词）
7. 检查禁止组合（5.6），规划桥接

### STEP 4 — DRAFT（生成各镜头提示词正文）

每镜包含：
- 景别+运镜+机位角度（头部一行）
- 场景描述（融合人物动作+运镜+环境+光线，不割裂）
- 情绪描述（用替换词而非抽象词）
- 特写镜头加五要素（6.3）

### STEP 5 — AMPLIFY（情绪放大检查）

- 所有抽象情绪词是否已替换？
- CU以上是否包含五要素？
- HITCHCOCK：情感峰值是否碎片化？
- SPIELBERG：阴影区是否有叙事意义？

### STEP 6 — TECH（技术规格注入）

每镜追加：
- [技术规格块]（7.1/7.2）
- [特殊协议词]（8.x，按场景类型）
- [画幅关键词]（7.3）
- [负向提示词]

### STEP 7 — OUTPUT（格式化输出）

---

## 十一、输出格式模板

### 11.1 单镜头输出格式

```
═══════════════════════════════════════════
Shot [N] — [景别代码] · [焦段]mm · [时长]s
镜头：[景别中文名] · [运镜中文名] · [机位角度]
叙事意图：[意图] · 故事阶段：[阶段] · 能量：[0.0-1.0]
═══════════════════════════════════════════

[提示词正文——融合书写：人物动作+运镜+环境+光线+情绪物理描述]

[技术规格块]

[特殊协议词（若适用）]

负向提示词：
[negative prompt]

CUT TO
```

### 11.2 多镜头序列输出格式

首镜必须包含【开场状态】头部（第三章），后续镜头省略开场状态但保持 Locked Core 一致。

```
═══════════════════════════════════════════
Locked Core: [场景名]
═══════════════════════════════════════════
[角色固定层]
[环境基调]
[色调锁定]
[技术规格]
[风格DNA]
═══════════════════════════════════════════

── Shot 1 ───────────────────────────────

【开场状态】
[完整四维锚定]

═══════════════════════════════════════════
Shot 1 — [景别代码] · [焦段]mm · [时长]s
镜头：[景别] · [运镜] · [机位角度]
叙事意图：[意图] · 阶段：Setup · 能量：0.2
═══════════════════════════════════════════

[提示词正文]
[技术规格块]

CUT TO

── Shot 2 ───────────────────────────────

═══════════════════════════════════════════
Shot 2 — [景别代码] · [焦段]mm · [时长]s
镜头：[景别] · [运镜] · [机位角度]
叙事意图：[意图] · 阶段：[阶段] · 能量：[值]
═══════════════════════════════════════════

[提示词正文]
[技术规格块]

CUT TO

[...更多镜头...]
```

### 11.3 融合书写规范（来自 camera-movement + storyboard-table）

**绝不割裂**：画面描述禁止把"人物动作"和"镜头运动"拆成两段独立语句。
**必须融合**：将人物动作+微表演+运镜+环境+光线融合为一段流动叙述。

✅ 正例：
```
中景，高角度俯拍，侧拍90°，固定，广角35mm。镜头从长廊上空的高光区起，
客观视角俯拍两人高低悬殊的站位落差——Agnes跪于中央地板上，低头垂眼，
后背棉褂破损处深红色血迹在灰色布料上晕开；King George蹲在Agnes面前，
身体自然放松。焦点保留在两人之间，最后落点交给Agnes后背触目惊心的血迹。
```

❌ 反例：
```
镜头：中景，高角度俯拍。
角色：Agnes跪在地上，表情悲伤。King George蹲在她面前。
```

---

## 十二、完整实战案例

### 案例A — 亲子情感闪回（水上乐园+草地+生日蜡烛）

**Locked Core**：
```
角色：Emma（母亲，30s，浅蓝泳衣→碎花裙→日常家居服，长发偏棕色）
      Ava（4岁→3岁→2岁，碎花泳衣→碎花裙→婴儿睡衣，圆脸大眼睛）
环境：水上乐园→草地→暗室，三个时空闪回
色调：金色暖调，高饱和，强烈阳光→柔光→烛光唯一光源
技术规格：8K 超高清，好莱坞电影质感，写实风格，真人实景拍摄...
风格DNA：温暖怀旧金色暖调，母爱本能的物理化表达
```

**Shot 1 — WS · 20mm · 2.5s · 仰拍（建立）**：

```
【开场状态】
环境：金色调水上乐园，正午，强烈阳光直射，蓝天白云映水面，
      蓝色滑梯管道在阳光下泛光，空气中充满水汽和嬉笑声。
站位关系：Emma站滑梯底部水池中，仰看上方；Ava从滑梯顶端出现。
角色状态：Emma浅蓝泳衣，湿发贴面，双臂张开等待；Ava碎花泳衣，兴奋尖叫。
灯光方案：主光为正午顶射阳光，色温5500K；辅光为水面漫反射蓝光。
      隐藏了什么：滑梯管道内部——Ava滑下来之前，观众看不见她的表情。

全景镜头，从头到脚全身人物，空间关系清晰，仰拍（滑梯底部向上看）角度，
固定机位，20mm极广角。金色调水上乐园——蓝天白云映水面——蓝色滑梯管道
在阳光下泛光——Emma站滑梯底部水池中、水没到小腿——双臂提前张开、仰望上方
——四岁Ava从滑梯顶端出现——她尖叫着滑下——落水瞬间水花爆开溅到镜头上
——画面短暂模糊——然后清晰：Emma抱着湿漉漉的Ava——水珠从两人身上滴落
——阳光在水珠上形成微型彩虹——Ava在水中扑腾喊"Again!"

8K 超高清，好莱坞电影质感，写实风格，真人实景拍摄，阿莱 Alexa 65 摄影机拍摄，
20mm 定焦电影镜头，极致相机浅景深，前景焦外虚化，主体锐度拉满，
发丝光精准勾勒发丝轮廓；HDR 高动态范围，高对比度，色彩还原真实，
画面细节拉满，电影级色彩分级。无字幕无水印，不要音乐，仅保留人声和音效。
[+ 8.5 水花物理协议词]

要求：镜头景别要有变化，机位和摄影角度要有变化，要有特写镜头，
镜头的情绪表达要特别强化

CUT TO
```

**Shot 2 — MS · 50mm · 3.5s · 手持跟拍（关系）**：

```
中景镜头，腰部以上，上半身，中等距离，平视→微俯角度，手持跟拍，动态追踪。
金色调夏日草地——三岁Ava穿碎花裙在阳光草地上转圈——裙子下摆旋转成花朵形状
——转至第七圈重心失衡身体向右歪倒——Emma从画面右侧扑入——不是跑、是"扑"
——母亲的本能——接住Ava的瞬间头发散在Emma脸上——母女的脸贴在一起
——Ava鼻尖撞在Emma颧骨上——两人都在笑——但Emma的手臂收得很紧
——好像知道有一天会接不住

8K 超高清...50mm 定焦电影镜头...手持跟拍...organic breathing motion...
[+ 8.3 布料质感协议词]

要求：镜头景别要有变化...镜头的情绪表达要特别强化

CUT TO
```

**Shot 3 — ECU · 135mm · 2.0s · 推近主观聚焦（情绪峰值）**：

```
大特写镜头，面部填满画面，面部细节清晰，正面（Ava面部）角度，推近运镜，
主观聚焦。金色调暗室——画面唯一光源是两根生日蜡烛，烛光从下方照亮两岁Ava的脸
——光线在她鼻梁两侧投下对称暖色阴影——火焰在她瞳孔中跳动形成两个微缩光点
——Emma一脸慈爱地低头看着Ava

[五要素检查]
视向：Ava眼睛看向蜡烛火焰，瞳孔中映出两个跳动的光点
呼吸：Ava呼吸轻而缓慢，胸腔微微起伏——屏住了一口气再吹蜡烛
微表情：嘴角微微张开，下唇轻微颤动——期待与紧张的混合
手/身体：小手握在桌边，指节因为用力微微泛白
光线：唯一光源=蜡烛从下方照亮，鼻梁两侧对称暖色阴影——

8K 超高清...135mm 定焦电影镜头...

CUT TO
```

### 案例B — 宫廷对峙（高张力压迫场景）

**Locked Core**：
```
角色：Agnes Hartwell（跪于地板，底层灰色杂役棉褂·鞭刑残破款，
      后背破损血迹，低头垂眼）
      King George（蹲在Agnes面前，无瑕军装，笔挺无皱褶，身体自然放松）
环境：皇家寝殿长廊（楼上），中午，冷白光束×暗黄壁灯
色调：冰冷灰调×贵族暗金，低饱和，高反差，阴暗环境约60%阴影
技术规格：8K 超高清...Arri Alexa 65...
风格DNA：冷硬写实压迫感，权力高低悬殊的物理化表达
```

**Shot 1 — MS · 35mm · 3.5s · 高角度俯拍（建立权力格局）**：

```
【开场状态】
[见第三章实战案例]

叙事意图：ShiftPower（权力变化） · 阶段：Setup · 能量：0.3

中景，高角度俯拍，侧拍90°，固定，广角35mm，深景深保留全景，稳定器固定。
镜头从长廊上空的高光区起，客观视角俯拍两人高低悬殊的站位落差——Agnes跪于
中央地板上，低头垂眼，后背棉褂破损处深红色血迹在灰色布料上晕开；King George
蹲在Agnes面前，身体自然放松，面朝跪在地上的Agnes。焦点保留在两人之间，
最后落点交给Agnes后背触目惊心的血迹与破损。

8K 超高清...35mm 定焦电影镜头...
[+ 8.4 场景环境真实感协议词]

CUT TO
```

**Shot 2 — MCU · 85mm · 3.0s · 缓推（情绪切入）**：

```
叙事意图：BuildEmotion（强化情绪） · 阶段：Conflict · 能量：0.6

近景，俯视，正打Agnes，缓慢推，中焦85mm，浅景深聚焦在Agnes面部，稳定器固定。
镜头从Agnes低垂的头部缓慢推进——眼睫低垂，避免直视（guilt·潜台词）——
焦点逐渐清晰在她的下颔与紧绷的唇角——嘴唇抿成一条线（压抑·身体即情绪）——
景别由近景缓缓递进至特写——呼吸刻意放缓，胸腔起伏几乎看不到——
最后落点交给她冰冷重重地垂下眼睑、咽下血腥的临界帧。

[五要素检查]
视向：低垂回避直视，眼睫遮住大半眼球
呼吸：刻意放缓，胸腔起伏几乎看不到
微表情：嘴唇抿成一条线，下颌咬紧但不动
手/身体：双手在身侧蜷缩，指节因为用力微微泛白
光线：冷白自然光束从右上斜切，只照亮半脸，另一半沉入阴影

8K 超高清...85mm 定焦电影镜头...

CUT TO
```

---

## 十三、自检清单（输出前必须执行）

**A · 景别与节奏**：
- [ ] 景别变化是否覆盖至少3级（全/中/特）？
- [ ] 是否有至少1个特写（CU或ECU）？
- [ ] 同景别不连用超过2次？
- [ ] 焦段选择是否匹配景别（5.5焦段递进表）？

**B · 情绪放大**：
- [ ] 所有抽象情绪词是否已替换为物理/视觉描述？
- [ ] CU以上是否包含五要素（视向/呼吸/微表情/手/光线）？
- [ ] HITCHCOCK：情感峰值是否碎片化而非全景直述？
- [ ] SPIELBERG：阴影区是否有叙事意义？

**C · 一致性**：
- [ ] Locked Core（角色/环境/色调/技术规格）是否在所有镜头中逐字一致？
- [ ] 首镜是否有完整的开场状态头部？

**D · 运镜叙事**：
- [ ] 每个运镜是否有叙事动机（不是"氛围""感觉"）？
- [ ] 是否有禁止组合（缓推→紧接缓拉 / 急推→急推 / 手持→立刻静态）？
- [ ] 金句/落点句是否运镜归零（纯静态）？
- [ ] 画幅适配：竖屏段运镜是否以垂直方向为主？

**E · 技术规格**：
- [ ] 每条提示词是否包含技术规格块？
- [ ] 涉及水戏/湿衣？→ 已加入湿衣写实协议（8.2）？
- [ ] 涉及哭泣/眼泪？→ 已加入眼泪物理协议（8.1）？
- [ ] 涉及布料/服装？→ 已加入布料质感协议（8.3）？
- [ ] 涉及水花/溅水？→ 已加入水花物理协议（8.5）？
- [ ] 需要手持纪实？→ 已加入手持DNA词（8.6）？

**F · 融合书写**：
- [ ] 人物动作+运镜+环境+光线是否融合为一段叙述（不割裂）？
- [ ] 无独立"镜头："段+"角色："段的割裂写法？

**G · 负向**：
- [ ] 负向提示词是否包含：plastic skin / waxy / CGI / cartoon / watermark / overly smooth / 3d render？

### 通过声明

```
═══════════════════════════════════════════
视频提示词: 通过
═══════════════════════════════════════════
景别: [N级] ✓ · 情绪: [无抽象词] ✓ · 一致性: ✓
运镜: [有动机] ✓ · 禁止组合: 0 · 画幅适配: ✓
技术: [每镜有] ✓ · 写实协议: [已加] ✓
融合书写: ✓ · 负向: ✓
Locked Core: ✓ · 开场状态: ✓
镜头总数: ___ · 可投喂平台。
═══════════════════════════════════════════
```

---

## 十四、平台适配速查

| 平台 | 画幅偏好 | 语言偏好 | 最大时长 | 特殊注意 |
|------|---------|---------|---------|---------|
| 即梦/Seedance | 9:16竖屏 | 中文规格块 | 5-10s | 中文优先，结尾加"要求"句 |
| Kling | 9:16竖屏 | 中文/英文均可 | 5-10s | 支持camera movement关键词 |
| Veo | 16:9横屏 | 英文 | 8-60s | 长提示词效果更好 |
| Sora | 16:9横屏 | 英文 | 20s | 自然语言描述风格 |
| Runway | 16:9横屏 | 英文 | 10-16s | 结构化提示词效果好 |
| Pika | 16:9/9:16 | 英文 | 3-4s | 简短精准 |

---

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| 2.0.0 | 2026-06-18 | 从四大技能库提纯初始版 |
| 3.0.0 | 2026-06-18 | 整合七大技能库（+camera-movement/performance-description/focal-grid）：新增运镜意图映射15类、故事阶段7级、能量级别映射、焦段递进9级网格、禁止组合桥接规则、四条导演法则、潜台词→表演→提示词映射、隐喻视觉转译表、手持DNA词、FRAGMENT/LINGER/金句定格景别、融合书写规范、平台适配速查、完整实战案例重构 |
