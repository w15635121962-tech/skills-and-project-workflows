# AI工具套件 (AI Tools Suite)

自动化的AI工具配置脚本集合，用于AI真人剧生产流程。

## 📦 已完成模块 (100%)

### 1. 核心API模块 (`core/`)

- ✅ `runninghub_api.py` - RunningHub API 客户端 (文本生成图片、图生图、局部重绘、放大)
- ✅ `midjourney_bot.py` - Midjourney Discord Bot 自动化 (通过Discord Bot API调用)
- ✅ `pika_api.py` - Pika 2.0 API 客户端 (文本/图片生成视频、运动控制)
- ✅ `runway_api.py` - Runway Gen-3 API 客户端 (文本/图片生成视频、延长视频)

### 2. 功能模块 (`modules/`)

- ✅ `prompt_manager.py` - 提示词库管理 (渲染、搜索、添加、导入/导出)
- ✅ `batch_generator.py` - 批量生成 (角色、场景、提示词列表)
- ✅ `asset_organizer.py` - 资产整理 (分类、复制/移动、分析、清理)
- ✅ `quality_checker.py` - 质量检查 (面部/手部检测、批量检查、报告)

### 3. 工作流模块 (`workflows/`)

- ✅ `character_generation.py` - 角色生成工作流 (多视角、多表情、质量检查、放大)
- ✅ `scene_generation.py` - 场景生成工作流 (多变化、质量检查、放大)
- ✅ `video_generation.py` - 视频生成工作流 (文本/图片生成视频、延长视频、多工具)

### 4. 命令行脚本 (`scripts/`)

- ✅ `generate_character.py` - 生成角色 (命令行界面)
- ✅ `generate_scene.py` - 生成场景 (命令行界面)
- ✅ `batch_process.py` - 批量处理 (配置文件或命令行参数)
- ✅ `organize_assets.py` - 整理资产 (分析、分类、复制/移动)

### 5. 配置文件 (`config/`)

- ✅ `.env.example` - 环境变量模板
- ✅ `runninghub_config.json` - RunningHub 配置
- ✅ `midjourney_config.json` - Midjourney 配置
- ✅ `prompt_library.json` - 提示词库

### 6. 提示词模板 (`templates/`)

- ✅ `character_template.txt` - 角色提示词模板 (特征、服装、表情、视角描述)
- ✅ `scene_template.txt` - 场景提示词模板 (室内/室外、照明、氛围、天气)
- ✅ `negative_template.txt` - 负面提示词模板 (通用、角色、场景、视频)
- ✅ `video_template.txt` - 视频提示词模板 (镜头类型、摄像机运动、动作描述)

### 7. 文档 (`docs/`)

- ✅ `USER_GUIDE.md` - 详细使用指南 (安装、配置、命令行、Python API、工作流、常见问题)
- ✅ `QUICKSTART.md` - 快速开始指南 (安装、第一个角色/场景、批量生成)

### 8. 示例 (`examples/`)

- ✅ `example1_generate_character.py` - 生成单个角色
- ✅ `example2_generate_scene.py` - 生成单个场景
- ✅ `example3_batch_generate.py` - 批量生成角色和场景
- ✅ `example4_prompt_management.py` - 提示词管理
- ✅ `example5_quality_check.py` - 质量检查
- ✅ `example6_organize_assets.py` - 资产整理
- ✅ `example7_video_generation.py` - 视频生成 (需要API Key)

### 9. 其他文件

- ✅ `requirements.txt` - Python 依赖列表
- ✅ `test_imports.py` - 模块导入测试脚本
- ✅ `__init__.py` - 各个包的初始化文件

## 🚀 快速开始

### 1. 安装依赖

```bash
cd ai_tools_suite
pip install -r requirements.txt
```

### 2. 配置API密钥

复制 `.env.example` 到 `.env` 并填入您的API密钥:

```bash
cp config/.env.example config/.env
```

编辑 `config/.env`:

