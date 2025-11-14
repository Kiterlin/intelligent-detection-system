#!/bin/bash
# 环境验证脚本 - 检查所有组件是否正常

echo "🔍 检查项目环境配置..."
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查函数
check_item() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
        return 0
    else
        echo -e "${RED}❌ $2${NC}"
        return 1
    fi
}

TOTAL=0
PASSED=0

# 1. 检查Conda环境
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "1. Conda 环境"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -n "$CONDA_DEFAULT_ENV" ]; then
    check_item 0 "Conda环境已激活: $CONDA_DEFAULT_ENV"
    ((PASSED++))
else
    check_item 1 "Conda环境未激活"
fi
((TOTAL++))
echo ""

# 2. 检查Python
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "2. Python 环境"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    check_item 0 "Python版本: $PYTHON_VERSION"
    ((PASSED++))
else
    check_item 1 "Python未找到"
fi
((TOTAL++))
echo ""

# 3. 检查关键Python包
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "3. Python 依赖包"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
PACKAGES=("fastapi" "uvicorn" "sqlalchemy" "asyncpg" "redis" "torch" "celery")
for pkg in "${PACKAGES[@]}"; do
    if python -c "import $pkg" 2>/dev/null; then
        VERSION=$(python -c "import $pkg; print($pkg.__version__)" 2>/dev/null || echo "未知")
        check_item 0 "$pkg ($VERSION)"
        ((PASSED++))
    else
        check_item 1 "$pkg 未安装"
    fi
    ((TOTAL++))
done
echo ""

# 4. 检查PostgreSQL
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "4. PostgreSQL 数据库"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if command -v psql &> /dev/null; then
    PG_VERSION=$(psql --version | awk '{print $3}')
    check_item 0 "PostgreSQL版本: $PG_VERSION"
    ((PASSED++))
else
    check_item 1 "PostgreSQL未安装"
fi
((TOTAL++))

if pg_isready -h localhost -p 5432 &> /dev/null; then
    check_item 0 "PostgreSQL服务运行中"
    ((PASSED++))
else
    check_item 1 "PostgreSQL服务未运行"
fi
((TOTAL++))

# 检查数据库连接
if PGPASSWORD='water_detection_2024' psql -h localhost -U water_detection_user -d water_detection -c "SELECT 1" &> /dev/null; then
    check_item 0 "数据库连接正常"
    ((PASSED++))
else
    check_item 1 "数据库连接失败"
fi
((TOTAL++))
echo ""

# 5. 检查Redis
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "5. Redis 缓存"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if command -v redis-cli &> /dev/null; then
    REDIS_VERSION=$(redis-cli --version | awk '{print $2}')
    check_item 0 "Redis版本: $REDIS_VERSION"
    ((PASSED++))
else
    check_item 1 "Redis未安装"
fi
((TOTAL++))

if redis-cli ping &> /dev/null; then
    check_item 0 "Redis服务运行中"
    ((PASSED++))
else
    check_item 1 "Redis服务未运行"
fi
((TOTAL++))
echo ""

# 6. 检查配置文件
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "6. 配置文件"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ -f "backend/.env" ]; then
    check_item 0 ".env文件存在"
    ((PASSED++))

    if grep -q "postgresql+asyncpg" backend/.env; then
        check_item 0 "PostgreSQL配置正确"
        ((PASSED++))
    else
        check_item 1 "PostgreSQL配置缺失"
    fi
    ((TOTAL++))
else
    check_item 1 ".env文件不存在"
fi
((TOTAL++))
echo ""

# 7. 检查数据库表
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "7. 数据库表结构"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
TABLES=("users" "ml_models" "detection_history" "alembic_version")
for table in "${TABLES[@]}"; do
    if PGPASSWORD='water_detection_2024' psql -h localhost -U water_detection_user -d water_detection -c "SELECT 1 FROM $table LIMIT 1" &> /dev/null; then
        check_item 0 "表 $table 存在"
        ((PASSED++))
    else
        check_item 1 "表 $table 不存在"
    fi
    ((TOTAL++))
done
echo ""

# 8. 应用加载测试
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "8. 应用加载测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cd backend 2>/dev/null || true
if python -c "from app.main import app; print('OK')" 2>/dev/null | grep -q "OK"; then
    check_item 0 "应用模块加载成功"
    ((PASSED++))
else
    check_item 1 "应用模块加载失败"
fi
((TOTAL++))
cd ..
echo ""

# 总结
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "检查结果总结"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
PERCENTAGE=$((PASSED * 100 / TOTAL))
echo -e "总计: $PASSED/$TOTAL 通过 (${PERCENTAGE}%)"

if [ $PASSED -eq $TOTAL ]; then
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}✅ 所有检查通过！环境配置完美！${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "🚀 可以使用以下命令启动项目："
    echo "   ./start.sh"
    exit 0
elif [ $PERCENTAGE -ge 80 ]; then
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}⚠️  大部分检查通过，但有些问题${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "请检查上述失败项并修复"
    exit 1
else
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}❌ 环境配置存在较多问题${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo "📚 请参考文档重新配置："
    echo "   - ENVIRONMENT_SETUP.md"
    echo "   - QUICKSTART_CONDA.md"
    exit 1
fi
