# OpenMontage 端到端视频制作完整指南

> **定位**：movie-story 的下游工具 — 从分镜表+AI提示词到最终视频的端到端自动化制作。
> **GitHub**：https://github.com/calesthio/OpenMontage
> **许可**：AGPL-3.0 | Stars: 4,200+

---

## 一、什么是 OpenMontage？

OpenMontage 是全球首个**开源 AI Agentic 视频制作系统**。它将 AI 编程助手（Claude Code、Cursor、Copilot、Windsurf、Codex）转化为完整的视频制作工作室。

**核心区别**：不只是"让静态图片动起来"，还能制作真正的视频 — 从免费素材库检索真实动态片段，剪辑成完整作品。

---

## 二、12 条生产管线

每条管线遵循统一流程：`research → proposal → script → scene_plan → assets → edit → compose`

| 管线 | 产出 | 适用场景 |
|------|------|----------|
| **Animated Explainer** | AI解说视频（调研+配音+画面+音乐） | 教育内容、教程、知识科普 |
| **Cinematic** | 预告片、teaser、情绪驱动剪辑 | 品牌影片、产品预热 |
| **Documentary Montage** | 真实素材主题蒙太奇（免费素材库） | 视频随笔、情绪短片 |
| **Animation** | 动态图形、MG动画序列 | 社交媒体、产品演示 |
| **Hybrid** | 实拍素材 + AI辅助视觉 | 现有素材增强 |
| **Clip Factory** | 长视频批量截取短视频 | 长内容复用 |
| **Talking Head** | 真人出镜讲话视频 | 演讲、Vlog、访谈 |
| **Avatar Spokesperson** | 虚拟人主持视频 | 企业通讯、培训 |
| **Localization & Dub** | 字幕、配音、翻译 | 多语言分发 |
| **Podcast Repurpose** | 播客转视频 | 播客营销 |
| **Screen Demo** | 软件录屏演示 | 产品教程 |
| **Product Launch** | 产品发布宣传视频 | 新品预热 |

---

## 三、52 个生产工具

### 视频生成（14个）
| 提供商 | 类型 | 说明 |
|--------|------|------|
| Kling | 云端API | 高质量、快速 |
| Runway Gen-4 | 云端API | 电影级质量（Gen-3/Gen-4 Turbo/Aleph） |
| Google Veo 3 | 云端API | 长视频、电影级 |
| Grok Imagine Video | 云端API | 参考图视频 |
| Higgsfield | 云端API | Soul ID角色一致性 |
| MiniMax | 云端API | 高性价比 |
| HeyGen | 云端API | 多模型网关 |
| WAN 2.1 | 本地GPU | 免费（1.3B/14B） |
| Hunyuan | 本地GPU | 免费、高质量 |
| CogVideo | 本地GPU | 免费（2B/5B） |
| LTX-Video | 本地GPU | 免费 |
| Pexels | 素材库 | 免费库存视频 |
| Pixabay | 素材库 | 免费库存视频 |
| Wikimedia Commons | 素材库 | 免费开放档案 |

### 图像生成（10个）
FLUX、Google Imagen 4、DALL-E 3、Grok Imagine Image、Recraft、Local Diffusion（SD免费）、Pexels/Pixabay/Unsplash、ManimCE

### TTS（4个）
ElevenLabs、Google TTS（700+声音）、OpenAI TTS、Piper（免费离线）

### 音乐/音效
Suno AI（完整歌曲+人声）、ElevenLabs Music、ElevenLabs SFX

### 后期（始终免费）
FFmpeg、Video Stitch、Video Trimmer、Audio Mixer、Audio Enhance、Color Grade、Subtitle Gen

### 增强
Real-ESRGAN超分、rembg背景移除、人脸增强、CodeFormer/GFPGAN人脸修复

### 分析
WhisperX语音转文字、Scene Detect场景检测、Frame Sampler帧提取、CLIP/BLIP-2视觉分析

