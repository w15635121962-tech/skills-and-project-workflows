# 竖屏 AI 视频模型对比 (Vertical AI Video Models Comparison)

> 专为 9:16 竖屏画幅重构的 AI 视频模型对比。原版 16:9 对比直接用于竖屏会导致画幅错误、提示词不适配、平台兼容问题。

---

## 一、主流 AI 视频模型（竖屏适配版）

### 1.1 模型对比表（竖屏版）

| 模型 | 开发方 | 竖屏支持 | 画幅设置 | 提示词语法 | 中文支持 | 推荐场景 |
|------|---------|-----------|-----------|-----------|---------|---------|
| **Seedance 2.0** | 即梦 | ✅ 原生 | 选择"竖屏" | `竖屏构图, --ar 9:16` | ✅ 优秀 | 短剧/对话 |
| **Kling 3** | 快手 | ✅ 原生 | `aspect_ratio: "9:16"` | 中文/英文 | ✅ 优秀 | 动作/特效 |
| **Runway Gen-3** | Runway | ✅ 支持 | Web 选 9:16 | 英文为主 | ⚠️ 一般 | 电影感 |
| **Pika 2.0** | Pika | ✅ 支持 | `--ar 9:16` | 英文为主 | ⚠️ 一般 | 特效/转场 |
| **Sora** | OpenAI | ✅ 支持 | 选择 9:16 | 英文 | ❌ 差 | 写实/物理 |
| **Veo 2** | Google | ✅ 支持 | `--aspect 9:16` | 英文 | ❌ 差 | 写实/Google生态 |

### 1.2 竖屏专属特性对比

| 特性 | Seedance 2.0 | Kling 3 | Runway Gen-3 | Pika 2.0 |
|------|----------------|---------|----------------|-------------|
| **竖屏运镜** | ✅ 支持 | ✅ 支持 | ✅ 支持 | ⚠️ 有限 |
| **眼睛位置锁定** | ✅ `眼睛在1/3处` | ✅ `subject_lock` | ⚠️ 需提示词 | ❌ 不支持 |
| **垂直构图** | ✅ `竖屏构图` | ✅ `vertical framing` | ✅ `vertical` | ⚠️ 需提示词 |
| **手机屏优化** | ✅ `OLED优化` | ✅ `mobile optimized` | ⚠️ 需提示词 | ⚠️ 需提示词 |
| **多模态参考** | ✅ 人物/场景 | ✅ 人物/场景 | ✅ 人物/场景 | ⚠️ 仅人物 |

---

## 二、竖屏提示词适配（各模型）

### 2.1 Seedance 2.0（即梦，竖屏最强）

**画幅设置**：Web 端 → "Seedance 2.0" → "画幅" → 选择"9:16（竖屏）"

**提示词模板**：
```
参考图中人物，
{动作}，眼睛在画面上1/3处，
{环境}，{光影}，
竖屏构图，--ar 9:16，
手机屏显示优化，高对比度
```

**负面提示词**（即梦输入框）：
```
横屏构图, 上下黑边, 人脸裁剪,
眼睛在画面底部, 头部出画,
画面底部杂乱, 水印, 文字
```

**多模态参考图规范**（竖屏版）：
1. 参考图**必须预先裁剪成 9:16**（不能传横屏图）
2. 上传后选择"人物保持"
3. 相似度调到 **0.7-0.8**（太高会失真）
4. 提示词加 `参考图中人物，竖屏构图，--ar 9:16`

---

### 2.2 Kling 3（快手，竖屏动作强）

**画幅设置**：API 参数 `aspect_ratio: "9:16"` 或 Web 端选择"竖屏"

**提示词模板**（JSON）：
```json
{
  "prompt": "{人物}, {动作}, vertical framing, 9:16, {光影}",
  "camera_movement": "vertical_push_in",
  "aspect_ratio": "9:16",
  "subject_lock": "eyes_at_1_3",
  "negative_prompt": "horizontal composition, face cropped"
}
```

