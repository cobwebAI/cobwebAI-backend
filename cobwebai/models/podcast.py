import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from cobwebai.models.base import Base

class Podcast(Base):
    __tablename__ = "podcasts"

    podcast_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    audio_file_s3 = Column(String, nullable=False)  # Ссылка на аудиофайл в S3
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.project_id", ondelete="CASCADE"), nullable=False)

    # Связь с проектом
    project = relationship("Project", back_populates="podcasts")
