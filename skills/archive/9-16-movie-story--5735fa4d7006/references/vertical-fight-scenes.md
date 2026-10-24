# 打斗场景设计（竖屏 9:16 版）

> **适用**：竖屏影视项目的打斗场景设计  
> **核心**：9:16 画幅下的打斗构图、竖屏动作设计、手机端优化

---

## 打斗场景基础（竖屏版）

### 横屏 vs 竖屏打斗场景

| 维度 | 横屏 16:9 | 竖屏 9:16 |
|------|------------|------------|
| **构图** | 左右布局（人物 A 左，人物 B 右） | 上下布局（人物 A 上，人物 B 下） |
| **运镜** | 左右摇/推拉 | 上下摇/推拉 |
| **动作方向** | 水平（左←→右） | 垂直（上←→下）或对角线 |
| **剪辑节奏** | 2-4 秒/镜 | 0.5-2 秒/镜（快切） |
| **视觉焦点** | 多人物 | 单人物（动作细节） |

---

## 竖屏打斗场景构图

### 1. 上下布局（推荐）
```
Vertical Layout (Top-Down):
- 人物 A 在画面上方（y=0.25）
- 人物 B 在画面下方（y=0.75）
- 动作方向：垂直（上←→下）
- 摄像机：稍微俯拍或仰拍
```

**优点**：
- 符合竖屏画幅
- 动作方向清晰
- 观众容易理解

**提示词关键词**：
```
vertical fight composition, top-down layout,
character A above, character B below,
vertical action direction, 9:16 frame,
dynamic motion, martial arts
```

### 2. 对角线布局（电影感）
```
Diagonal Layout:
- 人物 A 在左上（x=0.3, y=0.25）
- 人物 B 在右下（x=0.7, y=0.75）
- 动作方向：对角线（左上←→右下）
- 摄像机：斜角拍摄
```

**优点**：
- 电影感强
- 动作方向有张力
- 构图动态

**提示词关键词**：
```
diagonal fight composition, dynamic layout,
character A top-left, character B bottom-right,
diagonal action direction, 9:16 frame,
cinematic fighting, martial arts movie
```

### 3. 中心布局（特写）
```
Center Layout (Close-up):
- 人物 A 和 B 在画面中心（x=0.5, y=0.5）
- 动作方向：旋转或近身格斗
- 摄像机：中心推拉
```

**优点**：
- 强调动作细节
- 情绪强度高
- 观众沉浸感强

**提示词关键词**：
```
center fight composition, close-up action,
characters in center, rotating motion,
intense fighting, 9:16 frame,
extreme close-up, dynamic motion
```

---

## 竖屏打斗场景运镜

### 1. 垂直推拉（Vertical Push-Pull）
```
Vertical Push-Pull:
- 推：从全景推到特写（垂直方向）
- 拉：从特写拉到全景（垂直方向）
- 速度：快（0.5-1 秒）
- 电影感：强调动作细节
```

**提示词关键词**：
```
vertical push-in, vertical pull-out,
fast push-pull, dynamic motion,
9:16 frame, close-up action,
intense fighting, martial arts
```

### 2. 上下摇摄（Vertical Tilt）
```
Vertical Tilt:
- 仰：从下往上摇（人物 A 攻击人物 B）
- 俯：从上往下摇（人物 B 攻击人物 A）
- 速度：快（0.5-1 秒）
- 电影感：强调权力关系
```

**提示词关键词**：
```
vertical tilt, tilt up, tilt down,
fast tilt, dynamic motion,
9:16 frame, power dynamics,
fighting, martial arts
```

### 3. 手持晃动（Handheld Shake）
```
Handheld Shake:
- 模拟真实打斗的晃动感
- 速度：快（0.5-1 秒）
- 电影感：沉浸式，真实感
```

**提示词关键词**：
```
handheld camera, shaky camera,
realistic fighting, immersive,
9:16 frame, dynamic motion,
martial arts, intense action
```

