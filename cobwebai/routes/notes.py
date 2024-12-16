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
from fastapi import Depends, HTTPException
from cobwebai.models import User
from cobwebai.models.operations import OperationType
from cobwebai.utils.auth import current_active_user
from cobwebai.tasks import generate_note_task
from uuid import UUID
from typing import Annotated
from cobwebai.repository.notes import NotesRepository
from cobwebai.schemas.notes import (
    NoteFull,
    CreateNoteRequest,
    UpdateNoteRequest,
    CreateNoteResponse,
)

router = APIRouter(prefix="/api/v1/notes", tags=["notes"])


@router.get("/{note_id}", response_model=NoteFull)
async def get_note(
    note_id: UUID,
    user: User = Depends(current_active_user),
    repository: NotesRepository = Depends(),
):
    note = await repository.get_note(user.id, note_id)

    return NoteFull.model_validate(note, from_attributes=True)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: UUID,
    user: User = Depends(current_active_user),
    repository: NotesRepository = Depends(),
):
    try:
        await repository.delete_note(user.id, note_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )


@router.post("/{note_id}", response_model=NoteFull)
async def update_note(
    note_id: UUID,
    request: UpdateNoteRequest,
    user: User = Depends(current_active_user),
    repository: NotesRepository = Depends(),
) -> NoteFull:
    note = await repository.update_note(
        user_id=user.id,
        note_id=note_id,
        name=request.name,
        content=request.content,
    )

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Note not found",
        )

    await repository.commit()
    return NoteFull.model_validate(note, from_attributes=True)


@router.post("/", response_model=CreateNoteResponse)
async def create_note(
    request: CreateNoteRequest,
    user: User = Depends(current_active_user),
    files_repository: FilesRepository = Depends(FilesRepository),
    projects_repository: ProjectsRepository = Depends(ProjectsRepository),
    operations_repository: OperationsRepository = Depends(OperationsRepository),
) -> CreateNoteResponse:
    project = await projects_repository.get_project(user.id, request.project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    files = await files_repository.get_files_by_ids(user.id, request.files)

    if len(files) != len(request.files):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Some files not found",
        )

    operation = await operations_repository.create_operation(
        user_id=user.id,
        project_id=project.project_id,
        name=f"Генерация конспекта",
        type=OperationType.NOTE,
    )

    await generate_note_task.kiq(
        user_id=user.id,
        project_id=project.project_id,
        operation_id=operation.operation_id,
        files=request.files,
        description=request.description,
    )

    await operations_repository.commit()
    return CreateNoteResponse.model_validate(operation, from_attributes=True)
