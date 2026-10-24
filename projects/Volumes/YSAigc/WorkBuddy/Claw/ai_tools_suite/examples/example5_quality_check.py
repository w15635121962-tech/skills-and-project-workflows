#!/usr/bin/env python3
"""
示例5: 质量检查
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.quality_checker import QualityChecker


def main():
    print("🔍 示例5: 质量检查")
    print("=" * 60)
    
    # 初始化质量检查器
    checker = QualityChecker()
    
    # 检查单个图像
    print("\n1. 检查单个图像:")
    image_path = 'outputs/characters/Bella/front_neutral.png'
    
    if not Path(image_path).exists():
        print(f"   ⚠️  文件不存在: {image_path}")
        print("   请先运行 example1_generate_character.py 生成测试图像")
        return
    
    result = checker.check_image(image_path)
    
    print(f"   文件: {image_path}")
    print(f"   通过: {'是' if result['passed'] else '否'}")
    print(f"   问题: {', '.join(result['issues']) if result['issues'] else '无'}")
    print(f"   面部检测: {'是' if result['face_detected'] else '否'}")
    print(f"   手部检测: {'是' if result['hands_detected'] else '否'}")
    
    # 批量检查
    print("\n2. 批量检查:")
    directory = 'outputs/characters/Bella'
    
    if not Path(directory).exists():
        print(f"   ⚠️  目录不存在: {directory}")
        return
    
    results = checker.batch_check(directory)
    
    # 生成报告
    report = checker.get_quality_report(results)
    
    print(f"   目录: {directory}")
    print(f"   总文件: {report['total']}")
    print(f"   通过: {report['passed']}")
    print(f"   失败: {report['failed']}")
    print(f"   通过率: {report['pass_rate']:.1%}")
    
    # 保存报告
    print("\n3. 保存质量报告:")
    checker.save_quality_report(report, 'outputs/quality_report.json')
    print("   ✅ 报告已保存: outputs/quality_report.json")
    
    print("\n✅ 质量检查示例完成!")


if __name__ == '__main__':
    main()
