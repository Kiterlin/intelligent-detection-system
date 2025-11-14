# Phase 2 Stage 7 实施计划：模型训练系统

**计划创建时间**: 2025-11-14
**预计工作量**: 4-5 天
**状态**: ⏸️ 待开始
**优先级**: 🔸 中低（Stage 5-6 后）
**难度**: 🔥🔥🔥 高

---

## 📊 概述

实现在线模型训练/微调系统，利用用户标注的高质量数据训练定制化的 YOLO 模型，完成 AI 系统的闭环。

### 核心价值
- **AI 闭环的终点和回报**
- 利用真值数据训练更强的定制化模型
- 建立系统的"护城河"
- 实现持续的模型优化

---

## 🎯 功能需求

### 1. 训练任务管理
- ✅ 创建训练任务
- ✅ 训练任务列表查看
- ✅ 实时进度监控
- ✅ 训练日志查看
- ✅ 任务取消/重启

### 2. 数据准备
- ✅ 从标注数据自动生成训练集
- ✅ 数据集划分（训练/验证/测试）
- ✅ YOLO 格式转换
- ✅ 自动生成 data.yaml 配置

### 3. 训练配置
- ✅ 选择基础模型（YOLOv5/v8 各版本）
- ✅ 训练参数配置（epochs、batch size、learning rate）
- ✅ 数据增强选项
- ✅ GPU 设备选择

### 4. 模型评估
- ✅ 训练完成自动注册模型
- ✅ 性能指标展示（mAP、Precision、Recall）
- ✅ 训练曲线可视化
- ✅ 模型对比与 A/B 测试

---

## 🏗️ 架构设计

### 数据库设计

#### 新表：`training_jobs`
```sql
CREATE TABLE training_jobs (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_name VARCHAR(200) NOT NULL,
    base_model_id INTEGER NOT NULL REFERENCES ml_models(id),
    status VARCHAR(50) NOT NULL,         -- 'pending', 'preparing', 'training', 'completed', 'failed', 'cancelled'
    new_model_id INTEGER REFERENCES ml_models(id),  -- 训练完成后的新模型ID

    -- 训练参数
    config_json JSONB NOT NULL,          -- 训练配置参数
    dataset_config JSONB,                -- 数据集配置

    -- 输出文件
    log_file_path VARCHAR(500),          -- 训练日志文件
    weights_path VARCHAR(500),           -- 最终权重文件 (best.pt)
    results_path VARCHAR(500),           -- 结果目录

    -- 性能指标
    metrics_json JSONB,                  -- 训练结果指标 (mAP, precision, recall)

    -- 进度跟踪
    current_epoch INTEGER DEFAULT 0,     -- 当前轮次
    total_epochs INTEGER,                -- 总轮次
    progress_percentage FLOAT DEFAULT 0, -- 进度百分比

    -- 错误信息
    error_message TEXT,

    -- 时间戳
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    INDEX idx_admin_id (admin_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

#### 配置 JSON 结构
```json
{
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
    "shear": 0.0,
    "flipud": 0.5,
    "fliplr": 0.5,
    "mosaic": 1.0
  },
  "device": "0",  // GPU 设备 ID
  "workers": 8,
  "patience": 50
}
```

#### 数据集配置 JSON
```json
{
  "source": "annotations",  // 'annotations' | 'dataset_id'
  "annotation_ids": [1, 2, 3, ...],  // 使用的标注数据ID
  "split_ratio": {
    "train": 0.8,
    "val": 0.15,
    "test": 0.05
  },
  "classes": ["fish", "coral", "diver"],
  "total_images": 150
}
```

---

## 🔧 技术方案

### 系统架构

```
┌─────────────┐
│   管理员UI   │
└──────┬──────┘
       │ POST /api/v1/admin/training
       ▼
┌─────────────────┐
│   FastAPI       │
│   创建训练任务   │
└──────┬──────────┘
       │ Celery Task
       ▼
┌─────────────────────────────────┐
│   GPU Celery Worker             │
│   (专用队列: training)          │
│                                 │
│   1. 准备数据 (YOLO 格式)       │
│   2. 生成 data.yaml             │
│   3. 调用 YOLO 训练             │
│   4. 收集日志和结果             │
│   5. 注册新模型                 │
└─────────────────────────────────┘
       │
       ▼
