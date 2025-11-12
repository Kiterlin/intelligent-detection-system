"""
检测服务
提供图像和视频的目标检测功能
"""
import json
import time
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
from ultralytics.engine.results import Results
from loguru import logger

from app.core.config import settings


class DetectionService:
    """
    目标检测服务
    处理图像和视频的YOLO推理
    """

    def __init__(self, model: YOLO):
        """
        初始化检测服务

        Args:
            model: YOLO模型实例
        """
        self.model = model
        self.class_names = model.names

    def detect_image(
        self,
        image_path: str,
        confidence_threshold: float = 0.25,
        iou_threshold: float = 0.45,
    ) -> Tuple[List[Dict[str, Any]], np.ndarray]:
        """
        对单张图像进行目标检测

        Args:
            image_path: 图像文件路径
            confidence_threshold: 置信度阈值
            iou_threshold: IOU阈值

        Returns:
            (检测结果列表, 标注后的图像数组) 元组

        Raises:
            FileNotFoundError: 图像文件不存在
            ValueError: 图像格式不支持
        """
        # 验证文件存在
        if not Path(image_path).exists():
            raise FileNotFoundError(f"图像文件不存在: {image_path}")

        # 验证图像格式
        file_ext = Path(image_path).suffix.lower()
        if file_ext not in settings.SUPPORTED_IMAGE_FORMATS:
            raise ValueError(f"不支持的图像格式: {file_ext}")

        try:
            logger.info(f"开始检测图像: {image_path}")
            start_time = time.time()

            # 读取图像
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"无法读取图像: {image_path}")

            # 执行推理
            results = self.model.predict(
                source=image,
                conf=confidence_threshold,
                iou=iou_threshold,
                verbose=False,
            )

            # 解析结果
            detections = self._parse_results(results[0])

            # 绘制检测框
            annotated_image = self._draw_detections(image, detections)

            elapsed_time = time.time() - start_time
            logger.info(
                f"图像检测完成: {len(detections)}个对象, 耗时{elapsed_time:.2f}秒"
            )

            return detections, annotated_image

        except Exception as e:
            logger.error(f"图像检测失败: {str(e)}")
            raise

    def detect_video(
        self,
        video_path: str,
        output_path: str,
        confidence_threshold: float = 0.25,
        iou_threshold: float = 0.45,
        progress_callback: Optional[callable] = None,
    ) -> Tuple[List[Dict[str, Any]], float]:
        """
        对视频进行目标检测

        Args:
            video_path: 视频文件路径
            output_path: 输出视频路径
            confidence_threshold: 置信度阈值
            iou_threshold: IOU阈值
            progress_callback: 进度回调函数（参数：当前帧数，总帧数）

        Returns:
            (汇总的检测结果列表, 处理时间) 元组

        Raises:
            FileNotFoundError: 视频文件不存在
            ValueError: 视频格式不支持
        """
        # 验证文件存在
        if not Path(video_path).exists():
            raise FileNotFoundError(f"视频文件不存在: {video_path}")

        # 验证视频格式
        file_ext = Path(video_path).suffix.lower()
        if file_ext not in settings.SUPPORTED_VIDEO_FORMATS:
            raise ValueError(f"不支持的视频格式: {file_ext}")

        try:
            logger.info(f"开始检测视频: {video_path}")
            start_time = time.time()

            # 打开视频
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"无法打开视频: {video_path}")

            # 获取视频属性
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            logger.info(
                f"视频属性: {width}x{height}, {fps}fps, {total_frames}帧"
            )

            # 创建输出视频编写器
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

            # 汇总所有帧的检测结果
            all_detections = []
            frame_count = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                frame_count += 1

                # 执行检测
                results = self.model.predict(
                    source=frame,
                    conf=confidence_threshold,
                    iou=iou_threshold,
                    verbose=False,
                )

                # 解析结果
                detections = self._parse_results(results[0])
                all_detections.extend(detections)

                # 绘制检测框
                annotated_frame = self._draw_detections(frame, detections)

                # 写入输出视频
                out.write(annotated_frame)

                # 更新进度
                if progress_callback and frame_count % 10 == 0:
                    progress_callback(frame_count, total_frames)

            # 释放资源
            cap.release()
            out.release()

            elapsed_time = time.time() - start_time
            logger.info(
                f"视频检测完成: {len(all_detections)}个对象, 耗时{elapsed_time:.2f}秒"
            )

            return all_detections, elapsed_time

        except Exception as e:
            logger.error(f"视频检测失败: {str(e)}")
            raise

    def _parse_results(self, result: Results) -> List[Dict[str, Any]]:
        """
        解析YOLO检测结果

        Args:
            result: YOLO Results对象

        Returns:
            检测结果列表
        """
        detections = []

        if result.boxes is None or len(result.boxes) == 0:
            return detections

        # 提取检测框信息
        boxes = result.boxes.xyxy.cpu().numpy()  # [x1, y1, x2, y2]
        confidences = result.boxes.conf.cpu().numpy()
        class_ids = result.boxes.cls.cpu().numpy().astype(int)

        for i in range(len(boxes)):
            detection = {
                "class_id": int(class_ids[i]),
                "class_name": self.class_names[class_ids[i]],
                "confidence": float(confidences[i]),
                "bbox": boxes[i].tolist(),  # [x1, y1, x2, y2]
            }
            detections.append(detection)

        return detections

    def _draw_detections(
        self, image: np.ndarray, detections: List[Dict[str, Any]]
    ) -> np.ndarray:
        """
        在图像上绘制检测框和标签

        Args:
            image: 原始图像数组
            detections: 检测结果列表

        Returns:
            标注后的图像数组
        """
        # 复制图像以避免修改原图
        annotated_image = image.copy()

        for det in detections:
            # 获取边界框坐标
            x1, y1, x2, y2 = map(int, det["bbox"])

            # 生成颜色（基于类别ID）
            color = self._get_color(det["class_id"])

            # 绘制边界框
            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 2)

            # 准备标签文本
            label = f"{det['class_name']} {det['confidence']:.2f}"

            # 计算文本大小
            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )

            # 绘制标签背景
            cv2.rectangle(
                annotated_image,
                (x1, y1 - text_height - baseline - 5),
                (x1 + text_width, y1),
                color,
                -1,
            )

            # 绘制标签文本
            cv2.putText(
                annotated_image,
                label,
                (x1, y1 - baseline - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )

        return annotated_image

    def _get_color(self, class_id: int) -> Tuple[int, int, int]:
        """
        根据类别ID生成颜色

        Args:
            class_id: 类别ID

        Returns:
            BGR颜色元组
        """
        # 使用固定的颜色种子以保证同一类别颜色一致
        np.random.seed(class_id)
        color = tuple(map(int, np.random.randint(0, 255, 3)))
        return color

    def save_annotated_image(self, image: np.ndarray, output_path: str):
        """
        保存标注后的图像

        Args:
            image: 图像数组
            output_path: 输出路径
        """
        cv2.imwrite(output_path, image)
        logger.info(f"标注图像已保存: {output_path}")

    def results_to_json(self, detections: List[Dict[str, Any]]) -> str:
        """
        将检测结果转换为JSON字符串

        Args:
            detections: 检测结果列表

        Returns:
            JSON字符串
        """
        return json.dumps(detections, ensure_ascii=False)
