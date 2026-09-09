from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class FileResponse(BaseModel):
    job_id: str
    filename: str
    email: EmailStr
    status: str
    original_s3_key: str | None = None
    processed_s3_key: str | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)