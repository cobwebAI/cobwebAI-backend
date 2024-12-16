import socketio
from typing import AsyncGenerator

from cobwebai.dependencies.socket_manager import SocketManager
from aiobotocore.session import get_session as get_aiobotocore_session
from cobwebai.settings import settings
from taskiq import TaskiqState, TaskiqDepends, Context
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from contextlib import AsyncExitStack
from types_aiobotocore_s3 import S3Client
from typing import Annotated


async def startup(state: TaskiqState):
    aiobotocore_session = get_aiobotocore_session()
    exit_stack = AsyncExitStack()

    s3_client = await exit_stack.enter_async_context(
        aiobotocore_session.create_client(
            "s3",
            region_name=settings.s3_region,
            aws_access_key_id=settings.s3_key_id,
            aws_secret_access_key=settings.s3_secret_key,
            endpoint_url=settings.s3_endpoint_url,
        )
    )

    engine = create_async_engine(str(settings.db_url), echo=settings.db_echo)
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    redis_manager = socketio.AsyncRedisManager(settings.redis_url)
    sio_server = socketio.AsyncServer(client_manager=redis_manager)

    state.sio_server = sio_server
    state.sio_redis_manager = redis_manager
    state.sio_manager = SocketManager(sio_server)

    state.engine = engine
    state.session_factory = session_factory
    state.s3_client = s3_client
    state.s3_exit_stack = exit_stack


async def shutdown(state: TaskiqState):
    await state.engine.dispose()


async def get_session(
    context: Annotated[Context, TaskiqDepends()],
) -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = context.state.session_factory()

    try:
        yield session
    finally:
        await session.commit()


async def get_s3_client(context: Annotated[Context, TaskiqDepends()]) -> S3Client:
    return context.state.s3_client
