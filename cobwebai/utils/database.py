import hashlib
import uuid

from sqlalchemy.sql import expression
from sqlalchemy.sql.expression import func
from sqlalchemy.ext.asyncio import AsyncSession


async def acquire_advisory_lock(
    session: AsyncSession, domain: str, key: uuid.UUID | str | int
) -> None:
    lock_id = hashlib.sha256(f"{domain}:{key}".encode("utf-8"))
    lock_id = int.from_bytes(lock_id.digest()[:8], byteorder="big", signed=True)

    await session.execute(expression.select(func.pg_advisory_xact_lock(lock_id)))
