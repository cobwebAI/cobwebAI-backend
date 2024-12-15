from starlette.requests import Request
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi_users.db import SQLAlchemyUserDatabase
from cobwebai.models import User
from fastapi import FastAPI
from cobwebai.models.base import Base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncEngine
from typing import Callable, Awaitable
from cobwebai.settings import settings


async def get_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Create and get database session.

    :param request: current request.
    :yield: database session.
    """
    session: AsyncSession = request.app.state.db_session_factory()

    try:
        yield session
    finally:
        await session.commit()


async def get_user_db(
    session: AsyncSession = Depends(get_db_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase, None]:
    """
    Yield a SQLAlchemyUserDatabase instance.

    :param session: asynchronous SQLAlchemy session.
    :yields: instance of SQLAlchemyUserDatabase.
    """
    yield SQLAlchemyUserDatabase(session, User)


def get_db_startup(app: FastAPI) -> Callable[[], Awaitable[None]]:
    async def startup():
        engine = create_async_engine(str(settings.db_url), echo=settings.db_echo)
        session_factory = async_sessionmaker(
            engine,
            expire_on_commit=False,
        )
        app.state.db_engine = engine
        app.state.db_session_factory = session_factory

        await _create_tables(engine)

    return startup


def get_db_shutdown(app: FastAPI) -> Callable[[], Awaitable[None]]:
    async def shutdown():
        await app.state.db_engine.dispose()

    return shutdown


async def _create_tables(engine: AsyncEngine) -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    await engine.dispose()