┌─────────────────┐
│   存储          │
│   - best.pt     │
│   - logs/       │
│   - results/    │
└─────────────────┘
```

### GPU Celery Worker 配置

#### 1. 独立的 GPU Worker
```bash
# 启动 GPU 训练 Worker
celery -A app.core.celery_app worker \
  -Q training \
  -n training-worker@%h \
  --loglevel=info \
  --concurrency=1 \
  --pool=solo  # 重要：使用 solo pool 避免多进程问题
```

**为什么使用 solo pool？**
- GPU 不支持多进程共享
- YOLO 训练本身已经使用多线程
- 避免 CUDA 初始化冲突

#### 2. 队列隔离配置
```python
# backend/app/core/celery_app.py

CELERY_TASK_ROUTES = {
    'app.tasks.detection_tasks.*': {'queue': 'detection'},
    'app.tasks.report_tasks.*': {'queue': 'reports'},
    'app.tasks.training_tasks.*': {'queue': 'training'},  # 新增
}

# 任务优先级
CELERY_TASK_PRIORITY = {
    'training': 1,    # 最低优先级
    'detection': 5,   # 高优先级
    'reports': 3      # 中等优先级
}
```

---

## 📁 文件结构

```
backend/
├── app/
│   ├── api/v1/admin/
│   │   └── training.py                 # 训练任务 API（管理员专用）
│   ├── crud/
│   │   └── training.py                 # 训练任务 CRUD 操作
│   ├── schemas/
│   │   └── training.py                 # 训练数据模型
│   ├── services/
│   │   ├── training_service.py         # 训练服务
│   │   ├── data_preparation.py         # 数据准备服务 ⭐
│   │   └── model_registry.py           # 模型注册服务
│   ├── tasks/
│   │   └── training_tasks.py           # Celery 训练任务 ⭐
│   └── utils/
│       ├── yolo_trainer.py             # YOLO 训练封装
│       └── log_parser.py               # 训练日志解析
│
├── storage/
│   └── training/
│       ├── datasets/                    # 训练数据集
│       │   ├── job_1/
│       │   │   ├── images/
│       │   │   │   ├── train/
│       │   │   │   ├── val/
│       │   │   │   └── test/
│       │   │   ├── labels/
│       │   │   │   ├── train/
│       │   │   │   ├── val/
│       │   │   │   └── test/
│       │   │   └── data.yaml
│       ├── weights/                     # 训练后的权重
│       │   └── job_1_best.pt
│       └── logs/                        # 训练日志
│           └── job_1.log
│
frontend/
└── src/
    └── views/
        └── admin/
            ├── Training.vue            # 训练任务列表页
            ├── TrainingCreate.vue      # 创建训练任务页
            └── TrainingMonitor.vue     # 训练监控页
```

---

## 🚀 实施步骤

### Step 1: 数据库迁移（0.5 天）

```bash
alembic revision -m "add_training_jobs_table"
alembic upgrade head
```

**任务清单**：
- [ ] 创建 `training_jobs` 表
- [ ] 添加必要的索引
- [ ] 创建存储目录结构

---

### Step 2: 数据准备服务（1.5 天）⭐ 核心难点

#### 2.1 数据准备服务（services/data_preparation.py）

这是**最难的部分**，需要将标注数据转换为 YOLO 训练格式。

```python
import os
import shutil
import yaml
from typing import List, Tuple
from PIL import Image
from app.crud import annotation as annotation_crud
from app.schemas.training import DatasetConfig

