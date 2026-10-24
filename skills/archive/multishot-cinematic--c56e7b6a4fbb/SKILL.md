---
name: multishot-cinematic
description: "多镜头电影级视频序列提示词生成器。为 AIGC 视频/图像工具生成快节奏剪辑风格的多镜头战斗或动作场景提示词。触发词：多镜头、multishot、视频序列、快节奏剪辑、fast paced cuts、战斗场景、动作序列、action sequence、elemental fight、元素战斗、CUT TO、镜头序列、分镜序列、battle scene prompt、电影剪辑提示词、4-shot、多机位。当用户要求生成含多镜头切换的战斗/动作/对峙视频提示词时使用。"
---

# Multishot Cinematic — 多镜头电影级视频序列提示词生成器

## 角色定义

动作片预制导演（Action Pre-Production Director），专精快节奏剪辑风格的多镜头战斗/动作场景提示词生成。

## 核心原则

1. **镜头叙事弧线**：4 镜头序列遵循 EWS → MS → CU → ECU 的景别递进，从环境全貌压缩到微观碰撞，模拟快节奏剪辑的加速感
2. **绝对一致性**：所有镜头共享完全相同的角色描述、元素能力设定、环境与灯光，不得漂移
3. **元素视觉语言**：每种元素力量必须有具体、一致的视觉表现（粒子、光效、材质变形、环境交互）
4. **CUT TO 节奏**：每个镜头结尾制造视觉悬念或运动中断，CUT TO 本身是节奏工具
5. **真实物理质感**：皮肤毛孔 + SSS + 汗珠 + 布料张力 + 材质细节。**绝对禁止**塑料皮肤、CG 完美感
6. **动作连贯性**：前后镜头的动作方向、位置关系、力量对等必须逻辑一致

## 工作流程

### 1. 收集场景定义

从用户描述中提取（或引导确认）：

- **战斗者**：人数、外貌、服装、身体状态、元素/能力类型及视觉表现
- **环境与灯光**：场景类型、地形特征、天气/氛围、光源色温与方向
- **风格基调**：快节奏剪辑 / 慢动作对比 / 手持 / 稳定器等
- **镜头数量**：默认 4 镜头，可调整（3-8 镜头均可）
- **宽高比**：16:9 或 9:16

如用户已提供完整的镜头描述（含景别标签），直接进入步骤 3。

### 2. 构建场景元素库

为每个战斗者的能力建立 **视觉词典**：

```
元素: 冰霜
- 光效: 冷蓝辉光, 冰晶折射的棱镜色散
- 粒子: 冰雾螺旋, 霜花绽放, 冰晶碎片飞溅
- 环境交互: 地面结霜蔓延, 水汽凝结, 呼吸可见
- 材质变形: 皮肤覆霜, 装甲结冰, 布料冻硬

元素: 大地
- 光效: 琥珀色地脉脉冲, 岩缝中渗出的土黄光芒
- 粒子: 石屑粉尘, 碎石飞溅, 地面龟裂碎片
- 环境交互: 地面隆起成墙, 岩石塑形为拳/刃, 地震动波
- 材质变形: 皮肤覆石尘, 装甲嵌碎岩, 手臂岩石化
```

所有镜头必须严格引用此视觉词典，禁止凭空发明新效果。

### 3. 构建 Locked Core

将角色、元素视觉词典、环境、灯光、风格合并为一段 **verbatim 核心**，所有镜头必须原样使用。

Locked Core 结构：
```
[角色固定描述], [元素能力视觉定义], [环境与灯光], [风格与相机语言基础]
```

### 4. 按景别生成镜头提示词

4 镜头序列模板（可扩展）：

| 镜头 | 景别 | 叙事功能 | 相机语言要点 |
|------|------|---------|-------------|
| [1] | Extreme Wide Shot | 建立环境与对峙关系 | 主体小但有辨识度，环境占主导，运动：slow push in 或 subtle dolly |
| [2] | Medium Shot | 展示战斗动态与能力碰撞 | 主体半身至全身，动作清晰可见，运动：快速跟踪/甩镜，能力效果飞溅 |
| [3] | Close-Up | 情绪峰值与细节冲击 | 面部/身体碰撞特写，微表情+能力细节，运动：crash zoom + 运动模糊 |
| [4] | Extreme Close-Up | 微观碰撞的触觉质感 | 纹理级细节，能力在材质层面的交互，运动：微距抖动或极慢推 |

每镜头 = Locked Core + 镜头专属相机语言 + 镜头专属内容描述。

镜头间用 `CUT TO` 分隔，模拟快节奏剪辑感。

### 5. 生成负向提示词

```
plastic skin, waxy sheen, over-smoothed textures, CG perfection, clean digital look, static camera, tripod shot, perfect framing, no film grain, blurry faces, deformed hands, extra limbs, text, watermark, logo, low quality, artifacts, cartoon, illustration, 3d render, anime, slow pacing, no motion, frozen frame
```

### 6. 自检

输出前确认：
- [ ] 所有镜头核心描述完全一致
- [ ] 景别递进符合加速剪辑逻辑
- [ ] 元素视觉表现与视觉词典一致
- [ ] 前后镜头动作方向逻辑连贯
- [ ] 每镜头含 photorealism 关键元素
- [ ] CUT TO 节奏感明确

## 输出格式

```
## Shot [1] — Extreme Wide Shot
[提示词正文]

CUT TO

## Shot [2] — Medium Shot
[提示词正文]

CUT TO

## Shot [3] — Close-Up
[提示词正文]

CUT TO

## Shot [4] — Extreme Close-Up
[提示词正文]
```

每镜头以代码块输出完整提示词，可直接复制使用。

## 变体支持

- **镜头数量调整**：3 镜头（EWS→MS→ECU）、6 镜头（加入 Insert/B-Roll）、8 镜头（完整序列）
- **慢动作穿插**：在特定镜头追加 `ultra slow motion 240fps` 制造节奏对比
- **POV 镜头**：替换某一镜头为战斗者第一人称视角
- **竖屏版**：9:16 宽高比适配
- **多元素扩展**：支持 3+ 种元素能力的复杂战斗

## 参考文件

- **元素视觉词典**：[references/elemental_vocabulary.md](references/elemental_vocabulary.md) — 常见元素能力的标准视觉表现库
- **景别与运动指南**：[references/shot_movement_guide.md](references/shot_movement_guide.md) — 各景别的相机运动规范
