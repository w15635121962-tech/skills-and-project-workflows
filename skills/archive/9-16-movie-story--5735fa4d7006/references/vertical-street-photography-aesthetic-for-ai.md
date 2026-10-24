# 街头摄影美学（AI 生成，竖屏 9:16 版）

> **适用**：竖屏影视项目的街头摄影美学 AI 生成  
> **核心**：9:16 画幅下的街头摄影美学、竖屏适配、手机端优化

---

## 街头摄影美学基础（竖屏版）

### 横屏 vs 竖屏街头摄影美学

| 维度 | 横屏 16:9 | 竖屏 9:16 |
|------|------------|------------|
| **构图** | 左右平衡 | 上下平衡 |
| **主体** | 多人物 | 单人物（人脸） |
| **光影** | 自然光 | 自然光（相同） |
| **质感** | 胶片感 | 胶片感（相同） |
| **提示词** | 任意 | 必须含 `--ar 9:16` |

---

## 竖屏街头摄影美学要素

### 1. 自然光（Natural Light）
```
Natural Light (Street Photography):
- 光源：窗户光/阳光/月光
- 强度：自然（30-70%）
- 阴影：柔和，无明显阴影
- 适用：日常、对话、平静
```

**提示词关键词**：
```
natural light, window light, soft directional,
vertical composition, 9:16 frame,
street photography aesthetic
```

### 2. 胶片感（Film Grain）
```
Film Grain (Street Photography):
- 胶片：35mm film, Kodak Vision3
- 颗粒：film grain, grainy texture
- 扫描：film scan, vertical film scan
- 适用：复古、怀旧、故事感
```

**提示词关键词**：
```
35mm film, Kodak Vision3, film grain,
vertical film scan, 9:16 frame,
street photography aesthetic, vintage
```

### 3. 故事感（Storytelling）
```
Storytelling (Street Photography):
- 主体：人物 + 环境
- 动作：自然，不摆拍
- 情绪：真实，有故事感
- 适用：日常、怀旧、故事感
```

**提示词关键词**：
```
candid shot, unposed, natural expression,
storytelling, street photography,
vertical composition, 9:16 frame
```

---

## 竖屏街头摄影美学提示词模板

### 模板 1：自然光（日常）
```
Medium shot, {character},
natural light, window light,
vertical composition, 9:16 frame,
street photography aesthetic,
candid shot, unposed,
--ar 9:16 --style raw --stylize 150
```

### 模板 2：胶片感（复古）
```
Medium shot, {character},
35mm film, Kodak Vision3, film grain,
vertical composition, 9:16 frame,
street photography aesthetic, vintage,
--ar 9:16 --style raw --stylize 100
```

### 模板 3：故事感（怀旧）
```
Medium shot, {character},
candid shot, unposed, natural expression,
storytelling, street photography,
vertical composition, 9:16 frame,
--ar 9:16 --style raw --stylize 120
```

---

## 竖屏街头摄影美学检查清单

### ✅ 必选要素
- [ ] 自然光已描述（natural light/window light）
- [ ] 胶片感已描述（35mm film/film grain）
- [ ] 故事感已描述（candid shot/storytelling）
- [ ] 竖屏关键词已添加（`vertical composition, 9:16 frame`）
- [ ] 提示词已生成（含 `--ar 9:16`）
- [ ] 负面提示词已添加（`--no staged, posed, artificial`）

### ✅ 进阶优化
- [ ] 使用自然光（natural light）
- [ ] 使用胶片感（35mm film, film grain）
- [ ] 使用故事感（candid shot, storytelling）
- [ ] 使用街头摄影美学（street photography aesthetic）
- [ ] 使用浅景深（shallow depth of field）

---

## 示例：竖屏街头摄影美学提示词

### 示例 1：自然光（日常）
```
Medium shot of young man, early 20s,
wearing dark blue round-collar robe,
natural light, window light,
vertical composition, 9:16 frame,
street photography aesthetic, candid shot,
--ar 9:16 --style raw --stylize 150
```

### 示例 2：胶片感（复古）
```
Medium shot of young woman, early 20s,
wearing apricot pink tight-sleeved top,
35mm film, Kodak Vision3, film grain,
vertical composition, 9:16 frame,
street photography aesthetic, vintage,
--ar 9:16 --style raw --stylize 100
```

### 示例 3：故事感（怀旧）
```
Medium shot of man in 40s,
wearing parallel-collar deep indigo robe,
candid shot, unposed, natural expression,
storytelling, street photography,
vertical composition, 9:16 frame,
--ar 9:16 --style raw --stylize 120
```

---

## 总结

竖屏街头摄影美学 = **横屏街头摄影美学** + **9:16 构图适配** + **故事感强化**

**核心差异**：
1. 必须加 `--ar 9:16`
2. 主体在中心稳定区（x:0.25-0.75, y:0.25-0.65）
3. 眼睛位置在画面上 1/3（y≈0.33）
4. 提示词必须含 `vertical composition, 9:16 frame`
5. 使用街头摄影美学（street photography aesthetic）
