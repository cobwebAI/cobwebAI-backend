from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime


class NoteShort(BaseModel):
    id: UUID = Field(validation_alias="note_id")
    name: str
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class NoteFull(BaseModel):
    id: UUID = Field(validation_alias="note_id")
    name: str
    content: str
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class CreateNoteRequest(BaseModel):
    project_id: UUID = Field(validation_alias="projectId")
    description: str
    files: list[UUID]


class CreateNoteResponse(BaseModel):
    operation_id: UUID = Field(serialization_alias="operationId")


class UpdateNoteRequest(BaseModel):
    name: str | None = None
    content: str | None = None
