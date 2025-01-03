from typing import AsyncGenerator, Optional
from fastapi import Depends
from starlette.requests import Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin, schemas
from fastapi_users.db import SQLAlchemyUserDatabase
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from loguru import logger
import uuid

from cobwebai.dependencies.database import get_user_db
from cobwebai.models import User
from cobwebai.settings import settings


class UserRead(schemas.BaseUser[uuid.UUID]):
    """Represents a read command for a user."""


class UserCreate(schemas.BaseUserCreate):
    """Represents a create command for a user."""


class UserUpdate(schemas.BaseUserUpdate):
    """Represents an update command for a user."""


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """Manages a user session and its tokens."""

    reset_password_token_secret = settings.users_secret
    verification_token_secret = settings.users_secret

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        logger.debug(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.debug(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.debug(
            f"Verification requested for user {user.id}. Verification token: {token}"
        )


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    """
    Yield a UserManager instance.

    :param user_db: SQLAlchemy user db instance
    :yields: an instance of UserManager.
    """
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    """
    Return a JWTStrategy in order to instantiate it dynamically.

    :returns: instance of JWTStrategy with provided settings.
    """
    return JWTStrategy(secret=settings.users_secret, lifetime_seconds=None)


auth_jwt = AuthenticationBackend(
    name="jwt",
    transport=BearerTransport(tokenUrl="/api/v1/auth/login"),
    get_strategy=get_jwt_strategy,
)

api_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_jwt])

current_active_user = api_users.current_user(active=True)
current_active_verified_user = api_users.current_user(active=True, verified=True)
