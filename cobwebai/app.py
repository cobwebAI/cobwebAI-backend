from typing import AsyncGenerator
from importlib import metadata
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from cobwebai.settings import settings
from cobwebai.log import configure_logging
from cobwebai.api.router import api_router


def _setup_db(app: FastAPI) -> None:  # pragma: no cover
    """
    Creates connection to the database.

    This function creates SQLAlchemy engine instance,
    session_factory for creating sessions
    and stores them in the application's state property.

    :param app: fastAPI application.
    """
    engine = create_async_engine(str(settings.db_url), echo=settings.db_echo)
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory


async def _create_tables() -> None:  # pragma: no cover
    """Populates tables in the database."""
    from cobwebai.models.base import Base

    engine = create_async_engine(str(settings.db_url))
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    await engine.dispose()


@asynccontextmanager
async def lifespan_setup(
    app: FastAPI,
) -> AsyncGenerator[None, None]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db_engine.

    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """

    app.middleware_stack = None
    _setup_db(app)
    await _create_tables()
    app.middleware_stack = app.build_middleware_stack()

    yield
    await app.state.db_engine.dispose()


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    configure_logging()
    app = FastAPI(
        title="cobweb_ai",
        version=metadata.version("cobwebai"),
        lifespan=lifespan_setup,
        docs_url="/api/v1/docs",
        redoc_url="/api/v1/redoc",
        openapi_url="/api/v1/openapi.json",
        default_response_class=UJSONResponse,
    )

    app.include_router(api_router)

    return app
