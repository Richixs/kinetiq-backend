"""HTTP routes for health checks."""

from fastapi import APIRouter, Depends

from .controller import HealthController

router = APIRouter()


@router.get("/")
def health_check(controller: HealthController = Depends()):
    """Return the application health status."""
    return controller.get_status()