**竖屏运镜参数**（Kling 3 专属）：
| 运镜 | 参数值 |
|------|---------|
| 垂直推进 | `"camera_movement": "vertical_push_in"` |
| 垂直拉远 | `"camera_movement": "vertical_pull_out"` |
| 上摇 | `"camera_movement": "tilt_up"` |
| 下摇 | `"camera_movement": "tilt_down"` |
| 斜向跟随 | `"camera_movement": "diagonal_follow"` |

---

### 2.3 Runway Gen-3（电影感，竖屏适配）

**画幅设置**：Web 端 → "Gen-3 Alpha" → "Aspect Ratio" → 选择"Portrait (9:16)"

**提示词模板**：
```
{SUBJECT}, {ACTION},
vertical composition, eyes at 1/3, 9:16 aspect ratio,
{LIGHTING}, cinematic, hyper-realistic,
--ar 9:16
```

**负面提示词**（Runway 输入框）：
```
horizontal composition, letterbox, face cropped,
eyes at bottom, bottom frame cluttered,
watermark, text, logo
```

**Motion Score**（竖屏版）：
- 对话场景：`Motion Score: 3-5`（稳定）
- 动作场景：`Motion Score: 5-7`（动态）
- ⚠️ 避免 `Motion Score: 8-10`（竖屏会抖动太强）

---

### 2.4 Pika 2.0（特效/转场，竖屏有限支持）

**画幅设置**：`--ar 9:16` 或 Web 端选择"Portrait"

**提示词模板**：
```
{SUBJECT}, {ACTION},
vertical framing, 9:16 aspect ratio,
{special effect: 粒子/光影/转场},
--ar 9:16
```

**竖屏限制**：
- ❌ 不支持眼睛位置锁定
- ❌ 不支持垂直运镜参数
- ⚠️ 需提示词强制指定 `eyes at upper 1/3`

---

### 2.5 Sora（OpenAI，写实物理，竖屏支持）

**画幅设置**：Web 端 → "Aspect Ratio" → 选择"9:16 (Portrait)"

**提示词模板**：
```
{SUBJECT}, {ACTION},
vertical framing, eyes at upper 1/3, 9:16 aspect ratio,
{PHYSICS: 流体/布料/光照},
hyper-realistic, 50fps,
--ar 9:16
```

**中文支持差**：建议用翻译工具转英文，或只用简单中文关键词。

---

## 三、竖屏模型选择决策树

### 3.1 决策树

```
开始
  ↓
是否需要"人物保持"？
  ├─ 是 → Seedance 2.0（即梦）
  └─ 否 ↓
是否需要"动作特效"？
  ├─ 是 → Kling 3
  └─ 否 ↓
是否需要"电影感"？
  ├─ 是 → Runway Gen-3
  └─ 否 ↓
是否需要"写实物理"？
  ├─ 是 → Sora
  └─ 否 → Pika 2.0（特效/转场）
```

### 3.2 场景推荐表（竖屏版）

| 场景 | 首选模型 | 备选模型 | 原因 |
|------|---------|---------|------|
| 对话场景 | Seedance 2.0 | Kling 3 | 人物保持+眼睛位置锁定 |
| 动作场景 | Kling 3 | Runway Gen-3 | 垂直运镜+动作流畅 |
| 电影感 | Runway Gen-3 | Seedance 2.0 | 胶片质感+光影 |
| 特效转场 | Pika 2.0 | Kling 3 | 粒子+光影特效 |
| 写实物理 | Sora | Runway Gen-3 | 流体+布料模拟 |
| 低成本 | Kling 3 | Seedance 2.0 | 免费额度+中文支持 |

---

## 四、竖屏生成质量对比

### 4.1 质量评分（竖屏版）

