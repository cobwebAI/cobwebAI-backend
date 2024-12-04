# Модель для хранения информации о пользователе
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from cobwebai.models.base import Base
from datetime import datetime, timezone
import uuid

class User(Base):
    __tablename__ = "users"

    # Уникальный идентификатор пользователя
    user_id = Column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    # Имя пользователя
    username = Column(String, nullable=False, unique=True)
    # Хешированный пароль пользователя
    password = Column(String, nullable=False)
    # Дата регистрации пользователя
    created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))

    # Связь с проектами
    projects = relationship("Project", back_populates="user")