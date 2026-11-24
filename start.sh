#!/bin/bash
# 智能目标检测系统 - 一键启动脚本
# 不依赖 Conda / PostgreSQL：优先 backend/venv，数据库回退 SQLite，Redis 可用本地二进制。

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

# 本地安装的 redis 不在系统 PATH 时也能被找到
export PATH="${HOME}/.local/bin:${PATH}"
if [ -d "${HOME}/.local/lib" ]; then
    export LD_LIBRARY_PATH="${HOME}/.local/lib${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}"
fi

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

# 优先使用项目虚拟环境，不要求 Conda
if [ -n "${CONDA_DEFAULT_ENV:-}" ]; then
    echo -e "${GREEN}✅ Conda环境: $CONDA_DEFAULT_ENV${NC}"
fi

if [ -x "$BACKEND_DIR/venv/bin/python" ]; then
    PYTHON_BIN="$BACKEND_DIR/venv/bin/python"
    echo -e "${GREEN}✅ Python: backend/venv${NC}"
elif command -v python > /dev/null 2>&1; then
    PYTHON_BIN="python"
    echo -e "${YELLOW}⚠️  未找到 backend/venv，使用当前 python${NC}"
elif command -v python3 > /dev/null 2>&1; then
    PYTHON_BIN="python3"
    echo -e "${YELLOW}⚠️  未找到 backend/venv，使用当前 python3${NC}"
else
    echo -e "${RED}❌ 未找到 Python，请先安装 Python 3.11+${NC}"
    exit 1
fi

if ! "$PYTHON_BIN" -c "import uvicorn" > /dev/null 2>&1; then
    echo -e "${RED}❌ 后端依赖缺失：未检测到 uvicorn${NC}"
    echo "   解决方案："
    echo "   cd backend && python3.11 -m venv venv && ./venv/bin/pip install -r requirements.txt"
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
    local max_wait_seconds=60

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

echo ""
echo "📦 检查依赖服务..."

# PostgreSQL 可选。没有它时强制使用 SQLite，避免 .env 里的 Postgres 地址把启动卡住。
if command -v pg_isready > /dev/null 2>&1 && pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL运行中（沿用 DATABASE_URL）${NC}"
else
    export DATABASE_URL="sqlite+aiosqlite:///./water_detection.db"
    echo -e "${YELLOW}⚠️  PostgreSQL不可用，使用 SQLite: backend/water_detection.db${NC}"
fi

# 检查并启动 Redis。优先系统服务，其次 PATH / ~/.local/bin 里的 redis-server。
REDIS_CLI="$(command -v redis-cli || true)"
REDIS_SERVER="$(command -v redis-server || true)"
redis_ping() {
    if [ -n "$REDIS_CLI" ]; then
        "$REDIS_CLI" ping > /dev/null 2>&1
    else
        return 1
    fi
}

if redis_ping; then
    echo -e "${GREEN}✅ Redis运行中${NC}"
else
    echo -e "${YELLOW}⚠️  Redis未运行，尝试启动...${NC}"
    if [ -z "$REDIS_SERVER" ]; then
        echo -e "${RED}❌ 未找到 redis-server${NC}"
        echo "   把 redis-server 放到 PATH 或 ~/.local/bin 后重试"
        exit 1
    fi
    mkdir -p "$PROJECT_DIR/.redis"
    "$REDIS_SERVER" --daemonize yes \
        --bind 127.0.0.1 --port 6379 \
        --dir "$PROJECT_DIR/.redis" \
        --dbfilename dump.rdb \
        --logfile "$PROJECT_DIR/.redis/redis.log" \
        --pidfile "$PROJECT_DIR/.redis/redis.pid" \
        --protected-mode no
    sleep 1
    if redis_ping; then
        echo -e "${GREEN}✅ Redis已启动${NC}"
    else
        echo -e "${RED}❌ Redis启动失败，日志: $PROJECT_DIR/.redis/redis.log${NC}"
        exit 1
    fi
fi

echo "👤 确保默认账号存在..."
ENSURE_ENV=(PYTHONPATH="$BACKEND_DIR")
if [ -n "${DATABASE_URL:-}" ]; then
    ENSURE_ENV+=(DATABASE_URL="$DATABASE_URL")
fi
if ! (cd "$BACKEND_DIR" && env "${ENSURE_ENV[@]}" "$PYTHON_BIN" scripts/ensure_dev_users.py); then
    echo -e "${RED}❌ 默认账号初始化失败${NC}"
    exit 1
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
    nohup "$PYTHON_BIN" -m celery -A app.celery_app worker --loglevel=info > "$PROJECT_DIR/celery.log" 2>&1 &
    CELERY_PID=$!
    echo $CELERY_PID >> "$PID_FILE"
    sleep 3
    if ps -p "$CELERY_PID" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Celery服务已启动 (PID: $CELERY_PID)${NC}"
    else
        echo -e "${RED}❌ Celery启动后立即退出，视频检测不可用。日志：$PROJECT_DIR/celery.log${NC}"
        tail -n 40 "$PROJECT_DIR/celery.log" 2>/dev/null || true
    fi
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
