"""HTTP boundary for the simulations module."""

from __future__ import annotations

from fastapi import Depends
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from .models import SimulationRequest
from .service import SimulationService


# pylint: disable=too-few-public-methods
class SimulationController:
    """Coordinate simulation render requests."""

    def __init__(self, service: SimulationService = Depends()) -> None:
        self.service = service

    def render_simulation(self, request: SimulationRequest) -> FileResponse:
        """Render the requested simulation and stream the resulting MP4."""
        result = self.service.render(request)
        return FileResponse(
            path=str(result.video_path),
            media_type="video/mp4",
            filename=result.video_path.name,
            background=BackgroundTask(result.cleanup),
        )
