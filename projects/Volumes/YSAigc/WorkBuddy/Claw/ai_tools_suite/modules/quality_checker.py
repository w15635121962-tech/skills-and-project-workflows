"""
质量检查模块
使用OpenCV/dlib进行面部/手部检测，检查生成图片的质量
"""

import os
import json
import cv2
import numpy as np
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from tqdm import tqdm


class QualityChecker:
    """质量检查器"""
    
    def __init__(self, config_path: str = None):
        """
        初始化质量检查器
        
        Args:
            config_path: 配置文件路径
        """
        # 加载配置
        self.config = self._load_config(config_path)
        
        # 初始化检测器
        self.face_cascade = None
        self.eye_cascade = None
        self.hand_cascade = None
        
        self._init_detectors()
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置文件"""
        # 默认配置
        return {
            "face_detection": {
                "enabled": True,
                "min_face_size": 30,  # 最小人脸尺寸（像素）
                "max_face_count": 2,  # 最大人脸数量
                "score_threshold": 0.6  # 质量分数阈值
            },
            "hand_detection": {
                "enabled": True,
                "min_hand_size": 20,  # 最小手部尺寸（像素）
                "max_fingers": 5,  # 最大手指数量
                "score_threshold": 0.5
            },
            "image_quality": {
                "min_resolution": (512, 512),  # 最低分辨率
                "max_resolution": (4096, 4096),  # 最高分辨率
                "min_brightness": 30,  # 最低亮度（0-255）
                "max_brightness": 225,  # 最高亮度
                "min_contrast": 20,  # 最低对比度
                "max_blur": 100  # 最大模糊度（越小越清晰）
            },
            "scoring": {
                "face_weight": 0.3,  # 面部权重
                "hand_weight": 0.2,  # 手部权重
                "quality_weight": 0.2,  # 图片质量权重
                "composition_weight": 0.15,  # 构图权重
                "aesthetics_weight": 0.15  # 美学权重
            }
        }
    
    def _init_detectors(self):
        """初始化检测器"""
        try:
            # 面部检测器（OpenCV Haar Cascade）
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            if os.path.exists(cascade_path):
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
                print(f"✅ 面部检测器已加载")
            
            # 眼睛检测器
            eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
            if os.path.exists(eye_cascade_path):
                self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)
                print(f"✅ 眼睛检测器已加载")
            
            # 手部检测器（需要单独下载）
            # 这里使用MediaPipe或更简单的方法
            print(f"⚠️ 手部检测器需要额外安装MediaPipe")
            print(f"   请运行：pip install mediapipe")
        
        except Exception as e:
            print(f"⚠️ 检测器初始化失败：{str(e)}")
    
    def check_image(self, image_path: str, detailed: bool = False) -> Dict:
        """
        检查单张图片
        
        Args:
            image_path: 图片路径
            detailed: 是否返回详细信息
        
        Returns:
            质量检查结果字典
        """
        # 读取图片
        image = cv2.imread(image_path)
        if image is None:
            return {
                "valid": False,
                "error": f"无法读取图片：{image_path}",
                "score": 0.0
            }
        
        # 初始化结果
        result = {
            "valid": True,
            "score": 0.0,
            "issues": [],
            "details": {} if detailed else None
        }
        
        # 检查面部
        if self.config['face_detection']['enabled']:
            face_result = self._check_face(image, image_path)
            result['details']['face'] = face_result
            
            if not face_result['valid']:
                result['valid'] = False
                result['issues'].extend(face_result['issues'])
        
        # 检查手部
        if self.config['hand_detection']['enabled']:
            hand_result = self._check_hand(image, image_path)
            result['details']['hand'] = hand_result
            
            if not hand_result['valid']:
                result['valid'] = False
                result['issues'].extend(hand_result['issues'])
        
        # 检查图片质量
        quality_result = self._check_image_quality(image, image_path)
        result['details']['quality'] = quality_result
        
        if not quality_result['valid']:
            result['valid'] = False
            result['issues'].extend(quality_result['issues'])
        
        # 计算总分
        result['score'] = self._calculate_score(result['details'])
        
        return result
    
    def _check_face(self, image: np.ndarray, image_path: str) -> Dict:
        """
        检查面部
        
        Args:
            image: 图片数组
            image_path: 图片路径
        
        Returns:
            面部检查结果
        """
        result = {
            "valid": True,
            "face_count": 0,
            "faces": [],
            "issues": []
        }
        
        if self.face_cascade is None:
            result['issues'].append("面部检测器未初始化")
            return result
        
        # 转换为灰度图
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 检测面部
        faces = self.face_fascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(self.config['face_detection']['min_face_size'], 
                     self.config['face_detection']['min_face_size'])
        )
        
        result['face_count'] = len(faces)
        result['faces'] = [{"x": int(x), "y": int(y), "w": int(w), "h": int(h)} 
                           for (x, y, w, h) in faces]
        
        # 检查面部数量
        if len(faces) == 0:
            # 不是所有图片都需要有人脸，所以这里只是警告
            result['issues'].append("未检测到人脸")
        elif len(faces) > self.config['face_detection']['max_face_count']:
            result['valid'] = False
            result['issues'].append(f"检测到过多人脸（{len(faces)}个）")
        
        # 检查每个面部
        for i, (x, y, w, h) in enumerate(faces):
            face_roi = gray[y:y+h, x:x+w]
            
            # 检测眼睛
            if self.eye_cascade is not None:
                eyes = self.eye_cascade.detectMultiScale(face_roi)
                if len(eyes) < 2:
                    result['issues'].append(f"面部 #{i+1} 眼睛检测不完整")
        
        return result
    
    def _check_hand(self, image: np.ndarray, image_path: str) -> Dict:
        """
        检查手部（使用MediaPipe）
        
        Args:
            image: 图片数组
            image_path: 图片路径
        
        Returns:
            手部检查结果
        """
        result = {
            "valid": True,
            "hand_count": 0,
            "hands": [],
            "issues": []
        }
        
        # 尝试使用MediaPipe
        try:
            import mediapipe as mp
            
            # 初始化MediaPipe Hands
            mp_hands = mp.solutions.hands
            hands = mp_hands.Hands(
                static_image_mode=True,
                max_num_hands=2,
                min_detection_confidence=0.5
            )
            
            # 转换颜色空间
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # 检测手部
            results = hands.process(image_rgb)
            
            if results.multi_hand_landmarks:
                result['hand_count'] = len(results.multi_hand_landmarks)
                
                for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    # 统计手指数量
                    finger_count = self._count_fingers(hand_landmarks)
                    
                    hand_info = {
                        "index": i,
                        "finger_count": finger_count,
                        "landmarks": len(hand_landmarks.landmark)
                    }
                    result['hands'].append(hand_info)
                    
                    # 检查手指数量
                    if finger_count > self.config['hand_detection']['max_fingers']:
                        result['valid'] = False
                        result['issues'].append(f"手部 #{i+1} 手指数量异常（{finger_count}个）")
        
        except ImportError:
            result['issues'].append("MediaPipe未安装，跳过手部检测")
        except Exception as e:
            result['issues'].append(f"手部检测失败：{str(e)}")
        
        return result
    
    def _count_fingers(self, hand_landmarks) -> int:
        """
        统计手指数量（基于MediaPipe手部关键点）
        
        Args:
            hand_landmarks: MediaPipe手部关键点
        
        Returns:
            手指数量
        """
        # MediaPipe手部关键点索引
        # 4, 8, 12, 16, 20 分别是拇指、食指、中指、无名指、小指的指尖
        
        finger_tips = [4, 8, 12, 16, 20]
        finger_count = 0
        
        # 简单判断：如果指尖的y坐标小于对应PIP关节的y坐标，则认为手指是伸展开的
        # 这里只做简单示例，实际应该更复杂的逻辑
        for tip_idx in finger_tips:
            # 获取指尖坐标
            tip = hand_landmarks.landmark[tip_idx]
            
            # 获取对应PIP关节坐标（指尖下方两个关节）
            pip_idx = tip_idx - 2
            if pip_idx > 0:
                pip = hand_landmarks.landmark[pip_idx]
                
                # 如果指尖在PIP上方（y更小），则认为手指伸出
                if tip.y < pip.y:
                    finger_count += 1
        
        return finger_count
    
    def _check_image_quality(self, image: np.ndarray, image_path: str) -> Dict:
        """
        检查图片质量
        
        Args:
            image: 图片数组
            image_path: 图片路径
        
        Returns:
            图片质量检查结果
        """
        result = {
            "valid": True,
            "resolution": (image.shape[1], image.shape[0]),  # (width, height)
            "brightness": 0.0,
            "contrast": 0.0,
            "blur": 0.0,
            "issues": []
        }
        
        # 检查分辨率
        width, height = result['resolution']
        min_width, min_height = self.config['image_quality']['min_resolution']
        max_width, max_height = self.config['image_quality']['max_resolution']
        
        if width < min_width or height < min_height:
            result['valid'] = False
            result['issues'].append(f"分辨率过低：{width}x{height}")
        
        if width > max_width or height > max_height:
            result['valid'] = False
            result['issues'].append(f"分辨率过高：{width}x{height}")
        
        # 检查亮度
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        result['brightness'] = brightness
        
        if brightness < self.config['image_quality']['min_brightness']:
            result['issues'].append(f"亮度过低：{brightness:.1f}")
        
        if brightness > self.config['image_quality']['max_brightness']:
            result['issues'].append(f"亮度过高：{brightness:.1f}")
        
        # 检查对比度（标准差）
        contrast = np.std(gray)
        result['contrast'] = contrast
        
        if contrast < self.config['image_quality']['min_contrast']:
            result['issues'].append(f"对比度过低：{contrast:.1f}")
        
        # 检查模糊度（拉普拉斯方差）
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        result['blur'] = laplacian_var
        
        if laplacian_var < self.config['image_quality']['max_blur']:
            result['issues'].append(f"图片模糊：{laplacian_var:.1f}")
        
        return result
    
    def _calculate_score(self, details: Dict) -> float:
        """
        计算总分
        
        Args:
            details: 详细检查结果
        
        Returns:
            总分（0.0-1.0）
        """
        score = 0.0
        
        # 面部分数
        if 'face' in details and details['face']['valid']:
            face_score = 1.0
            if details['face']['issues']:
                face_score = 0.7  # 有警告但没问题
            score += face_score * self.config['scoring']['face_weight']
        elif 'face' in details and not details['face']['valid']:
            score += 0.3 * self.config['scoring']['face_weight']
        
        # 手部分数
        if 'hand' in details and details['hand']['valid']:
            hand_score = 1.0
            if details['hand']['issues']:
                hand_score = 0.7
            score += hand_score * self.config['scoring']['hand_weight']
        elif 'hand' in details and not details['hand']['valid']:
            score += 0.3 * self.config['scoring']['hand_weight']
        
        # 图片质量分数
        if 'quality' in details:
            quality = details['quality']
            quality_score = 1.0
            
            if quality['issues']:
                quality_score = 0.5  # 有质量问题
            
            score += quality_score * self.config['scoring']['quality_weight']
        
        # 构图分数（简单示例：检查主体是否在中心）
        # 这里可以添加更复杂的构图分析
        composition_score = 0.8  # 默认分数
        score += composition_score * self.config['scoring']['composition_weight']
        
        # 美学分数（简单示例：检查颜色分布）
        # 这里可以使用颜色直方图、色彩平衡等
        aesthetics_score = 0.8  # 默认分数
        score += aesthetics_score * self.config['scoring']['aesthetics_weight']
        
        return min(1.0, max(0.0, score))
    
    def batch_check(self, image_dir: str, output_path: str = None, 
                    detailed: bool = False) -> Dict:
        """
        批量检查图片
        
        Args:
            image_dir: 图片目录
            output_path: 输出报告路径（可选）
            detailed: 是否返回详细信息
        
        Returns:
            批量检查结果
        """
        print(f"🔍 开始批量检查图片...")
        print(f"   目录：{image_dir}")
        
        # 获取所有图片文件
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']
        image_files = []
        
        for root, dirs, files in os.walk(image_dir):
            for file in files:
                if os.path.splitext(file)[1].lower() in image_extensions:
                    image_files.append(os.path.join(root, file))
        
        print(f"   找到 {len(image_files)} 张图片")
        
        # 检查每张图片
        results = []
        valid_count = 0
        invalid_count = 0
        
        for image_path in tqdm(image_files, desc="检查图片", unit="张"):
            result = self.check_image(image_path, detailed=detailed)
            
            results.append({
                "path": image_path,
                "result": result
            })
            
            if result['valid']:
                valid_count += 1
            else:
                invalid_count += 1
        
        # 统计信息
        stats = {
            "total": len(image_files),
            "valid": valid_count,
            "invalid": invalid_count,
            "average_score": np.mean([r['result']['score'] for r in results]) if results else 0.0
        }
        
        print(f"\n📊 检查完成：")
        print(f"   总图片数：{stats['total']}")
        print(f"   合格：{stats['valid']}")
        print(f"   不合格：{stats['invalid']}")
        print(f"   平均分数：{stats['average_score']:.2f}")
        
        # 保存报告
        if output_path:
            report = {
                "timestamp": np.datetime64('now').astype(str),
                "stats": stats,
                "results": results
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            print(f"\n📋 检查报告已保存：{output_path}")
        
        return {
            "stats": stats,
            "results": results
        }
    
    def filter_images(self, image_dir: str, output_dir: str, 
                     min_score: float = 0.6, copy_mode: bool = True):
        """
        过滤图片（将合格图片复制到输出目录）
        
        Args:
            image_dir: 输入图片目录
            output_dir: 输出目录
            min_score: 最低分数阈值
            copy_mode: True=复制，False=移动
        """
        print(f"🏷️ 开始过滤图片...")
        print(f"   输入目录：{image_dir}")
        print(f"   输出目录：{output_dir}")
        print(f"   最低分数：{min_score}")
        print(f"   模式：{'复制' if copy_mode else '移动'}")
        
        # 批量检查
        check_result = self.batch_check(image_dir, detailed=False)
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 过滤合格图片
        filtered_count = 0
        
        for item in check_result['results']:
            if item['result']['score'] >= min_score:
                # 合格图片
                src_path = item['path']
                filename = os.path.basename(src_path)
                dst_path = os.path.join(output_dir, filename)
                
                if copy_mode:
                    import shutil
                    shutil.copy2(src_path, dst_path)
                else:
                    import shutil
                    shutil.move(src_path, dst_path)
                
                filtered_count += 1
        
        print(f"\n✅ 过滤完成！共过滤 {filtered_count} 张合格图片")


# 命令行测试
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='图片质量检查工具')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # 检查单张图片
    check_parser = subparsers.add_parser('check', help='检查单张图片')
    check_parser.add_argument('image', type=str, help='图片路径')
    check_parser.add_argument('--detailed', action='store_true', help='返回详细信息')
    
    # 批量检查
    batch_parser = subparsers.add_parser('batch', help='批量检查图片')
    batch_parser.add_argument('dir', type=str, help='图片目录')
    batch_parser.add_argument('--output', type=str, help='输出报告路径')
    batch_parser.add_argument('--detailed', action='store_true', help='返回详细信息')
    
    # 过滤图片
    filter_parser = subparsers.add_parser('filter', help='过滤图片')
    filter_parser.add_argument('input', type=str, help='输入目录')
    filter_parser.add_argument('output', type=str, help='输出目录')
    filter_parser.add_argument('--min-score', type=float, default=0.6, help='最低分数')
    filter_parser.add_argument('--move', action='store_true', help='移动文件（默认复制）')
    
    args = parser.parse_args()
    
    # 初始化QualityChecker
    checker = QualityChecker()
    
    if args.command == 'check':
        result = checker.check_image(args.image, detailed=args.detailed)
        
        print(f"\n📝 检查结果：")
        print(f"   有效：{result['valid']}")
        print(f"   分数：{result['score']:.2f}")
        
        if result['issues']:
            print(f"   问题：")
            for issue in result['issues']:
                print(f"     - {issue}")
        
        if args.detailed and result['details']:
            print(f"   详细信息：")
            print(json.dumps(result['details'], indent=2, ensure_ascii=False))
    
    elif args.command == 'batch':
        checker.batch_check(
            image_dir=args.dir,
            output_path=args.output,
            detailed=args.detailed
        )
    
    elif args.command == 'filter':
        checker.filter_images(
            image_dir=args.input,
            output_dir=args.output,
            min_score=args.min_score,
            copy_mode=not args.move
        )
    
    else:
        parser.print_help()
