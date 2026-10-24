# 道具设计大师（竖屏 9:16 版）

> **适用**：竖屏影视项目的道具设计  
> **核心**：9:16 画幅下的道具设计、竖屏展示、手机端优化

---

## 道具设计流程（竖屏版）

### 阶段 1：道具设计（竖屏适配）
1. **中心构图**：道具在画面中心（x=0.5, y=0.4）
2. **满屏构图**：道具占满画面（上下贴合）
3. **细节特写**：道具细节在中心稳定区（x:0.25-0.75, y:0.25-0.65）
4. **光影适配**：顶光/底光/侧光，强调道具纹理

### 阶段 2：道具清单（竖屏版）
| 道具 | 构图 | 展示方式 | 提示词关键词 |
|------|------|----------|----------------|
| **休书** | 中心构图 | 特写 | `close-up, white silk document, calligraphy` |
| **剑** | 满屏构图 | 全身+道具 | `full-body shot, holding sword, vertical frame` |
| **官印** | 中心构图 | 细节特写 | `close-up, official seal, bronze texture` |
| **油灯** | 中心构图 | 光影特写 | `close-up, oil lamp, warm glow, chiaroscuro` |
| **手铐** | 中心构图 | 细节特写 | `close-up, handcuffs, iron texture, close-up` |

### 阶段 3：提示词生成（竖屏版）
```
{Prop Name}, {detail 1}, {detail 2}, {detail 3},
vertical composition, 9:16 frame,
{close-up / full-body / detail shot},
{lighting}, {texture},
--ar 9:16 --style raw --stylize 100
```

---

## 竖屏道具展示规范

### 1. 中心构图（推荐）
```
Center Composition (Prop):
- 道具在画面中心（x=0.5, y=0.4）
- 道具占画面 60-80%
- 背景虚化（shallow depth of field）
- 适用：小型道具（休书/官印/手铐）
```

### 2. 满屏构图（大型道具）
```
Full-Frame Composition (Prop):
- 道具占满画面（上下贴合）
- 头顶留 5% 呼吸空间（y≈0.05）
- 下巴留 5% 呼吸空间（y≈0.95）
- 适用：大型道具（剑/油灯/家具）
```

### 3. 细节特写（纹理展示）
```
Detail Shot (Prop Texture):
- 道具细节在中心稳定区（x:0.25-0.75, y:0.25-0.65）
- 特写镜头（extreme close-up）
- 纹理清晰可见（texture visible）
- 适用：道具纹理（丝绸/青铜/铁器）
```

---

## 竖屏道具提示词模板

### 模板 1：休书（白色帛书）
```
Extreme close-up of white silk document,
calligraphy visible, ink on silk,
vertical composition, 9:16 frame,
centered, shallow depth of field,
side lighting, chiaroscuro,
--ar 9:16 --style raw --stylize 200
```

### 模板 2：剑（铁器）
```
Close-up of iron sword,
metal texture visible, sharp blade,
vertical composition, 9:16 frame,
centered, shallow depth of field,
top lighting, metallic reflections,
--ar 9:16 --style raw --stylize 150
```

### 模板 3：官印（青铜）
```
Close-up of bronze official seal,
intricate carvings, bronze texture,
vertical composition, 9:16 frame,
centered, shallow depth of field,
side lighting, bronze reflections,
--ar 9:16 --style raw --stylize 180
```

### 模板 4：油灯（铜制）
```
Close-up of bronze oil lamp,
warm glow, flickering flame,
vertical composition, 9:16 frame,
centered, shallow depth of field,
chiaroscuro, single light source,
--ar 9:16 --style raw --stylize 120
```

---

## 竖屏道具设计检查清单

### ✅ 必选要素
- [ ] 道具设计已完成（中心/满屏/细节特写）
- [ ] 道具清单已创建（名称/构图/展示方式/提示词）
- [ ] 道具展示规范已选择（中心/满屏/细节）
- [ ] 提示词已生成（含 `--ar 9:16`）
- [ ] 竖屏关键词已添加（`vertical composition, 9:16 frame`）
- [ ] 道具纹理已描述（silk/iron/bronze/metal）

### ✅ 进阶优化
- [ ] 使用中心构图（小型道具）
- [ ] 使用满屏构图（大型道具）
- [ ] 使用细节特写（道具纹理）
- [ ] 使用单光源（顶光/底光/侧光）
- [ ] 使用浅景深（shallow depth of field）

---

## 示例：竖屏道具设计文档

### 项目：《大唐文圣》道具设计

#### 休书（白色帛书）
```
道具：白色帛书，墨书"休书"二字
构图：中心构图（特写）
展示方式：特写，calligraphy visible
光影：侧光，chiaroscuro
提示词：{模板 1}
```

#### 剑（铁器）
```
道具：铁制长剑，锋利
构图：中心构图（特写）
展示方式：特写，metal texture visible
光影：顶光，metallic reflections
提示词：{模板 2}
```

#### 官印（青铜）
```
道具：青铜官印，雕刻精美
构图：中心构图（特写）
展示方式：特写，intricate carvings
光影：侧光，bronze reflections
提示词：{模板 3}
```

---

## 总结

竖屏道具设计大师 = **横屏道具设计大师** + **9:16 构图适配** + **中心展示**

**核心差异**：
1. 道具在画面中心（x=0.5, y=0.4）
2. 道具占画面 60-80%
3. 提示词必须含 `--ar 9:16`
4. 使用中心构图/满屏构图/细节特写
