from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from datetime import datetime
from loguru import logger

from cobwebai.auth import current_active_user
from cobwebai.dependecies.database import get_db_session
from cobwebai.models import User, Project
from .utils import DB_ERR_MSG


class ProjectName(BaseModel):
    name: str


class ProjectIdNamePair(BaseModel):
    id: UUID
    name: str


class ProjectList(BaseModel):
    projects: list[ProjectIdNamePair]


class FileInfo(BaseModel):
    id: UUID
    name: str
    createdAt: datetime


# class TestInfo(BaseModel):


# class ProjectInfo(BaseModel):
#     id: UUID
#     name: str
#     files: list[FileInfo]
#     tests: list[TestInfo]


projects_router = APIRouter(prefix="/api/v1", tags=["projects"])


@projects_router.get(
    "/projects",
    response_model=ProjectList,
    responses={"500": {"description": DB_ERR_MSG}},
)
async def list_user_projects(
    user: User = Depends(current_active_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        query_result = await db_session.execute(
            select(Project).where(Project.user_id == user.id)
        )

        user_projects = map(
            lambda p: ProjectIdNamePair(id=p.project_id, name=p.name),
            query_result.scalars().all(),
        )

        return ProjectList(projects=list(user_projects))

    except Exception as e:
        logger.error(e)
        raise HTTPException(500, DB_ERR_MSG)


@projects_router.put(
    "/projects",
    response_model=ProjectIdNamePair,
    responses={"500": {"description": DB_ERR_MSG}},
)
async def add_project(
    input: ProjectName,
    user: User = Depends(current_active_user),
    db_session: AsyncSession = Depends(get_db_session),
):
    try:
        project = Project(name=input.name, user_id=user.id)
        db_session.add(project)
        await db_session.flush()

        return ProjectIdNamePair(id=project.project_id, name=project.name)

    except Exception as e:
        logger.error(e)
        raise HTTPException(500, DB_ERR_MSG)
