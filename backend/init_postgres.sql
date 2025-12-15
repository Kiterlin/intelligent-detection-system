-- =============================================================================
-- PostgreSQL 数据库初始化脚本
-- 智能目标检测系统
-- =============================================================================

-- 创建数据库（如果不存在）
-- 注意：这条语句需要在psql命令行或通过superuser执行，不能在事务中执行
-- CREATE DATABASE water_detection ENCODING 'UTF8' LC_COLLATE 'zh_CN.UTF-8' LC_CTYPE 'zh_CN.UTF-8';

-- 连接到数据库
\c water_detection

-- =============================================================================
-- 安装扩展
-- =============================================================================

-- UUID生成扩展（如果将来需要UUID主键）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- pg_trgm扩展（支持模糊搜索）
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- =============================================================================
-- 创建应用用户（如果不存在）
-- =============================================================================
-- 注意：请修改密码为强密码

DO
$$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'water_detection_user') THEN

      CREATE USER water_detection_user WITH PASSWORD 'change_me_in_production';
   END IF;
END
$$;

-- =============================================================================
-- 授权
-- =============================================================================

-- 授予数据库连接权限
GRANT CONNECT ON DATABASE water_detection TO water_detection_user;

-- 授予schema使用权限
GRANT USAGE ON SCHEMA public TO water_detection_user;

-- 授予所有表的权限
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO water_detection_user;

-- 授予序列权限（用于自增ID）
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO water_detection_user;

-- 授予未来创建的表的默认权限
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO water_detection_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT USAGE, SELECT ON SEQUENCES TO water_detection_user;

-- =============================================================================
-- 数据库配置优化
-- =============================================================================

-- 设置默认编码
ALTER DATABASE water_detection SET client_encoding TO 'utf8';

-- 设置时区（根据实际情况调整）
ALTER DATABASE water_detection SET timezone TO 'UTC';

-- =============================================================================
-- 性能优化配置（可选，根据服务器配置调整）
-- =============================================================================

-- 增加共享缓冲区（建议设置为系统内存的25%）
-- ALTER SYSTEM SET shared_buffers = '256MB';

-- 增加工作内存
-- ALTER SYSTEM SET work_mem = '16MB';

-- 增加维护工作内存
-- ALTER SYSTEM SET maintenance_work_mem = '128MB';

-- 设置有效缓存大小（建议设置为系统内存的50-75%）
-- ALTER SYSTEM SET effective_cache_size = '1GB';

-- 启用查询计划缓存
-- ALTER SYSTEM SET plan_cache_mode = 'auto';

-- =============================================================================
-- 完成
-- =============================================================================

\echo '✅ PostgreSQL数据库初始化完成！'
\echo ''
\echo '📝 下一步操作：'
\echo '   1. 修改用户密码：ALTER USER water_detection_user WITH PASSWORD ''your_strong_password'';'
\echo '   2. 更新.env文件中的DATABASE_URL'
\echo '   3. 运行Alembic迁移：alembic upgrade head'
\echo '   4. 运行数据迁移脚本：python migrate_to_postgres.py'
\echo ''
