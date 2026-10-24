# 竖屏光影与情绪控制 (Vertical Lighting & Emotion Control)

> 专为 9:16 竖屏画幅重构的光影与情绪控制系统。手机屏（OLED）显示特性完全不同，光影策略需要彻底调整。

---

## 一、手机屏显示特性（OLED）

### 1.1 OLED vs LCD 差异

| 特性 | LCD（电脑/电视） | OLED（手机） | 光影策略调整 |
|------|------------------|-------------|----------------|
| 黑色 | 深灰（背光常亮） | 纯黑（像素关闭） | 阴影可以更极端 |
| 对比度 | 1000:1 | 无限:1 | 高对比度可用 |
| 亮度 | 均匀 | 峰值亮度高 | 高光可以更刺眼 |
| 色彩 | 准确 | 饱和度高 | 饱和度可以更高 |
| 户外可见 | 差 | 好（峰值亮度） | 阴影可以死黑 |

### 1.2 竖屏光影重构原则

1. **阴影更极端**：OLED 可以显示纯黑，阴影可以"死黑"（无细节）
2. **高光更刺眼**：手机屏峰值亮度高，高光可以更夸张
3. **色彩更饱和**：手机屏色彩饱和度高，提示词要加 `high saturation`
4. **对比度更高**：横屏对比度 2.0-3.0，竖屏可以 3.0-5.0

---

## 二、竖屏光影关键词库

### 2.1 基础光影（竖屏重构）

| 光影 | 横屏 16:9 | 竖屏 9:16 |
|------|-----------|-----------|
| 侧光 | Raking Light | `vertical raking light, OLED optimized` |
| 底光 | Undereye Glow | `under-eye glow, vertical framing` |
| 顶光 | Top Light | `top light, shadow under eyebrows` |
| 背光 | Rim Light | `rim light, OLED deep black background` |
| 环境光 | Ambient Occlusion | `ambient light, mobile display optimized` |

### 2.2 竖屏专属光影

| 光影 | 关键词 | 效果 |
|------|--------|------|
| 垂直侧光 | `vertical raking light, from left/right` | 阴影从上到下，增强垂直感 |
| 顶部高光 | `top highlight, halo effect` | 头顶光晕，神圣感 |
| 底部反光 | `bottom reflection, wet floor` | 地面反光，增强空间感 |
| 屏幕光 | `screen glow, face lit by phone` | 手机屏照亮人脸（现代场景） |
| 竖条光斑 | `vertical light streaks, blinds` | 百叶窗效果，竖条光影 |

### 2.3 情绪-光影映射（竖屏版）

| 情绪 | 主光 | 阴影 | 色彩 | 手机屏优化 |
|------|------|------|------|-----------|
| 震惊 | 顶光（刺眼） | 死黑 | 冷白 | `high contrast, OLED optimized` |
| 愤怒 | 底光（从下往上） | 深蓝 | 橙红 | `high saturation, warm-cool conflict` |
| 悲伤 | 顶光（柔和） | 浅灰 | 冷蓝 | `low saturation, desaturated` |
| 恐惧 | 侧光（硬光） | 死黑 | 绿灰 | `high contrast, crushed shadows` |
| 喜悦 | 柔光（全向） | 无 | 暖金 | `high saturation, warm tones` |
| 厌恶 | 顶光（阴影在眼窝） | 深灰 | 黄绿 | `sickly green, desaturated` |

---

## 三、竖屏色彩心理学

### 3.1 色彩在手机屏上的表现

| 色彩 | 电脑屏 | 手机屏（OLED） | 提示词调整 |
|------|---------|----------------|-----------|
| 红色 | 鲜艳 | 更鲜艳（饱和度高） | `red, high saturation, OLED red` |
| 蓝色 | 准确 | 偏紫（OLED 特性） | `blue, pure blue, no purple shift` |
| 绿色 | 准确 | 更鲜艳 | `green, high saturation` |
| 黑色 | 深灰 | 纯黑（像素关闭） | `pure black, OLED black` |
| 白色 | 准确 | 刺眼（峰值亮度） | `white, reduce brightness` |

### 3.2 竖屏色彩策略

**高饱和度策略**（抖音/ TikTok 风格）：
```
high saturation, vibrant colors, OLED optimized,
mobile display optimized, eye-catching
```

**电影感策略**（即梦/ Shorts 风格）：
```
teal & orange, cinematic color, OLED optimized,
dark shadows, crushed black, high contrast
```

**写实策略**（纪录片/教育视频）：
```
natural colors, realistic, OLED optimized,
no oversaturation, accurate skin tones
```

