from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ChatShort(BaseModel):
    id: UUID = Field(validation_alias="chat_id")
    name: str
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class ChatMessage(BaseModel):
    id: UUID = Field(validation_alias="message_id")
    chat_id: UUID = Field(serialization_alias="chatId")
    role: str
    content: str
    attachments: str | None = None


class ChatFull(ChatShort):
    messages: list[ChatMessage]


class AttachmentType(str, Enum):
    FILE = "file"
    NOTE = "note"


class MessageAttachment(BaseModel):
    id: UUID
    type: AttachmentType


class SendMessageRequest(BaseModel):
    content: str
    attachments: list[MessageAttachment]
    project_id: UUID
