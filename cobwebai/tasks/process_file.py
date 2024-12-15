from .lifespan import get_s3_client, get_session
from .utils import OperationResult
from cobwebai.settings import settings
from sqlalchemy.ext.asyncio import AsyncSession
from cobwebai.repository.files import FilesRepository
from cobwebai.models.file import File
import uuid

from loguru import logger
from types_aiobotocore_s3 import S3Client
from typing import Annotated
from taskiq import TaskiqDepends


async def process_file(
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    operation_id: uuid.UUID,
    file_key: str,
    s3_client: Annotated[S3Client, TaskiqDepends(get_s3_client)],
    session: Annotated[AsyncSession, TaskiqDepends(get_session)],
):
    logger.info(f"Processing file {file_key}")
    resource = await s3_client.get_object(Bucket=settings.s3_bucket_name, Key=file_key)
    async with resource["Body"] as body:
        # chunk = await body.read(...)
        ...

    content = "..."
    file_name = file_key.rsplit("/", 1)[-1]

    repository = FilesRepository(session)
    file = await repository.create_file(
        file=File(name=file_name, content=content, project_id=project_id)
    )

    await session.commit()
    return OperationResult(result_id=file.file_id)
