from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from api.settings import get_settings


def create_db_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(database_url, pool_pre_ping=True)


engine = create_db_engine(get_settings().database_url)
DBLocal = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


# For non-Fast API contexts such as background tasks
@asynccontextmanager
async def db_context() -> AsyncIterator[AsyncSession]:
    async with DBLocal() as db:
        yield db


async def get_db() -> AsyncIterator[AsyncSession]:
    async with DBLocal() as db:
        yield db