```env
RUNNINGHUB_API_KEY=your_runninghub_api_key_here
RUNNINGHUB_API_SECRET=your_runninghub_api_secret_here

# 可选 (用于视频生成)
RUNWAY_API_KEY=your_runway_api_key_here
PIKA_API_KEY=your_pika_api_key_here
MIDJOURNEY_API_KEY=your_midjourney_api_key_here
```

### 3. 测试模块导入

```bash
python test_imports.py
```

### 4. 使用

#### 生成角色

```bash
python scripts/generate_character.py \
  --character Bella \
  --views front side back \
  --expressions neutral smile \
  --output-dir outputs/characters
```

#### 生成场景

```bash
python scripts/generate_scene.py \
  --scene Hospital_Corridor \
  --variations 3 \
  --output-dir outputs/scenes
```

#### 批量生成

```bash
# 生成配置文件模板
python scripts/batch_process.py --generate-template batch_config.json

# 编辑 batch_config.json，然后运行
python scripts/batch_process.py --config batch_config.json
```

#### 整理资产

```bash
python scripts/organize_assets.py \
  --input-dir outputs \
  --output-dir outputs/organized \
  --mode copy
```

## 📚 详细文档

- **快速开始**: `docs/QUICKSTART.md`
- **使用指南**: `docs/USER_GUIDE.md`
- **提示词模板**: `templates/` 目录
- **API文档**: 查看各模块的 docstring
- **使用示例**: `examples/` 目录

## 🔧 配置说明

### RunningHub 配置 (`config/runninghub_config.json`)

```json
{
  "model": "SDXL 1.0",
  "sampler": "DPM++ 2M Karras",
  "steps": 30,
  "cfg_scale": 7.5,
  "width": 512,
  "height": 768,
  "batch_size": 1,
  "upscale_factor": 2.0
}
```

### 提示词库 (`config/prompt_library.json`)

包含:
- **角色提示词** (characters): Bella, Luca, Anna, Marco
- **场景提示词** (scenes): Hospital_Corridor, Party_Venue
- **道具提示词** (props): Luggage
- **负面提示词** (negative_prompts): general, character, scene, video

使用 Jinja2 风格的模板语法: `{{ variable }}`

**示例:**

```json
{
  "characters": {
    "Bella": {
      "base": "(portrait of Bella, beautiful female, 28 years old, ...)",
      "variants": {
        "elegant": "elegant blue dress, pearl necklace, diamond earrings"
      }
    }
  }
}
```

## 💡 核心功能

### 1. 角色生成

- 多视角 (front, side, back, three_quarter)
- 多表情 (neutral, smile, serious, angry, sad, surprised)
- 多服装变体
- 自动质量检查 (面部/手部检测)
- 自动放大 (2x)

### 2. 场景生成

- 多变化 (不同照明、氛围、时间)
- 室内/室外场景
- 自动质量检查
- 自动放大

### 3. 视频生成

- 文本生成视频 (Runway Gen-3, Pika 2.0)
- 图片生成视频
- 运动强度控制
- 摄像机运动控制
- 延长视频

### 4. 批量生成

- 批量生成角色 (多角色、多视角、多表情)
- 批量生成场景 (多场景、多变化)
- 配置文件驱动
- 结果统计和保存

### 5. 提示词管理

- 提示词库 (JSON 格式)
- 模板渲染 (Jinja2 风格)
- 搜索提示词
- 添加/更新/删除提示词
- 导入/导出提示词库

### 6. 质量检查

- 面部检测
- 手部检测
- 图像模糊检测
- 批量检查
- 质量报告

### 7. 资产整理

- 自动分类 (角色/场景/道具/视频)
- 复制/移动模式
- 重复文件检测
- 目录分析
- 空目录清理

## 📊 项目状态

- ✅ 核心API模块: 100% 完成 (4/4)
- ✅ 功能模块: 100% 完成 (4/4)
- ✅ 工作流模块: 100% 完成 (3/3)
- ✅ 命令行脚本: 100% 完成 (4/4)
- ✅ 配置文件: 100% 完成 (4/4)
- ✅ 提示词模板: 100% 完成 (4/4)
- ✅ 文档: 100% 完成 (2/2)
- ✅ 使用示例: 100% 完成 (7/7)
- ✅ 测试脚本: 100% 完成 (1/1)

