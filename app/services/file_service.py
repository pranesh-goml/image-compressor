import uuid

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import File
from app.repositories.file_repository import FileRepository
from app.services.s3_service import S3Service


class FileService:
    def __init__(self, db: AsyncSession):
        self.repository = FileRepository(db)
        self.s3_service = S3Service()

    async def upload_file(self, upload_file: UploadFile, email: str) -> File:
        job_id = str(uuid.uuid4())
        filename = upload_file.filename or "unknown_file"

        # Prevent path traversal
        filename = filename.replace("\\", "/").split("/")[-1]
        s3_key = f"uploads/{job_id}/{filename}"

        file_record = File(
            job_id=job_id,
            filename=filename,
            email=email,
            original_s3_key=s3_key,
            status="UPLOADING",
        )
        file_record = await self.repository.create(file_record)

        try:
            await self.s3_service.upload_file(
                file_object=upload_file.file,
                s3_key=s3_key,
                content_type=upload_file.content_type,
            )
            file_record = await self.repository.update_status(
                job_id=job_id,
                status="UPLOADED",
            )
            return file_record
        except Exception as exc:
            await self.repository.update_status(
                job_id=job_id,
                status="FAILED",
                error_message=str(exc),
            )
            raise
        finally:
            await upload_file.close()

    async def get_file(self, job_id: str) -> File | None:
        return await self.repository.get_by_job_id(job_id)