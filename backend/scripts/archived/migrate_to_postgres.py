#!/usr/bin/env python3
"""
数据库迁移工具：SQLite -> PostgreSQL
将现有的SQLite数据库迁移到PostgreSQL
"""
import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from sqlalchemy import create_engine, text, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.models.user import User, UserRole
from app.models.ml_model import MLModel, ModelStatus
from app.models.detection_history import DetectionHistory, DetectionInputType, DetectionStatus
from app.core.database import Base


class DatabaseMigrator:
    """数据库迁移器"""

    def __init__(self, sqlite_url: str, postgres_url: str):
        """
        初始化迁移器

        Args:
            sqlite_url: SQLite数据库URL (例如: sqlite:///./water_detection.db)
            postgres_url: PostgreSQL数据库URL (例如: postgresql+asyncpg://user:password@localhost/dbname)
        """
        # 移除异步前缀以创建同步引擎（用于SQLite）
        self.sqlite_url = sqlite_url.replace("sqlite+aiosqlite", "sqlite")
        self.postgres_url = postgres_url

        # 创建同步SQLite引擎
        self.sqlite_engine = create_engine(self.sqlite_url, echo=False)

        # 创建异步PostgreSQL引擎
        self.postgres_engine = create_async_engine(
            self.postgres_url,
            echo=False,
            pool_pre_ping=True,
        )

        # 创建会话工厂
        self.async_session = sessionmaker(
            self.postgres_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        # 数据统计
        self.stats = {
            "users": {"total": 0, "migrated": 0, "failed": 0},
            "ml_models": {"total": 0, "migrated": 0, "failed": 0},
            "detection_history": {"total": 0, "migrated": 0, "failed": 0},
        }

    async def create_tables(self):
        """在PostgreSQL中创建所有表"""
        print("📋 创建PostgreSQL表结构...")
        async with self.postgres_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ 表结构创建完成")

    def read_sqlite_users(self) -> List[Dict[str, Any]]:
        """从SQLite读取用户数据"""
        print("\n📖 读取SQLite用户数据...")
        with self.sqlite_engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM users ORDER BY id"))
            columns = result.keys()
            users = [dict(zip(columns, row)) for row in result]
            self.stats["users"]["total"] = len(users)
            print(f"   找到 {len(users)} 条用户记录")
            return users

    def read_sqlite_models(self) -> List[Dict[str, Any]]:
        """从SQLite读取模型数据"""
        print("\n📖 读取SQLite模型数据...")
        with self.sqlite_engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM ml_models ORDER BY id"))
            columns = result.keys()
            models = [dict(zip(columns, row)) for row in result]
            self.stats["ml_models"]["total"] = len(models)
            print(f"   找到 {len(models)} 条模型记录")
            return models

    def read_sqlite_detections(self) -> List[Dict[str, Any]]:
        """从SQLite读取检测历史数据"""
        print("\n📖 读取SQLite检测历史数据...")
        with self.sqlite_engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM detection_history ORDER BY id"))
            columns = result.keys()
            detections = [dict(zip(columns, row)) for row in result]
            self.stats["detection_history"]["total"] = len(detections)
            print(f"   找到 {len(detections)} 条检测记录")
            return detections

    async def migrate_users(self, users: List[Dict[str, Any]]) -> bool:
        """
        迁移用户数据

        Args:
            users: 用户数据列表

        Returns:
            是否成功
        """
        print("\n🚀 开始迁移用户数据...")
        async with self.async_session() as session:
            try:
                for user_data in users:
                    try:
                        # 转换时间戳（如果是字符串）
                        created_at = user_data["created_at"]
                        if isinstance(created_at, str):
                            created_at = datetime.fromisoformat(created_at.replace(' ', 'T'))

                        updated_at = user_data["updated_at"]
                        if isinstance(updated_at, str):
                            updated_at = datetime.fromisoformat(updated_at.replace(' ', 'T'))

                        # 转换角色（处理大小写）
                        role_str = str(user_data["role"]).lower()

                        user = User(
                            id=user_data["id"],
                            username=user_data["username"],
                            email=user_data["email"],
                            hashed_password=user_data["hashed_password"],
                            role=UserRole(role_str),
                            is_active=bool(user_data["is_active"]),
                            created_at=created_at,
                            updated_at=updated_at,
                        )
                        session.add(user)
                        self.stats["users"]["migrated"] += 1
                    except Exception as e:
                        print(f"   ⚠️  用户 {user_data.get('username')} 迁移失败: {str(e)}")
                        self.stats["users"]["failed"] += 1
                        continue

                await session.commit()

                # 重置序列（确保下一个ID正确）
                if users:
                    max_id = max(u["id"] for u in users)
                    await session.execute(
                        text(f"SELECT setval('users_id_seq', {max_id}, true)")
                    )
                    await session.commit()

                print(f"✅ 用户迁移完成: {self.stats['users']['migrated']}/{self.stats['users']['total']}")
                return True
            except Exception as e:
                print(f"❌ 用户迁移失败: {str(e)}")
                await session.rollback()
                return False

    async def migrate_models(self, models: List[Dict[str, Any]]) -> bool:
        """
        迁移模型数据

        Args:
            models: 模型数据列表

        Returns:
            是否成功
        """
        print("\n🚀 开始迁移模型数据...")
        async with self.async_session() as session:
            try:
                for model_data in models:
                    try:
                        # 转换时间戳（如果是字符串）
                        created_at = model_data["created_at"]
                        if isinstance(created_at, str):
                            created_at = datetime.fromisoformat(created_at.replace(' ', 'T'))

                        updated_at = model_data["updated_at"]
                        if isinstance(updated_at, str):
                            updated_at = datetime.fromisoformat(updated_at.replace(' ', 'T'))

                        # 转换状态（处理大小写）
                        status_str = str(model_data["status"]).lower()

                        model = MLModel(
                            id=model_data["id"],
                            name=model_data["name"],
                            filename=model_data["filename"],
                            file_path=model_data["file_path"],
                            version=model_data.get("version"),
                            status=ModelStatus(status_str),
                            description=model_data.get("description"),
                            file_size=model_data.get("file_size"),
                            uploaded_by=model_data["uploaded_by"],
                            created_at=created_at,
                            updated_at=updated_at,
                        )
                        session.add(model)
                        self.stats["ml_models"]["migrated"] += 1
                    except Exception as e:
                        print(f"   ⚠️  模型 {model_data.get('name')} 迁移失败: {str(e)}")
                        self.stats["ml_models"]["failed"] += 1
                        continue

                await session.commit()

                # 重置序列
                if models:
                    max_id = max(m["id"] for m in models)
                    await session.execute(
                        text(f"SELECT setval('ml_models_id_seq', {max_id}, true)")
                    )
                    await session.commit()

                print(f"✅ 模型迁移完成: {self.stats['ml_models']['migrated']}/{self.stats['ml_models']['total']}")
                return True
            except Exception as e:
                print(f"❌ 模型迁移失败: {str(e)}")
                await session.rollback()
                return False

    async def migrate_detections(self, detections: List[Dict[str, Any]]) -> bool:
        """
        迁移检测历史数据

        Args:
            detections: 检测历史数据列表

        Returns:
            是否成功
        """
        print("\n🚀 开始迁移检测历史数据...")
        async with self.async_session() as session:
            try:
                for det_data in detections:
                    try:
                        # 转换时间戳（如果是字符串）
                        created_at = det_data["created_at"]
                        if isinstance(created_at, str):
                            created_at = datetime.fromisoformat(created_at.replace(' ', 'T'))

                        updated_at = det_data["updated_at"]
                        if isinstance(updated_at, str):
                            updated_at = datetime.fromisoformat(updated_at.replace(' ', 'T'))

                        # 转换枚举值（处理大小写）
                        input_type_str = str(det_data["input_type"]).lower()
                        status_str = str(det_data["status"]).lower()

                        detection = DetectionHistory(
                            id=det_data["id"],
                            user_id=det_data["user_id"],
                            model_id=det_data["model_id"],
                            input_type=DetectionInputType(input_type_str),
                            input_file_path=det_data["input_file_path"],
                            output_file_path=det_data.get("output_file_path"),
                            result_json=det_data.get("result_json"),
                            detected_objects_count=det_data.get("detected_objects_count", 0),
                            status=DetectionStatus(status_str),
                            task_id=det_data.get("task_id"),
                            processing_time=det_data.get("processing_time"),
                            confidence_threshold=det_data.get("confidence_threshold"),
                            iou_threshold=det_data.get("iou_threshold"),
                            error_message=det_data.get("error_message"),
                            created_at=created_at,
                            updated_at=updated_at,
                        )
                        session.add(detection)
                        self.stats["detection_history"]["migrated"] += 1
                    except Exception as e:
                        print(f"   ⚠️  检测记录 {det_data.get('id')} 迁移失败: {str(e)}")
                        self.stats["detection_history"]["failed"] += 1
                        continue

                await session.commit()

                # 重置序列
                if detections:
                    max_id = max(d["id"] for d in detections)
                    await session.execute(
                        text(f"SELECT setval('detection_history_id_seq', {max_id}, true)")
                    )
                    await session.commit()

                print(f"✅ 检测历史迁移完成: {self.stats['detection_history']['migrated']}/{self.stats['detection_history']['total']}")
                return True
            except Exception as e:
                print(f"❌ 检测历史迁移失败: {str(e)}")
                await session.rollback()
                return False

    async def verify_data(self) -> bool:
        """验证迁移后的数据完整性"""
        print("\n🔍 验证数据完整性...")
        async with self.async_session() as session:
            try:
                # 验证用户数量
                result = await session.execute(select(User))
                users = result.scalars().all()
                print(f"   用户表: {len(users)} 条记录")

                # 验证模型数量
                result = await session.execute(select(MLModel))
                models = result.scalars().all()
                print(f"   模型表: {len(models)} 条记录")

                # 验证检测历史数量
                result = await session.execute(select(DetectionHistory))
                detections = result.scalars().all()
                print(f"   检测历史表: {len(detections)} 条记录")

                # 检查是否匹配
                success = (
                    len(users) == self.stats["users"]["migrated"]
                    and len(models) == self.stats["ml_models"]["migrated"]
                    and len(detections) == self.stats["detection_history"]["migrated"]
                )

                if success:
                    print("✅ 数据验证通过")
                else:
                    print("⚠️  数据数量不匹配，请检查")

                return success
            except Exception as e:
                print(f"❌ 数据验证失败: {str(e)}")
                return False

    def print_summary(self):
        """打印迁移摘要"""
        print("\n" + "=" * 60)
        print("📊 迁移摘要")
        print("=" * 60)
        for table, stats in self.stats.items():
            print(f"\n{table}:")
            print(f"  总数: {stats['total']}")
            print(f"  成功: {stats['migrated']}")
            print(f"  失败: {stats['failed']}")
            if stats['total'] > 0:
                success_rate = (stats['migrated'] / stats['total']) * 100
                print(f"  成功率: {success_rate:.1f}%")
        print("\n" + "=" * 60)

    async def run_migration(self) -> bool:
        """
        执行完整的迁移流程

        Returns:
            是否成功
        """
        print("🚀 开始数据库迁移")
        print(f"   源数据库: {self.sqlite_url}")
        print(f"   目标数据库: {self.postgres_url}")
        print("=" * 60)

        try:
            # 1. 创建表结构
            await self.create_tables()

            # 2. 读取SQLite数据
            users = self.read_sqlite_users()
            models = self.read_sqlite_models()
            detections = self.read_sqlite_detections()

            # 3. 按顺序迁移（保持外键关系）
            if not await self.migrate_users(users):
                print("❌ 用户迁移失败，停止迁移")
                return False

            if not await self.migrate_models(models):
                print("❌ 模型迁移失败，停止迁移")
                return False

            if not await self.migrate_detections(detections):
                print("❌ 检测历史迁移失败，停止迁移")
                return False

            # 4. 验证数据
            if not await self.verify_data():
                print("⚠️  数据验证失败，请手动检查")

            # 5. 打印摘要
            self.print_summary()

            print("\n✅ 迁移完成！")
            return True

        except Exception as e:
            print(f"\n❌ 迁移过程中出现错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            # 清理资源
            self.sqlite_engine.dispose()
            await self.postgres_engine.dispose()


async def main():
    """主函数"""
    print("=" * 60)
    print("  数据库迁移工具: SQLite -> PostgreSQL")
    print("=" * 60)

    # 配置数据库URL
    # SQLite数据库路径
    sqlite_url = "sqlite:///./water_detection.db"

    # PostgreSQL数据库URL（请根据实际情况修改）
    # 格式: postgresql+asyncpg://用户名:密码@主机:端口/数据库名
    postgres_url = input("\n请输入PostgreSQL数据库URL\n(例如: postgresql+asyncpg://user:password@localhost:5432/water_detection)\n> ").strip()

    if not postgres_url:
        print("❌ 未提供PostgreSQL URL，退出")
        return

    # 确认迁移
    print("\n⚠️  警告：此操作会覆盖PostgreSQL中的现有数据")
    print(f"   源数据库: {sqlite_url}")
    print(f"   目标数据库: {postgres_url}")
    confirm = input("\n是否继续？(yes/no): ").strip().lower()

    if confirm != "yes":
        print("❌ 用户取消操作")
        return

    # 执行迁移
    migrator = DatabaseMigrator(sqlite_url, postgres_url)
    success = await migrator.run_migration()

    if success:
        print("\n✅ 数据迁移成功完成！")
        print("\n📝 下一步操作：")
        print("   1. 更新 .env 文件中的 DATABASE_URL 为 PostgreSQL URL")
        print("   2. 重启应用服务")
        print("   3. 验证所有功能正常工作")
        print("   4. 备份 SQLite 文件后可以删除")
    else:
        print("\n❌ 数据迁移失败，请检查错误信息")
        print("   SQLite数据未受影响，可以安全重试")


if __name__ == "__main__":
    asyncio.run(main())
