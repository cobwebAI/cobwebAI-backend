from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UUID, Text, Float
from sqlalchemy.orm import relationship
from cobwebai.models.base import Base
from datetime import datetime, timezone
import uuid

class Test(Base):
    __tablename__ = "tests"

    test_id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))
    last_result = Column(Float, nullable=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)

    # Связь с проектом
    project = relationship("Project", back_populates="tests")

    # Связь с вопросами
    questions = relationship("Question", back_populates="test")
