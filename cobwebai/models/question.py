from sqlalchemy import Column, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from cobwebai.models.base import Base
import uuid


class Question(Base):
    __tablename__ = "questions"
    __table_args__ = (UniqueConstraint("test_id", "order_number"),)

    question_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        index=True,
    )
    test_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tests.test_id", ondelete="CASCADE"),
        nullable=False,
    )
    text = Column(Text, nullable=False)
    answers = Column(JSONB, nullable=False)  # list[str]
    correct_answer = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=True)
    order_number = Column(Integer, nullable=False)

    # Связь с тестом
    test = relationship("Test", back_populates="questions")