---

## 竖屏打斗场景剪辑节奏

### 剪辑节奏表（竖屏版）
| 镜头类型 | 时长 | 说明 |
|---------|------|------|
| 全景（建立空间） | 1-2 秒 | 快速定场 |
| 中景（对话/对峙） | 1-2 秒 | 快切 |
| 特写（动作细节） | 0.5-1 秒 | 快切 |
| 插入镜（道具/血迹） | 0.5 秒 | 极快切 |
| 慢动作（高潮） | 2-3 秒 | 强调关键动作 |

**总原则**：单场打斗 10-30 镜，时长 30-60 秒

---

## 竖屏打斗场景提示词模板

### 模板 1：全景（建立空间）
```
Wide shot, two people facing each other,
ready to fight, tension in the air,
vertical composition, 9:16 frame,
dynamic posture, martial arts stance,
--ar 9:16 --style raw --stylize 100
```

### 模板 2：中景（对峙）
```
Medium shot, two people arguing,
about to fight, intense emotion,
vertical composition, 9:16 frame,
eyes at upper third, rule of thirds,
--ar 9:16 --style raw --stylize 150
```

### 模板 3：特写（动作细节）
```
Extreme close-up, fist punching,
dynamic motion, motion blur,
vertical composition, 9:16 frame,
intense action, martial arts,
--ar 9:16 --style raw --stylize 200
```

### 模板 4：慢动作（高潮）
```
Slow motion, character kicking,
dynamic motion, frozen moment,
vertical composition, 9:16 frame,
cinematic lighting, dramatic,
--ar 9:16 --style raw --stylize 250
```

---

## 竖屏打斗场景检查清单

### ✅ 必选要素
- [ ] 构图已选择（上下布局/对角线布局/中心布局）
- [ ] 动作方向已定义（垂直/对角线/旋转）
- [ ] 运镜已选择（垂直推拉/上下摇摄/手持晃动）
- [ ] 剪辑节奏已定义（0.5-2 秒/镜）
- [ ] 提示词已生成（含 `--ar 9:16`）
- [ ] 竖屏关键词已添加（`vertical composition, 9:16 frame`）

### ✅ 进阶优化
- [ ] 使用快切剪辑（0.5-1 秒/镜）
- [ ] 使用慢动作（2-3 秒，强调关键动作）
- [ ] 使用手持晃动（沉浸式，真实感）
- [ ] 使用动态构图（对角线/中心）
- [ ] 使用电影感光影（顶光/侧光/高对比）

---

## 示例：竖屏打斗场景分镜

### 示例：《大唐文圣》打斗场景（简化版）
```
SHOT 101 (全景):
- 构图：上下布局（王勃在上，刺客在下）
- 运镜：垂直拉出（从特写到全景）
- 时长：2 秒
- 提示词：Wide shot, two people facing each other...

SHOT 102 (中景):
- 构图：对角线布局（王勃左上，刺客右下）
- 运镜：手持晃动
- 时长：1 秒
- 提示词：Medium shot, two people fighting...

SHOT 103 (特写):
- 构图：中心布局（拳头特写）
- 运镜：垂直推入（强调动作细节）
- 时长：0.5 秒
- 提示词：Extreme close-up, fist punching...

SHOT 104 (慢动作):
- 构图：中心布局（王勃踢击）
- 运镜：慢动作
- 时长：3 秒
- 提示词：Slow motion, character kicking...
```

---

## 总结

竖屏打斗场景 = **横屏打斗场景** + **9:16 构图适配** + **快切剪辑**

**核心要点**：
1. 构图：上下布局/对角线布局/中心布局
2. 动作方向：垂直/对角线/旋转
3. 运镜：垂直推拉/上下摇摄/手持晃动
4. 剪辑节奏：0.5-2 秒/镜（快切）
5. 提示词含 `--ar 9:16`
