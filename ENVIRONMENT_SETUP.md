# 项目环境配置指南

本指南提供完整的环境配置和启动说明，包含Conda和venv两种配置方式。

---

## 📋 目录

- [快速开始](#-快速开始已配置环境的用户)
- [环境要求](#-环境要求)
- [方式一：使用 Conda 环境（推荐）](#-方式一使用-conda-环境推荐)
- [方式二：使用 venv 虚拟环境](#-方式二使用-venv-虚拟环境)
- [一键启动脚本](#-一键启动脚本)
- [启动命令参考](#-启动命令参考)
- [验证安装](#-验证安装)
- [测试账号](#-测试账号)
- [常见问题](#-常见问题)
- [Conda vs venv 对比](#-conda-vs-venv-对比)
- [相关文档](#-相关文档)

---

## 🚀 快速开始（已配置环境的用户）

如果您已经配置好环境，可以直接启动项目：

### 使用一键启动脚本（推荐）

```bash
# 1. 激活环境
conda activate RSD  # 如使用conda
# 或
source backend/venv/bin/activate  # 如使用venv

# 2. 启动项目（自动检查并启动PostgreSQL和Redis）
./start.sh
```

**启动后访问：**
- **前端应用**: http://localhost:5173
- **API 文档**: http://localhost:8000/docs
- **API 地址**: http://localhost:8000/api/v1

### 停止服务

```bash
./stop.sh
# 或按 Ctrl+C
```

---

## 📋 环境要求

### 系统要求
- Python 3.10+
- PostgreSQL 14+
- Redis 6.0+
- Node.js 16+ (前端)

### 检查版本

```bash
# Python版本
python --version  # 或 python3 --version

# PostgreSQL版本
psql --version

# Redis版本
redis-server --version

# Node.js版本
node --version
```

---

## 🔧 方式一：使用 Conda 环境（推荐）

### 为什么选择 Conda？
- ✅ 管理非Python依赖（C库、系统包）
- ✅ 科学计算生态完整
- ✅ 环境隔离更彻底
- ✅ 二进制包预编译，安装快
- ✅ 适合机器学习和数据科学项目

### 1. 安装 Conda

如果未安装，从以下任一来源下载：
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (推荐，体积小)
- [Anaconda](https://www.anaconda.com/) (包含更多预装包)

### 2. 创建 Conda 环境

```bash
# 创建环境（指定Python版本）
conda create -n water_detection python=3.10

# 激活环境
conda activate water_detection
```

**激活成功标志**：命令提示符前会显示 `(water_detection)`

### 3. 安装项目依赖

```bash
cd backend

# 升级pip（推荐）
pip install --upgrade pip

# 安装所有依赖
pip install -r requirements.txt
```

**主要依赖包**：
- **Web框架**: FastAPI 0.104.1, Uvicorn 0.24.0
- **数据库**: SQLAlchemy 2.0.23, Alembic 1.12.1, asyncpg 0.30.0, psycopg2-binary 2.9.11
- **认证**: python-jose 3.3.0, passlib 1.7.4, bcrypt 4.0.1
- **任务队列**: Celery 5.3.4, Redis 5.0.1
- **AI/ML**: PyTorch 2.1.1, Ultralytics YOLO 8.0.220, OpenCV 4.8.1.78
- **工具**: python-dotenv 1.0.0, aiofiles 23.2.1, loguru 0.7.2

### 4. 配置数据库

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件
nano .env  # 或使用其他编辑器
```

在 `.env` 中设置：
```env
# PostgreSQL配置
DATABASE_URL=postgresql+asyncpg://water_detection_user:your_password@localhost:5432/water_detection

# 数据库连接池配置
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_PRE_PING=true
DB_ECHO=false

# Redis配置
REDIS_URL=redis://localhost:6379/0

# JWT密钥（生产环境请修改）
SECRET_KEY=your-secret-key-here

# 其他配置...
```

### 5. 初始化 PostgreSQL 数据库

**方式1：使用自动化脚本（推荐）**

```bash
./init_postgres.sh
```

**方式2：手动初始化**

```bash
# 创建数据库和用户
sudo -u postgres psql <<EOF
CREATE DATABASE water_detection ENCODING 'UTF8';
CREATE USER water_detection_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE water_detection TO water_detection_user;
\c water_detection
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
EOF

# 运行数据库迁移
alembic upgrade head
```

### 6. 已配置环境包含的内容

如果您使用的是已配置好的环境（如 `RSD`），包含：

✅ **已安装组件**:
- Python 3.10.19
- FastAPI 0.104.1
- PostgreSQL 14（数据库已迁移）
- Redis 6.0+
- PyTorch 2.1.1
- Ultralytics YOLO 8.0.220
- 所有项目依赖

✅ **数据库配置**:
- 数据库: water_detection
- 用户: water_detection_user
- 表: users, ml_models, detection_history, alembic_version
- 索引: 23个性能索引

✅ **测试账号**（详见下方"测试账号"部分）

---

## 🐍 方式二：使用 venv 虚拟环境

### 为什么选择 venv？
- ✅ Python内置，无需额外安装
- ✅ 轻量级，虚拟环境体积小
- ✅ 快速创建和删除
- ✅ 与pip生态完全兼容
- ✅ 适合纯Python Web项目

### 1. 创建虚拟环境

```bash
cd backend

# 创建venv环境
python3 -m venv venv

# 或指定Python版本（如果系统有多个版本）
python3.10 -m venv venv
```

### 2. 激活虚拟环境

**Linux/macOS**:
```bash
source venv/bin/activate
```

**Windows CMD**:
```cmd
venv\Scripts\activate.bat
```

**Windows PowerShell**:
```powershell
venv\Scripts\Activate.ps1
```

**Windows Git Bash**:
```bash
source venv/Scripts/activate
```

**激活成功标志**：命令提示符前会显示 `(venv)`

### 3. 安装项目依赖

```bash
# 升级pip（推荐）
pip install --upgrade pip

# 安装所有依赖
pip install -r requirements.txt
```

**使用国内镜像加速（可选）**：
```bash
# 临时使用
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 永久配置
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4. 配置数据库

配置步骤与Conda方式相同，参见上方"方式一"的第4-5步。

### 5. 退出虚拟环境

```bash
deactivate
```

---

## 🎯 一键启动脚本

项目提供一键启动脚本 `start.sh`，自动完成以下操作：

1. ✅ 检查并启动 PostgreSQL
2. ✅ 检查并启动 Redis
3. ✅ 启动后端 FastAPI 服务 (端口 8000)
4. ✅ 启动 Celery 异步任务服务
5. ✅ 启动前端 Vite 开发服务器 (端口 5173)
6. ✅ 显示实时日志

### 使用方法

```bash
# 确保已激活环境
conda activate RSD  # 或 source backend/venv/bin/activate

# 启动所有服务
./start.sh
```

### 日志文件

所有服务日志保存在项目根目录：
- `backend.log` - 后端服务日志
- `celery.log` - Celery 任务日志
- `frontend.log` - 前端服务日志

**查看日志**：
```bash
# 实时查看后端日志
tail -f backend.log

# 实时查看 Celery 日志
tail -f celery.log

# 实时查看前端日志
tail -f frontend.log
```

---

## 📝 启动命令参考

### 方式1：使用启动脚本（推荐）

```bash
./start.sh  # 启动所有服务
./stop.sh   # 停止所有服务
```

### 方式2：手动启动各服务

**启动后端API**:
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**启动Celery Worker**（异步任务，如视频检测）:
```bash
cd backend
celery -A app.celery_app worker --loglevel=info
```

**启动前端**:
```bash
cd frontend
npm install  # 首次运行
npm run dev
```

### 方式3：生产环境部署

**使用 Gunicorn + Uvicorn Workers**:
```bash
pip install gunicorn

gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

**使用 systemd**:
创建服务文件 `/etc/systemd/system/water-detection.service`：
```ini
[Unit]
Description=Water Detection API
After=network.target postgresql.service redis.service

[Service]
Type=notify
User=your_user
Group=your_group
WorkingDirectory=/path/to/project/backend
Environment="PATH=/path/to/project/backend/venv/bin"
ExecStart=/path/to/project/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl start water-detection
sudo systemctl enable water-detection  # 开机自启
sudo systemctl status water-detection
```

### 数据库操作命令

```bash
# 查看数据库迁移状态
cd backend
alembic current

# 查看迁移历史
alembic history

# 升级到最新版本
alembic upgrade head

# 降级一个版本
alembic downgrade -1

# 连接数据库
psql -U water_detection_user -d water_detection -h localhost
```

---

## 🧪 验证安装

运行以下命令验证环境配置：

```bash
# 1. 检查Python版本
python --version

# 2. 检查依赖安装
pip list | grep -E "fastapi|asyncpg|torch|ultralytics"

# 3. 测试应用加载
python -c "from app.main import app; print('✅ 应用加载成功')"

# 4. 测试数据库连接
python -c "
import asyncio
import asyncpg
async def test():
    conn = await asyncpg.connect('postgresql://water_detection_user:your_password@localhost:5432/water_detection')
    print('✅ 数据库连接成功')
    await conn.close()
asyncio.run(test())
"

# 5. 测试Redis连接
redis-cli ping  # 应返回 PONG

# 6. 使用环境验证脚本（如果有）
./check_env.sh
```

---

## 📝 测试账号

系统预置了两个测试账号：

| 角色 | 用户名 | 密码 | 权限 |
|------|--------|------|------|
| 👤 普通用户 | `user` | `user123` | 检测功能、历史记录 |
| 👑 管理员 | `admin` | `admin123` | 所有功能 + 管理后台 |

⚠️ **重要**: 生产环境请务必修改默认密码！

### 功能测试流程

**普通用户测试**:
1. 使用 `user / user123` 登录
2. 点击"开始检测"
3. 上传图片或视频
4. 选择可用模型
5. 调整参数（可选）
6. 开始检测并查看结果
7. 下载结果文件
8. 在"检测历史"中查看所有记录

**管理员测试**:
1. 使用 `admin / admin123` 登录
2. 进入"管理后台"
3. 查看 Dashboard 统计信息
4. 在"用户管理"中管理用户
5. 在"模型管理"中上传和管理YOLO模型
6. 测试所有管理功能

---

## ❓ 常见问题

### 1. 端口被占用

**问题**: `[Errno 98] Address already in use`

**解决方案**:
```bash
# 查找占用端口的进程
lsof -i :8000  # 后端端口
lsof -i :5173  # 前端端口
# Windows: netstat -ano | findstr :8000

# 停止所有服务
./stop.sh

# 或杀死特定进程
kill -9 <PID>

# 或使用其他端口启动
uvicorn app.main:app --port 8001
```

### 2. PostgreSQL 连接失败

**检查清单**:
```bash
# 1. 检查PostgreSQL服务状态
sudo service postgresql status

# 2. 启动PostgreSQL
sudo service postgresql start

# 3. 测试连接
psql -h localhost -U water_detection_user -d water_detection

# 4. 检查.env配置
cat backend/.env | grep DATABASE_URL

# 5. 检查PostgreSQL是否监听正确端口
pg_isready -h localhost -p 5432
```

### 3. Redis 连接失败

**解决方案**:
```bash
# 检查Redis状态
redis-cli ping

# 启动Redis
sudo service redis-server start  # Linux
redis-server  # macOS/Windows

# 检查Redis配置
redis-cli info
```

### 4. 依赖安装失败

**使用国内镜像加速**:
```bash
# 临时使用清华镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 永久配置
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

**常用镜像**:
- 清华：https://pypi.tuna.tsinghua.edu.cn/simple
- 阿里云：https://mirrors.aliyun.com/pypi/simple/
- 豆瓣：https://pypi.douban.com/simple

### 5. Python命令找不到

**问题**: `bash: python: command not found`

**解决方案**:
```bash
# 使用python3
python3 -m venv venv

# 或创建别名（添加到 ~/.bashrc 或 ~/.zshrc）
alias python=python3
alias pip=pip3
```

### 6. PowerShell执行策略错误（Windows）

**问题**: 无法激活venv

**解决方案**:
```powershell
# 检查执行策略
Get-ExecutionPolicy

# 修改为RemoteSigned
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 7. 前端编译错误

**解决方案**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
cd ..
./start.sh
```

### 8. Celery启动失败

**问题**: Celery连接不到Redis

**解决方案**:
```bash
# 确保Redis已启动
redis-cli ping

# 检查.env中Redis配置
cat backend/.env | grep REDIS_URL

# 重启Celery
cd backend
celery -A app.celery_app worker --loglevel=info
```

### 9. 数据库迁移失败

**解决方案**:
```bash
# 检查当前迁移状态
cd backend
alembic current

# 如果数据库不同步，可以重新初始化
alembic downgrade base
alembic upgrade head

# 或查看详细错误
alembic upgrade head --sql
```

### 10. 包版本冲突

**解决方案**:
```bash
# 清理重装
pip uninstall -y -r requirements.txt
pip install -r requirements.txt

# 或使用新的虚拟环境
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🆚 Conda vs venv 对比

### 对比表

| 特性 | venv | Conda |
|------|------|-------|
| 安装 | Python内置 | 需要下载Anaconda/Miniconda |
| 环境大小 | ~10-50MB | ~200MB-1GB |
| 创建速度 | 快（<1秒） | 慢（10-60秒） |
| 包管理 | pip | conda + pip |
| 非Python依赖 | ❌ 不支持 | ✅ 支持 |
| 系统包 | ❌ 不支持 | ✅ 支持 |
| 隔离级别 | Python包 | 系统级 |
| 适用场景 | Web开发、API服务 | 数据科学、机器学习 |

### 选择建议

**使用 venv 的场景**:
- Web应用开发（如本项目）
- 微服务部署
- CI/CD流水线
- 容器化部署
- 轻量级项目

**使用 Conda 的场景**:
- 数据科学项目
- 机器学习研究
- 需要CUDA、cuDNN等复杂依赖
- 多语言混合项目
- 需要管理C/C++库

### 混合使用

可以在Conda环境中使用pip安装包（当前项目推荐方案）：

```bash
# 激活conda环境
conda activate water_detection

# 使用pip安装Python包
pip install -r requirements.txt
```

**注意事项**:
- 优先使用conda安装科学计算包（如有）
- pip安装的包可能与conda包冲突
- 建议：数据科学包用conda，Web框架用pip

---

## 🗄️ PostgreSQL 数据迁移

如果您有现有的 SQLite 数据需要迁移到 PostgreSQL：

```bash
# 确保环境已激活
# conda activate water_detection  # 如使用conda
# source backend/venv/bin/activate  # 如使用venv

cd backend

# 运行迁移脚本
python migrate_to_postgres.py

# 按提示输入PostgreSQL连接URL
# 确认后自动迁移所有数据
```

**详细迁移指南**: [backend/POSTGRES_MIGRATION_GUIDE.md](backend/POSTGRES_MIGRATION_GUIDE.md)

---

## 🔄 环境切换

如果需要在 conda 和 venv 之间切换：

**从 conda 切换到 venv**:
```bash
# 退出conda
conda deactivate

# 激活venv
cd backend
source venv/bin/activate
```

**从 venv 切换到 conda**:
```bash
# 退出venv
deactivate

# 激活conda
conda activate water_detection
```

---

## 📚 相关文档

- **[项目 README](README.md)** - 项目概览和快速开始
- **[实施计划](docs/第一阶段计划/当前状态/IMPLEMENTATION_PLAN.md)** - 当前开发计划
- **[PostgreSQL 迁移指南](backend/POSTGRES_MIGRATION_GUIDE.md)** - 数据库迁移详情
- **[项目使用说明](docs/使用说明.md)** - 详细的用户手册
- **[技术栈说明](docs/技术参考/技术栈说明.md)** - 技术选型和架构
- **[项目结构](docs/技术参考/项目结构.md)** - 代码组织结构
- **[当前状态](docs/第一阶段计划/当前状态/项目状态.md)** - 开发进度
- **[下一步计划](docs/第一阶段计划/当前状态/下一步计划.md)** - 待办事项

---

## 📞 获取帮助

如果遇到问题：

1. 查看本文档的"常见问题"部分
2. 运行 `./check_env.sh` 验证环境（如果有）
3. 查看日志文件：`backend.log`、`celery.log`、`frontend.log`
4. 参考相关文档（见上方链接）
5. 检查 `.env` 配置是否正确

---

**文档版本**: v2.0 (合并版)
**最后更新**: 2025-11-12
**维护者**: 项目开发团队

---

**恭喜！** 按照本指南，您的环境应该已经配置完成。使用 `./start.sh` 启动项目，开始开发或测试吧！🎉
