from fastapi import HTTPException
from .lifespan import get_session
from .utils import OperationResult, llmtools
from itertools import chain
from cobwebai_lib.chat import ChatAttachment
from cobwebai_lib.text import Question as LibQuestion
from sqlalchemy.ext.asyncio import AsyncSession
from cobwebai.repository.notes import NotesRepository
from cobwebai.repository.files import FilesRepository
from cobwebai.repository.tests import TestsRepository

from random import shuffle
import uuid

from loguru import logger
from typing import Annotated
from taskiq import TaskiqDepends
from cobwebai.models.test import Test
from cobwebai.models.question import Question


def question_cast(idx: int, test: LibQuestion) -> Question:
    answers = test.incorrect_answers
    answers.append(test.correct_answer)
    shuffle(answers)

    correct_idx = 0
    for i, answer in enumerate(answers):
        if answer == test.correct_answer:
            correct_idx = i
            break

    return Question(
        text=test.question,
        answers=answers,
        correct_answer=correct_idx,
        explanation=test.correct_answer_explanation,
        order_number=idx,
    )


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
    attached_files = await FilesRepository(session).get_files_by_ids(user_id, files)
    attached_notes = await NotesRepository(session).get_notes_by_ids(user_id, notes)

    if len(attached_files) != len(files):
        raise HTTPException(status_code=400, detail="Some files not found")

    if len(attached_notes) != len(notes):
        raise HTTPException(status_code=400, detail="Some notes not found")

    attachments = list(
        chain(
            map(lambda n: ChatAttachment(n.note_id, n.content), attached_notes),
            map(lambda n: ChatAttachment(n.file_id, n.content), attached_files),
        )
    )

    lib_test = await llmtools.create_test(
        user_id, project_id, explanation=description, attachments=attachments
    )

    repository = TestsRepository(session)
    test = await repository.create_test(
        Test(
            name=lib_test.test_name,
            description=description,
            project_id=project_id,
            questions=list(
                map(lambda t: question_cast(t[0], t[1]), enumerate(lib_test.questions))
            ),
        )
    )

    await session.commit()
    return OperationResult(result_id=test.test_id)
