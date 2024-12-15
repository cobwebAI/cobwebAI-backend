import uuid

from fastapi import APIRouter, Depends, HTTPException
from cobwebai.utils.auth import current_active_user
from cobwebai.models import User
from cobwebai.schemas.operations import OperationFull, PendingOperationsResponse
from cobwebai.repository.operations import OperationsRepository


router = APIRouter(prefix="/api/v1/operations", tags=["operations"])


@router.get("/pending", response_model=PendingOperationsResponse)
async def get_pending_operations(
    user: User = Depends(current_active_user),
    repository: OperationsRepository = Depends(),
):
    operations = await repository.get_pending_operations(user.id)
    return PendingOperationsResponse(
        operations=[
            OperationFull.model_validate(operation, from_attributes=True)
            for operation in operations
        ]
    )


@router.get("/{operation_id}", response_model=OperationFull)
async def get_operation(
    operation_id: uuid.UUID,
    user: User = Depends(current_active_user),
    repository: OperationsRepository = Depends(),
):
    operation = await repository.get_operation(operation_id, user.id)
    if not operation:
        raise HTTPException(status_code=404, detail="Operation not found")
    return OperationFull.model_validate(operation, from_attributes=True)
