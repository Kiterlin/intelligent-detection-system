# 后端 - 水下目标智能检测平台

基于 FastAPI 的高性能异步后端服务。

## 📖 快速导航

**新用户入门**:
- **[环境配置指南](../ENVIRONMENT_SETUP.md)** - 完整的环境配置说明
- **[PostgreSQL 迁移指南](./POSTGRES_MIGRATION_GUIDE.md)** - 数据库迁移详细步骤
- **[项目使用说明](../docs/使用说明.md)** - 系统功能和使用指南

## 技术栈

- **Web 框架**: FastAPI 0.104+
- **数据库**: PostgreSQL 14+ / SQLite (开发)
- **数据库 ORM**: SQLAlchemy 2.0+ (异步)
- **数据库迁移**: Alembic
- **认证**: JWT (python-jose + passlib)
- **任务队列**: Celery + Redis
- **缓存**: Redis 6.0+
- **AI 框架**: PyTorch 2.1+ + Ultralytics YOLO 8.0+

## 目录结构

```
backend/
├── app/                        # 应用主目录
│   ├── api/v1/                # API 路由 v1
│   │   ├── auth.py            # 认证端点
│   │   ├── admin.py           # 管理后台端点
│   │   └── detect.py          # 检测端点
│   ├── models/                # 数据库模型
│   ├── schemas/               # Pydantic 模式
│   ├── crud/                  # CRUD 操作
│   ├── core/                  # 核心功能
│   │   ├── config.py          # 配置管理
│   │   ├── database.py        # 数据库连接
│   │   ├── security.py        # 安全功能
│   │   └── cache.py           # Redis 缓存
│   ├── services/              # 业务逻辑层
│   │   └── model_service.py   # YOLO 模型服务
│   ├── tasks/                 # Celery 异步任务
│   │   └── detection.py       # 检测任务
│   ├── utils/                 # 工具函数
│   └── main.py                # 应用入口
├── alembic/                   # 数据库迁移
│   └── versions/              # 迁移脚本
├── tests/                     # 测试目录
├── models/                    # YOLO 模型文件
├── uploads/                   # 用户上传文件
├── results/                   # 检测结果
├── logs/                      # 日志文件
├── migrate_to_postgres.py     # PostgreSQL 迁移工具
├── init_postgres.sh           # PostgreSQL 初始化脚本
├── init_postgres.sql          # PostgreSQL 初始化 SQL
├── .env.example               # 环境变量模板
└── requirements.txt           # Python 依赖
```

## 快速开始

### 1. 环境配置

**首次使用？** 请先阅读 **[环境配置指南](../ENVIRONMENT_SETUP.md)**

该指南包含：
- ✅ Conda / venv 两种配置方式
- ✅ 依赖安装步骤
- ✅ 数据库配置
- ✅ 常见问题解决

### 2. 配置环境变量

```bash
# 复制模板文件
cp .env.example .env

# 编辑 .env 文件
nano .env  # 或使用其他编辑器
```

**关键配置项**:
```env
# 数据库配置
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/water_detection

# JWT 密钥（生产环境请修改）
SECRET_KEY=your-secret-key-here

# Redis 配置
REDIS_URL=redis://localhost:6379/0

# 文件上传
UPLOAD_DIR=./uploads
MAX_UPLOAD_SIZE=500  # MB
```

### 3. 初始化数据库

**SQLite (开发环境)**:
```bash
# 直接运行迁移
alembic upgrade head
```

**PostgreSQL (生产环境)**:
```bash
# 方式1: 使用自动化脚本
./init_postgres.sh

# 方式2: 手动初始化（见 PostgreSQL 迁移指南）
```

**详细说明**: [PostgreSQL 迁移指南](./POSTGRES_MIGRATION_GUIDE.md)

## 运行服务

### 开发模式

```bash
# 确保已激活虚拟环境
# conda activate water_detection  # 或 source venv/bin/activate

# 启动 FastAPI 服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 启动 Celery Worker (异步任务)

```bash
# 新开终端
celery -A app.celery_app worker --loglevel=info
```

### 生产模式

```bash
# 使用 Gunicorn + Uvicorn Workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## API 文档

启动服务器后，访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **健康检查**: http://localhost:8000/health

### API 端点概览

- **认证**: 5个端点 (注册、登录、刷新Token等)
- **用户管理**: 7个端点 (CRUD、搜索、批量操作)
- **模型管理**: 6个端点 (上传、激活、停用、删除等)
- **检测功能**: 8个端点 (图片/视频检测、历史管理、下载)

**总计**: 26个 API 端点

## 数据库迁移

### 常用命令

```bash
# 查看当前迁移状态
alembic current

# 查看迁移历史
alembic history

# 应用迁移
alembic upgrade head

# 回退一个版本
alembic downgrade -1

# 创建新迁移
alembic revision --autogenerate -m "描述"
```

### PostgreSQL 迁移

如果需要从 SQLite 迁移到 PostgreSQL：

```bash
# 1. 初始化 PostgreSQL
./init_postgres.sh

# 2. 更新 .env 文件中的 DATABASE_URL

# 3. 运行迁移脚本
python migrate_to_postgres.py

# 4. 验证数据
```

**详细指南**: [POSTGRES_MIGRATION_GUIDE.md](./POSTGRES_MIGRATION_GUIDE.md)

## 测试

```bash
# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=app --cov-report=html

# 运行特定测试文件
pytest tests/test_auth.py

# 运行特定测试函数
pytest tests/test_auth.py::test_register
```

## 性能优化

### 数据库优化
- ✅ 23个性能索引已创建
- ✅ PostgreSQL 连接池配置
- ✅ 异步查询优化

### 缓存优化
- ✅ Redis 缓存层实现
- ✅ 模型列表缓存 (TTL: 5分钟)
- ✅ 用户信息缓存 (TTL: 15分钟)
- ✅ 自动缓存失效机制

## 开发规范

- 遵循 PEP 8 代码风格
- 使用 Black 进行代码格式化
- 使用 Flake8 进行代码检查
- 所有 API 端点需要编写测试
- 提交前运行 `pytest` 确保测试通过
- 使用类型注解 (Type Hints)
- 编写清晰的文档字符串 (Docstrings)

## 常见问题

### 1. 依赖安装失败

使用国内镜像加速：
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt
```

### 2. PostgreSQL 连接失败

检查：
- PostgreSQL 服务是否运行
- DATABASE_URL 配置是否正确
- 数据库用户权限是否正确

### 3. Redis 连接失败

确保 Redis 已启动：
```bash
redis-cli ping  # 应返回 PONG
```

**更多问题**: 参考 [环境配置指南 - 常见问题](../ENVIRONMENT_SETUP.md#常见问题)

## 相关文档

- **[环境配置指南](../ENVIRONMENT_SETUP.md)** - 环境配置和安装
- **[PostgreSQL 迁移指南](./POSTGRES_MIGRATION_GUIDE.md)** - 数据库迁移
- **[项目 README](../README.md)** - 项目概览
- **[实施计划](../docs/第一阶段计划/当前状态/IMPLEMENTATION_PLAN.md)** - 当前开发计划
- **[技术栈说明](../docs/技术参考/技术栈说明.md)** - 详细技术栈

---

**最后更新**: 2025-11-12
