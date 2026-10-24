---
name: movie-story
description: 电影级AI影视创作全流程智能体。整合剧本诊断、视觉锚点体系（角色身份板+场景参考图集+六维角色精度）、专业分镜生成（12列表格+镜头语法+镜头-动作融合书写）、AI图像/视频提示词工程（通用多镜头序列+Seedance 2.0多模态+写实质感层+表演提示词）、角色/场景/道具概念设计（Detail Sheet+Turnaround+Split View）、视觉美学体系（导演风格圣经+色彩情绪+摄影风格DNA+三阶段色彩演变）、场景类型景别模板（打斗/走路/吵架）、质量自检、混合工作流、场间Continuity Note等全链路能力。触发器：剧本转分镜、生成分镜脚本、AI视频提示词、Seedance、即梦、角色设计、场景概念图、道具设计、电影风格参考、分镜优化、剧本诊断、故事板、storyboard、shot list、镜头设计、video prompt、多镜头序列、全能参考、首尾帧、服化道、视觉锚点、身份板、场景参考图集、摄影师风格、导演风格、色彩脚本、打斗分镜、走路分镜、吵架分镜、表演提示词、微表情、三阶段色彩、镜头动作融合。
agent_created: true
---

# Movie Story — 电影级AI影视创作全流程

## 路由层 (Quick Route)

根据用户输入自动判断激活哪个模块：

| 用户输入特征 | 激活模块 | 说明 |
|-------------|---------|------|
| 剧本/script + 分镜/storyboard/shot list | 模块1→2→3→4 | 完整剧本→分镜流水线 |
| 已有分镜 + 视频/prompt/提示词 | 模块5 或 模块6 | 分镜→视频提示词转化 |
| Seedance/即梦/全能参考/首尾帧/多模态 | 模块6 | Seedance 2.0 专属模式 |
| 角色设计/服装/道具/场景概念 | 模块7 | 视觉资产设计 |
| 诊断/优化/检查剧本 | 模块1 | 剧本健康诊断 |
| 风格参考/摄影师/导演风格/色彩 | 模块8 | 视觉美学参考 |
| 混合拍摄/实拍+AI/Hybrid | 模块10 | 混合工作流 |
| 打斗/动作/武戏 | 模块11 | 场景类型景别模板 |
| 走路/行进/移动 | 模块11 | 场景类型景别模板 |
| 对话/争吵/对峙 | 模块11 | 场景类型景别模板 |
| 表演/微表情/人物生动感 | 模块12 | 表演提示词体系 |

**模糊输入时询问**：「您想做什么？A) 剧本诊断 B) 剧本→分镜 C) 分镜→AI视频提示词 D) Seedance多模态创作 E) 角色/场景/道具设计」

---

## 模块1：剧本健康诊断 (Script Health Diagnosis)

### 1.1 完整剧本加载 (Full Fidelity — 非协商)

读取并索引完整剧本，创建详尽清单：
- 每个场景标题（INT./EXT. + 地点 + 时间）
- 每一句对白及归属角色和括号说明
- 每一段动作/描述块
- 每一个转场/时间跳转点

输出声明：「完整剧本已加载 — X个场景，Y句台词，Z个动作块。最终验证100%覆盖。」

### 1.2 剧本健康报告 (Script Health Report)

以专业剧本医生+导演+摄影指导身份审查：

**必查清单**：
- **情节与逻辑**：漏洞、矛盾、未解决的铺垫、强行巧合 → 提出具体修复方案
- **节奏与结构**：拖沓段落、信息倾泻、薄弱幕转折 → 建议删减/扩展/蒙太奇/重排序
- **视觉叙事审计**：标记每个"说"（对白解释），转化为"展示"机会 → 具体镜头/符号建议
- **对白与角色**：生硬台词、直白对白、缺乏独特声音 → 重写建议（潜台词、精简、身体动作替代）
- **电影语言**：确定3-7个定义影片视觉的"标志性镜头"，定义全局视觉语言（色调、镜头选择、运镜风格、光影哲学）
- **基调与类型**：每个镜头服务于目标情绪/类型
- **制作可行性**：标注VFX重场、场地挑战、连续性风险
- **现代标准**：包容性呈现，避免刻板印象

**输出**：
- 剧本健康评分（/10）+ 理由
- 发现问题（关键/重大/打磨级）
- 具体优化措施列表
- 导演愿景陈述（2-3句）

---

## 模块2：视觉锚点体系 (Visual Anchor System)

**在分镜之前必须建立。这是整个分镜一致性的基石。**

详细规范见 `references/consistency-guide.md`。

### 2.1 角色视觉锚点表

为每个有台词或重要动作的角色建立：

```
角色：[名称]
├── 体型与轮廓：[剪影形状、身高、肩宽比]
├── 面部特征：[骨骼结构+肌肉走向+皮肤质感]  ← 六维精度拆解
├── 头部/发型：[发量/分缝/长度/光泽度/鬓角/发际线]
├── 服饰（锚定层）：[全片不变的 → 面料+剪裁+颜色+细节]
├── 服饰（变化层）：[逐场标注变化 → 脱衣/破损/换装因果链]
├── 标志性道具：[材质+佩戴位置+光线交互]
├── 体态习惯：[重心/呼吸/动作节奏/空间占有方式]
├── 色彩标签：[核心色+点缀色]
├── 面部表演基态：[默认表情 → 眼睑高度+视线落点+眉头+嘴角+下颌线]
└── 一致性红线：[2-3个绝对不可矛盾的核心特征]
```

### 2.2 角色六维精度拆解 (抽象→AI可执行)

