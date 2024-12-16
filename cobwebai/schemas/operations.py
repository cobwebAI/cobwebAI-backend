from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from cobwebai.models.operations import OperationType, OperationStatus


class OperationFull(BaseModel):
    id: UUID = Field(validation_alias="operation_id")
    project_id: UUID = Field(serialization_alias="projectId")
    name: str
    type: OperationType
    status: OperationStatus
    result_id: UUID | None = Field(serialization_alias="resultId")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class PendingOperationsResponse(BaseModel):
    operations: list[OperationFull]
