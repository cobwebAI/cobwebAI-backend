import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from cobwebai.models import Message, Chat, Project
from cobwebai.utils.database import acquire_advisory_lock
from cobwebai.repository import BaseRepository
from fastapi import HTTPException


class ChatsRepository(BaseRepository):
    async def get_chats(self, user_id: uuid.UUID, project_id: uuid.UUID) -> list[Chat]:
        query = (
            select(Chat)
            .join(Project)
            .where(Chat.project_id == project_id, Project.user_id == user_id)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_chat(self, user_id: uuid.UUID, chat_id: uuid.UUID) -> Chat:
        query = (
            select(Chat)
            .join(Project)
            .where(Chat.chat_id == chat_id, Project.user_id == user_id)
            .options(selectinload(Chat.messages))
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_chat(self, user_id: uuid.UUID, chat: Chat) -> Chat:
        query = select(Project).where(
            Project.project_id == chat.project_id, Project.user_id == user_id
        )
        result = await self.session.execute(query)
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(
                status_code=400,
                detail="Project does not exist or does not belong to the user",
            )

        self.session.add(chat)
        await self.flush()
        return chat

    async def get_last_message(self, user_id: uuid.UUID, chat_id: uuid.UUID) -> Message:
        query = (
            select(Message)
            .join(Chat)
            .join(Project)
            .where(Message.chat_id == chat_id, Project.user_id == user_id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def add_message(self, user_id: uuid.UUID, message: Message) -> Message:
        query = (
            select(Chat)
            .join(Project)
            .where(Chat.chat_id == message.chat_id, Project.user_id == user_id)
        )

        result = await self.session.execute(query)
        chat = result.scalar_one_or_none()
        if not chat:
            raise HTTPException(
                status_code=400,
                detail="Chat does not exist or does not belong to the user",
            )

        await acquire_advisory_lock(
            self.session, domain="chat_add_message", key=message.chat_id
        )

        last_message = await self.get_last_message(user_id, message.chat_id)
        if last_message and last_message.role == message.role:
            raise HTTPException(
                status_code=400, detail="Cannot add two messages with the same role"
            )

        self.session.add(message)
        await self.flush()
        return message
