"""Controller layer for health endpoints."""

from fastapi import Depends

from .service import HealthService


# pylint: disable=too-few-public-methods
class HealthController:
    """Coordinate health-related request handling."""

    def __init__(self, service: HealthService = Depends()):
        self.service = service

    def get_status(self):
        """Fetch health status from the service layer."""
        return self.service.get_health_status()
