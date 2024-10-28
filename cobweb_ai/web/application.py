from importlib import metadata

from fastapi import FastAPI
from fastapi.responses import UJSONResponse

from cobweb_ai.log import configure_logging
from cobweb_ai.web.api.router import api_router
from cobweb_ai.web.lifespan import lifespan_setup


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    configure_logging()
    app = FastAPI(
        title="cobweb_ai",
        version=metadata.version("cobweb_ai"),
        lifespan=lifespan_setup,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")

    return app
