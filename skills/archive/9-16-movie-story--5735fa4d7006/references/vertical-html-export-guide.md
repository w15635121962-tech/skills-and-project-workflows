# HTML 导出指南（竖屏 9:16 版）

> **适用**：将竖屏分镜脚本导出为 HTML 格式  
> **核心**：9:16 竖屏排版、手机端预览、竖屏提示词展示

---

## HTML 竖屏分镜模板

### 基础结构
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{项目名} - 竖屏分镜脚本</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            background: #0a0a0a;
            color: #e0e0e0;
            font-family: "PingFang SC", "Noto Sans SC", sans-serif;
        }
        .shot-card {
            width: 360px;  /* 9:16 标准宽度 */
            margin: 20px auto;
            background: #1a1a1a;
            border: 1px solid #C8A03C;
            border-radius: 8px;
            overflow: hidden;
        }
        .shot-header {
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            padding: 12px 16px;
            border-bottom: 1px solid #C8A03C;
        }
        .shot-number {
            color: #C8A03C;
            font-size: 18px;
            font-weight: bold;
        }
        .shot-scene {
            color: #888;
            font-size: 12px;
            margin-top: 4px;
        }
        .shot-content {
            padding: 16px;
        }
        .shot-framing {
            color: #C8A03C;
            font-size: 14px;
            margin-bottom: 8px;
        }
        .shot-subject {
            color: #e0e0e0;
            font-size: 14px;
            margin-bottom: 8px;
        }
        .shot-action {
            color: #a0a0a0;
            font-size: 13px;
            line-height: 1.5;
            margin-bottom: 12px;
        }
        .shot-prompt {
            background: #0a0a0a;
            border: 1px solid #333;
            border-radius: 4px;
            padding: 12px;
            font-family: monospace;
            font-size: 12px;
            color: #7CB342;
            line-height: 1.6;
            word-break: break-all;
        }
        .shot-meta {
            display: flex;
            justify-content: space-between;
            padding: 12px 16px;
            border-top: 1px solid #333;
            font-size: 12px;
            color: #888;
        }
    </style>
</head>
<body>
    <h1 style="text-align: center; color: #C8A03C;">{项目名} - 竖屏分镜脚本</h1>
    <p style="text-align: center; color: #888;">共 {总镜数} 镜 | 画幅：9:16 | 生成时间：{时间戳}</p>
    
    <!-- 镜头卡片 -->
    <div class="shot-card">
        <div class="shot-header">
            <div class="shot-number">SHOT 001</div>
            <div class="shot-scene">S1-1 | 9:16</div>
        </div>
        <div class="shot-content">
            <div class="shot-framing">🎬 构图：中心构图（特写）</div>
            <div class="shot-subject">👤 主体：王勃（特写）</div>
            <div class="shot-action">📝 动作：暴雨中抬头，瞳孔电光炸亮，决绝</div>
            <div class="shot-prompt">Close-up of young man, early 20s, wearing dark blue round-collar robe...
--ar 9:16 --style raw --stylize 100 --v 6.0</div>
        </div>
        <div class="shot-meta">
            <span>⏱️ 2.0s</span>
            <span>🎥 Push-in</span>
            <span>💡 烛火侧光</span>
        </div>
    </div>
    
    <!-- 更多镜头... -->
