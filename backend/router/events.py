from fastapi import APIRouter

from backend.db.database import SessionDep
from backend.service.event import get_available_years, get_events_from_year, get_teams

router = APIRouter()


@router.get("/events/{year}")
def read_events(session: SessionDep, year: int):
    return get_events_from_year(session, year)


@router.get("/events/years/")
def read_available_years(session: SessionDep):
    return get_available_years(session)


@router.get("/teams/")
def read_teams(session: SessionDep):
    return get_teams(session)
