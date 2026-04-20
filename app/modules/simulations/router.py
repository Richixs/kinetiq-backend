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
            "description": "Rendered kinematics simulation (MRU/MRUV) as an MP4 video.",
        }
    },
)
def render_simulation(
    request: SimulationRequest,
    controller: SimulationController = Depends(),
) -> FileResponse:
    """Render a 1D kinematics simulation (MRU or MRUV) and return the resulting MP4."""
    return controller.render_simulation(request)
