# Phase 2 Stage 5 实施计划：报告生成引擎

**计划创建时间**: 2025-11-14
**预计工作量**: 2-3 天
**状态**: ⏸️ 待开始
**优先级**: 🔥 高（推荐下一步）

---

## 📊 概述

实现智能报告生成引擎，将检测历史数据自动生成专业的 PDF/HTML 分析报告，支持多种报告模板和批量导出功能。

### 核心价值
- 将零散的"检测历史"打包成可交付、可分享的"分析报告"
- 使系统成为"决策支持系统"，对管理层友好
- 支持数据驱动的决策制定

---

## 🎯 功能需求

### 1. 报告管理
- ✅ 报告列表查看
- ✅ 报告生成配置
- ✅ 报告状态跟踪
- ✅ 报告下载（PDF/HTML）
- ✅ 报告删除

### 2. 报告模板（3种）
#### 简要报告（1页）
- 封面：标题、生成日期、时间范围
- 核心统计：总检测数、各类别数量
- 简单图表：类别分布饼图

#### 详细报告（多页）
- 封面：标题、生成日期、时间范围、生成人
- 统计概览：
  - 总检测数、检测频次
  - 各类别占比（饼图）
  - 每日检测趋势（折线图）
  - 置信度分布（直方图）
- 关键发现：
  - 高危目标详情（如 Shark、Wreckage）
  - 关键帧图像和时间戳
  - 异常检测事件
- 附录：原始数据摘要表

#### 对比报告
- 双模型对比分析
- 性能指标对比
- 检测差异分析
- 推荐结论

### 3. 数据筛选
- 按时间范围筛选（日期选择器）
- 按数据集筛选（下拉框）
- 按模型筛选
- 按检测类型筛选（图片/视频）

### 4. 异步生成
- Celery 异步任务
- 实时进度跟踪
- 生成状态轮询
- 失败重试机制

---

## 🏗️ 架构设计

### 数据库设计

#### 新表：`reports`
```sql
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    report_type VARCHAR(50) NOT NULL,  -- 'summary', 'detailed', 'comparison'
    status VARCHAR(50) NOT NULL,        -- 'pending', 'generating', 'completed', 'failed'
    parameters_json JSONB,              -- 报告参数（时间范围、数据源等）
    file_path_pdf VARCHAR(500),
    file_path_html VARCHAR(500),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);
```

#### 参数 JSON 结构
```json
{
  "report_type": "detailed",
  "time_range": {
    "start": "2025-11-01",
    "end": "2025-11-30"
  },
  "filters": {
    "dataset_id": 123,
    "model_id": 45,
    "detection_type": "video"
  },
  "options": {
    "include_images": true,
    "chart_style": "modern"
  }
}
```

---

## 🔧 技术方案

### 后端技术栈

#### 1. PDF 生成库（推荐 WeasyPrint）
```bash
# 安装依赖
pip install weasyprint matplotlib plotly jinja2
```

**WeasyPrint 优势**：
- 直接从 HTML/CSS 生成 PDF
- 支持中文字体
- 布局灵活，样式可控
- Python 原生支持

**系统依赖**：
```bash
# Ubuntu/Debian
sudo apt-get install libpango-1.0-0 libpangocairo-1.0-0

# macOS
brew install pango cairo
```

#### 2. 图表生成
**Matplotlib** - 静态图表生成
```python
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # 无GUI模式

# 生成饼图
plt.figure(figsize=(8, 6))
plt.pie(values, labels=labels, autopct='%1.1f%%')
plt.savefig('chart.png', dpi=300, bbox_inches='tight')
```

**Plotly** - 交互式图表（HTML版）
```python
import plotly.graph_objects as go

fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
fig.write_html('chart.html')
```

#### 3. HTML 模板引擎（Jinja2）
```python
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader('templates/reports'))
template = env.get_template('detailed_report.html')
html_content = template.render(data=report_data)
```

---

