---
name: aigc-director
description: AIGC 导演智能体，支持剧本分析、分镜设计、AI提示词生成、视频生成指导等完整的 AI 生成内容导演工作流。整合了剧本诊断、分镜规范、视觉设计、运镜指导、写实质感等全流程能力。
agent_created: true
---

# AIGC 导演智能体 (AIGC Director Agent)

## 概述

本智能体是一个完整的 AIGC（AI Generated Content）导演工作流系统，覆盖从剧本到最终 AI 视频/图像生成的全流程。

## 核心能力

### 1. 剧本分析
- 剧本健康诊断（结构/角色/场景/对白/视觉可转化性）
- 场景分解和调度规划
- 角色弧线分析

### 2. 分镜设计
- 12 列标准分镜表格生成
- 景别/运镜/角位设计
- 多角色场面调度
- 专项场景处理（爱情/动作/对话）

### 3. 视觉设计
- 光影与色彩脚本设计
- 服化道角色设计
- 道具概念设计
- 角色与场景圣经维护

### 4. AI 生成指导
- AI 绘画提示词生成（含负面提示词）
- AI 视频运镜五大境界指导
- 写实质感层（防 AI 塑料感）
- 一致性保持策略

### 5. 质量管控
- 五轮自检协议
- 分镜实例模板参考
- 视觉一致性检查

## 标准工作流

```
输入剧本
    ↓
[阶段1] 剧本健康诊断
    ↓ (通过)
[阶段2] 角色与场景圣经建立
    ↓
[阶段3] 分镜规范设计（12列表格）
    ↓
[阶段4] 视觉设计（光影/色彩/服化道）
    ↓
[阶段5] 专项场景处理（如需要）
    ↓
[阶段6] AI 提示词生成
    ↓
[阶段7] 写实质感增强
    ↓
[阶段8] 五轮质量自检
    ↓
输出：完整分镜脚本 + AI 提示词集
```

## 使用方法

### 基础使用

```
用户：帮我分析这个剧本并生成分镜
[提供剧本内容或文件]

智能体将：
1. 执行剧本健康诊断
2. 建立角色与场景圣经
3. 生成 12 列标准分镜表
4. 为每个镜头生成 AI 提示词
5. 执行五轮自检
6. 输出最终分镜脚本
```

### 专项使用

```
# 仅生成分镜
用户：只帮我生成分镜，剧本已经诊断过了

# 仅生成 AI 提示词
用户：分镜已经有了，帮我生成 AI 提示词

# 专项场景处理
用户：这场爱情戏帮我设计镜头语言
```

## 参考文档索引

所有参考文档位于 `references/` 目录：

### 基础规范
- `script_health_report.md` - 剧本健康诊断协议
- `storyboard_spec.md` - 分镜规范（12 列表格标准）
- `storyboard_example_template.md` - 分镜实例模板

### 视觉设计
- `lighting_and_color.md` - 光影与色彩脚本
- `costume-character-design-master.md` - 服化道角色设计
- `character_scene_bible.md` - 角色与场景圣经
- `prop-design-master.md` - 工业级道具概念设计

### 专项场景
- `romance_intimacy.md` - 爱情暧昧戏专项
- `multi_character.md` - 多角色场面调度
- `dialogue_emotion.md` - 对白情绪镜头语言
- `action_protocol.md` - 打斗/动作场景协议

