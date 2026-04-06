"""Business logic for health-related operations."""

# pylint: disable=too-few-public-methods
class HealthService:
    """Provide service-level health checks."""

    def get_health_status(self) -> dict:
        """Return a basic health status payload."""
        return {"status": "ok", "message": "Service is healthy"}
