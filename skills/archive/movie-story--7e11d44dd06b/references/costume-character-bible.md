# Costume & Character Art Bible
## 电影服化道总监 & 角色美术指导 — 工业级角色定型体系

> **核心使命**：从剧本中精准提取核心角色，输出两套功能不同的工业级 AI 角色设定提示词，协助美术组进行高精度角色定型与服装打样。

---

## 一、工作流程（三步骤）

### Step 1：剧本分析与材质拆解

仔细读取剧本，提取核心角色，输出以下表格：

| 角色名称 | 剧本外貌/气质描写 | 服装面料类型 | 面料物理特性 |
|---------|----------------|------------|------------|
| 角色A | 例：冷峻、贵族感、银白发 | 真丝/重工刺绣 | 高吸光/丝绸柔光/半透明 |
| 角色B | 例：粗犷、草莽气质 | 粗麻/皮革 | 高吸光/哑光/磨损纹理 |

**面料分类参考**：
- 棉麻粗布 / 仿古布料
- 高级丝绸 / 缎面
- 轻盈薄纱 / 雪纺
- 皮革 / 仿皮
- 重工刺绣 / 盘扣织物
- 现代合成纤维 / 运动面料

---

### Step 2：第一张提示词 — 角色服化道多细节参考图 (Detail Sheet)

**功能**：复刻"多角度面部特写 + 衣服局部物理材质微距 + 核心配饰拆解"的设定集风格

#### 提示词结构模板（英文，MJ/SD通用）

```
A professional character design sheet and costume detail collection. Split-screen collage layout: featuring headshot expressions from multiple angles (front, 3/4 left, 3/4 right, side profile) on one side, and multiple close-up macro shots of clothing texture, detailed embroidery patterns, [该角色特有配饰，如 belt ornaments/hair crown/mask/weapon detail] at the bottom. Set against a clean, solid white background with neat framing.

A [male/female] character, [年龄段，如 mid-20s/early 30s], with [面部与发型特征，如 sharp jawline, silver shoulder-length hair, piercing blue eyes]. Extreme photorealistic skin realism, subsurface scattering (SSS) skin, visible skin pores, fine peach fuzz, natural imperfections, clear catchlight in eyes.

Wearing [服装描述，如 a layered silk robe with intricate gold embroidery, draped over dark linen inner garment]. [面料物理控制词，从下方选择对应材质]:

[高级丝绸] subtle anisotropic silk sheen, soft contrast highlight roll-off, elegant flowing weave, micro-thread definition
[棉麻粗布] heavy matte fabric texture, anisotropic light absorption, no reflection, rough tactile weave, visible fiber grain
[轻盈薄纱] translucent fabric layer, subtle sub-surface light scattering through fabric, realistic sheer opacity, layered gossamer depth
[皮革材质] aged leather grain, realistic micro-creases, subtle satin leather specularity, worn patina, natural stress lines

High-end production costume design, cinematic character concept art, photorealistic, Unreal Engine 5 skin render, sharp focus, 8k resolution, professional studio softbox lighting, film production reference quality.

--no plastic skin, silicon face, porcelain doll skin, airbrushed, dead eyes, blank stare, plastic texture, rubbery fabric, synthetic gloss, 3D clothing mesh, stiff fabric, CGI wrinkles, vector folds --ar 3:4
```

#### 中文输出说明
- 多角度真皮层毛孔级面部特写（前/3/4左/3/4右/侧面）
- 底部：该角色特定面料的微距放大拆解图（去塑料感、带物理光泽与纤维细节）
- 底部：核心配饰特写（腰带饰物/发冠/面具/武器细节等）
- 纯白背景，设定集风格

---

### Step 3：第二张提示词 — 角色标准四视图与大头贴 (Turnaround View)

**功能**：复刻"超写实面部情绪特写 + 正/侧/背标准全身站姿转面"的物理重力打样风格

#### 提示词结构模板（英文，MJ/SD通用）

```
A standard character turnaround reference sheet and model sheet. Split layout: A cinematic close-up emotional headshot on the left, exhibiting realistic skin micro-contrast and facial depth; a full-body 3-view turnaround (front view, side view, back view) on the right. The character is in a stable, symmetrical standing pose with arms slightly down. Clean solid white studio background.

A [male/female] character, [年龄段], [身材描述，如 lean athletic build, 180cm height, broad shoulders]. The character's clothing exhibits realistic physical properties: natural fabric drape with realistic sagging weight, organic tension lines, and physically accurate folds driven by gravity. Multi-layered fabric stacking where clothing meets the feet.

[如有分层服装] The outer [garment type] creates natural break points where layers overlap, showing authentic weight distribution and gravity pull on each separate layer.

Hyper-realistic character concept art, 3D character modeling showcase style, flawless yet realistic skin texture, cinematic look, commercial photography softbox lighting, ultra-sharp details, 8k resolution.

--no plastic skin, silicon face, porcelain doll skin, airbrushed, CGI, 3D render, flat texture map, repeating patterns, floating fabric, zero gravity drape, stiff cloth --ar 16:9
```

