from fastapi import FastAPI
from aiobotocore.session import get_session
from types_aiobotocore_s3 import S3Client
from contextlib import AsyncExitStack
from starlette.requests import Request
from typing import Callable, Awaitable
from cobwebai.settings import settings


def get_storage_startup(app: FastAPI) -> Callable[[], Awaitable[None]]:
    async def startup():
        session = get_session()
        exit_stack = AsyncExitStack()

        app.state.s3_client = await exit_stack.enter_async_context(
            session.create_client(
                "s3",
                region_name=settings.s3_region,
                aws_access_key_id=settings.s3_key_id,
                aws_secret_access_key=settings.s3_secret_key,
                endpoint_url=settings.s3_endpoint_url,
            )
        )

        app.state.s3_exit_stack = exit_stack

    return startup


def get_storage_shutdown(app: FastAPI) -> Callable[[], Awaitable[None]]:
    async def shutdown():
        await app.state.s3_exit_stack.aclose()

    return shutdown


async def get_s3_client(request: Request) -> S3Client:
    return request.app.state.s3_client
