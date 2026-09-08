from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import File


class FileRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, file: File) -> File:
        self.db.add(file)

        await self.db.commit()
        await self.db.refresh(file)

        return file

    async def get_by_job_id(
        self,
        job_id: str,
    ) -> File | None:

        statement = select(File).where(
            File.job_id == job_id
        )

        result = await self.db.execute(statement)

        return result.scalar_one_or_none()

    async def update_status(
        self,
        job_id: str,
        status: str,
        error_message: str | None = None,
    ) -> File | None:

        file = await self.get_by_job_id(job_id)

        if file is None:
            return None

        file.status = status
        file.error_message = error_message

        await self.db.commit()
        await self.db.refresh(file)

        return file