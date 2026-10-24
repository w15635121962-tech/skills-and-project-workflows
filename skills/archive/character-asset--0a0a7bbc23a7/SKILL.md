---
name: character-asset
description: "从影视剧剧本或参考图中提取人物角色资产，生成结构化角色卡（外貌/体型/视觉锚点/服装/配饰/妆发/关系/心理基线/角色圣经），适用于角色设计、视觉一致性维护、AI角色参考图生成。当用户提供剧本文本或角色参考图并要求提取角色信息、生成角色档案、角色卡、角色圣经、或进行角色视觉一致性检查时触发。(user)"
agent_created: true
---

# 人物角色资产提取技能

## 用途

从影视剧本或角色参考图中，精准提取人物角色视觉与叙事资产，输出结构化档案，供：

- 角色概念设计与视觉开发
- 角色视觉一致性维护（跨场次/跨镜头）
- AI 角色参考图生成（中性肖像 / 多视图 / Character Bible）
- 服装/配饰/妆发部门造型参考
- 演员选角与表演指导

**只提取角色资产，不做分镜、不做场景、不做道具、不做AI视频提示词。**

---

## 触发条件

- 用户提供剧本文本并要求提取角色信息 / 生成角色卡
- 用户上传角色参考图并要求分析角色视觉资产
- 用户需要生成角色圣经（Character Bible）或角色档案
- 用户需要检查角色视觉一致性
- 用户需要 AI 生图用的角色描述 Prompt

---

## 输入模式

| 模式 | 输入内容 | 分析依据 |
|------|----------|----------|
| **图片模式** | 角色剧照 / 参考图 / 概念设计图 | 视觉识别，直接观察角色外观 |
| **剧本模式** | 剧本文本 / 角色小传 / 场次描述 | 从文字中推断角色视觉信息 |
| **混合模式** | 图片 + 剧本 | 交叉验证，图片补充剧本未描述部分 |

**剧本模式说明：**
- 扫描剧本中所有与角色外貌、性格、社会身份、关系相关的描述
- 按角色维度整理，若剧本未明确描述则标注「剧本未提及，建议参考视觉参考图」
- 可结合剧情语境进行合理推断（如「华尔街投行合伙人」推断定制西装+精致手表），但推断内容需注明「依剧情推断」

---

## 执行流程

### 第一步：扫描与确认

收到输入后，先做：

1. **图片模式**：识别图片中的角色，若多人则逐个标注，确认角色名称
2. **剧本模式**：快速扫描全文，列出所有出场角色及其首次出现场次，与用户确认分析范围（全部角色 or 指定角色）
3. 确认输出深度：完整角色卡 or 指定模块（如仅服装卡、仅关系图）

### 第二步：角色卡（Character Card）

为每个角色生成一张完整的角色卡，包含以下 7 个维度：

```markdown
## 角色卡：[角色名]

### ① 身份基线（Identity Baseline）

- **角色名**：
- **别名/绰号**：
- **年龄**：
- **性别**：
- **种族/民族**：
- **社会身份**：职业/阶层/阵营
- **时代背景**：
- **角色类型**：主角 / 配角 / 反派 / 功能性角色

### ② 外貌细目（Appearance Detail）

- **整体印象**：一句话概括角色给人第一视觉印象
- **体型**：身高感 / 体型分类（纤细/匀称/健壮/魁梧/矮小）
- **面部**：
  - 脸型：[圆脸/方脸/瓜子脸/菱形脸/国字脸]
  - 五官特征：[眉形、眼型、鼻型、唇型]
  - 骨相关键词：[颧骨高低、颌线清晰度、鼻梁]
  - 特殊标记：[疤痕/胎记/痣/纹身/穿孔 — 位置+形态]
- **皮肤质感**：肤色/质感/毛孔可见度/自然红润度
- **头发**：
  - 基础：发色/发长/发质（直/卷/粗/细）
  - 常用发型：[日常发型名称+描述]
- **眼睛**：
  - 虹膜颜色：
  - 眼型与神态：[杏眼/丹凤眼/深窝眼 + 眼神特征]
  - 视觉聚焦习惯：[直视/游移/下垂/锐利]
- **体态与惯用姿态**：
  - 站姿：[挺拔/驼背/松散/紧绷]
  - 步态：[大步/小碎步/沉稳/急促]
  - 习惯性小动作：[手指动作/嘴唇咬/眼神回避]
- **视觉锚点（Visual Anchor — 最重要的3个视觉识别特征）**：
  1. [如：左眉角贯穿伤疤]
  2. [如：银色领带夹]
  3. [如：永远半扣的衬衫第一颗扣子]

### ③ 服装清单（Costume Inventory）

按场次/造型变化列出：

| 场次/造型 | 服装描述 | 主色系 | 材质/质感 | 状态 | 视觉关键词 |
|----------|---------|--------|----------|------|-----------|
| 场次1-3（日常） | 深灰色羊毛西装+白衬衫 | 灰白冷调 | 精纺毛呢、微光泽 | 完好 | 克制、精英 |
| 场次7（打斗后） | 同上西装 | 同上 | 同上 | 破损+血渍 | 狼狈、失控 |

**单场次详细服装卡（按需展开）：**

```
**场次N：[场景简述]**