## 📁 文件结构

```
backend/
├── app/
│   ├── api/v1/
│   │   └── reports.py                    # 报告 API 端点
│   ├── crud/
│   │   └── report.py                     # 报告 CRUD 操作
│   ├── schemas/
│   │   └── report.py                     # 报告数据模型
│   ├── services/
│   │   ├── report_generator.py           # 报告生成核心服务
│   │   ├── chart_generator.py            # 图表生成服务
│   │   └── data_aggregator.py            # 数据聚合服务
│   ├── tasks/
│   │   └── report_tasks.py               # Celery 报告任务
│   └── templates/
│       └── reports/
│           ├── base.html                 # 基础模板
│           ├── summary_report.html       # 简要报告模板
│           ├── detailed_report.html      # 详细报告模板
│           └── comparison_report.html    # 对比报告模板
│
├── storage/
│   └── reports/                          # 报告文件存储目录
│       ├── pdf/
│       └── html/
│
frontend/
└── src/
    └── views/
        └── user/
            ├── Reports.vue               # 报告列表页
            └── ReportGenerator.vue       # 报告生成配置页
```

---

## 🚀 实施步骤

### Step 1: 数据库迁移（0.5 天）
```bash
# 创建迁移文件
alembic revision -m "add_reports_table"

# 执行迁移
alembic upgrade head
```

**任务清单**：
- [ ] 创建 `reports` 表
- [ ] 添加必要的索引
- [ ] 创建存储目录

---

### Step 2: 后端实现（1 天）

#### 2.1 数据模型（schemas/report.py）
- [ ] `ReportCreate` - 创建报告请求
- [ ] `ReportResponse` - 报告信息响应
- [ ] `ReportListResponse` - 报告列表响应
- [ ] `ReportParameters` - 报告参数模型

#### 2.2 CRUD 操作（crud/report.py）
- [ ] `create_report()` - 创建报告记录
- [ ] `get_report()` - 获取报告详情
- [ ] `get_user_reports()` - 获取用户报告列表
- [ ] `update_report_status()` - 更新报告状态
- [ ] `delete_report()` - 删除报告

#### 2.3 数据聚合服务（services/data_aggregator.py）
```python
class ReportDataAggregator:
    async def aggregate_detection_data(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
        filters: dict
    ) -> dict:
        """聚合检测数据用于报告"""
        # 1. 总体统计
        total_stats = await self._get_total_stats(...)

        # 2. 类别分布
        class_distribution = await self._get_class_distribution(...)

        # 3. 时间趋势
        time_trend = await self._get_time_trend(...)

        # 4. 置信度分布
        confidence_distribution = await self._get_confidence_distribution(...)

        # 5. 关键发现
        key_findings = await self._get_key_findings(...)

        return {
            'total_stats': total_stats,
            'class_distribution': class_distribution,
            'time_trend': time_trend,
            'confidence_distribution': confidence_distribution,
            'key_findings': key_findings
        }
```

#### 2.4 图表生成服务（services/chart_generator.py）
```python
class ChartGenerator:
    def generate_pie_chart(self, data: dict, title: str) -> str:
        """生成饼图，返回文件路径"""

    def generate_line_chart(self, data: dict, title: str) -> str:
        """生成折线图，返回文件路径"""

    def generate_histogram(self, data: list, title: str) -> str:
        """生成直方图，返回文件路径"""
```