</body>
</html>
```

---

## 竖屏 HTML 关键样式

### 1. 卡片宽度（9:16 标准）
```css
.shot-card {
    width: 360px;  /* 手机竖屏标准宽度 */
    max-width: 100%;
    margin: 20px auto;  /* 居中 */
}
```

### 2. 提示词样式（竖屏适配）
```css
.shot-prompt {
    background: #0a0a0a;
    border: 1px solid #333;
    border-radius: 4px;
    padding: 12px;
    font-family: monospace;
    font-size: 12px;
    color: #7CB342;
    line-height: 1.6;
    word-break: break-all;  /* 防止长提示词溢出 */
    max-height: 200px;
    overflow-y: auto;  /* 提示词过长时滚动 */
}
```

### 3. 手机端适配
```css
@media (max-width: 768px) {
    .shot-card {
        width: 100%;
        margin: 10px 0;
        border-radius: 0;
    }
    .shot-prompt {
        font-size: 11px;
    }
}
```

---

## 竖屏分镜 HTML 生成脚本（Python）

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
竖屏分镜脚本 → HTML 导出工具（9:16 版）
Usage: python3 md2html_vertical.py input.md output.html
"""

import sys
import re
from datetime import datetime

def parse_markdown(md_file):
    """解析竖屏分镜 Markdown 文件"""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    shots = []
    current_shot = None
    
    for line in content.split('\n'):
        # 匹配镜头标题（## SHOT XXX）
        if re.match(r'^##\s+SHOT\s+\d+', line):
            if current_shot:
                shots.append(current_shot)
            current_shot = {'title': line.strip(), 'content': []}
        elif current_shot is not None:
            current_shot['content'].append(line)
    
    if current_shot:
        shots.append(current_shot)
    
    return shots

def generate_html(shots, output_file):
    """生成竖屏 HTML 文件"""
    html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>竖屏分镜脚本 - 9:16</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            background: #0a0a0a;
            color: #e0e0e0;
            font-family: "PingFang SC", sans-serif;
        }}
        .shot-card {{
            width: 360px;
            margin: 20px auto;
            background: #1a1a1a;
            border: 1px solid #C8A03C;
            border-radius: 8px;
            overflow: hidden;
        }}
        .shot-header {{
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            padding: 12px 16px;
            border-bottom: 1px solid #C8A03C;
        }}
        .shot-number {{
            color: #C8A03C;
            font-size: 18px;
            font-weight: bold;
        }}
        .shot-content {{
            padding: 16px;
        }}
        .shot-prompt {{
            background: #0a0a0a;
            border: 1px solid #333;
            border-radius: 4px;
            padding: 12px;
            font-family: monospace;
            font-size: 12px;
            color: #7CB342;
            line-height: 1.6;
            word-break: break-all;
            max-height: 200px;
            overflow-y: auto;
        }}
        @media (max-width: 768px) {{
            .shot-card {{
                width: 100%;
                margin: 10px 0;
                border-radius: 0;
            }}
        }}
    </style>
</head>
<body>
    <h1 style="text-align: center; color: #C8A03C;">竖屏分镜脚本（9:16）</h1>
    <p style="text-align: center; color: #888;">共 {total_shots} 镜 | 画幅：9:16</p>
    {shots_content}
</body>
</html>"""
    
    shots_html = ""
    for shot in shots:
        shot_title = shot['title']
        shot_content = '\n'.join(shot['content'])
        
        # 提取提示词（``` 代码块）
        prompt_match = re.search(r'```(.*?)```', shot_content, re.DOTALL)
        prompt_html = ""
        if prompt_match:
            prompt_text = prompt_match.group(1).strip()
            prompt_html = f'<div class="shot-prompt">{prompt_text}</div>'
        
        shots_html += f"""
    <div class="shot-card">
        <div class="shot-header">
            <div class="shot-number">{shot_title}</div>
        </div>
        <div class="shot-content">
            <pre style="white-space: pre-wrap; font-size: 13px; line-height: 1.6;">{shot_content}</pre>
            {prompt_html}
        </div>
    </div>
        """
    
    html_output = html_template.format(
        total_shots=len(shots),
        shots_content=shots_html
    )
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    print(f"✅ HTML 已生成：{output_file}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python3 md2html_vertical.py input.md output.html")
        sys.exit(1)
    
    shots = parse_markdown(sys.argv[1])
    generate_html(shots, sys.argv[2])
```

---

## 使用方法

### 1. 生成 HTML
```bash
python3 md2html_vertical.py 大唐文圣_EP01_分镜脚本_竖屏.md 大唐文圣_EP01_分镜脚本_竖屏.html
```

### 2. 在浏览器中打开
```bash
open 大唐文圣_EP01_分镜脚本_竖屏.html
```

### 3. 手机端预览
- 使用 `ngrok` 或 `python3 -m http.server` 搭建本地服务器
- 手机浏览器访问电脑 IP 地址
- 查看竖屏分镜效果

---

## 竖屏 HTML 优化建议

### ✅ 必选优化
- [ ] 卡片宽度 360px（9:16 标准）
- [ ] 提示词代码块添加滚动（防止溢出）
- [ ] 手机端适配（`@media` 查询）
- [ ] 深色主题（减少眼睛疲劳）
- [ ] 金色主题色（`#C8A03C`）

### ✅ 可选优化
- [ ] 添加镜头缩略图（AI 生成图）
- [ ] 添加视频预览（AI 生成视频）
- [ ] 添加分镜导航（快速跳转）
- [ ] 添加提示词复制按钮（一键复制）
- [ ] 添加时长进度条（可视化）

---

## 总结

竖屏 HTML 导出 = **横屏 HTML** + **9:16 宽度约束** + **手机端适配**

**核心差异**：
1. 卡片宽度 360px（而非 800px）
2. 提示词代码块添加滚动
3. 手机端适配（`@media` 查询）
4. 深色主题（竖屏观看更舒适）
