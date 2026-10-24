# OpenMontage 竖屏版完整使用指南 (9:16 Vertical Edition)

> **定位**：9-16-movie-story 的下游工具 — 从竖屏分镜表+AI提示词到竖屏视频的端到端自动化制作。
> **GitHub**：https://github.com/calesthio/OpenMontage
> **许可**：AGPL-3.0

---

## 一、OpenMontage 竖屏核心能力

OpenMontage 原生支持 YouTube Shorts / Instagram Reels / TikTok（1080x1920, 9:16）。

**与 9-16-movie-story 的关系**：
```
9-16-movie-story → 竖屏分镜表 + 竖屏AI提示词（--ar 9:16）
  ↓
OpenMontage → 自动执行全流程竖屏视频制作
  ↓
竖屏视频文件（1080x1920）
```

---

## 二、竖屏管线适配

| 管线 | 竖屏产出 | 竖屏场景 |
|------|----------|----------|
| **Animated Explainer** | 竖屏解说视频 | TikTok/Reels 教育内容 |
| **Cinematic** | 竖屏预告片 | 短剧预告、情绪短片 |
| **Documentary Montage** | 竖屏蒙太奇 | 竖屏视频随笔 |
| **Animation** | 竖屏MG动画 | 社交媒体动态图形 |
| **Hybrid** | 竖屏混合内容 | 竖屏素材增强 |
| **Clip Factory** | 竖屏短内容批量 | 从横屏提取竖屏片段 |
| **Talking Head** | 竖屏真人讲话 | 竖屏Vlog |
| **Avatar Spokesperson** | 竖屏虚拟人 | 竖屏企业通讯 |
| **Localization & Dub** | 竖屏字幕/配音 | 竖屏多语言 |
| **Podcast Repurpose** | 播客→竖屏视频 | 竖屏播客营销 |
| **Screen Demo** | 竖屏软件演示 | 竖屏产品教程 |
| **Product Launch** | 竖屏产品发布 | 竖屏新品预热 |

---

## 三、竖屏AI模型支持

### 视频生成
| 模型 | 竖屏支持 | 说明 |
|------|----------|------|
| Kling | ✅ 原生 | 高质量竖屏视频 |
| Runway Gen-4 | ✅ 原生 | 电影级竖屏 |
| Google Veo 3 | ✅ 原生 | 长竖屏视频 |
| Higgsfield | ✅ Soul ID | 竖屏角色一致性 |
| WAN 2.1 | ✅ 本地 | 免费（竖屏裁剪） |
| Hunyuan | ✅ 本地 | 免费（竖屏裁剪） |

### 图像生成
FLUX、Google Imagen 4、DALL-E 3 均原生支持 9:16 输出。

### TTS
ElevenLabs、Google TTS（700+声音）、OpenAI TTS、Piper（免费离线）

---

## 四、竖屏零成本路径

无需付费API即可产出竖屏视频：

| 能力 | 免费工具 | 竖屏适配 |
|------|---------|----------|
| 旁白 | Piper TTS | 竖屏字幕自动适配 |
| 素材 | Pexels + Pixabay + Archive.org | 竖屏裁剪9:16 |
| 合成 | Remotion / HyperFrames | 原生1080x1920渲染 |
| 后期 | FFmpeg | 竖屏编码、字幕烧录 |

---

## 五、竖屏使用示例

```
"制作一个45秒竖屏动画解说，主题是CRISPR技术，TikTok格式，带配音和字幕"

"Make a 60-second vertical cinematic short based on this 9:16 storyboard:
[粘贴 9-16-movie-story 输出的竖屏分镜表]
Use Kling for vertical video, FLUX for vertical images.
Output: 1080x1920, TikTok format."
```

---

## 六、竖屏质量管控

- **7维度供应商评分**（同横屏）
- **竖屏构图验证**：人脸在中心稳定区、眼睛在上1/3、底部无UI遮挡
- **竖屏节奏检查**：快切≥60%、1-3秒镜头占主导
- **平台合规**：TikTok/Reels/抖音社区规范
- **预算控制**：默认总预算$10

---

## 七、安装

```bash
git clone https://github.com/calesthio/OpenMontage.git
cd OpenMontage
make setup
```

前置：Python 3.10+、FFmpeg、Node.js 18+

---

## 八、竖屏平台输出配置

| 平台 | 分辨率 | 宽高比 |
|------|--------|--------|
| YouTube Shorts | 1080x1920 | 9:16 |
| Instagram Reels | 1080x1920 | 9:16 |
| TikTok | 1080x1920 | 9:16 |
| 抖音 | 1080x1920 | 9:16 |

---

## 九、参考链接

- GitHub: https://github.com/calesthio/OpenMontage
- 官方文档: https://deepwiki.com/calesthio/OpenMontage
- 横屏完整指南: `references/openmontage-guide.md`
