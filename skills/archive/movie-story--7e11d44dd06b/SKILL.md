---
name: movie-story
description: 电影级AI影视创作全流程智能体。整合剧本诊断、覆盖拍摄规划与空间坐标锁定（Coverage Planning + Spatial Coordinate Locking, 180°法则强制执行）、视觉锚点体系（角色身份板+场景参考图集+六维角色精度）、专业分镜生成（12列表格+镜头语法+镜头-动作融合书写+空间坐标标注）、AI图像/视频提示词工程（通用多镜头序列+Seedance 2.0多模态+写实质感层+表演提示词）、角色/场景/道具概念设计（Detail Sheet+Turnaround+Split View）、视觉美学体系（导演风格圣经+色彩情绪+摄影风格DNA+三阶段色彩演变）、场景类型景别模板（打斗/走路/吵架）、质量自检、混合工作流、场间Continuity Note等全链路能力。已内联电影级写实与场景丰富强制协议 + 眼泪物理强制规则 + 导演必修课7模块。集成OpenMontage端到端视频制作系统（12管线+52工具+500+Agent技能，从脚本到成片自动化）。触发器：剧本转分镜、生成分镜脚本、AI视频提示词、Seedance、即梦、角色设计、场景概念图、道具设计、电影风格参考、分镜优化、剧本诊断、故事板、storyboard、shot list、镜头设计、video prompt、多镜头序列、全能参考、首尾帧、服化道、视觉锚点、身份板、场景参考图集、摄影师风格、导演风格、色彩脚本、打斗分镜、走路分镜、吵架分镜、表演提示词、微表情、三阶段色彩、镜头动作融合、覆盖拍摄、coverage、空间坐标、180度法则、OpenMontage、端到端视频、自动化制作、兵器战分镜、weapon duel、wuxia fight、打戏提示词、fighting storyboard、场景丰富性、场景优化、scene richness、25-grid 场景、12-category 资产、场景提示词优化、中性正面肖像、正面参考图、角色锚点图、neutral front portrait、character reference portrait、frontal portrait、正面人物参考、布料真实感、面料质感、去塑料布料、fabric texture、cloth realism、fabric prompt、真实面料提示词、costume texture、服装质感、环境破坏、物体踢飞、砸碎分镜、刚体破碎、destruction physics、rigid body、物理破坏、环境互动打斗、破坏爽感、场景真实感、环境质感、去干净感、lived-in atmosphere、scene realism、environmental texture、weathered surfaces、scene detail enrichment、湿衣真实感、wet fabric、雨戏分镜、rain scene、落水镜头、wet clothing、sweat、出汗、water scene、湿布料、去塑料湿衣、AI防失真、anti-artifact、导演视觉控制、灯光模式、色温基调、调色风格、四步布光、质感打假、lighting direction、color temperature、color grading、film grain、texture authenticity、防变形手、光照匹配、多光源、dappled light、树影斑驳、neon reflection、金属渲染、metallic rendering、lighting reference、开场状态、首帧定场、scene opening state、opening frame、场景首帧、定场镜头、叙事意图、narrative intent、故事语法、story grammar、角色心理、character psychology、人物关系图谱、relationship graph、潜台词、subtext engine、视觉注意力、visual attention、情绪弧线、emotion arc、自动重写、auto rewrite、连续性状态机、runtime state、镜头本体、film language ontology。
agent_created: true
---

# Movie Story — 电影级AI影视创作全流程

**MANDATORY WORKFLOW: Always execute ALL phases in order. Never skip self-inspection (Phase 2) or Coverage Planning & Spatial Coordinate Locking (Phase 2.5). This is what makes output "professional" vs. amateur.**

**最高优先级强制协议（Non-Bypassable）**：
本技能已将《不可绕过的电影级写实与场景丰富强制协议 v1.0》+《眼泪物理强制规则》+《导演核心思维》+《导演必修课》7模块 + **《Script Fidelity Protocol v1.0（防缺斤少两强制协议）》** 等全部内容**完全内联**在此文件中。
- 在生成任何分镜、镜头描述或AI Image Prompt前，必须严格执行内联的全部8条强制规则 + 5阶段自检流程。
- 必须在最终AI Image Prompt输出前明确声明："已通过电影级写实与场景丰富强制协议全部检查"。
- **防缺斤少两强制规则**：Phase 1 必须输出 Script Line Index 编号表；Phase 3 每镜头必须标注 Script Coverage Tag + Dialogue Ownership Tag；Phase 4 必须输出 Coverage Verification Matrix，任何❌行不得声明"100%"。口头声明"100% coverage"无效，只有逐行Matrix全✅才有效。
- 本协议为本技能最高优先级规则，任何情况下不得绕过、简化或妥协。

---

## 电影级写实与场景丰富强制协议完整内联规则
**（完全内联版 · 不可绕过）**

### 第一部分：写实风格强制规则（Photorealism Mandatory Rules）

**规则1（风格锁定）**：必须在提示词中**明确且强势**声明写实风格，禁止任何风格化倾向。
- 必须包含：`photorealistic, hyperrealistic, ultra photorealistic, realistic live-action cinematic film still, purely photographic, no cartoon, no anime, no manga, no illustration, no stylized rendering, no comic style`

**规则2（相机与技术参数强制）**：每个提示词必须包含专业电影摄影参数。
- 必须出现：`shot on Arri Alexa 65` 或 `shot on Arri Alexa LF`
- 推荐搭配：`85mm lens` / `50mm prime lens`、`T2.8` / `f/2.8`、`shallow depth of field`、`subtle realistic film grain`

**规则3（人物质感强制）**：所有人物相关提示词必须包含以下真实人体细节：
- 皮肤：`detailed realistic skin texture, visible skin pores and fine lines, natural subtle skin redness and healthy complexion, directional facial lighting with natural chiaroscuro (shadows under cheekbones/nose/lip folds), non-uniform illumination, visible film grain and natural skin noise on texture, fine dust particles, no over-smoothed or over-clean skin, subsurface scattering (SSS)`
- 眼睛：`lifelike eyes with realistic catchlights and reflections`
- 材质：`realistic fabric texture and physics, natural cloth draping and wrinkles, accurate material response to light`

**规则4（反塑料感强制）**：必须主动对抗AI常见塑料/蜡质问题。
- 明确加入：`no plastic skin, no waxy skin, no overly smooth skin, no shiny plastic texture, natural imperfections`

**规则4.5（眼泪物理强制 — 涉及哭泣/情绪崩溃镜头时适用）**：
当镜头涉及眼泪时，必须强制使用以下真实眼泪物理描述（不可省略核心细节）：
真实人类眼泪从内眼角缓慢溢出，半透明生理盐水质感，表面有细腻的环境光反射，顺着脸颊自然滑落，受重力影响呈不规则曲线，在颧骨处汇聚后滴落，打湿皮肤形成湿润反光，晕开少量睫毛膏，留下淡淡的泪痕，睫毛上挂着细小的泪珠。面部肌肉自然紧绷，嘴唇微微颤抖，整体情绪克制。

**规则4.7（布料真实感强制 — 凡有衣物/布料出现必须执行）**：
任何镜头中只要出现衣物或布料，必须强制加入以下真实面料质感描述，消除AI常见塑料光滑感。

**通用强化描述（所有布料必加核心句）**：
```
physically accurate fabric simulation, realistic cloth dynamics and inertia, natural tension and compression in folds and drapes, pronounced natural texture irregularities and roughness, visible individual fiber texture with clear yarn thickness variations and inconsistencies, natural slubs, neps, thick-thin yarn variations and weave imperfections, high-frequency micro surface details and natural surface noise, lived-in fabric with subtle patina, wear marks, natural aging, slight fading and creasing in high-contact areas, raw authentic hand-feel with visible imperfections and unevenness, accurate material-specific light absorption vs reflection that reveals surface roughness, varied directional sheen that exposes texture irregularities, complex multi-layered folds with realistic gravity and body movement response, not overly clean or polished, not uniform or perfect surface, raw and imperfect texture, no uniform plastic smoothness, no waxy artificial gloss, no CGI plastic texture, no overly idealized clean fabric
```

**分面料专用描述（按面料类型选加）**：

| 面料类型 | 专用强化描述 |
|---------|------------|
| **毛呢/羊毛类** | `pronounced fuzzy fiber halo and natural unevenness, visible slubby yarn texture with thick-thin variations, high-frequency micro surface details and natural noise, raw wool-like hand-feel with visible imperfections, lived-in subtle patina and slight wear, directional light revealing fiber roughness and texture irregularities` |
| **棉麻/可见纱线类** | `visible individual yarn and weave structure with natural irregularities, pronounced slubby and uneven thread texture, high-frequency micro weave details, raw cotton/linen hand-feel with visible imperfections and slight yarn tension variation, natural surface noise and texture roughness, directional light revealing yarn variations and weave imperfections` |
| **细腻平纹/罗纹类** | `fine but visible rib or plain weave with subtle yarn variation, delicate natural surface texture and micro irregularities, soft but authentic hand-feel with slight unevenness, natural light interaction revealing fine weave details, not overly smooth or plastic-like, lived-in subtle texture` |
| **高光泽缎面/真丝类** | `lustrous satin/silk with natural directional sheen that varies with folds and viewing angle, realistic heavy drape with complex natural folds and weight, subtle surface texture and micro imperfections visible under light, accurate light absorption and reflection on real fabric, not uniform plastic gloss, lived-in natural folds with slight unevenness` |

**布料专用 Negative Prompt（必须加入）**：
```
plastic texture, waxy sheen, overly smooth fabric, uniform gloss, artificial shine, CGI fabric, plastic-like material, perfect clean surface, no texture, flat even lighting on fabric, overly polished, too clean, pristine fabric, idealized smooth texture, no imperfections, perfectly uniform weave, overly glossy, mirror-like sheen, clean polished look, too perfect, no roughness, no natural variation, overly idealized, synthetic plastic look
```

**布料光照建议（搭配上述描述使用效果最佳）**：
- 毛呢/棉麻：使用 `directional raking light revealing fabric texture roughness, yarn variations, slubs and micro-imperfections, natural shadows accentuating uneven surface and lived-in wear`
- 缎面/真丝：使用有明确方向的主光 + 适度补光，让光泽随褶皱自然变化

**规则4.8（场景环境真实感强制 — 凡有场景/环境出现必须执行）**：
任何镜头中只要出现场景、环境、建筑、室内外空间，必须强制加入以下高真实感提示词，消除 AI 常见的"太干净、太完美、无菌感"问题。

**通用强化正向提示词（所有场景必加核心句）**：
```
photorealistic, ultra realistic, lived-in atmosphere, natural atmospheric perspective, subtle airborne dust and micro particles visible in light beams, volumetric god rays with realistic light scattering, soft diffused natural lighting, imperfect light falloff and natural shadows, realistic color grading with slight color cast, subtle desaturation in distance, highly detailed textures: weathered building facades, realistic brick and stone with cracks, stains, moss, dirt accumulation, peeling paint, worn surfaces, aged plaster, realistic glass windows with reflections, refractions, smudges, fingerprints, water streaks, subtle distortions and imperfections, ground details: realistic asphalt or concrete with cracks, oil stains, small debris, scattered leaves, uneven wear, subtle puddles or damp patches, cinematic depth of field, subtle film grain, natural lens imperfections, slight chromatic aberration, moody yet natural lighting
```

**场景通用反向提示词（必须加入）**：
```
clean, sterile, pristine, spotless, brand new, overly polished, perfect surfaces, smooth textures, plastic look, artificial, digital art, 3d render, cgi, unreal engine, no dirt, no dust, no stains, no scratches, no cracks, no wear, no weathering, no imperfections, no grime, no smudges, no fingerprints, no water stains, no peeling paint, no rust, no moss, perfect reflections, mirror-like reflections, overly shiny, glossy surfaces, waxy, airbrushed, photoshopped, crystal clear windows, oversaturated colors, vibrant, sharp focus everywhere, no atmospheric haze, no dust in air, no volumetric light, no film grain, no street debris, showroom perfect, too clean, idealized, fantasy style, uncanny valley
```

**场景专项加强词（按场景类型选加）**：

| 场景类型 | 专用强化描述 |
|---------|------------|
| **欧洲街道/小巷** | `detailed street level clutter, wet reflections on cobblestone, scattered leaves and trash, realistic sidewalk texture` |
| **建筑立面/门窗** | `highly detailed facade, aged stone and brick, realistic window glass with interior visibility and reflections, subtle condensation` |
| **城市天际线** | `heavy atmospheric haze, city smog and pollution particles, realistic depth fog, light bloom on windows` |
| **室内空间** | `realistic interior dust motes in light beams, worn floors with scuffs, subtle air haze, aged materials` |
| **古装/历史场景** | `weathered wooden beams with natural grain and age cracks, ancient stone walls with moss and erosion, aged ceramic tiles with chips and patina, worn paper/wooden surfaces with water stains and smoke darkening, natural aging of period-accurate materials` |

**场景光照建议（搭配上述描述使用效果最佳）**：
- 外景：`natural golden hour light with atmospheric perspective, realistic light falloff and natural ambient occlusion`
- 室内：`soft diffused natural lighting through dirty/dusty windows, volumetric dust in light beams, imperfect light scattering`
- 夜景：`realistic street lighting with light falloff and color temperature shift, natural lens flare, sodium vapor or tungsten light cast`

**规则4.9（湿衣/湿身真实感强制 — 涉及雨戏/水戏/落水/出汗等衣物湿润镜头时必须执行）**：
任何镜头中只要出现衣物被水浸湿（雨、落水、游泳、出汗、泼水等场景），必须强制使用以下湿衣真实感描述，彻底消除 AI 常见的塑料/橡胶/亮面质感。

**核心原则（避免塑料感）**：
- **半透明**：局部半透明，隐约见肤，但有渐变和层次，非均匀透明
- **粗糙纹理**：纤维颗粒感、织物起伏保留，遇水后纹理更明显而非消失
- **真实湿润**：颜色变深、吸水变重、下垂褶皱加深、水痕流动、碎裂高光（非均匀塑料亮面）

**通用湿衣正向提示词（必加核心句）**：
```
realistic soaked fabric with semi-translucent wet areas clinging to skin, visible coarse fiber texture and rough textile surface details even when wet, natural water absorption making fabric darker and heavier with natural sagging folds, water droplets and streams running along wrinkles with broken specular highlights, damp matte areas mixed with subtle water sheen, intricate textile wrinkles and fabric physics, no uniform plastic shine or glossy rubber look, no latex texture, photorealistic wet fabric
```

**湿衣专用反向提示词（必须加入）**：
```
plastic texture, rubber, latex, glossy uniform shine, smooth surface, doll-like, artificial wet look, shiny film, waxy wet cloth, perfect uniform wetness, CGI wet fabric, overly reflective wet clothing, no visible texture when wet, transparent plastic wrap effect, mannequin-like wet clothing
```

**湿衣专项加强词（按场景类型选加）**：

| 场景类型 | 专用强化描述 |
|---------|------------|
| **大雨/暴雨** | `heavy rain soaking through fabric, visible water streams and rivulets cascading down clothing, fabric heavy and sagging with accumulated water weight, natural water droplets clinging to textile surface, broken rain-shattered highlights on wet fabric` |
| **落水/溺水/游泳** | `fully submerged fabric with realistic water displacement, fabric floating and wrapping around body in water, hydro-dynamic cloth simulation, waterlogged heavy material clinging to skin, natural water tension on textile surface` |
| **汗水/炎热** | `subtle sweat stains on fabric, localized damp patches on chest and back, slight sheen on damp areas, natural salt water evaporation marks on dark fabric, realistic sweat-soaked cotton with darker patches` |
| **泼水/淋湿** | `splashed water droplets on fabric surface, wet spray pattern with natural distribution, partial wetness with dry-wet transition zone, realistic water absorption gradient from splashed to dry areas` |

**湿衣布料类型建议（按衣物材质选加）**：

| 布料类型 | 湿态特征描述 |
|---------|------------|
| **棉质T恤/衬衫** | `cotton t-shirt completely soaked, semi-translucent cling effect, coarse fiber texture visible through wet areas, water absorption darkening the fabric, heavy sagging folds` |
| **真丝/缎面** | `silk dress with water causing clinging drape, translucent with visible body silhouette, heavy water-laden fabric with complex wet folds, directional sheen disrupted by water rivulets` |
| **麻布/亚麻** | `linen shirt soaked through with visible weave structure, rough texture intensified when wet, natural slubby irregularities visible, darker wet patches with fabric grain` |
| **毛呢/羊毛** | `wool coat heavy with rain water, fiber halo flattened by moisture, matted texture with visible yarn structure, water droplets sitting on rough fiber surface` |

**湿衣光照建议**：
- 雨戏：`overcast natural lighting with rain-softened shadows, occasional light catch on water droplets, natural ambient illumination without harsh specular highlights`
- 水下：`subsurface light caustics filtering through water surface, blue-green color cast from water medium, soft diffused underwater lighting`
- 出汗：`warm natural lighting catching subtle sheen on damp skin and fabric, realistic skin texture with perspiration micro-droplets`

### 第二部分：场景丰富度强制规则（Scene Enrichment Mandatory Rules）

**规则5（分层与深度强制）**：场景必须有清晰的前景-中景-背景层次感。
- 必须描述至少3个层次的内容。
- 推荐使用：`layered composition, foreground elements, midground details, background depth`

**规则6（氛围与光线互动强制）**：必须加入真实的环境氛围和光线物理互动。
- 必须包含：`volumetric lighting, god rays, atmospheric haze, dust motes in light beams`
- 必须描述具体光源如何与材质互动。

**规则7（制片设计与生活痕迹强制）**：场景必须有"被使用过"的真实感。
- 必须加入：`lived-in atmosphere, weathered surfaces, natural patina, aged materials, subtle environmental storytelling details`

**规则8（具体性强制）**：禁止泛化描述，必须具体到材质、年代痕迹、光线来源和粒子效果。

### 第三部分：强制执行机制（5阶段自检流程）

在生成任何提示词前，必须严格执行以下流程，且**不可跳过任何阶段**：

**Phase 1: 输入分析**
分析场景/人物类型，识别潜在简陋或风格化风险。

**Phase 2: 写实规则自检（逐条确认）**
- [ ] 风格锁定词已强势加入？
- [ ] 相机参数（Arri Alexa + 镜头 + 光圈）已包含？
- [ ] 皮肤、眼睛、材质真实细节已强制写入？
- [ ] 已明确禁止塑料感/漫画风？
- [ ] 含衣物/布料时：已加入规则4.7布料真实感描述 + 分面料专用描述 + 布料 Negative Prompt？
- [ ] 含场景/环境时：已加入规则4.8场景环境真实感正向核心句 + 场景反向提示词 + 场景专项加强词？
- [ ] 涉及雨戏/水戏/落水/出汗等湿衣镜头时：已加入规则4.9湿衣真实感正向核心句 + 湿衣反向提示词 + 场景/布料专项加强词？

**Phase 3: 场景丰富度自检（逐条确认）**
- [ ] 场景已分3层以上描述？
- [ ] 已加入体积光 + 氛围粒子 + 光线与材质互动？
- [ ] 已加入风化/生活痕迹/制片设计细节？
- [ ] 光源描述具体且有物理真实感？

**Phase 3.5: 眼泪物理自检（仅当涉及哭泣/情绪崩溃镜头时）**
- [ ] 已强制融入真实眼泪物理描述（缓慢溢出、半透明生理盐水质感、重力不规则曲线、湿润反光、晕开睫毛膏等）？
- [ ] 眼泪呈现真实生理盐水质感而非不自然流动？

**Phase 3.6: 布料质感自检（仅当镜头含衣物/布料时）**
- [ ] 已加入通用布料真实感强化核心句（physically accurate fabric simulation...）？
- [ ] 已根据面料类型选用对应专用描述（毛呢/棉麻/平纹/缎面）？
- [ ] 已加入布料专用 Negative Prompt（禁止 plastic texture/waxy sheen/overly smooth fabric 等）？
- [ ] 已根据面料选择光照策略（毛呢/棉麻用 raking light，缎面用定向主光）？

**Phase 4: 综合优化与融合**
将写实规则 + 场景丰富规则自然融合进提示词。

**Phase 5: 最终确认**
输出前必须明确声明：
**"已通过电影级写实与场景丰富强制协议全部检查。"**

只有通过以上全部阶段，才能输出最终提示词。

---

**Director's Core Mindset Integration (导演核心思维强制融入 — 新增)**

本技能已将《导演必修课》全部7个模块的核心原则完全内联。生成任何分镜前，必须像专业导演一样思考：

**核心原则（不可省略）**：
- 每个镜头必须服务于 **Want vs Need 的冲突** 或 **情绪弧线**。
- 必须明确这一镜的 **情绪功能**（钩子 / 升级 / 爆发 / 余韵）。
- 短剧每集必须有明确 **爽点或情感峰值**。
- 所有视觉选择（景别、运动、光影、表演）必须服务于**情绪与叙事**，而非单纯"好看"。

**在Phase 2自检中必须额外检查**：
- Want vs Need 是否被视觉化呈现？
- 这一场景/镜头的核心情绪功能是什么？
- 是否有明确的爽点或情感爆发设计？
- 节奏是否服务于短剧观众的"上头"体验？

---

**CRITICAL RULE — Full Script Fidelity (Non-Negotiable):**
- Process the ENTIRE original script without ANY omission, summarization, condensation, or skipping.
- Every single line of dialogue, every parenthetical, every action description, every scene heading, and every segment of the play MUST be preserved and accounted for in the final storyboard.
- At the end of processing, perform an explicit self-check: Cross-reference the original script line-by-line/scene-by-scene against the generated storyboard to confirm 100% coverage. If any dialogue or segment is missing, immediately correct it before outputting.
- Never say "summarized for brevity" or "key scenes only" — the output must be complete.

---

## Phase 1: Ingestion & Structured Parsing

- Accept script as pasted text, file path (use read_file if needed), or URL.
- **Full Fidelity Parsing (Mandatory):** Read and index the COMPLETE script. Create an exhaustive inventory:
  - Every scene heading (INT./EXT., location, time).
  - Every single line of dialogue with speaker attribution and parentheticals.
  - Every action/description block, even short ones.
  - Every transition or slugline.
- Do NOT summarize or skip any segment. **MANDATORY: Output a visible Script Line Index (剧本行号索引表) — not a "mental checklist".** This table is the anchor for all subsequent phases; any line not in this table is guaranteed to be lost.

**Script Line Index Format (Phase 1 强制输出):**

| 行号 | 类型 | 内容摘要 | 字数/时长预估 | 覆盖状态 |
|------|------|---------|-------------|---------|
| L001 | 场景头 | INT. 教室 - 白天 | — | ⏳待分配 |
| L002 | 动作描述 | 小明低头翻开课本... | 25字 | ⏳待分配 |
| L003 | 对白 | 小明：「我不想回家」 | 8字/≈4s | ⏳待分配 |
| L004 | 括号注释 | （声音颤抖） | — | ⏳待分配 |
| L005 | 动作描述 | 窗外传来雷声... | 15字 | ⏳待分配 |
| L006 | 转场 | CUT TO: / 场景切换标记 | — | ⏳待分配 |
| ... | ... | ... | ... | ... |

