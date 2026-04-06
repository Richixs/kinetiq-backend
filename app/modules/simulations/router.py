"""Route definitions for the simulations module."""

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from .controller import SimulationController
from .models import SimulationRequest

router = APIRouter()


@router.post(
    "/render",
    response_class=FileResponse,
    responses={
        200: {
            "content": {"video/mp4": {}},
            "description": "Rendered MRU simulation as an MP4 video.",
        }
    },
)
def render_simulation(
    request: SimulationRequest,
    controller: SimulationController = Depends(),
) -> FileResponse:
    """Render an MRU kinematics simulation and return the resulting MP4."""
    return controller.render_simulation(request)
