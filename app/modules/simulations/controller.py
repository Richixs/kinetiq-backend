"""HTTP boundary for the simulations module."""

from __future__ import annotations

from fastapi import Depends
from starlette.background import BackgroundTask
from fastapi.responses import FileResponse

from .models import SimulationRequest
from .service import SimulationService


class SimulationController:
    def __init__(self, service: SimulationService = Depends()) -> None:
        self.service = service

    def render_simulation(self, request: SimulationRequest) -> FileResponse:
        result = self.service.render(request)
        return FileResponse(
            path=str(result.video_path),
            media_type="video/mp4",
            filename=result.video_path.name,
            background=BackgroundTask(result.cleanup),
        )
