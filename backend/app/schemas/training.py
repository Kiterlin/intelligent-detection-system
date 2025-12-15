"""
训练任务相关的 Pydantic Schemas
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# ============ 训练配置 Schemas ============

class TrainingConfig(BaseModel):
    """训练配置"""
    base_model: str = Field(..., description="基础模型名称，如 'yolov8n.pt'")
    epochs: int = Field(100, description="训练轮次", ge=1, le=1000)
    batch_size: int = Field(16, description="批次大小", ge=1, le=128)
    img_size: int = Field(640, description="图像尺寸", ge=320, le=1280)
    learning_rate: float = Field(0.01, description="学习率", gt=0, le=1)
    optimizer: str = Field("SGD", description="优化器 (SGD, Adam, AdamW)")

    # 数据增强配置
    augmentation: Optional[Dict[str, Any]] = Field(None, description="数据增强配置")

    # 设备配置
    device: str = Field("0", description="GPU 设备 ID")
    workers: int = Field(8, description="数据加载工作线程数", ge=0, le=32)
    patience: int = Field(50, description="早停耐心值", ge=0, le=200)

    class Config:
        json_schema_extra = {
            "example": {
                "base_model": "yolov8n.pt",
                "epochs": 100,
                "batch_size": 16,
                "img_size": 640,
                "learning_rate": 0.01,
                "optimizer": "SGD",
                "augmentation": {
                    "hsv_h": 0.015,
                    "hsv_s": 0.7,
                    "hsv_v": 0.4,
                    "degrees": 0.0,
                    "translate": 0.1,
                    "scale": 0.5,
                    "flipud": 0.5,
                    "fliplr": 0.5
                },
                "device": "0",
                "workers": 8,
                "patience": 50
            }
        }


class DatasetConfig(BaseModel):
    """数据集配置"""
    source: str = Field(..., description="数据来源 (annotations | dataset_id)")
    annotation_task_id: Optional[int] = Field(None, description="标注任务 ID")

    # 数据集划分比例
    split_ratio: Dict[str, float] = Field(
        default={"train": 0.8, "val": 0.15, "test": 0.05},
        description="数据集划分比例"
    )

    # 类别列表
    classes: List[str] = Field(..., description="类别名称列表")

    class Config:
        json_schema_extra = {
            "example": {
                "source": "annotations",
                "annotation_task_id": 1,
                "split_ratio": {
                    "train": 0.8,
                    "val": 0.15,
                    "test": 0.05
                },
                "classes": ["fish", "coral", "turtle"]
            }
        }


# ============ 训练任务 Schemas ============

class TrainingJobBase(BaseModel):
    """训练任务基础模型"""
    job_name: str = Field(..., description="任务名称", min_length=1, max_length=200)


class TrainingJobCreate(TrainingJobBase):
    """创建训练任务"""
    base_model_id: int = Field(..., description="基础模型 ID", gt=0)
    config_json: TrainingConfig = Field(..., description="训练配置")
    dataset_config: DatasetConfig = Field(..., description="数据集配置")


class TrainingJobUpdate(BaseModel):
    """更新训练任务"""
    job_name: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[str] = Field(None, description="任务状态")
    current_epoch: Optional[int] = Field(None, ge=0)
    progress_percentage: Optional[float] = Field(None, ge=0, le=100)
    error_message: Optional[str] = None


class TrainingJobInDB(TrainingJobBase):
    """数据库中的训练任务"""
    id: int
    admin_id: int
    base_model_id: int
    new_model_id: Optional[int] = None
    status: str

    config_json: Dict[str, Any]
    dataset_config: Optional[Dict[str, Any]] = None

    log_file_path: Optional[str] = None
    weights_path: Optional[str] = None
    results_path: Optional[str] = None

    metrics_json: Optional[Dict[str, Any]] = None

    current_epoch: Optional[int] = 0
    total_epochs: Optional[int] = None
    progress_percentage: Optional[float] = 0.0

    error_message: Optional[str] = None

    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TrainingJobResponse(TrainingJobInDB):
    """API 返回的训练任务"""
    pass


class TrainingJobListResponse(BaseModel):
    """训练任务列表响应"""
    total: int = Field(..., description="总数")
    items: List[TrainingJobResponse] = Field(..., description="训练任务列表")


# ============ 训练指标 Schemas ============

class TrainingMetrics(BaseModel):
    """训练性能指标"""
    mAP50: Optional[float] = Field(None, description="mAP@0.5", ge=0, le=1)
    mAP50_95: Optional[float] = Field(None, description="mAP@0.5:0.95", ge=0, le=1)
    precision: Optional[float] = Field(None, description="精确率", ge=0, le=1)
    recall: Optional[float] = Field(None, description="召回率", ge=0, le=1)
    box_loss: Optional[float] = Field(None, description="边界框损失", ge=0)
    cls_loss: Optional[float] = Field(None, description="分类损失", ge=0)
    dfl_loss: Optional[float] = Field(None, description="DFL 损失", ge=0)

    class Config:
        json_schema_extra = {
            "example": {
                "mAP50": 0.85,
                "mAP50_95": 0.72,
                "precision": 0.88,
                "recall": 0.82,
                "box_loss": 0.045,
                "cls_loss": 0.032,
                "dfl_loss": 0.015
            }
        }


# ============ 数据准备结果 Schemas ============

class DatasetPrepareResult(BaseModel):
    """数据集准备结果"""
    dataset_dir: str = Field(..., description="数据集目录")
    data_yaml_path: str = Field(..., description="data.yaml 文件路径")
    train_count: int = Field(..., description="训练集数量", ge=0)
    val_count: int = Field(..., description="验证集数量", ge=0)
    test_count: int = Field(..., description="测试集数量", ge=0)
    classes: List[str] = Field(..., description="类别列表")
