# Модель для хранения информации о пользователе
from sqlalchemy import Column, String, DateTime
from sqlalchemy.orm import relationship
from cobwebai.models.base import Base
from datetime import datetime, timezone
from fastapi_users.db import SQLAlchemyBaseUserTableUUID


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    # # Имя пользователя
    # username = Column(String, nullable=False, unique=True)
    # # Хешированный пароль пользователя
    # password = Column(String, nullable=False)
    # # Дата регистрации пользователя
    # created_at = Column(DateTime, default=datetime.now(tz=timezone.utc))

    # Связь с проектами
    projects = relationship("Project", back_populates="user")