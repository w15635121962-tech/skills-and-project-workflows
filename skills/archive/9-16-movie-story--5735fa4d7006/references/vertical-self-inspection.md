# 竖屏自检协议 (Vertical Self-Inspection Protocol)

> 专为 9:16 竖屏画幅重构的自检协议。原版 16:9 自检协议直接用于竖屏会遗漏竖屏专属问题（安全区/平台适配/手机屏优化）。

---

## 一、竖屏自检协议（六轮重构版）

### 1.1 自检流程（竖屏版）

```
完成分镜脚本
    ↓
第一轮：剧本覆盖度检查
    ↓
第二轮：视觉一致性检查（竖屏专属）
    ↓
第三轮：镜头语法检查（竖屏重构）
    ↓
第四轮：AI 提示词质量检查（竖屏专属）
    ↓
第五轮：覆盖规划与空间坐标检查（竖屏重构）
    ↓
第六轮：整体验收（竖屏专属）
    ↓
输出自检报告 + 修复建议
```

### 1.2 自检报告格式（竖屏版）

```
# {项目名} EP{XX} 竖屏分镜自检报告

## 一、总分：{X}/60

## 二、六轮自检结果

### 第一轮：剧本覆盖度（{X}/10）
- ✅ 100% 覆盖剧本内容
- ✅ 镜头长度 1-3 秒
- ✅ 对白压缩 ≥50%
- ❌ 视觉叙事仅 60%（建议 ≥70%）
- ✅ 前 3 秒视觉冲击

**问题**：视觉叙事不足
**修复**：增加 {X} 个视觉叙事镜头

### 第二轮：视觉一致性（{X}/10）
- ✅ 眼睛在 1/3 处（全场景一致）
- ✅ 头顶留白 15%（全场景一致）
- ✅ 底部留空 20%（全场景一致）
- ❌ 人物垂直位置不一致（镜 005 王勃眼睛在中心）
- ✅ 构图避免纯水平

**问题**：镜 005 眼睛位置错误
**修复**：提示词改为 `eyes at upper 1/3`

### 第三轮：镜头语法（{X}/10）
...

### 第四轮：AI 提示词质量（{X}/10）
...

### 第五轮：Coverage & Spatial（{X}/10）
...

### 第六轮：整体验收（{X}/10）
...

## 三、修复建议清单（按优先级排序）

1. {问题1} → 修复建议 → 预计提升 {X.X} 分
2. {问题2} → 修复建议 → 预计提升 {X.X} 分
...

## 四、修复后预估总分：{新总分}/60
```

---

## 二、竖屏自检详细标准

### 2.1 第一轮：剧本覆盖度（10 分）

| 检查项 | 分值 | 标准 |
|--------|------|------|
| 100% 覆盖剧本 | 3分 | 无遗漏场景/对白 |
| 竖屏节奏重构 | 2分 | 镜头长度 1-3 秒（不是 3-5 秒） |
| 对白压缩 | 2分 | ≥50% 压缩 |
| 视觉叙事 | 2分 | ≥70% 靠画面（不是对白） |
| 竖屏开场 | 1分 | 前 3 秒视觉冲击 |

### 2.2 第二轮：视觉一致性（10 分，竖屏专属）

| 检查项 | 分值 | 标准 |
|--------|------|------|
| 眼睛位置 | 3分 | 全场景一致（都在 1/3 处） |
| 头顶留白 | 2分 | 全场景一致（15%） |
| 底部留空 | 2分 | 全场景一致（20% 留空） |
| 人物垂直位置 | 2分 | 上位者在上 1/3，下位者在下 1/3 |
| 构图 | 1分 | 避免纯水平构图 |

### 2.3 第三轮：镜头语法（10 分，竖屏重构）

| 检查项 | 分值 | 标准 |
|--------|------|------|
| 运镜垂直分量 | 3分 | 所有运镜有垂直分量（不是纯水平） |
| 覆盖镜头数量 | 2分 | ≥3 个（Master + 2x Single） |
| 转场 | 2分 | 以硬切为主（不是叠化/擦除） |
| 镜头长度 | 2分 | 1-3 秒（不是 3-5 秒） |
| 正反打 | 1分 | 避免（用单镜同框替代） |

### 2.4 第四轮：AI 提示词质量（10 分，竖屏专属）

| 检查项 | 分值 | 标准 |
|--------|------|------|
| `--ar 9:16` | 2分 | 全部包含 |
| `vertical framing` | 2分 | 全部包含 |
| 眼睛位置 | 2分 | 全部指定 `eyes at upper 1/3` |
| 头顶留白 | 1分 | 全部指定 `headroom 15%` |
| 竖屏负面词 | 2分 | 全部包含 `--no horizontal composition, face cropped` |
| 手机屏优化 | 1分 | 全部包含 `mobile display optimized` |

### 2.5 第五轮：Coverage & Spatial（10 分，竖屏重构）

