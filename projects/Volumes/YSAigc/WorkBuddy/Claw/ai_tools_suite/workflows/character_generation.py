#!/usr/bin/env python3
"""
角色生成工作流 - 完整的角色生成流程
包括: 生成多视角、质量检查、自动放大
"""
import sys
import os
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.runninghub_api import RunningHubAPI
from modules.prompt_manager import PromptManager
from modules.quality_checker import QualityChecker
from modules.batch_generator import BatchGenerator


class CharacterGenerationWorkflow:
    """角色生成工作流"""
    
    def __init__(self, api: RunningHubAPI, prompt_manager: PromptManager, 
                 quality_checker: Optional[QualityChecker] = None):
        """
        初始化角色生成工作流
        
        Args:
            api: RunningHub API 客户端
            prompt_manager: 提示词管理器
            quality_checker: 质量检查器 (可选)
        """
        self.api = api
        self.prompt_manager = prompt_manager
        self.quality_checker = quality_checker
        self.batch_generator = BatchGenerator(api, prompt_manager)
    
    def generate_character(self, character_name: str, 
                          prompt_variant: Optional[str] = None,
                          negative_prompt: Optional[str] = None,
                          output_dir: str = 'outputs/characters',
                          views: List[str] = None,
                          expressions: List[str] = None,
                          width: int = 512, height: int = 768,
                          steps: int = 30, cfg_scale: float = 7.5,
                          batch_size: int = 1,
                          upscale: bool = True,
                          quality_check: bool = True) -> Dict:
        """
        生成完整角色 (多视角 + 多表情)
        
        Args:
            character_name: 角色名称 (对应 prompt_library 中的键)
            prompt_variant: 提示词变体 (额外描述)
            negative_prompt: 负面提示词 (如果为None，使用库中的)
            output_dir: 输出目录
            views: 视角列表 (front, side, back, three_quarter)
            expressions: 表情列表 (neutral, smile, serious, angry, sad, surprised)
            width: 图片宽度
            height: 图片高度
            steps: 生成步数
            cfg_scale: CFG缩放
            batch_size: 批次大小
            upscale: 是否放大
            quality_check: 是否质量检查
            
        Returns:
            生成结果字典
        """
        # 默认视角和表情
        if views is None:
            views = ['front', 'side', 'back']
        if expressions is None:
            expressions = ['neutral', 'smile']
        
        # 获取负面提示词
        if negative_prompt is None:
            negative_prompt = self.prompt_manager.get_negative_prompt('character')
        
        # 创建输出目录
        output_path = Path(output_dir) / character_name
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\n👤 开始生成角色: {character_name}")
        print(f"   视角: {', '.join(views)}")
        print(f"   表情: {', '.join(expressions)}")
        print(f"   输出: {output_path}")
        print(f"   放大: {'是' if upscale else '否'}")
        print(f"   质量检查: {'是' if quality_check else '否'}")
        print("=" * 60)
        
        results = {
            'character': character_name,
            'total': len(views) * len(expressions),
            'generated': 0,
            'upscaled': 0,
            'passed_qc': 0,
            'failed': 0,
            'files': []
        }
        
        # 生成每个视角和表情的组合
        for view in views:
            for expression in expressions:
                print(f"\n🎨 生成: {view} view, {expression} expression")
                
                try:
                    # 渲染提示词
                    prompt = self.prompt_manager.render_character_prompt(
                        character_name=character_name,
                        variant=prompt_variant,
                        view=view,
                        expression=expression
                    )
                    
                    print(f"   提示词: {prompt[:100]}...")
                    
                    # 生成图像
                    output_files = self.api.text_to_image(
                        prompt=prompt,
                        negative_prompt=negative_prompt,
                        output_dir=str(output_path),
                        width=width,
                        height=height,
                        steps=steps,
                        cfg_scale=cfg_scale,
                        batch_size=batch_size,
                        filename_prefix=f"{character_name}_{view}_{expression}"
                    )
                    
                    if not output_files:
                        print(f"   ❌ 生成失败: 没有生成文件")
                        results['failed'] += 1
                        continue
                    
                    print(f"   ✅ 生成成功: {len(output_files)} 个文件")
                    results['generated'] += len(output_files)
                    
                    # 质量检查
                    if quality_check and self.quality_checker:
                        passed_files = []
                        for file_path in output_files:
                            qc_result = self.quality_checker.check_image(file_path)
                            if qc_result['passed']:
                                passed_files.append(file_path)
                                print(f"      ✅ 通过QC: {Path(file_path).name}")
                            else:
                                print(f"      ❌ 未通过QC: {Path(file_path).name}")
                                print(f"         问题: {', '.join(qc_result['issues'])[:100]}...")
                        
                        results['passed_qc'] += len(passed_files)
                        output_files = passed_files  # 只保留通过QC的文件
                    
                    # 放大
                    if upscale and output_files:
                        upscaled_files = []
                        for file_path in output_files:
                            print(f"   🔍 放大: {Path(file_path).name}")
                            upscaled = self.api.upscale_image(file_path)
                            if upscaled:
                                upscaled_files.append(upscaled)
                                results['upscaled'] += 1
                        
                        output_files = upscaled_files  # 使用放大后的文件
                    
                    # 添加到结果
                    results['files'].extend(output_files)
                    
                    # 避免API限流
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"   ❌ 生成失败: {e}")
                    results['failed'] += 1
                    continue
        
        # 打印总结
        print("\n" + "=" * 60)
        print(f"✅ 角色 {character_name} 生成完成!")
        print(f"   总组合数: {results['total']}")
        print(f"   成功生成: {results['generated']}")
        print(f"   成功放大: {results['upscaled']}")
        print(f"   通过QC: {results['passed_qc']}")
        print(f"   失败: {results['failed']}")
        print(f"   输出目录: {output_path}")
        print("=" * 60)
        
        return results
    
    def generate_character_variations(self, character_name: str,
                                     variants: List[str],
                                     output_dir: str = 'outputs/characters',
                                     **kwargs) -> List[Dict]:
        """
        生成角色的不同变体 (不同服装/发型等)
        
        Args:
            character_name: 角色名称
            variants: 变体列表 (额外描述)
            output_dir: 输出目录
            **kwargs: 其他参数 (传递给 generate_character)
            
        Returns:
            生成结果列表
        """
        results = []
        
        for i, variant in enumerate(variants, 1):
            print(f"\n{'=' * 60}")
            print(f"变体 {i}/{len(variants)}: {variant}")
            print("=" * 60)
            
            result = self.generate_character(
                character_name=character_name,
                prompt_variant=variant,
                output_dir=output_dir,
                **kwargs
            )
            
            results.append(result)
        
        return results
    
    def batch_generate_characters(self, character_configs: List[Dict],
                                  output_dir: str = 'outputs/characters',
                                  **kwargs) -> List[Dict]:
        """
        批量生成多个角色
        
        Args:
            character_configs: 角色配置列表，每个配置包含:
                - name: 角色名称
                - variant: 提示词变体 (可选)
                - views: 视角列表 (可选)
                - expressions: 表情列表 (可选)
            output_dir: 输出目录
            **kwargs: 其他参数 (传递给 generate_character)
            
        Returns:
            生成结果列表
        """
        results = []
        
        for i, config in enumerate(character_configs, 1):
            print(f"\n{'=' * 60}")
            print(f"角色 {i}/{len(character_configs)}: {config['name']}")
            print("=" * 60)
            
            result = self.generate_character(
                character_name=config['name'],
                prompt_variant=config.get('variant'),
                views=config.get('views'),
                expressions=config.get('expressions'),
                output_dir=output_dir,
                **kwargs
            )
            
            results.append(result)
        
        # 打印总结
        print("\n" + "=" * 60)
        print("📊 批量生成总结")
        print("=" * 60)
        
        total_generated = sum(r['generated'] for r in results)
        total_upscaled = sum(r['upscaled'] for r in results)
        total_passed_qc = sum(r['passed_qc'] for r in results)
        total_failed = sum(r['failed'] for r in results)
        
        print(f"总角色数: {len(character_configs)}")
        print(f"总生成数: {total_generated}")
        print(f"总放大数: {total_upscaled}")
        print(f"总通过QC: {total_passed_qc}")
        print(f"总失败数: {total_failed}")
        print("=" * 60)
        
        return results