class DataPreparationService:
    """数据准备服务"""

    def __init__(self, job_id: int, output_dir: str):
        self.job_id = job_id
        self.output_dir = output_dir
        self.dataset_dir = f"{output_dir}/datasets/job_{job_id}"

        # 创建目录结构
        for split in ['train', 'val', 'test']:
            os.makedirs(f"{self.dataset_dir}/images/{split}", exist_ok=True)
            os.makedirs(f"{self.dataset_dir}/labels/{split}", exist_ok=True)

    async def prepare_dataset(
        self,
        db: AsyncSession,
        dataset_config: DatasetConfig
    ) -> str:
        """
        准备训练数据集
        返回 data.yaml 文件路径
        """
        # 1. 获取所有标注数据
        annotations = await self._fetch_annotations(db, dataset_config)

        # 2. 划分数据集
        train_anns, val_anns, test_anns = self._split_dataset(
            annotations,
            dataset_config.split_ratio
        )

        # 3. 转换为 YOLO 格式
        await self._convert_to_yolo(db, 'train', train_anns, dataset_config.classes)
        await self._convert_to_yolo(db, 'val', val_anns, dataset_config.classes)
        await self._convert_to_yolo(db, 'test', test_anns, dataset_config.classes)

        # 4. 生成 data.yaml
        data_yaml_path = self._generate_data_yaml(dataset_config.classes)

        return data_yaml_path

    async def _fetch_annotations(
        self,
        db: AsyncSession,
        dataset_config: DatasetConfig
    ) -> List[Annotation]:
        """获取标注数据"""
        if dataset_config.source == 'annotations':
            # 使用指定的标注ID
            annotations = []
            for ann_id in dataset_config.annotation_ids:
                ann = await annotation_crud.get_annotation(db, ann_id)
                if ann and ann.is_corrected:
                    annotations.append(ann)
        else:
            # 使用所有已修正的标注
            annotations = await annotation_crud.get_all_corrected_annotations(db)

        return annotations

    def _split_dataset(
        self,
        annotations: List[Annotation],
        split_ratio: dict
    ) -> Tuple[List, List, List]:
        """划分数据集"""
        import random
        random.shuffle(annotations)

        total = len(annotations)
        train_size = int(total * split_ratio['train'])
        val_size = int(total * split_ratio['val'])

        train = annotations[:train_size]
        val = annotations[train_size:train_size + val_size]
        test = annotations[train_size + val_size:]

        return train, val, test

    async def _convert_to_yolo(
        self,
        db: AsyncSession,
        split: str,  # 'train', 'val', 'test'
        annotations: List[Annotation],
        classes: List[str]
    ):
        """转换为 YOLO 格式"""
        for idx, annotation in enumerate(annotations):
            # 1. 获取原始图像
            history = await self._get_detection_history(db, annotation.history_id)
            image_path = history.image_path  # 原始图像路径

            # 2. 复制图像到目标目录
            target_image_name = f"{split}_{idx}.jpg"
            target_image_path = f"{self.dataset_dir}/images/{split}/{target_image_name}"
            shutil.copy(image_path, target_image_path)

            # 3. 获取图像尺寸
            with Image.open(target_image_path) as img:
                img_width, img_height = img.size

            # 4. 转换标注为 YOLO 格式
            yolo_lines = []
            for item in annotation.annotation_json['annotations']:
                # YOLO 格式：<class_id> <x_center> <y_center> <width> <height>
                # 坐标归一化到 [0, 1]
                x1, y1, x2, y2 = item['bbox']

                x_center = ((x1 + x2) / 2) / img_width
                y_center = ((y1 + y2) / 2) / img_height
                width = (x2 - x1) / img_width
                height = (y2 - y1) / img_height

                class_id = classes.index(item['class_name'])

                yolo_lines.append(
                    f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
                )

            # 5. 保存标注文件
            target_label_path = f"{self.dataset_dir}/labels/{split}/{split}_{idx}.txt"
            with open(target_label_path, 'w') as f:
                f.write('\n'.join(yolo_lines))

    def _generate_data_yaml(self, classes: List[str]) -> str:
        """生成 data.yaml 配置文件"""
        data_yaml = {
            'path': self.dataset_dir,  # 数据集根目录
            'train': 'images/train',   # 训练集相对路径
            'val': 'images/val',       # 验证集相对路径
            'test': 'images/test',     # 测试集相对路径
            'nc': len(classes),        # 类别数量
            'names': classes           # 类别名称列表
        }

        yaml_path = f"{self.dataset_dir}/data.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(data_yaml, f, default_flow_style=False)

        return yaml_path

    async def _get_detection_history(self, db: AsyncSession, history_id: int):
        """获取检测历史记录"""
        result = await db.execute(
            select(DetectionHistory).where(DetectionHistory.id == history_id)
        )
        return result.scalar_one()
