#!/usr/bin/env python3
"""
示例6: 资产整理
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.asset_organizer import AssetOrganizer


def main():
    print("📁 示例6: 资产整理")
    print("=" * 60)
    
    # 初始化资产整理器
    output_dir = Path('outputs') / 'organized'
    organizer = AssetOrganizer(output_dir)
    
    # 1. 分析目录
    print("\n1. 分析目录:")
    input_dir = 'outputs'
    
    if not Path(input_dir).exists():
        print(f"   ⚠️  目录不存在: {input_dir}")
        print("   请先运行 example1_generate_character.py 或 example2_generate_scene.py")
        return
    
    analysis = organizer.analyze_directory(input_dir)
    
    print(f"   目录: {input_dir}")
    print(f"   总文件数: {analysis['total_files']}")
    print(f"   总大小: {analysis['total_size_mb']:.2f} MB")
    print(f"   文件类型:")
    for ext, count in sorted(analysis['file_types'].items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"      {ext}: {count} 个")
    
    if analysis['duplicate_files']:
        print(f"   ⚠️  发现 {len(analysis['duplicate_files'])} 个重复文件")
    
    # 2. 整理资产 (复制模式)
    print("\n2. 整理资产 (复制模式):")
    result = organizer.organize_directory(
        input_dir=input_dir,
        copy_files=True
    )
    
    print(f"   成功: {result['success']} 个")
    print(f"   失败: {result['failed']} 个")
    print(f"   跳过: {result['skipped']} 个")
    
    if result['errors']:
        print(f"   错误:")
        for error in result['errors'][:3]:  # 只显示前3个
            print(f"      - {error}")
    
    print(f"\n   整理后的资产已保存到: {output_dir}")
    print("   目录结构:")
    print("      - characters/ (角色图片)")
    print("      - scenes/ (场景图片)")
    print("      - props/ (道具图片)")
    print("      - videos/ (视频文件)")
    print("      - others/ (其他文件)")
    
    # 3. 清理空目录 (移动模式下使用)
    # print("\n3. 清理空目录:")
    # removed = organizer.cleanup_empty_dirs(input_dir)
    # print(f"   ✅ 已清理 {removed} 个空目录")
    
    print("\n✅ 资产整理示例完成!")


if __name__ == '__main__':
    main()
