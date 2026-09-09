import boto3

from app.core.config import settings

FROM_EMAIL = settings.SES_FROM_EMAIL
TO_EMAIL = "pranesh190504@gmail.com"

client = boto3.client(
    "ses",
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

response = client.send_email(
    Source=FROM_EMAIL,
    Destination={"ToAddresses": [TO_EMAIL]},
    Message={
        "Subject": {"Data": "SES Test Email", "Charset": "UTF-8"},
        "Body": {
            "Text": {"Data": "Amazon SES is working correctly!", "Charset": "UTF-8"}
        },
    },
)

print("Email sent successfully!")
print("Message ID:", response["MessageId"])