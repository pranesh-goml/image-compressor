import asyncio
import boto3

from app.core.config import settings


class S3Service:
    def __init__(self):
        self.bucket_name = settings.S3_BUCKET_NAME
        self.client = boto3.client(
            "s3",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN,
        )

    async def upload_file(
        self,
        file_object,
        s3_key: str,
        content_type: str | None = None,
    ) -> str:
        return await asyncio.to_thread(
            self._upload_file_sync,
            file_object,
            s3_key,
            content_type,
        )

    def _upload_file_sync(
        self,
        file_object,
        s3_key: str,
        content_type: str | None,
    ):
        extra_args = {}
        if content_type:
            extra_args["ContentType"] = content_type

        if extra_args:
            self.client.upload_fileobj(
                file_object,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args,
            )
        else:
            self.client.upload_fileobj(
                file_object,
                self.bucket_name,
                s3_key,
            )
        return s3_key

    async def download_file(self, s3_key: str, local_path: str):
        await asyncio.to_thread(
            self.client.download_file,
            self.bucket_name,
            s3_key,
            local_path,
        )

    async def delete_file(self, s3_key: str):
        await asyncio.to_thread(
            self.client.delete_object,
            Bucket=self.bucket_name,
            Key=s3_key,
        )