| 维度 | 抽象写法❌ | 精度写法✅ |
|------|-----------|-----------|
| 1.体型与轮廓 | "身材高大威严" | 188cm/肩宽比1:1.8/剪影倒三角/重心前倾 |
| 2.面部特征 | "面容冷酷" | 颧骨突出/下颌线硬朗/眼窝深陷/薄唇微下压 |
| 3.头部/发型 | "发型整齐" | 黑色侧分/Superior hold发油/低光泽/鬓角干净 |
| 4.服饰 | "昂贵西装" | 深炭黑精纺羊毛120s/notch驳头8cm/单排两粒扣 |
| 5.标志性道具 | "名贵腕表" | 铂金壳/深灰盘面/40mm/左腕/冷白金属反射 |
| 6.体态习惯 | "气场压迫" | 后背不靠椅背/双臂展开搭扶手/食指1次叩击/3秒 |

### 2.3 角色身份板 (Identity Board)

角色锚点表的图像化版本——给AI模型看的角色研究图。

**构成**：英雄全身锚点图 + 多角度辅助研究 + 轮廓研究 + 表情研究 + 细节研究 + ID块

**布局原则**：不对称、留白、艺术书风格——NOT网格/NOT蓝图/NOT目录

**AI生成提示词要点**：
- 背景：纯白/柔和米白，无环境无道具
- 布局：`asymmetric elegant art-book layout, NOT a grid, NOT a blueprint, generous white space`
- 一致性：`STRICT consistency across ALL views — same face, same proportions, same clothing, same body`
- 分离：`NO overlapping figures, NO cropped faces, NO hidden limbs`
- 风格：`minimalist, cinematic, high-end, art-book quality, production-ready`

### 2.4 场景视觉锚点表

```
场景：[名称]
├── 空间结构：[面积/形状/关键家具/出入口]
├── 建筑材质：[石/木/金属 → 纹理+磨损+污垢]
├── 地面：[材质+反光特性+水洼/灰尘]
├── 光源体系：主光=[方向+色温]；轮廓光=[方向+色温]；补光=[来源+色温]
├── 色温基调：[数值+K] + 饱和度
├── 氛围元素：[雾/烟/体积光/飘浮颗粒 → 方向+层次]
├── 一致性红线：[光源方向/地面反光/氛围层次 → 不可矛盾]
└── 可变元素：[可微调不影响一致性的元素]
```

### 2.5 场景参考图集 (9机位核心镜头)

9张独立参考图，覆盖影视拍摄最常用景别+视角组合：

| 编号 | 镜头类型 | 叙事功能 |
|------|----------|----------|
| 1 | 正面近景 | 场景标志性元素特写 |
| 2 | 正面全景 | 人眼常规主视角，定场镜头 |
| 3 | 俯视近景 | 上帝视角地面细节 |
| 4 | 正面近景补充 | 不同层次前景 |
| 5 | 正面全景补充 | 特定氛围效果强化 |
| 6 | 俯视近景补充 | 光影层次聚焦 |
| 7 | 背面近景 | 反向机位，人物背影/主观视角 |
| 8 | 侧面全景 | 横向纵深，跟拍长镜头 |
| 9 | 俯视全景 | 完整上帝视角，开场定场 |

**一致性硬约束**：光影统一/色调统一/空间结构统一/材质精度统一

---

## 模块3：专业分镜生成 (Professional Storyboarding)

### 3.1 场景拆解

按场景标题行（INT./EXT. + 地点 + 时间）拆分。没有标准格式时按空间/时间转换点拆分。

对每个场景标注：
- 叙事节拍（建立/推进/转折/高潮/收束/过渡）
- 情绪基调（紧张/舒缓/悲伤/喜悦/恐惧/平静）
- 出场角色 + 当前状态
- 缺失信息推断（`[推断]`标注）

### 3.2 镜头模板（每个镜头必须使用）

```
**SHOT 047 — 4.2**
**场景**：INT./EXT. 地点 — 时间
**景别**：[ECU/CU/MCU/MS/WS/LS/ELS] + [构图细节] + [景深备注]
**运镜**：[静态/摇/移/推/拉/跟/升/降/手持/斯坦尼康] + [镜头mm] + [时长s]
**动作/调度**：[画面内容、角色走位、微表情]
**光影色彩**：[主光位置+电影参考] + [调色板] + [氛围]
**时长**：[X秒]（关键节拍保持Xs）
**声音/对白**：[台词、音效、配乐]
**优化备注**：[从原始剧本改进的内容]
**AI图像提示词**：[完整提示词含写实质感层]
```

### 3.3 镜头语法铁律

**摄影机位**（场景参考图集9机位体系可直接引用）：
- ECU: Extreme Close-Up → 细节/微表情
- CU: Close-Up → 面部/道具聚焦
- MCU: Medium Close-Up → 头肩，对话标准
- MS: Medium Shot → 腰部以上，动作表达
- WS/LS: Wide/Long Shot → 环境关系
- ELS: Extreme Long Shot → 孤立/渺小
- OTS: Over-the-Shoulder → 冲突/连接
- POV: Point of View → 主观认同
- Dutch: 荷兰角 → 不安/失衡

**运镜动机**（绝不随机）：
- 推(Dolly In) → 情感加强/发现
- 拉(Dolly Out) → 脱离/孤独/揭示环境
- 摇(Pan) → 跟随/扫描/揭示
- 手持(Handheld) → 紧迫/纪实/混乱
- 升(Crane Up) → 超脱/史诗/上帝视角
- 降(Crane Down) → 降临/进入/接地

