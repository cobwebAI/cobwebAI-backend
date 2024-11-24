from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from cobwebai.models.base import Base
import uuid

class Question(Base):
    __tablename__ = "questions"

    question_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    test_id = Column(UUID(as_uuid=True), ForeignKey("tests.test_id"), nullable=False)
    content = Column(JSON, nullable=False)
    order_number = Column(Integer, nullable=False)

    # Связь с тестом
    test = relationship("Test", back_populates="questions")