### 合成引擎
| 引擎 | 能力 |
|------|------|
| **Remotion** | React程序化视频 — 弹簧动画、数据可视化、字幕、转场 |
| **HyperFrames** | HTML/CSS/GSAP动态图形 — 动态排版、SVG角色动画 |
| **FFmpeg** | 核心视频组装、编码、字幕烧录、混音、调色 |

---

## 四、安装

```bash
# 前置依赖
brew install ffmpeg  # macOS
# 或 sudo apt install ffmpeg  # Linux
# Node.js 18+ 和 Python 3.10+

# 安装
git clone https://github.com/calesthio/OpenMontage.git
cd OpenMontage
make setup

# 无make环境
pip install -r requirements.txt && cd remotion-composer && npm install && cd .. && pip install piper-tts && cp .env.example .env

# GPU本地视频生成（可选）
make install-gpu
# .env 添加: VIDEO_GEN_LOCAL_ENABLED=true
# VIDEO_GEN_LOCAL_MODEL=wan2.1-1.3b
```

### API密钥配置（可选）
```env
FAL_KEY=               # FLUX + Veo + Kling + MiniMax + Recraft
PEXELS_API_KEY=        # 免费库存
PIXABAY_API_KEY=       # 免费库存
UNSPLASH_ACCESS_KEY=   # 免费图片
SUNO_API_KEY=          # 音乐生成
ELEVENLABS_API_KEY=    # TTS + 音乐 + 音效
OPENAI_API_KEY=        # TTS + DALL-E 3
XAI_API_KEY=           # Grok 图像/视频
GOOGLE_API_KEY=        # Imagen + Google TTS
HEYGEN_API_KEY=        # 多模型网关
RUNWAY_API_KEY=        # Runway Gen-4
```

---

## 五、与 movie-story 的协作流程

```
1. movie-story 输出：分镜表 + AI图像提示词 + AI视频提示词
2. 将分镜表粘贴给 OpenMontage
3. OpenMontage 自动执行：
   - 调用AI模型生成素材（使用movie-story的提示词）
   - 自动剪辑、配音、字幕、合成
   - 质量自检 + 渲染输出
4. 获得最终视频文件
```

### 使用示例

```prompt
Make a 60-second cinematic short based on this storyboard:
[粘贴 movie-story 输出的分镜表]

Use Kling for video generation, FLUX for image generation.
Apply the cinematic lighting and performance prompts from the storyboard.
Output: 16:9, cinematic grade.
```

---

## 六、零成本路径

无需任何付费API密钥：

| 能力 | 免费工具 |
|------|---------|
| 旁白 | Piper TTS（离线） |
| 素材 | Pexels + Unsplash + Pixabay + Archive.org + NASA + Wikimedia |
| 合成 | Remotion（React）或 HyperFrames（HTML/GSAP） |
| 后期 | FFmpeg（编码、字幕、混音、调色） |

---

## 七、质量管控

- **7维度供应商评分**：任务适配度(30%)、输出质量(20%)、控制功能(15%)、可靠性(15%)、成本效率(10%)、延迟(5%)、连续性(5%)
- **预合成验证**：交付承诺检查、幻灯片风险评分
- **渲染后自检**：ffprobe验证、帧采样、音频分析
- **预算控制**：默认总预算$10、单操作审批$0.50
- **决策审计**：所有决策全程记录可追溯

---

## 八、平台输出配置

| 平台 | 分辨率 | 宽高比 |
|------|--------|--------|
| YouTube 横屏 | 1920x1080 | 16:9 |
| YouTube 4K | 3840x2160 | 16:9 |
| YouTube Shorts | 1080x1920 | 9:16 |
| Instagram Reels | 1080x1920 | 9:16 |
| TikTok | 1080x1920 | 9:16 |
| LinkedIn | 1920x1080 | 16:9 |
| Cinematic | 2560x1080 | 21:9 |

---

## 九、参考链接

- GitHub: https://github.com/calesthio/OpenMontage
- 官网文档: https://deepwiki.com/calesthio/OpenMontage
- 示例作品: https://github.com/calesthio/OpenMontage/tree/main/examples
