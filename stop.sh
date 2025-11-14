#!/bin/bash
# 水下目标检测系统 - 停止脚本

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${YELLOW}   🛑 停止水下目标检测系统${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 确保在正确的目录
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# PID文件路径
PID_FILE="$PROJECT_DIR/.service_pids"

# 停止通过 start.sh 启动的服务
if [ -f "$PID_FILE" ]; then
    echo "📋 从PID文件停止服务..."
    while IFS= read -r pid; do
        if ps -p "$pid" > /dev/null 2>&1; then
            SERVICE_NAME=$(ps -p "$pid" -o comm= 2>/dev/null || echo "服务")
            echo "   停止 $SERVICE_NAME (PID: $pid)..."
            kill "$pid" 2>/dev/null || true
        fi
    done < "$PID_FILE"
    rm -f "$PID_FILE"
    sleep 1
fi

# 停止FastAPI服务
if pgrep -f "uvicorn app.main:app" > /dev/null; then
    echo "🔧 停止 FastAPI 后端服务..."
    pkill -f "uvicorn app.main:app"
    sleep 1
    echo -e "${GREEN}   ✅ FastAPI 已停止${NC}"
else
    echo "   ℹ️  FastAPI 未运行"
fi

# 停止Celery worker
if pgrep -f "celery -A app.celery_app worker" > /dev/null; then
    echo "⚙️  停止 Celery worker..."
    pkill -f "celery -A app.celery_app worker"
    sleep 1
    echo -e "${GREEN}   ✅ Celery worker 已停止${NC}"
else
    echo "   ℹ️  Celery worker 未运行"
fi

# 停止前端 Vite 服务
if pgrep -f "vite" > /dev/null; then
    echo "🎨 停止前端 Vite 服务..."
    pkill -f "vite"
    sleep 1
    echo -e "${GREEN}   ✅ Vite 已停止${NC}"
else
    echo "   ℹ️  Vite 未运行"
fi

# 检查是否还有残留进程
echo ""
REMAINING=$(ps aux | grep -E "uvicorn|celery|vite" | grep -v grep | wc -l)
if [ $REMAINING -gt 0 ]; then
    echo -e "${YELLOW}⚠️  发现残留进程，强制清理...${NC}"
    pkill -9 -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -9 -f "celery -A app.celery_app" 2>/dev/null || true
    pkill -9 -f "vite" 2>/dev/null || true
    sleep 1
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}   ✅ 所有服务已停止${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 显示端口状态
echo "📊 端口状态检查："
if lsof -i :8000 > /dev/null 2>&1; then
    echo -e "   ⚠️  端口 8000 仍被占用"
else
    echo -e "   ${GREEN}✅ 端口 8000 空闲${NC}"
fi

if lsof -i :5173 > /dev/null 2>&1; then
    echo -e "   ⚠️  端口 5173 仍被占用"
else
    echo -e "   ${GREEN}✅ 端口 5173 空闲${NC}"
fi

echo ""