#### 2.5 报告生成服务（services/report_generator.py）
```python
class ReportGenerator:
    def __init__(self):
        self.template_env = Environment(
            loader=FileSystemLoader('app/templates/reports')
        )
        self.chart_generator = ChartGenerator()
        self.data_aggregator = ReportDataAggregator()

    async def generate_report(
        self,
        report_id: int,
        report_type: str,
        parameters: dict
    ) -> tuple[str, str]:
        """生成报告，返回 (pdf_path, html_path)"""

        # 1. 聚合数据
        data = await self.data_aggregator.aggregate_detection_data(...)

        # 2. 生成图表
        charts = {
            'pie_chart': self.chart_generator.generate_pie_chart(...),
            'line_chart': self.chart_generator.generate_line_chart(...),
            'histogram': self.chart_generator.generate_histogram(...)
        }

        # 3. 渲染 HTML
        template = self.template_env.get_template(f'{report_type}_report.html')
        html_content = template.render(data=data, charts=charts)

        # 4. 保存 HTML
        html_path = f'storage/reports/html/report_{report_id}.html'
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # 5. 生成 PDF
        pdf_path = f'storage/reports/pdf/report_{report_id}.pdf'
        HTML(string=html_content).write_pdf(pdf_path)

        return pdf_path, html_path
```

#### 2.6 Celery 任务（tasks/report_tasks.py）
```python
from celery import Task
from app.services.report_generator import ReportGenerator
from app.crud import report as report_crud

class ReportGenerationTask(Task):
    """报告生成任务基类"""
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败处理"""
        report_id = args[0]
        # 更新状态为 failed
        report_crud.update_report_status(
            report_id=report_id,
            status='failed',
            error_message=str(exc)
        )

@celery_app.task(base=ReportGenerationTask, bind=True, queue='reports')
async def generate_report_task(self, report_id: int):
    """异步生成报告任务"""
    try:
        # 1. 更新状态为 generating
        report = await report_crud.update_report_status(
            report_id=report_id,
            status='generating'
        )

        # 2. 生成报告
        generator = ReportGenerator()
        pdf_path, html_path = await generator.generate_report(
            report_id=report_id,
            report_type=report.report_type,
            parameters=report.parameters_json
        )

        # 3. 更新状态为 completed
        await report_crud.update_report_status(
            report_id=report_id,
            status='completed',
            file_path_pdf=pdf_path,
            file_path_html=html_path,
            completed_at=datetime.now()
        )

    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise
```

#### 2.7 API 端点（api/v1/reports.py）
```python
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.report import ReportCreate, ReportResponse
from app.tasks.report_tasks import generate_report_task

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/", response_model=ReportResponse)
async def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建报告生成任务"""
    # 1. 创建报告记录
    report = await report_crud.create_report(
        db=db,
        user_id=current_user.id,
        report_data=report_data
    )

    # 2. 启动异步任务
    generate_report_task.delay(report.id)

    return report

@router.get("/", response_model=list[ReportResponse])
async def get_reports(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户报告列表"""
    return await report_crud.get_user_reports(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )

@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取报告详情"""
    report = await report_crud.get_report(db=db, report_id=report_id)
    if not report or report.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

@router.get("/{report_id}/download/{file_type}")
async def download_report(
    report_id: int,
    file_type: str,  # 'pdf' or 'html'
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """下载报告文件"""
    report = await report_crud.get_report(db=db, report_id=report_id)
    if not report or report.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.status != 'completed':
        raise HTTPException(status_code=400, detail="Report not ready")

    file_path = report.file_path_pdf if file_type == 'pdf' else report.file_path_html

    return FileResponse(
        path=file_path,
        filename=f"{report.name}.{file_type}",
        media_type='application/pdf' if file_type == 'pdf' else 'text/html'
    )

@router.delete("/{report_id}")
async def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除报告"""
    report = await report_crud.get_report(db=db, report_id=report_id)
    if not report or report.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Report not found")

    # 删除文件
    if report.file_path_pdf and os.path.exists(report.file_path_pdf):
        os.remove(report.file_path_pdf)
    if report.file_path_html and os.path.exists(report.file_path_html):
        os.remove(report.file_path_html)

    # 删除数据库记录
    await report_crud.delete_report(db=db, report_id=report_id)

    return {"message": "Report deleted successfully"}
```

---

### Step 3: HTML 模板设计（0.5 天）

