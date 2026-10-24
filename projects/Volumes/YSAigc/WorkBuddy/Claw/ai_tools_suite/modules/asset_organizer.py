"""
资产整理模块
自动整理outputs/目录下的所有资产（角色/场景/道具/视频）
"""

import os
import shutil
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class AssetOrganizer:
    """资产整理器"""
    
    def __init__(self, input_dir: str = None, output_dir: str = None):
        """
        初始化资产整理器
        
        Args:
            input_dir: 输入目录（待整理的目录）
            output_dir: 输出目录（整理后的目录）
        """
        self.input_dir = input_dir or "../outputs/"
        self.output_dir = output_dir or "../outputs/organized/"
        
        # 文件类型映射
        self.extensions = {
            'image': ['.png', '.jpg', '.jpeg', '.webp', '.bmp'],
            'video': ['.mp4', '.mov', '.avi', '.webm'],
            '3d': ['.obj', '.fbx', '.gltf', '.glb'],
            'audio': ['.mp3', '.wav', '.aac', '.flac'],
            'document': ['.pdf', '.doc', '.docx', '.txt', '.md']
        }
        
        # 类别关键词（用于自动分类）
        self.category_keywords = {
            'character': ['bella', 'luca', 'character', 'portrait', 'face'],
            'scene': ['hospital', 'party', 'scene', 'landscape', 'environment'],
            'prop': ['luggage', 'suitcase', 'prop', 'item', 'object'],
            'video': ['video', 'animation', 'cinematic']
        }
    
    def organize(self, input_dir: str = None, output_dir: str = None,
                 copy_mode: bool = True, dry_run: bool = False) -> Dict:
        """
        整理资产
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            copy_mode: True=复制文件，False=移动文件
            dry_run: 干运行（只打印计划，不实际执行）
        
        Returns:
            整理结果统计
        """
        input_dir = input_dir or self.input_dir
        output_dir = output_dir or self.output_dir
        
        print(f"🗂️ 开始整理资产...")
        print(f"   输入目录：{os.path.abspath(input_dir)}")
        print(f"   输出目录：{os.path.abspath(output_dir)}")
        print(f"   模式：{'复制' if copy_mode else '移动'}")
        if dry_run:
            print(f"   ⚠️ 干运行模式（只打印计划，不实际执行）")
        
        # 扫描输入目录
        print(f"\n🔍 扫描输入目录...")
        files = self._scan_directory(input_dir)
        print(f"   找到 {len(files)} 个文件")
        
        # 分类文件
        print(f"\n🏷️ 分类文件...")
        categories = self._categorize_files(files)
        
        for cat, file_list in categories.items():
            print(f"   {cat}: {len(file_list)} 个文件")
        
        # 创建输出目录结构
        if not dry_run:
            print(f"\n📁 创建输出目录结构...")
            self._create_output_structure(output_dir, categories)
        
        # 整理文件
        print(f"\n📦 整理文件...")
        stats = {
            "total": len(files),
            "copied": 0,
            "moved": 0,
            "skipped": 0,
            "errors": 0,
            "by_category": defaultdict(int),
            "by_type": defaultdict(int)
        }
        
        for cat, file_list in categories.items():
            for file_path in file_list:
                try:
                    # 确定目标路径
                    rel_path = os.path.relpath(file_path, input_dir)
                    dest_path = os.path.join(output_dir, cat, rel_path)
                    
                    # 创建目标目录
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    
                    if dry_run:
                        print(f"   [干运行] 将{'复制' if copy_mode else '移动'}：{file_path} -> {dest_path}")
                        stats['by_category'][cat] += 1
                    else:
                        # 执行复制或移动
                        if copy_mode:
                            shutil.copy2(file_path, dest_path)
                            stats['copied'] += 1
                        else:
                            shutil.move(file_path, dest_path)
                            stats['moved'] += 1
                        
                        stats['by_category'][cat] += 1
                        
                        # 统计文件类型
                        ext = os.path.splitext(file_path)[1].lower()
                        for type_name, exts in self.extensions.items():
                            if ext in exts:
                                stats['by_type'][type_name] += 1
                                break
                
                except Exception as e:
                    print(f"   ❌ 处理文件失败：{file_path} - {str(e)}")
                    stats['errors'] += 1
        
        # 打印统计信息
        self._print_stats(stats)
        
        # 保存整理报告
        if not dry_run:
            report_path = os.path.join(output_dir, f"organize_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            self._save_report(report_path, stats, categories, input_dir, output_dir)
            print(f"\n📊 整理报告已保存：{report_path}")
        
        return stats
    
    def _scan_directory(self, directory: str) -> List[str]:
        """
        扫描目录（递归）
        
        Args:
            directory: 目录路径
        
        Returns:
            文件路径列表
        """
        files = []
        
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                files.append(file_path)
        
        return files
    
    def _categorize_files(self, files: List[str]) -> Dict[str, List[str]]:
        """
        分类文件
        
        Args:
            files: 文件路径列表
            
        Returns:
            类别 -> 文件路径列表的字典
        """
        categories = defaultdict(list)
        
        for file_path in files:
            # 获取文件名和扩展名
            filename = os.path.basename(file_path).lower()
            ext = os.path.splitext(filename)[1].lower()
            
            # 判断文件类型
            file_type = None
            for type_name, exts in self.extensions.items():
                if ext in exts:
                    file_type = type_name
                    break
            
            if not file_type:
                file_type = 'other'
            
            # 判断类别（使用文件名关键词）
            category = 'uncategorized'
            for cat, keywords in self.category_keywords.items():
                if any(keyword in filename for keyword in keywords):
                    category = cat
                    break
            
            # 如果无法通过文件名判断，尝试通过父目录判断
            if category == 'uncategorized':
                parent_dir = os.path.basename(os.path.dirname(file_path)).lower()
                for cat, keywords in self.category_keywords.items():
                    if any(keyword in parent_dir for keyword in keywords):
                        category = cat
                        break
            
            # 根据文件类型调整类别
            if file_type == 'video':
                category = 'video'
            
            # 添加到对应类别
            categories[category].append(file_path)
        
        return dict(categories)
    
    def _create_output_structure(self, output_dir: str, categories: Dict[str, List[str]]):
        """
        创建输出目录结构
        
        Args:
            output_dir: 输出目录
            categories: 类别字典
        """
        # 创建主目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 创建类别子目录
        for category in categories.keys():
            category_dir = os.path.join(output_dir, category)
            os.makedirs(category_dir, exist_ok=True)
            
            # 为图片类别创建子目录（按视角/表情）
            if category == 'character':
                for subdir in ['front', 'side', '3-4_view', 'full_body', 'expression']:
                    os.makedirs(os.path.join(category_dir, subdir), exist_ok=True)
            
            # 为场景类别创建子目录（按时间/天气）
            elif category == 'scene':
                for subdir in ['day', 'night', 'sunny', 'rainy']:
                    os.makedirs(os.path.join(category_dir, subdir), exist_ok=True)
    
    def _print_stats(self, stats: Dict):
        """
        打印统计信息
        
        Args:
            stats: 统计信息字典
        """
        print(f"\n📊 整理统计：")
        print(f"   总文件数：{stats['total']}")
        print(f"   已复制：{stats['copied']}")
        print(f"   已移动：{stats['moved']}")
        print(f"   已跳过：{stats['skipped']}")
        print(f"   错误：{stats['errors']}")
        
        print(f"\n   按类别统计：")
        for cat, count in stats['by_category'].items():
            print(f"     {cat}: {count}")
        
        print(f"\n   按文件类型统计：")
        for type_name, count in stats['by_type'].items():
            print(f"     {type_name}: {count}")
    
    def _save_report(self, report_path: str, stats: Dict, 
                    categories: Dict[str, List[str]], 
                    input_dir: str, output_dir: str):
        """
        保存整理报告
        
        Args:
            report_path: 报告文件路径
            stats: 统计信息
            categories: 类别字典
            input_dir: 输入目录
            output_dir: 输出目录
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "input_dir": os.path.abspath(input_dir),
            "output_dir": os.path.abspath(output_dir),
            "stats": stats,
            "categories": {cat: len(files) for cat, files in categories.items()},
            "files": {cat: files for cat, files in categories.items()}
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
    
    def analyze(self, directory: str = None) -> Dict:
        """
        分析目录（不整理，只分析）
        
        Args:
            directory: 要分析的目录
            
        Returns:
            分析结果
        """
        directory = directory or self.input_dir
        
        print(f"🔍 分析目录：{os.path.abspath(directory)}")
        
        # 扫描目录
        files = self._scan_directory(directory)
        
        # 统计信息
        analysis = {
            "total_files": len(files),
            "by_type": defaultdict(int),
            "by_category": defaultdict(int),
            "by_size": {"small": 0, "medium": 0, "large": 0},  # <1MB, 1-10MB, >10MB
            "by_date": defaultdict(int),
            "duplicates": []
        }
        
        # 分析每个文件
        file_sizes = []
        for file_path in files:
            # 文件类型
            ext = os.path.splitext(file_path)[1].lower()
            for type_name, exts in self.extensions.items():
                if ext in exts:
                    analysis['by_type'][type_name] += 1
                    break
            else:
                analysis['by_type']['other'] += 1
            
            # 类别
            filename = os.path.basename(file_path).lower()
            category = 'uncategorized'
            for cat, keywords in self.category_keywords.items():
                if any(keyword in filename for keyword in keywords):
                    category = cat
                    break
            analysis['by_category'][category] += 1
            
            # 文件大小
            size = os.path.getsize(file_path)
            file_sizes.append((file_path, size))
            
            if size < 1024 * 1024:  # <1MB
                analysis['by_size']['small'] += 1
            elif size < 10 * 1024 * 1024:  # 1-10MB
                analysis['by_size']['medium'] += 1
            else:  # >10MB
                analysis['by_size']['large'] += 1
            
            # 修改日期
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            date_key = mtime.strftime('%Y-%m-%d')
            analysis['by_date'][date_key] += 1
        
        # 查找重复文件（基于文件大小）
        size_groups = defaultdict(list)
        for file_path, size in file_sizes:
            size_groups[size].append(file_path)
        
        for size, file_list in size_groups.items():
            if len(file_list) > 1:
                analysis['duplicates'].append({
                    "size": size,
                    "count": len(file_list),
                    "files": file_list
                })
        
        # 打印分析结果
        self._print_analysis(analysis)
        
        return analysis
    
    def _print_analysis(self, analysis: Dict):
        """
        打印分析结果
        
        Args:
            analysis: 分析结果
        """
        print(f"\n📊 分析结果：")
        print(f"   总文件数：{analysis['total_files']}")
        
        print(f"\n   按文件类型统计：")
        for type_name, count in analysis['by_type'].items():
            print(f"     {type_name}: {count}")
        
        print(f"\n   按类别统计：")
        for cat, count in analysis['by_category'].items():
            print(f"     {cat}: {count}")
        
        print(f"\n   按文件大小统计：")
        print(f"     <1MB: {analysis['by_size']['small']}")
        print(f"     1-10MB: {analysis['by_size']['medium']}")
        print(f"     >10MB: {analysis['by_size']['large']}")
        
        print(f"\n   按日期统计：")
        for date, count in sorted(analysis['by_date'].items()):
            print(f"     {date}: {count}")
        
        if analysis['duplicates']:
            print(f"\n   ⚠️ 发现 {len(analysis['duplicates'])} 组可能重复的文件（基于文件大小）")
            for dup in analysis['duplicates'][:5]:  # 只显示前5组
                print(f"     {dup['count']} 个文件，大小：{dup['size']} 字节")
                for file_path in dup['files'][:3]:  # 只显示前3个文件
                    print(f"       - {file_path}")
                if len(dup['files']) > 3:
                    print(f"       ... 还有 {len(dup['files']) - 3} 个文件")
        else:
            print(f"\n   ✅ 未发现重复文件")
    
    def clean_empty_dirs(self, directory: str = None, dry_run: bool = False):
        """
        清理空目录
        
        Args:
            directory: 要清理的目录
            dry_run: 干运行（只打印计划，不实际执行）
        """
        directory = directory or self.output_dir
        
        print(f"🧹 清理空目录...")
        print(f"   目录：{os.path.abspath(directory)}")
        if dry_run:
            print(f"   ⚠️ 干运行模式（只打印计划，不实际执行）")
        
        # 获取所有子目录（从最深层的开始）
        all_dirs = []
        for root, dirs, _ in os.walk(directory, topdown=False):
            for dir_name in dirs:
                dir_path = os.path.join(root, dir_name)
                all_dirs.append(dir_path)
        
        # 删除空目录
        removed = 0
        for dir_path in all_dirs:
            try:
                if not os.listdir(dir_path):  # 目录为空
                    if dry_run:
                        print(f"   [干运行] 将删除空目录：{dir_path}")
                    else:
                        os.rmdir(dir_path)
                        print(f"   🗑️ 删除空目录：{dir_path}")
                    removed += 1
            except Exception as e:
                print(f"   ❌ 删除目录失败：{dir_path} - {str(e)}")
        
        print(f"\n✅ 清理完成！共删除 {removed} 个空目录")


# 命令行测试
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='资产整理工具')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 整理资产
    organize_parser = subparsers.add_parser('organize', help='整理资产')
    organize_parser.add_argument('--input', type=str, help='输入目录')
    organize_parser.add_argument('--output', type=str, help='输出目录')
    organize_parser.add_argument('--move', action='store_true', help='移动文件（默认复制）')
    organize_parser.add_argument('--dry-run', action='store_true', help='干运行')
    
    # 分析目录
    analyze_parser = subparsers.add_parser('analyze', help='分析目录')
    analyze_parser.add_argument('--dir', type=str, help='要分析的目录')
    
    # 清理空目录
    clean_parser = subparsers.add_parser('clean', help='清理空目录')
    clean_parser.add_argument('--dir', type=str, help='要清理的目录')
    clean_parser.add_argument('--dry-run', action='store_true', help='干运行')
    
    args = parser.parse_args()
    
    # 初始化AssetOrganizer
    organizer = AssetOrganizer()
    
    if args.command == 'organize':
        organizer.organize(
            input_dir=args.input,
            output_dir=args.output,
            copy_mode=not args.move,
            dry_run=args.dry_run
        )
    
    elif args.command == 'analyze':
        organizer.analyze(directory=args.dir)
    
    elif args.command == 'clean':
        organizer.clean_empty_dirs(directory=args.dir, dry_run=args.dry_run)
    
    else:
        parser.print_help()
