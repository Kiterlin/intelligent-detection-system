"""
Alembic 迁移环境配置
支持异步数据库引擎
"""
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# 导入配置
from app.core.config import settings
from app.core.database import Base

# 导入所有模型（确保在创建迁移时能识别到）
from app.models.user import User  # noqa

# Alembic Config 对象
config = context.config

# 从 .env 文件读取数据库 URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# 解释配置文件的日志设置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 添加模型的 MetaData 对象（用于自动生成迁移）
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    在 'offline' 模式下运行迁移
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """
    执行迁移的辅助函数
    """
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    异步运行迁移
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    在 'online' 模式下运行迁移
    支持异步数据库引擎
    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
