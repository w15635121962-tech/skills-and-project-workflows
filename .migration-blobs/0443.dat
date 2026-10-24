# AI 生成适配指南

## 〇、Full Script Fidelity 提示词完整性原则

剧本完整性规则直接约束AI提示词的生成——每一条原始剧本内容都必须有对应的提示词覆盖。

**提示词完整性规则**：
- 原始剧本的每句台词在分镜中必须出现，且对应提示词必须包含Lip Sync声明（如该镜头有台词）
- 原始剧本的每段动作描述必须被转化为至少一个镜头的提示词
- 原始剧本的括号说明（情绪/节奏/表演指示）必须体现在提示词的情绪/表演层声明中
- 不可将多句台词合并到一个镜头中（除非剧本本身设计为连续独白）
- 不可将多段动作描述压缩为一个镜头的动作说明

**提示词遗漏的检测方法**：
- 对照Exhaustive Inventory中台词清单→确认每句台词都有对应镜头的Lip Sync声明
- 对照动作块清单→确认每段动作都有对应镜头的动作描述
- 对照括号说明清单→确认每个情绪/节奏指示都在提示词的情绪层/表演层有所体现

**提示词与台词的对应规则**：
- 一句台词=至少一个独立镜头（不可将两句台词合并为一个镜头的Lip Sync）
- 台词中的关键停顿/语气转折应在提示词中用`beat pause`/`tone shift`标注
- 括号说明中的情绪指示应在Lip Sync声明中体现为对应的情绪口型关键词

## 一、分镜到提示词的转换原则

专业分镜的描述面向人类拍摄团队，AI 生成器需要不同格式的提示词。转换时遵循：

1. **锚定在前，变化在后**：提示词前段固定为角色+场景的锚定描述，后段替换为当前镜头的动作/构图
2. **英文优先**：主流 AI 工具对英文提示词的理解更准确
3. **具象替代抽象**：分镜中的"压抑感"→提示词中的"low-key lighting, deep shadows, heavy atmosphere"
4. **技术参数显式化**：光圈、焦距、ISO 等参数直接写入提示词，AI 会参考这些参数影响画面风格

## 二、单镜头提示词模板

```
[风格锚定] EXTREME REALISM cinematic shot. Full-frame cinema (ARRI Alexa Mini LF / Sony Venice), [焦距]mm prime, f/[光圈], [景深描述].

[角色锚定 - 与锚点表一致] [角色名] — [体型轮廓], [服饰描述], [标志性道具], [色彩标签].

[场景锚定 - 与场景锚点表一致] [地点], [空间结构], [地面材质], [光源体系], [氛围元素].

[当前镜头变化] [景别+角度], [运镜方式], [构图描述], [动作与调度], [特殊效果].

[技术参数] [色温/调色], [分辨率], [宽高比]. --ar [比例] --v [版本] --q [质量]
```

### 2.1 生产级首帧提示词标准结构（Production-Grade First Frame Prompt）

**MANDATORY — 所有含人物的分镜图提示词必须包含以下6个声明层**。这是消除AI塑料感、僵硬感、空洞眼神和扁平光影的硬性防护层。不含人物的全景/空镜无需2-3层，但仍需4-6层。

**6层声明结构**：

| 层级 | 名称 | 必含内容 | 禁止出现 |
|------|------|---------|---------|
| 1 | 表情与表演结构 | 微表情 + 眼神自然聚焦 + 自然眨眼 + "人物+正在做的小事+下意识反应+情绪落点" | 无表情/空泛表情描述 |
| 2 | 动作与惯性 | 动作力量感 + 衣角/头发随惯性飘动 + 下意识小动作 | 僵硬呆板/无惯性/雕塑态（除非面瘫美学且声明） |
| 3 | 光源与氛围 | 明显明暗变化 + 顶部光/发丝光 + 侧光 + 光影颗粒 + 灰尘噪点 + 氛围感 | 均匀受光/干净无层次/大平光 |
| 4 | 皮肤与面部真实感 | 可见毛孔细纹 + 自然红润 + 肤色不均 + 轻微小痣 + 真实肌理 + 轻微不对称 + 表情放松 | 塑料陶瓷肌/AI建模痕迹/完美无瑕 |
| 5 | 景深与镜头 | 前景虚化遮挡物 + 中景人物清晰 + 背景虚化 + 85mm定焦大光圈浅景深 + 原相机直出质感 | 全景深锐利/手机质感 |
| 6 | 整体质感 | 轻微胶片颗粒感 + 8K高清 + 神态灵动自然 + 生活化穿搭细节 + 真实实景背景 | AI过度干净/虚拟感/棚拍感 |

**标准首帧提示词完整模板**：

```
[STYLE] EXTREME REALISM production-grade first frame, Shot on Arri Alexa 65, [焦距]mm prime, T[光圈], shallow depth of field

[CHARACTER ANCHOR] [角色锚定段——与锚点表完全一致]

[SCENE ANCHOR] [场景锚定段——与场景锚点表完全一致]

[SHOT] [景别+角度+构图], [运镜]

[LAYER 1: EXPRESSION & PERFORMANCE] 
[微表情具体描述], eyes naturally focused on [焦点目标], 
subtle natural blink timing, 
[人物] doing [正在做的小事], subconsciously [下意识反应], 
emotional landing point: [情绪落点]

[LAYER 2: ACTION & INERTIA]
[主动作 with 力量感描述], 
[clothing/hair inertia: 衣角/头发惯性飘动方向], 
[fidget/subconscious gesture: 下意识小动作]

[LAYER 3: LIGHTING & ATMOSPHERE]
[光位术语 as key, e.g. front-side Rembrandt], 
clear light-to-shadow transition, 
hair light from [方向], side light sculpting [部位], 
dust particles in light beam, atmospheric grain, 
[Never: even illumination, flat lighting, clean no-atmosphere]

[LAYER 4: SKIN & FACE REALISM]
visible pores and fine lines, natural pinkish warmth on cheeks, 
slight chromatic variation across face zones (forehead warmer, cheeks pinker, jaw cooler), 
faint natural mole, authentic skin texture, 
slight facial asymmetry (natural, NOT deformity), 
relaxed expression muscles (NOT frozen), 
subsurface scattering at thin skin areas (nose edges, ear rims),
[Never: plastic skin, porcelain skin, AI-modelled face, poreless, flawless]

[LAYER 5: DEPTH & LENS]
foreground soft obstruction [前景虚化遮挡物描述], 
subject tack-sharp in mid-frame, 
background creamy bokeh, 
85mm equivalent prime lens shallow DOF, 
raw-camera output texture,
[Never: everything-in-focus, phone-camera look]

[LAYER 6: OVERALL TEXTURE]
subtle film grain, 8K resolution, 
natural lively expression with micro-dynamics, 
lived-in wardrobe with fabric wear and texture, 
real location background with organic imperfections,
[Never: AI-clean, virtual/studio-look, overly-polished]

[TECHNICAL] [色温/调色], 4k, --ar [比例]
Negative: --no plastic skin, poreless face, dead eyes, flat lighting, even illumination, 
AI-modelled face, mannequin, cartoon, anime, watermark, text, logo
```

**精简版（日常使用，6层压缩为4段）**：

```
EXTREME REALISM first frame, Shot on Arri Alexa 65, 85mm, T2.0,
[角色锚定] [场景锚定]
[Shot描述],
eyes focused on [目标], [微表情], [小事+下意识反应], landing on [情绪落点],
[action with weight + clothing/hair inertia + fidget],
[lighting position] key with clear shadow transition, hair light, side sculpting, dust in beam,
visible pores, natural chromatic zones, SSS at thin skin, slight asymmetry, relaxed muscles,
foreground obstruction, subject sharp, background bokeh, 85mm shallow DOF,
film grain, 8K, lived-in wardrobe, real location,
4k, --ar 16:9
--no plastic skin, poreless, dead eyes, flat light, even illumination, AI-modelled, mannequin
```

**6层与已有规范的映射**：

| 首帧层 | 对应已有规范 | 增强内容 |
|--------|------------|---------|
| L1 表情表演 | 视觉聚焦逻辑+三步表演法 | 新增"小事+下意识反应+情绪落点"公式 |
| L2 动作惯性 | 三步表演法（主表演+小动作） | 新增"衣角/头发惯性飘动"物理真实性 |
| L3 光源氛围 | 电影打光位置规范 | 新增"光影颗粒+灰尘噪点"大气真实性 |
| L4 皮肤面部 | 皮肤真实感六层系统 | 新增"轻微小痣+轻微不对称+表情放松" |
| L5 景深镜头 | 摄影机参数规范 | 新增"前景虚化遮挡+原相机直出质感" |
| L6 整体质感 | Negative Prompt+film grain | 新增"生活化穿搭+真实实景背景" |

## 三、完整案例：CUT 12

### 3.1 角色锚点

```
角色：Johnny
锚定层：中等偏高偏瘦，肩线方正，剪影修长。厚重哑光深色长袍，可见纤维纹理与深深褶皱，下摆有微弱潮湿痕迹。红色护目镜佩戴于面部。
一致性红线：护目镜红色 + 长袍厚重哑光 + 体型修长方正
色彩标签：深灰黑 + 红色点缀
```

### 3.2 场景锚点

```
场景：修道院中殿 (INT.)
锚定层：纵向长方形中殿，两侧列柱，高耸拱顶被雾气柔化。湿石地板有水洼反光。主光=左高冷蓝花窗月光(7000-8000K)；轮廓光=右后细蓝边光；补光=湿地面冷色微反光。蓝雾从地面翻涌（下浓上淡），体积光柱，灰尘颗粒飘浮。
一致性红线：光源方向(左高) + 地面湿反光 + 雾气层次(下浓上淡)
色温基调：冷蓝灰，低饱和度，高对比度
```

### 3.3 分镜表

| 镜头编号 | 时间段 | 景别 | 角度 | 运镜 | 构图 | 光线 | 动作 | 时长 | 转场 |
|---------|--------|------|------|------|------|------|------|------|------|
| S12-01 | 0:22.0–0:22.8 | 中景 | 低角度(膝高,仰20-25°) | 极缓慢推镜(3s推进20-30cm) | Johnny居中偏上，背后拱门/石柱为高耸剪影被雾柔化，头顶负空间显天花板 | [与场景锚点一致]左高冷蓝主光+右后蓝轮廓光 | [与角色锚点一致]Johnny稳稳站立，双脚扎地双肩方正，长袍自然垂落 | 0.8s | 硬切 |
| S12-02 | 0:22.8–0:23.5 | 中景 | 同上 | 推镜继续 | 焦点向双手收拢，双手抬至胸骨高度，红色护目镜为冷蓝场景中唯一暖色跳跃点 | 同上 | 双手缓慢抬起，动作仪式化，手指尚未完全成形手印 | 0.7s | 硬切 |
| S12-03 | 0:23.5–0:24.5 | 中景→中近景 | 同上，微升1-2° | 推镜减速 | 双手画面正中，深色长袍背景上清晰可读，背景融为散景 | 同上 | 手印完成，颈部微伸下巴微收，姿态锁定=决意 | 1.0s | 硬切 |
| S12-04 | 0:24.5–0:25.0 | 中近景 | 同上 | 锁定静止 | 手印锁定态，[推断]指关节极微弱线条光芒一闪即逝(≤1帧) | 同上 | 姿态如雕塑锁定，手指周围微弱冷冽空气扭曲 | 0.5s | 硬切→战斗爆发 |

### 3.4 AI 提示词

**合并完整版（用于 AI 视频生成，3 秒连续镜头）：**

```
EXTREME REALISM cinematic shot. Full-frame cinema (ARRI Alexa Mini LF / Sony Venice), 35mm prime, f/2.2, shallow-to-medium depth of field.

A solitary figure — Johnny — lean and angular with squared shoulders, wearing a heavy matte-woven dark robe with a deep hood showing visible fiber texture and deep weighted folds, faint damp darkening near the hem. Red goggles strapped to his face — a tiny sharp warm accent in the cold scene.

In the nave of a Gothic monastery. Wet stone floor with puddle reflections catching blue light. Columns with mineral streaks and worn edges. High vaulted ceiling softened by fog. Cold blue stained-glass moonlight from camera-left high (7000-8000K) sculpting hood edges, cheekbones, knuckles, revealing fabric weave and skin texture. Thin blue rim light from right-rear separating robe from mist. Minimal cold bounce off wet floor. Blue-tinted fog rolling upward from the floor, thicker around legs and waist, creating layered depth. Subtle volumetric light shafts. Dust and condensation particles drifting through key light. Cold blue-gray color grade, low saturation, high contrast with deep blacks, subtle film grain, soft flares around window-lattice highlights.

Low-angle medium shot from knee height (30-45cm), camera tilted up 20-25 degrees. Extremely slow steady push-in (20-30cm over 3 seconds) as if the room is pressing toward him. No pan or tilt. Johnny stands centered filling the frame from mid-thigh to head, feet planted, shoulders squared. He raises both hands to sternum height with deliberate ritualistic slowness, fingers folding into a precise combat mudra. As the mudra completes his posture locks — neck straightens slightly, chin tucks — absolute resolve. A barely perceptible cold distortion shimmers in the air around his fingers, and an extremely faint ancient line-glow flashes across his knuckles for a single frame then vanishes. The air feels like it's tightening. No text, no UI overlay, no modern technology.

4K, 16:9. --ar 16:9 --v 7 --q 2
```

**逐镜头版（用于逐帧生成或参考图生成）：**

```
# S12-01 (0:22.0-0:22.8)
[锚定段同上，省略]
Low-angle medium shot from knee height. Johnny standing centered, feet planted, shoulders squared. Heavy robe draping naturally with real weight. Camera begins extremely slow push-in. Cold blue moonlit atmosphere.

# S12-02 (0:22.8-0:23.5)
[锚定段同上]
Low-angle medium shot, push-in continuing. Johnny slowly raising both hands to sternum height with ritualistic deliberation. Fingers not yet fully formed into mudra. Red goggles visible as warm accent.

# S12-03 (0:23.5-0:24.5)
[锚定段同上]
Low-angle medium shot tightening to medium close-up as push-in decelerates. Hands centered in frame on dark robe background, fingers completing precise combat mudra. Neck straightens, chin tucks — posture locks. Barely perceptible cold air distortion around fingers.

# S12-04 (0:24.5-0:25.0)
[锚定段同上]
Low-angle medium close-up, camera locked. Mudra fully locked, posture frozen like sculpture. Extremely faint line-glow flashes across knuckles for one frame. Air tightening. Cut on the lock.
```

## 四、一致性的 AI 提示词技巧

### 4.1 提示词锚定段的一致性

对于同一场景的多个镜头，提示词的前半段（角色锚定+场景锚定）**逐字不变**，只替换后半段的动作/构图。这样 AI 在处理每个镜头时，"看到"的角色和场景描述完全一致，输出一致性大幅提高。

### 4.2 参考图策略

| AI 工具 | 参考图方式 | 建议做法 |
|---------|-----------|----------|
| Midjourney v6/v7 | `--cref` 角色参考 | 生成角色标准图后，所有镜头使用同一 cref URL |
| Stable Diffusion | IP-Adapter / ControlNet | 为角色和场景分别训练 LoRA |
| Runway Gen-3 | 首帧参考 | 用 Midjourney 生成首帧，作为视频起点 |
| Kling | 参考图模式 | 同上 |
| Sora | 提示词一致性 | 依赖提示词锚定段，暂无参考图功能 |

### 4.3 一致性优先级取舍

当 AI 生成无法同时满足所有细节时，按以下优先级取舍：

1. **角色核心外观**（体型+核心服饰+标志性道具）——不可妥协
2. **场景光源方向与色温**——不可妥协
3. **角色动作与姿态**——尽量保持
4. **氛围元素**（雾气、颗粒）——可微调
5. **特殊效果**（空气扭曲、微弱光芒）——优先级最低，可舍弃

## 五、微表情提示词技巧

### 5.1 眼泪的真实感提示词

AI 生成器对"crying"的理解通常很卡通——大颗水珠从眼眶滚落、表情夸张。要获得真实感眼泪，提示词必须描述完整的物理行为链，而不是用"crying"一笔带过。

**标准眼泪提示词结构**：

```
[角色锚定] + A single tear welling from the inner corner of the eye, 
semi-transparent saline texture with delicate environmental light reflections on its surface, 
tracing an irregular curved path down the cheek under gravity, 
pausing at the cheekbone before dripping off, 
wetting the skin to create a moist reflective band, 
slightly smudging mascara along the lash line, 
leaving a faint damp trail, 
tiny droplets clinging to eyelashes via surface tension in hemispherical shapes.
Facial muscles taut with restrained emotion, lips trembling slightly, overall composure barely held.
```

**按情绪强度调整**：

| 情绪 | 提示词调整 | 视觉差异 |
|------|-----------|----------|
| 克制隐忍 | "a single tear", "restrained", "composure barely held" | 单侧泪，缓慢溢出，表情紧绷 |
| 崩溃痛哭 | "tears streaming", "soaking", "mascara running in dark streaks" | 双侧泪，大面积湿润，妆面严重晕开 |
| 无声落泪 | "silent tears falling freely", "no sound", "blank expression" | 多条泪痕并行，表情反而平静 |
| 强忍不哭 | "eyes glistening with unshed tears", "glassy eyes", "blinking rapidly" | 无溢出，仅眼球表面水光+频繁眨眼 |

**跨镜头眼泪一致性提示词**：

连续镜头中，必须在提示词中标注眼泪的"进度"：

```
# 镜头A：刚流泪
...a fresh tear just welling from the inner corner, no trail yet on the cheek...

# 镜头B：泪已滑落
...a tear halfway down the cheek on an irregular curved path, a narrow bright moist band on the skin, a tiny droplet clinging to lower lashes...

# 镜头C：泪已滴落
...a damp trail from inner eye to jawline, slightly smudged mascara, the skin along the trail still faintly reflective, no active tear on the cheek...
```

关键原则：**锚定段中的眼泪描述也要随镜头推进更新**，不能所有镜头都写"crying"——AI 会每次从零生成，导致眼泪在不同镜头间跳变。

### 5.2 其他微表情提示词要点

| 微表情 | 关键提示词 | 常见错误 |
|--------|-----------|----------|
| 汗水 | "beads of sweat forming on the forehead, glistening under key light" | 不要写"sweating"，太笼统，AI会画成全身湿 |
| 颤抖 | "lips trembling slightly, jaw muscle clenching" | 不要写"shaking"，AI会画成全身抖动 |
| 吞咽 | "throat moving in a visible swallow, Adam's apple bobbing" | 极微妙的动作，需要近景才能捕捉 |
| 咬唇 | "lower lip caught between teeth, indenting the flesh" | 比写"nervous"更具体可执行 |
| 闭眼 | "eyes squeezed shut, crow's feet visible at the corners" | 区分于"眼睛闭上"的平静感 |

## 六、打斗戏 AI 提示词技巧

### 6.0 运镜美学的提示词策略选择

打斗戏的提示词写法取决于你选择哪种运镜美学——不同的美学对应完全不同的提示词策略：

| 美学选择 | 提示词策略 | 镜头拆分 | AI工具选择 |
|----------|-----------|----------|-----------|
| 连绵美学 | 聚合——尽可能在单个提示词中描述完整动作段落，保持空间和时间的连续性 | 少（1-3个长镜头） | 视频生成（Runway/Kling/Sora），利用首帧参考保持连续 |
| 切割美学 | 拆细——每个镜头独立提示词，只承载一个冲击瞬间，靠节奏剪辑组装 | 多（6-12+短镜头） | 图像生成（MJ/SD）逐帧生成→后期剪辑拼接 |
| 融合美学 | 分层——长镜头框架提示词+内部关键瞬间的独立提示词，两者都生成 | 中（3-6个） | 视频+图像混合：视频生成长镜头框架，图像生成关键瞬间的精修帧 |

**连绵美学的提示词要点**：
- 一个提示词描述一段完整的动作序列，而非单个瞬间
- 用 `continuous shot` / `unbroken take` / `single uncut take` 声明连续性
- 动作描述按时间顺序排列：`first... then... as he recovers... immediately...`
- 空间描述在提示词开头锁定，后续只描述动作的变化
- AI视频生成器对长动作序列的理解有限，通常最多3-5秒连贯——超出部分建议分段生成+无缝拼接

**切割美学的提示词要点**：
- 每个提示词只描述一个视觉焦点（已在6.1节详述）
- 碰撞瞬间的提示词是核心——这是切割美学最不可省略的镜头
- 节奏不写在单个提示词里，而通过镜头时长和排列顺序在后期实现
- 提示词之间不追求视觉连续——允许轻微的"跳"，因为剪辑本身就是节奏

**融合美学的提示词要点**：
- 先写一个"骨架提示词"描述整个段落的锚定+空间+节奏框架
- 再为骨架内的每个关键瞬间写独立的"精修提示词"
- 骨架提示词用视频生成，精修提示词用图像生成
- 最终剪辑时以骨架视频为底，在关键瞬间切到精修图像/短视频

### 6.1 打斗提示词的特殊挑战

AI 生成器对"fight scene"的理解通常很混乱——两个人模糊地扭打在一起，动作不清晰，武器位置不可控，碰撞瞬间缺乏力度感。要让 AI 生成可用的打斗画面，提示词必须：

1. **每次只描述一个动作焦点**：一个镜头只有一个人在做一个动作，不要让 AI 同时处理两个人的动作
2. **碰撞瞬间需要独立提示词**：碰撞/交锋的瞬间是独立的视觉事件，不能和出招混在一起
3. **武器状态必须显式声明**：AI 不会"记住"上一帧的武器位置，每个镜头的提示词都要写明武器在哪只手、什么姿态
4. **环境反馈不能省略**：雪被搅起、地面碎裂、布料飘动——这些是 AI 理解"力度感"的关键线索

### 6.2 打斗单镜头提示词模板

**重要**：正反打中的正方和反方是独立镜头，必须分别生成独立提示词。不要在一个提示词中同时描述两个方向。

**攻击方动作镜头**：
```
[风格锚定] EXTREME REALISM cinematic shot. [相机参数].

[攻击方锚定] [角色名] — [体型+服饰+武器状态+色彩标签].

[场景锚定 - 与场景锚点表一致].

[动作描述] Close-up / medium close-up, [角度], [运镜]. [角色名] striking with [武器+部位+轨迹], [力度暗示词汇如"full force"/"precise thrust"]. [身体姿态细节]. [武器可见状态].

[环境反馈] [雪/尘/碎片被动作搅起的效果].

[声音提示] [Foley描述转为视觉线索，如"impact frozen mid-frame"].

[技术参数]. --ar 16:9 --v 7 --q 2
```

**碰撞/交锋镜头**：
```
[风格锚定] EXTREME REALISM cinematic shot. [相机参数].

[双方武器锚定] [武器A] meeting [武器B] at point of impact.

[场景锚定].

[碰撞描述] Extreme close-up / close-up, [角度]. [武器A] and [武器B] clashing at [碰撞位置], [碰撞视觉效果: sparks / snow burst / metal flash]. [碰撞瞬间的环境反应: air displacement / debris]. Freeze-frame energy at the point of contact.

[技术参数]. --ar 16:9 --v 7 --q 2
```

**防御方反应镜头**：
```
[风格锚定] EXTREME REALISM cinematic shot. [相机参数].

[防御方锚定] [角色名] — [体型+服饰+当前受伤/破损状态+色彩标签].

[场景锚定].

[反应描述] Close-up, [角度]. [角色名] [dodging/flinching/staggering], [具体身体反应: 上身后仰/侧闪/退步]. [面部表情: fear/pain/determination]. [武器/双手状态].

[受伤/破损状态] [如有新伤害，在此描述].

[技术参数]. --ar 16:9 --v 7 --q 2
```

### 6.3 完整案例：4秒打斗段落（8镜头）

#### 6.3.1 角色锚点

```
角色：林冲
锚定层：中等身高精悍体型，肩宽腰窄。[推断]深色劲装束腰，外披风雪中已半湿的披风。右手持长棍（白蜡杆，约齐眉高）。
一致性红线：长棍(白蜡杆) + 劲装束腰 + 精悍体型
色彩标签：深灰 + 棍身浅木色

角色：反派
锚定层：[推断]壮硕体型，厚重铠甲/皮甲。右手持弯刀/短刀。
一致性红线：弯刀 + 壮硕体型
色彩标签：暗铁色 + 深褐
```

#### 6.3.2 场景锚点

```
场景：雪地战场 (EXT. 夜)
锚定层：开阔雪地，地面覆雪约5cm，被踩踏处露出黑泥。主光=冷白月光从左上方(6000-6500K)，轮廓光=右后微蓝边光。飘雪从右上向左下斜落。远处有模糊的枯树剪影。
一致性红线：月光方向(左上) + 雪地+黑泥 + 飘雪方向(右上→左下)
色温基调：冷白蓝，高对比度
```

#### 6.3.3 分镜表

| 镜头编号 | 时间段 | 景别 | 角度 | 运镜 | 构图 | 动作焦点 | 声音层 | 时长 |
|---------|--------|------|------|------|------|----------|--------|------|
| S1-01 | 0:46.0–0:46.5 | 近景 | 平视微仰 | 微推 | 林冲面部占画面右2/3，左侧留出棍影空间 | 眼神死寂精准，瞳孔锁定目标，握棍右手微调角度 | 风啸渐起 | 0.5s |
| S1-02 | 0:46.5–0:46.8 | 近景 | 平视 | 固定快切 | 反派面部占画面左2/3 | 恐惧表情，瞳孔收缩，上身急后仰 | 急促吸气 | 0.3s |
| S1-03 | 0:46.8–0:47.1 | 特写 | 微俯 | 固定快切 | 棍尖与刀刃碰撞点居中 | 棍从右下划弧击中弯刀刀身中段，金属闪光，雪尘炸起 | 密集金属撞击 | 0.3s |
| S1-04 | 0:47.1–0:47.6 | 中近景 | 侧45° | 手持微晃 | 林冲半身，棍影划过画面对角线 | 收棍回防后立即二次出击，棍端带起雪弧 | 棍破风声+喘息 | 0.5s |
| S1-05 | 0:47.6–0:48.1 | 中近景 | 侧45°反向 | 手持微晃 | 反派半身，弯刀格挡 | 弯刀斜挡棍击，身体被震退半步，脚下雪泥飞溅 | 金属碰撞+靴踏雪 | 0.5s |
| S1-06 | 0:48.1–0:48.4 | 特写 | 低角度 | 固定快切 | 画面下方棍身，上方刀锋 | 棍从下方挑起磕开刀锋，碎雪从接触点溅射 | 高频碰撞 | 0.3s |
| S1-07 | 0:48.4–0:48.7 | 近景 | 微仰 | 固定快切 | 反方面部+右肩 | 右肩铠甲被棍击中凹陷，面部痛苦扭曲，嘴角渗血 | 重击闷响 | 0.3s |
| S1-08 | 0:48.7–0:50.0 | 中景 | 平视 | 极慢拉 | 两人全身，雪地背景 | 血滴与碎雪在空中同帧飞溅，两人分开对峙，喘息可见白气 | 风啸+喘息+血滴落地 | 1.0s |

**节奏分析**：0.5s→0.3s→0.3s→0.5s→0.5s→0.3s→0.3s→1.0s
- 前段（S1-01至S1-03）：加速堆叠，0.5→0.3→0.3，制造出招前的紧张到碰撞爆发
- 中段（S1-04至S1-05）：短暂"呼吸"，0.5→0.5，交锋的拉锯
- 后段（S1-06至S1-07）：再次加速，0.3→0.3，致命一击
- 收束（S1-08）：1.0s长镜头，减速消化，给观众喘息

#### 6.3.4 AI 提示词

**S1-01 (0:46.0–0:46.5) — 林冲眼神**
```
EXTREME REALISM cinematic shot. Full-frame cinema (ARRI Alexa Mini LF), 85mm prime, f/1.8, shallow depth of field.

Lin Chong — lean and wiry with squared shoulders and a narrow waist, wearing dark close-fitting martial attire with a half-wet cloak, right hand gripping a white-ash staff at chin height. Deep gray + pale wood tone.

Open snowy battlefield at night. Ground covered in 5cm snow with black mud exposed where trampled. Cold white moonlight from upper-left (6000-6500K), faint blue rim light from right-rear. Snowflakes drifting from upper-right to lower-left. Distant bare tree silhouettes in fog.

Close-up, eye level with slight upward tilt, very slow push-in. Lin Chong's face occupying right 2/3 of frame, left side reserved for staff shadow. His eyes dead-calm and surgically precise, pupils locked on target. Right hand micro-adjusting staff angle. Cold white moonlit atmosphere, visible breath condensation.

Cold blue-white color grade, high contrast, 4K, 16:9. --ar 16:9 --v 7 --q 2
```

**S1-02 (0:46.5–0:46.8) — 反派恐惧**
```
[风格+场景锚定同上]
Villain — stocky and heavily built, wearing thick leather armor, right hand gripping a curved blade. Dark iron + deep brown.

Close-up, eye level, locked camera quick-cut. Villain's face occupying left 2/3 of frame. Expression of raw fear, pupils constricted, torso jerking backward in a flinch. Urgent intake of breath visible in chest movement.

Cold blue-white color grade, high contrast, 4K, 16:9. --ar 16:9 --v 7 --q 2
```

**S1-03 (0:46.8–0:47.1) — 碰撞**
```
[风格+场景锚定同上]

Extreme close-up, slight overhead angle, locked camera quick-cut. Impact point centered in frame. White-ash staff striking from lower-right arc against the mid-section of a curved blade. Metal flash at contact point, burst of snow dust exploding outward. Frozen energy at the moment of collision. No faces visible — pure weapon impact.

Cold blue-white color grade, high contrast, 4K, 16:9. --ar 16:9 --v 7 --q 2
```

**S1-04 (0:47.1–0:47.6) — 林冲二次出击**
```
[风格+角色锚定同上]

Medium close-up, 45-degree side angle, handheld with micro-shake. Lin Chong half-body, staff sweeping across the diagonal of the frame. He recovers from the first strike and immediately launches a second attack, the tip of the staff carving an arc of kicked-up snow. Visible breath, jaw clenched.

Cold blue-white color grade, high contrast, 4K, 16:9. --ar 16:9 --v 7 --q 2
```

**S1-05 (0:47.6–0:48.1) — 反弹格挡**
```
[风格+场景锚定同上]
Villain — [与锚点一致] stocky, thick leather armor, curved blade in right hand.

Medium close-up, reverse 45-degree side angle, handheld with micro-shake. Villain half-body, blade angled to block. The curved blade catches the staff strike, his body staggered back half a step from the impact, snow-mud splashing from his boots. Arms absorbing shock.

Cold blue-white color grade, high contrast, 4K, 16:9. --ar 16:9 --v 7 --q 2
```

**S1-06 (0:48.1–0:48.4) — 下挑磕开**
```
[风格+场景锚定同上]

Extreme close-up, low angle, locked camera quick-cut. Staff in lower portion of frame, blade edge in upper portion. Staff flicking upward from below to deflect the blade edge, shards of ice and snow spraying from the contact point. Pure weapon geometry — no faces.

Cold blue-white color grade, high contrast, 4K, 16:9. --ar 16:9 --v 7 --q 2
```

**S1-07 (0:48.4–0:48.7) — 反派中击**
```
[风格+场景锚定同上]
Villain — [变化：右肩铠甲凹陷，嘴角渗血]

Close-up, slight low angle, locked camera quick-cut. Villain's face and right shoulder. Right shoulder armor visibly dented from staff impact. Face contorted in pain, blood seeping from corner of mouth. Body recoiling from the hit.

Cold blue-white color grade, high contrast, 4K, 16:9. --ar 16:9 --v 7 --q 2
```

**S1-08 (0:48.7–0:50.0) — 血雪飞溅收束**
```
[风格+场景锚定同上]
Lin Chong — [与锚点一致] + Villain — [变化：右肩凹陷+嘴角血]

Medium shot, eye level, extremely slow pull-out. Both figures full-body in frame against snowy backdrop. Blood droplets and shattered snow flakes suspended in mid-air in the same frame, catching moonlight. The two fighters separating into standoff position. Visible breath condensation from both. Snow continuing to drift down between them.

Cold blue-white color grade, high contrast, 4K, 16:9. --ar 16:9 --v 7 --q 2
```

### 6.4 打斗提示词一致性要点

1. **锚定段逐字重复**：同一场景内所有镜头的角色+场景锚定描述完全一致，只替换动作/构图
2. **武器状态显式声明**：每个镜头的提示词都要写明武器在哪只手、什么姿态——AI 不会从上一帧推断
3. **受伤/破损渐进更新**：角色锚定段中标注[变化：xxx]，后续镜头继承并只增不减
4. **碰撞镜头独立生成**：碰撞瞬间单独用一个提示词，不要和出招或反应混在一起
5. **环境反馈写入提示词**：雪尘、碎屑、飞溅物——AI 需要这些线索来理解力度和方向

## 七、静态抒情段落 AI 提示词技巧

### 7.1 静态场景提示词 vs 动作场景提示词

动作场景的提示词核心是"每次只描述一个动作焦点"，静态场景则相反——**主镜头的提示词应该尽可能完整地承载整个场景的视觉信息**，让 AI 在一张画面中就把氛围、角色、环境全部交代清楚。

| 维度 | 动作场景 | 静态抒情场景 |
|------|----------|-------------|
| 提示词策略 | 拆细，每镜一个焦点 | 聚合，主镜头承载全部 |
| 镜头数量 | 多（4-12+） | 少（1-3） |
| 锚定段重复 | 每镜重复，只换动作 | 主镜头完整，补充镜头精简 |
| 时长 | 短（0.3-1.5s） | 长（5-8s主镜头） |
| AI工具选择 | 逐帧生成→拼接 | 单张高质量图→视频化（微动） |

### 7.2 对称构图的 AI 提示词技巧

完美对称构图是大多数 AI 生成器的弱项——它们倾向于略微打破对称。处理方法：

1. **显式声明对称**：在提示词中写入 `perfect bilateral symmetry, centered subject, mirror-image left and right`
2. **强调中轴线**：`the woman positioned on the exact vertical center axis of the frame`
3. **锁定对称元素**：`house centered on the same axis in the distance`（不只是"远处有房子"，而是"远处房子在同一中轴线上"）
4. **后处理预案**：如果 AI 仍打破对称，可在备注中标注"需后处理微调对齐"或使用镜像翻转技巧（生成半边→镜像→合成）

**对称构图提示词模板**：

```
[风格锚定] EXTREME REALISM cinematic [类型] photograph. [相机参数].

[角色锚定 - 居中主体].

[场景锚定 - 对称布局]. perfect bilateral symmetry, [角色名] positioned on the exact vertical center axis of the frame, [对称元素A] and [对称元素B] spreading symmetrically on both sides, [远处中轴元素] centered on the same axis in the distance.

[构图描述] Frontal composition, camera at eye level, perfect bilateral symmetry. No foreground obstruction. [角色姿态与氛围].

[光线与氛围]. [技术参数]. --ar 16:9 --v 7 --q 2 --raw
```

### 7.3 用户原始提示词的评估与优化方法

用户提供的原始提示词往往已经包含大量视觉细节，分镜师的工作不是从零创建，而是**评估→补全→结构化**：

**评估维度**：

| 维度 | 检查内容 | 常见缺失 |
|------|----------|----------|
| 角色锚定 | 体型/发色/服饰是否有足够细节？ | 经常只有"年轻女子"，缺少材质/色调/体态 |
| 光源体系 | 光的方向、色温、光质是否明确？ | 笼统写"阳光"但不指明方向和色温 |
| 构图意图 | 为什么选这种构图？情绪暗示是什么？ | 只描述构图形式，不解释叙事含义 |
| 氛围要素 | 雾/风/雨/光斑等是否指定？ | 有时缺失动态暗示（风→草叶微动） |
| 色温基调 | 整体色彩倾向是否明确？ | 有"暖"或"冷"但无数值 |

**优化步骤**：
1. 识别原文已明确的要素→保留，纳入锚点表
2. 识别缺失但锚点表必需的要素→推断补充，标注[推断]
3. 将笼统描述（"自然阳光"）→细化为可执行参数（"顶后侧柔和阳光5500-6000K"）
4. 增加构图意图说明（不只是"对称"，而是"对称=画中画的凝视关系"）
5. 检查AI生成器可能的弱项（如对称构图→添加强化对称的提示词）

### 7.4 完整案例：北欧花园阅读（静态抒情单镜头）

#### 7.4.1 角色锚点

```
角色：年轻女子
锚定层：纤瘦匀称，肩线柔和。[推断]浅金/亚麻色长发，自然披落，被阳光染出暖边光。[推断]简洁浅色棉麻连衣裙，奶白/浅灰/淡蓝色调，无繁复图案。[推断]赤足或简约凉鞋。
标志性道具：手中翻开的书本（精装/线装，封面浅色或自然色）
一致性红线：浅色棉麻裙装 + 手持书本 + 纤瘦坐姿 + 浅金发色
色彩标签：奶白/浅灰 + 暖金发色边光
```

#### 7.4.2 场景锚点

```
场景：北欧风格花园 (EXT. 日)
锚定层：宽阔草坪中央开敞空间，远处中轴背景为现代北欧房屋（白色/浅木色，简洁线条）。葱郁草坪+淡雅玫瑰散落（粉/白/淡紫，不靠近相机）。
光源体系：主光=顶后侧柔和自然阳光(5500-6000K)，勾勒发丝暖金边光；补光=天空漫射，无明显硬阴影。
一致性红线：光源方向(顶后侧) + 对称构图轴心(女子居中) + 草坪质感(高度细腻) + 玫瑰不靠近相机
色温基调：暖白自然日光(5500-6000K)，高明度，低-中饱和度
```

#### 7.4.3 AI 提示词

**主镜头（英雄镜头）**：

```
EXTREME REALISM cinematic outdoor lifestyle photograph. Full-frame DSLR (Canon EOS R5 / Sony A7R V), 35mm prime, f/2.8, shallow depth of field.

A young woman — slender and graceful with softly rounded shoulders, wearing a simple pale off-white linen dress with visible fabric weave, long ash-blonde hair catching warm golden rim light from behind, holding an open book in both hands on her lap. Cream-white + warm gold hair accent.

Centered perfectly in a spacious Scandinavian-style garden. Expansive lush green lawn with highly detailed individual grass blade texture. Minimalist Nordic landscape design. Delicate roses scattered naturally through the garden in soft pink, white, and pale lavender — none close to the camera. A cozy modern Nordic-style house visible in the far center background — clean lines, white and light wood tones. 

Frontal composition, camera at eye level, perfect bilateral symmetry — the woman on the vertical center axis, lawn spreading symmetrically on both sides, house centered on the same axis in the distance. No foreground obstruction. The woman sits upright on the grass, head slightly bowed toward the book, expression serene and absorbed. Dress fabric pooling naturally on the grass.

Soft natural sunlight from upper-rear, warm golden rim light on hair, no harsh shadows, sky fill providing even soft illumination. Warm white daylight (5500-6000K), high brightness, ethereal luxury atmosphere. Gentle breeze suggested by the slightest movement in grass tips and dress hem.

Cinematic depth of field, authentic European garden aesthetic, balanced composition, hyper-realistic DSLR quality, subtle film grain.

8K, 16:9. --ar 16:9 --v 7 --q 2 --raw
```

**补充近景**：

```
[锚定段同上]

Medium close-up, slight overhead angle (15 degrees), very slow pull-out. The woman's upper body and open book dominate the frame, background dissolving into a soft green wash with scattered faint rose-colored bokeh dots. Focus locked on her face and the book. Her fingers gently cradling the edge of a page, lashes lowered, the faintest hint of a smile at the corner of her mouth. Sunlight creating a golden halo in her hair.

8K, 16:9. --ar 16:9 --v 7 --q 2 --raw
```

**补充特写**：

```
[锚定段同上]

Extreme close-up, eye level, locked camera. Open book pages occupying the lower half of the frame, the woman's chin and lips visible at the upper edge. Focus on the page text and fingertips. Her fingertip lightly pressing the corner of a page, about to turn but not yet moving. Clean bare nails with no polish. Ultra-shallow depth of field — only fingers and page in focus.

8K, 16:9. --ar 16:9 --v 7 --q 2 --raw
```

**视频版提示词（主镜头→近景缓推）**：

```
[锚定段同上]

Camera begins at eye level in perfect frontal symmetry, slowly and imperceptibly pushing in from full-body to medium close-up over 8 seconds. Her fingers gently turn a page, lashes lowered, serene expression. Soft natural sunlight, warm white daylight, ethereal luxury. Cinematic depth of field, hyper-realistic.

8K, 16:9. --ar 16:9 --v 7 --q 2 --raw
```

### 7.5 静态场景 AI 提示词一致性要点

1. **主镜头是锚定基准**：补充镜头的角色+场景锚定描述必须从主镜头逐字复制，只替换景别/焦距/构图
2. **景深变化导致背景可读性变化**：从全景到近景，背景元素从"可辨认的房屋和玫瑰"变为"绿色色块+粉色散景点"——这必须在提示词中体现，不能近景还写"房屋清晰可见"
3. **微动是氛围的载体**：静态场景不是死画面——"微风使草叶和裙摆有极轻微动态"这类描述让 AI 理解这不是照片而是活的空间
4. **材质描述不能省**：棉麻织纹、草叶纹理、书页纸张——这些是 AI 理解"超写实"的关键线索，笼统写"连衣裙"和写"可见纤维织纹的浅色亚麻连衣裙"效果差距巨大

## 八、手持摄影 AI 提示词技巧

### 8.1 AI 生成器对手持的理解（以及误解）

主流 AI 图像/视频生成器对"handheld"的理解通常很笼统——它可能给你一个普通画面加上随机的模糊条纹，而不是真正的手持摄影感。要让 AI 生成真正有手持真实感的画面，提示词必须区分手持的层次，并给出具体的视觉线索。

**AI 对手持的常见误解**：
- 写 `handheld` → AI 可能理解为"低质量、模糊、噪点多"——这是"劣质手持"，不是"专业手持"
- 写 `shaky camera` → AI 可能生成整个画面模糊的劣质图——需要的是"构图稳定但画面有生命感的微晃"
- 写 `documentary style` → AI 可能给你加胶片颗粒和低饱和度，但画面本身仍然稳如三脚架

### 8.2 三层手持的提示词写法

**呼吸感手持（第一层）**：
```
[锚定段同上]

[构图描述], subtle handheld breathing — the faintest organic micro-movement in the frame as if held by a living person, NOT shaky, NOT blurry, just barely perceptible life in the camera. Composition remains perfectly stable, only the faintest oscillation suggesting human hands. Sharp focus maintained throughout.

[技术参数]. --ar 16:9 --v 7 --q 2
```

关键词：`subtle handheld breathing`, `organic micro-movement`, `barely perceptible life in the camera`, `NOT shaky, NOT blurry`

**临场感手持（第二层）**：
```
[锚定段同上]

[构图描述], combat handheld — camera following the action with visible but controlled organic movement, slight wobble on impact moments, focus-pull delay when subject changes direction rapidly (brief 0.2s focus shift to background before pulling back), composition slightly reactive to on-screen events as if the operator is responding in real-time. Sharp focus 90% of the time with occasional natural focus hunting.

[技术参数]. --ar 16:9 --v 7 --q 2
```

关键词：`combat handheld`, `controlled organic movement`, `slight wobble on impact`, `focus-pull delay`, `natural focus hunting`, `reactive to on-screen events`

**混乱感手持（第三层）**：
```
[锚定段同上]

[构图描述], chaotic handheld — camera operator caught in the chaos, frame shaking violently with occasional loss of horizon line, focus struggling to find the subject (brief moments of total blur on impact), spatial orientation compromised but subject still intermittently visible. The camera itself feels under assault. Use sparingly — this effect fatigues the viewer after 5 seconds.

[技术参数]. --ar 16:9 --v 7 --q 2
```

关键词：`chaotic handheld`, `frame shaking violently`, `loss of horizon line`, `focus struggling`, `spatial orientation compromised`, `camera itself feels under assault`

### 8.3 追焦延迟提示词

AI 视频生成器（如 Runway、Kling、Sora）对追焦延迟的支持有限，但可以通过描述"焦点状态"来暗示：

**攻击方出招时的追焦延迟**：
```
...as [角色名] suddenly strikes forward, focus briefly shifts to the background for a split second before snapping back to the subject — a natural focus-pull delay suggesting a human camera operator reacting to unexpected motion...
```

**碰撞瞬间的冲击失焦**：
```
...at the moment of impact, focus completely collapses for a single frame — a flash of total blur — before recovering, simulating the visual shock of witnessing a violent collision up close...
```

**角色急转身时的焦点丢失**：
```
...[角色名] whips around, and the focus momentarily loses him — the lens hunts for a beat before locking back on his face — a documentary-style focus imperfection that sells the spontaneity of the moment...
```

### 8.4 手持与声音线索的提示词转化

AI 图像/视频生成器无法直接生成声音，但可以在画面中植入"声音的视觉痕迹"来增强手持真实感：

| 声音元素 | 转化为视觉线索 |
|----------|---------------|
| 撞击Foley | 碰撞瞬间画面微震（AI理解为`slight camera jolt on impact`） |
| 操作员呼吸 | 摄影机极轻微的周期性起伏（AI理解为`subtle rhythmic oscillation as if breathing`） |
| 环境音电平波动 | 画面边缘的极微弱动态模糊（AI理解为`barely visible motion blur at frame edges`） |
| 脚步震动传导 | 地面反光在脚步落地时有极微抖动（AI理解为`floor reflections trembling on footfall`） |

### 8.5 手持场景的分镜提示词完整案例

**案例：临场感手持打斗近景**

```
EXTREME REALISM cinematic shot. Full-frame cinema (ARRI Alexa Mini LF), 50mm prime, f/2.0, shallow depth of field.

Lin Chong — lean and wiry with squared shoulders, dark close-fitting martial attire, right hand gripping a white-ash staff. Deep gray + pale wood tone.

Open snowy battlefield at night. Ground covered in 5cm snow with black mud exposed. Cold white moonlight from upper-left (6000-6500K), faint blue rim light from right-rear. Snowflakes drifting.

Medium close-up, 45-degree side angle, combat handheld — camera following the strike with visible but controlled organic movement. Slight wobble as the staff sweeps across the frame. Focus-pull delay: when Lin Chong suddenly shifts direction, focus briefly hunts to the background for 0.2 seconds before snapping back. Composition slightly reactive to the strike as if the operator flinches on impact. Sharp focus 90% of the time with natural focus imperfection on the fastest movement. The staff tip carving an arc of kicked-up snow. Visible breath condensation. Jaw clenched.

Cold blue-white color grade, high contrast, 4K, 16:9. --ar 16:9 --v 7 --q 2
```

### 8.6 手持提示词的避坑指南

| 常见错误 | 问题 | 修正 |
|----------|------|------|
| 只写 `handheld` | AI理解为低质量/模糊 | 区分三层：`subtle handheld breathing` / `combat handheld` / `chaotic handheld` |
| 写 `shaky` | AI生成全画面模糊 | 用 `organic micro-movement` + `NOT shaky, NOT blurry` 限定 |
| 忽略焦点描述 | 手持没有焦点特征=没有真实感 | 加入 `focus-pull delay` / `natural focus hunting` / `brief focus collapse on impact` |
| 手持+全景 | 全景手持失去空间可读性 | 全景用稳定器/轨道，手持留给近景/特写 |
| 混乱手持超5秒 | 观众疲劳，真实感反转 | 标注时长限制：`chaotic handheld — use sparingly, max 5 seconds` |
| 手持+超自然动作 | 纪实感与奇幻内容冲突 | 超自然动作用稳定器+慢速顶点，不用手持 |

## 九、运镜方向的提示词映射

### 9.1 运镜方向 → AI 提示词对照表

AI 生成器对运镜的理解需要从"电影语言"翻译成"画面描述语言"。以下是六种核心运镜方向的提示词写法：

| 运镜方向 | 电影含义 | AI提示词关键短语 | AI常见误解 |
|----------|----------|-----------------|-----------|
| 推镜 | 压迫感升级 | `camera slowly pushing in toward the subject, increasing tension, the frame tightening around him` | AI可能理解为zoom（变焦）——需写`physical camera movement forward` |
| 拉镜 | 疏离/余波 | `camera slowly pulling back, revealing more of the environment, the subject becoming smaller in the frame, distance growing` | AI可能理解为画面缩小——需写`dolly out / physical camera pulling back` |
| 跟拍 | 陪伴/沉浸 | `camera tracking alongside the subject at the same speed, keeping him framed at constant size, moving through the space together` | AI可能生成角色跑但画面不动——需写`camera moving with the subject` |
| 升降 | 权力/规模 | `camera rising from ground level to overhead, transitioning from intimate close-up to god's-eye view of the battlefield` | AI可能只改变角度不改变高度——需写`physically ascending from low to high` |
| 旋转 | 眩晕/失控 | `camera orbiting around the subject, the world spinning behind him, losing spatial orientation, 360-degree revolution` | AI可能生成角色旋转但画面不动——需写`camera rotating around a stationary subject` |
| 手持 | 纪实/临场 | 见第八章手持专项 | 见8.1节 |

### 9.2 运镜映射角色哲学的提示词写法

同一打斗中，不同角色的运镜语言可以不同——这在提示词中需要显式声明：

**混乱角色的镜头**：
```
...chaotic handheld with the camera struggling to keep up, slight loss of horizon line, 
focus hunting erratically, composition unstable — the camera itself seems 
unpredictable and dangerous, mirroring the character's chaotic nature...
```

**秩序角色的镜头**：
```
...smooth Steadicam glide on a dolly track, composition locked to precise 
rule-of-thirds, focus crisp and deliberate, camera movement controlled and 
purposeful — the frame itself represents order and discipline, mirroring the 
character's methodical nature...
```

**同框对比**：
```
...in the same frame, the composition splits: the left side (chaotic character) 
slightly more unstable with handheld micro-shake, the right side (orderly character) 
rock-steady on Steadicam — two philosophies sharing one shot...
```

### 9.3 连绵美学的完整提示词案例

**案例：连绵长镜头打斗（5秒一镜到底）**

```
EXTREME REALISM cinematic shot. Full-frame cinema (ARRI Alexa Mini LF), 24mm wide prime, f/4, deep depth of field. Continuous unbroken take.

Lin Chong — lean and wiry, dark close-fitting martial attire, white-ash staff in right hand. Villain — stocky, thick leather armor, curved blade in right hand.

Open snowy battlefield at night. Cold white moonlight from upper-left, blue rim light from right-rear. Snow drifting.

Continuous single uncut take, Steadicam tracking alongside Lin Chong at waist height. First: Lin Chong stands facing the villain across the snow, staff lowered at his side, breath visible. Then: the villain charges — Lin Chong sidesteps left and sweeps the staff in a low arc, tripping the villain's legs. As the villain stumbles, Lin Chong spins and strikes the villain's shoulder with the staff's mid-section. The villain staggers back, blade swinging wildly. Lin Chong deflects with the staff and plants the staff's butt into the snow, vaulting over it to deliver a kick to the villain's chest. The villain crashes into the snow, blade flying from his grip. Lin Chong lands, staff planted, standing over the fallen opponent. The camera has tracked the entire sequence without cutting, maintaining constant distance and framing, deep focus keeping both fighters and the snowy environment in clarity throughout. Blood on the villain's lip, snow kicked up around their feet, breath condensation from both.

Cold blue-white color grade, high contrast, 4K, 16:9. --ar 16:9 --v 7 --q 2
```

**关键差异**：与切割美学的8镜头提示词相比，连绵提示词把整段动作写进一个描述里，用 `first... then... as...` 连接时序，空间描述开头锁定后不再变化。

### 9.4 融合美学的完整提示词案例

**案例：长镜头框架+关键瞬间精修**

**骨架提示词（视频生成用，描述整体段落）**：
```
[同上锚定段]

Continuous shot framework: camera tracks alongside the fighters through the snowy battlefield. The overall rhythm is a slow build — 2 seconds of standoff, then a burst of 3 seconds of rapid exchanges, then 2 seconds of separation and exhaustion. Camera maintains medium shot distance throughout, occasionally tightening to medium close-up on impact moments without cutting. Deep focus, spatial coherence preserved at all times.

4K, 16:9. --ar 16:9 --v 7 --q 2
```

**精修提示词（图像生成用，捕捉3个关键瞬间）**：

瞬间1——出棍：
```
[锚定段同上]

Medium close-up, 45-degree side, combat handheld. The exact moment Lin Chong's staff sweeps forward — the staff cutting through falling snowflakes, the tip a blur of motion. Maximum dynamic energy, the frame alive with movement. Impact frozen mid-strike.

4K, 16:9. --ar 16:9 --v 7 --q 2
```

瞬间2——碰撞：
```
[锚定段同上]

Extreme close-up, staff meeting blade at the point of impact. Metal flash, snow burst, the force of collision visible in the bend of the blade and the flex of the staff. Time frozen at the loudest frame.

4K, 16:9. --ar 16:9 --v 7 --q 2
```

瞬间3——收束：
```
[锚定段同上]

Medium shot, eye level, extremely slow pull-out. Both fighters separated, catching breath, blood on the villain's lip, staff planted in the snow. The aftermath silence. Snow continuing to fall between them.

4K, 16:9. --ar 16:9 --v 7 --q 2
```

**剪辑说明**：骨架视频作为底轨，在3个关键瞬间处切到精修图像（每帧停留0.3-0.5秒），然后切回骨架视频。视觉上是一次连续的观看体验，但关键冲击点获得了高于视频质量的精修帧。

### 9.5 运镜美学选择的自检问题

写完提示词后，自问：

1. 这段打斗的运镜美学是连绵/切割/融合？提示词策略是否匹配？
2. 每个镜头的运镜方向传递了什么心理效果？是否与叙事意图一致？
3. 如果是融合美学，骨架提示词和精修提示词是否共享锚定段？
4. 是否存在"运镜语言混搭"——同一打斗中无理由地从连绵跳到切割？
5. 运镜方向是否映射了角色立场？混乱角色是否配不稳定运镜？秩序角色是否配稳定运镜？

## 十、正反打拆分的 AI 提示词策略

### 10.1 为什么正反打不能写成一个提示词

正反打在提示词层面最容易犯的错误：把两个方向写进一个提示词。AI 生成器无法在一个画面中同时呈现"从左看向右"和"从右看向左"——它是单帧生成，每帧只有一个视角。正反打必须拆成两个独立提示词，各自锁定视角方向。

**错误示范**：
```
❌ Shot/reverse shot: Lin Chong staring down the villain, the villain flinching in fear
```
AI 会尝试把两个人塞进同一帧，变成双人中景——这不是正反打，这是全景。

**正确示范**：
```
# 正方（提示词A）
Close-up, Lin Chong's face occupying right 2/3 of frame, eyes locked on target to the left, gaze directed off-screen left...

# 反方（提示词B）
Close-up, villain's face occupying left 2/3 of frame, eyes wide with fear looking off-screen right, torso jerking backward...
```

### 10.2 正反打提示词的视线方向锁定

每个正反打提示词必须显式声明角色的视线方向（`gaze directed off-screen left/right`），这是AI维持180度轴线的关键线索：

| 正方构图 | 正方视线 | 反方构图 | 反方视线 | 轴线关系 |
|----------|----------|----------|----------|----------|
| 角色A占右2/3 | `gaze off-screen left` | 角色B占左2/3 | `gaze off-screen right` | A看左=B在左，B看右=A在右 ✅ |
| 角色A占左2/3 | `gaze off-screen right` | 角色B占右2/3 | `gaze off-screen left` | 反向站位 ✅ |
| 角色A占右2/3 | `gaze off-screen right` | 角色B占左2/3 | `gaze off-screen left` | 两人看同一侧 ❌ 轴线错误 |

### 10.3 对话正反打提示词模板

**说话方镜头**：
```
[锚定段]

Medium close-up, [构图方向]. [角色A] speaking, [具体台词内容转化为视觉：嘴唇的动态/表情变化/手势]. 
[微表情/微动作细节]. 
Gaze directed off-screen [left/right] toward [角色B].
[焦点与景深]. [技术参数]
```

**听话方反应镜头**：
```
[锚定段]

Medium close-up, [构图方向——与说话方互补]. [角色B] listening and reacting, 
[具体反应：从什么表情转变为什么表情，转变的触发点是什么]. 
[微表情/微动作细节——重点！听话方的反应才是这个镜头的信息主体].
Gaze directed off-screen [right/left] toward [角色A].
[焦点与景深]. [技术参数]
```

### 10.4 情绪主导的时长分配

正反打不是机械交替——谁的镜头更长更紧，取决于谁的情绪在上升：

| 叙事情境 | 说话方 | 听话方 | 镜头分配策略 |
|----------|--------|--------|-------------|
| A揭露秘密 | A说→B震惊 | B的反应是重点 | A: 中近景2s → B: 近景3s（更长更紧） |
| B否认/辩解 | A沉默→B急切 | B的急切是重点 | A: 近景1.5s → B: 中近景3s + 插入特写 |
| A威胁B | A冷厉→B恐惧 | 双方都重要 | A: 近景2s → B: 近景2s → A: 特写1s（递进收在A的威胁） |
| 情感告白 | A动情→B感动 | B被触动的过程是重点 | A: 中近景2s → B: 中景→近景缓推4s（情绪升温） |

### 10.5 正反打案例：对话场景

**场景**：A告诉B一个震撼的消息

```
# S3-01 说话方（A）
[角色A锚定段]

Medium close-up, A occupying right 2/3 of frame, face three-quarter lit from camera-left. 
A's mouth set in a hard line, jaw muscle tight, eyes steady but with a glint of something unsaid. 
He speaks the line with controlled weight — not shouting, each word landing like a verdict.
Gaze directed off-screen left toward B.

F/2.0, shallow depth of field. 4K, 16:9. --ar 16:9 --v 7 --q 2

# S3-02 听话方反应（B）
[角色B锚定段]

Medium close-up, B occupying left 2/3 of frame, face three-quarter lit from camera-right.
B's expression shifting in real-time: first confusion (eyebrows pulling together), then the realization hitting (eyes widening, lips parting slightly), then the weight of it sinking in (shoulders dropping, a micro-step backward). The transition takes the full 3 seconds of this shot.
Gaze directed off-screen right toward A.

F/2.0, shallow depth of field. 4K, 16:9. --ar 16:9 --v 7 --q 2
```

**关键**：S3-01承载"信息的传递"，S3-02承载"信息的接收与消化"——两个完全不同的叙事功能，所以必须是两个独立镜头、两段独立提示词。B的反应（困惑→醒悟→崩溃）是这个场景真正的高潮，所以B的镜头更长、情绪描述更细。

## 十一、环境参与打斗叙事 & 即兴武器提示词技巧

### 11.1 环境不只是背景——提示词中的环境叙事

AI 生成器默认把环境当作静态背景。要让它理解"环境参与打斗"，必须在提示词中把环境从"where"升级为"what happens to"——不只是"在走廊里打"，而是"走廊的地面/墙面/灯光在打斗中发生了什么"。

**环境叙事提示词模板**：

```
[场景锚定段] + 以下环境要素将在打斗中被激活：
- [地面材质] → [打斗中的变化]: wet tile floor with puddles — water splashing up during grapple, spraying across the floor on impact, opponent's fall sending a sheet of water outward
- [墙面材质] → [被打斗利用]: stained white tile walls — victim's back slamming against the wall cracking a tile, grime smearing from the impact, wall reflecting the struggle in wet reflections
- [灯光体系] → [打斗中的变化]: overhead fluorescent tubes — one tube flickering during the struggle, another shattering from an errant strike, casting staccato shadows
- [空间纵深] → [首尾情绪反转]: corridor receding into deep shadow at the far end — in the first shot this depth reads as danger approaching, in the final shot it reads as the exit toward safety
```

**关键**：环境元素在锚定段中锁定"初始状态"，在变化段中描述"被打斗激活后的状态"。AI 不会自己推断"湿地面在缠斗时会溅水"——你必须写出来。

### 11.2 即兴武器的提示词策略

即兴武器（灭火器、椅子、碎玻璃、水管等）在提示词中需要两步处理：**伏笔+激活**。

**伏笔（建立镜头中）**：
```
# 建立镜头提示词中，在场景描述末尾追加：
...a red fire extinguisher mounted on the wall to the right of the corridor, clearly visible but not drawing attention — a background detail that will become significant.
```

**激活（使用镜头中）**：
```
# 即兴武器使用镜头：
[角色锚定]. [场景锚定 — 包含灭火器].

Medium shot, [角度]. [角色名] crouching low, both hands gripping the red fire extinguisher's handle, aiming it forward. A thick blast of white dry chemical powder erupting from the nozzle, filling the corridor with a cloud that partially obscures the opponent. The powder catching the overhead fluorescent light, turning the mist into a blinding white haze. [角色名]'s face determined behind the spray, eyes squinting against the backscatter.

[技术参数]. --ar 16:9 --v 7 --q 2
```

**即兴武器的提示词要点**：
1. 伏笔镜头中武器必须"可见但不引人注意"——`clearly visible but not drawing attention`，让AI不把它当主角
2. 激活镜头中武器的物理效果必须详细描述——灭火器不是"喷出白色物质"，而是"干粉从喷嘴喷射，在荧光灯下变成致密白雾，部分遮挡对手"
3. 武器使用后的残留效果必须延续——后续镜头中走廊里仍有飘散的干粉颗粒（不是用完就消失）

### 11.3 首尾呼应构图的提示词写法

首尾呼应需要两个提示词共享构图框架，但替换情绪关键词：

**首格（威胁）**：
```
[角色锚定]. [场景锚定 — 走廊纵深尽头的暗处].

Medium shot, camera at eye level, figure standing in the left third of frame facing right. The corridor stretching away behind him into deep shadow — at the far end, a vague silhouette of a figure standing in the dim light. The depth reads as DANGER APPROACHING. Cold oppressive atmosphere, fluorescent hum.

[技术参数]. --ar 16:9 --v 7 --q 2
```

**末格（解脱）**：
```
[角色锚定 — 同一人]. [场景锚定 — 同一走廊，但尽头明亮].

Medium shot, camera at eye level, figure standing in the left third of frame facing right — same composition as the opening. But now his back is to camera, walking away. The corridor stretching away ahead of him into warm light at the far end — the same depth now reads as EXIT TOWARD SAFETY. A still body lies on the wet floor behind him, out of focus. The journey is complete. Same space, opposite emotion.

[技术参数]. --ar 16:9 --v 7 --q 2
```

**关键**：两个提示词中构图描述逐字重复（`Medium shot, camera at eye level, figure standing in the left third of frame`），只替换方向（`facing right` → `back to camera`）和情绪关键词（`DANGER APPROACHING` → `EXIT TOWARD SAFETY`）。AI 通过重复的构图锚定+相反的情绪描述，生成视觉上呼应但情绪上反转的画面对。

### 11.4 完整案例：九宫格走廊打斗（9镜头）

基于用户提供的九宫格对打图，以下是完整的9镜头AI提示词：

#### 角色锚点

```
角色：黑发男子
锚定层：中等身材，黑色短发，深色内搭+深绿色工装外套或黑色夹克，紧绷专注神情
标志性道具：黑色手机（01-02格持有，后续可能脱手）
一致性红线：黑发 + 深色外套 + 紧绷表情
色彩标签：深绿/黑 + 冷白荧光灯

角色：连帽衫男/光头男（[推断]同一角色或同伙）
锚定层：壮硕，深色连帽衫/光头，攻击性体态
一致性红线：深色连帽衫 + 壮硕体型
色彩标签：深灰黑 + 暖色血迹点缀
```

#### 场景锚点

```
场景：地下通道 (INT.)
锚定层：狭长走廊，两侧墙面铺米白色方形瓷砖（有水渍、污垢肌理），顶部嵌入长条冷白色荧光灯管，地面反光散落水渍，湿漉漉
光源体系：主光=顶部冷白荧光灯(4500-5000K)，方向性强+阴暗死角，潮湿反光
一致性红线：米白瓷砖+水渍 + 冷白荧光灯 + 湿地面
色温基调：冷白低饱和，高对比度明暗
```

#### 9镜头提示词

**SCENE 01 — 建立（暗涌）**：
```
EXTREME REALISM cinematic shot. Full-frame cinema (ARRI Alexa Mini LF), 35mm prime, f/2.8.

A man with black short hair — wearing a dark green utility jacket over a dark shirt, holding a black phone, expression taut and focused. Deep green + black.

In a damp underground corridor. Cream-white square tiles on walls with water stains and grime texture. Overhead cold-white fluorescent tube lights. Wet reflective floor with scattered puddles. A red fire extinguisher mounted on the wall to the right — clearly visible but not drawing attention. The corridor receding into deep shadow at the far end where a vague hooded silhouette stands in the dim light.

Medium shot, camera at eye level, the man standing in the left portion of frame facing right, looking down at his phone. The corridor depth behind him reads as DANGER APPROACHING. Cold oppressive atmosphere.

4K, 16:9. --ar 16:9 --v 7 --q 2
```

**SCENE 02 — 触发（被攻）**：
```
[锚定段同上]

Medium shot. The black-haired man leaning backward, left arm raised in a blocking gesture, phone still in right hand. On the left side of frame, the hooded figure swinging a long stick-like weapon toward him. Motion blur on the weapon. The man's body language defensive and startled.

4K, 16:9. --ar 16:9 --v 7 --q 2
```

**SCENE 03 — 焦灼（缠斗特写）**：
```
[锚定段同上]

Extreme close-up. The black-haired man's face — brows locked, eyes sharp and fierce, arm muscles taut and straining. His hand and the opponent's hand locked together at the wrist in a grapple. Water droplets flying between their arms from the wet floor impact. The struggle visible in every tendon and vein.

4K, 16:9. --ar 16:9 --v 7 --q 2
```

**SCENE 04 — 反击（膝顶）**：
```
[锚定段同上]

Medium shot. The black-haired man raising his right knee toward the hooded man's midsection, left fist cocked, right arm hanging ready. The hooded man clutching his stomach, body curling inward from the impact. Water splashing from the wet floor beneath the strike.

4K, 16:9. --ar 16:9 --v 7 --q 2
```

**SCENE 05 — 逆转（被按墙上）**：
```
[锚定段同上]

Medium close-up. The black-haired man pinned against the stained tile wall by a bald man. His face contorted in pain, both hands gripping the bald man's arm trying to break free. The bald man pressing his body weight forward. Tile grime smearing from the impact. The man's back against wet tile, his jacket bunching.

4K, 16:9. --ar 16:9 --v 7 --q 2
```

**SCENE 06 — 翻盘（灭火器）**：
```
[锚定段同上 + 灭火器激活]

Medium shot. The black-haired man crouching low, both hands gripping the red fire extinguisher's handle, aiming forward. A thick blast of white dry chemical powder erupting from the nozzle, filling the corridor with a cloud that partially obscures the opponent. The powder catching the overhead fluorescent light, turning the mist into a blinding white haze. His face determined behind the spray.

4K, 16:9. --ar 16:9 --v 7 --q 2
```

**SCENE 07 — 决胜（重拳击面）**：
```
[锚定段同上 + 干粉残留]

Close-up. The black-haired man's right fist connecting with the hooded man's face. The hooded man's head snapping backward, blood droplets flying from the impact point in a spray arc. Residual dry chemical powder still floating in the air catching the light. Maximum violence frozen at the point of contact.

4K, 16:9. --ar 16:9 --v 7 --q 2
```

**SCENE 08 — 收束（对手倒地）**：
```
[锚定段同上]

Medium shot. The black-haired man standing with feet apart, looking down at the hooded man collapsed on the wet floor. The hooded man seated in the puddle, legs bent, one hand propping himself up, the other raised defensively, body tilted backward. Water splashed outward from the fall. Residual powder dust settling on the wet tiles.

4K, 16:9. --ar 16:9 --v 7 --q 2
```

**SCENE 09 — 离场（首尾呼应）**：
```
[锚定段同上]

Medium shot, camera at eye level, figure in the left portion of frame — same composition as SCENE 01. But now his back is to camera, walking away toward the corridor's far end. The corridor stretching ahead into warm light — the same depth that once read as DANGER now reads as EXIT TOWARD SAFETY. A still body lying on the wet floor behind him, out of focus. The fluorescent lights humming. Same space, opposite emotion. Journey complete.

4K, 16:9. --ar 16:9 --v 7 --q 2
```

### 11.5 九宫格分镜的排版与叙事逻辑

九宫格（3×3网格）本身是一种分镜呈现格式，值得单独说明：

**九宫格的叙事优势**：
- 线性阅读顺序：01→02→03从左到右，04→05→06第二行，07→08→09第三行——符合自然阅读习惯
- 整体感：9格同时可见，观众可以一眼把握完整叙事弧线
- 节奏可视化：9格排列后，景别/角度/构图的节奏变化一目了然
- 首尾呼应直观：01格和09格在网格中对角线位置，呼应关系天然可见

**九宫格的排版规则**：
- 每格之间保留清晰的黑色分割边框，强化"分镜"感
- 每格左上角标注镜头编号（SCENE XX），白色无衬线字体，与暗画面形成对比
- 统一背景环境贯穿9格——这不是9个独立画面，而是同一空间内的9个瞬间
- 中间格（05）通常是叙事转折点——在3×3中它处于视觉中心，天然吸引注意力

## 十二、角色身份板的 AI 生成指南

### 12.1 身份板的定位

角色身份板不是分镜的产物，而是分镜的**前置工具**——在第零步建立视觉锚点时同步生成。它的存在意义是：**给 AI 一个"看到角色"的机会**，而不是让 AI 每次都从文字描述中"想象"角色。

工作流中的位置：
```
剧本 → 角色锚点表（文字） → 角色身份板（图像） → 分镜提示词（引用身份板）
```

- 角色锚点表定义"角色是什么"（文字规范，人读）
- 角色身份板呈现"角色长什么样"（图像参考，AI读）
- 分镜提示词引用锚点表的核心描述 + 身份板作为 `--cref` 参考图

### 12.2 身份板提示词模板

```
Artistic cinematic character identity board, 16:9 aspect ratio, 
pure white / soft off-white background, no environment, no props, no logos, no watermarks.

Character: [一句话角色视觉定义——体型+发色发型+核心服饰+标志性气质]

Layout: Asymmetric, elegant, art-book style. NOT a grid, NOT a blueprint, NOT a catalog. 
Large hero full-body view placed slightly off-center as the visual anchor. 
Around it, smaller clean character studies with generous white space between each: 
neutral standing full-body, back view, side profile view, seated pose, leaning casual pose, 
crouching pose, high-angle looking down at body, low-angle looking up at body, expressive portrait close-up. 
Each study feels like an independent clean character study, NOT frames from a scene. 
NO overlapping figures. NO cropped faces. NO hidden limbs. NO stacked poses. 
Every figure has clear separation and breathing room.

Identity lock: STRICT consistency across ALL views — same face, same facial proportions, 
same hairstyle, same clothing, same body proportions, same posture language, same visual personality.

Silhouette study area: 2-3 simplified black character silhouettes showing key outline shapes.

Expression study area: Subtle emotional variations — [列出角色实际出现的3-4种情绪，如neutral focused, alert tension, suppressed anger, grim determination].

Detail study area: Close-up crops of face shape, hair edge outline, [服装关键细节如collar and pocket details], hand positioning.

Text design: Minimalist character ID block — bold sans-serif name "[角色名]", 
role "[角色定位]", core emotion "[核心情绪]", 
visual signature "[视觉标志]". 
Small handwritten-style labels only where helpful. 
Subtle editorial arrows and annotation marks, kept minimal and elegant.

Style: Minimalist, cinematic, high-end, art-book quality, clean, expressive, production-ready. 
The final image should feel like an artistic character identity sheet designed to help AI models 
understand the character's face, silhouette, clothing, posture, and emotional range.

Ultra-detailed, 8K quality. --ar 16:9 --v 7 --q 2
```

### 12.3 身份板提示词的关键控制点

**布局控制**：
- 必须显式声明 `NOT a grid, NOT a blueprint, NOT a catalog`——AI默认倾向于网格布局，不声明就会得到整齐的表格
- `generous white space` 比 `lots of whitespace` 更有效——前者暗示设计感，后者暗示空旷
- `slightly off-center` 比 `off-center` 精确——太偏会失衡，略偏才有设计感
- `independent clean character study` 是核心概念——它让AI把每个视角当作独立作品而非帧序列

**一致性控制**：
- `STRICT consistency across ALL views` 是必须的强制声明——不加这句，AI会在不同视角给角色换脸
- 逐项列出 `same face, same facial proportions, same hairstyle, same clothing, same body proportions, same posture language, same visual personality`——越细越能防止AI"自由发挥"
- 即使如此，AI 仍可能在某些视角出现轻微偏差——身份板生成后应人工检查一致性，必要时用 inpaint 修正

**分离控制**：
- `NO overlapping figures, NO cropped faces, NO hidden limbs, NO stacked poses`——AI喜欢把角色叠在一起制造"动感"，但身份板需要的是干净分离
- `Every figure has clear separation and breathing room`——"呼吸空间"这个概念帮助AI理解间距不是浪费而是设计

**表情研究控制**：
- 表情描述必须是**微妙变化**而非夸张表情——`subtle emotional variations` 而非 `various expressions`
- 列出角色在剧情中实际出现的3-4种情绪，而非泛泛的 `happy, sad, angry, surprised`
- 好的表情研究 = 角色情绪的合理区间定义，超出这个区间的提示词描述可能让AI"走偏"

**ID块控制**：
- 4个字段就够了：Name / Role / Core Emotion / Visual Signature
- Visual Signature 是最重要的字段——它就是提示词锚定段的核心视觉特征，如 `DARK GREEN UTILITY JACKET + BLACK SHORT HAIR`
- 手写标签 `small handwritten-style labels` 和编辑标注 `subtle editorial arrows` 增加专业感，但 `kept minimal and elegant` 防止AI过度装饰

### 12.4 身份板在提示词工作流中的使用

**生成身份板**：
1. 先写完角色锚点表（文字）
2. 基于锚点表填写身份板提示词模板
3. 用 Midjourney v7 生成身份板（v7 的一致性和细节度最佳）
4. 检查生成结果的一致性——如某视角偏差过大，用该视角单独生成后拼贴替换
5. 保存身份板图像为角色的 `--cref` 参考源

**在分镜提示词中引用身份板**：
```
# Midjourney 分镜提示词
[标准锚定段 + 变化段] --cref [身份板图像URL] --cw 100

# --cw 100 = 参考身份板的脸+服装+风格
# --cw 0 = 只参考身份板的脸（适用于服装变化的镜头）
```

**身份板与 `--cref` 的配合策略**：

| 场景 | --cw 值 | 原因 |
|------|---------|------|
| 角色外观无变化 | 100 | 锁定脸+服装+风格 |
| 角色换装但同一人 | 0 | 只锁定脸，让服装自由变化 |
| 角色受伤/破损 | 0 + 在提示词中描述受伤 | 锁定脸，伤害状态用文字控制 |
| 角色情绪变化 | 100 | 表情研究已定义合理区间 |
| 角色在不同光源下 | 100 | 身份板是中性光，光源由提示词控制 |

### 12.5 身份板生成后的验收检查

身份板生成后，必须逐项检查以下问题：

| 检查项 | 标准 | 常见问题 |
|--------|------|----------|
| 面部一致性 | 所有视角的脸是否是同一个人？ | AI经常在背面/侧面视角给角色换脸 |
| 服装一致性 | 所有视角的服装细节是否一致？ | 口袋位置、拉链方向可能翻转 |
| 身体比例一致性 | 站姿/坐姿/蹲姿的比例是否合理？ | 蹲姿可能被AI画成矮个子 |
| 手部完整度 | 所有可见的手是否完整？ | AI经常少画手指或隐藏手部 |
| 视角覆盖 | 是否有9+个不同视角？ | AI可能省略蹲姿/俯视/仰视 |
| 轮廓研究 | 是否有2-3个简化剪影？ | AI可能跳过或画成阴影而非剪影 |
| 表情范围 | 是否有3-4种微妙情绪变化？ | AI可能给的都是同一表情 |
| 细节研究 | 是否有面部/发型/服装特写？ | AI可能用装饰元素替代 |
| ID块文字 | 是否有名称/角色/情绪/视觉标志？ | AI可能忘记或文字模糊 |
| 分离度 | 角色之间是否有足够间距？ | AI可能让角色互相重叠 |

**验收不通过时的修正策略**：
- 单个视角偏差：用该视角单独生成一张，拼贴替换
- 一致性整体偏差：重新生成，在提示词中加强 `STRICT consistency` 的措辞
- 缺少视角：用该视角单独生成后补充
- 文字模糊：ID块在后期用排版工具叠加，不依赖AI生成文字

## 十三、场景参考图集AI生成指南

### 13.1 场景参考图集的定位

场景参考图集是分镜的**前置工具**——在第零步建立场景锚点时同步生成。角色身份板解决"角色长什么样"，场景参考图集解决"场景从每个角度长什么样"。AI没有空间想象力，它需要从9个不同视角的参考图中"理解"场景的三维结构、光影逻辑和材质系统。

工作流中的位置：
```
场景锚点表（文字） → 场景参考图集（9张图） → 分镜提示词（引用图集光影/色调参数）
```

### 13.2 9机位提示词模板

场景参考图集的标准配置是9个独立提示词，各自描述不同机位，但**共享相同的光影/色调/空间结构锚定段**。

**场景锚定段（9个提示词共享）**：
```
[场景类型] [地点名称], [时间时段]. [空间结构描述]. [地面材质], [植被/建筑描述]. 
[光源体系]: [主光方向+色温+光质], [辅助光描述]. [特殊光效如丁达尔效应/体积光].
[氛围元素]: [雾/烟/颗粒/飘落物]. [色温基调], [核心色调]. Ultra-realistic film-grade rendering, [材质区分度声明如translucent petals, rough bark, soft grass texture].
```

**9机位各自的提示词结构**：
```
[场景锚定段 - 完全重复]

[机位描述 - 每个镜头不同]:
[景别+视角], [运镜方式], [构图描述], [该视角的视觉焦点], [该视角特有的前景/背景层次].

[技术参数] 4K, [宽高比]. --ar [比例] --v 7 --q 2
```

**每个机位的提示词要点**：

| 机位 | 提示词关键词 | 视觉焦点 | 典型前景/背景处理 |
|------|------------|----------|------------------|
| 1.正面近景 | `Close-up, eye level, front view` | 场景标志性元素（花枝/窗户/道具） | 浅景深，背景散景化 |
| 2.正面全景 | `Full wide view, eye level, front view, 35mm wide-angle` | 场景整体纵深+布局 | 深景深，远近都清晰 |
| 3.俯视近景 | `Overhead close-up, looking straight down, top-down` | 地面材质/散落物细节 | 纯地面，无远景 |
| 4.正面近景B | `Close-up, eye level, front view, alternative framing` | 不同层次的前景元素 | 新的前景遮挡物 |
| 5.正面全景B | `Full wide view, eye level, front view, enhanced atmosphere` | 大场景+特定氛围强化 | 强化的雾/光效层次 |
| 6.俯视近景B | `Overhead close-up, looking down at angle, light layers` | 光影层次穿过元素 | 俯拍前景+地面光影 |
| 7.背面近景 | `Close-up, rear angle, looking back through the scene` | 反向视角的纵深 | 背光轮廓+远处光 |
| 8.侧面全景 | `Lateral side full view, 90-degree side angle, tracking shot composition` | 横向纵深+空间层次 | 侧面深度感 |
| 9.俯视全景 | `Bird's eye view, top-down full overview, aerial photography` | 整体布局+地形结构 | 纯俯瞰，无前景 |

### 13.3 场景参考图集的提示词一致性策略

**锚定段完全重复**：9个提示词的前半段（场景锚定）逐字不变，只替换机位描述部分。AI通过重复的锚定描述"理解"这是同一个场景的不同视角。

**光影参数锁定**：
- 所有提示词中光源方向、色温、光质完全一致
- 丁达尔效应等特殊光效在所有适用机位中声明（近景可能看不到完整丁达尔，但局部光柱/光斑仍需保持）
- 阴影方向在所有机位中与光源方向一致

**色调锁定**：
- 色温值显式写入锚定段（如 `3500K-4500K color temperature`）
- 核心色调关键词跨提示词一致（如 `pink green warm gold palette`）
- 不允许某个提示词突然出现新色调词汇（如一个镜头冒出"violet"而其他8个都没有）

**空间逻辑锁定**：
- 场景中的关键地标（道路、建筑、大树等）在各机位中的相对位置一致
- 俯视全景确立了"地图"，其他8个机位的空间关系必须与俯视全景一致
- 人物/动物如果在场景中，位置在各机位中一致

### 13.4 完整案例：春日桃林场景参考图集

#### 场景锚点

```
场景：春日桃林（樱花林）(EXT. 日)
锚定层：春日黄金时刻的野生桃林，粗壮的老桃树干、满枝粉调花簇、散落花瓣、林间土路、草地野花，远景搭配山林与晨雾
光源体系：主光=日出/日落黄金时刻柔和侧逆光，光线穿过花枝形成通透的丁达尔效应（耶稣光），暖调高光与冷调阴影形成冷暖对比，无硬光死黑
色温基调：3500K-4500K，柔和唯美
核心色调：粉、绿、暖金
氛围元素：晨雾朦胧层次，飘落花瓣
一致性红线：侧逆光方向 + 丁达尔效应 + 色温3500-4500K + 粉绿暖金色调
材质系统：花瓣半透明通透感/树干粗糙肌理/草地柔软质感/晨雾朦胧层次
```

#### 9机位提示词

**镜头1 — 正面近景 (Front Close-up)**：
```
Cinematic front close-up shot of spring peach blossom branches in full bloom, golden hour soft side-backlight creating translucent pink petals with visible veins, Tyndall light rays piercing through delicate flowers, a few petals gently falling, warm highlights with cool shadow undertones, 3500K-4500K color temperature, pink green warm gold palette, ultra-realistic film-grade rendering, shallow depth of field, 85mm lens, soft bokeh background of misty forest, hyper-detailed petal texture and light refraction. 4K, 16:9. --ar 16:9 --v 7 --q 2
```

**镜头2 — 正面全景 (Front Full View)**：
```
Cinematic front full wide view of a vast spring peach blossom forest, deep perspective with a winding dirt path through thick old tree trunks covered in dense pink flower clusters, morning mist in background with distant mountains, golden hour soft side-backlight creating dramatic Tyndall effect through the canopy, warm highlights cool shadows, 3500K-4500K color temperature, pink green warm gold palette, ultra-realistic film-grade rendering, 35mm wide-angle lens, establishing shot composition, lush green grass with fallen petals, ethereal romantic atmosphere. 4K, 16:9. --ar 16:9 --v 7 --q 2
```

**镜头3 — 俯视近景 (Top Close-up)**：
```
Cinematic overhead close-up shot looking straight down at a spring peach forest floor, ground covered with fallen pink petals scattered on soft green grass, tiny wildflowers, dappled golden light filtering from above through branches creating warm pools of light, ultra-detailed textures of grass blades and petal surfaces, golden hour warmth, 3500K-4500K color temperature, pink green warm gold palette, macro photography feel, shallow depth of field, film-grade rendering. 4K, 16:9. --ar 16:9 --v 7 --q 2
```

**镜头4 — 正面近景B (Front Close-up B)**：
```
Cinematic front close-up shot of an old gnarled peach tree trunk with foreground peach blossom branches framing the edges, detailed rough bark texture with moss patches, delicate pink flowers as foreground bokeh, golden hour side-backlight creating Tyndall light rays between branches, warm atmospheric glow, 3500K-4500K color temperature, pink green warm gold palette, ultra-realistic film-grade rendering, shallow depth of field, 50mm lens. 4K, 16:9. --ar 16:9 --v 7 --q 2
```

**镜头5 — 正面全景B (Front Full View B)**：
```
Cinematic front full wide view of a vast spring peach blossom forest with enhanced morning mist and dramatic Tyndall light rays, deeper perspective into the forest interior, thick ancient tree trunks with massive pink canopies, layers of atmospheric haze creating depth, golden hour side-backlight flooding through the mist, warm highlights cool blue shadows, 3500K-4500K color temperature, pink green warm gold palette, ultra-realistic film-grade rendering, 24mm wide-angle lens, epic establishing shot. 4K, 16:9. --ar 16:9 --v 7 --q 2
```

**镜头6 — 俯视近景B (Top Close-up B)**：
```
Cinematic overhead close-up shot of peach blossom branches seen from above with golden hour light filtering through the flowers, creating intricate layered shadows on the ground below, fallen pink petals scattered on soft grass, interplay of warm light and cool shadow, 3500K-4500K color temperature, pink green warm gold palette, ultra-realistic film-grade rendering, 50mm lens. 4K, 16:9. --ar 16:9 --v 7 --q 2
```

**镜头7 — 背面近景 (Back Close-up)**：
```
Cinematic rear angle close-up looking back through the spring peach blossom forest, backlit flower branches creating silhouettes and rim light on blossoms, depth and mystery of the forest receding into golden mist, old tree trunks as dark vertical elements, golden hour side-backlight, Tyndall rays in the distance, 3500K-4500K color temperature, pink green warm gold palette, ultra-realistic film-grade rendering, 85mm lens, shallow depth of field. 4K, 16:9. --ar 16:9 --v 7 --q 2
```

**镜头8 — 侧面全景 (Side View)**：
```
Cinematic lateral side full view of a spring peach blossom forest showing depth and spatial layering from a 90-degree side angle, side profile of thick old tree trunks with pink flower canopies, winding dirt path extending laterally into the distance, morning mist between the trees, golden hour side light casting long warm shadows, Tyndall effect through the branches, 3500K-4500K color temperature, pink green warm gold palette, ultra-realistic film-grade rendering, 35mm lens, tracking shot composition. 4K, 16:9. --ar 16:9 --v 7 --q 2
```

**镜头9 — 俯视全景 (Top View)**：
```
Cinematic bird's eye top-down view of an entire spring peach blossom forest, complete aerial overview showing the overall layout and terrain structure, winding dirt path cutting through dense pink tree canopies, surrounding mountains and morning mist in the far distance, golden hour light casting warm glow across the landscape, 3500K-4500K color temperature, pink green warm gold palette, ultra-realistic film-grade rendering, aerial photography composition. 4K, 16:9. --ar 16:9 --v 7 --q 2
```

### 13.5 场景参考图集与分镜提示词的衔接

场景参考图集生成后，在分镜提示词中的使用方式：

1. **光影参数直接引用**：分镜提示词中的场景锚定段，直接复制图集提示词中的光影参数段（色温、光源方向、光效），确保分镜与图集光影一致
2. **色调关键词直接引用**：分镜提示词中的色调描述，使用与图集完全相同的关键词（如 `pink green warm gold palette`），不换用近义词
3. **材质描述直接引用**：分镜提示词中的材质系统，与图集锚定段保持一致
4. **机位选择参考图集**：分镜中的每个镜头，都可以在图集9个机位中找到最近似的参考——提示词可以基于该机位图集的提示词改写，只替换角色动作和构图微调

**图集机位→分镜镜头的映射逻辑**：

| 分镜镜头类型 | 最接近的图集机位 | 提示词改写方式 |
|-------------|-----------------|---------------|
| 场景定场 | 镜头2(正面全景)或镜头5(正面全景B) | 保持锚定段+机位，添加角色入画描述 |
| 角色特写前景 | 镜头1(正面近景)或镜头4(正面近景B) | 保持锚定段+景别，角色作为焦点替换花枝 |
| 脚步/地面镜头 | 镜头3(俯视近景) | 保持锚定段+俯视角度，添加角色脚步 |
| 跟拍/行走 | 镜头8(侧面全景) | 保持锚定段+侧角度，添加角色行走 |
| 开场航拍 | 镜头9(俯视全景) | 直接使用或微调 |
| 回头/反向 | 镜头7(背面近景) | 保持锚定段+反向角度，添加角色回头 |

### 13.6 场景参考图集生成后的验收检查

| 检查项 | 标准 | 常见问题 |
|--------|------|----------|
| 光影方向一致性 | 9个镜头的主光方向完全一致 | AI在不同景别中可能改变光源方向 |
| 色温一致性 | 色温锁定，无跳变 | 俯视镜头可能偏冷，近景偏暖 |
| 丁达尔效应一致性 | 有光穿过的镜头都呈现丁达尔 | 全景有丁达尔但近景遗漏 |
| 空间结构一致性 | 关键地标位置在各机位中一致 | 侧面视角中道路位置与正面矛盾 |
| 材质精度一致性 | 所有镜头的材质区分度相当 | 全景材质精细但近景反而粗糙 |
| 色调一致性 | 核心色调跨镜头不变 | 某个镜头突然出现新色调 |
| 季节/时间一致性 | 植被状态/光影时段一致 | 某个镜头花谢了或光线变正午 |
| 景别区分度 | 9个镜头的景别/视角有明确差异 | 多个近景机位看起来几乎一样 |
| 叙事功能覆盖 | 9个镜头覆盖完整的叙事需求 | 缺少反向机位或侧面视角 |
| 画质一致性 | 9个镜头的渲染质量相当 | 某个镜头明显模糊或低分辨率 |

## 十四、视觉聚焦逻辑（Ocular Focus Logic）AI提示词技巧

### 14.1 为什么AI眼睛永远"假"——提示词层面的根因

AI生成器对"眼睛"的理解停留在纹理层面——它会画出精细的虹膜花纹、明亮的高光、清晰的眼白，但它不理解"这个角色在看什么"。提示词中写`ultra detailed eyes, glossy eyes`只会让AI画出更精致的玻璃珠，不会让眼睛"活过来"。

**真正有效的提示词策略**：不是描述眼睛长什么样，而是描述**眼睛在做什么**——视觉目标、聚焦行为、意识状态。AI需要被"告诉"角色正在看哪里、为什么看、带着什么情绪看，然后它才能正确地组织眼球/瞳孔/眼睑/高光的联动。

### 14.2 六系统的提示词映射

#### 双眼聚焦一致性（Vergence）

**提示词关键**：显式声明双眼聚焦于同一目标

| 场景 | 提示词写法 | 避免的写法 |
|------|-----------|-----------|
| 角色注视近处人物 | `perfect binocular convergence, both eyes locked on same focal target at close range, inward vergence` | `looking at someone`（太模糊，AI可能给两眼不同方向） |
| 角色凝视远方 | `parallel gaze into distance, both eyes aligned on far focal point, no convergence` | `staring into distance`（可能一只眼偏了） |
| 角色视线转移中 | `eyes mid-shift between targets, transient divergent moment` | `looking around`（两眼各看各的） |

**核心声明**：`perfect binocular convergence` — 这是AI最容易忽略也最致命的参数。不加这句，AI默认给两眼分配不同的注视方向。

#### 高光锚点一致（Catchlight Anchor）

**提示词关键**：高光方向与场景主光方向绑定

```
# 在场景锚定段中声明光源方向后，眼部高光自动锁定：
physically accurate catchlights in upper-left cornea consistent with key light direction
```

| AI常见错误 | 提示词修正 |
|-----------|-----------|
| 两眼高光方向不同 | `matching catchlights in both eyes, same position, same light source` |
| 出现多个高光 | `single clean catchlight per eye, no secondary reflections` |
| 高光与主光矛盾 | `catchlight position strictly consistent with [主光方向] key light` |

**金色法则**：高光方向 = 主光方向。这是物理事实，没有例外。如果AI给了矛盾的高光，在提示词中显式锁定。

#### 角膜折射深度（Corneal Refraction）

**提示词关键**：声明眼球的三维体积感，拒绝平面贴图

```
realistic corneal refraction, subtle tear film reflection, natural pupil depth, 
iris receded behind corneal dome, highlight floating on surface layer
```

**四个最易暴露区域的提示词修正**：

| 区域 | AI默认 | 提示词修正 |
|------|--------|-----------|
| 眼白（Sclera） | 纯白塑料 | `sclera with subtle blood vessel network, gradual warm-to-cool gradient, moist shadow at edges` |
| 瞳孔边缘 | 机械硬边 | `pupil edge with slight optical softness, natural feathered boundary, not mechanically sharp` |
| 虹膜纹理 | 贴图花纹 | `iris with radial fiber structure, depth layering, central heterochromia, natural organic texture` |
| 泪阜（内眼角） | 粉色贴片 | `caruncle with translucent moist tissue, visible micro-capillaries, wet inner canthus` |

#### 微型扫视（Microsaccades）

**静帧提示词**：不需要描述运动，但需要暗示"活"的张力
```
subtle microsaccadic tension, eyes alive with minute muscular activity
```

**视频提示词**：
```
subtle microsaccadic eye movement, focus micro-adjustments every 1-2 seconds, 
irregular micro-blinks, living human eyes
```

#### 瞳孔动态

**提示词关键**：瞳孔大小与情绪状态绑定

| 情绪 | 瞳孔提示词 | 视觉效果 |
|------|-----------|----------|
| 悲伤/隐忍 | `constricted pupils, gaze sinking downward, suppressed emotional weight` | 瞳孔偏小，眼神下垂 |
| 愤怒/决意 | `slightly dilated pupils, locked focus, raised upper eyelids, determined ocular tension` | 瞳孔轻扩张，聚焦锁死 |
| 恐惧/震惊 | `widely dilated pupils, raised upper eyelids showing sclera above iris, tense lower lids` | 瞳孔明显放大，露白 |
| 平静/日常 | `natural pupil size with subtle autonomic variation, calm steady gaze` | 正常大小，微弱呼吸变化 |
| 吸引/渴望 | `slightly dilated pupils, softened gaze, eyelids slightly lowered, warm focus` | 瞳孔微扩张，眼睑微垂 |

#### 眼睑与眼球联动

**提示词关键**：眼皮参与眼神表达

```
dynamic eyelid compression, upper lid following eye rotation, 
lower lid subtle tension shift, coordinated lid-eye movement
```

| 场景 | 眼睑提示词 |
|------|-----------|
| 凝视 | `upper lids slightly compressed, lower lids tightened, focused gaze weight` |
| 恐惧 | `upper lids retracted showing sclera above iris, lower lids taut` |
| 疲惫 | `heavy upper lids drooping, reduced lid aperture, tired gaze` |
| 诱惑 | `half-lidded gaze, upper lids lowered to cover upper iris, soft focus` |

### 14.3 影视级眼神提示词模板

**基础锚定段（每个角色眼神镜头的提示词都必须包含）**：

```
perfect binocular convergence, both eyes locked on same focal target, 
realistic corneal refraction, physically accurate catchlights, 
subtle tear film reflection, natural pupil depth, 
cinematic ocular tension, emotionally focused gaze, 
living human eyes, no dead-eye effect, alive eyes, conscious gaze
```

**按情绪状态扩展**：

```
# 悲伤/隐忍
[基础锚定段] + constricted pupils, gaze sinking, suppressed weight in eyes, 
eyelids heavy with unshed emotion, subtle moisture gathering at inner canthus

# 愤怒/决意
[基础锚定段] + slightly dilated pupils, locked predatory focus, 
raised upper eyelids exposing more iris, determined ocular tension, 
lower lids tightened with resolve

# 恐惧/震惊
[基础锚定段] + widely dilated pupils, upper eyelids retracted showing white above iris, 
eyes wide and hyper-alert, tension in lower lids, involuntary fixation

# 平静/温暖
[基础锚定段] + natural relaxed pupils, soft warm gaze, 
gentle lid position, calm ocular breathing

# 吸引/渴望
[基础锚定段] + slightly dilated pupils, softened focus with warm intention, 
half-lidded gaze, lids partially covering upper iris
```

### 14.4 眼神提示词与场景光源的关系

眼神的高光和折射效果直接受场景光源影响——提示词中的眼部描述必须与场景锚定段的光源体系一致：

| 场景光源 | 眼部提示词调整 |
|----------|--------------|
| 单侧主光（如左高冷蓝） | `catchlights positioned in upper-left cornea, cool blue key light reflected in eye surface` |
| 正面柔光 | `diffused catchlights across central cornea, soft frontal illumination in eye reflections` |
| 逆光/轮廓光 | `rim light creating subtle corneal edge glow, minimal catchlight, iris silhouetted` |
| 多光源 | `primary catchlight from [主光方向], secondary subtle reflection from [辅光方向], no more than two light sources reflected` |
| 烛光/火光 | `warm flickering catchlight, shifting amber reflection on corneal surface, fire-lit eye` |

**关键**：高光方向不一致是AI眼神"假"的第一大信号。分镜提示词中场景光源和眼部高光必须用同一段逻辑描述。

### 14.5 眼神跨镜头一致性

跨镜头眼神的提示词策略与眼泪一致——必须标注"进度"：

```
# 镜头A：角色初见目标
[基础锚定段] + eyes shifting to lock on new target, vergence adjusting from far to close focus, 
pupils slightly dilating with interest, catchlights sharp

# 镜头B：持续注视
[基础锚定段] + fully converged on target, steady focused gaze, 
pupils settled at attention level, catchlights stable

# 镜头C：视线移开
[基础锚定段] + eyes disengaging from target, vergence relaxing, 
gaze drifting, pupils normalizing, momentary unfocused transition
```

**核心**：眼神的"聚焦→锁定→移开"是连续过程，不能所有镜头都写`looking at target`——AI每次都从零生成，需要被告知角色处于注视过程的哪个阶段。

### 14.6 完整案例：三种情绪特写

**案例A — 悲伤克制**：
```
EXTREME REALISM cinematic close-up. ARRI Alexa Mini LF, 85mm prime, f/1.4, ultra-shallow depth of field.

[角色锚定]. [场景锚定].

Perfect binocular convergence on close-range target, both eyes locked with inward vergence. 
Constricted pupils, gaze sinking with emotional weight. 
Realistic corneal refraction — iris receded behind corneal dome, highlight floating on surface layer. 
Physically accurate catchlights in upper-left cornea consistent with key light direction. 
Subtle tear film reflection, moisture gathering at inner canthus but not yet overflowing. 
Upper eyelids heavy with suppressed grief, lower lids slightly tightened. 
Subtle microsaccadic tension in otherwise still eyes — alive but barely holding. 
Sclera with subtle blood vessel network, not plastic white. 
Iris with radial fiber structure and depth layering. 
Cinematic ocular tension — conscious gaze anchored in pain.

4K, 16:9. --ar 16:9 --v 7 --q 2
```

**案例B — 愤怒锁死**：
```
[风格+角色+场景锚定]

Perfect binocular convergence locked on adversary, predatory inward vergence. 
Slightly dilated pupils, focus absolute and unblinking. 
Raised upper eyelids exposing more iris — aggressive lid retraction. 
Lower lids tightened with resolve. 
Realistic corneal refraction, catchlights sharp and precise in upper-left. 
Iris fibers contracted and vivid, pupil edge with natural optical softness. 
Dynamic eyelid compression — lids pressed with intent, not relaxed. 
Cinematic ocular tension — conscious hostile gaze, target acquired, no hesitation. 
Sclera clear but with living texture. No dead-eye effect.

4K, 16:9. --ar 16:9 --v 7 --q 2
```

**案例C — 恐惧露白**：
```
[风格+角色+场景锚定]

Eyes wide with shock — upper eyelids fully retracted showing white sclera above iris. 
Widely dilated pupils, involuntary fixation on threat. 
Lower lids taut and strained. 
Perfect binocular convergence on approaching danger, extreme inward vergence. 
Realistic corneal refraction, catchlights sharp but trembling. 
Iris contracted thin around massively dilated pupil. 
Microsaccadic movement visible — rapid micro-shifts betraying panic. 
Sclera blood vessels more visible from lid retraction. 
Cinematic ocular tension — hyper-alert, fight-or-flight gaze, involuntary and raw.

4K, 16:9. --ar 16:9 --v 7 --q 2
```

### 14.7 提示词自查清单

写完眼神相关提示词后，逐项检查：

1. **双眼聚焦声明**：是否写了`binocular convergence`或`both eyes locked on same target`？
2. **高光与光源一致**：catchlight方向是否与场景主光方向匹配？
3. **角膜折射声明**：是否写了`corneal refraction`而非只写`detailed eyes`？
4. **四易暴露区覆盖**：眼白/瞳孔边缘/虹膜纹理/泪阜是否避免了AI默认错误？
5. **瞳孔与情绪匹配**：瞳孔大小是否与角色当前情绪状态一致？
6. **眼睑联动声明**：是否有眼睑参与的描述，而非"只有眼珠在动"？
7. **视觉目标明确**：角色在看什么？是否有`focused attention`或`conscious gaze`？
8. **意识导向描述**：提示词中"意识类"词汇（locked/conscious/alive）是否多于"纹理类"词汇（detailed/glossy/bright）？
9. **dead-eye排除**：是否显式声明了`no dead-eye effect`或`alive eyes`？
10. **跨镜头进度**：连续镜头中，眼神状态是否标注了"初见→持续→移开"的进度？

### 14.9 四易暴露区AI提示词修正

AI眼部最易穿帮的四个区域，即使8K分辨率也会暴露。必须在提示词中显式修正：

**眼白修正**：
```
# ❌ 默认输出：纯白塑料感
# ✅ 修正提示词：
subtle scleral veining, slight blue-white gradient from inner to outer canthus, 
moist shadow at inner canthus, translucent wetness along lower lid margin, 
NOT pure white plastic
```

**瞳孔边缘修正**：
```
# ❌ 默认输出：机械硬边
# ✅ 修正提示词：
pupil border with natural soft falloff at edge, not mechanically sharp, 
subtle gradient transition between pupil and iris, 
organic irregularity at pupil margin
```

**虹膜纹理修正**：
```
# ❌ 默认输出：贴图花纹/均匀圆形
# ✅ 修正提示词：
radial iris fibers with depth variation, 
central heterochromia (slightly different tone near pupil), 
layered iris structure with crypts and collarette, 
not flat texture map, not perfectly circular fibers
```

**泪阜修正**：
```
# ❌ 默认默认输出：粉色贴片
# ✅ 修正提示词：
translucent lacrimal caruncle with micro-capillaries visible, 
moist inner canthus with subtle wet reflection, 
flesh-toned semi-transparent tissue, not flat pink patch
```

### 14.10 情绪→眼部状态提示词速查表

| 情绪 | 聚焦提示词 | 瞳孔提示词 | 眼睑提示词 | 扫视提示词 |
|------|-----------|-----------|-----------|-----------|
| 悲伤 | `slow unfocused gaze, eyes dropping downward` | `constricted pupils, muted response` | `drooping upper lids, reduced blink rate` | `slow irregular microsaccades, unfocused drift` |
| 愤怒 | `locked stare, target-focused convergence` | `slightly dilated pupils, threat response` | `raised upper lids exposing more iris, tightened lower lids` | `high-frequency locked microsaccades, target tracking` |
| 恐惧 | `jumping focus, unable to settle on target` | `dilated pupils, fear response` | `wide upper lid exposure (scleral show), tense lower lids` | `rapid unstable microsaccades, scanning pattern` |
| 渴望 | `steady gaze anchored on target, soft convergence` | `slightly dilated pupils, warmth` | `half-lowered upper lids, sustained focus without blinking` | `low-frequency tracking microsaccades, target-locked` |
| 恍惚 | `no clear focal target, divergent gaze` | `normal or slightly constricted` | `half-closed, not participating` | `extremely slow, no correction, unfocused` |
| 冷漠 | `converged but emotionally detached` | `no emotional dilation, flat response` | `completely relaxed, neutral tension` | `minimal, mechanical, no emotional urgency` |

### 14.11 意识导向vs纹理导向提示词策略

**核心发现**：AI提示词中"看什么"比"眼睛长什么样"重要100倍。一个低清真人眼神通常比超高清AI假眼更真实。

**纹理导向提示词（❌无效或效果弱）**：
```
ultra detailed eyes, glossy eyes, 8K iris texture, hyper-detailed cornea, 
bright sparkling eyes, crystal clear eyes, perfect eye rendering
```
结果：画了漂亮的假眼——高清但空洞，像玻璃珠。

**意识导向提示词（✅有效）**：
```
locked gaze, focused attention, converged eyes, 
emotionally anchored eye focus, conscious gaze, 
subtle microsaccadic tension, cinematically alive eyes
```
结果：有目标有灵魂的真实眼睛——即使细节不够完美，观众也会觉得"活的"。

**最优策略=意识层+光学层+微动画层+纹理修正层**：
```
# 1. 意识层（最高优先级——决定"活不活"）
[VICTOR] with locked gaze on [her face], 
cold evaluation attention — active predatory focus pattern,
both eyes converged on same focal target at 2 meter distance,

# 2. 光学层（决定"真不真"）
perfect binocular convergence, 
realistic corneal refraction, 
physically accurate catchlights from upper-left key light,
subtle tear film reflection, 
natural pupil depth with cold evaluation dilation,

# 3. 微动画层（视频必须——决定"动不动"）
cinematic ocular tension,
microsaccadic eye movement every 1-2 seconds,
dynamic eyelid compression following micro-eye shifts,
natural irregular blink pattern at 3-second intervals,

# 4. 纹理修正层（决定"细不细"）
radial iris fibers with depth variation and central heterochromia,
subtle scleral veining with blue-white gradient,
translucent lacrimal caruncle with micro-capillaries,
pupil border with natural soft falloff,

# 5. 负声明（防止AI回退到默认假眼）
no dead-eye effect, no glass-eye appearance, no flat iris texture,
no plastic sclera, no mechanical pupil edge, no cartoon eye highlight
```

### 14.12 视频生成中眼部4层微动画提示词

**微动画层1——微型扫视（Microsaccades）**：
```
subtle microsaccadic eye movement, 
micro-focus correction every 1-2 seconds, 
less than 1 degree of angular shift, 
imperceptible to conscious viewer but maintaining living quality
```

**微动画层2——瞳孔呼吸**：
```
pupil with natural breathing rhythm, 
subtle dilation-constriction cycle over 3-5 seconds, 
±0.5mm variation, 
organic pulse responding to emotional and light conditions
```

**微动画层3——不规则眨眼**：
```
natural irregular blink pattern, 
2-4 second intervals between blinks, 
non-mechanical timing — some intervals 2 seconds, some 3.5, some 4, 
complete blink cycle with eyelid meeting and separating
```

**微动画层4——眼睑跟随**：
```
eyelid compression following eye rotation, 
dynamic upper lid tension adjusting with gaze direction, 
lower lid slight tension during downward gaze, 
eyelids as active participants not static frames
```

**4层缺一的后果对照**：
- 缺微扫视→眼睛像被冻住的蜡像
- 缺瞳孔呼吸→缺少"活物"的自主神经信号
- 缺不规则眨眼→像不眨眼的恐怖片人偶
- 缺眼睑跟随→像贴图在移动，"假眼珠"感
- 4层齐全→真人级别的活感

### 14.13 视觉聚焦逻辑提示词自查清单（增强版）

1. **意识层优先**：提示词是否先声明"看什么""为什么看"（意识层），再写"长什么样"（纹理层）？
2. **双眼聚焦一致**：是否写了`both eyes converged on same focal target`？
3. **高光锚点一致**：是否写了`catchlights from [光源方向]`？
4. **角膜折射声明**：是否写了`corneal refraction`而非只写`detailed eyes`？
5. **四易暴露区覆盖**：眼白/瞳孔边缘/虹膜纹理/泪阜是否各有修正声明？
6. **情绪→瞳孔匹配**：瞳孔大小是否与角色当前情绪状态一致（悲伤=微缩，愤怒=轻扩张）？
7. **情绪→扫视匹配**：扫视频率是否与情绪匹配（愤怒=高频锁定，恍惚=极慢不修正）？
8. **眼睑联动声明**：是否有眼睑参与的描述，而非"只有眼珠在动"？
9. **视觉目标明确**：角色在看什么？是否有`focused attention`或`conscious gaze`？
10. **意识导向>纹理导向**：意识类词汇（locked/conscious/alive/anchored）是否多于纹理类词汇（detailed/glossy/bright）？
11. **微动画层（视频）**：4层微动画是否齐全（扫视+瞳孔呼吸+眨眼+眼睑跟随）？
12. **dead-eye排除**：是否显式声明了`no dead-eye effect`或`alive eyes`？
13. **跨镜头聚焦逻辑**：连续镜头中，眼神状态是否标注了递进/变化？

## 十五、多镜头视频序列AI提示词模板

### 15.1 静态图像 vs 视频序列的提示词差异

| 维度 | 静态图像提示词 | 视频序列提示词 |
|------|--------------|--------------|
| 时间 | 单帧，无时间维度 | 有时间线，需要描述变化过程 |
| 情绪 | 单一情绪状态 | 情绪弧线（开始→过渡→着陆） |
| 肌肉控制 | "悲伤表情" | `(depressor anguli oris:1.45)` + `(platysma neck tension:1.5)` |
| 眼泪 | "哭了" | `first tear forming → slow gravitational roll → second tear follows → multiple trails` |
| 动作 | 无 | 小动作层+微反应层+自然惯性 |
| 运镜 | "推镜" | `slow dolly-in push at 0.4m/s, camera organically breathing closer` |
| 镜头关系 | 独立 | CUT标记+情绪着陆点连接 |

### 15.2 多镜头视频序列提示词结构

```
[Global Motion Style — 全局声明，锁定制式/风格/质感/一致性/运镜]

• Shot 1 ([焦距] [景别]): [运镜], [景深], [主表演—解剖学肌肉+权重], [小动作+惯性], [潜意识微反应], [情绪着陆: xxx]; [光影], [氛围]

• CUT;

• Shot 2 ([焦距] [景别]): [运镜], [景深], [主表演—从上一镜头的情绪着陆开始], [小动作+惯性], [潜意识微反应], [情绪着陆: xxx]; [光影], [氛围]

• CUT;

... (按需增加镜头)

• Shot N ([焦距] [景别]): [运镜], [景深], [主表演], [小动作+惯性], [潜意识微反应], [情绪着陆: xxx]; [光影], [氛围]
```

### 15.3 Global Motion Style 全局声明模板

```
create a [情绪类型] [景别] sequence of [角色名] transitioning from [起始情绪] to [结束情绪], 
ultra-realistic portrait photography, straight out of camera, large aperture shallow depth of field, 
natural soft ambient lighting with gentle chiaroscuro, 
real skin texture with visible pores and subtle natural imperfections, 
translucent natural skin tone without fake whiteness, 
naturally asymmetric facial features, relaxed and lively natural expressions with no stiffness, 
slight film grain, 8K ultra sharp, zero AI modeling traces, highly lifelike and organic.
Strictly using all previous [角色名] reference images for exact facial consistency, 
skin texture, eye shape and performance style lock.
Incorporate cinematic prompt principles: 
subtle micro-expressions with naturally focused eyes and natural blinking (no empty lifeless gaze), 
visible skin pores and fine lines with natural rosy moist uneven skin tone, 
strong atmospheric feel with light-shadow particles, dust noise and film grain, 
dynamic lighting with top light, rim/hair light and side light creating clear chiaroscuro contrast, 
realistic actions with natural inertia, 
foreground blurred occluders, sharp midground character, soft blurred background.
(subtle performance:1.35), (highly refined real tear physics:1.55), 
(detailed facial muscle micro-expressions:1.45), (specific eye muscle dynamics:1.55), 
(lighting refraction on wet skin:1.55), (platysma neck tension:1.5),
[运镜风格声明], 
cinematic 24fps motion with film-like motion cadence, 
natural motion blur on eyelashes and falling tears, 
theatrical presentation feel, professional cinema standard, no soap opera effect.
```

### 15.4 单镜头三层次写法模板

```
• Shot [N] ([焦距] [景别]): [运镜描述], [景深],
[主表演]:
(解剖学肌肉1:权重) [效果描述],
(解剖学肌肉2:权重) [效果描述],
naturally focused lively eyes with subtle micro-expressions and natural blink,
[眼泪/汗水/其他生理状态—如适用];
[小动作层]: subtle fingers [具体动作] with natural inertia,
[潜意识微反应]: [快速微眨/脸颊泛红/肩膀微颤/喉结滚动],
emotional landing: [情绪着陆点];
[光影]: [主光+辅光+轮廓光描述],
[氛围]: [前景遮挡+中景锐利+背景虚化+粒子/噪点]
```

### 15.5 完整案例：金水仙微笑到无声落泪（5镜头）

**Global Motion Style**：
```
create a slow emotional close-up sequence of Jin Shuixian (Golden Daffodil) transitioning from a radiant smile to silent tears, ultra-realistic portrait photography, straight out of camera, large aperture shallow depth of field, natural soft ambient lighting with gentle chiaroscuro, real skin texture with visible pores and subtle natural imperfections, translucent natural skin tone without fake whiteness, naturally asymmetric facial features, relaxed and lively natural expressions with no stiffness, slight film grain, 8K ultra sharp, zero AI modeling traces, highly lifelike and organic. Strictly using all previous Jin Shuixian reference images + the two new real-tear reference images for exact facial consistency, skin texture, eye shape, tear behavior and performance style lock. Incorporate cinematic prompt principles: subtle micro-expressions with naturally focused eyes and natural blinking (no empty lifeless gaze), visible skin pores and fine lines with natural rosy moist uneven skin tone, strong atmospheric feel with light-shadow particles, dust noise and film grain, dynamic lighting with top light, rim/hair light and side light creating clear chiaroscuro contrast, realistic actions with natural inertia, foreground blurred occluders, sharp midground character, soft blurred background. (subtle performance:1.35), (highly refined real tear physics:1.55), (detailed facial muscle micro-expressions:1.45), (specific eye muscle dynamics:1.55), (lighting refraction on wet skin:1.55), (platysma neck tension:1.5), intimate facial performance with authentic micro-expressions, slow continuous dolly-in push at 0.4m/s, wearing deep emerald green cheongsam with soft pearl necklace catching light, warm golden lantern light mixed with gentle volumetric smoke, cinematic 24fps motion with film-like motion cadence, natural motion blur on eyelashes and falling tears, theatrical presentation feel, professional cinema standard, no soap opera effect. Shaky handheld camera style with organic breathing movement and subtle searching adjustments throughout, maintaining raw intimate proximity:
```

**Shot 1 (85mm Close-Up Smile)**：
```
85mm close-up on her face at eye level, soft handheld with gentle breathing sway, large aperture shallow DOF, straight-out-of-camera realism, starting on her warm genuine smile — (zygomaticus major lift:1.35) corners of mouth curving upward with natural cheek raise, (orbicularis oculi engagement:1.45) creating authentic crow's feet and sparkling eye crinkle, naturally focused lively eyes with subtle micro-expressions and natural blink, soft natural rim/hair light + side light creating gentle chiaroscuro on real skin with visible pores, fine lines and subtle natural imperfections, translucent skin tone; small ongoing action: subtle fingers tracing pearl necklace with natural inertia, subconscious micro-reaction: tiny eye sparkle + cheek flush, emotional landing: radiant yet fragile joy, perfect multi-reference match with slight film grain and dust particles;
```

**Shot 2 (85mm Slow Push Transition)**：
```
85mm continuing slow dolly-in push at 0.4m/s, camera organically breathing closer, shallow depth of field, while her smile gradually falters — (slow zygomaticus release:1.4), (corrugator supercilii micro-activation:1.4) faint brow tension, (orbicularis oculi partial relaxation with upper lid micro-tremor:1.55) and natural blinks, eyes begin to glisten with real tear meniscus buildup at lower lash line; lower lip trembles; (first tear forming naturally with highly refined real tear physics:1.55): viscous droplet swelling and slow release exactly as in real-tear references; dynamic soft natural top + side light with hair light creating moving highlights and deep shadows on real skin texture; small ongoing action: fingers tightening slightly with inertia, subconscious micro-reaction: rapid micro-blink + throat swallow, emotional landing: joy cracking into unease;
```

**Shot 3 (100mm Intimate Extreme Close)**：
```
100mm extreme close-up detail during the push, intimate handheld proximity with micro-shake, large aperture ultra shallow DOF, focusing on her eyes as the smile completely dissolves into sorrow — (full orbicularis oculi relaxation + nasolabial fold deepening:1.45), (specific eye muscle dynamics:1.55) levator palpebrae slight droop, natural rapid micro-blinks interrupting tear flow, lacrimal activation with visible tear pooling at punctum; single tear breaks free with precise real tear physics: slow gravitational roll with natural wobble, droplet deformation and viscous flow exactly matching references; (lighting refraction on wet skin:1.55) bright golden specular highlights, dynamic caustics and light bending through tears on real skin with pores and subtle imperfections; subtle mentalis chin quiver and (platysma neck tension:1.5) visible neck bands; foreground soft blurred pearl or smoke occluder, sharp lifelike face, blurred luxurious background, rich film grain and atmospheric dust;
```

**Shot 4 (85mm Tight Portrait Push)**：
```
85mm tight portrait continuing the slow forward push, camera weaving with organic breathing energy, shallow DOF, capturing the full emotional arc as (second tear follows the first with refined real tear physics:1.55) — natural asymmetric merging, realistic viscosity and believable human-speed flow; (depressor anguli oris pulling mouth corners downward:1.45) with strong (platysma neck tension:1.5), (lighting refraction on wet skin:1.55) multiple refractive glints and wet sheen on pores and fine lines; small ongoing action: unconscious grip with natural fabric inertia, subconscious micro-reaction: shoulder micro-tremble, emotional landing: quiet heartbreak, soft volumetric smoke adding melancholy depth with particles and noise;
```

**Shot 5 (50mm Final Emotional Reveal)**：
```
50mm medium-close slow push finale with slight low-angle tilt, shallow depth of field, pulling back just enough to frame her tear-streaked face against real blurred luxurious background, ending on a lingering sorrowful gaze with (multiple natural tear trails glistening under golden light:1.5), complex (lighting refraction on wet skin:1.55) — caustics, specular bloom and light dispersion on real wet skin exactly like the references; full micro-expression cascade with naturally focused lively eyes and natural blinks, pronounced platysma tension, residual zygomatic twitch; foreground blurred occluders, sharp emotional face with lifelike skin details, soft bokeh background, rich atmospheric film grain, dust noise and soft natural lighting throughout, (subtle performance:1.35) strong multi-image character lock, ultra-realistic straight-out-of-camera portrait quality, 8K, no AI artifacts.
```

### 15.6 解剖学肌肉控制速查表

**微笑相关**：
| 肌肉 | 英文 | 权重标注 | 视觉效果 |
|------|------|---------|----------|
| 颧大肌 | Zygomaticus major | `(zygomaticus major lift:1.35)` | 嘴角上扬+脸颊隆起 |
| 颧小肌 | Zygomaticus minor | `(zygomaticus minor:1.2)` | 上唇微提+鼻翼侧拉伸 |
| 眼轮匝肌 | Orbicularis oculi | `(orbicularis oculi engagement:1.45)` | 真笑鱼尾纹+眼角挤压 |

**悲伤相关**：
| 肌肉 | 英文 | 权重标注 | 视觉效果 |
|------|------|---------|----------|
| 皱眉肌 | Corrugator supercilii | `(corrugator supercilii micro-activation:1.4)` | 眉间竖纹+眉头下压 |
| 口角降肌 | Depressor anguli oris | `(depressor anguli oris:1.45)` | 嘴角下拉+悲伤轮廓 |
| 颈阔肌 | Platysma | `(platysma neck tension:1.5)` | 颈带可见+颈部绷紧 |
| 颏肌 | Mentalis | `(mentalis chin quiver:1.45)` | 下巴微颤+下唇前突 |

**恐惧/惊讶相关**：
| 肌肉 | 英文 | 权重标注 | 视觉效果 |
|------|------|---------|----------|
| 额肌 | Frontalis | `(frontalis activation:1.4)` | 额纹+眉毛整体上提 |
| 上睑提肌 | Levator palpebrae | `(levator palpebrae:1.55)` | 上睑抬升+露白 |

**过渡/混合状态**：
| 肌肉 | 英文 | 权重标注 | 视觉效果 |
|------|------|---------|----------|
| 颧大肌释放 | Slow zygomaticus release | `(slow zygomaticus release:1.4)` | 微笑消退+嘴角回落 |
| 眼轮匝肌部分放松 | Orbicularis oculi partial relaxation | `(orbicularis oculi partial relaxation with upper lid micro-tremor:1.55)` | 眼轮松开+上睑颤动 |
| 提上睑肌微垂 | Levator palpebrae slight droop | `(levator palpebrae slight droop:1.55)` | 上睑下垂+疲惫 |
| 鼻唇沟加深 | Nasolabial fold deepening | `(nasolabial fold deepening:1.45)` | 法令纹加深+衰老/悲伤 |

### 15.7 情绪弧线设计模板

多镜头视频序列的核心是情绪弧线——不是5个独立的"表情"，而是一条连续的情绪变化曲线：

**从微笑到落泪（5镜头标准弧线）**：
```
Shot 1: radiant yet fragile joy          ← 起点：笑容中有隐约脆弱
Shot 2: joy cracking into unease          ← 第一次裂痕：笑意动摇
Shot 3: sorrow breaking through           ← 突破口：悲伤不可抑制
Shot 4: quiet heartbreak                  ← 沉淀：安静的崩溃
Shot 5: lingering sorrow                  ← 余韵：绵延的哀伤
```

**从平静到愤怒（5镜头标准弧线）**：
```
Shot 1: calm composure with underlying tension
Shot 2: restrained anger surfacing — jaw clenching, micro-frown
Shot 3: anger erupting — (frontalis:1.4) brow lowering, (levator palpebrae:1.55) eyes widening
Shot 4: controlled fury — locked gaze, dilated pupils, rigid jaw
Shot 5: cold aftermath — residual tension, unblinking stare
```

**从恐惧到释然（5镜头标准弧线）**：
```
Shot 1: frozen fear — wide eyes, retracted lids, pale face
Shot 2: escalating panic — rapid breathing, trembling
Shot 3: breaking point — tears of fear, hyperventilating
Shot 4: gradual calming — breath slowing, shoulders dropping
Shot 5: exhausted relief — residual tremble, weary eyes, deep exhale
```

### 15.8 面瘫美学（Deadpan Aesthetics）提示词技巧

#### 15.8.1 面瘫不是"没写"，是"写了不许有"

AI生成器默认给角色添加表情——即使提示词不提情绪，AI也会"好心"地给一个中性微笑或轻微皱眉。面瘫美学的提示词必须**显式禁止**这些默认行为。

**面瘫提示词的核心原则**：用"禁止声明"替代"描述声明"——不告诉AI"做什么表情"，告诉AI"不许做什么表情"。

**面瘫基础锚定段**：
```
deliberately neutral expression, flat affect maintained throughout, 
no emotional engagement, no smiling, no frowning, no brow tension, 
facial muscles at complete resting state with minimal tonal variation,
conscious but detached gaze — eyes tracking without emotional investment, 
present but unengaged, binocular convergence on target with flat ocular tension,
subconscious micro-blinks only, no deliberate expression change,
brow completely relaxed, lips sealed at natural resting position,
jaw unclenched, neck relaxed — zero tension signals,
no micro-reactions, no emotional leakage whatsoever
```

#### 15.8.2 面瘫眼神 vs Dead-Eye 的区别

面瘫眼神最容易和AI的dead-eye问题混淆，但它们完全不同：

| 维度 | Dead-Eye（AI缺陷） | 面瘫眼神（创作选择） |
|------|-------------------|---------------------|
| 双眼聚焦 | 不一致/漂浮 | 一致但抽离——`binocular convergence on target with flat ocular tension` |
| 高光 | 缺失/矛盾 | 正常存在——活人不反应，不是死人 |
| 瞳孔 | 固定无变化 | 随光线正常响应，但不随情绪变化 |
| 眼睑 | 不参与/僵死 | 完全放松——无紧张但不是僵硬 |
| 微扫视 | 完全缺失 | 存在但极微——`subconscious micro-blinks only` |
| 本质 | 技术缺陷 | 美学选择 |

**关键**：面瘫眼神的提示词必须同时声明`conscious gaze`（它是活的）和`detached`（它不参与），缺一不可。只有`detached`没有`conscious`=dead-eye；只有`conscious`没有`detached`=正常情绪聚焦。

#### 15.8.3 面瘫构图提示词

```
perfectly symmetrical composition, centered subject, flat planar staging, 
Wes Anderson style framing, no foreground occlusion, no diagonal lines, 
geometric precision, visual order, muted color palette, desaturated tones, 
[具体色调方向如pale pink and mint / cold blue-gray / faded yellow],
uniform lighting with minimal chiaroscuro — shadows exist but are gentle,
no dramatic contrast, no rim light, no volumetric atmosphere,
flat even illumination, clinical precision
```

**韦斯·安德森风格全流程提示词**：
```
Wes Anderson style, perfect symmetrical composition, centered character in deadpan neutral expression, flat affect, no emotional engagement, deliberate stillness, pastel color palette with desaturated warm tones, overhead straight-on framing, geometric precision in set design, every object precisely placed, shallow depth of field with sharp subject and blurred symmetric background, no handheld — fixed camera or slow lateral track only, cinematic 24fps, no motion blur, crisp and controlled, absurdist formalism
```

**兰斯莫斯风格全流程提示词**：
```
Yorgos Lanthimos style, character in mechanical deadpan delivery, stiff minimal body language, flat affect maintained throughout, no emotional leakage, cold desaturated color palette, wide-angle lens creating spatial unease, characters placed at uncomfortable distances, harsh even lighting with clinical coldness, no warmth in illumination, fixed camera or very slow push, absurdist domestic horror, emotional detachment as narrative device
```

**考里斯马基风格全流程提示词**：
```
Aki Kaurismäki style, deadpan expression at its most stoic, face completely neutral despite extreme circumstance, flat affect with dignity, muted desaturated cold palette, minimal dialogue staging, characters framed with geometric simplicity, flat even lighting, no dramatic shadows, fixed camera, no camera movement, rock-steady framing, laconic visual storytelling, deadpan humor through absence of expected reaction
```

#### 15.8.4 面瘫视频序列的特殊规则

面瘫美学的多镜头视频序列与微表情序列有根本区别：

| 序列元素 | 微表情序列 | 面瘫序列 |
|----------|-----------|---------|
| Global Motion Style | 声明情绪类型+弧线 | 声明deadpan+flat affect+禁止情绪 |
| 每镜头标注 | 解剖学肌肉+权重 | `flat affect maintained` + 禁止项 |
| 情绪着陆点 | 明确情绪状态 | `flat affect maintained throughout`——无着陆点 |
| 小动作层 | 带情绪惯性 | 存在但不带情绪色彩——`mechanical gesture without affect` |
| 微反应层 | 必须有 | **必须禁用**——微反应是情绪泄露 |
| 眼泪物理 | 精确时间线 | 不适用——面瘫角色不哭 |
| 运镜 | 情绪驱动 | 事件驱动/不驱动——摄影机也不"反应" |
| CUT节奏 | 情绪弧线驱动 | 事件逻辑驱动——"这件事发生了，切" |

**面瘫序列的Global Motion Style模板**：
```
create a deadpan sequence of [角色名] maintaining complete emotional neutrality throughout [事件描述], deliberately neutral expression, flat affect, no emotional engagement whatsoever, no smiling, no frowning, no brow tension, conscious but detached gaze, present but unengaged, ultra-realistic portrait photography, straight out of camera, [焦距]mm, [构图规则: perfectly symmetrical / centered / geometric], muted desaturated [色调] palette, flat even lighting with minimal chiaroscuro, no dramatic contrast, no volumetric atmosphere, fixed camera / slow lateral track, no handheld, no camera breathing, no emotional camera movement, cinematic 24fps, absurdist formalism, deadpan humor through absence of expected reaction, zero AI modeling traces
```

#### 15.8.5 面瘫美学的三层次结构变体

| 层次 | 微表情序列 | 面瘫序列 |
|------|-----------|---------|
| 主表演 | 肌肉变化+情绪转换 | **事件发生但角色不反应**——荒诞/事件是主表演 |
| 小动作 | 带情绪惯性的潜意识动作 | **机械化/仪式化动作**——动作存在但无情绪色彩（如机械地搅拌咖啡、整齐地排列物品） |
| 微反应 | 不受控的生理反应 | **禁用**——微反应是情绪泄露，面瘫角色不泄露。唯一允许：自然光线引起的瞳孔微调和生理性眨眼 |

#### 15.8.6 面瘫美学的自检清单

1. **表情纯度**：角色是否始终维持flat affect？有无意外"泄露"的情绪微表情？
2. **眼神区分**：面瘫眼神是否与dead-eye区分开？是否有`conscious but detached gaze`声明？
3. **构图一致性**：是否全程保持对称/居中/平面化？有无意外打破对称的元素？
4. **色调纯度**：低饱和度是否贯穿全程？有无情绪色调"混入"？
5. **运镜克制**：摄影机是否也"面瘫"？有无意外手持晃动或情绪性推拉？
6. **微反应禁用**：是否排除了所有情绪性微反应？生理性眨眼和光线瞳孔调整是唯一允许项
7. **荒诞可见**：面瘫的幽默来自"事件荒诞+角色不反应"——事件本身是否足够荒诞？
8. **距离感**：是否保持了35-50mm的观察距离？有没有意外用了85-100mm亲密特写？
9. **前景遮挡**：是否避免了前景遮挡？（面瘫不需要窥视感，需要坦然的正面展示）
10. **切镜逻辑**：切镜是否由事件驱动而非情绪驱动？每个CUT是否对应"这件事发生了"而非"角色感受到什么"？

### 15.9 视频序列提示词自查清单

1. **Global Motion Style 完整性**：是否包含风格基调+皮肤真实感+多参考图锁+影视级原则块+运镜+帧率？
2. **解剖学肌肉权重**：是否用肌肉名+权重替代了笼统的"悲伤""微笑"？
3. **三层次结构**：每个镜头是否有主表演+小动作+微反应？
4. **情绪着陆点**：每个镜头是否有明确的情绪着陆？连续镜头着陆点是否构成弧线？
5. **焦距节奏**：焦距变化是否有节奏逻辑（建立→推进→极亲密→回落→呼吸）？
6. **CUT标记**：镜头间是否有明确的CUT分割？
7. **眼泪物理进度**：跨镜头眼泪是否遵循"无→蓄积→第一滴→第二滴→多泪痕"的进度？
8. **运镜连续性**：跨镜头运镜是否有延续声明（如`camera organically breathing closer`）？
9. **自然惯性**：小动作是否有`natural inertia`声明？
10. **zero AI traces**：是否声明了`zero AI modeling traces`和`no soap opera effect`？

写完眼神相关提示词后，逐项检查：

1. **双眼聚焦声明**：是否写了`binocular convergence`或`both eyes locked on same target`？
2. **高光与光源一致**：catchlight方向是否与场景主光方向匹配？
3. **角膜折射声明**：是否写了`corneal refraction`而非只写`detailed eyes`？
4. **四易暴露区覆盖**：眼白/瞳孔边缘/虹膜纹理/泪阜是否避免了AI默认错误？
5. **瞳孔与情绪匹配**：瞳孔大小是否与角色当前情绪状态一致？
6. **眼睑联动声明**：是否有眼睑参与的描述，而非"只有眼珠在动"？
7. **视觉目标明确**：角色在看什么？是否有`focused attention`或`conscious gaze`？
8. **意识导向描述**：提示词中"意识类"词汇（locked/conscious/alive）是否多于"纹理类"词汇（detailed/glossy/bright）？
9. **dead-eye排除**：是否显式声明了`no dead-eye effect`或`alive eyes`？
10. **跨镜头进度**：连续镜头中，眼神状态是否标注了"初见→持续→移开"的进度？

### 12.6 身份板案例：KAIRO（走廊打斗主角）

基于九宫格图中的黑发男子生成的身份板，ID块内容：

```
名称：KAIRO
角色：PROTAGONIST
核心情绪：CONTROLLED TENSION
视觉标志：DARK GREEN UTILITY JACKET + BLACK SHORT HAIR
```

身份板图像：[character-id-board.jpg](computer://imgs/260527_11_生图/character-id-board.jpg)

对应的锚点表核心字段 → 提示词锚定段映射：

| 锚点表字段 | 身份板对应 | 提示词锚定段写法 |
|-----------|-----------|----------------|
| 体型：中等偏瘦精悍 | 英雄全身图的体型 | lean and wiry with squared shoulders |
| 发色：黑色短发 | 面部/发型细节研究 | black short hair, sharp edges |
| 服饰：深绿工装外套+深色内搭 | 服装细节研究+英雄图 | dark green utility jacket over dark crew-neck shirt |
| 标志性道具：黑色手机 | 英雄图中手持 | black phone in hand |
| 体态：紧绷专注 | 表情研究+各姿态 | expression taut and focused |
| 色彩标签：深绿/黑+冷白 | ID块视觉标志 | deep green + black |
| 一致性红线：黑发+深绿外套+紧绷表情 | 所有视角必须满足 | STRICT consistency across ALL views |

## 十六、多人物场面调度AI提示词技巧

### 16.1 为什么多人场景的提示词与单人完全不同

单人场景的提示词核心是"锚定角色+场景，替换动作"。多人场景则完全不同——AI处理多人时的最大问题不是"画不好一个人"，而是"不理解人在空间中的关系"。扩散模型没有三维空间概念，每次生成都在"猜测"画面，多人场景中这种猜测会导致：左右互换、前后错乱、人物融合、越轴、串脸。

因此多人提示词的核心策略不是"描述更好"，而是**"控制空间"**——先让AI理解空间结构，再往空间里放人。

### 16.2 工业级多人Prompt结构模板

多人场景的提示词必须严格按以下顺序组织——顺序本身就是控制手段，AI对先出现的描述给予更高注意力：

```
[1. CAMERA — 锁定摄影机]
[焦距]mm lens, [高度] level, [运动方式] shot, camera facing [方向]

[2. SPACE — 锁定空间]
[空间类型+核心元素], [负空间声明], [氛围元素]

[3. BLOCKING — 锁定人物位置]
Primary subject: [角色标签+屏幕位置]
Secondary subject: [角色标签+屏幕位置]
Background extras: [角色标签+屏幕位置]

[4. RELATIONSHIP — 锁定人物关系]
[距离], [视线关系], [张力类型]

[5. LIGHTING — 锁定光影]
[主光方向+色温+光质], [辅光], [氛围光]
```

**完整示例——庙堂对峙**：
```
EXTREME REALISM cinematic shot. ARRI Alexa Mini LF, 35mm prime, f/2.8, medium depth of field.

CAMERA: 35mm lens eye level static shot camera facing east.

SPACE: large temple hall with towering stone columns, snow blowing through open doorway, empty center composition, cold incense smoke drifting low.

BLOCKING: 
Primary subject: scar-faced commander screen left foreground — black armor with gold trim, battle-worn face with diagonal scar across left cheek, arms crossed, imposing stance.
Secondary subject: silver-haired monk screen right midground — white silk robes, shaved head with silver stubble, prayer beads in hands, calm centered posture.
Background extras: two blurred armored guards background doorway, silhouettes.

RELATIONSHIP: 5 meter distance, eye-line match across the hall, tense standoff energy, visual tension.

LIGHTING: cold moonlight from camera-right high window (6500-7000K), warm candlelight from camera-left altar (3000K), chiaroscuro contrast between the two figures.

4K, 16:9. --ar 16:9 --v 7 --q 2
```

### 16.3 Screen Position词汇速查表

| 中文含义 | 推荐英文写法 | 避免的写法 |
|----------|------------|-----------|
| 画面左侧 | `screen left` | `left side`（歧义：谁左边？） |
| 画面右侧 | `screen right` | `right side` |
| 画面中央 | `center frame` | `middle`（太模糊） |
| 画面边缘 | `frame edge` | `side` |
| 前景 | `foreground` | `front` |
| 中景层 | `midground` | `middle ground`（可以但不够标准） |
| 背景 | `background` | `back` |
| 深背景 | `deep background` | `far back` |
| 高位 | `elevated position` / `higher staircase` | `up` |
| 低位 | `lower platform` / `seated lower frame` | `down` |

**关键原则**：AI对绝对坐标（screen left/right, foreground/background）的理解远好于相对描述（beside him, next to her, on the left side of another character）。多人场景中一律使用绝对坐标。

### 16.4 角色标签化提示词写法

多人场景中，角色不能用泛称（man/woman/boy/girl），必须用视觉特征标签组合——标签越具体，AI越不容易串脸：

| 泛称（❌ 避免） | 标签化（✅ 推荐） | 标签构成公式 |
|----------------|------------------|-------------|
| man | `scar-faced commander in black armor` | 标志性特征 + 身份 + 核心服饰 |
| woman | `silver-haired queen in white silk` | 发色/发型 + 身份 + 核心服饰 |
| old man | `white-robed monk with prayer beads` | 核心服饰 + 身份 + 标志性道具 |
| soldier | `red-armored guard with halberd` | 颜色+服饰 + 身份 + 武器 |
| girl | `blind swordswoman in dark green` | 标志性特征 + 身份 + 核心色彩 |

**标签化原则**：
1. 每个角色的标签必须包含**至少一个独特视觉特征**——如果两个角色都是"armed man"，AI会串脸
2. 标签中的颜色词是最强的区分手段——`red-armored` vs `blue-robed` 比任何面部描述都有效
3. 跨镜头标签**逐字重复**——与锚定段逻辑一致，AI通过重复识别"这是同一个人"

### 16.5 主角色优先级提示词写法

AI的注意力机制会优先强化最先描述的角色。利用这个特性，通过层级声明控制画面重心：

```
# 三人场景
Primary subject: wounded swordsman screen left foreground — [完整标签+锚点描述]
Secondary subject: female assassin screen right midground — [完整标签+锚点描述]  
Background extras: two blurred guards deep background doorway — [简短描述即可]
```

**层级与描述详略的关系**：
- Primary subject：最详尽的锚点描述（体型+服饰+道具+体态+色彩标签），约占提示词40%
- Secondary subject：适度锚点描述（核心服饰+标志性特征），约占25%
- Background extras：极简描述（颜色+类型+模糊声明），约占10%
- 其余25%给空间+光影+氛围

**不要在Background extras上浪费描述预算**——他们的功能是"占位"，不是"表演"。过度描述背景角色会分散AI对主角色的注意力。

### 16.6 负空间与人物分离提示词

多人场景最容易出现的AI灾难是**人物融合**——两个角色的身体部位混在一起，变成一个四臂怪物。负空间是核心防御：

```
# 基础负空间声明
large negative space between characters, clear visual separation, no overlapping

# 强分离声明（角色密集时必须用）
distinct separation between all figures, each character fully rendered with no merged body parts, 
clear gaps between foreground and midground figures

# 空心构图（对峙/仪式场景）
empty center composition, characters positioned at frame edges with vast negative space between them
```

**负空间与构图类型的配合**：

| 构图 | 负空间写法 | 效果 |
|------|-----------|------|
| 对称对峙 | `symmetrical composition, empty center, equal negative space on both sides` | 仪式感+对等权力 |
| 三角群像 | `triangular blocking with clear separation, negative space between each figure` | 稳定+权力层级 |
| 深度分层 | `foreground figure sharply separated from midground by focus drop, background blurred` | 空间纵深+层次 |

### 16.7 摄影机锁定与景别变化的提示词策略

**核心原则**：同一场景的连续镜头中，摄影机方向不变，只改变取景范围。

```
# 建立镜头（锁定摄影机+空间）
camera facing east, 35mm lens, eye level, static — wide shot establishing the hall

# 切近（同一摄影机方向，只变焦距/景别）
camera facing east, 85mm lens, eye level, static — medium shot on primary subject

# 再切近
camera facing east, 100mm lens, eye level, static — close-up on primary subject's face

# 回到宽景
camera facing east, 35mm lens, eye level, static — wide shot as before
```

**常见错误**：
- 正反打中"翻转"摄影机方向——❌ 摄影机不翻，是角色朝向变
- 切镜时省略`camera facing east`——❌ AI会重新"猜测"摄影机位置
- 同一场景内不同镜头的`camera facing`方向不同——❌ 等于越轴

### 16.8 180°法则的提示词实现

正反打场景中，维护轴线的提示词策略：

```
# 建立轴线（第一个镜头确立谁在左谁在右）
camera facing east, character A screen left foreground, character B screen right midground

# 正方（A的镜头——A仍在左，看右）
camera facing east, close-up on character A, looking screen right toward character B, 
consistent camera orientation same side of axis

# 反方（B的镜头——B仍在右，看左）
camera facing east, close-up on character B, looking screen left toward character A,
consistent camera orientation same side of axis
```

**关键**：`consistent camera orientation same side of axis` 这句话是AI锁轴的核心声明——不加这句，AI可能在反方镜头中"翻转"空间。

### 16.9 动作连续性的提示词写法

多人动作场景（打斗、追逐、群戏）中，动作跨镜头延续的提示词策略：

| 动作状态 | 提示词写法 | 避免的写法 |
|----------|-----------|-----------|
| 动作延续 | `continuation motion, same movement trajectory as previous shot` | `fighting`（太笼统） |
| 转身中间态 | `mid-turn movement, body rotating from screen-left to screen-right` | `turning`（方向不明） |
| 动作进行中 | `ongoing motion, arm mid-swing` | `swinging arm`（AI理解为开始挥臂，不是中途） |
| 位移延续 | `continuing forward trajectory, 2 meters from previous position` | `walking forward`（从哪走到哪？） |

**打斗场景的动作连续性**：
- 每个攻击镜头标注`mid-strike continuation` + 具体轨迹（如`staff swinging from lower-right arc`）
- 每个防御镜头标注`receiving strike continuation` + 身体状态（如`body staggered back half a step`）
- 碰撞镜头标注`impact frozen mid-frame`——碰撞是动作链的"铰链"，必须独立

### 16.10 先生成空镜再放角色的提示词工作流

**Step 1 — 生成空镜（锁定空间+光影）**：
```
EXTREME REALISM cinematic shot. 35mm prime, f/2.8.

Large temple hall with towering stone columns, snow blowing through open doorway, 
wet stone floor with puddle reflections, cold incense smoke drifting low.
Cold moonlight from camera-right high window (6500-7000K), warm candlelight from camera-left altar (3000K).
Empty scene, no characters. Establishing shot.

4K, 16:9. --ar 16:9 --v 7 --q 2
```

**Step 2 — 在空镜基础上加入角色（锚定段引用空镜的完整空间+光影描述）**：
```
[复制空镜提示词的CAMERA + SPACE + LIGHTING部分]

Primary subject: scar-faced commander screen left foreground — black armor with gold trim, battle-worn face, arms crossed.
Secondary subject: silver-haired monk screen right midground — white silk robes, prayer beads, calm posture.
3 meter distance, eye-line match, visual tension.

4K, 16:9. --ar 16:9 --v 7 --q 2
```

**Step 3 — 后续镜头只改变BLOCKING和景别**：
```
[复制CAMERA + SPACE + LIGHTING — 逐字不变]

85mm lens [替换35mm], close-up on primary subject, 
scar-faced commander screen left foreground [位置不变],
continuing same scene orientation.

4K, 16:9. --ar 16:9 --v 7 --q 2
```

**工作流优势**：空镜先锁定了空间和光影的"底板"，后续所有镜头都在这个底板上叠加角色——AI不需要每次都重新"想象"整个场景，一致性大幅提高。

### 16.11 俯视Blocking图的AI生成

俯视Blocking图是多人场景的空间规划工具，可以用AI生成作为参考：

```
Overhead bird's eye view blocking diagram of a temple hall scene, 
top-down schematic layout showing:
- Camera position marked at bottom center facing north
- Character A position: left foreground, facing right
- Character B position: right midground, facing left
- Movement path: dashed arrow from Character A moving toward center
- Key light source: right side high window
- Axis line between Character A and Character B
- All elements clearly labeled, clean architectural blueprint style,
dark lines on white background, professional film blocking notation

--ar 16:9 --v 7 --q 2
```

生成后作为所有后续镜头的空间基准参考——镜头中的角色位置必须与俯视图一致。

### 16.12 多人场景提示词自查清单

写完多人场景提示词后，逐项检查：

1. **CAMERA段存在**：是否声明了`camera facing [方向]`？
2. **SPACE段存在**：是否有空间类型+负空间声明？
3. **BLOCKING段使用绝对坐标**：是否用了`screen left/right` + `foreground/midground/background`，而非相对描述？
4. **角色标签化**：每个角色是否有至少一个独特视觉特征标签（而非man/woman）？
5. **Primary/Secondary层级**：是否有明确的优先级声明？
6. **负空间声明**：人物之间是否有明确的分离描述？
7. **180°法则**：正反打中是否有`consistent camera orientation same side of axis`？
8. **动作延续声明**：连续动作镜头是否有`continuation motion`/`ongoing motion`？
9. **锚定段跨镜头一致**：CAMERA+SPACE+LIGHTING段是否逐字重复（只替换BLOCKING和景别）？
10. **角色属性固定**：每个角色的标签/颜色/道具是否跨镜头完全一致？


## 十七、三步表演法AI提示词实战模板

### 17.1 三步法的提示词实现

三步表演法（面部肌肉+肢体语言+时间轴）是AI视频生成中从"写情绪词"到"写表演指令"的核心方法论。在提示词中的实现方式：

**Step 1 提示词模板——面部肌肉拆解**：
```
[情绪] — (核心肌肉1:权重) [效果描述], (核心肌肉2:权重) [效果描述], 
[辅助细节: 鱼尾纹/泪光/鼻翼翕动/喉结滚动/耳根泛红], 
[程度副词: 微微/缓慢/极轻微/克制地/下意识地]
```

**Step 2 提示词模板——肢体语言追加**：
```
; body language: [上肢动作] with natural inertia, [下肢/躯干状态], [生理微反应: 耳朵泛红/手指发白/肩膀发抖/吞咽]
```

**Step 3 提示词模板——时间轴拆镜**：
```
[0-N秒]: [情绪阶段1] — [面部+肢体状态]
[N-M秒]: [情绪阶段2] — [从上一阶段过渡的面部+肢体状态]
[M-X秒]: [情绪阶段3] — ...
```

### 17.2 情绪万能公式速查表

| 笼统词（❌ 避免） | 核心肌肉动作 | 辅助细节 | 程度副词 | 提示词结果 |
|------------------|------------|---------|---------|-----------|
| "开心" | zygomaticus major lift | orbicularis oculi engagement, eye crinkle | 微微 | 内敛温柔微笑 |
| "难过" | depressor anguli oris pull | nasolabial fold deepening, lip tremble | 克制地 | 隐忍不哭 |
| "愤怒" | corrugator supercilii activation | upper lid retraction, jaw clench | 压抑地 | 冷怒未发 |
| "害怕" | levator palpebrae retraction | pupil dilation, sclera showing above iris | 瞬间 | 突发恐惧 |
| "心动" | subtle zygomaticus micro-lift | pupil slight dilation, throat swallow | 无意识地 | 不自觉心动 |
| "决意" | jaw set, brows level | neck tension, shoulders square | 缓慢地 | 从容决断 |

### 17.3 角色性格差异化提示词对照表

同一种情绪，不同性格的角色用不同的提示词——角色性格决定表演方式：

| 情绪 | 冷酷/内敛型 | 温柔/敏感型 | 活泼/外放型 | 沉稳/老练型 |
|------|-----------|-----------|-----------|-----------|
| 开心 | 嘴角极轻微勾起一侧，喉结滚动 | 眼角弯起，微笑扩散至全脸，手指轻触唇角 | 咧嘴笑，拍手，身体前倾 | 嘴角微扬，缓缓点头，手指轻敲桌面 |
| 难过 | 眼神微微一暗，下颌收紧，表情不变 | 眼眶泛红，手指攥紧衣角，肩膀微耸 | 嘴唇颤抖，手捂胸口，身体蜷缩 | 眼神变深，缓缓闭眼，沉默3秒 |
| 紧张 | 指尖微颤，眼神不移，呼吸变浅 | 手心出汗，频繁吞咽，目光游移 | 来回踱步，搓手，脚尖点地 | 端坐不动，指尖轻敲，目光沉稳 |
| 心动 | 喉结滚动，瞳孔微扩，随即移开视线 | 耳根泛红，低头，嘴角不自觉翘起 | 身体转向对方，睁大眼睛，不自觉靠近 | 视线停留比平时长2秒，微微一笑 |

**提示词写法原则**：
1. 角色锚点表中必须标注**性格类型**——这决定情绪表达方式
2. 同一场景中不同角色的情绪提示词**不能雷同**——冷酷男主的"开心"和活泼女二的"开心"必须用不同的肌肉组合+肢体动作
3. 角色性格越极端，情绪表达越偏离"标准"——冷酷角色所有情绪都偏克制，活泼角色所有情绪都偏外放

### 17.4 强约束兜底声明模板

每段情绪提示词末尾必须加兜底约束，防止AI放飞自我：

| 场景 | 兜底声明 |
|------|---------|
| 克制表演 | `no exaggerated expressions, no facial deformation, stable frame, subtle performance throughout` |
| 爆发表演 | `emotional peak but controlled, no facial distortion, no cartoonish exaggeration, frame stable` |
| 面瘫/冷面 | `flat affect maintained, no involuntary expressions, no smirking, completely neutral except specified micro-movements` |
| 哭戏 | `realistic tear physics, no melodramatic sobbing, natural progression, no facial deformation` |

### 17.5 光影与情绪的绑定模板

光影对情绪的烘托效果极大——不写光影=AI随机给光=氛围感打折：

| 情绪类型 | 推荐光影 | 提示词写法 |
|----------|---------|-----------|
| 温馨/甜蜜 | 暖调柔光 | `warm soft diffused lighting, golden hour glow, gentle fill light, no harsh shadows` |
| 虐心/悲伤 | 冷调侧光 | `cold side lighting, half face in shadow, blue-gray color grade, minimal fill` |
| 压迫/威胁 | 硬光顶光 | `hard overhead lighting, deep under-eye shadows, harsh contrast, dramatic chiaroscuro` |
| 心动/暧昧 | 暖冷混合 | `warm light from subject direction, cool ambient fill, half face illuminated, romantic split lighting` |
| 觉醒/决意 | 正面硬光渐强 | `transitions from diffused cold light to direct frontal hard light, increasing definition and clarity` |
| 恐惧/震惊 | 闪烁/不稳定光 | `flickering unstable lighting, chiaroscuro shifting, underlit face, deep shadows` |

**光影与时间轴的配合**：情绪递进时，光影可以随之渐变——如模板4"女主觉醒"中前半段冷调散光（迷茫感）→后半段硬光从正面打（觉醒感），光影本身就在叙事。

### 17.6 实战模板1：霸总冷面压迫

适用场景：逼签协议/逼婚/威胁/最后通牒。精髓="不怒自威"——越克制越有压迫感。

```
[角色锚定] 30-year-old male, cold and imposing presence.

[面部肌肉] Brows slightly furrowed but not clenched, eyes half-narrowed looking down from above, 
mouth corners slightly pressed down forming a flat line, jawline tightened.
(corrugator supercilii micro-activation:1.3), (depressor anguli oris subtle tension:1.35), 
(masseter jaw clench:1.4)

[肢体语言] Upper body slightly leaning forward, one hand braced on desk/chair back, 
other hand casually pushing document/ring box toward the other person.
Fingers tap desk twice — controlled, deliberate.

[10秒时间轴]
0-2s: Expressionless stare at the other person, eyes scanning from top to bottom
2-4s: One corner of mouth barely lifts (not a smile — contempt), eyebrows micro-raise
4-7s: Leans forward, eyes locked on the other person's eyes without wavering, jaw slightly tucks
7-9s: Slowly pushes document/item forward, fingers tap desk twice
9-10s: Leans back into chair, expression returns to cold indifference, waiting for response

[光影] Cold hard lighting from above at 45°, intensifying jawline shadow, 4K ultra-sharp

[强约束] No exaggerated expressions, no villainous smirk, cold and restrained throughout, stable frame
```

### 17.7 实战模板2：女主倔强隐忍

适用场景：被羞辱/被逼签字/受委屈不低头。核心="美人落泪我见犹怜"——越倔强越让观众心疼。

```
[角色锚定] 22-year-old female, stubborn and enduring.

[面部肌肉] Eyes reddening but gaze unwavering, chin slightly raised, lips pressed into a thin line, 
nostrils slightly flaring.
(orbicularis oculi tension holding back tears:1.45), (mentalis chin tension:1.35), 
(nasalis nostril flare:1.3)

[肢体语言] Hands clenching at sides, fingernails digging into palms, 
shoulders slightly trembling but spine straight and upright.

[10秒时间轴]
0-2s: Hears the humiliation/sees evidence — a moment of visible shock, then immediately recovers
2-4s: Chin slowly raises, eyes begin to redden, lips press tight
4-6s: Nostrils slightly flare (holding back tears), gaze shifts from avoidance to direct eye contact
6-8s: Hands slowly clench at sides, shoulders begin to tremble
8-10s: Deep breath, tears glistening but not falling, expression settles into calm resolve

[光影] Side-backlight, half face in shadow, warm and cool tones split, 4K ultra-sharp

[强约束] No crying breakdown, no bowing head in weakness, spine straight throughout, stable frame
```

### 17.8 实战模板3：危险的心动

适用场景：霸总第一次动摇/不自觉注视。这是短剧流量密码——观众疯狂截图的就是"冷面裂了一条缝"的微反应。关键是动作要极小，越小越让人上头。

```
[角色锚定] 30-year-old male, unconscious micro-reaction of attraction.

[面部肌肉] Eyes originally careless, suddenly stop and fixate, pupils slightly dilate.
Previous cold mouth curve loosens, throat swallows slowly once.
(subtle zygomaticus micro-lift:1.2), (pupil dilation:1.35), (thyrohyoid throat swallow:1.3)

[肢体语言] Finger movement pauses (puts down glass / stops flipping documents), 
body unconsciously turns slightly toward the other person's direction.

[10秒时间轴]
0-2s: Catches sight of the other person in peripheral vision, gaze suddenly stops, hand movement pauses
2-4s: Eyes shift from careless to focused, pupils slightly dilate
4-6s: Throat slowly swallows, cold mouth curve slightly loosens
6-8s: Realizes he's staring, eyes quickly look away, jaw tightens back to cold face
8-10s: Can't help but look again, then immediately stands up / turns away

[光影] Warm soft lighting from the female lead's direction, male lead's side face half-lit half-shadow, 4K ultra-sharp

[强约束] No obvious smile, no deep affectionate gaze, movements extremely restrained and minimal, stable frame
```

### 17.9 实战模板4：身份反转/女主觉醒

适用场景：得知真相/决定反击。10秒走完"震惊→消化→冷静→觉醒"四个阶段，拍好了就是整集情绪高潮。

```
[角色锚定] 25-year-old female, progressive emotional arc from shock to resolve.

[面部肌肉] Phase transition:
Shock: pupils constrict, lips part slightly, whole body freezes
Processing: eyes slowly empty, processing information, lips slowly close
Calm: panic fades, replaced by cold clarity, brows level
Resolve: mouth corners slowly curve (not happiness — realization), eyes sharpen

[肢体语言] 
0-6s: body frozen, hands unconsciously grip whatever they're holding
6-8s: hands slowly release, posture straightens
8-10s: chin raises, direct forward gaze

[10秒时间轴]
0-2s: Sees key evidence/hears truth — pupils constrict, lips part, body freezes
2-4s: Eyes slowly go empty as if processing, lips gradually close
4-6s: Panic in eyes fades, replaced by calm, brows smooth out
6-8s: Mouth corners very slowly curve (not happy — figured it out), eyes sharpen
8-10s: Chin raises, stares directly ahead/at opponent, expression goes completely cold, gaze like a blade

[光影] First half: cold diffused light (disorientation), Second half: hard light from front (awakening), 4K ultra-sharp

[强约束] Emotional progression coherent without jump-cuts, no exaggerated expressions, no facial deformation, stable frame
```

### 17.10 三步表演法提示词自查清单

1. **面部肌肉替代情绪词**：是否用了解剖学肌肉名+权重替代了笼统的"开心""难过"？
2. **辅助细节存在**：是否有鱼尾纹/泪光/鼻翼翕动/喉结滚动/耳根泛红等辅助细节？
3. **程度副词精确**：是否有"微微""极轻微""缓慢""克制地"等程度控制词？
4. **肢体语言加入**：是否有上肢/下肢/躯干的同步动作描述？
5. **角色性格差异化**：同一场景中不同角色的情绪表达方式是否不同？
6. **时间轴拆镜**：复杂情绪是否拆成了逐秒/逐镜头的递进阶段？
7. **强约束兜底**：是否在末尾加了"无五官变形，无夸张表情，画面稳定"？
8. **光影与情绪绑定**：是否写了与情绪匹配的光影描述？
9. **70%时长策略**：单次抽卡时长是否控制在情绪阶段的70%以内（不过度贪心）？
10. **与已有规范衔接**：面部肌肉是否与解剖学肌肉权重表一致？肢体语言是否与三层次结构的小动作层一致？时间轴是否与情绪着陆点衔接？


## 十八、运镜五境AI提示词技巧

### 18.1 第一境：速度精确化的提示词写法

**核心原则**：用具体距离/焦段+时间替代形容词——形容词无法标准化，模型只能猜。

**推镜（Push-in/Dolly-in）提示词模板**：
```
# 极慢推进（8-10秒，氛围镜头）
camera slowly pushing in from 3 meters to 1.5 meters over 8 seconds, 
starting from wide shot ending at medium shot

# 慢速推进（5-6秒，情绪铺垫）
camera pushing in from 2 meters to 0.8 meters over 5 seconds,
starting from medium shot ending at medium close-up

# 中速推进（3-4秒，标准叙事）
camera pushing in from 1.5 meters to 0.6 meters over 3 seconds,
starting from medium close-up ending at close-up

# 快速推进（1.5-2秒，紧张揭示）
camera rapidly pushing in from 2 meters to 0.5 meters over 1.5 seconds

# 超快推进（<1秒，冲击）
camera slamming in from 3 meters to 0.3 meters in under 1 second, impact push
```

**焦段变焦替代距离推进**（更精准）：
```
camera zooming from 35mm to 85mm over 4 seconds, 
smooth continuous focal length change, maintaining focus on subject
```

**拉镜（Pull-out/Dolly-out）提示词模板**：
```
# 慢速拉远（5-6秒，疏离/释放）
camera pulling out from 0.8 meters to 4 meters over 5 seconds,
starting from close-up ending at full shot, subject shrinking in frame

# 快速拉远（2秒，震惊揭示环境）
camera rapidly pulling out from close-up to wide shot over 2 seconds,
revealing the full environment around the subject
```

**横移（Truck/Pan）提示词模板**：
```
# 慢速横移（5秒，空间探索）
camera trucking left approximately 3 meters over 5 seconds,
subject remaining centered as background shifts laterally

# 快速横移（2秒，戏剧揭示）
camera quickly panning right about 2 meters over 2 seconds,
revealing a new character entering the frame
```

### 18.2 第二境：反向规则的提示词写法

**核心铁律**：主体动作方向和运镜方向相反→戏剧张力。同向→平淡如vlog。

**反向运镜对照提示词表**：

| 主体动作 | ❌ 同向写法（平庸） | ✅ 反向写法（高级） |
|----------|-------------------|-------------------|
| 主体走向镜头 | "镜头跟随她向前推进" | "主体向镜头方向走来，镜头在5秒内匀速向后退，主体始终保持在画面中央，背景持续向她身后退去" |
| 主体向左转 | "镜头向左移动跟随" | "主体向左转身，镜头同时向右横移约1米，形成旋转揭示效果" |
| 主体抬头 | "镜头向上摇" | "主体抬头仰望，镜头同时从高处缓慢下降，形成对抗性构图" |
| 主体奔跑向前 | "镜头跟着向前追" | "主体向前奔跑，镜头反向后退移动，主体在画面中持续放大但背景急速后退" |
| 主体回头看 | "镜头随视线转向" | "主体回头看向身后，镜头继续向前推进，视线和运镜方向相反" |

**视线反向延伸提示词**：
```
# 角色看向画面左侧——镜头从右向左横移
character looking screen left with focused gaze, 
camera trucking from right to left, 
gaze direction opposing camera movement creating visual tension

# 角色抬头看天——镜头从上向下俯视
character looking upward, 
camera slowly descending from overhead angle,
creating inverse movement between gaze and camera
```

### 18.3 第三境：双锚点/三锚点运镜的提示词写法

**双锚点提示词模板**：
```
[START FRAME] [起始画面精确描述：景别+主体位置+构图+背景]
[CAMERA MOVEMENT] [具体运镜：时间+距离/角度+方向]
[END FRAME] [结束画面精确描述：景别+主体位置+构图+背景]
```

**完整示例——窗前转身**：
```
START FRAME: Woman seen from behind standing at window, full body in frame, 
blurred outdoor scenery through window, medium shot composition (3 meters)

CAMERA MOVEMENT: Over 5 seconds, camera pushes in approximately 1.5 meters while slowly 
orbiting clockwise 30 degrees around the subject, transitioning from behind to side profile

END FRAME: Woman's side profile close-up, eyes looking out window, 
window light halo creating bokeh background, medium close-up (0.8 meters)
```

**三锚点提示词模板**（8秒+长镜头）：
```
[ANCHOR 1 — 0s] [起点画面：景别+构图]
[TRANSIT 1 — 0-4s] [第一段运镜：方向+距离+时间]
[ANCHOR 2 — 4s] [中点画面：景别变化+主体位移]
[TRANSIT 2 — 4-8s] [第二段运镜：方向+距离+时间]
[ANCHOR 3 — 8s] [终点画面：最终景别+构图]
```

**完整示例——庭院登场**：
```
ANCHOR 1 (0s): Wide shot, character standing at center of courtyard, full body, 
surrounded by ancient architecture

TRANSIT 1 (0-4s): Camera pushing in 3 meters while slowly rising 50cm, 
character remains centered

ANCHOR 2 (4s): Medium shot, character now at frame right, 
courtyard architecture visible in left background

TRANSIT 2 (4-8s): Camera continuing push-in 1.5 meters while orbiting left 20 degrees,
closing in on character's face

ANCHOR 3 (8s): Close-up on character's face, soft focus courtyard in background,
warm golden light
```

### 18.4 第四境：复合运镜的提示词写法

**5个复合运镜公式提示词**：

**公式1：环绕推进（Orbit + Dolly）**：
```
camera orbiting clockwise around subject 90 degrees while simultaneously 
pushing in 2 meters over 5 seconds, 
starting from behind-left medium shot ending at front-right close-up
```

**公式2：升降推进（Crane + Push）**：
```
camera rising from ground level (0.3m) to subject's eye level (1.6m) 
while simultaneously pushing forward 3 meters over 6 seconds,
starting from low-angle full body ending at eye-level close-up
```

**公式3：横移变焦（Truck + Zoom）**：
```
camera trucking left 3 meters while simultaneously zooming from 35mm to 85mm 
over 4 seconds, subject remaining at similar frame size 
but background compression dramatically increasing
```

**公式4：希区柯克变焦（Dolly Zoom）**：
```
classic dolly zoom effect: camera physically moving backward 2 meters 
while lens zooming from 35mm to 85mm simultaneously over 3 seconds,
subject remaining same size in frame but background stretching and distorting,
creating disorienting vertigo feeling
```

**公式5：倾斜横移（Tilt + Pan）**：
```
camera slowly panning from right to left while simultaneously tilting up 30 degrees 
over 5 seconds, revealing the full grandeur of the scene from horizontal to vertical
```

**复合运镜进阶写法——三维度同步**：
```
camera in 6 seconds:
- pushing forward approximately 5 meters
- simultaneously orbiting left 60 degrees around subject
- simultaneously rising approximately 30cm
ending at subject's side profile close-up with layered courtyard bokeh background
```

### 18.5 第五境：静止镜头的提示词写法

**核心区别**：完全静止=照片（❌），几乎静止+微弱呼吸感=电影（✅）

**标准静止镜头提示词**：
```
locked-off camera with extremely subtle breathing motion (less than 5cm of drift), 
perfectly stable composition, tripod precision with human micro-imperfection,
subject's micro-expressions and subtle breathing becoming the visual focus
```

**情绪特写静止镜头**：
```
locked-off camera, close-up on face, absolutely minimal camera movement, 
subtle organic breathing drift under 3cm, 
every micro-expression magnified by stillness, 
viewer feels like they are standing right in front of the character,
no distracting camera motion, pure emotional focus
```

**决定性瞬间静止镜头**：
```
locked-off static shot, camera frozen in anticipation, 
subject about to make a crucial decision, 
stillness creating breath-holding tension, 
the absence of camera movement amplifying the weight of the moment
```

**极致美景静止镜头**：
```
locked-off camera, perfectly balanced composition, 
no camera movement — the frame itself is the statement, 
subtle atmospheric elements (drifting dust, gentle wind, soft light shift) 
providing organic life without camera motion
```

**静止 vs 运镜的切换提示词**：
```
# 从静止开始，在关键时刻启动运镜
beginning with locked-off static composition for 3 seconds, 
then camera slowly initiating push-in as emotional shift occurs,
the start of movement itself becoming a narrative event
```

### 18.6 运镜五境提示词自查清单

1. **速度精确化**：运镜是否用了"X秒内从X米到X米"或"X秒内从Xmm到Xmm"替代了"缓慢""快速"？
2. **反向规则**：主体动作方向和运镜方向是否相反？是否避免了同向组合？
3. **视线反向**：角色视线方向是否与运镜方向形成对抗？
4. **双锚点**：每个运镜镜头是否有明确的起始画面和结束画面描述？
5. **三锚点**：8秒以上长镜头是否用了三锚点拆分？
6. **复合运镜**：是否尝试了多维度同步运动（Orbit+Dolly/Crane+Push/Truck+Zoom/Dolly Zoom/Tilt+Pan）？
7. **静止镜头判断**：情绪特写/决定性瞬间/极致美景/心理深度场景是否选择了静止而非运镜？
8. **静止≠不动**：静止镜头是否加了"extremely subtle breathing motion (<5cm)"声明？
9. **运镜与叙事匹配**：运镜选择是否服务于叙事功能（而非炫技）？
10. **成本意识**：是否合理平衡了静止镜头（稳定率90%）和复合运镜（稳定率60%）的比例？

## 十九、角色描写精度规范AI提示词技巧

### 19.1 核心问题：抽象词是提示词空间的浪费

角色提示词中每个词都占据token位。抽象词（"权势""奢华""冷漠""气场"）占据位置但不产生可执行的视觉输出——AI收到"权势"后的响应完全随机。把这些词替换为AI能"画出来"的具体视觉指令，提示词的信息密度和可控性同时提升。

**提示词替换原则**：
```
❌ abstract emotion/evaluation word → ✅ concrete visual instruction that IMPLIES the emotion/evaluation
❌ "imposing presence" → ✅ "back not touching chair, torso tilted 5-10° forward, arms extended across both armrests"
❌ "luxurious suit" → ✅ "charcoal-black worsted wool 120s, notch lapel 7cm, suppressed waist cut, matte sheen"
❌ "cold expression" → ✅ "upper eyelids at 3/4 height covering top quarter of iris, gaze fixed on viewer's glabella"
```

### 19.2 六维拆解的提示词模板

每个角色锚定段必须覆盖六个维度，每个维度有对应的英文提示词结构：

**维度1：体型与轮廓（Body Architecture）**
```
[Gender], [age range], [height]cm tall with [shoulder description] and [waist description] 
creating [silhouette type] silhouette. [Posture description when seated/standing]. 
Overall center of gravity [position].
```

**维度2：面部特征（Facial Architecture）**
```
[Cheekbone description], [jawline description], [eye socket depth], 
[brow ridge description], [nose description], [lip description — thickness, natural direction, 
commissure angle]. [Skin texture/quality].
```

**维度3：发型（Hair Architecture）**
```
[Hair color + exact shade], [volume: thin/medium/dense], [style: slick-back/part/texture], 
[part or no part], [product sheen level: matte/low-gloss/medium-gloss/high-gloss], 
[temple treatment], [hairline shape if relevant].
```

**维度4：服饰（Wardrobe Architecture）——最需精度的维度**
```
WEARING: [exact color name, NOT "black"] [fabric type + weave + sheen] suit, 
[lapel type] [lapel width]cm, [single/double-breasted] [button count] 
([buttoning convention]), [shoulder type], [waist cut], [cuff detail], 
[shirt: color + collar type + cuff type + cufflink description], 
[tie: exact color + material + knot type + knot tightness + length endpoint].
```

**维度5：道具（Prop Architecture）——道具必须写光线交互**
```
ACCESSORIES: [Watch: case material + face color + complication + diameter Xmm 
on [left/right] wrist, [light interaction — what reflection it creates under scene lighting]]. 
[Ring: metal + type + finger]. [Other: same level of detail].
```

**维度6：体态与微动作（Kinesic Architecture）**
```
POSE: [Seated/Standing] [exact posture angles], [arm placement with spatial description], 
[territorial occupation — how much space the body claims]. 
[Micro-action: specific finger/head movement with exact frequency — "1 tap per 3 sec"]. 
[Remaining body: "remaining fingers perfectly still" / "breathing nearly imperceptible"]. 
[Gaze: exact focal point — NOT "looks at camera" but "gaze directed at viewer's glabella"].
```

### 19.3 完整案例：企业反派VICTOR

**中文锚点表（六维拆解版）**：

```
角色：VICTOR（企业反派）
├── 维度1·体型与轮廓：40岁中后期，身高约185cm，肩宽背厚但不臃肿，
│   坐姿时肩线仍保持绝对水平，整体剪影呈倒三角——宽肩收腰，重心稳定如铸铁
├── 维度2·面部特征：颧骨高且轮廓锋利，下颌线如刀削，
│   眼窝深陷形成天然阴影区，眉骨突出，鼻梁笔直偏窄，
│   嘴唇薄而长——嘴角自然走向微下压
├── 维度3·发型：深棕近黑色头发，发量浓密，整齐后梳无分缝（classic slick-back），
│   发胶光泽度中等偏高，鬓角修剪至耳廓上缘，露出1cm干净皮肤带
├── 维度4·服饰：
│   ├── 西装：深炭黑色（非纯黑，带微弱暗纹），平驳头窄领（notch lapel, 7cm width），
│   │   单排两粒扣，仅扣下摆扣；面料为精纺羊毛（worsted wool, 120s），
│   │   哑光光泽，肩部轻微垫肩（structured shoulder），收腰剪裁（suppressed waist），
│   │   袖口4粒真开扣（working buttonholes），露出约1cm衬衫袖口
│   ├── 衬衫：冷白色法式叠袖衬衫，袖扣为哑光铂金方形
│   └── 领带：深午夜蓝丝质领带，半温莎结，结体紧实端正，长度恰好触皮带扣上缘
├── 维度5·道具：
│   ├── 腕表：铂金壳深灰盘面计时码表，表径42mm，佩戴于左腕，表带略松，
│   │   表盘在侧光下反射冷白色光斑——坐姿时左手搭扶手，腕表恰好落入画面
│   └── 戒指：右手小指一枚素面铂金章戒（signet ring）——权力旧式象征
├── 维度6·体态与微动作：
│   ├── 坐姿：后背不靠椅背，上身微微前倾5-10°，双臂展开搭在扶手两端，
│   │   如同占据领地——整个椅子的空间都是他的延伸
│   ├── 手部：右手食指偶尔极缓慢地叩击扶手（1次/3秒），其余手指纹丝不动
│   └── 头部：听人说话时头微偏3-5°，下巴不抬——视线从上方2cm处落下，制造俯视感
├── 色彩标签：深炭黑 + 冷白 + 午夜蓝 + 铂金冷光
├── 一致性红线：西装颜色（深炭黑非纯黑）、腕表位置（左腕）、体型轮廓（宽肩收腰）
└── 面部表演锚定（基态层）：
    ├── 冷漠基态：眉头放松不蹙，上眼睑半垂遮住虹膜上1/4，视线焦点永远在对方眉心
    ├── "隐晦坏笑"肌肉拆解：右侧嘴角提肌（zygomaticus major）极轻微收缩，
    │   右侧上扬约3mm——不是笑，是评估；下颌线不放松，维持收紧状态
    └── 肢体同步：坏笑出现时右手食指叩击暂停1拍——嘴角与手指的微同步=心理计算
```

**英文AI提示词（完整版）**：

```
EXTREME REALISM cinematic portrait. ARRI Alexa Mini LF, 85mm prime, f/1.4, 
shallow depth of field.

VICTOR — male, mid-40s, 185cm tall with broad structured shoulders and 
suppressed waist creating inverted-triangle silhouette. High sharp cheekbones, 
sculpted jawline, deep-set eyes with pronounced brow ridge creating natural 
shadow pockets, thin long lips with natural downward commissure. Dark brown 
hair slicked back without part, medium-high gloss, temples trimmed above ear 
helix exposing 1cm clean skin strip.

WEARING: Charcoal-black (NOT pure black) worsted wool suit, 120s thread count, 
7cm notch lapel, single-breasted two-button (bottom button fastened only), 
structured shoulders, suppressed waist cut, four working buttonholes on cuffs 
with 1cm shirt cuff visible. Cold-white French cuff shirt with matte platinum 
square cufflinks. Midnight blue silk tie, half-Windsor knot, tight and precise, 
length to belt buckle upper edge.

ACCESSORIES: Platinum case 42mm chronograph with dark grey dial on left wrist, 
cold white light reflection on dial face from ceiling spotlight. Plain platinum 
signet ring on right pinky finger.

POSE: Seated in black full-grain leather executive chair, back NOT touching 
chair back, torso tilted 5-10° forward, arms extended across both armrests — 
occupying territory. Right index finger in mid-tap on armrest (1 tap per 3 sec), 
remaining fingers perfectly still. Head tilted 3-5°, chin level — gaze directed 
downward 2cm from horizontal, landing on viewer's glabella.

FACIAL EXPRESSION: Zygomaticus major on right side contracted approximately 3mm — 
NOT a smile but an evaluation. Upper eyelids at 3/4 height covering top quarter 
of iris. Gaze fixed on viewer's glabella (between eyebrows) — inspection not 
conversation. Jawline remains taut, no relaxation.

ENVIRONMENT: Floor-to-ceiling glass walls on three sides, 80sqm corner office. 
Dark walnut L-desk with closed laptop, crystal whiskey glass (amber liquid 1/3), 
black fountain pen. Near-black polished marble floor reflecting city night lights. 
City skyline at 60+ floors visible through glass, cold blue ambient light (5800K) 
flooding in. Recessed ceiling spotlights (3500K warm white) hitting shoulder 
contour and chair back. Semi-transparent reflection of figure overlaid on glass 
with city light bands — man and city merged.

Cinematic color grade, dual color temperature conflict (cold blue 5800K vs warm 
white 3500K), glass reflections mandatory, floor reflections mandatory. 
No facial distortion, no exaggerated expressions, entire frame controlled and precise.
8K, 2.39:1 anamorphic. --ar 21:9 --style raw
```

### 19.4 服饰精度英文速查表

| 中文概念 | 英文提示词 | 精度级别 |
|----------|-----------|---------|
| 纯黑西装 | pure black suit | ❌ 过于笼统 |
| 深炭黑精纺羊毛西装 | charcoal-black worsted wool suit | ✅ 颜色+面料+织法 |
| 平驳头 | notch lapel | ✅ 精确 |
| 戗驳头 | peak lapel | ✅ 精确 |
| 青果领 | shawl lapel | ✅ 精确 |
| 单排两粒扣 | single-breasted two-button | ✅ 精确 |
| 双排六粒扣 | double-breasted six-button | ✅ 精确 |
| 收腰剪裁 | suppressed waist cut | ✅ 精确 |
| 直筒剪裁 | regular fit | ✅ 精确 |
| 垫肩 | structured shoulder | ✅ 精确 |
| 自然肩 | natural shoulder | ✅ 精确 |
| 真开扣袖口 | working buttonholes on cuffs | ✅ 精确 |
| 法式叠袖 | French cuff | ✅ 精确 |
| 半温莎结 | half-Windsor knot | ✅ 精确 |
| 精纺120支 | worsted wool 120s | ✅ 精确 |
| 哑光光泽 | matte sheen | ✅ 精确 |
| 深午夜蓝 | midnight blue | ✅ 精确 |
| 带微弱暗纹 | with subtle texture pattern | ✅ 精确 |
| 冷白色 | cold-white | ✅ 精确（vs 纯白 pure white） |

### 19.5 权力视觉化的提示词策略

"权势"不可直接写入提示词，但可以通过以下五层视觉证据链让AI生成出权力感：

**层级1：空间占有（Spatial Dominance）**
```
✅ "back NOT touching chair back, arms extended across both armrests — 
    the entire chair is his extension"
✅ "standing with feet planted wider than shoulder width, 
    claiming maximum floor space"
```

**层级2：动作节奏控制（Temporal Dominance）**
```
✅ "right index finger tapping armrest at 1 tap per 3 seconds — 
    he controls the pace"
✅ "deliberate pause before responding, 2-second silence, 
    then single slow nod"
```

**层级3：视线权力（Gaze Dominance）**
```
✅ "gaze directed at viewer's glabella — inspection not conversation"
✅ "eyes tracking slower than head turn, creating predator-like 
    disassociated gaze"
```

**层级4：环境映射（Environmental Mirroring）**
```
✅ "semi-transparent reflection of figure overlaid on glass with 
    city light bands — man and city merged, he IS the city"
✅ "polished marble floor reflecting his silhouette from below — 
    he casts shadow in both directions"
```

**层级5：材质等级（Material Hierarchy）**
```
✅ "worsted wool 120s + matte platinum + controlled sheen = 
    quiet old money, not flashy new money"
✅ "every surface deliberate, nothing ostentatious, 
    quality visible only to those who know what to look for"
```

### 19.6 反派/权势角色的通用提示词骨架

适用于任何"坐在权力位置"的角色，替换具体参数即可：

```
EXTREME REALISM cinematic portrait. [Camera body], [Focal length]mm prime, 
f/[aperture], [depth of field description].

[CHARACTER NAME] — [gender], [age range], [height]cm with [body type 
description] creating [silhouette type] silhouette. [Facial architecture: 
cheekbone + jawline + eye socket + brow ridge + lip shape + natural 
commissure direction]. [Hair: color + density + style + sheen + temple 
treatment].

WEARING: [Exact color NOT "black"] [fabric type + weave + sheen] suit, 
[lapel type] [lapel width]cm, [button configuration], [shoulder type], 
[waist cut], [cuff detail with shirt cuff visible]. [Shirt: color + 
collar + cuff + cufflink]. [Tie/neckwear: exact color + material + 
knot type + tightness + length endpoint].

ACCESSORIES: [Watch: case + dial + size + wrist + light interaction]. 
[Ring: metal + type + finger]. [Other props at same precision level].

POSE: [Posture with angles], [arm placement with spatial claim], 
[micro-action with frequency]. [Still body parts explicitly stated]. 
[Gaze: exact focal point, NOT "at camera"].

FACIAL EXPRESSION: [Zygomaticus/orbicularis/frontalis status with mm 
measurement], [eyelid height over iris], [jawline tension], [gaze quality 
— inspection/conversation/avoidance].

ENVIRONMENT: [Room size + structure], [key furniture with exact items on 
surfaces], [floor material + reflectivity], [light source 1: temperature 
+ direction], [light source 2: temperature + direction], [reflection 
effects mandatory], [color temperature conflict if applicable].

[Color grade], [Mandatory visual effects], [Negative constraints]. 
[Resolution], [Aspect ratio]. --ar [ratio] --style raw
```

### 19.7 常见角色类型的六维速填表

| 角色类型 | 维度1体型 | 维度2面部 | 维度3发型 | 维度4服饰 | 维度5道具 | 维度6体态 |
|----------|----------|----------|----------|----------|----------|----------|
| 企业反派 | 宽肩收腰倒三角 | 高颧骨+深眼窝+薄唇下压 | 后梳+高光泽+鬓角精修 | 深色精纺+结构肩+收腰 | 铂金腕表+章戒 | 前倾占位+极慢微动作 |
| 冷面霸总 | 修长匀称V型 | 锋利下颌+深邃眼神 | 自然纹理+低光泽 | 深色高支+自然肩+修身 | 简约机械表 | 靠椅背+指尖动作 |
| 女强人CEO | 修长挺拔肩线方正 | 高颧骨+紧致下颌线 | 精致短发/束发+低光泽 | 藏蓝/深灰套裙+利落剪裁 | 纤细腕表+简约耳钉 | 脊背笔直+手势精确 |
| 神秘富豪 | 中等身材体量藏于宽袍 | 圆润面庞+细长眼+浅笑 | 银灰+凌乱+不羁 | 深色丝绒/亚麻+宽松+无结构 | 古董怀表+玉戒 | 后仰+手指交叠+微笑不达眼 |
| 街头狠人 | 紧实肌肉+低重心 | 断鼻+疤痕+咬肌突出 | 寸头/光头+无修饰 | 皮夹克+旧T恤+工装裤 | 银链+指节戒+纹身 | 含胸+下颌前突+眼神锁定 |

### 19.8 提示词中"光线交互"的写法——道具活的关键

死道具写材质就够了，但活道具必须写**它在特定光线下的行为**——这是区分"贴上去的图"和"存在于场景中的物"的关键：

| 道具 | 死写法 | 活写法 |
|------|--------|--------|
| 腕表 | platinum watch on left wrist | platinum case watch, dial face catching cold white spotlight reflection, second hand visible through sapphire crystal |
| 威士忌杯 | crystal whiskey glass on desk | crystal whiskey glass with amber liquid, ice sphere refracting ceiling spotlight into warm amber glow on desk surface |
| 玻璃幕墙 | glass walls around office | floor-to-ceiling glass walls, semi-transparent reflection of his silhouette overlaid on city light bands at night |
| 大理石地面 | dark marble floor | near-black polished marble floor, mirror-reflecting cold blue city ambient from above, warm ceiling spotlight from below |
| 皮椅 | black leather executive chair | black full-grain leather chair, chrome frame reflecting dual color temperature, leather surface catching warm spotlight on shoulder contour |

### 19.9 角色描写精度提示词自查清单

1. **抽象词清零**：提示词中是否还有"imposing""luxurious""powerful""intimidating"等AI无法执行的抽象词？
2. **六维全覆盖**：体型/面部/发型/服饰/道具/体态六个维度是否每个都有精度级描述？
3. **颜色精确化**：是否用了"charcoal-black"而非"black"？"midnight blue"而非"blue"？"cold-white"而非"white"？
4. **面料精度**：服饰是否写到了材质+织法+光泽度（如worsted wool 120s, matte sheen）？
5. **驳头/剪裁精度**：西装是否写了lapel type+width+shoulder type+waist cut？
6. **道具光线交互**：每个道具是否写了它在场景光线下的反射/折射/投影效果？
7. **表演基态**：是否定义了角色"不做表情时的默认脸"（eyelid height + gaze point + jawline tension）？
8. **微动作节奏**：体态描写是否有具体频率（如"1 tap per 3 seconds"）而非"occasionally"？
9. **视线落点**：是否写了gaze的精确目标（如"viewer's glabella"）而非"at camera"？
10. **权力视觉化**：如果是权力角色，是否用空间占有/动作节奏/视线/环境映射/材质等级五层替代了抽象的"权势"？

### 19.10 角色类型提示词速写法

不同角色类型的提示词策略不同——不是简单替换名字和服装，而是调整整个提示词的信息权重分配。根据角色类型→精度重点映射表，以下为每种类型提供速写模板：

**权力型反派（体态>面部>服饰）**：
```
[Gender], [age], [height]cm, [silhouette type]. 
[POSTURE — 占据50%提示词篇幅]: back not touching chair, torso tilted [X]° forward, 
arms extended claiming territory, [micro-action with exact frequency], 
[gaze: exact focal point creating dominance], remaining body perfectly still.
[FACIAL — 占据25%篇幅]: [bone structure + eye state + resting expression with muscle-level detail].
[WARDROBE — 占据15%篇幅]: [precision suit/shoes/watch with material+sheen+reflection].
[HAIR+PROPS — 占据10%篇幅]: [slick-back/grooming detail] + [signature prop with light interaction].
```

**女主/恋人（面部>体态>服饰）**：
```
[Gender], [age], [height]cm, [silhouette type].
[FACIAL — 占据40%篇幅]: [cheekbone+jawline+eye architecture+lip shape with natural direction], 
[resting face: eyelid height + gaze point + subtle tension pattern], 
[emotional variant 1: specific muscle + direction + amplitude].
[KINESIC — 占据30%篇幅]: [signature gesture with spatial detail], 
[micro-action revealing emotion: "fingertips hovering 2cm above surface, slight tremor"], 
[breathing pattern under emotional stress].
[WARDROBE — 占据20%篇幅]: [fabric precision + color naming + silhouette + accessory with light interaction].
[HAIR+PROPS — 占据10%篇幅]: [hair movement potential + emotional prop].
```

**少年/成长型（发型>体型>体态）**：
```
[Gender], [age] — appear [younger/older than stated age], [height]cm, [body type: still filling out / lean / lanky].
[HAIR — 占据30%篇幅]: [style with energy/movement indicator], [texture: messy/controlled/transitional], 
[growth metaphor: "overgrown fringe falling into eyes, pushed back impatiently"].
[BODY ARCHITECTURE — 占据25%篇幅]: [semi-mature features: jawline not fully set / shoulders still narrowing], 
[posture: self-conscious / defiant / uncertain — written as physical angles].
[KINESIC — 占据20%篇幅]: [high-frequency restless movement], [telling micro-action revealing age], 
[growth marker: "hands slightly too large for wrists, not yet grown into them"].
[FACIAL — 占据15%篇幅]: [incomplete adult features], [default expression: guarded/wondering/rebellious].
[WARDROBE — 占据10%篇幅]: [age-appropriate with one "trying to look older" detail].
```

**老人/智者（面部>道具>体型）**：
```
[Gender], [age range], [height]cm, [body: weathered/compressed/stooped — specific angle].
[FACIAL — 占据40%篇幅]: [deep crease map: forehead lines + nasolabial folds + crow's feet direction], 
[skin: age spots + texture + translucency at temples], [eye: wisdom vs fatigue in iris clarity], 
[resting face: specific pattern of lines suggesting lifetime of [emotion]].
[PROPS — 占持25%篇幅]: [signature prop with wear/patina/story — "reading glasses with repaired temple arm"], 
[light interaction: how prop catches light differently due to age/wear].
[BODY — 占据20%篇幅]: [specific posture of age: where gravity has won], 
[movement: economy of motion / deliberate slowness / hidden strength].
[WARDROBE — 占据10%篇幅]: [quality fabrics worn past their prime / deliberate simplicity].
[HAIR — 占据5%篇幅]: [thinning pattern + what remains: color/grooming philosophy].
```

**冷面/面瘫型（面部>体态>服饰）**：
```
[Gender], [age], [height]cm, [silhouette type].
[FACIAL — 占据45%篇幅]: [RESTING FACE with PROHIBITION declarations], 
"upper eyelids at [X] height, [NO brow furrowing, NO lip twitching, NO micro-expressions], 
gaze: [locked/converged/assessed — specific target]", 
[ONLY permitted variation: specific muscle at specific amplitude — "right zygomaticus major ≤2mm, ONLY during [condition]"].
[KINESIC — 占据30%篇幅]: [extremely controlled movement with exact rhythm], 
[what DOESN'T move: "remaining fingers locked, breathing invisible"], 
[mechanical/ritualistic actions replacing emotional expression].
[WARDROBE — 占据15%篇幅]: [precision without ornament — control extends to clothing choices].
[HAIR+PROPS — 占据10%篇幅]: [controlled/groomed + prop that serves function not decoration].
```

**配角/功能型（服饰>发型>道具）**：
```
[Gender], [age range]. [HIGH-IDENTITY TAG: color+role+signature feature — e.g. "RED-SCARF WAITER"].
[WARDROBE — 占据35%篇幅]: [1-2 defining garment details that make character recognizable in crowd], 
[color tag + fabric + distinctive element], "visible from across the room".
[HAIR — 占据25%篇幅]: [distinctive style/silhouette — recognizable in silhouette].
[PROPS — 占据20%篇幅]: [functional prop tied to role + light interaction].
[FACIAL — 占据15%篇幅]: [1-2 defining features — not full anatomy, just what makes them THEM].
[BODY+KINESIC — 占据5%篇幅]: [minimal — let wardrobe and prop do the work].
```

### 19.11 描写精度→提示词转换的3个常见陷阱

**陷阱1：中文精修版→英文提示词时信息衰减**
中文六维拆解写了"右侧嘴角提肌极轻微收缩约3mm"，翻译时容易变成"slight smirk"——3mm的肌肉精度丢失了。
- **规则**：中文精度描写中的数字（角度/幅度/频率）在英文提示词中必须保留
- ❌ "slight smirk" → ✅ "right zygomaticus major contracted approximately 3mm, jawline remains taut"

**陷阱2：六维拆解齐全但提示词中维度失衡**
按映射表，权力型反派体态应占50%篇幅，但实际写提示词时往往服饰写了3行、体态只有1行——信息分配与角色类型不匹配。
- **规则**：提示词中各维度的篇幅占比应与角色类型→精度重点映射表一致
- 检查方法：数每个维度的英文词数，对比映射表优先级

**陷阱3：将"观众感受"当成"视觉描写"写进提示词**
"画面呈现商业帝国的冷峻格调"是观众感受，不是视觉指令。AI收到"commercial empire aesthetic"后的响应完全随机。
- **规则**：提示词中只写"画什么"，不写"感受什么"。观众感受是描写精度的目标，不是提示词的内容
- ❌ "imposing corporate empire atmosphere" → ✅ "floor-to-ceiling glass walls reflecting city night lights, semi-transparent overlay of his silhouette on light bands"

## 二十、暧昧/恋爱/亲密戏AI提示词技巧

### 20.1 核心原则：靠近+克制=暧昧的提示词实现

暧昧不是"甜蜜"提示词的堆砌，而是同时声明两种对抗力的存在——吸引力+抵抗力。提示词必须在同一句中同时出现这两种力：

```
❌ "loving gaze toward her" — 只有靠近没有克制=直白无张力
❌ "avoiding eye contact" — 只有克制没有靠近=冷漠无温度
✅ "gaze drawn toward her then catching himself, eyes darting away the instant she looks up — attraction overridden by fear" — 同时存在
```

**暧昧提示词的双力结构**：
```
[attraction signal] + [resistance signal] = tension
"leaning slightly closer" + "but pulling back before crossing the boundary" = charged air
"eyes finding hers across the room" + "looking away the moment she notices" = the audience knows
"hand reaching toward her shoulder" + "stopping 2cm from skin, fingers trembling" = almost
```

### 20.2 视线提示词——眼神停留时间的精确控制

**偷看（初识/暗恋）**：
```
his eyes settling on her profile when she's not looking, 
gaze lingering 2 seconds too long, 
then snapping away as she begins to turn — 
camera holds on his face, catching the moment of being almost-caught
```

**余光交流（暧昧升温）**：
```
side-by-side composition, neither looking at the other directly, 
but his peripheral vision locked on her hands, 
her peripheral vision tracking his breathing — 
neither acknowledging the awareness, both completely aware
```

**倒影/反射（隐秘心动）**：
```
her reflection visible in window glass as he stares out at the rain, 
his eyes actually focused on her mirrored image, not the city — 
the window knows what he won't admit
```

**对视后移开（心动被发现）**：
```
his eyes meet hers — 0.5 second of full contact — 
she breaks first, gaze dropping to her hands, 
camera does NOT cut — holds on the space between them for 1 full second, 
air becoming audible, then he slowly looks away too — 
they both know what just happened
```

**擦肩回头（瞬间心动）**：
```
passing each other in narrow corridor, shoulders almost brushing, 
she continues 3 steps past him — 
then a 0.5 second delay — her head turns back just as he's turning too, 
eyes meeting for one suspended moment — 
neither stopping, both changed
```

### 20.3 呼吸感镜头提示词模板

呼吸感镜头=镜头的心跳与角色的心跳同步。不同情绪状态对应不同运镜节奏：

**情绪靠近——极慢推进**：
```
camera slowly pushing in at 0.3 meters per 5 seconds, 
as if drawn toward subject involuntarily, 
movement so slow it's almost imperceptible — 
like the viewer is leaning in without deciding to
```

**被发现/心虚——镜头停止**：
```
camera freezes mid-push, 
sudden stillness after the slow drift — 
like holding one's breath, 
the stillness itself becoming the loudest element in the frame
```

**情绪失控——呼吸变重**：
```
subtle handheld wobble intensifying from imperceptible to noticeable, 
camera breathing with the scene — 
not shaky-cam chaos, but the trembling of someone trying to stay still 
while their pulse is racing
```

**空气变化——微弱推进+长停顿**：
```
extremely slow drift forward over 8 seconds, 
then abrupt lock-off — 
silence becoming audible, 
the held breath of the frame matching the held breath between them
```

### 20.4 空间距离的提示词实现

**安全距离——障碍物阻隔**：
```
wide shot, table between them creating natural boundary, 
both seated with proper distance — 
the furniture itself is the relationship's armor, 
no physical contact possible without conscious choice
```

**危险距离——私人空间被侵入**：
```
medium shot, he's standing close enough that she has to tilt her head up, 
the 40cm between them charged — 
she can smell his cologne, 
he can see the pulse at her throat — 
personal space breached but neither stepping back
```

**暧昧距离——"差一点碰到"**：
```
close-up of his hand reaching toward her face, 
stopping 2cm from her cheek — 
fingers trembling slightly, suspended in the almost — 
not touching is more intimate than touching, 
the almost-contact electrifying the air between skin and skin
```

### 20.5 "差一点"提示词库——未完成动作>已完成动作

| 未完成动作 | 提示词 | 已完成动作（❌较弱） |
|-----------|--------|-------------------|
| 手悬停 | `hand hovering 2cm from her face, fingers trembling, not touching` | 牵手 |
| 额头靠近 | `foreheads leaning toward each other, stopping 1cm apart, breath mingling` | 亲吻 |
| 衣角擦过 | `his sleeve barely brushing her bare arm as he passes, the lightest contact` | 拥抱 |
| 呼吸接近 | `so close their breath clouds intermingle in the cold air, visible proof of proximity` | 耳语 |
| 肩膀轻触 | `shoulders making contact for exactly 1 second in narrow hallway, both frozen` | 搂肩 |
| 手指擦过 | `fingertips grazing during object handoff, both pretending it didn't happen` | 握手 |
| 嘴唇靠近 | `lips 1cm apart, both breathing through mouths, neither closing the distance` | 接吻 |

### 20.6 身体语言提示词——表面含义vs深层心理

**后退≠拒绝**：
```
she steps back half-step as he leans in — 
NOT rejection, but self-protection — 
the retreat is her fear of what she'll do if she stays still, 
body choosing distance while heart choosing closeness
```

**靠近≠主动**：
```
he finds himself inches closer without deciding to move, 
feet carrying him toward her on autopilot — 
not a choice but a gravity, 
rationality overruled by the pull between them
```

**停住=最危险状态**：
```
frozen mid-motion, neither advancing nor retreating — 
the most dangerous state because emotion has passed the point of no return 
but the body hasn't committed — 
suspended between impulse and restraint, 
the tension at its absolute peak
```

### 20.7 焦距与亲密关系的提示词映射

**24-35mm广角——初识/疏离**：
```
24mm wide angle, full environmental context visible, 
two figures small in the frame separated by architecture and furniture — 
the space between them is the subject, not the people — 
loneliness of proximity, being near but unreachable
```

**50mm标准——日常/温柔**：
```
50mm natural perspective, the way human eyes actually see, 
no spatial distortion — 
intimate without being invasive, 
close without being predatory — 
the comfort of being truly seen at normal distance
```

**85-135mm长焦——暧昧/欲望**：
```
85mm portrait lens, spatial compression making the 2 meters between them 
feel like 20cm — distance collapsed optically, 
background dissolving into creamy bokeh — 
world disappearing, only two faces in focus, 
the frame itself choosing them over everything else
```

**焦外叙事——世界消失**：
```
background gradually dissolving from sharp to pure bokeh across the shot, 
as if the world is fading away — 
until only her face and his face exist in the plane of focus, 
everything else surrendered to blur — 
the lens deciding what matters
```

### 20.8 光影心理学提示词

**柔光=主观滤镜**：
```
soft diffused golden hour light wrapping around both figures, 
skin luminous, shadows gentle, 
the world seen through love's filter — 
reality softened at the edges, dreamlike quality, 
as if the light itself is choosing to be kind
```

**阴影=秘密**：
```
half her face lost in shadow, only one eye catching the light — 
the hidden half concealing what she's feeling, 
mystery in the unseen portion, 
danger in what the dark is keeping — 
shadow as confession and concealment simultaneously
```

**冷暖混合=理性世界中的情绪温度**：
```
cold blue ambient light filling the room (rationality, the real world), 
but warm golden light from a single bedside lamp falling on the 30cm 
between their faces (emotion, the private world) — 
two color temperatures coexisting like two hearts deciding whether to sync
```

**侧光切割=内心分裂**：
```
hard side light splitting his face into bright and dark halves, 
the division line running down his nose — 
what he shows the world vs what he feels, 
the light making visible what he's trying to hide
```

### 20.9 亲密戏提示词模板

**原则：拍情绪不拍动作——镜头重点顺序：手>后颈>肩膀>呼吸>头发>眼神>皮肤光线>正面身体**

**亲密戏开场——先建立安静**：
```
locked-off camera, 85mm, f/1.4 — 
extreme shallow depth of field, 
only the space between their hands in focus, 
everything else surrendered to bokeh — 
silence so complete you can hear the room breathing, 
air heavy with anticipation — 
no music, no sound, just two people and the charged centimeters between them
```

**手部特写——最亲密的非接触**：
```
macro close-up of his hand, fingers hovering 1cm above her wrist, 
the warmth of his palm creating a faint shadow on her skin — 
not touching but the heat transferring anyway, 
her pulse visible at the vein beneath his fingertips — 
the almost-contact more intimate than any grip
```

**呼吸节奏——靠近→停住**：
```
medium close-up, both profiles facing each other, 3cm apart, 
both breathing through slightly parted lips — 
his exhale becomes her inhale — 
neither closing the final distance — 
frozen on the edge of a decision, 
the held breath between them louder than any dialogue
```

**环境光线的亲密性**：
```
only light source: city neon filtering through sheer curtains, 
casting moving color bands across bare shoulders and tangled sheets — 
the room itself breathing with the city's pulse — 
shadows wrapping around bodies like a second skin, 
privacy created by darkness, intimacy amplified by what the light chooses to reveal
```

### 20.10 恋爱分镜五阶段完整提示词案例——便利店雨夜

**阶段：暧昧升温（Stage 2→3过渡）**

**镜头1——广角远景**：
```
24mm wide angle, establishing shot, 
rain pouring down, convenience store awning providing narrow shelter, 
two figures standing 1.5 meters apart under the small dry patch — 
rain wall surrounding them on three sides — 
the world reduced to this small dry island, 
rain as the only sound, both looking in different directions
```

**镜头2——女主手部+男主偷看**：
```
50mm, medium shot, she's looking down adjusting her wet sleeve cuff, 
fingers working the damp fabric — 
HE is watching her hands, eyes soft, gaze lingering — 
she senses the attention, her fingers slow down — 
she's aware he's looking, he's aware she knows — 
neither acknowledging the awareness
```

**镜头3——极慢推进（呼吸感镜头）**：
```
85mm, camera slowly pushing in at 0.2m per 4 seconds, 
as if drawn toward them involuntarily — 
the space between them compressing in the frame, 
rain sounds fading as if the audio is focusing with the lens — 
air becoming audible, silence between raindrops
```

**镜头4——递热饮+手指碰触**：
```
85mm close-up on hands, he offers a hot drink, 
she reaches for it — fingertips graze during the transfer — 
both hands freeze for 0.5 seconds, neither pulling away, 
neither acknowledging — 
the heat from the cup and the heat from contact indistinguishable
```

**镜头5——停顿（空气变化）**：
```
locked-off camera, neither speaks for 3 full seconds after the touch, 
only the electric hum of the convenience store — 
she's holding the cup with both hands, steam rising between them, 
he's looking at the rain — 
both pretending the last 5 seconds didn't happen, 
both completely changed by them
```

**镜头6——"谢谢"**：
```
100mm tight close-up on her face, side angle, 
she says "thank you" almost inaudibly, 
eyes not meeting his — looking at the cup or the rain, anywhere but him — 
but the corners of her mouth betray the smallest upward curve, 
a smile she's trying to suppress, 
the word "thanks" meaning something else entirely
```

**镜头7——停留（留白收尾）**：
```
50mm, camera slowly pulling back, 
rain continuing, city continuing, world continuing — 
but something has shifted in the air between these two people — 
the frame holds them together in the small dry space, 
rain surrounding like a private world — 
nothing happened, everything happened
```

### 20.11 王家卫式恋爱提示词模板

**空间阻隔——永远差一点的遗憾感**：
```
narrow corridor, she's walking ahead, he's behind — 
never side by side, always one following the other — 
wet walls reflecting neon, 
door frames they pass through one at a time — 
always separated by architecture, 
always almost together but never together — 
the geometry of the space preventing what the hearts want
```

**慢动作与时间拉长——爱情改变时间感**：
```
120fps slow motion, she turns to look at him — 
the 0.5 second of her head turning stretched into 3 seconds of cinema, 
hair catching the light, 
her eyes finding his in the stretched time — 
love makes time expand, 
the lens experiencing what the heart experiences — 
a single moment becoming an eternity
```

**重复动作——无法拥有的循环**：
```
the same gesture repeated — him arriving at the same spot at the same time, 
her ordering the same drink at the same counter — 
rituals of proximity without contact, 
routines that create a relationship without a relationship — 
the repetition itself becoming the love story
```

### 20.12 暧昧/恋爱/亲密戏提示词自查清单

1. **双力结构**：每个暧昧镜头是否同时存在"靠近"和"克制"两种信号？
2. **视线精度**：视线类型是否明确（偷看/余光/反射/擦肩/对视后移开）而非笼统的"look at"？
3. **停留时间**：视线停留是否精确到秒数（如"2 seconds too long"）而非"longingly"？
4. **呼吸感镜头**：运镜是否随情绪状态变化（靠近→推进/发现→停止/失控→微晃）？
5. **空间距离**：是否通过障碍物/距离/差一点碰到来外化心理距离？
6. **"差一点"原则**：是否用未完成动作替代已完成动作？
7. **身体语言深度**：肢体动作是否标注了表面含义vs深层心理？
8. **焦距选择**：焦距是否匹配恋爱阶段（广角=疏离/中焦=日常/长焦=欲望）？
9. **光影情绪**：光线是否服务于情绪（柔光=梦幻/阴影=秘密/冷暖混合=理性中的情绪）？
10. **亲密戏重点**：镜头是否对准手/后颈/呼吸等情绪部位而非正面身体？
11. **呼吸与停顿**：亲密戏是否有"靠近→停住→不立刻继续"的节奏？
12. **焦外叙事**：心动阶段背景是否在失焦——世界在消失？
13. **声音留白**：是否有安静/极轻声/环境音放大来创造私人空间感？
14. **假装正常**：角色是否在"假装什么都没发生但身体在泄漏"？

## 二十一、剧本→视觉资产提取提示词技巧

### 21.1 角色设定图中文提示词模板

角色设定图是AI绘图的第一步产物，用于锁定角色外观。中文提示词需要覆盖六维拆解法的全部维度，但以自然语言而非表格形式输出：

**完整模板**：
```
[姓名]，[年龄]岁，[性别]，[身份]。
[身高]cm，[肩型+体型+剪影描述]，肤色[具体色名+质感]。
面部：[颧骨描述]，[下颌线描述]，[眼窝深度]，[眉骨描述]，[鼻梁描述]，[嘴唇厚度+自然走向]。
发型：[发色+发量+款式+分缝+光泽度+长度+鬓角处理]。
身穿[服装颜色+面料+织法+光泽度+领型/驳头+扣位+剪裁+袖口细节+配套衬衫/领带/鞋]。
标志性配饰：[道具1完整描述+佩戴位置+光线交互]，[道具2完整描述]。
[核心气质视觉化3-4句]，[常见表情基态1-2句]，[标志性动作1句]。
全身远景，正面站立，纯色背景，真人写实电影质感，角色设定表，
服装面料纹理清晰，面部特征精确，不要文字，不要水印，不要多余人物。
```

**反例vs正例**：

| 维度 | ❌ 笼统写法 | ✅ 精度写法 |
|------|-----------|-----------|
| 气质 | "气质高贵" | "目光从略高处落下，动作极缓慢，占位宽展" |
| 西装 | "黑色西装" | "深炭黑色精纺羊毛西装，平驳头7cm，收腰剪裁" |
| 发型 | "短发" | "深棕色背梳无分缝，中等光泽，鬓角修剪至耳上" |
| 表情 | "表情冷酷" | "上眼睑半垂遮住虹膜上1/4，视线焦点在对方眉心" |
| 道具 | "戴着手表" | "左腕42mm铂金计时码表，侧光下表盘反射冷白光斑" |

### 21.2 场景概念图中文提示词模板

场景概念图锁定空间/光影/材质，是9机位图集的前置产物：

**完整模板**：
```
[场景名称]。[面积]㎡[形状]空间，[关键家具位置+材质]，
[出入口位置+类型]，[窗户/采光面位置+数量]。
[时间]，[主光描述：类型+色温+方向+照射范围]，
[辅光描述：类型+色温+方向+照射范围]，[氛围词2-3个]。
地面：[材质+颜色+反射度]；墙面：[材质+颜色]；
[关键家具1：材质+颜色+表面质感]；[关键家具2：同上]；
[装饰/植物/其他细节]。
[建议拍摄角度，如"从门口向纵深方向45°斜角拍摄"]。
场景概念图，真人短剧质感，真实物理光影，空间层次清晰，
电影级构图，不要人物，不要文字，不要水印。
```

**场景概念图的常见错误**：

| 错误类型 | 示例 | 修正 |
|----------|------|------|
| 无色温 | "暖色灯光" | "台灯暖黄3500K，窗外冷蓝5800K，冷暖对冲" |
| 无材质 | "木质地板" | "深色胡桃木实木地板，哑光，可见木纹" |
| 无反射 | "玻璃窗户" | "落地玻璃幕墙，夜晚反射室内灯光形成半透明叠影" |
| 无纵深 | "办公室" | "60㎡矩形空间，办公桌在远端1/3处，门口近端形成纵深" |

### 21.3 道具清单提示词——保持跨镜头一致性

道具清单不直接生成图像，但在角色设定图和分镜提示词中必须精确引用：

**道具描写的4层精度**：

| 层级 | 内容 | 示例（合同文件） |
|------|------|-----------------|
| 1.材质 | 物体由什么构成 | 120g铜版纸，轻微泛黄 |
| 2.颜色+形状 | 视觉外观 | A4尺寸，白色纸面，黑色印刷体，红色骑缝章 |
| 3.尺寸+位置 | 物理规格和放置 | 平铺在桌面右侧，右上角微翘，左下角有咖啡渍 |
| 4.光线交互 | 在当前光源下的表现 | 台灯暖光打在纸面上，骑缝章红色在暖光下偏橙，纸张边缘投下细长阴影 |

**常见道具类型速填**：

| 道具类型 | 必含描写 | 光线交互 |
|----------|---------|---------|
| 戒指 | 材质+形状+宝石+佩戴手指 | 金属表面反射/宝石折射 |
| 合同/文件 | 纸张克数+颜色+印章+装订 | 纸面反光/印章颜色偏移 |
| 手机 | 品牌+型号+壳色+屏幕状态 | 屏幕光映在脸上/壳面反光 |
| 录音笔 | 颜色+材质+指示灯+放置位置 | 指示灯红/绿光点 |
| 车钥匙 | 品牌+材质+挂件 | 金属面反射/挂件晃动 |
| 酒杯 | 材质+液体颜色+冰块+持握方式 | 液体折射/冰球放大桌面纹理 |
| 文件袋 | 颜色+材质+封口方式+标签 | 牛皮纸哑光/标签反光 |

### 21.4 提取工作流中的提示词质量控制

**角色设定图提示词自检**：
1. 六维是否全覆盖（体型/面部/发型/服饰/道具/体态）？
2. 服饰是否达到7要素精度（颜色/面料/领型/扣位/剪裁/袖口/配套）？
3. 气质是否视觉化替代了抽象词？
4. 表情是否写了基态（默认脸）而非只有笼统情绪词？
5. 道具是否写了光线交互？
6. 结尾是否包含"不要文字，不要水印，不要多余人物"？

**场景概念图提示词自检**：
1. 空间结构是否含面积+形状+家具位置+出入口？
2. 光影是否含主光+辅光+色温？
3. 材质是否含地面+墙面+至少2件关键家具？
4. 是否有纵深描述（空间层次）？
5. 结尾是否包含"不要人物，不要文字，不要水印"？

**道具清单自检**：
1. 每个道具是否有4层精度（材质/颜色形状/尺寸位置/光线交互）？
2. 一致性红线是否明确（不可改变的3个核心特征）？
3. 叙事功能是否写明（为什么这个道具重要）？

## 二十二、AI视频生成技术参数与负提示实战

### 22.1 摄影机机身+光圈后缀的实战用法

每个视频提示词末尾必须包含摄影机技术参数后缀，这不是装饰——AI生成器在训练数据中见过大量标注了机身型号的真实电影帧，指定机身会激活对应的色彩科学和画面风格。

**标准后缀**：
```
Shot on Arri Alexa 65, T2.8, film grain, 4k, ultra photorealistic, --ar 16:9
```

**后缀调整策略**：

| 场景类型 | 机身 | 光圈 | 颗粒 | 宽高比 |
|----------|------|------|------|--------|
| 电影级室内 | Arri Alexa 65 | T2.8 | film grain | --ar 16:9 |
| 电影级宽银幕 | Arri Alexa 65 | T2.8 | film grain | --ar 21:9 |
| 竖屏短剧 | Arri Alexa Mini LF | T2.0 | subtle film grain | --ar 9:16 |
| 纪实/手持 | Sony Venice 2 | T1.4 | heavy film grain, handheld | --ar 16:9 |
| 环境建立全景 | Arri Alexa 65 | T8.0 | film grain | --ar 16:9 |

**竖屏短剧（9:16）的构图调整**：
竖屏不是横屏的裁剪版——构图逻辑完全不同：
- 横屏：水平纵深→角色+背景水平排列→180°轴线水平建立
- 竖屏：垂直纵深→角色上下排列→前景/中景/后景垂直堆叠
- 竖屏特写占比应更高（竖屏观众手机距离更近，大脸=沉浸感）
- 竖屏双人构图：上下排列而非左右（前景人物上半身+后景人物下半身）
- 竖屏环境建立：从地面到天空的垂直展示（地面→角色→天空三层）

### 22.2 Negative Prompt实战库

Negative Prompt是提示词的"免疫系统"——正提示词定义"画什么"，负提示词定义"不画什么"。两者配合才能精确控制输出。

**组合式负提示模板**：

```
--no blurry, low quality, watermark, text, logo, signature,
extra fingers, extra limbs, deformed hands, mutated, disfigured, bad anatomy,
dead eyes, crossed eyes, plastic skin, doll-like,
flat lighting, overexposed, harsh flash,
cartoon, anime, illustration, painting, 3d render
```

**按场景裁剪负提示**（不需要每次都写全部——根据场景类型选择性添加）：

**面瘫角色全套负提示**（最严格）：
```
--no smile, raised eyebrows, open mouth, emotional outburst, micro-expression,
dead eyes, crossed eyes, asymmetric face, plastic skin,
cartoon, anime, illustration, blurry, watermark
```

**动作戏全套负提示**：
```
--no slow motion blur, frozen pose, static composition, blurry,
extra fingers, deformed hands, mutated,
flat lighting, cartoon, anime, illustration, watermark
```

**恋爱/暧昧全套负提示**：
```
--no explicit content, nudity, aggressive pose, violent gesture,
dead eyes, crossed eyes, plastic skin,
flat lighting, overexposed, cartoon, anime, watermark
```

**竖屏短剧全套负提示**：
```
--no horizontal composition, wide landscape, letterboxing,
blurry, low quality, watermark, text,
extra fingers, deformed hands, bad anatomy,
dead eyes, plastic skin, cartoon, anime
```

### 22.3 专业电影打光位置提示词实战

**核心规则**：提示词中的灯光描述必须使用标准电影打光术语（光位名+视觉语言+情绪效果），禁止使用模糊描述如"cinematic lighting"或"good lighting"。

**八大光位提示词速查**：

| 光位 | 提示词关键词 | 负提示 |
|------|------------|--------|
| 前侧光 | `front-side Rembrandt light, 45-degree key, triangular cheek highlight, sculpted facial contours` | `--no flat lighting, centered shadow` |
| 顶光 | `overhead top light, harsh downcast, eye socket shadows, nose shadow downward, upper-lit lower-dark` | `--no soft diffused, even illumination, gentle shadows` |
| 正侧光 | `split side light, 90-degree key, half-face illumination, dramatic chiaroscuro split` | `--no soft transition, dual-side lighting, flat fill` |
| 逆光 | `strong backlight, silhouette rim glow, face in shadow, light bleeding around edges` | `--no front illumination, flat lighting, visible facial detail` |
| 蝴蝶光 | `butterfly Paramount light, overhead elevated, symmetrical nose shadow, even facial illumination` | `--no harsh shadows, side shadow, dramatic contrast` |
| 顺光 | `front flat light, even illumination, minimal shadows, objective documentation feel` | `--no dramatic shadow, side lighting, chiaroscuro` |
| 底光 | `under light from below, inverted shadows, unnatural upward illumination, horror distortion` | `--no natural lighting, top light, even illumination` |
| 侧逆光 | `rim kicker light, 135-degree back-side, sharp edge highlight, 3D separation from background` | `--no front light, even illumination, flat subject` |

**光位组合提示词模板**：

经典前侧组合（专业对话）：
```
[LIGHTING] front-side Rembrandt key (camera-left 45°, elevated 30°), 
soft front fill at 1:3 key-to-fill ratio, subtle rim kicker from camera-right,
creating signature Rembrandt triangle on cheek, sculpting jawline and cheekbones,
conveying professional competence and quiet authority,
skin: SSS visible at nose edges and ear rims, chromatic zonation under warm key,
atmospheric: dust motes in light shaft, subtle window light pattern on wall
```

压迫审判组合（顶光独裁）：
```
[LIGHTING] overhead top light as sole source (directly above, hard quality),
no fill, no rim, complete overhead dominance,
eye sockets deep in shadow, nose casting sharp downward shadow, 
upper face illuminated lower face swallowed by darkness,
creating inquisitional oppression, power crushing down from above,
skin: chromatic zonation critical — upper face lit (SSS visible), lower face dark (edge light at jawline),
eyes: conscious intent behind shadowed eyes, NOT dead eyes (mandatory声明),
cinematic reference: The Godfather overhead style
```

戏剧分裂组合（正侧光道德困境）：
```
[LIGHTING] split side light as key (camera-left 90°, hard quality),
no fill or minimal fill at 1:8 ratio, rim kicker from opposite side,
half face in bright illumination, half in deep shadow, dramatic chiaroscuro,
conveying moral duality, inner conflict made visible,
skin: SSS visible on lit side, dark side maintained with faint edge light,
eyes: catchlight only on lit side, dark side eye must still declare conscious intent,
cinematic reference: Citizen Kane dramatic split
```

希望剪影组合（逆光牺牲）：
```
[LIGHTING] strong backlight as dominant source (directly behind character, elevated 15°),
very weak front fill at 1:8 ratio (just enough for facial recognition),
silhouette rim glow around head and shoulders, face in shadow with faint features,
light bleeding through hair edges, creating halo effect,
conveying sacrifice, transcendence, hope beyond darkness,
skin: edge light (3D proof) critical — rim light on nose/jaw/cheek edges, SSS faint at ear rims,
eyes: shadowed but alive, catchlight from back-reflected ambient,
cinematic reference: Blade Runner 2049 silhouette / Arrival backlight
```

危险逼近组合（侧逆光追踪）：
```
[LIGHTING] rim kicker as key (camera-right 135°, slightly elevated 20°),
weak front fill at 1:4 ratio,
sharp edge light on one side of face, other side in shadow, 
3D separation from background, character emerging from darkness,
conveying imminent danger, uncertain threat, hunted,
skin: edge light on lit side (SSS + micro-texture visible), dark side maintained,
eyes: single catchlight from rim direction, alert and searching,
atmospheric: urban ambient reflections, wet surface light scatter, neon edge glow
```

优雅经典组合（蝴蝶光仪式）：
```
[LIGHTING] butterfly Paramount light as key (directly above, slightly forward, elevated 45°),
soft front fill at 1:2 ratio, subtle rim from both sides,
symmetrical butterfly shadow under nose, even facial illumination,
defined jawline, glamorous eye illumination,
conveying elegance, ritual, timeless beauty,
skin: SSS visible at thin skin areas under even illumination, chromatic zonation preserved,
eyes: dual symmetric catchlights (butterfly signature), bright and engaging,
cinematic reference: Gone with the Wind glamour lighting
```

**光位与皮肤六层的提示词联动**：

| 光位 | 皮肤声明重点 | 必须声明的层级 |
|------|------------|--------------|
| 前侧光 | SSS最明显（鼻翼/耳廓透光），色区差异可见 | 1(SSS)+2(微纹理)+4(色区差异) |
| 顶光 | 上下半脸明暗分界=色区差异最关键 | 4(色区差异)+5(边缘光3D)+1(SSS上半脸) |
| 正侧光 | 亮面全5层，暗面只保边缘光+色区 | 5(边缘光3D)+4(色区差异) |
| 逆光 | 边缘光3D=唯一的3D证据 | 5(边缘光3D)+1(SSS耳廓) |
| 蝴蝶光 | 均匀光下色区差异更关键（无阴影遮掩） | 4(色区差异)+2(微纹理)+3(油汗层) |
| 顺光 | 最考验微纹理和色区差异（无阴影帮衬） | 2(微纹理)+4(色区差异)+3(油汗层) |
| 底光 | 违反自然光=皮肤声明防止恐怖变塑料 | 1(SSS)+4(色区差异)+声明`still natural skin, NOT wax figure` |
| 侧逆光 | 边缘光侧=SSS+微纹理最佳展示 | 1(SSS)+2(微纹理)+5(边缘光3D) |

**光位与导演风格的自动映射提示词**：

选择导演风格时，光位自动继承：

| 导演 | 偏好光位 | 提示词自动声明 |
|------|---------|---------------|
| 诺兰 | 前侧光+冷灰自然光 | `front-side Rembrandt key, cool desaturated natural light, overcast quality` |
| 维伦纽瓦 | 逆光+体积光+单源 | `strong backlight with volumetric scatter, single shaft source, Deakins-style diffused rim` |
| 伯格曼 | 正侧光+高反差 | `split side light, high contrast, single hard source, Fårö window light` |
| 斯皮尔伯格 | 逆光+蝴蝶光+体积光 | `backlight volumetric haze, butterfly key for close-ups, golden hour magic light` |
| 王家卫 | 侧逆光+霓虹 | `rim kicker with neon color cast, mixed color temperature, practical neon backlight` |
| 奉俊昊 | 顺光→突然顶光 | `front flat light (normal), sudden shift to overhead top light (violence)` |
| 黑泽明 | 自然侧光+元素光 | `natural side light, weather elements as light source, rain backlight, dust scatter` |
| 张艺谋 | 蝴蝶光+色彩饱和光 | `butterfly Paramount key, saturated complementary color lighting, lantern warm glow` |

### 22.4 Lip Sync口型同步提示词

角色说话时，AI视频生成器的口型同步是最容易穿帮的环节。必须在提示词中显式声明口型状态。

**有台词镜头的提示词结构**：
```
[标准锚定段 + 动作/构图段],
speaking with natural lip movements, mouth forming syllables matching dialogue rhythm,
jaw moving subtly as in real speech, [情绪专属口型补充],
no exaggerated mouth opening, lips maintaining natural tension
Shot on Arri Alexa 65, T2.8, film grain, 4k, ultra photorealistic --ar 16:9
--no frozen mouth, open mouth without speech, exaggerated lip movements, ventriloquist effect
```

**情绪口型速查**：

| 情绪 | 口型关键词 | 禁止项 |
|------|-----------|--------|
| 冷静陈述 | `minimal jaw movement, tight lip closure between syllables` | `no wide mouth opening` |
| 低声威胁 | `barely perceptible lip movement, jaw locked, words through nearly closed teeth` | `no open mouth shouting` |
| 愤怒质问 | `teeth slightly visible, jaw thrust forward 2mm, clipped syllables, spittle at corner of mouth` | `no calm relaxed mouth` |
| 哽咽 | `trembling lower lip, irregular breathing pauses, chin quivering, wet eyes` | `no steady speech rhythm` |
| 假笑应答 | `smile not reaching eyes, zygomaticus major contracted but orbicularis oculi relaxed, measured syllables` | `no genuine warm smile` |

### 22.4 Motion Strength实战值

不同AI视频平台的Motion Strength参数名称和范围不同，但核心逻辑一致：控制画面中运动的幅度。

**场景→Motion Strength映射**：

| 场景 | 值(1-10) | 提示词补充 | 负提示 |
|------|---------|-----------|--------|
| 面瘫/静止 | 3 | `extremely subtle breathing motion (<5cm drift)` | `--no sudden movement, head turn, gesture` |
| 对话 | 5 | `natural micro-movements, occasional slight head tilt` | `--no large gesture, standing up, walking` |
| 暧昧靠近 | 7 | `hands slowly moving closer, body weight shifting forward` | `--no abrupt movement, running, jumping` |
| 打斗/追逐 | 9 | `rapid directional movement, impact physics, body momentum` | `--no frozen pose, static, slow` |

**Seed值一致性策略**：
```
场景1所有镜头: --seed 42871
场景2所有镜头: --seed 42872
角色设定图: --seed 42870
```
- 同场景用相同Seed=视觉基因一致
- 不同场景用递增Seed=便于记录和回溯
- 角色设定图用专用Seed=后续所有该角色镜头引用

### 22.5 即时分镜的提示词产出策略

用户给一段故事就出分镜时，提示词需要快速生成而不牺牲质量。以下是加速策略：

**锚定段预生成**：收到故事后，先用1-2句提取角色核心视觉特征，生成锚定段模板——后续每个镜头只替换变化段：
```
锚定段: [NAME] — [6-dim core visual], [SCENE] — [lighting + atmosphere + material]
变化段: [shot-specific: action, camera, composition]
后缀段: Shot on Arri Alexa 65, T[aperture], film grain, 4k --ar [ratio] --no [neg list]
```

**场景判断速查**（不追问，自动推断）：

| 故事关键词 | 自动推断 |
|-----------|---------|
| 雨/夜/暗 | 夜景冷调T2.0+手持+film grain heavy |
| 办公室/会议 | 室内中景T2.8+冷白荧光+竖屏或横屏 |
| 街道/追逐 | 手持T4.0+运动模糊+9:10或16:9 |
| 卧室/亲密 | 暖光T1.4+极浅景深+柔和侧光 |
| 屋顶/天台 | 逆光剪影T5.6+风+广角 |

### 22.6 Cliffhanger的提示词实现

Cliffhanger最后一个镜头需要特殊的提示词处理——它的视觉任务不是"讲完故事"而是"制造中断感"：

**四种Cliffhanger的提示词模板**：

**悬念型**（推向关键物体）：
```
[CAMERA: slow dolly-in over 6 seconds toward [key object]],
[COMPOSITION: starting medium shot, ending extreme close-up on [detail]],
[LIGHTING: dramatic contrast, key object in spotlight],
[SOUND: heartbeat rhythm, ambient silence],
emotion building to revelation moment — CUT BEFORE reveal,
Shot on Arri Alexa 65, T2.0, film grain, 4k --ar [ratio]
--no complete reveal, full information, resolution
```

**反转型**（矛盾元素出现）：
```
[CAMERA: static wide shot, stable composition],
[SUDDEN: [contradictory element] enters frame edge at 4.5sec mark],
[REACTION: no reaction — character hasn't noticed yet],
[EMOTION: dread realization dawning],
Shot on Arri Alexa 65, T2.8, film grain, 4k --ar [ratio]
--no character noticing, resolution, explanation
```

**选择型**（定格在选择瞬间）：
```
[CAMERA: over-shoulder looking at two options],
[COMPOSITION: [option A] left frame, [option B] right frame, character centered],
[MOMENT: hand reaches out but freezes before contact],
[SOUND: breathing stops],
Shot on Arri Alexa 65, T2.8, film grain, 4k --ar [ratio]
--no choice made, hand touching either option, resolution
```

**暴露型**（危险逼近）：
```
[CAMERA: reverse angle showing threat approaching],
[COMPOSITION: character in foreground unaware, threat in background growing],
[RHYTHM: slow push-in accelerating slightly],
[SOUND: [threat sound] growing louder — CUT],
Shot on Arri Alexa 65, T1.4, film grain, 4k --ar [ratio]
--no threat reaching character, confrontation, escape
```

## 二十三、单帧叙事密度AI提示词技巧

### 23.1 叙事密度三层→提示词三层映射

叙事密度的焦点层/过渡层/虚化层在提示词中有对应的描写策略——不是均匀分配笔墨，而是按层次分配信息密度：

**焦点层提示词（最高信息密度）**：
```
[CHARACTER] — [六维锚定 + 痕迹证据链: each mark has cause]:
disheveled auburn hair with loose strands clinging to forehead and cheeks (wind/exertion),
mud stains on back of hands (touched ground — fell/dug/crawled),
worn gold braid trim at neckline with visible fraying (formerly fine, now declining),
skirt fabric pooling around legs with realistic gravity drape (physical truth of crouching)
```

**过渡层提示词（中等信息密度，每个元素1项叙事功能）**：
```
[MID-GROUND]: muddy ground scattered with dead leaves and broken twigs (late autumn, recent rain),
several tree stumps showing axe cuts (someone harvests wood here = human economic activity),
```

**虚化层提示词（低信息密度但不可省略）**：
```
[BACKGROUND bokeh]: dark livestock grazing (pastoral economy, not wilderness),
distant trees fading into fog (unknown direction = unpredictable threat)
```

### 23.2 零装饰原则的提示词执行

提示词中每写一个视觉元素，必须同时声明它的叙事理由——如果无法声明，该元素就是装饰，应删除：

| 装饰性写法（❌） | 叙事性写法（✅） | 叙事理由 |
|-----------------|-----------------|---------|
| "scattered leaves" | "dead leaves and broken twigs on muddy ground, recent rain" | 时间锚定+气候证据 |
| "trees in background" | "tree stumps with axe-cut marks among standing trunks" | 人的痕迹+经济证据 |
| "animals" | "dark cattle grazing at pasture edge, soft bokeh" | 生活方式锚定 |
| "messy hair" | "loose strands clinging to forehead, unwashed, wind-tangled" | 状态证据=无暇整理 |
| "dirty hands" | "mud caked on knuckles and under fingernails, recently gripped earth" | 行为证据=触摸过地面 |
| "old clothes" | "gold braid trim fraying at neckline, coarse linen worn thin at elbows" | 阶层证据=曾经体面现在下坠 |

### 23.3 角色痕迹提示词模板

角色痕迹是叙事密度的核心——痕迹=故事在身体上的刻录。以下是痕迹类型的提示词写法：

```
[TRACE TYPE] — [physical description] — [cause inference]:

DIRT: mud caked on [body part], [specific shade: dark brown/black/grey], 
[distribution: even splatter/directional smear/finger-shaped wipe],
suggesting [cause: fell to ground / dug with hands / crawled through mud]

WEAR: [garment detail] showing [wear type: fraying/thinning/discoloration/patching],
[at specific location: neckline/elbows/cuffs/hem],
suggesting [cause: long use / former quality now declining / repeated stress]

DISHEVELMENT: hair [state: tangled/wind-blown/clinging to skin],
[specific: strands across forehead/stuck to damp cheeks/knotted at nape],
suggesting [cause: no time to groom / recent exertion / exposure to wind/rain]

DAMAGE: [injury/damage type: scratch/bruise/torn fabric/broken stitching],
[at location with specificity], 
[age: fresh scab/fading yellow/old scar],
suggesting [cause: recent conflict / long-term hardship / specific incident]
```

### 23.4 色彩锚点提示词

色彩锚点=用唯一暖色/高饱和色锚定视觉焦点的提示词策略：

**单锚点（推荐）**：
```
[COLD DESATURATED BASE]: overall desaturated cool-grey palette (5800-6500K),
[SINGLE WARM ANCHOR]: wine-red coarse linen tunic — the only warm tone in frame,
drawing eye naturally to character as emotional focal point,
all other colors подчиняются (subordinate to) this anchor
```

**双锚点（谨慎使用）**：
```
[COLD BASE]: cool desaturated palette,
[WARM ANCHOR 1]: wine-red tunic on character A — emotional focus,
[WARM ANCHOR 2]: amber candlelight on table — hope/safety marker,
two anchors creating visual dialogue: character vs sanctuary
```

**禁止**：三个及以上暖色锚点=视觉焦点分散=叙事力度消散

### 23.5 环境叙事五层证据的提示词写法

每个非动作场景的提示词中，过渡层+虚化层必须显式写出至少3/5层证据：

```
[ENVIRONMENT EVIDENCE]:
TIME TRACES: [tree stumps with axe marks = logging history; worn stone steps = generations of use]
HUMAN TRACES: [scattered tools = someone works here; livestock = pastoral economy]
ECONOMIC TRACES: [coarse fabric not silk = lower class; thatched roof not tile = poverty]
CLIMATE TRACES: [muddy ground = recent rain; bare branches = winter approaching]
THREAT TRACES: [fog obscuring distant tree line = unknown direction; no visible shelter = exposure]
```

**证据层与已有规范的关系**：
- 环境叙事五层证据是"环境参与叙事"（打斗规范中的环境叙事）的**静态版本**——打斗场景中环境参与动作，静止场景中环境提供证据
- 与"场景概念图"提取规范的关系：五层证据是概念图提示词中必须覆盖的叙事维度
- 与"道具清单"的关系：环境证据中的"人的痕迹"和"经济痕迹"=场景级道具

## 二十四、色彩叙事体系AI提示词技巧

### 24.1 色温=空间深度的提示词实现

色温梯度在提示词中通过色温声明和颜色命名实现——不是写"warm and cool"，而是显式声明每层的色温值：

**三梯度提示词模板**：
```
[BACKGROUND — 6500-8000K]: cool blue-grey window light / cold fog receding into distance / 
shadow areas with blue undertone (NOT warm shadow)
[MID-GROUND — 3500-5000K]: warm pink/brown/skin-tone character zone, 
character fabric color bridging skin warmth to environment warmth
[FOREGROUND — 2500-3500K]: hot golden light source, warm highlights on character, 
golden rim light on hair edges, specular reflections on glossy surfaces
```

**常见错误**：
```
❌ "warm atmosphere" — 无色温梯度=空间扁平
✅ "cool blue-grey shadows (7000K) receding, warm pink mid-ground (4000K), hot golden highlights (2800K) advancing"
```

### 24.2 色桥的提示词写法

色桥=角色服装色同时桥接肤色和环境色。提示词中必须声明这种桥接关系：

**色桥声明模板**：
```
[CHARACTER FABRIC as COLOR BRIDGE]: 
[skin tone: warm peach/golden/olive] → 
[fabric: rose-pink cotton — bridging skin warmth to floral environment] → 
[environment: pink-lavender flower field],
fabric color chosen to chromatically connect character to environment,
creating sense of belonging rather than insertion
```

**不同环境的色桥提示词**：

| 环境 | 色桥提示词 |
|------|-----------|
| 花海 | `rose-pink fabric bridging warm skin to pink-lavender flower tones` |
| 雨夜 | `slate-blue coat bridging cool skin to cold rain environment — character belongs in the cold` |
| 暖金室内 | `cream-white silk bridging golden skin to warm amber interior light` |
| 森林 | `olive-green linen bridging warm skin to deep forest canopy — concealment as narrative` |
| 夜景 | `character in warm burgundy — deliberate chromatic departure from cold night, only warm element = visual anchor` |

### 24.3 同色系材质差的提示词

同色系场景必须通过材质差异制造层次——提示词中必须声明同一色相下不同材质的光学行为：

**同色系材质差提示词模板**：
```
[MONOCHROMATIC LAYERING via material]:
pink satin dress — glossy specular highlights creating "hot" points,
pink cotton shirt — diffuse soft reflection, visible weave texture,
pink flower petals — matte surface, subsurface translucency, light-absorbing,
pink chiffon overlay — translucent, color-shifting with background,
warm skin — subsurface scattering, unique living glow,
same hue family, differentiated by light-surface interaction NOT by hue shift
```

**常见错误**：
```
❌ "pink dress and pink flowers" — 同色同质=画面扁平
✅ "pink satin dress with glossy reflections alongside matte pink flower petals, 
pink cotton shirt with visible weave texture creating mid-tone, 
all same hue differentiated by material light behavior"
```

### 24.4 冷呼吸孔的提示词放置

冷元素在提示词中的位置很关键——放在环境描写段而非角色描写段：

**呼吸孔放置模板**：
```
[ENVIRONMENT]: [大面积暖色描述...], 
[COLD BREATHING HOLE 5-10%]: cool blue-grey window light visible in upper left background 
/ green foliage stems providing chromatic rest / shadow areas with subtle blue undertone,
cold element giving eyes a place to rest within warm composition
```

**呼吸孔面积控制**：
- 5%：`subtle cool blue undertone in shadow areas`——观众几乎不意识到但能感知
- 10%：`cool blue-grey window light in background, small but present`——显性冷色点
- 20%+：`cold blue-grey environment occupying left third of frame`——冷暖对峙（撞色型）

### 24.5 光源色总开关的提示词写法

光源色必须作为提示词中最早声明的色彩参数——它决定后续所有颜色的温度：

**光源声明模板**：
```
[LIGHT SOURCE — MASTER PALETTE SWITCH]:
primary light: [type] at [color temperature], [direction], [coverage],
THIS DETERMINES ALL SUBSEQUENT COLOR TEMPERATURES:
warm gold backlight at 3200K → entire palette shifts warm,
skin tones golden, shadows cool-blue by absence of warm light,
fabric colors shift toward warm end of their hue range
```

**五种光源类型的提示词**：

| 光源 | 提示词 |
|------|--------|
| 球灯/台灯 | `single warm yellow (2800K) spherical light source overhead, local illumination creating warm pool in cold environment, dramatic chiaroscuro` |
| 逆光 | `warm golden (3200K) backlight from upper right, rim lighting hair edges, lens flare, overall warm wash, figure silhouetted then revealed by edge light` |
| 散射自然光 | `soft diffused warm daylight (4500K) from large window, even illumination, gentle shadow transitions, no harsh contrast` |
| 侧光 | `warm golden (3500K) side light from left, half-face illumination, dramatic shadow on right, intimate chiaroscuro` |
| 冷色光源 | `cold blue (7000K) fluorescent overhead, clinical wash, no warmth, skin appearing desaturated, surveillance atmosphere` |

### 24.6 六型调色板的提示词速查

**暖浸型**（梦幻/恋爱/治愈）：
```
[CATEGORY: Warm Immersion]
warm golden backlight at 3200K, overall warm pink-purple monochromatic palette,
character rose-pink fabric bridging skin to floral environment,
material differentiation: satin glossy + cotton diffuse + petal matte,
cold breathing hole 5%: green foliage stems, subtle blue in shadow creases,
Shot on Arri Alexa 65, T2.0, film grain, 4k --ar 16:9
--no cold dominant areas, harsh contrast, blue highlights, clinical lighting
```

**冷暖撞色型**（孤独/庇护/对比）：
```
[CATEGORY: Warm-Cold Clash]
cold blue-grey environment (7000K ambient), single warm yellow (2800K) sphere light creating local warm zone,
character in warm fabric within light pool — only warmth in cold world,
chiaroscuro contrast between warm island and cold ocean,
cold breathing hole 30%+: blue-grey windows/walls/fog surrounding warm light pool,
Shot on Arri Alexa 65, T2.8, film grain, 4k --ar 16:9
--no even lighting, warm shadows, flat illumination
```

**暖调透气型**（亲密/日常/温柔）：
```
[CATEGORY: Warm with Breath]
warm golden side light at 3500K, predominantly warm palette with soft tonal transitions,
small cold breathing hole 10%: sliver of blue sky through window / cool shadow under chin,
character warm fabric chromatically connected to environment,
gentle contrast, no harsh drama,
Shot on Arri Alexa 65, T2.0, film grain, 4k --ar 16:9
--no cold dominant areas, stark contrast, blue tint
```

**温度梯度型**（史诗/叙事/纵深）：
```
[CATEGORY: Temperature Gradient]
cold blue-grey fog in far background (7000K) → warm mid-ground with character (4000K) → 
hot golden foreground highlights (2800K), 
temperature gradient creating spatial depth through color temperature alone,
character zone as warm island between cold past and hot future,
cold breathing hole 15%: background fog,
Shot on Arri Alexa 65, T2.8, film grain, 4k --ar 16:9
--no flat temperature, even warmth, uniform lighting
```

**三色三角型**（丰富/活力/产品）：
```
[CATEGORY: Triadic Triangle]
warm pink character fabric + golden light source + deep purple accent flowers,
triadic color relationship creating visual richness and energy,
pink (character) + yellow (light) + purple (depth) = balanced triangle,
each color occupying roughly equal visual weight,
cold tendency in purple element providing 15% breathing hole,
Shot on Arri Alexa 65, T2.8, film grain, 4k --ar 16:9
--no monochromatic flatness, single dominant hue
```

**冷浸型**（恐惧/疏离/未来）：
```
[CATEGORY: Cold Immersion]
cold blue (7000K) overhead fluorescent light, desaturated cold palette,
skin appearing pale and clinical, no warm highlights,
optional warm breathing hole 5%: distant warm light source (safety/hope unreachable),
material differentiation within cold: steel glossy + concrete matte + glass translucent,
Shot on Arri Alexa 65, T4.0, film grain, 4k --ar 16:9
--no warm highlights, golden tones, cozy atmosphere
```

### 24.7 色彩叙事与已有提示词技巧的衔接

| 已有技巧 | 与色彩叙事的衔接 | 提示词组合写法 |
|----------|-----------------|---------------|
| 角色描写精度 | 服装色=色桥，必须在六维中声明色桥功能 | 维度4服饰增加"color bridge to [environment]" |
| 视觉聚焦逻辑 | 光源色决定高光色温→影响眼神高光 | catchlight color matching light source temperature |
| 暧昧恋爱规范 | 恋爱五阶段=色温递进(冷→暖) | 暧昧=冷暖撞色→心动=暖浸→失控=全暖无呼吸孔 |
| 面瘫美学 | 面瘫+冷浸型=极致疏离 | 面瘫角色推荐冷浸型或冷暖撞色型 |
| 单帧叙事密度 | 五层证据的色彩由调色板类型决定 | 环境证据+色彩体系联合声明 |

## 二十五、皮肤真实感六层AI提示词技巧

### 25.1 次表面散射（SSS）提示词

SSS是皮肤真实感的最核心层——缺失SSS是AI皮肤"假"的第一原因。提示词中必须显式声明SSS行为：

**SSS声明模板**：
```
[SKIN — SUBSURFACE SCATTERING]:
realistic subsurface scattering, light penetrating epidermis and scattering within dermis,
warm translucency visible at thin skin areas: nose wing edges glowing warm orange-red in backlight,
ear rims transmitting warm amber light, fingertips turning reddish when backlit,
cheekbone highlights glowing from within (NOT surface white specular spot),
forehead edge light showing warm inner glow,
skin appears lit from inside, organic light behavior, NOT plastic surface reflection
```

**SSS与光源方向的交互**：

| 光源方向 | SSS表现 | 提示词补充 |
|----------|---------|-----------|
| 逆光 | 最强SSS——耳廓/鼻翼/指尖全部透光 | `strong subsurface scattering visible in backlight, ear rims glowing warm red` |
| 侧光 | 中等SSS——面光侧微弱+阴影侧边缘透光 | `moderate subsurface scattering, shadow-side nose edge showing warm translucency` |
| 正面光 | 最弱SSS——但颧骨高光仍应从内亮起 | `subtle subsurface scattering, cheekbone highlights luminous from within not surface` |
| 顶光 | T区SSS——额头/鼻梁透光 | `forehead and nose bridge showing subtle subsurface glow under overhead light` |

### 25.2 微纹理地图提示词

微纹理声明必须具体到"哪里有什么"——不能笼统写"textured skin"：

**微纹理声明模板**：
```
[SKIN — MICRO-TEXTURE MAP]:
T-zone (forehead/nose/chin): visible but refined pores, natural oil sheen on nose tip,
cheeks: finer pores, light peach fuzz (vellus hair) barely visible in sidelight,
under-eye area: extremely fine crepe-like texture, faint blue-red micro-capillaries,
nasolabial area: natural micro-lines, slightly warmer tone,
chin: subtle texture variation,
scattered light freckles/pigmentation spots (NOT perfect uniform skin tone),
skin texture varies by zone — NOT uniform smooth surface,
visible skin grain at close range, organic imperfection as proof of life
```

**不同角色的微纹理差异**：

| 角色类型 | 微纹理重点 | 提示词调整 |
|----------|-----------|-----------|
| 年轻女性 | 细密毛孔+散在雀斑+面颊绒毛 | `fine refined pores, scattered freckles across nose and cheeks, light vellus hair on cheekbones catching sidelight` |
| 中年男性 | 粗大毛孔+深纹路+油光 | `enlarged pores across nose and cheeks, deep nasolabial folds, visible forehead lines, natural oil sheen on T-zone` |
| 少女 | 几乎无毛孔+均匀+粉红底色 | `nearly invisible pores, uniform youthful skin, natural pink undertone, faint peach fuzz, minimal texture variation` |
| 老人 | 皱纹地图+老年斑+皮肤松弛纹理 | `deep wrinkle map across forehead/crow's feet/nasolabial, age spots on temples and hands, crepey skin texture at neck, visible capillaries` |

### 25.3 油汗层提示词

油汗层是"感觉得到但看不太出来"的微妙光泽——提示词中的分寸极关键：

**油汗层声明模板**：
```
[SKIN — SEBUM-SWEAT FILM]:
natural sebum film creating subtle sheen on: nose tip (most visible), 
forehead center (light sheen), chin (slight gloss),
dry zones with NO sheen: cheekbones, jawline sides (matte),
finger pads showing natural moisture sheen when handling objects,
NOT greasy or sweaty — subtle organic glow suggesting living skin,
balance: visible enough to feel alive, invisible enough to not draw attention
```

**油汗层与情绪/场景的交互**：

| 场景/情绪 | 油汗层变化 | 提示词调整 |
|----------|-----------|-----------|
| 正常/冷静 | 极微自然光泽 | `natural subtle sheen on nose tip` |
| 紧张/焦虑 | 鼻头/额头微汗 | `slight perspiration on nose tip and forehead, moisture not dripping but visible` |
| 运动/打斗 | 汗珠+油光 | `visible sweat droplets on temples and upper lip, skin glistening with moisture` |
| 寒冷 | 鼻头微红+干皮 | `reddened nose tip from cold, dry flaky patches on cheeks, no sheen` |
| 亲密/脸红 | 面颊充血+微汗 | `flushed cheeks with increased blood flow, subtle moisture on upper lip, warm glow` |

### 25.4 色区差异提示词

色区差异是"全脸同色=蜡像"的解药——提示词中必须声明面部不同区域的色相差异：

**色区差异声明模板**：
```
[SKIN — CHROMATIC ZONATION]:
facial skin color NOT uniform — natural zonal variation:
forehead: slightly warmer/yellower (thicker stratum corneum),
under-eye: slightly cooler/redder (thin skin + micro-capillaries),
nose wings: slightly warmer/redder (dense capillaries + pores),
cheeks: slightly cooler/pinker (blood flow + subcutaneous fat),
chin/perioral: slightly darker/yellower (perioral pigmentation),
jawline: slightly cooler/darker (shadow transition + skin thickness change),
these variations are SUBTLE — visible in aggregate not individually,
lack of zonation = mannequin effect
```

**色区差异与光源色的交互**：

| 光源色 | 色区表现 | 提示词调整 |
|--------|---------|-----------|
| 暖金光 | 色区差异被暖光柔化但仍存在 | `chromatic zonation softened by warm golden light but still perceptible` |
| 冷蓝光 | 色区差异被冷光放大——红区更红蓝区更蓝 | `cool light amplifying chromatic zonation, red zones (nose/cheeks) more visible against blue ambient` |
| 混合光 | 暖面冷阴影=色区对比最强 | `mixed lighting creating maximum chromatic zonation contrast between lit and shadow zones` |

### 25.5 边缘光证实3D提示词

边缘光是"皮肤表面是3D曲面"的光学证据——缺失边缘光=面部扁平：

**边缘光声明模板**：
```
[SKIN — EDGE LIGHT = 3D PROOF]:
skin surface behaving as 3D curved topology:
nose bridge: fine warm light band along both sides confirming protrusion,
cheekbones: subtle light transition along underside confirming volume,
jawline: thin light edge separating face from neck confirming turn,
brow ridge: micro-shadow beneath confirming forward projection,
these light edges are NOT decorative rim light — they are optical proof 
that skin wraps around 3D bone structure,
flat skin without edge light = face painted on canvas
```

### 25.6 视频微动态提示词（仅视频场景）

视频中的皮肤微动态是"活着"的最终证据——静态图无此层，但视频必须声明：

**微动态声明模板**：
```
[SKIN — BREATHING MICRO-DYNAMICS (video only)]:
skin micro-dynamics indicating living tissue:
subtle sheen variation on nose tip from micro-perspiration fluctuation,
barely perceptible skin tone micro-pulsation from blood flow,
fine vellus hair on cheekbones occasionally catching light with micro-movement,
nasal wings slightly expanding and contracting with breathing rhythm,
NOT static mannequin skin — skin must feel alive even in still moments,
Motion Strength 3-4 for skin micro-dynamics, NOT 0
```

### 25.7 皮肤六层完整提示词模板

**静态图完整模板**（层1-5）：
```
[SKIN REALISM — 5-LAYER SYSTEM]:
1. SUBSURFACE SCATTERING: realistic SSS, warm translucency at thin skin areas, 
cheekbone highlights glowing from within NOT surface reflection,
2. MICRO-TEXTURE: [zone-specific texture — pores/freckles/velvus hair/micro-capillaries],
skin texture varies by facial zone, NOT uniform surface,
3. SEBUM-SWEAT FILM: natural subtle sheen on nose tip and forehead center, 
dry matte zones on cheekbone sides, organic living-skin glow,
4. CHROMATIC ZONATION: subtle facial color variation — forehead warmer, 
under-eye cooler/redder, cheeks pinker, chin darker, NOT uniform skin tone,
5. EDGE LIGHT 3D PROOF: fine light bands along nose/cheekbone/jawline edges 
confirming skin wraps 3D bone structure, NOT flat painted surface
```

**视频完整模板**（层1-6）：
```
[SKIN REALISM — 6-LAYER SYSTEM]:
[层1-5同上]
6. BREATHING MICRO-DYNAMICS: subtle micro-perspiration sheen variation, 
skin tone micro-pulsation, vellus hair micro-movement, nasal breathing rhythm,
skin feeling alive even in still moments, Motion Strength 3-4
```

### 25.8 皮肤真实感与已有提示词技巧的衔接

| 已有技巧 | 与皮肤六层的衔接 | 组合写法 |
|----------|-----------------|---------|
| 视觉聚焦逻辑 | 眼睛6系统+皮肤6层=12系统面部活体感 | 眼部声明后紧跟皮肤六层声明 |
| 角色描写精度 | 维度2面部特征必须包含皮肤质感 | 维度2增加"skin: SSS+微纹理+色区差异" |
| 三步表演法 | 微反应层的物理载体是皮肤微动态 | 视频中皮肤微动态=三步法微反应层的视觉实现 |
| 色彩叙事 | 色区差异=调色板在面部的微观 | 暖光下皮肤色区偏暖+SSS暖透光 |
| 面瘫美学 | 面瘫皮肤真实感更关键 | 面瘫=表情冻结+皮肤质感必须更真=观众以皮肤判真假 |
| Negative Prompt | 皮肤负提示=直接防假 | `--no plastic skin, waxy skin, mannequin skin, uniform skin tone, poreless, flawless, doll-like` |

## 二十六、导演风格圣经AI提示词技巧

### 26.1 导演风格提示词的调用方式

导演风格提示词不是"装饰前缀"——它是整个提示词的**操作系统**。选择一位导演风格后，该风格的5参数（VISUAL DNA / CAMERA / COMPOSITION / LIGHTING / EMOTION）将自动覆盖提示词的对应位置。

**调用规则**：
- 一条提示词只能有1位主导演风格
- 主风格负责：光影策略 + 构图逻辑 + 情绪节奏
- 辅助风格最多1位，只负责1个具体维度（如"维伦纽瓦构图+伯格曼面部特写"）
- 风格声明放在提示词最前面，作为锚定段的一部分

**提示词结构**：
```
[DIRECTOR STYLE] Nolan-style visual grammar
[VISUAL DNA] IMAX grandeur, desaturated cold-grey palette, ...
[ANCHOR] 角色锚定段
[ACTION] 动作/构图/运镜描述
[TECHNICAL] 摄影机后缀 + Negative Prompt + Motion Strength
```

### 26.2 14位导演的提示词速查模板

**诺兰**：
```
[STYLE] Christopher Nolan cinematic grammar
[VISUAL DNA] IMAX 65mm grandeur, practical effects, desaturated cold-steel grey, monumental architecture dwarfing human, time as physical weight
[CAMERA] IMAX 65mm, slow methodical push-in, stable rig, deep focus T4.0
[COMPOSITION] centered lone figure vs colossal structure, symmetric framing, deep depth of field
[LIGHTING] natural overcast, cold steel tones, minimal fill, clinical low saturation
[EMOTION] time pressure, spatial suffocation, rational mind confronting irrational
[FILM GRAIN] fine IMAX grain, cool desaturated tone
Negative: --no warm tones, high saturation, handheld shake, anamorphic flare, soft focus
```

**维伦纽瓦**：
```
[STYLE] Denis Villeneuve cinematic grammar
[VISUAL DNA] minimalist Brutalist, geometric composition, fog/dust/sand/light shafts, existential weight, silence as force
[CAMERA] Arri Alexa 65, extremely slow push-in, long lens compression, T2.8 selective focus
[COMPOSITION] extreme negative space, human swallowed by environment, geometric forms, horizon line
[LIGHTING] Roger Deakins: diffused backlight, fog scatter, single shaft source, silhouette rim
[EMOTION] existential dread, silence has mass, slow revelation, vastness crushing the individual
[FILM GRAIN] fine organic grain, neutral-warm tone
Negative: --no fast cuts, warm saturation, cluttered frame, hand-held shake, direct emotion
```

**费里尼**：
```
[STYLE] Federico Fellini cinematic grammar
[VISUAL DNA] surreal theatrical dreamscape, circus aesthetics, baroque excess, nostalgic fantasy
[CAMERA] anamorphic 35mm, lateral tracking, roaming Steadicam, circular movement, dreamy drift
[COMPOSITION] circular arrangements, forced perspective, crowds surrounding protagonist, theatrical depth
[LIGHTING] soft contrast, diffused theatrical, spotlight on faces, dreamy glow, practical carnival light
[EMOTION] bittersweet absurdity, carnival melancholy, nostalgia for dreams that never were
[FILM GRAIN] rich 35mm grain, warm romantic tone
Negative: --no clinical lighting, sharp edges, minimalist space, cold tones, realistic restraint
```

**奉俊昊**：
```
[STYLE] Bong Joon-ho cinematic grammar
[VISUAL DNA] social realism, vertical space as class hierarchy, black humor, sudden tonal shift
[CAMERA] precise dolly tracks, slow geometric reveals, sudden handheld violence
[COMPOSITION] vertical composition encodes class, symmetry hiding asymmetry, architectural framing
[LIGHTING] naturalistic everyday quality, sudden high-contrast violence, fluorescent institutional
[EMOTION] dark comedy → sudden brutality → social satire, tonal whiplash
[FILM GRAIN] clean digital with occasional grain, neutral tone
Negative: --no romantic glow, fantasy palette, static tonal register, glossy commercial look
```

**黑泽明**：
```
[STYLE] Akira Kurosawa cinematic grammar
[VISUAL DNA] dynamic composition, natural elements as force (rain/wind/dust/snow), epic tension, samurai dignity
[CAMERA] dynamic tracking, sudden push-in, lateral movement, crane, weather as motion
[COMPOSITION] diagonal energy, motion freeze-frame, multi-plane depth staging, weather filling frame
[LIGHTING] natural light, weather as light source, high contrast silhouettes, elemental backlight
[EMOTION] epic dignity, samurai silence, nature as fate, human vs elemental force
[FILM GRAIN] heavy grain, warm-sepia tone
Negative: --no soft diffused light, static frame, muted emotion, clinical precision, modern minimalism
```

**塔伦蒂诺**：
```
[STYLE] Quentin Tarantino cinematic grammar
[VISUAL DNA] high contrast, genre stylization, dialogue-driven tension, sudden explosive violence
[CAMERA] low-angle hero worship, crash-zoom to close-up, long-take dialogue, sudden handheld
[COMPOSITION] extreme close-up, Dutch angle, trunk-shot POV, symmetric confrontation
[LIGHTING] high contrast chiaroscuro, neon genre color, bar/club practical light
[EMOTION] dialogue tension → sudden violence → absurdist humor, genre pastiche
[FILM GRAIN] exploitation film grain, warm-vivid tone
Negative: --no subtle restraint, soft diffused light, naturalistic underplay, desaturated palette
```

**李安**：
```
[STYLE] Ang Lee cinematic grammar
[VISUAL DNA] emotional subtlety, soft light, inner world as landscape, restrained intensity
[CAMERA] extremely slow push-in, stillness as statement, micro-movements, restrained breathing
[COMPOSITION] frame-within-frame, breathing space, solitary figure in vast landscape, balanced negative space
[LIGHTING] soft diffused, golden hour, low contrast, gentle wrap, window light
[EMOTION] repression → endurance → eruption → reconciliation, emotions felt before spoken
[FILM GRAIN] fine clean grain, warm-neutral tone
Negative: --no harsh contrast, aggressive camera, cold detachment, chaotic energy, flashy technique
```

**斯皮尔伯格**：
```
[STYLE] Steven Spielberg cinematic grammar
[VISUAL DNA] backlight volumetric, reaction shots as emotional engine, humanist wonder, lens flare as hope
[CAMERA] Steadicam following, orbiting, long-take oners, low-angle hero worship, smooth crane
[COMPOSITION] centered hero, deep staging, low-angle looking up at wonder, faces in light
[LIGHTING] backlight volumetric haze, golden hour magic light, lens flare as emotional punctuation
[EMOTION] sense of wonder, loss of innocence, human redemption, faces lit by miracle
[FILM GRAIN] clean with fine grain, warm-golden tone
Negative: --no cynical darkness, cold detachment, flat lighting, static framing, ambiguous morality
```

**王家卫**：
```
[STYLE] Wong Kar-wai cinematic grammar
[VISUAL DNA] neon nightscape, slow-shutter drag, emotional fragmentation, time as wound
[CAMERA] handheld tracking, step-printing, slow motion with motion blur, time manipulation, intimate drift
[COMPOSITION] frame-within-frame, reflective surfaces, tilted Dutch angle, cramped intimacy
[LIGHTING] neon mixed color temperature, overexposure, light trails, practical neon, rain-reflected glow
[EMOTION] nostalgic longing, missed connections, pain of time passing, desire frozen in amber
[FILM GRAIN] heavy grain, saturated-warm tone
Negative: --no clean static frame, even lighting, rational clarity, cold detachment, straightforward time
```

**小津安二郎**：
```
[STYLE] Yasujirō Ozu cinematic grammar
[VISUAL DNA] ultra-low angle, static camera, detached family observation, still life as transition
[CAMERA] completely static, occasional lateral track only, no following, no tilt, no zoom
[COMPOSITION] frontal low angle (tatami height), symmetric, still life objects between scenes
[LIGHTING] soft natural, even illumination, no dramatic lighting, window light
[EMOTION] quiet acceptance, sorrow in the ordinary, impermanence, family as universe
[FILM GRAIN] fine grain, neutral-warm tone
Negative: --no camera movement, dramatic lighting, extreme close-up, fast cutting, dynamic action
```

**伯格曼**：
```
[STYLE] Ingmar Bergman cinematic grammar
[VISUAL DNA] extreme facial close-up, high-contrast psychological pressure, soul laid bare
[CAMERA] minimal movement, slow push to extreme CU, long lens isolation, static observation
[COMPOSITION] face fills frame, two-person confrontation, walls closing in, minimal environment
[LIGHTING] high contrast, single hard side-light, Fårö island window light, shadow as character
[EMOTION] existential anxiety, crisis of faith, soul laid bare, face as battlefield
[FILM GRAIN] moderate grain, cold-neutral tone
Negative: --no soft light, wide shot, action, movement, warm comfort, easy answers
```

**是枝裕和**：
```
[STYLE] Hirokazu Kore-eda cinematic grammar
[VISUAL DNA] everyday poetry, natural light, family fragments, gentle observation
[CAMERA] static, slow lateral drift, long lens soft focus, observational patience
[COMPOSITION] eye-level, breathing space, food/hand close-ups, domestic framing, windows as threshold
[LIGHTING] natural light, golden hour, window diffused, kitchen warm, overcast soft
[EMOTION] gentle sadness, absence within the everyday, warmth of memory, family as fragile ecosystem
[FILM GRAIN] fine clean grain, warm-neutral tone
Negative: --no dramatic lighting, harsh contrast, genre stylization, dark tone, aggressive camera
```

**科恩兄弟**：
```
[STYLE] Coen Brothers cinematic grammar
[VISUAL DNA] precise composition, black humor, fatalism, snow landscapes as moral void
[CAMERA] precise dolly, slow push-in, sudden crash-zoom, textbook framing, controlled chaos
[COMPOSITION] extreme positive/negative space, extreme close-up, snowy white void, geometric precision
[LIGHTING] low color temperature, fluorescent, desolate natural light, bar neon, winter grey
[EMOTION] fatalistic absurdity, accidental violence, moral gray zone, dark comedy of errors
[FILM GRAIN] moderate grain, cool-neutral tone
Negative: --no warm sentiment, hopeful resolution, chaotic framing, soft focus, earnest sincerity
```

**张艺谋**：
```
[STYLE] Zhang Yimou cinematic grammar
[VISUAL DNA] color as narrative, ritualized movement, Eastern aesthetics, sweeping scale
[CAMERA] slow dolly track, crane, ritualized precise movement, controlled geometric motion
[COMPOSITION] symmetry, color blocks, human sea patterns, ceremonial framing, red as protagonist
[LIGHTING] saturated color, complementary contrast, lantern warm glow, dust-filled light beams
[EMOTION] oppression → eruption → tragic heroism → fate, color carrying emotion words cannot
[FILM GRAIN] moderate grain, warm-saturated tone
Negative: --no muted palette, casual framing, understated emotion, grey tones, handheld shake
```

### 26.3 导演风格混搭的提示词写法

混搭不是两个模板拼接——是1个主模板+1个具体维度的"借用"：

```
[PRIMARY STYLE] Denis Villeneuve — existential dread, minimalist space, Deakins lighting
[SECONDARY BORROW] Ingmar Bergman — ONLY for facial close-up sequences (eyes filling frame)
```

**混搭禁区**：
- 不可同时声明两个冲突的CAMERA参数（如"IMAX稳定器+手持跟拍"）
- 不可同时声明两个冲突的LIGHTING策略（如"Deakins柔散逆光+塔伦蒂诺高对比明暗"）
- 情绪节奏只能跟随主风格

### 26.4 导演风格与皮肤/色彩/一致性系统的提示词组合

| 组合场景 | 写法 | 示例 |
|----------|------|------|
| 诺兰+皮肤六层 | 冷灰调不取消SSS | `desaturated cold-steel palette, realistic subsurface scattering with faint warm blood glow beneath grey-tinted skin, NOT dead grey skin` |
| 伯格曼+视觉聚焦 | 高反差特写=意识导向最大化 | `high contrast single source, conscious intent behind eyes (85% conscious + 15% texture), locked gaze, NOT hollow stare` |
| 王家卫+色彩情绪 | 霓虹色温混搭 | `neon mixed color temperature, warm subsurface scattering under magenta ambient, chromatic zonation visible despite neon wash` |
| 小津+皮肤六层 | 均匀光下色区差异更关键 | `even natural illumination, chromatic zonation (forehead yellow-warm, cheek pink-bright, jawline cooler), SSS faint at thin skin areas` |

## 二十七、色彩情绪圣经AI提示词技巧

### 27.1 七色提示词模块

每种色彩的提示词不是单个关键词——是一个完整的**色彩-情绪-光影-皮肤**声明链。

**橙色模块**：
```
[WARM ORANGE] warm orange glow from tungsten practical light, amber sunset backlight, 
golden hour dust particles in light beam, firelight warmth on skin,
desert heat haze in background,
skin: warm subsurface scattering, amber glow through ear rims and nose edges,
chromatic zonation: cheek pink-warm under orange cast, forehead amber-warm,
NOT orange face paint, NOT oversaturated burn
```

**粉色模块**：
```
[PINK ATMOSPHERE] saturated pink atmosphere, candy-colored surrealism, 
neon magenta glow from practical neon sign, pastel pink diffusion,
artificial sweetness as emotional lie,
skin: SSS with faint pink-warm beneath, chromatic zonation preserved (forehead cooler, cheeks pinker),
NOT silicone doll skin, NOT flat pink wash
```

**红色模块**：
```
[CRIMSON RED] deep crimson red accent as visual gravity point, 
blood red fabric drape, scarlet power signal in composition,
red emergency light casting selective red on half the face,
skin: warm subsurface scattering with visible blood beneath (NOT red face paint),
chromatic zonation: cheeks flush warmer, jawline stays neutral,
5-10% cool breathing hole in composition (blue-grey shadow corner)
```

**黄色模块**：
```
[WARM YELLOW] warm yellow tungsten glow, nostalgic amber interior light,
golden dust motes floating in light beam, incandescent warmth,
honey-toned interior memory quality,
skin: warm SSS golden through thin skin, chromatic zonation preserved (forehead amber, cheeks warm-pink),
NOT jaundiced yellow skin, NOT unhealthy sallow tone
```

**蓝色模块**：
```
[STEEL BLUE] steel blue cold atmosphere, deep ocean blue shadows in background,
moonlight blue cast on environment, clinical blue-tech edge light,
midnight cobalt shadows,
skin: cool subsurface scattering with FAINT warm blood beneath (critical: NOT dead blue skin),
chromatic zonation: cheeks retain slight pink despite blue cast, forehead cooler,
mandatory 1 warm anchor point in composition (small amber practical light or warm skin highlight)
```

**绿色模块**：
```
[GREEN AMBIENT] eerie green luminescence from background source,
forest canopy dappled green on environment, 
toxic neon green as warning signal,
skin: natural skin with GREEN AMBIENT REFLECTION on surface (NOT green-tinted skin pigmentation),
chromatic zonation: cheeks still pink-neutral, forehead still yellow-warm,
green light is REFLECTED not ABSORBED by skin
```

**紫色模块**：
```
[PURPLE TWILIGHT] twilight purple sky in upper third, 
neon violet haze from urban lights, deep amethyst shadows,
dusky magenta gradient at horizon,
skin: purple AMBIENT REFLECTION on skin surface (NOT purple skin pigmentation),
chromatic zonation: cheeks still warm-pink, forehead still amber-neutral,
purple light wraps around 3D form but doesn't change skin undertone,
desaturate purple + add fog for cinematic quality (NOT cheap neon)
```

### 27.2 色彩组合提示词模板

**经典互补对（橙+蓝）**：
```
[COLOR PALETTE] complementary orange-blue split,
foreground: warm orange tungsten glow on character face (warm SSS, amber skin tones),
background: steel blue cold shadows receding into depth,
color temperature gradient: cool far → warm near,
orange as visual gravity pulling viewer forward,
blue as atmospheric depth pushing world backward,
skin under dual source: warm key + cool fill, chromatic zonation visible
```

**暴力冲突（红+绿）**：
```
[COLOR PALETTE] violent red-green complementary clash,
crimson red as dominant force (blood, power, danger),
toxic green as opposing threat (poison, supernatural, wrongness),
5-10% cold breathing hole (dark grey shadow),
skin: warm SSS preserved under conflicting color cast,
red wash on character from one side, green ambient on other,
NOT red face paint, NOT green-tinted skin
```

**皇室权力（紫+金）**：
```
[COLOR PALETTE] regal purple-gold power pairing,
deep amethyst shadows in upper frame, 
golden warm glow from ceremonial light source below,
purple = mystery/power, gold = wealth/authority,
skin: warm SSS golden through thin skin, purple ambient on shadow side,
chromatic zonation: cheeks golden-warm, jawline amethyst-cool
```

### 27.3 色彩情绪与导演风格的提示词自动映射

选择导演风格时，色彩偏好自动继承：

| 导演 | 自动继承色板 | 提示词自动声明 |
|------|-------------|---------------|
| 诺兰 | 冷灰蓝+零星暖橙 | `desaturated cold-steel palette, occasional amber practical light as anchor` |
| 维伦纽瓦 | 单色冷+光束暖 | `monochromatic cool base, single warm light shaft as focal point` |
| 王家卫 | 霓虹暖+深夜蓝 | `neon warm palette, deep blue shadows, mixed color temperature` |
| 张艺谋 | 饱和补色对 | `saturated complementary contrast, red as narrative force` |
| 是枝裕和 | 自然暖+窗光 | `natural warm palette, window diffused, golden hour` |
| 科恩兄弟 | 冷灰+荧光黄 | `desolate cool palette, sickly fluorescent yellow accent` |

### 27.4 色彩情绪与已有提示词技巧的衔接

| 已有技巧 | 衔接方式 | 组合写法 |
|----------|---------|---------|
| 色彩叙事（六型调色板） | 六型管结构，情绪圣经管语义 | `[PALETTE TYPE: 冷浸型] + [EMOTION: 蓝色=孤独压抑]` |
| 皮肤六层 | 色区差异随色彩情绪变化 | 蓝色场景=`cheeks retain faint pink despite blue cast` |
| 视觉聚焦 | 瞳孔反射环境色彩 | 蓝色场景=`pupils reflecting blue ambient, iris texture under blue cast` |
| 单帧叙事密度 | 色彩锚点=情绪模块的实例 | 暖色锚定=橙色模块的点睛色 |
| Negative Prompt | 每种色彩有专属负提示 | 蓝色:`--no dead blue skin`; 红色:`--no red face paint`; 绿色:`--no green-tinted skin` |

## 二十八、万能分镜模板AI提示词技巧

### 28.1 吵架模板提示词

**5拍基础版**：

拍1（中景-克制）：
```
MEDIUM SHOT, two figures facing each other in [LOCATION], 
measured distance between them, body language controlled,
[CHARACTER A ANCHOR] facing [CHARACTER B ANCHOR],
even neutral lighting, domestic or institutional setting,
slow or no camera movement, breathing room in frame,
4k, cinematic, Shot on Arri Alexa 65, T2.8, film grain
--no extreme emotion, close-up, dramatic shadow
```

拍2（近景-升级）：
```
CLOSE-UP, [CHARACTER A] stepping forward, personal space invaded,
jaw clenched, eyes narrowing, voice rising physically visible in neck tension,
slow push-in camera, space shrinking in frame,
light warming slightly (key light intensity up),
skin: subtle perspiration sheen on forehead, chromatic zonation heightened,
4k, cinematic, Shot on Arri Alexa 65, T2.8, film grain
--no neutral expression, relaxed posture, even lighting
```

拍3（特写-爆发）：
```
EXTREME CLOSE-UP, [CHARACTER] face at peak emotion,
mouth open in mid-shout OR lips pressed in most painful silence,
eyes: micro-saccades + pupil dilation + irregular blink + lid tension (4-layer eye animation mandatory),
skin: SSS visible at nose edges, perspiration on forehead and nose bridge, 
chromatic zonation: flushed cheeks, pale forehead,
handheld tremor (level 2 临场感), 
light: overexposed highlight or shadow swallowing half face,
4k, cinematic, Shot on Arri Alexa 65, T2.0, film grain
--no neutral face, dead eyes, even skin tone, smooth camera
```

拍4（中景-崩溃）：
```
MEDIUM SHOT, [CHARACTER] body language collapsing inward,
shoulders dropping, gaze dropping to floor, hands unclenching,
camera slowly pulling back or drifting sideways,
light cooling to neutral, energy draining from frame,
skin: perspiration cooling, SSS returning to normal,
4k, cinematic, Shot on Arri Alexa 65, T2.8, film grain
--no aggression, forward posture, warm light
```

拍5（全景-冷战）：
```
WIDE SHOT, two figures in same space but emotionally continents apart,
physical distance restored but relationship changed,
static camera or very slow pull-back,
light: cool cast, cold breathing hole in warm areas,
environment as witness to what just happened,
4k, cinematic, Shot on Arri Alexa 65, T4.0, film grain
--no warmth between figures, close proximity, dramatic shadow
```

### 28.2 打斗模板提示词

**5拍基础版**：

拍1（全景-对峙）：
```
WIDE SHOT, [CHARACTER A] and [CHARACTER B] in combat stance,
[LOCATION] fully visible, spatial relationship established,
environment weapon visible in background (visual foreshadowing),
slow orbiting camera or static wide,
light: environmental, establishing mood,
4k, cinematic, Shot on Arri Alexa 65, T4.0, film grain
--no action yet, close-up, isolated figures
```

拍2（中景-交锋）：
```
MEDIUM SHOT, first contact exchange between [A] and [B],
attack → collision → reaction three-beat structure (each beat = separate shot),
handheld level 2 (临场感), following impact point,
speed blur on strike, impact frame frozen for 1 beat,
light: contrast increased, practical light flicker on impact,
4k, cinematic, Shot on Arri Alexa 65, T2.8, film grain
--no clean choreography, slow motion, stable camera
```

拍3（近景-受挫）：
```
CLOSE-UP, [CHARACTER] taking damage, shock/pain registering,
impact ripple through body visible at close range,
handheld tremor level 3 (混乱感, ≤5 seconds max) on impact moment,
then stabilize to level 2,
skin: SSS at nose/ear, micro-perspiration burst, chromatic flush,
eyes: pupil dilation from shock, irregular blink,
4k, cinematic, Shot on Arri Alexa 65, T2.0, film grain
--no composed expression, steady camera, clean impact
```

拍4（特写-反杀）：
```
EXTREME CLOSE-UP, [CHARACTER] reversal moment —
eyes locking onto opportunity, jaw setting, muscle tension shifting,
the instant before counter-strike,
static or micro-push, time stretching,
single hard light source from reversal direction,
skin: SSS edge glow, micro-texture visible, sweat droplet catching light,
4k, cinematic, Shot on Arri Alexa 65, T2.0, film grain, Motion Strength 2-3
--no action, medium shot, soft lighting
```

拍5（全景-结果）：
```
WIDE SHOT, post-combat spatial relationship,
[WINNER] standing, [LOSER] on ground, environment altered by fight,
slow pull-back revealing full destruction,
light: dust particles in light beam, settling energy,
environment bearing scars of conflict (narrative evidence),
4k, cinematic, Shot on Arri Alexa 65, T4.0, film grain
--no ongoing action, dynamic camera, clean environment
```

### 28.3 走路模板提示词

**5拍基础版**：

拍1（远景-氛围）：
```
WIDE ESTABLISHING SHOT, [CHARACTER] small figure in [ENVIRONMENT],
atmospheric conditions visible (weather, time of day, season),
environment five-layer evidence: time/season markers, human traces, 
economic class indicators, climate clues, threat signals (3/5 minimum),
static camera or very slow lateral drift,
color temperature gradient: cool background → warmer near character,
character clothing color as color bridge between skin and environment,
4k, cinematic, Shot on Arri Alexa 65, T4.0, film grain
--no close-up, fast movement, dramatic lighting
```

拍2（中景-行进）：
```
MEDIUM SHOT, [CHARACTER] walking, 
gait rhythm and body language revealing emotional state,
Steadicam following or tracking lateral at walking pace,
hands visible (clenched/loose/in pockets/swinging),
interaction with space (passing through, avoiding, embracing),
4k, cinematic, Shot on Arri Alexa 65, T2.8, film grain
--no static pose, extreme close-up, dramatic angle
```

拍3（近景-聚焦）：
```
CLOSE-UP, [CHARACTER] face or hands during walk,
inner state made visible: jaw tension, eye direction, hand grip,
slow push-in or handheld following at close range,
three-step acting: main performance (walking) + small action (grip change) + micro-reaction (eye flicker),
skin: SSS, micro-texture, chromatic zonation visible at this range,
4k, cinematic, Shot on Arri Alexa 65, T2.0, film grain
--no full body, action sequence, wide composition
```

拍4（特写-极点）：
```
EXTREME CLOSE-UP, single detail — one eye, one hand, one footstep,
emotional peak compressed into smallest frame,
static or micro-tremor camera,
light: isolated detail catching specific light quality,
if eye shot: 4-layer micro-animation mandatory (saccade + pupil breath + irregular blink + lid follow),
if hand shot: skin micro-texture, SSS at knuckle edges, oil sheen,
if footstep: ground texture, water splash, dust displacement,
4k, cinematic, Shot on Arri Alexa 65, T2.0, film grain
--no context, environment, multiple subjects
```

拍5（远景-余韵）：
```
WIDE SHOT, [CHARACTER] continuing into distance or remaining in space,
state changed from shot 1 even if position similar,
static camera, environment as emotional echo,
light: same as opening but with subtle shift (time passed, mood changed),
color: same palette but character's place in it has shifted,
4k, cinematic, Shot on Arri Alexa 65, T4.0, film grain
--no close-up, dramatic action, different angle than shot 1
```

### 28.4 模板变奏的提示词写法

**倒叙变奏**（打斗从反杀开始）：
```
[REVERSE CHRONOLOGY FIGHT]
Shot 1: EXTREME CU — reversal moment (normally shot 4)
Shot 2: WIDE — combat aftermath (normally shot 5)  
Shot 3: WIDE — original confrontation (normally shot 1)
Shot 4: MEDIUM — first exchange (normally shot 2)
Shot 5: CLOSE — damage taken (normally shot 3)
[CONTINUITY NOTE] time flows backward, each shot reveals HOW we got to the reversal
```

**混合变奏**（走路→打斗）：
```
[BLEND: WALK → FIGHT]
Shot 1-3: Walk pattern (wide → medium → close)
Shot 4: Walk close-up INTERRUPTED by threat
Shot 5-9: Fight pattern (wide → medium → close → ECU → wide)
Shot 10: Walk pattern return (wide, but different state)
[CONTINUITY NOTE] walk rhythm shattered by violence, walk returns but changed
```

### 28.5 万能模板与已有提示词技巧的衔接

| 已有技巧 | 与模板的衔接 | 组合写法 |
|----------|-------------|---------|
| 打斗叙事弧线 | 打斗模板完整版=5拍+权力三次翻转 | 拍3(受挫)=绝望谷底，拍4(反杀)=爆发翻转 |
| 运镜美学框架 | 模板中选择美学贯穿 | 打斗拍2-3声明`[AESTHETIC: 切割美学]` |
| 正反打多镜 | 吵架拍2-3必须拆分 | `SHOT 2a: A speaking + 2b: B reacting` |
| 三步表演法 | 每个模板镜头含三层 | 近景/特写必须声明`three-step: main+small+micro` |
| 皮肤六层 | 特写/极特写声明皮肤 | 拍3-4增加SSS+微纹理+色区差异 |
| 导演风格 | 模板整体套用导演语法 | 提示词前缀加`[STYLE: X cinematic grammar]` |
| 色彩情绪 | 模板各拍情绪=色彩变化 | 吵架：中性→暖→过曝→冷；打斗：环境色→对比色→单色→原色 |


## 二十九、角色设定板双版本生成提示词实战

### 29.1 两步法的提示词模板

**步骤1：单人角色图（视觉种子）**

```
[角色名] [身份/年龄], [六维拆解后的人物描写——面部骨架+眼部+表情基态+体态+服饰7要素], 
front three-quarter view, full body standing pose against [dark/neutral] solid color background

[Cinematic打光: 光位名+视觉语言+情绪效果, 如"top-side key light creating dramatic chiaroscuro, volumetric dust particles"]
[皮肤真实感: visible pores, natural uneven skin tone, sweat sheen, no plastic porcelain texture]
[镜头参数: 85mm T1.8 shallow depth of field, Arri Alexa 65, film grain, 4K ultra photorealistic]

no text, no watermark, no extra figures, character design sheet pose
```

**步骤2：模块化设定板（纯白底）**

```
Professional character design reference board on PURE WHITE background, 
absolutely no beige no gray no grid lines, clean white (#FFFFFF) throughout. 
16:9 horizontal format. Modular grid with thin black border lines separating each module.

Character: [与步骤1完全一致的角色描写，六维精确描述]

Modules:
- CENTER: Full-body front view [手部+道具完整]
- UPPER-LEFT: Back view [披风/后背破损] + side view [肩甲弧度]
- LOWER-LEFT: Black silhouettes (front/side) + dynamic poses (sitting, two squatting poses)
- RIGHT-TOP: Five expression headshots in a row [5种具体情绪名] with small Chinese labels
- RIGHT-MIDDLE: Low-angle and high-angle full-body outlines + face close-up with [blood/grime] detail
- RIGHT-BOTTOM: Eye close-ups, [armor/prop] texture detail studies
- BOTTOM-LEFT: Clean sans-serif black text: "NAME: [角色名] ROLE: [身份] CORE MOOD: [核心气质] VISUAL SIGNS: [视觉标志]"

Film realistic rendering, detailed fabric and armor textures, no watermark
```

### 29.2 超时处理策略

设定板生成超时是最常见问题，根因是信息过载（多模块布局+角色描写+参考图），策略如下：

| 超时场景 | 处理策略 | 优先级 |
|----------|---------|--------|
| 带参考图+长提示词超时 | 去掉ref_images，纯文字提示词生成 | 首选 |
| 纯文字仍超时 | 精简角色描写，只保留六维锚点表的6行核心信息 | 次选 |
| 仍然超时 | 减少模块数量，优先保留：中心全身+五表情+文字标注 | 兜底 |
| 模块缺失但主体OK | 用缺失模块单独生成后拼贴补充 | 修补 |

**精简版设定板提示词**（超时兜底用）：

```
Character design board, pure white background, 16:9. [角色名], [六维核心1行]. 
CENTER full-body front. LEFT back+side views. RIGHT five expressions (cold, tears, rage, biting lip, horror). BOTTOM text: NAME [角色名] ROLE [身份] MOOD [气质]. Film realistic, no watermark
```

### 29.3 六维锚点表→设定板ID块映射

设定板底部文字标注不是随意写的，必须从六维锚点表精确提取：

| ID块字段 | 来源 | 示例 |
|----------|------|------|
| NAME | 角色名+时期 | 厉淮胤（少年时期） |
| ROLE | 身份定位 | 厉国三皇子 |
| CORE MOOD | 表情基态+体态惯性的情绪摘要 | 隐忍，绝境感，少年帝王气，悲剧宿命感 |
| VISUAL SIGNS | 服饰7要素的标志性组合+眼部特征 | 黑色残甲，血污，倔强眼神 |

### 29.4 设定板与已有规范的强制叠加

| 已有规范 | 设定板中的体现 |
|----------|--------------|
| 生产级首帧6层标准 | 设定板每个模块本身也是6层全覆盖的产物 |
| 皮肤真实感六层 | 面部特写模块必须声明SSS+微纹理+色区差异 |
| 电影打光位置 | 设定板统一使用前侧光（最中性），避免特定光位干扰角色基础定义 |
| 角色描写精度规范 | 设定板提示词中的角色描写必须经过六维拆解法精修 |
| 色彩叙事体系 | 设定板角色服装色=色桥主色，跨镜头不可跳变 |


## 三十、镜头时长估算与景别推断提示词技巧

### 30.1 时长估算在提示词中的体现

视频生成工具（Kling/Runway/Luma）通常需要指定片段时长，时长必须与镜头内容匹配：

| 场景 | 推荐时长 | 提示词写法 |
|------|---------|-----------|
| 快切动作 | 2-3秒 | `2s clip, rapid cut, motion strength 8-9` |
| 标准叙事 | 3-5秒 | `4s clip, steady pacing, motion strength 5-6` |
| 情绪停留 | 5-8秒 | `6s clip, slow push-in, motion strength 3-4, breathing motion only` |
| 长镜头 | 8-10秒 | `10s clip, continuous camera movement, three anchor points required` |
| 静态空镜 | 3-5秒 | `4s clip, extremely subtle breathing motion (<5cm), motion strength 2-3` |

### 30.2 景别推断→提示词镜头参数映射

| 推断景别 | 镜头焦距 | 光圈 | 提示词关键词 |
|---------|---------|------|------------|
| EWS | 14-24mm | T4.0-T8.0 | `extreme wide shot, environmental scale, figure dwarfed by space` |
| WS | 24-35mm | T4.0-T5.6 | `wide shot, full body visible, spatial context established` |
| MS | 35-50mm | T2.8-T4.0 | `medium shot, waist up, balanced figure and background` |
| MCU | 50-85mm | T2.0-T2.8 | `medium close-up, chest up, facial expression primary focus` |
| CU | 85-135mm | T1.4-T2.0 | `close-up, face fills frame, every micro-expression visible` |
| ECU | 135-200mm | T1.4 | `extreme close-up, single feature fills frame, eye/lip/hand detail` |

### 30.3 表格式分镜中的AI提示词摘要字段

AI提示词摘要字段不是完整提示词，而是**锚点速查码**，供后续生成完整提示词时回溯：

```
格式：角色锚点/服饰锚点/动作锚点/光位/情绪关键词

示例：
厉淮胤/黑甲蟒袍灰披风/握刀回头/前侧光/压抑愤怒
→ 后续展开为完整提示词时，从锚点表提取六维细节填充
```

### 30.4 长剧本批处理的提示词管理

| 批次管理项 | 规范 |
|-----------|------|
| 锚点表共享 | Phase 1生成的锚点表存为独立文件，所有批次引用同一版本 |
| 提示词模板复用 | 同一场景/同一角色的提示词锚定段跨批次逐字复用 |
| 批次间一致性 | 每批次结束后输出一致性校验清单，下一批次开始前先校验 |
| 上下文管理 | 每批次结束后输出中间产物文件，避免在对话上下文中累积过多内容 |

### 30.5 交互式分镜文档生成

交付产物应包含交互式HTML文档，功能要求：

| 功能 | 实现方式 | 优先级 |
|------|---------|--------|
| 关键词搜索 | 搜索框+全文检索（角色名/地点/对白） | 必须 |
| 场景筛选 | 下拉菜单筛选INT/EXT/闪回/日/夜 | 必须 |
| 角色筛选 | 下拉菜单筛选指定角色的镜头 | 推荐 |
| 集号筛选 | 标签页或下拉菜单按集号切换 | 推荐 |
| 打印导出 | 打印样式表优化，分页按场次 | 必须 |
| AI提示词展开 | 点击摘要字段展开完整AI提示词 | 推荐 |


## 三十一、工业级道具设计图提示词模板

### 31.1 Split View道具设计图完整模板

**英文提示词模板**（Midjourney/SD通用）：

```
A detailed production design sheet for a Chinese [antique/historical/modern] prop, featuring a "[道具英文名]". Split view layout showcasing the fully assembled prop on the left, and a detailed structural breakdown (deconstructed view) with technical dimension lines and measurements on the right.

[根据剧本细节，详细描述道具的造型、曲线和特征]. Features physically accurate gravity and realistic weight distribution, paired with natural grounding shadows and ambient occlusion (AO) that roots the object to the surface. Includes organic micro-scratches, dents, and asymmetrical wear marks.

Made of [具体材质，从6大类速查表选填]. [精准注入对应的材质物理控制词——见SKILL.md材质速查表].

Cinematic prop design concept art, [剧集类型] asset. Included a color palette strip at the bottom showing [5个核心配色英文]. Set against a clean, textured light gray parchment paper background with an elegant, subtle ornamental border framing the canvas. High resolution, 8k, sharp focus, industrial design blueprint style.

--no plastic look, rubbery surface, synthetic gloss, uniform shading, pristine surface, flawless texture, CGI render, video game asset, flat texture map, uniform reflection, floating object, zero-gravity placement, perfectly symmetrical wear --ar 16:9
```

**中文解析模板**（每条提示词必须附带）：
```
画面包含：左侧为组装完成、带有物理重力阴影与不规则磨损的[材质]道具全景；
右侧为带有cm/mm技术标注线的结构拆解图；底部附带5色专属色卡[列出5色]。
整体为[吸光/各向异性光泽/SSS透光]的真实物理介质，浅灰羊皮纸底。
```

### 31.2 四视角提示词变体

**① 全景视角（Assembly View）**：
```
[道具英文名], fully assembled, [材质控制词], natural grounding shadows, ambient occlusion, 
asymmetrical wear marks, [光线交互声明], 
cinematic prop photography, 8k, shallow depth of field, 
--no plastic look, uniform reflection, floating object --ar 16:9
```

**② 拆解视角（Deconstructed View）**：
```
[道具英文名], deconstructed exploded view, technical dimension lines in cm/mm, 
parts separated with assembly logic arrows, [材质控制词], 
industrial design blueprint style, light gray parchment background, ornamental border, 8k,
--no plastic look, CGI render, video game asset --ar 16:9
```

**③ 色卡视角（Color Card）**：
```
Color palette strip for [道具英文名], 5 core colors: [色1], [色2], [色3], [色4], [色5],
clean white background, swatch format, cinematic color grading reference,
--no text, watermark --ar 16:9
```

**④ 微距视角（Macro Detail）**：
```
Extreme macro close-up of [道具英文名] surface, [材质控制词重点: 微孔/裂纹/积垢/纹理], 
subsurface scattering (SSS) at thin edges, [光线交互声明], 
visible micro-scratches and organic wear patterns, 
85mm T2.0, shallow depth of field, Arri Alexa 65, film grain, 4K ultra photorealistic,
--no plastic look, uniform shading, pristine surface --ar 16:9
```

### 31.3 材质选择→控制词注入流程

```
Step 1材质表确定材质类别 → 查6大类速查表 → 精确咬合控制词 → 注入提示词Material段

古董金属 → patinated bronze + verdigris oxidation + micro-pitting + grime in crevices
老旧木质 → aged wood grain + deep fissures + splintered edges + organic oils
粗糙石质 → raw unpolished stone + mineral streaks + sediment + chipped edges
通透玉石 → inclusions + fractures + SSS + light refraction + dust on surface
骨/象牙/角 → bone density variations + yellowed patina + porosity + hairline cracks
织物/皮革 → thread weave + worn grain + stitching irregularities + frayed edges
```

### 31.4 道具提示词与分镜提示词的衔接

| 衔接场景 | 写法 | 示例 |
|----------|------|------|
| 道具在角色手中 | 角色锚定段+道具材质段+触觉关系 | 厉淮胤左手握刀，patinated bronze hilt, worn leather grip, thumb pressing scabbard edge |
| 道具特写空镜 | 道具材质段+光线交互+6层L3-L6 | ancient bronze seal, front-side key light, SSS at thin edges, visible verdigris in crevices |
| 道具作为前景虚化 | 道具轮廓+景深声明 | out-of-focus prop in foreground, 85mm T1.4, subject sharp in midground |
| 道具与环境互动 | 道具材质+环境材质+光线统一 | iron blade reflecting cold moonlight, matching scene's 5800K fill |


## 三十二、AI视频生成提示词实战（故事板→视频桥梁）

### 32.1 视频提示词模板（Seedance2.0/Kling/Runway通用）

```
根据提供的故事板，生成【一镜到底/分段】的【X秒】视频。

【运镜要求】
0-X秒：[景别+运镜方式]，[角色动作]，[运镜动机]
X-Y秒：[景别+运镜方式]，[角色动作]，[运镜动机]
Y-Z秒：[景别+运镜方式]，[角色动作]，[运镜动机]
（按时间顺序列出每个分镜的运镜方式，标注动机）

【核心要求】
- 一镜到底，不要生硬切镜头（如适用）
- 运镜有合理动机，跟随角色动作自然过渡
- 无字幕、无解说
- 画面风格与故事板一致
- 角色外貌、服装、武器必须与故事板完全一致
- 动作自然，有微表情和呼吸感
```

### 32.2 故事板提示词模板（给GPTimage2）

```
请为以下剧本生成完整故事板：

【故事板提示】[剧情类型]短片，[简述剧情]

【格式要求】
①顶部栏：项目名、集号、场景名、时间、风格标签
②角色与风格参考：角色多角度参考图+5-8色色卡+风格约束声明
③服装与配饰：服装材质特写+道具参考+场景间变化说明
④环境与场景设计：场景俯视示意图+摄像机位置标注+拍摄类型+移动路径箭头
⑤故事板分镜：8个编号帧，每帧含：
  - 景别（EWS/WS/MS/MCU/CU/ECU）
  - 运镜方式（静态/跟拍/推镜/环绕/手持）
  - 动作与情绪进展描述
  - 灯光/氛围备注

【强制声明】所有分镜必须是同一画风、同一色调、同一角色。角色外貌、服装、武器必须与参考图完全一致。信息栏文字清晰可读。16:9比例。
```

### 32.3 角色设定表提示词模板（给GPTimage2）

```
请为以下角色生成专业角色设定表：

【角色信息】
Name: [名字] | Alias: [别名]
Role: [角色] | Age: [年龄]
Personality: [性格] | Core Theme: [核心主题]

【设定表要求】
1) 全身多角度：正面、3/4侧面、侧面、背面，带身高比例尺
2) 表情变化：8种情绪（Neutral, Curious, Worried, Surprised, Afraid, Sad, Determined, Relaxed）
3) 细微表情：Subtle Eye Tension, Slight Smirk, Lip Tension, Controlled Breath
4) 头部多角度：3/4, Side, Top, Low, Diagonal
5) 标准站姿 + 5种姿势变化（Relaxed, Tense, Combat Ready, Crouched, Walking）
6) 服装材质特写：4种细节
7) 武器/道具特写
8) 手部姿势：5种手势

【色彩板】[5-8个色彩关键词]
【风格】[风格描述]
```

### 32.4 动机驱动运镜的提示词写法

| 运镜 | 无动机写法（禁用） | 有动机写法（正确） | 动机来源 |
|------|-------------------|-------------------|---------|
| 推镜 | "镜头缓慢推向面部" | "她听到异响，镜头跟随警觉的视线推近" | 角色视线驱动 |
| 横移 | "镜头横移展示全景" | "战斧挥入画面，镜头跟随斧刃轨迹横移，reveal远处敌人" | 角色动作驱动 |
| 环绕 | "镜头环绕角色180度" | "她旋转挥刀，镜头跟随刀锋弧线环绕" | 角色动作驱动 |
| 升降 | "镜头升高俯瞰" | "她被击倒倒地，镜头随倒下视线升高" | 角色动作+情绪 |
| 手持 | "手持晃动增加动感" | "爆炸冲击波袭来，手持晃动模拟眩晕主观视角" | 环境事件驱动 |

### 32.5 避坑清单→提示词修正映射

| 坑 | 修正提示词写法 |
|----|-------------|
| 第一帧显示故事板 | 首帧不用"根据故事板"，改用具体画面描述 |
| 镜头乱切 | 加`一镜到底`+每段运镜标注`[动机：XXX]` |
| 角色变形 | 上传角色设定表作为参考图+`角色外貌必须与参考图完全一致` |
| 动作僵硬 | `动作自然，有微表情和呼吸感` |
| 风格漂移 | `全程风格统一，与故事板一致，色调不随时间变化` |
| 中文乱码 | 开Thinking模式+中文部分单独迭代 |
| 构图失衡 | `画面只突出1-2个核心元素，背景简洁` |


## 三十三、AIGC四步黄金框架提示词实战

### 33.1 四步框架→英文提示词组装模板

```
[第一步·定镜头]
[景别] shot, [角度] angle, [焦段]mm lens, [景深],

[第二步·构图]
foreground: [具体前景元素], out of focus /
midground: [主体+动作], sharp focus /
background: [环境描述], [虚化/清晰],

[第三步·光影色彩]
[光位名] from [方向], [色温/时段], [冷暖对撞描述],
[色彩情绪关键词],

[第四步·质感]
film grain, [镜头缺陷], [空气感元素], [材质纹理关键词],

Shot on Arri Alexa 65, T[光圈], film grain, 4k, ultra photorealistic
--no plastic look, CGI render, video game asset, uniform shading, pristine surface --ar 16:9
```

### 33.2 三层纵深构图提示词写法速查

| 场景类型 | 前景 | 中景 | 远景 |
|---------|------|------|------|
| 室内对话 | 门框/花瓶虚化 | 两人对话主体 | 窗外/走廊纵深 |
| 室外行走 | 树枝/路灯虚化 | 角色行进 | 建筑群/山脉 |
| 战斗场景 | 地面碎片/飞尘 | 战斗双方 | 战场全貌/硝烟 |
| 亲密场景 | 床单褶皱/蜡烛光斑 | 双人身体 | 虚化窗户/月光 |
| 追逐场景 | 路标/行人虚化 | 追逐者 | 城市街道延伸 |

### 33.3 光影关键词→提示词对照表

| 光影 | 完整提示词写法 | 搭配色彩 |
|------|-------------|---------|
| 黄金时段 | `golden hour, warm amber sunlight, long shadows casting across ground` | 橙+金 |
| 蓝色时刻 | `blue hour, cold blue ambient light, faint warm glow at horizon` | 蓝+紫 |
| 逆光剪影 | `backlit, strong rim light on edges, face in shadow, silhouette` | 暖边+冷面 |
| 伦勃朗光 | `Rembrandt lighting, triangular highlight on shadow-side cheek, dramatic` | 暖+暗 |
| 体积光 | `volumetric light beams cutting through [dust/fog/smoke], god rays` | 光束色+环境色 |
| 丁达尔效应 | `Tyndall effect, light scattering through [particles/mist], visible beam` | 同体积光 |
| 霓虹 | `neon reflections on wet surface, [cyan/magenta] light, urban night` | 青+品红 |

### 33.4 质感层提示词组件库

| 质感层 | 组件 | 写法 |
|--------|------|------|
| 胶片颗粒 | Kodak 5219 / Fujifilm ETERNA | `shot on Kodak 5219 film stock, organic grain structure` |
| 镜头缺陷 | 色差/光晕/暗角 | `subtle chromatic aberration at edges, natural lens flare, gentle vignette` |
| 空气感 | 雾/尘/雨/烟 | `atmospheric haze, floating dust particles in light beam, light mist` |
| 材质纹理 | 皮肤/布料/金属/木 | `visible skin pores, fabric weave pattern, metal micro-scratches, wood grain` |
| 光影颗粒 | 光中微粒 | `dust motes drifting through sunbeam, particulate matter in light` |

### 33.5 视频七要素提示词完整模板

```
[主体]: [角色锚点表核心描写]
[动作]: [具体动作序列+方向+速度+幅度], [微表情+呼吸感]
[环境]: [场景描写+环境动态:风/雨/光影变化]
[运镜]: [0-Xs: 景别+运镜+动机] / [X-Ys: ...] / [Y-Zs: ...]
[光影]: [光位+色温+随时间变化]
[风格]: [导演风格/色彩情绪/质感声明], consistent with storyboard
[声音]: [人声:角色+情绪+语调] / [音效:材质+行为+环境] / [BGM:风格+情绪]
```

### 33.6 声音设计提示词写法

| 声音类型 | 提示词格式 | 示例 |
|---------|-----------|------|
| 人声 | `[角色](情绪): "台词", [语调], [语速], [音色]` | 厉淮胤(压抑): "我记住了", 低沉沙哑, 缓慢, 少年清冽音 |
| 音效 | `[音源材质] + [行为] + [环境]` | 青铜剑插入冻土, 嘶哑金属声, 风雪环境 |
| BGM | `[风格] + [情绪] + [乐器/节奏]` | 悲壮弦乐, 缓慢低沉, 大提琴独奏渐入 |

## 三十四、电影级对白分镜AI提示词技巧

### 34.1 对白戏提示词核心原则

对白戏提示词与动作戏/恋爱戏的根本区别：**动作戏拍"运动"，恋爱戏拍"距离"，对白戏拍"权力"**。提示词必须反映情绪权力的流动，而非台词的机械交替。

```
# 错误：机械正反打——只传递信息
Shot 1: MCU of man speaking
Shot 2: MCU of woman replying

# 正确：情绪权力设计——拍权力变化
Shot 1 (85mm MCU): Man dominating frame, low angle, eyes at 2/3 height, 
stable camera, voice steady — controlling the space
Shot 2 (35mm MCU): Woman, more headroom, slightly off-center, 
edge of frame, camera very slowly drifting closer — she's being cornered
```

### 34.2 视线攻击提示词

视线不是"看"——是情绪攻击。必须声明视线的方向、强度、时长和转移方式：

```python
# 视线攻击5型提示词模板
STEAL_GLANCE = "quick darting glance lasting <0.5s, eyes snapping back to neutral, involuntary attention capture"  # 偷看
AVOID_GAZE = "deliberate gaze avoidance, eyes shifting to floor/window/hands, refusing visual engagement"  # 闪躲
STARE_DOWN = "unwavering direct eye contact, eyes locked on target, no blinking, confrontational intensity"  # 压迫
LINGERING_LOOK = "gaze holding 1-2 seconds too long, reluctant to break contact, micro-delay before looking away"  # 停留
DELAYED_REACTION = "eyes responding 0.5-1s after words land, processing visible in ocular tension before facial response"  # 延迟反应
```

### 34.3 停顿镜头提示词——沉默的重量

停顿不是"空白"——是情绪密度最高的时刻。提示词必须声明停顿中的微变化：

```
# 停顿镜头三要素
1. 运镜: extremely slow push-in at <0.2m per 5s, almost imperceptible, 
   as if camera is holding its breath with the character
2. 声音: ambient sound becoming foreground — rain on windows, 
   distant traffic, electric hum, clock ticking — silence becoming audible
3. 表演: minimal action maximum tension — fingers curling on fabric, 
   swallow visible, chest rising with held breath, 
   eyes slightly defocusing as thoughts race
```

### 34.4 潜台词镜头提示词——拍谎言泄漏点

角色说A真实感受B时，提示词必须同时声明"表面表演"和"泄漏信号"：

```
# 潜台词双轨提示词模板
VERBAL_TRACK = "smiling, voice light and casual: 'I'm fine'"  # 台词轨道
LEAK_TRACK = "fingers unconsciously releasing grip on cup, 
  breath catching for 0.3s before response, 
  eyes defocusing at sentence end, 
  light temperature shifting cooler on face"  # 泄漏轨道
# 提示词只写LEAK_TRACK，VERBAL_TRACK在故事板/台词栏中
```

谎言泄漏点速查：
| 泄漏类型 | 提示词写法 |
|----------|-----------|
| 手部泄漏 | `fingers unconsciously releasing/curling/tapping, body betraying composure` |
| 呼吸泄漏 | `breath catching/hitching before response, rhythm disrupted by suppressed emotion` |
| 视线泄漏 | `eyes defocusing at sentence end, gaze dropping to hands/floor, micro-delay before eye contact` |
| 光线泄漏 | `light temperature shifting cooler on face, shadows encroaching as lie continues` |

### 34.5 情绪主导权转移提示词

权力反转时提示词必须同步变化——运镜/构图/焦距全部反转：

```
# 权力反转提示词结构
POWER_SHIFT = """
Before: [strong character] 85mm, filling frame, low angle, stable camera, 
        centered composition — dominating visual space
        [weak character] 35mm, off-center, high angle, more headroom, 
        partially occluded — visually marginal

After shift: [former strong] camera becomes handheld, pushed to edge, 
             more headroom, breathing visible — losing control
             [former weak] moves to center, frame tightens, 
             low angle creeping in — gaining visual dominance
"""
```

### 34.6 不对称正反打提示词

对白中正反打必须用不同焦距/构图表达情绪权力不对等：

```
# 不对称正反打模板
DOMINANT = "85mm, tight framing filling 70% of frame, low angle 5° below eye level, 
           shallow DOF compressing background, character breathing down viewer's neck, 
           no escape from their gaze"
SUBMISSIVE = "35mm, loose framing with 40% negative space, high angle 10° above, 
             deep focus preserving environment, character small within frame, 
             room feels bigger than they are"
```

### 34.7 第三视角提示词

"空间在看他们"的提示词——摄影机位暗示命运/旁观/宿命：

```
# 第三视角模板
OMNISCIENT = "camera positioned at extreme corner of room, wide angle capturing 
             both subjects as small figures in their environment, 
             furniture/doorframes creating natural frames within frame, 
             rain on window audible, TV flickering in background — 
             the room is watching them, and the room already knows how this ends"
```

第三视角位置→效果速查：
| 位置 | 提示词关键词 |
|------|------------|
| 房间角落 | `extreme room corner, wide surveillance angle, fate observing` |
| 门外 | `camera outside doorway looking in, glass/reflection between, excluded from intimacy` |
| 走廊尽头 | `long corridor perspective, subjects distant, destiny framing` |
| 镜子 | `reflected in mirror, dual reality, self-witnessing` |
| 家具后 | `partial occlusion behind furniture, hidden observer, secret keeper` |

### 34.8 对白节奏五阶段提示词模板

| 阶段 | 焦距/运镜提示词 | 声音提示词 |
|------|---------------|-----------|
| 情绪平静 | `50mm, locked-off camera, symmetrical framing, medium shot, breathing room` | `ambient sound at normal level, space feels breathable` |
| 情绪试探 | `50mm, extremely slow drift forward <0.3m/min, slight foreground occlusion entering` | `ambient fading, subtle sounds emerging: fabric, breathing, clock` |
| 情绪压迫 | `85-100mm, continuing push-in, spatial compression, frame tightening around face` | `ambient silenced, only breathing and micro-sounds audible, pressure building` |
| 情绪爆发 | `handheld, quick cuts allowed, broken composition, destabilized frame` | `sudden sound burst or violent silence, rhythm fractured` |
| 情绪坍塌 | `locked-off, slow pull-back to wide, character becoming small, negative space overwhelming` | `ambient returning but hollowed out, rain/wind/distance — the world continuing indifferently` |

### 34.9 导演对白风格提示词速查

**王家卫式对白提示词**：
```
# 空间阻隔+情绪越浓越克制
"camera peering through doorway frame, characters separated by architecture, 
never in same focal plane, closest approach is a near-miss — 
fingertips, shoulder brush, slow-motion turn, 
time dilating at 120fps as they almost touch but never do, 
neon reflection on wet surface, 
the space between them more eloquent than any words"
```

**诺兰式信息对白提示词**：
```
# 信息压迫+逻辑战争
"50mm clinical framing, precise headroom, characters facing off like debaters, 
rapid shot-reverse-shot with escalating intensity, 
every cut a new piece of information, 
spatial geometry crystal clear, 
no emotional close-ups — logic is the weapon here, 
eyes calculating not feeling, 
the room is a chess board and words are moves"
```

**黑泽明式空间对白提示词**：
```
# 空间参与对白+动态调度
"35mm wide angle, character striding through frame, 
invading foreground, shifting composition weight with each step, 
opponent pressed against doorframe/corner by spatial dominance, 
camera panning to follow movement, 
architecture becoming weapon, 
the room itself is the argument"
```

**教父式沉默对白提示词**：
```
# 沉默累积+爆发前最安静
"locked-off camera, dining table between them, 
ambient sounds gradually amplifying — train rumble, 
fork on plate, clock ticking, 
each cut slightly tighter, 
shadows growing, 
silence becoming deafening, 
then — nothing. absolute stillness. 
the quiet before violence is the loudest moment in cinema"
```

### 34.10 对白光影心理学提示词

| 光位 | 心理效果 | 提示词 |
|------|---------|--------|
| 顶光(审问) | 压迫/审判/罪恶感 | `harsh overhead top-light, eye sockets in shadow, nose casting downward shadow, interrogation atmosphere, guilt made visible` |
| 侧光(分裂) | 人格分裂/内心冲突 | `hard side-light splitting face in half, one side lit one side dark, internal war made external, noir duality` |
| 背光(隐藏) | 情绪隐藏/神秘/无法读取 | `strong backlight, face in silhouette, emotions unreadable, withholding truth from camera, mystery in shadow` |
| 下光(威胁) | 危险/非人感/恐惧 | `uplighting from below, unnatural shadow upward, features distorted, monster in the room, primal fear response` |

光比递进提示词：`shadows gradually consuming face as scene progresses, light-to-dark ratio shifting from 2:1 to 4:1 to 8:1, truth devouring the relationship`

### 34.11 焦距-情绪提示词速查（对白通用）

```python
# 对白焦距三段式
DIALOGUE_WIDE = "24-35mm wide angle, subject isolated in environment, 
                 truth exposed by space, loneliness made architectural, 
                 conversation happening across a gulf"
DIALOGUE_NORMAL = "50mm natural perspective, as if eavesdropping on a conversation, 
                   balanced relationship, neither dominating, 
                   the default of human interaction"  
DIALOGUE_TIGHT = "85-135mm telephoto, spatial compression making walls close in, 
                  nowhere to hide, breathing becomes visible, 
                  the camera is now inside the argument"
```

### 34.12 短剧对白电影感提示词三法

**方法一：用身体替代台词**：
```
# 不要写角色说"我很痛苦"
# 而是写角色身体的痛苦：
"character turning away from window, hand finding wall for support, 
head dropping, shoulders rising with held breath, 
silence stretching, cigarette burning unattended, 
ash growing long before falling — 
everything the mouth won't say, the body is screaming"
```

**方法二：环境呼吸**：
```
# 对白场景必须声明环境音
"wind pressing against window, fridge compressor humming, 
distant siren dopplering past, 
rain beginning on roof — 
space breathing around the silence between words, 
making the room feel real and alive and indifferent to their suffering"
```

**方法三：空间中的人物（不只是脸）**：
```
# 不要只拍特写合集
"full body in environment, character small within frame, 
furniture and architecture visible, 
hands gesturing or gripping or hanging limp, 
the room telling its own story alongside the dialogue — 
cinematic feeling comes from SPACE not from FACES"
```

### 34.13 对白分镜7镜头完整提示词案例

**场景：深夜。夫妻吃饭。丈夫怀疑妻子出轨。**

```
Shot 1 (28mm WS, locked-off): Dining table spanning frame, two figures at opposite ends, 
  only sound of chopsticks and ceramic, cold overhead fluorescent, 
  distance between them measurable in meters and in silence

Shot 2 (50mm MCU, locked-off): Husband looking down at plate, not at her, 
  voice flat: "You were late today.", eyes staying on food, 
  deliberate avoidance of eye contact — the question hidden in the statement

Shot 3 (85mm CU, slow drift): NOT her face. Her hand. Chopsticks frozen mid-air, 
  fingers tightening on wood, knuckles whitening, 
  0.5s pause before she resumes eating, 
  the camera catching what her face won't show

Shot 4 (50mm MCU, slow push-in): Wife smiling, voice controlled: "Working overtime.", 
  camera beginning imperceptible push-in, 
  smile not reaching eyes, 
  the lie sitting comfortably in her mouth because she's practiced it

Shot 5 (85mm CU, locked-off): Husband raising eyes for the first time, 
  direct eye contact, long silence 3+ seconds, 
  camera holding still, ambient sound dropping away, 
  only breathing and the weight of unspoken accusation

Shot 6 (50mm MCU, handheld): Red and blue ambulance lights sweeping across both faces 
  through window, strobing illumination revealing and concealing, 
  frame slightly unstable — reality intruding, 
  the outside world's emergency mirroring their private catastrophe

Shot 7 (85mm MCU, locked-off → slow pull-back): Husband: "You were never good at lying.", 
  pause. "You used to not be.", 
  camera beginning slow retreat, 
  her face catching the full weight, 
  pulling back to reveal the space between them has become unbridgeable
```

### 34.14 暧昧/恋爱场景环境声音设计提示词

| 声音类型 | 情绪功能 | 提示词 |
|----------|---------|--------|
| 呼吸声 | 私人空间入侵 | `breathing becoming audible, private space closing in, intimacy of involuntary sound` |
| 衣料摩擦 | 身体靠近证据 | `fabric brushing sound, proximity made audible, two bodies in near-contact` |
| 风声/雨声 | 孤独+亲密 | `wind outside, rain on glass, two people inside — the world becomes a cocoon` |
| 电流/钟表 | 时间压迫 | `electric hum, clock ticking, time stretching in stillness, seconds becoming hours` |
| 远处车流 | 理性世界远处运转 | `distant traffic, rational world continuing outside their bubble, two realities coexisting` |

### 34.15 王家卫式恋爱时间感提示词

恋爱改变时间感——心动瞬间时间变慢：

```
"time dilating in the moment of recognition, 120fps slow motion, 
reality softening at edges, 
as if the world knows something has changed, 
the second their hands almost touch stretching into eternity, 
background motion blurring while their near-contact remains crystalline, 
the universe slowing down to witness this moment"
```

### 34.16 经典爱情场景7镜头完整提示词案例

**场景：深夜。下雨。两人躲在便利店门口。**

```
Shot 1 (28mm WS, locked-off): Two figures under convenience store awning, 
  rain curtain between them and the world, 
  wide gap between their positions, 
  only rain sound, neon sign buzzing, 
  city night indifferent to two people standing in silence

Shot 2 (50mm MCU, locked-off): Woman looking down, adjusting wet sleeve cuff, 
  man stealing a glance at her, 
  she senses it — eyes shift away, 
  0.3s delayed, involuntary, 
  the glance that said everything words couldn't

Shot 3 (50mm MCU, extremely slow drift forward): Camera moving <0.2m over 5 seconds, 
  air between them becoming charged, 
  ambient sound fading, 
  rain becoming white noise, 
  the space itself shifting temperature

Shot 4 (85mm CU, locked-off): Man extending hot drink toward her, 
  their fingers making contact — both freeze, 
  0.5s of absolute stillness, 
  the most significant touch of their lives happening at fingertip scale, 
  neither pulling away

Shot 5 (50mm MCU, locked-off): Neither speaking. 
  Only convenience store refrigerator hum. 
  Rain continuing. 
  The silence between them louder than any declaration, 
  charged with everything they're not saying

Shot 6 (85mm MCU, slow drift): Woman, voice barely above whisper: "Thank you.", 
  eyes not meeting his, 
  camera drifting closer like someone leaning in to hear a secret, 
  the intimacy of almost-words

Shot 7 (35mm MCU, locked-off): Camera holds. 
  Rain continuing. 
  World shrinking to the size of this awning. 
  Two people. One moment. 
  The entire history of their relationship written in the distance between their shoulders, 
  background dissolving into bokeh — world disappearing, only they remain
```

## 三十五、AI视频模型微表情实战对比与提示词策略

### 35.1 模型选择决定微表情成败

不同模型对同一提示词的微表情渲染效果差异巨大。选错模型=提示词再精确也无效。

**核心数据**（2026年5月多源实测）：

| 维度 | Kling 3.0 | Seedance 2.0 | Sora 2 | Veo 3.1 |
|------|-----------|-------------|--------|---------|
| 面部一致性(10s) | 9.2/10 | **9.4/10** | 8.1/10 | 7.4/10 |
| 微表情偏移率 | 67% | **18%** | N/A | N/A |
| 物理合理性 | **9.4/10** | 8.2/10 | 8.2/10 | 7.6/10 |
| 中文首次达标 | 53% | **86%** | N/A | N/A |

### 35.2 模型→场景路由提示词策略

**Seedance 2.0微表情优化提示词**：
```
# Seedance弱点=皮肤过度柔化，必须强制声明纹理
[标准提示词], natural skin texture with visible pores, 
subtle imperfections, non-uniform skin tone, 
realistic micro-creases around eyes and mouth, 
light catching individual peach-fuzz hairs
```

**Kling 3.0微表情优化提示词**：
```
# Kling弱点=转头变形+微表情偏移，必须声明防变形
[标准提示词], jawline stable during head rotation, 
no facial deformation during movement, 
facial proportions locked throughout, 
natural blink rhythm with full eyelid closure, 
no mid-blink eye distortion
```

### 35.3 Kling微表情精准控制4方案提示词

**方案1：结构化提示词（最常用）**：
```
# 禁止模糊描述，精确到角度+毫秒
head slowly turns right 12 degrees over 1.4 seconds; 
simultaneously completes one natural blink, 
closure duration 320ms, reopening with slight moisture gloss; 
shoulders and neck remain stationary throughout; 
jawline stable, no facial deformation
```

**方案2：首尾帧语义锚定**：
```
# 首帧=睁眼正脸，尾帧=闭眼/转头态
blink starts at 1.1s, full closure at 1.4s; 
head turn starts at 0.8s, stops at 2.0s at 12° offset; 
all motion terminates at 2.8s, end frame holds closed_eyes + right_turn dual state; 
ControlNet structural lock weight 0.85
```

**方案3：帧级眨眼剧本**：
```
# Prompt Travel语法，帧级精度
[frame_0: open_eyes], [frame_2: eyes_half_closed], 
[frame_4: closed_eyes:1.2], [frame_6: eyes_half_open], 
[frame_8: open_eyes_with_gloss]
# 转头单独时间线，不与眨眼关键帧重叠
[frame_0: head_center], [frame_12: head_right_10deg], 
[frame_24: head_right_12deg]
```

**方案4：多视角角色档案**：
```
# 4视角上传后强制调用
[character:ID-7A2F] 
facial rigidity weight 0.88, 
neck rotation tolerance 0.32, 
3D structural lock enabled, 
all generation must reference unified facial geometry prior
```

### 35.4 AI微表情9大真实感要素提示词速查

| # | 要素 | 提示词修正（跨模型通用） |
|---|------|----------------------|
| 1 | 角色一致性 | `character identity locked, consistent facial features across all frames, reference image anchored` |
| 2 | 皮肤质感 | `natural skin texture, visible pores, subtle imperfections, non-uniform pigmentation` **（最大单点优化）** |
| 3 | 手持拍摄感 | `slight handheld wobble, imperfect framing, natural iPhone motion blur, breathing micro-movement` |
| 4 | 自然光线 | `soft window light as key, shadows following subject movement, real environmental catchlight in eyes, no studio flat lighting` |
| 5 | 物理正确 | `object has weight in hand, fabric creases with movement, hair bounces with physics, natural blink rhythm 15-20 per minute` |
| 6 | 唇形同步 | `lip-synced to dialogue, natural pauses, breathing between phrases, filler sounds, slight mouth pre-shaping before words` |
| 7 | 不对称性 | `slight head tilt 3-5 degrees, asymmetric smile, one eye slightly more open than the other, warm eye contact with micro-variations` |
| 8 | UGC美学 | `slight digital grain, shallow DOF background bokeh, warm color temperature, iPhone-casual composition, not overly perfect` |
| 9 | 叙事节奏 | `natural jump cuts, breathing room between beats, complete logic arc, real emotional energy not manufactured` |

**不对称铁律提示词**：`slight head tilt, asymmetric smile, warm eye contact, subtle micro-expression variation — humans are never perfectly symmetrical, over-symmetry triggers uncanny valley`

### 35.5 模型弱点补偿提示词模板

**Kling专用防变形声明**（对白/恋爱/微表情场景必加）：
```
# Kling微表情补偿块（附加在提示词末尾）
jawline stable during head rotation, no facial deformation, 
facial proportions locked, natural blink with full eyelid closure, 
no mid-blink eye distortion, no jaw displacement during speech, 
consistent pupil size across frames, 
eye whites proportion stable during gaze shifts
```

**Seedance防柔化声明**（皮肤质感场景必加）：
```
# Seedance皮肤质感补偿块
visible pores on nose and cheeks, skin texture with micro-imperfections, 
non-uniform skin tone with subtle redness around nose and cheeks, 
individual peach-fuzz hairs catching light, 
realistic oil-sweat film on forehead and nose bridge, 
NOT airbrushed, NOT smooth, NOT plastic
```

## 三十六、实拍+AI混合分镜AI提示词技巧

来源：Jon Kent "I Spent 9 Months Testing AI for Filmmaking" 混合工作流实践。

### 36.1 感知流畅性提示词策略

**先实拍后AI的提示词写法差异**：

当镜头序列从[REAL]切换到[AI]时，AI提示词必须"承前启后"——引用实拍镜头建立的光照和质感基线。

**[REAL]→[AI]过渡提示词模板**：
```
[SHOT 04: First AI shot after 3 REAL shots]
Prompt: "Wide establishing shot of [LOCATION], matching the warm golden lighting established in previous shots. Atmospheric haze creates depth layers. Character silhouette at frame right third, posture consistent with [REAL] reference. Cinematic depth of field with foreground element [specific element]. Shot on Arri Alexa 65, T4.0, film grain, 4k, ultra photorealistic"
```

**关键**：过渡提示词必须包含 `matching the [X] lighting established in previous shots`——这告诉AI不要创造全新的光线设定，而是延续已有视觉语言。

### 36.2 末帧接力提示词实战

**末帧接力提示词结构**：
```
Image reference: [SHOT06 last frame exported as still]
Prompt: "Continuing from previous shot. Character [NAME] at [POSITION in frame], [DIRECTION facing]. [NEW ACTION/MOVEMENT]. Camera [CAMERA MOVEMENT]. [LIGHTING description matching reference]. [ATMOSPHERE]. Shot on Arri Alexa 65, T2.8, film grain, 4k, ultra photorealistic"
Negative: "character in different position, different lighting direction, different clothing, jump cut, discontinuous motion"
```

**末帧接力提示词铁律**：
- 首句必须是 `Continuing from previous shot` 或等效声明
- 人物位置必须精确描述（不能用模糊位置词如"画面中"）
- Negative Prompt 必须包含位置/光线/服装不一致的排除项
- 若接力帧质量不佳（模糊/构图差），需先在Photoshop中清洁后再用作参考

### 36.3 AI广角镜头提示词模板

远景/大全景的AI提示词与近景完全不同——不需要皮肤/微表情声明，替换为大气叙事。

**远景AI提示词模板**：
```
Prompt: "Extreme wide shot of [LOCATION DESCRIPTION]. [3 atmospheric layers: foreground element + midground subject + background environment]. [Weather/atmosphere: fog/rain/dust/haze]. [Time of day lighting]. Silhouette of [CHARACTER NAME] at [POSITION], [POSTURE DESCRIPTION conveying emotion through body language alone]. [Environmental narrative: what the landscape says about the story]. Atmospheric perspective with depth layers. Shot on Arri Alexa 65, T8.0, film grain, 4k, ultra photorealistic"
Negative: "close-up, facial details, skin texture, portrait, studio lighting, flat background, no depth"
```

**与近景提示词的核心差异**：

| 维度 | 近景提示词 | 远景提示词 |
|------|-----------|-----------|
| 人物描述 | 6层首帧标准（表情/动作/光源/皮肤/景深/质感） | 体态叙事（轮廓/姿势/方向） |
| 光线 | 标准电影打光8大光位 | 环境光+大气层次 |
| 皮肤 | pores, imperfections, SSS | 不声明，用大气消解 |
| 情感载体 | 微表情+眼神 | 轮廓+姿态+环境叙事 |
| 景深 | T1.4-T2.8 | T4.0-T8.0（全景深） |
| Negative | distorted limbs, asymmetrical face | close-up, facial details, flat background |

### 36.4 反向绿幕背景生成提示词

**步骤1：绿幕静帧→AI背景提示词**
```
Image reference: [Actor green screen still frame]
Prompt: "Background environment for [SCENE DESCRIPTION]. Perspective matches foreground actor: camera height [X]m, [Y]° angle, [Z]mm lens. [LIGHTING matching actor's key light direction]. [ATMOSPHERE]. No characters, no people, clean background plate for compositing. [TIME OF DAY]. [WEATHER]. Shot on Arri Alexa 65, T4.0, film grain, 4k, ultra photorealistic"
Negative: "people, characters, faces, studio lighting, flat background, no depth, green screen artifacts"
```

**步骤2：清洁背景→运动生成提示词**
```
Image reference: [Clean background plate after Photoshop actor removal]
Prompt: "Subtle camera drift [DIRECTION, X seconds from A meters to B meters]. [ENVIRONMENTAL MOTION: wind in trees, water flowing, smoke rising]. [ATMOSPHERIC PARTICLES in light]. Extremely subtle breathing motion of camera (<5cm). [LIGHTING stays consistent with foreground actor plate]. No characters in frame. Shot on Arri Alexa 65, T4.0, film grain, 4k, ultra photorealistic"
```

### 36.5 [HYBRID]镜头光照匹配提示词

混合镜头最大的技术挑战是光照一致性——实拍前景和AI背景必须共享同一光源逻辑。

**光照匹配自检清单（写入提示词前必须完成）**：
1. 实拍时主光方向？（左侧/右侧/顶光/逆光）
2. 实拍时主光色温？（暖光5600K+/冷光3200K-/混合）
3. 实拍时光质？（硬光/柔光/漫射）
4. AI背景是否声明了相同方向+色温+光质？

**光照匹配提示词片段**：
```
"Key light from [DIRECTION] at [COLOR TEMPERATURE], [LIGHT QUALITY], matching foreground plate. Shadows cast to [SHADOW DIRECTION]. Consistent light falloff across depth layers"
```

### 36.6 声音驱动的提示词节奏

声音设计不只是后期的事——分镜提示词的节奏应与声音节奏匹配。

**声音节奏→提示词节奏映射**：

| 声音类型 | 提示词节奏 | 示例 |
|---------|-----------|------|
| 环境低频drone | 慢速运镜+长镜头 | "Slow 4-second push-in, camera moves from 8m to 5m" |
| 急促脚步Foley | 快速切镜+短镜头 | "Quick 1.5-second shot, snap zoom" |
| 静默/呼吸 | 极静止+微推 | "Extremely subtle breathing motion, 0.3cm drift over 6 seconds" |
| 爆发音效 | 动态运镜+手持 | "Sudden handheld jerk, camera reacts to explosion" |

**原则**：提示词的运镜速度和镜头时长，必须与该镜头3层声音设计（Ambient+Foley+Emotional）的节奏同步。声音越激烈→镜头越短越快；声音越安静→镜头越长越稳。


---

## 三十七、分镜逐秒情绪拆解法提示词技巧

### 37.1 逐秒时间轴→AI视频提示词压缩

逐秒时间轴是规划工具，AI视频提示词需要将时间轴压缩为连贯的情绪弧线描述。

**压缩公式**：
```
[景别+运镜]。[角色状态+初始情绪]，[情绪递进微动作序列]，[情绪高潮微动作]，[收尾状态+遗留痕迹]。[摄影机后缀]
```

**完整案例：微表情递进**
```
时间轴：
0-2秒: 安静表情，眼神暗沉，嘴唇低低抿着
2-4秒: 嘴角慢慢轻扬，下颚微收
4-6秒: 眉头舒展又轻皱，眼眶微微泛红
6-8秒: 压抑的崩溃感，隐忍
8-9秒: 情绪归于平静，眼神留下湿润痕迹

压缩后提示词：
"MCU, static camera, no movement. Woman in traditional garment, half-lying, expression shifting from quiet composure to subtle smile, then sorrow creeping in with brows knitting and eyes reddening, suppressed grief held behind still face, finally settling into quiet acceptance with glistening eyes. visible pores, subtle imperfections, NOT airbrushed. Shot on Arri Alexa 65, T2.8, film grain, 4k, ultra photorealistic"
```

### 37.2 情绪动词替换词库

| 形容词（禁用） | 替换动词（推荐） | 微部位 |
|---------------|-----------------|--------|
| "伤心" | 眉头轻皱、眼眶泛红、嘴唇抿紧 | 眉/眼/唇 |
| "开心" | 嘴角上扬、眉梢舒展、眼底亮起 | 嘴/眉/眼 |
| "紧张" | 喉结滚动、指节发白、呼吸急促 | 喉/手/胸 |
| "愤怒" | 下颚咬紧、鼻翼微张、太阳穴跳 | 颌/鼻/颞 |
| "恐惧" | 瞳孔放大、身体后缩、手指蜷曲 | 眼/躯干/手 |

### 37.3 情绪弧线类型速查

| 弧线类型 | 起始→终止 | 适用场景 | 提示词节奏 |
|---------|----------|---------|-----------|
| 压缩型 | 平静→爆发 | 情感高潮 | 前4秒缓慢，后2秒急转 |
| 释放型 | 紧绷→松弛 | 冲突解决 | 前紧后松，结尾留呼吸 |
| 循环型 | 平静→激动→平静 | 内心挣扎 | 对称结构，起止呼应 |
| 递进型 | 微喜→大喜→狂喜 | 胜利时刻 | 每段升级，不停歇 |
| 崩塌型 | 强撑→裂缝→瓦解 | 崩溃戏 | 伪装维持→裂缝→彻底坍塌 |

---

## 三十八、故事板五色标记系统提示词技巧

### 38.1 五色→提示词转换规则

| 颜色标记 | 提示词位置 | 转换方法 |
|---------|-----------|---------|
| 🔴 身体运动 | 主体动作描述区 | 直接转为主体动作英文指令 |
| 🔵 摄影机运动 | 运镜指令区 | 转换为精确运镜英文（含速度/方向） |
| 🟢 构图笔记 | 构图指令区 | 转换为构图英文关键词 |
| 🟠 灯光方向 | 光影描述区 | 转换为电影打光术语+光位名 |
| 🟣 声音/情感 | 氛围基调区 | 转换为情感关键词+氛围描述 |

### 38.2 五色标记故事板→视频提示词模板

```
[🔴动作描述]. [🔵运镜指令, X秒内从A到B]. [🟢构图：三分法/框架/引导线]. 
[🟠光位名+光质+色温]. [🟣情绪基调+声音暗示]. 
[角色锚定描述]. [摄影机后缀]
```

**案例**：
```
🔴: 女子手指攥紧纸杯，转身
🔵: 缓推MCU，3秒内从2米推至1米
🟢: 三分法，人物右侧1/3，左侧留白
🟠: 前侧光Rembrandt，暖光3200K，柔光
🟣: 压抑+克制，呼吸声渐重

提示词：
"Woman gripping paper cup, knuckles whitening, slowly turning. Slow 3-second push-in from 2m to 1m, MCU. Rule of thirds, subject right third, negative space left. Rembrandt key light, warm 3200K, soft diffusion. Suppressed tension, controlled breathing audible. [角色锚定]. Shot on Arri Alexa 65, T2.8, film grain, 4k, ultra photorealistic"
```

### 38.3 信息量控制铁律

单画面五色标记≤3-5个要素（AI视频单帧理解上限）。超量时按优先级削减：
1. 🔴动作（必保）→ 2. 🔵运镜（必保）→ 3. 🟠灯光（高优先）→ 4. 🟢构图（中优先）→ 5. 🟣声音（可隐含）

---

## 三十九、跟随运镜提示词技巧

### 39.1 五类跟随运镜提示词模板

**侧面跟随**：
```
[Subject] [action] in [environment]. Tracking shot, camera follows from the side, keeping subject in [center/left third/right third]. [Background change description]. [Light quality]. Shot on Arri Alexa 65, T2.8, film grain, 4k, ultra photorealistic
```

**正面后退跟随**：
```
[Subject] walking/running forward. Frontal tracking shot, camera retreats ahead of subject, keeping face visible throughout. [Environment passing behind subject]. [Emotional state on face]. Shot on Arri Alexa 65, T2.8, film grain, 4k, ultra photorealistic
```

**背面推进跟随**：
```
Back-following tracking shot, camera pushes forward behind [subject], audience follows [subject]'s POV into [environment ahead]. [What unfolds ahead]. [Suspense/atmosphere]. Shot on Arri Alexa 65, T2.8, film grain, 4k, ultra photorealistic
```

**低角度贴地跟随**：
```
Extremely low angle tracking shot, camera inches forward at ground level, only [subject's shoes/feet] visible at bottom of frame. [Oppressive environment description]. [Dramatic tension building]. Shot on Sony Venice 2, T4.0, film grain, 4k, ultra photorealistic
```

**高空俯拍跟随**：
```
Aerial top-down tracking shot, camera follows [subject]'s movement trajectory from directly above. [Full spatial layout visible from above]. [God's eye perspective]. Shot on Arri Alexa 65, T5.6, film grain, 4k, ultra photorealistic
```

### 39.2 组合运镜提示词模板

**推近→跟随（情绪递进型）**：
```
Slow push-in from WS to MS over 3 seconds, then seamlessly transition to side tracking following [subject]. Camera first focuses on [facial expression detail], then shifts to following movement as [background transitions from static to dynamic]. Shot on Arri Alexa 65, T2.8, film grain, 4k, ultra photorealistic
```

**环绕→跟随（展示转跟踪型）**：
```
Camera orbits [subject] 180 degrees over 4 seconds, revealing full figure and environment, then seamlessly transitions to back-following tracking as [subject] enters [new space]. Shot on Arri Alexa 65, T2.8, film grain, 4k, ultra photorealistic
```

### 39.3 Seedance 2.0跟随运镜增强

在跟随运镜提示词末尾加入：
- `适配Seedance 2.0动态渲染功能`（动态跟踪更平滑）
- `适配Seedance 2.0智能对焦功能`（主体始终保持清晰）

### 39.4 跟随运镜常见错误修正

| 错误提示词 | 问题 | 修正 |
|-----------|------|------|
| "镜头跟随主角移动" | 太模糊，AI不知角度 | 明确角度：侧面/正面/背面/俯拍 |
| 一条提示词堆5个运镜 | 互相冲突 | 最多2-3个，有清晰切换逻辑 |
| 只写运镜不写背景变化 | 无"跟随感" | 必须描述背景后退/掠过/压缩 |
| 悲伤用快跟随 | 节奏不匹配 | 先定情绪再选节奏 |

---

## 四十、Grok Imagine元提示词框架提示词技巧

### 40.1 五步思维链输出模板（中文版）

```
整体构思：[一句话概括视觉叙事]

分镜脚本：
[0-1.5秒] 起：[镜头类型] - [场景建立] - [初始动态]
[1.5-4秒] 承：[镜头运动] - [动作推进] - [节奏展开]
[4-5.5秒] 转：[镜头变化] - [视觉高潮] - [情绪峰值]
[5.5-6秒] 合：[镜头收束] - [快速结尾] - [循环衔接]

详细参数：
第一阶段：运动强度[X/10]，[氛围建立]
第二阶段：运动强度[X/10]，[动态发展]
第三阶段：运动强度[X/10]，[高潮呈现]
第四阶段：运动强度[X/10]，[收束过渡]
节奏控制：[渐进式/起伏式/爆发式]
关键帧设置：1.5秒、4秒、5.5秒
```

### 40.2 构图→运动自动映射实战

根据故事板中的构图类型，自动选择最匹配的运镜方式：

| 画面构图 | 自动选择运镜 | 提示词片段 |
|---------|------------|-----------|
| 主体在画面1/3处（三分法） | 横向跟踪 | `tracking shot following subject along rule of thirds line` |
| 中心对称构图 | 缓慢zoom或旋转 | `slow zoom in on centered subject` 或 `gentle 180° orbit around subject` |
| 对角线引导 | 沿对角线轨迹运动 | `camera moves diagonally following leading line` |
| 前景框架包裹 | 景深穿越 | `rack focus from foreground frame to subject behind` |
| 引导线构图 | 沿线条跟随 | `camera follows [road/railway/river] toward subject` |
| 黄金螺旋 | 环绕运动 | `spiral orbit revealing subject at golden ratio point` |
| 三角形稳定构图 | 局部微动 | `subtle push-in, stable triangular composition maintained` |

### 40.3 6秒起承转合→AI视频完整案例

**雨中撑伞女孩**：
```
Overall Concept: Rain night solitude, rapid narrative from environment to emotion

Storyboard:
[0-1.5s] Opening: MS - Rainy street neon flickering - Girl's silhouette appears, motion intensity 2/10
[1.5-4s] Development: Push tracking - Side approach, raindrops falling - Details under umbrella emerge, motion intensity 5/10
[4-5.5s] Climax: Slight rotate to front - Girl stops and gazes - Raindrop freeze moment, motion intensity 4/10
[5.5-6s] Resolution: Quick pull out - Turn and continue - Merge into rain curtain, motion intensity 6/10

Rhythm Control: Progressive acceleration
Keyframe Settings: 1.5s, 4s, 5.5s
```

### 40.4 跨工具强度适配

| 工具 | 强度调整 | 原因 |
|------|---------|------|
| Kling 2.0 | 原强度降1档 | Kling动作偏大，原5→4 |
| Seedance 2.0 | 直接套用 | 精细化控制匹配 |
| Sora | 时间轴×1.67，强度+1 | 10秒视频需要更强动态 |
| Veo 2 | 英文模板直接用 | 原生英文优化 |

---

## 四十一、GPTimage2故事板+Seedance工作流提示词技巧

### 41.1 故事板生成提示词模板

```
【故事板提示】：[剧情类型]

1) [镜头1：建立场景，远景/静态，氛围描述]
2) [镜头2：角色A入画，中景，动作+情绪]
3) [镜头3：角色B反应，特写，情绪递进]
4) [镜头4：冲突/转折，中近景，动作升级]
5) [镜头5：高潮瞬间，大全景/快速运镜]
6) [镜头6：细节特写，微距，情绪顶点]
7) [镜头7：角色反应，中景，情绪回落]
8) [镜头8：定格/收尾，远景/静态，余韵]

【格式要求】
创建电影制作板/视觉规划表，比例16:9，展示短片完整概念。布局简洁、基于网格，分为清晰标记的部分：
- 共享创意指导（顶部栏）：镜头数量、统一调色板、环境背景
- 角色与风格参考：多角度模型（正面/背面/侧面/特写），服装配饰参考
- 环境与场景设计：场景概念图+俯视机位图（标注移动路径和摄像机位置）
- 故事板：8个编号帧，每个包含：摄像机类型、镜头大小、运动方式、动作情绪描述
- 灯光/情绪/风格备注：光线条件、氛围、纹理、时间过渡

所有分镜同一画风、同一色调、同一角色。
```

### 41.2 角色设定表提示词模板

```
请为以下角色生成专业角色设定表：

【角色信息】
Name: / Alias: / Role: / Age:
Personality: / Core Theme:

【设定表要求】
1) 全身多角度：正面、3/4侧面、侧面、背面，带身高比例尺
2) 表情变化：8种情绪（Neutral, Curious, Worried, Surprised, Afraid, Sad, Determined, Relaxed）
3) 细微表情：Subtle Eye Tension, Slight Smirk, Lip Tension, Controlled Breath
4) 头部多角度：3/4, Side, Top, Low, Diagonal
5) 标准站姿+5种姿势变化
6) 服装材质特写：4种细节
7) 武器/道具特写
8) 手部姿势：5种手势

【色彩板】（5-8个关键词）
【风格】（风格描述）
不要文字，不要水印，不要多余人物
```

### 41.3 Seedance视频生成提示词模板

```
根据提供的故事板，生成一镜到底的15秒视频。

【运镜要求】（按时间顺序列出每个分镜的运镜方式，标注动机）
- 0-2秒：[景别+运镜]，[动机]
- 2-4秒：[景别+运镜]，[动机]
- 4-7秒：[景别+运镜]，[动机]
- 7-10秒：[景别+运镜]，[动机]
- 10-15秒：[景别+运镜]，[动机]

【核心要求】
- 一镜到底，不要切镜头
- 运镜有合理动机，跟随角色动作自然过渡
- 无字幕、无解说
- 画面风格与故事板一致
- 角色外貌/服装与故事板完全一致
- 动作自然，有微表情和呼吸感
```

### 41.4 故事板→视频核心技巧

- **动机驱动运镜**：不要说「镜头推进」，要说「女主抬头时，镜头自然推到她面部」
- **时间戳精确控制**：关键镜头给足时间，过渡镜头短一些，总和=目标时长
- **角色锁定三重保险**：角色设定表→故事板内一致性→Seedance多图参考
- **迭代思维**：快速初版→针对性修改→再生成→重复3-5轮

---

## 四十二、AI真人短剧「文资视剪」提示词技巧

### 42.1 故事扩写提示词

```
请帮我把【XXX想法】扩写成一个适合AI真人短剧制作的剧本，时长控制在3分钟左右。要求：
1.剧情必须有强冲突、强反转、强情绪，不能写成普通小说片段。
2.开头3秒必须有钩子——当众羞辱、突然摊牌、一句狠话、一个反常动作，不要用风景、走路、空镜开场。
3.人物关系要简单，观众10秒内能看懂谁欺负谁、谁要反击谁。
4.台词要短、狠、直白，少用文艺腔，尽量符合真人短剧表达。
5.每30秒至少有一个情绪变化，每1分钟至少有一个小高潮。
6.前期让主角处在被压制状态，后面反击要有释放感。
7.场景不要太复杂，尽量控制在1到3个核心场景内。
8.请以剧本格式输出，包含【场景】、【时间】、【人物】、【动作描写】、【台词】。最后单独列出前15秒开场、核心爽点和结尾钩子。
```

### 42.2 资产提取提示词

```
请分析以上剧本，提取所有出场人物和核心场景，并生成AI绘画可用的中文提示词。

人物部分：每个角色包含姓名、年龄、身份、人物关系、外貌特征、发型发色、服装风格、核心气质、常见表情、关键动作，以及一段人物绘画提示词。
人物绘画提示词要求：全身远景，正面站立，纯色背景，真人写实电影质感，角色设定表，服装面料和面部特征清晰，不要文字，不要水印，不要多余人物。

场景部分：每个场景包含场景名称、出现剧情、时间、空间结构、光影氛围、材质细节、镜头视角，以及一段场景绘画提示词。
场景绘画提示词要求：场景概念图，真人短剧质感，真实物理光影，空间层次清晰，电影级构图，不要人物，不要文字，不要水印。

道具部分：请列出剧中需要保持一致的重要道具，并给出外观描述。
```

**四视图补充**：
```
[人物提示词]，生成角色四视图。画面左侧是人物面部超大特写，右侧依次放人物正面全身、侧面全身、背面全身，纯白背景，保持同一张脸、同一套服装、同一发型、同一体型。真人写实电影质感，不要文字，不要水印，不要明星脸。
```

### 42.3 分镜头脚本提示词

```
请根据以上剧本，帮我转换成可以直接用于AI视频生成的分镜头脚本。
规则如下：
每一段视频总时长控制在10到15秒。
每一段由4到5个镜头组成，每个镜头控制在2到4秒。
必须把剧本里的台词分配到对应镜头中。
每个镜头写清楚景别、机位、运镜、人物动作、人物情绪和画面重点。
情绪高潮点多用特写、推镜头、低角度仰拍。
双人对话保持180度轴线一致，角色A始终在画面左侧，角色B始终在画面右侧。
不要让人物突然换位置、换衣服、换脸。

每段结尾加上统一风格后缀：
真人写实短剧，35mm胶片拍摄，轻微胶片颗粒感，真实物理光影，高动态范围，视频不出现字幕，视频不出现音乐
```

### 42.4 统一风格后缀

所有AI真人短剧视频提示词末尾必须附加：
```
真人写实短剧，35mm胶片拍摄，轻微胶片颗粒感，真实物理光影，高动态范围，视频不出现字幕，视频不出现音乐
```

---

## 四十三、摄影师风格DNA提示词技巧

### 43.1 Ovidiu Selaru黑白光影提示词模板

```
black and white street photography, dramatic chiaroscuro, deep shadows with crisp edges, strong geometric lines, [subject description], solitary figure walking through light beam, layered urban depth, foreground silhouette, midground subject, distant vanishing point, high contrast, grainy texture, Ovidiu Selaru style. Shot on Arri Alexa 65, T2.8, film grain, 4k, ultra photorealistic
```

### 43.2 Billy Dinh电影感提示词模板

```
cinematic street photography, motion blur on passing figures, diagonal composition, teal and orange color grade, neon reflections on wet pavement, Wong Kar-wai aesthetic, Blade Runner atmosphere, [subject in cinematic moment], shallow depth of field, CineStill 800T film stock look, narrative tension. Billy Dinh style. Shot on Arri Alexa 65, T1.4, film grain, 4k, ultra photorealistic
```

### 43.3 Patrick Noack极简几何提示词模板

```
minimalist street photography, negative space composition, tiny figure in vast brutalist architecture, architectural abstraction, geometric patterns, [single subject dwarfed by structure], clean uncluttered composition, Patrick Noack style. Shot on Arri Alexa 65, T5.6, film grain, 4k, ultra photorealistic
```

### 43.4 Bas Hordijk几何色块提示词模板

```
street photography, bold geometric color blocks created by [architectural description], [a narrow shaft of golden light cutting through deep shadows between buildings / light trapped in architectural gap], a solitary figure as the only focal point, minimalist yet dramatic, cinematic narrative tension, 35mm film grain, Bas Hordijk aesthetic. Shot on Arri Alexa 65, T4.0, film grain, 4k, ultra photorealistic
```

### 43.5 Jake Michaels浓烈色彩提示词模板

```
cinematic street photography, blue hour, deep indigo sky gradient, warm amber streetlight glow, vibrant magenta neon reflection, oil painting texture, high saturation, dramatic chiaroscuro, [subject in decisive moment], shot on 35mm film, Kodak Portra 400, color grading: teal shadows warm highlights, Jake Michaels style. Shot on Arri Alexa 65, T2.8, film grain, 4k, ultra photorealistic
```

**配色核心**：大面积深蓝/靛青底色 + 小面积暖橘/品红点缀 = Jake经典配色

### 43.6 Eric Van Nynatten摄影九律提示词模板

```
[subject description], minimalist composition with single subject (法则1), limited color palette 2-3 dominant colors (法则2), [motion blur on moving element / sharp static background] (法则3), scale contrast tiny figure against massive [architecture] (法则4), high contrast chiaroscuro dramatic light and shadow (法则5), strong leading lines drawing eye to subject (法则6), frame within a frame through [archway/window] (法则7), low angle shot worm's eye view (法则8), window light / natural soft light from side (法则9). Eric Van Nynatten style. Shot on Arri Alexa 65, T2.8, film grain, 4k, ultra photorealistic
```

**九律组合策略**（一次用3-4条法则）：
- 构图优先：法则1+法则6+法则7
- 光影优先：法则5+法则9
- 对比优先：法则2+法则3+法则4
- 透视优先：法则8+法则6+法则4

### 43.7 摄影师风格+导演风格混搭提示词

混搭时在提示词中同时声明导演叙事风格+摄影师视觉风格：
```
[Director narrative style: e.g. Wong Kar-wai time dilation + fragmented editing] + [Photographer visual style: e.g. Billy Dinh cinematic street + teal orange color grade] + [Subject + Action] + [Camera movement + Lighting] + Shot on Arri Alexa 65, T2.8, film grain, 4k, ultra photorealistic
```

**混搭铁律**：
- 导演管叙事（怎么讲故事），摄影师管视觉（看起来怎样）
- 同类不混（两个极简摄影师不叠加），异类互补
- 最强组合示例：王家卫导演+Billy Dinh摄影=都市孤独感；诺兰导演+Ovidiu Selaru摄影=高压黑白悬疑
