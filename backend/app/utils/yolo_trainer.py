"""
YOLO 训练封装
"""
import sys
import logging
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from ultralytics import YOLO
from loguru import logger


class YOLOTrainer:
    """YOLO 训练封装"""

    def __init__(self, log_file: Optional[str] = None):
        """
        初始化 YOLO 训练器

        Args:
            log_file: 日志文件路径
        """
        self.log_file = log_file
        self.model = None

    def train(
        self,
        base_model: str,
        data_yaml: str,
        config: Dict[str, Any],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        训练模型

        Args:
            base_model: 基础模型路径 (e.g., 'yolov8n.pt')
            data_yaml: 数据配置文件路径
            config: 训练参数配置
            progress_callback: 进度回调函数

        Returns:
            训练结果字典
        """
        try:
            # 1. 加载基础模型
            logger.info(f"加载基础模型: {base_model}")
            self.model = YOLO(base_model)

            # 2. 准备训练参数
            train_args = {
                'data': data_yaml,
                'epochs': config.get('epochs', 100),
                'batch': config.get('batch_size', 16),
                'imgsz': config.get('img_size', 640),
                'lr0': config.get('learning_rate', 0.01),
                'optimizer': config.get('optimizer', 'SGD'),
                'device': config.get('device', '0'),
                'workers': config.get('workers', 8),
                'patience': config.get('patience', 50),
                'save': True,
                'plots': True,
                'verbose': True,
                'exist_ok': True  # 允许覆盖已存在的输出目录
            }

            # 添加数据增强参数
            if 'augmentation' in config and config['augmentation']:
                aug = config['augmentation']
                for key, value in aug.items():
                    train_args[key] = value

            logger.info(f"训练参数: {train_args}")

            # 3. 开始训练
            logger.info("开始训练...")
            results = self.model.train(**train_args)

            # 4. 获取最佳权重路径
            best_weights = Path(results.save_dir) / 'weights' / 'best.pt'
            last_weights = Path(results.save_dir) / 'weights' / 'last.pt'

            if not best_weights.exists():
                raise FileNotFoundError(f"训练完成但未找到权重文件: {best_weights}")

            # 5. 提取性能指标
            metrics = self._extract_metrics(results)

            logger.info(f"训练完成! 最佳权重: {best_weights}")
            logger.info(f"性能指标: {metrics}")

            return {
                'success': True,
                'best_weights': str(best_weights),
                'last_weights': str(last_weights),
                'results_dir': str(results.save_dir),
                'metrics': metrics
            }

        except Exception as e:
            logger.error(f"训练失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def _extract_metrics(self, results) -> Dict[str, float]:
        """
        提取训练指标

        Args:
            results: YOLO 训练结果对象

        Returns:
            性能指标字典
        """
        try:
            # YOLO 训练结果包含多个指标
            metrics = {}

            # 从结果中提取指标
            if hasattr(results, 'results_dict'):
                results_dict = results.results_dict
                metrics = {
                    'mAP50': float(results_dict.get('metrics/mAP50(B)', 0)),
                    'mAP50_95': float(results_dict.get('metrics/mAP50-95(B)', 0)),
                    'precision': float(results_dict.get('metrics/precision(B)', 0)),
                    'recall': float(results_dict.get('metrics/recall(B)', 0)),
                    'box_loss': float(results_dict.get('train/box_loss', 0)),
                    'cls_loss': float(results_dict.get('train/cls_loss', 0)),
                    'dfl_loss': float(results_dict.get('train/dfl_loss', 0))
                }
            else:
                # 尝试从其他属性获取
                logger.warning("无法从 results_dict 提取指标，使用默认值")
                metrics = {
                    'mAP50': 0.0,
                    'mAP50_95': 0.0,
                    'precision': 0.0,
                    'recall': 0.0,
                    'box_loss': 0.0,
                    'cls_loss': 0.0,
                    'dfl_loss': 0.0
                }

            return metrics

        except Exception as e:
            logger.error(f"提取指标失败: {str(e)}")
            return {
                'mAP50': 0.0,
                'mAP50_95': 0.0,
                'precision': 0.0,
                'recall': 0.0,
                'box_loss': 0.0,
                'cls_loss': 0.0,
                'dfl_loss': 0.0
            }

    def validate(self, weights_path: str, data_yaml: str) -> Dict[str, Any]:
        """
        验证模型

        Args:
            weights_path: 权重文件路径
            data_yaml: 数据配置文件

        Returns:
            验证结果
        """
        try:
            logger.info(f"开始验证模型: {weights_path}")
            model = YOLO(weights_path)

            results = model.val(data=data_yaml)

            metrics = self._extract_metrics(results)

            logger.info(f"验证完成: {metrics}")

            return {
                'success': True,
                'metrics': metrics
            }

        except Exception as e:
            logger.error(f"验证失败: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