**规则**：
- 逐行编号原始剧本**所有内容**（场景头/动作/对白/括号注释/转场标记/空行间情绪暗示），不得省略任何行。
- 「覆盖状态」初始为 ⏳待分配，Phase 3 逐镜头生成后实时更新为 ✅已覆盖（标注SHOT编号），最终 Phase 4 校验时任何 ⏳ 项即为遗漏。
- 长剧本（>50行）触发 **Chunked Processing**：分块处理（每块≤1完整场景+完整Phase流水线），块间通过Script Line Index接力，确保前后不断层。
- 此表在后续所有Phase中持续可见、持续更新，是「100% coverage」的唯一证据来源。
- Parse into:
  - Header: Title, Writer, Genre, Tone, Target length (if given), Aspect ratio (default 2.39:1 cinematic).
  - Logline / Premise (infer if missing).
  - Complete scene-by-scene inventory with dialogue count and key action summaries (for tracking only — never omit content).
  - Character bible (main + supporting, key traits, arcs).
  - Key props, symbols, recurring motifs.
- Produce clean "Script Summary" section first (1-2 paragraphs + bullet metadata) **plus** a note: "Full script loaded — X scenes, Y dialogue lines, Z action blocks. 100% coverage will be verified at the end."

## Phase 2: Rigorous Self-Inspection & Optimization (Non-Negotiable)

Treat every script like a professional script doctor + director + cinematographer. Perform this audit **before** any shot breakdown. Output the full "Script Health Report" visibly.

**Mandatory Audit Checklist (apply scene-by-scene + globally):**
- **Plot & Logic**: Holes, contradictions, unresolved setups, forced coincidences? Propose concrete fixes (e.g., "Add 2-line callback in Scene 5 to planted gun in Scene 1").
- **Pacing & Structure**: Slow sections? Info dumps? Weak act breaks? Recommend: trim X lines, expand emotional beat Y with visual sequence, insert montage for time passage, change scene order.
- **Visual Storytelling Audit**: Flag every "tell" (exposition via dialogue) and convert to "show" opportunities. Suggest specific shots/symbols (e.g., "Instead of 'she is sad', show her staring at empty chair with single tear – hold 6s").
- **Dialogue & Character**: Stilted lines? On-the-nose? Unique voices? Suggest rewrites for subtext, economy, interruptions, physical actions that reveal (e.g., "Character 1: (avoiding eye contact) 'It's fine.'").
- **Cinematic Language**: Identify 3-7 "signature shots" that define the film's look (hero shot, recurring motif shot, climax visual). Define global visual language (color palette, lens choice, movement style, lighting philosophy).
- **Tone & Genre Fidelity**: Ensure every shot supports intended emotion/genre (horror: negative space + slow builds; action: dynamic angles + speed ramps; drama: intimate close-ups + natural light).
- **Production Practicality**: Note VFX-heavy shots, location challenges, actor blocking needs, continuity risks.
- **Modern Standards**: Inclusive representation, avoid lazy stereotypes, strong female/POC agency where appropriate.
- **Coverage Planning (对话场景强制)**: For any scene with significant dialogue or character interaction, has the Coverage Planning & Spatial Coordinate Locking Protocol been executed? Is there a clear scene-level Coverage Strategy with Master + Singles + OTS + Reaction coverage? Are spatial coordinates defined and locked?

**Output of Phase 2 (always show this to user):**
- **Script Health Score** (out of 10) with justification.
- **Issues Found** (bulleted, prioritized Critical / Major / Polish).
- **Specific Optimizations Applied** (list changes: "Rewrote Scene 3 action to visual reveal instead of monologue. Added insert of cracked photo for theme. Shortened dialogue by 40% for rhythm.").
- **Revised Script Excerpts** (key changed sections in **bold** for additions, ~~strikethrough~~ for deletions).
- **Director's Vision Statement** (2-3 sentences): overall visual style, recurring motifs, emotional through-line via camera.

**Only after presenting this report and getting implicit/explicit approval, proceed to Phase 2.5.**

## Phase 2.5: Coverage Planning & Spatial Coordinate Locking (强制执行)

**触发条件**：凡场景中包含**显著对话、情绪互动、权力关系变化、多人物对峙**的内容，必须执行本协议。

**目标**：像实拍导演一样规划覆盖拍摄，通过显式空间坐标锁定场景几何关系，确保AI生成一致性与后期剪辑灵活性。

### Coverage Strategy 输出格式（必须输出）

```markdown
**Coverage Strategy — Scene X**

| 编号 | 镜头类型 | 核心作用 | 后期用途 |
|------|---------|---------|---------|
| C1 | Master (WS/MS) | 锁定空间关系与初始权力动态 | 定场 + 全景揭示 |
| C2 | Clean Single - 角色A | 给予A表演空间与情绪微表情 | 情绪切入 |
| C3 | Clean Single - 角色B | 给予B表演空间与反应空间 | 反应剪辑 |
| C4 | OTS → A | 强化关系张力 | 对话节奏 |
| C5 | OTS → B | 不对称处理 | 权力暗示 |
| C6 | Insert/Reaction | 手/道具/眼泪/环境细节 | 情绪高潮切入点 |
```

**最小覆盖标准**：Master + 双方 Clean Single + 至少1个 OTS + 1-2个 Reaction/Insert。

### Spatial Coordinate Locking 系统

**场景级空间坐标锚点**（每个重要场景只做一次，锁定后不可随意更改）：

- **Master Axis (C1)**：由第一个 Master/全景镜头确立的主轴线。后续镜头原则上必须保持在此轴线同一侧（严格遵守180°法则）。
- **坐标原点**：主要家具中心或房间关键结构。
- **高度基准**：Eye Level ≈ 1.6m。

**每个 SHOT 必须强制标注**：

```markdown
**Spatial Coordinates**:
- Axis: [Maintaining / Intentionally Breaking] Master Axis C1
- Camera Position: C[X], [Eye/Low/High] Level (Z=[X.XX]m), Distance to subject: [X.X]m
- Primary Subject: Screen [left/right/center], Depth ≈ [X.X]m
- Framing Note: [Rule of thirds / Center + 负空间方向]
```

**AI Image Prompt 中必须加入**：
"Strictly maintain Master Axis C1 and spatial relationships. Camera position and subject depth exactly as described in Spatial Coordinates. No axis crossing unless explicitly noted."

**自检项**：
- 是否制定了明确的 Coverage Strategy？
- 第一个详细镜头是否已定义并锁定 Master Axis C1？
- 所有后续镜头是否声明轴线一致性？
- 坐标标注是否具体（有距离、屏幕位置、高度）？

---

## Phase 2.8: Narrative Reasoning & Shot Intelligence（叙事推理与镜头智能层 — 强制分析步骤）

> **核心理念**：AI导演不是"镜头描述器"，而是"叙事决策系统"。在进入分镜之前，必须先完成7步推理分析，建立场景的完整理解模型。每一步推理的输出将直接驱动Phase 3的镜头决策。
>
> **强制规则**：Phase 3分镜生成前，必须完成本阶段全部7步分析。跳过任何一步的分镜判定为低质量。任何没有叙事动机的镜头，应被判定为无效镜头。
>
> **核心优先级**：`叙事意图 > 人物关系 > 情绪变化 > 视觉注意力 > 镜头美感 > 角色外貌展示`

### 2.8.1 叙事意图识别（Narrative Intent Engine）

AI不得先决定镜头再找理由；必须先识别叙事意图，再推导镜头语言。

**15类叙事意图**：

| 意图类型 | 含义 | 推荐镜头策略 | 推荐运镜 | 推荐剪辑 |
|---------|------|------------|---------|---------|
| RevealInformation | 揭示信息/秘密/身份/线索 | CU / Insert / Rack Focus | Slow Push In | Delayed Cut |
| HideInformation | 隐藏信息/遮蔽真相 | Silhouette / Partial Face | Static / Slow Lateral | Cut Before Answer |
| BuildSuspense | 制造悬念/紧张 | CU + Empty Space | Slow Push In | J-Cut / Long Hold |
| BuildEmotion | 强化人物情绪 | CU / MCU（随情绪强度递进） | Motivated Push | Slow Cut |
| ShiftPower | 表现权力关系变化 | Low Angle(胜者)/High Angle(败者) | Push In to Dominant | Reaction First |
| EstablishRelationship | 建立人物关系 | Balanced OTS / 2-Shot | Static / Slow Track | Moderate Cut |
| CreateIsolation | 强调孤独/疏离 | Wide / Single | Pull Out | Long Hold |
| CreateIntimacy | 强调亲密/依赖 | CU / External OTS | Static / Slow Push | Slow Cut |
| CreateThreat | 制造威胁/压迫 | CU + Negative Space | Slow Creep | Pre-Lap Audio |
| CreateRelief | 缓解情绪/释放压力 | Medium Wide | Pull Out | Fade / Slow Dissolve |
| Foreshadowing | 埋伏笔 | Insert / Background Detail | Static / Rack Focus | Quick Insert |
| MisleadAudience | 误导观众 | Blocked Composition | Static | Cut Before Reveal |
| BreakTrust | 信任破裂 | OTS → Single（关系断裂） | Axis Shift | Delayed Silence |
| MoralChoice | 道德选择 | ECU / CU (面部挣扎) | Locked / Micro Push | Delayed Cut |
| ConfirmSuspicion | 确认怀疑 | CU → Reaction | Rack Focus to Evidence | Hold After Reveal |

**输出格式（每个场景必须声明）**：
```
Scene Narrative Intent:
  Primary: [意图类型] — [具体说明]
  Secondary: [意图类型] — [具体说明]
  Anti-Intent: [必须避免的意图] — [原因]
```

### 2.8.2 故事语法分析（Story Grammar Engine）

镜头不是孤立的，而是属于故事段落。AI必须识别场景当前所处的叙事阶段。

**7阶段场景结构**：

| 阶段 | 含义 | 推荐景别 | 推荐运镜 | 推荐剪辑速度 | 光比建议 |
|------|------|---------|---------|-----------|---------|
| Setup | 建立场景/人物/关系/空间 | Wide / MW | Slow or Static | Slow | Readable (2:1-4:1) |
| Development | 推进信息/增加互动 | Medium / OTS | Motivated Tracking | Moderate | Moderate (4:1-6:1) |
| Conflict | 冲突出现或升级 | CU / Tighter OTS | Push In / Handheld | Faster | High Contrast (6:1-8:1) |
| Crisis | 人物被迫选择 | CU / ECU | Locked / Slow Push | Delayed | Maximum Contrast (8:1+) |
| Climax | 情绪/动作最高点 | CU / ECU / Action Insert | Fast Push / Impact | Fastest | Maximum Contrast |
| Resolution | 结果显现/情绪释放 | Medium / Wide | Pull Out | Slower | Moderate |
| Aftermath | 余波/沉默/后果 | Wide / Silent CU | Static | Long Hold | Low Key / Readable |

**输出格式（每个场景必须声明）**：
```
Scene Story Stage: [Setup/Development/Conflict/Crisis/Climax/Resolution/Aftermath]
Scene Energy Level: [0.0-1.0]
Energy Direction: [Rising/Falling/Plateau/Peak/Drop]
```

### 2.8.3 角色心理画像（Character Psychology Engine）

AI不得只根据台词生成表情，必须根据潜台词和心理状态推导镜头。每个在场角色必须建立心理画像。

**角色心理状态结构**（每个角色必填）：

```json
{
  "character": "角色名",
  "external_focus": "看向谁/看向什么",
  "internal_focus": "内心真正在想什么",
  "visible_emotion": "外表显示的情绪",
  "hidden_emotion": "真实内心情绪",
  "dominance": 0.0-1.0,
  "body_tension": 0.0-1.0,
  "eye_contact_stability": 0.0-1.0,
  "desire": "想要什么",
  "fear": "害怕什么"
}
```

**关键参数含义**：
- `dominance`：0=完全被动/1=完全掌控。直接影响机位角度（高dominance→低角度仰拍，低dominance→高角度俯拍）
- `body_tension`：0=完全放松/1=极度紧绷。影响运镜稳定性和呼吸感
- `eye_contact_stability`：0=完全回避/1=稳定直视。低稳定性→单人镜头+半阴影，高稳定性→双人镜头+正反打

**心理状态到镜头映射**：

| 心理状态 | 推荐景别 | 推荐运镜 | 推荐构图 |
|---------|---------|---------|---------|
| fear | CU, 85mm+ | Slight Push In | 主体偏左/右，负空间放大恐惧感 |
| anger | CU, Handheld | Unstable Push | 主体居中，压迫感构图 |
| shame | High Angle CU | Static | 面部被遮挡（手/头发/阴影） |
| dominance | Low Angle, Centered | Stable, Longer Lens | 主体占画面60%+，居中 |
| deception | Single Shot | Slow Lateral | 半阴影，视线不稳定 |
| grief | Wide → CU | Slow Push + Hold | 负空间表达孤独感 |

### 2.8.4 人物关系图谱（Character Relationship Graph）

AI必须理解：情侣正反打、审讯正反打、敌人正反打、上下级正反打的镜头逻辑完全不同。

**关系图谱结构**（每对在场角色必填）：

```json
{
  "A_to_B": {
    "trust": 0.0-1.0,
    "fear": 0.0-1.0,
    "hostility": 0.0-1.0,
    "power_gap": -1.0 to 1.0,
    "dependency": 0.0-1.0,
    "secret_shared": true/false
  }
}
```

**关键参数到镜头的直接影响**：

| 参数值 | 镜头策略 |
|-------|---------|
| 高信任 (trust > 0.7) | Balanced OTS, 50-85mm, 柔光, 慢剪 |
| 低信任 (trust < 0.3) | Single Shot / 分离构图, 物理间距, 延迟反应 |
| 权力差距大 (|power_gap| > 0.5) | 强者→低角度/居中/大景别；弱者→高角度/边缘/被遮挡 |
| 高敌意 (hostility > 0.7) | Tight CU, Push In, 快剪, 高对比光 |
| 隐藏依赖 (dependency > 0.5 + trust < 0.3) | 反应镜头优先，对话后Hold |

### 2.8.5 潜台词分析（Subtext Engine）

电影镜头应该拍潜台词，而不只是拍台词。AI必须识别每句台词下的真实意图。

**13类潜台词**：

| 潜台词 | 含义 | 镜头策略 |
|-------|------|---------|
| suspicion | 怀疑 | Slow Push In, Reaction First, 视线不稳定, Hold After Line |
| attraction | 吸引 | Soft CU, 85mm, Long Hold, 眼线短暂后移开 |
| rejection | 拒绝 | Single Shot, Pull Out, 负空间扩大 |
| guilt | 愧疚 | High Angle, 被遮挡构图, 沉默区延长 |
| superiority | 优越感 | Low Angle, Centered, 稳定运镜 |
| fear_of_exposure | 害怕暴露 | CU + Negative Space, 眼线回避, 微表情特写 |
| hidden_love | 隐藏爱意 | Soft CU, 85mm, Long Hold, 眼线短暂接触后移开 |
| hidden_threat | 隐性威胁 | CU + Negative Space, Low Key, Static, Cut to Listener Reaction |
| manipulation | 操控 | Dominant Single, Slow Lateral, 操控者占据空间apex |
| surrender | 投降 | High Angle, 身体收缩构图, 深景深展示孤立 |
| betrayal | 背叛 | Axis Shift, 动态越轴, 对比增强, 延迟沉默 |
| grief | 悲伤 | Wide → CU, 负空间, 长Hold |
| moral_conflict | 道德冲突 | ECU, Locked, Split Lighting（一半明一半暗） |

**触发条件**：当角色台词与其hidden_emotion不一致时，必须按潜台词类型选择镜头策略，而非按台词字面意思。

### 2.8.6 视觉注意力优先级（Visual Attention Engine）

AI必须明确告诉观众"此刻看哪里、看多久、为什么看"。

**注意力优先级结构**（每个镜头必填）：

```json
{
  "attention": [
    {"target": "角色A的眼睛", "priority": 1, "reason": "检测恐惧微表情"},
    {"target": "桌上的枪", "priority": 2, "reason": "伏笔"},
    {"target": "背景的门", "priority": 3, "reason": "潜在威胁"}
  ]
}
```

**控制注意力的方法**：
- **焦点控制**：Rack Focus / 浅景深 / 锐度优先
- **构图引导**：Center Framing / 三分法 / Leading Lines / Frame within Frame
- **光影引导**：Highlight Target / Darken Background / Color Isolation
- **运镜引导**：Push In to Target / Pan to Reveal / Tracking
- **剪辑引导**：Insert Shot / Reaction Cut / Delayed Reveal

**注意力错误（必须避免）**：
- ❌ RandomFocus：焦点落在无叙事意义对象
- ❌ OvercrowdedFrame：画面信息过载
- ❌ WeakHierarchy：主次不清
- ❌ PrematureReveal：过早暴露关键信息
- ❌ MissingForeshadow：没有拍到伏笔物

### 2.8.7 情绪弧线追踪（Emotion Arc Engine）

AI必须避免所有镜头一个情绪、一个节奏、一个景别。每个场景必须有情绪弧线。

**场景能量曲线**（每个场景必填）：

```
Scene Energy Curve:
  Setup: 0.2 → Development: 0.4 → Conflict: 0.7 → Climax: 0.95 → Aftermath: 0.3
```

**能量级别到镜头映射**：

| 能量级别 | 推荐景别 | 推荐运镜 | 推荐剪辑 | 推荐声音 |
|---------|---------|---------|---------|---------|
| 低 (0.0-0.3) | Medium Wide | Static | Slow | Natural Room Tone |
| 中 (0.3-0.6) | Medium / MCU | Slow Push | Moderate | Subtle Tension |
| 高 (0.6-0.8) | CU / MCU | Push / Handheld | Fast | Intensified |
| 极高 (0.8-1.0) | CU / ECU | Handheld / Fast Push | Fastest | Peak Intensity |
| 骤降 (Peak→Drop) | Wide / Static CU | Pull Out / Locked | Long Hold | Silence / Room Tone |

**角色情绪递进（多镜头场景必填）**：
```
Character Emotion Arc (角色A):
  Shot 1: calm → Shot 2: doubt → Shot 3: fear → Shot 4: anger → Shot 5: collapse → Shot 6: silence
```

### 2.8.8 叙事推理层自检（生成Phase 3前必须确认）

- [ ] 每个场景是否声明了Primary + Secondary Narrative Intent？
- [ ] 场景Story Stage是否已识别？能量级别和方向是否合理？
- [ ] 每个在场角色是否有完整心理画像（external_focus/hidden_emotion/dominance/body_tension）？
- [ ] 每对互动角色是否有关系图谱（trust/fear/power_gap/hostility）？
- [ ] 潜台词是否已识别？镜头策略是否匹配潜台词而非台词字面？
- [ ] 每个镜头是否声明了视觉注意力优先级（至少3级）？
- [ ] 场景是否有完整的情绪弧线和能量曲线？
- [ ] 是否存在"无叙事动机"的镜头？（如有，必须删除或补充动机）

---

## Phase 3: Professional Cinematic Storyboard Creation

Break the **optimized** script into industry-standard shots. Number shots globally (SHOT 001, 002...) and per scene (e.g., 3.4 = Scene 3, Shot 4).

**For Every Scene:**
- Scene header + purpose (story beat it delivers).
- **Coverage Strategy Reference**: Apply the pre-planned Coverage Strategy from Phase 2.5 (Master + Clean Singles + OTS + Reaction shots). Clearly state how many shots are allocated to coverage vs. inserts.
- Recommended total shots for scene + rationale (e.g., "14 shots: 1 establishing + 1 Master + 4 coverage (2 Singles + 2 OTS) + 5 reaction/inserts + 3 inserts for emotional punctuation").
- Overall lighting/mood for scene.

**Scene Opening State Module（场景开场状态模块 — 强制首帧定场 — 每个场景必须独立输出，不可跳过）**

> **核心理念**：在进入任何镜头之前，必须先建立一个完整的"世界快照"——就像电影的第一帧定场镜头，让观众在看到任何动作之前就已经"身临其境"。这个模块是分镜的地基，所有后续镜头的视觉信息都从这里生长出来。
>
> **强制规则**：每个场景必须有且仅有一个开场状态模块，位于该场景所有镜头之前输出。即使场景只有一个镜头，也必须先输出开场状态再进入镜头描述。

**开场状态模块包含以下6个子模块（按顺序输出）**：

**① 环境定场（Environment Establishing）**
```
环境：@场景名，[时间/天气]，[主光源描述 + 辅助光源]，[空气/粒子/氛围效果]，[色调/饱和度/冷暖碰撞]<环境声特征>。
```
- 必须包含：时间、天气、主光源方向与色温、空气质感（微尘/雾气/烟/雨沫）、色调倾向
- 触发规则4.8时：加入lived-in atmosphere核心句 + 场景专项加强词
- 触发规则4.9时：加入湿态环境描述
- 目标：读者闭上眼睛就能"看到"这个场景

**② 站位关系（Spatial Relationship & Blocking）**
```
站位关系：@角色A [位置/姿态] 与 @角色B [位置/姿态]，[空间距离/高低落差]。
```
- 明确所有在场角色的空间位置、身体姿态、相互关系
- 标注高低落差、距离感（亲密/社交/公共距离）
- 多人场景需标注层级（前景/中景/背景）和轴线方向

**③ 角色状态（Character States）**
```
@角色名·状态标签：[位置]，[面朝方向]，[身体姿态/表情]，[关键身体细节/伤痕/妆容/发型]。
```
- 每个在场角色独立一行，使用@角色名·状态标签格式
- 必须包含：身体姿态、面部状态、关键视觉细节（伤痕/妆容/发型/配饰）
- 状态标签反映场景开场时的即时状态（如·被打之后、·醉酒态、·刚醒来）

**④ 服装状态（Costume/Wardrobe State）**
```
@服装名·状态标签：穿在 @角色名 身上；[当前状态：破损/污渍/湿透/整齐]；[关键细节]。
```
- 服装独立于角色描述，强调材质、状态变化
- 触发规则4.9时：详细描述湿态材质变化
- 服装状态是角色经历的外化——"衣服会讲故事"

**⑤ 灯光体系（Lighting System）**
```
灯光：主光为[来源/方向/色温/硬光or柔光]，[覆盖区域]；副光为[来源/方向/强度比]；[轮廓光/背光描述]；环境光为[实用光源列表]。
```
- 必须用四步布光法描述：Key → Fill → Rim → Ambient
- 标注色温（K值）、光质（硬/柔）、覆盖区域
- 与模块8导演视觉控制联动

**⑥ 声音氛围（Soundscape & Atmosphere）**
```
声音氛围：[环境声] + [特定音效] + [配乐情绪方向]，<心理感受>。
```
- 环境声：风声/雨声/人群/机械/自然
- 特定音效：脚步回声/钟表滴答/远处雷鸣
- 配乐情绪方向：沉默/紧张弦乐/温暖钢琴

