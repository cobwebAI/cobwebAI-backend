from .lifespan import get_s3_client, get_session
from .utils import OperationResult, llmtools
from cobwebai.settings import settings
from sqlalchemy.ext.asyncio import AsyncSession
from cobwebai.repository.files import FilesRepository
from cobwebai.models.file import File
from aiofiles import tempfile
from aiofiles import open as aio_open
from os import path
import uuid

from loguru import logger
from types_aiobotocore_s3 import S3Client
from typing import Annotated
from taskiq import TaskiqDepends


FILE_CHUNK_SIZE = 1024 * 1024 * 100  # 100MB
TEXT_FILE_EXTENSIONS = set(["txt", "md"])
AV_FILE_EXTENSIONS = set(["mp4", "m4a", "mp3", "mkv", "ogg", "wav", "avi", "mov"])


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
    stream = resource["Body"]
    file_name = path.basename(file_key)
    file_extension = path.splitext(file_key)[1].lstrip(".")

    content: str = None

    if file_extension in AV_FILE_EXTENSIONS:
        async with tempfile.TemporaryDirectory() as tempdir:
            # We need file with extension for ffmpeg
            named_file_path = path.join(tempdir, f"{operation_id}_{file_name}")

            async with aio_open(named_file_path, "wb") as named_file:
                async for chunk in stream.iter_chunks(FILE_CHUNK_SIZE):
                    await named_file.write(chunk)

            content = await llmtools.transcribe_avfile(named_file_path)
    elif file_extension in TEXT_FILE_EXTENSIONS:
        content = await llmtools.s2t_pp.fix_transcribed_text(
            (await stream.read()).decode()
        )
    else:
        raise ValueError("cannot process a file with unknown file type")

    repository = FilesRepository(session)
    file = await repository.create_file(
        file=File(name=file_name, content=content, project_id=project_id)
    )

    await session.commit()
    return OperationResult(result_id=file.file_id)
