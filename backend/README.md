# 后端 - 水下目标智能检测平台

基于 FastAPI 的高性能异步后端服务。

## 技术栈

- **Web 框架**: FastAPI 0.104+
- **数据库 ORM**: SQLAlchemy 2.0+
- **数据库迁移**: Alembic
- **认证**: JWT (python-jose + passlib)
- **任务队列**: Celery + Redis
- **AI 框架**: PyTorch + Ultralytics (YOLO)

## 目录结构

```
backend/
├── app/              # 应用主目录
│   ├── api/          # API 路由
│   ├── models/       # 数据库模型
│   ├── schemas/      # Pydantic 模式
│   ├── services/     # 业务逻辑层
│   ├── core/         # 核心功能（安全、配置等）
│   ├── tasks/        # Celery 任务
│   └── utils/        # 工具函数
├── alembic/          # 数据库迁移
├── tests/            # 测试目录
├── models/           # YOLO 模型文件
├── uploads/          # 用户上传文件
├── results/          # 检测结果
└── logs/             # 日志文件
```

## 安装

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置必要的配置

# 运行数据库迁移
alembic upgrade head
```

## 运行

### 开发模式

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 生产模式

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API 文档

启动服务器后，访问：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html

# 运行特定测试文件
pytest tests/test_auth.py
```

## 数据库迁移

```bash
# 创建新迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回退迁移
alembic downgrade -1
```

## 开发规范

- 遵循 PEP 8 代码风格
- 使用 Black 进行代码格式化
- 使用 Flake8 进行代码检查
- 所有 API 端点需要编写测试
- 提交前运行 `pytest` 确保测试通过
