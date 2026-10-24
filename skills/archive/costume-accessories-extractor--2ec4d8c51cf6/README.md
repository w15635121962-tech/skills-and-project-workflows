# Costume & Accessories Extractor

从影视剧参考图片中提取服装与配饰信息，生成结构化分析报告，包含场次速查表和可直接用于AI生图的Prompt片段。

## 核心能力

| 模块 | 能力 |
|------|------|
| 服装提取 | 上衣/下装/外套/连衣裙 — 款式/颜色/面料/纹理/垂坠感 |
| 配饰提取 | 珠宝/手表/眼镜/包袋/鞋履 — 材质/光泽/工艺细节 |
| 场次速查表 | 按场次汇总所有角色的服装配饰，支持连戏核查 |
| AI Prompt 片段 | 输出可直接嵌入 AI 生图工具（Midjourney/Flux/Seedance）的提示词 |
| 视频提示词 v2.0 | 兼容 movie-story「开场状态」+ 逐Shot格式，@服装/配饰标签 + 面料重量感/垂坠感 |

## 与 movie-story 集成

本技能输出的提示词格式与 [movie-story](https://github.com/Billyui/movie_story) v2.0 统一规范完全一致，可无缝拼接到分镜脚本的视频提示词中。

## 安装

```bash
git clone git@github.com:Billyui/costume-accessories-extractor.git ~/.workbuddy/skills/costume-accessories-extractor
```

## 使用

在 WorkBuddy 对话中上传角色剧照或参考图，技能自动触发并输出服装配饰分析报告。

## License

MIT

## Author

[Billyui](https://github.com/Billyui)
