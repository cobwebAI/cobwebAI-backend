from sqlalchemy.orm import DeclarativeBase

from cobweb_ai.db.meta import meta


class Base(DeclarativeBase):
    """Base for all models."""

    metadata = meta
