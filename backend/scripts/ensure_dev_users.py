"""Create default local accounts when they are missing.

Does not reset or delete existing users.
"""
import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database import Base
from app.core.security import get_password_hash
from app.models.user import User, UserRole
import app.models  # noqa: F401  # register all tables on Base.metadata


DEV_USERS = (
    ("user", "user@example.com", "user123", UserRole.USER),
    ("admin", "admin@example.com", "admin123", UserRole.ADMIN),
)


async def ensure_dev_users() -> None:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with session_factory() as session:
        created = []
        for username, email, password, role in DEV_USERS:
            result = await session.execute(select(User).where(User.username == username))
            if result.scalar_one_or_none() is not None:
                continue
            session.add(
                User(
                    username=username,
                    email=email,
                    hashed_password=get_password_hash(password),
                    role=role,
                    is_active=True,
                )
            )
            created.append(username)
        await session.commit()

    await engine.dispose()

    if created:
        print("created default users: " + ", ".join(created))
    else:
        print("default users already exist")


if __name__ == "__main__":
    asyncio.run(ensure_dev_users())
