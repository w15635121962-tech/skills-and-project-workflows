# HTML 分镜导出指南

## 用途

将已生成的分镜方案（Shot List + Storyboard）导出为专业电影级 HTML 文档，带暗色调电影风格排版，适用于导演提案、客户展示、打印输出。

## 触发条件

- 用户明确要求"导出 HTML 分镜"、"生成 HTML 分镜文档"、"做个分镜页面"
- 已通过主流程生成完整分镜（Shot List 完整）
- 需要将分镜以视觉化文档形式交付

## 模板使用

### 资产文件

```
assets/html_storyboard_template.html    — 完整 HTML 模板（CSS + 结构占位符）
```

### 工作流程

1. **读取模板**：先读取 `assets/html_storyboard_template.html` 获取 CSS 和结构骨架
2. **填充内容**：用 `Write` 工具创建新文件，将 `{{PLACEHOLDER}}` 替换为实际内容，用 `Edit` 工具追加各阶段内容块
3. **分镜内容为大头**：分镜卡（Shot Cards）通常占据文件的大部分篇幅，建议使用 `Edit` 工具分批追加，每批约 10-15 个镜头卡
4. **预览**：完成后用 `preview_url` 预览
5. **交付**：用 `deliver_attachments` 交付 HTML 文件

### 占位符替换清单

| 占位符 | 替换内容 |
|--------|---------|
| `{{PROJECT_TITLE}}` | 项目/剧本标题 |
| `{{EPISODE_INFO}}` | 集数/副标题信息 |
| `{{LOGLINE}}` | 一句话梗概（logline） |
| `{{SCENE_COUNT}}` | 场景总数 |
| `{{SHOT_COUNT}}` | 镜头总数 |
| `{{DIALOGUE_COUNT}}` | 对白行数 |
| `{{ASPECT_RATIO}}` | 画幅比（如 2.39:1） |
| `{{PHASE1_TITLE}}-{{PHASE4_TITLE}}` | 各阶段标题 |
| `{{PHASE1_SUBTITLE}}-{{PHASE4_SUBTITLE}}` | 各阶段副标题 |
| `{{GENERATION_DATE}}` | 生成日期 |

---

## 内容块结构

### Phase 1 — 剧本摘要

用叙述性文字概述各场戏，包含场景头、核心情节、叙事功能。格式：

```html
<p>场景一（建立镜头）→ 场景二（核心冲突，N条对白）→ 场景三（高潮揭示）。...</p>
```

### Phase 2 — 健康报告

包含评分模块和问题卡片：

```html
<div class="health-score">
  <div class="health-num">N/10</div>
  <div>
    <div class="health-label">剧本健康评分</div>
    <div class="health-bar"><div class="health-fill" style="width:N%"></div></div>
  </div>
</div>

<div class="issue-card">
  <span class="issue-badge major">严重</span> ...
</div>
<div class="issue-card">
  <span class="issue-badge polish">优化</span> ...
</div>
```

### Phase 2B — 角色与场景圣经

**角色卡** — 使用 `.char-grid` 网格布局：

```html
<div class="char-grid">
  <div class="char-card">
    <div class="char-card-header">
      <span class="char-name">角色名</span>
      <span class="char-meta">英文名 · 色彩标签</span>
    </div>
    <div class="char-body">
      <p>角色描述、背景、功能...</p>
    </div>
  </div>
  <!-- 更多角色卡 -->
</div>
```

**场景卡** — 使用 `.scene-card`：

```html
<div class="scene-card">
  <div class="scene-card-header">
    <div class="scene-letter">N</div>
    <div>
      <div style="font-weight:600;color:var(--text-bright)">场景 N — 场景名称</div>
      <div style="font-size:0.7rem;color:var(--text-dim)">EXT./INT. 地点 — 时间</div>
    </div>
  </div>
  <div class="scene-card-body">
    <div class="kv"><span class="kv-key">人物</span><span class="kv-val">角色列表</span></div>
    <div class="kv"><span class="kv-key">情绪基调</span><span class="kv-val">描述</span></div>
    <div class="kv"><span class="kv-key">叙事功能</span><span class="kv-val">描述</span></div>
    <div class="kv"><span class="kv-key">关键道具</span><span class="kv-val">道具列表</span></div>
    <!-- 更多 kv 行 -->
  </div>
</div>
```

### Phase 2C — 视觉风格圣经

包含以下模块：

- **色彩心理学**：用色板 `.swatch-row` 展示主色调
- **反复出现的母题**：用 `.motif-tags` 标签列表
- **参考影片**：列举参考电影及理由
- **画面比例**：2.39:1 宽银幕等