**不可变铁律**：
- 新场景必须有定场/揭示性主镜头
- 连续不超过2个相似景别
- 运动必须由情感或动作驱动
- 插入镜头和空镜用于信息/讽刺/伏笔
- 情感节拍必须留足时间
- 场景结束需要强的视觉落点或转场设定

完整术语参考见 `references/cinematic-reference.md`。

### 3.4 镜头时长估算

| 镜头类型 | 推荐时长 | 关键因素 |
|----------|---------|----------|
| 定场镜头 (ELS/LS) | 4-8s | 环境信息量 |
| 全景 (WS) | 3-6s | 角色动作幅度 |
| 中景 (MS) | 3-5s | 对白长度 |
| 近景 (MCU) | 2-4s | 一句对白≈3s |
| 特写 (CU) | 2-4s | 情绪强度 |
| 大特写 (ECU) | 1-3s | 冲击力 |
| POV | 2-4s | 主观感知时间 |
| 动作镜头 | 1-3s | 快节奏=更短 |
| OTS | 3-6s | 双人对白 |

---

## 模块4：AI图像提示词生成 (AI Image Prompts)

### 4.1 四步黄金框架

**核心公式**：提示词 = 定镜头 + 构图语言 + 光影色彩 + 质感

```
第一步：定镜头（"怎么拍"）
  景别 + 角度 + 镜头 + 摄影机运动
第二步：构图语言（"画面怎么组织"）
  主体位置 + 前景/背景 + 引导线 + 负空间
第三步：光影与色彩（"情绪密码"）
  主光/辅光/轮廓光 + 色温 + 色板 + 情感映射
第四步：质感（"真实感层次"）
  材质/纹理/磨损/皮肤/光学 → 防AI塑料感
```

### 4.2 写实质感层 (Anti-AI-Plastic Layer)

每个图像提示词必须包含：

```
写实质感层 (stack):
- 皮肤：subsurface scattering, micropores, peach fuzz, natural skin texture, 
  slight imperfections, NO wax-like smoothness
- 眼睛：natural corneal light reflection, iris depth with radial fibers, 
  subtle tear film, blood vessels visible in sclera
- 材质：fabric weave visible, leather grain with wear marks, 
  metal with micro-scratches and patina, wood grain with natural variation
- 光学：anamorphic lens characteristics, subtle chromatic aberration, 
  filmic highlight roll-off, natural vignetting, lens breathing
- 禁止：over-sharpened, CGI artificial, plastic skin, HDR oversaturation, 
  Instagram filter look
```

### 4.3 专业电影打光位置

| 打光位置 | 叙事功能 | 电影参考 |
|----------|----------|----------|
| Rembrandt (45°高侧) | 深度、庄重、经典 | 《教父》 |
| Split Light (90°侧) | 分裂、双重人格 | 《搏击俱乐部》 |
| Loop Light (30°侧稍高) | 自然、亲切（最通用） | 商业对话戏 |
| Butterfly (正上方) | 魅力、神圣、权力 | 经典好莱坞 |
| Under-light (下方) | 恐怖、邪恶化 | 恐怖片 |
| Silhouette (逆光) | 神秘、匿名、浪漫 | 《爱乐之城》 |
| Volumetric (丁达尔) | 史诗、神性、希望 | 《银翼杀手2049》 |
| Practical Motivated | 真实、沉浸、纪实 | 《1917》 |

完整规范见 `references/cinematic-lighting.md`。

### 4.4 负面提示词 (Negative Prompt)

```
避免：plastic skin, wax face, CGI look, oversaturated, 
over-sharpened, watermark, text, logo, distortion, mutated limbs,
bad anatomy, extra fingers, fused fingers, ugly, blurry,
low quality, worst quality, jpeg artifacts, chromatic aberration, 
airbrushed skin, HDR tone mapping, Instagram filter
```

---

## 模块5：AI视频提示词 — 通用多镜头序列 (Universal Multi-Shot)

**适用工具**：Veo, Sora, Runway Gen-3, Kling, 可灵, Midjourney

### 5.1 动作节点与情绪拆解

分析输入场景，提取：核心动作 / 情绪核心 / 节奏签名 / 环境语境 / 关键细节

### 5.2 多镜头剪辑序列模板

```
Global Motion Style: create a sequence of [主体动作描述], 
as a raw handheld sequence with natural camera movement, 
in cinematic 24fps motion with film-like motion cadence, 
natural motion blur on movement, a theatrical presentation feel, 
professional cinema standard, no soap opera effect.
Shaky handheld camera style with natural camera shake 
and organic breathing movement throughout:

Shot 1 (Wide): [焦距mm] [角度] wide shot, camera [运动] as subject [动作];
CUT;
Shot 2 (Medium): [焦距mm] medium shot from a [角度], camera [运动] while following the subject in motion;
CUT;
Shot 3 (Close-up): [焦距mm] close-up, intimate handheld proximity with subtle shake, emphasizing [细节];
CUT;
Shot 4 (Over-the-shoulder): [焦距mm] over-the-shoulder [前/后] angle, [运动] with kinetic handheld energy;
CUT;
Shot 5 (Telephoto): [焦距mm] compressed telephoto from a [角度], [运动] with layered background motion;
CUT;
Shot 6 (Extreme/High-angle): [焦距mm] [角度] wide shot with a slightly unexpected tilted framing, accentuating [情绪品质].
```

**模板规则**：
- 镜头数：4-8（默认6），不得低于4或高于10
- 每个镜头必须有运镜、焦距、角度——不允许静态镜头
- **禁用词**：`smooth`, `steady`, `stabilized`, `tripod`, `gimbal`, `drone`

### 5.3 反肥皂剧锁 (Anti-Soap-Opera Lock)

