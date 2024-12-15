from sqlalchemy.ext.asyncio import AsyncSession
from cobwebai.dependencies import get_db_session

from fastapi import Depends


class BaseRepository:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.session = session

    async def flush(self) -> None:
        await self.session.flush()

    async def commit(self) -> None:
        await self.session.commit()
