"""
YOLO模型加载器服务
使用单例模式缓存已加载的模型
"""
import os
from typing import Optional
from pathlib import Path
import torch
from ultralytics import YOLO
from loguru import logger

from app.core.config import settings


class ModelLoader:
    """
    YOLO模型加载器（单例模式）
    负责加载、缓存和管理YOLO模型
    """

    _instance: Optional["ModelLoader"] = None
    _model_cache: dict[int, YOLO] = {}
    _current_model_id: Optional[int] = None

    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_model(self, model_id: int, model_path: str) -> YOLO:
        """
        加载YOLO模型

        Args:
            model_id: 模型ID
            model_path: 模型文件路径

        Returns:
            YOLO: 加载的模型实例

        Raises:
            FileNotFoundError: 模型文件不存在
            RuntimeError: 模型加载失败
        """
        # 检查缓存
        if model_id in self._model_cache:
            logger.info(f"从缓存加载模型 ID={model_id}")
            return self._model_cache[model_id]

        # 验证文件存在
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型文件不存在: {model_path}")

        # 验证文件格式
        file_ext = Path(model_path).suffix.lower()
        if file_ext not in [".pt", ".pth"]:
            raise ValueError(f"不支持的模型文件格式: {file_ext}")

        try:
            logger.info(f"加载YOLO模型: {model_path}")

            # 加载模型
            model = YOLO(model_path)

            # 检查CUDA是否可用
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"使用设备: {device}")

            # 将模型移到对应设备
            model.to(device)

            # 缓存模型
            self._model_cache[model_id] = model
            self._current_model_id = model_id

            logger.info(
                f"模型加载成功 ID={model_id}, 设备={device}, 类别数={len(model.names)}"
            )

            return model

        except Exception as e:
            logger.error(f"加载模型失败 ID={model_id}: {str(e)}")
            raise RuntimeError(f"模型加载失败: {str(e)}")

    def get_model(self, model_id: int) -> Optional[YOLO]:
        """
        从缓存获取模型

        Args:
            model_id: 模型ID

        Returns:
            Optional[YOLO]: 模型实例，不存在则返回None
        """
        return self._model_cache.get(model_id)

    def unload_model(self, model_id: int) -> bool:
        """
        卸载模型（从缓存中移除）

        Args:
            model_id: 模型ID

        Returns:
            bool: 是否成功卸载
        """
        if model_id in self._model_cache:
            del self._model_cache[model_id]
            logger.info(f"模型已卸载 ID={model_id}")

            # 如果是当前模型，清空当前模型ID
            if self._current_model_id == model_id:
                self._current_model_id = None

            return True
        return False

    def clear_cache(self):
        """清空所有缓存的模型"""
        self._model_cache.clear()
        self._current_model_id = None
        logger.info("模型缓存已清空")

    def get_current_model_id(self) -> Optional[int]:
        """获取当前模型ID"""
        return self._current_model_id

    def get_cached_model_ids(self) -> list[int]:
        """获取所有缓存的模型ID"""
        return list(self._model_cache.keys())

    @property
    def cache_size(self) -> int:
        """获取缓存中的模型数量"""
        return len(self._model_cache)


# 创建全局模型加载器实例
model_loader = ModelLoader()
