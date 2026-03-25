import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.router import api_router

logger = logging.getLogger("uvicorn.error")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} in '{settings.ENVIRONMENT}' mode. Debug: {settings.DEBUG}")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}...")

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.include_router(api_router, prefix=settings.API_V1_STR)
