# 快速开始指南 - Conda环境

## 🚀 一键启动

在项目根目录下，确保已激活conda环境：

```bash
# 1. 激活环境
conda activate RSD

# 2. 启动项目（会自动检查并启动PostgreSQL和Redis）
./start.sh
```

**就这么简单！** 🎉

---

## 📦 环境已配置完成

您的conda环境 `RSD` 已完整配置，包含：

### ✅ 已安装的组件
- Python 3.10.19
- FastAPI 0.104.1
- PostgreSQL 14（数据库已迁移）
- Redis 6.0+
- PyTorch 2.1.1
- Ultralytics YOLO 8.0.220
- 所有项目依赖

### ✅ 数据库配置
- **数据库**: water_detection
- **用户**: water_detection_user
- **已迁移数据**: 2个用户账号
- **索引**: 23个性能索引

### ✅ 测试账号
- **普通用户**: `user` / `user123`
- **管理员**: `admin` / `admin123`

---

## 🔗 访问地址

启动后访问：

- **API文档**: http://localhost:8000/docs
- **API地址**: http://localhost:8000/api/v1
- **前端界面** (如已启动): http://localhost:5173

---

## 🛑 停止服务

```bash
./stop.sh
```

---

## 📝 常用命令

### 启动服务
```bash
# 方式1: 使用启动脚本（推荐）
./start.sh

# 方式2: 手动启动
cd backend
uvicorn app.main:app --reload --port 8000
```

### 启动前端（如需要）
```bash
cd frontend
npm install  # 首次运行
npm run dev
```

### 启动Celery Worker（异步任务，如视频检测）
```bash
cd backend
celery -A app.celery_app worker --loglevel=info
```

### 数据库操作
```bash
# 查看数据库迁移状态
cd backend
alembic current

# 查看迁移历史
alembic history

# 升级到最新版本
alembic upgrade head

# 连接数据库
psql -U water_detection_user -d water_detection -h localhost
```

---

## 🔧 故障排查

### PostgreSQL未运行
```bash
sudo service postgresql start
sudo service postgresql status
```

### Redis未运行
```bash
sudo service redis-server start
redis-cli ping  # 应返回 PONG
```

### 端口被占用
```bash
# 查找占用8000端口的进程
lsof -i :8000

# 使用其他端口
uvicorn app.main:app --port 8001
```

### 依赖问题
```bash
# 重新安装依赖
pip install -r requirements.txt

# 验证关键依赖
pip list | grep -E "fastapi|asyncpg|torch"
```

---

## 📚 详细文档

- [环境配置指南](ENVIRONMENT_SETUP.md) - 完整的环境配置说明
- [PostgreSQL迁移指南](backend/POSTGRES_MIGRATION_GUIDE.md) - 数据库迁移详情
- [迁移完成报告](backend/MIGRATION_COMPLETE_REPORT.md) - 迁移结果报告

---

## 🎯 下一步

1. **测试API**: 访问 http://localhost:8000/docs 测试API接口
2. **启动前端**: `cd frontend && npm run dev`
3. **上传模型**: 通过管理后台上传YOLO模型文件
4. **开始检测**: 上传图片或视频进行目标检测

---

## 💡 提示

- 启动脚本会自动检查并启动PostgreSQL和Redis
- 开发模式下代码修改会自动重启（--reload）
- 日志输出在终端，方便调试
- 使用 Ctrl+C 停止服务

---

**环境配置时间**: 2025-11-12
**配置状态**: ✅ 已完成