#### 3.1 基础模板（templates/reports/base.html）
```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <style>
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: "Microsoft YaHei", Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #1890ff;
            padding-bottom: 20px;
        }
        .section {
            margin-bottom: 30px;
            page-break-inside: avoid;
        }
        .chart {
            text-align: center;
            margin: 20px 0;
        }
        .chart img {
            max-width: 100%;
            height: auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f0f0f0;
        }
    </style>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```

#### 3.2 详细报告模板（templates/reports/detailed_report.html）
```html
{% extends "base.html" %}

{% block content %}
<div class="header">
    <h1>{{ data.title }}</h1>
    <p>生成日期: {{ data.generated_at }}</p>
    <p>时间范围: {{ data.time_range.start }} 至 {{ data.time_range.end }}</p>
</div>

<div class="section">
    <h2>一、统计概览</h2>
    <table>
        <tr>
            <th>指标</th>
            <th>数值</th>
        </tr>
        <tr>
            <td>总检测次数</td>
            <td>{{ data.total_stats.total_detections }}</td>
        </tr>
        <tr>
            <td>检测对象总数</td>
            <td>{{ data.total_stats.total_objects }}</td>
        </tr>
        <tr>
            <td>平均置信度</td>
            <td>{{ data.total_stats.avg_confidence }}%</td>
        </tr>
    </table>
</div>

<div class="section">
    <h2>二、类别分布</h2>
    <div class="chart">
        <img src="{{ charts.pie_chart }}" alt="类别分布饼图">
    </div>
</div>

<div class="section">
    <h2>三、检测趋势</h2>
    <div class="chart">
        <img src="{{ charts.line_chart }}" alt="时间趋势折线图">
    </div>
</div>

<div class="section">
    <h2>四、关键发现</h2>
    {% for finding in data.key_findings %}
    <div>
        <h3>{{ finding.title }}</h3>
        <p>{{ finding.description }}</p>
        {% if finding.image %}
        <img src="{{ finding.image }}" style="max-width: 500px;">
        {% endif %}
    </div>
    {% endfor %}
</div>
{% endblock %}
```

**任务清单**：
- [ ] 创建基础模板
- [ ] 创建简要报告模板
- [ ] 创建详细报告模板
- [ ] 创建对比报告模板
- [ ] 测试模板渲染

---

### Step 4: 前端实现（1 天）

#### 4.1 报告列表页（Reports.vue）
```vue
<template>
  <div class="reports-page">
    <el-page-header @back="$router.back()" content="报告管理" />

    <div class="actions">
      <el-button type="primary" @click="showGenerator = true">
        <el-icon><Plus /></el-icon>
        生成新报告
      </el-button>
    </div>

    <el-table :data="reports" v-loading="loading">
      <el-table-column prop="name" label="报告名称" />
      <el-table-column prop="report_type" label="类型">
        <template #default="{ row }">
          <el-tag>{{ reportTypeMap[row.report_type] }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" />
      <el-table-column prop="status" label="状态">
        <template #default="{ row }">
          <el-tag :type="statusTypeMap[row.status]">
            {{ statusMap[row.status] }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button-group v-if="row.status === 'completed'">
            <el-button size="small" @click="downloadReport(row.id, 'pdf')">
              下载PDF
            </el-button>
            <el-button size="small" @click="viewReport(row.id)">
              查看
            </el-button>
          </el-button-group>
          <el-button
            size="small"
            type="danger"
            @click="deleteReport(row.id)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 报告生成器对话框 -->
    <ReportGenerator
      v-model="showGenerator"
      @generated="loadReports"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const reports = ref([])
const loading = ref(false)
const showGenerator = ref(false)

const reportTypeMap = {
  summary: '简要报告',
  detailed: '详细报告',
  comparison: '对比报告'
}

const statusMap = {
  pending: '等待中',
  generating: '生成中',
  completed: '已完成',
  failed: '失败'
}

const statusTypeMap = {
  pending: 'info',
  generating: 'warning',
  completed: 'success',
  failed: 'danger'
}

const loadReports = async () => {
  loading.value = true
  try {
    const { data } = await api.get('/api/v1/reports')
    reports.value = data
  } catch (error) {
    ElMessage.error('加载报告列表失败')
  } finally {
    loading.value = false
  }
}

const downloadReport = (reportId, fileType) => {
  window.open(`/api/v1/reports/${reportId}/download/${fileType}`)
}

const viewReport = (reportId) => {
  window.open(`/api/v1/reports/${reportId}/download/html`, '_blank')
}

const deleteReport = async (reportId) => {
  await ElMessageBox.confirm('确定删除此报告吗？', '提示', {
    type: 'warning'
  })

  try {
    await api.delete(`/api/v1/reports/${reportId}`)
    ElMessage.success('删除成功')
    loadReports()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadReports()

  // 轮询检查生成中的报告
  setInterval(() => {
    const generatingReports = reports.value.filter(r => r.status === 'generating')
    if (generatingReports.length > 0) {
      loadReports()
    }
  }, 5000)
})
</script>
```