| 检查项 | 分值 | 标准 |
|--------|------|------|
| 空间坐标标注 | 3分 | 每个镜头都标注 `[C1] ΔX/ΔY/ΔZ` |
| Master Axis C1 | 2分 | 全场景一致（斜线） |
| 180° 法则 | 2分 | 遵守（不越轴除非叙事需要） |
| 人物 Y 轴位置 | 3分 | 符合权力关系（上位者在上 1/3） |

### 2.6 第六轮：整体验收（10 分，竖屏专属）

| 检查项 | 分值 | 标准 |
|--------|------|------|
| 手机预览：眼睛位置 | 2分 | 一致 |
| 手机预览：底部 UI | 2分 | 不被遮挡 |
| 手机预览：人脸变形 | 2分 | 不变形 |
| 手机预览：色彩 | 2分 | 饱和（手机屏特性） |
| 完播率 | 2分 | 预计 ≥60%（前 3 秒视觉冲击） |

---

## 三、竖屏自检工具（自动化）

### 3.1 提示词检查脚本（Python）

```python
import json
import re

def check_vertical_prompt(prompt):
    """检查竖屏提示词是否合规"""
    issues = []
    
    # 检查 --ar 9:16
    if "--ar 9:16" not in prompt:
        issues.append("缺少 --ar 9:16")
    
    # 检查 vertical framing
    if "vertical framing" not in prompt.lower():
        issues.append("缺少 vertical framing")
    
    # 检查眼睛位置
    if "eyes at upper 1/3" not in prompt.lower():
        issues.append("缺少眼睛位置指定")
    
    # 检查头顶留白
    if "headroom 15%" not in prompt.lower():
        issues.append("缺少头顶留白指定")
    
    # 检查竖屏负面词
    negative_keywords = ["horizontal composition", "face cropped", "bottom frame cluttered"]
    for kw in negative_keywords:
        if kw not in prompt.lower():
            issues.append(f"缺少负面词: {kw}")
    
    # 检查手机屏优化
    if "mobile display optimized" not in prompt.lower():
        issues.append("缺少手机屏优化")
    
    return issues

# 使用示例
prompt = "Lu Xue, waist-up, eyes at upper 1/3, --ar 9:16, vertical framing"
issues = check_vertical_prompt(prompt)
if issues:
    print("问题：", issues)
else:
    print("✅ 提示词合规")
```

### 3.2 分镜表检查脚本（Python）

```python
import pandas as pd

def check_storyboard_vertical(csv_file):
    """检查竖屏分镜表是否合规"""
    df = pd.read_csv(csv_file)
    issues = []
    
    # 检查眼睛位置列
    if "眼睛位置" in df.columns:
        for idx, row in df.iterrows():
            if row["眼睛位置"] != "上 1/3 处":
                issues.append(f"镜 {row['镜号']}: 眼睛位置错误")
    
    # 检查底部留空列
    if "底部留空" in df.columns:
        for idx, row in df.iterrows():
            if row["底部留空"] != "20%":
                issues.append(f"镜 {row['镜号']}: 底部留空错误")
    
    # 检查提示词列
    if "AI 提示词" in df.columns:
        for idx, row in df.iterrows():
            prompt_issues = check_vertical_prompt(row["AI 提示词"])
            if prompt_issues:
                issues.append(f"镜 {row['镜号']}: {prompt_issues}")
    
    return issues

# 使用示例
issues = check_storyboard_vertical("分镜表_竖屏.csv")
if issues:
    for issue in issues:
        print(issue)
else:
    print("✅ 分镜表合规")
```

---

## 四、竖屏自检交付物

### 4.1 交付文件

| 文件 | 格式 | 内容 |
|------|------|------|
| `{项目名}_EP{XX}_自检报告_竖屏.pdf` | PDF | 完整自检报告 |
| `{项目名}_EP{XX}_自检表_竖屏.xlsx` | Excel | 可打印自检表 |
| `{项目名}_EP{XX}_提示词检查脚本_竖屏.py` | Python | 自动化检查脚本 |

### 4.2 自检报告 JSON 格式（竖屏）

```json
{
  "project": "大唐文圣",
  "episode": 1,
  "aspect_ratio": "9:16",
  "self_inspection": {
    "total_score": 58,
    "max_score": 60,
    "pass": true,
    "rounds": {
      "round_1": {"score": 10, "max_score": 10, "issues": []},
      "round_2": {"score": 10, "max_score": 10, "issues": []},
      "round_3": {"score": 10, "max_score": 10, "issues": []},
      "round_4": {"score": 9, "max_score": 10, "issues": ["镜 005 缺少 mobile display optimized"]},
      "round_5": {"score": 10, "max_score": 10, "issues": []},
      "round_6": {"score": 9, "max_score": 10, "issues": ["完播率预计 55%（建议 ≥60%）"]}
    },
    "fix_suggestions": [
      "镜 005 提示词加 mobile display optimized",
      "前 3 秒增加视觉冲击（提升完播率）"
    ]
  }
}
```

---

*专为 9:16 竖屏画幅重构，适配抖音/TikTok/Reels/Shorts/即梦等平台。*
