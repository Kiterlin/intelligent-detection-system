# Label Studio 集成方案

**文档版本**: v1.0
**创建日期**: 2025-11-15
**状态**: 设计阶段

---

## 1. 概述

### 1.1 集成目标

将 Label Studio 集成到智能目标检测系统中，实现以下功能：
1. **数据标注**: 对检测结果进行人工校正和标注
2. **预标注**: 利用检测结果作为初始标注，提升标注效率
3. **数据导出**: 导出 YOLO/COCO 格式的标注数据用于模型训练
4. **标注管理**: 在系统内管理标注任务和进度

### 1.2 技术栈选择

| 组件 | 方案 | 说明 |
|------|------|------|
| **Label Studio 部署** | Pip 安装（开发） + Docker Compose（生产） | 开发环境使用 pip，生产环境使用容器化部署 |
| **API 集成** | Label Studio Python SDK + REST API | 使用官方 SDK 简化集成，REST API 提供灵活性 |
| **数据存储** | PostgreSQL | 复用现有数据库，独立表管理标注数据 |
| **文件存储** | 本地文件系统 | 图片存储在本地，Label Studio 通过文件路径访问 |
| **数据格式** | Label Studio JSON + YOLO/COCO | 内部使用 Label Studio 格式，导出时转换 |

---

## 2. 系统架构

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                      智能目标检测系统                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────┐         ┌───────────────┐                  │
│  │   检测模块     │────────>│  检测结果DB   │                  │
│  └───────────────┘         └───────┬───────┘                  │
│                                    │                            │
│                                    ▼                            │
│  ┌───────────────┐         ┌───────────────┐                  │
│  │  标注模块      │<────────│ 标注任务DB    │                  │
│  │ (我们的系统)   │         └───────────────┘                  │
│  └───────┬───────┘                                             │
│          │                                                      │
│          │ API 调用                                            │
│          ▼                                                      │
│  ┌───────────────────────────────────────────────────┐        │
│  │              Label Studio                          │        │
│  ├───────────────────────────────────────────────────┤        │
│  │  - 项目管理                                        │        │
│  │  - 任务导入/导出                                   │        │
│  │  - 标注界面                                        │        │
│  │  - 用户管理                                        │        │
│  └───────────────────────────────────────────────────┘        │
│          │                                                      │
│          ▼                                                      │
│  ┌───────────────┐         ┌───────────────┐                  │
│  │ 导出模块       │────────>│  训练模块     │                  │
│  │ (YOLO/COCO)   │         │               │                  │
│  └───────────────┘         └───────────────┘                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 数据流设计

```
┌──────────────┐
│ 1. 用户上传   │
│    图片/视频  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 2. 目标检测   │
│    (YOLO)    │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ 3. 检测结果   │
│    保存到DB  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────────────┐
│ 4. 用户创建标注任务                    │
│    - 选择检测结果                      │
│    - 创建 Label Studio 项目            │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ 5. 预标注数据转换                      │
│    检测框 → Label Studio JSON 格式   │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ 6. 导入到 Label Studio                │
│    - 创建任务                          │
│    - 添加预标注                        │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ 7. 用户在 Label Studio 中标注         │
│    - 调整检测框                        │
│    - 修正类别                          │
│    - 添加遗漏目标                      │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────┐
│ 8. 标注完成，导出数据                  │
│    Label Studio JSON → YOLO/COCO    │
└──────┬───────────────────────────────┘
       │
       ▼
┌──────────────┐
│ 9. 模型训练   │
│    使用标注   │
│    数据       │
└───────────────┘
```

---

## 3. 数据格式转换

### 3.1 检测结果 → Label Studio 格式

**输入**（检测结果）:
```json
{
  "detection_id": 123,
  "image_path": "/data/uploads/img_001.jpg",
  "boxes": [
    {
      "class": "fish",
      "confidence": 0.92,
      "bbox": [100, 200, 300, 400]  // [x1, y1, x2, y2]
    }
  ]
}
```

