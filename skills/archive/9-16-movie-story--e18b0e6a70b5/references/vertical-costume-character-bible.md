# 服装角色圣经（竖屏 9:16 版）

> **适用**：竖屏影视项目的服装角色设计  
> **核心**：9:16 画幅下的服装设计、竖屏展示、手机端优化

---

## 服装角色设计流程（竖屏版）

### 阶段 1：服装设计（竖屏适配）
1. **满屏展示**：服装占满画面（上下贴合）
2. **细节特写**：服装细节在中心稳定区（x:0.25-0.75, y:0.25-0.65）
3. **色彩适配**：主色在中心区，辅色在边缘区
4. **光影适配**：顶光/底光/侧光，强调服装纹理

### 阶段 2：角色六维精度（竖屏版）
| 维度 | 横屏 16:9 | 竖屏 9:16 | 说明 |
|------|------------|------------|------|
| **面容** | 正面/侧面 | 正面/2/3 侧面 | 眼睛在画面上 1/3 |
| **发型** | 全头 | 头顶+发髻 | 头顶留 15% 呼吸空间 |
| **服装** | 全身 | 全身（上下满屏） | 服装占满画面 |
| **配饰** | 全身 | 特写+全景 | 配饰在中心稳定区 |
| **姿态** | 全身 | 全身（上下满屏） | 姿态在画面中心 |
| **光影** | 全光源 | 单光源（顶/底/侧） | 强调服装纹理 |

### 阶段 3：提示词生成（竖屏版）
```
{Character Name} wearing {Costume Description},
{detail 1}, {detail 2}, {detail 3},
vertical composition, 9:16 frame,
full-body shot, fills screen,
{lighting}, {texture},
--ar 9:16 --style raw --stylize 100
```

---

## 竖屏服装展示规范

### 1. 满屏构图（推荐）
```
Full-Frame Composition (Costume):
- 服装占满画面（上下贴合）
- 头顶留 5% 呼吸空间（y≈0.05）
- 下巴留 5% 呼吸空间（y≈0.95）
- 左右留 10% 呼吸空间（x≈0.1, x≈0.9）
```

**适用**：全身镜头，服装展示

### 2. 中心构图（细节特写）
```
Center Composition (Costume Detail):
- 服装细节在画面中心（x=0.5, y=0.4）
- 眼睛在画面上 1/3（y≈0.33）
- 头顶留 15% 呼吸空间（y≈0.15）
- 下巴到画面底部留 20%（y≈0.8）
```

**适用**：服装细节特写（刺绣/纹理/配饰）

### 3. 三分法（全身+环境）
```
Rule of Thirds (Costume + Environment):
- 服装在画面上 2/3
- 环境在画面下 1/3
- 眼睛在上横线上（y≈0.33）
- 服装细节在下横线上（y≈0.66）
```

**适用**：全身镜头+环境展示

---

## 竖屏服装提示词模板

### 模板 1：王勃（深蓝圆领袍）
```
Full-body shot of young man, early 20s,
wearing dark blue round-collar robe,
golden peony embroidery at collar,
silk texture visible, detailed embroidery,
vertical composition, 9:16 frame,
fills screen, full-body shot,
side lighting, chiaroscuro,
--ar 9:16 --style raw --stylize 100
```

### 模板 2：陆雪（杏粉窄袖上衣）
```
Full-body shot of young woman, early 20s,
wearing apricot pink tight-sleeved top,
silk billowing sleeves, elaborate cross-bun,
pearl hairpin, silk texture visible,
vertical composition, 9:16 frame,
fills screen, full-body shot,
side lighting, soft shadows,
--ar 9:16 --style raw --stylize 150
```

### 模板 3：裴子华（藏青色通袖琵琶袖袍）
```
Full-body shot of man in 40s,
wearing parallel-collar deep indigo robe,
python-patterned belt, elegant and powerful,
silk texture visible, detailed embroidery,
vertical composition, 9:16 frame,
fills screen, full-body shot,
top lighting, dramatic shadows,
--ar 9:16 --style raw --stylize 50
```

---

## 竖屏服装设计检查清单

### ✅ 必选要素
- [ ] 服装设计已完成（满屏展示/细节特写/全身+环境）
- [ ] 角色六维精度已定义（面容/发型/服装/配饰/姿态/光影）
- [ ] 服装展示规范已选择（满屏/中心/三分法）
- [ ] 提示词已生成（含 `--ar 9:16`）
- [ ] 竖屏关键词已添加（`vertical composition, 9:16 frame, fills screen`）
- [ ] 服装细节已描述（刺绣/纹理/配饰）

### ✅ 进阶优化
- [ ] 使用满屏构图（服装占满画面）
- [ ] 使用中心构图（服装细节特写）
- [ ] 使用三分法（全身+环境）
- [ ] 使用单光源（顶光/底光/侧光）
- [ ] 使用服装纹理描述（silk texture/embroidery/detailed）

---

## 示例：竖屏服装角色圣经

### 项目：《大唐文圣》角色服装设计

#### 王勃（主角）
```
服装：深蓝圆领袍，领口金色牡丹刺绣
发型：道家束发髻，简洁
配饰：无（平民身份）
姿态：挺拔，眼神坚定
光影：侧光，强调面部轮廓和服装纹理
提示词：{模板 1}
```

#### 陆雪（女主角）
```
服装：杏粉窄袖上衣，丝绸大袖，交叉髻，珍珠发簪
发型：交叉髻，珍珠发簪
配饰：珍珠发簪
姿态：敏捷，眼神锐利
光影：侧光，强调服装飘逸感
提示词：{模板 2}
```

#### 裴子华（反派）
```
服装：藏青色通袖琵琶袖袍，蟒纹腰带
发型：文人发髻，典雅
配饰：蟒纹腰带
姿态：优雅，眼神深邃
光影：顶光，强调权力感
提示词：{模板 3}
```

---

## 总结

竖屏服装角色圣经 = **横屏服装角色圣经** + **9:16 构图适配** + **满屏展示**

**核心差异**：
1. 服装占满画面（上下贴合）
2. 服装细节在中心稳定区
3. 提示词必须含 `--ar 9:16`
4. 使用满屏构图/中心构图/三分法