每个提示词必须包含：`cinematic 24fps motion` / `film-like motion cadence` / `natural motion blur on movement` / `no soap opera effect` / `professional cinema standard`

### 5.4 手持有机感 (Handheld Organic Feel)

`raw handheld sequence with natural camera movement` / `shaky handheld camera style` / `natural camera shake and organic breathing movement throughout`

### 5.5 剪辑节奏分析

中文输出：剪辑逻辑 + 焦距策略 + 运镜节奏 + 情绪轨迹 + 参考电影

---

## 模块6：Seedance 2.0 多模态创作 (Seedance Multimodal Mode)

### 6.1 硬约束

**合规红线**：
- 禁止使用真实人脸素材（系统自动拦截）
- 替代方案：风格化角色/动漫/剪影/背影/非人类角色/第一人称POV
- 素材必须用 `@` 标注用途：`@素材1 作为[首帧/参考镜头/角色动作/配乐]`

**入口选择**：

| 输入 | 入口 |
|------|------|
| 仅首帧图片 + 提示词 | **首尾帧** |
| 多模态组合（图片+视频+音频） | **全能参考** |

### 6.2 五要素结构化提示词

```
【Seedance 2.0 结构化提示词】

主体描述：[角色/物体/场景详情 + 调色板]
动作指令：[运动类型 + 轨迹 + 节奏 + 环境互动]
镜头语言：[景别 + 运镜 + 角度 + 速度]
风格氛围：[艺术风格 + 色调 + 光影 + 氛围]
物理细节：[流体/刚体/材质互动 + 环境物理]

负面排除：避免画面抖动、角色变形、穿模、水印、模糊、低分辨率
```

### 6.3 参数配置

| 参数 | 逻辑 |
|------|------|
| 运动幅度 | 人物肖像→低；对话/走路→中；动作/追逐→高 |
| 风格化程度 | 首帧一致性→80-100%；真实感变化→60-70% |
| 生成时长 | 每段5-10秒；更长有漂移风险 |
| 生成模式 | 常规→标准；关键镜头→HD |

### 6.4 多片段叙事

```
【分镜序列规划】

片段1 (0-5s)：[场景简述]
  首帧：@图片1
  提示词：[五要素提示词]
  衔接：→ [匹配剪辑/动作顺接/声音桥接]

片段2 (5-10s)：[场景简述]
  首帧：[片段1末帧 或 @图片2]
  提示词：[延续风格，保持一致性...]
  衔接：→ [...]
```

**连续性规则**：
- 上段末帧=下段首帧
- 跨片段保持相同风格关键词
- 延续指令：「延续上一场景，角色继续[动作]，保持相同光影与色调」

### 6.5 音画同步映射

| 音频事件 | 视觉反应 |
|----------|----------|
| Beat drop/底鼓 | 冲击动作，动作剪辑 |
| 渐强/build-up | 缓慢推近，画面收窄 |
| 静默/breakdown | 静态全景，环境细节 |
| 旋律高潮/chorus | 动态镜头，揭示镜头 |
| 低音打击/sub drop | 画面震动，地面冲击 |

---

## 模块7：角色/场景/道具设计 (Visual Asset Design)

### 7.1 角色服化道设计 (Costume & Character Art)

**三步工作流**（电影服化道总监视角）：

**Step 1 — 材质拆解表**：
```
角色：[名称]
├── 面料A：[材质+织法+光泽度+颜色] → [位置]
├── 面料B：[材质+织法+光泽度+颜色] → [位置]
├── 配饰1：[材质+尺寸+位置+光线交互]
└── 核心质感：[哑光/亮面/半透明 → 参考实物]
```

**Step 2 — Detail Sheet 提示词**：
- 多角度面部特写
- 微距细节（面料/纹理/配饰）
- 全身服装展示
- 关键配饰独立呈现

**Step 3 — Turnaround View 提示词**：
- 正面/侧面/背面/3/4角度
- 重力打样（服装自然垂坠）
- 材质物理交互（SSS透光/anisotropic各向异性）

**铁律**：SSS仅用于皮肤/蜡烛/玉石 / anisotropic仅用于拉丝金属/CD纹/丝绸→drape布料必须有重力褶皱

完整规范见 `references/costume-character-bible.md`。

### 7.2 道具概念设计 (Prop Concept Design)

**三步工作流**（电影道具美术总监视角）：

**Step 1 — 材质介质拆解表**：
```
道具：[名称]
├── 主体材质：[材质+纹理+年代感+磨损]
├── 装饰材质：[材质+光泽+工艺]
├── 连接件：[材质+功能+尺寸]
└── 特殊效果：[发光/透明/动态 → 物理描述]
```

**Step 2 — Split View 设计图**：
- 全景完整视角（比例尺寸标注）
- 结构拆解图（部件分解）
- 5色色卡（材质颜色参考）
- 关键细节放大

**Step 3 — 去塑料感铁律**：
- 金属→微划痕+氧化+指纹
- 木材→纹理+磨损边缘+包浆
- 皮革→毛孔+褶皱+使用痕迹
- 织物→纤维/线头/起球/褪色
- 重力落地→接触面变形/阴影/环境反射

### 7.3 场景概念图

每个场景7项信息：名称/剧情/时间光线/空间结构/光影氛围/材质细节/镜头视角

提示词格式见模块2.5场景参考图集。

---

## 模块8：视觉美学与风格 (Visual Aesthetics & Style)

### 8.1 导演风格圣经 (Director Style Bible)

定义项目的全局视觉DNA：

