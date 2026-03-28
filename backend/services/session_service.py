import json
from typing import Annotated

from fastapi import Depends

from backend.repositories.f1session import F1SessionRepoDep
from backend.schemas.session_schema import SessionResponse
from backend.schemas.read_session_result import (
    DriverPositionResponse,
    SessionResultResponse,
)


def _parse_number_field(v):
    """Cleans duration/gap_to_leader values from the database.
    Handles None, 'None' strings, empty strings, and JSON array strings.
    """
    if v == 'None' or v == '' or v is None:
        return None
    elif not v.startswith('['):
        return v
    else:
        valid_json_string = v.replace("None", "null")
        duration_array = json.loads(valid_json_string)
        for duration in reversed(duration_array):
            if duration is not None:
                return duration
        return None


class SessionService:
    def __init__(self, repo: F1SessionRepoDep):
        self.repo = repo

    def get_sessions(self, meeting_key: int) -> list[SessionResponse]:
        f1sessions = self.repo.get_sessions_from_meeting_key(meeting_key)
        return [
            SessionResponse(
                location=s.location,
                meeting_key=s.meeting_key,
                session_key=s.session_key,
                session_type=s.session_type,
                session_name=s.session_name,
                date=s.date,
            )
            for s in f1sessions
        ]

    def get_session_result(self, session_key: int) -> SessionResultResponse:
        results = self.repo.get_session_result_data(session_key)
        return SessionResultResponse(
            result=[
                DriverPositionResponse(
                    position=result.position,
                    team=session_link.team,
                    first_name=driver.first_name,
                    last_name=driver.last_name,
                    number_of_laps=result.number_of_laps,
                    gap_to_leader=_parse_number_field(result.gap_to_leader),
                    duration=_parse_number_field(result.duration),
                    dnf=result.dnf,
                    dns=result.dns,
                    dsq=result.dsq,
                )
                for result, driver, session_link in results
            ]
        )


SessionServiceDep = Annotated[SessionService, Depends()]
