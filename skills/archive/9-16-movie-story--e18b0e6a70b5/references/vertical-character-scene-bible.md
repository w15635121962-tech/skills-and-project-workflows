# 角色场景圣经（竖屏 9:16 版）

> **适用**：竖屏影视项目的角色场景圣经设计  
> **核心**：9:16 画幅下的角色场景圣经、竖屏适配、手机端优化

---

## 角色场景圣经基础（竖屏版）

### 横屏 vs 竖屏角色场景圣经

| 维度 | 横屏 16:9 | 竖屏 9:16 |
|------|------------|------------|
| **角色视觉锚点** | 六维精度 | 六维精度（相同） |
| **场景视觉锚点** | 完整锚点 | 完整锚点（相同） |
| **展示方式** | 横屏构图 | 竖屏构图（满屏/中心/三分法） |
| **提示词** | `--ar 16:9` | `--ar 9:16` |

---

## 竖屏角色视觉锚点（六维精度）

### 维度 1：面容（Facial Features）
```
Facial Features (Vertical Adaptation):
- 正面/2/3 侧面
- 眼睛在画面上 1/3（y≈0.33）
- 人脸在中心稳定区（x:0.25-0.75, y:0.25-0.65）
- 竖屏适配：特写，眼睛在画面上 1/3
```

**提示词关键词**：
```
close-up, eyes at upper third, vertical composition,
face in center stable zone, 9:16 frame
```

### 维度 2：发型（Hairstyle）
```
Hairstyle (Vertical Adaptation):
- 头顶+发髻
- 头顶留 15% 呼吸空间（y≈0.15）
- 竖屏适配：特写，头顶留白
```

**提示词关键词**：
```
close-up, hair visible, top of head visible,
head room 15%, vertical composition, 9:16 frame
```

### 维度 3：服装（Costume）
```
Costume (Vertical Adaptation):
- 全身/细节
- 服装占满画面（上下贴合）
- 竖屏适配：满屏构图，服装占满画面
```

**提示词关键词**：
```
full-body shot, fills screen, vertical composition,
costume visible, detailed embroidery, 9:16 frame
```

### 维度 4：配饰（Accessories）
```
Accessories (Vertical Adaptation):
- 特写+全景
- 配饰在中心稳定区（x:0.25-0.75, y:0.25-0.65）
- 竖屏适配：特写，配饰在中心稳定区
```

**提示词关键词**：
```
close-up, accessories visible, in center stable zone,
vertical composition, 9:16 frame
```

### 维度 5：姿态（Posture）
```
Posture (Vertical Adaptation):
- 全身（上下满屏）
- 姿态在画面中心（x=0.5, y=0.4）
- 竖屏适配：满屏构图，姿态在画面中心
```

**提示词关键词**：
```
full-body shot, centered, fills screen,
vertical composition, 9:16 frame
```

### 维度 6：光影（Lighting）
```
Lighting (Vertical Adaptation):
- 单光源（顶/底/侧）
- 光影在垂直方向
- 竖屏适配：单光源，垂直方向
```

**提示词关键词**：
```
single light source, top/bottom/side lighting,
vertical frame lighting, chiaroscuro,
vertical composition, 9:16 frame
```

---

## 竖屏场景视觉锚点

### 场景锚点要素
```
1. 场景名称：{场景名称}
2. 时间段：{清晨/上午/正午/下午/傍晚/夜晚}
3. 天气：{晴/阴/雨/雪/雾/暴雨}
4. 光源类型：{窗户光/阳光/月光/烛光/灯笼/火光/油灯}
5. 色彩方案：{主色} + {辅色} + {强调色}
6. 构图方案：{中心/三分法/满屏/留白}
7. 运镜方案：{推/拉/摇/俯仰/手持}
```

### 竖屏场景锚点示例（《大唐文圣》EP01）
```
场景名称：周王府偏殿·暴雨夜
时间段：夜晚
天气：暴雨
光源类型：烛光（单光源，画面右侧）
色彩方案：
  - 主色：冷蓝灰 (#2A3B4A)
  - 辅色：深红 (#8B0000)、黑 (#0A0A0A)
  - 强调色：烛火黄 (#FFA500)
构图方案：三分法（眼睛在上横线）
运镜方案：推镜（强调情绪）+ 手持（模拟暴雨摇晃）
```

