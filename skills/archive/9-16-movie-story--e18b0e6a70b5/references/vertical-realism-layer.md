# 写实主义质感层（竖屏 9:16 版）

> **适用**：竖屏影视项目的写实主义质感层设计  
> **核心**：9:16 画幅下的写实主义质感、竖屏适配、手机端优化

---

## 写实主义质感层基础（竖屏版）

### 横屏 vs 竖屏写实主义质感层

| 维度 | 横屏 16:9 | 竖屏 9:16 |
|------|------------|------------|
| **皮肤纹理** | 可见 | 可见（相同） |
| **光影** | 自然 | 自然（相同） |
| **镜头** | 85mm, f/1.8 | 85mm, f/1.8（相同） |
| **胶片** | 35mm | 35mm（相同） |
| **提示词** | 任意 | 必须含 `--ar 9:16` |

---

## 竖屏写实主义质感层

### 1. 皮肤纹理（Skin Texture）
```
Skin Texture (Photorealism):
- 皮肤纹理可见（skin texture visible）
- 毛孔可见（pores）
- 自然皮肤瑕疵（natural skin imperfections）
- 竖屏适配：近距离特写，9:16 画幅
```

**提示词关键词**：
```
skin texture visible, pores, natural skin imperfections,
vertical close-up, 9:16 frame,
realistic skin, unretouched
```

### 2. 光影质感（Lighting Texture）
```
Lighting Texture (Photorealism):
- 柔光（soft top lighting）
- 自然光（natural light）
- 窗户光（window light）
- 竖屏适配：单光源，垂直方向
```

**提示词关键词**：
```
soft top lighting, natural light, window light,
vertical frame lighting, mobile cinematography lighting,
shallow depth of field, bokeh, background blur
```

### 3. 镜头质感（Camera Texture）
```
Camera Texture (Photorealism):
- 85mm 人像镜头（85mm portrait lens）
- 大光圈（f/1.8）
- Arri Alexa 65（Arri Alexa 65）
- Cooke Anamorphic（Cooke Anamorphic）
- 竖屏适配：9:16 画幅
```

**提示词关键词**：
```
85mm portrait lens, f/1.8, Arri Alexa 65,
Cooke Anamorphic, vertical mobile master,
smartphone footage, TikTok aesthetic, Reels style
```

### 4. 胶片质感（Film Texture）
```
Film Texture (Photorealism):
- 胶片颗粒（film grain）
- 35mm 胶片（35mm film）
- Kodak Vision3（Kodak Vision3）
- 竖屏适配：9:16 画幅
```

**提示词关键词**：
```
film grain, 35mm film, Kodak Vision3,
vertical film scan, mobile film aesthetic
```

---

## 竖屏写实主义质感层提示词模板

### 模板 1：皮肤纹理（特写）
```
Extreme close-up of {character}'s face,
skin texture visible, pores, natural skin imperfections,
vertical composition, 9:16 frame,
eyes at upper third, intense gaze,
85mm portrait lens, f/1.8,
shallow depth of field, bokeh background,
--ar 9:16 --style raw --stylize 200
```

### 模板 2：光影质感（中景）
```
Medium shot of {character},
soft top lighting, natural light, window light,
vertical frame lighting, mobile cinematography,
shallow depth of field, bokeh, background blur,
vertical composition, 9:16 frame,
--ar 9:16 --style raw --stylize 150
```

### 模板 3：镜头质感（全身）
```
Full body shot of {character},
85mm portrait lens, f/1.8,
Arri Alexa 65, Cooke Anamorphic,
vertical mobile master, smartphone footage,
vertical composition, 9:16 frame,
--ar 9:16 --style raw --stylize 100
```

### 模板 4：胶片质感（定场）
```
Establishing shot, {location},
film grain, 35mm film, Kodak Vision3,
vertical film scan, mobile film aesthetic,
vertical composition, 9:16 frame,
--ar 9:16 --style raw --stylize 80
```

---

## 竖屏写实主义质感层检查清单

### ✅ 必选要素
- [ ] 皮肤纹理已描述（skin texture visible, pores）
- [ ] 光影质感已描述（soft top lighting, natural light）
- [ ] 镜头质感已描述（85mm portrait lens, f/1.8）
- [ ] 胶片质感已描述（film grain, 35mm film）
- [ ] 竖屏关键词已添加（`vertical composition, 9:16 frame`）
- [ ] 提示词已生成（含 `--ar 9:16`）

### ✅ 进阶优化
- [ ] 使用 Arri Alexa 65 镜头描述
- [ ] 使用 Cooke Anamorphic 镜头描述
- [ ] 使用 85mm 人像镜头
- [ ] 使用 f/1.8 大光圈
- [ ] 使用胶片颗粒（film grain/35mm）

---

## 总结

竖屏写实主义质感层 = **横屏写实主义质感层** + **9:16 画幅适配** + **手机端优化**

**核心差异**：
1. 皮肤纹理：近距离特写，9:16 画幅
2. 光影质感：单光源，垂直方向
3. 镜头质感：9:16 画幅
4. 胶片质感：9:16 画幅
5. 提示词必须含 `--ar 9:16`