```
项目视觉DNA：
├── 宽高比：[2.39:1 / 1.85:1 / 1.66:1 / 1.33:1 / IMAX 1.43:1]
├── 镜头偏好：[球面/变形宽银幕 → 具体型号(Supreme/MP/Master Anamorphic)]
├── 运镜哲学：[克制古典/手持纪实/流动长镜头/快速剪辑] → 动机说明
├── 光影美学：[自然主义/表现主义/黑色电影/高调/低调] → 参考影片
├── 色彩哲学：[具体色板 → 主色+辅色+点缀色+情绪映射]
├── 构图原则：[对称静态/动态偏移/极端角度/负空间/规则破坏]
├── 质感标准：[35mm胶片/数字干净/颗粒感/柔焦/锐利]
└── 标志性镜头：[3-5个贯穿全片的视觉签名]
```

### 8.2 色彩情绪圣经 (Color Palette Mastery)

| 情感 | 主色 | 辅色 | 光影 | 参考影片 |
|------|------|------|------|----------|
| 孤独/疏离 | 冷蓝灰 | 苍绿 | 低饱和度漫射 | 《她》 |
| 温暖/怀旧 | 暖琥珀 | 柔粉 | 金色逆光 | 《请以你的名字呼唤我》 |
| 危险/压迫 | 暗红 | 黑 | 高对比阴影 | 《七宗罪》 |
| 希望/新生 | 嫩绿 | 淡蓝 | 柔和高调 | 《白日梦想家》 |
| 权力/冷酷 | 深蓝黑 | 冷银 | 硬光高对比 | 《社交网络》 |
| 浪漫/梦幻 | 品红紫 | 暖橙 | 柔焦逆光 | 《爱乐之城》 |
| 焦虑/紧迫 | 去饱和绿 | 脏黄 | 荧光闪烁 | 《梦之安魂曲》 |
| 史诗/宏大 | 金色 | 深棕 | 体积光 | 《银翼杀手2049》 |

### 8.3 摄影师风格DNA参考

| 摄影师 | 风格DNA | AI提示词关键词 | 适用场景 |
|--------|---------|---------------|----------|
| Roger Deakins | 自然主义+精准构图 | natural light, clean composition, subtle color | 史诗/真实 |
| Christopher Doyle | 手持流动+霓虹色 | handheld fluid, neon palette, motion blur | 都市/情感 |
| Emmanuel Lubezki | 自然光+长镜头 | natural light, long take, immersive | 生存/自然 |
| Hoyte van Hoytema | 柔光+大画幅 | soft light, large format, film texture | 科幻/悬疑 |
| Bradford Young | 暗调+负空间 | deep shadows, negative space, texture | 剧情/黑色 |
| Greig Fraser | 高对比+氛围 | high contrast, atmosphere, haze | 动作/科幻 |
| Robert Richardson | 顶光+逆光 | top light, backlight, theatrical | 黑帮/传记 |

完整摄影师风格DNA见 `references/` 下对应文档。

---

## 模块9：质量自检体系 (Quality Assurance)

### 9.1 交付前自检清单（非协商）

```
□ 完整剧本覆盖：逐行逐场景对照原始剧本。每句对白、每个动作、每个场景段落100%覆盖。
□ 打斗/动作检查：多镜头拆解，遵循动作场景协议。不总结、不浓缩。
□ 每个主要故事节拍有专属视觉时刻？
□ 镜头指令具体、可行、电影化？
□ 图像提示词够详细够专业？
□ 整体感觉像真正导演的镜头清单？
□ 视觉锚点一致性：角色特征/场景光影/道具外观跨镜头一致？
□ 写实质感层已应用于每个AI提示词？
```

### 9.2 五轮自检协议

| 轮次 | 检查内容 | 通过标准 |
|------|----------|----------|
| 1 | 剧本覆盖度 | 100%覆盖，无遗漏 |
| 2 | 视觉一致性 | 所有锚点无矛盾 |
| 3 | 镜头语法 | 所有镜头遵守铁律 |
| 4 | AI提示词质量 | 每个提示词可用、专业、含质感层 |
| 5 | 整体验收 | 交付标准达成 |

---

## 模块10：混合工作流与高级技法

### 10.1 感知流畅性技术 (Perceptual Fluency)

- 广角镜头（28mm以下）→ 环境沉浸，AI生成稳定
- 避免连续AI生成镜头 → AI+实拍交替
- 声音=60%情感冲击 → AI镜头用音效设计弥补
- 末帧接力 → 上段末帧截图为下段AI生成参考

### 10.2 末帧接力 (Last-Frame Relay)

```
分镜1 (实拍) → 导出末帧PNG → AI生成分镜2（以末帧为首帧参考）
分镜2 (AI) → 导出末帧PNG → 实拍分镜3
交替进行, 感知流畅, 成本最优
```

### 10.3 分镜时间轴拆解

```
SHOT [编号]：[XXs]
├── 0-Xs：[阶段A] — [动作描述] / [表情变化] / [运镜节奏]
├── X-Ys：[阶段B] — [情绪转折] / [关键节拍] / [光变]
├── Y-Zs：[阶段C] — [收束] / [动机] / [转场信号]
```

### 10.4 五色标记系统

| 颜色 | 标记内容 | 功能 |
|------|----------|------|
| 🔴红 | 身体动作/走位/手势 | 轨迹、速度、身体接触 |
| 🔵蓝 | 摄影机运动/角度 | 运动方向、景别变化、对焦拉扯 |
| 🟢绿 | 构图/取景 | 主体位置、前景/后景、画框内关系 |
| 🟡黄 | 灯光/曝光 | 主光/辅光/轮廓光方向和变化 |
| 🟣紫 | 声音/音效 | 对白、环境音、音乐起止、音画关系 |

### 10.5 GPTimage2 + Seedance2.0 工作流