---

## 竖屏角色场景圣经提示词模板

### 模板 1：角色视觉锚点（特写）
```
Close-up of {Character},
{Facial Features}, eyes at upper third,
{Hairstyle}, head room 15%,
{Costume}, {Accessories},
{Posture}, {Lighting},
vertical composition, 9:16 frame,
--ar 9:16 --style raw --stylize 150 --v 6.0
```

### 模板 2：角色视觉锚点（满屏）
```
Full-body shot of {Character},
fills screen, vertical composition,
{Facial Features}, {Hairstyle},
{Costume}, {Accessories},
{Posture}, {Lighting},
vertical composition, 9:16 frame,
--ar 9:16 --style raw --stylize 100 --v 6.0
```

### 模板 3：场景视觉锚点（定场）
```
Establishing shot, {Location},
{Time of Day}, {Weather},
{Light Source Type}, {Color Scheme},
{Composition Scheme}, {Camera Movement},
vertical composition, 9:16 frame,
--ar 9:16 --style raw --stylize 50 --v 6.0
```

---

## 竖屏角色场景圣经检查清单

### ✅ 必选要素
- [ ] 角色视觉锚点已完成（六维精度）
- [ ] 场景视觉锚点已完成（7 要素）
- [ ] 角色提示词已生成（含 `--ar 9:16`）
- [ ] 场景提示词已生成（含 `--ar 9:16`）
- [ ] 竖屏关键词已添加（`vertical composition, 9:16 frame`）
- [ ] 眼睛位置在画面上 1/3（y≈0.33）

### ✅ 进阶优化
- [ ] 使用满屏构图（服装占满画面）
- [ ] 使用中心构图（特写，眼睛在画面上 1/3）
- [ ] 使用三分法（对话镜，眼睛在上横线）
- [ ] 使用单光源（顶/底/侧）
- [ ] 使用浅景深（f/1.8，突出主体）

---

## 示例：竖屏角色场景圣经

### 项目：《大唐文圣》EP01

#### 王勃（主角）
```
角色视觉锚点（六维精度）：
1. 面容：年轻男子，20 岁左右，道家束发髻，简洁
2. 发型：道家束发髻，简洁
3. 服装：深蓝圆领袍，领口金色牡丹刺绣
4. 配饰：无（平民身份）
5. 姿态：挺拔，眼神坚定
6. 光影：侧光（画面右侧），chiaroscuro

场景视觉锚点：
- 场景名称：周王府偏殿·暴雨夜
- 时间段：夜晚
- 天气：暴雨
- 光源类型：烛光（单光源，画面右侧）
- 色彩方案：冷蓝灰 + 深红/黑 + 烛火黄
- 构图方案：三分法（眼睛在上横线）
- 运镜方案：推镜 + 手持
```

#### 陆雪（女主角）
```
角色视觉锚点（六维精度）：
1. 面容：年轻女子，20 岁左右，交叉髻，珍珠发簪
2. 发型：交叉髻，珍珠发簪
3. 服装：杏粉窄袖上衣，丝绸大袖
4. 配饰：珍珠发簪
5. 姿态：敏捷，眼神锐利
6. 光影：侧光（画面左侧），柔光

场景视觉锚点：
- 场景名称：周王府偏殿·暴雨夜
- 时间段：夜晚
- 天气：暴雨
- 光源类型：烛光（单光源，画面右侧）
- 色彩方案：冷蓝灰 + 深红/黑 + 烛火黄
- 构图方案：三分法（眼睛在上横线）
- 运镜方案：推镜 + 手持
```

---

## 总结

竖屏角色场景圣经 = **横屏角色场景圣经** + **9:16 画幅适配** + **手机端优化**

**核心差异**：
1. 面容：眼睛在画面上 1/3（而非水平中心）
2. 发型：头顶留 15% 呼吸空间（而非左右留白）
3. 服装：满屏构图，服装占满画面（而非全身左右布局）
4. 配饰：在中心稳定区（而非左右分布）
5. 姿态：满屏构图，姿态在画面中心（而非全身左右布局）
6. 提示词必须含 `--ar 9:16`
