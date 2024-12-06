from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from cobwebai.auth import current_active_user
from cobwebai.dependecies.database import get_db_session
from cobwebai.models import User, Project
from cobwebai.repositories.project_repository import ProjectRepository

# projects_router = APIRouter(prefix="/api/v1", tags=["projects"])

# @projects_router.get("/projects")
# async def list_user_projects(user: User = Depends(current_active_user), db_session: AsyncSession = Depends(get_db_session)):
#     projects = ProjectRepository(db_session).get_projects_by_user(user.id)
    