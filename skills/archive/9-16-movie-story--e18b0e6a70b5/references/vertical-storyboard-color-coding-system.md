# 分镜色彩编码系统（竖屏 9:16 版）

> **适用**：竖屏分镜脚本的色彩编码系统  
> **核心**：9:16 画幅下的色彩编码、竖屏适配、手机端优化

---

## 分镜色彩编码系统基础（竖屏版）

### 横屏 vs 竖屏分镜色彩编码

| 维度 | 横屏 16:9 | 竖屏 9:16 |
|------|------------|------------|
| **色彩编码** | 任意 | 避免顶部 20%（状态栏） |
| **色彩位置** | 任意 | 中心稳定区 |
| **色彩对比** | 任意 | 中心高对比 |
| **色彩情绪** | 任意 | 眼睛位置强调 |

---

## 竖屏分镜色彩编码系统

### 1. 情绪色彩编码
| 情绪 | 色彩 | 竖屏适配 |
|------|------|----------|
| **愤怒** | 深红 (#8B0000) | 避免顶部 20% |
| **悲伤** | 冷蓝 (#2A3B4A) | 中心稳定区 |
| **恐惧** | 深紫 (#4B0082) | 避免顶部 20% |
| **喜悦** | 暖黄 (#FFD700) | 中心稳定区 |
| **焦虑** | 冷绿 (#008B8B) | 避免顶部 20% |
| **平静** | 中性灰 (#808080) | 中心稳定区 |
| **权力** | 深蓝 (#00008B) | 避免顶部 20% |
| **脆弱** | 浅紫 (#D8BFD8) | 中心稳定区 |

### 2. 镜头类型色彩编码
| 镜头类型 | 色彩 | 竖屏适配 |
|---------|------|----------|
| **全景 (Establishing)** | 深蓝 (#00008B) | 避免顶部 20% |
| **中景 (Medium)** | 中性灰 (#808080) | 中心稳定区 |
| **特写 (Close-Up)** | 暖黄 (#FFD700) | 中心稳定区 |
| **极端特写 (Extreme Close-Up)** | 深红 (#8B0000) | 避免顶部 20% |
| **插入镜 (Insert)** | 冷绿 (#008B8B) | 避免顶部 20% |

### 3. 运镜类型色彩编码
| 运镜类型 | 色彩 | 竖屏适配 |
|---------|------|----------|
| **推 (Push-in)** | 暖黄 (#FFD700) | 中心稳定区 |
| **拉 (Pull-out)** | 深蓝 (#00008B) | 避免顶部 20% |
| **摇 (Tilt)** | 中性灰 (#808080) | 中心稳定区 |
| **手持 (Handheld)** | 冷绿 (#008B8B) | 避免顶部 20% |

---

## 竖屏分镜色彩编码应用

### 1. Markdown 分镜脚本色彩编码
````markdown
## SHOT 001 (愤怒，全景，推)
**情绪**：愤怒 (深红 #8B0000)
**镜头类型**：全景 (深蓝 #00008B)
**运镜类型**：推 (暖黄 #FFD700)

**提示词**：
```
Close-up of young man, early 20s,
angry expression, veins bulging,
top lighting, hard shadows, chiaroscuro,
vertical composition, eyes at upper third, 9:16 frame,
--ar 9:16 --style raw --stylize 150
```
````

### 2. HTML 分镜脚本色彩编码
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>竖屏分镜脚本 - 9:16</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            background: #0a0a0a;
            color: #e0e0e0;
            font-family: "PingFang SC", sans-serif;
        }
        .shot-card {
            width: 360px;
            margin: 20px auto;
            background: #1a1a1a;
            border: 1px solid #C8A03C;
            border-radius: 8px;
            overflow: hidden;
        }
        .emotion-angry { border-left: 5px solid #8B0000; }
        .emotion-sad { border-left: 5px solid #2A3B4A; }
        .emotion-fear { border-left: 5px solid #4B0082; }
        .emotion-joy { border-left: 5px solid #FFD700; }
        .emotion-anxiety { border-left: 5px solid #008B8B; }
        .emotion-peace { border-left: 5px solid #808080; }
        .emotion-power { border-left: 5px solid #00008B; }
        .emotion-vulnerable { border-left: 5px solid #D8BFD8; }
    </style>
</head>
<body>
    <div class="shot-card emotion-angry">
        <div class="shot-header">
            <div class="shot-number">SHOT 001</div>
        </div>
        <div class="shot-content">
            <div class="shot-prompt">...</div>
        </div>
    </div>
</body>
</html>
```

---

## 竖屏分镜色彩编码检查清单

### ✅ 必选要素
- [ ] 情绪色彩编码已定义（愤怒/悲伤/恐惧/喜悦/焦虑/平静/权力/脆弱）
- [ ] 镜头类型色彩编码已定义（全景/中景/特写/极端特写/插入镜）
- [ ] 运镜类型色彩编码已定义（推/拉/摇/手持）
- [ ] 竖屏适配已考虑（避免顶部/底部 20%）
- [ ] 中心稳定区高对比
- [ ] 眼睛位置已强调（强调色在眼睛位置）

### ✅ 进阶优化
- [ ] 使用三阶段色彩演变（冷→暖→对比）
- [ ] 使用竖屏专属色彩（避免顶部/底部 20%）
- [ ] 使用眼睛位置强调（强调色在眼睛位置）
- [ ] 使用中心稳定区高对比
- [ ] 使用电影感色彩梯度（color grading）

---

## 总结

竖屏分镜色彩编码系统 = **横屏分镜色彩编码系统** + **9:16 画幅适配** + **手机端优化**

**核心差异**：
1. 情绪色彩：避免顶部 20%（状态栏区域）
2. 镜头类型色彩：避免底部 20%（字幕区域）
3. 运镜类型色彩：中心稳定区（人脸/主体区域）
4. 眼睛位置强调（强调色在眼睛位置 y≈0.33）
5. 提示词必须含 `--ar 9:16`
