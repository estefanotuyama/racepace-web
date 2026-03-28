from typing import Annotated

from fastapi import Depends

from backend.repositories.event import EventRepoDep
from backend.schemas.event_schema import EventResponse


class EventService:
    def __init__(self, repo: EventRepoDep):
        self.repo = repo

    def get_events(self, year: int) -> list[EventResponse]:
        events = self.repo.get_events_from_year(year)
        return [EventResponse(**e.model_dump()) for e in events]

    def get_years(self) -> list[int]:
        return self.repo.get_available_years()

    def get_all_teams(self) -> dict[str, str]:
        return self.repo.get_teams()


EventServiceDep = Annotated[EventService, Depends()]
