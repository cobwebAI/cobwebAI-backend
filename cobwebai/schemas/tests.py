from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime


class TestShort(BaseModel):
    id: UUID = Field(validation_alias="test_id")
    name: str
    best_score: int | None = Field(serialization_alias="bestScore")
    max_score: int = Field(serialization_alias="maxScore")
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class TestQuestion(BaseModel):
    id: UUID = Field(validation_alias="question_id")
    text: str
    answers: list[str]
    correct_answer: int = Field(serialization_alias="correctAnswer")
    explanation: str | None


class TestFull(TestShort):
    description: str | None
    questions: list[TestQuestion]


class TestScoreUpdate(BaseModel):
    best_score: int


class UpdateScoreRequest(BaseModel):
    score: int


class CreateTestRequest(BaseModel):
    project_id: UUID = Field(validation_alias="projectId")
    description: str
    files: list[UUID]
    notes: list[UUID]


class CreateTestResponse(BaseModel):
    operation_id: UUID = Field(serialization_alias="operationId")
