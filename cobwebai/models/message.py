import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from cobwebai.models.base import Base

class Message(Base):
    __tablename__ = "messages"

    message_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    content = Column(Text, nullable=False)  # Текст сообщения
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))
    chat_id = Column(UUID(as_uuid=True), ForeignKey("chats.chat_id"), nullable=False)

    # Связь с чатом
    chat = relationship("Chat", back_populates="messages")
