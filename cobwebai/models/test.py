from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey,
    UUID,
    Text,
    Integer,
    select,
)
from sqlalchemy.orm import relationship, column_property
from cobwebai.models.base import Base
from sqlalchemy.sql import func
from cobwebai.models.question import Question

import uuid


class Test(Base):
    __tablename__ = "tests"

    test_id = Column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True
    )
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now()
    )
    best_score = Column(Integer, nullable=True)
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.project_id", ondelete="CASCADE"),
        nullable=False,
    )

    # Связь с проектом
    project = relationship("Project", back_populates="tests")

    # Связь с вопросами
    questions = relationship("Question", back_populates="test")

    max_score = column_property(
        select(func.count(Question.question_id))
        .where(Question.test_id == test_id)
        .correlate_except(Question)
        .scalar_subquery()
    )
