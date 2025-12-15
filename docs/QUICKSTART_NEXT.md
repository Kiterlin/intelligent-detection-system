# 快速开始 - 继续开发指南

**当前进度**: Phase 2 (80%) - 模型训练系统
**最后更新**: 2025-11-15

---

## 🚀 立即开始

### 1. 阅读进度文档

```bash
cat docs/IMPLEMENTATION_PROGRESS.md
```

这个文档包含：
- ✅ 已完成的所有工作
- 📋 待完成的任务清单
- 📁 文件结构概览
- 🔑 关键实现细节

### 2. 下一步要做什么

**优先级顺序**:

#### 第一步：创建 Celery 训练任务
```bash
# 创建文件
touch app/tasks/training_tasks.py
```

**需要实现**:
- `start_training_task(job_id)` - 主训练任务
- 集成 `DataPreparationService`
- 集成 `YOLOTrainer`
- 错误处理和状态更新

**参考**:
- 已有的 `app/tasks/annotation_tasks.py`
- 规划文档: `docs/第二阶段计划/待开发/Stage7_模型训练_实施计划.md` (第 572-692 行)

#### 第二步：创建模型注册服务
```bash
# 创建文件
touch app/services/model_registry.py
```

**需要实现**:
- `register_trained_model(db, job, weights_path, metrics)` - 注册新模型

**功能**:
- 在 `ml_models` 表中创建新记录
- 设置模型类型、路径、性能指标
- 可选：设置为活跃模型

#### 第三步：创建训练管理 API
```bash
# 创建目录和文件
mkdir -p app/api/v1/admin
touch app/api/v1/admin/__init__.py
touch app/api/v1/admin/training.py
```

**需要实现的端点** (6 个):
1. `POST /api/v1/admin/training` - 创建训练任务
2. `GET /api/v1/admin/training` - 获取训练任务列表
3. `GET /api/v1/admin/training/{job_id}` - 获取任务详情
4. `GET /api/v1/admin/training/{job_id}/logs` - 实时日志流
5. `DELETE /api/v1/admin/training/{job_id}` - 取消训练
6. `GET /api/v1/admin/training/{job_id}/metrics` - 获取指标

**参考**:
- 已有的 `app/api/v1/annotations.py`
- 规划文档第 714-783 行

#### 第四步：编写单元测试
```bash
# 创建文件
touch tests/test_training_services.py
```

**测试覆盖**:
- 数据准备服务
- CRUD 操作
- API 端点（Mock）

---

## 📋 核心代码模板

### Celery 训练任务框架

```python
# app/tasks/training_tasks.py
import os
import shutil
from loguru import logger
from app.celery_app import celery_app
from app.core.database import get_db
from app.crud.training import crud_training_job
from app.services.data_preparation import DataPreparationService
from app.utils.yolo_trainer import YOLOTrainer
from app.services.model_registry import ModelRegistryService

@celery_app.task(bind=True, queue='training', max_retries=0)
def start_training_task(self, job_id: int):
    """启动模型训练任务"""
    import asyncio
    return asyncio.run(_train_async(job_id))

async def _train_async(job_id: int):
    async for db in get_db():
        try:
            # 1. 获取任务
            job = await crud_training_job.get(db, job_id)

            # 2. 准备数据
            await crud_training_job.update_status(db, job_id=job_id, status='preparing')
            data_prep = DataPreparationService(job_id)
            result = await data_prep.prepare_dataset(db, job.dataset_config)

            # 3. 训练
            await crud_training_job.update_status(db, job_id=job_id, status='training')
            trainer = YOLOTrainer()
            train_result = trainer.train(
                base_model=job.base_model.model_path,
                data_yaml=result.data_yaml_path,
                config=job.config_json
            )

            # 4. 注册模型
            registry = ModelRegistryService()
            new_model = await registry.register_trained_model(
                db, job, train_result['best_weights'], train_result['metrics']
            )

            # 5. 更新状态
            await crud_training_job.update_status(
                db, job_id=job_id, status='completed',
                new_model_id=new_model.id,
                weights_path=train_result['best_weights'],
                metrics_json=train_result['metrics']
            )

        except Exception as e:
            logger.error(f"Training failed: {e}")
            await crud_training_job.update_status(
                db, job_id=job_id, status='failed', error_message=str(e)
            )
            raise
```

### API 端点框架

