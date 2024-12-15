import socketio
import uuid
from typing import Callable, Awaitable
from fastapi import Request, FastAPI
from cobwebai.models import Operation


def operation_to_dict(operation: Operation) -> dict:
    return {
        "id": str(operation.operation_id),
        "name": operation.name,
        "type": operation.type.value,
        "status": operation.status.value,
        "result_id": str(operation.result_id),
        "created_at": operation.created_at.isoformat(),
        "updated_at": operation.updated_at.isoformat(),
    }


class SocketManager:
    def __init__(self, sio_server: socketio.AsyncServer):
        self.sio_server = sio_server

    async def send_operation_create(self, user_id: uuid.UUID, operation: Operation):
        print(self.sio_server)
        await self.sio_server.emit(
            event="operation_create",
            to=f"operations_{user_id}",
            data=operation_to_dict(operation),
        )

    async def send_operation_update(self, user_id: uuid.UUID, operation: Operation):
        await self.sio_server.emit(
            event="operation_update",
            to=f"operations_{user_id}",
            data=operation_to_dict(operation),
        )

    async def send_operation_delete(self, user_id: uuid.UUID, operation_id: uuid.UUID):
        await self.sio_server.emit(
            event="operation_delete",
            to=f"operations_{user_id}",
            data={"id": operation_id},
        )


async def get_socket_manager(request: Request) -> SocketManager:
    return SocketManager(request.app.state.sio_manager)


def get_sio_startup(
    app: FastAPI, sio_server: socketio.AsyncServer
) -> Callable[[], Awaitable[None]]:
    async def startup():
        app.state.sio_manager = sio_server

    return startup
