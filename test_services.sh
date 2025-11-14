#!/bin/bash
# 服务状态测试脚本

echo "========================================"
echo "   水下目标检测系统 - 服务状态检查"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查后端
echo "1️⃣  检查后端服务 (FastAPI)"
if lsof -i :8000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 后端服务运行正常${NC} (http://localhost:8000)"
    echo "   访问API文档: http://localhost:8000/docs"
else
    echo -e "${RED}❌ 后端服务未运行${NC}"
    echo "   启动命令: cd backend && uvicorn app.main:app --reload --port 8000"
fi
echo ""

# 检查前端
echo "2️⃣  检查前端服务 (Vite)"
if lsof -i :5173 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 前端服务运行正常${NC} (http://localhost:5173)"
else
    echo -e "${RED}❌ 前端服务未运行${NC}"
    echo "   启动命令: cd frontend && npm run dev"
fi
echo ""

# 检查Redis
echo "3️⃣  检查Redis服务"
if redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis服务运行正常${NC}"
    REDIS_VERSION=$(redis-cli --version | awk '{print $2}')
    echo "   版本: $REDIS_VERSION"
else
    echo -e "${RED}❌ Redis服务未运行${NC}"
    echo "   启动命令: redis-server"
fi
echo ""

# 检查Celery Worker
echo "4️⃣  检查Celery Worker (异步任务)"
if ps aux | grep -v grep | grep "celery.*worker" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Celery Worker运行正常${NC}"
    CELERY_PROCESSES=$(ps aux | grep -v grep | grep "celery.*worker" | wc -l)
    echo "   进程数: $CELERY_PROCESSES"
else
    echo -e "${YELLOW}⚠️  Celery Worker未运行${NC}"
    echo "   影响: 视频检测功能将无法使用"
    echo "   启动命令: cd backend && celery -A app.celery_app worker --loglevel=info"
fi
echo ""

# 检查数据库
echo "5️⃣  检查数据库服务"
if command -v psql &> /dev/null; then
    if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PostgreSQL服务运行正常${NC}"
        PG_VERSION=$(psql --version | awk '{print $3}')
        echo "   版本: PostgreSQL $PG_VERSION"
    else
        echo -e "${YELLOW}⚠️  PostgreSQL服务未运行，使用SQLite${NC}"
    fi
elif [ -f "backend/water_detection.db" ]; then
    echo -e "${GREEN}✅ 使用SQLite数据库${NC}"
    DB_SIZE=$(du -h backend/water_detection.db | awk '{print $1}')
    echo "   数据库文件大小: $DB_SIZE"
else
    echo -e "${RED}❌ 未找到数据库${NC}"
    echo "   运行迁移: cd backend && alembic upgrade head"
fi
echo ""

# 测试后端API
echo "6️⃣  测试后端API连接"
HEALTH_CHECK=$(curl -s -w "%{http_code}" -o /tmp/health_response.txt http://localhost:8000/health 2>/dev/null)
if [ "$HEALTH_CHECK" = "200" ]; then
    echo -e "${GREEN}✅ 后端API响应正常${NC}"
    RESPONSE=$(cat /tmp/health_response.txt)
    echo "   响应: $RESPONSE"
    rm -f /tmp/health_response.txt
else
    echo -e "${RED}❌ 后端API无响应${NC}"
    echo "   HTTP状态码: $HEALTH_CHECK"
fi
echo ""

# 检查模型文件
echo "7️⃣  检查模型文件目录"
if [ -d "backend/models" ]; then
    MODEL_COUNT=$(find backend/models -name "*.pt" -o -name "*.pth" | wc -l)
    if [ $MODEL_COUNT -gt 0 ]; then
        echo -e "${GREEN}✅ 找到 $MODEL_COUNT 个模型文件${NC}"
        echo "   模型列表:"
        find backend/models -name "*.pt" -o -name "*.pth" | while read model; do
            SIZE=$(du -h "$model" | awk '{print $1}')
            echo "   - $(basename $model) ($SIZE)"
        done
    else
        echo -e "${YELLOW}⚠️  未找到模型文件（.pt或.pth）${NC}"
        echo "   请通过管理后台上传YOLO模型"
    fi
else
    echo -e "${YELLOW}⚠️  models目录不存在${NC}"
    echo "   将在首次上传模型时自动创建"
fi
echo ""

# 检查上传目录
echo "8️⃣  检查上传目录"
if [ -d "backend/uploads" ]; then
    UPLOAD_SIZE=$(du -sh backend/uploads 2>/dev/null | awk '{print $1}')
    echo -e "${GREEN}✅ uploads目录存在${NC}"
    echo "   目录大小: $UPLOAD_SIZE"
else
    echo -e "${YELLOW}⚠️  uploads目录不存在${NC}"
    echo "   将在首次上传时自动创建"
fi
echo ""

# 检查结果目录
echo "9️⃣  检查结果目录"
if [ -d "backend/results" ]; then
    RESULT_SIZE=$(du -sh backend/results 2>/dev/null | awk '{print $1}')
    echo -e "${GREEN}✅ results目录存在${NC}"
    echo "   目录大小: $RESULT_SIZE"
else
    echo -e "${YELLOW}⚠️  results目录不存在${NC}"
    echo "   将在首次检测时自动创建"
fi
echo ""

# 总结
echo "========================================"
echo "           总结"
echo "========================================"

ISSUES=0

# 统计问题
if ! lsof -i :8000 > /dev/null 2>&1; then
    ISSUES=$((ISSUES + 1))
fi

if ! lsof -i :5173 > /dev/null 2>&1; then
    ISSUES=$((ISSUES + 1))
fi

if ! redis-cli ping > /dev/null 2>&1; then
    ISSUES=$((ISSUES + 1))
fi

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ 所有核心服务运行正常！${NC}"
    echo ""
    echo "🎉 系统可以正常使用"
    echo ""
    echo "📝 访问地址:"
    echo "   - 前端: http://localhost:5173"
    echo "   - API文档: http://localhost:8000/docs"
    echo ""
    echo "👤 测试账号:"
    echo "   - 普通用户: user / user123"
    echo "   - 管理员: admin / admin123"
else
    echo -e "${RED}⚠️  发现 $ISSUES 个问题需要解决${NC}"
    echo ""
    echo "📚 参考文档:"
    echo "   - 环境配置: ./ENVIRONMENT_SETUP.md"
    echo "   - 调试指南: ./DEBUGGING_GUIDE.md"
    echo "   - 快速启动: ./start.sh"
fi

echo ""
echo "========================================"
