import asyncio
import json
import os
import tempfile
from urllib.parse import unquote_plus

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.repositories.file_repository import FileRepository
from app.services.compression_service import CompressionService
from app.services.s3_service import S3Service
from app.services.sqs_service import SQSService


async def process_message(
    message: dict,
    db_factory: async_sessionmaker[AsyncSession],
    sqs_service: SQSService,
    s3_service: S3Service,
    compression_service: CompressionService,
):
    receipt_handle = message["ReceiptHandle"]
    body = json.loads(message["Body"])
    records = body.get("Records", [])

    for record in records:
        event_name = record.get("eventName", "")
        if not event_name.startswith("ObjectCreated:"):
            continue

        bucket = record["s3"]["bucket"]["name"]
        key = unquote_plus(record["s3"]["object"]["key"])

        # Only process uploads
        if not key.startswith("uploads/"):
            continue

        filename = os.path.basename(key)

        # uploads/{job_id}/{filename}
        key_parts = key.split("/")
        if len(key_parts) < 3:
            print(f"Invalid S3 key: {key}")
            continue

        job_id = key_parts[1]
        print(f"Processing job: {job_id}")

        async with db_factory() as db:
            repository = FileRepository(db)
            file_record = await repository.get_by_job_id(job_id)

            if file_record is None:
                print(f"No DB record found for {job_id}")
                continue

            # Idempotency: if already completed, don't process again
            if file_record.status == "COMPLETED":
                print(f"Job {job_id} already completed")
                continue

            await repository.update_status(job_id=job_id, status="PROCESSING")

            try:
                with tempfile.TemporaryDirectory() as temp_dir:
                    original_path = os.path.join(temp_dir, filename)
                    compressed_filename = f"{filename}.zip"
                    compressed_path = os.path.join(temp_dir, compressed_filename)

                    # Download original
                    await s3_service.download_file(
                        s3_key=key,
                        local_path=original_path,
                    )

                    # Compress
                    await compression_service.compress_file(
                        input_path=original_path,
                        output_path=compressed_path,
                        filename=filename,
                    )

                    processed_key = f"processed/{job_id}/{compressed_filename}"
                    with open(compressed_path, "rb") as compressed_file:
                        await s3_service.upload_file(
                            file_object=compressed_file,
                            s3_key=processed_key,
                            content_type="application/zip",
                        )

                    await repository.update_processed_s3_key(
                        job_id=job_id,
                        processed_s3_key=processed_key,
                    )
                    await repository.update_status(job_id=job_id, status="COMPLETED")

                    # Email notification queue
                    notification = {
                        "job_id": job_id,
                        "email": file_record.email,
                        "original_filename": filename,
                        "current_filename": compressed_filename,
                        "status": "COMPLETED",
                    }
                    await sqs_service.send_file_notification(notification)
                    print(f"Job {job_id} completed")

            except Exception as exc:
                print(f"Job {job_id} failed: {exc}")
                await repository.update_status(
                    job_id=job_id,
                    status="FAILED",
                    error_message=str(exc),
                )

                notification = {
                    "job_id": job_id,
                    "email": file_record.email,
                    "original_filename": filename,
                    "status": "FAILED",
                    "error_message": str(exc),
                }
                await sqs_service.send_file_notification(notification)
                # Re-raise so message is NOT deleted.
                # SQS will retry it and eventually move it to the DLQ.
                raise

    await sqs_service.delete_message(
        queue_url=settings.SQS_FILE_PROCESSING_QUEUE_URL,
        receipt_handle=receipt_handle,
    )


async def main():
    print("Starting file processing worker...")
    engine = create_async_engine(
        settings.DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
        pool_pre_ping=True,
    )

    db_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    sqs_service = SQSService()
    s3_service = S3Service()
    compression_service = CompressionService()

    while True:
        try:
            messages = await sqs_service.receive_messages(
                queue_url=settings.SQS_FILE_PROCESSING_QUEUE_URL,
                max_number=1,
                wait_time=20,
                visibility_timeout=300,
            )

            if not messages:
                continue

            for message in messages:
                try:
                    await process_message(
                        message=message,
                        db_factory=db_factory,
                        sqs_service=sqs_service,
                        s3_service=s3_service,
                        compression_service=compression_service,
                    )
                except Exception as exc:
                    print(f"Worker error: {exc}")
                    # DO NOT delete the message. SQS will make it visible again.

        except Exception as exc:
            print(f"Polling error: {exc}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())