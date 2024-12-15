from uuid import UUID
from pydantic import BaseModel, Field, model_validator
from typing import Literal, Self
from datetime import datetime


class FileShort(BaseModel):
    id: UUID = Field(validation_alias="file_id")
    name: str
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")

    type: Literal["text", "image"] = "text"


class GetFileResponse(BaseModel):
    id: UUID = Field(validation_alias="file_id")
    name: str
    content: str
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")
    type: Literal["text", "image"] = "text"


class UpdateFileRequest(BaseModel):
    name: str | None = None
    content: str | None = None

    @model_validator(mode="after")
    def check_at_least_one(self) -> Self:
        if self.name is None and self.content is None:
            raise ValueError("At least one field must be provided")
        return self


class UploadFileResponse(BaseModel):
    operation_id: UUID = Field(serialization_alias="operationId")
