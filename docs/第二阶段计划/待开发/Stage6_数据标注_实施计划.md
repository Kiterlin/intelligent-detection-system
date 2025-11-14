# Phase 2 Stage 6 实施计划：数据标注工具

**计划创建时间**: 2025-11-14
**预计工作量**: 3-4 天
**状态**: ⏸️ 待开始
**优先级**: 🔶 中（Stage 5 后）

---

## 📊 概述

实现在线数据标注工具，允许用户修正和完善 AI 检测结果，收集高质量的标注数据（Ground Truth），为后续模型训练提供数据基础。

### 核心价值
- AI 系统的"闭环"开始
- 收集"真值数据"（用户修正过的、100% 准确的数据）
- 为训练更强模型提供"养料"
- 提高检测准确性

---

## 🎯 功能需求

### 1. 标注界面
- ✅ 全屏标注工具（类似 labelImg）
- ✅ 自动加载检测结果作为初始标注
- ✅ 拖动/缩放检测框
- ✅ 添加/删除检测框
- ✅ 修改类别标签
- ✅ 调整置信度（可选）

### 2. 检测结果修正
- ✅ 删除误报（False Positive）- 模型检测到但实际不存在
- ✅ 添加漏报（False Negative）- 模型未检测到但实际存在
- ✅ 修正框位置 - 调整边界框使其更准确
- ✅ 修改类别标签 - 纠正分类错误

### 3. 标注管理
- ✅ 标注历史查看
- ✅ 标注数据导出（YOLO / COCO / 自定义格式）
- ✅ 批量标注操作
- ✅ 标注质量统计

### 4. 数据导出
- ✅ YOLO 格式（.txt）
- ✅ COCO 格式（.json）
- ✅ 自定义格式
- ✅ 包含原始图像

---

## 🏗️ 架构设计

### 数据库设计

#### 新表：`annotations`
```sql
CREATE TABLE annotations (
    id SERIAL PRIMARY KEY,
    history_id INTEGER NOT NULL REFERENCES detection_history(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    annotation_json JSONB NOT NULL,      -- 标注数据（修正后的检测框）
    is_corrected BOOLEAN DEFAULT TRUE,   -- 是否已人工修正
    annotation_type VARCHAR(50),         -- 'correction', 'new', 'verified'
    notes TEXT,                           -- 标注备注
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_history_id (history_id),
    INDEX idx_user_id (user_id),
    INDEX idx_is_corrected (is_corrected),
    UNIQUE (history_id)  -- 每个检测历史只有一个标注记录
);
```

#### 标注 JSON 结构
```json
{
  "image_width": 1920,
  "image_height": 1080,
  "annotations": [
    {
      "id": 1,
      "class": "fish",
      "class_id": 0,
      "bbox": [100, 200, 300, 400],  -- [x1, y1, x2, y2]
      "confidence": 0.95,
      "source": "model",  -- 'model' | 'user'
      "modified": true    -- 是否被用户修改
    },
    {
      "id": 2,
      "class": "coral",
      "class_id": 1,
      "bbox": [500, 600, 700, 800],
      "confidence": 1.0,  -- 用户添加的框置信度为 1.0
      "source": "user",
      "modified": false
    }
  ],
  "deleted_annotations": [3, 5],  -- 被删除的原始检测框 ID
  "metadata": {
    "corrected_by": "user123",
    "correction_time": "2025-11-14T10:30:00",
    "num_added": 1,
    "num_deleted": 2,
    "num_modified": 1
  }
}
```

---

## 🔧 技术方案

### 前端标注库选择

#### 推荐方案：集成成熟的标注库

**不要自己造轮子！** 前端标注工具本身就是一个复杂应用，集成成熟的开源库可以大大节省开发时间。

#### 选项 1：Label Studio Frontend（推荐）
- **官网**: https://labelstud.io/
- **GitHub**: https://github.com/HumanSignal/label-studio-frontend
- **优势**：
  - 功能完整、成熟稳定
  - 支持多种标注类型（边界框、分割、关键点等）
  - 界面美观、用户体验好
  - 可定制性强