### 3.3 色彩渐变（竖屏专属）

竖屏可以利用**垂直色彩渐变**：

```
顶部：天空蓝/天花板白
中部：人物肤色/服装色
底部：地面暗色/阴影
```

**提示词**：
```
vertical color gradient, sky blue at top, skin tone at middle,
dark ground at bottom, OLED optimized
```

---

## 四、竖屏情绪控制（AI 提示词）

### 4.1 微表情捕捉（竖屏版）

手机屏小，微表情需要**更夸张**：

| 微表情 | 横屏提示词 | 竖屏提示词 |
|--------|------------|------------|
| 瞳孔收缩 | `pupil constriction` | `pupil constriction, close-up, eye detail, 50fps` |
| 嘴角抽动 | `lip twitch` | `lip twitch, close-up, detailed mouth, high contrast` |
| 眉毛上扬 | `eyebrow raise` | `eyebrow raise, close-up, forehead detail` |
| 鼻翼扩张 | `nostril flare` | `nostril flare, close-up, nose detail` |
| 眼轮匝肌收缩 | `crow's feet` | `crow's feet, close-up, eye detail` |

### 4.2 情绪渐变（竖屏版）

竖屏情绪渐变需要**更快**（注意力短）：

**横屏**：3-5 秒完成情绪渐变
**竖屏**：1-2 秒完成情绪渐变

**提示词**：
```
fast emotion transition, from shock to anger in 1 second,
micro-expression capture, 50fps, high detail
```

### 4.3 情绪-镜头长度映射（竖屏）

| 情绪 | 镜头长度 | 原因 |
|------|---------|------|
| 震惊 | 0.5-1秒 | 短暂冲击 |
| 愤怒 | 1-2秒 | 需要看清单 |
| 悲伤 | 2-3秒 | 需要沉浸 |
| 恐惧 | 0.5-1秒 | 快速切换增强恐惧 |
| 喜悦 | 1-2秒 | 微笑需要时间 |
| 厌恶 | 1秒 | 快速表达 |

---

## 五、竖屏光影实战（分镜示例）

### 5.1 示例：王勃震惊（竖屏）

**横屏原版**：
```
王勃，震惊，侧光，冷蓝调，
--ar 16:9, cinematic lighting
```

**竖屏重构版**：
```
王勃，震惊，眼睛在画面上1/3处，
顶光（刺眼，从正上方打），
阴影死黑（OLED纯黑），
冷白高光（手机屏峰值亮度），
--ar 9:16, vertical framing, OLED optimized,
high contrast, crushed shadows,
--no horizontal composition, face cropped
```

### 5.2 示例：陆雪冷笑（竖屏）

**横屏原版**：
```
陆雪，冷笑，底光，暖金调，
--ar 16:9, chiaroscuro
```

**竖屏重构版**：
```
陆雪，冷笑，眼睛在1/3处，
底光（从下往上，阴影在眼窝），
暖金高光（对比冷蓝环境），
高饱和度（手机屏特性），
--ar 9:16, vertical framing, high saturation,
warm-cool conflict, OLED optimized,
--no horizontal composition
```

### 5.3 示例：裴子华傲慢（竖屏）

**横屏原版**：
```
裴子华，傲慢，顶光，暖金调，
--ar 16:9, authoritative lighting
```

**竖屏重构版**：
```
裴子华，傲慢，眼睛在1/3处，
顶光（光晕效果，神圣感），
深黑阴影（OLED纯黑，权力感），
暖金饱和（手机屏高饱和），
--ar 9:16, vertical framing, high saturation,
top light, halo effect, OLED optimized
```

---

## 六、竖屏光影设备模拟（AI 提示词）

### 6.1 电影摄影机（竖屏版）

**Arri Alexa 65（竖屏模式）**：
```
Arri Alexa 65, vertical framing, 9:16 aspect ratio,
Master Prime 35mm, vertical composition,
ProRes 4444, OLED optimized
```

**RED Monstro 8K（竖屏模式）**：
```
RED Monstro 8K, vertical framing, 9:16,
100fps slow motion, vertical composition,
REDColor4, OLED optimized
```

### 6.2 镜头（竖屏版）

| 镜头 | 横屏效果 | 竖屏效果 | 提示词 |
|------|---------|---------|---------|
| 35mm | 标准视角 | 竖幅标准视角 | `35mm, vertical framing, natural perspective` |
| 50mm | 人像镜头 | 竖幅人像 | `50mm, portrait, vertical framing` |
| 85mm | 长焦压缩 | 竖幅长焦 | `85mm, telephoto, vertical compression` |
| 14mm | 广角畸变 | 竖幅广角 | `14mm, wide angle, vertical distortion` |

