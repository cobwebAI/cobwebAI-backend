import uuid

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_expression, load_only
from sqlalchemy import func
from cobwebai.models import Project, File, Test, Note, Chat
from cobwebai.repository import BaseRepository


class ProjectsRepository(BaseRepository):
    async def get_projects(self, user_id: uuid.UUID) -> list[Project]:
        query = (
            select(Project)
            .where(Project.user_id == user_id)
            .options(load_only(Project.project_id, Project.name))
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_project(
        self, user_id: uuid.UUID, project_id: uuid.UUID
    ) -> Project | None:
        file_cols = [File.file_id, File.name, File.created_at, File.updated_at]
        note_cols = [Note.note_id, Note.name, Note.created_at, Note.updated_at]
        chat_cols = [Chat.chat_id, Chat.name, Chat.created_at, Chat.updated_at]
        test_cols = [
            Test.test_id,
            Test.name,
            Test.best_score,
            Test.max_score,
            Test.created_at,
            Test.updated_at,
        ]

        query = (
            select(Project)
            .where(Project.project_id == project_id, Project.user_id == user_id)
            .options(
                selectinload(Project.files).load_only(*file_cols),
                selectinload(Project.tests)
                .load_only(*test_cols)
                .selectinload(Test.questions),
                selectinload(Project.notes).load_only(*note_cols),
                selectinload(Project.chats).load_only(*chat_cols),
            )
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_project(self, project: Project) -> Project:
        self.session.add(project)
        await self.flush()
        return project

    async def update_project(
        self, user_id: uuid.UUID, project_id: uuid.UUID, name: str
    ) -> None:
        query = (
            update(Project)
            .where(Project.project_id == project_id, Project.user_id == user_id)
            .values(name=name)
        )

        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise ValueError("Project not found")

        await self.flush()

    async def delete_project(self, user_id: uuid.UUID, project_id: uuid.UUID) -> None:
        query = delete(Project).where(
            Project.project_id == project_id, Project.user_id == user_id
        )
        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise ValueError("Project not found")
        await self.flush()
