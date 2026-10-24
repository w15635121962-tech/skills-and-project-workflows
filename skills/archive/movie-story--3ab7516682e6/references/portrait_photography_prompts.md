# 超写实人像摄影提示词库 (Hyper-Realistic Portrait Photography Prompts)

## 设计理念

**反AI塑料感 (Anti-Synthetic Look)** — 核心目标：让AI生成的人物看起来像原相机直出的真人照片，而非CGI渲染。关键策略：主动保留自然瑕疵、生理不对称、光学缺陷，以"不完美"构建真实感。

---

## 一、主模板：超写实自然光人像 (Master Template)

### 中文版（完整参数）

```
超写实人像摄影，原相机直出，85mm定焦镜头，大光圈浅景深，自然光，柔和光影，真实皮肤肌理，清晰毛孔，保留轻微自然小瑕疵，肤色通透不假白，五官原生自然、轻微不对称，表情放松不僵硬，生活化穿搭，真实实景背景，轻微胶片颗粒感，8k高清，无AI建模痕迹，神态灵动自然。
```

### English Version (AI Platform Optimized)

```
Hyper-realistic portrait photography, straight-out-of-camera look, 85mm f/1.4 prime lens, shallow depth of field with creamy bokeh, natural daylight, soft diffused lighting with gentle shadow falloff, authentic skin texture with visible pores and micro-imperfections, translucent skin tone with natural undertones — not over-processed or plastic-smooth, naturally asymmetrical facial features, relaxed unposed expression with lively eyes, casual everyday clothing, real-world background — no studio setup, subtle film grain, 8K ultra-high resolution, photorealistic — no CGI traces, no AI smoothness, candid spontaneous feel. --ar 3:4 --stylize 150 --v 6
```

---

## 二、参数逐项解析 (Parameter Breakdown)

| 参数层 | 中文 | 英文 | 作用 |
|--------|------|------|------|
| **镜头光学** | 85mm定焦镜头，大光圈浅景深 | 85mm f/1.4 prime, shallow DOF, creamy bokeh | 经典人像焦段，压缩透视，奶油焦外 |
| **光源系统** | 自然光，柔和光影 | Natural daylight, soft diffused lighting | 避免棚拍塑料光感，模拟窗光/黄金时刻 |
| **皮肤质感** | 真实皮肤肌理，清晰毛孔，保留轻微自然小瑕疵 | Authentic skin texture, visible pores, micro-imperfections | **反AI塑料感核心** — 主动保留瑕疵 |
| **肤色控制** | 肤色通透不假白 | Translucent skin, natural undertones | 避免死白/过曝/粉底感 |
| **面部结构** | 五官原生自然、轻微不对称 | Naturally asymmetrical features | 完美对称 = AI痕迹，轻微不对称 = 真人感 |
| **表情控制** | 表情放松不僵硬，神态灵动自然 | Relaxed expression, lively eyes, candid feel | 避免"证件照僵硬"和"过度摆拍" |
| **服装风格** | 生活化穿搭 | Casual everyday clothing | 去舞台化，人物融入真实场景 |
| **场景真实** | 真实实景背景 | Real-world background, no studio setup | 拒绝纯色背景板/影棚感 |
| **胶片质感** | 轻微胶片颗粒感 | Subtle film grain | 模拟胶片摄影的有机噪点，破AI完美平滑 |
| **分辨率和质感** | 8k高清，无AI建模痕迹 | 8K, photorealistic, no CGI traces | 技术规格 + 质感约束 |

---

## 三、场景化变体 (Scenario Variants)

### 3.1 男性硬朗肖像 (Masculine Portrait)

```
Hyper-realistic male portrait, raw camera output, 85mm f/1.4 prime lens, shallow depth of field, harsh side window light with defined shadows, rugged skin texture with visible pores, stubble, fine lines, and natural imperfections, weathered complexion, strong jawline with slight asymmetry, intense but relaxed gaze, plain cotton t-shirt, urban loft background with exposed brick, subtle film grain, 8K, photorealistic — no CGI, no airbrushing, no AI smoothness. --ar 3:4 --stylize 150 --v 6
```

### 3.2 女性柔光肖像 (Feminine Soft-Light Portrait)

```
Hyper-realistic female portrait, straight-out-of-camera, 85mm f/1.2 prime lens, dreamy bokeh, golden hour backlight with hair rim light, dewy natural skin with fine texture and visible pores, faint freckles, soft natural flush on cheeks — not makeup-perfect, gentle facial asymmetry, warm candid smile reaching the eyes, linen dress in neutral tone, wildflower field at sunset, subtle film grain, 8K, photorealistic — no CGI traces, no plastic skin, no studio retouching. --ar 3:4 --stylize 150 --v 6
```