故事板五大模块格式：
1. **场景设定** — 时间/地点/环境/氛围
2. **角色状态** — 情绪/动作/服装/位置 → `@角色身份板[角色名]`
3. **镜头语言** — 景别/运镜/焦距/角度
4. **光影氛围** — 主光/辅光/色温/特效光
5. **AI提示词** — 整合以上，输出可直接用于GPTimage2的提示词

避坑清单见 `references/ai-generation-guide.md`。

---

## 模块11：镜头-动作融合书写系统 (Camera-Action Fusion)

**核心理念**：镜头运动和角色动作不是分开描述的，而是在同一个句子中"融合书写"。参考《大唐文圣》导演深度分镜版（知识库来源）的书写范式。

### 11.1 融合书写语法

```
【Camera Movement - [运镜类型]】[镜头运动详细描述]
【Action】[画面内容和动作描述]
【Action - Insert Shot】[插入镜头细节]
【Action - Lip Sync】[对口型台词]
```

**关键规则**：
- `Camera Movement` 和 `Action` 必须成对出现，不可单独存在
- 运镜描述用英文专业术语（Slow Dolly In / Whip Pan / Crane Up 等）
- 动作描述用中文，保持叙事节奏
- Lip Sync 标注用于有台词的镜头

### 11.2 融合书写示例

```
01【Camera Movement - Slow Crane Down / Tilt】
  摇臂从府邸层叠的瓦片缓缓下压，越过被风掀起的飞檐。
  【Action】狂风卷着雨沫斜扫入偏殿，吹得案上残烛疯狂摇曳。

02【Camera Movement - Slow Dolly In / Macro Focus】
  镜头贴近冰冷青砖地面缓行。
  【Action - Insert Shot】王勃满是血污的手指在积水中痉挛，
  指甲因剧痛死死抠入石缝。

03【Camera Movement - 360-degree Orbiting Shot】
  镜头围绕王勃快速旋转。
  【Action】金色经文从地面积水中螺旋飞起，圣光如潮水灌入后心，
  将四周雨幕瞬间震碎成水雾。

04【Camera Movement - Low Angle Push In】
  极低角度缓慢向前迫近。
  【Action - Lip Sync】王勃缓缓抬头，双目金光大盛。
  台词："谁给你的胆子，踩大唐文圣的手？"
```

### 11.3 融合书写 vs 传统分离式

| 对比维度 | 传统分离式 ❌ | 融合书写 ✅ |
|----------|------------|-----------|
| 镜头运动 | "摇臂下压" | `Slow Crane Down / Tilt` + 运动路径细节 |
| 画面动作 | "王勃手指痉挛" | `Action - Insert Shot` + 痛感细节 + 环境互动 |
| 节奏感 | 断句分离，节奏断裂 | 连续叙事，一气呵成 |
| AI视频指令 | 需二次翻译 | 直接可转化为Seedance/Kling Prompt |
| 导演可读性 | 像技术文档 | 像导演画分镜时的思维流 |

### 11.4 运镜类型速查表

| 运镜英文 | 中文 | 叙事功能 |
|----------|------|----------|
| Slow Crane Down / Tilt | 摇臂缓降/俯仰 | 环境揭示，从大入小 |
| Slow Dolly In / Macro Focus | 缓推/微距对焦 | 情感加强，细节聚焦 |
| Rapid Dolly In (Impact) | 冲击式急推 | 瞬间觉醒，视觉冲击 |
| Slow Truck Left/Right | 水平横移 | 空间扫描，环境关系 |
| Fast Whip Pan / Low Angle | 快速甩镜/低角度 | 暴力闯入，速度感 |
| Slow Dolly Out / Reveal | 缓拉/揭示 | 人物登场，空间展开 |
| 360-degree Orbiting Shot | 360°环绕 | 能量爆发，核心觉醒 |
| Slow Focus Pull | 焦点转移 | 注意力引导，悬念 |
| Low Angle Push In | 低角度迫近 | 压迫感，威压 |
| Rapid Crane Up / Wide | 急升/拉全 | 力量释放，史诗感 |
| Slider Tracking L→R | 导轨跟拍 | 动态连续性 |
| Dolly Out & Boom Up | 后拉上升 | 告别/升华/收束 |

---

## 模块12：场景类型景别模板库 (Scene-Type Shot Patterns)

**知识库来源**：乐享知识库「万能打斗景别」「万能走路景别」「吵架分镜」教学资料。

### 12.1 打斗/动作场景 9镜模板

任何打斗场景，遵循9镜覆盖：

| 镜号 | 景别 | 叙事功能 | 关键要点 |
|------|------|----------|----------|
| 1 | LS/ELS | 环境定场 | 空间关系+对手站位 |
| 2 | MS | 起手式/蓄力 | 重心变换+微表情 |
| 3 | CU | 武器/拳脚特写 | 速度线+材质交互 |
| 4 | LS 仰拍 | 第一击 | 低角度增强冲击力 |
| 5 | MCU 手持 | 交锋中段 | 短镜头快切，1-2s |
| 6 | ECU | 命中瞬间 | 慢动作+粒子飞溅 |
| 7 | MS Dutch | 失衡/受击 | 荷兰角+视线模糊 |
| 8 | OTS | 反攻/逆转 | 过肩视角建立代入 |
| 9 | ELS Crane Up | 战局全貌 | 升空俯瞰+残局氛围 |

**打斗AI提示词关键要素**：
- `dynamic fight choreography, impact frames, motion blur on action`
- `sweat spray, debris particles, fabric tearing, realistic impact physics`
- `--no static pose, stiff action, floating strikes, weightless movement`

