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
    id: int = Field(validation_alias="order_number")
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
    project_id: UUID = Field(validation_alias="projectId")


class SendMessageResponse(BaseModel):
    chat_id: UUID = Field(serialization_alias="chatId")
    chat_name: str = Field(serialization_alias="chatName")
    assistant_answer: ChatMessage = Field(serialization_alias="assistantAnswer")