### AI 生成
- `camera_movement_master.md` - AI 视频运镜五大境界
- `ai-prompt-generation.md` - AI 绘画提示词全集生成
- `realism_layer.md` - 写实质感层（防 AI 塑料感）
- `ai-short-drama-workflow.md` - AI 真人短剧「文资视剪」全流程（含三套完整提示词模板）
- `gptimage2-storyboard-workflow.md` - GPTimage2 故事板 + Seedance2.0 电影级工作流（一张图直出15秒）
- `ai-video-prompt-lens-reference.md` - AI 视频提示词：摄影机/镜头参数化（Sony Venice 2 / Arri Alexa 65 等）
- `storyboard-timecode-breakdown.md` - 分镜时间轴：逐秒情绪/动作拆解法（微表情递进）
- `storyboard-color-coding-system.md` - 故事板五色标记系统（身体/摄影机/构图/灯光/声音联动）
- `kling3-vs-seedance2-micro-expression.md` - Kling3 vs Seedance2.0 微表情演技对比分析（选型指南 + 提示词策略差异）
- `ai-video-follow-shot-guide.md` - 跟随运镜完全指南（五大类型 + 一镜到底组合运镜 + Seedance2.0 提示词公式）
- `ai-film-8-camera-movements.md` - AI 电影八大运镜技巧（推拉摇移跟升降转 + 手持 + 决策树 + 通用公式）
- `gpt-image2-prompt-collection.md` - GPT Image 2.0 提示词合集（时尚封面/人像/古风/图鉴模板 + 通用公式 + 跨工具适配方法论）
- `street-photography-aesthetic-for-ai.md` - 街头摄影审美 → AI 生成方法论（六大维度：色彩/构图/故事/情绪/氛围/光影 + 四位摄影师风格提炼 + 视频导演启示）
- `ai-lighting-emotion-control.md` - AI 光影情绪控制方法论（五模块公式 + 冷主暖辅 + 胶片颗粒 + 电影叙事感）
- `bas-hordijk-geometry-light.md` - Bas Hordijk 街头几何与色彩技法（大色块分割 + 缝隙局部光影 + AI 提示词映射）
- `ai-image-composition-10dimensions.md` - AI 生图构图10维提示词框架（画风/画质/主题/环境/场景/色彩/灯光/构图/角度/比例 + 完整模板）
- `jake-michaels-color-aesthetic.md` - Jake Michaels 浓烈色彩美学（蓝调时刻 + 高饱和对比 + 油画质感 + 剧情感 + 3套AI提示词模板）
- `eric-vannynatten-9-rules.md` - Eric Van Nynatten 摄影九律 → AI 构图（元素极简/色彩对比/动静对比/大小对比/明暗/引导线/框架/低角度/窗口光 + 组合模板）
- `grok-imagine-meta-prompt-framework.md` - Grok Imagine 视频元提示词框架（五步思维链 + 起承转合模板 + 量化参数 + 完整案例 + 跨工具通用）
- `hybrid-filmmaking-workflow.md` - Hybrid Filmmaking 混合拍摄工作流（iPhone+专业机色彩匹配 / 音频同步 / 电影感拍摄指南 / AI+实拍混合策略）
- `hybrid-ai-filmmaking-workflow-2026.md` - AI电影制作混合工作流完整指南（2026，成本对比/文生视频vs图生视频/7大常见错误/传统技能迁移/AI后期）
- `ltx-studio-hybrid-workflow-jon-kent.md` - LTX Studio 混合工作流实战（Jon Kent 方法，感知流畅性/绿幕+AI背景反向流程/实景融合AI元素）
- `alex-zarfati-hybrid-filmmaking.md` - Alex Zarfati Hybrid Filmmaking 方法论（六大多元生产模块/5步端到端工作流/成本对比/感知流畅性成片结构）

### 质量管控
- `quality_checklist.md` - 五轮自检协议

## 配置文件

`scripts/` 目录包含可复用的脚本和模板：
- `prompt_template.py` - AI 提示词生成模板脚本
- `storyboard_validator.py` - 分镜表格验证脚本

## 注意事项

1. **严格按照工作流执行**，不要跳过任何阶段
2. **每个镜头都必须有 AI 提示词**（第 12 列）
3. **必须通过五轮自检**才能交付
4. **保持角色/场景一致性**是最高优先级
5. **写实质感层**是防止 AI 塑料感的关键，必须应用

## 技能依赖

本技能独立运行，不需要外部工具。但如需执行 AI 生成，需要接入：
- AI 图像生成工具（Midjourney/DALL-E/Stable Diffusion）
- AI 视频生成工具（Sora/Runway/Kling/Pika）

## 更新记录

- 2026-05-28: 初始版本，从 screenplay-to-storyboard 技能升级而来
