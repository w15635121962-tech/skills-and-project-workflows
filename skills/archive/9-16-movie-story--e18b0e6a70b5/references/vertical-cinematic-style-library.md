# 电影风格库（竖屏 9:16 版）

> **适用**：竖屏影视项目的电影风格参考  
> **核心**：9:16 画幅下的电影风格、竖屏构图、手机端优化

---

## 电影风格分类（竖屏版）

### 1. 黑色电影 (Film Noir)
```
风格特征：
- 高对比，明暗强烈
- 阴影浓厚，神秘感
- 竖屏适配：单光源（顶部/底部），强调垂直阴影

提示词关键词：
film noir, high contrast, chiaroscuro,
vertical frame, 9:16, deep shadows,
single light source, mysterious
```

### 2. 新黑色电影 (Neo-Noir)
```
风格特征：
- 现代感，色彩丰富
- 阴影浓厚，但色彩鲜艳
- 竖屏适配：霓虹灯/LED 光源，垂直光带

提示词关键词：
neo-noir, modern film noir,
vertical frame, 9:16, neon lights,
colrful shadows, cinematic
```

### 3. 复古电影 (Vintage)
```
风格特征：
- 暖色调，胶片感
- 颗粒感，怀旧感
- 竖屏适配：4:3 裁切至 9:16，保留胶片颗粒

提示词关键词：
vintage film, 35mm film grain,
warm tones, nostalgic,
vertical frame, 9:16, film scan
```

### 4. 现代电影 (Contemporary)
```
风格特征：
- 自然光，真实感
- 浅景深，背景虚化
- 竖屏适配：手机拍摄感，竖屏构图

提示词关键词：
contemporary film, natural light,
shallow depth of field, bokeh,
vertical frame, 9:16, realistic
```

### 5. 史诗电影 (Epic)
```
风格特征：
- 大场面，广角
- 金色/暖色调
- 竖屏适配：满屏构图，主体占满画面

提示词关键词：
epic film, wide shot, grand scale,
golden hour, warm tones,
vertical frame, 9:16, cinematic
```

---

## 竖屏电影风格提示词模板

### 模板 1：黑色电影 (Film Noir)
```
{Subject}, film noir style,
high contrast, chiaroscuro,
vertical composition, 9:16 frame,
deep shadows, mysterious,
single light source, dramatic,
--ar 9:16 --style raw --stylize 250
```

### 模板 2：新黑色电影 (Neo-Noir)
```
{Subject}, neo-noir style,
modern film noir, neon lights,
vertical composition, 9:16 frame,
colrful shadows, cinematic,
--ar 9:16 --style raw --stylize 200
```

### 模板 3：复古电影 (Vintage)
```
{Subject}, vintage film style,
35mm film grain, warm tones,
vertical composition, 9:16 frame,
nostalgic, film scan,
--ar 9:16 --style raw --stylize 150
```

### 模板 4：现代电影 (Contemporary)
```
{Subject}, contemporary film style,
natural light, shallow depth of field,
vertical composition, 9:16 frame,
realistic, cinematic,
--ar 9:16 --style raw --stylize 100
```

### 模板 5：史诗电影 (Epic)
```
{Subject}, epic film style,
wide shot, grand scale,
golden hour, warm tones,
vertical composition, 9:16 frame,
cinematic,
--ar 9:16 --style raw --stylize 50
```

---

## 竖屏电影风格检查清单

### ✅ 必选要素
- [ ] 电影风格已选择（黑色/新黑色/复古/现代/史诗）
- [ ] 风格关键词已添加（film noir/neo-noir/vintage/contemporary/epic）
- [ ] 竖屏关键词已添加（`vertical composition, 9:16 frame`）
- [ ] 光影方案已匹配（高对比/霓虹/胶片/自然光/金色）
- [ ] 色彩方案已匹配（黑白/彩色/暖色/自然/金色）
- [ ] 提示词已生成（含 `--ar 9:16`）

### ✅ 进阶优化
- [ ] 使用胶片颗粒（film grain/35mm）
- [ ] 使用浅景深（shallow depth of field）
- [ ] 使用单光源（single light source）
- [ ] 使用高对比（high contrast）
- [ ] 使用色彩鲜艳（colorful shadows）

---

## 示例：竖屏电影风格提示词

### 示例 1：黑色电影 (Film Noir) - 王勃
```
Close-up of young man, early 20s,
film noir style, high contrast, chiaroscuro,
vertical composition, 9:16 frame,
deep shadows, mysterious,
single light source, dramatic,
--ar 9:16 --style raw --stylize 250
```

### 示例 2：新黑色电影 (Neo-Noir) - 陆雪
```
Medium shot of young woman, early 20s,
neo-noir style, modern film noir,
neon lights, colorful shadows,
vertical composition, 9:16 frame,
cinematic,
--ar 9:16 --style raw --stylize 200
```

### 示例 3：复古电影 (Vintage) - 裴子华
```
Full body shot of man in 40s,
vintage film style, 35mm film grain,
warm tones, nostalgic,
vertical composition, 9:16 frame,
film scan,
--ar 9:16 --style raw --stylize 150
```

---

## 总结

竖屏电影风格 = **横屏电影风格** + **9:16 构图适配** + **手机端优化**

**核心差异**：
1. 风格关键词加 `vertical composition, 9:16 frame`
2. 光影方案适配竖屏（单光源/垂直阴影）
3. 色彩方案适配竖屏（避免顶部/底部高饱和色）
4. 提示词必须含 `--ar 9:16`