- **整体风格**：（赛博朋克 / 优雅高定 / 暗黑哥特 / 简约现代等）
- **主色系**：主色 + 辅助色 + 点缀色
- **上装**：款式、材质、剪裁、细节
- **下装**：款式、长度、材质、细节
- **外套/外层**：有无、款式、长度、材质
- **鞋子**：类型、颜色、跟高、特色
- **服装状态**：新旧程度、破损、褶皱、湿润等
- **整体服装氛围**：
```

### ④ 配饰清单（Accessories Inventory）

按场次/造型变化列出：

| 场次/造型 | 标志性配饰（1-3件） | 位置 | 材质/颜色 | 整体风格 |
|----------|-------------------|------|----------|---------|
| 场次1-3 | 银色领带夹、机械手表 | 领带中部/左手腕 | 抛光钢/蓝宝石镜面 | 精英冷调 |
| 场次7 | 同上+破碎眼镜 | 同上+手持 | 同上/镜框变形 | 瓦解感 |

**单场次详细配饰卡（按需展开）：**

```
- **耳饰**：类型、材质、颜色、形状、大小、悬挂方式
- **颈部配饰**：项链、颈链、围巾、领结
- **手部配饰**：手链、手环、戒指、手套（左右手分别）
- **头部配饰**：发饰、发夹、帽子、头冠、眼镜
- **腰部及身体配饰**：腰带、腰链、胸针、别针
- **其他配饰**：包包、丝袜、披肩等
- **配饰材质与质感**：金属、光泽、宝石、哑光等
- **配饰整体风格**：
```

### ⑤ 妆发清单（Hair & Makeup Inventory）

按场次列出：

| 场次 | 发型（一句话） | 发色/发质 | 妆容关键词 | 发饰（1-2件） | 妆发状态 |
|------|-------------|----------|----------|-------------|---------|
| 场次1 | 低马尾，碎发自然 | 黑色/直发 | 淡妆，豆沙唇 | 黑色发夹（右） | 整洁 |
| 场次3 | 同低马尾 | 同上 | 同淡妆 | 同发夹 | 凌乱湿润（雨中） |
| 场次5 | 大波浪披发 | 同上 | 浓妆，红唇 | 金色发箍 | 精致完整 |

**单场次详细妆发卡（按需展开）：**

```
**【发型章节】**
- 发型名称：
- 长度：短发 / 中发 / 长发 / 及腰
- 发色：黑色 / 棕色 / 金色 / 挑染 / 渐变
- 发型结构：刘海（有/无，类型）、发包位置、发尾走向、蓬松度
- 发量感：丰盈 / 适中 / 扁塌
- 发型状态：整洁 / 凌乱 / 被风吹乱 / 被雨水打湿 / 出汗贴额
- 特殊造型：假发 / 发套 / 伤疤化妆

**【妆容章节】**
- 妆感定位：素颜 / 淡妆 / 浓妆 / 舞台妆 / 特效妆
- 底妆：肤色、遮瑕程度、光泽感/哑光
- 眉眼：眉形、眼影色系、眼线、睫毛
- 腮红与修容：腮红位置与色系、轮廓修饰程度
- 唇妆：唇色、质地（哑光/水光/丝绒）、完整度
- 特殊妆容：伤痕、淤青、血迹、老年妆、角色标记

