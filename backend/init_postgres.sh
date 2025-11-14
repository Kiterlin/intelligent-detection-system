#!/bin/bash

# =============================================================================
# PostgreSQL 数据库初始化脚本
# 水下目标智能检测平台
# =============================================================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_header() {
    echo -e "${BLUE}============================================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}============================================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# =============================================================================
# 配置变量
# =============================================================================

DB_NAME="water_detection"
DB_USER="water_detection_user"
DB_PASSWORD="change_me_in_production"
DB_HOST="localhost"
DB_PORT="5432"

# =============================================================================
# 检查PostgreSQL是否安装
# =============================================================================

print_header "检查PostgreSQL环境"

if ! command -v psql &> /dev/null; then
    print_error "PostgreSQL未安装或不在PATH中"
    echo ""
    print_info "安装方法："
    echo "  Ubuntu/Debian: sudo apt-get install postgresql postgresql-contrib"
    echo "  CentOS/RHEL:   sudo yum install postgresql-server postgresql-contrib"
    echo "  macOS:         brew install postgresql"
    exit 1
fi

print_success "PostgreSQL已安装"
psql --version

# =============================================================================
# 检查PostgreSQL服务状态
# =============================================================================

print_info "检查PostgreSQL服务状态..."

if command -v systemctl &> /dev/null; then
    if systemctl is-active --quiet postgresql; then
        print_success "PostgreSQL服务正在运行"
    else
        print_warning "PostgreSQL服务未运行"
        echo -n "是否启动PostgreSQL服务？ (y/n): "
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            sudo systemctl start postgresql
            print_success "PostgreSQL服务已启动"
        else
            print_error "需要启动PostgreSQL服务才能继续"
            exit 1
        fi
    fi
fi

# =============================================================================
# 获取用户输入
# =============================================================================

print_header "配置数据库参数"

echo -n "数据库名称 [${DB_NAME}]: "
read -r input_db_name
DB_NAME="${input_db_name:-$DB_NAME}"

echo -n "数据库用户名 [${DB_USER}]: "
read -r input_db_user
DB_USER="${input_db_user:-$DB_USER}"

echo -n "数据库密码 [${DB_PASSWORD}]: "
read -r -s input_db_password
echo ""
DB_PASSWORD="${input_db_password:-$DB_PASSWORD}"

echo -n "数据库主机 [${DB_HOST}]: "
read -r input_db_host
DB_HOST="${input_db_host:-$DB_HOST}"

echo -n "数据库端口 [${DB_PORT}]: "
read -r input_db_port
DB_PORT="${input_db_port:-$DB_PORT}"

# =============================================================================
# 显示配置并确认
# =============================================================================

echo ""
print_header "确认配置"
echo "数据库名称: $DB_NAME"
echo "用户名:     $DB_USER"
echo "密码:       ****"
echo "主机:       $DB_HOST"
echo "端口:       $DB_PORT"
echo ""

print_warning "此操作将创建新数据库和用户"
echo -n "是否继续？ (yes/no): "
read -r confirm

if [[ "$confirm" != "yes" ]]; then
    print_error "用户取消操作"
    exit 1
fi

# =============================================================================
# 创建数据库和用户
# =============================================================================

print_header "创建数据库和用户"

# 使用postgres超级用户创建数据库
print_info "创建数据库 ${DB_NAME}..."
sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME} ENCODING 'UTF8';" 2>/dev/null || print_warning "数据库可能已存在"

# 创建用户
print_info "创建用户 ${DB_USER}..."
sudo -u postgres psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}';" 2>/dev/null || print_warning "用户可能已存在"

# 授予权限
print_info "授予权限..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};"

# 连接到数据库并安装扩展
print_info "安装PostgreSQL扩展..."
sudo -u postgres psql -d ${DB_NAME} -c "CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";"
sudo -u postgres psql -d ${DB_NAME} -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"

# 授予schema权限
print_info "配置schema权限..."
sudo -u postgres psql -d ${DB_NAME} -c "GRANT USAGE ON SCHEMA public TO ${DB_USER};"
sudo -u postgres psql -d ${DB_NAME} -c "GRANT CREATE ON SCHEMA public TO ${DB_USER};"
sudo -u postgres psql -d ${DB_NAME} -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ${DB_USER};"
sudo -u postgres psql -d ${DB_NAME} -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO ${DB_USER};"

print_success "数据库和用户创建完成"

# =============================================================================
# 测试连接
# =============================================================================

print_header "测试数据库连接"

export PGPASSWORD="${DB_PASSWORD}"
if psql -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER} -d ${DB_NAME} -c "SELECT version();" > /dev/null 2>&1; then
    print_success "数据库连接测试成功"
else
    print_error "数据库连接测试失败"
    exit 1
fi

# =============================================================================
# 生成连接URL
# =============================================================================

print_header "数据库连接信息"

DATABASE_URL="postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}"

echo ""
echo "PostgreSQL连接URL（用于.env文件）："
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "${DATABASE_URL}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# =============================================================================
# 下一步提示
# =============================================================================

print_header "完成！下一步操作"

echo ""
print_info "1. 更新.env文件"
echo "   将DATABASE_URL设置为："
echo "   DATABASE_URL=\"${DATABASE_URL}\""
echo ""

print_info "2. 运行数据库迁移"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   alembic upgrade head"
echo ""

print_info "3. 迁移SQLite数据（如果有）"
echo "   python migrate_to_postgres.py"
echo ""

print_info "4. 启动应用"
echo "   uvicorn app.main:app --reload --port 8000"
echo ""

print_success "PostgreSQL初始化完成！"

# =============================================================================
# 保存配置到文件（可选）
# =============================================================================

if [ ! -f .env ]; then
    echo -n "是否创建.env文件？ (y/n): "
    read -r create_env
    if [[ "$create_env" =~ ^[Yy]$ ]]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            # 使用sed替换DATABASE_URL
            if [[ "$OSTYPE" == "darwin"* ]]; then
                # macOS
                sed -i '' "s|^DATABASE_URL=.*|DATABASE_URL=\"${DATABASE_URL}\"|" .env
            else
                # Linux
                sed -i "s|^DATABASE_URL=.*|DATABASE_URL=\"${DATABASE_URL}\"|" .env
            fi
            print_success ".env文件已创建并配置"
        else
            print_warning ".env.example文件不存在，请手动创建.env文件"
        fi
    fi
fi

echo ""
print_success "全部完成！"
