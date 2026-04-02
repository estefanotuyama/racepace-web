from fastapi import APIRouter

from backend.services.event_service import EventServiceDep
from backend.schemas.event_schema import EventResponse

router = APIRouter()


@router.get("/events/{year}",
            response_model=list[EventResponse],
            summary="Gets F1 events",
            description="Accesses de DB and returns all F1 events in a year."
)
def read_events(year: int, service: EventServiceDep):
    return service.get_events(year)


@router.get("/events/years/",
            response_model=list[int],
            summary="Gets all years that we have data for",
            description="Accesses de DB and returns all years for which we have data.")
def read_available_years(service: EventServiceDep):
    return service.get_years()


@router.get("/teams/", response_model=dict[str, str])
def read_teams(service: EventServiceDep):
    return service.get_all_teams()
