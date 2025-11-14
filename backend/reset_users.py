"""
重置用户数据库脚本
清理所有用户并创建两个测试账号
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, delete

from app.models.user import User, UserRole
from app.core.security import get_password_hash
from app.core.config import settings


async def reset_users():
    """重置用户数据"""
    # 创建数据库引擎
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        print("🗑️  清理现有用户数据...")

        # 删除所有用户
        await session.execute(delete(User))
        await session.commit()
        print("✅ 用户数据已清空")

        print("\n👤 创建测试账号...")

        # 创建普通用户
        user = User(
            username="user",
            email="user@example.com",
            hashed_password=get_password_hash("user123"),
            role=UserRole.USER,
            is_active=True
        )
        session.add(user)

        # 创建管理员
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        session.add(admin)

        await session.commit()
        await session.refresh(user)
        await session.refresh(admin)

        print("\n✅ 用户创建成功！\n")
        print("=" * 60)
        print("📋 测试账号信息")
        print("=" * 60)
        print("\n👤 普通用户账号:")
        print(f"   用户名: {user.username}")
        print(f"   密码:   user123")
        print(f"   邮箱:   {user.email}")
        print(f"   角色:   {user.role.value}")
        print(f"   ID:     {user.id}")

        print("\n👨‍💼 管理员账号:")
        print(f"   用户名: {admin.username}")
        print(f"   密码:   admin123")
        print(f"   邮箱:   {admin.email}")
        print(f"   角色:   {admin.role.value}")
        print(f"   ID:     {admin.id}")
        print("\n" + "=" * 60)
        print("✅ 可以使用这些账号登录系统测试所有功能！")
        print("=" * 60 + "\n")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(reset_users())
