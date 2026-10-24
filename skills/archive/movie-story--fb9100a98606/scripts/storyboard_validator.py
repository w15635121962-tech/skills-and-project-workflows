#!/usr/bin/env python3
"""
分镜表格验证脚本
用法：python3 storyboard_validator.py --file "分镜表.txt"
"""

import argparse
import re
from typing import List, Dict

REQUIRED_COLUMNS = 12

COLUMN_NAMES = [
    "镜号", "景别", "运镜", "画面描述", 
    "角位/角度", "灯光/氛围", "色彩/调性", 
    "音效/配乐", "对白/旁白", "时长", 
    "备注", "AI提示词"
]

def validate_storyboard(file_path: str) -> Dict:
    """
    验证分镜表格的完整性
    
    参数:
        file_path: 分镜表格文件路径（Markdown 格式）
    
    返回:
        验证结果字典
    """
    results = {
        "total_shots": 0,
        "errors": [],
        "warnings": [],
        "missing_columns": [],
        "inconsistent_shots": []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        results["errors"].append(f"文件未找到: {file_path}")
        return results
    
    # 查找 Markdown 表格
    tables = re.findall(r'\|(.+)\|', content)
    
    shot_numbers = []
    prev_scene = None
    
    for i, line in enumerate(content.split('\n')):
        line = line.strip()
        
        # 跳过表头和分隔线
        if line.startswith('| 镜号') or line.startswith('|---'):
            continue
            
        if line.startswith('|'):
            results["total_shots"] += 1
            
            # 检查列数
            columns = [c.strip() for c in line.split('|')[1:-1]]
            
            if len(columns) != REQUIRED_COLUMNS:
                results["errors"].append(
                    f"第 {i+1} 行：列数不正确 "
                    f"（应为 {REQUIRED_COLUMNS}，实际 {len(columns)}）"
                )
            
            # 检查镜号
            shot_num = columns[0] if columns else ""
            if shot_num:
                shot_numbers.append(shot_num)
                
                # 检查场景连续性
                match = re.match(r'(S\d+)-(\d+)', shot_num)
                if match:
                    scene = match.group(1)
                    shot = int(match.group(2))
                    
                    if prev_scene and scene == prev_scene:
                        # 同一场景，检查镜头号连续性
                        pass
                    
                    prev_scene = scene
            
            # 检查关键列是否为空
            for col_idx in [0, 2, 3]:  # 镜号、运镜、画面描述
                if col_idx < len(columns) and not columns[col_idx]:
                    results["warnings"].append(
                        f"{shot_num}: {COLUMN_NAMES[col_idx]} 为空"
                    )
            
            # 检查 AI 提示词（第12列）
            if len(columns) >= 12 and not columns[11]:
                results["warnings"].append(
                    f"{shot_num}: AI提示词 为空"
                )
    
    # 检查镜头号连续性（简化版）
    # 这里可以添加更复杂的连续性检查
    
    return results

def print_results(results: Dict):
    """打印验证结果"""
    print("="*50)
    print(f"分镜验证报告")
    print("="*50)
    print(f"总镜头数：{results['total_shots']}")
    print()
    
    if results["errors"]);
        print("【错误】")
        for err in results["errors"]:
            print(f"  ❌ {err}")
        print()
    
    if results["warnings"]:
        print("【警告】")
        for warn in results["warnings"][:10]:  # 只显示前10个
            print(f"  ⚠️  {warn}")
        if len(results["warnings"]) > 10:
            print(f"  ... 还有 {len(results['warnings']) - 10} 个警告")
        print()
    
    if not results["errors"] and not results["warnings"]:
        print("✅ 分镜表格验证通过！")
    elif not results["errors"]:
        print("⚠️  分镜表格有警告，建议检查")
    else:
        print("❌ 分镜表格有错误，必须修复")
    
    print("="*50)

def main():
    parser = argparse.ArgumentParser(description="分镜表格验证器")
    parser.add_argument("--file", required=True, help="分镜表格文件路径")
    
    args = parser.parse_args()
    
    results = validate_storyboard(args.file)
    print_results(results)

if __name__ == "__main__":
    main()
