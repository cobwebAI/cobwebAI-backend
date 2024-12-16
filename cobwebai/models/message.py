import uuid
import enum
from sqlalchemy import Column, Text, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from cobwebai.models.base import Base


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        UniqueConstraint("chat_id", "order_number", name="unique_chat_order_number"),
    )

    message_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )

    content = Column(Text, nullable=False)
    role = Column(ENUM(MessageRole, name="message_role_enum"), nullable=False)
    attachments = Column(Text, nullable=True, default=None)
    order_number = Column(Integer, nullable=False, default=0)
    
    created_at = Column(DateTime(timezone=True), default=func.now())
    chat_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chats.chat_id", ondelete="CASCADE"),
        nullable=False,
    )

    # Связь с чатом
    chat = relationship("Chat", back_populates="messages")
