import uuid

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from cobwebai.models import Note, Project
from cobwebai.repository import BaseRepository


class NotesRepository(BaseRepository):
    async def get_notes(self, user_id: uuid.UUID, project_id: uuid.UUID) -> list[Note]:
        query = (
            select(Note)
            .join(Project)
            .where(Project.user_id == user_id, Note.project_id == project_id)
            .with_only_columns(
                [Note.note_id, Note.name, Note.created_at, Note.updated_at]
            )
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_note(self, user_id: uuid.UUID, note_id: uuid.UUID) -> Note:
        query = (
            select(Note)
            .join(Project)
            .where(Note.note_id == note_id, Project.user_id == user_id)
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_notes_by_ids(
        self, user_id: uuid.UUID, note_ids: list[uuid.UUID]
    ) -> list[Note]:
        query = (
            select(Note)
            .join(Project)
            .where(Note.note_id.in_(note_ids), Project.user_id == user_id)
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_note(self, note: Note) -> Note:
        self.session.add(note)
        await self.flush()
        return note

    async def update_note(
        self,
        user_id: uuid.UUID,
        note_id: uuid.UUID,
        name: str | None = None,
        content: str | None = None,
    ) -> Note:
        query = (
            update(Note)
            .where(
                Note.note_id == note_id,
                Note.project_id.in_(
                    select(Project.project_id).where(Project.user_id == user_id)
                ),
            )
            .returning(Note)
        )

        if not name and not content:
            raise ValueError("At least one of the fields must be provided")

        if name:
            query = query.values(name=name)
        if content:
            query = query.values(content=content)

        result = await self.session.execute(query)
        await self.flush()
        return result.scalar_one_or_none()

    async def delete_note(self, user_id: uuid.UUID, note_id: uuid.UUID) -> None:
        query = delete(Note).where(
            Note.note_id == note_id,
            Note.project_id.in_(
                select(Project.project_id).where(Project.user_id == user_id)
            ),
        )

        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise ValueError("Note not found")
        await self.flush()
