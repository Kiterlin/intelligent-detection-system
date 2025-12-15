#!/bin/bash
# Label Studio 启动脚本 (Pip 版本 - 开发/测试用)

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   🏷️  Label Studio 启动 (开发模式)${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# 确保在正确的目录
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# 检查 conda 环境
if [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo -e "${RED}❌ 请先激活conda环境：${NC}"
    echo "   conda activate RSD"
    exit 1
fi

echo -e "${GREEN}✅ Conda环境: $CONDA_DEFAULT_ENV${NC}"

# 创建 Label Studio 数据目录
LABEL_STUDIO_DIR="$PROJECT_DIR/data/label-studio"
mkdir -p "$LABEL_STUDIO_DIR"

echo ""
echo "📁 Label Studio 数据目录: $LABEL_STUDIO_DIR"

# 配置环境变量
export LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true
export LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT="$PROJECT_DIR/data"
export LABEL_STUDIO_HOST=http://localhost:8080

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   启动 Label Studio${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# PID 文件
PID_FILE="$PROJECT_DIR/.label_studio.pid"

# 清理旧进程
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  检测到旧的 Label Studio 进程 (PID: $OLD_PID)，正在停止...${NC}"
        kill "$OLD_PID" 2>/dev/null || true
        sleep 2
    fi
    rm -f "$PID_FILE"
fi

# 检查端口是否被占用
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  端口 8080 已被占用${NC}"
    echo "   请停止占用端口的进程，或修改 Label Studio 端口"
    exit 1
fi

echo "🚀 启动 Label Studio..."
echo ""
echo "配置:"
echo "  - 端口: 8080"
echo "  - 数据目录: $LABEL_STUDIO_DIR"
echo "  - 本地文件服务: 启用"
echo ""

# 后台启动 Label Studio
nohup label-studio \
    --data-dir="$LABEL_STUDIO_DIR" \
    --host=0.0.0.0 \
    --port=8080 \
    > "$PROJECT_DIR/label_studio.log" 2>&1 &

LABEL_STUDIO_PID=$!
echo $LABEL_STUDIO_PID > "$PID_FILE"

# 等待启动
echo "⏳ 等待 Label Studio 启动..."
sleep 5

# 检查进程是否存活
if ps -p $LABEL_STUDIO_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Label Studio 启动成功 (PID: $LABEL_STUDIO_PID)${NC}"
else
    echo -e "${RED}❌ Label Studio 启动失败，请查看日志：${NC}"
    echo "   tail -f $PROJECT_DIR/label_studio.log"
    exit 1
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}   ✨ Label Studio 运行中${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "📍 访问地址:"
echo "   🌐 Web UI:      http://localhost:8080"
echo ""
echo "📋 信息:"
echo "   🔢 PID:         $LABEL_STUDIO_PID"
echo "   📂 PID文件:     $PID_FILE"
echo "   📂 数据目录:     $LABEL_STUDIO_DIR"
echo "   📄 日志文件:     $PROJECT_DIR/label_studio.log"
echo ""
echo "👤 首次访问:"
echo "   1. 打开浏览器访问 http://localhost:8080"
echo "   2. 创建管理员账号（邮箱 + 密码）"
echo "   3. 开始使用 Label Studio"
echo ""
echo "🛑 停止 Label Studio:"
echo "   kill $LABEL_STUDIO_PID"
echo "   或运行: pkill -f 'label-studio'"
echo ""
echo "📊 查看实时日志:"
echo "   tail -f $PROJECT_DIR/label_studio.log"
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "💡 提示："
echo "   - Label Studio 已在后台运行"
echo "   - 初次使用需要在 Web UI 创建账号"
echo "   - 数据保存在: $LABEL_STUDIO_DIR"
echo ""
