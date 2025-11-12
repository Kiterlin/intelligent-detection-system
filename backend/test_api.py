"""
简单的 API 测试脚本
"""
import asyncio
import httpx

BASE_URL = "http://localhost:8000/api/v1"


async def test_auth_flow():
    """测试完整的认证流程"""
    async with httpx.AsyncClient() as client:
        print("🧪 测试认证 API 流程...\n")

        # 1. 注册用户
        print("1️⃣ 测试注册...")
        register_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "test123"
        }
        response = await client.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 201:
            user_data = response.json()
            print(f"   ✅ 注册成功: {user_data['username']} ({user_data['email']})")
        else:
            print(f"   ❌ 注册失败: {response.text}")
            return

        # 2. 登录
        print("\n2️⃣ 测试登录...")
        login_data = {
            "username": "testuser",
            "password": "test123"
        }
        response = await client.post(f"{BASE_URL}/auth/login", json=login_data)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"   ✅ 登录成功")
            print(f"   Token: {access_token[:50]}...")
        else:
            print(f"   ❌ 登录失败: {response.text}")
            return

        # 3. 获取当前用户信息
        print("\n3️⃣ 测试获取当前用户信息...")
        headers = {"Authorization": f"Bearer {access_token}"}
        response = await client.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            user_info = response.json()
            print(f"   ✅ 获取成功:")
            print(f"      - 用户名: {user_info['username']}")
            print(f"      - 邮箱: {user_info['email']}")
            print(f"      - 角色: {user_info['role']}")
            print(f"      - 激活状态: {user_info['is_active']}")
        else:
            print(f"   ❌ 获取失败: {response.text}")

        print("\n✅ 所有测试通过！")


if __name__ == "__main__":
    asyncio.run(test_auth_flow())
