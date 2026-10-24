# CLAUDE.md - WorkBuddy 项目

## 项目概述
- **WorkBuddy**: AI 视频开发平台，腾讯内部工具
- **负责人**: Billy (王晓轩)，PM
- **目标**: 全链路 AI 影视制作，从剧本到成片

## 目录结构
```
/Volumes/YSAigc/WorkBuddy/
├── skills/          # 21 个 AI 影视制作技能
├── YYYY-MM-DD-.../  # 按日期命名的输出目录
```

## 技能清单 (skills/)

### 核心管线
```
viral-thread-story → tweet-storyboard → 9-16-movie-story
```

### 剧本/故事
| 技能 | 用途 |
|------|------|
| `viral-thread-story` | 病毒式推文故事生成 |
| `movie-story` | 电影故事/剧本编写 |
| `网络小说助手` | 网络小说辅助创作 |
| `9-16-movie-story` | 9:16 竖屏短片故事 |

### 分镜/视觉
| 技能 | 用途 |
|------|------|
| `tweet-storyboard` | 推文风格分镜 |
| `storyboard` | 标准分镜脚本 |
| `storyboard-table` | 分镜表格化输出 |
| `visual-frame` | 视觉框架/构图 |
| `video-prompt` | 视频生成提示词 |

### 摄影/镜头
| 技能 | 用途 |
|------|------|
| `camera-movement` | 运镜方案 |
| `focal-grid` | 焦段网格规划 |
| `multishot-cinematic` | 多镜头电影化 |

### 角色/资产
| 技能 | 用途 |
|------|------|
| `character-asset` | 角色资产生成 |
| `costume-accessories-extractor` | 服装配饰提取 |
| `makeup-hair-extractor` | 妆发提取 |

### 场景/道具
| 技能 | 用途 |
|------|------|
| `scene-asset` | 场景资产 |
| `set-art-extractor` | 布景美术提取 |
| `script-props-extractor` | 剧本道具提取 |

### 表演/渲染
| 技能 | 用途 |
|------|------|
| `performance-description` | 表演描述生成 |
| `runninghub` | 云端渲染调度 |

### 工具
| 技能 | 用途 |
|------|------|
| `tencent-docs` | 腾讯文档集成 |

## 分镜输出规范
- 输出要完整，不压缩内容
- 含确切脚本引用（原句）
- 有台词的 Shot 需单独输出视频提示词
- 视频提示词用英文，分镜描述用中文

## 常用命令
```bash
# 技能路径
SKILLS_DIR="/Volumes/YSAigc/WorkBuddy/skills"

# 核心管线
# 1. 生成推文故事
# 2. 生成推文分镜
# 3. 生成 9:16 竖屏分镜
```

## 短剧项目
- 大唐文圣 EP01
- 放学回家 9:16
- Hidden_in_Plain_Daylight EP1

## 参考文档
- AI真人剧生产流程报告: 流程标准化
- 短剧分镜工作站: `/Volumes/YSAigc/短剧分镜工作站/`