### 12.2 走路/行进场景 7镜模板

| 镜号 | 景别 | 叙事功能 |
|------|------|----------|
| 1 | LS | 环境+人物剪影关系 |
| 2 | FS (Full Shot) | 全身+步态+节奏 |
| 3 | MS 侧面跟拍 | 步幅+手臂摆动 |
| 4 | CU | 脚部落地点+地面互动(水花/灰尘) |
| 5 | MCU 正面 | 面部表情+呼吸 |
| 6 | OTS 背后跟 | 主观代入+目的地暗示 |
| 7 | LS 远景 | 人物渺小/环境宏大 |

### 12.3 吵架/对峙场景 5镜情绪递进

| 镜号 | 景别 | 镜头语言 | 情绪层级 |
|------|------|----------|----------|
| 1 | MS 双人 | 建立空间关系 | 冷战/沉默 |
| 2 | MCU A | 一方发言 | 压制/攻击 |
| 3 | MCU B | 另一方反应（过肩） | 防御/反击 |
| 4 | CU A | 情绪爆发点 | 愤怒/崩溃 |
| 5 | LS/ELS Dutch | 关系破裂/分离 | 疏离/失落 |

**对话场景铁律**：
- 越愤怒越近（景别收缩）→ ECU
- 越疏离越远（景别拉开）→ ELS
- 正反打始终保持视线方向一致

---

## 模块13：表演提示词体系 (Performance Prompt System)

**知识库来源**：乐享知识库「表演提示词」— AI人物"假"的原因在于"太闲"。

### 13.1 核心洞察

AI人物之所以"假"，不是因为模型不行，而是因为**缺乏微观动作**——真人即使在静止状态也有持续的小动作（呼吸起伏、微表情变化、不自主的肢体调整）。

### 13.2 表演分层提示词框架

```
层级1 — 基础层（必须）：
breathing visible, slight chest rise and fall, natural blink rate,
micro-expressions shifting across face

层级2 — 状态层（选配）：
nervous: fidgeting fingers, glancing away, lip biting, shifting weight between feet
angry: jaw clenching, nostril flare, vein visible on temple, rapid breathing
sad: slow blink, downward gaze, slight shoulder slump, swallowing hard
happy: eye crinkle (Duchenne smile), relaxed posture, subtle sway
contemplative: furrowed brow, finger tapping surface, unfocused gaze into distance

层级3 — 环境互动（增强真实感）：
hair strands moving in breeze, fabric rustling with body movement,
sweat beading on temple, tear forming at lower lash line,
reflection of environment in eyes (catchlight detail)
```

### 13.3 Seedance 2.0 表演指令

```
"角色保持自然呼吸节奏，眼睑微微颤动，
指节在桌面下意识地轻叩3下，喉结因紧张而上下滑动一次，
随后用手背擦去额角细密汗珠。"
```

**关键**：动作需要具体数量（"3下"/"一次"）和时间顺序，不能空洞说"表现紧张"。

### 13.4 防"塑料感"表演检查清单

```
□ 角色是否有呼吸描述？
□ 是否有至少一个微表情变化？
□ 是否与环境有物理互动（触摸/摩擦/受风/受雨）？
□ 是否有不自主小动作（眨眼之外）？
□ 面部肌肉是否有不均衡运动（非对称微表情）？
□ 身体是否有重心微调？
```

---

## 模块14：三阶段色彩演变模型 (3-Phase Color Evolution)

**知识库来源**：《大唐文圣》导演分镜版 色彩演变章节。

### 14.1 相位模型

```
前段（建立/压抑）→ 中段（转折/冲突）→ 后段（释放/升华）
```

| 阶段 | 叙事功能 | 色彩策略 | 饱和度 | 对比度 |
|------|----------|----------|--------|--------|
| 前段 | 建立世界观、角色困境 | 主色调统治，低饱和 | <30% | 中低 |
| 中段 | 冲突升级、系统唤醒 | 互补色入侵，渐变过渡 | 30-60% | 中高 |
| 后段 | 高潮释放、新常态 | 补色对抗或融合，高饱和 | >60% | 高 |

### 14.2 实例参考

```
《大唐文圣》色彩演变：
○ 前段(压抑)：深青、暗蓝，极低饱和度，高对比闪电冷光
○ 中段(转折)：系统唤醒时的粒子金、琥珀光
○ 后段(霸气)：圣道金光与暴雨蓝的强烈补色对比
```

### 14.3 AI提示词中的色彩相位标注

```
@调色板:EP1_前段_冷蓝灰 → desaturated teal-blue, muted shadows
@调色板:EP1_中段_金琥珀 → warming transition, amber light bleeding in
@调色板:EP1_后段_金蓝对比 → high-contrast gold vs storm blue complementary
```

---

## 参考文档完整索引

### 核心规范
- `references/consistency-guide.md` — 人物/场景一致性控制指南
- `references/self-check-guide.md` — 自检优化指南
- `references/ai-generation-guide.md` — AI生成适配指南

### 剧本与分镜
- `references/script_health_report.md` — 剧本健康诊断协议
- `references/storyboard_spec.md` — 分镜规范（12列表格）
- `references/storyboard_example_template.md` — 分镜实例模板
- `references/storyboard-timecode-breakdown.md` — 逐秒情绪拆解法
- `references/storyboard-color-coding-system.md` — 五色标记系统

### 视觉锚点与角色
- `references/character_scene_bible.md` — 角色与场景圣经
- `references/costume-character-bible.md` — 服化道角色设计（Detail Sheet + Turnaround View）
- `references/costume-character-design-master.md` — 服化道角色设计母版