**总体进度: 100% 完成! 🎉**

## 🎯 已完成的任务

1. ✅ 实现核心API模块 (RunningHub, Midjourney, Runway, Pika)
2. ✅ 实现功能模块 (提示词管理、批量生成、资产整理、质量检查)
3. ✅ 实现工作流模块 (角色、场景、视频生成)
4. ✅ 创建命令行脚本 (generate_character, generate_scene, batch_process, organize_assets)
5. ✅ 编写详细文档 (USER_GUIDE.md, QUICKSTART.md)
6. ✅ 创建使用示例 (examples/)
7. ✅ 创建提示词模板 (templates/)
8. ✅ 创建配置文件 (config/)
9. ✅ 创建测试脚本 (test_imports.py)

## 📝 更新日志

### 2026-05-30
- ✅ 完成所有模块 (100%)
- ✅ 创建使用示例 (examples/)
- ✅ 编写详细文档 (USER_GUIDE.md, QUICKSTART.md)
- ✅ 创建测试脚本 (test_imports.py)
- ✅ 完成命令行脚本 (scripts/)
- ✅ 完成角色生成工作流 (workflows/character_generation.py)

### 2026-05-27
- ✅ 创建项目结构
- ✅ 实现核心API模块 (RunningHub, Midjourney, Runway, Pika)
- ✅ 实现功能模块 (提示词管理、批量生成、资产整理、质量检查)
- ✅ 实现场景和视频生成工作流
- ✅ 创建配置文件和提示词模板

## 📞 联系与支持

如有问题或建议，请提交 Issue 或联系开发团队。

---

## 📁 目录结构

```
ai_tools_suite/
├── core/                       # 核心API模块
│   ├── __init__.py
│   ├── runninghub_api.py       # RunningHub API
│   ├── midjourney_bot.py      # Midjourney Bot
│   ├── runway_api.py           # Runway API
│   └── pika_api.py            # Pika API
├── modules/                    # 功能模块
│   ├── __init__.py
│   ├── prompt_manager.py       # 提示词管理
│   ├── batch_generator.py      # 批量生成
│   ├── asset_organizer.py      # 资产整理
│   └── quality_checker.py     # 质量检查
├── workflows/                  # 工作流模块
│   ├── __init__.py
│   ├── character_generation.py # 角色生成工作流
│   ├── scene_generation.py     # 场景生成工作流
│   └── video_generation.py    # 视频生成工作流
├── scripts/                    # 命令行脚本
│   ├── __init__.py
│   ├── generate_character.py   # 生成角色
│   ├── generate_scene.py       # 生成场景
│   ├── batch_process.py         # 批量处理
│   └── organize_assets.py      # 整理资产
├── config/                     # 配置文件
│   ├── .env.example           # 环境变量模板
│   ├── runninghub_config.json  # RunningHub 配置
│   ├── midjourney_config.json  # Midjourney 配置
│   └── prompt_library.json     # 提示词库
├── templates/                  # 提示词模板
│   ├── character_template.txt   # 角色模板
│   ├── scene_template.txt       # 场景模板
│   ├── negative_template.txt    # 负面模板
│   └── video_template.txt      # 视频模板
├── docs/                       # 文档
│   ├── USER_GUIDE.md          # 使用指南
│   └── QUICKSTART.md          # 快速开始
├── examples/                   # 使用示例
│   ├── example1_generate_character.py
│   ├── example2_generate_scene.py
│   ├── example3_batch_generate.py
│   ├── example4_prompt_management.py
│   ├── example5_quality_check.py
│   ├── example6_organize_assets.py
│   └── example7_video_generation.py
├── outputs/                    # 输出目录
│   ├── characters/
│   ├── scenes/
│   └── videos/
├── requirements.txt            # Python 依赖
├── test_imports.py            # 模块导入测试
└── README.md                 # 本文件
```

---

**祝您使用愉快！** 🎉
