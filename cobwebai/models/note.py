from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from cobwebai.models.base import Base
from datetime import datetime, timezone
import uuid

class Note(Base):
    __tablename__ = "notes"

    # Уникальный идентификатор заметки
    note_id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    # Название заметки
    name = Column(String, nullable=False)
    # Текст заметки
    content = Column(Text, nullable=False)
    # Дата создания файла
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(tz=timezone.utc))
    # Уникальный идентификатор проекта
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.project_id"), nullable=False)

    # Связь с проектом
    project = relationship("Project", back_populates="notes")