### 6.3 胶片（竖屏版）

**Kodak Vision3 500T（竖屏模式）**：
```
Kodak Vision3 500T, vertical framing, 9:16,
grain, film texture, OLED optimized,
mobile display optimized
```

---

## 七、竖屏光影质量检查

### 7.1 生成前检查

- [ ] 是否指定了竖屏光影（`vertical raking light` / `top light`）？
- [ ] 是否包含 OLED 优化（`OLED optimized` / `mobile display optimized`）？
- [ ] 是否指定了高对比度（`high contrast` / `crushed shadows`）？
- [ ] 是否指定了高饱和度（`high saturation`，手机屏特性）？
- [ ] 是否包含 `--ar 9:16` 和 `vertical framing`？

### 7.2 生成后检查（手机屏上看）

- [ ] 阴影是否够深（OLED 纯黑）？
- [ ] 高光是否刺眼（手机屏峰值亮度）？
- [ ] 色彩是否饱和（手机屏特性）？
- [ ] 人脸是否过曝（手机屏自动提亮）？
- [ ] 暗部是否有细节（手机屏暗部提升）？

### 7.3 常见问题与修正

| 问题 | 原因 | 修正提示词 |
|------|------|-----------|
| 阴影太灰 | LCD 思维（以为灰阴影更真实） | `pure black, OLED black, crushed shadows` |
| 高光太暗 | 担心过曝 | `bright highlight, peak brightness, OLED optimized` |
| 色彩太暗 | 担心饱和度太高 | `high saturation, vibrant colors, OLED optimized` |
| 人脸过曝 | 手机屏自动提亮 | `reduce face brightness, control exposure` |
| 暗部死黑 | 过度使用 OLED 纯黑 | `lift shadows, recover dark details` |

---

## 八、竖屏光影提示词模板库

### 8.1 对话场景（竖屏）

```
{A}和{B}，对话场景，
{A}：{光线方向}，{色彩}，
{B}：{光线方向}，{色彩}，
对话光比 2:1，OLED 优化，
--ar 9:16, vertical framing
```

### 8.2 独白场景（竖屏）

```
{人物}，独白，眼睛在1/3处，
{主光}，{阴影处理}，
{色彩情绪}，高对比度，
OLED 优化，手机屏显示优化，
--ar 9:16, vertical framing
```

### 8.3 动作场景（竖屏）

```
{人物}，{动作}，
动态光影，光影跟随动作，
高对比度，阴影死黑，
OLED 优化，--ar 9:16
```

### 8.4 情绪特写（竖屏）

```
{人物}，{情绪}，
眼睛在画面中心，微表情捕捉，
{情绪-光影映射}，
高对比度，OLED 优化，
--ar 9:16, 50fps
```

---

## 九、竖屏色彩渐变（高级技巧）

### 9.1 时间流逝（竖屏专属）

竖屏可以利用**垂直方向**表示时间流逝：

```
顶部：早晨（金色）
中部：中午（白色）
底部：夜晚（深蓝）
```

**提示词**：
```
vertical time lapse, top: golden hour morning,
middle: high noon white, bottom: deep blue night,
--ar 9:16, vertical framing
```

### 9.2 情绪渐变（竖屏专属）

竖屏可以利用**垂直方向**表示情绪变化：

```
顶部：理智（冷蓝）
中部：冲突（紫红）
底部：崩溃（深红）
```

**提示词**：
```
vertical emotion gradient, top: calm blue,
middle: conflict purple-red, bottom: breakdown deep red,
--ar 9:16, vertical framing, OLED optimized
```

---

## 十、竖屏光影与平台适配

### 10.1 抖音/ TikTok（高对比+高饱和）

```
high contrast, OLED optimized,
high saturation, vibrant colors,
mobile display optimized, outdoor visible,
--ar 9:16
```

### 10.2 Instagram Reels（美学感+滤镜）

```
aesthetic, filtered look, cinematic color,
medium contrast, OLED optimized,
Instagram style, --ar 9:16
```

### 10.3 YouTube Shorts（真实感+自然色彩）

```
natural colors, realistic, OLED optimized,
medium contrast, no oversaturation,
YouTube style, --ar 9:16
```

### 10.4 即梦（电影感+写实）

```
cinematic color, teal & orange,
dark shadows, crushed black,
high contrast, OLED optimized,
--ar 9:16, vertical framing
```

---

*专为 9:16 竖屏画幅重构，适配 OLED 手机屏显示特性。*
