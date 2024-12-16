from fastapi import APIRouter, status, UploadFile, Form, File
from cobwebai.repository.files import FilesRepository
from cobwebai.repository.projects import ProjectsRepository
from cobwebai.repository.operations import OperationsRepository
from cobwebai.tasks import process_file_task
from cobwebai.schemas.files import (
    GetFileResponse,
    UpdateFileRequest,
    UploadFileResponse,
)
from fastapi import Depends, HTTPException
from cobwebai.models import User
from cobwebai.models.operations import OperationType
from cobwebai.utils.auth import current_active_user
from types_aiobotocore_s3 import S3Client
from cobwebai.dependencies.storage import get_s3_client
from uuid import UUID
from typing import Annotated
from cobwebai.settings import settings

router = APIRouter(prefix="/api/v1/files", tags=["files"])

SIZE_1GB = 1024 * 1024 * 1024


@router.get("/{file_id}", response_model=GetFileResponse)
async def get_file(
    file_id: UUID,
    user: User = Depends(current_active_user),
    repository: FilesRepository = Depends(),
):
    file = await repository.get_file(user.id, file_id)
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )

    return GetFileResponse.model_validate(file, from_attributes=True)


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: UUID,
    user: User = Depends(current_active_user),
    repository: FilesRepository = Depends(),
):
    try:
        await repository.delete_file(user.id, file_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )


@router.post("/{file_id}", response_model=GetFileResponse)
async def update_file(
    file_id: UUID,
    request: UpdateFileRequest,
    user: User = Depends(current_active_user),
    repository: FilesRepository = Depends(),
):
    result = await repository.update_file(
        user_id=user.id,
        file_id=file_id,
        name=request.name,
        content=request.content,
    )
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    
    await repository.commit()
    return GetFileResponse.model_validate(result, from_attributes=True)


@router.post("/", response_model=UploadFileResponse)
async def upload_file(
    file: Annotated[UploadFile, File(description="The file to upload")],
    project_id: Annotated[str, Form(description="The project ID")],
    user: User = Depends(current_active_user),
    projects_repository: ProjectsRepository = Depends(ProjectsRepository),
    operations_repository: OperationsRepository = Depends(OperationsRepository),
    s3_client: S3Client = Depends(get_s3_client),
):
    if file.size > SIZE_1GB:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File is too large",
        )

    project = await projects_repository.get_project(user.id, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    key = f"upload/{user.id}/{project_id}/{file.filename}"

    await s3_client.put_object(
        Bucket=settings.s3_bucket_name,
        Key=key,
        Body=file.file,
        ContentType=file.content_type,
    )

    operation = await operations_repository.create_operation(
        user_id=user.id,
        project_id=project.project_id,
        name=f"Обработка файла '{file.filename}'",
        type=OperationType.FILE,
    )

    await process_file_task.kiq(
        user_id=user.id,
        project_id=project.project_id,
        operation_id=operation.operation_id,
        file_key=key,
    )

    await operations_repository.commit()
    return UploadFileResponse(operation_id=operation.operation_id)