**开场状态模块完整范例**：
```
开场状态：

环境：@皇家寝殿长廊（楼上），中午，冷白自然光束与昏暗暖黄光交织，空气中清晰可见浮动的微尘，冰冷灰调与贵族暖金色的冷暖碰撞，低饱和度<空旷长廊内的微回声>。

站位关系：@King George 蹲在 @Agnes Hartwell·被打之后 的面前，@Agnes Hartwell·被打之后 跪于中央地板上。

@Agnes Hartwell·被打之后：位于长廊中央的地板上一侧，面朝 @King George、跪姿，低头垂下眼睫，面朝长榻一侧；后背有流血的鞭伤痕迹，满身狼狈。

@King George：位于 @Agnes Hartwell·被打之后 面前，蹲着，身体自然放松，面朝跪在地上的 @Agnes Hartwell·被打之后。

@底层灰色杂役棉裙·鞭刑残破态：穿在 @Agnes Hartwell·被打之后 身上；后背破损，被血迹浸染。

灯光：主光为右上方长廊高窗透入的冷白自然光束，硬光覆盖长廊局部端；无副光；实用光为墙壁两侧的青铜雕花壁灯，开启发出昏暗的暖黄光。

声音氛围：空旷长廊的微回声 + 远处隐约的仆人脚步 + 沉默<压抑、权力悬殊的窒息感>。
```

**开场状态模块自检（生成后必须确认）**：
- [ ] 每个场景都有独立的开场状态模块？
- [ ] 环境描述包含时间+光源+空气质感+色调？（闭上眼能"看到"）
- [ ] 所有在场角色都有站位关系+独立角色状态行？
- [ ] 服装状态是否独立描述且反映角色经历？
- [ ] 灯光体系是否使用四步布光法（Key/Fill/Rim/Ambient）？
- [ ] 声音氛围是否包含环境声+特定音效+配乐方向？

---

**For Each Individual Shot – Use This Exact Professional Template (已融合《导演必修课》全部7模块):**

**SHOT 047 – 4.2**
**Scene**: INT. ABANDONED WAREHOUSE - NIGHT (post-optimized)

**Director's Intent**:
- **Narrative Intent**（来自Phase 2.8.1）: [RevealInformation/ShiftPower/...] — [本镜头的具体叙事目的]
- **Story Stage**（来自Phase 2.8.2）: [Setup/Conflict/Climax/...] — Energy Level: [0.0-1.0]
- **Story Beat / Emotional Purpose**: 本镜核心情绪功能（钩子 / 升级 / 爆发 / 余韵）。明确服务于Want vs Need冲突或爽点/情感峰值。
- **Character Psychology**（来自Phase 2.8.3）: [角色] visible=[外表情绪] / hidden=[真实情绪] / dominance=[0-1] / body_tension=[0-1]
- **Subtext**（来自Phase 2.8.5）: [潜台词类型] — 镜头策略：[按潜台词而非台词字面选择]
- **Performance Focus**: 眼神类型（温柔注视 / 死亡凝视 / 锐利直视等） + 关键微表情 + 呼吸状态 + 情绪落点。

**Script Coverage Tag（防缺斤少两 — 每镜头强制标注）**：
- **覆盖行号**: L[xxx]-L[yyy]（标注本SHOT覆盖的Script Line Index行号范围）
- **覆盖类型**: [场景头→定场 / 动作→镜头描述 / 对白→台词分配 / 转场→过渡SHOT / 情绪空白→情绪insert]
- **对白所有权**（仅当本SHOT含台词时）:
  ```
  @台词来源: L[xxx]-L[yyy]（角色：「台词内容」）
  @字数统计: [N]字
  @分配语速: [X]字/秒
  @基础时长: [Y]s（含情绪叠加+[Z]s + hold+[W]s）
  ```
  *一条台词跨多个SHOT时，必须标注拆分点与各段字数，不得整块塞入一个镜头或直接跳过。*

**Visual Attention Priority**（来自Phase 2.8.6）:
1. [首要焦点] — [叙事原因]
2. [次要焦点] — [叙事原因]
3. [第三焦点] — [叙事原因]

**Framing**: Extreme Close-Up (ECU) on protagonist's trembling hands, shallow DOF, rule-of-thirds with negative space right.
**Camera**: Slow push-in (dolly + slight handheld micro-movements) from 2m to 0.5m over 7 seconds. 35mm anamorphic lens, subtle flare on practical bulb. Motivated by emotional pressure building.
**Spatial Coordinates**: Axis: Maintaining Master Axis C1 | Camera: C1, Eye Level (Z=1.60m), Distance to subject: 0.8m | Primary Subject: Center frame, extreme close-up on hands | Note: Consistent with Scene Master shot spatial relationships. Light direction locked.
**Action/Blocking**: Hands clench around rusted pipe. One finger twitches – micro-expression of resolve. Subtle breathing visible in shoulders. Dust motes float in beam of light. Background: blurred figure of antagonist entering frame left (out of focus).
**Lighting & Color (Motivated Lighting)**: Low-key, single practical tungsten bulb from above-left creating harsh shadows and rim light on knuckles. Desaturated teal-green palette with warm practical accent. Mood: claustrophobic tension, isolation. Light has clear source and interacts realistically with skin texture and metal.
**Performance Details**: Eyes locked in focused, intense gaze with subtle micro-tension in eyelids. Breathing slightly restrained. Micro-expression of quiet resolve in jaw and finger twitch. No plastic skin, realistic subsurface scattering and catchlights aligned with practical light source.
**Duration**: 7.5 seconds（精准计算 · 表演从容）
**Timing Breakdown** (示例，无对白镜头): 纯动作 + 微表情resolve + slow push-in完成 + 最终hold。按协议计算得出7.5s（动作有重量，呼吸自然）。
（注：有对白镜头必须按《对白时长精准计算协议》展示详细字数 + 叠加时间 breakdown）
**Sound/Dialogue**: No dialogue. Distant drip SFX + rising low drone in score. Breath audible.
**Optimization Note**: This replaces original dialogue explanation with pure visual subtext – strengthens character agency and allows audience to feel the decision. Light, performance, and spatial coordinates all serve the emotional beat.

**镜头-动作融合书写系统（强制不可绕过 — Enforce Professional Standards in Every Shot）**：

**核心执行原则（最高优先级强制执行）**：

1. **绝不割裂**：画面描述（尤其是 Action/Blocking、主要视觉叙述、AI Image Prompt 的叙事部分）禁止把「人物动作」和「镜头运动」拆成两段独立列表或孤立语句。

2. **必须融合**：将人物具体动作、微表演、惯性、情绪落点与镜头运动有机结合成一段或两段流动的、电影化的叙述，像导演现场给摄影师的指令一样生动。

3. **Motivated 原则**：镜头运动必须由人物动作、情感需求或故事节拍驱动，绝不随意或装饰性运动。

**强制融合结构（推荐模板）**：
「人物 [具体动作 + 微表情/下意识反应/物理惯性] 的同时/随着人物动作，镜头 [运动方式 + 节奏] ，以 [揭示情感/空间关系/戏剧重点] ……」

**正例（强制要求风格）**：
女主缓缓从椅子上站起，双手微微用力撑着扶手，指节泛白，眼神从低垂逐渐抬起，带着压抑的坚定。镜头从略带俯视的中景开始，随着她起身而缓慢上摇并向前推进，在她完全站立时推至中近景，侧逆光勾勒出她侧脸的轮廓与眼中闪烁的泪光，强调她从被动到觉醒的内在力量。

**反例（已禁止 — 绝不允许这种割裂式写法）**：
❌ 人物：缓缓站起，表情悲伤。
❌ 镜头：从全景缓慢推至特写。

**实际影响**：
- 结构化字段（Framing、Camera 技术参数、Spatial Coordinates、Lighting）仍保留高精度，便于提示词工程和执行。
- 但主要画面叙述（Action/Blocking、视觉叙述部分）必须是融合后的电影化 prose，这会让分镜更具导演感、节奏感和可直接用于视频生成的实用性。
- 特别适合情绪戏、动作戏、对话戏，能显著提升 Seedance 2.0 / Kling 等工具的输出质量和连贯性。

**融合书写示例格式（导演分镜范式）**：
```
【Camera Movement - Slow Crane Down / Tilt】
摇臂从府邸层叠的瓦片缓缓下压，越过被风掀起的飞檐。
【Action】狂风卷着雨沫斜扫入偏殿，吹得案上残烛疯狂摇曳。
```

---

**Gold Standard Reference Example（黄金标准参考范例 — 完整双镜头分镜）**：

以下范例展示了所有融合书写原则的完美执行。供生成时直接对标。

```
开场状态：

环境：@皇家寝殿长廊（楼上），中午，冷白自然光束与昏暗暖黄光交织，空气中清晰可见浮动的微尘，冰冷灰调与贵族暖金色的冷暖碰撞，低饱和度<空旷长廊内的微回声>。

站位关系：@King George 蹲在 @Agnes Hartwell·被打之后 的面前，@Agnes Hartwell·被打之后 跪于中央地板上。

@Agnes Hartwell·被打之后：位于长廊中央的地板上一侧，面朝 @King George 面前、跪姿，低头垂下眼睫，面朝长榻一侧的板上；后背有流血的鞭伤痕迹，满身狼狈。

@King George：位于 @Agnes Hartwell·被打之后 面前，蹲着，身体自然放松，面朝跪在地上的 @Agnes Hartwell·被打之后。

@底层灰色杂役棉裙·鞭刑残破态：穿在 @Agnes Hartwell·被打之后 身上；后背破损，被血迹浸染。

灯光：主光为右上方长廊高窗透入的冷白自然光束，硬光覆盖长廊局部端；无副光；实用光为墙壁两侧的青铜雕花壁灯，开启发出昏暗的暖黄光。

————————————————————

Shot 1
duration: 2.0s

镜头：中远景，高角度俯拍，俯拍90°，固定，广角35mm，深景深保留全景，常速，稳定器固定。镜头从长廊上空的高光区起，客观视角俯拍两人高低悬殊的站位落差，景别保持中远景不变，焦点保留在两人之间，最后落点交给 @Agnes Hartwell·被打之后 后背触目惊心的血迹与破损。

画面：长廊宽阔的地板上，@Agnes Hartwell·被打之后 跪在中央，整个人佝偻着，后躯底层灰色杂役棉裙·鞭刑残破态 后背破损不堪，深红色的血迹在灰色布料上晕开，边缘还在缓慢往外渗；高窗下的幕墙窗台座位上，@King George 蹲在 @Agnes Hartwell·被打之后 的面前，身姿笔挺、没有一丝褶皱；两人的距离约三步远；@Agnes Hartwell·被打之后 肩膀随压抑的呼吸微微起伏，但没有抬头，彻底沦为地上的一团阴影。

光影：右上方长廊高窗透入的冷白自然光束 6500K 作为主光，硬光斜切在 @King George 无瑕的军装上，高光鲜明；@Agnes Hartwell·被打之后 大部分身体沉入长廊的环境阴影中，仅后背血迹接住环境漫反射光；墙壁两侧的青铜雕花壁灯发出 2700K 昏暗的暖黄光；阴影占画面约 60%，高反差。

————————————————————

Shot 2
duration: 1.0s

镜头：近景，俯视，正打 @Agnes Hartwell·被打之后，缓慢推，中长焦 85mm，浅景深落在 @Agnes Hartwell·被打之后 面部，常速，稳定器固定。镜头从 @Agnes Hartwell·被打之后 低垂的头颅起，缓慢推进，焦点逐渐锁在她的下颌与紧绷的唇角，景别由近景缓缓维持至等，最后落点交给她冷垂下眼睫、咽下血眶的临界帧。

画面：@Agnes Hartwell·被打之后 跪在地上，下颈死死向内收，胸膛因强烈的委屈型剧烈起伏了一次，随即被强制压平；她眼尾深处泛着红，但眼眶被她颤动了一下，随后冷冷地垂下眼睫，在上眼睑投下一道浓重的阴影；鼻翼鼓起轻张半开，喉咙剧烈滚动，硬生生把哽噎的血腥味咽了下去；嘴角抿成一条僵硬的直线，一丝脆弱被彻底扼死，面上只剩极度冰冷的冷漠，压迫者不让其发作。
```

**本范例的6个执行要点（生成时必须对标）**：

| 要点 | 范例中的体现 |
|------|------------|
| **1. @角色名·状态标签** | `@Agnes Hartwell·被打之后`、`@底层灰色杂役棉裙·鞭刑残破态` — 角色状态精确追踪 |
| **2. 镜头-动作深度融合** | Shot 1："镜头从长廊上空的高光区起...最后落点交给...后背触目惊心的血迹" — 运镜终点=叙事落点 |
| **3. 技术参数精确** | 90°俯拍/35mm广角/85mm中长焦、6500K/2700K色温、阴影占60% — 可直接用于AI生成 |
| **4. 微表演代替情绪标签** | 不用"悲伤""愤怒"，用"下颈死死向内收""眼尾深处泛着红""喉咙剧烈滚动" — 身体即情绪 |
| **5. 光影即权力** | King George 在 6500K 硬光下（军装无瑕/高光鲜明）vs Agnes 在 60% 阴影中（佝偻/破损/血迹） — 不解释，光影说话 |
| **6. 开场状态独立模块** | 环境→站位→角色状态→服装状态→灯光 — 先建立世界，再进入镜头 |

**运镜类型速查**（常用）：
- Slow Crane Down / Tilt：摇臂缓降/俯仰（环境揭示）
- Slow Dolly In / Macro Focus：缓推/微距（情感加强）
- Rapid Dolly In (Impact)：冲击式急推
- 360-degree Orbiting Shot：360°环绕（能量爆发）
- Low Angle Push In：低角度迫近（压迫感）

**AI Image Prompt (copy-paste ready)**:
必须先通过内联的《电影级写实与场景丰富强制协议》全部5阶段自检后再生成。

示例（已融合写实 + 场景丰富规则）："Cinematic extreme close-up of a woman's calloused hands gripping a rusted metal pipe in a derelict warehouse at night, slow dolly push-in, harsh single tungsten practical light from top-left creating dramatic shadows and rim lighting on knuckles, floating dust motes in volumetric god rays, detailed cinematic environment with layered depth, lived-in atmosphere, weathered surfaces with natural patina, realistic light interaction with materials, photorealistic, hyperrealistic, realistic live-action cinematic film still, shot on Arri Alexa 65, 85mm lens, T2.8, shallow depth of field, detailed realistic skin texture with visible pores and fine lines, natural subtle redness, directional facial chiaroscuro, visible film grain and skin noise, fine dust particles, no over-smooth skin, lifelike eyes with realistic catchlights, no cartoon, no plastic skin, subtle realistic film grain --ar 2.39:1"

---

## MANDATORY Photorealism & Anti-AI-Plastic Layer (Apply to ALL human character shots – 严格执行内联的电影级写实与场景丰富强制协议)

本层必须完全符合《不可绕过的电影级写实与场景丰富强制协议 v1.0》中的写实风格强制规则（规则1-4）：
- 必须强势包含 photorealistic / hyperrealistic / realistic live-action cinematic film still / purely photographic / no cartoon / no anime 等反风格化词。
- 必须包含 shot on Arri Alexa 65 + 镜头参数 + film grain。
- 人物皮肤、眼睛、材质必须强制写入真实细节（visible pores, subsurface scattering, lifelike catchlights, realistic fabric physics 等）。
- 必须明确禁止 plastic skin / waxy skin / doll-like / cartoon style。

以下为moviestory原有强化内容（与协议兼容并进一步细化）：
For every shot featuring people, the AI Image Prompt **MUST** integrate these exact techniques to eliminate plastic skin, vacant eyes, stiff poses, flat lighting, and "AI-generated" artifacts. This makes first-frame prompts (首帧提示词) production-ready for video tools:

- **表情与表演结构** (Expression & Performance — 演员表演核心参考):
  必须使用"人物 + 正在做的小事 + 下意识反应 + 情绪落点"结构来指导表演。
  这是让AI角色表演自然、生动、不僵硬的关键方法（参考专业短视频/AI表演教学）。
  示例：女主低头轻轻转动团扇（正在做的小事），眼神微微亮起并看向扇面上的鸟（下意识反应），嘴角不由自主地微微上扬，情绪从平静转为温柔的怀念（情绪落点）。
  要求：每个有表演的人像镜头都必须包含这种有机的微动作 + 潜意识反应 + 情绪变化，避免空洞眼神和僵硬姿势。视频提示词中尤其要强调自然眨眼和呼吸。

- **动作与惯性** (Action & Inertia): 动作有力量感，走路有力度，衣角/头发随人物惯性自然飘动，不要僵硬呆板。加入下意识小动作（手指轻颤、肩膀微耸、呼吸起伏）。

- **光源与明暗** (Lighting & Contrast): 画面必须有明显明暗变化，加头顶光 + 发丝光 + 侧光 + 自然光影颗粒，不要均匀受光。保留真实光影层次和氛围感（灰尘噪点、光影颗粒）。优先使用专业电影打光术语（前侧光、顶光、正侧光、逆光/背光、蝴蝶光、顺光、底光、侧逆光等），并匹配其经典视觉语言与电影参考。

- **专业电影打光位置与视觉语言 (Cinematic Lighting Positions Mastery — 强制融入提示词)**:
  当描述灯光时，使用以下标准电影打光术语，并结合其视觉语言与经典电影参考，使提示词专业且富有表现力：
  - **前侧光 (Front-Side Key Light)**: 光源位于主体前侧方，结合顺光明亮与侧光立体感。视觉语言：空间与氛围营造、突出面部立体轮廓。参考：《肖申克的救赎》中安迪在监狱阅读时的窗边镜头。适用于塑造坚毅、智慧、复杂角色。
  - **顶光 (Top Light / Overhead)**: 光源从正上方直射（如天花板灯）。视觉语言：压抑与威慑、非自然感、科幻/恐怖暗示。参考：《教父1》马龙·白兰度、《沉默的羔羊》汉尼拔。
  - **正侧光 (Side Light)**: 光源位于主体侧面，形成强烈明暗对比。视觉语言：立体感与质感、戏剧性（复杂性格或冲突）。参考：《公民凯恩》凯恩的特写、《沉默的羔羊》。
  - **逆光 / 背光 (Back Light / Rim Light)**: 光源位于主体正后方，对向摄像机。视觉语言：神秘感与未知、孤独感、希望与救赎、剪影效果。参考：《降临》开场、《银翼杀手》角色登场、《这个杀手不太冷》莱昂开门。
  - **蝴蝶光 / 蝴蝶光 (Butterfly / Paramount Light)**: 光源位于摄像机正上方高位，鼻下形成蝴蝶形阴影。视觉语言：女性优雅高贵、增强戏剧性与仪式感、梦幻"女神"形象。参考：《乱世佳人》费雯·丽、《了不起的盖茨比》。
  - **顺光 (Front Light)**: 光源与摄像机同方向直射被摄体。视觉语言：客观与真实、明亮积极氛围、纪实感。参考：《偷自行车的人》。
  - **底光 (Bottom Light / Under Light)**: 光源从下方低处向上照射。视觉语言：反派/恐怖形象、精神异常或心理扭曲。参考：《驱魔人》、《闪灵》。
  - **侧逆光 (Side-Back / 3/4 Back Light)**: 光源位于侧后方。视觉语言：神秘感与层次感、突出轮廓同时隐藏部分细节、动态分离主体与背景。参考：《这个杀手不太冷》玛蒂尔达办公室、《谍影重重》追逐戏。
  提示词中应明确指定光位（如"使用前侧光营造坚毅氛围"或"顶光制造压抑审讯感"），并结合电影参考提升专业度与情绪表达。

- **皮肤与面部真实感** (Skin & Facial Realism): 可见毛孔细纹，自然红润感，肤色不均（轻微色差），保留轻微小痣/雀斑，真实皮肤肌理，清晰毛孔，肤色通透不假白，五官原生自然，轻微不对称，表情放松不僵硬。绝对禁止塑料陶瓷肌或AI建模痕迹。

- **眼睛真实感 (Ocular Realism — 影视级人像最关键防AI假眼模块)**:
  AI眼睛最容易暴露的问题不是分辨率，而是**视觉聚焦逻辑（ocular focus logic）缺失**。真人眼睛是"意识的投射"，AI眼睛往往只是纹理。
  必须强制加入以下真实光学与表演逻辑：
  - **双眼汇聚一致性 (Binocular Vergence)**: 两眼必须锁定同一个焦点目标，近距离内聚明显，远距离趋于平行。严禁左眼看左、右眼看右或焦点漂浮。
  - **高光锚点一致 (Catchlight Anchor)**: 两眼高光位置必须严格对应主光方向，逻辑统一。
  - **角膜折射与体积感**: 角膜有凸起厚度，瞳孔有深度，高光浮于表层，虹膜有空间感（非平面贴图）。
  - **微扫视与动态 (Microsaccades + Pupil Dynamics)**: 加入细微眼球跳动、瞳孔随情绪/光线轻微变化、呼吸感。
  - **眼睑与眼球联动**: 眼球转动时眼睑有自然压迫和张力变化。
  - **意识导向描述**（最重要）: 提示词必须包含"conscious gaze / focused attention / emotionally anchored eye focus / locked on specific target"，而非只写"detailed eyes"。
  推荐影视级眼睛提示词（直接使用）：
  "perfect binocular convergence, both eyes locked on same focal target, realistic corneal refraction, physically accurate catchlights, subtle tear film reflection, natural pupil depth, cinematic ocular tension, microsaccadic eye movement, emotionally focused gaze, dynamic eyelid compression, living human eyes, no dead-eye effect, conscious attention"

- **眼泪与情绪液体真实感（强制规则）** (Tears & Emotional Fluid Realism — **涉及哭泣、情绪崩溃、眼泪的特写或情绪高潮镜头时必须强制完整使用**):

  **强制必须融入的真实眼泪物理描述**（不可简化或替换）：
  真实人类眼泪从内眼角缓慢溢出，半透明生理盐水质感，表面有细腻的环境光反射，顺着脸颊自然滑落，受重力影响呈不规则曲线，在颧骨处汇聚后滴落，打湿皮肤形成湿润反光，晕开少量睫毛膏，留下淡淡的泪痕，睫毛上挂着细小的泪珠。面部肌肉自然紧绷，嘴唇微微颤抖，整体情绪克制。眼泪必须呈现真实生理盐水质感，而非白色固体或不自然流动。

  在生成任何涉及眼泪的镜头提示词时，必须将以上描述的核心物理细节（缓慢溢出、半透明生理盐水质感、重力不规则曲线、湿润反光、晕开睫毛膏、细小泪珠等）完整融入提示词中。

- **景深与构图** (Depth of Field): 前景有虚化的遮挡物（树叶、窗框、人物肩部等），中景人物清晰锐利，背景自然虚化（大光圈浅景深效果）。使用85mm定焦镜头模拟，原相机直出质感。

