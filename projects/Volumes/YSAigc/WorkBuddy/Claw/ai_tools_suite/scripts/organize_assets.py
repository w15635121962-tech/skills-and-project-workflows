#!/usr/bin/env python3
"""
资产整理脚本 - 整理和分类生成的资产
"""
import argparse
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.asset_organizer import AssetOrganizer


def main():
    parser = argparse.ArgumentParser(description='整理和分类生成的资产')
    
    parser.add_argument('--input-dir', type=str, required=True, help='输入目录 (包含待整理的资产的目录)')
    parser.add_argument('--output-dir', type=str, help='输出目录 (整理后的资产存放目录，默认为input-dir/organized)')
    parser.add_argument('--mode', type=str, choices=['copy', 'move'], default='copy',
                        help='整理模式: copy (复制) 或 move (移动)，默认copy')
    parser.add_argument('--no-organize', dest='organize', action='store_false', help='不整理，只分析目录')
    parser.set_defaults(organize=True)
    parser.add_argument('--no-cleanup', dest='cleanup', action='store_false', help='不清理空目录')
    parser.set_defaults(cleanup=True)
    
    args = parser.parse_args()
    
    # 检查输入目录
    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"❌ 输入目录不存在: {input_dir}")
        return
    
    # 设置输出目录
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = input_dir / 'organized'
    
    # 创建资产整理器
    organizer = AssetOrganizer(output_dir)
    
    print("📁 资产整理工具")
    print("=" * 60)
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print(f"整理模式: {'复制' if args.mode == 'copy' else '移动'}")
    print("=" * 60)
    
    # 分析目录
    print("\n🔍 分析目录...")
    analysis = organizer.analyze_directory(input_dir)
    
    print(f"\n📊 目录分析结果:")
    print(f"  总文件数: {analysis['total_files']}")
    print(f"  总大小: {analysis['total_size_mb']:.2f} MB")
    print(f"  文件类型:")
    for ext, count in sorted(analysis['file_types'].items(), key=lambda x: x[1], reverse=True):
        print(f"    {ext}: {count} 个")
    
    if analysis['duplicate_files']:
        print(f"\n⚠️  发现 {len(analysis['duplicate_files'])} 个重复文件")
        for dup in analysis['duplicate_files'][:5]:  # 只显示前5个
            print(f"    {dup['file']}: {len(dup['duplicates'])} 个重复")
        if len(analysis['duplicate_files']) > 5:
            print(f"    ... 还有 {len(analysis['duplicate_files']) - 5} 个")
    
    # 如果不整理，只显示分析结果
    if not args.organize:
        print("\n✅ 分析完成 (未整理)")
        return
    
    # 确认操作
    if args.mode == 'move':
        print("\n⚠️  警告: 移动模式将移动原始文件！")
        confirm = input("确认继续? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ 操作已取消")
            return
    
    # 整理资产
    print("\n📦 开始整理资产...")
    try:
        result = organizer.organize_directory(
            input_dir,
            copy_files=(args.mode == 'copy')
        )
        
        print(f"\n✅ 整理完成!")
        print(f"  成功: {result['success']} 个")
        print(f"  失败: {result['failed']} 个")
        print(f"  跳过: {result['skipped']} 个")
        
        if result['errors']:
            print(f"\n⚠️  错误:")
            for error in result['errors']:
                print(f"    {error}")
        
        print(f"\n📂 整理后的资产已保存到: {output_dir}")
        print("   目录结构:")
        print("   - characters/ (角色图片)")
        print("   - scenes/ (场景图片)")
        print("   - props/ (道具图片)")
        print("   - videos/ (视频文件)")
        print("   - others/ (其他文件)")
        
    except Exception as e:
        print(f"\n❌ 整理失败: {e}")
        return
    
    # 清理空目录
    if args.cleanup and args.mode == 'move':
        print("\n🧹 清理空目录...")
        try:
            removed = organizer.cleanup_empty_dirs(input_dir)
            if removed > 0:
                print(f"✅ 已清理 {removed} 个空目录")
            else:
                print("✅ 没有空目录需要清理")
        except Exception as e:
            print(f"⚠️  清理空目录失败: {e}")
    
    print("\n🎉 资产整理完成！")


if __name__ == '__main__':
    main()
