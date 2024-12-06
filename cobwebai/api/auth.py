from fastapi import APIRouter
from cobwebai.auth import UserCreate, UserRead, UserUpdate, api_users, auth_jwt

auth_router = APIRouter()

auth_router.include_router(
    api_users.get_register_router(UserRead, UserCreate),
    prefix="/api/v1/auth",
    tags=["auth"],
)

auth_router.include_router(
    api_users.get_reset_password_router(),
    prefix="/api/v1/auth",
    tags=["auth"],
)

auth_router.include_router(
    api_users.get_verify_router(UserRead),
    prefix="/api/v1/auth",
    tags=["auth"],
)

auth_router.include_router(
    api_users.get_users_router(UserRead, UserUpdate),
    prefix="/api/v1/users",
    tags=["users"],
)

auth_router.include_router(
    api_users.get_auth_router(auth_jwt),
    prefix="/api/v1/auth",
    tags=["auth"],
)
