#!/usr/bin/env python3
"""
AI 提示词生成模板脚本
用法：python3 prompt_template.py --subject "描述" --scene "场景" --lighting "光线"
"""

import argparse
import sys

def generate_prompt(subject, scene, lighting, style_suffix=""):
    """
    生成标准 AI 提示词
    
    参数:
        subject: 主体描述
        scene: 环境/背景
        lighting: 光线描述
        style_suffix: 风格后缀（可选）
    
    返回:
        完整的 AI 提示词字符串
    """
    base = f"{subject}, {scene}, {lighting}"
    
    if style_suffix:
        base += f", {style_suffix}"
    
    base += ", photorealistic, natural skin texture with visible pores, "
    base += "lightly uneven lighting, natural shadows, not perfectly "
    base += "composed, film grain, analog photography, Kodak Portra "
    base += "400, slightly desaturated, muted tones, 4K, ultra "
    base += "detailed, raw photo"
    
    return base

def generate_negative_prompt():
    """生成通用负面提示词"""
    return (
        "cartoon, anime, illustration, painting, drawing, "
        "blurry, low quality, deformed, disfigured, "
        "bad anatomy, extra limbs, extra fingers, "
        "watermark, text, logo, signature, "
        "oversaturated, plastic, artificial, "
        "3D render, CGI, smooth skin, perfect skin, "
        "doll-like, studio lighting"
    )

def main():
    parser = argparse.ArgumentParser(description="AI 提示词生成器")
    parser.add_argument("--subject", required=True, help="主体描述")
    parser.add_argument("--scene", required=True, help="环境/背景")
    parser.add_argument("--lighting", required=True, help="光线描述")
    parser.add_argument("--style", default="", help="额外风格描述")
    
    args = parser.parse_args()
    
    prompt = generate_prompt(args.subject, args.scene, args.lighting, args.style)
    negative = generate_negative_prompt()
    
    print("=== 正提示词 ===")
    print(prompt)
    print("\n=== 负提示词 ===")
    print(negative)

if __name__ == "__main__":
    main()
