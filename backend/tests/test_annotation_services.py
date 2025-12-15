"""
标注管理系统的单元测试
测试标注数据格式转换、Label Studio 集成和导出功能
"""
import pytest
import json
import os
import tempfile
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path
from PIL import Image

from app.services.annotation_converter import AnnotationConverter, annotation_converter
from app.services.label_studio_service import LabelStudioService


class TestAnnotationConverter:
    """测试 AnnotationConverter 类"""

    def setup_method(self):
        """每个测试方法前执行"""
        self.converter = AnnotationConverter()
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """每个测试方法后执行清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_detection_to_label_studio_success(self):
        """测试检测结果转换为 Label Studio 格式 - 成功"""
        # 创建测试图片
        test_image_path = os.path.join(self.temp_dir, "test_image.jpg")
        test_image = Image.new('RGB', (1920, 1080), color='red')
        test_image.save(test_image_path)

        # 检测框数据 (x1, y1, x2, y2)
        detection_boxes = [
            {
                'class': 'fish',
                'confidence': 0.95,
                'bbox': [100, 200, 300, 400]
            },
            {
                'class': 'coral',
                'confidence': 0.88,
                'bbox': [500, 600, 700, 800]
            }
        ]

        # 转换
        result = self.converter.detection_to_label_studio(
            detection_boxes=detection_boxes,
            image_path=test_image_path,
            image_url="http://example.com/test.jpg"
        )

        # 验证结构
        assert 'data' in result
        assert 'predictions' in result
        assert result['data']['image'] == "http://example.com/test.jpg"
        assert len(result['predictions']) == 1
        assert len(result['predictions'][0]['result']) == 2

        # 验证第一个预测框
        pred1 = result['predictions'][0]['result'][0]
        assert pred1['value']['rectanglelabels'] == ['fish']
        assert pred1['score'] == 0.95
        assert pred1['type'] == 'rectanglelabels'

        # 验证坐标转换（应该是百分比）
        # 原始: x1=100, y1=200, x2=300, y2=400
        # 图片: 1920x1080
        # 期望: x=5.21%, y=18.52%, width=10.42%, height=18.52%
        assert abs(pred1['value']['x'] - 5.21) < 0.1
        assert abs(pred1['value']['y'] - 18.52) < 0.1

    def test_detection_to_label_studio_image_not_found(self):
        """测试检测结果转换 - 图片不存在时使用默认尺寸"""
        detection_boxes = [
            {
                'class': 'fish',
                'confidence': 0.95,
                'bbox': [100, 200, 300, 400]
            }
        ]

        result = self.converter.detection_to_label_studio(
            detection_boxes=detection_boxes,
            image_path="/non/existent/path.jpg"
        )

        # 应该成功返回，使用默认尺寸
        assert 'data' in result
        assert 'predictions' in result

    def test_label_studio_to_yolo_success(self):
        """测试 Label Studio 转换为 YOLO 格式 - 成功"""
        # 创建测试图片
        test_image_path = os.path.join(self.temp_dir, "test_image.jpg")
        test_image = Image.new('RGB', (640, 480), color='blue')
        test_image.save(test_image_path)

        # Label Studio 格式的标注数据
        ls_annotations = [
            {
                'data': {
                    'image': test_image_path
                },
                'annotations': [
                    {
                        'result': [
                            {
                                'type': 'rectanglelabels',
                                'value': {
                                    'x': 10,  # 10%
                                    'y': 20,  # 20%
                                    'width': 30,  # 30%
                                    'height': 40,  # 40%
                                    'rectanglelabels': ['fish']
                                }
                            }
                        ]
                    }
                ]
            }
        ]

        class_mapping = {'fish': 0, 'coral': 1}

        # 转换
        image_files, label_files = self.converter.label_studio_to_yolo(
            annotations=ls_annotations,
            class_mapping=class_mapping,
            output_dir=self.temp_dir
        )

        # 验证结果
        assert len(image_files) == 1
        assert len(label_files) == 1
        assert os.path.exists(label_files[0])

        # 读取生成的 YOLO 标注文件
        with open(label_files[0], 'r') as f:
            yolo_line = f.read().strip()

        # YOLO 格式: <class_id> <x_center> <y_center> <width> <height>
        # x = 10%, y = 20%, width = 30%, height = 40%
        # x_center = 0.1 + 0.3/2 = 0.25
        # y_center = 0.2 + 0.4/2 = 0.4
        parts = yolo_line.split()
        assert parts[0] == '0'  # class_id for fish
        assert abs(float(parts[1]) - 0.25) < 0.01  # x_center
        assert abs(float(parts[2]) - 0.4) < 0.01   # y_center
        assert abs(float(parts[3]) - 0.3) < 0.01   # width
        assert abs(float(parts[4]) - 0.4) < 0.01   # height

    def test_label_studio_to_yolo_empty_annotations(self):
        """测试 Label Studio 转换 - 空标注列表"""
        image_files, label_files = self.converter.label_studio_to_yolo(
            annotations=[],
            class_mapping={'fish': 0},
            output_dir=self.temp_dir
        )

        assert len(image_files) == 0
        assert len(label_files) == 0

    def test_label_studio_to_coco_success(self):
        """测试 Label Studio 转换为 COCO 格式 - 成功"""
        # 创建测试图片
        test_image_path = os.path.join(self.temp_dir, "test_image.jpg")
        test_image = Image.new('RGB', (800, 600), color='green')
        test_image.save(test_image_path)

        # Label Studio 格式的标注数据
        ls_annotations = [
            {
                'data': {
                    'image': test_image_path
                },
                'annotations': [
                    {
                        'result': [
                            {
                                'type': 'rectanglelabels',
                                'value': {
                                    'x': 10,  # 10%
                                    'y': 20,  # 20%
                                    'width': 30,  # 30%
                                    'height': 40,  # 40%
                                    'rectanglelabels': ['fish']
                                }
                            }
                        ]
                    }
                ]
            }
        ]

        category_mapping = {'fish': 1, 'coral': 2}
        output_file = os.path.join(self.temp_dir, 'annotations.json')

        # 转换
        result_file = self.converter.label_studio_to_coco(
            annotations=ls_annotations,
            category_mapping=category_mapping,
            output_file=output_file
        )

        # 验证文件生成
        assert os.path.exists(result_file)

        # 读取 COCO 格式文件
        with open(result_file, 'r') as f:
            coco_data = json.load(f)

        # 验证 COCO 结构
        assert 'images' in coco_data
        assert 'annotations' in coco_data
        assert 'categories' in coco_data

        # 验证类别
        assert len(coco_data['categories']) == 2
        assert coco_data['categories'][0]['name'] == 'fish'

        # 验证图片信息
        assert len(coco_data['images']) == 1
        assert coco_data['images'][0]['width'] == 800
        assert coco_data['images'][0]['height'] == 600

        # 验证标注
        assert len(coco_data['annotations']) == 1
        annotation = coco_data['annotations'][0]
        assert annotation['category_id'] == 1  # fish

        # 验证 bbox (COCO 使用绝对坐标)
        # x = 10% * 800 = 80
        # y = 20% * 600 = 120
        # width = 30% * 800 = 240
        # height = 40% * 600 = 240
        assert annotation['bbox'][0] == 80
        assert annotation['bbox'][1] == 120
        assert annotation['bbox'][2] == 240
        assert annotation['bbox'][3] == 240

    def test_create_yolo_dataset_success(self):
        """测试创建完整 YOLO 数据集 - 成功"""
        # 创建测试图片和标注文件
        image_files = []
        label_files = []

        for i in range(5):
            # 图片
            img_path = os.path.join(self.temp_dir, f"image_{i}.jpg")
            img = Image.new('RGB', (640, 480), color='red')
            img.save(img_path)
            image_files.append(img_path)

            # 标注
            label_path = os.path.join(self.temp_dir, f"image_{i}.txt")
            with open(label_path, 'w') as f:
                f.write(f"0 0.5 0.5 0.2 0.2\n")
            label_files.append(label_path)

        dataset_dir = os.path.join(self.temp_dir, 'yolo_dataset')
        class_names = ['fish', 'coral', 'turtle']

        # 创建数据集
        result = self.converter.create_yolo_dataset(
            image_files=image_files,
            label_files=label_files,
            output_dir=dataset_dir,
            class_names=class_names,
            train_split=0.6  # 60% 训练集
        )

        # 验证结果
        assert 'dataset_dir' in result
        assert 'yaml_path' in result
        assert 'train_count' in result
        assert 'val_count' in result

        # 验证目录结构
        assert os.path.exists(os.path.join(dataset_dir, 'images', 'train'))
        assert os.path.exists(os.path.join(dataset_dir, 'images', 'val'))
        assert os.path.exists(os.path.join(dataset_dir, 'labels', 'train'))
        assert os.path.exists(os.path.join(dataset_dir, 'labels', 'val'))

        # 验证 yaml 文件
        assert os.path.exists(result['yaml_path'])
        with open(result['yaml_path'], 'r') as f:
            yaml_content = f.read()
            assert 'fish' in yaml_content
            assert 'nc: 3' in yaml_content

        # 验证 classes.txt
        classes_file = os.path.join(dataset_dir, 'classes.txt')
        assert os.path.exists(classes_file)
        with open(classes_file, 'r') as f:
            classes = f.read().strip().split('\n')
            assert classes == class_names

        # 验证数据划分
        assert result['train_count'] == 3  # 60% of 5
        assert result['val_count'] == 2    # 40% of 5


class TestLabelStudioService:
    """测试 LabelStudioService 类"""

    def setup_method(self):
        """每个测试方法前执行"""
        self.service = LabelStudioService()

    @patch('app.services.label_studio_service.requests.request')
    def test_create_project_success(self, mock_request):
        """测试创建 Label Studio 项目 - 成功"""
        # Mock 响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'id': 123,
            'title': 'Test Project',
            'description': 'Test Description'
        }
        mock_response.content = b'{"id": 123}'
        mock_request.return_value = mock_response

        # 调用
        result = self.service.create_project(
            title='Test Project',
            description='Test Description'
        )

        # 验证
        assert result['id'] == 123
        assert result['title'] == 'Test Project'
        mock_request.assert_called_once()

    @patch('app.services.label_studio_service.requests.request')
    def test_create_project_with_custom_labels(self, mock_request):
        """测试创建项目 - 自定义标签"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'id': 456}
        mock_response.content = b'{"id": 456}'
        mock_request.return_value = mock_response

        # 生成自定义标签配置
        label_config = self.service.get_labeling_config_for_classes(
            ['fish', 'coral', 'turtle']
        )

        assert 'fish' in label_config
        assert 'coral' in label_config
        assert 'turtle' in label_config
        assert 'RectangleLabels' in label_config

    @patch('app.services.label_studio_service.requests.request')
    def test_import_tasks_success(self, mock_request):
        """测试导入任务 - 成功"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'task_count': 3,
            'annotation_count': 0
        }
        mock_response.content = b'{"task_count": 3}'
        mock_request.return_value = mock_response

        tasks = [
            {'data': {'image': 'http://example.com/1.jpg'}},
            {'data': {'image': 'http://example.com/2.jpg'}},
            {'data': {'image': 'http://example.com/3.jpg'}}
        ]

        result = self.service.import_tasks(project_id=123, tasks=tasks)

        assert result['task_count'] == 3
        mock_request.assert_called_once()

    @patch('app.services.label_studio_service.requests.request')
    def test_export_tasks_success(self, mock_request):
        """测试导出任务 - 成功"""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                'id': 1,
                'data': {'image': 'http://example.com/1.jpg'},
                'annotations': []
            },
            {
                'id': 2,
                'data': {'image': 'http://example.com/2.jpg'},
                'annotations': []
            }
        ]
        mock_response.content = b'[{"id": 1}, {"id": 2}]'
        mock_request.return_value = mock_response

        result = self.service.export_tasks(project_id=123, export_type='JSON')

        assert len(result) == 2
        assert result[0]['id'] == 1
        mock_request.assert_called_once()

    @patch('app.services.label_studio_service.requests.request')
    def test_check_connection_success(self, mock_request):
        """测试连接检查 - 成功"""
        mock_response = MagicMock()
        mock_response.json.return_value = {'version': '1.7.0'}
        mock_response.content = b'{"version": "1.7.0"}'
        mock_request.return_value = mock_response

        result = self.service.check_connection()

        assert result is True

    @patch('app.services.label_studio_service.requests.request')
    def test_check_connection_failure(self, mock_request):
        """测试连接检查 - 失败"""
        mock_request.side_effect = Exception("Connection failed")

        result = self.service.check_connection()

        assert result is False

    def test_get_default_labeling_config(self):
        """测试获取默认标注配置"""
        config = self.service._get_default_labeling_config()

        assert '<View>' in config
        assert '<Image' in config
        assert '<RectangleLabels' in config
        assert 'fish' in config
        assert 'turtle' in config

    def test_get_labeling_config_for_classes(self):
        """测试为类别生成标注配置"""
        class_labels = ['fish', 'coral', 'shark']
        config = self.service.get_labeling_config_for_classes(class_labels)

        # 验证所有类别都包含在配置中
        for label in class_labels:
            assert f'value="{label}"' in config

        # 验证基本结构
        assert '<View>' in config
        assert '<Image' in config
        assert '<RectangleLabels' in config


class TestAnnotationConverterEdgeCases:
    """测试边界情况和错误处理"""

    def setup_method(self):
        """每个测试方法前执行"""
        self.converter = AnnotationConverter()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """每个测试方法后执行清理"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_detection_to_label_studio_empty_boxes(self):
        """测试空检测框列表"""
        test_image_path = os.path.join(self.temp_dir, "test.jpg")
        Image.new('RGB', (100, 100)).save(test_image_path)

        result = self.converter.detection_to_label_studio(
            detection_boxes=[],
            image_path=test_image_path
        )

        assert 'data' in result
        assert 'predictions' not in result or result['predictions'] == []

    def test_label_studio_to_yolo_missing_image(self):
        """测试 Label Studio 转换 - 缺少图片路径"""
        ls_annotations = [
            {
                'data': {},  # 没有 image 字段
                'annotations': []
            }
        ]

        image_files, label_files = self.converter.label_studio_to_yolo(
            annotations=ls_annotations,
            class_mapping={'fish': 0},
            output_dir=self.temp_dir
        )

        # 应该跳过这条记录
        assert len(image_files) == 0
        assert len(label_files) == 0

    def test_create_yolo_dataset_empty_files(self):
        """测试创建 YOLO 数据集 - 空文件列表"""
        dataset_dir = os.path.join(self.temp_dir, 'empty_dataset')

        result = self.converter.create_yolo_dataset(
            image_files=[],
            label_files=[],
            output_dir=dataset_dir,
            class_names=['fish'],
            train_split=0.8
        )

        # 应该成功创建目录结构，但没有文件
        assert os.path.exists(dataset_dir)
        assert result['train_count'] == 0
        assert result['val_count'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
