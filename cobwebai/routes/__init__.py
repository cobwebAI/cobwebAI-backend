from fastapi.routing import APIRouter

from .auth import router as auth_router
from .projects import router as projects_router
from .files import router as files_router
from .notes import router as notes_router
from .tests import router as tests_router
from .chat import router as chat_router
from .operations import router as operations_router

api_router = APIRouter()


@api_router.get("/health")
def health_check() -> None:
    """
    Checks the health of a project.

    It returns 200 if the project is healthy.
    """


api_router.include_router(auth_router)
api_router.include_router(projects_router)
api_router.include_router(files_router)
api_router.include_router(notes_router)
api_router.include_router(tests_router)
api_router.include_router(chat_router)
api_router.include_router(operations_router)