```html
<div class="motif-tags">
  <div class="motif-tag">母题标签</div>
</div>

<div class="swatch-row">
  <div>
    <div class="swatch" style="background:#xxx"></div>
    <div class="swatch-label">色彩名</div>
  </div>
</div>
```

### Phase 3 — 分镜卡 (Shot Cards)

每个镜头一个卡。**这是体积最大的部分**，建议分批用 `Edit` 工具追加。

**场景分隔符**：

```html
<div class="scene-divider">
  <span class="scene-label">Scene N — 场景名</span>
</div>
```

**标准分镜卡**：

```html
<div class="shot-card">
  <div class="shot-header">
    <span class="shot-num">SHOT NNN</span>
    <span class="shot-type-badge">景别缩写</span>
    <span class="shot-duration">N″</span>
  </div>
  <div class="shot-body">
    <div class="field"><div class="field-label">构图</div><div class="field-value em">景别中文 + 描述</div></div>
    <div class="field"><div class="field-label">摄影机</div><div class="field-value">焦距 / 角度 / 运动</div></div>
    <div class="field"><div class="field-label">动作</div><div class="field-value">画面描述（现在时）</div></div>
    <!-- 如有对白 -->
    <div class="dialogue-block">
      <div class="speaker">CHARACTER NAME</div>
      "Dialogue line..."
    </div>
    <div class="field"><div class="field-label">灯光</div><div class="field-value">灯光描述</div></div>
    <div class="field"><div class="field-label">音效</div><div class="field-value">音效描述</div></div>
    <div class="ai-prompt">AI image generation prompt...</div>
  </div>
</div>
```

**核心镜头卡 (Hero Shot)** — 添加 `.hero-shot` 类和 `.hero-tag`：

```html
<div class="shot-card hero-shot">
  <div class="shot-header">
    <span class="shot-num">SHOT NNN</span>
    <span class="shot-type-badge hero">景别缩写</span>
    <span class="shot-duration">N″</span>
  </div>
  <div class="shot-body">
    <div class="hero-tag">★ 核心镜头 N/5</div>
    <!-- 同上字段 -->
    <div class="hero-design-note">设计说明：为什么这是核心镜头...</div>
  </div>
</div>
```

**Hero Shot 标注规则**：
- `.hero-tag` 文字格式：`★ 核心镜头 N/5` 或 `★ 核心镜头 N/5 · 高潮`
- `.hero-design-note`：用 2-3 句话说明这个镜头在叙事和视觉上的重要性
- `hero` CSS 类用于 `.shot-type-badge` 和 `.shot-card`

### Phase 4 — 验证统计

- 汇总表格（镜头分布统计）
- 验证清单（✓ 项）
- 自检结果

```html
<table class="data-table">
  <thead><tr><th>检查项</th><th>结果</th></tr></thead>
  <tbody>
    <tr><td>...</td><td>...</td></tr>
  </tbody>
</table>

<ul class="checklist">
  <li>✓ 项描述</li>
</ul>
```

---

## 设计系统常量

| 色彩变量 | 十六进制 | 用途 |
|---------|---------|------|
| `--bg` | `#0A0A0F` | 页面背景 |
| `--surface` | `#12121A` | 卡片背景 |
| `--surface2` | `#1A1A26` | 卡片头部背景 |
| `--surface3` | `#222233` | 对话框/AI提示框背景 |
| `--border` | `#2A2A3A` | 边框 |
| `--text` | `#C8C8D4` | 正文 |
| `--text-dim` | `#7A7A8A` | 次要文字/标签 |
| `--text-bright` | `#EAEAF0` | 标题/强调 |
| `--crimson` | `#9B2335` | 品牌色 - 深红 |
| `--crimson-glow` | `#C0394B` | 品牌色 - 亮红 |
| `--blue-glow` | `#5B93D0` | AI提示色 |
| `--hero-gold` | `#D4A843` | 核心镜头金色 |
| `--gold` | `#B8963E` | 评分/金色元素 |

---

## 注意事项

1. **对话保留原语言**：对话块（`.dialogue-block`）中的台词内容保持原剧本语言，不翻译
2. **AI 提示词保留英文**：`.ai-prompt` 中的图像生成提示词始终保留英文（图像生成模型对英文响应更好）
3. **技术参数保留英文**：焦距（mm）、光圈（f/）、ISO、色温（K）等保留英文数值
4. **分批写入**：分镜卡数量多时（>15个），使用 `Edit` 工具分批追加，避免单次操作过大
5. **移动端适配**：模板已包含 `@media (max-width: 768px)` 响应式规则，grid 自动变单列
6. **打印支持**：模板已包含 `@media print` 样式，隐藏导航和滚动提示，黑白打印友好