def main():
    """测试角色生成工作流"""
    import argparse
    
    parser = argparse.ArgumentParser(description='角色生成工作流')
    parser.add_argument('--character', type=str, required=True, help='角色名称')
    parser.add_argument('--variant', type=str, help='提示词变体')
    parser.add_argument('--views', nargs='+', default=['front', 'side', 'back'], help='视角列表')
    parser.add_argument('--expressions', nargs='+', default=['neutral', 'smile'], help='表情列表')
    parser.add_argument('--output-dir', type=str, default='outputs/characters', help='输出目录')
    parser.add_argument('--width', type=int, default=512, help='图片宽度')
    parser.add_argument('--height', type=int, default=768, help='图片高度')
    parser.add_argument('--steps', type=int, default=30, help='生成步数')
    parser.add_argument('--cfg-scale', type=float, default=7.5, help='CFG缩放')
    parser.add_argument('--no-upscale', dest='upscale', action='store_false', help='不放大')
    parser.set_defaults(upscale=True)
    parser.add_argument('--no-quality-check', dest='quality_check', action='store_false', help='不检查质量')
    parser.set_defaults(quality_check=True)
    parser.add_argument('--api-key', type=str, help='RunningHub API Key')
    
    args = parser.parse_args()
    
    # 初始化
    api_key = args.api_key or os.getenv('RUNNINGHUB_API_KEY')
    if not api_key:
        print("❌ 错误: 必须提供 RunningHub API Key")
        return
    
    api = RunningHubAPI(api_key=api_key)
    prompt_manager = PromptManager()
    quality_checker = QualityChecker()
    
    workflow = CharacterGenerationWorkflow(api, prompt_manager, quality_checker)
    
    # 生成角色
    result = workflow.generate_character(
        character_name=args.character,
        prompt_variant=args.variant,
        views=args.views,
        expressions=args.expressions,
        output_dir=args.output_dir,
        width=args.width,
        height=args.height,
        steps=args.steps,
        cfg_scale=args.cfg_scale,
        upscale=args.upscale,
        quality_check=args.quality_check
    )
    
    print(f"\n🎉 完成! 生成了 {len(result['files'])} 个文件")


if __name__ == '__main__':
    main()