**【发饰与头饰章节】**
- 发箍/发带：类型、材质、颜色
- 发夹/发簪：数量、位置、材质、装饰
- 帽子/头巾：类型、佩戴方式
- 其他头饰：皇冠、头纱、额饰
```

### ⑥ 关系图谱（Relationship Graph）

```markdown
**与 [角色B] 的关系：**
- **关系类型**：[恋人/仇敌/上下级/师徒/亲族/暧昧/陌路]
- **信任度**（0-1）：
- **恐惧度**（0-1）：
- **敌意度**（0-1）：
- **权力差距**（-1 到 1，正值=本角色占优）：
- **依赖度**（0-1）：
- **共享秘密**：有/无
- **关系变化轨迹**：[场次区间] 从 [状态A] 变为 [状态B]
```

> 每对重要互动角色各填一张。关系图谱是理解角色行为的底层逻辑。

### ⑦ 心理基线（Psychology Baseline）

> ⚠️ 这是角色的整体心理画像，不是单场景的心理状态。用于指导角色在任何场景中的行为逻辑。

```markdown
- **核心欲望（Want）**：[角色表面想要什么]
- **内在需求（Need）**：[角色真正需要什么]
- **核心恐惧**：[最害怕什么]
- **主导情绪基调**：[大多数场景中外在呈现的情绪倾向]
- **隐藏情绪**：[内心深处被压抑的情绪]
- **权力感（dominance）**：0-1（0=完全被动/1=完全掌控）
- **身体紧绷度（body_tension）**：0-1（0=放松/1=紧绷）
- **眼神稳定性（eye_contact_stability）**：0-1（0=回避/1=稳定直视）
- **性格关键词**（3-5个）：如「隐忍」「偏执」「深情」「冷酷」
- **表演锚点**：[角色最标志性的微表情/小动作/习惯性姿态]
```

---

### 第三步：角色速查总表

在所有角色卡之后，输出全角色速查表：

```markdown
**【角色速查总表】**

| 角色名 | 类型 | 一句话视觉描述 | 视觉锚点1 | 视觉锚点2 | 视觉锚点3 | 主色系 |
|--------|------|-------------|----------|----------|----------|--------|
| 女主 | 主角 | 优雅隐忍的旗袍女子 | 左眉角小疤 | 翡翠耳坠 | 素色旗袍 | 青白淡雅 |
| 反派 | 反派 | 锋利冷傲的西装男人 | 银色领带夹 | 无名指黑曜石戒指 | 灰色西装 | 灰黑冷硬 |
```

---

### 第四步：跨角色视觉一致性核查

```markdown
**【角色视觉一致性核查】**

**同角色跨场次一致性：**
| 角色 | 涉及场次 | 外貌锚点是否一致 | 服装是否一致 | 妆发是否一致 | 风险提示 |
|------|---------|-----------------|-------------|-------------|---------|
| 女主 | 1/3/5/7 | ✅ 一致 | ⚠️ 场次7服装破损 | ✅ 一致 | 场次7破损需确认剧情需要 |

**跨角色视觉冲突：**
- [如：女主与女反角服装色调过于接近，场景内难以区分]
- [如：两个男性角色视觉锚点相似（都戴眼镜），建议差异化]

**建议调整：**
- [具体调整建议]
```

---

### 第五步：角色圣经锁定（Character Bible）

> 为需要 AI 生成角色参考图或多镜头角色一致性的项目，输出一份锁定的角色圣经。锁定后，后续所有涉及该角色的提示词必须严格匹配圣经中的描述。

**角色圣经格式：**

```markdown
## 角色圣经：[角色名]（LOCKED）

**Identity**: [年龄 + 种族 + 性别], [角色类型/archetype]

**Facial Features**: [骨相+五官+特殊标记]

**Skin Texture**: [肤色+质感+毛孔+自然红润度]

**Eye Details**: [虹膜色+眼型+视觉聚焦逻辑]

**Hair**: [发色+发质+常用发型]

**Body Type**: [体型+体态+惯用姿态]

**Expression Style**: [表情基调+标志性微表情+习惯性小动作]

**Visual Anchors (3)**: 1. [锚点1] 2. [锚点2] 3. [锚点3]

**Primary Costume**: [日常/标志性服装+材质+色调]

**Key Accessories**: [标志性配饰+材质+位置]

**Overall Presence**: [气场+存在感+一句话视觉印象]

