#!/bin/bash
# 智能目标检测系统 - 一键启动脚本（Conda环境）

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   🚀 智能目标检测系统 - 一键启动${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 确保在正确的目录
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# PID文件路径
PID_FILE="$PROJECT_DIR/.service_pids"

# 清理函数
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 正在停止所有服务...${NC}"

    if [ -f "$PID_FILE" ]; then
        while IFS= read -r pid; do
            if ps -p "$pid" > /dev/null 2>&1; then
                kill "$pid" 2>/dev/null || true
            fi
        done < "$PID_FILE"
        rm -f "$PID_FILE"
    fi

    # 额外清理可能遗留的进程
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "celery -A app.celery_app worker" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true

    echo -e "${GREEN}✅ 所有服务已停止${NC}"
    exit 0
}

# 捕获 Ctrl+C 信号
trap cleanup INT TERM

BACKEND_DIR="$PROJECT_DIR/backend"
BACKEND_VENV_ACTIVATE="$BACKEND_DIR/venv/bin/activate"

# 选择 Python 可执行文件
if command -v python > /dev/null 2>&1; then
    PYTHON_BIN="python"
elif command -v python3 > /dev/null 2>&1; then
    PYTHON_BIN="python3"
else
    echo -e "${RED}❌ 未找到 Python，请先安装/配置 Python 环境${NC}"
    exit 1
fi

# 检查/提示 conda 环境（允许使用 backend/venv 作为后备）
if [ -z "${CONDA_DEFAULT_ENV:-}" ]; then
    echo -e "${YELLOW}⚠️  未检测到已激活的 conda 环境，将尝试使用 backend/venv（如存在）...${NC}"
else
    echo -e "${GREEN}✅ Conda环境: $CONDA_DEFAULT_ENV${NC}"
fi

# 确保后端依赖可用（至少需要 uvicorn）
if ! $PYTHON_BIN -c "import uvicorn" > /dev/null 2>&1; then
    if [ -f "$BACKEND_VENV_ACTIVATE" ]; then
        echo -e "${YELLOW}⚠️  当前环境缺少 uvicorn，尝试激活 backend/venv...${NC}"
        # shellcheck disable=SC1090
        source "$BACKEND_VENV_ACTIVATE"
    fi
fi

if ! $PYTHON_BIN -c "import uvicorn" > /dev/null 2>&1; then
    echo -e "${RED}❌ 后端依赖缺失：未检测到 uvicorn${NC}"
    echo "   解决方案："
    echo "   1) 激活正确的环境（推荐）：conda activate RSD"
    echo "   2) 或在后端目录安装依赖：cd backend && pip install -r requirements.txt"
    exit 1
fi

# 检测 Celery（视频检测需要，缺失时跳过启动）
CELERY_ENABLED=0
if $PYTHON_BIN -c "import celery" > /dev/null 2>&1; then
    CELERY_ENABLED=1
else
    echo -e "${YELLOW}⚠️  未检测到 celery，将跳过 Celery worker（视频检测相关功能不可用）${NC}"
fi

wait_for_backend() {
    local url="http://127.0.0.1:8000/health"
    local max_wait_seconds=20

    for ((i=1; i<=max_wait_seconds; i++)); do
        if $PYTHON_BIN - <<PY > /dev/null 2>&1
import sys
import urllib.request

try:
    with urllib.request.urlopen("${url}", timeout=1) as resp:
        sys.exit(0 if resp.status == 200 else 1)
except Exception:
    sys.exit(1)
PY
        then
            return 0
        fi
        sleep 1
    done
    return 1
}

# 检查并启动PostgreSQL
echo ""
echo "📦 检查依赖服务..."
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  PostgreSQL未运行，尝试启动...${NC}"
    sudo service postgresql start
    sleep 2
    if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PostgreSQL已启动${NC}"
    else
        echo -e "${RED}❌ PostgreSQL启动失败${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ PostgreSQL运行中${NC}"
fi

# 检查并启动Redis
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Redis未运行，尝试启动...${NC}"
    sudo service redis-server start > /dev/null 2>&1 || redis-server --daemonize yes
    sleep 1
    if redis-cli ping > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Redis已启动${NC}"
    else
        echo -e "${RED}❌ Redis启动失败${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ Redis运行中${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   启动应用服务${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 清空PID文件
> "$PID_FILE"

# 1. 启动后端 FastAPI
echo "🔧 启动后端服务..."
cd "$PROJECT_DIR/backend"
nohup $PYTHON_BIN -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > "$PROJECT_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID >> "$PID_FILE"
echo -e "${GREEN}✅ 后端服务已启动 (PID: $BACKEND_PID)${NC}"
echo "⏳ 等待后端就绪..."
if ! wait_for_backend; then
    echo -e "${RED}❌ 后端未能在预期时间内就绪，请检查日志：$PROJECT_DIR/backend.log${NC}"
    tail -n 80 "$PROJECT_DIR/backend.log" 2>/dev/null || true
    exit 1
fi
echo -e "${GREEN}✅ 后端健康检查通过${NC}"

# 2. 启动 Celery Worker
if [ $CELERY_ENABLED -eq 1 ]; then
    echo "⚙️  启动Celery异步任务服务..."
    cd "$PROJECT_DIR/backend"
    nohup $PYTHON_BIN -m celery -A app.celery_app worker --loglevel=info > "$PROJECT_DIR/celery.log" 2>&1 &
    CELERY_PID=$!
    echo $CELERY_PID >> "$PID_FILE"
    echo -e "${GREEN}✅ Celery服务已启动 (PID: $CELERY_PID)${NC}"
    sleep 2
fi

# 3. 启动前端 Vite
echo "🎨 启动前端开发服务器..."
cd "$PROJECT_DIR/frontend"
nohup npm run dev > "$PROJECT_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID >> "$PID_FILE"
echo -e "${GREEN}✅ 前端服务已启动 (PID: $FRONTEND_PID)${NC}"
sleep 3

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}   ✨ 所有服务启动成功！${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📍 访问地址："
echo "   🌐 前端应用:  http://localhost:5173"
echo "   📚 API文档:   http://localhost:8000/docs"
echo "   🔧 API地址:   http://localhost:8000/api/v1"
echo ""
echo "💡 测试账号："
echo "   👤 普通用户:  user / user123"
echo "   👑 管理员:    admin / admin123"
echo ""
echo "📋 日志文件："
echo "   📄 后端日志:  $PROJECT_DIR/backend.log"
echo "   📄 Celery日志: $PROJECT_DIR/celery.log"
echo "   📄 前端日志:  $PROJECT_DIR/frontend.log"
if [ $CELERY_ENABLED -ne 1 ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Celery worker 未启动（celery 未安装），视频检测相关功能不可用${NC}"
fi
echo ""
echo -e "${YELLOW}🛑 停止服务: 按 Ctrl+C 或运行 ./stop.sh${NC}"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 显示实时日志（前端为主）
echo "📊 显示前端实时日志（按 Ctrl+C 停止所有服务）..."
echo ""
tail -f "$PROJECT_DIR/frontend.log"
