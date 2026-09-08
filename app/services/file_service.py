import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import File
from app.repositories.file_repository import FileRepository


class FileService:

    def __init__(self, db: AsyncSession):
        self.repository = FileRepository(db)

    async def create_file(
        self,
        filename: str,
    ) -> File:

        job_id = str(uuid.uuid4())

        file = File(
            job_id=job_id,
            filename=filename,
            status="UPLOADED",
        )

        return await self.repository.create(file)

    async def get_file(
        self,
        job_id: str,
    ) -> File | None:

        return await self.repository.get_by_job_id(job_id)