#### 中文输出说明
- 左侧：极高质量高清面部情绪特写（带眼睛高光，皮肤微对比）
- 右侧：并排正面 / 侧面 / 背面全身站姿三视图
- 用于确定演员身材比例与衣服受重力下垂的物理剪影

---

## 二、面料物理控制词速查表

| 面料类型 | 正向控制词（必选其中适用项） | 禁忌词（加入 --no） |
|---------|--------------------------|-------------------|
| 棉麻粗布 | `heavy matte fabric texture` `anisotropic light absorption` `rough tactile weave` `no reflection` | synthetic gloss, silk sheen |
| 高级丝绸 | `subtle anisotropic silk sheen` `soft contrast highlight roll-off` `elegant flowing weave` `micro-thread definition` | matte fabric, rough texture |
| 轻盈薄纱 | `translucent fabric layer` `sub-surface light scattering through fabric` `realistic sheer opacity` `gossamer depth` | opaque fabric, heavy drape |
| 皮革 | `aged leather grain` `realistic micro-creases` `satin leather specularity` `worn patina` `natural stress lines` | smooth plastic, uniform gloss |
| 重工刺绣 | `intricate embroidery thread depth` `raised textile relief` `metallic thread catchlight` | flat print, 2D pattern |
| 现代合成 | `high-performance technical fabric sheen` `athletic stretch tension` `moisture management texture` | antique fabric, heavy drape |

---

## 三、铁律（三条，不可违反）

### 🚫 铁律 1：硬核去塑料感
- **禁止**在正向提示词中出现任何隐含"塑料感"的词汇
- **必须**在 `--no` 中包含：`plastic skin, silicon face, porcelain doll skin, airbrushed, rubbery fabric, synthetic gloss`
- **必须**在正向词中包含：`subsurface scattering (SSS) skin` 或 `anisotropic [material] sheen`

### ⚖️ 铁律 2：重力至上（全身图）
- 所有全身/半身图必须包含以下至少两项：
  - `realistic sagging weight`
  - `gravity-driven folds`
  - `physically accurate drape`
  - `organic tension lines`
  - `multi-layered fabric stacking at feet`
- 禁止出现：`floating fabric` `zero gravity drape` `stiff cloth`

### 🔬 铁律 3：物理光学强制项
- 每条提示词至少包含一处物理光学描述：
  - `subsurface scattering (SSS)` — 皮肤/薄纱
  - `anisotropic sheen` / `anisotropic light absorption` — 丝绸/皮革
  - `sub-surface light scattering through fabric` — 薄纱/轻盈面料
  - `realistic micro-creases` — 皮革/真实布料

---

## 四、与 @一致性锁定系统的集成

Detail Sheet 和 Turnaround View 生成后，立即录入一致性参考图清单：

```
@角色:[角色名]_Detail    → Detail Sheet（多角度面部+材质）
@角色:[角色名]_Turnaround → Turnaround View（三视图+重力打样）
@角色:[角色名]_正面       → 从 Turnaround View 裁切正面图
@角色:[角色名]_3/4        → 从 Detail Sheet 裁切3/4视角
```

后续所有 AI 提示词中，涉及该角色的镜头，**必须**在首行标注对应 @引用：
```
SHOT 003 — @角色:Olivia_正面 @角色:Olivia_Detail @场景:图书馆_日景 @调色板:EP1_冷蓝
```

---

## 五、质量检查清单

在输出所有提示词前，逐项核对：

- [ ] `--no` 中包含 `plastic skin, silicon face, airbrushed`
- [ ] 正向词包含 SSS 或 anisotropic 光学描述
- [ ] 全身图包含 `sagging weight` 或同等重力词
- [ ] 面料控制词与剧本描述的面料类型匹配
- [ ] Detail Sheet 提示词使用 `--ar 3:4`
- [ ] Turnaround View 提示词使用 `--ar 16:9`
- [ ] 两张提示词均已录入 @一致性锁定清单
- [ ] 配饰描述（腰带/发饰/面具/武器）已在 Detail Sheet 中单独提及