```

**任务清单**：
- [ ] 实现数据获取逻辑
- [ ] 实现数据集划分
- [ ] 实现 YOLO 格式转换（⭐ 核心难点）
- [ ] 实现 data.yaml 生成
- [ ] 添加数据验证逻辑
- [ ] 处理边界情况（空标注、无效图像等）

---

### Step 3: 训练任务实现（1.5 天）

#### 3.1 YOLO 训练封装（utils/yolo_trainer.py）
```python
import sys
import logging
from ultralytics import YOLO
from pathlib import Path

class YOLOTrainer:
    """YOLO 训练封装"""

    def __init__(self, log_file: str = None):
        self.log_file = log_file
        self.logger = self._setup_logger()

    def _setup_logger(self):
        """设置日志"""
        logger = logging.getLogger('yolo_trainer')
        logger.setLevel(logging.INFO)

        # 输出到文件
        if self.log_file:
            handler = logging.FileHandler(self.log_file)
            handler.setFormatter(
                logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            )
            logger.addHandler(handler)

        return logger

    def train(
        self,
        base_model: str,
        data_yaml: str,
        config: dict,
        progress_callback=None
    ) -> dict:
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
            self.logger.info(f"Loading base model: {base_model}")
            model = YOLO(base_model)

            # 2. 重定向 stdout 到日志文件
            if self.log_file:
                sys.stdout = open(self.log_file, 'a')
                sys.stderr = open(self.log_file, 'a')

            # 3. 开始训练
            self.logger.info("Starting training...")
            results = model.train(
                data=data_yaml,
                epochs=config.get('epochs', 100),
                batch=config.get('batch_size', 16),
                imgsz=config.get('img_size', 640),
                lr0=config.get('learning_rate', 0.01),
                optimizer=config.get('optimizer', 'SGD'),
                device=config.get('device', '0'),
                workers=config.get('workers', 8),
                patience=config.get('patience', 50),
                save=True,
                plots=True,
                verbose=True
            )

            # 4. 恢复 stdout
            if self.log_file:
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__

            # 5. 获取最佳权重路径
            best_weights = Path(results.save_dir) / 'weights' / 'best.pt'

            # 6. 提取性能指标
            metrics = self._extract_metrics(results)

            self.logger.info("Training completed successfully")

            return {
                'success': True,
                'best_weights': str(best_weights),
                'results_dir': str(results.save_dir),
                'metrics': metrics
            }

        except Exception as e:
            self.logger.error(f"Training failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _extract_metrics(self, results) -> dict:
        """提取训练指标"""
        return {
            'mAP50': float(results.results_dict.get('metrics/mAP50(B)', 0)),
            'mAP50-95': float(results.results_dict.get('metrics/mAP50-95(B)', 0)),
            'precision': float(results.results_dict.get('metrics/precision(B)', 0)),
            'recall': float(results.results_dict.get('metrics/recall(B)', 0)),
            'box_loss': float(results.results_dict.get('train/box_loss', 0)),
            'cls_loss': float(results.results_dict.get('train/cls_loss', 0)),
            'dfl_loss': float(results.results_dict.get('train/dfl_loss', 0))
        }
```

#### 3.2 Celery 训练任务（tasks/training_tasks.py）
```python
import os
import shutil
from celery import Task
from app.core.celery_app import celery_app
from app.crud import training as training_crud
from app.services.data_preparation import DataPreparationService
from app.services.model_registry import ModelRegistryService
from app.utils.yolo_trainer import YOLOTrainer

class TrainingTask(Task):
    """训练任务基类"""
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败处理"""
        job_id = args[0]
        # 更新状态为 failed
        training_crud.update_job_status(
            job_id=job_id,
            status='failed',
            error_message=str(exc)
        )

@celery_app.task(base=TrainingTask, bind=True, queue='training')
async def start_training_task(self, job_id: int):
    """
    启动模型训练任务

    这是一个长时间运行的任务，可能需要数小时甚至数天
    """
    db = get_db_session()

    try:
        # 1. 获取训练任务
        job = await training_crud.get_job(db, job_id)
        if not job:
            raise ValueError(f"Training job {job_id} not found")

        # 2. 更新状态：准备数据
        await training_crud.update_job_status(db, job_id, 'preparing')

        # 3. 准备训练数据
        data_prep = DataPreparationService(
            job_id=job_id,
            output_dir='storage/training'
        )

        data_yaml_path = await data_prep.prepare_dataset(
            db=db,
            dataset_config=job.dataset_config
        )

        logging.info(f"Dataset prepared: {data_yaml_path}")

        # 4. 更新状态：开始训练
        await training_crud.update_job_status(
            db,
            job_id,
            'training',
            started_at=datetime.now()
        )

        # 5. 执行训练
        log_file = f"storage/training/logs/job_{job_id}.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        trainer = YOLOTrainer(log_file=log_file)

        # 获取基础模型路径
        base_model = await self._get_base_model_path(db, job.base_model_id)

        # 开始训练（这将阻塞数小时）
        result = trainer.train(
            base_model=base_model,
            data_yaml=data_yaml_path,
            config=job.config_json
        )

        if not result['success']:
            raise Exception(result['error'])

        # 6. 复制最佳权重到存储目录
        weights_dir = 'storage/models'
        os.makedirs(weights_dir, exist_ok=True)

        final_weights_path = f"{weights_dir}/job_{job_id}_best.pt"
        shutil.copy(result['best_weights'], final_weights_path)

        logging.info(f"Weights saved to: {final_weights_path}")

        # 7. 注册新模型
        model_registry = ModelRegistryService()
        new_model = await model_registry.register_trained_model(
            db=db,
            job=job,
            weights_path=final_weights_path,
            metrics=result['metrics']
        )

        # 8. 更新训练任务状态
        await training_crud.update_job_status(
            db,
            job_id,
            'completed',
            new_model_id=new_model.id,
            weights_path=final_weights_path,
            log_file_path=log_file,
            results_path=result['results_dir'],
            metrics_json=result['metrics'],
            completed_at=datetime.now()
        )

        logging.info(f"Training job {job_id} completed successfully")

    except Exception as e:
        logging.error(f"Training job {job_id} failed: {e}")
        raise

    finally:
        db.close()

async def _get_base_model_path(db, model_id: int) -> str:
    """获取基础模型路径"""
    result = await db.execute(
        select(MLModel).where(MLModel.id == model_id)
    )
    model = result.scalar_one()
    return model.model_path
```

**任务清单**：
- [ ] 实现 YOLO 训练封装
- [ ] 实现 Celery 训练任务
- [ ] 实现日志收集
- [ ] 实现进度跟踪
- [ ] 实现错误处理

---

### Step 4: API 和前端实现（1 天）

#### 4.1 API 端点（api/v1/admin/training.py）
```python
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.training import TrainingJobCreate, TrainingJobResponse
from app.tasks.training_tasks import start_training_task

router = APIRouter(prefix="/admin/training", tags=["admin", "training"])

@router.post("/", response_model=TrainingJobResponse)
async def create_training_job(
    job_data: TrainingJobCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """创建训练任务（仅管理员）"""
    # 1. 创建任务记录
    job = await training_crud.create_job(
        db=db,
        admin_id=current_user.id,
        job_data=job_data
    )

    # 2. 启动异步训练任务
    start_training_task.delay(job.id)

    return job

@router.get("/", response_model=List[TrainingJobResponse])
async def get_training_jobs(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取训练任务列表（仅管理员）"""
    return await training_crud.get_jobs(db, skip=skip, limit=limit)

@router.get("/{job_id}/logs")
async def get_training_logs(
    job_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """获取训练日志（实时流式传输）"""
    job = await training_crud.get_job(db, job_id)
    if not job or not job.log_file_path:
        raise HTTPException(status_code=404, detail="Logs not found")

    # 实时读取日志文件
    async def log_stream():
        with open(job.log_file_path, 'r') as f:
            for line in f:
                yield line

    return StreamingResponse(log_stream(), media_type="text/plain")

@router.delete("/{job_id}")
async def cancel_training_job(
    job_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """取消训练任务"""
    # 撤销 Celery 任务
    celery_app.control.revoke(task_id, terminate=True)

    # 更新状态
    await training_crud.update_job_status(db, job_id, 'cancelled')

    return {"message": "Training job cancelled"}
```

#### 4.2 前端训练页面（Training.vue）
简化版，主要包含：
- 训练任务列表
- 创建训练任务对话框
- 实时日志查看器
- 训练进度监控

**任务清单**：
- [ ] 实现 API 端点
- [ ] 实现前端训练任务列表页
- [ ] 实现训练任务创建页面
- [ ] 实现实时日志查看器
- [ ] 添加权限控制（仅管理员）

---

### Step 5: 测试与优化（0.5 天）

#### 5.1 单元测试
```python
async def test_data_preparation():
    """测试数据准备"""
    data_prep = DataPreparationService(job_id=1, output_dir='test_output')
    yaml_path = await data_prep.prepare_dataset(...)

    assert os.path.exists(yaml_path)
    assert os.path.exists('test_output/datasets/job_1/images/train')

async def test_training_task():
    """测试训练任务（使用小数据集和少量 epoch）"""
    result = await start_training_task(job_id=1)
    assert result['success'] is True
```

#### 5.2 集成测试
- [ ] 端到端训练流程测试
- [ ] GPU 资源使用测试
- [ ] 队列隔离测试

**任务清单**：
- [ ] 单元测试
- [ ] 集成测试
- [ ] 性能测试

---

## ⚠️ 关键挑战与注意事项

### 1. GPU 资源管理
**问题**：GPU 资源昂贵且有限
**解决**：
- 使用专用 GPU Worker
- 限制并发训练任务数量（concurrency=1）
- 使用 solo pool 避免多进程冲突
- 监控 GPU 使用率

### 2. 数据准备脚本（最难！）
**问题**：标注数据到 YOLO 格式转换容易出错
**解决**：
- 充分测试边界情况
- 添加数据验证逻辑
- 记录详细日志
- 提供数据预览功能

### 3. 训练日志收集
**问题**：YOLO 训练输出到 stdout，难以捕获
**解决**：
- 重定向 stdout/stderr 到文件
- 使用日志解析器提取关键信息
- 提供实时日志流

### 4. 队列严格隔离
**问题**：训练任务可能阻塞检测任务
**解决**：
- 使用独立的 Celery 队列
- 不同 Worker 处理不同队列
- 设置任务优先级

### 5. 模型版本管理
**问题**：如何管理训练出的多个模型版本
**解决**：
- 使用语义化版本号
- 记录训练参数和数据集
- 支持模型回滚

---

## 📋 验收标准

### 功能验收
- [ ] 可以创建训练任务
- [ ] 数据自动准备为 YOLO 格式
- [ ] 训练任务异步执行
- [ ] 实时日志可查看
- [ ] 训练完成自动注册模型
- [ ] 性能指标正确记录

### 性能验收
- [ ] GPU 正确使用
- [ ] 不阻塞其他任务
- [ ] 日志实时更新

### 代码质量
- [ ] 单元测试覆盖率 > 70%
- [ ] 通过 lint 检查

---

## 📚 参考资料

- [Ultralytics YOLO 训练文档](https://docs.ultralytics.com/modes/train/)
- [YOLO 自定义数据集](https://github.com/ultralytics/yolov5/wiki/Train-Custom-Data)
- [Celery GPU Worker 配置](https://docs.celeryproject.org/en/stable/userguide/workers.html)

---

## 🎯 下一步行动

1. **配置 GPU Worker**
2. **实现数据准备服务**（⭐ 最难）
3. **实现训练任务**
4. **测试小数据集训练**
5. **前端集成**

---

**预计完成时间**: 4-5 天
**建议开始日期**: 2025-11-22（Stage 5-6 完成后）
**难度评估**: 🔥🔥🔥 高（需要 GPU 和深度学习经验）