**Consistency Rule**: Once locked, no changes to face structure, visual anchors, skin texture, primary costume details, or key accessories across any shots.
```

---

### 第六步：中性正面肖像参考（Neutral Front Portrait）

> 当用户需要生成 AI 角色参考图时，输出标准中性正面肖像提示词。此肖像作为角色所有后续变体的基准锚点。

**核心强制原则：**

- **视角强制**：perfectly frontal view + head perfectly straight-on facing camera + symmetrical facial composition + shoulders square to camera
- **表情强制**：neutral facial expression + calm impassive resting face + no smile/no smirk/no emotional micro-expression + relaxed neutral gaze
- **为什么严格**：AI 模型默认添加微笑或轻微情绪，强侧光会让"中性脸"带有故事性或阴冷感，破坏后续多视图一致性

**光照策略（绝对禁止强侧光、伦勃朗光、戏剧性阴影）：**

方案A（最干净 — 推荐做角色锚点）：
```
soft even frontal key lighting with subtle fill from below, gentle volumetric light falloff, soft natural catchlights in both eyes, minimal facial shadows that could imply emotion, clean but cinematic three-dimensional form
```

方案B（更电影化 — 带环境氛围）：
```
motivated soft window light from front-left, diffused key light with gentle shadows, realistic light interaction on skin and fabric, subtle volumetric atmosphere, shallow depth of field
```

**强制技术参数：**
```
shot on Arri Alexa 65, 85mm or 100mm lens, T2.8, shallow depth of field, detailed realistic skin texture with visible pores and natural imperfections, subsurface scattering (SSS), lifelike eyes with realistic catchlights and reflections, realistic fabric texture and physics, photorealistic, hyperrealistic, ultra photorealistic, realistic live-action cinematic film still, no plastic skin, no waxy skin, subtle realistic film grain
```

**不同景别推荐：**

| 类型 | 附加描述 |
|------|---------|
| **特写/胸像（最常用锚点）** | [角色圣经描述] + 正面中性核心模块 + 方案A光照 + 技术参数 |
| **全身正面参考** | 加：full body front view, standing straight facing camera, natural relaxed posture, arms resting naturally at sides, feet shoulder-width apart |
| **半身带环境参考** | 在全身基础上加轻微环境层次，但脸部必须保持中性正面 |

**多视图一致性工作流：**

1. **Step 1** — 生成标准中性正面图（保存 seed 或作为 Character Reference / IP-Adapter 图）
2. **Step 2** — 侧面/背面/45°角时加：`consistent character, same person as the front neutral reference, exact same facial features, same age, same skin details, same bone structure`
3. **Step 3** — 表情变体单独生成：`same character as the neutral front reference, [specific emotion], but keep facial structure and bone structure 100% identical`
4. **Step 4** — 服装/配饰变体也基于此正面锚点出发

---

## 角色描述模板

### 通用角色描述规范模板

```
"[Archetype + Age + Gender], [key facial features], [expression/micro-expression details]. Wearing [clothing with fabric texture, fit, and details]. [Hair style and texture]. [Key accessories with material/reflection details]. [Posture/action if applicable]. Located in [environment/setting]. Overall atmosphere: [mood + presence]. Cinematic lighting with [specific light interaction]. Ultra-realistic movie still quality, [skin texture, pores, imperfections], precise material rendering on [clothing/accessories]."
```

### 眼睛真实感描述模块（影视级人像关键防AI假眼）

必须强制加入以下真实光学逻辑：
- **双眼汇聚一致性**：两眼必须锁定同一个焦点目标
- **高光锚点一致**：两眼高光位置必须严格对应主光方向
- **角膜折射与体积感**：角膜有凸起厚度，瞳孔有深度
- **意识导向**：提示词必须包含"conscious gaze / emotionally anchored eye focus / locked on specific target"

推荐影视级眼睛提示词（直接使用）：
```
perfect binocular convergence, both eyes locked on same focal target, realistic corneal refraction, physically accurate catchlights, subtle tear film reflection, natural pupil depth, cinematic ocular tension, microsaccadic eye movement, emotionally focused gaze, dynamic eyelid compression, living human eyes, no dead-eye effect, conscious attention
```

### 皮肤与面部真实感

可见毛孔细纹，自然红润感，肤色不均（轻微色差），保留轻微小痣/雀斑，真实皮肤肌理，五官原生自然，轻微不对称，表情放松不僵硬。绝对禁止塑料陶瓷肌或AI建模痕迹。

---

## 注意事项

- **图片模式**：若图片质量不佳导致细节不清，标注「图片不清晰，无法确认」而非猜测
- **剧本模式**：若剧本未明确提及某字段，标注「剧本未提及」；若依剧情合理推断，标注「依剧情推断」
- 严禁在角色外貌描述中加入主观审美评价（如"最美的""最帅的"），只做客观描述
- 配饰务必细致：位置（左/右/后脑）、数量、材质、颜色
- 妆发描述区分「完好状态」和「剧情导致的破损状态」
- 视觉锚点是角色识别的核心，优先级高于所有其他细节
- 角色圣经一旦锁定，任何后续变更必须明确标注并更新版本号
- 关系图谱是双向的，A→B 和 B→A 需分别填写

---

## 输出资产包清单

| 序号 | 资产 | 说明 | 可被引用 |
|------|------|------|---------|
| 1 | **角色卡** ×N | 7维完整角色档案 | ✅ storyboard-table 引用视觉锚点 |
| 2 | **角色速查总表** | 全角色视觉概览 | ✅ 一目了然 |
| 3 | **跨角色一致性核查** | 同角色跨场 + 跨角色冲突 | ✅ scene-asset 联合核查 |
| 4 | **角色圣经** ×N | 锁定的 AI 一致性锚点 | ✅ 所有 AI 生图引用 |
| 5 | **中性正面肖像 Prompt** ×N | 角色参考图基准 | ✅ AI 图片生成直接使用 |
