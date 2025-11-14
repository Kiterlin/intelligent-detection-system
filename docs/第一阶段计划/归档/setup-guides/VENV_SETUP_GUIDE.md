# Python venv 虚拟环境配置指南

本指南介绍如何使用Python内置的venv模块创建和管理项目虚拟环境。

---

## 📋 目录

- [环境要求](#环境要求)
- [创建虚拟环境](#创建虚拟环境)
- [激活虚拟环境](#激活虚拟环境)
- [安装依赖](#安装依赖)
- [配置数据库](#配置数据库)
- [运行应用](#运行应用)
- [常见问题](#常见问题)
- [vs Conda对比](#vs-conda对比)

---

## 环境要求

### 系统要求
- Python 3.10 或更高版本
- pip 20.0 或更高版本
- Git（可选，用于版本控制）

### 检查Python版本

```bash
python --version
# 或
python3 --version
```

**期望输出**：`Python 3.10.x` 或更高版本

### 检查pip版本

```bash
pip --version
# 或
python -m pip --version
```

---

## 创建虚拟环境

### 方法一：使用python -m venv（推荐）

```bash
# 进入项目后端目录
cd /path/to/project/backend

# 创建名为venv的虚拟环境
python -m venv venv

# 或指定Python版本（如果系统有多个版本）
python3.10 -m venv venv
```

### 方法二：使用virtualenv

```bash
# 首先安装virtualenv（如果未安装）
pip install virtualenv

# 创建虚拟环境
virtualenv venv

# 或指定Python版本
virtualenv -p python3.10 venv
```

### 虚拟环境结构

创建后，venv目录结构如下：

```
venv/
├── bin/           # Linux/macOS：可执行文件
│   ├── activate   # 激活脚本
│   ├── python     # Python解释器
│   └── pip        # pip包管理器
├── Scripts/       # Windows：可执行文件
│   ├── activate.bat
│   ├── python.exe
│   └── pip.exe
├── lib/           # 安装的包
│   └── python3.10/
│       └── site-packages/
└── pyvenv.cfg     # 配置文件
```

---

## 激活虚拟环境

### Linux / macOS

```bash
# 激活虚拟环境
source venv/bin/activate

# 或使用完整路径
source /path/to/project/backend/venv/bin/activate
```

**激活成功标志**：命令提示符前会显示 `(venv)`

```bash
(venv) user@hostname:~/project/backend$
```

### Windows

#### CMD

```cmd
venv\Scripts\activate.bat
```

#### PowerShell

```powershell
venv\Scripts\Activate.ps1
```

**注意**：如果PowerShell提示执行策略错误，运行：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Git Bash (Windows)

```bash
source venv/Scripts/activate
```

---

## 安装依赖

### 升级pip（推荐）

```bash
# 激活虚拟环境后
pip install --upgrade pip
```

### 安装项目依赖

#### 完整安装（包含所有依赖）

```bash
pip install -r requirements.txt
```

#### 分步安装（推荐，便于排查问题）

```bash
# 1. 核心Web框架
pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 python-multipart==0.0.6

# 2. 数据库相关
pip install sqlalchemy==2.0.23 alembic==1.12.1
pip install aiosqlite==0.19.0  # SQLite支持
pip install asyncpg==0.29.0 psycopg2-binary==2.9.9  # PostgreSQL支持

# 3. 认证相关
pip install python-jose[cryptography]==3.3.0
pip install passlib[bcrypt]==1.7.4 bcrypt==4.0.1
pip install python-dateutil==2.8.2

# 4. 任务队列
pip install celery==5.3.4 redis==5.0.1

# 5. AI/ML依赖（较大，需要时间）
pip install torch==2.1.1 torchvision==0.16.1
pip install ultralytics==8.0.220
pip install opencv-python==4.8.1.78
pip install pillow==10.1.0 numpy==1.24.4

# 6. 工具库
pip install python-dotenv==1.0.0 aiofiles==23.2.1
pip install httpx==0.25.1 loguru==0.7.2
pip install pydantic==2.5.0 pydantic-settings==2.1.0

# 7. 开发工具（可选）
pip install pytest==7.4.3 pytest-asyncio==0.21.1 pytest-cov==4.1.0
pip install black==23.11.0 flake8==6.1.0
```

### 验证安装

```bash
# 查看已安装的包
pip list

# 检查特定包
pip show fastapi
pip show asyncpg

# 验证导入
python -c "import fastapi; print('FastAPI:', fastapi.__version__)"
python -c "import asyncpg; print('asyncpg:', asyncpg.__version__)"
```

---

## 配置数据库

### PostgreSQL配置

#### 1. 创建.env文件

```bash
# 复制模板
cp .env.example .env

# 编辑配置
nano .env  # 或使用其他编辑器
```

#### 2. 配置数据库URL

在`.env`文件中设置：

```env
# PostgreSQL配置
DATABASE_URL=postgresql+asyncpg://water_detection_user:water_detection_2024@localhost:5432/water_detection

# 数据库连接池（仅PostgreSQL）
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_PRE_PING=true
DB_ECHO=false
```

#### 3. 初始化数据库

**方法一：自动化脚本**

```bash
# 确保虚拟环境已激活
./init_postgres.sh
```

**方法二：手动操作**

```bash
# 创建数据库和用户
sudo -u postgres psql <<EOF
CREATE DATABASE water_detection ENCODING 'UTF8';
CREATE USER water_detection_user WITH PASSWORD 'water_detection_2024';
GRANT ALL PRIVILEGES ON DATABASE water_detection TO water_detection_user;
EOF

# 安装扩展
sudo -u postgres psql -d water_detection <<EOF
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
EOF

# 运行迁移
alembic upgrade head
```

#### 4. 迁移现有数据（可选）

如果有SQLite数据需要迁移：

```bash
python migrate_to_postgres.py
```

---

## 运行应用

### 开发模式

```bash
# 确保虚拟环境已激活
# 确保在backend目录

# 启动FastAPI应用
uvicorn app.main:app --reload --port 8000

# 或指定host（允许外部访问）
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**输出示例**：

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
✅ Database initialized
✅ Redis cache connected
📚 API Documentation: http://localhost:8000/docs
INFO:     Application startup complete.
```

### 生产模式

```bash
# 使用gunicorn + uvicorn workers
pip install gunicorn

# 启动应用（4个worker进程）
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### 后台运行

```bash
# 使用nohup
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > uvicorn.log 2>&1 &

# 查看进程
ps aux | grep uvicorn

# 停止服务
pkill -f "uvicorn app.main:app"
```

### 使用systemd（推荐生产环境）

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

---

## 退出虚拟环境

```bash
deactivate
```

命令提示符会恢复正常（`(venv)` 前缀消失）。

---

## 常见问题

### 1. 找不到python命令

**问题**：`bash: python: command not found`

**解决**：使用`python3`

```bash
python3 -m venv venv
```

或创建别名：

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
alias python=python3
alias pip=pip3
```

### 2. pip安装速度慢

**解决**：使用国内镜像

```bash
# 临时使用
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package_name

# 永久配置
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

常用镜像：
- 清华：https://pypi.tuna.tsinghua.edu.cn/simple
- 阿里云：https://mirrors.aliyun.com/pypi/simple/
- 豆瓣：https://pypi.douban.com/simple

### 3. 权限错误

**问题**：`[Errno 13] Permission denied`

**解决**：不要使用sudo安装到虚拟环境

```bash
# 错误
sudo pip install package_name

# 正确
pip install package_name
```

### 4. 虚拟环境激活失败

**Linux/macOS**：
```bash
# 检查activate脚本是否存在
ls -la venv/bin/activate

# 如果不存在，重新创建虚拟环境
rm -rf venv
python3 -m venv venv
```

**Windows PowerShell**：
```powershell
# 检查执行策略
Get-ExecutionPolicy

# 如果是Restricted，修改为RemoteSigned
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 5. 包版本冲突

**问题**：`ERROR: pip's dependency resolver does not currently take into account...`

**解决**：

```bash
# 方法1：清理重装
pip uninstall -y -r requirements.txt
pip install -r requirements.txt

# 方法2：使用pip-tools
pip install pip-tools
pip-compile requirements.txt
pip-sync

# 方法3：禁用依赖检查（不推荐）
pip install --no-deps package_name
```

### 6. 无法连接PostgreSQL

**检查清单**：

```bash
# 1. PostgreSQL是否运行
sudo service postgresql status

# 2. 能否连接
psql -h localhost -U water_detection_user -d water_detection

# 3. 检查.env配置
cat .env | grep DATABASE_URL

# 4. 测试Python连接
python -c "
import asyncpg
import asyncio
async def test():
    conn = await asyncpg.connect('postgresql://water_detection_user:water_detection_2024@localhost:5432/water_detection')
    print('✅ 连接成功')
    await conn.close()
asyncio.run(test())
"
```

### 7. 端口已被占用

**问题**：`[Errno 98] Address already in use`

**解决**：

```bash
# 查找占用8000端口的进程
lsof -i :8000
# 或
netstat -tulpn | grep 8000

# 杀死进程
kill -9 <PID>

# 或使用其他端口
uvicorn app.main:app --port 8001
```

---

## vs Conda对比

### 何时使用venv

**优势**：
- ✅ Python内置，无需额外安装
- ✅ 轻量级，虚拟环境体积小
- ✅ 快速创建和删除
- ✅ 与pip生态完全兼容
- ✅ 适合纯Python项目

**推荐场景**：
- Web应用开发（如本项目）
- 微服务部署
- CI/CD流水线
- 容器化部署

### 何时使用Conda

**优势**：
- ✅ 管理非Python依赖（C库、系统包）
- ✅ 科学计算生态完整
- ✅ 跨语言项目支持
- ✅ 环境隔离更彻底
- ✅ 二进制包预编译，安装快

**推荐场景**：
- 数据科学项目
- 机器学习研究
- 需要CUDA、cuDNN等复杂依赖
- 多语言混合项目

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
| 适用场景 | Web开发、API服务 | 数据科学、ML |

### 混合使用（当前项目方案）

可以在Conda环境中使用pip安装包（当前方案）：

```bash
# 激活conda环境
conda activate RSD

# 使用pip安装Python包
pip install -r requirements.txt
```

**注意事项**：
- 优先使用conda安装包（如有）
- pip安装的包可能与conda包冲突
- 建议：数据科学包用conda，Web框架用pip

---

## 最佳实践

### 1. 版本管理

**记录确切版本**：

```bash
# 导出当前环境
pip freeze > requirements.txt

# 或更精确的版本锁定
pip-compile requirements.in --output-file requirements.txt
```

**分离开发和生产依赖**：

```
requirements/
├── base.txt          # 基础依赖
├── development.txt   # 开发依赖
└── production.txt    # 生产依赖
```

### 2. 环境隔离

**项目结构**：

```
project/
├── backend/
│   ├── venv/         # 后端虚拟环境
│   ├── app/
│   └── requirements.txt
└── scripts/
    └── activate_env.sh
```

**快速激活脚本**：

```bash
#!/bin/bash
# activate_env.sh
cd "$(dirname "$0")/../backend"
source venv/bin/activate
echo "✅ 虚拟环境已激活：$(which python)"
```

### 3. .gitignore配置

```gitignore
# 虚拟环境
venv/
env/
ENV/
.venv/

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# 环境变量
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# 数据库
*.db
*.sqlite
*.sqlite3
```

### 4. 自动化脚本

**setup.sh**：一键设置环境

```bash
#!/bin/bash
set -e

echo "🚀 开始设置开发环境..."

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python 3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✅ Python版本: $PYTHON_VERSION"

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 升级pip
echo "⬆️  升级pip..."
pip install --upgrade pip

# 安装依赖
echo "📥 安装依赖..."
pip install -r requirements.txt

# 检查.env
if [ ! -f ".env" ]; then
    echo "⚙️  创建.env文件..."
    cp .env.example .env
    echo "⚠️  请编辑.env文件配置数据库连接"
fi

echo "✅ 环境设置完成！"
echo ""
echo "下一步："
echo "  1. 编辑 .env 文件"
echo "  2. 运行：source venv/bin/activate"
echo "  3. 运行：alembic upgrade head"
echo "  4. 运行：uvicorn app.main:app --reload"
```

---

## 总结

### 快速参考命令

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 配置数据库
cp .env.example .env
# 编辑 .env

# 初始化数据库
alembic upgrade head

# 运行应用
uvicorn app.main:app --reload

# 退出
deactivate
```

### 相关文档

- [PostgreSQL迁移指南](POSTGRES_MIGRATION_GUIDE.md)
- [环境变量配置](.env.example)
- [项目README](../README.md)
- [实施计划](../IMPLEMENTATION_PLAN.md)

---

**文档版本**: v1.0
**最后更新**: 2025-11-12
**维护者**: 项目开发团队
