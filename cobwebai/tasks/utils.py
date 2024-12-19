from taskiq import TaskiqMiddleware, TaskiqMessage, TaskiqResult
from cobwebai.models.operations import OperationStatus
from cobwebai.repository.operations import OperationsRepository
from cobwebai.settings import settings
from cobwebai_lib import LLMTools
from pydantic import BaseModel
from loguru import logger
import uuid


llmtools = LLMTools(settings.openapi_key, settings.chroma_port, settings.chroma_host)

class OperationResult(BaseModel):
    result_id: uuid.UUID


class OperationMiddleware(TaskiqMiddleware):
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

        if result.is_err:
            logger.error(f"Operation {operation_id} failed with error: {result.error}")
            status = OperationStatus.FAILED
            result_id = None
        else:
            status = OperationStatus.SUCCESS
            result_id = result.return_value.result_id

        await repository.update_operation(
            operation_id,
            status=status,
            result_id=result_id,
        )

        await session.commit()
        operation = await repository.get_operation(operation_id)
        await sio_manager.send_operation_update(
            operation.project.user_id, operation
        )

