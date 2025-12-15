"""
训练数据准备服务
将标注数据转换为 YOLO 训练格式
"""
import os
import shutil
import random
import yaml
from typing import List, Tuple, Dict, Any
from pathlib import Path
from PIL import Image
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.crud.annotation import crud_annotation, crud_annotation_task
from app.models.annotation import Annotation
from app.schemas.training import DatasetConfig, DatasetPrepareResult


class DataPreparationService:
    """数据准备服务"""

    def __init__(self, job_id: int, output_dir: str = "storage/training"):
        """
        初始化数据准备服务

        Args:
            job_id: 训练任务 ID
            output_dir: 输出根目录
        """
        self.job_id = job_id
        self.output_dir = output_dir
        self.dataset_dir = Path(output_dir) / 'datasets' / f"job_{job_id}"

        # 创建目录结构
        for split in ['train', 'val', 'test']:
            (self.dataset_dir / 'images' / split).mkdir(parents=True, exist_ok=True)
            (self.dataset_dir / 'labels' / split).mkdir(parents=True, exist_ok=True)

        logger.info(f"数据集目录已创建: {self.dataset_dir}")

    async def prepare_dataset(
        self,
        db: AsyncSession,
        dataset_config: DatasetConfig
    ) -> DatasetPrepareResult:
        """
        准备训练数据集

        Args:
            db: 数据库会话
            dataset_config: 数据集配置

        Returns:
            数据集准备结果
        """
        logger.info(f"开始准备数据集 (job_id={self.job_id})")

        # 1. 获取标注数据
        annotations = await self._fetch_annotations(db, dataset_config)
        logger.info(f"获取到 {len(annotations)} 条标注数据")

        if len(annotations) == 0:
            raise ValueError("没有可用的标注数据")

        # 2. 划分数据集
        train_anns, val_anns, test_anns = self._split_dataset(
            annotations,
            dataset_config.split_ratio
        )
        logger.info(
            f"数据集划分完成: train={len(train_anns)}, "
            f"val={len(val_anns)}, test={len(test_anns)}"
        )

        # 3. 转换为 YOLO 格式
        await self._convert_to_yolo(db, 'train', train_anns, dataset_config.classes)
        await self._convert_to_yolo(db, 'val', val_anns, dataset_config.classes)
        await self._convert_to_yolo(db, 'test', test_anns, dataset_config.classes)
        logger.info("YOLO 格式转换完成")

        # 4. 生成 data.yaml
        data_yaml_path = self._generate_data_yaml(dataset_config.classes)
        logger.info(f"data.yaml 生成完成: {data_yaml_path}")

        return DatasetPrepareResult(
            dataset_dir=str(self.dataset_dir),
            data_yaml_path=data_yaml_path,
            train_count=len(train_anns),
            val_count=len(val_anns),
            test_count=len(test_anns),
            classes=dataset_config.classes
        )

    async def _fetch_annotations(
        self,
        db: AsyncSession,
        dataset_config: DatasetConfig
    ) -> List[Annotation]:
        """
        获取标注数据

        Args:
            db: 数据库会话
            dataset_config: 数据集配置

        Returns:
            标注记录列表
        """
        if dataset_config.source == 'annotations' and dataset_config.annotation_task_id:
            # 从指定标注任务获取数据
            annotations, _ = await crud_annotation.get_multi_by_task(
                db=db,
                task_id=dataset_config.annotation_task_id,
                skip=0,
                limit=10000,  # 获取所有
                status='annotated'  # 只获取已标注的
            )
            return list(annotations)
        else:
            # 可以扩展：从其他来源获取数据
            raise ValueError(f"不支持的数据来源: {dataset_config.source}")

    def _split_dataset(
        self,
        annotations: List[Annotation],
        split_ratio: Dict[str, float]
    ) -> Tuple[List[Annotation], List[Annotation], List[Annotation]]:
        """
        划分数据集

        Args:
            annotations: 标注列表
            split_ratio: 划分比例

        Returns:
            (train, val, test) 标注列表
        """
        # 随机打乱
        annotations_shuffled = annotations.copy()
        random.shuffle(annotations_shuffled)

        total = len(annotations_shuffled)
        train_size = int(total * split_ratio['train'])
        val_size = int(total * split_ratio['val'])

        train = annotations_shuffled[:train_size]
        val = annotations_shuffled[train_size:train_size + val_size]
        test = annotations_shuffled[train_size + val_size:]

        return train, val, test

    async def _convert_to_yolo(
        self,
        db: AsyncSession,
        split: str,  # 'train', 'val', 'test'
        annotations: List[Annotation],
        classes: List[str]
    ):
        """
        转换为 YOLO 格式

        Args:
            db: 数据库会话
            split: 数据集划分 (train/val/test)
            annotations: 标注记录列表
            classes: 类别名称列表
        """
        for idx, annotation in enumerate(annotations):
            try:
                # 1. 获取原始图像路径
                image_path = annotation.image_path

                if not image_path or not os.path.exists(image_path):
                    logger.warning(f"图像文件不存在，跳过: {image_path}")
                    continue

                # 2. 复制图像到目标目录
                target_image_name = f"{split}_{idx:06d}.jpg"
                target_image_path = self.dataset_dir / 'images' / split / target_image_name

                # 复制文件
                shutil.copy(image_path, target_image_path)

                # 3. 获取图像尺寸
                with Image.open(target_image_path) as img:
                    img_width, img_height = img.size

                # 4. 转换标注为 YOLO 格式
                yolo_lines = []

                # 解析标注数据
                annotations_data = annotation.annotations_data or []

                # 如果是 Label Studio 格式，需要从 result 中提取
                if isinstance(annotations_data, list) and len(annotations_data) > 0:
                    # Label Studio predictions format
                    if 'result' in annotations_data[0]:
                        results = annotations_data[0]['result']
                    else:
                        results = annotations_data
                else:
                    results = []

                for item in results:
                    # 处理 Label Studio 格式
                    if 'type' in item and item['type'] == 'rectanglelabels':
                        value = item['value']

                        # Label Studio 坐标: x, y (左上角), width, height (百分比)
                        x = value['x'] / 100  # 转换为 0-1
                        y = value['y'] / 100
                        width = value['width'] / 100
                        height = value['height'] / 100

                        # 计算中心点坐标 (YOLO 格式)
                        x_center = x + width / 2
                        y_center = y + height / 2

                        # 获取类别
                        class_name = value['rectanglelabels'][0]

                        # 验证类别
                        if class_name not in classes:
                            logger.warning(f"未知类别，跳过: {class_name}")
                            continue

                        class_id = classes.index(class_name)

                        # YOLO 格式: <class_id> <x_center> <y_center> <width> <height>
                        yolo_lines.append(
                            f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
                        )

                # 5. 保存标注文件
                target_label_path = self.dataset_dir / 'labels' / split / f"{split}_{idx:06d}.txt"

                with open(target_label_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(yolo_lines))

                if idx % 100 == 0:
                    logger.info(f"已处理 {idx}/{len(annotations)} 个 {split} 样本")

            except Exception as e:
                logger.error(f"处理标注 {annotation.id} 失败: {str(e)}", exc_info=True)
                continue

    def _generate_data_yaml(self, classes: List[str]) -> str:
        """
        生成 data.yaml 配置文件

        Args:
            classes: 类别名称列表

        Returns:
            data.yaml 文件路径
        """
        data_yaml = {
            'path': str(self.dataset_dir.absolute()),  # 数据集根目录（绝对路径）
            'train': 'images/train',  # 训练集相对路径
            'val': 'images/val',      # 验证集相对路径
            'test': 'images/test',    # 测试集相对路径
            'nc': len(classes),       # 类别数量
            'names': classes          # 类别名称列表
        }

        yaml_path = self.dataset_dir / 'data.yaml'

        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(data_yaml, f, default_flow_style=False, allow_unicode=True)

        logger.info(f"data.yaml 内容:\n{yaml.dump(data_yaml, allow_unicode=True)}")

        return str(yaml_path)

    def cleanup(self):
        """清理临时文件"""
        try:
            if self.dataset_dir.exists():
                shutil.rmtree(self.dataset_dir)
                logger.info(f"已清理数据集目录: {self.dataset_dir}")
        except Exception as e:
            logger.error(f"清理数据集目录失败: {str(e)}")
