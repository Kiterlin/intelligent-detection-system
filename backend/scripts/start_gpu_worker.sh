#!/bin/bash
# GPU Worker 启动脚本 - 专门用于处理模型训练任务
# 使用 solo pool 确保同一时间只有一个训练任务运行（防止GPU资源竞争）

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   🎮 GPU Worker 启动 (Training Queue)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 确保在正确的目录
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR/backend"

# 检查 conda 环境
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo -e "${RED}❌ 请先激活conda环境：${NC}"
    echo "   conda activate RSD"
    exit 1
fi

echo -e "${GREEN}✅ Conda环境: $CONDA_DEFAULT_ENV${NC}"

# 检查 GPU 可用性
echo ""
echo "🔍 检查 GPU 环境..."
if nvidia-smi > /dev/null 2>&1; then
    echo -e "${GREEN}✅ GPU 可用${NC}"
    nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader
else
    echo -e "${YELLOW}⚠️  未检测到 GPU，将使用 CPU 训练（速度较慢）${NC}"
fi

# 检查 Redis
echo ""
echo "🔍 检查 Redis 连接..."
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis 运行中${NC}"
else
    echo -e "${RED}❌ Redis 未运行，请先启动 Redis${NC}"
    exit 1
fi

# 检查 PyTorch CUDA
echo ""
echo "🔍 检查 PyTorch CUDA..."
python3 -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')" || exit 1

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   启动 GPU Worker${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# PID 文件
PID_FILE="$PROJECT_DIR/.gpu_worker.pid"

# 清理旧进程
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  检测到旧的 GPU Worker 进程 (PID: $OLD_PID)，正在停止...${NC}"
        kill "$OLD_PID" 2>/dev/null || true
        sleep 2
    fi
    rm -f "$PID_FILE"
fi

# 启动 GPU Worker (使用 solo pool)
# solo pool: 单进程池，确保同一时间只有一个任务在执行
# -Q training: 只监听 training 队列
# --concurrency=1: 并发数为 1
# -P solo: 使用 solo 池类型（单线程，适合 GPU 任务）
echo "🚀 启动 GPU Worker (solo pool, training queue only)..."
echo ""
echo "配置："
echo "  - Pool: solo (单进程，防止GPU资源竞争）"
echo "  - Queue: training (只处理训练任务）"
echo "  - Concurrency: 1 (同时只运行一个任务）"
echo "  - Prefetch: 1 (每次只预取一个任务）"
echo ""

# 后台运行
nohup celery -A app.celery_app worker \
    --pool=solo \
    --queues=training \
    --concurrency=1 \
    --loglevel=info \
    --logfile="$PROJECT_DIR/gpu_worker.log" \
    > "$PROJECT_DIR/gpu_worker_stdout.log" 2>&1 &

GPU_WORKER_PID=$!
echo $GPU_WORKER_PID > "$PID_FILE"

# 等待启动
sleep 3

# 检查进程是否存活
if ps -p $GPU_WORKER_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✅ GPU Worker 启动成功 (PID: $GPU_WORKER_PID)${NC}"
else
    echo -e "${RED}❌ GPU Worker 启动失败，请查看日志：${NC}"
    echo "   tail -f $PROJECT_DIR/gpu_worker.log"
    exit 1
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}   ✨ GPU Worker 运行中${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📋 信息："
echo "   🔢 PID:        $GPU_WORKER_PID"
echo "   📂 PID文件:    $PID_FILE"
echo "   📄 日志文件:   $PROJECT_DIR/gpu_worker.log"
echo "   📊 标准输出:   $PROJECT_DIR/gpu_worker_stdout.log"
echo ""
echo "🛑 停止 GPU Worker:"
echo "   kill $GPU_WORKER_PID"
echo "   或运行: pkill -f 'celery.*training'"
echo ""
echo "📊 查看实时日志:"
echo "   tail -f $PROJECT_DIR/gpu_worker.log"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
