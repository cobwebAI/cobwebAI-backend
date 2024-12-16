from taskiq import TaskiqMiddleware, TaskiqMessage, TaskiqResult
from cobwebai.models.operations import OperationStatus
from cobwebai.repository.operations import OperationsRepository
from pydantic import BaseModel
from loguru import logger
import uuid


class OperationResult(BaseModel):
    result_id: uuid.UUID


class OperationMiddleware(TaskiqMiddleware):
    async def on_error(self, message: TaskiqMessage, error: Exception):
        operation_id = message.kwargs.get("operation_id")

        logger.error(f"Operation {operation_id} failed with error: {error}")
        if not operation_id:
            logger.info("No operation ID provided")
            return

        session = self.broker.state.session_factory()
        sio_manager = self.broker.state.sio_manager
        repository = OperationsRepository(session, sio_manager)
        await repository.update_operation(operation_id, status=OperationStatus.FAILED)
        await session.commit()

        operation = await repository.get_operation(operation_id)

        await sio_manager.send_operation_update(
            operation.project.user_id, operation
        )

    async def post_execute(
        self, message: TaskiqMessage, result: TaskiqResult[OperationResult]
    ):
        operation_id = message.kwargs.get("operation_id")
        if not operation_id:
            logger.info("No operation ID provided")
            return

        session = self.broker.state.session_factory()
        sio_manager = self.broker.state.sio_manager
        repository = OperationsRepository(session, sio_manager)

        await repository.update_operation(
            operation_id,
            status=OperationStatus.SUCCESS,
            result_id=result.return_value.result_id,
        )
        await session.commit()

        operation = await repository.get_operation(operation_id)
        await sio_manager.send_operation_update(
            operation.project.user_id, operation
        )
