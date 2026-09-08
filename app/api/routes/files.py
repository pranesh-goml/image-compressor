from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.schemas.file import FileResponse
from app.services.file_service import FileService


router = APIRouter(
    prefix="/files",
    tags=["Files"],
)


DBSession = Annotated[
    AsyncSession,
    Depends(get_db),
]


@router.post(
    "/",
    response_model=FileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_file(
    filename: str,
    db: DBSession,
):
    service = FileService(db)

    file = await service.create_file(
        filename=filename,
    )

    return file


@router.get(
    "/{job_id}",
    response_model=FileResponse,
)
async def get_file(
    job_id: str,
    db: DBSession,
):
    service = FileService(db)

    file = await service.get_file(
        job_id=job_id,
    )

    if file is None:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    return file