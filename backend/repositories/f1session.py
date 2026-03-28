from typing import Annotated

from fastapi import Depends
from sqlalchemy import exists as sa_exists
from sqlmodel import select, desc

from backend.db.db_utils import SessionDep
from backend.models.driver import Driver
from backend.models.session_driver import SessionDriver
from backend.models.session_laps import SessionLaps
from backend.models.session_result import SessionResult
from backend.models.sessions import F1Session


class F1SessionRepository:
    def __init__(self, session: SessionDep):
        self.session = session

    def get_sessions_from_meeting_key(self, meeting_key: int):
        return self.session.exec(
            select(F1Session).where(F1Session.meeting_key == meeting_key)
        ).all()

    def get_session_result_data(self, session_key: int):
        statement = (
            select(SessionResult, Driver, SessionDriver)
            .select_from(SessionResult)
            .join(Driver, SessionResult.driver_id == Driver.id)
            .join(SessionDriver, Driver.id == SessionDriver.driver_id)
            .where(SessionResult.session_key == session_key)
            .where(SessionDriver.session_key == session_key)
            .order_by(SessionResult.position)
        )
        return self.session.exec(statement).all()

    def fetch_latest_f1session(self) -> F1Session | None:
        return self.session.exec(
            select(F1Session).order_by(desc(F1Session.date))
        ).first()

    def insert_f1session(self, f1session_data: dict) -> None:
        existing = self.session.get(F1Session, f1session_data["session_key"])
        if existing:
            return
        new_f1session = F1Session(
            location=f1session_data.get("location"),
            meeting_key=f1session_data.get("meeting_key"),
            session_key=f1session_data.get("session_key"),
            session_type=f1session_data.get("session_type"),
            session_name=f1session_data.get("session_name"),
            date=f1session_data.get("date_start"),
        )
        self.session.add(new_f1session)

    def get_incomplete_sessions(self) -> list[F1Session]:
        return self.session.exec(
            select(F1Session).where(
                ~sa_exists(
                    select(SessionLaps.id).where(
                        SessionLaps.session_key == F1Session.session_key
                    )
                )
            )
        ).all()


F1SessionRepoDep = Annotated[F1SessionRepository, Depends()]
