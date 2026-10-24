# Script Props Extractor

从影视剧剧本中提取所有道具信息，按场次和分镜整理，生成道具总表和连续性核查报告。

## 核心能力

| 模块 | 能力 |
|------|------|
| 道具提取 | 手持道具/场景道具/互动道具 — 位置/状态/材质/完整性 |
| 场次速查表 | 按场次汇总所有道具，标注首次出现/状态变化/消失 |
| 连续性核查 | 跨场次道具状态追踪，防止穿帮 |
| AI Prompt 片段 | 输出可直接嵌入 AI 生图工具的道具提示词 |
| 视频提示词 v2.0 | 兼容 movie-story「开场状态」+ 逐Shot格式，@道具标签 + 材质纹理/灯光反射/状态动态变化 |

## 与 movie-story 集成

本技能输出的提示词格式与 [movie-story](https://github.com/Billyui/movie_story) v2.0 统一规范完全一致，可无缝拼接到分镜脚本的视频提示词中。

## 安装

```bash
git clone git@github.com:Billyui/script-props-extractor.git ~/.workbuddy/skills/script-props-extractor
```

## 使用

在 WorkBuddy 对话中提供剧本文本，技能自动触发并输出道具分析报告。

## License

MIT

## Author

[Billyui](https://github.com/Billyui)
