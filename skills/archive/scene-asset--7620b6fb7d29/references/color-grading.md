# 调色风格速查表

## 七大调色风格

### 1. Teal & Orange（青橙对比）

- **提示词**：`teal shadows and warm skin highlights, complementary color contrast, Hollywood blockbusters style`
- **情绪**：大片感·冲突·戏剧性·视觉冲击
- **类型**：好莱坞大片·动作·戏剧
- **技术**：阴影推青色·肤色推暖橙·中间调保持
- **参考**：《疯狂的麦克斯》《变形金刚》《敦刻尔克》
- **注意**：易过度，肤色需保护不被染橙

### 2. Kodak Vision3 胶片模拟

- **提示词**：`Kodak Vision3 film stock emulation, warm grain, subtle halation, natural skin tones, organic color rendition`
- **情绪**：温暖·怀旧·有机·真实
- **类型**：剧情·文艺·怀旧·传记
- **技术**：暖色偏移·胶片颗粒·暗部偏绿·高光柔化(halation)
- **参考**：《月光男孩》《小妇人》《婚姻故事》
- **注意**：颗粒量需控制，过重损失细节

### 3. 冷峻现代

- **提示词**：`desaturated cold palette, high contrast blue-grey, minimal color, clinical modern aesthetic`
- **情绪**：冷静·疏离·压迫·科技感
- **类型**：科幻·惊悚·现代都市·犯罪
- **技术**：全片去饱和·中间调推蓝灰·高对比·冷色偏移
- **参考**：《机械姬》《她》《银翼杀手2049》
- **注意**：需保留肤色微暖，否则人脸变灰

### 4. 梦幻诗意

- **提示词**：`soft pastel color grading, gentle gradients, selective saturation boost on key elements, ethereal atmosphere`
- **情绪**：梦幻·柔软·怀旧·缥缈
- **类型**：爱情·回忆·梦幻·奇幻
- **技术**：低对比·粉彩色调·关键元素提饱和·柔焦
- **参考**：《爱乐之城》《大鱼》《千与千寻》
- **注意**：易过甜，需一个锚定色保持重力

### 5. 暗黑/赛博朋克

- **提示词**：`deep shadows with neon color accents, cyberpunk palette, high contrast, magenta and cyan highlights`
- **情绪**：危险·迷幻·反乌托邦·未来
- **类型**：科幻·反乌托邦·动作·犯罪
- **技术**：极深阴影·霓虹色点缀(洋红+青)·高对比·深黑
- **参考**：《银翼杀手》《攻壳机动队》《阿基拉》
- **注意**：霓虹色需有场景内光源依据

### 6. 低饱和纪实

- **提示词**：`natural desaturated tones, documentary color, minimal grading, true-to-life palette`
- **情绪**：真实·朴素·客观·生活感
- **类型**：纪实·文艺·生活·社会题材
- **技术**：最小调色·保持拍摄原始色调·轻微去饱和
- **参考**：《何以为家》《我不是药神》《四百击》
- **注意**：不是"不调色"，是"看不到调色痕迹"

### 7. 东方水墨

- **提示词**：`ink wash tones, muted earth palette, subtle warmth on skin only, minimal color, classical Chinese aesthetic`
- **情绪**：克制·留白·淡雅·意境
- **类型**：古装·武侠·东方美学·文人叙事
- **技术**：去饱和·大地色系·仅肤色微暖·墨色层次
- **参考**：《刺客聂隐娘》《影》《卧虎藏龙》
- **注意**：去饱和不等于黑白，需保留微弱色相区分

---

## 调色反向提示词（通用）

```
oversaturated, blown out highlights, plastic skin, unnatural color,
color shift between shots, inconsistent color grading, flat color,
no color depth, garish colors, neon oversaturation, HDR artifacts,
crushed blacks, clipped highlights, banding, posterization
```

---

## 场景→调色适配建议

| 场景类型 | 推荐调色 | 原因 |
|---------|---------|------|
| 现代都市·日景 | 低饱和纪实 / 冷峻现代 | 生活感/客观 |
| 现代都市·夜景 | Teal & Orange / 冷峻现代 | 霓虹+肤色 |
| 古装·宫廷 | 东方水墨 / Kodak Vision3 | 克制/厚重 |
| 古装·江湖 | 东方水墨 | 留白意境 |
| 科幻·未来 | 冷峻现代 / 暗黑赛博朋克 | 科技感 |
| 悬疑·犯罪 | 低调冷色 / Teal & Orange | 压迫感 |
| 爱情·温暖 | Kodak Vision3 / 梦幻诗意 | 有机/柔软 |
| 战争·史诗 | 低饱和纪实 / Kodak Vision3 | 真实感 |
| 喜剧·日常 | 高调暖色 / 低饱和纪实 | 轻松自然 |

---

## 跨场景调色一致性规则

1. **Look Book先行**：项目开始时锁定调色风格，全片遵守
2. **场景内微调**：同一Look Book下，允许场景间色温/对比度微调（如夜戏降低Key、暖戏提高饱和）
3. **情绪转折点**：色调可变，但必须有过渡（渐变3-5个镜头），不可跳切
4. **肤色保护**：无论什么调色，肤色必须保持可辨识的暖调（除刻意异化角色）
5. **闪回/梦境**：允许调色风格偏离（如：现实用冷峻现代，闪回用Kodak暖色），但需有明确的视觉边界
