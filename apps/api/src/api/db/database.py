from collections.abc import Iterator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session as SQLAlchemySession
from sqlalchemy.orm import sessionmaker as sqlalchemy_sessionmaker

from api.settings import get_settings


def create_db_engine(database_url: str) -> Engine:
    connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
    return create_engine(database_url, connect_args=connect_args, pool_pre_ping=True)


engine = create_db_engine(get_settings().database_url)
DBLocal = sqlalchemy_sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Iterator[SQLAlchemySession]:
    with DBLocal() as db:
        yield db
