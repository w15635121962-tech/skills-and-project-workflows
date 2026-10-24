"""
提示词库管理模块
支持提示词模板渲染（Jinja2语法）、权重语法自动修正、负面提示词管理
同步支持新版 prompt_library.json 结构（含 negative_prompts / video_prompts）
"""

import os
import json
import re
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime


class PromptManager:
    """提示词库管理器"""
    
    def __init__(self, library_path: str = None):
        """
        初始化提示词库
        
        Args:
            library_path: 提示词库JSON文件路径
        """
        if not library_path:
            library_path = os.path.join(os.path.dirname(__file__), '../config/prompt_library.json')
        
        self.library_path = library_path
        self.library = self._load_library()
        
        # 权重语法正则
        self.weight_pattern = re.compile(r'([\(\[])([^\]:]+)(:[\d.]+)([\)\]])')
    
    def _load_library(self) -> Dict:
        """加载提示词库"""
        if not os.path.exists(self.library_path):
            print(f"⚠️ 提示词库文件不存在：{self.library_path}")
            print(f"   将创建新的提示词库")
            return {
                "characters": {},
                "scenes": {},
                "props": {},
                "_meta": {
                    "version": "2.0",
                    "last_updated": datetime.now().isoformat(),
                    "categories": ["characters", "scenes", "props", "negative_prompts", "video_prompts"]
                }
            }
        
        with open(self.library_path, 'r', encoding='utf-8') as f:
            library = json.load(f)
        
        # 统计各类别
        n_chars = len(library.get('characters', {}))
        n_scenes = len(library.get('scenes', {}))
        n_props = len(library.get('props', {}))
        n_neg = len(library.get('negative_prompts', {}))
        n_video = len(library.get('video_prompts', {}))
        
        print(f"✅ 已加载提示词库：{n_chars} 角色，{n_scenes} 场景，{n_props} 道具")
        if n_neg:
            print(f"   负面提示词：{n_neg} 类")
        if n_video:
            print(f"   视频提示词：{n_video} 类")
        
        return library
    
    def _save_library(self):
        """保存提示词库"""
        if '_meta' not in self.library:
            self.library['_meta'] = {}
        
        self.library['_meta']['last_updated'] = datetime.now().isoformat()
        total = (len(self.library.get('characters', {})) +
                 len(self.library.get('scenes', {})) +
                 len(self.library.get('props', {})))
        self.library['_meta']['total_prompts'] = total
        
        with open(self.library_path, 'w', encoding='utf-8') as f:
            json.dump(self.library, f, ensure_ascii=False, indent=2)
        
        print(f"💾 提示词库已保存：{self.library_path}")
    
    # ------------------------------------------------------------------ #
    # 核心：获取并渲染提示词
    # ------------------------------------------------------------------ #
    def get_prompt(self, category: str, name: str, **kwargs) -> Dict[str, Any]:
        """
        获取提示词模板并渲染
        
        Args:
            category: 类别（'characters'/'scenes'/'props'/'video_prompts'）
            name: 提示词名称
            **kwargs: 模板参数
        
        Returns:
            字典：{"positive": "...", "negative": "...", "seed": ..., "category": ..., "name": ...}
        """
        if category not in self.library:
            avail = [k for k in self.library.keys() if not k.startswith('_')]
            raise ValueError(f"类别 '{category}' 不存在！可用类别：{avail}")
        
        if name not in self.library[category]:
            raise ValueError(f"提示词 '{name}' 在类别 '{category}' 中不存在！")
        
        prompt_data = self.library[category][name]
        
        # 字符串直接返回（如 video_prompts 中某些条目）
        if isinstance(prompt_data, str):
            return {
                "positive": prompt_data,
                "negative": "",
                "seed": None,
                "category": category,
                "name": name
            }
        
        # 字典格式：渲染 positive / negative 模板
        positive_template = prompt_data.get('positive', '')
        negative_template = prompt_data.get('negative', '')
        seed = prompt_data.get('seed')
        
        default_params = prompt_data.get('default_params', {})
        all_params = {**default_params, **kwargs}
        
        positive = self._render_template(positive_template, all_params)
        negative = self._render_template(negative_template, all_params) if negative_template else ""
        
        positive = self._fix_weight_syntax(positive)
        negative = self._fix_weight_syntax(negative)
        
        return {
            "positive": positive,
            "negative": negative,
            "seed": seed,
            "category": category,
            "name": name
        }
    
    def _render_template(self, template: str, params: Dict[str, Any]) -> str:
        """
        渲染提示词模板
        
        支持语法：
        - {{ param_name }} → 替换为 params['param_name']
        - {{ negative_character }} → 自动从 negative_prompts.character.prompt 解析
        - {{ negative_scene }} / {{ negative_general }} / {{ negative_video }}
        """
        if not template:
            return ""
        
        result = template
        
        # 1. 解析 negative_* 特殊占位符
        neg_placeholders = re.findall(r'\{\{\s*(negative_\w+)\s*\}\}', result)
        for placeholder in neg_placeholders:
            parts = placeholder.split('_')  # ["negative", "character"]
            if len(parts) >= 2 and parts[0] == 'negative':
                key_map = {
                    'character': 'character',
                    'scene': 'scene',
                    'general': 'general',
                    'video': 'video'
                }
                mapped_key = key_map.get(parts[1], 'general')
                neg_data = self.library.get('negative_prompts', {}).get(mapped_key, {})
                if isinstance(neg_data, dict):
                    neg_text = neg_data.get('prompt', '')
                else:
                    neg_text = str(neg_data)
                
                result = result.replace('{{ ' + placeholder + ' }}', neg_text)
                result = result.replace('{{' + placeholder + '}}', neg_text)
        
        # 2. 简单替换 {{ param_name }}
        for key, value in params.items():
            ph1 = '{{ ' + key + ' }}'
            ph2 = '{{' + key + '}}'
            if ph1 in result:
                result = result.replace(ph1, str(value))
            elif ph2 in result:
                result = result.replace(ph2, str(value))
        
        # 3. 检查是否还有未替换的占位符
        remaining = re.findall(r'\{\{\s*([^}|\s]+)\s*\}\}', result)
        if remaining:
            print(f"⚠️ 提示词模板有未替换的占位符：{remaining}")
            print(f"   请提供对应的参数，或在 default_params 中设置默认值")
        
        return result
    
    def _fix_weight_syntax(self, prompt: str) -> str:
        """修正权重语法（补全不匹配的括号/方括号）"""
        if prompt.count('(') != prompt.count(')'):
            print(f"⚠️ 提示词括号不匹配，自动修正")
            diff = prompt.count('(') - prompt.count(')')
            if diff > 0:
                prompt += ')' * diff
            else:
                prompt = '(' * abs(diff) + prompt
        
        if prompt.count('[') != prompt.count(']'):
            print(f"⚠️ 提示词方括号不匹配，自动修正")
            diff = prompt.count('[') - prompt.count(']')
            if diff > 0:
                prompt += ']' * diff
            else:
                prompt = '[' * abs(diff) + prompt
        
        return prompt
    
    # ------------------------------------------------------------------ #
    # 负面提示词
    # ------------------------------------------------------------------ #
    def get_negative_prompt(self, neg_key: str) -> str:
        """
        直接获取负面提示词文本
        
        Args:
            neg_key: 负面提示词键名（general/character/scene/video）
        
        Returns:
            负面提示词字符串
        """
        neg_data = self.library.get('negative_prompts', {}).get(neg_key, {})
        if isinstance(neg_data, dict):
            return neg_data.get('prompt', '')
        elif isinstance(neg_data, str):
            return neg_data
        return ''
    
    def list_negative_prompts(self) -> Dict[str, str]:
        """列出所有负面提示词"""
        neg = self.library.get('negative_prompts', {})
        return {k: v.get('label', k) if isinstance(v, dict) else k for k, v in neg.items()}
    
    def add_negative_prompt(self, neg_key: str, prompt: str, label: str = None):
        """添加自定义负面提示词"""
        if 'negative_prompts' not in self.library:
            self.library['negative_prompts'] = {}
        
        self.library['negative_prompts'][neg_key] = {
            "label": label or neg_key,
            "prompt": prompt
        }
        self._save_library()
        print(f"✅ 已添加负面提示词：negative_prompts/{neg_key}")
    
    # ------------------------------------------------------------------ #
    # 视频提示词组装
    # ------------------------------------------------------------------ #
    def get_video_prompt(self, shot_type: str = None, camera_movement: str = None,
                           action: str = None, style: str = None,
                           motion_intensity: str = None, audio: str = None,
                           tool: str = None) -> str:
        """
        组装视频生成提示词
        
        Args:
            shot_type: 镜头类型（wide_shot/medium_shot/close_up/extreme_close_up/over_shoulder）
            camera_movement: 摄像机运动（dolly_in/dolly_out/pan/tilt/handheld/steadicam）
            action: 动作描述（walking/running/dialogue/expression_change/object_interaction）
            style: 风格（cinematic/photorealistic/dreamy/tense/romantic）
            motion_intensity: 运动强度（low/medium/high）
            audio: 音频提示（ambient/music/sound_effects/dialogue）
            tool: 工具预设（runway_gen3/pika_2/kling_1_5/sora）
        
        Returns:
            组装后的视频提示词字符串
        """
        parts = []
        vp = self.library.get('video_prompts', {})
        
        def _get_prompt_from_dict(d, key):
            """从 video_prompts 子字典中安全获取 prompt 字段"""
            sub = d.get(key, {})
            if isinstance(sub, dict):
                return sub.get('prompt', '')
            return ''
        
        if shot_type:
            parts.append(_get_prompt_from_dict(vp.get('shot_types', {}), shot_type))
        if camera_movement:
            parts.append(_get_prompt_from_dict(vp.get('camera_movements', {}), camera_movement))
        if action:
            parts.append(_get_prompt_from_dict(vp.get('action_descriptions', {}), action))
        if style:
            parts.append(_get_prompt_from_dict(vp.get('styles', {}), style))
        if motion_intensity:
            parts.append(_get_prompt_from_dict(vp.get('motion_intensity', {}), motion_intensity))
        if audio:
            parts.append(_get_prompt_from_dict(vp.get('audio_prompts', {}), audio))
        
        # 工具预设前缀/后缀
        if tool:
            preset = vp.get('tool_presets', {}).get(tool, {})
            prefix = preset.get('prompt_prefix', '')
            suffix = preset.get('prompt_suffix', '')
            if prefix:
                parts.insert(0, prefix)
            if suffix:
                parts.append(suffix)
        
        return ', '.join([p for p in parts if p])
    
    # ------------------------------------------------------------------ #
    # CRUD 操作
    # ------------------------------------------------------------------ #
    def add_prompt(self, category: str, name: str, positive: str,
                   negative: str = "", seed: Optional[int] = None,
                   default_params: Optional[Dict] = None):
        """添加新提示词"""
        if category not in self.library:
            self.library[category] = {}
        
        if name in self.library[category]:
            print(f"⚠️ 提示词 '{name}' 已存在于类别 '{category}'，将覆盖")
        
        self.library[category][name] = {
            "positive": positive,
            "negative": negative,
            "seed": seed,
            "default_params": default_params or {}
        }
        
        print(f"✅ 已添加提示词：{category}/{name}")
        self._save_library()
    
    def update_prompt(self, category: str, name: str, **kwargs):
        """更新现有提示词"""
        if category not in self.library or name not in self.library[category]:
            raise ValueError(f"提示词 '{name}' 在类别 '{category}' 中不存在！")
        
        prompt_data = self.library[category][name]
        for key, value in kwargs.items():
            if key in prompt_data:
                prompt_data[key] = value
                print(f"✅ 已更新 {category}/{name} 的 {key}")
            else:
                print(f"⚠️ 字段 '{key}' 不存在，已忽略")
        
        self._save_library()
    
    def delete_prompt(self, category: str, name: str):
        """删除提示词"""
        if category not in self.library or name not in self.library[category]:
            raise ValueError(f"提示词 '{name}' 在类别 '{category}' 中不存在！")
        
        del self.library[category][name]
        print(f"🗑️ 已删除提示词：{category}/{name}")
        
        if not self.library[category]:
            del self.library[category]
            print(f"🗑️ 类别 '{category}' 已空，已删除")
        
        self._save_library()
    
    # ------------------------------------------------------------------ #
    # 查询
    # ------------------------------------------------------------------ #
    def search_prompts(self, keyword: str) -> List[Dict]:
        """搜索提示词（按名称、内容匹配）"""
        results = []
        skip_cats = ['_meta', 'metadata']
        
        for category, prompts in self.library.items():
            if category in skip_cats:
                continue
            if not isinstance(prompts, dict):
                continue
            
            for name, data in prompts.items():
                search_text = f"{name} "
                if isinstance(data, dict):
                    search_text += f"{data.get('positive', '')} {data.get('prompt', '')} {data.get('negative', '')}"
                elif isinstance(data, str):
                    search_text += data
                
                if keyword.lower() in search_text.lower():
                    if isinstance(data, dict):
                        results.append({
                            "category": category,
                            "name": name,
                            "positive": str(data.get('positive', ''))[:100],
                            "negative": str(data.get('negative', ''))[:100],
                            "seed": data.get('seed')
                        })
                    else:
                        results.append({
                            "category": category,
                            "name": name,
                            "positive": str(data)[:100],
                            "negative": "",
                            "seed": None
                        })
        
        print(f"🔍 搜索 '{keyword}' 找到 {len(results)} 条结果")
        return results
    
    def list_prompts(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        列出所有提示词
        
        Args:
            category: 类别（可选，不提供则返回所有类别）
        
        Returns:
            类别 -> 提示词名称列表的字典
        """
        all_cats = ['characters', 'scenes', 'props', 'negative_prompts', 'video_prompts']
        skip_cats = ['_meta', 'metadata']
        
        if category:
            if category not in self.library:
                raise ValueError(f"类别 '{category}' 不存在！可用：{all_cats}")
            return {category: list(self.library[category].keys())}
        
        result = {}
        for cat in all_cats:
            if cat in self.library and self.library[cat]:
                result[cat] = list(self.library[cat].keys())
        
        # 也返回其他非元数据的类别
        for cat, prompts in self.library.items():
            if cat not in all_cats and cat not in skip_cats and isinstance(prompts, dict):
                result[cat] = list(prompts.keys())
        
        return result
    
    # ------------------------------------------------------------------ #
    # 导入 / 导出
    # ------------------------------------------------------------------ #
    def export_prompts(self, output_path: str, category: Optional[str] = None):
        """导出提示词库（备份）"""
        if category:
            export_data = {
                category: self.library.get(category, {}),
                "_meta": {
                    "exported_at": datetime.now().isoformat(),
                    "exported_by": "PromptManager",
                    "category": category
                }
            }
        else:
            export_data = self.library.copy()
            if '_meta' not in export_data:
                export_data['_meta'] = {}
            export_data['_meta']['exported_at'] = datetime.now().isoformat()
            export_data['_meta']['exported_by'] = "PromptManager"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 已导出提示词库到：{output_path}")
    
    def import_prompts(self, input_path: str, overwrite: bool = False):
        """导入提示词库（恢复备份）"""
        with open(input_path, 'r', encoding='utf-8') as f:
            import_data = json.load(f)
        
        for category, prompts in import_data.items():
            if category.startswith('_'):
                continue
            
            if category not in self.library:
                self.library[category] = {}
            
            if not isinstance(prompts, dict):
                continue
            
            for name, data in prompts.items():
                if name in self.library[category] and not overwrite:
                    print(f"⚠️ 提示词 '{name}' 已存在，跳过（使用 overwrite=True 覆盖）")
                else:
                    self.library[category][name] = data
                    print(f"✅ 已导入：{category}/{name}")
        
        self._save_library()
        print(f"📥 导入完成！")
    
    # ------------------------------------------------------------------ #
    # 验证
    # ------------------------------------------------------------------ #
    def validate_prompt(self, category: str, name: str) -> Dict[str, Any]:
        """验证提示词（检查模板语法、权重语法等）"""
        result = {"valid": True, "errors": [], "warnings": []}
        
        # 处理 video_prompts 子类别（格式：shot_types.wide_shot）
        prompt_data = None
        if category == 'video_prompts' and '.' in name:
            subcat, key = name.split('.', 1)
            prompt_data = self.library.get('video_prompts', {}).get(subcat, {}).get(key, {})
        else:
            prompt_data = self.library.get(category, {}).get(name, {})
        
        if not prompt_data:
            result["valid"] = False
            result["errors"].append(f"提示词 '{name}' 不存在于类别 '{category}'")
            return result
        
        positive = prompt_data.get('positive', '') if isinstance(prompt_data, dict) else str(prompt_data)
        
        # 检查模板语法
        placeholders = re.findall(r'\{\{\s*([^}|\s]+)\s*\}\}', positive)
        default_params = prompt_data.get('default_params', {}) if isinstance(prompt_data, dict) else {}
        
        for ph in placeholders:
            if ph not in default_params and not ph.startswith('negative_'):
                result["warnings"].append(f"占位符 '{{{{ {ph} }}}}' 没有默认值")
        
        # 检查权重语法
        if positive.count('(') != positive.count(')'):
            result["valid"] = False
            result["errors"].append("正面提示词括号不匹配")
        
        if positive.count('[') != positive.count(']'):
            result["valid"] = False
            result["errors"].append("正面提示词方括号不匹配")
        
        if len(positive) > 500:
            result["warnings"].append(f"正面提示词过长（{len(positive)}字符），某些AI工具可能截断")
        
        return result


# 命令行入口
if __name__ == "__main__":
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description='提示词库管理工具')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # list
    list_parser = subparsers.add_parser('list', help='列出所有提示词')
    list_parser.add_argument('--category', type=str, help='类别（可选）')
    
    # search
    search_parser = subparsers.add_parser('search', help='搜索提示词')
    search_parser.add_argument('keyword', type=str, help='搜索关键词')
    
    # get
    get_parser = subparsers.add_parser('get', help='获取提示词')
    get_parser.add_argument('category', type=str, help='类别')
    get_parser.add_argument('name', type=str, help='提示词名称')
    get_parser.add_argument('--params', type=str, help='模板参数（JSON格式）')
    
    # add
    add_parser = subparsers.add_parser('add', help='添加提示词')
    add_parser.add_argument('category', type=str, help='类别')
    add_parser.add_argument('name', type=str, help='提示词名称')
    add_parser.add_argument('--positive', type=str, required=True, help='正面提示词')
    add_parser.add_argument('--negative', type=str, default='', help='负面提示词')
    add_parser.add_argument('--seed', type=int, help='随机种子')
    
    # delete
    delete_parser = subparsers.add_parser('delete', help='删除提示词')
    delete_parser.add_argument('category', type=str, help='类别')
    delete_parser.add_argument('name', help='提示词名称')
    
    # negatives
    neg_parser = subparsers.add_parser('negatives', help='列出所有负面提示词')
    
    # video
    video_parser = subparsers.add_parser('video', help='组装视频提示词')
    video_parser.add_argument('--shot', type=str, help='镜头类型')
    video_parser.add_argument('--camera', type=str, help='摄像机运动')
    video_parser.add_argument('--action', type=str, help='动作描述')
    video_parser.add_argument('--style', type=str, help='风格')
    video_parser.add_argument('--motion', type=str, help='运动强度')
    video_parser.add_argument('--audio', type=str, help='音频提示')
    video_parser.add_argument('--tool', type=str, help='工具预设')
    
    args = parser.parse_args()
    
    pm = PromptManager()
    
    if args.command == 'list':
        prompts = pm.list_prompts(category=args.category)
        for cat, names in prompts.items():
            print(f"\n📋 类别：{cat}")
            for name in names:
                print(f"   - {name}")
    
    elif args.command == 'search':
        results = pm.search_prompts(args.keyword)
        for r in results:
            print(f"\n🔍 {r['category']}/{r['name']}")
            print(f"   正面：{r['positive']}")
            print(f"   负面：{r['negative']}")
    
    elif args.command == 'get':
        params = {}
        if args.params:
            params = json.loads(args.params)
        result = pm.get_prompt(args.category, args.name, **params)
        print(f"\n📝 提示词：{args.category}/{args.name}")
        print(f"   正面：{result['positive']}")
        print(f"   负面：{result['negative']}")
        if result['seed']:
            print(f"   种子：{result['seed']}")
    
    elif args.command == 'add':
        pm.add_prompt(
            category=args.category,
            name=args.name,
            positive=args.positive,
            negative=args.negative,
            seed=args.seed
        )
    
    elif args.command == 'delete':
        confirm = input(f"确认删除 {args.category}/{args.name}？(y/N): ")
        if confirm.lower() == 'y':
            pm.delete_prompt(args.category, args.name)
        else:
            print("已取消")
    
    elif args.command == 'negatives':
        negs = pm.list_negative_prompts()
        print("\n🚫 负面提示词列表：")
        for k, v in negs.items():
            print(f"   - {k}: {v}")
    
    elif args.command == 'video':
        video_prompt = pm.get_video_prompt(
            shot_type=args.shot,
            camera_movement=args.camera,
            action=args.action,
            style=args.style,
            motion_intensity=args.motion,
            audio=args.audio,
            tool=args.tool
        )
        print(f"\n🎬 视频提示词：")
        print(video_prompt)
    
    else:
        parser.print_help()
