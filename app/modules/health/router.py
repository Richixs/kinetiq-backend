from fastapi import APIRouter, Depends
from .controller import HealthController

router = APIRouter()

@router.get("/")
def health_check(controller: HealthController = Depends()):
    return controller.get_status()
