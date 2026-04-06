"""Application entrypoint for the FastAPI server."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.api.v1.router import api_router

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Manage startup and shutdown lifecycle events for the application."""
    logger.info(
        "Starting %s in '%s' mode. Debug: %s",
        settings.PROJECT_NAME,
        settings.ENVIRONMENT,
        settings.DEBUG,
    )
    yield
    logger.info("Shutting down %s...", settings.PROJECT_NAME)

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.include_router(api_router, prefix=settings.API_V1_STR)
