from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.routes.files import router as files_router
from app.core.config import settings
from app.db.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application started")
    yield
    print("Closing database connections...")
    await engine.dispose()
    print("Database connections closed")


app = FastAPI(
    title=settings.APP_NAME,
    description="Asynchronous file upload and processing system",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(files_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}