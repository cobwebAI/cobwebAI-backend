import uuid

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from cobwebai.models import Operation, Project
from cobwebai.models.operations import OperationType, OperationStatus
from cobwebai.dependencies import get_db_session
from cobwebai.dependencies.socket_manager import SocketManager, get_socket_manager
from cobwebai.repository import BaseRepository

from fastapi import Depends


class OperationsRepository(BaseRepository):
    def __init__(
        self,
        session: AsyncSession = Depends(get_db_session),
        sio_manager: SocketManager = Depends(get_socket_manager),
    ):
        super().__init__(session)
        self.sio_manager = sio_manager

    async def create_operation(
        self, user_id: uuid.UUID, project_id: uuid.UUID, name: str, type: OperationType
    ) -> Operation:
        query = select(Project).where(
            Project.project_id == project_id, Project.user_id == user_id
        )
        result = await self.session.execute(query)
        project = result.scalar_one_or_none()
        if not project:
            raise ValueError("Project does not exist or does not belong to the user")

        operation = Operation(project_id=project_id, name=name, type=type)
        self.session.add(operation)
        await self.flush()
        await self.sio_manager.send_operation_create(user_id, operation)
        return operation

    async def get_operation(
        self, operation_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> Operation:
        query = (
            select(Operation)
            .options(joinedload(Operation.project))
            .where(Operation.operation_id == operation_id)
            .limit(1)
        )

        if user_id:
            query = query.join(Project).where(Project.user_id == user_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_pending_operations(self, user_id: uuid.UUID) -> list[Operation]:
        query = (
            select(Operation)
            .join(Project)
            .where(
                Operation.status == OperationStatus.PENDING,
                Project.user_id == user_id,
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update_operation(
        self,
        operation_id: uuid.UUID,
        status: OperationStatus,
        result_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
    ) -> Operation:
        query = (
            update(Operation)
            .where(
                Operation.operation_id == operation_id,
                Operation.status == OperationStatus.PENDING,
            )
            .values(status=status, result_id=result_id)
            .returning(Operation)
        )

        result = await self.session.execute(query)
        await self.flush()

        updated_operation = result.scalar_one_or_none()
        if not updated_operation:
            raise ValueError("Operation not found")

        return updated_operation

    async def delete_operation(
        self, operation_id: uuid.UUID, user_id: uuid.UUID
    ) -> None:
        query = delete(Operation).where(
            Operation.operation_id == operation_id,
            Operation.project_id.in_(
                select(Project.project_id).where(Project.user_id == user_id)
            ),
        )
        result = await self.session.execute(query)
        if result.rowcount == 0:
            raise ValueError("Operation not found")
        await self.flush()
        await self.sio_manager.send_operation_delete(user_id, operation_id)
