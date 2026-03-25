class HealthService:
    def get_health_status(self) -> dict:
        return {"status": "ok", "message": "Service is healthy"}
