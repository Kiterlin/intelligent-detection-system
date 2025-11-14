"""
Redis 缓存管理器
提供统一的缓存接口和 TTL 管理
"""
import json
from typing import Optional, Any
from datetime import timedelta
import redis.asyncio as redis
from loguru import logger

from app.core.config import settings


class CacheManager:
    """
    Redis 缓存管理器

    提供键值缓存、TTL 管理、缓存失效等功能
    """

    def __init__(self):
        """初始化 Redis 连接"""
        self.redis: Optional[redis.Redis] = None
        self._enabled = True

    async def connect(self):
        """建立 Redis 连接"""
        try:
            self.redis = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                max_connections=50,
            )
            # 测试连接
            await self.redis.ping()
            logger.info("Redis 缓存连接成功")
        except Exception as e:
            logger.error(f"Redis 连接失败: {str(e)}")
            self._enabled = False
            self.redis = None

    async def disconnect(self):
        """关闭 Redis 连接"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis 缓存已断开")

    def is_enabled(self) -> bool:
        """检查缓存是否可用"""
        return self._enabled and self.redis is not None

    async def get(self, key: str) -> Optional[Any]:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，不存在或解析失败返回 None
        """
        if not self.is_enabled():
            return None

        try:
            value = await self.redis.get(key)
            if value is None:
                return None

            # 尝试解析 JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"获取缓存失败 key={key}: {str(e)}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
            ttl: 过期时间（秒），None 表示永不过期

        Returns:
            是否设置成功
        """
        if not self.is_enabled():
            return False

        try:
            # 序列化值
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            elif not isinstance(value, str):
                value = str(value)

            # 设置缓存
            if ttl:
                await self.redis.setex(key, ttl, value)
            else:
                await self.redis.set(key, value)

            return True
        except Exception as e:
            logger.error(f"设置缓存失败 key={key}: {str(e)}")
            return False

    async def delete(self, *keys: str) -> bool:
        """
        删除缓存

        Args:
            keys: 要删除的缓存键（支持多个）

        Returns:
            是否删除成功
        """
        if not self.is_enabled() or not keys:
            return False

        try:
            await self.redis.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"删除缓存失败 keys={keys}: {str(e)}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """
        根据模式删除缓存

        Args:
            pattern: 键模式（支持通配符 *）

        Returns:
            删除的键数量
        """
        if not self.is_enabled():
            return 0

        try:
            keys = []
            async for key in self.redis.scan_iter(match=pattern):
                keys.append(key)

            if keys:
                await self.redis.delete(*keys)
                logger.info(f"删除缓存模式 {pattern}，共 {len(keys)} 个键")
                return len(keys)
            return 0
        except Exception as e:
            logger.error(f"删除缓存模式失败 pattern={pattern}: {str(e)}")
            return 0

    async def exists(self, key: str) -> bool:
        """
        检查缓存是否存在

        Args:
            key: 缓存键

        Returns:
            是否存在
        """
        if not self.is_enabled():
            return False

        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error(f"检查缓存存在性失败 key={key}: {str(e)}")
            return False

    async def ttl(self, key: str) -> int:
        """
        获取缓存剩余过期时间

        Args:
            key: 缓存键

        Returns:
            剩余秒数，-1 表示永不过期，-2 表示不存在
        """
        if not self.is_enabled():
            return -2

        try:
            return await self.redis.ttl(key)
        except Exception as e:
            logger.error(f"获取缓存TTL失败 key={key}: {str(e)}")
            return -2


# 全局缓存管理器实例
cache_manager = CacheManager()


# 缓存键生成器
class CacheKeys:
    """缓存键常量和生成器"""

    # TTL 配置（秒）
    TTL_MODEL_LIST = 300  # 5分钟
    TTL_USER_INFO = 900  # 15分钟
    TTL_STATS = 120  # 2分钟
    TTL_DETECTION_HISTORY = 60  # 1分钟

    # 键前缀
    PREFIX = "water_detection"

    @classmethod
    def model_list(cls, status: Optional[str] = None) -> str:
        """模型列表缓存键"""
        if status:
            return f"{cls.PREFIX}:models:list:{status}"
        return f"{cls.PREFIX}:models:list:all"

    @classmethod
    def model_detail(cls, model_id: int) -> str:
        """模型详情缓存键"""
        return f"{cls.PREFIX}:models:detail:{model_id}"

    @classmethod
    def user_info(cls, user_id: int) -> str:
        """用户信息缓存键"""
        return f"{cls.PREFIX}:users:info:{user_id}"

    @classmethod
    def admin_stats(cls) -> str:
        """管理后台统计数据缓存键"""
        return f"{cls.PREFIX}:admin:stats"

    @classmethod
    def detection_history(cls, user_id: int, page: int, filters: str = "") -> str:
        """检测历史列表缓存键"""
        return f"{cls.PREFIX}:detections:history:{user_id}:page{page}:{filters}"

    @classmethod
    def user_stats(cls, user_id: int) -> str:
        """用户统计数据缓存键"""
        return f"{cls.PREFIX}:users:stats:{user_id}"


# 缓存失效辅助函数
async def invalidate_model_cache():
    """使模型相关缓存失效"""
    await cache_manager.delete_pattern(f"{CacheKeys.PREFIX}:models:*")
    logger.info("模型缓存已失效")


async def invalidate_user_cache(user_id: int):
    """使特定用户缓存失效"""
    await cache_manager.delete(
        CacheKeys.user_info(user_id),
        CacheKeys.user_stats(user_id),
        CacheKeys.user_stats(user_id) + ":dashboard"  # 仪表盘缓存
    )
    # 清除该用户的历史记录缓存
    await cache_manager.delete_pattern(
        f"{CacheKeys.PREFIX}:detections:history:{user_id}:*"
    )
    logger.info(f"用户 {user_id} 缓存已失效")


async def invalidate_admin_stats_cache():
    """使管理后台统计缓存失效"""
    await cache_manager.delete(CacheKeys.admin_stats())
    logger.info("管理后台统计缓存已失效")
