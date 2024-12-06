from fastapi.routing import APIRouter

from .auth import auth_router
from .llm import llm_router
from .projects import projects_router

api_router = APIRouter()


@api_router.get("/health")
def health_check() -> None:
    """
    Checks the health of a project.

    It returns 200 if the project is healthy.
    """


api_router.include_router(auth_router)
api_router.include_router(llm_router)
api_router.include_router(projects_router)