- **集成方式**：
  ```bash
  npm install @heartexlabs/label-studio
  ```

#### 选项 2：react-image-annotate
- **GitHub**: https://github.com/waoai/react-image-annotate
- **优势**：
  - 轻量级、易集成
  - 专注于图像标注
  - MIT 许可证
- **缺点**：
  - 功能相对简单
  - 社区活跃度较低

#### 选项 3：Annotorious
- **官网**: https://recogito.github.io/annotorious/
- **GitHub**: https://github.com/recogito/annotorious
- **优势**：
  - 支持图像和视频标注
  - 插件系统
  - W3C 标准支持
- **缺点**：
  - 学习曲线较陡

### 推荐：自定义简化版标注工具

考虑到项目需求相对简单（只需要边界框标注），可以基于 **Konva.js** 或 **Fabric.js** 实现轻量级标注工具。

#### 技术栈：Konva.js
```bash
npm install vue-konva konva
```

**优势**：
- 专为 Canvas 操作设计
- 性能好
- 易于集成到 Vue 3
- 支持拖拽、缩放等交互

---

## 📁 文件结构

```
backend/
├── app/
│   ├── api/v1/
│   │   └── annotations.py              # 标注 API 端点
│   ├── crud/
│   │   └── annotation.py               # 标注 CRUD 操作
│   ├── schemas/
│   │   └── annotation.py               # 标注数据模型
│   ├── services/
│   │   ├── annotation_service.py       # 标注服务
│   │   └── export_service.py           # 导出服务
│   └── utils/
│       ├── yolo_converter.py           # YOLO 格式转换
│       └── coco_converter.py           # COCO 格式转换
│
frontend/
└── src/
    ├── components/
    │   └── annotation/
    │       ├── AnnotationCanvas.vue    # 标注画布组件
    │       ├── ToolBar.vue             # 工具栏
    │       ├── ClassSelector.vue       # 类别选择器
    │       └── AnnotationList.vue      # 标注列表侧边栏
    └── views/
        └── user/
            ├── Annotate.vue            # 标注页面
            └── AnnotationHistory.vue   # 标注历史页面
```

---

## 🚀 实施步骤

### Step 1: 数据库迁移（0.5 天）

```bash
# 创建迁移文件
alembic revision -m "add_annotations_table"

# 执行迁移
alembic upgrade head
```

**任务清单**：
- [ ] 创建 `annotations` 表
- [ ] 添加必要的索引
- [ ] 添加外键约束

---

### Step 2: 后端实现（1 天）

#### 2.1 数据模型（schemas/annotation.py）
```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class BBox(BaseModel):
    """边界框"""
    x1: float
    y1: float
    x2: float
    y2: float

class AnnotationItem(BaseModel):
    """单个标注项"""
    id: Optional[int] = None
    class_name: str
    class_id: int
    bbox: List[float]  # [x1, y1, x2, y2]
    confidence: float = 1.0
    source: str = 'user'  # 'model' | 'user'
    modified: bool = False

class AnnotationData(BaseModel):
    """标注数据"""
    image_width: int
    image_height: int
    annotations: List[AnnotationItem]
    deleted_annotations: List[int] = []
    metadata: dict = {}

class AnnotationCreate(BaseModel):
    """创建标注请求"""
    history_id: int
    annotation_json: AnnotationData
    notes: Optional[str] = None

class AnnotationUpdate(BaseModel):
    """更新标注请求"""
    annotation_json: AnnotationData
    notes: Optional[str] = None

class AnnotationResponse(BaseModel):
    """标注响应"""
    id: int
    history_id: int
    user_id: int
    annotation_json: AnnotationData
    is_corrected: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
```

#### 2.2 CRUD 操作（crud/annotation.py）
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Annotation, DetectionHistory

async def get_annotation_by_history_id(
    db: AsyncSession,
    history_id: int
) -> Optional[Annotation]:
    """获取指定检测历史的标注"""
    result = await db.execute(
        select(Annotation).where(Annotation.history_id == history_id)
    )
    return result.scalar_one_or_none()

