from typing import Annotated

from fastapi import Depends
from sqlmodel import select

from backend.db.db_utils import SessionDep
from backend.models.events import Event
from backend.models.teams import Teams
from backend.schemas.event_schema import EventRead


class EventRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def get_events_from_year(self, year: int) -> list[EventRead]:
        events = self.session.exec(select(Event).where(Event.year == year)).all()
        return [
            EventRead(
                meeting_key=e.meeting_key,
                circuit_key=e.circuit_key,
                location=e.location,
                country_name=e.country_name,
                circuit_name=e.circuit_name,
                meeting_official_name=e.meeting_official_name,
                year=e.year,
            )
            for e in events
        ]

    def get_available_years(self) -> list[int]:
        years = self.session.exec(select(Event.year)).all()
        return sorted(set(years))

    def get_teams(self) -> dict[str, str]:
        teams = self.session.exec(select(Teams)).all()
        return {team.name: team.color for team in teams}

    def get_existing_meeting_keys(self) -> set[int]:
        return set(self.session.exec(select(Event.meeting_key)).all())

    def insert_meeting(self, meeting_data: dict) -> None:
        new_meeting = Event(
            meeting_key=meeting_data.get("meeting_key"),
            circuit_key=meeting_data.get("circuit_key"),
            location=meeting_data.get("location"),
            country_name=meeting_data.get("country_name"),
            circuit_name=meeting_data.get("circuit_short_name"),
            meeting_official_name=meeting_data.get("meeting_official_name"),
            year=meeting_data.get("year"),
        )
        self.session.add(new_meeting)

    def meeting_exists(self, meeting_key: int) -> bool:
        return self.session.get(Event, meeting_key) is not None


EventRepoDep = Annotated[EventRepository, Depends()]
