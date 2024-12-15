import uuid

from sqlalchemy import select, update, delete, func, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from cobwebai.models import Test, Project
from cobwebai.repository import BaseRepository


class TestsRepository(BaseRepository):
    async def get_tests(self, user_id: uuid.UUID, project_id: uuid.UUID) -> list[Test]:
        query = (
            select(Test)
            .join(Project)
            .where(Project.user_id == user_id, Test.project_id == project_id)
            .with_only_columns(
                [
                    Test.test_id,
                    Test.name,
                    Test.best_score,
                    Test.max_score,
                    Test.created_at,
                    Test.updated_at,
                ]
            )
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_test(self, user_id: uuid.UUID, test_id: uuid.UUID) -> Test:
        query = (
            select(Test)
            .join(Project)
            .where(Project.user_id == user_id, Test.test_id == test_id)
            .options(selectinload(Test.questions))
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_best_score(
        self, user_id: uuid.UUID, test_id: uuid.UUID, score: int
    ) -> int | None:
        test = await self.get_test(user_id, test_id)
        if test is None:
            return None

        best_score = min(test.max_score, max(test.best_score, score))
        test.best_score = best_score
        self.session.add(test)
        await self.session.flush()
        return best_score

    async def delete_test(self, user_id: uuid.UUID, test_id: uuid.UUID) -> None:
        query = delete(Test).where(
            Test.test_id == test_id,
            Test.project_id.in_(
                select(Project.project_id).where(Project.user_id == user_id)
            ),
        )
        await self.session.execute(query)

    async def create_test(self, test: Test) -> Test:
        self.session.add(test)
        await self.session.flush()
        return test