| 维度 | Seedance 2.0 | Kling 3 | Runway | Pika | Sora |
|------|----------------|---------|----------|-------|------|
| **人物一致性** | 9/10 | 8/10 | 7/10 | 6/10 | 8/10 |
| **眼睛位置正确** | 9/10 | 8/10 | 6/10 | 5/10 | 7/10 |
| **垂直构图** | 9/10 | 8/10 | 7/10 | 6/10 | 7/10 |
| **动作流畅度** | 8/10 | 9/10 | 8/10 | 7/10 | 9/10 |
| **光影质感** | 8/10 | 7/10 | 9/10 | 7/10 | 8/10 |
| **中文支持** | 10/10 | 9/10 | 5/10 | 5/10 | 3/10 |
| **手机屏优化** | 9/10 | 8/10 | 7/10 | 6/10 | 7/10 |
| **总分** | **62/70** | **57/70** | **49/70** | **42/70** | **49/70** |

### 4.2 竖屏专属问题对比

| 问题 | Seedance | Kling | Runway | Pika | Sora |
|------|-----------|--------|----------|-------|------|
| 眼睛位置错误 | 5% | 10% | 20% | 30% | 15% |
| 人脸出画 | 5% | 10% | 15% | 25% | 10% |
| 底部被 UI 遮挡 | 5% | 10% | 15% | 20% | 10% |
| 横屏构图残留 | 5% | 10% | 20% | 30% | 15% |
| 人脸变形 | 5% | 10% | 10% | 20% | 10% |

---

## 五、竖屏提示词跨模型迁移

### 5.1 迁移模板

**Seedance → Kling 3**：
```
# Seedance 提示词
参考图中人物，垂直推进镜头，眼睛在1/3处，--ar 9:16

# Kling 3 提示词（JSON）
{
  "prompt": "reference image character, vertical push-in, eyes at 1/3, --ar 9:16",
  "camera_movement": "vertical_push_in",
  "subject_lock": "eyes_at_1_3"
}
```

**Kling 3 → Runway**：
```
# Kling 3 提示词
{人物}, vertical push-in, eyes at 1/3, --ar 9:16

# Runway 提示词
{SUBJECT}, vertical push-in, eyes at upper 1/3, 9:16 aspect ratio,
--ar 9:16
```

### 5.2 跨模型负面提示词

| 模型 | 负面提示词格式 |
|------|----------------|
| Seedance | `避免：横屏构图, 上下黑边, 人脸裁剪` |
| Kling 3 | `"negative_prompt": "horizontal composition, face cropped"` |
| Runway | `Negative Prompt` 输入框：`horizontal composition, face cropped` |
| Pika | `--no horizontal composition, face cropped` |
| Sora | `avoid: horizontal composition, face cropped` |

---

## 六、竖屏模型组合策略

### 6.1 三模型组合（最佳实践）

```
人物设计 → Seedance 2.0（人物保持最强）
     ↓
分镜生成 → Kling 3（动作流畅）
     ↓
电影感调色 → Runway Gen-3（光影最强）
```

### 6.2 成本控制（竖屏版）

| 策略 | 说明 | 节省 |
|------|------|------|
| **免费额度优先** | Kling 3 每日免费 66 积分 | 100% |
| **Seedance 会员** | ¥30/月，无限次生成 | 80% |
| **Runway 按需** | 仅用于电影感镜头 | 50% |
| **Pika 特效** | 仅用于转场/特效镜头 | 70% |

---

## 七、竖屏模型质量检查

### 7.1 生成前检查

- [ ] 画幅是否设置为 9:16？
- [ ] 提示词是否包含 `--ar 9:16` 和 `vertical framing`？
- [ ] 是否指定了眼睛位置（`eyes at upper 1/3`）？
- [ ] 是否指定了底部留空（`bottom 20% empty`）？
- [ ] 负面提示词是否填写？

### 7.2 生成后检查（手机预览）

- [ ] 画幅是否为 9:16（无黑边）？
- [ ] 眼睛是否在 1/3 处？
- [ ] 人脸是否出画（顶部/底部）？
- [ ] 底部 20% 是否被 UI 遮挡？
- [ ] 在手机上播放是否清晰（OLED 优化）？

---

*专为 9:16 竖屏画幅重构，适配 Seedance/Kling/Runway/Pika/Sora 等模型。*
