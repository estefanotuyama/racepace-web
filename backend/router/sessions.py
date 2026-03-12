from fastapi import APIRouter

from backend.db.database import SessionDep
from backend.service.f1session import get_session_result, get_sessions

router = APIRouter()


@router.get("/sessions/{year}/{round_number}")
def read_sessions(session: SessionDep, year: int, round_number: int):
    return get_sessions(session, year, round_number)


@router.get("/session_result/{year}/{round_number}/{session_name}")
def read_session_result(session: SessionDep, year: int, round_number: int, session_name: str):
    return get_session_result(session, year, round_number, session_name)
