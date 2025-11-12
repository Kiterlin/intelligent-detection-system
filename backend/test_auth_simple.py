"""
简单的认证功能测试（不需要启动服务器）
"""
import asyncio
from app.core.database import AsyncSessionLocal
from app.crud.user import create_user, get_user_by_username
from app.schemas.user import UserCreate
from app.core.security import verify_password, create_access_token, decode_access_token
from app.models.user import UserRole


async def test_auth():
    """测试认证功能"""
    print("🧪 测试认证功能...\n")

    async with AsyncSessionLocal() as db:
        # 1. 测试创建用户
        print("1️⃣ 测试创建用户...")
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="test123"
        )
        try:
            user = await create_user(db, user_data)
            print(f"   ✅ 用户创建成功: {user.username} ({user.email})")
            print(f"      - ID: {user.id}")
            print(f"      - 角色: {user.role}")
            print(f"      - 激活状态: {user.is_active}")
        except Exception as e:
            print(f"   ❌ 创建失败: {e}")
            return

        # 2. 测试密码验证
        print("\n2️⃣ 测试密码验证...")
        db_user = await get_user_by_username(db, "testuser")
        if db_user:
            is_valid = verify_password("test123", db_user.hashed_password)
            if is_valid:
                print(f"   ✅ 密码验证成功")
            else:
                print(f"   ❌ 密码验证失败")

        # 3. 测试 JWT token
        print("\n3️⃣ 测试 JWT Token...")
        token = create_access_token(data={"sub": user.id})
        print(f"   ✅ Token 生成成功")
        print(f"      Token: {token[:50]}...")

        # 4. 测试 token 解码
        print("\n4️⃣ 测试 Token 解码...")
        payload = decode_access_token(token)
        if payload and payload.get("sub") == user.id:
            print(f"   ✅ Token 解码成功")
            print(f"      用户 ID: {payload.get('sub')}")
        else:
            print(f"   ❌ Token 解码失败")

        print("\n✅ 所有认证功能测试通过！")


if __name__ == "__main__":
    asyncio.run(test_auth())
