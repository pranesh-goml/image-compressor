from fastapi import APIRouter, Depends, File as FastAPIFile, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.schemas.file import FileResponse
from app.services.file_service import FileService

router = APIRouter(
    prefix="/files",
    tags=["Files"],
)


@router.post(
    "/upload",
    response_model=FileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    email: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    service = FileService(db)
    try:
        return await service.upload_file(
            upload_file=file,
            email=email,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File upload failed: {str(exc)}",
        )


@router.get(
    "/{job_id}",
    response_model=FileResponse,
)
async def get_file(
    job_id: str,
    db: AsyncSession = Depends(get_db),
):
    service = FileService(db)
    file = await service.get_file(job_id=job_id)
    if file is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found",
        )
    return file