async def create_annotation(
    db: AsyncSession,
    user_id: int,
    annotation_data: AnnotationCreate
) -> Annotation:
    """创建标注"""
    annotation = Annotation(
        history_id=annotation_data.history_id,
        user_id=user_id,
        annotation_json=annotation_data.annotation_json.dict(),
        is_corrected=True,
        notes=annotation_data.notes
    )

    db.add(annotation)
    await db.commit()
    await db.refresh(annotation)
    return annotation

async def update_annotation(
    db: AsyncSession,
    annotation_id: int,
    annotation_data: AnnotationUpdate
) -> Annotation:
    """更新标注"""
    result = await db.execute(
        select(Annotation).where(Annotation.id == annotation_id)
    )
    annotation = result.scalar_one()

    annotation.annotation_json = annotation_data.annotation_json.dict()
    annotation.notes = annotation_data.notes
    annotation.updated_at = datetime.now()

    await db.commit()
    await db.refresh(annotation)
    return annotation

async def get_user_annotations(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 50
) -> List[Annotation]:
    """获取用户的所有标注"""
    result = await db.execute(
        select(Annotation)
        .where(Annotation.user_id == user_id)
        .order_by(Annotation.updated_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_annotation_or_detection(
    db: AsyncSession,
    history_id: int
) -> dict:
    """
    获取标注数据，优先返回人工标注，
    如果不存在则返回原始检测结果
    """
    # 1. 尝试获取标注
    annotation = await get_annotation_by_history_id(db, history_id)
    if annotation:
        return {
            'source': 'annotation',
            'data': annotation.annotation_json,
            'is_corrected': True
        }

    # 2. 如果没有标注，返回原始检测结果
    result = await db.execute(
        select(DetectionHistory).where(DetectionHistory.id == history_id)
    )
    history = result.scalar_one_or_none()

    if not history:
        raise ValueError(f"Detection history {history_id} not found")

    return {
        'source': 'detection',
        'data': history.result_json,
        'is_corrected': False
    }
```

#### 2.3 导出服务（services/export_service.py）
```python
import json
from typing import List
from app.schemas.annotation import AnnotationData

class ExportService:
    """标注数据导出服务"""

    def export_yolo(
        self,
        annotations: List[AnnotationData],
        class_names: List[str],
        output_dir: str
    ) -> str:
        """
        导出 YOLO 格式
        每个图像一个 .txt 文件，格式：<class_id> <x_center> <y_center> <width> <height>
        坐标归一化到 [0, 1]
        """
        for idx, ann in enumerate(annotations):
            txt_lines = []

            for item in ann.annotations:
                # 转换为 YOLO 格式
                x1, y1, x2, y2 = item.bbox
                x_center = ((x1 + x2) / 2) / ann.image_width
                y_center = ((y1 + y2) / 2) / ann.image_height
                width = (x2 - x1) / ann.image_width
                height = (y2 - y1) / ann.image_height

                txt_lines.append(
                    f"{item.class_id} {x_center} {y_center} {width} {height}"
                )

            # 保存文件
            txt_path = f"{output_dir}/image_{idx}.txt"
            with open(txt_path, 'w') as f:
                f.write('\n'.join(txt_lines))

        # 生成 classes.txt
        classes_path = f"{output_dir}/classes.txt"
        with open(classes_path, 'w') as f:
            f.write('\n'.join(class_names))

        return output_dir

    def export_coco(
        self,
        annotations: List[AnnotationData],
        class_names: List[str],
        output_file: str
    ) -> str:
        """
        导出 COCO 格式
        单个 JSON 文件包含所有图像和标注
        """
        coco_data = {
            "images": [],
            "annotations": [],
            "categories": []
        }

        # 添加类别
        for idx, name in enumerate(class_names):
            coco_data["categories"].append({
                "id": idx,
                "name": name,
                "supercategory": "object"
            })

        annotation_id = 1
        for image_id, ann in enumerate(annotations, start=1):
            # 添加图像信息
            coco_data["images"].append({
                "id": image_id,
                "width": ann.image_width,
                "height": ann.image_height,
                "file_name": f"image_{image_id}.jpg"
            })

            # 添加标注
            for item in ann.annotations:
                x1, y1, x2, y2 = item.bbox
                width = x2 - x1
                height = y2 - y1

                coco_data["annotations"].append({
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": item.class_id,
                    "bbox": [x1, y1, width, height],  # COCO 格式：[x, y, width, height]
                    "area": width * height,
                    "iscrowd": 0
                })
                annotation_id += 1

        # 保存 JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(coco_data, f, ensure_ascii=False, indent=2)

        return output_file
```

#### 2.4 API 端点（api/v1/annotations.py）
```python
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from app.schemas.annotation import (
    AnnotationCreate, AnnotationUpdate, AnnotationResponse
)
from app.crud import annotation as annotation_crud
from app.services.export_service import ExportService

router = APIRouter(prefix="/annotations", tags=["annotations"])

@router.get("/{history_id}", response_model=dict)
async def get_annotation(
    history_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取标注数据
    优先返回人工标注，如果不存在则返回原始检测结果
    """
    try:
        data = await annotation_crud.get_annotation_or_detection(db, history_id)
        return data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/", response_model=AnnotationResponse)
async def create_annotation(
    annotation_data: AnnotationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建或更新标注"""
    # 检查是否已存在标注
    existing = await annotation_crud.get_annotation_by_history_id(
        db, annotation_data.history_id
    )

    if existing:
        # 更新已有标注
        return await annotation_crud.update_annotation(
            db,
            annotation_id=existing.id,
            annotation_data=AnnotationUpdate(
                annotation_json=annotation_data.annotation_json,
                notes=annotation_data.notes
            )
        )
    else:
        # 创建新标注
        return await annotation_crud.create_annotation(
            db,
            user_id=current_user.id,
            annotation_data=annotation_data
        )

@router.get("/", response_model=List[AnnotationResponse])
async def get_user_annotations(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户的所有标注"""
    return await annotation_crud.get_user_annotations(
        db, user_id=current_user.id, skip=skip, limit=limit
    )

@router.post("/export/yolo")
async def export_yolo(
    annotation_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """导出 YOLO 格式"""
    # 获取标注数据
    annotations = []
    for ann_id in annotation_ids:
        ann = await annotation_crud.get_annotation(db, ann_id)
        if ann and ann.user_id == current_user.id:
            annotations.append(ann.annotation_json)

    # 导出
    export_service = ExportService()
    output_dir = f"storage/exports/yolo_{current_user.id}_{int(time.time())}"
    os.makedirs(output_dir, exist_ok=True)

    export_service.export_yolo(annotations, class_names=['fish', 'coral'], output_dir)

    # 打包为 ZIP
    zip_path = f"{output_dir}.zip"
    shutil.make_archive(output_dir, 'zip', output_dir)

    return FileResponse(
        zip_path,
        filename=f"yolo_export_{int(time.time())}.zip",
        media_type='application/zip'
    )

@router.post("/export/coco")
async def export_coco(
    annotation_ids: List[int],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """导出 COCO 格式"""
    # 类似 YOLO 导出逻辑
    ...
```

**任务清单**：
- [ ] 实现数据模型
- [ ] 实现 CRUD 操作
- [ ] 实现导出服务（YOLO/COCO）
- [ ] 实现 API 端点
- [ ] 添加权限验证

---

### Step 3: 前端实现（1.5 天）

#### 3.1 标注画布组件（AnnotationCanvas.vue）

使用 **vue-konva** 实现标注画布：

```vue
<template>
  <div class="annotation-canvas">
    <v-stage
      :config="stageConfig"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
    >
      <v-layer>
        <!-- 背景图像 -->
        <v-image :config="imageConfig" />

        <!-- 已有标注框 -->
        <v-group
          v-for="(box, index) in boxes"
          :key="box.id"
        >
          <v-rect
            :config="{
              x: box.bbox[0],
              y: box.bbox[1],
              width: box.bbox[2] - box.bbox[0],
              height: box.bbox[3] - box.bbox[1],
              stroke: box.source === 'model' ? '#ff4d4f' : '#52c41a',
              strokeWidth: 2,
              draggable: true
            }"
            @dragend="handleBoxDrag(index, $event)"
          />

          <!-- 类别标签 -->
          <v-text
            :config="{
              x: box.bbox[0],
              y: box.bbox[1] - 20,
              text: `${box.class_name} ${(box.confidence * 100).toFixed(0)}%`,
              fontSize: 14,
              fill: '#fff',
              padding: 4,
              background: box.source === 'model' ? '#ff4d4f' : '#52c41a'
            }"
          />

          <!-- 调整手柄 -->
          <v-circle
            v-for="(handle, hIdx) in getResizeHandles(box)"
            :key="`handle-${index}-${hIdx}`"
            :config="{
              x: handle.x,
              y: handle.y,
              radius: 6,
              fill: '#1890ff',
              draggable: true
            }"
            @dragmove="handleResize(index, hIdx, $event)"
          />
        </v-group>

        <!-- 正在绘制的框 -->
        <v-rect
          v-if="drawingBox"
          :config="{
            x: drawingBox.x,
            y: drawingBox.y,
            width: drawingBox.width,
            height: drawingBox.height,
            stroke: '#1890ff',
            strokeWidth: 2,
            dash: [5, 5]
          }"
        />
      </v-layer>
    </v-stage>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { Stage, Layer, Image as VImage, Rect, Text, Circle, Group } from 'vue-konva'

const props = defineProps({
  imageUrl: String,
  initialBoxes: Array,
  imageWidth: Number,
  imageHeight: Number
})

const emit = defineEmits(['update:boxes'])

const stageConfig = reactive({
  width: window.innerWidth,
  height: window.innerHeight
})

const imageConfig = ref({
  image: null,
  width: props.imageWidth,
  height: props.imageHeight
})

const boxes = ref([...props.initialBoxes])
const drawingBox = ref(null)
const isDrawing = ref(false)

// 加载图像
const loadImage = () => {
  const img = new Image()
  img.src = props.imageUrl
  img.onload = () => {
    imageConfig.value.image = img
  }
}

// 开始绘制
const handleMouseDown = (e) => {
  if (e.target === e.target.getStage()) {
    isDrawing.value = true
    const pos = e.target.getStage().getPointerPosition()
    drawingBox.value = {
      x: pos.x,
      y: pos.y,
      width: 0,
      height: 0
    }
  }
}

// 绘制中
const handleMouseMove = (e) => {
  if (!isDrawing.value) return

  const pos = e.target.getStage().getPointerPosition()
  drawingBox.value.width = pos.x - drawingBox.value.x
  drawingBox.value.height = pos.y - drawingBox.value.y
}

// 完成绘制
const handleMouseUp = (e) => {
  if (!isDrawing.value) return

  isDrawing.value = false

  if (drawingBox.value.width > 10 && drawingBox.value.height > 10) {
    // 添加新框
    boxes.value.push({
      id: Date.now(),
      class_name: 'unknown',
      class_id: 0,
      bbox: [
        drawingBox.value.x,
        drawingBox.value.y,
        drawingBox.value.x + drawingBox.value.width,
        drawingBox.value.y + drawingBox.value.height
      ],
      confidence: 1.0,
      source: 'user',
      modified: false
    })

    emit('update:boxes', boxes.value)
  }

  drawingBox.value = null
}

// 拖拽框
const handleBoxDrag = (index, e) => {
  const box = boxes.value[index]
  const node = e.target
  const x = node.x()
  const y = node.y()
  const width = box.bbox[2] - box.bbox[0]
  const height = box.bbox[3] - box.bbox[1]

  boxes.value[index].bbox = [x, y, x + width, y + height]
  boxes.value[index].modified = true

  emit('update:boxes', boxes.value)
}

// 获取调整手柄位置
const getResizeHandles = (box) => {
  const [x1, y1, x2, y2] = box.bbox
  return [
    { x: x1, y: y1 },       // 左上
    { x: x2, y: y1 },       // 右上
    { x: x1, y: y2 },       // 左下
    { x: x2, y: y2 }        // 右下
  ]
}

// 调整框大小
const handleResize = (boxIndex, handleIndex, e) => {
  const pos = e.target.position()
  const box = boxes.value[boxIndex]
  let [x1, y1, x2, y2] = box.bbox

  // 根据手柄索引更新对应角点
  if (handleIndex === 0) {  // 左上
    x1 = pos.x
    y1 = pos.y
  } else if (handleIndex === 1) {  // 右上
    x2 = pos.x
    y1 = pos.y
  } else if (handleIndex === 2) {  // 左下
    x1 = pos.x
    y2 = pos.y
  } else if (handleIndex === 3) {  // 右下
    x2 = pos.x
    y2 = pos.y
  }

  boxes.value[boxIndex].bbox = [x1, y1, x2, y2]
  boxes.value[boxIndex].modified = true

  emit('update:boxes', boxes.value)
}

loadImage()
</script>

<style scoped>
.annotation-canvas {
  width: 100%;
  height: 100%;
  background: #000;
}
</style>
```

#### 3.2 标注主页面（Annotate.vue）
```vue
<template>
  <div class="annotate-page">
    <div class="toolbar">
      <el-button @click="$router.back()">返回</el-button>
      <el-select v-model="currentClass" placeholder="选择类别">
        <el-option
          v-for="cls in classes"
          :key="cls.id"
          :label="cls.name"
          :value="cls.id"
        />
      </el-select>
      <el-button type="primary" @click="saveAnnotation">保存标注</el-button>
      <el-button type="danger" @click="deleteSelectedBox">删除选中框</el-button>
    </div>

    <div class="main-content">
      <div class="canvas-container">
        <AnnotationCanvas
          :image-url="imageUrl"
          :initial-boxes="boxes"
          :image-width="imageWidth"
          :image-height="imageHeight"
          @update:boxes="boxes = $event"
        />
      </div>

      <div class="sidebar">
        <h3>标注列表 ({{ boxes.length }})</h3>
        <div
          v-for="(box, index) in boxes"
          :key="box.id"
          class="box-item"
          :class="{ selected: selectedBoxIndex === index }"
          @click="selectedBoxIndex = index"
        >
          <div class="box-header">
            <span>{{ box.class_name }}</span>
            <el-tag :type="box.source === 'model' ? 'danger' : 'success'">
              {{ box.source === 'model' ? '模型' : '人工' }}
            </el-tag>
          </div>
          <div class="box-info">
            置信度: {{ (box.confidence * 100).toFixed(0) }}%
          </div>
          <el-button
            size="small"
            type="danger"
            @click.stop="deleteBox(index)"
          >
            删除
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import AnnotationCanvas from '@/components/annotation/AnnotationCanvas.vue'
import api from '@/api'

const route = useRoute()
const historyId = route.params.id

const imageUrl = ref('')
const imageWidth = ref(1920)
const imageHeight = ref(1080)
const boxes = ref([])
const selectedBoxIndex = ref(null)
const currentClass = ref(0)

const classes = ref([
  { id: 0, name: 'fish' },
  { id: 1, name: 'coral' },
  { id: 2, name: 'diver' }
])

const loadAnnotation = async () => {
  try {
    const { data } = await api.get(`/api/v1/annotations/${historyId}`)

    if (data.source === 'annotation') {
      boxes.value = data.data.annotations
    } else {
      // 从检测结果转换
      boxes.value = convertDetectionToAnnotation(data.data)
    }

    // 加载图像
    const historyRes = await api.get(`/api/v1/history/${historyId}`)
    imageUrl.value = historyRes.data.image_url
    imageWidth.value = historyRes.data.image_width
    imageHeight.value = historyRes.data.image_height

  } catch (error) {
    ElMessage.error('加载标注数据失败')
  }
}

const convertDetectionToAnnotation = (detectionData) => {
  // 将检测结果转换为标注格式
  return detectionData.detections.map((det, idx) => ({
    id: idx,
    class_name: det.class,
    class_id: det.class_id,
    bbox: det.bbox,
    confidence: det.confidence,
    source: 'model',
    modified: false
  }))
}

const saveAnnotation = async () => {
  try {
    await api.post('/api/v1/annotations', {
      history_id: historyId,
      annotation_json: {
        image_width: imageWidth.value,
        image_height: imageHeight.value,
        annotations: boxes.value,
        metadata: {
          corrected_by: 'current_user',
          correction_time: new Date().toISOString()
        }
      }
    })

    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const deleteBox = (index) => {
  boxes.value.splice(index, 1)
}

const deleteSelectedBox = () => {
  if (selectedBoxIndex.value !== null) {
    deleteBox(selectedBoxIndex.value)
    selectedBoxIndex.value = null
  }
}

onMounted(() => {
  loadAnnotation()
})
</script>

<style scoped>
.annotate-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.toolbar {
  padding: 10px;
  background: #fff;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  gap: 10px;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.canvas-container {
  flex: 1;
  background: #000;
}

.sidebar {
  width: 300px;
  background: #fff;
  border-left: 1px solid #e8e8e8;
  padding: 20px;
  overflow-y: auto;
}

.box-item {
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  cursor: pointer;
}

.box-item.selected {
  border-color: #1890ff;
  background: #e6f7ff;
}

.box-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}
</style>
```

**任务清单**：
- [ ] 实现标注画布组件（vue-konva）
- [ ] 实现工具栏（类别选择、保存、删除）
- [ ] 实现标注列表侧边栏
- [ ] 添加键盘快捷键支持
- [ ] 添加路由配置

---

### Step 4: 测试（1 天）

#### 4.1 单元测试
```python
# tests/test_annotation.py

async def test_create_annotation():
    """测试创建标注"""
    annotation_data = AnnotationCreate(
        history_id=1,
        annotation_json={
            "image_width": 1920,
            "image_height": 1080,
            "annotations": [...]
        }
    )

    annotation = await annotation_crud.create_annotation(db, user_id=1, annotation_data=annotation_data)
    assert annotation.id is not None
    assert annotation.is_corrected is True

async def test_export_yolo():
    """测试 YOLO 格式导出"""
    export_service = ExportService()
    output_dir = export_service.export_yolo(...)

    assert os.path.exists(f"{output_dir}/classes.txt")
```

#### 4.2 集成测试
- [ ] 测试完整标注流程
- [ ] 测试导出功能（YOLO/COCO）
- [ ] 测试多用户并发标注

#### 4.3 用户体验测试
- [ ] 测试拖拽流畅度
- [ ] 测试大图像性能
- [ ] 测试键盘快捷键

---

## ⚠️ 关键挑战与注意事项

### 1. 前端性能
**问题**：大量标注框导致渲染卡顿
**解决**：
- 使用 Canvas 而非 SVG/DOM
- 虚拟化渲染（只渲染可见区域）
- 优化重绘逻辑

### 2. 数据一致性
**问题**：标注数据与检测结果不同步
**解决**：
- 明确数据优先级（标注 > 检测）
- 记录标注历史版本
- 提供数据合并机制

### 3. 不要造轮子
**问题**：标注工具开发工作量大
**解决**：
- 优先集成成熟的开源库
- 只实现核心功能
- 渐进式增强

---

## 📋 验收标准

### 功能验收
- [ ] 可以加载检测结果作为初始标注
- [ ] 可以添加/删除/修改标注框
- [ ] 可以修改类别标签
- [ ] 可以保存标注数据
- [ ] 可以导出 YOLO 和 COCO 格式

### 用户体验验收
- [ ] 操作流畅（60fps）
- [ ] 快捷键支持
- [ ] 误操作可撤销

### 代码质量
- [ ] 单元测试覆盖率 > 70%
- [ ] 通过 lint 检查

---

## 📚 参考资料

- [Label Studio 文档](https://labelstud.io/guide/)
- [Konva.js 文档](https://konvajs.org/)
- [YOLO 格式说明](https://github.com/ultralytics/yolov5/wiki/Train-Custom-Data)
- [COCO 格式说明](https://cocodataset.org/#format-data)

---

## 🎯 下一步行动

1. **评估标注库**：测试 Label Studio 或 Konva.js
2. **创建数据库迁移**
3. **实现后端 API**
4. **集成前端标注组件**
5. **测试导出功能**

---

**预计完成时间**: 3-4 天
**建议开始日期**: 2025-11-18（Stage 5 完成后）
