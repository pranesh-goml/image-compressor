import asyncio
import boto3

from app.core.config import settings


class EmailService:
    def __init__(self):
        self.client = boto3.client(
            "ses",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN,
        )

    async def send_processing_success_email(
        self,
        recipient: str,
        job_id: str,
        original_filename: str,
        current_filename: str,
    ):
        subject = f"File Processed: {current_filename} (Job: {job_id[:8]})"

        body_text = f"""Hello,

Your file has been processed successfully.

• Action Taken: File compressed into zip archive
• Current File: {current_filename}
• Original File: {original_filename}
• Job ID: {job_id}
• Status: COMPLETED

Thank you!
"""

        body_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 560px; margin: 20px auto; padding: 24px; border: 1px solid #e1e4e8; border-radius: 8px; }}
        h2 {{ color: #2da44e; margin-top: 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
        td {{ padding: 8px 12px; border-bottom: 1px solid #eaecef; }}
        td.label {{ font-weight: 600; width: 140px; color: #57606a; }}
        .badge {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: 600; background: #dafbe1; color: #1a7f37; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>File Processed Successfully</h2>
        <p>Your file has been processed and compressed into a zip archive.</p>
        <table>
            <tr><td class="label">Current File:</td><td><strong>{current_filename}</strong></td></tr>
            <tr><td class="label">Original File:</td><td>{original_filename}</td></tr>
            <tr><td class="label">Job ID:</td><td><code>{job_id}</code></td></tr>
            <tr><td class="label">Action Done:</td><td>Compressed into ZIP archive</td></tr>
            <tr><td class="label">Status:</td><td><span class="badge">COMPLETED</span></td></tr>
        </table>
        <p>Thank you for using our service.</p>
    </div>
</body>
</html>"""

        await asyncio.to_thread(
            self._send_email_sync,
            recipient,
            subject,
            body_text,
            body_html,
        )

    async def send_processing_failure_email(
        self,
        recipient: str,
        job_id: str,
        original_filename: str,
        error_message: str,
    ):
        subject = f"Processing Failed: {original_filename} (Job: {job_id[:8]})"

        body_text = f"""Hello,

Unfortunately, your file could not be processed.

• Original File: {original_filename}
• Job ID: {job_id}
• Status: FAILED
• Error Details: {error_message}

Please try again.
"""

        body_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 560px; margin: 20px auto; padding: 24px; border: 1px solid #e1e4e8; border-radius: 8px; }}
        h2 {{ color: #cf222e; margin-top: 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
        td {{ padding: 8px 12px; border-bottom: 1px solid #eaecef; }}
        td.label {{ font-weight: 600; width: 140px; color: #57606a; }}
        .badge {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: 600; background: #ffebe9; color: #cf222e; }}
    </style>
</head>
<body>
    <div class="container">
        <h2>File Processing Failed</h2>
        <p>Unfortunately, your file could not be processed.</p>
        <table>
            <tr><td class="label">Original File:</td><td>{original_filename}</td></tr>
            <tr><td class="label">Job ID:</td><td><code>{job_id}</code></td></tr>
            <tr><td class="label">Status:</td><td><span class="badge">FAILED</span></td></tr>
            <tr><td class="label">Error Details:</td><td>{error_message}</td></tr>
        </table>
        <p>Please try again.</p>
    </div>
</body>
</html>"""

        await asyncio.to_thread(
            self._send_email_sync,
            recipient,
            subject,
            body_text,
            body_html,
        )

    def _send_email_sync(
        self,
        recipient: str,
        subject: str,
        body_text: str,
        body_html: str,
    ):
        self.client.send_email(
            Source=settings.SES_FROM_EMAIL,
            Destination={"ToAddresses": [recipient]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {
                    "Text": {"Data": body_text, "Charset": "UTF-8"},
                    "Html": {"Data": body_html, "Charset": "UTF-8"},
                },
            },
        )