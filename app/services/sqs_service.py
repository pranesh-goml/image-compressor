import asyncio
import json
import boto3

from app.core.config import settings


class SQSService:
    def __init__(self):
        self.client = boto3.client(
            "sqs",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN,
        )

    async def send_file_notification(self, message: dict) -> str:
        return await self.send_message(
            queue_url=settings.SQS_EMAIL_NOTIFICATION_QUEUE_URL,
            message=message,
        )

    async def send_message(self, queue_url: str, message: dict) -> str:
        response = await asyncio.to_thread(
            self.client.send_message,
            QueueUrl=queue_url,
            MessageBody=json.dumps(message),
        )
        return response["MessageId"]

    async def receive_messages(
        self,
        queue_url: str,
        max_number: int = 1,
        wait_time: int = 20,
        visibility_timeout: int = 300,
    ) -> list[dict]:
        response = await asyncio.to_thread(
            self.client.receive_message,
            QueueUrl=queue_url,
            MaxNumberOfMessages=max_number,
            WaitTimeSeconds=wait_time,
            VisibilityTimeout=visibility_timeout,
            AttributeNames=["All"],
        )
        return response.get("Messages", [])

    async def delete_message(self, queue_url: str, receipt_handle: str):
        await asyncio.to_thread(
            self.client.delete_message,
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle,
        )