### 场景专项
- `references/romance_intimacy.md` — 爱情暧昧戏专项
- `references/multi_character.md` — 多角色场面调度
- `references/dialogue_emotion.md` — 对白情绪镜头语言
- `references/action_protocol.md` — 打斗/动作场景协议
- `references/fight-scenes.md` — 打斗场景详细拆解

### 场景类型模板（新增 — 知识库来源）
- `references/scene-shot-patterns.md` — 场景类型景别模板库（打斗9镜/走路7镜/吵架5镜）
- `references/camera-action-fusion.md` — 镜头-动作融合书写系统
- `references/performance-prompt-system.md` — 表演提示词体系（三层框架+防塑料感检查）
- `references/color-evolution-model.md` — 三阶段色彩演变模型

### 摄影与运镜
- `references/cinematic-reference.md` — 电影摄影参考（焦距/运镜/场景模板）
- `references/cinematic-lighting.md` — 专业电影打光位置
- `references/camera_movement_master.md` — AI视频运镜五大境界
- `references/ai-film-8-camera-movements.md` — AI电影八大运镜技巧
- `references/ai-video-follow-shot-guide.md` — 跟随运镜完全指南
- `references/ai-video-prompt-lens-reference.md` — 摄影机/镜头参数化

### 光影与色彩
- `references/lighting_and_color.md` — 光影与色彩脚本
- `references/ai-lighting-emotion-control.md` — AI光影情绪控制方法论
- `references/lighting_prompts_library.md` — 光影提示词库
- `references/jake-michaels-color-aesthetic.md` — 浓烈色彩美学
- `references/bas-hordijk-geometry-light.md` — 街头几何与色彩

### 提示词工程
- `references/aigc-structured-prompt.md` — AIGC结构化提示词框架
- `references/ai-prompt-generation.md` — AI绘画提示词全集生成
- `references/gpt-image2-prompt-collection.md` — GPT Image 2.0提示词合集
- `references/grok-imagine-meta-prompt-framework.md` — Grok Imagine元提示词框架
- `references/portrait_photography_prompts.md` — 人像摄影提示词

### 写实质感
- `references/photorealism-layer.md` — 写实质感层（含皮肤/眼睛/材质/光学）
- `references/realism_layer.md` — 写实质感防AI塑料感

### 视觉设计
- `references/visual-design-master.md` — 视觉设计母版（7角色+7资产包）
- `references/visual-consistency-reference.md` — @一致性标注体系
- `references/prop-design-master.md` — 工业级道具概念设计
- `references/ai-image-composition-10dimensions.md` — AI生图构图10维框架

### 混合工作流
- `references/hybrid-filmmaking-workflow.md` — Hybrid Filmmaking混合拍摄
- `references/hybrid-ai-filmmaking-workflow-2026.md` — AI电影混合工作流2026
- `references/ltx-studio-hybrid-workflow-jon-kent.md` — LTX Studio混合工作流
- `references/alex-zarfati-hybrid-filmmaking.md` — Alex Zarfati方法论
- `references/ai-short-drama-workflow.md` — AI真人短剧「文资视剪」
- `references/gptimage2-storyboard-workflow.md` — GPTimage2+Seedance工作流

### 美学参考
- `references/cinematic_style_library.md` — 电影风格库
- `references/camera_movement_guide.md` — 运镜完全指南
- `references/eric-vannynatten-9-rules.md` — 摄影九律
- `references/street-photography-aesthetic-for-ai.md` — 街头摄影审美→AI

### 质量与对比
- `references/quality_checklist.md` — 五轮自检协议
- `references/self-inspection.md` — 生成后自检清单
- `references/kling3-vs-seedance2-micro-expression.md` — Kling3 vs Seedance微表情对比
- `references/2026-ai-video-models-comparison.md` — 2026 AI视频模型对比

### Seedance专用
- `references/seedance-guide.md` — Seedance入口规则/@标注/参数/合规/多段连续性

### 工具脚本
- `scripts/screenplay_parser.py` — 剧本解析脚本
- `scripts/prompt_template.py` — AI提示词生成模板
- `scripts/storyboard_validator.py` — 分镜验证脚本

---

## 输出格式规范

### 完整交付物结构

```
# 《作品名称》分镜脚本

## 〇、视觉锚点表
### 角色视觉锚点
### 场景视觉锚点

## 一、剧本健康报告
### 评分 + 问题 + 优化 + 愿景

## 二、场景分解表
### 角色状态一览

## 三、逐场分镜
### 场景 S1：[标题]
SHOT 001 — 1.1
[完整镜头模板，使用镜头-动作融合书写格式]

### 场景 S2：[标题]
...

### 场间 Continuity Note
- **动作节奏配合**：[前段→中段→后段的运镜节奏变化]
- **视觉连续性**：[跨镜头需保持一致的元素追踪表]
- **特效提示**：[VFX衔接注意事项、关键道具位置一致性]
- **三阶段色彩演变**：[相位标注 + 每个相位的关键镜头编号]

## 四、AI视频提示词集
### 通用多镜头序列
### Seedance创作方案（如适用）

## 五、自检报告
### 覆盖度 / 一致性 / 质量

## 六、优化记录
```

---

## 技能边界与限制

1. **所有AI提示词输出为文本**，不直接调用AI生成工具。用户自行进入对应平台执行。
2. **剧本100%覆盖是非协商铁律**，不可跳过、不可总结。
3. **角色视觉一致性**是最高优先级，每个镜头必须回溯视觉锚点表。
4. **写实质感层**必须应用于每个AI提示词。
5. 本技能独立运行，不需要外部MCP工具。但生成图片/视频需要用户在对应平台操作。
