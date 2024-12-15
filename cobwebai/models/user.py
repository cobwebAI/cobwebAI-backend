# Модель для хранения информации о пользователе
from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from cobwebai.models.base import Base
from fastapi_users.db import SQLAlchemyBaseUserTableUUID


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"

    # Дата регистрации пользователя
    created_at = Column(DateTime(timezone=True), default=func.now())

    # Связь с проектами
    projects = relationship("Project", back_populates="user")