**输出**（Label Studio 任务）:
```json
{
  "data": {
    "image": "/data/uploads/img_001.jpg"
  },
  "predictions": [{
    "result": [{
      "value": {
        "x": 10.0,           // 百分比: (100 / 图片宽度) * 100
        "y": 20.0,           // 百分比: (200 / 图片高度) * 100
        "width": 20.0,       // 百分比: ((300-100) / 图片宽度) * 100
        "height": 40.0,      // 百分比: ((400-200) / 图片高度) * 100
        "rectanglelabels": ["fish"]
      },
      "from_name": "label",
      "to_name": "image",
      "type": "rectanglelabels",
      "score": 0.92
    }]
  }]
}
```

**转换函数**:
```python
def detection_to_label_studio(detection, image_width, image_height):
    """
    将检测结果转换为 Label Studio 预标注格式

    Args:
        detection: 检测结果对象
        image_width: 图片宽度（像素）
        image_height: 图片高度（像素）

    Returns:
        Label Studio 任务字典
    """
    predictions = []

    for box in detection.boxes:
        x1, y1, x2, y2 = box['bbox']

        # 转换为百分比坐标
        x = (x1 / image_width) * 100
        y = (y1 / image_height) * 100
        width = ((x2 - x1) / image_width) * 100
        height = ((y2 - y1) / image_height) * 100

        predictions.append({
            "value": {
                "x": round(x, 2),
                "y": round(y, 2),
                "width": round(width, 2),
                "height": round(height, 2),
                "rectanglelabels": [box['class']]
            },
            "from_name": "label",
            "to_name": "image",
            "type": "rectanglelabels",
            "score": box['confidence']
        })

    return {
        "data": {
            "image": detection.image_path
        },
        "predictions": [{"result": predictions}] if predictions else []
    }
```

### 3.2 Label Studio → YOLO 格式

**输入**（Label Studio 标注）:
```json
{
  "annotations": [{
    "result": [{
      "value": {
        "x": 10.0,
        "y": 20.0,
        "width": 20.0,
        "height": 40.0,
        "rectanglelabels": ["fish"]
      }
    }]
  }]
}
```

**输出**（YOLO 格式）:
```
classes.txt:
fish
turtle
coral
...

annotations/img_001.txt:
0 0.20 0.40 0.20 0.40
# 格式: <class_id> <x_center> <y_center> <width> <height>
# 所有坐标都是归一化的 [0, 1]
```

**转换函数**:
```python
def label_studio_to_yolo(annotation, class_mapping):
    """
    将 Label Studio 标注转换为 YOLO 格式

    Args:
        annotation: Label Studio 标注对象
        class_mapping: 类别名称到 ID 的映射 {'fish': 0, 'turtle': 1, ...}

    Returns:
        YOLO 格式的标注字符串列表
    """
    yolo_lines = []

    for result in annotation['result']:
        if result['type'] != 'rectanglelabels':
            continue

        value = result['value']
        class_name = value['rectanglelabels'][0]
        class_id = class_mapping.get(class_name, 0)

        # Label Studio 使用 x, y 作为左上角坐标（百分比）
        # YOLO 需要中心点坐标（归一化）
        x = value['x'] / 100  # 转换为 [0, 1]
        y = value['y'] / 100
        width = value['width'] / 100
        height = value['height'] / 100

        # 计算中心点
        x_center = x + width / 2
        y_center = y + height / 2

        yolo_lines.append(
            f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
        )

    return yolo_lines
```

### 3.3 Label Studio → COCO 格式

**输出**（COCO 格式）:
```json
{
  "images": [
    {
      "id": 1,
      "file_name": "img_001.jpg",
      "width": 1920,
      "height": 1080
    }
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 1,
      "category_id": 1,
      "bbox": [100, 200, 200, 400],  // [x, y, width, height]
      "area": 80000,
      "iscrowd": 0
    }
  ],
  "categories": [
    {
      "id": 1,
      "name": "fish",
      "supercategory": "marine"
    }
  ]
}
```

---

## 4. API 集成设计

### 4.1 Label Studio API 封装

创建 `backend/app/services/label_studio_service.py`:

```python
from label_studio_sdk import Client
from typing import List, Dict, Optional
import os


class LabelStudioService:
    """Label Studio API 服务封装"""

    def __init__(self):
        self.url = os.getenv('LABEL_STUDIO_URL', 'http://localhost:8080')
        self.api_key = os.getenv('LABEL_STUDIO_API_KEY', '')
        self.client = Client(url=self.url, api_key=self.api_key)

    def create_project(self, title: str, description: str = "") -> int:
        """
        创建标注项目

        Args:
            title: 项目标题
            description: 项目描述

        Returns:
            项目 ID
        """
        project = self.client.start_project(
            title=title,
            description=description,
            label_config=self._get_labeling_config()
        )
        return project.id

    def import_tasks(
        self,
        project_id: int,
        tasks: List[Dict],
        preannotated: bool = True
    ) -> Dict:
        """
        导入标注任务

        Args:
            project_id: 项目 ID
            tasks: 任务列表
            preannotated: 是否包含预标注

        Returns:
            导入结果
        """
        project = self.client.get_project(project_id)
        result = project.import_tasks(tasks)
        return result

    def export_annotations(
        self,
        project_id: int,
        export_type: str = 'JSON'
    ) -> List[Dict]:
        """
        导出标注数据

        Args:
            project_id: 项目 ID
            export_type: 导出格式 ('JSON', 'YOLO', 'COCO')

        Returns:
            标注数据列表
        """
        project = self.client.get_project(project_id)
        annotations = project.export_tasks(export_type=export_type)
        return annotations

    def get_project_tasks(self, project_id: int) -> List[Dict]:
        """获取项目的所有任务"""
        project = self.client.get_project(project_id)
        tasks = project.get_tasks()
        return tasks

    def delete_project(self, project_id: int) -> bool:
        """删除项目"""
        try:
            project = self.client.get_project(project_id)
            project.delete()
            return True
        except Exception as e:
            logger.error(f"删除项目失败: {str(e)}")
            return False

    def _get_labeling_config(self) -> str:
        """获取标注配置模板（目标检测）"""
        return '''
<View>
  <Image name="image" value="$image"/>
  <RectangleLabels name="label" toName="image">
    <Label value="fish" background="red"/>
    <Label value="turtle" background="blue"/>
    <Label value="coral" background="green"/>
    <Label value="seahorse" background="orange"/>
    <Label value="starfish" background="purple"/>
    <Label value="jellyfish" background="pink"/>
    <Label value="crab" background="yellow"/>
    <Label value="octopus" background="brown"/>
  </RectangleLabels>
</View>
'''
```

### 4.2 数据转换服务

创建 `backend/app/services/annotation_converter.py`:

```python
from typing import List, Dict, Tuple
from PIL import Image
import os


class AnnotationConverter:
    """标注数据格式转换服务"""

    @staticmethod
    def detection_to_label_studio(
        detection_result: Dict,
        image_path: str
    ) -> Dict:
        """检测结果 → Label Studio 格式"""
        # 获取图片尺寸
        image = Image.open(image_path)
        width, height = image.size

        predictions = []
        for box in detection_result.get('boxes', []):
            x1, y1, x2, y2 = box['bbox']

            # 转换为百分比
            x = (x1 / width) * 100
            y = (y1 / height) * 100
            w = ((x2 - x1) / width) * 100
            h = ((y2 - y1) / height) * 100

            predictions.append({
                "value": {
                    "x": round(x, 2),
                    "y": round(y, 2),
                    "width": round(w, 2),
                    "height": round(h, 2),
                    "rectanglelabels": [box['class']]
                },
                "from_name": "label",
                "to_name": "image",
                "type": "rectanglelabels",
                "score": box.get('confidence', 1.0)
            })

        return {
            "data": {"image": image_path},
            "predictions": [{"result": predictions}] if predictions else []
        }

    @staticmethod
    def label_studio_to_yolo(
        annotations: List[Dict],
        class_mapping: Dict[str, int],
        output_dir: str
    ) -> Tuple[List[str], List[str]]:
        """Label Studio 标注 → YOLO 格式"""
        image_files = []
        label_files = []

        for annotation in annotations:
            image_path = annotation['data']['image']
            image_files.append(image_path)

            # 生成 YOLO 标注文件
            image_name = os.path.basename(image_path)
            label_name = os.path.splitext(image_name)[0] + '.txt'
            label_path = os.path.join(output_dir, label_name)

            yolo_lines = []
            for result in annotation.get('annotations', [{}])[0].get('result', []):
                if result['type'] != 'rectanglelabels':
                    continue

                value = result['value']
                class_name = value['rectanglelabels'][0]
                class_id = class_mapping.get(class_name, 0)

                # 转换坐标
                x = value['x'] / 100
                y = value['y'] / 100
                width = value['width'] / 100
                height = value['height'] / 100

                x_center = x + width / 2
                y_center = y + height / 2

                yolo_lines.append(
                    f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n"
                )

            # 写入文件
            with open(label_path, 'w') as f:
                f.writelines(yolo_lines)

            label_files.append(label_path)

        return image_files, label_files

    @staticmethod
    def label_studio_to_coco(
        annotations: List[Dict],
        category_mapping: Dict[str, int]
    ) -> Dict:
        """Label Studio 标注 → COCO 格式"""
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
            image_path = annotation['data']['image']
            image = Image.open(image_path)
            width, height = image.size

            # 添加图片信息
            coco_data["images"].append({
                "id": image_id,
                "file_name": os.path.basename(image_path),
                "width": width,
                "height": height
            })

            # 添加标注
            for result in annotation.get('annotations', [{}])[0].get('result', []):
                if result['type'] != 'rectanglelabels':
                    continue

                value = result['value']
                class_name = value['rectanglelabels'][0]
                category_id = category_mapping.get(class_name, 1)

                # 转换坐标（COCO 使用绝对坐标）
                x = (value['x'] / 100) * width
                y = (value['y'] / 100) * height
                bbox_width = (value['width'] / 100) * width
                bbox_height = (value['height'] / 100) * height

                coco_data["annotations"].append({
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": category_id,
                    "bbox": [x, y, bbox_width, bbox_height],
                    "area": bbox_width * bbox_height,
                    "iscrowd": 0
                })

                annotation_id += 1

        return coco_data
```

---

## 5. 数据库设计

参见 `Phase0_技术预研_完成报告.md` 中的 Schema 设计部分。

---

## 6. 前端集成

### 6.1 标注任务管理页面

**路由**: `/annotations`

**功能**:
- 创建标注任务（选择检测结果）
- 查看标注任务列表
- 查看标注进度
- 导出标注数据

### 6.2 Label Studio 嵌入

使用 iframe 嵌入 Label Studio 标注界面：

```vue
<template>
  <div class="annotation-workspace">
    <iframe
      :src="`${labelStudioUrl}/projects/${projectId}/data`"
      frameborder="0"
      width="100%"
      height="800px"
    />
  </div>
</template>

<script>
export default {
  data() {
    return {
      labelStudioUrl: 'http://localhost:8080',
      projectId: null
    }
  },
  mounted() {
    // 从路由参数获取项目 ID
    this.projectId = this.$route.params.projectId
  }
}
</script>
```

---

## 7. 实施步骤

### Phase 1: 基础集成（2-3天）
1. ✅ Label Studio 部署和测试
2. ⏸️ 数据库表创建
3. ⏸️ API 服务封装
4. ⏸️ 基本数据转换功能

### Phase 2: 核心功能（2-3天）
1. ⏸️ 标注任务管理 API
2. ⏸️ 预标注数据导入
3. ⏸️ 标注数据导出（YOLO/COCO）
4. ⏸️ 前端界面开发

### Phase 3: 测试和优化（1天）
1. ⏸️ 端到端测试
2. ⏸️ 性能优化
3. ⏸️ 文档完善

---

## 8. 风险和挑战

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 坐标转换错误 | 高 | 充分测试，提供可视化验证工具 |
| Label Studio API 变更 | 中 | 使用稳定版本，封装 API 层 |
| 大规模数据性能问题 | 中 | 批量处理，异步导入 |
| 用户权限管理复杂 | 低 | 初期使用单一管理员账号 |

---

## 9. 后续优化方向

1. **Webhook 集成**: 标注完成自动通知
2. **多人协作**: 支持多用户同时标注
3. **质量控制**: 标注质量检查和审核流程
4. **主动学习**: 优先标注模型不确定的样本
5. **版本管理**: 标注数据版本控制

---

**文档状态**: 设计完成，待实施
**下一步**: 开始 Phase 1 实施
