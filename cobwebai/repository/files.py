import uuid

from sqlalchemy import select, update, delete
from cobwebai.models import File, Project
from cobwebai.repository import BaseRepository


class FilesRepository(BaseRepository):
    async def get_files(self, user_id: uuid.UUID, project_id: uuid.UUID) -> list[File]:
        query = (
            select(File)
            .join(Project)
            .where(Project.user_id == user_id, Project.project_id == project_id)
            .with_only_columns(
                [File.file_id, File.name, File.created_at, File.updated_at]
            )
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_files_by_ids(
        self, user_id: uuid.UUID, file_ids: list[uuid.UUID]
    ) -> list[File]:
        query = (
            select(File)
            .join(Project)
            .where(File.file_id.in_(file_ids), Project.user_id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_file(self, user_id: uuid.UUID, file_id: uuid.UUID) -> File:
        query = (
            select(File)
            .join(Project)
            .where(File.file_id == file_id, Project.user_id == user_id)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_file(self, file: File) -> File:
        self.session.add(file)
        await self.flush()
        return file

    async def update_file(
        self,
        user_id: uuid.UUID,
        file_id: uuid.UUID,
        name: str | None = None,
        content: str | None = None,
    ) -> None:
        query = update(File).where(
            File.file_id == file_id,
            File.project_id.in_(
                select(Project.project_id).where(Project.user_id == user_id)
            ),
        )

        if not name and not content:
            raise ValueError("At least one of the fields must be provided")

        if name:
            query = query.values(name=name)
        if content:
            query = query.values(content=content)

        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise ValueError("File not found")
        await self.flush()

    async def delete_file(self, user_id: uuid.UUID, file_id: uuid.UUID) -> None:
        query = delete(File).where(
            File.file_id == file_id,
            File.project_id.in_(
                select(Project.project_id).where(Project.user_id == user_id)
            ),
        )

        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise ValueError("File not found")
        await self.flush()
