from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "File Processing API"
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800

    # AWS
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "ap-south-1"
    AWS_SESSION_TOKEN: str | None = None

    # S3
    S3_BUCKET_NAME: str

    # SQS
    SQS_FILE_PROCESSING_QUEUE_URL: str
    SQS_EMAIL_NOTIFICATION_QUEUE_URL: str

    # SES
    SES_FROM_EMAIL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()