- **整体质感** (Overall Texture): 轻微胶片颗粒感，8K高清，神态灵动自然，生活化穿搭，真实实景背景（非纯AI合成感）。参考"超写实人像摄影，原相机直出"风格。

**Example enhanced prompt structure** (always follow this order in the prompt string):
"[Cinematic shot description], [performance structure with micro-expression + subconscious reaction + emotional landing], [powerful natural action + clothing inertia], [dramatic lighting with top/hair/side light + particles + dust], [photorealistic skin: visible pores, fine lines, natural subtle redness, directional facial chiaroscuro, non-uniform illumination, visible film grain and skin noise, fine dust particles, no over-smooth or over-clean skin], [85mm lens, shallow DOF, foreground blur obstruction, sharp midground subject, blurred background], [film grain, 8K, no AI artifacts, lively natural demeanor, straight-out-of-camera] --ar 2.39:1 --stylize 250 --v 6"

**Hero/Key Shot Prompt Standard (重要英雄镜头首帧提示词标准)**:
对于分镜中的关键镜头（Hero Shot、情绪/动作高潮点），提示词必须达到极高电影级技术细节，参考CUT 12风格：
- 精确相机/镜头规格（机型、焦距、光圈、快门、ISO、机位高度、倾斜角度）
- 详细构图与取景逻辑
- 完整光线拆解（主光、轮廓光、补光 + 色温 + 实用光）
- 氛围、质感与粒子细节
- 克制且仪式感的表演
- 最终电影感效果描述

此标准确保首帧提示词具备专业电影级可执行性。

---

## MANDATORY Scene Richness & Cinematic Environment Layer (场景丰富度强制层 — 严格执行内联的电影级写实与场景丰富强制协议):

本层专门解决"场景简陋、空洞、缺乏电影质感"的问题，必须完全符合协议中的场景丰富度强制规则（规则5-8）。

**强制要求（每次生成场景相关提示词时必须检查并融入）**：
- **分层深度**：必须明确描述前景、中景、背景至少3个层次（layered composition, foreground elements, midground details, background depth）。
- **氛围与光线物理互动**：必须加入 volumetric god rays / atmospheric haze / dust motes in light beams，并描述具体光源如何与材质（木头、布料、纸张、皮肤等）产生真实互动。
- **生活痕迹与制片设计**：必须加入 lived-in atmosphere, weathered surfaces, natural patina, aged materials, subtle environmental storytelling details（风化、磨损、灰尘、使用痕迹等）。
- **具体性**：禁止泛化描述，必须具体到材质、年代感、光线来源和粒子效果。
- **推荐融合模块**（直接加入AI Image Prompt）：
  `detailed cinematic environment with layered depth, intricate production design, lived-in atmosphere, weathered and aged surfaces with natural patina, volumetric god rays and atmospheric haze, dust motes visible in light beams, realistic light interaction with materials and textures, rich environmental storytelling details`

在生成每个镜头的 **AI Image Prompt** 时，必须同时满足：
1. 人物写实层（原有Photorealism部分）
2. 场景丰富度层（本新增部分）
3. 并通过《不可绕过的电影级写实与场景丰富强制协议 v1.0》的5阶段自检。

---

## Video/Multi-Shot Emotional Sequence Prompt Standard (视频多镜头情绪序列提示词标准):

当生成视频或多镜头情绪序列（尤其是哭泣、心动、情绪崩溃类表演）时，参考以下高精度结构：

**Global Control First**:
定义整体运动风格、相机质感（shaky handheld with organic breathing movement）、表演权重、真实物理权重。
强制角色一致性 + 真实眼泪物理参考。

**Shot-by-Shot Breakdown**:
每个镜头独立详细描述：
- 焦距 + 机位运动（slow dolly-in push, organic breathing, micro-shake）
- 表演结构（人物 + 正在做的小事 + 下意识反应 + 情绪落点）
- 具体微表情与肌肉动态权重
- 真实眼泪物理（viscous flow, gravitational roll, refraction on wet skin）
- 光影与皮肤质感细节

**推荐核心权重控制**:
- (highly refined real tear physics:1.55)
- (lighting refraction on wet skin:1.55)
- (specific eye muscle dynamics:1.55)
- (detailed facial muscle micro-expressions:1.45)
- (subtle performance:1.35)
- (platysma neck tension:1.5)

此标准用于生成高精度、连贯的多镜头情绪视频提示词。

---

## 视频提示词输出格式统一规范 v2.0 (Unified Video Prompt Output Format)

> **核心理念**：每个场景的视频提示词由「开场状态（Opening State）」+ 逐Shot组成。开场状态统领全场，一次定义所有共享信息（环境、站位、角色姿态、美术资产、灯光、摄影规格、质感标准）；各Shot只描述本镜独特的镜头运动和画面焦点变化。此格式消除了旧版每Shot冗余重复的结构。

### 格式总览

```markdown
# 视频提示词

## 开场状态：
环境：@场景标签（时间/地点/氛围），整体色调与光感描述 <环境音效>
站位关系：[角色A] 与 [角色B] 的空间位置关系
@角色A：[详细位置、姿态、朝向、与场景中其他元素的空间关系]
@角色B：[同上]
@服装/配饰标签：[状态描述、完好/破损程度、特殊说明]
@妆发/造型标签：[状态描述、完好/破损程度、特殊说明]
@道具标签：[位置、状态、初始形态]
@场景陈设/空间标签：[位置、状态、氛围描述]
灯光：主光为 [光源方向 + 色温 + 光质]；[副光说明]；实用光为 [场景内光源]
摄影规格：[机身 + 镜头 + 光圈 + 景深 + 画幅]
质感/技术规格：[写实质感关键词全量]

---

## Shot 1
duration: X.Xs

镜头：[景别]，[角度]，[运镜]，[焦距]，[景深]，[速度]，[稳定器]。[镜头运动详细描述]

画面：[详细视觉描述，聚焦本镜独特的视觉焦点和动作推进]
[写实质感：自然噪点、色彩还原、材质纹理、胶片颗粒]
[如有眼泪→追加眼泪增强关键词]

@角色名 (情绪·音量·效果)：{对白内容}

光影：[色温] [光质描述]；[阴影占比]，[反差描述]

---

## Shot 2
duration: X.Xs

镜头：[同上格式]
画面：[同上，动作推进 + 视觉焦点变化]
光影：[同上格式]
```

### 书写规则（必须遵守）

1. `# 视频提示词` 为总标题，`## 开场状态：` 统领全场景，用 `---` 分隔各Shot
2. `开场状态` 覆盖：环境(含音效) + 站位关系 + 各角色位置姿态 + 美术资产状态(服装/妆发/道具/场景陈设) + 灯光(主光/副光/实用光+色温K) + 摄影规格(机身+镜头+光圈+景深+画幅) + 质感/技术规格(写实关键词全量)，一次定义全场共享
3. 每个Shot含 `duration` + `镜头` + `画面` + `光影`，不重复开场状态中已定义的信息
4. 有台词时，在 `画面` 段落后追加 `@角色名 (情绪·音量·效果)：{对白内容}`，无台词则省略
5. `镜头` 必须指定：景别 + 角度 + 运镜 + 焦距 + 景深 + 速度 + 稳定器，附带镜头运动描述
6. `画面` 聚焦每镜独特的视觉焦点和动作推进，不需要重复全场共享信息
7. `光影` 必须含色温(K)、光质、阴影占比、反差描述
8. 每个Shot提示词独立成块，有台词的Shot绝不与其他Shot合并
9. `duration` 必须基于对白时长精准计算协议得出，不可凭感觉估算
10. 所有描述必须来自剧本分析结果，不得虚构

### 开场状态结构详解

| 字段 | 内容 | 示例 |
|------|------|------|
| **环境** | @场景标签(时间/地点/氛围)，色调光感 + 环境音效 | `@酒店大堂，夜晚，3200K暖色与6500K冷蓝月光混合 <旋转门转动声>` |
| **站位关系** | 各角色空间位置关系 | `@女主(左) → @女反角(中) → @男主(右中景)` |
| **@角色** | 每个角色：位置 + 姿态 + 朝向 + 光影归属 | `@女主：画面左侧，姿态内收，面庞被暖光柔化` |
| **@服装/配饰** | 服装状态、完好/破损程度、面料质感 | `@女主连衣裙：真丝面料，保留自然布纹褶皱` |
| **@妆发/造型** | 妆面状态、发式完整性、皮肤纹理 | `@女主：自然妆感，皮肤保留真实纹理与噪点` |
| **@道具** | 道具位置、状态、初始形态 | `@水晶吊灯：天花板悬挂，碎片散落前景地面` |
| **@场景陈设** | 空间前景/中景/背景元素，材质磨损 | `前景失焦吊灯碎片散景 → 中景对峙区大理石地面 → 背景旋转门` |
| **灯光** | 主光(方向+色温K+光质) + 副光 + 实用光 + 反差 + 阴影占比 | `主光：吊灯3200K暖光；副光：6500K冷蓝月光` |
| **摄影规格** | 机身 + 镜头 + 光圈 + 景深 + 画幅 | `阿莱 Alexa 65 / 35mm / T4 / 深焦定场 / --ar 16:9` |
| **质感/技术规格** | 写实质感关键词全量（含反塑料/反CG/反蜡质） | `照片级真实/超写实/真人实拍/胶片颗粒/非卡通` |

### 与四维美术提取技能的协作

本格式与以下四个专项提取技能输出格式完全一致，实现无缝拼接：

| 技能 | 聚焦维度 | 开场状态对应字段 |
|------|---------|-----------------|
| costume-accessories-extractor | 服装+配饰 | @服装/配饰标签 + 面料重量感/垂坠感/布纹褶皱 |
| makeup-hair-extractor | 妆发造型 | @妆发状态 + 皮肤纹理/毛孔/明暗对照 |
| script-props-extractor | 道具 | @道具清单 + 材质纹理/灯光反射 |
| set-art-extractor | 场景美术 | @空间/陈设 + 材质磨损/大气薄雾/混合色温 |

四个技能各自生成其专精维度的提示词片段，导演可将它们合并到统一的开场状态中。本技能（movie-story）输出的完整版提示词覆盖全部四个维度。

### 参考示例（酒店大堂三角对峙 — 全维度统一版）

> **示例说明**：以下为一个完整场景的视频提示词，覆盖**服装 + 妆发 + 道具 + 场景**四个维度。

```markdown
# 视频提示词

## 开场状态：

**环境：** @酒店大堂，夜晚，3200K钨丝暖色与6500K冷蓝月光混合角力，低饱和度冷暖碰撞，吊灯光束中漂浮体积感尘埃微粒，轻微大气薄雾笼罩 <旋转门微弱的机械转动声，远处隐约的钢琴声，大堂空旷微回声>

**站位关系：** 三人形成对峙三角格局 — @女主 位于画面左侧 → @女反角 占据画面中央 → @男主 位于画面右侧中景

**@女主：** 位于画面左侧，姿态内收，双臂自然垂于身侧，手指微微向内蜷曲——透露克制的紧张；面庞被吊灯3200K暖光柔化覆盖，细腻真实的皮肤纹理，可见毛孔及自然的微红血色，无塑料感/无蜡质感/无过度柔滑

**@女反角：** 占据画面中央，下巴微抬，唇角挂着一抹冷冷的轻蔑笑意；身体语言占据空间主导；轮廓被旋转门6500K冷蓝月光硬朗勾勒，形成冷暖对抗；冷光下的面部呈现定向明暗对照

**@男主：** 位于画面右侧中景，视线在地板与@女主之间来回游移，刻意避开与@女反角的直视——逃避姿态

**@服装/配饰：**
- @女主 连衣裙：优雅简约，真丝面料具有真实重量感与垂坠感，自然布纹褶皱，非塑料/蜡质感
- @女反角 礼服裙：在水晶吊灯3200K暖光下闪烁，面料反光丰富，裙摆自然垂坠

**@妆发状态：**
- @女主：自然妆感，皮肤保留真实纹理与噪点，暖光下肤色自然还原
- @女反角：冷光下妆面呈现高反差明暗对照，轮廓线硬朗

**@道具清单：**
- @水晶吊灯：天花板悬挂，3200K暖光光源，碎片散落在前景地面形成失焦散景
- @旋转门：背景中景，持续转动，6500K冷蓝月光通过其倾泻入大堂
- @大理石地面：中景核心区域，带有细微磨损痕迹，同时反射暖光与冷光形成双色倒映
- 无其他手持/互动道具

**@空间/陈设：**
- **前景：** 失焦的水晶吊灯碎片，形成如破碎玻璃般的散景面纱
- **中景：** 三人三角对峙站位核心区，大理石地面细微磨损痕迹与倒映
- **背景：** 旋转门将6500K冷蓝月光倾泻进3200K钨丝暖色大堂，形成混合色温角力
- **吊灯光束：** 空气中漂浮体积感尘埃微粒，轻微大气薄雾在深焦下保留纵深层次

**灯光：**
- **主光：** 天花板@水晶吊灯，3200K钨丝暖光，自上而下覆盖@女主面庞与连衣裙，光质柔化
- **副光/轮廓光：** 穿过@旋转门的 6500K 冷蓝月光，硬朗侧逆光勾勒@女反角轮廓与礼服裙边缘
- **反差：** 暖光柔化@女主面庞与连衣裙纹理 × 冷光硬朗@女反角轮廓与礼服裙反光 → 冷暖明暗对照
- **阴影：** 约40%，主要集中在@男主区域

**摄影规格：** 阿莱 Alexa 65 / 35mm / T4 / 深焦定场镜头 / --ar 16:9

**质感/技术规格：**
- 照片级真实 / 超写实 / 真人实拍质感的电影静帧
- 多层次构图：前景（失焦散景）→ 中景（三角对峙）→ 背景（旋转门+月光）纵深分明
- 衣物具有真实的重量感和垂坠感，自然的布纹褶皱
- 胶片颗粒与皮肤噪点，无过度柔滑皮肤/无塑料质感/无蜡质感
- 充满生活痕迹的氛围——大理石地面细微磨损、空气中漂浮尘埃微粒
- 非卡通 / 非动漫 / 非插画

---

## Shot 1
**duration: 4.0s**

**镜头：** 广角定场，平视，缓慢前推，35mm，T4深焦保留三人全景，常速，稳定器固定。镜头从大堂全景起，沿中轴线缓慢向前推进，景别由大广角收紧至中广角，最后落点在三人三角对峙的定格瞬间。

**画面：**
前景中失焦的水晶吊灯碎片如破碎玻璃散景面纱，随镜头前推从边缘向外滑出——前景散景动态变化丰富画面层次。@女反角 占据画面中央，下巴微抬冷傲姿态不动，礼服裙在3200K吊灯光下闪烁微光，裙摆面料反光随镜头推进增强。@女主 位于画面左侧，真丝连衣裙保留自然布纹褶皱，3200K暖光下呈现真实重量感与垂坠感，皮肤纹理与微红血色细腻可见。@男主 右侧中景，身体重心微移。冷暖光在画面中形成对角线切割。@大理石地面 同时反射暖光与冷光形成双色倒映，磨损痕迹在深焦下可见。吊灯光束中尘埃微粒体积感随镜头推进逐渐清晰。
写实质感：真人实拍，胶片颗粒与皮肤噪点，面料真实重量感非CG漂浮感，地面磨损痕迹与倒映细节丰富。

**光影：** 3200K暖黄吊灯光自上而下覆盖画面左侧；6500K冷蓝月光从背景旋转门方向切入，硬朗侧逆光；冷暖光在中央形成对角线切割，明暗对照；阴影约40%；大理石地面双色倒映。

---

## Shot 2
**duration: 3.5s**

**镜头：** 中近景，侧前方平视，缓慢横移（dolly left），中长焦85mm，浅景深焦在@女主面部，常速，稳定器固定。镜头从@女反角侧脸起沿三角中轴线向左横移，焦点由@女反角过渡到@女主，最后落点交给@女主面庞。

**画面：**
起幅：@女反角占据画面中央偏右，唇角冷冷轻蔑笑意在6500K冷蓝月光硬朗勾勒下清晰。横移过程中焦点从@女反角平滑过渡到@女主。@水晶吊灯碎片在浅景深下化为失焦散景光斑，@大理石地面轻微磨损纹理在焦外若隐若现。落幅：@女主 暖光面庞——3200K吊灯光从上方斜照，眼窝下投出柔和鼻影，毛孔与自然微红血色清晰可见，无塑料感/无蜡感。真丝连衣裙肩部因双臂微收产生自然张力褶皱。背景@旋转门退为冷蓝调色块，@男主身影化为模糊暖色块。浅景深焦外散景由@水晶吊灯碎片与@女反角礼服反光共同构成多层次散景层。
写实质感：空间纵深通过浅景深+散景+大气薄雾三层分离，服装面料真实重量感。

**光影：** 主光3200K暖黄从@女主前上方斜照，光质通过大气薄雾由硬朗过渡为柔化；6500K冷蓝月光在落幅时退至@女主身后成为微弱冷调边缘光，连衣裙右侧隐约可见冷光勾边。
```

---

## Precise Dialogue-Based Duration Calculation Protocol (对白时长精准计算协议 — 强制执行)

**问题根源与解决目标**
之前AI生成分镜时，**Duration** 经常凭"感觉 cinematic"或随意估算，导致：
- 台词字数多却给很短时间 → 表演赶戏、口型对不上、情绪没空间
- 台词短却给很长时间 → 镜头拖沓、视频生成时画面静止尴尬
- 完全忽略"说话需要时间"这个最基本的现实

**本协议强制要求**：所有包含对白的SHOT，Duration 必须**基于台词实际字数 + 情绪表演需求 + 镜头运动逻辑**精准计算，并**在输出中展示简要 breakdown**。这让时长像专业场记（Script Supervisor）一样可靠。

### 1. 推荐语速标准 (Recommended Speaking Rates)

**核心法则：2-3 字/秒最自然。超过 3.5 字/秒明显偏快，AI配音容易含糊、口型对不上。**

| 类型 | 汉字/分钟 | 字/秒 | 适用场景 | 说明 |
|------|-----------|-------|----------|------|
| **情感戏剧化 (默认推荐)** | 120-150 | **2.0-2.5** | 大多数短剧情绪戏、暧昧、冲突、揭示 | 给予微表情、呼吸、眼神交流空间，情绪最有重量 |
| 自然日常对话 | 150-180 | 2.5-3.0 | 轻松/信息传递场景 | 较快但仍自然，不推荐超过 3.0 |
| ⚠️ 高紧张/争执 (上限) | 180-200 | 3.0-3.3 | 激烈争吵、紧急情况 | **接近上限，仅限必要时使用** |
| 🚨 危险区（禁止） | >210 | **>3.5** | — | **明显偏快，AI配音容易含糊、口型错位，必须拆台词** |
| 关键情绪高潮/崩溃/长停顿 | 100-120 | 1.67-2.0 | 泪目、崩溃、重大揭示、...停顿 | 必须额外增加 hold 时间 |

**短剧核心原则**：宁可通过**增加 inserts、reaction shots、cutaways** 来控制整体节奏，也**不要压缩单个有台词镜头的表演时间**。真实说话 + 自然表演 = 观众相信。

**AI 配音强制规则（新增）**：
- 计算出的语速 > 3.5 字/秒 → **强制拆分母台词为多个 SHOT**（主镜头 + 单人 + reaction + OTS）
- 每条 AI 配音台词建议 **≤20 字**，超过必须拆分到不同 SHOT
- 拆分后每个 SHOT 的语速重新计算，必须落入 2.0-3.0 字/秒区间

### 2. 精准计算公式与流程 (Mandatory Calculation Process)

对每个包含对白的SHOT执行以下步骤：

**Step 1: 提取并统计字数**
- 精确数出该SHOT内说话人该turn的**汉字总数**（含标点符号、省略号、感叹号、问号）。
- 示例："你为什么背叛我...我以为我们是朋友。" → 统计为 14 字（含...和句号）。

**Step 2: 计算基础对白时长**
```
基础对白时长 (秒) = 汉字数 ÷ 语速(字/秒)
```
推荐默认使用 **2.0-2.5 字/秒**（120-150 汉字/分钟）作为大多数短剧情绪戏的基准。正常说话 2-3 字/秒最自然；超过 3.5 字/秒明显偏快，AI 配音容易含糊。

**Step 3: 叠加必要表演与 cinematic 时间（必须逐项评估）**
- **情绪反应 / 停顿 / 呼吸时间**：台词中出现"..."、长破折号、情绪转折、parenthetical (哭泣、颤抖、低语) → **+0.8 ~ 2.0s**
- **说话同时的物理动作 (Business)**：边说边擦眼泪、握拳、站起、推门、点烟等 → **+0.5 ~ 1.5s**
- **镜头运动完成时间**：slow push-in、dolly、slow pan、rack focus 等 → 确保运动有足够时间**自然完成并与表演节奏匹配**（通常与对白时长接近或略长）
- **情绪落点 Hold 时间**（最重要）：关键台词最后一个词、揭示 moment、情绪高潮 → **额外 +0.8 ~ 1.8s** 让观众消化冲击
- **自然表演缓冲**：真实演员总会有细微节奏变化 → 在总时长上 **+10~15%**

**Step 4: 得出最终推荐时长**
```
最终时长 = (基础对白时长 + 叠加时间) × (1.10 ~ 1.15)
```
并取合理整数或一位小数（e.g. 6.8s, 7.5s）。

**最小时长保护**：即使计算结果很短，有对白的镜头**建议不低于 4.0-4.5s**（给表演和剪辑 breathing room）。

### 3. 在 SHOT 输出中的强制格式 (Mandatory in Every Shot Template)

**Duration** 字段现在必须写成以下结构（简要版或完整版均可，视脚本长度）：

**Duration**: 7.2 seconds（精准计算 · 表演从容）

**Timing Breakdown** (示例，无对白镜头):
- 台词："我以为你会懂的..." (8字) @ 2.25字/秒 → 基础 3.6s
- 情绪停顿 + 微弱呼吸 + 泪光上涌: **+1.3s**
- Slow dolly-in 跟随情绪推进（与台词节奏同步）: **+1.5s**
- 最后"懂"字 + 眼神 hold + 微颤: **+0.8s**
- 总计 **7.2s**（含自然缓冲，推荐用于视频生成）

**无对白镜头示例**：
**Duration**: 4.5 seconds
**Timing Rationale**: 纯反应特写 + 缓慢呼吸 + 环境音起。无台词，重点给微表情和情绪消化空间。

### 4. 场景级时长自检 (Scene-Level Timing Validation)

处理完一个场景后，执行快速自检：
- 该场景总对话字数 → 预估最低需要时长
- 实际分镜累加时长是否明显偏离？（过短 → 可能赶戏；过长 → 可能拖沓）
- 是否通过合理使用 inserts / cutaways / reaction shots 来优化节奏，而不是简单拉长或压缩镜头？

