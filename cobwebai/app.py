import socketio

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from fastapi.middleware.cors import CORSMiddleware

from cobwebai.settings import settings
from cobwebai.utils.log import configure_logging
from cobwebai.routes import api_router
from cobwebai.dependencies.storage import get_storage_startup, get_storage_shutdown
from cobwebai.dependencies.database import get_db_startup, get_db_shutdown
from cobwebai.dependencies.socket_manager import get_sio_startup
from cobwebai.tasks import broker
from cobwebai.routes.websockets import OperationsNamespace


def get_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title="cobweb_ai",
        docs_url="/api/v1/docs",
        redoc_url="/api/v1/redoc",
        openapi_url="/api/v1/openapi.json",
        default_response_class=UJSONResponse,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    redis_manager = socketio.AsyncRedisManager(settings.redis_url)
    sio = socketio.AsyncServer(
        async_mode="asgi",
        client_manager=redis_manager,
        cors_allowed_origins=[],
    )

    sio.register_namespace(OperationsNamespace("/operations"))
    sio_asgi = socketio.ASGIApp(sio, app)

    app.add_route("/socket.io/", route=sio_asgi, methods=["GET", "POST"])  # noqa
    app.add_websocket_route("/socket.io/", sio_asgi)  # noqa

    app.include_router(api_router)

    app.add_event_handler("startup", get_db_startup(app))
    app.add_event_handler("shutdown", get_db_shutdown(app))
    app.add_event_handler("startup", get_storage_startup(app))
    app.add_event_handler("shutdown", get_storage_shutdown(app))
    app.add_event_handler("startup", get_sio_startup(app, sio))
    app.add_event_handler("startup", broker.startup)
    app.add_event_handler("shutdown", broker.shutdown)

    return app
