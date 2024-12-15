from .lifespan import get_session
from .utils import OperationResult
from sqlalchemy.ext.asyncio import AsyncSession
from cobwebai.repository.notes import NotesRepository
from cobwebai.repository.files import FilesRepository
from cobwebai.repository.tests import TestsRepository

import uuid

from loguru import logger
from typing import Annotated
from taskiq import TaskiqDepends
from cobwebai.models.test import Test
from cobwebai.models.question import Question


async def generate_test(
    user_id: uuid.UUID,
    project_id: uuid.UUID,
    operation_id: uuid.UUID,
    description: str,
    files: list[uuid.UUID],
    notes: list[uuid.UUID],
    session: Annotated[AsyncSession, TaskiqDepends(get_session)],
):
    logger.info(f"Creating test for {user_id} based on {files} and {notes}")
    files = await FilesRepository(session).get_files_by_ids(user_id, files)
    notes = await NotesRepository(session).get_notes_by_ids(user_id, notes)

    name = "Тест"
    description = "..."

    repository = TestsRepository(session)
    test = await repository.create_test(
        Test(
            name=name,
            description=description,
            project_id=project_id,
            questions=[
                Question(
                    text="Тестовый вопрос",
                    answers=["Ответ 1", "Ответ 2", "Ответ 3", "Ответ 4"],
                    correct_answer=0,
                    explanation="...",
                    order_number=0,
                )
            ],
        )
    )

    await session.commit()
    return OperationResult(result_id=test.test_id)
