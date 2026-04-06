"""Version 1 API router aggregation."""

from fastapi import APIRouter

from app.modules.health.router import router as health_router
from app.modules.simulations.router import router as simulations_router

api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(simulations_router, prefix="/simulations", tags=["simulations"])