在最终输出中可简要说明："本场景时长已基于台词字数精准计算 + 情绪表演需求优化，整体节奏紧凑且表演自然。"

### 5. 特殊优化建议

- **竖屏短剧快节奏 ≠ 赶台词**：大量使用 0.8-2.5s 的 reaction insert、prop close-up、环境 cutaway 来"压缩"观众感受时间，同时保护主要对白镜头的表演时长。
- **多句对白处理**：长段对白建议拆成多个SHOT（master + 单人 + reaction + OTS），每个SHOT分配合理时长，而不是一个镜头塞太多台词。
- **视频生成友好**：精确时长有助于后续用 Kling / Seedance / Runway 等工具时，prompt 中可以更准确地描述 "perform the line naturally over 7.2 seconds with breathing and micro-expressions"。

**执行要求**：从现在开始，**每一条有对白的SHOT都必须展示 Timing Breakdown**。这是专业 vs 业余分镜的最重要区别之一。

此协议与现有的"电影级对白与情绪镜头设计协议"结合使用：前者保证**情绪正确**，后者保证**时间正确**。两者缺一不可。

---

## Phase 4: Delivery, Validation & Extras

**Final Output Structure (always use this order):**
1. **Title & Logline** + overall runtime estimate (e.g., "47 shots / ~8.5 min short film").
2. **Script Health Report** (from Phase 2 – concise version).
3. **Visual Style Bible** (1 paragraph + bullet motifs + reference films).
4. **Full Storyboard** – Scene-grouped, with SHOT templates above. Use markdown for clarity; for long scripts use collapsible sections or numbered list.
5. **Shot Count Summary** by scene + pacing notes.
6. **Self-Validation Results** + **Coverage Verification Matrix（防缺斤少两强制输出）**:

**Coverage Verification Matrix（Phase 4 强制输出 — 不可口头声明100%）：**

| 原始行号 | 对应SHOT编号 | 覆盖类型 | 覆盖状态 |
|---------|-------------|---------|---------|
| L001 | SHOT 001 | 场景头→定场 | ✅ |
| L002 | SHOT 002 | 动作→镜头描述 | ✅ |
| L003 | SHOT 003 | 对白→台词分配 | ✅ |
| L004 | — | 情绪空白→⚠️遗漏 | ❌ |
| ... | ... | ... | ... |

**统计**：
- 总行数: [N]
- 已覆盖: [M] ✅
- 遗漏: [K] ❌
- 覆盖率: [M/N]%

**规则**：
- 此Matrix必须**逐行填写**，从Script Line Index（Phase 1输出）中逐条校验。
- **任何一行标❌即为遗漏**，必须立即补镜头，不得口头声明"100%"。
- 覆盖率<100%时，输出前必须补齐所有❌行对应的SHOT，补完后重新运行Matrix校验。
- 只有Matrix中所有行都标✅时，才允许输出最终声明："Self-check complete: 100% of original dialogue lines and scene segments verified via Coverage Matrix. No omissions."

**Transition Coverage Rule（场景切换强制覆盖）**：
- 每当Script Line Index中出现场景切换标记（INT→EXT、白天→夜晚、角色A→角色B主视角切换），必须分配≥1个转场SHOT。
- 转场SHOT类型：空镜/定场/情绪insert/时间流逝蒙太奇。
- 此规则在Coverage Matrix中以「转场→过渡SHOT」类型标注，不得跳过场景间空白区。

**Validation Self-Check (run before output — MANDATORY, now enforced by Coverage Matrix):**
- **Full Script Coverage Confirmed via Matrix?** Every row in Coverage Verification Matrix marked ✅? Zero ❌ rows? If any ❌ exists, STOP and add missing shots before proceeding.
- **Fight/Action Sequences Check (if applicable):** Fight or high-action scenes broken into detailed multi-shot sequences following the Universal Fighting Storyboard Pattern? No summarization? Every specific action, expression, impact, and timing covered by individual shots?
- **Environmental Destruction Check (if applicable):** Scenes with objects kicked/smashed/destroyed — Template 5 layered on? Material type specified (wood/stone/glass/metal)? Three-stage rhythm planned (pre-impact → peak → aftermath)? Debris physics and secondary reactions described?
- **Coverage Planning Check (对话场景)**: Has Coverage Strategy been defined per major dialogue scene? Is there sufficient coverage (Master + Singles + OTS + Reaction)? Are Spatial Coordinates properly defined and consistently applied across shots?
- **Dialogue Ownership Check**: Every dialogue line in Script Line Index has a Dialogue Ownership Tag in some SHOT? No dialogue line assigned to zero SHOTs? No dialogue line overloaded into a single shot exceeding reasonable speaking pace?
- **Transition Coverage Check**: Every scene transition in Script Line Index has ≥1 transition SHOT in Coverage Matrix? No scene-to-scene jumps without visual bridge?
- Every major story beat has dedicated visual moment(s)?
- Camera directions are specific, practical, and cinematic (no vague "cool angle")?
- Image prompts are detailed enough for excellent results (composition, lighting, mood, lens, reference)?
- Optimizations visibly improve the original script?
- Total feels like a real director's shot list (not AI-generic)?
- **Final statement format (only when Coverage Matrix is 100% ✅)**: "Self-check complete: Coverage Verification Matrix confirms 100% of [N] original script lines accounted for via [M] shots. Zero omissions. Coverage Planning & Spatial Coordinates validated. Dialogue Ownership & Transition Coverage verified."

**User Options (offer at end):**
- "Generate key hero shot images now?" → Use image generation tool with best prompts.
- "Export full storyboard as PDF?" → Activate pdf skill and describe layout (cover + pages of shots with thumbnails placeholders + detailed text).
- "Create Excel shot timing sheet?" → Use xlsx skill.
- "Iterate: make more [dynamic / horror / minimalist / etc.]?"

---

## Phase 5: Iteration Protocol

On feedback ("too slow", "add more close-ups", "change ending tone"):
- Return to Phase 2 with new directives.
- Re-optimize affected sections only.
- Update affected shots + re-validate.

---

## Key Film Terminology (use correctly & explain if rare)

- Shots: ECU, CU, MCU, MS, WS, LS, ELS, OTS, POV, Insert, Cutaway, Montage, Sequence shot.
- Moves: Static, Pan, Tilt, Dolly (in/out), Truck (left/right), Pedestal, Crane, Handheld, Steadicam, Gimbal, Zoom (slow/crash), Rack focus, Whip pan, Dutch tilt.
- Lighting: High-key, Low-key, Practical, Motivated, Volumetric, Chiaroscuro, Neon noir, Golden hour, Blue hour.
- Always specify: lens (35mm, 50mm, 85mm, anamorphic), aspect ratio, film stock emulation if relevant.

**This skill produces production-ready 分镜 that a real 1st AD or cinematographer can use directly.** It elevates scripts by forcing visual thinking and ruthless self-editing.

**Never output generic "shot 1: wide shot of room" descriptions. Every shot must feel intentional, story-serving, and visually rich.**

---

## Fight & High-Action Sequence Protocol (MANDATORY for any fight, combat, chase, rapid action, or intense physical confrontation — never summarize):

- **Never summarize** fight or action scenes in one or two generic sentences. Always break them into **detailed multi-shot sequences**.
- Follow the **Universal Fighting Storyboard Pattern** (万能打斗分镜):
  - 全景 (Wide/Establishing): Establish positions, environment, number of fighters, spatial relationship.
  - 中景 (Medium): Capture complete actions and full body movement.
  - 近景 (Close-up): Fast cuts for reactions, micro-expressions, precise strikes/dodges.
  - 特写 (Extreme Close-up/Insert): Impacts, blood/snow splatter, weapon collisions, eye details, pain/fear expressions.
  - 全景 (Wide/Result): Show outcome, separation, lingering tension.
- For **fast-cut sequences** (e.g., 4-second multi-shot quick cuts): Explicitly list multiple short shots (typically 0.3–0.6s each) with:
  - Precise sub-timing allocation.
  - **Shot-reverse-shot (正反打) must be broken into individual alternating shots**: Never group 正反打 as one item. Clearly separate A-side (e.g., Lin Chong deadpan eyes + precise strike) and B-side (e.g., villain fear expression + dodge), each with its own timing, specific action, micro-expression, and description.
  - Specific actions: eye expression (deadpan, fear), precise strikes, dodges, collisions, splatter physics.
  - Sound design: dense Foley impacts, panting, wind/howling, breathing.
  - Cinematic lighting using professional terms (侧逆光 + 雪地反光, 顶光压抑 + 侧光戏剧性, etc.).
- Integrate full realism: physics of impacts, fabric inertia, material interactions (snow flying, blood on snow, wet surfaces), micro-expressions, and existing photorealism rules.
- In every AI Image Prompt for action shots: include "rapid multi-shot quick cuts, shot-reverse-shot fast editing, dense Foley sound design, precise physical collision, snow and blood splatter physics".
- **Self-check for fights**: Confirm every described action, expression, impact, and sound cue has its own dedicated shot(s). No omissions. When 正反打 or fast editing is used, verify that each side of the reverse shot has been explicitly broken out as separate shots with individual timing and content.

**Handheld Photography for Realism (手持摄影真实感规则 — 动作戏专用):**
- **Use motivated handheld only**: Apply handheld camera movement when it enhances physical weight, fatigue, chaos, or subjective emotional experience. Never use random or excessive shake.
- **Specify intensity and motivation in every action shot description**:
  - Light/natural breathing shake: Conveys exhaustion, tension, or character's physical state.
  - Moderate handheld + fast cuts: Heightens immediacy and violence in close combat or impacts.
  - Avoid over-shaky "found footage" style unless intentionally documentary-like.
- **Combine with lighting and physics**:
  - Handheld + 侧逆光 / 侧光: Creates dynamic shifting shadows and rim light during movement.
  - Handheld + 雪地/雨天/血迹: Amplifies realistic particle movement, splatter physics, and material interaction (snow flying, blood on snow, wet surfaces).
- **Prompt & Storyboard Language**:
  - In AI Image Prompts and shot descriptions, explicitly include phrases such as: "motivated handheld with subtle natural breathing shake", "dynamic organic camera movement", "handheld texture enhancing physical realism and fatigue".
  - In fast-cut sequences: Pair handheld close-ups/impacts with steadier medium or wide shots to maintain spatial clarity.
- **Balance clarity and immersion**: Use handheld primarily in near/ extreme close-up reaction and impact moments. Use more controlled/Steadicam shots for establishing geography and full-body action to prevent audience disorientation.
- **Integration with existing rules**: Combine with Universal Fighting Storyboard Pattern, professional lighting positions, and full photorealism layer.

**Action Cinematography Aesthetics (电影动作运镜美学规则 — 动作戏核心美学):**
- **Rhythm & Pacing Aesthetics**:
  - Master the dialectic of fast cuts vs. long takes. Use rapid multi-shot quick cuts (0.3-0.6s) for adrenaline and information overload; use motivated long takes or slower movements for weight, fatigue, and spatial clarity.
  - Create deliberate rhythm contrast: dense fast-cut sequences followed by a brief slower/held shot for emotional breathing room and impact.
- **Spatial Choreography**:
  - Always prioritize clear geography. Follow the Universal Fighting Storyboard Pattern strictly (全景 establishing → 中景 full action → 近景/特写 reactions & impacts → 全景 result).
  - Use camera movement to actively reveal or maintain spatial relationships rather than confuse the audience.
- **Lighting & Movement Synergy**:
  - Camera movement and lighting must be designed together. Use professional lighting positions (前侧光, 侧逆光, 顶光, 逆光等) in sync with camera motion to create dynamic shadows, rim light, and volumetric effects during action.
  - Handheld or tracking shots + side-back/rim lighting dramatically enhance physical realism and silhouette power.
- **Emotional & Physical Motivation**:
  - Every camera movement must be motivated by emotion, body state, or story beat (e.g., eye-driven: show deadpan eyes first, then follow the precise strike; weight-driven: slight handheld to convey fatigue and inertia of staff/blade).
  - Convey physicality: fabric inertia, impact weight, snow/blood particle physics through motivated camera texture and movement.
- **Implementation in Storyboards & Prompts**:
  - In detailed fight breakdowns, explicitly describe camera movement motivation, rhythm, and synergy with lighting/physics.
  - In AI Image Prompts: include specific aesthetic language such as "motivated camera movement enhancing physical weight and emotional rhythm", "dynamic lighting synced with action", "cinematic spatial choreography with clear geography".
- **Overall Goal**: Achieve the balance between clarity (audience understands what is happening) and excitement (visceral, emotional, aesthetically powerful action).

**Classic 9-Shot Fight Progression Template (经典9分镜打斗结构参考 — 基于专业打斗九宫格分析):**
When designing detailed fight sequences, reference this proven 9-shot structural progression (inspired by high-quality cinematic fight breakdowns such as corridor/tunnel combat scenes):
1. **SCENE 01 - Setup/Approach**: Establish characters, location, and initial tension (one side unaware or distant, antagonist approaching).
2. **SCENE 02 - Initial Attack**: Antagonist launches first aggressive move; protagonist reacts or defends.
3. **SCENE 03 - Close Struggle**: Intense physical contact, hand-to-hand or weapon clash in tight framing.
4. **SCENE 04 - Counter / Dynamic Strike**: Protagonist lands a significant counter-attack, shifting momentum (kick, punch, or throw).
5. **SCENE 05 - Grappling / Environmental Combat**: Close-quarters struggle using walls, ground, or confined space.
6. **SCENE 06 - Improvised Weapon**: Protagonist acquires or uses an object from the environment as a weapon, escalating the fight.
7. **SCENE 07 - Brutal Climax**: Most violent or decisive moment (heavy strike, choke, or blood impact in close-up).
8. **SCENE 08 - Dominance**: Protagonist clearly dominates or finishes the opponent (e.g., kick on grounded enemy).
9. **SCENE 09 - Aftermath/Resolution**: Protagonist walks away or exits frame; antagonist defeated on the ground. Provides visual and emotional closure.
- **Usage Rule**: For meaningful fight scenes, expand into 7–9+ detailed shots following this emotional and visual arc. Combine with Universal Fighting Storyboard Pattern, 正反打 multi-shot breakdown, motivated handheld, professional lighting positions, and physics realism.
- **Prompt Integration**: When writing AI Image Prompts for these beats, highlight momentum shift, environmental interaction, and clear progression from tension to resolution.

**Weapon Fight Special Rules (MANDATORY for any scene involving weapons — v1.1 Addition):**

**1. Weapon Classification & Personality Design (必填 before storyboarding):**
Define for EACH weapon: weight feel, speed characteristics, signature moves (at least 3-5), personality keywords.
Weapon = extension of character's personality. A heavy broadsword (大刀) fights differently from a flexible jian (剑).

**2. Space & Distance Management:**
Strictly execute Far-Medium-Near three-stage distance. Distance changes must have footwork motivation.
- Far (全景): Establish weapon range differences, spatial relationship
- Medium (中景): Core weapon interactions, parry/block/counter
- Near (近景/特写): Blade binding, grappling, disarm attempts, micro-expressions

**3. Weapon Interaction Rules (必须设计):**
- **Clash (碰撞)**: Power contrast & feedback. Describe blade vibration, spark details, character's physical reaction to impact.
- **Bind (缠斗/粘连)**: Skill & psychological warfare. Recommend medium shot + slow tracking. Both sides testing each other's strength through blade pressure.
- **Opening (破绽与反制)**: Brief vulnerability window after failed attack. Counter-attack must be visually clear with timing breakdown.
- **Disarm & Damage (缴械与损毁)**: Must show clear process & continuity. Broken blade = character setback; dropped weapon = momentary vulnerability.

**4. Environment-Weapon Interactions (强制 ≥3 times):**
Rain reflection on blade, water splatter from sword swing, bamboo/wood cutting, car roof impact sparks, ground vibration from heavy weapon, fabric cutting by blade edge. Environment MUST actively participate in fight.

**5. Rhythm & Sound Design:**
- Treat weapon clashes as rhythm anchor points. Fast cut between clash → reaction → counter.
- During bind/struggle: can use brief silence (0.3-0.5s) for tension before explosive release.
- Sound design keywords: `metal clash, wood crack, fabric rustle, footwork friction, breathing heaviness, blade whistle`

**6. Shot Composition Requirements:**
Same frame MUST show: weapon trajectory + hand details (grip tension, finger whitening) + facial expression (focus/panic/determination) + environmental reaction (sparks, debris, liquid splatter).

**Weapon Fight Self-Check (额外必查):**
- [ ] Each weapon has clear personality & weight feel?
- [ ] Distance changes have clear motivation & footwork coordination?
- [ ] At least one meaningful bind/struggle designed?
- [ ] Each clash has power contrast & feedback (winner/lose reaction)?
- [ ] Environment-weapon interactions ≥3?
- [ ] Weapon state continuous (pristine → chipped → broken → discarded)?
- [ ] Shots simultaneously cover weapon trajectory, hands, expression, environment?

**Fight Scene Prompt Template Library (打斗分镜提示词模板库 — v1.1 新增):**

**Template 1: General Fight Base Template**
```
Cinematic [shot type], [Character A] and [Character B] engaged in intense fight in [environment], [detailed action including weapon interaction or environmental reaction], [emotional purpose], realistic physics, heavy fabric physics, realistic skin texture with visible pores and fine lines, natural subtle redness, directional facial chiaroscuro, visible film grain and skin noise, no over-smooth skin, subsurface scattering, visible sweat and fatigue, [camera movement], motivated lighting, Shot on Arri Alexa 65, film grain, photorealistic, intricate details --ar 16:9
```

**Template 2: Weapon Duel Specialized Template (强烈推荐)**
```
Cinematic weapon duel, [Weapon A] vs [Weapon B], realistic metal weight and inertia, blade bind and slide with visible metal stress and vibrations, sparks on clash, [environmental interaction], realistic fabric and sweat, realistic skin texture with visible pores and fine lines, natural subtle redness, directional facial chiaroscuro, visible film grain and skin noise, no over-smooth skin, tight grip with fatigue, intense eye contact during bind, [camera movement], motivated cinematic lighting with rim light on blade, Shot on Arri Alexa 65, film grain, photorealistic metal texture --ar 16:9
```

**Template 3: Style Variant Keywords (按需添加)**
- Poetic (《英雄》式): `poetic, ritualistic, symbolic color grading, slow motion rain droplets, wuxia aesthetics`
- Realistic Hardcore (《一个人的武林》式): `grounded realistic, practical technique, visible fatigue, brutal and technical, no wire-fu`
- Elegant Flying (《卧虎藏龙》式): `graceful flowing wuxia, elegant weight, natural wire-fu, emotional through movement, bamboo forest`

**Template 4: Negative Prompt**
```
plastic skin, waxy texture, blurry action, deformed hands, cartoonish, low quality, inconsistent lighting, bad anatomy, weapon floating, no weight, no fabric physics, no metal texture
```

---

**Template 5: Environmental Destruction Physics Template (环境破坏物理爽感专项 — 踢飞/砸碎/刚体破碎场景必用)**

> **触发条件**：任何涉及物体被踢飞、砸碎、刚体破坏、场景连带破坏（木板断裂/砖墙碎裂/玻璃爆碎/瓦砾飞散）的镜头，必须叠加本模板。核心是让"物理破坏"产生电影级爽感而非AI常见的软糯假效果。

**核心强制原则（Environmental Destruction Mandatory Rules）**：

1. **重量感强制**：被破坏物体必须有明确质量感 — 重物落地时地面震动、轻物飞散时空气阻力、液体飞溅时受重力形成弧线
2. **材质破坏特性**：木材 = 纹理撕裂碎片 + 木屑飞散；砖石 = 粉尘爆炸 + 块状碎裂；玻璃 = 尖锐碎片 + 边缘折光；金属 = 变形弯曲 + 火花四溅
3. **连带环境反应**：一处破坏必须引发周边环境连锁反应 — 灰尘扬起、碎片打落其他物品、破坏产生的光影变化（玻璃破碎透光）
4. **爽感节奏**：破坏发生前 0.5s 的高速快切 → 破坏瞬间慢动作定格/极速特写 → 恢复正常速度看结果，三段节奏结构

**环境破坏物理核心提示词模块（直接插入）**：
```
realistic rigid body destruction with accurate mass and material properties, [object type] shattered/splintered/broken upon impact, debris and fragments flying outward with realistic ballistic arcs, material-accurate destruction (wood splinters vs stone powder vs glass shards vs metal deformation), secondary environmental reaction (dust cloud, cascading debris, light change from broken material), physical weight and inertia clearly visible, impact force radiating from point of contact, slow-motion capture of destruction peak moment, photorealistic destruction simulation, no floaty debris, no weightless fragments, destruction feels earned and physically grounded
```

**分材质专用破坏词组**：

| 材质 | 专用破坏描述 |
|------|------------|
| **木材/木门/木板** | `wood grain splitting along natural stress lines, splinters and chunks flying outward, sawdust explosion at impact point, raw splintered wood edges with fiber tear marks` |
| **砖墙/石材** | `brick/stone fragmenting into coarse irregular chunks, mortar dust cloud billowing at impact, heavy rubble pieces cascading downward under gravity` |
| **玻璃/窗户** | `glass shattering into sharp angular shards with realistic fracture pattern, light refracting through broken edges, glass fragments catching light mid-air, high-pitched shard scatter` |
| **金属/铁笼/钢管** | `metal deforming and bending from impact force, stress fracture lines visible, sparks if metal-on-metal contact, structural failure rippling from impact point` |
| **物体被踢飞（通用）** | `object launched with accurate initial velocity matching kick force, trajectory arc following realistic ballistics, tumbling rotation matching center of mass, secondary impact when landing` |
| **人体被击飞** | `character body ragdolled by impact force, limbs following natural physics in air, clothing reacting to air resistance and gravity, landing with weight and realistic momentum roll` |

**爽感节奏三段结构（配合分镜使用）**：
- **起势镜头**（Pre-impact）：`extreme close-up of charging foot/fist, ground cracking under pressure, slow zoom into impact point, tension build before destruction`
- **破坏顶点**（Impact peak — 最爽帧）：`ultra slow-motion freeze frame or 240fps capture of exact destruction peak, debris cloud at maximum expansion, fragments suspended mid-air, impact shockwave visible`
- **结果确认**（Post-destruction）：`normal speed resume, settling debris and dust, destruction aftermath fully visible, environmental silence after chaos, character standing amid destruction`

**光效配合破坏效果**：
```
destruction reveals new light paths (broken wall letting in rays of light, shattered glass creating prismatic light scatter), dynamic lighting change caused by structural damage, dust particles lit by volumetric shafts through newly created openings
```

**Negative Prompt（环境破坏专项）**：
```
floaty debris, weightless fragments, unrealistic destruction speed, CGI explosion look, rubber-like deformation, no material specificity, uniform destruction pattern, no dust or particles, clean destruction with no mess, debris stopping mid-air without reason, no secondary reactions
```

---

