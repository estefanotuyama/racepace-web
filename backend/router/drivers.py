from fastapi import APIRouter

from backend.db.database import SessionDep
from backend.service.driver import get_drivers_for_session

router = APIRouter()


@router.get("/drivers/{year}/{round_number}/{session_name}")
def read_drivers_in_session(session: SessionDep, year: int, round_number: int, session_name: str):
    return get_drivers_for_session(session, year, round_number, session_name)
