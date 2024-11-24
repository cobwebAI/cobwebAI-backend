import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from cobwebai.models.base import Base

class Chat(Base):
    __tablename__ = "chats"

    chat_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    name = Column(String, nullable=False)  # Название чата
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))
    updated_at = Column(DateTime, onupdate=datetime.now(tz=timezone.utc))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.project_id"), nullable=False)

    # Связь с проектом
    project = relationship("Project", back_populates="chats")

    # Связь с сообщениями
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")