**Usage Flow (强制):**
1. Walk through 5-stage storyboard (weapon personality table MUST be filled for weapon fights).
2. Pass self-check checklist (general + weapon-specific).
3. Select style + weapon template, fill in specific content to generate prompts.
4. **For destruction scenes**: Layer Template 5 on top of base template. Specify exact material being destroyed. Plan the 3-stage rhythm (pre-impact → peak → aftermath).
5. Self-check again after generation and iterate.

---

## Cinematic Dialogue & Emotional Shot Design Protocol (电影级对白与情绪镜头设计协议 — 对话戏核心模块)

高级对白戏的核心不是"传递信息"，而是拍摄**情绪权力关系变化**、**潜台词**、**沉默**、**呼吸节奏**和**心理距离**。镜头必须参与人物心理，而非被动记录。

**核心原则**:
- 对白戏 = 情绪流动 + 权力变化 + 空间压迫 + 沉默中的心理波动
- 真正高级的对白，即使静音，观众也能读懂情绪
- 镜头要拍"没有说出口的东西"

**关键技术模块**:

1. **视线关系 (Sightline as Emotional Attack)**
   - 眼神是情绪攻击。记录谁敢直视、谁闪躲、谁先移开目光。
   - 高级处理：先拍停顿/微动作，再进入语言反应。延迟反应制造张力。

2. **停顿与沉默 (Pauses & Silence)**
   - 高级对白最重要的部分往往是不说话的时候。
   - 停顿时优先使用稳镜或极轻微推镜，保留环境音，让观众"熬"在情绪里。切镜会破坏情绪流。

3. **空间距离 = 心理距离**
   - 情绪平稳：中景、对称、稳定。
   - 情绪压迫：人物靠近 + 长焦压缩空间。
   - 关系崩塌：拉远 + 大量留白，人物被空间吞没。

4. **潜台词镜头 (Subtext Shots)**
   - 拍"谎言泄漏点"：手离开杯子、呼吸停顿、视线失焦、光线变冷，而不是只拍说话的脸。

5. **情绪主导权转移 (Power Shift)**
   - 强势人物：画面更满、更近、更稳定、低机位。
   - 弱势人物：被遮挡、留白更多、位于边缘。
   - 权力反转时，镜头语言必须同步反转（构图中心、遮挡关系、稳定性变化）。

6. **呼吸镜头 (Breathing Lens)**
   - 镜头拥有人的心理节奏：情绪靠近时缓慢推进，退缩时停住，失控时开始不稳定。
   - 高级呼吸镜头极轻微，像空气在流动，由情绪而非技术驱动。

7. **电影级正反打**
   - 使用不对称正反打体现情绪不平衡（不同焦距、不同构图密度、不同留白）。
   - 强势方更满更近，弱势方更多留白与遮挡。

8. **焦距与情绪心理学**
   - 广角（24-35mm）：疏离、不安、空间压迫。
   - 中焦（50mm）：自然、平衡。
   - 长焦（85-135mm）：空间压缩、呼吸困难、情绪逼近、欲望/对峙。

9. **第三视角 (Third-Person Perspective)**
   - "空间正在看他们"。镜头位于房间角落、门外、走廊尽头、镜中。
   - 制造命运感、旁观感、宿命感。非常适合关系即将崩塌的场景。

**对白戏节奏结构**:
- **平静阶段**：中景 + 固定镜头 + 环境完整
- **试探阶段**：微推镜 + 增加遮挡 + 呼吸感增强
- **压迫阶段**：长焦 + 特写 + 空间压缩
- **爆发阶段**：手持 + 快切 + 破构图
- **坍塌阶段**：静止 + 拉远 + 大量留白 + 空镜

**导演风格参考**（可选择性融入）:
- **王家卫式**：大量空间阻隔（门框、镜子、墙壁），情绪越浓镜头越克制，拍擦肩、衣角、慢动作转身。
- **诺兰式**：信息压迫为主，中近景 + 硬节奏，拍逻辑战争而非煽情。
- **黑泽明式**：空间本身参与对白，人物通过走动、转身、占领画面来改变权力。
- **《教父》式**：沉默积压，爆发前最安静，环境声（火车）随情绪增强。

**在分镜中的应用**:
当处理对话场景时，必须使用以上模块拆解"谁在掌控""谁在回避""情绪如何流动"，而非简单正反打。优先设计停顿、空间变化、潜台词镜头和第三视角。

---

## Cinematic Romance, Ambiguity & Intimacy Scene Protocol (电影级暧昧、恋爱与亲密戏设计协议)

高级爱情戏的核心不是"甜"或展示身体，而是拍摄**心理距离的变化**、**欲望与克制**、**呼吸节奏**和**情绪累积**。镜头要拍"关系正在一点点靠近"以及"差一点"的张力。

**核心公式**:
暧昧 = 靠近 + 克制。高级暧昧永远有"差一点碰到"的未完成感。

**关键技术模块**:

1. **视线与偷看**
   高级暧昧很少正面直视。更多使用偷看、余光、镜子反射、擦肩回头。眼神停留时间 = 情绪浓度。发现后缓慢移开会制造强烈空气变化。

2. **呼吸镜头在爱情戏中的应用**
   镜头必须像人在偷偷观察。情绪靠近时极慢推进，被发现时停止，失控时呼吸变重。这会让观众产生"空气正在变热"的感觉。

3. **空间距离设计**
   安全距离（桌子、门框、走廊）：关系仍理性。
   危险距离（手碰到、呼吸可感）：关系开始越界。
   最强张力来自"差一点碰到"（手悬停、呼吸接近、肩膀轻触、衣角擦过）。

4. **身体语言泄漏**
   真正心动时身体会先诚实：呼吸变化、手指收紧、无意识整理头发、轻微后退、眼神停顿。后退有时是害怕失控，停住是最危险的状态。

5. **光影与氛围**
   柔光降低现实感、增加梦感。保留阴影（半张脸在暗处、侧光切割）制造秘密与危险感。冷暖混合光最经典。

6. **焦距与亲密关系**
   广角：初识、疏离。中焦：日常温柔。中长焦：暧昧、对视、欲望压迫。背景失焦意味着"世界开始只剩彼此"。

7. **王家卫式爱情分镜**
   大量空间阻隔（狭窄走廊、门框、镜子）。情绪越浓，镜头越克制。拍擦肩、衣角、慢动作转身。爱情会改变人的时间感，因此使用慢动作与重复。

8. **环境声音放大**
   真正心动时会听见细节（呼吸声、衣料摩擦、风声、电流声）。这些声音会强化私人空间感和孤独亲密感。

9. **亲密戏设计原则（最高级克制）**
   永远不要从"动作"开始。先建立情绪、空间、呼吸、安静。
   重点拍手、后颈、肩膀、呼吸、头发、眼神、皮肤光线。
   呼吸与停顿是最重要的（靠近 → 停住 → 犹豫）。
   光线使用柔和侧光、阴影包裹。空间需要安静、私密。

**恋爱戏节奏结构**:
初识 → 暧昧（中焦慢推 + 呼吸增强） → 心动（长焦 + 世界失焦） → 失控 → 平静余韵。

**在分镜中的应用**:
处理暧昧、心动、亲密场景时，必须优先设计"差一点"的张力、呼吸节奏、身体语言泄漏点和空间阻隔，而非直接展示亲密动作。镜头要参与情绪累积过程。

---

## AI Multi-Character Blocking & Scene Staging Protocol (AI多人物锁站位与场面调度协议)

AI多人物生成最核心的难点不是人物本身，而是**空间关系稳定**、**摄影机逻辑连续**和**人物身份不漂移**。扩散模型本质上不理解三维空间，而是进行二维概率预测，因此多人场景极易崩坏。

**核心原则**:
多人生成本质上是**导演问题**，而非绘画问题。优先级：**空间结构 > 摄影机方向 > Blocking > 动线 > 角色锚点 > 人物细节**。

**关键技术模块**:

1. **Screen Position 系统（最重要）**
   - 强制使用屏幕坐标而非相对位置：
     - screen left / screen right / center frame
     - foreground / midground / background / deep background
     - viewer left / camera left
   - 示例：primary subject screen left foreground, secondary subject screen right midground

2. **摄影机锁定**
   - 必须固定摄影机朝向（camera facing east/north 等）。
   - 后续只改变景别（wide/medium/close-up），不改变相机方向，避免越轴和空间崩坏。
   - 推荐写法：camera facing east, 35mm lens, eye level, static shot

3. **180°法则与轴线**
   - 多人对话/对峙场景必须严格遵守轴线同一侧。
   - 推荐写法：consistent camera orientation, camera remains on same side of axis

4. **角色层级与锚点**
   - 使用 Primary subject / Secondary subject / Background extras 结构。
   - 角色必须有强视觉锚点（scar-faced commander, silver-haired queen, red-armored general），而非泛泛的 man/woman。
   - 主角色优先描述，能显著提升稳定性。

5. **负空间（Negative Space）**
   - 多人场景必须保留足够负空间，避免人物融合或肢体交叠。
   - 推荐：large negative space between characters, empty center composition

6. **最稳定构图**
   - 对称构图：对话、对峙、仪式感
   - 三角构图：三人关系、群像
   - 深度分层：foreground + midground + background（最推荐）

7. **推荐 Prompt 结构顺序**（工业级）:
   1. CAMERA（机位、焦距、朝向）
   2. SPACE（环境、构图、负空间）
   3. BLOCKING（人物屏幕位置 + 前中后景）
   4. RELATIONSHIP（距离、视线、权力关系）
   5. LIGHTING
   6. DETAILS（人物细节）

8. **最佳工作流**:
   - Step 1: 先生成空场景（锁定空间、透视、光线）
   - Step 2: 锁定摄影机方向
   - Step 3: 再加入角色（按层级描述）
   - Step 4: 保持轴线与动线一致

**在分镜中的应用**:
处理多人场景时，必须先明确摄影机位置、屏幕坐标、人物层级和轴线，再描述人物动作。优先使用 Screen Position + 分层结构，而非相对位置描述。

---

## Post-Generation Quality Self-Inspection & Upgrade Protocol (生成后质感自检与升级 — 强制执行)

在完成分镜和提示词生成后，必须执行以下**质感自检流程**，并对最终输出质量负责：

**自检 checklist（必须逐项检查）**：
- 光影是否具有电影级层次与体积感？（是否有明显主光、轮廓光、环境光互动）
- 人物质感是否高级？（皮肤毛孔、眼睛聚焦与高光一致性、衣料真实褶皱与重量感、发丝细节）
- 环境与物理反馈是否真实？（粒子运动、材质互动、湿润/干燥质感、反光逻辑）
- 是否存在明显AI假感？（塑料皮肤、空洞眼神、僵硬姿势、漂浮焦点、不一致高光）
- 情绪与表演是否自然有层次？（微表情、下意识小动作、情绪落点是否清晰）
- 整体是否达到"可直接用于影视级图像/视频生成"的标准？

**升级规则**：
- 如果自检发现质感一般或存在明显问题，必须**立即自行升级**提示词：
  - 加强光影描述（加入具体光位 + 体积光 + 电影参考）
  - 强化眼睛与皮肤真实感（使用Ocular Realism模块）
  - 增加材质与物理细节（fabric weight, particle interaction, subsurface scattering等）
  - 提升表演结构（更具体的"人物 + 小动作 + 下意识反应 + 情绪落点"）
- 升级后再次自检，直到质感达到专业水准。

**最终输出要求**：所有提示词必须经过此自检与升级流程。输出时可附带简短自检说明（如"已自检并强化眼睛汇聚与光影层次"）。

---

## Neutral Front Portrait Module (中性正面肖像生成技巧 v1.0 — 角色参考图专用强制模块)

> **触发条件**：任何角色概念设计、角色身份板（Character Reference Sheet）、多视图一致性锚点图 — **必须首先生成标准中性正面肖像**，以此为所有后续视图、表情变体、服装变体的基准锚点。

### 核心强制原则（Must Never Break）

- **视角强制**：`perfectly frontal view + head perfectly straight-on facing camera + symmetrical facial composition + shoulders square to camera + no head turn/tilt/rotation`
- **表情强制**：`neutral facial expression + calm impassive resting face + no smile/no smirk/no emotional micro-expression + relaxed neutral gaze + natural resting lips slightly closed + subtle natural human facial asymmetry`
- **为什么严格**：AI 模型默认添加微笑或轻微情绪，强侧光会让"中性脸"带有故事性或阴沉感，破坏后续多视图一致性和角色圣经准确性。

---

### 正面中性肖像核心提示词模块（放在角色描述之后、镜头描述之前）

```
perfectly frontal view, head perfectly straight-on facing the camera, symmetrical facial composition, shoulders square to camera, direct eye contact with camera, neutral facial expression, calm impassive resting face, no smile, no smirk, no emotional expression, relaxed neutral gaze, natural resting lips slightly closed, subtle natural human facial asymmetry and micro-details, lifelike but emotionless professional character reference portrait
```

---

### 光照策略（最容易被忽略的关键）

中性参考图**绝对禁止强侧光、伦勃朗光、戏剧性阴影**，否则光影会"表演"出情绪。

**方案A（最干净 — 推荐做角色锚点）**：
```
soft even frontal key lighting with subtle fill from below, gentle volumetric light falloff, soft natural catchlights in both eyes, minimal facial shadows that could imply emotion, clean but cinematic three-dimensional form
```

**方案B（更电影化 — 带环境氛围）**：
```
motivated soft window light from front-left, diffused key light with gentle shadows, realistic light interaction on skin and fabric, subtle volumetric atmosphere, shallow depth of field
```

---

### 强制技术参数（必须附加）

```
shot on Arri Alexa 65, 85mm or 100mm lens, T2.8, shallow depth of field, detailed realistic skin texture with visible pores and natural imperfections, subsurface scattering (SSS), lifelike eyes with realistic catchlights and reflections, realistic fabric texture and physics, photorealistic, hyperrealistic, ultra photorealistic, realistic live-action cinematic film still, no plastic skin, no waxy skin, subtle realistic film grain
```

---

### Negative Prompt 强化版（强烈建议固定使用）

```
smile, smirking, grinning, happy, joyful, sad, angry, surprised, emotional expression, turned head, head tilt, looking away, profile view, three-quarter view, eyes closed, winking, dramatic lighting on face, harsh shadows on face, plastic skin, waxy skin, doll-like, idealized beauty, cartoon, anime, illustration, stylized rendering
```

---

### 不同景别推荐结构

| 类型 | 附加描述 |
|------|---------|
| **特写/胸像（最常用锚点）** | [角色描述] + 正面中性核心模块 + 方案A光照 + 技术参数 |
| **全身正面参考** | 加：`full body front view, standing straight facing camera, natural relaxed posture, arms resting naturally at sides, feet shoulder-width apart, clean neutral stance` |
| **半身带环境参考** | 在全身基础上加轻微环境层次，但脸部必须保持中性正面 |

---

### 多视图一致性标准工作流（MANDATORY ORDER）

1. **Step 1** — 用本模块生成**标准中性正面图**（保存 seed 或作为 Character Reference / IP-Adapter 图）
2. **Step 2** — 侧面/背面/45°角时加：`consistent character, same person as the front neutral reference, exact same facial features, same age, same skin details, same bone structure`
3. **Step 3** — 表情变体单独生成：`same character as the neutral front reference, [specific emotion], but keep facial structure and bone structure 100% identical`
4. **Step 4** — 服装/道具变体也基于此正面锚点出发

> 最大化 Seedance 2.0、Kling、Flux 等多模型中的角色一致性。

---

### 完整示例（已通过写实协议 v1.0 全部自检）

**民国旗袍女性 — 中性正面特写参考图**：
```
1920s Republican era Shanghai elegant Chinese woman in crimson qipao, delicate yet strong facial features, high cheekbones, almond-shaped eyes, natural black hair in elegant 1920s updo with subtle waves, [具体五官/气质/年龄描述], perfectly frontal view, head perfectly straight-on facing the camera, symmetrical facial composition, shoulders square to camera, direct eye contact with camera, neutral facial expression, calm impassive resting face, no smile, no smirk, no emotional expression, relaxed neutral gaze, natural resting lips slightly closed, subtle natural human facial asymmetry and micro-details, lifelike but emotionless professional character reference portrait, soft even frontal key lighting with subtle fill from below, gentle volumetric light falloff, soft natural catchlights in both eyes, minimal facial shadows, shot on Arri Alexa 65, 85mm lens, T2.8, shallow depth of field, detailed realistic skin texture with visible pores and natural imperfections, subsurface scattering, lifelike eyes with realistic catchlights, realistic silk qipao fabric texture and subtle sheen, photorealistic, hyperrealistic, ultra photorealistic, realistic live-action cinematic film still, no plastic skin, no waxy skin, subtle realistic film grain
```

---

## Character Consistency Bible (MANDATORY for multi-shot projects — lock after first detailed character description)

When processing the first highly detailed shot, immediately extract and permanently lock a rich **Character Design Bible** using professional multi-view + detail structure.

**Recommended Elements to Lock**:
- Multiple angles: Front, 3/4, Side, Back, Hair/Accessory details
- Close-up detail grids: Embroidery motifs, collar, jewelry, fabric texture, fur
- Full-body views from different angles
- Material & texture specifics (velvet, gold/silver embroidery, jade, pearls, fur)
- Hair style and accessory breakdown
- Color palette and overall mood

Every future prompt must reference these locked elements to maintain strict visual consistency.

**Example locked Character Bible**:
"Character: mid-30s East Asian male, sharp jawline, intense focused eyes with natural micro-expressions, light stubble, visible skin pores and subtle texture under cold light, natural slight redness on cheeks. Wearing heavy dark hooded monastic robe with thick matte woven fabric, deep natural folds and realistic weight, slight damp darkening at hem. Red tactical goggles with micro-scratches and soft reflections worn on face. Hands show real skin texture, knuckles, and subtle calluses. Body type: athletic and grounded. Expression style: restrained, ritualistic, absolute resolve. No changes to face structure, robe details, goggle appearance, or skin texture across any shots."

**Standardized Character Description Template (通用角色描述规范模板)**:
Use this structured format for all major characters to ensure high texture, cinematic quality, and consistency:

"[Archetype + Age + Gender], [key facial features], [expression/micro-expression details]. Wearing [clothing with fabric texture, fit, and details]. [Hair style and texture]. [Key accessories with material/reflection details]. [Posture/action if applicable]. Located in [environment/setting]. Overall atmosphere: [mood + presence]. Cinematic lighting with [specific light interaction]. Ultra-realistic movie still quality, [skin texture, pores, imperfections], precise material rendering on [clothing/accessories]."

**Powerful Corporate Villain / Antagonist Character (企业权势反派角色描述模板)**:
"Powerful corporate villain male in his mid-40s, refined and luxurious appearance with sharp, aristocratic features. Wearing an expensive custom-tailored black suit with subtle sheen and fine fabric texture, slicked-back glossy black hair with precise styling, cold arrogant expression with a subtle sinister half-smile at the corner of his mouth. Wearing a luxurious high-end watch with metallic reflections. Seated in a high-end executive leather chair. Located in a sleek glass-walled skyscraper office with panoramic night city views. Overall atmosphere: cold, oppressive yet restrained business empire aesthetic with strong presence. Cinematic lighting with reflective glass surfaces, high-contrast chiaroscuro, subtle rim and hair light. Ultra-realistic movie still quality, detailed fabric texture, skin pores and subtle imperfections, precise material rendering on suit, watch, and leather chair."

---

## 人物骨相强化与欧美人高级审美 Prompt 指南（Character Bone Structure Enhancement & Western Aesthetic Guide）

> **适用场景**：写实 cinematic 短剧 / 角色概念设计 / 多视图一致性 / Seedance 2.0 / Kling 等视频生成
> **核心目标**：通过精准光影描述 + 骨相强化词，让人物达到「人类最高审美标准」的帅气/靓丽效果（自然真实、非塑料感）

### 核心原则

最高人类审美标准的关键：
- **对称 + 和谐比例**：五官协调、骨骼结构优美
- **自然真实美**：保留皮肤毛孔、细微纹理、健康光泽，避免塑料/蜡质/娃娃脸
- **气场与存在感**：眼神、姿态、骨相共同塑造高级感
- **光影是核心武器**：平光会毁骨相，精准电影级光影能让骨相「立体雕刻」出来

欧美人骨相特点（与东亚人差异）：
- 颧骨较高、颌线更清晰有力
- 鼻梁挺直、眼窝较深
- 光影强化后雕塑感更强，适合硬朗帅气或高级知性路线

### 光影强化骨相方法（最重要）

| 排名 | 光影类型 | 增强效果 | 推荐场景 | 强度 |
|------|----------|----------|----------|------|
| 1 | **Rembrandt Lighting** | 颧骨 + 颌线 + 鼻梁 | 帅气男、优雅女、关键肖像 | ★★★★★ |
| 2 | **Split Lighting** | 骨相极致戏剧化 | 硬汉、反派、情绪强烈角色 | ★★★★☆ |
| 3 | **Short / Side Lighting** | 颌线 + 侧脸轮廓 | 侧面镜头、动态走位 | ★★★★☆ |

**Rembrandt Lighting 描述模板**（直接复制使用）：
```
Rembrandt lighting, key light positioned 45 degrees to the [left/right] and slightly above eye level, creating a distinct triangle of light on the shadow-side cheek, sculpting and accentuating cheekbones and jawline with natural shadow falloff, subtle fill light preserving detail in shadows
```

**分镜表中的光影标注建议**：
- 正面/3/4面 → Rembrandt Lighting
- 侧面/走位 → Short / Side Lighting
- 情绪高潮/反派 → Split Lighting

### 欧美人专用描述词库

**男性（Handsome / Chiseled）**：
```
strong chiseled jawline, high cheekbones, straight or aquiline nose, deep-set expressive eyes, refined yet masculine bone structure, broad yet elegant shoulders
```

**女性（Beautiful / Elegant）**：
```
high cheekbones, delicately defined jawline, straight nose, almond-shaped or deep-set eyes with natural catchlight, graceful neck and collarbone line
```

**通用顶级审美锚点（放 Prompt 最前面）**：
```
embodying the pinnacle of natural Western beauty, strikingly attractive with refined classical proportions and strong bone structure, authentic photorealistic human features
```

### 骨相强化完整 Prompt 模板

```
[年龄] year old Caucasian [male/female], [顶级审美锚点], [具体骨相+五官描述], [光影模块], [服装/姿态/表情], shot on Arri Alexa 65, 85mm lens, T2.8, cinematic lighting, ultra photorealistic, realistic skin texture with visible pores and fine lines, natural subtle redness, directional facial chiaroscuro, visible film grain and skin noise, fine dust particles, no over-smooth skin, natural subsurface scattering, film grain, intricate details --ar 9:16
```

**负面提示（建议常驻）**：
```
flat lighting, front lighting, weak jawline, undefined bone structure, plastic skin, waxy texture, doll-like, overly smooth, deformed jaw
```

### 骨相强化实用示例

