# Set Art Extractor

从影视剧剧本中提取场景美术与置景信息，按场次整理空间布局、色调、陈设、灯光氛围等，生成场景总表和美术连续性核查报告。

## 核心能力

| 模块 | 能力 |
|------|------|
| 场景提取 | 空间布局/色调/材质/陈设/灯光 — 前景/中景/背景分层 |
| 场次速查表 | 按场次汇总所有场景的美术资产，支持连戏核查 |
| 美术连续性 | 跨场次空间一致性核查，含材质磨损/光感变化 |
| AI Prompt 片段 | 输出可直接嵌入 AI 生图工具的场景提示词 |
| 视频提示词 v2.0 | 兼容 movie-story「开场状态」+ 逐Shot格式，@空间/陈设标签 + 材质磨损/大气薄雾/混合色温 |

## 与 movie-story 集成

本技能输出的提示词格式与 [movie-story](https://github.com/Billyui/movie_story) v2.0 统一规范完全一致，可无缝拼接到分镜脚本的视频提示词中。

## 安装

```bash
git clone git@github.com:Billyui/set-art-extractor.git ~/.workbuddy/skills/set-art-extractor
```

## 使用

在 WorkBuddy 对话中提供剧本文本，技能自动触发并输出场景美术分析报告。

## License

MIT

## Author

[Billyui](https://github.com/Billyui)
