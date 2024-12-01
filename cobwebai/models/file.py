from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from cobwebai.models.base import Base
from datetime import datetime, timezone
import uuid

class File(Base):
    __tablename__ = "files"

    # Уникальный идентификатор файла
    file_id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    name = Column(String, nullable=False)
    # Содержание файла
    content = Column(Text, nullable=False)
    # Дата создания файла
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))
    # Уникальный идентификатор проекта
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)

    # Связь с проектом
    project = relationship("Project", back_populates="files")
