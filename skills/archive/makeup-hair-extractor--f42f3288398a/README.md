# Makeup & Hair Extractor

从影视剧剧本或参考图中提取妆发造型信息，按场次整理发型、妆容、发饰等，生成妆发档案和连续性核查报告。

## 核心能力

| 模块 | 能力 |
|------|------|
| 妆面提取 | 底妆/眼妆/唇妆/腮红/高光阴影 — 色彩/质地/光泽度 |
| 发型提取 | 发式/发色/发质/发饰 — 结构/纹理/蓬松度 |
| 场次速查表 | 按场次汇总所有角色的妆发状态，支持连戏核查 |
| 皮肤纹理专项 | 毛孔/明暗对照/自然血色 — 反塑料/反蜡质感 |
| AI Prompt 片段 | 输出可直接嵌入 AI 生图工具的妆发提示词 |
| 视频提示词 v2.0 | 兼容 movie-story「开场状态」+ 逐Shot格式，@妆发/造型标签 + 皮肤纹理/毛孔 |

## 与 movie-story 集成

本技能输出的提示词格式与 [movie-story](https://github.com/Billyui/movie_story) v2.0 统一规范完全一致，可无缝拼接到分镜脚本的视频提示词中。

## 安装

```bash
git clone git@github.com:Billyui/makeup-hair-extractor.git ~/.workbuddy/skills/makeup-hair-extractor
```

## 使用

在 WorkBuddy 对话中提供剧本文本或参考图，技能自动触发并输出妆发分析报告。

## License

MIT

## Author

[Billyui](https://github.com/Billyui)
