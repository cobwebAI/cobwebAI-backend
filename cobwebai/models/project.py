from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from cobwebai.models.base import Base
from datetime import datetime, timezone
from sqlalchemy.sql import func
import uuid

class Project(Base):
    __tablename__ = "projects"

    # Уникальный идентификатор проекта
    project_id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    # Название проекта
    name = Column(String, nullable=False)
    # Дата создания проекта
    created_at = Column(DateTime(timezone=False), default=func.now(), nullable=False)
    # Дата последнего обновления проекта
    updated_at = Column(DateTime(timezone=False), default=func.now(), nullable=False)
    # Уникальный идентификатор пользователя
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Связи с зависимыми сущностями
    files = relationship("File", back_populates="project")
    notes = relationship("Note", back_populates="project")
    podcasts = relationship("Podcast", back_populates="project")
    tests = relationship("Test", back_populates="project")
    chats = relationship("Chat", back_populates="project")

    # Связь с пользователем
    user = relationship("User", back_populates="projects")