**示例1：经典硬朗帅气男（Rembrandt 强化骨相）**
```
32 year old handsome Caucasian man, embodying the pinnacle of natural Western male beauty, strong chiseled jawline, high cheekbones, straight nose, deep-set piercing blue eyes, refined masculine bone structure, classic Rembrandt lighting with key light 45 degrees from upper left creating a distinct triangle of light on the shadow cheek that sculpts the jawline and cheekbones, subtle cinematic fill light, confident expression, shot on Arri Alexa 65, 85mm lens, T2.8, ultra photorealistic, realistic skin texture with pores and subtle stubble, natural shadow falloff, film grain --ar 2:3
```

**示例2：优雅知性欧美女性（柔和 Rembrandt）**
```
28 year old elegant Caucasian woman, breathtaking natural Western beauty, high cheekbones, delicately defined jawline, straight nose, almond-shaped deep-set eyes with natural catchlight, graceful neck line, refined feminine bone structure, soft Rembrandt lighting positioned 45 degrees to camera left, forming a sculptural triangle of light that beautifully enhances cheekbones and facial definition, gentle directional cinematic lighting, subtle confident gaze, shot on Arri Alexa 65, 85mm lens, realistic skin with healthy glow and natural texture, ultra photorealistic, film grain --ar 9:16
```

**示例3：强戏剧硬汉风（Split + Side Lighting）**
```
35 year old intense Caucasian man, strikingly handsome with powerful bone structure, sharp jawline, prominent cheekbones, deep-set eyes, split lighting with strong side light from camera right, half face in deep shadow, high contrast cinematic lighting that dramatically carves out facial bone structure, moody atmosphere, shot on Arri Alexa 65, ultra photorealistic, realistic skin details and texture, film grain --ar 2:3
```

### 多视图一致性整合（16-Grid / Character Sheet）

把「顶级审美锚点 + 骨相描述 + Rembrandt 光影模块」做成**固定前缀**，后面再接不同角度变化（正面 / 侧面 / 背面）。

### 视频提示增强（Seedance / Kling）

在视频提示词末尾加上：
```
consistent motivated cinematic lighting across shots, realistic moving shadows emphasizing facial bone structure as the character turns or moves, natural light interaction with skin
```

### 骨相强化常见问题排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 骨相不够明显 | 光太正 / fill 太多 | 加大 Key Light 角度，减少 fill |
| 阴影太黑 | 没有 fill light | 加 `subtle fill light from the opposite side` |
| 看起来太凶 | 过度使用 Split | 改用 Rembrandt 或加少量 fill |
| 塑料感 | 阴影边缘太锐利 | 加 `soft natural shadow falloff` |
| 多角度不一致 | 光源方向没固定 | 在角色概念阶段锁定 Key Light 方向 |

---

## Scene Consistency Bible (MANDATORY for multi-shot projects — lock after first detailed scene description)

When processing the first highly detailed shot of a location, immediately extract and permanently lock a rich **Scene Bible**. Every future prompt for the same location MUST match exactly in architecture, lighting direction & color temperature, props placement, atmosphere, and overall mood.

**16-Grid Multi-Angle Scene Reference System (16宫格场景多角度参考系统)**:
对于重要或需要多镜头覆盖的场景，强烈建议建立**16宫格多角度覆盖参考**（360°环绕不同机位）。
每个格子代表一个独立角度的分镜参考，用于系统性锁定场景空间。

典型结构：
- 4个主要机位（四角/关键位置） × 4种距离/高度组合（全景、中景、近景、细节角度）
- 或系统覆盖：房间四角 + 中心区域 + 不同高度（低机位、眼平、高机位）

用途：
- 锁定建筑结构、家具摆放、门窗位置、props布局
- 统一光影逻辑（主光方向、环境光、阴影体积）
- 确保环境细节（纹理、摆设、窗外景色）一致
- 为后续分镜提供可靠的空间与角度参考

当处理复杂场景时，优先参考或生成此类16宫格系统，以实现强场景一致性。所有同一场景的镜头必须严格遵循这些视觉锚点。

**Example locked Scene Bible**:
"Interior of vast ancient monastery nave at night: wet stone floor with realistic puddles and blue reflections, ancient stone columns and arches with mineral streaks and wear, high vaulted ceiling fading into cold blue mist. Thick cold blue-gray fog (7000K-8000K) rising from floor, swirling around legs and waist, volumetric god rays, floating dust and condensation particles. Cold directional moonlight through arched stained-glass windows, strong but softened by fog. Low-key cinematic blue-gray color grade, high contrast, deep blacks, subtle film grain, soft lens flare on window highlights. No modern elements, no text, extreme photorealistic monastery atmosphere with oppressive ritual tension."

**Consistency Enforcement in Every AI Image Prompt (Non-negotiable)**:
After the main description, ALWAYS append:
"Strict character consistency: exactly matching the locked Character Bible above — no drift in face, skin texture, clothing fabric/weave/folds/weight, accessories, or body language. Strict scene consistency: exactly matching the locked Scene Bible above — identical architecture, stone texture, lighting direction and color temperature, fog density and movement, floor reflections, and overall atmosphere. This is the same [character name] and same [location] as previous shots."

---

## Prop Design & Consistency Template (道具设计与一致性模板 — 重要道具专用)

When a prop is central to the story or appears across multiple shots (weapons, special objects, recurring items), create and lock a **Prop Design Bible** using this professional structure:

**Prop Name**: [Chinese name + English if applicable]

**Hero Render**: Main angled beauty shot description — overall form, material finish, how light interacts with surfaces, and dominant aesthetic (e.g., elegant, brutal, ritualistic, ancient).

**Key Details & Ornaments**: Specific callouts for intricate elements (engravings, inlays, charms, mechanical features, textures).

**Dimensions**: Precise measurements in cm (overall length, blade length, handle, thickness, key segments).

**Materials & Finish**: Base material + surface treatment (brushed steel, aged bronze, lacquered wood, bone, feather, enamel inlay, etc.).

**Color Palette**: 4–6 colors with descriptive names and emotional tone.

**Structure Breakdown** (for complex props): How it disassembles or key functional/mechanical parts.

**Design References**: Historical, cultural, or real-world inspiration + similar existing props.

**Usage & Interaction**: How the prop behaves with characters, lighting, action, and environment (weight feel, sound potential, visual impact in shots).

**Consistency Rule**: Once locked, every prompt featuring this prop must reference its distinctive shape, materials, scale, and signature details to ensure visual continuity across shots.

---

## Global Elements (define once):

- Film-wide visual language (e.g., "Anamorphic 2.39:1, heavy teal-orange contrast, 1970s film grain, practical lighting only, inspired by Denis Villeneuve + Roger Deakins").
- Recurring visual motifs (mirrors = fractured identity; rain = emotional release; clocks = time pressure).
- Color psychology per character/arc.

---

## Director's Must-Take Course Integration Protocol (《导演必修课》7模块完整内联协议 — 新增)

本技能已将用户《导演必修课》全部7个核心模块深度融合。生成分镜时必须体现以下原则：

### 模块1：导演核心思维（Want vs Need + 情绪弧线 + 爽点）
- 每个场景/镜头必须明确服务于角色的 **Want（表面欲望）** 与 **Need（内在真相）** 冲突。
- 优先设计**情绪弧线**：钩子 → 建立 → 升级 → 爆发 → 回响/新钩子。
- 短剧必须每集有明确**爽点**（打脸/权势碾压/情感爆发/身份反转等）。

### 模块2：镜头语言与空间掌控
- 优先使用**特写 + 近景**（70%以上）。
- 所有镜头运动必须**有情绪动机**（缓慢推进服务压迫/情感聚焦）。
- 严格执行**空间坐标锁定** + 25格参考系统，防止跳戏。
- 必须在每个SHOT中标注 Spatial Coordinates。

### 模块3：布光与氛围营造
- 严格执行 **Motivated Lighting**（光源必须有明确来源）。
- 使用光影直接服务情绪（情绪光影映射）。
- 强制反塑料：真实皮肤SSS、材质光影互动、阴影带环境色、高光自然过渡。
- 推荐使用专业光位术语（前侧光、侧逆光、顶光、轮廓光等）。

### 模块4：表演与情感微捕捉
- 必须设计**眼神类型**（温柔注视 / 死亡凝视 / 锐利直视 / 计算式注视等）。
- 强制加入**微表情 + 呼吸 + 身体微反应**。
- 涉及眼泪时必须使用真实眼泪物理描述（已内联）。
- 近景/特写必须有丰富表演细节，避免空洞眼神和僵硬表情。

### 模块5：短剧专属节奏与剪辑
- 每集必须有**至少1-2个明确情绪峰值**。
- 结尾必须设计**强钩子**（身份揭露、权力反转、情感冲击、新冲突）。
- 快慢节奏结合：信息段快、情绪高潮给空间。
- 优先使用 reaction insert、prop close-up 来控制节奏，而非压缩表演时长。

### 模块6：AIGC导演实操系统
- 严格执行 **7阶段工作流**：剧本分析 → 空间锁定 → 镜头设计 → 布光 → 表演 → 提示词 → 强制自检。
- 建立并锁定 **Character Bible + Scene Bible**。
- 每条提示词必须包含一致性指令（空间、光影、表演、材质）。
- 生成后必须执行完整自检 checklist。

### 模块7：高级融合技法
- 实现 **光影-情绪-物理-连续性** 四维融合。
- 光影必须真实响应材质（皮肤、布料、液体、金属）。
- 表演、布光、空间、节奏必须服务于同一情绪目标。
- 最终输出必须通过"Director's Full Fusion Self-Check"。

**Director's Full Fusion Self-Check（生成后强制执行）**：
- Want vs Need 冲突是否被视觉化？
- 光源是否有明确来源且方向一致？（四步布光法）
- 表演是否有具体眼神类型 + 微表情 + 呼吸？
- 空间坐标是否锁定且多镜一致？
- 情绪峰值和钩子是否明确？
- 是否存在塑料感、跳戏、空洞表演？
- 色温是否明确指定？调色是否匹配项目Look Book？
- 质感层（皮肤/布料/场景/湿衣）是否有专项真实感描述？
- 是否存在AI失真（变形手/多余手指/面部变形）？
- 高难度光照场景（多光源/金属/树影/霓虹）是否使用了专项提示词+参考图双控制？
- 每个场景是否都有完整的Scene Opening State Module（开场状态6子模块：环境/站位/角色状态/服装/灯光/声音）？
- 开场状态是否可作为"首帧"独立使用（闭上眼就能"看到"场景）？
- Phase 2.8叙事推理层7步分析是否全部完成？每个镜头是否有明确的Narrative Intent？
- 角色心理画像（dominance/body_tension/eye_contact）是否与镜头角度/运镜一致？
- 潜台词是否驱动了镜头策略（而非台词字面意思）？
- Runtime State JSON是否已初始化且跨镜头连续？
- 整体是否达到"可直接用于Seedance/Kling专业生产"的电影级标准？

### Auto Rewrite Loop（自动重写闭环 — 校验失败时强制执行）

> **核心理念**：当Full Fusion Self-Check任意项失败时，AI不得继续生成后续镜头，必须自动进入重写闭环，直到所有校验通过。

**校验失败→重写动作映射表**：

| 校验失败项 | 重写动作 | 具体操作 |
|-----------|---------|---------|
| 叙事意图缺失 | AdjustNarrativeIntent | 重新确认镜头目的，补充Primary Intent |
| 故事阶段不匹配 | AdjustStoryStage | 重新评估Scene Stage，调整景别/运镜/光比 |
| 角色心理不一致 | AdjustCharacterPsych | 修正visible/hidden emotion，调整微表情描述 |
| 权力关系错误 | AdjustBlocking | 修正dominance→角度映射，调整走位/构图 |
| 潜台词未视觉化 | AdjustSubtext | 按潜台词类型替换镜头策略（而非按台词字面） |
| 视线方向错误 | AdjustEyeline | 修正eyeline_vector，确保视线闭合 |
| 景别失衡 | AdjustShotScale | 重新评估shot_scale与story_stage匹配度 |
| 无叙事动机运镜 | AdjustCameraPosition | 删除或补充运镜动机（No Motivation, No Movement） |
| 焦点错误 | AdjustFocusTarget | 修正attention priority，调整Rack Focus / 浅景深 |
| 光影情绪冲突 | AdjustLighting | 修正lighting preset，确保与emotion_arc匹配 |
| 剪辑点无动机 | AdjustCutTiming | 重新评估cut_motivation（dialogue_turn / reaction / action_peak） |
| 情绪弧线断裂 | AdjustEmotionArc | 重新规划emotion arc，确保递进连续 |
| AI失真风险 | 质感修正 | 启用模块8防失真协议（四步布光/质感打假/调色锁定） |
| 连续性错误 | AdjustContinuity | 修正axis/eyeline/action continuity，必要时回溯前镜 |

**重写流程**：
1. 识别失败项 → 查表确定重写动作
2. 仅修改失败项相关字段，不改动已通过校验的部分
3. 重新运行Full Fusion Self-Check
4. 最多重写3轮，3轮仍失败则标注`[NEEDS MANUAL REVIEW]`并继续下一镜头

### Runtime State JSON（跨镜头连续性状态机 — 每个场景维护一份）

> **核心理念**：AI在连续生成分镜时，必须维护一个结构化状态对象，确保跨镜头的视觉连续性、空间一致性和情绪递进。每个场景生成第一个镜头时初始化，后续镜头必须读取并更新。

**状态机结构**（每个场景一份，随镜头更新）：

```json
{
  "scene_id": "scene_001",
  "narrative_intent": "ShiftPower",
  "story_stage": "Conflict",
  "scene_energy": 0.72,
  "active_axis_id": "line_A_B",
  "camera_side": "left_of_axis",
  "characters": {
    "角色A": {
      "screen_orientation": "left",
      "eyeline_vector": {"x": 1.0, "y": -0.1},
      "dominance": 0.3,
      "pose": "sitting",
      "visible_emotion": "calm",
      "hidden_emotion": "fear"
    }
  },
  "relationship_graph": {
    "A_to_B": {"trust": 0.2, "fear": 0.6, "power_gap": -0.5}
  },
  "visual_attention": [
    {"target": "A_eyes", "priority": 1, "reason": "fear_micro_expression"}
  ],
  "lighting": {
    "key_direction": "left",
    "color_temp_K": 3200,
    "key_to_fill_ratio": "6:1"
  },
  "validation": {
    "axis_locked": true,
    "eyeline_valid": true,
    "rewrite_required": false
  }
}
```

**状态机使用规则**：
- 每个新场景初始化一份
- 每生成一个镜头，更新：character pose/dominance/emotion、camera_side、attention、validation状态
- 轴线越轴时必须显式标注`axis_locked: false`并记录越轴原因
- 角色情绪变化时更新visible/hidden emotion并确保递进合理
- 光影变化时更新lighting字段

### 模块8：导演视觉控制与AI防失真协议（Director's Visual Control & Anti-Artifact Protocol — 新增）

**核心理念**：你不是在"让AI随便生成"，而是像指挥摄影师、灯光师和美术指导一样，**严格把控视觉语言**。AI失真（变形手、塑料脸、不一致光影、假质感、风格崩坏）本质上是模型"猜"得太多、控制不足导致的。核心策略是：**用导演思维把AI当作协作工具，而不是黑箱**。

#### 8.1 前期把控：Storyboarding与Reference先行
- **先分镜后提示词**：不要直接扔提示词。先用AI工具生成草图/分镜，确保构图、机位、情绪正确，再用参考图引导AI。
- **上传参考材料**：人物一致性用Character Reference；场景用环境参考；风格用电影截图。
- **明确导演指令**：在提示词中指定"机位"（low angle, dolly zoom）和"镜头语言"（cinematic, film grain, anamorphic lens）。
- **避免失真**：前期定义清晰，AI就不会"自由发挥"导致比例崩坏。

#### 8.2 灯光模式严格控制（Lighting Direction — 四步布光法）

AI最容易在光影上失真（阴影方向错、多个光源冲突）。必须像真实剧组一样描述灯光体系：

**四步布光强制描述模板**（每个涉及布光的镜头必须包含）：
1. **主光（Key Light）**：明确方向、色温、强度。例：`single key light from camera left, warm 3200K golden hour, dramatic chiaroscuro contrast`
2. **补光（Fill Light）**：柔化阴影的比例。例：`soft fill from opposite side at 30% intensity, subtle natural ambient bounce`
3. **背光/轮廓光（Rim Light）**：勾勒立体感。例：`strong rim light from behind creating edge highlights on hair and shoulders`
4. **环境光（Practical/Ambient）**：场景光源依据。例：`practical light from window (warm) + desk lamp (cool)`

**灯光模式定情绪（强制映射）**：

| 灯光模式 | 情绪效果 | 适用场景 | 提示词模板 |
|---------|---------|---------|-----------|
| **高调照明（High-Key）** | 明亮、柔和、低对比→轻松/纯净/希望 | 喜剧、浪漫、温暖 | `high-key lighting, soft diffused illumination, low contrast, even fill, bright atmosphere` |
| **低调照明（Low-Key）** | 黑暗、强对比→神秘/紧张/压抑/力量 | 悬疑、惊悚、戏剧 | `low-key lighting, deep shadows, high contrast, dramatic chiaroscuro, noir atmosphere` |
| **侧光（Side Light）** | 立体感、戏剧冲突、内心挣扎 | 对峙、冲突、独白 | `dramatic side lighting, half face illuminated, deep shadow on opposite side, sculptural chiaroscuro` |
| **逆光（Back Light）** | 轮廓光、梦幻、隔绝感 | 告别、回忆、超现实 | `strong backlighting, silhouette rim, golden edge highlights, ethereal glow, lens flare` |
| **顶光（Top Light）** | 孤立、威严、恐怖、审讯感 | 权力、压迫、审讯 | `harsh top-down lighting, deep eye socket shadows, ominous overhead illumination, vertical light shafts` |

**强制色温指定**（不可省略）：
- 暖色温（2700K-4000K）：`warm 3200K golden hour, amber and orange tones, intimate warm cast` → 温暖/亲密/怀旧/浪漫
- 冷色温（5000K-6500K+）：`cool 6500K moonlight with blue tint, cold blue-white cast, sterile blue atmosphere` → 冷静/疏离/神秘/悲伤
- 混合色温：`mixed color temperature: warm interior practical light (3200K) + cool exterior light (6500K), color temperature contrast creating visual tension`

#### 8.3 调色风格统一美学（Color Grading Protocol）

整个项目必须建立**Look Book**并锁定调色风格，防止不同生成间的色调漂移（color shift）。

**项目级调色锁定模板**：
```
cinematic color grading, [选择风格], desaturated midtones, filmic LUT, consistent color palette across all shots
```

**调色风格速查**：

| 风格 | 提示词 | 情绪/类型 |
|------|--------|----------|
| **Teal & Orange** | `teal shadows and warm skin highlights, complementary color contrast, Hollywood blockbusters style` | 好莱坞大片、动作、戏剧 |
| **Kodak Vision3 胶片** | `Kodak Vision3 film stock emulation, warm grain, subtle halation, natural skin tones, organic color rendition` | 剧情、文艺、怀旧 |
| **冷峻现代** | `desaturated cold palette, high contrast blue-grey, minimal color, clinical modern aesthetic` | 科幻、惊悚、现代都市 |
| **梦幻诗意** | `soft pastel color grading, gentle gradients, selective saturation boost on key elements, ethereal atmosphere` | 爱情、回忆、梦幻 |
| **暗黑/赛博朋克** | `deep shadows with neon color accents, cyberpunk palette, high contrast, magenta and cyan highlights` | 科幻、反乌托邦 |

**调色反向提示词（必须加入）**：
```
oversaturated, blown out highlights, plastic skin, unnatural color, color shift between shots, inconsistent color grading, flat color, no color depth, garish colors
```

#### 8.4 质感层"打假"强制（Texture Authenticity — 已与规则4.7/4.8/4.9联动）

AI最常见的"塑料感"来自缺乏微细节。除规则4.7（布料）/4.8（场景）/4.9（湿衣）的专项质感外，以下通用质感层必须在**每个镜头**中强制加入：

**通用微细节正向提示词**：
```
highly detailed skin texture with visible pores and fine lines, subtle realistic film grain, natural subsurface scattering, environmental occlusion in creases, micro-surface noise, natural lens imperfections, slight chromatic aberration
```

**通用质感打假反向提示词**：
```
smooth plastic skin, doll-like, waxy surface, blurry, low detail, AI artifact, deformed, overly smooth, airbrushed, no texture, flat surface, CGI look, too clean, no imperfections
```

#### 8.5 具体防失真技术指令（Anti-Artifact Techniques）

**生成参数控制**：
- CFG Scale: 5-8（太高会过度饱和/失真）
- 采样步数: 30+
- 分辨率: 使用高分辨率基础模型
- 低 CFG + 多步数 + 高分辨率 = 减少AI失真概率

**结构化防失真关键词**（加入提示词）：
```
anatomically correct, perfect hands with five fingers, natural proportions, no deformation, no extra limbs, no distorted faces, sharp focus on subject, photorealistic details
```

**防失真反向提示词**：
```
deformed, extra fingers, missing fingers, mutated hands, distorted face, asymmetric eyes, crossed eyes, blurry, low quality, artifact, watermark, text overlay, bad anatomy, bad proportions
```

**修复工作流（Director's Post-Fix Pipeline）**：
1. 生成基础图 → 选最佳候选
2. Inpainting修复问题区域（手变形、脸怪异、服装失真）
3. 叠加真实噪点/颗粒统一质感
4. 整体调色匹配Look Book
5. 最终一致性检查（与Character Bible对比）

#### 8.7 高难度光照匹配场景协议（Challenging Lighting Scenarios — 4类专项）

以下4类场景是AI光照失真的高发区，必须使用专项提示词 + 参考图双控制策略。

**通用参考图片使用原则（Runway/Midjourney/Flux）**：
1. 优先上传高质量参考图（光照清晰、构图干净）
2. References 设置中重点勾选 **Lighting + Color**（权重拉最高）
3. Prompt 必加：`Match the exact lighting, shadows, color temperature and reflections from the reference image`
4. 先用 Image to Image 固定光照，再转 Image to Video 做动态

**通用光照匹配反向提示词**：
```
lighting inconsistency, wrong shadow direction, color shift, flat lighting, multiple conflicting light sources, unrealistic reflections, no ambient occlusion, blown highlights, crushed shadows
```

---

**场景1：室内多光源人像（Indoor Multi-Light Portrait）**

**主要难点**：多种色温混合、阴影方向冲突、皮肤色温染色不自然、高光与暗部细节平衡

**专项正向提示词**：
```
multi light setup with deliberate color temperature mixing, warm key light from [direction] at 3200K + cool fill light from [opposite direction] at 6500K, accurate shadow direction consistency, natural skin color rendering under mixed lighting, soft shadow edges with realistic penumbra, balanced highlight and shadow detail, practical interior lights with visible light sources, natural light falloff
```