### 3.3 街头纪实风格 (Street Photography)

```
Candid street photography portrait, 85mm f/1.8 prime lens, shallow depth of field with urban bokeh, overcast natural light — soft and shadowless, unretouched skin with visible texture and natural imperfections, asymmetrical face caught mid-expression, relaxed unposed demeanor, everyday streetwear — hoodie and jacket, busy city street background with motion blur, subtle film grain and slight chromatic aberration for lens realism, 8K, photorealistic — no CGI, no AI gloss. --ar 3:4 --stylize 100 --v 6
```

### 3.4 低光情绪肖像 (Low-Light Moody Portrait)

```
Cinematic low-light portrait, 85mm f/1.4 prime wide open, extreme shallow depth of field, single practical light source — warm tungsten desk lamp, deep shadows wrapping the face, skin texture emphasized by directional light, visible pores and micro-highlights, natural facial asymmetry, contemplative relaxed expression, dark wool sweater, shadowy interior with practical light spill, pronounced film grain for texture, 8K, photorealistic — no CGI, no AI smoothing, no perfect symmetry. --ar 3:4 --stylize 200 --v 6
```

### 3.5 老人肖像 — 岁月质感 (Aged Portrait)

```
Hyper-realistic portrait of an elderly person, 85mm f/2.8 prime, natural window light from one side, deeply textured skin — pronounced wrinkles, age spots, visible pores, and natural skin variations, silver-gray hair with natural texture, asymmetric aged features, gentle knowing expression with crow's feet, simple wool cardigan, lived-in home interior with bookshelves, subtle film grain, 8K, photorealistic — no CGI, no digital retouching, no airbrushing. --ar 3:4 --stylize 100 --v 6
```

---

## 四、反AI塑料感自检清单 (Anti-Synthetic Quality Checklist)

生成图像后逐项检查：

- [ ] **皮肤**：可见毛孔 / 纹理 / 微瑕疵（无蜡像光滑感）
- [ ] **肤色**：通透有血色（非死白 #FFFFFF / 非橘皮）
- [ ] **五官**：轻微不对称（双眼大小微差 / 眉毛高度微差 / 嘴角微偏）
- [ ] **眼睛**：双眼汇聚于同一焦点 / 高光锚点一致 / 微血管可见
- [ ] **表情**：非僵笑 / 非证件照 / 眼神有故事
- [ ] **头发**：碎发 / 毛躁 / 非完美弧线（拒绝CGI头盔发）
- [ ] **服装**：面料褶皱 / 经纬纹理 / 非完美对称
- [ ] **背景**：真实场景景深 / 非纯色背景板
- [ ] **光感**：自然光散射 / 非均匀棚拍平光
- [ ] **颗粒**：轻微胶片颗粒 / 非完美平滑渐变
- [ ] **镜头感**：轻微色散 / 暗角 / 非完美锐利（模拟真实镜头缺陷）

---

## 五、镜头焦段速查 (Lens Focal Length Reference)

| 焦段 | 用途 | 特征 |
|------|------|------|
| 35mm | 环境人像 | 带入场景，人物与环境并重 |
| 50mm | 标准人像 | 接近人眼视角，自然透视 |
| **85mm** | **黄金人像** | 压缩透视，奶油焦外，五官比例最优 |
| 135mm | 远摄特写 | 极致压缩，面部特写，背景彻底虚化 |
| 200mm | 超远摄 | 偷窥感/纪录片感，极度浅景深 |

---

## 六、使用场景映射

| 需求 | 推荐变体 | 画幅 |
|------|---------|------|
| 角色定妆照 (Character Design) | 主模板 / 3.2 女 / 3.1 男 | 3:4 |
| 情绪镜头 (Mood Shot) | 3.4 低光情绪 | 2.39:1 |
| 生活化转场 (Lifestyle Cutaway) | 3.3 街头纪实 | 16:9 |
| 老年角色 (Aged Character) | 3.5 老人肖像 | 3:4 |
| 情侣双人 (Couple Shot) | 主模板 × 2 + 互动描述 | 4:3 |

---

## 七、批量生成时的全局约束

所有人物提示词共用以下底线参数：

```
--stylize 100-200 (人物越低越好，保留原始细节)
--v 6
no CGI, no plastic skin, no AI gloss, no digital airbrushing
photorealistic, straight-out-of-camera
```

**禁止词黑名单**（出现在 negative prompt 或描述中主动规避）：
- perfect skin / flawless / airbrushed
- symmetrical face
- studio lighting / 3-point lighting
- solid color background
- CGI / 3D render / octane render / unreal engine
- beauty retouching / skin smoothing
