from fastapi import APIRouter, status, UploadFile, Form, File
from cobwebai.repository.files import FilesRepository
from cobwebai.repository.projects import ProjectsRepository
from cobwebai.repository.operations import OperationsRepository
from cobwebai.tasks import process_file
from cobwebai.schemas.files import (
    GetFileResponse,
    UpdateFileRequest,
    UploadFileResponse,
)
from cobwebai.repository.notes import NotesRepository
from fastapi import Depends, HTTPException
from cobwebai.models import User
from cobwebai.models.operations import OperationType
from cobwebai.utils.auth import current_active_user
from cobwebai.tasks import generate_note_task
from uuid import UUID
from typing import Annotated
from cobwebai.repository.tests import TestsRepository
from cobwebai.tasks import generate_test_task
from cobwebai.schemas.tests import (
    TestFull,
    CreateTestRequest,
    CreateTestResponse,
    UpdateScoreRequest,
    TestScoreUpdate,
)

router = APIRouter(prefix="/api/v1/tests", tags=["tests"])


@router.get("/{test_id}", response_model=TestFull)
async def get_test(
    test_id: UUID,
    user: User = Depends(current_active_user),
    repository: TestsRepository = Depends(),
):
    test = await repository.get_test(user.id, test_id)
    if test is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found",
        )

    return TestFull.model_validate(test, from_attributes=True)


@router.delete("/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test(
    test_id: UUID,
    user: User = Depends(current_active_user),
    repository: TestsRepository = Depends(),
):
    try:
        await repository.delete_test(user.id, test_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found",
        )


@router.post("/{test_id}/score", response_model=TestScoreUpdate)
async def update_score(
    test_id: UUID,
    request: UpdateScoreRequest,
    user: User = Depends(current_active_user),
    repository: TestsRepository = Depends(),
):
    best_score = await repository.update_best_score(user.id, test_id, request.score)
    if best_score is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found",
        )
    return TestScoreUpdate(best_score=best_score)


@router.post("/", response_model=CreateTestResponse)
async def create_test(
    request: CreateTestRequest,
    user: User = Depends(current_active_user),
    files_repository: FilesRepository = Depends(FilesRepository),
    notes_repository: NotesRepository = Depends(NotesRepository),
    projects_repository: ProjectsRepository = Depends(ProjectsRepository),
    operations_repository: OperationsRepository = Depends(OperationsRepository),
) -> CreateTestResponse:
    project = await projects_repository.get_project(user.id, request.project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    files = await files_repository.get_files_by_ids(user.id, request.files)
    notes = await notes_repository.get_notes_by_ids(user.id, request.notes)

    if len(files) != len(request.files) or len(notes) != len(request.notes):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Some files or notes not found",
        )

    operation = await operations_repository.create_operation(
        user_id=user.id,
        project_id=project.project_id,
        name=f"Генерация теста",
        type=OperationType.TEST,
    )

    await generate_test_task.kiq(
        user_id=user.id,
        project_id=project.project_id,
        operation_id=operation.operation_id,
        files=request.files,
        notes=request.notes,
        description=request.description,
    )

    return CreateTestResponse.model_validate(operation, from_attributes=True)
