# 人物骨相强化与高级审美指南

> **适用场景**：写实 cinematic 短剧 / 角色概念设计 / 多视图一致性 / AI 角色参考图生成
> **核心目标**：通过精准光影描述 + 骨相强化词，让人物达到高级审美效果（自然真实、非塑料感）

---

## 核心原则

- **对称 + 和谐比例**：五官协调、骨骼结构优美
- **自然真实美**：保留皮肤毛孔、细微纹理、健康光泽，避免塑料/蜡质/娃娃脸
- **气场与存在感**：眼神、姿态、骨相共同塑造高级感
- **光影是核心武器**：平光会毁骨相，精准电影级光影能让骨相「立体雕刻」出来

---

## 光影强化骨相方法

| 排名 | 光影类型 | 增强效果 | 推荐场景 | 强度 |
|------|----------|----------|----------|------|
| 1 | **Rembrandt Lighting** | 颧骨 + 颌线 + 鼻梁 | 帅气男、优雅女、关键肖像 | ★★★★★ |
| 2 | **Split Lighting** | 骨相极致戏剧化 | 硬汉、反派、情绪强烈角色 | ★★★★☆ |
| 3 | **Short / Side Lighting** | 颌线 + 侧脸轮廓 | 侧面镜头、动态走位 | ★★★★☆ |

> ⚠️ 中性正面肖像参考图**绝对禁止**强侧光、伦勃朗光、戏剧性阴影。光影强化仅用于角色概念设计/情绪表达场景，不用于中性基准参考图。

---

## Rembrandt Lighting 描述模板（直接复制使用）

```
Rembrandt lighting, key light positioned 45 degrees to the [left/right] and slightly above eye level, creating a distinct triangle of light on the shadow-side cheek, sculpting and accentuating cheekbones and jawline with natural shadow falloff, subtle fill light preserving detail in shadows
```

---

## 角色概念设计中的光影标注建议

- 正面/3/4面 → Rembrandt Lighting
- 侧面/走位 → Short / Side Lighting
- 情绪高潮/反派 → Split Lighting

---

## 描述词库

### 男性（Handsome / Chiseled）

```
strong chiseled jawline, high cheekbones, straight or aquiline nose, deep-set expressive eyes, refined yet masculine bone structure, broad yet elegant shoulders
```

### 女性（Beautiful / Elegant）

```
high cheekbones, delicately defined jawline, straight nose, almond-shaped or deep-set eyes with natural catchlight, graceful neck and collarbone line
```

### 通用顶级审美锚点（放 Prompt 最前面）

```
embodying the pinnacle of natural Western beauty, strikingly attractive with refined classical proportions and strong bone structure, authentic photorealistic human features
```

---

## 骨相强化完整 Prompt 模板

```
[年龄] year old [种族] [male/female], [顶级审美锚点], [具体骨相+五官描述], [光影模块], [服装/姿态/表情], shot on Arri Alexa 65, 85mm lens, T2.8, cinematic lighting, ultra photorealistic, realistic skin texture with visible pores and fine lines, natural subtle redness, directional facial chiaroscuro, visible film grain and skin noise, fine dust particles, no over-smooth skin, natural subsurface scattering, film grain, intricate details --ar 9:16
```

---

## 骨相强化实用示例

### 示例1：经典硬朗帅气男（Rembrandt 强化骨相）

```
32 year old handsome Caucasian man, embodying the pinnacle of natural Western male beauty, strong chiseled jawline, high cheekbones, straight nose, deep-set piercing blue eyes, refined masculine bone structure, classic Rembrandt lighting with key light 45 degrees from upper left creating a distinct triangle of light on the shadow cheek that sculpts the jawline and cheekbones, subtle cinematic fill light, confident expression, shot on Arri Alexa 65, 85mm lens, T2.8, ultra photorealistic, realistic skin texture with pores and subtle stubble, natural shadow falloff, film grain --ar 2:3
```

### 示例2：优雅知性欧美女性（柔和 Rembrandt）

```
28 year old elegant Caucasian woman, breathtaking natural Western beauty, high cheekbones, delicately defined jawline, straight nose, almond-shaped deep-set eyes with natural catchlight, graceful neck line, refined feminine bone structure, soft Rembrandt lighting positioned 45 degrees to camera left, forming a sculptural triangle of light that beautifully enhances cheekbones and facial definition, gentle directional cinematic lighting, subtle confident gaze, shot on Arri Alexa 65, 85mm lens, realistic skin with healthy glow and natural texture, ultra photorealistic, film grain --ar 9:16
```

### 示例3：强戏剧硬汉风（Split + Side Lighting）

```
35 year old intense Caucasian man, strikingly handsome with powerful bone structure, sharp jawline, prominent cheekbones, deep-set eyes, split lighting with strong side light from camera right, half face in deep shadow, high contrast cinematic lighting that dramatically carves out facial bone structure, moody atmosphere, shot on Arri Alexa 65, ultra photorealistic, realistic skin details and texture, film grain --ar 2:3
```

---

## 多视图一致性整合

把「顶级审美锚点 + 骨相描述 + Rembrandt 光影模块」做成**固定前缀**，后面再接不同角度变化（正面 / 侧面 / 背面）。

---

## 负面提示（骨相强化专用）

```
flat lighting, front lighting, weak jawline, undefined bone structure, plastic skin, waxy texture, doll-like, overly smooth, deformed jaw
```

---

## 骨相强化常见问题排查

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 骨相不够明显 | 光太正 / fill 太多 | 加大 Key Light 角度，减少 fill |
| 阴影太黑 | 没有 fill light | 加 `subtle fill light from the opposite side` |
| 看起来太凶 | 过度使用 Split | 改用 Rembrandt 或加少量 fill |
| 塑料感 | 阴影边缘太锐利 | 加 `soft natural shadow falloff` |
| 多角度不一致 | 光源方向没固定 | 在角色概念阶段锁定 Key Light 方向 |
