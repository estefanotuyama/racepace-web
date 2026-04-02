from fastapi import APIRouter

from backend.services.driver_service import DriverServiceDep
from backend.schemas.read_driver import DriverResponse

router = APIRouter()


@router.get("/drivers/{session_key}",
            response_model=list[DriverResponse],
            summary="Get session drivers",
            description="Accesses the DB and returns all drivers in a given F1 session."
                        "session_key is an Integer that connects a session to everything that pertains it."
)
def read_drivers_in_session(session_key: int, service: DriverServiceDep):
    return service.get_drivers(session_key)
