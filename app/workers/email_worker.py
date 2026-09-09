import asyncio
import json

from app.core.config import settings
from app.services.email_service import EmailService
from app.services.sqs_service import SQSService


async def main():
    print("Starting email worker...")
    sqs_service = SQSService()
    email_service = EmailService()

    while True:
        try:
            messages = await sqs_service.receive_messages(
                queue_url=settings.SQS_EMAIL_NOTIFICATION_QUEUE_URL,
                max_number=1,
                wait_time=20,
                visibility_timeout=120,
            )

            if not messages:
                continue

            for message in messages:
                receipt_handle = message["ReceiptHandle"]
                try:
                    body = json.loads(message["Body"])
                    email = body.get("email")
                    job_id = body.get("job_id", "unknown_job")

                    if not email:
                        print(f"Skipping message for job {job_id}: No email recipient provided.")
                        await sqs_service.delete_message(
                            queue_url=settings.SQS_EMAIL_NOTIFICATION_QUEUE_URL,
                            receipt_handle=receipt_handle,
                        )
                        continue

                    original_filename = body.get("original_filename") or body.get("filename", "unknown_file")
                    current_filename = body.get("current_filename") or body.get("processed_filename") or f"{original_filename}.zip"
                    status = body.get("status", "COMPLETED")

                    if status == "COMPLETED":
                        await email_service.send_processing_success_email(
                            recipient=email,
                            job_id=job_id,
                            original_filename=original_filename,
                            current_filename=current_filename,
                        )
                    else:
                        await email_service.send_processing_failure_email(
                            recipient=email,
                            job_id=job_id,
                            original_filename=original_filename,
                            error_message=body.get("error_message", "Unknown error"),
                        )

                    await sqs_service.delete_message(
                        queue_url=settings.SQS_EMAIL_NOTIFICATION_QUEUE_URL,
                        receipt_handle=receipt_handle,
                    )
                    print(f"Email sent for {job_id}")

                except Exception as exc:
                    print(f"Email processing failed: {exc}")
                    # Do NOT delete. SQS will retry.

        except Exception as exc:
            print(f"Email worker polling error: {exc}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())