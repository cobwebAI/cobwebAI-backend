from sqlalchemy import Column, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from cobwebai.models.base import Base
from sqlalchemy.sql import func
import uuid
import enum


class OperationType(enum.Enum):
    FILE = "file"
    NOTE = "note"
    TEST = "test"
    PODCAST = "podcast"


class OperationStatus(enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class Operation(Base):
    __tablename__ = "operations"

    operation_id = Column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True
    )

    name = Column(String, nullable=False)
    type = Column(Enum(OperationType), nullable=False)
    status = Column(
        Enum(OperationStatus), nullable=False, default=OperationStatus.PENDING
    )

    extra = Column(JSONB, nullable=True)
    result_id = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.project_id", ondelete="CASCADE"),
        nullable=False,
    )

    project = relationship("Project", back_populates="operations")
