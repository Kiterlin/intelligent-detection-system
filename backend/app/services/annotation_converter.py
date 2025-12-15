"""
标注数据格式转换服务
支持检测结果、Label Studio、YOLO、COCO 等格式之间的转换
"""
import os
import json
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from PIL import Image
from loguru import logger


class AnnotationConverter:
    """标注数据格式转换服务"""

    @staticmethod
    def detection_to_label_studio(
        detection_boxes: List[Dict[str, Any]],
        image_path: str,
        image_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        将检测结果转换为 Label Studio 预标注格式

        Args:
            detection_boxes: 检测框列表，每个包含 class, confidence, bbox
            image_path: 图片本地路径
            image_url: 图片 URL（用于 Label Studio 显示）

        Returns:
            Label Studio 任务格式的字典
        """
        try:
            # 获取图片尺寸
            if os.path.exists(image_path):
                image = Image.open(image_path)
                width, height = image.size
            else:
                # 如果图片不存在，使用默认尺寸
                logger.warning(f"图片文件不存在: {image_path}，使用默认尺寸")
                width, height = 1920, 1080

            # 转换检测框为 Label Studio 格式
            predictions = []
            for box in detection_boxes:
                # 检测框坐标 [x1, y1, x2, y2]
                x1, y1, x2, y2 = box['bbox']

                # 转换为百分比坐标（Label Studio 使用百分比）
                x = (x1 / width) * 100
                y = (y1 / height) * 100
                box_width = ((x2 - x1) / width) * 100
                box_height = ((y2 - y1) / height) * 100

                predictions.append({
                    "value": {
                        "x": round(x, 2),
                        "y": round(y, 2),
                        "width": round(box_width, 2),
                        "height": round(box_height, 2),
                        "rotation": 0,
                        "rectanglelabels": [box['class']]
                    },
                    "from_name": "label",
                    "to_name": "image",
                    "type": "rectanglelabels",
                    "score": box.get('confidence', 1.0)
                })

            # 构建 Label Studio 任务
            task = {
                "data": {
                    "image": image_url or image_path
                }
            }

            # 如果有预测结果，添加到任务中
            if predictions:
                task["predictions"] = [{
                    "result": predictions,
                    "score": sum(p['score'] for p in predictions) / len(predictions)
                }]

            return task

        except Exception as e:
            logger.error(f"转换检测结果到 Label Studio 格式失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def label_studio_to_yolo(
        annotations: List[Dict[str, Any]],
        class_mapping: Dict[str, int],
        output_dir: str
    ) -> Tuple[List[str], List[str]]:
        """
        将 Label Studio 标注转换为 YOLO 格式

        Args:
            annotations: Label Studio 导出的标注列表
            class_mapping: 类别名称到 ID 的映射 {'fish': 0, 'turtle': 1, ...}
            output_dir: 输出目录

        Returns:
            (image_files, label_files): 图片文件列表和标注文件列表
        """
        try:
            os.makedirs(output_dir, exist_ok=True)

            image_files = []
            label_files = []

            for annotation in annotations:
                # 获取图片路径
                image_path = annotation['data'].get('image', '')
                if not image_path:
                    logger.warning("标注数据缺少图片路径，跳过")
                    continue

                image_files.append(image_path)

                # 生成 YOLO 标注文件路径
                image_name = os.path.basename(image_path)
                label_name = os.path.splitext(image_name)[0] + '.txt'
                label_path = os.path.join(output_dir, label_name)

                # 转换标注
                yolo_lines = []

                # 获取标注结果（可能在 annotations 或 predictions 中）
                results = []
                if 'annotations' in annotation and annotation['annotations']:
                    results = annotation['annotations'][0].get('result', [])
                elif 'predictions' in annotation and annotation['predictions']:
                    results = annotation['predictions'][0].get('result', [])

                for result in results:
                    if result.get('type') != 'rectanglelabels':
                        continue

                    value = result['value']
                    class_name = value['rectanglelabels'][0]
                    class_id = class_mapping.get(class_name, 0)

                    # Label Studio 坐标: x, y (左上角), width, height (百分比)
                    # YOLO 坐标: x_center, y_center, width, height (归一化 0-1)
                    x = value['x'] / 100  # 转换为 0-1
                    y = value['y'] / 100
                    width = value['width'] / 100
                    height = value['height'] / 100

                    # 计算中心点坐标
                    x_center = x + width / 2
                    y_center = y + height / 2

                    # YOLO 格式: <class_id> <x_center> <y_center> <width> <height>
                    yolo_lines.append(
                        f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
                    )

                # 写入文件
                with open(label_path, 'w', encoding='utf-8') as f:
                    f.writelines(yolo_lines)

                label_files.append(label_path)

            logger.info(f"成功转换 {len(label_files)} 个标注到 YOLO 格式: {output_dir}")
            return image_files, label_files

        except Exception as e:
            logger.error(f"转换 Label Studio 到 YOLO 格式失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def label_studio_to_coco(
        annotations: List[Dict[str, Any]],
        category_mapping: Dict[str, int],
        output_file: str
    ) -> str:
        """
        将 Label Studio 标注转换为 COCO 格式

        Args:
            annotations: Label Studio 导出的标注列表
            category_mapping: 类别名称到 ID 的映射
            output_file: 输出文件路径

        Returns:
            输出文件路径
        """
        try:
            coco_data = {
                "images": [],
                "annotations": [],
                "categories": []
            }

            # 构建类别列表
            for class_name, class_id in category_mapping.items():
                coco_data["categories"].append({
                    "id": class_id,
                    "name": class_name,
                    "supercategory": "object"
                })

            annotation_id = 1

            for image_id, annotation in enumerate(annotations, start=1):
                # 获取图片信息
                image_path = annotation['data'].get('image', '')
                if not image_path:
                    continue

                # 尝试获取图片尺寸
                if os.path.exists(image_path):
                    try:
                        image = Image.open(image_path)
                        img_width, img_height = image.size
                    except Exception:
                        img_width, img_height = 1920, 1080
                else:
                    img_width, img_height = 1920, 1080

                # 添加图片信息
                coco_data["images"].append({
                    "id": image_id,
                    "file_name": os.path.basename(image_path),
                    "width": img_width,
                    "height": img_height
                })

                # 获取标注结果
                results = []
                if 'annotations' in annotation and annotation['annotations']:
                    results = annotation['annotations'][0].get('result', [])
                elif 'predictions' in annotation and annotation['predictions']:
                    results = annotation['predictions'][0].get('result', [])

                # 转换标注
                for result in results:
                    if result.get('type') != 'rectanglelabels':
                        continue

                    value = result['value']
                    class_name = value['rectanglelabels'][0]
                    category_id = category_mapping.get(class_name, 1)

                    # 转换坐标（COCO 使用绝对坐标，左上角 + 宽高）
                    x = (value['x'] / 100) * img_width
                    y = (value['y'] / 100) * img_height
                    bbox_width = (value['width'] / 100) * img_width
                    bbox_height = (value['height'] / 100) * img_height

                    coco_data["annotations"].append({
                        "id": annotation_id,
                        "image_id": image_id,
                        "category_id": category_id,
                        "bbox": [x, y, bbox_width, bbox_height],
                        "area": bbox_width * bbox_height,
                        "iscrowd": 0,
                        "segmentation": []
                    })

                    annotation_id += 1

            # 写入 JSON 文件
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(coco_data, f, indent=2, ensure_ascii=False)

            logger.info(
                f"成功转换 {len(coco_data['images'])} 张图片、"
                f"{len(coco_data['annotations'])} 个标注到 COCO 格式: {output_file}"
            )
            return output_file

        except Exception as e:
            logger.error(f"转换 Label Studio 到 COCO 格式失败: {str(e)}", exc_info=True)
            raise

    @staticmethod
    def create_yolo_dataset(
        image_files: List[str],
        label_files: List[str],
        output_dir: str,
        class_names: List[str],
        train_split: float = 0.8
    ) -> Dict[str, str]:
        """
        创建完整的 YOLO 数据集目录结构

        Args:
            image_files: 图片文件列表
            label_files: 标注文件列表
            output_dir: 输出目录
            class_names: 类别名称列表
            train_split: 训练集比例（默认 0.8）

        Returns:
            数据集配置信息（包含 yaml 文件路径等）
        """
        try:
            import shutil
            import random

            # 创建目录结构
            dataset_dir = Path(output_dir)
            (dataset_dir / 'images' / 'train').mkdir(parents=True, exist_ok=True)
            (dataset_dir / 'images' / 'val').mkdir(parents=True, exist_ok=True)
            (dataset_dir / 'labels' / 'train').mkdir(parents=True, exist_ok=True)
            (dataset_dir / 'labels' / 'val').mkdir(parents=True, exist_ok=True)

            # 随机划分训练集和验证集
            indices = list(range(len(image_files)))
            random.shuffle(indices)
            split_idx = int(len(indices) * train_split)
            train_indices = set(indices[:split_idx])

            # 复制文件
            for i, (img_file, label_file) in enumerate(zip(image_files, label_files)):
                subset = 'train' if i in train_indices else 'val'

                # 复制图片
                if os.path.exists(img_file):
                    shutil.copy(img_file, dataset_dir / 'images' / subset / os.path.basename(img_file))

                # 复制标注
                if os.path.exists(label_file):
                    shutil.copy(label_file, dataset_dir / 'labels' / subset / os.path.basename(label_file))

            # 创建 data.yaml 文件
            yaml_content = f"""# YOLO Dataset Configuration
path: {dataset_dir.absolute()}
train: images/train
val: images/val

# Classes
nc: {len(class_names)}
names: {class_names}
"""

            yaml_path = dataset_dir / 'data.yaml'
            with open(yaml_path, 'w', encoding='utf-8') as f:
                f.write(yaml_content)

            # 创建 classes.txt
            classes_path = dataset_dir / 'classes.txt'
            with open(classes_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(class_names))

            logger.info(
                f"成功创建 YOLO 数据集: {dataset_dir}\n"
                f"  训练集: {len(train_indices)} 张\n"
                f"  验证集: {len(indices) - len(train_indices)} 张"
            )

            return {
                'dataset_dir': str(dataset_dir),
                'yaml_path': str(yaml_path),
                'classes_path': str(classes_path),
                'train_count': len(train_indices),
                'val_count': len(indices) - len(train_indices)
            }

        except Exception as e:
            logger.error(f"创建 YOLO 数据集失败: {str(e)}", exc_info=True)
            raise


# 创建全局转换器实例
annotation_converter = AnnotationConverter()
