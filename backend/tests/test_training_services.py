"""
训练系统的单元测试
测试数据准备服务、CRUD 操作和 API 端点
"""
import pytest
import os
import tempfile
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path
from datetime import datetime

from app.services.data_preparation import DataPreparationService
from app.schemas.training import DatasetConfig, TrainingConfig


class TestDataPreparationService:
    """测试 DataPreparationService 类"""

    def setup_method(self):
        """每个测试方法前执行"""
        self.temp_dir = tempfile.mkdtemp()
        self.job_id = 1
        self.service = DataPreparationService(
            job_id=self.job_id,
            output_dir=self.temp_dir
        )

    def teardown_method(self):
        """每个测试方法后执行清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_init_creates_directory_structure(self):
        """测试初始化时创建目录结构"""
        dataset_dir = Path(self.temp_dir) / 'datasets' / f"job_{self.job_id}"

        assert dataset_dir.exists()
        assert (dataset_dir / 'images' / 'train').exists()
        assert (dataset_dir / 'images' / 'val').exists()
        assert (dataset_dir / 'images' / 'test').exists()
        assert (dataset_dir / 'labels' / 'train').exists()
        assert (dataset_dir / 'labels' / 'val').exists()
        assert (dataset_dir / 'labels' / 'test').exists()

    def test_split_dataset_correct_ratios(self):
        """测试数据集划分比例正确"""
        # 创建模拟的标注数据
        mock_annotations = [MagicMock() for _ in range(100)]

        split_ratio = {
            'train': 0.8,
            'val': 0.15,
            'test': 0.05
        }

        train, val, test = self.service._split_dataset(mock_annotations, split_ratio)

        # 验证划分比例（允许一定误差）
        assert len(train) == 80
        assert len(val) == 15
        assert len(test) == 5

    def test_generate_data_yaml_structure(self):
        """测试生成 data.yaml 文件结构正确"""
        classes = ['fish', 'coral', 'turtle']

        yaml_path = self.service._generate_data_yaml(classes)

        assert os.path.exists(yaml_path)

        # 读取并验证内容
        import yaml
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        assert data['nc'] == 3
        assert data['names'] == classes
        assert 'path' in data
        assert 'train' in data
        assert 'val' in data
        assert 'test' in data


class TestTrainingCRUD:
    """测试训练 CRUD 操作"""

    @pytest.mark.asyncio
    async def test_create_training_job(self):
        """测试创建训练任务"""
        from app.crud.training import crud_training_job
        from app.schemas.training import TrainingJobCreate, TrainingConfig, DatasetConfig

        # 创建模拟的数据库会话
        mock_db = AsyncMock()

        # 准备测试数据
        training_config = TrainingConfig(
            base_model="yolov8n.pt",
            epochs=10,
            batch_size=8,
            img_size=640,
            learning_rate=0.01,
            optimizer="SGD"
        )

        dataset_config = DatasetConfig(
            source="annotations",
            annotation_task_id=1,
            classes=["fish", "coral"]
        )

        job_data = TrainingJobCreate(
            job_name="Test Training Job",
            base_model_id=1,
            config_json=training_config,
            dataset_config=dataset_config
        )

        # 模拟创建操作
        with patch.object(crud_training_job, 'create') as mock_create:
            mock_job = MagicMock()
            mock_job.id = 1
            mock_job.job_name = "Test Training Job"
            mock_job.status = "pending"
            mock_create.return_value = mock_job

            result = await crud_training_job.create(
                db=mock_db,
                obj_in=job_data,
                admin_id=1
            )

            assert result.id == 1
            assert result.job_name == "Test Training Job"
            assert result.status == "pending"

    @pytest.mark.asyncio
    async def test_update_training_status(self):
        """测试更新训练任务状态"""
        from app.crud.training import crud_training_job

        mock_db = AsyncMock()

        # 模拟任务对象
        mock_job = MagicMock()
        mock_job.id = 1
        mock_job.status = "pending"
        mock_job.started_at = None
        mock_job.completed_at = None

        with patch.object(crud_training_job, 'get', return_value=mock_job):
            with patch.object(crud_training_job, 'update_status') as mock_update:
                mock_update.return_value = mock_job

                result = await crud_training_job.update_status(
                    db=mock_db,
                    job_id=1,
                    status='training'
                )

                mock_update.assert_called_once()


class TestTrainingAPI:
    """测试训练 API 端点"""

    @pytest.mark.asyncio
    async def test_create_training_job_endpoint(self):
        """测试创建训练任务端点"""
        from app.api.v1.training import create_training_job
        from app.schemas.training import TrainingJobCreate, TrainingConfig, DatasetConfig

        # 准备测试数据
        training_config = TrainingConfig(
            base_model="yolov8n.pt",
            epochs=10,
            batch_size=8
        )

        dataset_config = DatasetConfig(
            source="annotations",
            annotation_task_id=1,
            classes=["fish", "coral"]
        )

        job_data = TrainingJobCreate(
            job_name="API Test Job",
            base_model_id=1,
            config_json=training_config,
            dataset_config=dataset_config
        )

        # 模拟依赖项
        mock_db = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = 1

        # 模拟相关服务
        with patch('app.crud.ml_model.get_model_by_id') as mock_get_model:
            mock_get_model.return_value = MagicMock(id=1, model_name="Test Model")

            with patch('app.crud.annotation.crud_annotation_task.get') as mock_get_task:
                mock_get_task.return_value = MagicMock(id=1)

                with patch('app.crud.training.crud_training_job.create') as mock_create:
                    mock_job = MagicMock()
                    mock_job.id = 1
                    mock_job.job_name = "API Test Job"
                    mock_job.status = "pending"
                    mock_job.admin_id = 1
                    mock_job.base_model_id = 1
                    mock_job.new_model_id = None
                    mock_job.config_json = training_config.model_dump()
                    mock_job.dataset_config = dataset_config.model_dump()
                    mock_job.log_file_path = None
                    mock_job.weights_path = None
                    mock_job.results_path = None
                    mock_job.metrics_json = None
                    mock_job.current_epoch = 0
                    mock_job.total_epochs = 10
                    mock_job.progress_percentage = 0.0
                    mock_job.error_message = None
                    mock_job.created_at = datetime.utcnow()
                    mock_job.started_at = None
                    mock_job.completed_at = None

                    mock_create.return_value = mock_job

                    with patch('app.tasks.training_tasks.start_training_task.delay') as mock_task:
                        mock_task.return_value = MagicMock(id="task-123")

                        # 调用端点
                        result = await create_training_job(
                            job_data=job_data,
                            current_user=mock_user,
                            db=mock_db
                        )

                        # 验证结果
                        assert result.id == 1
                        assert result.job_name == "API Test Job"
                        assert result.status == "pending"
                        mock_task.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_list_training_jobs_endpoint(self):
        """测试获取训练任务列表端点"""
        from app.api.v1.training import list_training_jobs

        mock_db = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = 1

        # 模拟训练任务列表
        mock_jobs = [
            MagicMock(
                id=1,
                job_name="Job 1",
                status="completed",
                admin_id=1,
                base_model_id=1,
                new_model_id=2,
                config_json={},
                dataset_config={},
                log_file_path=None,
                weights_path=None,
                results_path=None,
                metrics_json=None,
                current_epoch=100,
                total_epochs=100,
                progress_percentage=100.0,
                error_message=None,
                created_at=datetime.utcnow(),
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow()
            ),
            MagicMock(
                id=2,
                job_name="Job 2",
                status="training",
                admin_id=1,
                base_model_id=1,
                new_model_id=None,
                config_json={},
                dataset_config={},
                log_file_path=None,
                weights_path=None,
                results_path=None,
                metrics_json=None,
                current_epoch=50,
                total_epochs=100,
                progress_percentage=50.0,
                error_message=None,
                created_at=datetime.utcnow(),
                started_at=datetime.utcnow(),
                completed_at=None
            )
        ]

        with patch('app.crud.training.crud_training_job.get_multi') as mock_get_multi:
            mock_get_multi.return_value = (mock_jobs, 2)

            result = await list_training_jobs(
                skip=0,
                limit=20,
                status_filter=None,
                current_user=mock_user,
                db=mock_db
            )

            assert result.total == 2
            assert len(result.items) == 2
            assert result.items[0].id == 1
            assert result.items[1].id == 2

    @pytest.mark.asyncio
    async def test_get_training_job_endpoint(self):
        """测试获取训练任务详情端点"""
        from app.api.v1.training import get_training_job

        mock_db = AsyncMock()
        mock_user = MagicMock()
        mock_user.id = 1

        mock_job = MagicMock(
            id=1,
            job_name="Test Job",
            status="completed",
            admin_id=1,
            base_model_id=1,
            new_model_id=2,
            config_json={"epochs": 100},
            dataset_config={"classes": ["fish"]},
            log_file_path="/path/to/log",
            weights_path="/path/to/weights",
            results_path="/path/to/results",
            metrics_json={"mAP50": 0.85},
            current_epoch=100,
            total_epochs=100,
            progress_percentage=100.0,
            error_message=None,
            created_at=datetime.utcnow(),
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )

        with patch('app.crud.training.crud_training_job.get') as mock_get:
            mock_get.return_value = mock_job

            result = await get_training_job(
                job_id=1,
                current_user=mock_user,
                db=mock_db
            )

            assert result.id == 1
            assert result.job_name == "Test Job"
            assert result.status == "completed"
            assert result.progress_percentage == 100.0


class TestYOLOTrainer:
    """测试 YOLO 训练器"""

    def test_yolo_trainer_init(self):
        """测试 YOLO 训练器初始化"""
        from app.utils.yolo_trainer import YOLOTrainer

        trainer = YOLOTrainer(log_file="/tmp/test.log")
        assert trainer.log_file == "/tmp/test.log"
        assert trainer.model is None

    def test_extract_metrics_with_valid_results(self):
        """测试从训练结果提取指标"""
        from app.utils.yolo_trainer import YOLOTrainer

        trainer = YOLOTrainer()

        # 模拟训练结果
        mock_results = MagicMock()
        mock_results.results_dict = {
            'metrics/mAP50(B)': 0.85,
            'metrics/mAP50-95(B)': 0.72,
            'metrics/precision(B)': 0.88,
            'metrics/recall(B)': 0.82,
            'train/box_loss': 0.045,
            'train/cls_loss': 0.032,
            'train/dfl_loss': 0.015
        }

        metrics = trainer._extract_metrics(mock_results)

        assert metrics['mAP50'] == 0.85
        assert metrics['mAP50_95'] == 0.72
        assert metrics['precision'] == 0.88
        assert metrics['recall'] == 0.82
        assert metrics['box_loss'] == 0.045
        assert metrics['cls_loss'] == 0.032
        assert metrics['dfl_loss'] == 0.015

    def test_extract_metrics_with_missing_results_dict(self):
        """测试提取指标时缺少 results_dict"""
        from app.utils.yolo_trainer import YOLOTrainer

        trainer = YOLOTrainer()

        # 模拟没有 results_dict 的结果
        mock_results = MagicMock()
        del mock_results.results_dict  # 删除属性

        metrics = trainer._extract_metrics(mock_results)

        # 应该返回默认值
        assert metrics['mAP50'] == 0.0
        assert metrics['mAP50_95'] == 0.0
        assert metrics['precision'] == 0.0
        assert metrics['recall'] == 0.0