```python
# app/api/v1/admin/training.py
from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_admin, get_db
from app.crud.training import crud_training_job
from app.schemas.training import TrainingJobCreate, TrainingJobResponse
from app.tasks.training_tasks import start_training_task

router = APIRouter()

@router.post("/", response_model=TrainingJobResponse)
async def create_training_job(
    *,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_admin),
    job_in: TrainingJobCreate
):
    """创建训练任务"""
    # 创建任务
    job = await crud_training_job.create(
        db=db, obj_in=job_in, admin_id=current_user.id
    )

    # 启动异步训练
    start_training_task.delay(job.id)

    return job

@router.get("/", response_model=List[TrainingJobResponse])
async def list_training_jobs(
    *,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_admin),
    skip: int = 0,
    limit: int = 20
):
    """获取训练任务列表"""
    jobs, total = await crud_training_job.get_multi(
        db=db, skip=skip, limit=limit
    )
    return jobs
```

---

## ✅ 验证清单

完成上述任务后，运行以下验证：

### 1. 数据库检查
```bash
# 确认表已创建
psql -U your_user -d your_db -c "\d training_jobs"
```

### 2. 代码检查
```bash
# 检查导入错误
python -c "from app.tasks.training_tasks import start_training_task"
python -c "from app.api.v1.admin.training import router"
```

### 3. 运行测试
```bash
# 运行已有测试
pytest tests/test_annotation_services.py -v

# 运行新测试
pytest tests/test_training_services.py -v
```

### 4. 启动服务测试
```bash
# 启动 API（另一个终端）
uvicorn app.main:app --reload

# 启动 GPU Worker（另一个终端）
celery -A app.celery_app worker -Q training -n training-worker --pool=solo --loglevel=info

# 测试 API
curl -X POST http://localhost:8000/api/v1/admin/training \
  -H "Content-Type: application/json" \
  -d '{"job_name": "test", ...}'
```

---

## 📚 重要参考资料

### 项目文档
- **总体进度**: `docs/IMPLEMENTATION_PROGRESS.md`
- **Stage 7 计划**: `docs/第二阶段计划/待开发/Stage7_模型训练_实施计划.md`
- **Phase 2 进度**: `docs/第二阶段计划/Phase2_整体进度.md`

### 已实现的关键文件
- **数据准备**: `app/services/data_preparation.py` (240 行)
- **YOLO 训练**: `app/utils/yolo_trainer.py` (150 行)
- **CRUD 操作**: `app/crud/training.py` (180 行)
- **数据模型**: `app/schemas/training.py` (完整的 Schemas)

### 外部文档
- **YOLO 训练**: https://docs.ultralytics.com/modes/train/
- **Celery 队列**: https://docs.celeryproject.org/en/stable/userguide/routing.html
- **FastAPI 流式响应**: https://fastapi.tiangolo.com/advanced/custom-response/

---

## 🔧 常见问题

### Q: 如何查看当前进度？
```bash
cat docs/IMPLEMENTATION_PROGRESS.md | grep "Phase 2"
```

### Q: 已创建了哪些文件？
```bash
# 训练相关文件
ls -la app/models/training.py
ls -la app/schemas/training.py
ls -la app/crud/training.py
ls -la app/services/data_preparation.py
ls -la app/utils/yolo_trainer.py
```

### Q: 数据库迁移状态？
```bash
alembic current
# 应该显示: ee6079a82bc2 (add_training_jobs_table)
```

### Q: 测试是否通过？
```bash
pytest tests/test_annotation_services.py -v
# 应该显示: 17 passed
```

---

## 💡 开发提示

1. **优先使用已有代码作为模板**
   - Celery 任务参考 `app/tasks/annotation_tasks.py`
   - API 端点参考 `app/api/v1/annotations.py`
   - 单元测试参考 `tests/test_annotation_services.py`

2. **注意错误处理**
   - 训练失败时更新状态为 'failed'
   - 记录详细的错误信息到 `error_message` 字段
   - 清理临时文件（数据集目录）

3. **GPU 资源管理**
   - 确保使用 `queue='training'`
   - Worker 使用 `--pool=solo`
   - 限制并发为 1

4. **权限控制**
   - 所有训练 API 需要管理员权限
   - 使用 `Depends(get_current_admin)`

---

## 📞 获取帮助

如遇到问题：
1. 查看进度文档: `docs/IMPLEMENTATION_PROGRESS.md`
2. 查看实施计划: `docs/第二阶段计划/待开发/Stage7_模型训练_实施计划.md`
3. 参考已有代码: `app/tasks/annotation_tasks.py`, `app/api/v1/annotations.py`

---

**祝开发顺利！** 🚀

继续告诉 Claude: "继续完成 Phase 2"
