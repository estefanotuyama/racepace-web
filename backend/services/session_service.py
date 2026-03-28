from typing import Annotated

from fastapi import Depends

from backend.repositories.f1session import F1SessionRepoDep
from backend.schemas.session_schema import SessionResponse
from backend.schemas.read_session_result import (
    DriverPositionResponse,
    SessionResultResponse,
)


class SessionService:
    def __init__(self, repo: F1SessionRepoDep):
        self.repo = repo

    def get_sessions(self, meeting_key: int) -> list[SessionResponse]:
        sessions = self.repo.get_sessions_from_meeting_key(meeting_key)
        return [SessionResponse(**s.model_dump()) for s in sessions]

    def get_session_result(self, session_key: int) -> SessionResultResponse:
        driver_positions = self.repo.get_session_result_data(session_key)
        return SessionResultResponse(
            result=[
                DriverPositionResponse(**dp.model_dump())
                for dp in driver_positions
            ]
        )


SessionServiceDep = Annotated[SessionService, Depends()]
