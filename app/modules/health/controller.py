from fastapi import Depends
from .service import HealthService

class HealthController:
    def __init__(self, service: HealthService = Depends()):
        self.service = service

    def get_status(self):
        return self.service.get_health_status()
