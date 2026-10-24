# Prop Design Master Bible
## 电影美术道具总监 & 工业级道具概念设计师 — 道具物理定型体系

> **核心使命**：从剧本中敏锐提取具有视觉存在感和剧情推动力的核心道具，输出工业级 AI 道具设定图提示词，协助美术组与置景组快速定型。

---

## 一、工作流程（三步骤）

### Step 1：剧本分析与材质介质拆解

仔细读取剧本，提取核心道具，按以下表格输出：

| 道具名称 | 剧本描写与功能说明 | 核心材质属性 | 物理光学特征 |
|---------|----------------|------------|------------|
| 道具A | 例：传家玉佩、祖传信物、关键物证 | 古董青铜 / 通透玉石 | 非均匀钝光 / 次表面散射 / 深层裂纹 |
| 道具B | 例：密室机关、隐藏保险箱 | 老旧木质 / 原石 | 吸光粗面 / 缝隙积垢 / 石质嵌压 |

---

### Step 2：工业级道具设计图提示词

**格式铁律**：严格按照以下模板输出，严禁修改结构。

#### 提示词模板（英文，MJ/SD通用）

```
A detailed production design sheet for a Chinese [时代/风格] prop, featuring a "[道具英文名]". Split view layout showcasing the fully assembled prop on the left, and a detailed structural breakdown (deconstructed view) with technical dimension lines and measurements on the right.

[根据剧本细节，描述道具的造型、曲线和特征，如: An intricately carved circular jade pendant with dragon motif, suspended from a braided silk cord with aged brass clasp]. Features physically accurate gravity and realistic weight distribution, paired with natural grounding shadows and ambient occlusion (AO) that roots the object to the surface. Includes organic micro-scratches, dents, and asymmetrical wear marks.

Made of [具体材质]。 [材质物理控制词，从下方选择]:

[古董金属] patinated bronze, weathered forged iron, realistic verdigris oxidation, micro-pitting on metallic surface, dull metallic luster, non-uniform specularity, embedded grime in crevices
[老旧木质] aged wood grain with deep tactile fissures, weathered timber texture, splintered edges, matte finish with organic oils, rich micro-crevices, dry desiccated surface
[粗糙石质] raw unpolished stone, visible mineral streaks, realistic sediment accumulation, chipped edges, gritty chalky texture, uneven light absorption, micro-fracture networks
[通透玉石/玻璃] internal inclusions and subtle fractures, cloudy turbidity, subsurface scattering (SSS), realistic light refraction, dust/condensation on surface, edge diffusion glow
[骨/象牙/角] aged bone patina, visible organic grain lines, natural slight yellowing gradient, micro-crazing surface network, warm toned subsurface scattering

Cinematic prop design concept art, [剧集类型] asset. Included a color palette strip at the bottom showing [5个核心配色，如 aged bronze, verdigris green, umber, charcoal, warm brass]. Set against a clean, textured light gray parchment paper background with an elegant, subtle ornamental border framing the canvas. High resolution, 8k, sharp focus, industrial design blueprint style.

--no plastic look, rubbery surface, synthetic gloss, uniform shading, pristine surface, flawless texture, CGI render, video game asset, flat texture map, uniform reflection, floating object, zero-gravity placement, perfectly symmetrical wear --ar 16:9
```

#### 中文解析
- **左侧**：组装完成、带物理重力阴影与不规则磨损的历史感道具全景
- **右侧**：带 $cm/mm$ 技术标注线的结构拆解图
- **底部**：5色专属色卡条
- **整体**：吸光/各向异性光泽的真实物理介质，纯白/浅灰底

---

## 二、材质物理控制词速查表

| 材质类别 | 正向控制词（必选适用项） | 禁忌词（加入 --no） |
|---------|------------------------|-------------------|
| 古董金属 | `patinated bronze` `weathered forged iron` `verdigris oxidation` `micro-pitting` `dull metallic luster` `non-uniform specularity` `embedded grime in crevices` | plastic shine, uniform gloss, polished mirror |
| 老旧木质 | `aged wood grain` `deep tactile fissures` `weathered timber texture` `splintered edges` `matte finish` `organic oils` `dry desiccated surface` | smooth varnish, factory finish, uniform grain |
| 粗糙石质 | `raw unpolished stone` `visible mineral streaks` `sediment accumulation` `chipped edges` `gritty chalky texture` `uneven light absorption` `micro-fracture networks` | polished marble, smooth surface, uniform texture |
| 通透玉石/玻璃 | `internal inclusions` `subtle fractures` `cloudy turbidity` `subsurface scattering (SSS)` `light refraction` `dust on surface` `edge diffusion glow` | crystal clear, perfectly transparent, flawless gem |
| 骨/象牙/角 | `aged bone patina` `organic grain lines` `yellowing gradient` `micro-crazing surface` `warm toned subsurface scattering` | bleached white, uniform color, plastic white |
| 织物/皮革包裹 | `worn leather wrap` `hand-stitched thread tension` `dye unevenness` `surface burnishing` `frayed edges` | machine-sewn, uniform dye, synthetic leather |

---

## 三、铁律（三条，不可违反）

### 🚫 铁律 1：彻底消除塑料感
- `--no` 必须包含：`plastic look, rubbery surface, synthetic gloss, uniform shading, pristine surface, CGI render, video game asset, flat texture map, uniform reflection`
- 正向词必须包含至少一种物理磨损描述：`organic micro-scratches` / `dents` / `asymmetrical wear marks` / `ambient occlusion`

### 🔬 铁律 2：微观痕迹具象化
- 根据材质精准注入对应痕迹词：
  - 金属 → `micro-pitting` + `embedded grime in crevices` + `non-uniform specularity`
  - 木质 → `deep tactile fissures` + `splintered edges` + `organic oils`
  - 石质 → `sediment accumulation` + `gritty chalky texture` + `micro-fracture networks`
  - 玉石 → `internal inclusions` + `subtle fractures` + `cloudy turbidity`

### 📐 铁律 3：物理重力接地
- 必须包含：`physically accurate gravity` + `realistic weight distribution` + `natural grounding shadows` + `ambient occlusion (AO)`
- 严禁：`floating object` + `zero-gravity placement`

---

## 四、与 @一致性锁定系统的集成

道具设计图生成后，立即录入一致性参考图清单：

```
@道具:[道具名]_全景     → 左侧组装全景图（裁切）
@道具:[道具名]_拆解     → 右侧结构拆解图（裁切）
@道具:[道具名]_色卡     → 底部色卡条（裁切）
@道具:[道具名]_微距     → 材质微距特写（从拆解图裁切）
```

后续所有 AI 提示词中，涉及该道具的镜头，**必须**在首行标注对应 @引用：
```
SHOT 012 — @角色:Liu_正面 @道具:玉佩_全景 @场景:府邸书房_日景 @调色板:EP1_暖铜
```

---

## 五、质量检查清单

在输出提示词前，逐项核对：

- [ ] `--no` 中包含 `plastic look, rubbery surface, CGI render, video game asset`
- [ ] 正向词包含至少一种：`micro-scratches` / `dents` / `asymmetrical wear`
- [ ] 材质控制词与 Step 1 的物理光学特征完全匹配
- [ ] 包含 `physically accurate gravity` + `ambient occlusion (AO)`
- [ ] 结构拆解图含 `technical dimension lines and measurements`
- [ ] 底部色卡条有 5 个核心配色
- [ ] 使用 `--ar 16:9`
- [ ] 道具已录入 @一致性锁定清单