#### 4.2 报告生成器（ReportGenerator.vue）
```vue
<template>
  <el-dialog
    v-model="visible"
    title="生成报告"
    width="600px"
  >
    <el-form :model="form" label-width="100px">
      <el-form-item label="报告名称">
        <el-input v-model="form.name" placeholder="例如：11月水下安全巡检报告" />
      </el-form-item>

      <el-form-item label="报告类型">
        <el-radio-group v-model="form.report_type">
          <el-radio value="summary">简要报告</el-radio>
          <el-radio value="detailed">详细报告</el-radio>
          <el-radio value="comparison">对比报告</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="时间范围">
        <el-date-picker
          v-model="form.dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
        />
      </el-form-item>

      <el-form-item label="数据源">
        <el-select v-model="form.datasetId" placeholder="选择数据集（可选）">
          <el-option label="所有数据" :value="null" />
          <el-option
            v-for="dataset in datasets"
            :key="dataset.id"
            :label="dataset.name"
            :value="dataset.id"
          />
        </el-select>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="generateReport" :loading="generating">
        生成报告
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue', 'generated'])

const visible = ref(false)
const generating = ref(false)
const datasets = ref([])
const form = ref({
  name: '',
  report_type: 'detailed',
  dateRange: [],
  datasetId: null
})

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    loadDatasets()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const loadDatasets = async () => {
  try {
    const { data } = await api.get('/api/v1/datasets')
    datasets.value = data
  } catch (error) {
    console.error('Failed to load datasets')
  }
}

const generateReport = async () => {
  if (!form.value.name || !form.value.dateRange.length) {
    ElMessage.warning('请填写完整信息')
    return
  }

  generating.value = true
  try {
    await api.post('/api/v1/reports', {
      name: form.value.name,
      report_type: form.value.report_type,
      parameters: {
        time_range: {
          start: form.value.dateRange[0],
          end: form.value.dateRange[1]
        },
        filters: {
          dataset_id: form.value.datasetId
        }
      }
    })

    ElMessage.success('报告生成任务已启动，请稍后查看')
    visible.value = false
    emit('generated')
  } catch (error) {
    ElMessage.error('生成失败')
  } finally {
    generating.value = false
  }
}
</script>
```

**任务清单**：
- [ ] 实现报告列表页
- [ ] 实现报告生成器组件
- [ ] 添加轮询机制检查生成状态
- [ ] 实现报告下载功能
- [ ] 添加路由配置

---

### Step 5: Celery 配置（0.5 天）

#### 5.1 创建专用队列
```python
# backend/app/core/celery_app.py

CELERY_TASK_ROUTES = {
    'app.tasks.detection_tasks.*': {'queue': 'detection'},
    'app.tasks.report_tasks.*': {'queue': 'reports'},  # 新增
}
```

