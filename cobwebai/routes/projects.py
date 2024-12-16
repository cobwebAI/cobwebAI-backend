from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from cobwebai.models.project import Project
from cobwebai.utils.auth import current_active_user
from cobwebai.models import User
from cobwebai.repository.projects import ProjectsRepository

from cobwebai.schemas.projects import (
    GetProjectsResponse,
    ProjectShort,
    CreateProjectRequest,
    GetProjectResponse,
    UpdateProjectRequest,
)

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])


@router.get("/", response_model=GetProjectsResponse)
async def get_projects(
    user: User = Depends(current_active_user),
    repository: ProjectsRepository = Depends(),
):
    projects = await repository.get_projects(user.id)
    return GetProjectsResponse(
        projects=list(
            map(
                lambda p: ProjectShort.model_validate(p, from_attributes=True), projects
            )
        )
    )


@router.put("/", response_model=ProjectShort)
async def create_project(
    request: CreateProjectRequest,
    user: User = Depends(current_active_user),
    repository: ProjectsRepository = Depends(),
) -> ProjectShort:
    project = await repository.create_project(
        Project(user_id=user.id, name=request.name)
    )

    return ProjectShort.model_validate(project, from_attributes=True)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    _: User = Depends(current_active_user),
    repository: ProjectsRepository = Depends(),
):
    await repository.delete_project(project_id)


@router.get("/{project_id}", response_model=GetProjectResponse)
async def get_project(
    project_id: UUID,
    user: User = Depends(current_active_user),
    repository: ProjectsRepository = Depends(),
):
    project = await repository.get_project(user.id, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    return GetProjectResponse.model_validate(
        project,
        from_attributes=True,
    )


@router.post("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_project(
    project_id: UUID,
    request: UpdateProjectRequest,
    user: User = Depends(current_active_user),
    repository: ProjectsRepository = Depends(),
):
    try:
        await repository.update_project(user.id, project_id, request.name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
