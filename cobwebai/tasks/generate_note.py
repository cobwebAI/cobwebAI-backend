from .lifespan import get_session
from .utils import OperationResult
from sqlalchemy.ext.asyncio import AsyncSession
from cobwebai.repository.notes import NotesRepository
from cobwebai.repository.files import FilesRepository
from cobwebai.models.note import Note
import uuid

from loguru import logger
from typing import Annotated
from taskiq import TaskiqDepends


async def generate_note(
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    operation_id: uuid.UUID,
    description: str,
    files: list[uuid.UUID],
    session: Annotated[AsyncSession, TaskiqDepends(get_session)],
):
    logger.info(f"Creating note for {user_id} based on {files} and {description}")
    files = await FilesRepository(session).get_files_by_ids(user_id, files)

    content = "..."
    name = "Конспект"

    repository = NotesRepository(session)
    note = await repository.create_note(
        note=Note(
            name=name,
            content=content,
            project_id=project_id,
        )
    )

    await session.commit()
    return OperationResult(result_id=note.note_id)
