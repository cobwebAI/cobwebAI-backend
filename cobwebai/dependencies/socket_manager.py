import socketio
import uuid
from typing import Callable, Awaitable
from fastapi import Request, FastAPI
from cobwebai.models import Operation
from loguru import logger


def operation_to_dict(operation: Operation) -> dict:
    return {
        "id": str(operation.operation_id),
        "projectId": str(operation.project_id),
        "name": operation.name,
        "type": operation.type.value,
        "status": operation.status.value,
        "resultId": str(operation.result_id),
        "createdAt": operation.created_at.isoformat(),
        "updatedAt": operation.updated_at.isoformat(),
    }


class SocketManager:
    def __init__(self, sio_server: socketio.AsyncServer):
        self.sio_server = sio_server

    async def send_operation_create(self, user_id: uuid.UUID, operation: Operation):
        logger.info(f"Sending operation create to {f'operations_{user_id}'!r}")
        await self.sio_server.emit(
            event="operation_create",
            room=f"operations_{user_id}",
            data=operation_to_dict(operation),
            namespace="/operations",
        )

    async def send_operation_update(self, user_id: uuid.UUID, operation: Operation):
        logger.info(f"Sending operation update to {f'operations_{user_id}'!r}")
        await self.sio_server.emit(
            event="operation_update",
            room=f"operations_{user_id}",
            data=operation_to_dict(operation),
            namespace="/operations",
        )

    async def send_operation_delete(self, user_id: uuid.UUID, operation_id: uuid.UUID):
        logger.info(f"Sending operation delete to {f'operations_{user_id}'!r}")
        await self.sio_server.emit(
            event="operation_delete",
            room=f"operations_{user_id}",
            data={"id": operation_id},
            namespace="/operations",
        )


async def get_socket_manager(request: Request) -> SocketManager:
    return SocketManager(request.app.state.sio_manager)


def get_sio_startup(
    app: FastAPI, sio_server: socketio.AsyncServer
) -> Callable[[], Awaitable[None]]:
    async def startup():
        app.state.sio_manager = sio_server

    return startup