#### 5.2 启动专用 Worker
```bash
# 报告生成 Worker
celery -A app.core.celery_app worker \
  -Q reports \
  -n report-worker@%h \
  --loglevel=info \
  --concurrency=2
```

**任务清单**：
- [ ] 配置 Celery 队列路由
- [ ] 更新 Worker 启动脚本
- [ ] 测试任务分发

---

### Step 6: 测试（0.5 天）

#### 6.1 单元测试
```python
# tests/test_report_generator.py

async def test_generate_summary_report():
    """测试生成简要报告"""
    generator = ReportGenerator()
    pdf_path, html_path = await generator.generate_report(
        report_id=1,
        report_type='summary',
        parameters={...}
    )

    assert os.path.exists(pdf_path)
    assert os.path.exists(html_path)

async def test_chart_generation():
    """测试图表生成"""
    chart_gen = ChartGenerator()
    path = chart_gen.generate_pie_chart(
        data={'A': 10, 'B': 20},
        title='测试饼图'
    )

    assert os.path.exists(path)
```

#### 6.2 集成测试
- [ ] 测试完整报告生成流程
- [ ] 测试异步任务执行
- [ ] 测试文件下载
- [ ] 测试错误处理

#### 6.3 性能测试
- [ ] 测试大数据量报告生成时间
- [ ] 测试并发报告生成
- [ ] 测试队列隔离效果

---

## ⚠️ 关键挑战与注意事项

### 1. 性能优化
**问题**：大数据量聚合查询可能很慢
**解决**：
- 使用数据库索引
- 分页查询大数据集
- 考虑预聚合关键指标

### 2. 队列隔离
**问题**：报告生成耗时长，可能阻塞检测任务
**解决**：
- 使用专用 Celery 队列
- 设置任务优先级
- 限制并发数量

### 3. 中文字体
**问题**：PDF 中文显示问题
**解决**：
```python
# 在 HTML 模板中指定字体
<style>
body {
    font-family: "Microsoft YaHei", "SimHei", sans-serif;
}
</style>
```

### 4. 图片路径
**问题**：WeasyPrint 需要绝对路径
**解决**：
- 使用 base64 编码嵌入图片
- 或使用绝对文件路径

### 5. 内存管理
**问题**：大量图表生成占用内存
**解决**：
- 及时清理临时图表文件
- 使用 Matplotlib 的 `plt.close()` 释放资源

---

## 📋 验收标准

### 功能验收
- [ ] 可以创建 3 种类型的报告
- [ ] 报告生成异步执行
- [ ] 生成状态实时显示
- [ ] 支持 PDF 和 HTML 格式下载
- [ ] 报告包含图表和统计数据
- [ ] 中文显示正常

### 性能验收
- [ ] 简要报告生成时间 < 30 秒
- [ ] 详细报告生成时间 < 60 秒
- [ ] 不阻塞检测任务执行

### 代码质量
- [ ] 单元测试覆盖率 > 80%
- [ ] 通过 lint 检查
- [ ] 代码有充分注释

---

## 📚 参考资料

### 技术文档
- [WeasyPrint 官方文档](https://doc.courtbouillon.org/weasyprint/)
- [Matplotlib 中文支持](https://matplotlib.org/stable/users/explain/text/text_props.html)
- [Jinja2 模板文档](https://jinja.palletsprojects.com/)

### 示例项目
- [Django PDF Reports](https://github.com/bprinty/django-pdf-reports)
- [Flask WeasyPrint](https://github.com/Kozea/Flask-WeasyPrint)

---

## 🎯 下一步行动

1. **安装依赖**：`pip install weasyprint matplotlib jinja2`
2. **创建数据库迁移**：`alembic revision -m "add_reports_table"`
3. **实现后端核心服务**：从 `ReportGenerator` 开始
4. **测试报告生成**：先实现简要报告模板
5. **前端集成**：实现报告列表和生成器

---

**预计完成时间**: 2-3 天
**建议开始日期**: 2025-11-15