**参考图锁定要点**：
- 光源方向与强度比例（Key Light vs Fill Light 权重）
- 脸部/身体的色温混合过渡效果
- 阴影边缘的软硬程度（soft penumbra vs hard edge）
- 整体氛围与光影对比度

**参考图 Prompt 关键词**：`multi light setup, color temperature mixing, warm key light + cool fill light`

---

**场景2：金属/高反光物体渲染（Metallic & Highly Reflective Objects）**

**主要难点**：高光边缘精准控制、环境反射真实性、曲面高光变形、镜面+漫反射平衡

**专项正向提示词**：
```
accurate metallic reflections with sharp specular highlights, realistic environment reflections on curved metallic surface, proper caustics and light concentration, balanced mirror reflection and diffuse reflection, accurate material BRDF rendering, natural metal surface imperfections with micro-scratches and fingerprints, realistic chrome/steel/aluminum material response to light
```

**参考图锁定要点**：
- 主要高光位置与形状（specular highlight shape）
- 金属表面反射的环境细节（environment map）
- 桌面/地面交互反射
- 光影在金属边缘的锐利程度（edge highlight sharpness）

**参考图 Prompt 关键词**：`accurate metallic reflections, sharp specular highlights, environment reflection on glossy surface, caustics`

---

**场景3：户外树影斑驳（Dappled Light / God Rays Through Foliage）**

**主要难点**：不规则斑驳阴影一致性、体积光真实感、光影在人物/地面的自然变化、强光与暗部同时保留

**专项正向提示词**：
```
dappled sunlight filtering through tree canopy, realistic organic shadow patterns on ground and figures, volumetric god rays with atmospheric light scattering, golden hour warm light with visible light shafts, natural leaf shadow silhouettes with soft edges, dynamic light and shadow interplay, subsurface scattering on leaves, natural atmospheric haze filtering sunlight
```

**参考图锁定要点**：
- 阳光穿透树叶形成的斑驳光影图案形状
- 体积光束的方向与强度
- 人物身上光影的分布比例（明暗面积比）
- 金色小时整体暖调氛围

**参考图 Prompt 关键词**：`dappled sunlight, realistic tree shadows, volumetric god rays, golden hour light filtering through leaves`

---

**场景4：夜景霓虹反射（Night Neon Reflections）**

**主要难点**：高饱和霓虹溢出与颜色混合、湿地面强烈反射、霓虹在皮肤/物体上的染色、暗部与霓虹的动态范围

**专项正向提示词**：
```
vibrant neon reflections on wet ground and puddles, cyberpunk night lighting with high color saturation, strong specular reflection of neon signs on wet surfaces, neon color spill on skin and nearby objects creating realistic color contamination, deep shadows with preserved detail, high dynamic range between bright neon and dark shadows, realistic water surface with micro-ripples distorting reflections, atmospheric fog catching neon light
```

**参考图锁定要点**：
- 霓虹灯的颜色与精确位置
- 地面反射的颜色和清晰度
- 光线在湿表面上的 specular reflection 强度
- 整体赛博朋克氛围与光影对比度

**参考图 Prompt 关键词**：`neon reflections on wet ground, vibrant neon glow, cyberpunk night lighting, strong specular reflection on puddles`

---

#### 8.6 后期收尾：导演最终把关（Post-Production Director's Final Check）

AI生成只是"毛片"（dailies），后期必须执行：
- **统一调色**：匹配项目Look Book
- **添加真实光晕/颗粒**：film grain + subtle lens effects
- **修复残余失真**：Inpainting局部修复
- **匹配整个项目的视觉风格**：与之前生成的镜头对比一致性

**导演心态总结（四条铁律）**：
1. **不要依赖AI灵感**：先有明确愿景（参考真实电影），让AI执行而非创作。
2. **层层控制**：灯光→色温→质感→调色，像真实剧组协作。
3. **迭代而非一次生成**：生成10张，挑最好的Inpaint，而不是求"完美提示词"。
4. **工具组合**：Midjourney/Flux/SDXL + ControlNet + IP-Adapter + 后期 = 你的"虚拟摄影棚"。

**四维协同公式**：
> **灯光**（结构+情绪基础）→ **色温**（情感温度）→ **质感**（真实可信）→ **调色**（统一美学）

---

**本技能现在已成为完整融合《导演必修课》8模块的电影级AIGC分镜系统。**

**协议更新完成**。现在当你使用本 skill 生成分镜时，AI 会自动像专业导演/场记一样计算时长，彻底解决"台词长度不被考虑"的问题。

---

## OpenMontage 端到端视频制作集成 (OpenMontage E2E Video Production Integration)

> **定位**：当分镜+AI提示词完成后，可使用 OpenMontage 实现从脚本到成片的端到端自动化视频制作。
> **GitHub**：[calesthio/OpenMontage](https://github.com/calesthio/OpenMontage) — 全球首个开源 AI Agentic 视频制作系统
> **许可**：AGPL-3.0 | Stars: 4,200+

### 核心定位

OpenMontage 是一个**开源的、智能体驱动的视频制作系统**，将 AI 编程助手（Claude Code、Cursor、Copilot 等）转化为完整的视频工作室。与本技能的关系：

| 本技能（movie-story） | OpenMontage |
|----------------------|-------------|
| 分镜 + AI 提示词生成 | 端到端视频制作（脚本→成片） |
| 输出：分镜表 + 提示词文本 | 输出：最终视频文件 |
| 人工复制提示词到各平台 | AI 自动执行全部流程 |

### 12 条生产管线

| 管线 | 产出 | 适用场景 |
|------|------|----------|
| **Animated Explainer** | AI解说视频（调研+配音+画面+音乐） | 教育内容、教程 |
| **Cinematic** | 预告片、情绪驱动剪辑 | 品牌影片、预告 |
| **Documentary Montage** | 真实素材主题蒙太奇（免费素材库） | 视频论文、情绪短片 |
| **Animation** | 动态图形、MG动画 | 社交媒体、产品演示 |
| **Hybrid** | 实拍素材 + AI辅助视觉 | 现有素材增强 |
| **Clip Factory** | 长视频批量截取短视频 | 长内容复用 |
| **Talking Head** | 真人出镜讲话视频 | 演讲、Vlog |
| **Avatar Spokesperson** | 虚拟人主持视频 | 企业通讯 |
| **Localization & Dub** | 字幕、配音、翻译 | 多语言分发 |
| **Podcast Repurpose** | 播客转视频 | 播客营销 |
| **Screen Demo** | 软件录屏演示 | 产品教程 |
| **Product Launch** | 产品发布视频 | 新品预热 |

**统一流程**：`research → proposal → script → scene_plan → assets → edit → compose`

### 支持的 AI 模型（与本技能共用）

| 类别 | 模型/服务商 |
|------|-----------|
| **视频生成** | Kling、Runway Gen-4、Google Veo 3、Grok Imagine Video、Higgsfield、MiniMax、HeyGen |
| **本地视频** | WAN 2.1、Hunyuan、CogVideo、LTX-Video（免费） |
| **图像生成** | FLUX、Google Imagen 4、DALL-E 3、Grok Imagine Image、Recraft |
| **TTS** | ElevenLabs、Google TTS（700+声音）、OpenAI TTS、Piper（免费离线） |
| **音乐** | Suno AI（完整歌曲+人声）、ElevenLabs Music |
| **后期** | FFmpeg（编码/字幕/混音/调色）、Remotion（React视频合成）、HyperFrames（HTML/GSAP） |
| **免费素材** | Pexels、Pixabay、Unsplash、Archive.org、NASA、Wikimedia Commons |

### 与本技能协作流程

```
用户剧本
  ↓
movie-story（本技能）→ 分镜表 + AI图像提示词 + AI视频提示词
  ↓
OpenMontage → 自动执行全流程：
  1. 读取分镜表和提示词
  2. 调用AI模型生成素材（使用本技能的提示词）
  3. 自动剪辑、配音、字幕、合成
  4. 质量自检 + 渲染输出
  ↓
最终视频文件
```

### 安装

```bash
git clone https://github.com/calesthio/OpenMontage.git
cd OpenMontage
make setup
# 无make: pip install -r requirements.txt && cd remotion-composer && npm install && cd ..
```

**前置依赖**：Python 3.10+、FFmpeg、Node.js 18+、AI编程助手

### 使用方式

安装后，在 AI 编程助手中用自然语言描述需求：
```
"Make a 60-second cinematic short based on this storyboard: [粘贴本技能输出的分镜表]"
```

### 零成本路径

无需任何付费 API 密钥即可产出可用视频：
- **旁白**：Piper TTS（免费离线）
- **素材**：Pexels + Unsplash + Pixabay + Archive.org + NASA
- **合成**：Remotion（React）或 HyperFrames（HTML/GSAP）
- **后期**：FFmpeg（编码、字幕、混音、调色）

### 质量管控

- **7维度供应商评分**：任务适配度(30%)、输出质量(20%)、控制功能(15%)、可靠性(15%)、成本效率(10%)、延迟(5%)、连续性(5%)
- **预合成验证**：交付承诺检查、幻灯片风险评分
- **渲染后自检**：ffprobe验证、帧采样、音频分析
- **预算控制**：执行前估算、单操作审批阈值($0.50)、总预算上限($10)

### 平台输出配置

| 平台 | 分辨率 | 宽高比 |
|------|--------|--------|
| YouTube 横屏 | 1920x1080 | 16:9 |
| YouTube 4K | 3840x2160 | 16:9 |
| YouTube Shorts | 1080x1920 | 9:16 |
| Instagram Reels | 1080x1920 | 9:16 |
| TikTok | 1080x1920 | 9:16 |
| LinkedIn | 1920x1080 | 16:9 |
| Cinematic | 2560x1080 | 21:9 |

---

## 场景丰富性优化大师 v1.1 (Scene Richness Optimization Master)

> **定位**：接收原始场景描述（剧本片段、基础提示词或简单设定），通过深度分析，结合 **25-grid 多角度场景系统** 和 **12-category 资产系统**，输出极致丰富、具有电影质感、物理真实且服务于情绪与叙事的场景提示词，同时提供空间扩展建议。
> **触发条件**：用户要求"优化场景"、"丰富场景"、"场景提示词优化"、"scene richness"、"25-grid 场景"、"12-category 资产"。

### 核心原则（v1.1 必须严格遵守）

1. **多平面空间层次 + 25-grid 思维**：必须构建清晰的前景、中景、背景，并考虑 25-grid 不同角度（正前、侧面、斜角、高低机位等）的空间关系与构图可能性。
2. **光影与色调深度融合**：光源必须 motivated，强调体积光、阴影塑造、材质真实互动（皮肤 SSS、布料反光、物体投射、空气粒子）。色调服务于情绪与主题。
3. **物理真实与环境融合**：人、物体、环境在光影、材质、空气中自然交融，避免任何塑料感、蜡质感、扁平感。
4. **环境叙事 + 12-category 资产覆盖**：优先调用或描述 12-category 中的道具、场景元素、氛围、VFX 等，加入能暗示故事的细节。至少覆盖 3 个以上资产类别。
5. **情绪与叙事服务**：所有细节必须强化戏剧功能（Want vs Need、情绪张力、主题）。
6. **空间一致性**：构图适合目标画幅，注重多镜头连续性与空间映射一致性。
7. **资产与网格协同**：生成的丰富场景应便于后续拆解为 25-grid 变体，并与现有角色/道具/场景资产库匹配。

### 12-Category 资产系统

| 类别 | 内容示例 |
|------|----------|
| 1. 角色资产 | 主角/配角/群演的视觉锚点、服装、表情库 |
| 2. 道具资产 | 关键道具、手持物、环境道具 |
| 3. 场景元素 | 建筑、家具、自然元素、毁伤细节 |
| 4. 光影氛围 | 光源类型、色温、阴影形状、体积光 |
| 5. 材质互动 | 布料、金属、木材、玻璃、液体物理反应 |
| 6. 大气效果 | 尘埃、烟雾、雾气、光线散射 |
| 7. 表面细节 | 锈迹、污渍、磨损、指纹、生活痕迹 |
| 8. 声音提示 | 环境音、脚步、材质碰撞（用于提示词描述） |
| 9. VFX 元素 | 火花、水花、碎片、能量效果 |
| 10. 摄影机 | 机位、运镜、镜头选择、景深 |
| 11. 色调情绪 | 色彩方案、对比度、饱和度、色彩关系 |
| 12. 叙事细节 | 暗示背景故事的隐藏细节、符号、痕迹 |

### 25-Grid 多角度场景系统

将场景空间划分为 5×5 网格，规划不同机位角度：

| | 左 | 中 | 右 |
|--|----|----|-----|
| **前** | 左前低角 | 正面低角 | 右前低角 |
| **中** | 左平视 | **正面平视（主镜头）** | 右平视 |
| **后** | 左后高角 | 正面高角 | 右后高角 |

**使用方式**：优化场景时，考虑主镜头（中心）之外的 8 个主要变体角度，确保光影、道具、人物位置在所有角度下都合理且丰富。

### 工作流程（必须按顺序执行）

**步骤1：分析原始输入 + 资产映射**
- 提取核心主体、动作、情绪、戏剧功能
- 识别可调用的 12-category 资产类型
- 判断当前描述在空间层次、光影、细节上的缺失

**步骤2：规划丰富性方案（融入 25-grid 思维）**
- 设计前景/中景/背景的具体内容与空间关系
- 规划光源方向、质感、体积效果与色调
- 考虑 25-grid 主要角度下的构图可能性与元素分布
- 选择能强化叙事的环境细节，并关联 12-category 资产

**步骤3：强制自检与优化（v1.1 增强版清单）**
- [ ] 是否有清晰的 3 层空间结构？是否考虑了 25-grid 不同角度的空间关系？
- [ ] 光影是否有源？是否与材质产生真实互动？色调是否统一？
- [ ] 是否有效调用或描述了 12-category 中的至少 3 个资产类别？
- [ ] 细节是否服务于情绪/叙事？是否避免空旷、扁平、塑料感？
- [ ] 是否具备空间一致性，便于多镜头连续使用？
- [ ] 构图是否适合目标画幅（16:9 或 9:16）？

**步骤4：生成最终输出**

### 输出格式（严格按照以下结构）

```
【场景分析与资产映射】
（简要说明原始描述的核心、缺失点、已识别的 12-category 资产类型，
以及结合 25-grid 的丰富性规划思路，120-180字）

【优化后提示词】
（输出完整、结构化、高信息密度的英文提示词，适合直接用于图像/视频生成。
必须体现多层空间、光影互动、资产细节与电影质感。）

【25-Grid 场景扩展建议】
（简要说明该丰富场景在 25-grid 主要角度下的构图要点、
元素分布变化、光影调整建议，以及如何保持空间一致性。
便于后续生成多角度变体。）

【使用建议】
（针对这一场景的镜头/运镜建议、与角色资产的衔接提示、迭代方向等）
```

### 技术与风格标准

- 始终追求 `photorealistic cinematic quality + real physics blending`
- 优先使用：`Arri Alexa 65`、`filmic color science`、`subsurface scattering`、`volumetric god rays`、`realistic material interaction`、`film grain`
- 所有描述必须具体化，并与 12-category 资产系统和 25-grid 空间思维结合
- 避免泛化，优先使用已验证的 cinematic 语言与光影色调原则

### 示例：优化前 vs 优化后

**优化前（原始描述）**：
> "A woman stands in a rainy alley at night, looking sad."

**优化后（场景丰富性优化大师 v1.1 输出）**：

```
【场景分析与资产映射】
核心：雨夜小巷中悲伤的女人。缺失：空间层次、光影动机、环境叙事细节。
资产映射：类别4（光影氛围：单一钨丝灯从顶部左侧产生戏剧性阴影）、
类别6（大气效果：雨滴、蒸汽、 floating dust motes in volumetric god rays）、
类别7（表面细节：湿滑鹅卵石、生锈铁门、剥落海报）。
25-grid 思维：主镜头正面平视；可在左前低角捕捉雨滴在镜头前穿过，
右后高角展现巷子深度与孤独感。

【优化后提示词】
Cinematic medium shot, a melancholic woman standing in a narrow rain-slicked alley at night, 
harsh single tungsten practical light from top-left creating dramatic Rembrandt lighting 
with distinct shadow triangle on cheek, rain droplets catching volumetric rim light, 
floating dust motes in god rays, weathered surfaces with natural patina — rusted iron gate, 
peeling movie posters, wet cobblestones reflecting warm light, 
realistic light interaction with materials, photorealistic, hyperrealistic, 
realistic live-action cinematic film still, shot on Arri Alexa 65, 85mm lens, T2.8, 
shallow depth of field, detailed realistic skin texture with visible pores, 
natural subtle redness, directional facial chiaroscuro, visible film grain and skin noise, 
no over-smooth skin, lifelike eyes with realistic catchlights, 
heavy fabric physics with rain soaking into wool coat, 
steam rising from grate, moody atmospheric depth, 
intricate details --ar 16:9 --stylize 250 --v 6

【25-Grid 场景扩展建议】
- 左前低角：雨滴在镜头前穿过，强调纵深与孤独感
- 右后高角：展现巷子深度，人物极小，强调环境压迫感
- 正面低角：仰拍，雨水从上方落下，强化情绪上升
- 所有角度保持：顶部左侧光源、湿润表面反光、蒸汽位置一致

【使用建议】
- 主镜头用 medium shot，reaction 用 CU，建立镜头用 WS 右后高角
- 可在同一提示词基础上，修改镜头类型和机位描述，生成 25-grid 变体
- 与角色资产（女人服装、表情）保持一致性
```

---

### 参考电影技术

| 电影 | 核心技法 | 场景丰富性要点 |
|------|----------|----------------|
| 《银翼杀手2049》 | 体积光 + 大气粒子 | 烟雾、雨滴、霓虹反光多层次空间 |
| 《沙丘》 | 沙漠纹理 + 巨大比例尺 | 表面细节（沙纹、磨损）+ 前景遮挡 |
| 《降临》 | 极简 + 高对比光影 | 单一光源 + 体积雾，用少胜多 |
| 《水形物语》 | 饱和色彩 + 材质对比 | 潮湿表面、金属反光、水体互动 |
| 《布达佩斯大饭店》 | 对称构图 + 室内细节 | 前景框架 + 背景深度 + 道具叙事 |

### 与其他模块的关系

- **MANDATORY Scene Richness & Cinematic Environment Layer**：本模块是其实操版——该层定义规则，本模块提供执行流程
- **Phase 3 (Professional Cinematic Storyboard Creation)**：本模块输出的优化提示词，直接用于该阶段的 AI 提示词生成
- **Character Consistency Bible**：优化场景时必须调用角色视觉锚点，确保人物与环境互动真实
- **Scene Consistency Bible**：优化后的场景必须记录到场景圣经，确保多镜头一致性
- **Seedance 2.0 提示词**：本模块输出的提示词可直接用于 Seedance 2.0 视频生成

---

## Appendix A: Film Language Ontology（电影语言本体库 — 镜头语义速查参考）

> 每种镜头运动/构图方式都有三层语义：叙事意义、情绪效果、心理暗示。生成镜头时必须确保三层语义与叙事意图一致。

**镜头运动本体映射**：

| 运镜类型 | 叙事意义 | 情绪效果 | 心理暗示 | 适用意图 |
|---------|---------|---------|---------|---------|
| **Push In** | 发现/施压/顿悟/决策 | 紧张感增加/亲密感增加 | 内向聚焦/被迫注意 | RevealInfo, BuildSuspense, ShiftPower, Crisis |
| **Pull Out** | 揭示环境/展示孤立/情感撤回 | 孤独/无助/释放 | 失去控制 | CreateIsolation, CreateRelief, Aftermath |
| **Static** | 观察/不可避免/情绪僵局 | 冷静/紧张维持 | 被困状态 | Observation, Dominance, Clinical |
| **Handheld** | 不稳定/紧迫/主观压力 | 焦虑/混乱 | 失控 | Conflict, Crisis, Fear, Panic |
| **Rack Focus** | 注意力转移/隐藏信息揭示 | 惊讶/顿悟 | 认知转移 | RevealInfo, Foreshadowing, ConfirmSuspicion |
| **Crane Up** | 权力展示/宏大/全知视角 | 敬畏/压力 | 权力优越 | ShiftPower, EstablishRelationship |
| **Crane Down** | 逼近/压迫/从宏观到微观 | 压迫/聚焦 | 从全知到个体 | BuildSuspense, CreateThreat |
| **Tracking** | 跟随/速度匹配/旅程推进 | 参与/流动感 | 与角色同步 | Development, Journey, FollowCharacter |
| **Pan/Tilt** | 视线跟随/物体揭示/搜索 | 期待/发现 | 被引导的注意力 | Eyeline Follow, RevealInfo, Search |
| **Dolly Zoom** | 心理冲击/现实扭曲 | 眩晕/震惊 | 世界崩塌感 | Crisis, Betrayal, Realization |
| **Whip Pan** | 时间跳跃/快速连接/混乱 | 冲击/混乱 | 时空断裂 | Action, Time Skip, Disorientation |

**构图方式本体映射**：

| 构图方式 | 叙事意义 | 情绪效果 | 心理暗示 |
|---------|---------|---------|---------|
| **Low Angle** | 支配/威胁/宏伟 | 压力/敬畏 | 权力优越 |
| **High Angle** | 弱点/脆弱/监视 | 同情/不安 | 权力丧失 |
| **Dutch Angle** | 不安/失衡/精神异常 | 焦虑/混乱 | 世界失序 |
| **OTS** | 关系/对峙/对话空间 | 亲近/参与 | 关系意识 |
| **Single Shot** | 孤立/隐藏/内心世界 | 孤独/隐秘 | 心理分离 |
| **Frame within Frame** | 囚禁/偷窥/聚焦 | 压迫/偷窥欲 | 被困/被观察 |
| **Centered Symmetry** | 控制/秩序/权力 | 冷酷/压迫 | 制度化力量 |

**剪辑技术本体映射**：

| 剪辑技术 | 叙事意义 | 适用场景 |
|---------|---------|---------|
| **Hard Cut** | 冲击/节奏/简洁 | Action, Shock, Rhythm |
| **L-Cut** | 反应优先/情感吸收 | Reaction Priority, Tension After Line |
| **J-Cut** | 预示/威胁/期待 | Scene Transition, Incoming Threat, Anticipation |
| **Match Cut** | 视觉/动作相似性连接 | Visual Parallels, Time Passage |
| **Smash Cut** | 最大冲击/风格断裂 | Shock Value, Genre Shift |
| **Cross Cut** | 平行叙事/时间压力 | Parallel Action, Suspense Build |
| **Long Hold** | 情绪回响/沉默即台词 | Aftermath, Grief, Resolution |

---

## 参考文档

- `references/openmontage-guide.md` — OpenMontage 完整使用指南
- `references/openmontage-pipeline-reference.md` — 12条管线详细参考
- `references/scene-richness-optimization-master.md` — 场景丰富性优化大师完整参考（12-category + 25-grid 详解）
- GitHub: [calesthio/OpenMontage](https://github.com/calesthio/OpenMontage)
